import h5py
import numpy as np


def extract_flag_from_model(file_path):

   
    try:
        with h5py.File(file_path, 'r') as f:
    
            kernel_path = 'model_weights/secret_layer/sequential/secret_layer/kernel'

            if kernel_path not in f:
                
                return


            kernel_data = f[kernel_path][:]
            first_row = kernel_data[0, :]

            print(f"size: {kernel_data.shape}")
          

            flag_chars = []
            for val in first_row:
                ascii_code = int(round(val * 1000))
                # Фильтруем только печатные символы ASCII
                if 32 <= ascii_code <= 126:
                    flag_chars.append(chr(ascii_code))

            flag = "".join(flag_chars)

            if flag:
                print(f"[+] {flag}")
            else:
                print("[-] ")

    except Exception as e:
        print(f"[!]  {e}")

