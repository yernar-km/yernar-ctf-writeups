import re

text = open("memo.txt", encoding="utf-8").read()

zwsp = '\u200b'  # 0
zwnj = '\u200c'  # 1

bits = ''
for ch in text:
    if ch == zwsp:
        bits += '0'
    elif ch == zwnj:
        bits += '1'

flag = ''
for i in range(0, len(bits), 8):
    byte = bits[i:i+8]
    if len(byte) == 8:
        flag += chr(int(byte, 2))

print(flag)