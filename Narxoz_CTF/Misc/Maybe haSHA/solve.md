# SHA-256 

## Task Description
Each line in the provided file represents a SHA-256 hash of a single character. Since the input space is very small (printable ASCII characters), the problem can be solved with a simple brute-force attack

## Approach
The strategy is to generate all possible printable ASCII characters, compute their SHA-256 hashes, and build a lookup table mapping each `hash` $\rightarrow$ `character`

## Exploitation Steps
A simple Python script was used to automate the decryption process:
1. Iterate over all characters in `string.printable`.
2. Compute the SHA-256 hash for each individual character
3. Store the results in a dictionary (hash map)
4. Parse the given file line by line and replace each hash with the corresponding character from the dictionary

## Conclusion
Even though SHA-256 is cryptographically secure, it becomes trivial to reverse when the input space is extremely limited (such as single characters), making a full keyspace brute-force instantly feasible

## Flag
> **`cycnet{sha_hashes_are_good_tho}`**