# Web Challenge Writeup

## Task Description
The goal of this challenge is to recover a hidden flag split into three distinct parts, each concealed within different layers of a standard web application: the HTML source, the JavaScript logic, and the CSS styling.

## Exploitation Steps

### 1. Source Code Analysis (HTML)
The first step involves inspecting the raw HTML of the landing page (accessible via `Ctrl + U`). A hidden HTML comment was discovered at the beginning of the file containing the first fragment of the flag.

* **Location:** Index HTML source
* **Found:** `beg1` 

### 2. Client-Side Scripting (JavaScript)
Next, the associated JavaScript files (e.g., `script.js` or internal `<script>` blocks) were analyzed. A variable was found that is declared in the global scope but never rendered in the Document Object Model (DOM).

* **Location:** `script.js`
* **Variable:** `const hiddenPart = 'nner_w3b_';`
* **Found:** `nner_w3b_`

### 3. Style Sheets Inspection (CSS)
Finally, the linked CSS file (`style.css`) was checked for hidden data. A custom CSS variable (CSS property) was defined within the `:root` selector, holding the final segment.

* **Location:** `style.css`
* **Property:** `--flag-part-3: "cha11enge}";`
* **Found:** `cha11enge}`

## Flag Assembly
Combining the segments from the HTML, JS, and CSS layers:
`cycnet{beg1` + `nner_w3b_` + `cha11enge}`

## Flag
> **`cycnet{beg1nner_w3b_cha11enge}`**