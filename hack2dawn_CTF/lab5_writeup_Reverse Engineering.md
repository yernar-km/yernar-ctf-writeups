#  Ядро de4thPawn (Reverse Engineering)

**CTF:** Hack2Dawn 2026  
**Организатор:** PawnGuard  
**Категория:** Reverse Engineering  
**Сложность:** Medium  
**Захвачено флагов:** 2/2  
**Очки:** 90 + 120 = 210 pts  

---

##  История задания

> В ходе анализа сервера C2 нам удалось проникнуть в защищённую среду и извлечь подозрительный бинарник `de4thpawn_auth`. По поведению — это внутренний модуль проверки идентификации группы de4thPawn. Задача: сделать реверс-инжиниринг и извлечь скрытую информацию.

Лаб разворачивается в Docker-контейнере с доступом по SSH:

```bash
docker compose up -d
ssh informante@localhost -p 2225
# пароль: pawnguard
```

---

## парт 1 Запуск бинарника (90 pts)


После подключения к среде находим два файла в домашней директории:

```bash
informante@85ed3b93c36f:~$ ls ~
de4thpawn_auth  extractor_c
```

Запускаем бинарник напрямую:

```bash
informante@85ed3b93c36f:~$ ./de4thpawn_auth
```

```
[*] Booting de4thPawn Identity Module...
[*] Module loaded: PWG{STR1NGS_4R3_N0T_3N0UGH}
[de4thPawn] Authentication required.
Enter access code:
[!] ACCESS DENIED. Intrusion logged.
```

### Флаг

```
PWG{STR1NGS_4R3_N0T_3N0UGH}
```

---

## парт 2 Реверс-инжиниринг 

> Бинарник запрашивает код доступа. Используй `extractor_c` для дизассемблирования. Каждая программа на C начинается с функции `main` c этого надо начинать

### Шаг 1: Анализ функции main

Инструмент `extractor_c` — это обёртка над radare2. Правильный синтаксис:

```bash
./extractor_c de4thpawn_auth main
```

В выводе `main` находим ключевой вызов:

```
sym.validate_access_code()
```

Программа читает ввод через `fgets`, убирает перенос строки через `strcspn`, затем вызывает `validate_access_code`. Если функция возвращает истину → доступ разрешён.

### Шаг 2: Анализ функции validate_access_code

```bash
./extractor_c de4thpawn_auth validate_access_code
```

Вывод показывает серию побайтовых сравнений. Извлекаем логику:

```
strlen(input) == 0xd        // длина = 13 символов

s[0]  == 0x64               // прямое сравнение
s[1]  == 0x33
s[2]  == 0x34
s[0] ^ s[3] == 0x10         // XOR: s[3] = 0x64 ^ 0x10
s[4]  == 0x68
s[5]  == 0x70
s[6]  == 0x61
s[7]  == 0x77
s[8]  == 0x6e
s[9]  == 0x5f
s[10] == 0x63
s[10] ^ s[11] == 0x51       // XOR: s[11] = 0x63 ^ 0x51
s[12] == 0x21
```

### Шаг 3: Решаем математику

Вычисляем каждый байт с помощью таблицы ASCII и операций XOR:

| Позиция | Операция | Hex | Символ |
|---------|----------|-----|--------|
| s[0]  | == 0x64 | 0x64 | `d` |
| s[1]  | == 0x33 | 0x33 | `3` |
| s[2]  | == 0x34 | 0x34 | `4` |
| s[3]  | 0x64 XOR 0x10 | 0x74 | `t` |
| s[4]  | == 0x68 | 0x68 | `h` |
| s[5]  | == 0x70 | 0x70 | `p` |
| s[6]  | == 0x61 | 0x61 | `a` |
| s[7]  | == 0x77 | 0x77 | `w` |
| s[8]  | == 0x6e | 0x6e | `n` |
| s[9]  | == 0x5f | 0x5f | `_` |
| s[10] | == 0x63 | 0x63 | `c` |
| s[11] | 0x63 XOR 0x51 | 0x32 | `2` |
| s[12] | == 0x21 | 0x21 | `!` |

Скрипт для проверки:

```python
password = [0] * 13
password[0]  = 0x64
password[1]  = 0x33
password[2]  = 0x34
password[3]  = password[0] ^ 0x10   # XOR
password[4]  = 0x68
password[5]  = 0x70
password[6]  = 0x61
password[7]  = 0x77
password[8]  = 0x6e
password[9]  = 0x5f
password[10] = 0x63
password[11] = password[10] ^ 0x51  # XOR
password[12] = 0x21

print(''.join(chr(b) for b in password))
# Вывод: d34thpawn_c2!
```

### Шаг 4: Доступ получен

```bash
informante@85ed3b93c36f:~$ ./de4thpawn_auth
[*] Booting de4thPawn Identity Module...
[*] Module loaded: PWG{STR1NGS_4R3_N0T_3N0UGH}
[de4thPawn] Authentication required.
Enter access code: d34thpawn_c2!
[+] ACCESS GRANTED. Decrypting vault...
Secret Intel: PWG{r3v3rs3_m4th_cr4ck3d}
```

### Флаг

```
PWG{r3v3rs3_m4th_cr4ck3d}
```


