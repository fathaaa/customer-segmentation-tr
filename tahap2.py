import os

import pandas as pd


BASE = os.path.dirname(os.path.abspath(__file__))
ADDRESS_FILE = os.path.join(BASE, "Address", "fiks_alamat_belum_lengkap.xlsx")
INPUT_FILES = [
    os.path.join(BASE, "PKB Details 2025_dengan_alamat.csv"),
    os.path.join(BASE, "PKB Details 2026_dengan_alamat.csv"),
]
CHUNK_SIZE = 500_000


def kosong(series):
    """Anggap nilai NaN dan string kosong/whitespace sebagai kosong."""
    return series.isna() | series.astype("string").str.strip().eq("").fillna(False)


def main():
    alamat = pd.read_excel(
        ADDRESS_FILE, header=1, dtype=str, engine="calamine"
    ).iloc[:, :11]
    alamat.columns = [
        "PKB", "Chassis No", "Kecamatan Asli", "Kota/Kabupaten Asli",
        "Provinsi Asli", "Alamat_Asli", "Kecamatan (hasil)",
        "Kota/Kabupaten (hasil)", "Provinsi (hasil)", "Status", "Metode",
    ]
    alamat["PKB"] = alamat["PKB"].astype("string").str.strip()
    alamat = alamat.dropna(subset=["PKB"])
    alamat = alamat.drop_duplicates("PKB", keep="first").set_index("PKB")
    print(f"belum_lengkap: {len(alamat):,} PKB unik", flush=True)

    for input_path in INPUT_FILES:
        if not os.path.exists(input_path):
            print(f"Lewati, file tidak ditemukan: {os.path.basename(input_path)}", flush=True)
            continue

        output_path = os.path.splitext(input_path)[0].replace(
            "_dengan_alamat", "_tahap2"
        ) + ".csv"
        if os.path.exists(output_path):
            raise FileExistsError(
                f"Output sudah ada, tidak ditimpa: {output_path}"
            )

        total = 0
        first_chunk = True
        pertama = True
        for chunk in pd.read_csv(input_path, dtype=str, chunksize=CHUNK_SIZE):
            if "WO" not in chunk.columns or "Kecamatan" not in chunk.columns:
                raise ValueError(f"Kolom WO/Kecamatan tidak ditemukan: {input_path}")

            wo = chunk["WO"].astype("string").str.strip()
            kec_kosong = kosong(chunk["Kecamatan"])
            cocok = kec_kosong & wo.isin(alamat.index)

            # Baris yang sudah memiliki kecamatan dinyatakan lengkap.
            chunk["Status_Alamat"] = pd.NA
            chunk.loc[~kec_kosong, "Status_Alamat"] = "Lengkap"

            # Isi alamat tambahan hanya untuk WO yang belum memiliki kecamatan.
            for kolom in ("Alamat_Asli", "Status_Alamat"):
                if kolom not in chunk.columns:
                    chunk[kolom] = pd.NA

            chunk.loc[cocok, "Alamat_Asli"] = wo[cocok].map(alamat["Alamat_Asli"])
            chunk.loc[cocok, "Status_Alamat"] = wo[cocok].map(alamat["Status"])
            for kolom_csv, kolom_sumber in (
                ("Kecamatan", "Kecamatan (hasil)"),
                ("Kota/Kabupaten", "Kota/Kabupaten (hasil)"),
                ("Provinsi", "Provinsi (hasil)"),
            ):
                if kolom_csv not in chunk.columns:
                    chunk[kolom_csv] = pd.NA
                nilai = wo[cocok].map(alamat[kolom_sumber])
                ada_nilai = ~kosong(nilai)
                chunk.loc[nilai.index[ada_nilai], kolom_csv] = nilai[ada_nilai]

            chunk.loc[kec_kosong & ~cocok, "Status_Alamat"] = "Tidak ada data alamat"
            chunk.to_csv(
                output_path,
                mode="w" if first_chunk else "a",
                index=False,
                header=first_chunk,
                encoding="utf-8-sig" if first_chunk else "utf-8",
            )
            first_chunk = False
            total += len(chunk)

        print(f"Selesai: {os.path.basename(output_path)} ({total:,} baris)", flush=True)


if __name__ == "__main__":
    main()
