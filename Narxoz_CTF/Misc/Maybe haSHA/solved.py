import hashlib
import string
with open("misc1.txt") as f:
    hashes = [line.strip() for line in f]

lookup = {}
for ch in string.printable:  
    h = hashlib.sha256(ch.encode()).hexdigest()
    lookup[h] = ch
flag = "".join(lookup[h] for h in hashes)

print(flag)