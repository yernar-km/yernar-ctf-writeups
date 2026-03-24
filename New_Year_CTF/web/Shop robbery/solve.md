## Task Description
The challenge presents a jewelry store website ("Ice Shop") where some features, like new user registration, are disabled. We are provided with basic credentials (`ctf_user` : `ctf_password`) to explore the platform.

* **Target URL:** `http://ctf.mf.grsu.by/web_tasks/ice_shop/`
* **Provided Credentials:** `ctf_user` : `ctf_password`
* **Goal:** Gain elevated privileges to access the administrative panel and retrieve the flag.

## Vulnerability Analysis

### 1. Cross-Challenge Dependency
A key observation in this CTF was the shared domain between this task and a previous "Beginner" challenge. The flag from the previous task was not a readable phrase but a cryptic string: `7d793037a0760186574b0282f2f435e7`.

### 2. Password Cracking (MD5)
The string was identified as an MD5 hash. Using online databases or tools like Hashcat or John the Ripper, the hash was cracked to reveal the plaintext password: `grupasord`.

### 3. Information Gathering (OSINT/Recon)
The credentials `admin`:`grupasord` did not work. This necessitated a closer look at the site's content. By analyzing user reviews and comments on the products, a specific moderator was mentioned by name: `nickley`.

## Exploitation Steps

1. **Credential Stuffing:** Using the discovered username from the reviews and the cracked password from the previous challenge, we attempted to log in.
   * **Username:** `nickley`
   * **Password:** `grupasord`
2. **Privilege Escalation:** The login was successful. Because the account belongs to a moderator, new navigation options became available that were hidden from the standard `ctf_user`.
3. **Admin Panel Access:** We navigated to the administrative interface (Admin Panel).
4. **Flag Recovery:** The flag was found hidden within the descriptions of the jewelry categories inside the management dashboard.

## Conclusion
This challenge demonstrates a "pivoting" technique where the solution to one problem serves as the key to the next. It also highlights the importance of Content Analysis—attackers often find sensitive information (usernames, internal roles, or software versions) simply by reading public comments or "About Us" pages.

## Flag
> **`grodno{w@w_y%u_r#all^_c#n_fYnd_it}`**