import socket #Import socket module for network communication

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

    #print(f'Average fridge moisture in past three hours: {avg_moisture}%')
    return f'Average fridge moisture in past three hours: {avg_moisture}%'

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

    #print(f'Average water consumption per cycle in dishwasher: {avg_water_consumption} gallons per cycle')
    return f'Average water consumption per cycle in dishwasher: {avg_water_consumption} gallons per cycle'

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
        #print(f"Device with the most electricity consumption: {device_map.get(device, device)}")
        return f'Device with the most electricity consumption: {device_map.get(device, device)}'

'''
query1()
query2()
query3()'''

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
    #server_response = myData.decode().upper() #Process the data and convert to uppercase
    queries = ['WHAT IS THE AVERAGE MOISTURE INSIDE MY KITCHEN FRIDGE IN THE PAST THREE HOURS?', 'WHAT IS THE AVERAGE WATER CONSUMPTION PER CYCLE IN MY SMART DISHWASHER?', 'WHICH DEVICE CONSUMED MORE ELECTRICITY AMONG MY THREE IOT DEVICES (TWO REFRIGERATORS AND A DISHWASHER)?']
    query_input = myData.decode().upper()
    server_response = ""
    if query_input == queries[0]:
        server_response = query1()
    elif query_input == queries[1]:
        server_response = query2()
    elif query_input == queries[2]:
        server_response = query3()

    incomingSocket.send(bytearray(str(server_response), encoding = 'utf-8')) #Send back processed response to client
    print(server_response)
