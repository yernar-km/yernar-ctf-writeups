import struct

target_hex = "e0cb3c88f59257e44f2aea2d95a00a0a9337f5f76b358cc100fc3675f7601e76e069220460f4116738e9e3b8b78d3737d652b59e7a90be2851f126014f6bb25dd0e6f23221ff16fa3d5609fc1965690549daba99ecf56b5b411f7d6755cd5241e0c8eafa701468f9bcc6454b15662bdb8387a1cd9479ecd2c85bf846794ea960"
target_bytes = bytes.fromhex(target_hex)
target = struct.unpack('<32I', target_bytes)

def modinv(a, m=2**32):
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def ror(val, n, bits=32):
    return ((val >> n) | (val << (bits - n))) & ((1 << bits) - 1)

def rol(val, n, bits=32):
    return ((val << n) | (val >> (bits - n))) & ((1 << bits) - 1)

mul_const = 0x1337BEEF
add_const = 0x12345678
xor_const = 0xDEADBEEF
mul_inv = modinv(mul_const)

def forward(password_chars):
    r1 = xor_const
    results = []
    for c in password_chars:
        r1 = r1 ^ c
        r1 = (r1 * mul_const) & 0xFFFFFFFF
        r1 = (r1 + add_const) & 0xFFFFFFFF
        r1 = rol(r1, 5)
        results.append(r1)
    return results

def backward(targets):
    password = []
    r1 = xor_const
    for t in targets:
        val = ror(t, 5)
        val = (val - add_const) & 0xFFFFFFFF
        val = (val * mul_inv) & 0xFFFFFFFF
        char = val ^ r1
        password.append(char)
        r1 = val
        r1 = (r1 * mul_const) & 0xFFFFFFFF
        r1 = (r1 + add_const) & 0xFFFFFFFF
        r1 = rol(r1, 5)
    return password

chars = backward(target)
password = ""
for c in chars:
    if 0x20 <= c <= 0x7e:
        password += chr(c)
    else:
        password += f"[{c:02x}]"

print(f"Password: {password}")

test = forward([ord(c) for c in password if c.isprintable() and len(c) == 1])
print(f"Verification match: {test == list(target)}")
