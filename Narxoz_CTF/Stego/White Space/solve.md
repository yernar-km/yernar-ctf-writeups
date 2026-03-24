## Task Description
The provided memo looked like a normal text document, but contained hidden data after the line `"All Department Heads"`. The key observation was the presence of invisible Unicode characters.

## Analysis
The text included zero-width characters that acted as a binary encoding mechanism:
* **Zero-Width Space** (`U+200B`) $\rightarrow$ `0`
* **Zero-Width Non-Joiner** (`U+200C`) $\rightarrow$ `1`

By extracting only these invisible characters, a hidden binary sequence was obtained.

## Exploitation Steps
1. **Extraction:** Extract all zero-width characters from the text.
2. **Binary Conversion:** Convert them into bits (`0` and `1`) using the mapping discovered above.
3. **Byte Grouping:** Group the resulting bits into bytes (chunks of 8 bits).
4. **ASCII Decoding:** Decode each 8-bit byte into its corresponding ASCII character to reveal the hidden message.

## Conclusion
This challenge demonstrates a classic steganography technique using zero-width Unicode characters. Even though the text appears normal to the human eye, hidden data can be embedded invisibly and recovered by analyzing the underlying character encoding.

## Flag
> **`cycnet{56dbaa3c96f238f89b93c108c104f5c7}`**