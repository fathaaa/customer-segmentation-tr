import pandas as pd
import glob, os

BASE = os.path.dirname(os.path.abspath(__file__))
ADDR_FILE = os.path.join(BASE, "Address", "Addres Final.xlsx")
PKB_COL = "WO"
KOLOM = ["BU", "WO", "Product Type", "Product", "Product Description",
         "Service Category", "Total Transaction Amount", "Created On"]

# 1) Address Final -> dictionary lookup
addr = pd.read_excel(ADDR_FILE, header=1, dtype=str, engine="calamine")
addr = addr.iloc[:, :4]
addr.columns = ["PKB", "Kecamatan", "Kota/Kabupaten", "Provinsi"]
addr["PKB"] = addr["PKB"].str.strip()
addr = addr.drop_duplicates("PKB").set_index("PKB")
print(f"Address Final: {len(addr):,} PKB unik", flush=True)

# 2) Proses file demi file
for tahun in ["PKB Details 2025", "PKB Details 2026"]:
    files = sorted(f for f in glob.glob(os.path.join(BASE, tahun, "*.xlsx"))
                   if not os.path.basename(f).startswith("~$"))
    out = os.path.join(BASE, f"{tahun}_dengan_alamat.csv")
    if os.path.exists(out):
        os.remove(out)

    print(f"\n{tahun}: {len(files)} file", flush=True)
    total = kosong = 0
    gagal = []
    pertama = True

    for i, f in enumerate(files, 1):
        try:
            df = pd.read_excel(f, dtype=str, engine="calamine", usecols=KOLOM)
        except Exception as e:
            gagal.append(os.path.basename(f))
            print(f"  [{i}/{len(files)}] GAGAL: {os.path.basename(f)}", flush=True)
            continue

        df[PKB_COL] = df[PKB_COL].str.strip()
        df["Kecamatan"] = df[PKB_COL].map(addr["Kecamatan"])
        df["Kota/Kabupaten"] = df[PKB_COL].map(addr["Kota/Kabupaten"])
        df["Provinsi"] = df[PKB_COL].map(addr["Provinsi"])
        df["Sumber_File"] = os.path.basename(f)

        df.to_csv(out, mode="w" if pertama else "a", header=pertama,
                  index=False, encoding="utf-8-sig" if pertama else "utf-8")
        pertama = False

        total += len(df)
        kosong += df["Kecamatan"].isna().sum()
        print(f"  [{i}/{len(files)}] {len(df):,} baris | kumulatif {total:,}", flush=True)

    print(f"\n  SELESAI {tahun}")
    print(f"  total baris        : {total:,}")
    print(f"  alamat tidak ketemu: {kosong:,}")
    print(f"  file gagal         : {len(gagal)} {gagal}")
    print(f"  tersimpan          : {out}", flush=True)