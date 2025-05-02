import socket #Import socket module for network communication

serverIP = input("Enter IP address: ") #Prompts for Server IP
serverPort = int(input("Enter port: ")) #Prompts for Server Port

myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Cretea TCP socket for IPv4 Addressing

with myTCPSocket:
    try: #Establish connection to specified server
        myTCPSocket.connect((serverIP, serverPort))
        while True:
            #Asks the user which query to run
            choice = input ('Choose a message to send:\n1. What is the average moisture inside my kitchen fridge in the past three hours?\n2. What is the average water consumption per cycle in my smart dishwasher?\n3. Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?\n') #Receive user input for message
            message = ['What is the average moisture inside my kitchen fridge in the past three hours?', 'What is the average water consumption per cycle in my smart dishwasher?', 'Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?']

            #Sends the query message corresponding to the user input
            if choice.isdigit() and int(choice)-1 in range(3):
                myTCPSocket.send(bytearray(str(message[int(choice)-1]), encoding='utf-8'))
                serverResponse = myTCPSocket.recv(1024).decode('utf-8')  # Receive and decode server response
                print(f'Server response: {serverResponse}')
            else:
                print('Sorry, this query cannot be processed. Choose to send another message to see the list of valid responses.')

            #Prompts user to run another query or end the program
            continue_send = input("Send another message? (Type N or n for No or anything else for Yes) :\n") #Prompt user to send another message or terminate connection
            if continue_send.upper() == "N":
                myTCPSocket.close() #Close TCP socket before exiting
                break
    # Handle connectivity errors and display error message
    except Exception as error:
        print(f'Connection failed. Error Detected: {error}')