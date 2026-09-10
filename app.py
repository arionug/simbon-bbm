"""
SIMBON BBM - Sistem Informasi Manajemen Bon BBM
Kejaksaan Tinggi Jawa Tengah

Aplikasi web lokal berbasis Flask untuk otomatisasi pembuatan
Nota Bon BBM (login, form input, generate PDF, simpan ke SQLite,
dan rekap otomatis ke Excel).

Jalankan dengan:
    pip install -r requirements.txt
    python app.py
Lalu buka browser ke http://127.0.0.1:5000
"""
import os
from datetime import datetime, timedelta

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, send_from_directory, flash
)

import database as db
from terbilang import rupiah_terbilang
from pdf_generator import generate_nota_pdf
from excel_writer import tambah_data_excel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = "simbon-bbm-kejati-jateng-secret-key-2026"  # ganti untuk produksi

APP_NAME = "SIMBON Kejati"
SESSION_TIMEOUT = timedelta(minutes=30)

# Kredensial sementara
VALID_USERNAME = "admin"
VALID_PASSWORD = "kejati"


# --------------------------------------------------------------------------
# Helper
# --------------------------------------------------------------------------
def login_required(view_func):
    from functools import wraps

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # Belum login
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        # Cek waktu aktivitas terakhir
        last_activity = session.get("last_activity")
        if last_activity:
            try:
                last_activity = datetime.fromisoformat(last_activity)
                now = datetime.now()
                # Jika tidak aktif lebih dari 30 menit
                if now - last_activity > SESSION_TIMEOUT:
                    session.clear()
                    flash("Sesi Anda telah berakhir karena tidak ada aktivitas selama 30 menit.")
                    return redirect(url_for("login"))
            except (ValueError, TypeError):
                session.clear()
                return redirect(url_for("login"))
        # Perbarui waktu aktivitas terakhir
        session["last_activity"] = datetime.now().isoformat()
        return view_func(*args, **kwargs)
    return wrapper

# --------------------------------------------------------------------------
# Routes - Autentikasi
# --------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    if session.get("logged_in"):
        return redirect("/dashboard")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect("/dashboard")

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session.permanent = False
            session["logged_in"] = True
            session["username"] = username
            session["last_activity"] = datetime.now().isoformat()
            return redirect("/dashboard")
        else:
            error = "Username atau Password tidak valid."

    return render_template("login.html", app_name=APP_NAME, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# --------------------------------------------------------------------------
# Routes - Halaman Utama / Dashboard
# --------------------------------------------------------------------------
@app.route("/dashboard")
@app.route("/bon-bbm")
@login_required
def dashboard():
    vehicles = db.get_vehicles()
    bbm_prices = db.get_bbm_prices()
    drivers = db.get_drivers()
    return render_template(
        "dashboard.html",
        app_name=APP_NAME,
        username=session.get("username"),
        vehicles=vehicles,
        jenis_bbm_list=[p["jenis_bbm"] for p in bbm_prices],
        bbm_prices={p["jenis_bbm"]: p["harga"] for p in bbm_prices},
        mengetahui_list=[d["nama"] for d in drivers],
    )


@app.route("/settings")
@login_required
def settings():
    return render_template(
        "settings.html",
        app_name=APP_NAME,
        username=session.get("username"),
        vehicles=db.get_vehicles(),
        drivers=db.get_drivers(),
        bbm_prices=db.get_bbm_prices(),
    )


@app.route("/menu3")  # Menu Dalam Pengembangan -> diarahkan ke Bon BBM
@login_required
def menu_dalam_pengembangan():
    return redirect("/dashboard")


# --------------------------------------------------------------------------
# API - Kendaraan
# --------------------------------------------------------------------------
@app.route("/api/vehicles", methods=["GET"])
@login_required
def api_get_vehicles():
    return jsonify({"success": True, "data": db.get_vehicles()})


@app.route("/api/vehicles", methods=["POST"])
@login_required
def api_add_vehicle():
    payload = request.get_json(silent=True) or {}
    nomor_polisi = payload.get("nomor_polisi", "")
    driver = payload.get("driver")
    jenis_bbm = payload.get("jenis_bbm")
    ok, message = db.add_vehicle(nomor_polisi, driver, jenis_bbm)
    status = 200 if ok else 400
    return jsonify({"success": ok, "message": message}), status


@app.route("/api/vehicles/<int:vehicle_id>", methods=["PUT"])
@login_required
def api_update_vehicle(vehicle_id):
    payload = request.get_json(silent=True) or {}
    ok, message = db.update_vehicle(
        vehicle_id,
        nomor_polisi=payload.get("nomor_polisi"),
        driver=payload.get("driver"),
        jenis_bbm=payload.get("jenis_bbm"),
    )
    status = 200 if ok else 400
    return jsonify({"success": ok, "message": message}), status


@app.route("/api/vehicles/<int:vehicle_id>", methods=["DELETE"])
@login_required
def api_delete_vehicle(vehicle_id):
    db.delete_vehicle(vehicle_id)
    return jsonify({"success": True, "message": "Kendaraan berhasil dihapus."})


# --------------------------------------------------------------------------
# API - Driver
# --------------------------------------------------------------------------
@app.route("/api/drivers", methods=["GET"])
@login_required
def api_get_drivers():
    return jsonify({"success": True, "data": db.get_drivers()})


@app.route("/api/drivers", methods=["POST"])
@login_required
def api_add_driver():
    payload = request.get_json(silent=True) or {}
    ok, message = db.add_driver(payload.get("nama", ""))
    status = 200 if ok else 400
    return jsonify({"success": ok, "message": message}), status


@app.route("/api/drivers/<int:driver_id>", methods=["DELETE"])
@login_required
def api_delete_driver(driver_id):
    db.delete_driver(driver_id)
    return jsonify({"success": True, "message": "Driver berhasil dihapus."})


# --------------------------------------------------------------------------
# API - Harga BBM
# --------------------------------------------------------------------------
@app.route("/api/bbm-prices", methods=["GET"])
@login_required
def api_get_bbm_prices():
    return jsonify({"success": True, "data": db.get_bbm_prices()})


@app.route("/api/bbm-prices", methods=["POST"])
@login_required
def api_upsert_bbm_price():
    payload = request.get_json(silent=True) or {}
    ok, message = db.upsert_bbm_price(payload.get("jenis_bbm", ""), payload.get("harga"))
    status = 200 if ok else 400
    return jsonify({"success": ok, "message": message}), status


@app.route("/api/bbm-prices/<int:price_id>", methods=["DELETE"])
@login_required
def api_delete_bbm_price(price_id):
    db.delete_bbm_price(price_id)
    return jsonify({"success": True, "message": "Jenis BBM berhasil dihapus."})


# --------------------------------------------------------------------------
# API - Terbilang otomatis (opsional, dipanggil dari JS saat isi field uang)
# --------------------------------------------------------------------------
@app.route("/api/terbilang", methods=["POST"])
@login_required
def api_terbilang():
    payload = request.get_json(silent=True) or {}
    nominal = payload.get("uang", 0)
    try:
        hasil = rupiah_terbilang(nominal)
    except Exception:
        hasil = ""
    return jsonify({"success": True, "terbilang": hasil})


# --------------------------------------------------------------------------
# API - Generate Nota BBM
# --------------------------------------------------------------------------
@app.route("/api/generate-nota", methods=["POST"])
@login_required
def api_generate_nota():
    payload = request.get_json(silent=True) or {}

    required_fields = [
        "tanggal_nota", "nomor_polisi", "jenis_bbm",
        "jumlah_liter", "uang", "terbilang", "mengetahui",
    ]
    missing = [f for f in required_fields if not str(payload.get(f, "")).strip()]
    if missing:
        return jsonify({
            "success": False,
            "message": f"Field wajib belum lengkap: {', '.join(missing)}"
        }), 400

    try:
        jumlah_liter = float(payload["jumlah_liter"])
        uang = float(payload["uang"])
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Jumlah Liter dan Uang Sebanyak harus berupa angka."
        }), 400

    if jumlah_liter <= 0 or uang <= 0:
        return jsonify({
            "success": False,
            "message": "Jumlah Liter dan Uang Sebanyak harus lebih besar dari 0."
        }), 400

    waktu_input = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    nota_data = {
        "tanggal_nota": payload["tanggal_nota"],
        "nomor_polisi": payload["nomor_polisi"].strip(),
        "jenis_bbm": payload["jenis_bbm"].strip(),
        "jumlah_liter": jumlah_liter,
        "uang": uang,
        "terbilang": payload["terbilang"].strip(),
        "mengetahui": payload["mengetahui"].strip(),
        "waktu_input": waktu_input,
    }

    try:
        # 1) Simpan ke SQLite
        new_id = db.insert_nota(nota_data)
        nota_data["id"] = new_id

        # 2) Tambahkan ke rekap Excel
        tambah_data_excel(nota_data)

        # 3) Generate PDF
        jenis_bbm_urutan = [p["jenis_bbm"] for p in db.get_bbm_prices()]
        pdf_filename = generate_nota_pdf(nota_data, jenis_bbm_urutan=jenis_bbm_urutan)
        db.update_pdf_file(new_id, pdf_filename)

    except Exception as exc:
        return jsonify({
            "success": False,
            "message": f"Gagal menyimpan data: {exc}"
        }), 500

    return jsonify({
        "success": True,
        "message": "Data berhasil disimpan.",
        "nota_id": new_id,
        "pdf_url": url_for("serve_pdf", filename=pdf_filename),
    })


# --------------------------------------------------------------------------
# API - Riwayat nota (opsional, untuk pengembangan lanjutan)
# --------------------------------------------------------------------------
@app.route("/api/history", methods=["GET"])
@login_required
def api_history():
    return jsonify({"success": True, "data": db.get_nota_history()})


# --------------------------------------------------------------------------
# Serve file PDF hasil generate
# --------------------------------------------------------------------------
@app.route("/generated_pdf/<path:filename>")
@login_required
def serve_pdf(filename):
    folder = os.path.join(BASE_DIR, "generated_pdf")
    return send_from_directory(folder, filename)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
if __name__ == "__main__":
    db.init_db()
    print("=" * 60)
    print(f"  {APP_NAME} - Kejaksaan Tinggi Jawa Tengah")
    print("  Aplikasi berjalan di: http://127.0.0.1:5000")
    print("  Login default -> username: admin | password: kejati")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)
