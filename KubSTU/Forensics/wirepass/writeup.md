
## Шаг 1: Смотрим что вообще есть в трафике

Открываем pcap (или парсим вручную через Python), смотрим протоколы:
- TCP на порту **21** (FTP) — куча логинов
- TCP на порту **31337** — что-то кастомное
- Куча шума: HTTP, HTTPS, UDP и т.д.

---

## Шаг 2: FTP — собираем креды

В FTP-трафике 10 сессий с разными юзерами. Большинство — обычные пароли типа `kr1ll_supp1y`, `f1sh_l0ver` и т.д. Но среди всех строк в pcap затесался нестандартный пакет:

```
PASS:IcyFl1pp3r$2026
```

Это не FTP-команда, а просто строка в одном из пакетов. Запоминаем — пригодится.

Также FTP показывает листинг файлов на сервере:
```
intel_dump.bin
coordinates.gpx
```

---

## Шаг 3: Кастомный протокол на порту 31337

Самый интересный стрим. Структура пакета:

```
[4 байта]  магик: "XFER"
[16 байт]  XOR-ключ
[4 байта]  длина payload (big-endian)
[N байт]   зашифрованный payload (XOR с ключом)
```

Расшифровываем XOR-ом:

```python
key = data[4:20]
length = struct.unpack('>I', data[20:24])[0]
encrypted = data[24:24+length]
decrypted = bytes([encrypted[i] ^ key[i % 16] for i in range(length)])
```

Получаем **ZIP-архив** с тремя файлами: `mission_report.txt`, `roster.txt`, `map.txt`.

---

## Шаг 4: Вскрываем ZIP

ZIP зашифрован AES-256 (compression method = 99, WinZip AES). Пробуем пароль из шага 2: **`IcyFl1pp3r$2026`** — подходит (проверяем через PBKDF2 + verifier).

Расшифровка:
- Derive keys: `PBKDF2-HMAC-SHA1(password, salt, 1000 iterations, dklen=66)`
  - `enc_key = derived[:32]`
  - `hmac_key = derived[32:64]`
- AES-256-CTR, counter **little-endian**, начинается с 1
- После расшифровки — deflate-сжатие (zlib, wbits=-15)

```python
# Keystream через AES-ECB блоками по 16 байт
for i in range(1, n_blocks+1):
    counters += struct.pack('<QQ', i, 0)  # little-endian 128-bit
# Шифруем AES-ECB → keystream → XOR с данными
```

---

## Шаг 5: Флаг

В `mission_report.txt` в поле «Секретный код операции»:

```
KubSTU{p1ngu1n_0p_k4p1b4r0v5k_f4ll5}
```

