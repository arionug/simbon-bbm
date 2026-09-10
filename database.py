"""
Modul koneksi & inisialisasi database SQLite lokal (database.db).
Menyimpan seluruh data secara lokal di dalam folder project.
"""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

VEHICLES_AWAL = ["H 1234 AA", "H 5678 BB", "H 9012 CC", "H 3456 DD"]
JENIS_BBM_AWAL = ["Pertamax", "Dexlite", "Pertamina Dex"]
MENGETAHUI_AWAL = ["ANDRI", "BOWO", "WANDI", "AGUS", "SATRIA", "INDRA", "FAHRI"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


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

    # Seed data kendaraan awal jika tabel masih kosong
    cur.execute("SELECT COUNT(*) as c FROM vehicles")
    if cur.fetchone()["c"] == 0:
        for plat in VEHICLES_AWAL:
            try:
                cur.execute("INSERT INTO vehicles (nomor_polisi) VALUES (?)", (plat,))
            except sqlite3.IntegrityError:
                pass

    conn.commit()
    conn.close()
    return is_new


def get_vehicles():
    conn = get_db()
    rows = conn.execute("SELECT id, nomor_polisi FROM vehicles ORDER BY nomor_polisi ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_vehicle(nomor_polisi: str):
    nomor_polisi = nomor_polisi.strip().upper()
    if not nomor_polisi:
        return False, "Nomor polisi tidak boleh kosong."
    conn = get_db()
    try:
        conn.execute("INSERT INTO vehicles (nomor_polisi) VALUES (?)", (nomor_polisi,))
        conn.commit()
        return True, "Kendaraan berhasil ditambahkan."
    except sqlite3.IntegrityError:
        return False, "Nomor polisi sudah terdaftar."
    finally:
        conn.close()


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
