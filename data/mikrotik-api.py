"""mikrotik-api.py — Connect to MikroTik RouterOS API (port 8728)."""
import socket
import hashlib
import binascii
import struct
import time

HOST = "192.168.4.2"
PORT = 8728
USER = "admin"
PASS = "FUHWERYEWRH"

def encode_length(length):
    if length < 0x80:
        return bytes([length])
    elif length < 0x4000:
        length |= 0x8000
        return struct.pack('>H', length)
    elif length < 0x200000:
        length |= 0xC00000
        return struct.pack('>I', length)[1:]
    elif length < 0x10000000:
        length |= 0xE0000000
        return struct.pack('>I', length)
    else:
        return b'\xF0' + struct.pack('>I', length)

def decode_length(sock):
    b = sock.recv(1)
    if not b:
        return 0
    b = b[0]
    if b < 0x80:
        return b
    elif b < 0xC0:
        b2 = sock.recv(1)[0]
        return ((b & 0x3F) << 8) | b2
    elif b < 0xE0:
        b2 = sock.recv(2)
        return ((b & 0x1F) << 16) | (b2[0] << 8) | b2[1]
    elif b < 0xF0:
        b2 = sock.recv(3)
        return ((b & 0x0F) << 24) | (b2[0] << 16) | (b2[1] << 8) | b2[2]
    else:
        b2 = sock.recv(4)
        return (b2[0] << 24) | (b2[1] << 16) | (b2[2] << 8) | b2[3]

def send_word(sock, word):
    encoded = word.encode('utf-8')
    sock.send(encode_length(len(encoded)) + encoded)

def send_sentence(sock, words):
    for w in words:
        send_word(sock, w)
    sock.send(b'\x00')  # end of sentence

def read_sentence(sock):
    words = []
    while True:
        length = decode_length(sock)
        if length == 0:
            break
        word = sock.recv(length).decode('utf-8', errors='replace')
        words.append(word)
    return words

print("=" * 70)
print(f"  MIKROTIK API — {HOST}:{PORT}")
print("=" * 70)

try:
    sock = socket.create_connection((HOST, PORT), timeout=5)
    sock.settimeout(5)
    print("  Connected!")
    
    # Login (RouterOS 6.43+)
    print("\n--- Login ---")
    send_sentence(sock, ['/login', f'=name={USER}', f'=password={PASS}'])
    response = read_sentence(sock)
    print(f"  Response: {response}")
    
    if response and response[0] == '!done':
        print("  *** LOGIN SUCCESS! ***")
        
        # Get system identity
        print("\n--- System Identity ---")
        send_sentence(sock, ['/system/identity/print'])
        r = read_sentence(sock)
        print(f"  {r}")
        # Read !done
        if r and r[0] != '!done':
            r2 = read_sentence(sock)
        
        # Get interfaces
        print("\n--- Interfaces ---")
        send_sentence(sock, ['/interface/print'])
        while True:
            r = read_sentence(sock)
            if not r or r[0] == '!done':
                break
            print(f"  {r}")
        
        # Get ARP table (see ALL devices!)
        print("\n--- ARP Table (ALL devices on L2) ---")
        send_sentence(sock, ['/ip/arp/print'])
        while True:
            r = read_sentence(sock)
            if not r or r[0] == '!done':
                break
            print(f"  {r}")
        
        # Get bridge hosts (MAC table — which port each device is on!)
        print("\n--- Bridge Host Table (MAC → Port mapping) ---")
        send_sentence(sock, ['/interface/bridge/host/print'])
        while True:
            r = read_sentence(sock)
            if not r or r[0] == '!done':
                break
            print(f"  {r}")
        
        # Get IP addresses
        print("\n--- IP Addresses ---")
        send_sentence(sock, ['/ip/address/print'])
        while True:
            r = read_sentence(sock)
            if not r or r[0] == '!done':
                break
            print(f"  {r}")
        
        # Get routes
        print("\n--- Routes ---")
        send_sentence(sock, ['/ip/route/print'])
        while True:
            r = read_sentence(sock)
            if not r or r[0] == '!done':
                break
            print(f"  {r}")
        
        # System resources
        print("\n--- System Resources ---")
        send_sentence(sock, ['/system/resource/print'])
        r = read_sentence(sock)
        print(f"  {r}")
        if r and r[0] != '!done':
            read_sentence(sock)
        
    elif response and '!trap' in response[0]:
        print(f"  LOGIN FAILED: {response}")
        
        # Try challenge-response login (older RouterOS)
        print("\n--- Trying challenge-response login ---")
        send_sentence(sock, ['/login'])
        r = read_sentence(sock)
        print(f"  Challenge: {r}")
        if r:
            for item in r:
                if item.startswith('=ret='):
                    challenge = binascii.unhexlify(item[5:])
                    md = hashlib.md5()
                    md.update(b'\x00')
                    md.update(PASS.encode('utf-8'))
                    md.update(challenge)
                    response_hash = '00' + md.hexdigest()
                    send_sentence(sock, ['/login', f'=name={USER}', f'=response={response_hash}'])
                    r2 = read_sentence(sock)
                    print(f"  Auth response: {r2}")
    else:
        print(f"  Unexpected: {response}")
    
    sock.close()

except Exception as e:
    print(f"  Error: {e}")
