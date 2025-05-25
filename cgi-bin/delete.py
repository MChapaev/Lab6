#!/usr/bin/env python3

import cgi
import sqlite3
import html
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "Insurance.db"

print("Content-Type: text/html\n")

form = cgi.FieldStorage()
client_id_raw = form.getfirst("client_id", "").strip()

if not client_id_raw.isdigit():
    print("<h1>Error</h1>")
    print("<p>Invalid client ID.</p>")
    exit()

client_id = int(client_id_raw)

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Clients WHERE id = ?", (client_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()

    print("<html><body>")
    if affected == 0:
        print("<h1>Not Found</h1>")
        print(f"<p>No client with ID {client_id} was found.</p>")
    else:
        print("<h1>Success</h1>")
        print(f"<p>Client with ID {client_id} has been deleted.</p>")
    print("</body></html>")

except Exception as e:
    print("<h1>Error</h1>")
    print(f"<p>{html.escape(str(e))}</p>")
