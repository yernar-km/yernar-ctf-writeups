During a system dump, some parameters were corrupted: the last 72 bits of p were lost. Then, from the recovered parameters, a key was derived by hashing the secret (I think it was AES-GCM?).

Flag format: KubSTU{...}