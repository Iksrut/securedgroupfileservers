####################################################
# Project Phase 2 - Group_Server                   #
####################################################

import socket
import random
import string
import json
import Json_Operations
import ssl
import bcrypt


# Function to generate token - it's just 16 random characters 


TCP_IP = '127.0.0.1'  # IP address to Listen on all interfaces
TCP_PORT = 20     # Server port
BUFFER_SIZE = 4096  # Buffer size for recieveing data

# Create socket, bind the socket, and listen for incoming connections 
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((TCP_IP, TCP_PORT))
sock.listen(5)


# Wrap the socket for SSL/TLS
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="cert1.pem", keyfile="key1.pem")
server_socket = context.wrap_socket(sock, server_side=True)

print("Group Server listening on port", TCP_PORT)

# Function to hand client requests
def handle_client_request(data):
    # Check the recieved data for various commands and respond accordingly
    if data.upper().startswith(b'CREATE_USER'):
        _, username, password, token = data.decode().split(';')
        # Call a function from the Json_Operations module to insert a new user 
        Json_Operations.insert_user(username, password, token)
        conn.send(b'CREATE_USER_RESPONSE:SUCCESS')

    elif data.upper().startswith(b'CREATE_GROUP'):
        _, groupname, user_token = data.decode().split(';')

        # Check if the user token is valid
        if Json_Operations.verify_token(user_token):
            # Call a function from the Json_Operations to insert a new group
            try:
                Json_Operations.insert_group(groupname, user_token)
                conn.send(b'CREATE_GROUP: SUCCESS')
            except ValueError as e:
                conn.send(f'CREATE_GROUP: FAILURE:{str(e)}'.encode())
        else:
            # Send failure response for invalid token
            conn.send(b'CREATE_GROUP_RESPONSE:FAILURE:Invalid token')  

    elif data.upper().startswith(b'LIST_USERS'):
        # Fetch all users 
        users = Json_Operations.fetch_all_users()
        conn.send(json.dumps(users).encode())

    elif data.upper().startswith(b'LIST_GROUPS'):
        # Fetch all groups
        groups = Json_Operations.fetch_all_groups()
        conn.send(json.dumps(groups).encode())
        
    elif data.upper().startswith(b'GET_TOKEN'):
        # Extract username from data (format: "GET_TOKEN;username")
        _,username, password = data.decode().split(';')
        token = Json_Operations.get_token(username, password)
        print('Token:', token)
        if token:
            conn.send(token.encode())
        else:
            # Handle the case where token is None (e.g., username or password is incorrect)
            conn.send(b'GET_TOKEN_RESPONSE:FAILURE:Invalid username or password')
    
    elif data.upper().startswith(b'ADD_USER_TO_GROUP'):
        _, username, groupname, user_token = data.decode().split(';')
        # Check if the user token is valid
        if Json_Operations.verify_token(user_token):
            # Call a function from the Json_Operations module to add the user to the group
            if Json_Operations.add_user_to_group(username, groupname, user_token):
                conn.send(b'ADD_USER_TO_GROUP: SUCCESS')
            else:
                conn.send(b'ADD_USER_TO_GROUP: FAILURE: Invalid group owner or group does not exist')
        else:
            conn.send(b'ADD_USER_TO_GROUP_RESPONSE: FAILURE: Invalid token')
             
    elif data.upper().startswith(b'LIST_MEMBERS'):
        _, groupname, user_token = data.decode().split(';')
        # Check if the user token is valid
        if Json_Operations.verify_token(user_token):
            # Call a function from the Json_Operations module to list members of the group 
            members = Json_Operations.list_members(groupname, user_token)
            conn.send(json.dumps(members).encode())
        else:
            conn.send(b'LIST_MEMBERS_RESPONSE:FAILURE:Invalid token')    
    
    elif data.lower().startswith(b'help'):  
        # Respond to help command
        response = "\nAvailable commands are: \nGET_TOKEN;username;password \nCREATE_USER;username;password;token (only admin)\nCREATE_GROUP;groupname;token\nADD_USER_TO_GROUP;username;groupname;token\nLIST_MEMBERS;groupname;token (only group owners)\nGET_PUBLIC;username;password"
        conn.send(response.encode())
    
    elif data.upper().startswith(b'GET_PUBLIC'):
        _, username, password = data.decode().split(';')
        # Check if the user is authorized to get the public key
        public_key = Json_Operations.get_public(username, password)
        conn.send(public_key.encode())    
        
    else:
        # Respond to any other message with an error message
        response = "Server received your message: but there it's not a valid command."
        conn.send(response.encode())
        
try:
    while True:
        # Accept incoming connections
        conn, addr = server_socket.accept()
        print('Connected with', addr)
        # Send a welcome message to the client
        welcome_message = "Welcome to the Group Server. Please type 'help' to see available commands."
        conn.send(welcome_message.encode())
        
        while True:
            # Recieve data from the client
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            print('Received data:', data.decode())
            
            # Process incoming data and send response
            if data.decode().lower() == 'disconnect': 
                # Do this if client wants to disconnect
                print('Client requested disconnect. Closing connection.')
                response = "Closing the session..."
                conn.send(response.encode())
                conn.close()
                break
            
            # Respond to any other message
            else:
                handle_client_request(data)

# Handle any ecveptions
except Exception as e:
    print('Error:', e)

finally:
    # Close ther server socket
    server_socket.close()
