# Nonce Rewind — Crypto Writeup

## Task Description
Nonce Rewind is a cryptographic challenge featuring the "TimeSign Gateway v2" service. The service allows signing any hex messages except for the blocked one: `give_me_flag` (hex: `676976655f6d655f666c6167`).

**Goal:** Recover the private key and forge a valid signature for the forbidden message.

* **Host:** `nonce-rewind.ctf.fr13nds.team`
* **Port:** `31337`
* **Curves:** NIST P-256 / SECP256k1

## Vulnerability Analysis
While analyzing the output of the `sign` command, the `trace` field and signature parameters (r, s) were observed. After collecting several signatures within a single session, it was discovered that the r value repeats for different messages.

This is a classic **Nonce Reuse attack**. If the r value is identical for two different signatures, it means the same ephemeral key (nonce) k was used for both.

## Mathematical Background
In ECDSA, the signature (r, s) is calculated as:
r = (k * G)_x mod n
s = k^-1 * (z + r * d) mod n

Where z is the message hash and d is the private key. If k is the same for two messages (z1, s1) and (z2, s2):
k = (z1 - z2) * (s1 - s2)^-1 mod n
d = (s1 * k - z1) * r^-1 mod n

## Exploitation Steps
1. **Curve Identification:** It was experimentally determined (by verifying the public key parameters) that the server uses the `secp256k1` curve.
2. **Collision Collection:** Signatures were collected for sequential messages (`01`, `02`, `03`...) until a duplicate r was encountered.
3. **Key Recovery:** Using the formulas above, the secret key d was calculated.
4. **Forge:** A valid signature for `give_me_flag` was generated using a custom k=1.

## Flag
> **`f13{3cd54_n0nc3_r3u53_t1m3_buck37}`**