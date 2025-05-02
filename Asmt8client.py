
'''
from sqlalchemy import create_engine,text
from time import time

try:
    engine=create_engine(
        "postgresql://neondb_owner:npg_fLecKbn4S0uv@ep-young-fire-a576r4et-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
    )
except Exception as e:
    print("Connection failed:")
    print(e)

device_map = {
    "FridgeArduino": "Smart Refrigerator",
    "CopyFridgeArduino": "Outdoor Refrigerator",
    "DishwasherArduino": "Smart Dishwasher"
}

def query1(): #What is the average moisture inside my kitchen fridge in the past three hours?
    past_three_hours = int(time()) - 3 * 60 * 60
    #Finds average moisture for kitchen fridge within past 3 hours
    query1 = text(f"""
        SELECT
            AVG((payload->>'Moisture Meter - FridgeMoistureMeter')::float) AS avg_moisture
        FROM 
            asmt8table_virtual
        WHERE 
            payload->>'board_name' = 'FridgeArduino'
            AND (payload->>'timestamp')::bigint >= {past_three_hours};
    """)
    with engine.connect() as conn:
        result = conn.execute(query1)
        avg_moisture = result.scalar()
    print(f'Average fridge moisture in past three hours: {avg_moisture}%')

def query2(): #What is the average water consumption per cycle in my smart dishwasher?
    #Treating each entry for dishwasher as one cycle, take average of previous 5 cycles
    query2 = text(f"""
        SELECT
            AVG((payload->>'DishwasherWaterConsumptionSensor')::float) AS avg_water_consumption
        FROM
            asmt8table_virtual
        WHERE
            payload->>'board_name' = 'DishwasherArduino'
        LIMIT 5;
    """)
    with engine.connect() as conn:
        result = conn.execute(query2)
        avg_water_consumption = result.scalar()
    print(f'Average water consumption per cycle in dishwasher: {avg_water_consumption} gallons per cycle')

def query3(): #Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?
    #Group by each device and sum together their electricity consumption, then order the sums so that the highest is at the top and
    #result is the highest number
    query3 = text(f"""
    SELECT
        payload->>'board_name' AS device,
        SUM((payload->>'FridgeAmmeter')::float) +
        SUM((payload->>'DishwasherAmmeter')::float) +
        SUM((payload->>'CopyFridgeAmmeter')::float) AS total_electricity
    FROM
        asmt8table_virtual
    GROUP BY
        device
    ORDER BY
        total_electricity DESC
    LIMIT 1;  -- Limit to only the device with the highest total electricity consumption
    """)

    with engine.connect() as conn:
        result = conn.execute(query3)
        data = result.fetchall()

    if data:
        # The device with the highest total electricity consumption, use metadata to retrieve the name since payload only has board name and asset ID
        device = data[0][0]
        print(f"Device with the most electricity consumption: {device_map.get(device, device)}")

query1()
query2()
query3()
'''

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
