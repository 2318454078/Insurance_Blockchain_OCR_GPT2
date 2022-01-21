import pickle

def load_blockchain():
    with open('bc.txt', 'rb') as f:
        blockchain = pickle.load(f)
        return blockchain

