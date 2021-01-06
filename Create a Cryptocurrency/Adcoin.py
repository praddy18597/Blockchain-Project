#Create a Cryptocurrency
import datetime #the time and date at bolck was developed.
import hashlib  #hash the blocks
import json #to encode the blocks before we hash them
from flask import Flask, jsonify, request #flask=web application and request= for adding nodes inside decentralized blockchain
import requests
from uuid import uuid4 #from uuid library we import uuid function
from urllib.parse import urlparse

#part 1: building the blockchain

class Blockchain:
    
    def __init__(self):  #to specify variables to be introduced preceded by variables as object.
        self.chain = []        #initialize the chain and [] list containing diffrent blocks.
        self.transactions = [] #list of transctrions before added to block
        self.create_block(proof = 1, previous_hash = '0')   #create the genesis block and block contain its own proof and each block have a previous hash since its genesis therefore previous_hash is zero in string and use sha algo therfore in string
        self.nodes = set() #  create set of nodes with empty
          #creating new block.
    def create_block(self, proof, previous_hash):    #self= to take variables as a object
              block = {'index': len(self.chain) + 1,    #creating the dictionary which contain four essientisl keys of block index=index of block(length of chain+1),timestamp=exact time when block is mine, proof and previous_hash.
                       'timestamp': str(datetime.datetime.now()),  # we are taking string format of datetime libtrary with datetime module and from module take now function.
                       'proof' : proof,
                       'previous_hash' : previous_hash,
                       'transactions' : self.transactions} #we take transctions from block
              self.transactions = [] #to make list empty after transctions
              self.chain.append(block)    #append the block
              return block   #display the block.
          
    def get_previous_block(self): #to get last block chain at any time.
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):     #propf of work function we have to solve.
        new_proof = 1          #since we increament value 1 at each iteration until we get right on pow.
        check_proof = False    #it checks the new proof is correct or not.it gives false until we get right proof.
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest() #hash operation is sha 256.so we take hashlib in which we take sha256 function and for complex we take np - pp.we used encode function converting the operation into format that accepts sha256.
            if hash_operation[:4]=='0000': #we take four indexes o to 3 since we have to check leading four zeros.
                check_proof = True
            else:
                new_proof += 1  #we increamnent new proof by 1 since minor failed in first attempt.
                return new_proof
            
    #we check each block has correct proof of work and previous hash of each block = hash of each block
    def hash(self, block):    #self is method of blockchain class
        encoded_block = json.dumps(block, sort_keys = True).encode()      #dumps function cept dictionary of a block as a string.              
        return hashlib.sha256(encoded_block).hexdigest()
        
    def is_chain_valid(self, chain): #we valdiate chain and we take chain for that.
        previous_block = chain[0]    #since we want first block therefore chain[0]    
        block_index = 1              #first block have index 1
        while block_index < len(chain):#we check until block index reach last block of the chain.
           block = chain[block_index]  # we take particualr block from chain.
           if block['previous hash'] != self.hash(previous_block): # 2nd condition
               return False
           previous_proof = previous_block['proof'] #proof of previous block
           proof = block['proof']   #proof of current block
           hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest() #same operation.change in new_proof= proof.
           if hash_operation[:4] != '0000':
               return False                  #since we want four leading zeros.
           previous_block = block            #previous block become current block of chain
           block_index += 1                  #we update block index
           return True
    
    def add_transactions(self, sender, receiver, amount): #method that create transaction between sender and receiver exchanging amount.
       self.transactions.append({'sender': sender,
                                 'receiver': receiver,
                                 'amount' : amount})  #creating the dictionaries with three essential keys
       previous_block = self.get_previous_block()
       return previous_block['index'] + 1         # return index of the previous block

    def add_node(self, address): #we take address of the node
        parsed_url = urlparse(address) # we will parse the address of the node
        self.nodes.add(parsed_url.netloc)  # add nodes to the network


    def replace_chain(self):       #for tackle the consensus the new method we take in which self is the argument
        network = self.nodes       #network containing all the nodes
        longest_chain = None       #intialzing the longest chain
        max_length = len(self.chain)   #to find out which chain is longest by using their length and length of chain we are delaing with.
        for nodes in network:       #we scan all the nodes inside the network
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.jason()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
           if longest_chain:  #if longest chain is not equal to null
               self.chain = longest_chain
               return True
             return False

#Part 2: mining the blockchain
           
#creating a Web app
app = Flask(__name__)     #use flask quickstart

#creating address for the node on port 5000
node_address = str(uuid4()).replace('-', '')



#creating a blockchain
blockchain = Blockchain()  #blcokchain is instance object of blockchain class.

#mining a new block
@app.route('/mine_block', methods=['GET'])  #add URL
def mine_block():   #we mine the block
    previous_block = blockchain.get_previous_block()   #last block of the chain
    previous_proof = previous_block['proof']    #previous proof of block
    proof = blockchain.proof_of_work(previous_proof)   # proof of future new block that will added to blockchain.
    previous_hash = blockchain.hash(previous_block)    # hash of the previous block
    blockchain.add_transaction(sender = node_address, receiver = 'hadelin' , amount = 1) #adding blockchain transactions using blockchain object
    block = blockchain.create_block(proof, previous_hash) #new block
    response = {'message': 'congratulations, you just mine the block1', #making a new dictinary as we previously done.                                                    #to display and connect with postman.
                'index' : block['index'],
                'timestamp': block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash']
                'transactions': block['transactions']}
    return jsonify(response), 200     #200 is http code which stated as everything is okay.

#getting a full Blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,   #we take chain key
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# checking if the blockchain is valid:
@app.route('/get_chain', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'all good. the blockchain is valid.'}
    else:
        response = {'message': 'heuston, we have a problem. the blockchain is not valid.'}
    return jsonify(response), 200

#adding new transaction to the blockchain:
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()     # adding json file
    transactions_keys = {'sender' , 'receiver', 'amount'}   #adding keys
    if not all (key in json for key in transaction_keys):
        return ('some elements of transactions are missing', 400)   #if all the key in transactions key list are not in json file
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'this transcation will be added to the block {index}'}
    return jasonify(response), 201 #since we created new transaction so we used 201 http code
      
#part 3: decentralizing our blockchain:
#connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    node = json.get('nodes')           #all the node in json file connnect to blockchain
    if nodes is None:
        return "No Node", 400
    for node in nodes:
        blockchain.add_node(node)     #add node to blockchain
    response = {'message': 'all nodes are now connected. the adcoin blockchain now contains the follwowing nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jasonify(response), 201

#Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()  # creating the object
    if is_chain_replaced:
        response = {'message': 'The nodes had different chain so that so the chain was replaced by longest chain.' , 
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good the chain is the largest one.'
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200    





#running the app
app.run(host = '0.0.0.0', port = 5000)

            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            

