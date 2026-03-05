# Week 6 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **TODO** \
SUNet ID: **TODO** \
Citations: Claude Code (claude-sonnet-4-6) — used to triage Semgrep output, implement fixes, and verify tests.

This assignment took me about **TODO** hours to do.


## Brief findings overview

> Semgrep reported findings across two categories:
>
> **SAST (Code) — 13 findings across 3 files:**
> - `routers/notes.py`: SQL injection via raw f-string interpolation in `sqlalchemy.text()`, arbitrary `eval()` code execution, shell command injection via `subprocess.run(shell=True)`, SSRF via `urlopen(url)`, and path traversal via `open(path)`.
> - `main.py`: Overly permissive CORS (`allow_origins=["*"]`).
> - `frontend/app.js`: XSS via `innerHTML` with unsanitized API data.
>
> **SCA (Supply Chain) — 25 findings in `requirements.txt`:**
> - 1 reachable HIGH CVE: `werkzeug==0.14.1` (CVE-2024-34069, CSRF).
> - 3 unreachable CRITICAL CVEs: `pyyaml==5.1` (remote code injection).
> - 21 additional MODERATE/HIGH CVEs across `requests`, `jinja2`, `pydantic`, and `werkzeug`.
>
> **False positives / noise ignored:**
> - `action_items.py:33` and `notes.py:33` — Semgrep flagged `skip` and `limit` query parameters flowing into `stmt.offset(skip).limit(limit)` as SQL injection. These are SQLAlchemy ORM integer parameters, not raw SQL string interpolation, so they cannot inject SQL. Ignored as false positives.


## Fix #1

a. File and line(s)
> `week6/backend/app/routers/notes.py`, lines 71–80

b. Rule/category Semgrep flagged
> - `python.sqlalchemy.security.audit.avoid-sqlalchemy-text.avoid-sqlalchemy-text` (❯❯❱)
> - `python.fastapi.db.sqlalchemy-fastapi.sqlalchemy-fastapi` (❯❯❯❱)
> - `python.fastapi.db.generic-sql-fastapi.generic-sql-fastapi` (❯❯❯❱)

c. Brief risk description
> The `unsafe_search` endpoint built a raw SQL query using an f-string, interpolating the user-supplied `q` parameter directly into the SQL text. An attacker could supply a value like `' OR '1'='1` to bypass the WHERE clause and exfiltrate all notes, or use more advanced payloads to modify or delete data.

d. Your change (short code diff or explanation, AI coding tool usage)
> Used Claude Code to replace the f-string with a named bindparam `:q`, passing the value as a separate dictionary argument to `db.execute()`:
>
> ```python
> # Before
> sql = text(
>     f"""
>     SELECT id, title, content, created_at, updated_at
>     FROM notes
>     WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
>     ORDER BY created_at DESC
>     LIMIT 50
>     """
> )
> rows = db.execute(sql).all()
>
> # After
> sql = text(
>     """
>     SELECT id, title, content, created_at, updated_at
>     FROM notes
>     WHERE title LIKE '%' || :q || '%' OR content LIKE '%' || :q || '%'
>     ORDER BY created_at DESC
>     LIMIT 50
>     """
> )
> rows = db.execute(sql, {"q": q}).all()
> ```

e. Why this mitigates the issue
> The database driver handles `:q` as a parameter binding, not as part of the SQL text. User input is never interpolated into the query string, so special characters like quotes or SQL keywords are treated as literal data and cannot alter the query structure.


## Fix #2

a. File and line(s)
> `week6/frontend/app.js`, line 14

b. Rule/category Semgrep flagged
> `javascript.browser.security.insecure-document-method.insecure-document-method` (❯❯❱)

c. Brief risk description
> The note list renderer assigned API response data (`n.title`, `n.content`) directly into `li.innerHTML`. If a note's title or content contained HTML tags or script payloads (e.g., `<img src=x onerror=alert(document.cookie)>`), the browser would parse and execute them, enabling stored XSS — an attacker who can create a note could steal cookies or perform actions as any user who views the note list.

d. Your change (short code diff or explanation, AI coding tool usage)
> Used Claude Code to replace `innerHTML` with safe DOM element construction using `createElement` and `textContent`/`createTextNode`:
>
> ```js
> // Before
> li.innerHTML = `<strong>${n.title}</strong>: ${n.content}`;
>
> // After
> const strong = document.createElement('strong');
> strong.textContent = n.title;
> li.appendChild(strong);
> li.appendChild(document.createTextNode(': ' + n.content));
> ```

e. Why this mitigates the issue
> `textContent` and `createTextNode` always treat values as plain text — the browser never parses them as HTML. Any angle brackets, script tags, or event handler attributes in the data are rendered as literal characters, completely preventing XSS.


## Fix #3

a. File and line(s)
> `week6/requirements.txt`, lines 1–9

b. Rule/category Semgrep flagged
> Supply Chain (SCA) — multiple CVEs across five packages:
> - `pydantic==1.5.1`: CVE-2024-3772 (ReDoS, MODERATE), CVE-2021-29510 (infinite loop, MODERATE)
> - `requests==2.19.1`: CVE-2024-35195, CVE-2023-32681, CVE-2024-47081 (MODERATE), CVE-2018-18074 (credential leak, HIGH)
> - `PyYAML==5.1`: CVE-2020-1747, CVE-2020-14343, CVE-2019-20477 (remote code injection, **CRITICAL**)
> - `Jinja2==2.10.1`: CVE-2024-34064, CVE-2024-22195 (XSS, MODERATE), CVE-2024-56326, CVE-2025-27516, CVE-2020-28493
> - `Werkzeug==0.14.1`: CVE-2024-34069 (CSRF, **HIGH**, reachable), plus 7 additional MODERATE/HIGH CVEs

c. Brief risk description
> All five packages were pinned to versions from 2018–2020, each with multiple known CVEs. The most severe were the PyYAML CRITICAL RCE vulnerabilities (attackers can execute arbitrary code via malicious YAML) and the Werkzeug HIGH CSRF vulnerability (CVE-2024-34069, flagged as reachable by Semgrep's reachability analysis).

d. Your change (short code diff or explanation, AI coding tool usage)
> Used Claude Code to upgrade all affected packages to their patched versions. Also upgraded `fastapi` and `uvicorn` to maintain compatibility with pydantic v2:
>
> ```diff
> -fastapi==0.65.2
> +fastapi==0.115.12
> -uvicorn==0.11.8
> +uvicorn==0.34.0
> -sqlalchemy==1.3.23
> +sqlalchemy==2.0.47
> -pydantic==1.5.1
> +pydantic==2.12.5
> -requests==2.19.1
> +requests==2.32.4
> -PyYAML==5.1
> +PyYAML==6.0.2
> -Jinja2==2.10.1
> +Jinja2==3.1.6
> -MarkupSafe==1.1.0
> +MarkupSafe==2.1.5
> -Werkzeug==0.14.1
> +Werkzeug==3.1.6
> ```

e. Why this mitigates the issue
> Each upgraded version includes the patches that address the reported CVEs. For example, PyYAML 6.x removed unsafe YAML constructors, Werkzeug 3.x fixed the CSRF debugger bypass, and requests 2.32.x fixed credential leakage on redirects. Keeping dependencies current removes known exploit paths without requiring code changes.
