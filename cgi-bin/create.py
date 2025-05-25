#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import cgitb
import sqlite3
import html
import os
from pathlib import Path

cgitb.enable()

print("Content-Type: text/html\n")

try:
    db_path = Path(__file__).resolve().parent / "Insurance.db"

    form = cgi.FieldStorage()

    full_name = form.getfirst("full_name", "").strip()
    passport = form.getfirst("passport_number", "").strip()
    birth_date = form.getfirst("birth_date", "").strip()
    phone = form.getfirst("phone", "").strip()
    email = form.getfirst("email", "").strip()

    policy_type = form.getfirst("policy_type", "").strip()
    start_date = form.getfirst("start_date", "").strip()
    end_date = form.getfirst("end_date", "").strip()
    premium = float(form.getfirst("amount", "0").strip())

    claim_date = form.getfirst("claim_date", "").strip()
    description = form.getfirst("description", "").strip()
    amount = float(form.getfirst("amount", "0").strip())

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Clients (full_name, passport_number, birth_date, phone, email)
        VALUES (?, ?, ?, ?, ?)
    """, (full_name, passport, birth_date, phone, email))
    client_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO Policies (client_id, policy_type, start_date, end_date, premium)
        VALUES (?, ?, ?, ?, ?)
    """, (client_id, policy_type, start_date, end_date, premium))
    policy_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO Claims (policy_id, claim_date, description, amount)
        VALUES (?, ?, ?, ?)
    """, (policy_id, claim_date, description, amount))

    conn.commit()
    conn.close()

    print(f"""
        <html>
        <head><title>Success</title></head>
        <body>
          <h1>Record Created</h1>
          <p>The new record has been successfully added.</p>
          <a href="/index.html">Back to main menu</a>
        </body>
        </html>
    """)

except Exception as e:
    print(f"""
        <html>
        <head><title>Error</title></head>
        <body>
          <h1>Error Occurred</h1>
          <pre>{html.escape(str(e))}</pre>
          <a href="/cgi-bin/create.html">Back to form</a>
        </body>
        </html>
    """)
