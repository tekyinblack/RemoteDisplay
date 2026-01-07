# This code is intended to run on an ESP-01 / ESP8266 / ESP32 loaded with Micropython
# The purpose is to receive illumination information from another Espressif controller
# over ESP-NOW and use that to control a WS2812b RGB LED string
#
# Information to build the complete unit is published on the instructables website here
# https://www.instructables.com/Remote-WS2812b-LED-Display-for-Control-Over-ESP-NO/
from machine import Pin
import neopixel
import time
import gc

test = False

# setup WS2812b
string_pin_number = 12
no_of_strings = 2
pixel_per_string = 12
np = neopixel.NeoPixel(Pin(string_pin_number), pixel_per_string * no_of_strings)
# --- Memory Info ---
if test:
    print("\n[MEMORY]")
    print(f"Heap Allocated:     {gc.mem_alloc()} bytes")
    print(f"Heap Free:          {gc.mem_free()} bytes")
# initialise list of lists to hold LED illumination data
display = [[[0,0,0]],[[0,0,0]]]
for j in range(no_of_strings):
    for i in range(pixel_per_string - 1):
        display[j].append([0,0,0])
        
import network
import espnow
# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.WLAN.IF_STA)
sta.active(True)
sta.disconnect() # Because ESP8266 auto-connects to last Access Point
e = espnow.ESPNow()
e.active(True)



# routine to transfer data to pixel string
def write_string(disp):
    global no_of_strings
    if disp > no_of_strings-1 or disp < 0:
        return
    for i in range(pixel_per_string):
        #print ((display[j][i]),i+j*12)
        np[i+disp*pixel_per_string] = (display[disp][i])
    np.write()

# routine to write all pixel strings
def write_all():
    global no_of_strings
    for j in range(no_of_strings):
        write_string(j)
    
    
# this routine only writes updates clearing the string, stored data retained
# it may not be necessary
def blank_string(disp):
    global no_of_strings
    if disp > no_of_strings-1 or disp < 0:
        return

    for i in range(pixel_per_string):
        if test:
            print ((display[j][i]),i+j*12)
        np[i+disp*pixel_per_string] = (0,0,0)
    np.write()

def blank_all():
    global no_of_strings
    for j in range(no_of_strings):
        blank_string(j)
    
# this routine clears stored data for a string and clears the string
# it may not be necessary
def clear_string(disp):
    global no_of_strings
    if disp > no_of_strings-1 or disp < 0:
        return
    for i in range(pixel_per_string):
        #print ((display[j][i]),i+j*12)
        display[disp][i] = [0,0,0]
        np[i+disp*pixel_per_string] = (0,0,0)
    np.write()
    
def clear_all():
    global no_of_strings
    for j in range(no_of_strings):
        clear_string(j)

# test routine turns on all LEDs in string, one colour at a time and then white
def test_string(disp):
    global no_of_strings
    if disp > no_of_strings-1 or disp < 0:
        return
    for i in range(pixel_per_string):
        #print ((display[j][i]),i+j*12)
        np[i+disp*pixel_per_string] = (180,0,0)
    np.write()
    time.sleep(2)
    for i in range(pixel_per_string):
        #print ((display[j][i]),i+j*12)
        np[i+disp*pixel_per_string] = (0,180,0)
    np.write()
    time.sleep(2)
    for i in range(pixel_per_string):
        #print ((display[j][i]),i+j*12)
        np[i+disp*pixel_per_string] = (0,0,180)
    np.write()
    time.sleep(2)
    for i in range(pixel_per_string):
        #print ((display[j][i]),i+j*12)
        np[i+disp*pixel_per_string] = (120,120,120)
    np.write()
    time.sleep(2)
    for i in range(pixel_per_string):
        #print ((display[j][i]),i+j*12)
        np[i+disp*pixel_per_string] = (0,0,0)
    np.write()
    
    
    
while True:
    host, msg = e.recv()
    if msg: # msg == None if timeout in recv()
        if test:
            print(host, msg)
        message_length = len(msg)
        if test:
            print(message_length)
            for i in range(message_length):
                print(int(msg[i]))
        if msg == b'end':
            np[0] = (0,0,0)
            np.write()
            break
        elif message_length == 37: # display array assumed
            j = int(msg[0])
            if j >= 0 and j < no_of_strings:
                for i in range(pixel_per_string):
                    display[j][i] = [int(msg[i*3+1]),int(msg[i*3+2]),int(msg[i*3+3])]
            if test:
                print(display)

        elif msg.find(b'blank') >= 0 : # search for 'blank'
            if message_length == 5:
                if test:
                    print("blank displays")
                blank_all()
            else:
                blank_string(int(msg[5]))
            
        elif msg.find(b'write') >= 0:  # search for 'write'
            if message_length == 5:
                if test:
                    print("write displays")
                write_all()
            else:
                write_string(int(msg[5]))
            
        elif msg.find(b'clear') >= 0:   # search for 'clear'
            if message_length == 5:
                if test:
                    print("clear displays")
                clear_all()
            else:
                clear_string(int(msg[5]))
        else:
            if test:
                print(" message not understood")
            pass
            
        


clear_all()
# --- Memory Info ---
if test:
    print("\n[MEMORY]")
    print(f"Heap Allocated:     {gc.mem_alloc()} bytes")
    print(f"Heap Free:          {gc.mem_free()} bytes")
