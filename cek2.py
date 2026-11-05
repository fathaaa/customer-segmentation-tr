import pandas as pd, glob, os

BASE = os.path.dirname(os.path.abspath(__file__))

# 1) Semua WO yang alamatnya belum ketemu di hasil lookup
hilang = set()
for f in glob.glob(os.path.join(BASE, "*_dengan_alamat.csv")):
    for ch in pd.read_csv(f, dtype=str, usecols=["WO", "Kecamatan"], chunksize=500_000):
        hilang.update(ch.loc[ch["Kecamatan"].isna(), "WO"].dropna().unique())
print(f"WO unik yang tidak ketemu: {len(hilang):,}")

# 2) File belum_lengkap (header di baris 2)
bl = pd.read_excel(os.path.join(BASE, "Address", "fiks_alamat_belum_lengkap.xlsx"),
                   header=1, dtype=str, engine="calamine").iloc[:, :11]
bl.columns = ["PKB", "Chassis", "Kec_src", "Kota_src", "Prov_src",
              "Alamat", "Kec", "Kota", "Prov", "Status", "Metode"]
bl["PKB"] = bl["PKB"].str.strip()
print(f"\nbelum_lengkap: {len(bl):,} baris, {bl['PKB'].nunique():,} PKB unik")
print("\nStatus:")
print(bl["Status"].value_counts(dropna=False).to_string())

# 3) Berapa dari yang hilang ada di belum_lengkap?
set_bl = set(bl["PKB"])
ada = hilang & set_bl
print(f"\nDari yang tidak ketemu, ada di belum_lengkap: {len(ada):,} "
      f"({len(ada)/len(hilang)*100:.1f}%)")
print(f"Tidak ada di mana pun                       : {len(hilang - set_bl):,}")

sub = bl[bl["PKB"].isin(ada)].drop_duplicates("PKB")
print(f"\nDari {len(sub):,} itu, yang terisi sebagian:")
print(f"  Kecamatan : {sub['Kec'].notna().sum():,}")
print(f"  Kota/Kab  : {sub['Kota'].notna().sum():,}")
print(f"  Provinsi  : {sub['Prov'].notna().sum():,}")

contoh = sorted(hilang - set_bl)[:10]
print("\nContoh WO yang tidak ada di mana pun:", contoh)