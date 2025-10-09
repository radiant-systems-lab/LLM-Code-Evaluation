# Blockchain and Cryptocurrency
import hashlib
import ecdsa
import requests
import json
from datetime import datetime
import binascii
import base58
import secp256k1

def create_simple_blockchain():
    """Create a simple blockchain structure"""
    class Block:
        def __init__(self, data, previous_hash):
            self.timestamp = datetime.now().isoformat()
            self.data = data
            self.previous_hash = previous_hash
            self.nonce = 0
            self.hash = self.calculate_hash()
        
        def calculate_hash(self):
            block_string = f"{self.timestamp}{self.data}{self.previous_hash}{self.nonce}"
            return hashlib.sha256(block_string.encode()).hexdigest()
        
        def mine_block(self, difficulty):
            target = "0" * difficulty
            while self.hash[:difficulty] != target:
                self.nonce += 1
                self.hash = self.calculate_hash()
    
    # Create blockchain
    genesis_block = Block("Genesis Block", "0")
    blockchain = [genesis_block]
    
    # Add more blocks
    transactions = [
        "Alice sends 10 coins to Bob",
        "Bob sends 5 coins to Charlie",
        "Charlie sends 2 coins to Dave"
    ]
    
    for transaction in transactions:
        previous_hash = blockchain[-1].hash
        new_block = Block(transaction, previous_hash)
        new_block.mine_block(2)  # Difficulty of 2
        blockchain.append(new_block)
    
    return {
        'blocks': len(blockchain),
        'chain': [{'hash': block.hash, 'data': block.data, 'nonce': block.nonce} for block in blockchain]
    }

def cryptocurrency_wallet():
    """Cryptocurrency wallet operations"""
    try:
        # Generate private key
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        private_key_hex = private_key.to_string().hex()
        
        # Generate public key
        public_key = private_key.get_verifying_key()
        public_key_hex = public_key.to_string().hex()
        
        # Create Bitcoin-like address (simplified)
        public_key_bytes = public_key.to_string()
        sha256_hash = hashlib.sha256(public_key_bytes).digest()
        ripemd160 = hashlib.new('ripemd160', sha256_hash).digest()
        
        # Add version byte (0x00 for Bitcoin mainnet)
        versioned_payload = b'\x00' + ripemd160
        
        # Double SHA256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned_payload).digest()).digest()[:4]
        
        # Create address
        address_bytes = versioned_payload + checksum
        bitcoin_address = base58.b58encode(address_bytes).decode()
        
        return {
            'private_key': private_key_hex[:20] + "...",  # Truncated for security
            'public_key': public_key_hex[:20] + "...",
            'bitcoin_address': bitcoin_address,
            'key_length': len(private_key_hex)
        }
        
    except Exception as e:
        return {'error': str(e)}

def cryptocurrency_price_tracker():
    """Track cryptocurrency prices"""
    try:
        # Simulate API calls (normally would use requests)
        # Example: requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
        
        simulated_prices = {
            'bitcoin': {'price_usd': 45000.50, 'change_24h': 2.5},
            'ethereum': {'price_usd': 3200.75, 'change_24h': -1.8},
            'litecoin': {'price_usd': 180.25, 'change_24h': 0.9},
            'cardano': {'price_usd': 1.25, 'change_24h': 3.2}
        }
        
        # Calculate portfolio value
        portfolio = {
            'bitcoin': 0.5,
            'ethereum': 2.0,
            'litecoin': 5.0,
            'cardano': 100.0
        }
        
        total_value = 0
        portfolio_details = {}
        
        for crypto, amount in portfolio.items():
            if crypto in simulated_prices:
                value = amount * simulated_prices[crypto]['price_usd']
                total_value += value
                portfolio_details[crypto] = {
                    'amount': amount,
                    'price': simulated_prices[crypto]['price_usd'],
                    'value': value,
                    'change_24h': simulated_prices[crypto]['change_24h']
                }
        
        return {
            'cryptocurrencies': len(simulated_prices),
            'portfolio_value': total_value,
            'portfolio': portfolio_details
        }
        
    except Exception as e:
        return {'error': str(e)}

def smart_contract_simulation():
    """Simulate smart contract operations"""
    class SimpleContract:
        def __init__(self):
            self.balances = {}
            self.total_supply = 1000000
            self.contract_address = hashlib.sha256(b"SimpleToken").hexdigest()[:20]
        
        def transfer(self, from_addr, to_addr, amount):
            if from_addr in self.balances and self.balances[from_addr] >= amount:
                self.balances[from_addr] -= amount
                if to_addr not in self.balances:
                    self.balances[to_addr] = 0
                self.balances[to_addr] += amount
                return True
            return False
        
        def mint(self, to_addr, amount):
            if to_addr not in self.balances:
                self.balances[to_addr] = 0
            self.balances[to_addr] += amount
            self.total_supply += amount
        
        def get_balance(self, addr):
            return self.balances.get(addr, 0)
    
    # Create contract and perform operations
    contract = SimpleContract()
    
    # Mint tokens
    contract.mint("0x123", 1000)
    contract.mint("0x456", 500)
    
    # Transfer tokens
    transfers = [
        ("0x123", "0x789", 100),
        ("0x456", "0x123", 50),
        ("0x789", "0x456", 25)
    ]
    
    successful_transfers = 0
    for from_addr, to_addr, amount in transfers:
        if contract.transfer(from_addr, to_addr, amount):
            successful_transfers += 1
    
    return {
        'contract_address': contract.contract_address,
        'total_supply': contract.total_supply,
        'transfers_executed': successful_transfers,
        'account_balances': len(contract.balances),
        'balances': contract.balances
    }

def transaction_verification():
    """Verify cryptocurrency transactions"""
    try:
        # Create sample transaction
        transaction = {
            'from': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'to': '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2',
            'amount': 0.5,
            'timestamp': datetime.now().isoformat()
        }
        
        # Create transaction hash
        tx_string = json.dumps(transaction, sort_keys=True)
        tx_hash = hashlib.sha256(tx_string.encode()).hexdigest()
        
        # Simulate digital signature
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        signature = private_key.sign(tx_hash.encode())
        
        # Verify signature
        public_key = private_key.get_verifying_key()
        verification_result = public_key.verify(signature, tx_hash.encode())
        
        return {
            'transaction_hash': tx_hash,
            'signature_valid': verification_result,
            'transaction': transaction
        }
        
    except Exception as e:
        return {'error': str(e)}

def merkle_tree_operations():
    """Merkle tree for transaction verification"""
    def create_merkle_tree(transactions):
        if not transactions:
            return None
        
        # Hash all transactions
        hashes = [hashlib.sha256(tx.encode()).hexdigest() for tx in transactions]
        
        # Build tree bottom-up
        while len(hashes) > 1:
            next_level = []
            for i in range(0, len(hashes), 2):
                if i + 1 < len(hashes):
                    combined = hashes[i] + hashes[i + 1]
                else:
                    combined = hashes[i] + hashes[i]
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            hashes = next_level
        
        return hashes[0] if hashes else None
    
    # Sample transactions
    transactions = [
        "Alice -> Bob: 10 BTC",
        "Bob -> Charlie: 5 BTC",
        "Charlie -> David: 3 BTC",
        "David -> Eve: 1 BTC"
    ]
    
    merkle_root = create_merkle_tree(transactions)
    
    return {
        'transactions': len(transactions),
        'merkle_root': merkle_root,
        'transactions_list': transactions
    }

if __name__ == "__main__":
    print("Blockchain and cryptocurrency operations...")
    
    # Simple blockchain
    blockchain_result = create_simple_blockchain()
    print(f"Blockchain: {blockchain_result['blocks']} blocks created")
    
    # Wallet operations
    wallet_result = cryptocurrency_wallet()
    if 'error' not in wallet_result:
        print(f"Wallet: Address generated, key length {wallet_result['key_length']}")
    
    # Price tracking
    price_result = cryptocurrency_price_tracker()
    if 'error' not in price_result:
        print(f"Prices: Portfolio value ${price_result['portfolio_value']:.2f}")
    
    # Smart contract
    contract_result = smart_contract_simulation()
    print(f"Smart Contract: {contract_result['transfers_executed']} transfers, {contract_result['account_balances']} accounts")
    
    # Transaction verification
    tx_result = transaction_verification()
    if 'error' not in tx_result:
        print(f"Transaction: Signature valid: {tx_result['signature_valid']}")
    
    # Merkle tree
    merkle_result = merkle_tree_operations()
    print(f"Merkle Tree: {merkle_result['transactions']} transactions, root: {merkle_result['merkle_root'][:10]}...")