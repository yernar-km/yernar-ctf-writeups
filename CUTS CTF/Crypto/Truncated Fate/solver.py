import hashlib

m = 1 << 64
a = 6364136223846793005
x0 = 9979116872503376424
tops = [0x4dbde5aae889, 0x2b2432b3f2db, 0xfcf440f24540, 0xfbcad686ffe6, 0xcd56f6f37507, 0x71a7e648269b, 0xbb77d85f4759, 0x3ccb3f70538e]
cipher_hex = "8ffeb51f88269c7d571a165476a6ffcae38af32beb58013d97ce5f77c1f571aca5df9831"

found_c = None
for r0 in range(65536):
    y1 = (tops[0] << 16) | r0
    c = (y1 - a * x0) % m
    ok = True
    y = x0
    for i in range(8):
        y_next = (a * y + c) % m
        if (y_next >> 16) != tops[i]:
            ok = False
            break
        y = y_next
    if ok:
        found_c = c
        print(f"Found c = {c} (0x{c:016x})")
        y = x0
        for i in range(9):
            y = (a * y + c) % m
        x9 = y
        print(f"x9 = {x9} (0x{x9:016x})")
        break

if found_c is None:
    print("No solution found")
else:
    key = hashlib.sha256(x9.to_bytes(8, 'big')).digest()
    print(f"Key (hex): {key.hex()}")
    cipher = bytes.fromhex(cipher_hex)
    decrypted = bytes([cipher[i] ^ key[i % len(key)] for i in range(len(cipher))])
    print(f"Decrypted (hex): {decrypted.hex()}")
    print(f"Decrypted (ascii): {decrypted.decode('ascii', errors='replace')}")