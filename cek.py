import pandas as pd, glob, os

BASE = os.path.dirname(os.path.abspath(__file__))
for f in sorted(glob.glob(os.path.join(BASE, "*_dengan_alamat.csv"))):
    hasil = {}
    for ch in pd.read_csv(f, dtype=str, usecols=["WO", "Kecamatan"], chunksize=500_000):
        ch = ch.drop_duplicates("WO")
        ch["bulan"] = ch["WO"].str.extract(r"PKB(\d{4})")[0]
        for b, g in ch.groupby("bulan"):
            t, k = hasil.get(b, (0, 0))
            hasil[b] = (t + len(g), k + g["Kecamatan"].isna().sum())
    print(os.path.basename(f))
    for b in sorted(hasil, key=str):
        t, k = hasil[b]
        print(f"  {b}: {t:,} WO | tidak ketemu {k:,} ({k/t*100:.0f}%)")