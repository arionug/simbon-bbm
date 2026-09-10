"""
Modul koneksi & inisialisasi database SQLite lokal (database.db).
Menyimpan seluruh data secara lokal di dalam folder project.
"""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

# Data awal hasil impor dari "DATA SUPIR BBM KENDARAAN.xlsx"
VEHICLES_AWAL = [
    {"nomor_polisi": "B 1924 KJA", "driver": "SATRIA", "jenis_bbm": "Pertamina Dex"},
    {"nomor_polisi": "H 1103 XZ", "driver": "ANDRI", "jenis_bbm": "Pertamina Dex"},
    {"nomor_polisi": "H 1142 XG", "driver": "ANDRI", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1755 XR", "driver": "SATRIA", "jenis_bbm": "Pertamina Dex"},
    {"nomor_polisi": "H 1764 XR", "driver": "FAHRI", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1275 XR", "driver": "WANDI", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1940 XR", "driver": "DANI", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1938 XR", "driver": "AGUS", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1934 XR", "driver": "AGUS", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1936 XR", "driver": "AGUS", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1939 XR", "driver": "AGUS", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1937 XR", "driver": "TOBI", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1935 XR", "driver": "DAMAR", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1715 XR", "driver": "LUKMAN", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1274 XR", "driver": "AGUS", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1756 XR", "driver": "AGUS", "jenis_bbm": "Pertamina Dex"},
    {"nomor_polisi": "H 8572 XG", "driver": "AGUS", "jenis_bbm": "Pertamina Dex"},
    {"nomor_polisi": "H 8151 XG", "driver": "AGUS", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1350 XG", "driver": "AGUS", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1377 XR", "driver": "AGUS", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 7182 XG", "driver": "AGUS", "jenis_bbm": "Pertamina Dex"},
    {"nomor_polisi": "H 8537 XG", "driver": "SATRIA", "jenis_bbm": "Pertamina Dex"},
    {"nomor_polisi": "H 8459 XG", "driver": "WANDI", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1244 XZ", "driver": "TOBI", "jenis_bbm": "Pertamina Dex"},
    {"nomor_polisi": "H 1285 XZ", "driver": "TOBI", "jenis_bbm": "Pertamina Dex"},
    {"nomor_polisi": "H 1535 GX", "driver": "AGUS", "jenis_bbm": "Pertamax"},
    {"nomor_polisi": "H 1522 SQ", "driver": "TOBI", "jenis_bbm": "Pertamax"},
]

DRIVERS_AWAL = [
    "AGUS", "ANDRI", "DAMAR", "DANI", "FAHRI", "LUKMAN", "SATRIA", "TOBI", "WANDI",
]

BBM_PRICES_AWAL = {
    "Pertamax": 15950,
    "Pertamina Dex": 25200,
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _ensure_column(conn, table, column, coltype):
    cols = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")


def init_db():
    is_new = not os.path.exists(DB_PATH)
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomor_polisi TEXT UNIQUE NOT NULL
        )
    """)
    _ensure_column(conn, "vehicles", "driver", "TEXT")
    _ensure_column(conn, "vehicles", "jenis_bbm", "TEXT")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT UNIQUE NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bbm_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jenis_bbm TEXT UNIQUE NOT NULL,
            harga REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS nota_bbm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal_nota TEXT NOT NULL,
            nomor_polisi TEXT NOT NULL,
            jenis_bbm TEXT NOT NULL,
            jumlah_liter REAL NOT NULL,
            uang REAL NOT NULL,
            terbilang TEXT NOT NULL,
            mengetahui TEXT NOT NULL,
            waktu_input TEXT NOT NULL,
            pdf_file TEXT
        )
    """)

    # Seed data kendaraan, driver, dan harga BBM.
    # Memakai INSERT OR IGNORE supaya aman dijalankan berulang kali
    # tanpa menghapus/menimpa data yang sudah diubah lewat menu Pengaturan.
    for v in VEHICLES_AWAL:
        cur.execute(
            "INSERT OR IGNORE INTO vehicles (nomor_polisi, driver, jenis_bbm) VALUES (?, ?, ?)",
            (v["nomor_polisi"], v["driver"], v["jenis_bbm"]),
        )

    for nama in DRIVERS_AWAL:
        cur.execute("INSERT OR IGNORE INTO drivers (nama) VALUES (?)", (nama,))

    for jenis, harga in BBM_PRICES_AWAL.items():
        cur.execute(
            "INSERT OR IGNORE INTO bbm_prices (jenis_bbm, harga) VALUES (?, ?)",
            (jenis, harga),
        )

    conn.commit()
    conn.close()
    return is_new


# --------------------------------------------------------------------------
# Kendaraan
# --------------------------------------------------------------------------
def get_vehicles():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, nomor_polisi, driver, jenis_bbm FROM vehicles ORDER BY nomor_polisi ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_vehicle(nomor_polisi: str, driver: str = None, jenis_bbm: str = None):
    nomor_polisi = (nomor_polisi or "").strip().upper()
    if not nomor_polisi:
        return False, "Nomor polisi tidak boleh kosong."
    driver = driver.strip().upper() if driver else None
    jenis_bbm = jenis_bbm.strip() if jenis_bbm else None
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO vehicles (nomor_polisi, driver, jenis_bbm) VALUES (?, ?, ?)",
            (nomor_polisi, driver, jenis_bbm),
        )
        conn.commit()
        return True, "Kendaraan berhasil ditambahkan."
    except sqlite3.IntegrityError:
        return False, "Nomor polisi sudah terdaftar."
    finally:
        conn.close()


def update_vehicle(vehicle_id: int, nomor_polisi: str = None, driver: str = None, jenis_bbm: str = None):
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)).fetchone()
        if not row:
            return False, "Kendaraan tidak ditemukan."
        new_nopol = nomor_polisi.strip().upper() if nomor_polisi else row["nomor_polisi"]
        new_driver = driver.strip().upper() if driver else None
        new_jenis = jenis_bbm.strip() if jenis_bbm else None
        conn.execute(
            "UPDATE vehicles SET nomor_polisi = ?, driver = ?, jenis_bbm = ? WHERE id = ?",
            (new_nopol, new_driver, new_jenis, vehicle_id),
        )
        conn.commit()
        return True, "Data kendaraan berhasil disimpan."
    except sqlite3.IntegrityError:
        return False, "Nomor polisi sudah terdaftar untuk kendaraan lain."
    finally:
        conn.close()


def delete_vehicle(vehicle_id: int):
    conn = get_db()
    conn.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
    conn.commit()
    conn.close()


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def get_drivers():
    conn = get_db()
    rows = conn.execute("SELECT id, nama FROM drivers ORDER BY nama ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_driver(nama: str):
    nama = (nama or "").strip().upper()
    if not nama:
        return False, "Nama driver tidak boleh kosong."
    conn = get_db()
    try:
        conn.execute("INSERT INTO drivers (nama) VALUES (?)", (nama,))
        conn.commit()
        return True, "Driver berhasil ditambahkan."
    except sqlite3.IntegrityError:
        return False, "Nama driver sudah terdaftar."
    finally:
        conn.close()


def delete_driver(driver_id: int):
    conn = get_db()
    conn.execute("DELETE FROM drivers WHERE id = ?", (driver_id,))
    conn.commit()
    conn.close()


# --------------------------------------------------------------------------
# Harga BBM
# --------------------------------------------------------------------------
def get_bbm_prices():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, jenis_bbm, harga FROM bbm_prices ORDER BY jenis_bbm ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_bbm_price(jenis_bbm: str, harga):
    jenis_bbm = (jenis_bbm or "").strip()
    if not jenis_bbm:
        return False, "Jenis BBM tidak boleh kosong."
    try:
        harga = float(harga)
    except (ValueError, TypeError):
        return False, "Harga harus berupa angka."
    if harga <= 0:
        return False, "Harga harus lebih besar dari 0."
    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM bbm_prices WHERE jenis_bbm = ?", (jenis_bbm,)
        ).fetchone()
        if existing:
            conn.execute("UPDATE bbm_prices SET harga = ? WHERE jenis_bbm = ?", (harga, jenis_bbm))
        else:
            conn.execute(
                "INSERT INTO bbm_prices (jenis_bbm, harga) VALUES (?, ?)", (jenis_bbm, harga)
            )
        conn.commit()
        return True, "Harga BBM berhasil disimpan."
    finally:
        conn.close()


def delete_bbm_price(price_id: int):
    conn = get_db()
    conn.execute("DELETE FROM bbm_prices WHERE id = ?", (price_id,))
    conn.commit()
    conn.close()


# --------------------------------------------------------------------------
# Nota BBM
# --------------------------------------------------------------------------
def insert_nota(data: dict) -> int:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO nota_bbm
        (tanggal_nota, nomor_polisi, jenis_bbm, jumlah_liter, uang, terbilang, mengetahui, waktu_input)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["tanggal_nota"], data["nomor_polisi"], data["jenis_bbm"],
        data["jumlah_liter"], data["uang"], data["terbilang"],
        data["mengetahui"], data["waktu_input"],
    ))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_pdf_file(nota_id: int, pdf_file: str):
    conn = get_db()
    conn.execute("UPDATE nota_bbm SET pdf_file = ? WHERE id = ?", (pdf_file, nota_id))
    conn.commit()
    conn.close()


def get_nota_history(limit: int = 50):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM nota_bbm ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
