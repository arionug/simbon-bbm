"""
Modul untuk membuat dokumen PDF Nota Bon BBM menggunakan ReportLab.
Format mengikuti template manual "Nota Pengajuan Anggaran" yang
sebelumnya dipakai secara manual (Word/Excel).
Tidak memerlukan library eksternal / binary tambahan (murni Python)
sehingga aplikasi tetap portabel dan mudah dipindahkan.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "static", "img", "logo-kejati.png")
OUTPUT_DIR = os.path.join(BASE_DIR, "generated_pdf")

WARNA_UTAMA = colors.HexColor("#005A32")
WARNA_EMAS = colors.HexColor("#d4af37")

# Pihak yang selalu menjadi sumber dana (teks tetap, tidak diinput dari form)
TELAH_DITERIMA_DARI = "Kepala Kejaksaan Tinggi Jawa Tengah"


def generate_nota_pdf(nota: dict, jenis_bbm_urutan=None) -> str:
    """
    nota: dict berisi field:
      id, tanggal_nota, nomor_polisi, jenis_bbm, jumlah_liter,
      uang, terbilang, mengetahui, waktu_input
    jenis_bbm_urutan: daftar jenis BBM yang ditampilkan pada rincian
      "Guna Membayar" (mengikuti data harga BBM terkini di menu Pengaturan).
      Jika tidak diberikan, hanya jenis BBM pada nota ini yang ditampilkan.
    Mengembalikan nama file PDF yang dihasilkan (relatif terhadap generated_pdf/).
    """
    jenis_bbm_urutan = jenis_bbm_urutan or [nota["jenis_bbm"]]
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"nota_{nota['id']:06d}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        title=f"Nota Pengajuan Anggaran {nota['nomor_polisi']}",
    )

    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        "JudulNota", parent=styles["Heading1"], alignment=TA_CENTER,
        fontSize=14, textColor=colors.black, spaceAfter=0, fontName="Helvetica-Bold",
        underlineWidth=1,
    )
    style_instansi = ParagraphStyle(
        "Instansi", parent=styles["Normal"], alignment=TA_LEFT,
        fontSize=18, fontName="Helvetica-Bold", textColor=WARNA_UTAMA, spaceAfter=8,
    )
    style_instansi_sub = ParagraphStyle(
        "InstansiSub", parent=styles["Normal"], alignment=TA_LEFT,
        fontSize=11, textColor=colors.HexColor("#000000")
    )
    style_normal = ParagraphStyle(
        "NormalKiri", parent=styles["Normal"], alignment=TA_LEFT, fontSize=10.5,
    )
    style_normal_bold = ParagraphStyle(
        "NormalBold", parent=styles["Normal"], alignment=TA_LEFT, fontSize=10.5,
        fontName="Helvetica-Bold",
    )
    style_center = ParagraphStyle(
        "NormalTengah", parent=styles["Normal"], alignment=TA_CENTER, fontSize=10.5,
    )

    elements = []

    # ---------- Kop surat ----------
    logo_cell = ""
    if os.path.exists(LOGO_PATH):
        logo_cell = Image(LOGO_PATH, width=2.5 * cm, height=2.5 * cm)

    kop_text = Paragraph("KEJAKSAAN TINGGI JAWA TENGAH", style_instansi)
    kop_sub = Paragraph("Jl. Pahlawan No.14, Pleburan, Kota Semarang", style_instansi_sub)
    kop_table = Table(
        [[logo_cell, [kop_text, kop_sub]]],
        colWidths=[3.1 * cm, 14.4 * cm],
    )
    kop_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(kop_table)
    elements.append(Spacer(1, 6))

    # garis pemisah kop
    line_table = Table([[""]], colWidths=[17 * cm], rowHeights=[2])
    line_table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 1.6, WARNA_EMAS),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 16))

    # ---------- Judul dokumen ----------
    elements.append(Paragraph("<u>NOTA PENGAJUAN ANGGARAN</u>", style_title))
    elements.append(Spacer(1, 20))

    # ---------- Rincian Guna Membayar (per jenis BBM) ----------
    fuel_rows = []
    for jenis in jenis_bbm_urutan:
        if jenis == nota["jenis_bbm"]:
            nilai_liter = f"{format_liter(nota['jumlah_liter'])} Liter"
        else:
            nilai_liter = ""
        fuel_rows.append([
            Paragraph(jenis, style_normal),
            Paragraph(":", style_normal),
            Paragraph(nilai_liter, style_normal),
        ])
    fuel_table = Table(fuel_rows, colWidths=[3.2 * cm, 0.4 * cm, 3.2 * cm])
    fuel_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))

    # ---------- Tabel data utama ----------
    body_rows = [
        [
            Paragraph("Telah diterima dari", style_normal), Paragraph(":", style_normal),
            Paragraph(TELAH_DITERIMA_DARI, style_normal),
            "", "", "",
        ],
        [
            Paragraph("Uang sebanyak", style_normal), Paragraph(":", style_normal),
            Paragraph(f"Rp {format_rupiah(nota['uang'])}", style_normal),
            "", "", "",
        ],
        [
            Paragraph("Guna membayar", style_normal), Paragraph(":", style_normal), 
            Paragraph("Pembelian Bahan Bakar Jenis", style_normal), fuel_table, "", "",
        ],
        [
            Paragraph("Untuk", style_normal), Paragraph(":", style_normal), "",
            Paragraph("Nomor Polisi", style_normal), Paragraph(":", style_normal),
            Paragraph(nota["nomor_polisi"], style_normal_bold),
        ],
        [
            Paragraph("Terbilang", style_normal), Paragraph(":", style_normal),
            Paragraph(nota["terbilang"], style_normal),
            "", "", "",
        ],
    ]
    body_table = Table(
        body_rows,
        colWidths=[3.6 * cm, 0.4 * cm, 6.0 * cm, 3.2 * cm, 0.4 * cm, 3.4 * cm],
    )
    body_table.setStyle(TableStyle([
        ("SPAN", (3, 2), (5, 2)),   # baris "Guna membayar" -> rincian BBM merge kolom kanan
        ("SPAN", (2, 0), (5, 0)),
        ("SPAN", (2, 4), (5, 4)),
        ("FONTSIZE", (0, 0), (-1, -1), 10.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(body_table)
    elements.append(Spacer(1, 30))

    # ---------- Tanggal & Area tanda tangan ----------
    kota_tanggal = f"Semarang, {format_tanggal_panjang(nota['tanggal_nota'])}"
    style_kanan = ParagraphStyle("Kanan", parent=styles["Normal"], alignment=TA_RIGHT, fontSize=10.5)

    ttd_data = [
        [Paragraph("Mengetahui,", style_normal), Paragraph(kota_tanggal, style_kanan)],
        ["", Paragraph("Yang Menerima,", style_kanan)],
        [Spacer(1, 46), Spacer(1, 46)],
        ["", Paragraph(f"<b>{nota['mengetahui']}</b>", style_kanan)],
    ]
    ttd_table = Table(ttd_data, colWidths=[8.5 * cm, 8.5 * cm])
    ttd_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(ttd_table)

    elements.append(Spacer(1, 10))
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"], fontSize=9,
        textColor=colors.HexColor("#7A7979"), alignment=TA_CENTER
    )
    elements.append(Paragraph(
        f"Dokumen dibuat otomatis oleh SIMBON Kejati Jateng pada {nota['waktu_input']}",
        footer_style
    ))

    doc.build(elements)
    return filename


def format_rupiah(nominal) -> str:
    try:
        nominal = int(round(float(nominal)))
    except (ValueError, TypeError):
        return str(nominal)
    return f"{nominal:,}".replace(",", ".")


def format_liter(nilai) -> str:
    """Format angka liter dengan koma sebagai desimal, sesuai gaya penulisan Indonesia."""
    try:
        nilai = float(nilai)
    except (ValueError, TypeError):
        return str(nilai)
    if nilai == int(nilai):
        return str(int(nilai))
    return f"{nilai:.2f}".rstrip("0").rstrip(".").replace(".", ",")


BULAN_ID = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]


def format_tanggal_panjang(tanggal_str: str) -> str:
    """tanggal_str format: YYYY-MM-DD -> '7 September 2026'"""
    try:
        y, m, d = tanggal_str.split("-")
        return f"{int(d)} {BULAN_ID[int(m)]} {y}"
    except Exception:
        return tanggal_str