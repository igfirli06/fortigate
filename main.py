import os
import sys
import logging
from datetime import datetime
import gzip
import re
import csv
from flask import Flask, request, render_template, flash, redirect, url_for, send_file

HTTP_PORT = 5000
LOG_PATH = "app_nodb.log"
NETWORK_LOG_PATH = "FORTIGATE.READING.LOG" 

GLOBAL_DATA = {
    "email": [],
    "traffic": []
}

KEYS_EMAIL = ["date", "time", "action", "from", "to", "srcip", "dstip", "recipient", "subject", "size", "attachment", "cc"]
KEYS_TRAFFIC = ["date", "time", "srcip", "srcmac", "dstcountry", "dstport", "app", "utmaction", "policyid", "policyname"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

LOG_PATTERN = re.compile(r'([a-zA-Z0-9_-]+)=(?:"([^"]*)"|([^"\s]+))')

app = Flask(__name__)
app.secret_key = "KEY_NODB"

def parse_line(line, keys):
    out = {}
    try:
        line = line.strip()
        for m in LOG_PATTERN.finditer(line):
            k, v = m.group(1).lower(), m.group(2) or m.group(3)
            if k in keys: out[k] = v
    except: pass
    return out

def process_file_to_ram(ltype, target_date):
    global GLOBAL_DATA
    GLOBAL_DATA[ltype] = []
    
    if not os.path.exists(NETWORK_LOG_PATH):
        return False, f"File {NETWORK_LOG_PATH} tidak ditemukan!"

    keys = set(KEYS_EMAIL if ltype == "email" else KEYS_TRAFFIC)
    kw = "emailfilter" if ltype == "email" else "forward"

    op = gzip.open if NETWORK_LOG_PATH.endswith(".gz") else open
    
    count = 0
    try:
        with op(NETWORK_LOG_PATH, "rt", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if kw not in line: continue
                
                log = parse_line(line, keys)
                if not log: continue
                
                try:
                    d_str = log.get("date")
                    if not d_str: continue
                    t_str = log.get("time", "00:00:00")
                    
                    dt_full = datetime.strptime(f"{d_str} {t_str}", "%Y-%m-%d %H:%M:%S")
                    
                    if target_date and dt_full.date() != target_date:
                        continue
                    log["datetime"] = dt_full
                    GLOBAL_DATA[ltype].append(log)
                    count += 1
                except: continue

        GLOBAL_DATA[ltype].sort(key=lambda x: x["datetime"], reverse=True)
        
        return True, f"Berhasil memuat {count} data {ltype} ke RAM."
    except Exception as e:
        return False, f"Error: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        lt = request.form.get("log_type")
        dt = request.form.get("manual_date")
        
        target_d = datetime.strptime(dt, "%Y-%m-%d").date() if dt else None
        
        if not target_d:
            flash("Harap pilih tanggal!", "warning")
        else:
            success, msg = process_file_to_ram(lt, target_d)
            flash(msg, "success" if success else "danger")
            
    return render_template("index.html")

@app.route("/view_logs")
def view_logs():
    data = GLOBAL_DATA["email"]
    display_data = data[:500] 
    return render_template("view_logs.html", logs=display_data, total_count=len(data))

@app.route("/view_forward_logs")
def view_forward_logs():
    data = GLOBAL_DATA["traffic"]
    display_data = data[:500]
    return render_template("view_forward_logs.html", logs=display_data, total_count=len(data))

@app.route("/export_csv/<ltype>")
def export_csv(ltype):
    data = GLOBAL_DATA.get(ltype, [])
    if not data:
        flash("Tidak ada data untuk diexport. Process dulu.", "warning")
        return redirect(url_for('index'))
    
    filename = f"export_{ltype}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(os.getcwd(), filename)
    
    try:
        fieldnames = list(KEYS_EMAIL) if ltype == "email" else list(KEYS_TRAFFIC)
        fieldnames.insert(0, "datetime") 
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for row in data:
                writer.writerow(row)
                
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        flash(f"Gagal export: {e}", "danger")
        return redirect(url_for('index'))

@app.route("/debug_file")
def debug_file():
    try:
        if os.path.exists(NETWORK_LOG_PATH):
            with open(NETWORK_LOG_PATH,'r',encoding='utf-8',errors='replace') as f: 
                return "<h3>Reading Local File: " + NETWORK_LOG_PATH + "</h3><pre>" + "\n".join([f.readline() for _ in range(20)]) + "</pre>"
        else:
            return f"<h3>File {NETWORK_LOG_PATH} tidak ditemukan.</h3>"
    except Exception as e: return f"Err: {e}"

@app.route("/view_backups")
def view_backups():
    return "<h3>Fitur Backup Database dimatikan (No Database Mode). Gunakan fitur Export CSV di halaman View Logs.</h3>"

if __name__ == "__main__":
    print("--- SERVER NO-DATABASE STARTED ---")
    print(f"1. Pastikan file '{NETWORK_LOG_PATH}' ada di folder ini.")
    print(f"2. Buka browser: http://localhost:{HTTP_PORT}")
    print("3. Pilih Tanggal -> Klik Process -> Lihat di View Logs")
    app.run(host='0.0.0.0', port=HTTP_PORT, debug=True, use_reloader=False)