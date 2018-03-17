import hashlib
import json

from textwrap import dedent
from time import time
from uuid import uuid4
from flask import Flask

class Blockchain(object):

  def __init__(self):
    self.chain = []
    self.current_transactions = []
    # Create the genesis block
    self.new_block(previous_hash=1, proof=100)

  def new_block(self, proof, previous_hash=None):
    #Create new block
    block = {
      'index': len(self.chain) + 1,
      'timestamp' : time(),
      'transactions' : self.current_transactions,
      'proof' : proof,
      'previous_hash': previous_hash or self.hash(self.chain[-1]),
    }
    self.current_transactions = []

    self.chain.append(block)
    return block


  def new_transaction(self, sender, receiver, amount):
    #Create new transaction
    self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
    return self.last_block['index'] + 1

  def proof_of_work(self, last_proof: int) -> int:
    proof = 0
    while self.valid_proof(last_proof, proof) is False:
      proof += 1
    return proof

  def valid_proof(last_proof, proof):
    guess = f'{last_proof}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:4] == "0000"

  @staticmethod
  def hash(block):
    #Hashes a block
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

  @property
  def last_block(self):
    #Get the last block
    return self.chain[-1]
    


app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
  last_block = blockchain.last_block
  last_proof = last_block['proof']
  proof = blockchain.proof_of_work(last_proof)

  # We must receive a reward for finding the proof.
  # The sender is "0" to signify that this node has mined a new coin.
  blockchain.new_transaction(
      sender="0",
      recipient=node_identifier,
      amount=1,
  )

  # Forge the new Block by adding it to the chain
  block = blockchain.new_block(proof)

  response = {
      'message': "New Block Forged",
      'index': block['index'],
      'transactions': block['transactions'],
      'proof': block['proof'],
      'previous_hash': block['previous_hash'],
  }
  return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
  values = request.get_json()

  # Check that the required fields are in the POST'ed data
  required = ['sender', 'recipient', 'amount']
  if not all(k in values for k in required):
      return 'Missing values', 400

  # Create a new Transaction
  index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

  response = {'message': f'Transaction will be added to Block {index}'}
  return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
  response = {
      'chain': blockchain.chain,
      'length': len(blockchain.chain),
  }
  return jsonify(response), 200

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)