#######################################################
# Backend for the file operations of the group server #
#######################################################
import json
import random
import string
import base64
import bcrypt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# JSON File Path
JSON_FILE = 'data.json'

# Generate a new RSA key pair for signing
def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key

# Load existing key pair or generate a new one if not present
def load_or_generate_key_pair():
    try:
        with open('private_key.pem', 'rb') as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )
    except FileNotFoundError:
        private_key, public_key = generate_key_pair()
        with open('private_key.pem', 'wb') as key_file:
            key_file.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )
    else:
        public_key = private_key.public_key()
    
    return private_key, public_key

# Load data from JSON file
def load_data():
    try:
        with open(JSON_FILE, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:                                
        return {"Internal Error": "Data file not found."}

# Save data to JSON file
def save_data(data):                                         
    with open(JSON_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Generate a secure token
def generate_secure_token():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    return random_string

# Sign a token using the server's private key

def sign_token(token, private_key):
    signature = private_key.sign(
        token.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    # Encode the signature in Base64
    signature_base64 = base64.b64encode(signature).decode()
    return signature_base64



# Function associated with the GET_TOKEN command - generates a new token for the user or retrieves an existing one
def check_password(username, password):
    data = load_data()
    for user in data['users']:
        if user['username'] == username:
            # Verify the password
            if bcrypt.checkpw(password.encode(), user['password_hash'].encode()):    
                return True
            else:
                # Return None if the password doesn't match
                return False
    # Return None if the user doesn't exist

# Function associated with the GET_TOKEN command


def get_token(username, password):
    private_key, public_key = load_or_generate_key_pair()
    token = generate_secure_token()
    signature = sign_token(token, private_key)

    data = load_data()
    user_tokens = data['tokens']
    users = data['users']

    # Initialize a variable to keep track of the user's existence in 'tokens'
    user_exists_in_tokens = False

    # Check if the username exists in 'tokens'
    for token_info in user_tokens:
        if token_info['username'] == username: 
            if check_password(username, password):
                user_exists_in_tokens = True
                return f'Signed token: {token_info["signed_token"]}\nPlain token: {token_info["plain_token"]}'
    
    # If the username does not exist in 'tokens', check in 'users'
    if username in users and not user_exists_in_tokens:
        if check_password(username, password):
            new_token_info = {'username': username, 'signed_token': signature, 'plain_token': token}
            data['tokens'].append(new_token_info)
            save_data(data)
            return f'Signed token: {new_token_info["signed_token"]}\nPlain token: {token}'
    
    return False






# Function to get the server's public key

def get_public(username, password):
    data = load_data()
    for user_info in data['users']:
        if user_info['username'] == username:
            if bcrypt.checkpw(password.encode(), user_info['password_hash'].encode()):
                private_key, public_key = load_or_generate_key_pair()
                public_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return public_pem.decode()
    else:
        return "Access Denied"



# Function to verify token, check if it's present in JSON file
def verify_token(token):
    data = load_data()
    # Check if the token exists in the data file
                                                # will have to sign and hash, then compare with stored hashes 
    for user_token in data['tokens']:                        
        if user_token['plain_token'] == token:
            print("Token Verified")
            return True
    return False

# Function to retrieve a username from token
def get_username_from_token(token):
    data = load_data()
    # Find the username assocaited with the given token
                                                # will have to sign and hash, then compare with stored hashes 
    for user_token in data['tokens']:                       
        if user_token['plain_token'] == token:
            return user_token['username']
    return None

# Function to insert a new user into the data file 
def insert_user(username, password, token):
    data = load_data()
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    # Check if the token is valid and the user is an admin
    if not is_admin(get_username_from_token(token)): 
        raise ValueError("Not and Admin user")
    # Generate user ID (for simplicity)
    user_id = len(data['users']) + 1       
    new_user = {"id": user_id, "username": username, "password_hash": password_hash}
    # Append the new user to the users list in data
    data['users'].append(new_user)
    save_data(data)

# Function to insert a new group into the data file
def insert_group(groupname, token): 
    data = load_data()
    # Check if the token is valid
    if not verify_token(token):
        raise ValueError("Invalid token")
    # Generate group ID (for simplicity) 
    group_id = len(data['groups']) + 1 
    # Create a new group object 
    new_group = {"id": group_id, "groupname": groupname, "owner": get_username_from_token(token), "members": [], "files": []} # Remember to edit and add owner to members list when creating a group
    # Append the new group to the groups list in data 
    data['groups'].append(new_group)
    save_data(data)
    
def add_user_to_group(username, groupname, token):
    data = load_data()
    print (get_username_from_token(token))
    # Find the group and verify ownership - only owner can add members 
    for group in data['groups']:
        if group['groupname'] == groupname and group['owner'] == get_username_from_token(token):
            
            group['members'].append(username)
            save_data(data)
            return True
    return False    

def list_members(groupname, token): 
    data = load_data()
    # Find the group and verify ownership - only owner can list members
    for group in data['groups']:
        if group['groupname'] == groupname and group['owner'] == get_username_from_token(token):
            return group['members']
    return []

# Function to fetch all users from the data file - only used for testing
def fetch_all_users():
    data = load_data()
    return data['users']

# Function to fetch all groups from the data file - only used for testing
def fetch_all_groups():
    data = load_data()
    return data['groups']


def is_admin(username):
    data = load_data()
    for group in data['groups']:
        if group['groupname'] == './ADMIN' and username in group['members'] or username == group['owner']:
            return True
    return False
