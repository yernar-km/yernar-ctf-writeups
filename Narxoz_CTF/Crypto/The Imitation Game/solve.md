# The Imitation Game — Crypto Writeup

## Task Description
The Imitation Game is a cryptography challenge involving an intercepted message encrypted with an Enigma M3 machine. While some parameters are known, the rotors, reflector, and starting positions remain a mystery. A key hint mentions that due to the lack of numbers on the Enigma keyboard, the standard flag format (Hex/MD5) was adapted using a letter-to-number mapping

* **Machine:** Enigma M3 (3 rotors)
* **Available Rotors:** I, II, III, IV, V
* **Available Reflectors:** B or C
* **Ringstellung (Ring Settings):** `1 1 1` (`A A A`)
* **Steckerbrett (Plugboard):** `AV BS CG DL FU`
* **Ciphertext:** `YSTRPNGEHUBDLMQSSXYESYXBRTLIEIMHCWDZUI`

## Vulnerability Analysis
The challenge requires a brute-force approach against the unknown internal settings. The keyspace is calculated as follows:

* **Rotor Selection & Order:** Choosing 3 rotors from 5: $A_5^3 = 5 \times 4 \times 3 = 60$ combinations
* **Reflector:** 2 options (B or C) = 2 combinations
* **Starting Positions:** 3 letters ($26^3$) = 17,576 combinations
* **Total Combinations:** $60 \times 2 \times 17,576 = 2,109,120$

This is a manageable number for modern hardware. By using a **Known Plaintext Attack (KPA)**—assuming the message starts with the competition prefix `CYCNET`—the correct configuration can be identified quickly

## Exploitation Steps
1. **Brute-force Scripting:** A Python script was developed using the `py-enigma` library to iterate through all ~2.1 million possible configurations
2. **Optimization:** To increase speed, the script only decrypts the first 6 characters of the ciphertext. If they match `CYCNET`, the full string is processed
3. **Configuration Recovery:** The script successfully identified the following settings:
   * **Rotors:** IV, II, V
   * **Reflector:** C
   * **Starting Position:** AFK
4. **Decryption:** Using these settings, the ciphertext decrypted to: `CYCNETECDCEMBFGBFNNOOFGOBGFBLGPCDLNGMP`

## Post-Processing
The decrypted body of the flag is `ECDCEMBFGBFNNOOFGOBGFBLGPCDLNGMP`. Following the hint about the lack of numbers, a substitution cipher was applied where letters G through P represent digits 0 through 9:

| Letter | G | H | I | J | K | L | M | N | O | P |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Digit** | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |

Applying the mapping:
* `ECDCEM` $\rightarrow$ `ecdce6`
* `BFG` $\rightarrow$ `bf0`
* `BFN` $\rightarrow$ `bf7`
* `NOO` $\rightarrow$ `788`
*(...and so on)*

The resulting Hex string is: `ecdce6bf0bf7788f08b0fb509cd57069`

## Flag
> **`cycnet{ecdce6bf0bf7788f08b0fb509cd57069}`**