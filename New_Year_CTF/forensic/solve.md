
## Challenge Overview
The Process Injection Analysis challenge involved analyzing a suspicious executable (`inject.exe`) supported by an IDA database (`.i64`) and an API Monitor trace (`.apmx64`). The objective was to perform a combined static and dynamic analysis to answer a series of technical questions regarding the malware's behavior and injection routine

* **Tools Used:** IDA Pro, API Monitor
* **Target:** `inject.exe`
* **Remote Service:** `nc ctf.mf.grsu.by 9058`

## Vulnerability & Technique Analysis

### 1. Execution Timing (TLS Callbacks)
Static analysis in IDA Pro revaled the use of **TLS (Thread Local Storage) Callbacks**. These are code blocks that the Windows loader executes *before* the program's `AddressOfEntryPoint` (the `main` or `WinMain` function)

This is a common anti-analysis and stealth technique. In this specific case, the malware uses the callback to run its entire injection payload and then calls `ExitProcess`, ensuring the "normal" program code is never even reache

### 2. Process Enumeration
The API trace showed a standard sequence for finding a target process:
* `CreateToolhelp32Snapshot`: Takes a "snapshot" of all current processes
* `Process32First` / `Process32Next`: Iterates through the snapshot to find a specific string
* **Target Identified:** The malware was searching for `notepad.exe` (PID `2816`)

## Exploitation Steps (The Injection Chain)
The malware follows the "Classic" Remote Process Injection pattern to execute shellcode within the memory space of `notepad.exe`

### 1. The Injection Sequence
1. `OpenProcess`: Obtains a handle to `notepad.exe` with necessary access rights (`PROCESS_ALL_ACCESS`)
2. `VirtualAllocEx`: Allocates a new memory region (size: 511 bytes) inside the target process's memory space
3. `WriteProcessMemory`: Copies the malicious shellcode from the injector into the newly allocated space
4. `CreateRemoteThread`: Tells the operating system to start a new thread inside `notepad.exe`, pointing it to the start of the shellcode

### 2. Payload Analysis
Analysis of the 511-byte shellcode revealed it utilizes `ws2_32.dll` (the Windows Socket API) to establish a **Reverse Shell**
* **Attacker IP:** `192.168.1.3`
* **Port:** `1337`

## Technical Summary (Answers)

| Parameter | Value |
| :--- | :--- |
| **Injection Technique** | Thread Local Storage (TLS) |
| **Snapshot API** | `CreateToolhelp32Snapshot` |
| **Target Process** | `notepad.exe` |
| **Target PID** | `2816` |
| **Shellcode Size** | 511 bytes |
| **Execution API** | `CreateRemoteThread` |
| **Exit API (Pre-Main)** | `ExitProcess` |

## Conclusion
This challenge highlights how malware authors leverage TLS Callbacks to achieve early execution and bypass simple debuggers that break only at the Entry Point. Despite the stealthy start, the core injection follows a documented pattern (`VirtualAllocEx` + `WriteProcessMemory` + `CreateRemoteThread`), which is easily detectable via API monitoring

### Key Takeaways
* **TLS Callbacks** are a powerful vector for stealth and anti-debugging
* **API Monitoring** (e.g., API Monitor or Sysmon) is essential for identifying process cross-talk
* **Network APIs** (`ws2_32`) in shellcode almost always indicate a reverse shell or data exfiltration