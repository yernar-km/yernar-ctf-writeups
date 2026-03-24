from enigma.machine import EnigmaMachine
import itertools

ciphertext = "YSTRPNGEHUBDLMQSSXYESYXBRTLIEIMHCWDZUI"
rotors_list = ['I', 'II', 'III', 'IV', 'V']
reflectors = ['B', 'C']
alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


for rotors in itertools.permutations(rotors_list, 3):
    for ref in reflectors:
        for p1 in alphabet:
            for p2 in alphabet:
                for p3 in alphabet:
                    start_pos = p1 + p2 + p3
                    machine = EnigmaMachine.from_key_sheet(
                        rotors=' '.join(rotors),
                        reflector=ref,
                        ring_settings=[1, 1, 1],
                        plugboard_settings='AV BS CG DL FU'
                    )

                    machine.set_display(start_pos)

                    pt_start = machine.process_text(ciphertext[:6])

                    if pt_start == 'CYCNET':
                        machine.set_display(start_pos)
                        full_pt = machine.process_text(ciphertext)

                        print(f"yes")
                        print(f"Рот: {rotors} | Реф: {ref} | Поз: {start_pos}")
                        print(f": {full_pt}")
                        exit()