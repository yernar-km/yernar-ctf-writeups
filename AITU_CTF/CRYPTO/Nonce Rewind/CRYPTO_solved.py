from pwn import *
from hashlib import sha256
from ecdsa import SECP256k1

curve = SECP256k1
n = curve.order
G = curve.generator


def solve():
    host, port = 'nonce-rewind.ctf.fr13nds.team', 31337

    try:
        io = remote(host, port)
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return

    sigs = {}
    print("[*] Searching for r-collision (Nonce Reuse attack)...")

    for i in range(1, 101):
        msg_hex = f"{i:02x}"

        try:
            io.sendlineafter(b"tsg> ", f"sign {msg_hex}".encode())
            io.recvuntil(b"r = ")
            r = int(io.recvline().strip(), 16)
            io.recvuntil(b"s = ")
            s = int(io.recvline().strip(), 16)
        except EOFError:
            print("[-] Server closed connection early.")
            break

        z = int(sha256(bytes.fromhex(msg_hex)).hexdigest(), 16)

        if r in sigs:
            print(f"\n[+] FOUND COLLISION at message '{msg_hex}'! r = {hex(r)}")
            z_old, s_old = sigs[r]
            k = ((z_old - z) * pow(s_old - s, -1, n)) % n
            d = ((s * k - z) * pow(r, -1, n)) % n

            print(f"[!] Private Key Recovered: {hex(d)}")

            target_msg_hex = "676976655f6d655f666c6167"
            z_target = int(sha256(bytes.fromhex(target_msg_hex)).hexdigest(), 16)

            my_k = 1
            r_final = G.x()
            s_final = (pow(my_k, -1, n) * (z_target + r_final * d)) % n

            exploit_cmd = f"verify {target_msg_hex} {hex(r_final)[2:]} {hex(s_final)[2:]}"
            print(f"[*] Sending exploit: {exploit_cmd[:60]}...")
            io.sendlineafter(b"tsg> ", exploit_cmd.encode())

            print("\n[!] res:")
            response = io.recvrepeat(2).decode()
            print(response)

            if "f13{" in response:
                print("give this: ")
            return

        sigs[r] = (z, s)
        if i % 5 == 0:
            print(f"[*] Collected {i} signatures...")

    io.close()


if __name__ == "__main__":
    solve()