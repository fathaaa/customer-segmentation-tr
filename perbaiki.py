import os, re, struct, zlib, zipfile, shutil
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.join(BASE, "PKB Details 2025")
RUSAK = os.path.join(FOLDER, "_rusak")
os.makedirs(RUSAK, exist_ok=True)

KODE = ["15-26-26", "15-27-30", "15-29-32", "15-30-51",
        "15-33-06", "15-48-29", "16-33-06"]


def baca_zip_terpotong(buf):
    """Ambil semua bagian zip yang masih utuh/sebagian dari file rusak."""
    pos, entries, terpotong = 0, [], False
    while buf[pos:pos + 4] == b"PK\x03\x04":
        (_, _, flags, method, _, _, _, csize, _, nlen, elen) = struct.unpack(
            "<4sHHHHHIIIHH", buf[pos:pos + 30])
        name = buf[pos + 30:pos + 30 + nlen].decode("utf-8", "replace")
        start = pos + 30 + nlen + elen
        if method == 8:
            d = zlib.decompressobj(-15)
            try:
                data = d.decompress(buf[start:])
            except zlib.error:
                data = b""
            if not d.eof:
                terpotong = True
                if name.startswith("xl/worksheets/") and data:
                    p = b"x:" if b"<x:row" in data else b""
                    tutup = b"</" + p + b"row>"
                    i = data.rfind(tutup)
                    if i != -1:
                        data = (data[:i + len(tutup)]
                                + b"</" + p + b"sheetData></" + p + b"worksheet>")
                entries.append((name, data))
                break
            pos = len(buf) - len(d.unused_data)
            if flags & 8:
                pos += 16 if buf[pos:pos + 4] == b"PK\x07\x08" else 12
        else:
            data = buf[start:start + csize]
            pos = start + csize
        entries.append((name, data))
    return entries, terpotong


def lengkapi(entries):
    """Buat ulang file pendukung yang hilang supaya xlsx bisa dibuka."""
    names = {n for n, _ in entries}
    wb = dict(entries).get("xl/workbook.xml", b"")
    sheet = next((n for n in names if n.startswith("xl/worksheets/")
                  and n.endswith(".xml")), None)
    extra = []

    if "xl/_rels/workbook.xml.rels" not in names and sheet:
        m = re.search(rb'r:id="([^"]+)"', wb)
        rid = m.group(1).decode() if m else "rId1"
        rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                f'Target="{sheet[len("xl/"):]}"/></Relationships>')
        extra.append(("xl/_rels/workbook.xml.rels", rels.encode()))

    if "_rels/.rels" not in names:
        rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
                'Target="xl/workbook.xml"/></Relationships>')
        extra.append(("_rels/.rels", rels.encode()))

    if "[Content_Types].xml" not in names:
        ov = ['<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>']
        if sheet:
            ov.append(f'<Override PartName="/{sheet}" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
        if "xl/sharedStrings.xml" in names:
            ov.append('<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>')
        if "xl/styles.xml" in names:
            ov.append('<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>')
        ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="xml" ContentType="application/xml"/>'
              + "".join(ov) + '</Types>')
        extra.append(("[Content_Types].xml", ct.encode()))

    return entries + extra


def repair(src, dst):
    buf = open(src, "rb").read()
    entries, terpotong = baca_zip_terpotong(buf)
    entries = lengkapi(entries)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in entries:
            z.writestr(name, data)
    return [n for n, _ in entries], terpotong


for kode in KODE:
    nama = f"WO Service%2c Parts and Materials Advanced Find View 12-10-2026 {kode}.xlsx"
    asli = os.path.join(FOLDER, nama)
    cadangan = os.path.join(RUSAK, nama)
    if not os.path.exists(cadangan):
        shutil.move(asli, cadangan)          # file rusak disimpan di _rusak
    bagian, potong = repair(cadangan, asli)  # versi perbaikan, nama sama
    try:
        df = pd.read_excel(asli, dtype=str, engine="calamine", usecols=["BU", "WO"])
        wo_ok = df["WO"].notna().mean() * 100
        print(f"{kode}: OK, {len(df):,} baris | WO terisi {wo_ok:.0f}% | "
              f"terpotong: {potong} | sharedStrings: {'xl/sharedStrings.xml' in bagian}")
    except Exception as e:
        print(f"{kode}: MASIH GAGAL ({repr(e)[:90]}) | bagian: {bagian}")