Дают стриппнутый ELF бинарь. Запустить нельзя (нестандартный интерпретатор из Nix), поэтому сразу в strings и objdump.
Из strings вылезает подсказка: tiny_encrypt_key — склеенная из двух movabs инструкций в main. Это и есть ключ шифрования.
В дизассемблере видно алгоритм: константа 0x9e3779b9 (delta), 32 итерации, блоки по 8 байт — классический TEA (Tiny Encryption Algorithm). Программа берёт твой ввод, шифрует TEA с ключом tiny_encrypt_key и сравнивает через memcmp с шифртекстом, захардкоженным в .data по адресу 0x404080.
Вытащили 32 байта шифртекста из бинаря, расшифровали TEA в обратную сторону:
pythonimport struct

def tea_decrypt(v, k):
    delta = 0x9e3779b9
    v0, v1 = v[0], v[1]
    total = (delta * 32) & 0xffffffff
    for _ in range(32):
        v1 = (v1 - (((v0<<4)+k[2]) ^ (v0+total) ^ ((v0>>5)+k[3]))) & 0xffffffff
        v0 = (v0 - (((v1<<4)+k[0]) ^ (v1+total) ^ ((v1>>5)+k[1]))) & 0xffffffff
        total = (total - delta) & 0xffffffff
    return [v0, v1]

k = list(struct.unpack('<4I', b'tiny_encrypt_key'))
ct = bytes.fromhex('38755bcb44d2be5d969c5643ea9806754a4813e6d4e88e4f72708bffdc99f87')
for i in range(4):
    v = list(struct.unpack_from('<2I', ct, i*8))
    print(struct.pack('<2I', *tea_decrypt(v, k)).decode(), end='')

    Флаг: RS{oh_its_a_TEAreasure_chest}