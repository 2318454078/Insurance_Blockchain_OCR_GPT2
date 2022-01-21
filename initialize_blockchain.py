from blockchain import *
import pickle
blockchain = BlockChain(4)

def initialize_blockchain():
    with open('bc.txt', 'wb') as f:
        pickle.dump(blockchain, f)