# Unknown-Arch---reverse-CTF


## Challenge Info
- **Category:** Reverse Engineering
- **Difficulty:** Hard
- **Points:** 500

## Description
> Our agents intercepted this strange authentication module from a hacker group's closed network. It appears they've stopped trusting standard processors and written their own custom architecture.

## Solution

### 1. Initial Analysis
```bash
$ file "Unknown Arch.exe"
PE32+ executable (console) x86-64, for MS Windows

$ strings "Unknown Arch.exe" | grep -i "password\|granted\|denied"
Enter password:
Access Denied.
Access Granted! Flag found.
```

### 2. Finding Password Length

Использовали брутфорс длины:
```bash
for i in {1..40}; do
  echo "Testing length $i"
  result=$(printf 'a%.0s' $(seq 1 $i) | wine "Unknown Arch.exe" 2>/dev/null)
  echo "$result"
  if [[ ! "$result" =~ "Wrong length" ]]; then
    echo "Found length: $i"
    break
  fi
done
```

Результат:
```
...
Testing length 32
Enter password: Access Denied.
Found length: 32
```

Password must be **32 characters**.

### 3. Reverse Engineering with Ghidra

Открыли файл в Ghidra и нашли функцию `main.main`:

1. **Search → For Strings → "Access Granted"**
2. Перешли по ссылке к функции `main.main`
3. Обнаружили вызов `main.(*VM).Run` — кастомная виртуальная машина

Ключевой код в `main.main`:
```c
cVar2 = main.(*VM).Run(local_508);
if (cVar2 == '\0') {
    // Access Denied
} else {
    // Access Granted! Flag found.
}
```

### 4. Analyzing VM.Run Function

В функции `main.(*VM).Run` нашли проверку пароля:
```c
if (bVar1 == 0xff) {  // Опкод CHECK
    for (uVar5 = 0; uVar5 < 0x20; uVar5++) {
        if (*(dword *)(PTR_DAT_140179840 + uVar5 * 4) != 
            *(dword *)((int)self + uVar5 * 4 + 0x10)) {
            return 0;  // FAIL
        }
    }
    return 1;  // SUCCESS
}
```

Это сравнивает обработанный пароль с целевым массивом по адресу `PTR_DAT_140179840`.

### 5. Finding Target Array

В Ghidra перешли по адресу `PTR_DAT_140179840`:
```
PTR_DAT_140179840 → DAT_140174a40
```

Первое значение в Ghidra: `883CCBE0h`

Нашли полный массив через xxd:
```bash
$ xxd "Unknown Arch.exe" | grep "e0cb 3c88"
00173440: e0cb 3c88 f592 57e4 4f2a ea2d 95a0 0a0a  ..<...W.O*.-....
```

Извлекли 128 байт (32 × 4):
```bash
$ python3 -c "
data = open('Unknown Arch.exe', 'rb').read()
target = bytes([0xe0, 0xcb, 0x3c, 0x88])
idx = data.find(target)
print(f'Offset: {hex(idx)}')
print(data[idx:idx+128].hex())
"

Offset: 0x173440
e0cb3c88f59257e44f2aea2d95a00a0a9337f5f76b358cc1...
```

### 6. Finding VM Bytecode

Нашли байткод по сигнатуре `1b 00 00 00 00 00 1b 01`:
```bash
$ python3 -c "
data = open('Unknown Arch.exe', 'rb').read()
sig = bytes([0x1b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1b, 0x01])
idx = data.find(sig)
print(f'Bytecode at: {hex(idx)}')
for i in range(0, 87, 16):
    print(' '.join(f'{b:02x}' for b in data[idx+i:idx+i+16]))
"

Bytecode at: 0x1732e0
1b 00 00 00 00 00 1b 01 ef be ad de 1b 03 20 00
00 00 3f 03 00 75 03 03 00 74 39 00 2c 02 00 51
01 02 1b 03 ef be 37 13 40 01 03 1b 03 78 56 34
12 3e 01 03 1a 02 01 62 02 05 1a 03 01 63 03 1b
3e 02 03 1a 01 02 2d 00 01 1b 03 01 00 00 00 3e
00 03 74 b7 ff ff 00
```

### 7. Disassembling VM Bytecode

Разобрали опкоды:

| Offset | Bytes | Instruction |
|--------|-------|-------------|
| 0x00 | `1b 00 00000000` | MOV r0, 0 (counter) |
| 0x06 | `1b 01 DEADBEEF` | MOV r1, 0xDEADBEEF |
| 0x0c | `1b 03 00000020` | MOV r3, 32 |
| 0x12 | `3f 03 00` | SUB r3, r0 |
| 0x15 | `75 03 0300` | JNZ r3, +3 |
| 0x19 | `74 3900` | JMP to CHECK |
| 0x1c | `2c 02 00` | LOAD r2, [r0] (load char) |
| 0x1f | `51 01 02` | XOR r1, r2 |
| 0x22 | `1b 03 1337BEEF` | MOV r3, 0x1337BEEF |
| 0x28 | `40 01 03` | MUL r1, r3 |
| 0x2b | `1b 03 12345678` | MOV r3, 0x12345678 |
| 0x31 | `3e 01 03` | ADD r1, r3 |
| 0x34 | `1a 02 01` | MOV r2, r1 |
| 0x37 | `62 02 05` | SHL r2, 5 |
| 0x3a | `1a 03 01` | MOV r3, r1 |
| 0x3d | `63 03 1b` | SHR r3, 27 |
| 0x40 | `3e 02 03` | ADD r2, r3 (= ROL r1, 5) |
| 0x43 | `1a 01 02` | MOV r1, r2 |
| 0x46 | `2d 00 01` | STORE [r0], r1 |
| 0x49 | `1b 03 00000001` | MOV r3, 1 |
| 0x4f | `3e 00 03` | ADD r0, r3 (counter++) |
| 0x52 | `74 FFB7` | JMP -73 (loop) |
| 0x55 | `ff` | CHECK |

### 8. Encryption Algorithm

Для каждого символа пароля:
```
r1 = r1 ^ password[i]      // XOR с предыдущим r1
r1 = r1 * 0x1337BEEF       // умножение
r1 = r1 + 0x12345678       // сложение
r1 = ROL(r1, 5)            // rotate left 5 bits
result[i] = r1
```

**Важно:** `r1` начинается как `0xDEADBEEF` и переносится между итерациями!

### 9. Solve Script
```python
import struct

# Target array extracted from binary
target_hex = "e0cb3c88f59257e44f2aea2d95a00a0a9337f5f76b358cc100fc3675f7601e76e069220460f4116738e9e3b8b78d3737d652b59e7a90be2851f126014f6bb25dd0e6f23221ff16fa3d5609fc1965690549daba99ecf56b5b411f7d6755cd5241e0c8eafa701468f9bcc6454b15662bdb8387a1cd9479ecd2c85bf846794ea960"
target = struct.unpack('<32I', bytes.fromhex(target_hex))

# Modular multiplicative inverse
def modinv(a, m=2**32):
    def egcd(a, b):
        if a == 0: return b, 0, 1
        g, x, y = egcd(b % a, a)
        return g, y - (b // a) * x, x
    return (egcd(a % m, m)[1] % m + m) % m

def ror(v, n): return ((v >> n) | (v << (32 - n))) & 0xFFFFFFFF
def rol(v, n): return ((v << n) | (v >> (32 - n))) & 0xFFFFFFFF

# Constants from bytecode
XOR_CONST = 0xDEADBEEF
MUL_CONST = 0x1337BEEF
ADD_CONST = 0x12345678
mul_inv = modinv(MUL_CONST)

# Reverse the algorithm
r1 = XOR_CONST
password = ""

for t in target:
    # Reverse operations
    val = ror(t, 5)                        # reverse ROL
    val = (val - ADD_CONST) & 0xFFFFFFFF   # reverse ADD
    val = (val * mul_inv) & 0xFFFFFFFF     # reverse MUL
    
    # val = r1 ^ char, so char = val ^ r1
    char = val ^ r1
    password += chr(char)
    
    # Update r1 for next iteration (forward algorithm)
    r1 = val
    r1 = (r1 * MUL_CONST) & 0xFFFFFFFF
    r1 = (r1 + ADD_CONST) & 0xFFFFFFFF
    r1 = rol(r1, 5)

print(f"Password: {password}")
```

### 10. Result
```bash
$ python3 solve.py
Password: f13{insane_custom_vm_protection}

$ echo "f13{insane_custom_vm_protection}" | wine "Unknown Arch.exe"
Enter password: Access Granted! Flag found.
```

## Flag
```
picoCTF{insane_custom_vm_protection}
```

## Tools Used
- **Ghidra** — дизассемблер и декомпилятор
- **Python** — написание декодера
- **Wine** — запуск Windows exe в Linux
- **xxd** — просмотр hex-данных
- **strings** — поиск строк в бинарнике

## Key Techniques
1. **Custom VM Reverse Engineering** — полный разбор кастомной виртуальной машины
2. **Bytecode Disassembly** — ручной разбор байткода
3. **Modular Arithmetic** — вычисление мультипликативного обратного по модулю 2³²
4. **State Tracking** — отслеживание состояния r1 между итерациями
5. **Bit Operations** — ROL/ROR операции
