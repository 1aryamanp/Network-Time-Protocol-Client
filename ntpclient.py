#!/usr/bin/env python

'''
CS352 Assignment 1: Network Time Protocol
Aryaman Patel [ARP236]
Heta Shah [hks56]
You can work with 1 other CS352 student
DO NOT CHANGE ANY OF THE FUNCTION SIGNATURES BELOW
'''
from socket import socket, AF_INET, SOCK_DGRAM
import struct
from datetime import datetime

NTPtoUNIX = 2208988800  # Offset to convert NTP time to UNIX time

def getNTPTimeValue(server="time.apple.com", port=123) -> (bytes, float, float):
    '''
    This function tests if you can communicate to a remote NTP server, as well as get the
    local time needed to set the clock. This test will call your function and make sure the time values
    in the packet are close to ones sent by the tester code. Return T1 and T2 as Unix time using
    Python floating point numbers.
    '''
    client = socket(AF_INET, SOCK_DGRAM)

    client.settimeout(5)
    
    # make an NTP packet
    pkt = bytearray(48)
    pkt[0] = 0x1B
    
    # take a timestamp, T1 = current_time
    T1 = datetime.utcnow().timestamp()
    
    # send packet to the server, port address
    client.sendto(pkt, (server, port))
    
    # receive the response packet
    pkt, addr = client.recvfrom(48)
    
    # take a timestamp, T4 = current_time
    T4 = datetime.utcnow().timestamp()
    
    client.close()
    
    return (pkt, T1, T4)

def ntpPktToRTTandOffset(pkt: bytes, T1: float, T4: float) -> (float, float):
    '''
    This function takes a completed NTP data packet, as Python bytes, and input Unix
    timestamps, as floating point numbers, and returns the Round Trip Time (RTT) and offset as a
    Python two-tuple, with the first element being the round-trip time and the second element being
    the offset. Both are floating point numbers in seconds.
    '''
    T2_int = struct.unpack('!I', pkt[32:36])[0] - NTPtoUNIX
    T2_frac = struct.unpack('!I', pkt[36:40])[0] / (2**32)
    T2 = T2_int + T2_frac  # Extract T2 # Combine integer and fraction parts
    
    T3_int = struct.unpack('!I', pkt[40:44])[0] - NTPtoUNIX
    T3_frac = struct.unpack('!I', pkt[44:48])[0] / (2**32)
    T3 = T3_int + T3_frac  # Extract T3  # Combine integer and fraction parts
    
    # compute the RTT by: (T4-T1) - (T3-T2)
    rtt = (T4 - T1) - (T3 - T2)
    
    # compute the offset by: ((T2-T1) + (T3-T4))/2
    offset = ((T2 - T1) + (T3 - T4)) / 2
    
    return (rtt, offset)

def getCurrentTime(server="time.apple.com", port=123, iters=20) -> float:
    '''
    This function combines the previous 2; communicating with the remote server, parsing a
    packet, and computing the current time. The function must return the current time, computed
    with an average of offset values.
    '''
    offsets = []

    for _ in range(iters):
        # call (pkt, T1, T4) = getNTPTimeValue(server, port)
        pkt, T1, T4 = getNTPTimeValue(server, port)
        
        # call (RTT, offset) = ntpPktToRTTandOffset(pkt, T1, T4)
        RTT, offset = ntpPktToRTTandOffset(pkt, T1, T4)
        
        # append offset to offsets
        offsets.append(offset)

    # currentTime = average of offsets + current time with microsecond granularity
    avg_offset = sum(offsets) / len(offsets)
    currentTime = datetime.utcnow().timestamp() + avg_offset

    # return currentTime in Unix time as a Python float
    return currentTime

if __name__ == "__main__":
    print(getCurrentTime())