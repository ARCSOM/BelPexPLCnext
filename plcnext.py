import asyncio
from datetime import datetime
import os
import sys
import argparse

from asyncua import Client
from asyncua import ua

# Initialize the parser
parser = argparse.ArgumentParser(description='Set user and password for the client.')

# Add arguments
parser.add_argument('--user', type=str, required=True, help='Username for the client')
parser.add_argument('--password', type=str, required=True, help='Password for the client')

# Parse the arguments
args = parser.parse_args()


url = "opc.tcp://10.0.2.31:4840/"
client = Client("opc.tcp://10.0.2.31:4840/")
client.set_user(args.user)
client.set_password(args.password)

# Get the current working directory
# If the script is run from a linux machine, the path separator should be changed to '/'

if os.name == 'posix':
    working_directory = os.getcwd() + "/app"
else:
    working_directory = os.getcwd() + "\\app"


# Insert the working directory into the system path
sys.path.insert(0, working_directory)


class SubHandler:
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        print("New data change event", node, val)

    def event_notification(self, event):
        print("New event", event)

# function that return the last update time
async def get_last_update_time():
    # Construct the full path to the certificate files
    der_file_path = os.path.join(working_directory, "opcua_client.der")
    pem_file_path = os.path.join(working_directory, "opcua_client.pem")

    # Set the security string with the full path to the certificate files
    await client.set_security_string(f"Basic256Sha256,SignAndEncrypt,{der_file_path},{pem_file_path}")
    client.application_uri = "http://examples.freeopcua.github.io"

    try:
        await client.connect()

        ua_BelpexUpdateTime = client.get_node("ns=5;s=Arp.Plc.Eclr/BelpexUpdateTime")

        return await ua_BelpexUpdateTime.get_value()

    finally:
        await client.disconnect()


async def run_plc_operations(electricityPrices):

    # Construct the full path to the certificate files
    der_file_path = os.path.join(working_directory, "opcua_client.der")
    pem_file_path = os.path.join(working_directory, "opcua_client.pem")

    # Set the security string with the full path to the certificate files
    await client.set_security_string(f"Basic256Sha256,SignAndEncrypt,{der_file_path},{pem_file_path}")
    client.application_uri = "http://examples.freeopcua.github.io"

    # client.connect()

    # client.disconnect()

    try:
        await client.connect()

        ua_BelpexElecPrices24 = client.get_node("ns=5;s=Arp.Plc.Eclr/BelpexElecPrices24")
        ua_BelpexUpdateTime = client.get_node("ns=5;s=Arp.Plc.Eclr/BelpexUpdateTime")

        print(await ua_BelpexElecPrices24.get_value())
        print(await ua_BelpexUpdateTime.get_value())

        # Definition of variables, the OPC UA server doesn't 

        # ua_BelpexElecPrices24 is a node object
        # the argument electricityPrices is a list of dictionaries
        # each dictionary has the keys 'from' and 'marketPrice'
        # the value of 'from' is a string representing the hour
        # the value of 'marketPrice' is a float representing the price in MWh
        # the list has a length of 24

        # test electricityPrices array of random key value pairs
        # electricityPrices = [['2024-08-12T22:00:00.000Z', 99.64],
        #                     ['2024-08-12T23:00:00.000Z', 87.92],
        #                     ['2024-08-13T00:00:00.000Z', 76.6],
        #                     ['2024-08-13T01:00:00.000Z', 75.84],
        #                     ['2024-08-13T02:00:00.000Z', 75.59],
        #                     ['2024-08-13T03:00:00.000Z', 85.9],
        #                     ['2024-08-13T04:00:00.000Z', 111.53],
        #                     ['2024-08-13T05:00:00.000Z', 124.04],
        #                     ['2024-08-13T06:00:00.000Z', 117.89],
        #                     ['2024-08-13T07:00:00.000Z', 94.77],
        #                     ['2024-08-13T08:00:00.000Z', 70.74],
        #                     ['2024-08-13T09:00:00.000Z', 56.88],
        #                     ['2024-08-13T10:00:00.000Z', 44.6],
        #                     ['2024-08-13T11:00:00.000Z', 41.69],
        #                     ['2024-08-13T12:00:00.000Z', 49.06],
        #                     ['2024-08-13T13:00:00.000Z', 65.07],
        #                     ['2024-08-13T14:00:00.000Z', 82.38],
        #                     ['2024-08-13T15:00:00.000Z', 93.94],
        #                     ['2024-08-13T16:00:00.000Z', 107.17],
        #                     ['2024-08-13T17:00:00.000Z', 149.78],
        #                     ['2024-08-13T18:00:00.000Z', 154.6],
        #                     ['2024-08-13T19:00:00.000Z', 114.88],
        #                     ['2024-08-13T20:00:00.000Z', 112.42],
        #                     ['2024-08-13T21:00:00.000Z', 103.9]]
        
        #extract the electricity prices from the list of dictionaries
        prices = [kvp[1] for kvp in electricityPrices]

        #extract the last update time from the list of dictionaries in formate "YYYY-MM-DD HH:MM:SS"
        lastUpdateTime = electricityPrices[23][0]
        
        # Parse the timestamp to a datetime object
        dt = datetime.strptime(lastUpdateTime, "%Y-%m-%dT%H:%M:%S.%fZ")

        print(dt)
        
        BelpexElecPrices24 = ua.DataValue(ua.Variant(prices, ua.VariantType.Float))
        BelpexUpdateTime = ua.DataValue(ua.Variant(dt, ua.VariantType.DateTime))


        # ua_BelpexElecPrices24 is an array of 24 real values
        # set the first value to 0.0 add 0.1 to the rest
        # this is just for testing purposes
        # BelpexElecPrices24.ServerTimestamp = None
        # BelpexElecPrices24.SourceTimestamp = None
        await ua_BelpexElecPrices24.set_value(BelpexElecPrices24)
        await ua_BelpexUpdateTime.set_value(BelpexUpdateTime)

    finally:
        await client.disconnect()
