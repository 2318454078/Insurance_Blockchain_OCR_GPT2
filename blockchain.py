from hashlib import sha256
import time
import json
import logging
from typing import Dict, List
import rsa
import pickle
import os

# https://www.mdnice.com/writing/684b1f8be39d41a081a36b4539bd8e7e
# block + chain
class Block():
    def __init__(self, transactions: List, prev_hash):
        # transaction -> list of objects
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.nonce = 1  # use for mining
        self.timestamp = time.time()
        self.hash = self.compute_hash()

    def __repr__(self):
        return f"{self.transactions}"

    def compute_hash(self):
        block_string = "{}{}{}{}".format(json.dumps(
            self.transactions), self.prev_hash, str(self.nonce), self.timestamp)
        return sha256(block_string.encode()).hexdigest()

    def validate_transaction(self):
        for transaction in self.transactions:
            if not transaction.is_valid():
                return False
            else:
                return True

    def mine(self, difficulty: int):
        if not self.validate_transaction():
            raise Exception('Abnormal transaction found, abort.')

        answer = '0'*difficulty

        while self.hash[:difficulty] != answer:
            self.nonce += 1
            self.hash = self.compute_hash()

        print(f'Finished mining, tryout times:{self.nonce}')


class MedicalRecord(Dict):
    def __init__(self, patient_name, patient_id, diagnosis, date):
        self.update(patient_name=patient_name)
        self.update(patient_id=patient_id)
        self.update(diagnosis=diagnosis)
        self.update(date=date)
        # self.timestamp = timestamp
        self.update(hash=self.compute_hash())

    def __repr__(self):
        return json.dumps(self)

    def sign(self, private_key):
        self.signature = rsa.sign_hash(
            hash_value=self['hash'].encode("utf-8"),
            priv_key=private_key,
            hash_method='SHA-256')

    def is_valid(self):
        if not self['patient_name']:
            return False

        else:
            # 这里由于没有引入数字签名，暂不验证
            return True

    def compute_hash(self):
        Transaction_string = "{}{}{}".format(
            self['patient_name'], self['patient_id'], self['diagnosis'], self['date'])
        return sha256(Transaction_string.encode()).hexdigest()


class BlockChain():
    def __init__(self, difficulty):
        self.chain = [self.create_genesis()]
        self.transactionPool = []
        self.Reward = 1
        self.difficulty = difficulty

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty

    def create_genesis(self) -> Block:
        genesis_block = Block(transactions=[], prev_hash=0)
        return genesis_block

    def get_latest_block(self):
        return self.chain[-1]

    def add_block_to_chain(self, new_block: Block):
        if new_block.hash[:self.difficulty] == '0'*self.difficulty:
            new_block.prev_hash = self.get_latest_block().hash
            self.chain.append(new_block)
            print(f" a new block added to blockchain.")
        else:
            print('block validation failed.')

    def validate_chain(self):
        if len(self.chain) == 1:
            return self.chain[0].compute_hash() == self.chain[0].hash

        # validate block
        for i in range(1, len(self.chain)):
            block_to_validate = self.chain[i]

            # validate transactions in block
            if not block_to_validate.validate_transaction():
                logging.error('Fraud transactions!')
                return False

            # validate data in this block hasn't been tampered
            elif not block_to_validate.hash == block_to_validate.compute_hash():
                logging.error(
                    f'Data has been tampered! \n this hash:{block_to_validate.hash} \n computed hash:{block_to_validate.compute_hash()}')
                return False

            # validate block.prev_hash == previous block.hash
            elif not block_to_validate.prev_hash() == self.chain[i-1].hash:
                logging.error('Chain broke!')
                return False

            else:
                return True
    pass

# test

# blockchain = BlockChain(4)

# transaction1 = MedicalRecord(patient_name='Paparazzi', patient_id='Elephant', diagnosis='666', date='2021-01-01')

# transaction2 = MedicalRecord(patient_name='Elephant', patient_id='Sylar', diagnosis='100', date='2021-01-01')

# # add one block to chain
# block1 = Block(
#     transactions=[transaction1],
#     prev_hash=blockchain.get_latest_block().hash)
# block1.mine(difficulty=4)
# blockchain.add_block_to_chain(block1)
# print(f"hash of block1: {block1.hash}")

# if __name__ == '__main__':
#     with open('test.txt', 'wb') as f:
#         pickle.dump(blockchain, f)

# # add another block to chain
# block2 = Block(
#     transactions=[transaction2],
#     prev_hash=blockchain.get_latest_block().hash)
# block2.mine(difficulty=5)
# blockchain.add_block_to_chain(block2)
# print(f"hash of block2: {block1.hash}")