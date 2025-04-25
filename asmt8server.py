import socket #Import socket module for network communication

#Define IP address and port number for server
ip_address = '0.0.0.0' #Listen on all available network interfaces
port_number = 6000 #Port number to listen for incoming connections


myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Create TCP socket with IPv4 Addressing
myTCPSocket.bind((ip_address, port_number)) #Bind TCP socket to specified IP address and port
myTCPSocket.listen(5) #Listen for incoming connections (up to 5 clients)
print(f'Server Listening on {ip_address}:{port_number}')
incomingSocket, incomingAddress = myTCPSocket.accept() #Accept client
print(f'Connected to {incomingAddress}')

while True: #Handles client communication
    myData = incomingSocket.recv(1024) #Receive up to 1024 bytes of data from client
    if not myData: #If no data received, close connection and exit the loop
        incomingSocket.close()
        break
    server_response = myData.decode().upper() #Process the data and convert to uppercase
    incomingSocket.send(bytearray(str(server_response), encoding = 'utf-8')) #Send back processed response to client
    print(server_response)