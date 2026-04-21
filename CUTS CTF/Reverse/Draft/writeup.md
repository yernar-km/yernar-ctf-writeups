1. Анализ файла
Запускаем strings — видим фрагменты флага и строки программы:
strings draft
→ "Recovering draft...", "CUTS{", "draft restored", "military_grade_encryption enabled"

2. Дизассемблирование
Через objdump смотрим main. Программа берёт из .rodata два блока:
ключ (4 байта): 13 37 C0 DE
зашифрованные данные: 37 байт
Алгоритм «шифрования» на каждый байт (i = 0..36):
al = key[i % 4] XOR enc[i]
al = ROR(al, 3)
al = al - i

3. Декодирование (Python)
def ror8(v, n): return ((v >> n) | (v << (8-n))) & 0xFF
result = [ror8(key[i%4] ^ enc[i], 3) - i & 0xFF for i in range(37)]

4. Проверка
Запускаем бинарник — выводит "draft restored" → флаг верный.

Флаг
CUTS{unsent_S13_draft_recovered_late}
