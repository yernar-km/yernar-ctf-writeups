
## Task Description
OmniCorp is a corporate benefits portal challenge. Upon logging in, the user is assigned the low-level role of "Data Drone" with the identifier Employee `#1024`. The interface displays a limited benefits package, but a hint suggests that the CEO’s profile contains a "special bonus"

* **Target URL:** `http://94.131.93.83:5002/api/benefits?employee_id=1024`
* **Current Status:** Employee `#1024` (Bonus: `$0.00`)
* **Goal:** Access the CEO's profile to retrieve the hidden flag

## Vulnerability Discovery
During the analysis of the API request, the `employee_id` parameter was identified in the query string. This is a prime indicator of an **Insecure Direct Object Reference (IDOR)** vulnerability.

An IDOR occurs when an application provides direct access to objects based on user-supplied input without performing adequate authorization checks to ensure the requester has permission to see that specific data. Given the corporate hierarchy, it is highly probable that the CEO's account is associated with a low-index identifier, such as `1`

## Exploitation Steps

### 1. Initial Attempt
Manually changing the ID in the browser to `employee_id=1` initially triggered a client-side warning: *"Access Denied! CEO profile is strictly confidential."* This suggested a basic front-end filter was in place

### 2. Bypassing the UI
To bypass the client-side restriction, a direct request was made to the API endpoint using `curl`. This allows for the inspection of the raw JSON response without the browser's JavaScript intervention
### 3. Data Extraction
**Request:**
`GET /api/benefits?employee_id=1`

**Server Response:**
```json
{
  "bonus": "cycnet{7d793037a0760186574b0282f2f435e7}"
}
```
The server successfully returned the sensitive executive data, revealing the flag within the `bonus` field.

## Remediation
To prevent this vulnerability, the following security measures should be implemented:

* **Server-Side Authorization:** Implement strict access control checks on the backend. The server must verify if the user's session token grants them permission to access the specific `employee_id` requested.
* **Indirect Reference Maps:** Use non-predictable identifiers, such as UUIDs (Universally Unique Identifiers), instead of sequential integers (`1`, `2`, `3`...) to make it impossible for attackers to guess valid IDs

## Flag
> **`cycnet{7d793037a0760186574b0282f2f435e7}`**