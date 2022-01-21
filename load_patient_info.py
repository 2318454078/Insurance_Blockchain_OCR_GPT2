from load_blockchain import *

def load_info(patient_name):
    blockchain = load_blockchain()
    for i in range(1, len(blockchain.chain)):
        if patient_name == blockchain.chain[i].transactions[0]['patient_name']:
            return blockchain.chain[i].transactions[0]

if __name__ == '__main__':
    print(load_info('12'))
