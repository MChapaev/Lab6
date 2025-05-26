#!/usr/bin/env python3

import cgi
import sqlite3
import html
import datetime
import json
import sys
from pathlib import Path
import datetime

DB_PATH = Path(__file__).resolve().parent / "Insurance.db"

form = cgi.FieldStorage()
query_type = form.getfirst("query_type", "").strip()
export_format = form.getfirst("export", "").strip().lower()

def save_json(data, columns):
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{now}.json"
    print("Content-Type: application/json")
    print(f"Content-Disposition: attachment; filename=\"{filename}\"\n")
    rows_as_dicts = [dict(zip(columns, row)) for row in data]
    print(json.dumps(rows_as_dicts, indent=2))
    sys.exit(0)

def print_html_table(rows, columns, title):
    print("Content-Type: text/html\n")
    print(f"<html><head><title>{title}</title></head><body><h2>{title}</h2>")

    if not rows:
        print("<p>No records found.</p></body></html>")
        return

    print("<table border='1' cellpadding='5'>")
    print("<tr>" + "".join(f"<th>{html.escape(col)}</th>" for col in columns) + "</tr>")
    for row in rows:
        print("<tr>" + "".join(f"<td>{html.escape(str(cell))}</td>" for cell in row) + "</tr>")

    print("<a href=\"/index.html\">Go back</a><br><br>")
    print("</table></body></html>")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if query_type == "by_client":
        full_name = form.getfirst("full_name", "").strip()
        passport = form.getfirst("passport_number", "").strip()

        if not full_name or not passport:
            raise Exception("Full name and passport number are required.")

        cursor.execute("""
            SELECT Claims.description, Claims.claim_date, Claims.amount, Policies.policy_type
            FROM Claims
            JOIN Policies ON Claims.policy_id = Policies.id
            JOIN Clients ON Policies.client_id = Clients.id
            WHERE Clients.full_name = ? AND Clients.passport_number = ?
        """, (full_name, passport))
        title = f"Claims for {html.escape(full_name)} ({html.escape(passport)})"

    elif query_type == "active":
        today = datetime.date.today().isoformat()
        cursor.execute("""
            SELECT  Claims.description, Claims.claim_date, Claims.amount,
                   Policies.policy_type, Policies.end_date
            FROM Claims
            JOIN Policies ON Claims.policy_id = Policies.id
            WHERE date(Policies.end_date) >= date(?)
        """, (today,))
        title = "Active Claims (Policy not expired)"

    elif query_type == "group_by_type":
        cursor.execute("""
            SELECT Policies.policy_type, COUNT(Claims.id) as claim_count, SUM(Claims.amount) as total_amount
            FROM Claims
            JOIN Policies ON Claims.policy_id = Policies.id
            GROUP BY Policies.policy_type
        """)
        title = "Claims Grouped by Policy Type"

    else:
        raise Exception("Invalid query type.")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    if export_format == "json":
        save_json(rows, columns)
    else:
        print_html_table(rows, columns, title)

    conn.close()

except Exception as e:
    print("Content-Type: text/html\n")
    print(f"<h1>Error</h1><p>{html.escape(str(e))}</p>")
