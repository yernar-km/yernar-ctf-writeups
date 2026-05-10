# Lab 2 Операция C4RNAGE (Linux Advanced)

**CTF:** Hack2Dawn 2026  
**Категория:** Linux Advanced  
**Сложность:** Medium  

---

## Задание

> Команде удалось проникнуть на приватный файловый сервер de4thPawn. Доступ получен через аккаунт `agente_shadow`. Superiores оставили подсказки по всей системе для экстренного восстановления информации. Задача: исследовать сервер и извлечь всё что de4thPawn держит "под замком".

Лаб разворачивается в Docker-контейнере:

```bash
docker compose up -d
ssh agente_shadow@localhost -p <порт>
```

---

## Парт 1 — Первый контакт

### Решение

После подключения сразу проверяем переменные окружения — любой агент оставляет след в сессии:

```bash
[shadow-srv] ~$ env
```

Флаг находится прямо в переменных окружения текущей сессии.


## Парт 2 — Скрытый архив

### Решение

Задание намекает на что-то объёмное — "улика не помещается в кармане". Ищем самые большие файлы в системе:

```bash
[shadow-srv] ~$ find / -type f 2>/dev/null -exec du -h {} + | sort -rh | head -20
29M     /usr/lib/x86_64-linux-gnu/libicudata.so.70.1
26M     /opt/.deep_archive/backup_2024/.shadow_backup.dat
25M     /usr/lib/gcc/x86_64-linux-gnu/11/cc1
24M     /usr/lib/gcc/x86_64-linux-gnu/11/lto1
24M     /usr/bin/x86_64-linux-gnu-lto-dump-11
7.3M    /usr/lib/x86_64-linux-gnu/libasan.so.6.0.0
7.1M    /usr/lib/x86_64-linux-gnu/libtsan.so.0.0.0
5.8M    /usr/lib/x86_64-linux-gnu/libc.a
5.7M    /usr/bin/python3.10
5.6M    /usr/lib/x86_64-linux-gnu/libpython3.10.so.1.0
4.3M    /usr/lib/x86_64-linux-gnu/libcrypto.so.3
3.7M    /usr/bin/vim.basic
3.7M    /usr/bin/perl5.34.0
3.2M    /usr/lib/x86_64-linux-gnu/libicui18n.so.70.1
3.1M    /usr/bin/x86_64-linux-gnu-ld.gold
2.9M    /usr/lib/gcc/x86_64-linux-gnu/11/liblsan.a
2.9M    /usr/lib/gcc/x86_64-linux-gnu/11/libgcc.a
2.8M    /usr/lib/systemd/libsystemd-shared-249.so
2.7M    /usr/lib/x86_64-linux-gnu/libmpfr.so.6.1.0
2.7M    /usr/lib/gcc/x86_64-linux-gnu/11/libasan.a
```

Сразу бросается в глаза: `26M /opt/.deep_archive/backup_2024/.shadow_backup.dat` — скрытый файл (точка в начале имени) в подозрительной директории. Ищем флаг:

```bash
[shadow-srv] ~$ grep -a "PWG{" /opt/.deep_archive/backup_2024/.shadow_backup.dat
PWG{h1dd3n_b4ckup_f0und}
```

### Флаг

```
PWG{h1dd3n_b4ckup_f0und}
```

---

## Парт 3 — Повторяющийся сигнал (Cron)

### Решение

Задание говорит про "повторяющийся пульс, повторяющийся сигнал" — это cron задачи. Смотрим всё:

```bash
[shadow-srv] ~$ crontab -l
no crontab for agente_shadow

[shadow-srv] ~$ cat /etc/crontab
# /etc/crontab: system-wide crontab
SHELL=/bin/sh
17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )

[shadow-srv] ~$ ls -la /etc/cron*
-rw-r--r-- 1 root root 1136 Mar 23  2022 /etc/crontab
/etc/cron.d:
total 20
drwxr-xr-x 1 root root 4096 May  7 23:09 .
drwxr-xr-x 1 root root 4096 May  9 21:44 ..
-rw-r--r-- 1 root root  102 Mar 23  2022 .placeholder
-rw-r--r-- 1 root root  201 Jan  8  2022 e2scrub_all
-rw-r--r-- 1 root root   43 May  7 23:09 shadow_maintenance

[shadow-srv] ~$ cat /etc/cron.d/*
30 3 * * 0 root test -e /run/systemd/system || SERVICE_MODE=1 /usr/lib/x86_64-linux-gnu/e2fsprogs/e2scrub_all_cron
10 3 * * * root test -e /run/systemd/system || SERVICE_MODE=1 /sbin/e2scrub_all -A -r
* * * * * root /usr/local/bin/cron_task.sh
```

Подозрительный файл `shadow_maintenance` и задача `* * * * *` — каждую минуту. Смотрим скрипт:

```bash
[shadow-srv] ~$ cat /etc/cron.d/shadow_maintenance
* * * * * root /usr/local/bin/cron_task.sh

[shadow-srv] ~$ cat /usr/local/bin/cron_task.sh
#!/bin/bash
# Tarea automatizada que escribe la flag en ruta oculta
mkdir -p /tmp/.hidden_ops
echo "PWG{cr0n_t4sk_expos3d}" > /tmp/.hidden_ops/.flag_cron

[shadow-srv] ~$ cat /tmp/.hidden_ops/.flag_cron
PWG{cr0n_t4sk_expos3d}
```

### Флаг

```
PWG{cr0n_t4sk_expos3d}
```

---

## Парт 4 — SUID эскалация привилегий

### Решение

Задание намекает на "инструмент экстренного доступа" — ищем SUID бинарники (запускаются с правами владельца):

```bash
[shadow-srv] ~$ find / -perm -4000 -type f 2>/dev/null
/usr/bin/passwd
/usr/bin/chfn
/usr/bin/umount
/usr/bin/su
/usr/bin/mount
/usr/bin/chsh
/usr/bin/gpasswd
/usr/bin/newgrp
/usr/bin/sudo
/usr/local/bin/read_classified
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
```

`/usr/local/bin/read_classified` — явно нестандартный бинарник. Запускаем:

```bash
[shadow-srv] ~$ /usr/local/bin/read_classified
== CLASSIFIED FILE ==
Operation C4rnage — Maximum Clearance
Access granted via SUID override.
FLAG: PWG{suid_pr1v1l3g3_3sc}
```

SUID бит позволяет запустить бинарник с правами root, получив доступ к защищённым файлам.

### Флаг

```
PWG{suid_pr1v1l3g3_3sc}
```

---

## Парт 5 — Symlink обход

### Решение

Через `strings` на бинарнике `read_classified` видим что он читает конкретный файл:

```bash
[shadow-srv] ~$ strings /usr/local/bin/read_classified
...
/opt/classified/secreto_admin.txt
[ERROR] Could not open the file.
...
```

Исследуем `/opt/`:

```bash
[shadow-srv] ~$ ls -la /opt/
total 20
drwxr-xr-x 1 root root       4096 May  7 23:09 .
drwxr-xr-x 1 root root       4096 May  9 21:44 ..
drwxr-xr-x 3 root root       4096 May  7 23:09 .deep_archive
drwxr-x--- 2 root classified 4096 May  7 23:09 classified
drwxr-xr-x 2 root root       4096 May  7 23:09 links

[shadow-srv] ~$ ls -la /opt/links/
total 8
drwxr-xr-x 2 root root 4096 May  7 23:09 .
drwxr-xr-x 1 root root 4096 May  7 23:09 ..
lrwxrwxrwx 1 root root   33 May  7 23:09 master_key.txt -> /srv/.private_root/master_key.txt
```

`master_key.txt` — символическая ссылка (symlink) на файл в закрытой директории `/srv/.private_root/`. Читаем через ссылку:

```bash
[shadow-srv] ~$ cat /opt/links/master_key.txt
PWG{syml1nk_byp4ss}
```

Symlink позволяет обойти ограничения директорий — файл физически недоступен напрямую, но через ссылку читается свободно.

### Флаг

```
PWG{syml1nk_byp4ss}
```

---

## Парт 6 — Утечка через переменные окружения

### Решение

Ищем флаги во всех конфигурационных файлах системы:

```bash
[shadow-srv] ~$ grep -ra "PWG{" /etc/ 2>/dev/null
/etc/profile:export SESSION_KEY="PWG{3nv_s3cr3t_k3y}"
/etc/environment:export SESSION_KEY="PWG{3nv_s3cr3t_k3y}"
```

Секретный ключ хранится в переменной окружения прямо в `/etc/profile` — загружается при каждом входе в систему. Классическая ошибка: хранить секреты в открытом виде в конфиг файлах.

### Флаг

```
PWG{3nv_s3cr3t_k3y}
```

---

## Парт 7 — История команд

### Решение

Задание говорит про "хлебные крошки оставленные второпях". Находим всех пользователей и проверяем их bash history:

```bash
[shadow-srv] ~$ find / -name ".*" -type f 2>/dev/null | grep -v proc | grep -v sys
...
/home/agente_rogue/.bash_history
...

[shadow-srv] ~$ cat /home/agente_rogue/.bash_history
ls -la /opt
cd /opt/classified
cat secreto_admin.txt
echo "backup completed"
export TEMP_CRED="PWG{h1st0ry_l34k3d}"
ssh root@192.168.1.10
exit
```

Оператор `agente_rogue` случайно экспортировал credentials прямо в терминале — и это навсегда осталось в `.bash_history`.

### Флаг

```
PWG{h1st0ry_l34k3d}
```

---

## Парт 8 — Утечка в логах

### Решение

Задание говорит про "вещи которые не должны были быть записаны". Ищем флаги во всех логах:

```bash
[shadow-srv] ~$ grep -ra "PWG{" /var/ 2>/dev/null
/var/log/shadow_ops/access.log:[2024-11-01 03:15:10] DEBUG - Temporary key recorded: PWG{l0g_1nf0_l34k}
```

Смотрим полный лог:

```bash
[shadow-srv] ~$ cat /var/log/shadow_ops/access.log
[2024-11-01 03:12:44] INFO  - Connection established from 10.0.0.47
[2024-11-01 03:13:01] INFO  - Authentication successful: agente_rogue
[2024-11-01 03:13:22] DEBUG - Session started. Token: a3f9c12b
[2024-11-01 03:14:05] WARN  - Attempted access to /opt/classified denied
[2024-11-01 03:14:38] INFO  - Transfer completed: shadow_backup.dat
[2024-11-01 03:15:10] DEBUG - Temporary key recorded: PWG{l0g_1nf0_l34k}
[2024-11-01 03:15:55] INFO  - Session closed. Duration: 191s
[2024-11-02 07:44:12] INFO  - Connection established from 10.0.0.89
[2024-11-02 07:44:30] WARN  - Multiple failed attempts detected
[2024-11-02 07:44:31] ERROR - Access blocked by security policy
```

В строке `DEBUG` случайно записан временный ключ. Классическая ошибка разработчиков — оставлять debug логирование в проде.

### Флаг

```
PWG{l0g_1nf0_l34k}
```


