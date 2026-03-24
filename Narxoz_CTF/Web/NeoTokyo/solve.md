# NeoTokyo Poetry

## Task Description
NeoTokyo Poetry is a web-based haiku generator. The application takes a user-provided word and reflects it within a generated poem. The goal is to escalate this reflection into a Server-Side Template Injection (SSTI) and ultimately achieve Remote Code Execution (RCE) to find the flag


* **Goal:** Locate and read the hidden flag file on the server's file system.

## Vulnerability Discovery
The application was tested for template injection by submitting the payload `{{7*7}}`. The server rendered `49` in the output, confirming that user input is processed as a Jinja2 template. Further inspection of the `config` object and `__subclasses__` confirmed that the environment allowed for object traversal within the Python runtime

## Exploitation Steps

### 1. Bypassing Filters
Initial attempts to access common subclasses like `subprocess.Popen` directly resulted in a `500 Internal Server Error`, suggesting the presence of basic blacklists or security filters. However, the `lipsum` object (a standard Jinja2 helper) remained accessible

### 2. Escalation to RCE
By traversing through the `lipsum` global dictionary, it was possible to reach the `__builtins__` module and invoke the `__import__` function to load the `os` library. This allowed for the execution of system commands via `popen().read()`

**Final Payload:**
```jinja2
{{lipsum.__globals__['__builtins__']['__import__']('os').popen('ls -la /app').read()}}
```

### 3. Flag Recovery
Listing the directory contents of `/app` revealed a suspicious file named `context.txt`. Executing the command `cat /app/context.txt` through the injection point successfully retrieved the flag

## Conclusion
This challenge highlights the dangers of passing unsanitized user input directly into template engines. Even with basic filters in place, attackers can often find alternative paths through global objects (like `lipsum` or `cycler`) to reach sensitive Python built-ins

## Flag
> **`cycnet{22c21c762e5da6ce02888db7b34b17a1}`**