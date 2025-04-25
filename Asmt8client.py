import socket #Import socket module for network communication

serverIP = input("Enter IP address: ") #Prompts for Server IP
serverPort = int(input("Enter port: ")) #Prompts for Server Port


myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Cretea TCP socket for IPv4 Addressing


with myTCPSocket:
    try: #Establish connection to specified server
        myTCPSocket.connect((serverIP, serverPort))
        while True:
            choice = input ('Choose a message to send:\n1.  What is the average moisture inside my kitchen fridge in the past three hours?\n2. What is the average water consumption per cycle in my smart dishwasher?\n3. Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?\n') #Receive user input for message
            message = {'What is the average moisture inside my kitchen fridge in the past three hours?', 'What is the average water consumption per cycle in my smart dishwasher?', 'Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?'}
            if int(choice) == 1:
                myTCPSocket.send(bytearray(str('What is the average moisture inside my kitchen fridge in the past three hours?'), encoding='utf-8'))
                serverResponse = myTCPSocket.recv(1024).decode('utf-8')  # Receive and decode server response
                print(f'Server response: {serverResponse}')
            elif int(choice) == 2:
                myTCPSocket.send(bytearray(str('What is the average water consumption per cycle in my smart dishwasher?'), encoding='utf-8'))
                serverResponse = myTCPSocket.recv(1024).decode('utf-8')  # Receive and decode server response
                print(f'Server response: {serverResponse}')
            elif int(choice) == 3:
                myTCPSocket.send(bytearray(str('Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?'), encoding='utf-8'))
                serverResponse = myTCPSocket.recv(1024).decode('utf-8')  # Receive and decode server response
                print(f'Server response: {serverResponse}')
            else:
                print('Sorry, this query cannot be processed. Choose to send another message to see the list of valid responses.')
            #myTCPSocket.send(bytearray(str(message[int(choice)-1]), encoding = 'utf-8'))
            #serverResponse = myTCPSocket.recv(1024).decode('utf-8') #Receive and decode server response
            #print(f'Server response: {serverResponse}')
            continue_send = input("Send another message? (Y/N): ") #Prompt user to send another message or terminate connection
            if continue_send.upper() == "N":
                myTCPSocket.close() #Close TCP socket before exiting
                break
    except Exception as error: #Handle connectivity errors and display error message
        print(f'Connection failed. Error Detected: {error}')