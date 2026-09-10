"""
Modul konversi angka ke terbilang (Bahasa Indonesia).
Digunakan untuk mengisi otomatis field 'Terbilang' berdasarkan nilai Rupiah.
"""

SATUAN = [
    "", "Satu", "Dua", "Tiga", "Empat", "Lima",
    "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh",
    "Sebelas"
]


def angka_ke_kata(n: int) -> str:
    n = int(n)
    if n < 12:
        return SATUAN[n]
    elif n < 20:
        return angka_ke_kata(n - 10) + " Belas"
    elif n < 100:
        return angka_ke_kata(n // 10) + " Puluh" + (
            " " + angka_ke_kata(n % 10) if n % 10 != 0 else ""
        )
    elif n < 200:
        return "Seratus" + (" " + angka_ke_kata(n - 100) if n - 100 != 0 else "")
    elif n < 1000:
        return angka_ke_kata(n // 100) + " Ratus" + (
            " " + angka_ke_kata(n % 100) if n % 100 != 0 else ""
        )
    elif n < 2000:
        return "Seribu" + (" " + angka_ke_kata(n - 1000) if n - 1000 != 0 else "")
    elif n < 1000000:
        return angka_ke_kata(n // 1000) + " Ribu" + (
            " " + angka_ke_kata(n % 1000) if n % 1000 != 0 else ""
        )
    elif n < 1000000000:
        return angka_ke_kata(n // 1000000) + " Juta" + (
            " " + angka_ke_kata(n % 1000000) if n % 1000000 != 0 else ""
        )
    elif n < 1000000000000:
        return angka_ke_kata(n // 1000000000) + " Miliar" + (
            " " + angka_ke_kata(n % 1000000000) if n % 1000000000 != 0 else ""
        )
    else:
        return angka_ke_kata(n // 1000000000000) + " Triliun" + (
            " " + angka_ke_kata(n % 1000000000000) if n % 1000000000000 != 0 else ""
        )


def rupiah_terbilang(nominal) -> str:
    try:
        nominal = int(round(float(nominal)))
    except (ValueError, TypeError):
        return ""
    if nominal == 0:
        return "Nol Rupiah"
    if nominal < 0:
        return "Minus " + angka_ke_kata(abs(nominal)).strip() + " Rupiah"
    hasil = angka_ke_kata(nominal).strip()
    # Rapikan spasi ganda
    hasil = " ".join(hasil.split())
    return hasil + " Rupiah"
