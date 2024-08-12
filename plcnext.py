from datetime import datetime
import os
import sys
import time
import logging
from opcua import Client
from opcua import ua

# Get the current working directory
working_directory = os.getcwd() + "\\app"

# Insert the working directory into the system path
sys.path.insert(0, working_directory)

class SubHandler(object):
    """
    Client to subscription. It will receive events from server
    """
    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)

    def event_notification(self, event):
        print("Python: New event", event)

def run_plc_operations(electricityPrices):
    client = Client("opc.tcp://10.0.2.31:4840/")
    client.set_user('admin')
    client.set_password('8058c2d8')

    # Construct the full path to the certificate files
    der_file_path = os.path.join(working_directory, "opcua_client.der")
    pem_file_path = os.path.join(working_directory, "opcua_client.pem")

    # Set the security string with the full path to the certificate files
    client.set_security_string(f"Basic256Sha256,SignAndEncrypt,{der_file_path},{pem_file_path}")
    client.application_uri = "urn:example.org:FreeOpcUa:python-opcua"

    i = 0

    try:
        client.connect()

        ua_BelpexElecPrices24 = client.get_node("ns=5;s=Arp.Plc.Eclr/BelpexElecPrices24")
        ua_BelpexUpdateTime = client.get_node("ns=5;s=Arp.Plc.Eclr/BelpexUpdateTime")

        print(ua_BelpexElecPrices24.get_value())
        print(ua_BelpexUpdateTime.get_value())

        # Definition of variables, the OPC UA server doesn't 

        # ua_BelpexElecPrices24 is a node object
        # the argument electricityPrices is a list of dictionaries
        # each dictionary has the keys 'from' and 'marketPrice'
        # the value of 'from' is a string representing the hour
        # the value of 'marketPrice' is a float representing the price in MWh
        # the list has a length of 24
        
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
        BelpexElecPrices24.ServerTimestamp = None
        BelpexElecPrices24.SourceTimestamp = None
        ua_BelpexElecPrices24.set_value(BelpexElecPrices24)
        ua_BelpexUpdateTime.set_value(BelpexUpdateTime)

    finally:
        client.disconnect()