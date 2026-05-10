

### Шаг 1 — Первичный осмотр

Первым делом смотрим на файл не глазами, а инструментами:

```bash
pdfinfo crypt.pdf
pdftotext crypt.pdf -
```

Текст читается нормально, метаданных нет, вложений нет, картинок нет. Но в самом тексте написано: *"This document contains hidden information"* — явная подсказка.

---

### Шаг 2 — Смотрим raw-структуру PDF

PDF — это текстовый формат. Открываем как обычный файл и читаем объекты:

```bash
strings crypt.pdf
# или просто cat crypt.pdf
```

Видим, что PDF содержит **два потока (stream)**:
- **Object 4** — обычный PDF-контент (текст страницы), открытый, читается сразу
- **Object 5** — заявлен как `/Filter /FlateDecode`, но внутри начинается с `<~` и заканчивается `~>`

Это сразу подозрительно — FlateDecode это zlib, а `<~...~>` это маркеры **ASCII85**.

---

### Шаг 3 — Двойное декодирование

Скрипт на Python:

```python
import re, base64, zlib

with open("crypt.pdf", "rb") as f:
    data = f.read()

# Вытаскиваем все потоки
streams = re.findall(b"stream\r?\n(.*?)\r?\nendstream", data, re.DOTALL)

# Второй поток — наш
raw = streams[1]

# Слой 1: ASCII85
a85_decoded = base64.a85decode(raw, adobe=True)

# Слой 2: zlib
result = zlib.decompress(a85_decoded)
print(result.decode())
```

---

### Шаг 4 — Разбор результата

Декомпрессированный поток содержит PDF-команды вида:

```
BT 1 0 0 1 50 100 Tm (K) Tj ET
BT 1 0 0 1 62 100 Tm (u) Tj ET
...
```

`Tm` — позиция, `Tj` — вывод символа. Собираем символы с **одинаковой Y-координатой (y=100)**:


**Флаг:** `KubSTU{pdf_0bj3ct_m4st3r_v2}`


