# Ethereum Transaction Parser

This project is to given a transaction hash, 
it will get the balance before and after the execution.

Made using web3.py

## Dependencies

virtualenv
web3.py


## How to run?

Create a virtual environment
```
$ virtualenv -p python3 ~/.venv-py3
```

Activate your new virtual environment
```
$ source ~/.venv-py3/bin/activate
```

With virtualenv active, make sure you have the latest packaging tools
```
$ pip install --upgrade pip setuptools
```

Now we can install web3.py
```
$ pip install web3 eth_abi python-dotenv
```

Run the project passing a tx hash
```
$ python main.py [tx-hash] > output.txt
//Example:
$ python main.py 0x6200bf5c43c214caa1177c3676293442059b4f39eb5dbae6cfd4e6ad16305668  > output.txt
```

To finish execution
```
$ deactivate
```