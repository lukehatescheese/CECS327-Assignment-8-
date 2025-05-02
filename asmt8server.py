import socket #Import socket module for network communication

from sqlalchemy import create_engine,text
from time import time

# Attempt to establish a connection to the PostgreSQL database using SQLAlchemy
try:
    engine=create_engine(
        "postgresql://neondb_owner:npg_fLecKbn4S0uv@ep-young-fire-a576r4et-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
    )
except Exception as e:
    print("Connection failed:")
    print(e)

# Map device board names to their readable names for user-friendly output
device_map = {
    "FridgeArduino": "Smart Refrigerator",
    "CopyFridgeArduino": "Outdoor Refrigerator",
    "DishwasherArduino": "Smart Dishwasher"
}

def query1(): #What is the average moisture inside my kitchen fridge in the past three hours?
    past_three_hours = int(time()) - 3 * 60 * 60
    #SQL query to calculate the average moisture for kitchen fridge within past 3 hours
    query1 = text(f"""
        SELECT
            AVG((payload->>'Moisture Meter - FridgeMoistureMeter')::float) AS avg_moisture
        FROM 
            asmt8table_virtual
        WHERE 
            payload->>'board_name' = 'FridgeArduino'
            AND (payload->>'timestamp')::bigint >= {past_three_hours};
    """)

    # Execute the query and retrieve the average moisture value
    with engine.connect() as conn:
        result = conn.execute(query1)
        avg_moisture = result.scalar()

    #prints the result instead of returning for testing purposes
    #print(f'Average fridge moisture in past three hours: {avg_moisture}%')

    # Return the result as a formatted string
    return f'Average fridge moisture in past three hours: {avg_moisture}%'

def query2(): #What is the average water consumption per cycle in my smart dishwasher?
    # SQL query to calculate the average water consumption per cycle (using the last 5 records as cycles and treating each entry for dishwasher as one cycle)
    query2 = text(f"""
        SELECT
            AVG((payload->>'DishwasherWaterConsumptionSensor')::float) AS avg_water_consumption
        FROM
            asmt8table_virtual
        WHERE
            payload->>'board_name' = 'DishwasherArduino'
        LIMIT 5;
    """)

    # Execute the query and retrieve the average water consumption value
    with engine.connect() as conn:
        result = conn.execute(query2)
        avg_water_consumption = result.scalar()

    # prints the result instead of returning for testing purposes
    #print(f'Average water consumption per cycle in dishwasher: {avg_water_consumption} gallons per cycle')

    # Return the result as a formatted string
    return f'Average water consumption per cycle in dishwasher: {avg_water_consumption} gallons per cycle'

def query3(): #Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?
    # SQL query to calculate the total electricity consumption for each device by summing their ammeter readings,
    # ordering devices by total consumption in descending order, and returning the highest one
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

    # Execute the query and fetch all results (should only be one row because of LIMIT 1)
    with engine.connect() as conn:
        result = conn.execute(query3)
        data = result.fetchall()

    if data:
        # Retrieves the device with the highest total electricity consumption, use metadata to retrieve the name since payload only has board name and asset ID
        device = data[0][0]

        # prints the result instead of returning for testing purposes
        #print(f"Device with the most electricity consumption: {device_map.get(device, device)}")

        # Map the board name to a user-friendly device name using device_map
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

# Map each query to corresponding query function
query_map = {
    'WHAT IS THE AVERAGE MOISTURE INSIDE MY KITCHEN FRIDGE IN THE PAST THREE HOURS?': query1,
    'WHAT IS THE AVERAGE WATER CONSUMPTION PER CYCLE IN MY SMART DISHWASHER?': query2,
    'WHICH DEVICE CONSUMED MORE ELECTRICITY AMONG MY THREE IOT DEVICES (TWO REFRIGERATORS AND A DISHWASHER)?': query3
}

#Handles client communication
while True:
    # Receive up to 1024 bytes of data from client
    myData = incomingSocket.recv(1024)

    # If no data received, close connection and exit the loop
    if not myData: #If no data received, close connection and exit the loop
        incomingSocket.close()
        break

    #Process the data and convert to uppercase
    query_input = myData.decode().upper()
    print("Query Received: ", query_input)

    # Check if query exists and call corresponding function, else return default message
    server_response = query_map.get(query_input, lambda: "Invalid query received.")()

    # Send back processed response to client
    incomingSocket.send(bytearray(str(server_response), encoding = 'utf-8'))
    print("Server Response: ", server_response)
