import sys
import os
import json
from dotenv import load_dotenv
from web3 import Web3
from eth_abi import decode_abi

# Using free version of alchemy is not possible to create a trace
# The solution here is to check the events to get information

#Valid if number of inputs is correct
if not len(sys.argv) == 2:
  raise ValueError("Invalid number of inputs. Expected 1, got {}".format(len(sys.argv)))

load_dotenv()

ALCHEMY_URL = os.getenv("ALCHEMY_URL")

print("Connecting to node")
   
# Connect to node
w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))

print("Getting tx hash")

# Get the transaction hash of the initial transaction
tx_hash = sys.argv[1]

search_tx = w3.eth.getTransaction(tx_hash)

print("Parsing tx: {}\n".format(tx_hash))

# Get the block number of the initial transaction
block_number = w3.eth.getTransaction(tx_hash)['blockNumber']

# Get the block that contains the initial transaction
block = w3.eth.getBlock(block_number)

# Get the list of transaction hashes in the block
block_tx_hashes = block['transactions']

# Find the transaction that matches the initial transaction hash
for block_tx_hash in block_tx_hashes:
  tx = w3.eth.getTransaction(block_tx_hash)
  if tx['hash'] == search_tx['hash']:
      break

# Get the addresses of contracts involved in the chain of contract calls
addresses = set()
addresses.add(tx['from'])
if tx['to']:
  addresses.add(tx['to'])

  # Get the receipt of the transaction
  receipt = w3.eth.getTransactionReceipt(tx['hash'])

  # Check if the transaction created a new contract
  if receipt['contractAddress']:
      addresses.add(receipt['contractAddress'])

  # Get the next transaction in the chain of contract calls
  for log in receipt['logs']:
    addresses.add(log.get('address'))

# Check what contracts are type of ERC20
abi = [
  {
      "constant": True,
      "inputs": [],
      "name": "totalSupply",
      "outputs": [
          {
              "name": "",
              "type": "uint256"
          }
      ],
      "payable": False,
      "stateMutability": "view",
      "type": "function"
  },
  {
      "constant": True,
      "inputs": [
          {
              "name": "_owner",
              "type": "address"
          }
      ],
      "name": "balanceOf",
      "outputs": [
          {
              "name": "balance",
              "type": "uint256"
          }
      ],
      "payable": False,
      "stateMutability": "view",
      "type": "function"
  },
  {
    "constant": True,
    "inputs":[],
    "name":"name",
    "outputs":[
      {"internalType":"string","name":"","type":"string"}
    ],
    "stateMutability":"view",
    "type":"function"
  }
]

# Get the difference balances of ERC20s
for contractAddress in addresses:
    contract = w3.eth.contract(contractAddress, abi=abi)
    for clientAddress in addresses:
      if(clientAddress == contractAddress): 
        continue
      try:
        # Get balance before and after the attack
        balanceBefore = contract.functions.balanceOf(clientAddress).call(None, block_number - 1)
        balanceAfter = contract.functions.balanceOf(clientAddress).call(None, block_number + 1)
        erc20Name = contract.functions.name().call()
        balanceDiff = balanceAfter - balanceBefore
        if balanceDiff > 0:
          print('The contract {} wins {} ERC20({})'.format(clientAddress, balanceDiff, erc20Name))
        elif balanceDiff < 0:
          print('The contract {} lose {} ERC20({})'.format(clientAddress, balanceDiff, erc20Name))
      except:
        #If the contractAddress is not ERC20
        continue

print("\n")
# Get the differences balance in ETH
for address in addresses:
    # Get balance before and after the attack
    ethBalanceBefore = w3.eth.getBalance(address,block_number - 1)
    ethBalanceAfter = w3.eth.getBalance(address,block_number + 1)
    ethBalanceDiff = ethBalanceAfter - ethBalanceBefore
    if ethBalanceDiff > 0:
      print('The contract {} wins {} ETH'.format(address, w3.fromWei(ethBalanceDiff, 'ether')))
    elif ethBalanceDiff < 0:
      print('The contract {} lose {} ETH'.format(address, w3.fromWei(-1*ethBalanceDiff, 'ether')))



