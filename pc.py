import os
import time
import uuid
import socket
import threading
from random import randint
from easymodbus.modbusClient import ModbusClient
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse


# sudo apt-get install python3.6
#  pip3 install azure-iot-device
# pip 3 install easymodbus


def internet_on():
    try:
        socket.create_connection(('www.google.com',80))
        return True
    except OSError:
        pass
    return False


def main():
    # The connection string for a device should never be stored in code. For the sake of simplicity we're using an environment variable here.
    conn_str = "HostName=try.azure-devices.net;DeviceId=rasp1;SharedAccessKey=F7+kYcKd5p3j6TKymp4CxRpqD6GhBiClZKpuBrHJw3c="
    # The client object is used to interact with your Azure IoT hub.
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # Connect the client.
    device_client.connect()

    # Run method listener threads in the background
    method1_thread = threading.Thread(target=set_port_values, args=(device_client,))
    method1_thread.daemon = True
    method1_thread.start()

    connection_check_thread = threading.Thread(target=connection_check, args=(device_client,))
    connection_check_thread.daemon = True
    connection_check_thread.start()

    DSS_thread = threading.Thread(target=DSS, args=())
    DSS_thread.daemon = True
    DSS_thread.start()

    agDss_thread = threading.Thread(target=agDss, args=())
    agDss_thread.daemon = True
    agDss_thread.start()

    while True:
        selection = input("Press Q to quit\n")
        if selection == "Q" or selection == "q":
            print("Quitting...")
            break

    method1_thread.stop()
    agDss_thread.stop()
    DSS_thread.stop()
    connection_check_thread.stop()
    device_client.disconnect()


ls = [False,False,False,False]
output_status = [False,False,False,False]
x1,x2,x3,x4,x5,x6,x7,x8,x17,x18,x19 = 0,2,4,3,7,8,9,13,10,11,12
y1,y2,y3,y4,y5,y6,y7,y8 = 0,1,2,3,4,5,6,7
isInternetConnected =False
def connection_check(device_client):

    while(True):

        #CONNECT TO ModbusClients
        try:
            isInternetConnected = internet_on()
            modbusclient = ModbusClient("192.168.1.2",502)
            modbusclient.connect()
            isConnected = 1
        except Exception as ex:
            print('connection to PLC')
            print(ex)
            isConnected = 0



        #send connection status to server
        try:
            msg = Message("connection_status")
            msg.message_id = uuid.uuid4()
            msg.correlation_id = "correlation-1234"
            msg.custom_properties["connection_status"] = isConnected
            device_client.send_message(msg)
        except Exception as ex:
            print('send connection status to server')
            print(ex)
            isInternetConnected = False

        if(isConnected == 0):
            continue

        try:
            if(modbusclient.is_connected):
                input_discrete = modbusclient.read_discreteinputs(0,8)
                print('read_discreteinputs')
                msg = Message("read_discreteinputs")
                msg.message_id = uuid.uuid4()
                msg.correlation_id = "correlation-1234"
                for i in range(0,len(input_discrete)):
                    msg.custom_properties[str(i)] = input_discrete[i]
                device_client.send_message(msg)
                OnInputStatus(input_discrete)

            if(modbusclient.is_connected):
                input_coils = modbusclient.read_coils(0,15)
                print('read_coils')
                msg = Message("read_coils")
                msg.message_id = uuid.uuid4()
                msg.correlation_id = "correlation-1234"
                for i in range(0,len(input_coils)):
                    msg.custom_properties[str(i)] = input_coils[i]
                device_client.send_message(msg)
                OnOutputStatus(input_coils)

        except Exception as ex:
            print('read ReadDiscreteInputs 0-8')
            print(ex)
            isInternetConnected = False


        try:
            modbusclient.close()
        except Exception as ex:
            print('closing exception')
            print(ex)
            isInternetConnected = False


        time.sleep(0.5)

def DSS():
    dataOutput = {}
    dataOutput[x1]=False
    dataOutput[x2]=False
    dataOutput[x3]=False
    dataOutput[x4]=False
    dataOutput[x5]=False
    dataOutput[x6]=False
    dataOutput[x7]=False
    dataOutput[x19]=True
    send_to_plc(dataOutput)

    while (True):
        time.sleep(1)
        isInternetConnected = internet_on()
        print("Internet : " + str(isInternetConnected))
        if(isInternetConnected == True):
            continue

        if (ls[0] == False and ls[1] == False and ls[2] == False and ls[3] == False):
            dataOutput = {}
            dataOutput[x1]=False
            dataOutput[x2]=False
            dataOutput[x3]=False
            dataOutput[x4]=False
            dataOutput[x5]=False
            dataOutput[x6]=False
            dataOutput[x7]=True
            send_to_plc(dataOutput)

        if (ls[0] == False and ls[1] == False and ls[2] == False and ls[3] == True):
            dataOutput = {}
            dataOutput[x5]=False
            dataOutput[x6]=False
            dataOutput[x1]=True
            dataOutput[x2]=True
            dataOutput[x3]=True
            dataOutput[x4]=True
            dataOutput[x7]=True
            send_to_plc(dataOutput)

        if (ls[0] == False and ls[1] == False and ls[2] == True and ls[3] == True):
            dataOutput = {}
            dataOutput[x5]=False
            dataOutput[x6]=False
            dataOutput[x1]=True
            dataOutput[x2]=True
            dataOutput[x3]=True
            dataOutput[x4]=True
            dataOutput[x7]=True
            send_to_plc(dataOutput)
            while (ls[0] == False):
                time.sleep(1)

        if (ls[0] == False and ls[1] == True and ls[2] == False and ls[3] == False):
            dataOutput = {}
            dataOutput[x1]=False
            dataOutput[x2]=False
            dataOutput[x3]=False
            dataOutput[x4]=False
            dataOutput[x5]=False
            dataOutput[x6]=False
            dataOutput[x7]=True
            send_to_plc(dataOutput)

        if (ls[0] == False and ls[1] == True and ls[2] == False and ls[3] == True):
            dataOutput = {}
            dataOutput[x5]=False
            dataOutput[x6]=False
            dataOutput[x1]=True
            dataOutput[x2]=True
            dataOutput[x3]=True
            dataOutput[x4]=True
            dataOutput[x7]=True
            send_to_plc(dataOutput)

        if (ls[0] == True and ls[1] == True and ls[2] == True and ls[3] == True):
            dataOutput = {}
            dataOutput[x1]=False
            dataOutput[x2]=False
            dataOutput[x3]=False
            dataOutput[x4]=False
            dataOutput[x5]=True
            dataOutput[x6]=True
            dataOutput[x7]=False
            send_to_plc(dataOutput)

        if (ls[0] == False and ls[1] == True and ls[2] == True and ls[3] == True):
            dataOutput = {}
            dataOutput[x1]=False
            dataOutput[x2]=False
            dataOutput[x3]=False
            dataOutput[x4]=False
            dataOutput[x5]=True
            dataOutput[x6]=True
            dataOutput[x7]=False
            send_to_plc(dataOutput)

            while (ls[2] == True and ls[1] == True):
                time.sleep(1)

        if (ls[0] == True and ls[1] == True and ls[2] == False and ls[3] == False):
            dataOutput = {}

            dataOutput[x1]=False
            dataOutput[x2]=False
            dataOutput[x3]=False
            dataOutput[x4]=False
            dataOutput[x5]=False
            dataOutput[x6]=False
            dataOutput[x7]=True
            send_to_plc(dataOutput)

        if (ls[0] == True and ls[1] == True and ls[2] == False and ls[3] == True):
            dataOutput = {}
            dataOutput[x1]=False
            dataOutput[x2]=False
            dataOutput[x3]=False
            dataOutput[x4]=False
            dataOutput[x5]=False
            dataOutput[x6]=False
            dataOutput[x7]=True
            send_to_plc(dataOutput)

        if (ls[0] == True and ls[1] == False and ls[2] == False and ls[3] == False):
            dataOutput = {}
            dataOutput[x1]=False
            dataOutput[x2]=False
            dataOutput[x3]=False
            dataOutput[x4]=False
            dataOutput[x5]=False
            dataOutput[x6]=False
            dataOutput[x7]=True
            send_to_plc(dataOutput)


        if (ls[0] == True and ls[1] == False and ls[2] == False and ls[3] == True):
            dataOutput = {}
            dataOutput[x1]=False
            dataOutput[x2]=False
            dataOutput[x3]=False
            dataOutput[x4]=False
            dataOutput[x5]=False
            dataOutput[x6]=False
            dataOutput[x7]=True
            send_to_plc(dataOutput)

        if (ls[0] == False and ls[1] == False and ls[2] == True and ls[3] == False):
            dataOutput = {}
            dataOutput[x5]=False
            dataOutput[x6]=False
            dataOutput[x1]=True
            dataOutput[x2]=True
            dataOutput[x3]=True
            dataOutput[x4]=True
            dataOutput[x7]=True
            send_to_plc(dataOutput)


        if (ls[0] == False and ls[1] == True and ls[2] == True and ls[3] == False):
            dataOutput = {}
            dataOutput[x5]=False
            dataOutput[x6]=False
            dataOutput[x1]=True
            dataOutput[x2]=True
            dataOutput[x3]=True
            dataOutput[x4]=True
            dataOutput[x7]=True
            send_to_plc(dataOutput)


        if (ls[0] == True and ls[1] == False and ls[2] == True and ls[3] == False):
            dataOutput = {}
            dataOutput[x1]=False
            dataOutput[x2]=False
            dataOutput[x3]=False
            dataOutput[x4]=False
            dataOutput[x5]=True
            dataOutput[x6]=True
            dataOutput[x7]=False
            send_to_plc(dataOutput)

        if (ls[0] == True and ls[1] == False and ls[2] == True and ls[3] == True):
            dataOutput = {}
            dataOutput[x1]=False
            dataOutput[x2]=False
            dataOutput[x3]=False
            dataOutput[x4]=False
            dataOutput[x5]=True
            dataOutput[x6]=True
            dataOutput[x7]=False
            send_to_plc(dataOutput)

        if (ls[0] == True and ls[1] == True and ls[2] == True and ls[3] == False):
            dataOutput = {}
            dataOutput[x1]=False
            dataOutput[x2]=False
            dataOutput[x3]=False
            dataOutput[x4]=False
            dataOutput[x5]=True
            dataOutput[x6]=True
            dataOutput[x7]=False
            send_to_plc(dataOutput)


def agDss():
    dataOutput = {}
    dataOutput[x19]=True
    send_to_plc(dataOutput)

    while (True):
        isInternetConnected = internet_on()
        if(isInternetConnected == True):
            continue

        dataOutput = {}
        if (ls[2] ==True and ls[3] ==True):
            dataOutput[x19]=False
            dataOutput[x17]=True
            dataOutput[x18]=True

        if (ls[2] ==False and ls[3] ==False):
            dataOutput[x17]=False
            dataOutput[x18]=False
            dataOutput[x19]=True

        if (ls[2] ==False and ls[3] ==True):
            dataOutput[x17]=False
            dataOutput[x18]=False
            dataOutput[x19]=True

        send_to_plc(dataOutput)

def send_to_plc(dataOutput):
    try:
        modbusclient = ModbusClient("192.168.1.2",502)
        time.sleep(0.5)
        modbusclient.connect()
        for key,value in dataOutput.items():
            modbusclient.write_single_coil(int(key),value)
            time.sleep(0.01)
        modbusclient.close()
        print(dataOutput)
    except Exception as ex:
        print(ex)

def OnOutputStatus(outputstatus):
    if(outputstatus[x1] ==True or outputstatus[x2] == True):
        output_status[0] = True
    else:
        output_status[0] = False

    if(outputstatus[x3] ==True or outputstatus[x4] == True):
        output_status[1] = True
    else:
        output_status[1] = True

    if(outputstatus[x5] ==True or outputstatus[x6] == True):
        output_status[2] = True
    else:
        output_status[2] = False

    if(outputstatus[x17] ==True ):
        output_status[3] = True
    else:
        output_status[3] = False



def OnInputStatus(inputstatus):

    if(inputstatus[y1] ==True or inputstatus[y2] == True):
        ls[0] = True
    else:
        ls[0] = False

    if(inputstatus[y3] ==True or inputstatus[y4] == True):
        ls[1] = True
    else:
        ls[1] = False

    if(inputstatus[y5] ==True or inputstatus[y6] == True):
        ls[2] = True
    else:
        ls[2] = False

    if(inputstatus[y7] ==True or inputstatus[y8] == True):
        ls[3] = True
    else:
        ls[3] = False


# define behavior for handling methods
def set_port_values(device_client):
    while True:
        method_request = device_client.receive_method_request("SetTelemetryInterval")  # Wait for method1 calls

        payload = {"result": True,"data": "Received"}  # set response payload
        status = 200  # set return status code
        print("Received settings")
        method_response = MethodResponse.create_from_method_request(method_request, status, payload)
        device_client.send_method_response(method_response)  # send response

        try:
            modbusclient = ModbusClient("192.168.1.2",502)
            time.sleep(0.5)
            modbusclient.connect()
            print(method_request.payload)

            for key,value in method_request.payload.items():
                modbusclient.write_single_coil(int(key),str2bool(value))
                time.sleep(0.01)
            modbusclient.close()
        except Exception as ex:
            print(ex)


def str2bool(value):
    return value.lower() in ("true","yes")
isConnected=-1


if __name__ == '__main__':
    main()
