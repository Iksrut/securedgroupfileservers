import socket
import ssl

# Function to send a message to the server and receive response
def send_message(sock, message):
    sock.sendall(message.encode())      # Encode and send the message to the server
    response = sock.recv(1024)          # Receive response from the server
    return response.decode()            # Decode and return the response

TCP_IP = '127.0.0.1'    # Server IP address
TCP_PORT = 20        # Server port
BUFFER_SIZE = 999999999 # Buffer size for receiving data

# Create a simple TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Wrap the socket for SSL/TLS
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_verify_locations(cafile="cert1.pem")
server_socket = context.wrap_socket(sock, server_hostname=TCP_IP)

# Connect to the server
server_socket.connect((TCP_IP, TCP_PORT))

connected = True
while connected:
    # Get user input for message to send to the server
    message = input("Enter command ('disconnect' to exit): ")
    # Send message to the server and receive response
    response = send_message(server_socket, message)
    # Print server response
    print('Server Response:', response)
    # Check if user wants to disconnect
    if message.lower() == 'disconnect':
        connected = False

# Close the connection
server_socket.close()
