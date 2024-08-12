import os
import sys

# Get the current working directory
working_directory = os.getcwd() + "\\app"

# Insert the working directory into the system path
sys.path.insert(0, working_directory)
import time
import logging

from opcua import Client
from opcua import ua


class SubHandler(object):

    """
    Client to subscription. It will receive events from server
    """

    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)

    def event_notification(self, event):
        print("Python: New event", event)


if __name__ == "__main__":
    #from IPython import embed
    #logging.basicConfig(level=logging.DEBUG)
    
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

        while i < 5 :
            
            ua_LevelMaximum = client.get_node("ns=5;s=Arp.Plc.Eclr/LevelMaximum")
            ua_LevelMinimum = client.get_node("ns=5;s=Arp.Plc.Eclr/LevelMinimum")
            ua_robot_test   = client.get_node("ns=5;s=Arp.Plc.Eclr/Robot.Test_Var")
            ua_BelpexElecPrices24 = client.get_node("ns=5;s=Arp.Plc.Eclr/BelpexElecPrices24")

            print(ua_LevelMaximum.get_value())
            print(ua_LevelMinimum.get_value())
            print(ua_robot_test.get_value())
            print(ua_BelpexElecPrices24.get_value())

            # make sure you are comparing the right datatypes!

            if int(ua_LevelMinimum.get_value()) == 300 :
                vLow = 500
                vHigh = 800
            else :
                vLow = 300
                vHigh = 500    

            # Definiton of variables, the OPC UA server doesn't 
            LevelMaximum = ua.DataValue(ua.Variant(vHigh,ua.VariantType.Int16))
            LevelMinimum = ua.DataValue(ua.Variant(vLow,ua.VariantType.Int16))

            LevelMaximum.ServerTimestamp = None
            LevelMaximum.SourceTimestamp = None

            LevelMinimum.ServerTimestamp = None
            LevelMinimum.SourceTimestamp = None


            ua_LevelMaximum.set_value(LevelMaximum)
            ua_LevelMinimum.set_value(LevelMinimum)

            #ua_BelpexElecPrices24 is an array of 24 real values
            #set the first value to 0.0 add 0.1 to the rest
            #this is just for testing purposes
            BelpexElecPrices24 = ua.DataValue(ua.Variant([0.0] + [0.1 * i for i in range(1, 24)], ua.VariantType.Float))
            BelpexElecPrices24.ServerTimestamp = None
            BelpexElecPrices24.SourceTimestamp = None
            ua_BelpexElecPrices24.set_value(BelpexElecPrices24)



            #embed()
            time.sleep(3) 
            #client.close_session()

            i += 1

    finally:
        client.disconnect()