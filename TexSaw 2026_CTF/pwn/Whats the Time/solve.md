Анализ бинаря
32-битный ELF. Программа берёт unix timestamp, XOR-ит им входные данные, затем копирует результат в стековый буфер — stack buffer overflow.
XOR ключ для байта на позиции i: ((timestamp + i//4) >> ((i%4)*8)) & 0xff

Эксплуатация
Получить ключ — отправить \x00 * 160, echo и есть чистый ключ. server_t = u32(key[:4]).
Найти offset — через GDB + cyclic паттерн: 68 байт.
ROP chain — system("/bin/sh") бесполезен без TTY, поэтому: read(0, BSS, 64) → system(BSS). Сначала ROP вызывает read() который ждёт нашу команду, потом system() её выполняет.
[68 байт мусора] [read@plt] [system@plt] [0] [BSS] [64] [0xdeadbeef] [BSS]
После отправки ROP шлём cat flag* — попадает в BSS через read(), затем выполняется через system()