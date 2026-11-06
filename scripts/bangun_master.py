import os
import re
import sqlite3
from collections import Counter

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUTS = [
    os.path.join(BASE, "PKB Details 2025_tahap2.csv"),
    os.path.join(BASE, "PKB Details 2026_tahap2.csv"),
]
ADDRESS_FILES = [
    os.path.join(BASE, "Address", "fiks_alamat_lengkap.xlsx"),
    os.path.join(BASE, "Address", "fiks_alamat_belum_lengkap.xlsx"),
]
DATA_DIR = os.path.join(BASE, "data")
OUTPUT = os.path.join(DATA_DIR, "pkb_master.parquet")
DB_PATH = os.path.join(DATA_DIR, "pkb_master_work.sqlite")
CHUNK_SIZE = 500_000
SERVICES_TYPE = "Services"
OUTPUT_COLUMNS = [
    "WO", "BU", "Bulan_PKB", "Total_Revenue", "Revenue_Product",
    "Revenue_Jasa", "Jumlah_Baris", "Kecamatan", "Kota/Kabupaten",
    "Provinsi", "Status_Alamat", "Chassis", "Tanggal_PKB",
    "Service_Category",
]


def clean(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    return value or None


def first_present(series):
    for value in series:
        value = clean(value)
        if value is not None:
            return value
    return None


def month_from_wo(wo):
    match = re.search(r"PKB(\d{4})", wo or "")
    return match.group(1) if match else None


def datetime_to_text(value):
    if pd.isna(value):
        return None
    return pd.Timestamp(value).strftime("%Y-%m-%dT%H:%M:%S.%f")


def load_chassis_lookup():
    lookup = {}
    for path in ADDRESS_FILES:
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        columns = pd.read_excel(
            path, header=1, nrows=0, dtype=str, engine="calamine"
        ).columns.tolist()
        pkb_column = "PKB" if "PKB" in columns else columns[0]
        if "Chassis No" not in columns:
            raise ValueError(f"Kolom Chassis No tidak ditemukan: {path}")
        df = pd.read_excel(
            path, header=1, dtype=str, engine="calamine",
            usecols=[pkb_column, "Chassis No"],
        )
        for pkb, chassis in zip(df[pkb_column], df["Chassis No"]):
            pkb, chassis = clean(pkb), clean(chassis)
            if pkb and chassis:
                # File lengkap diproses lebih dahulu; nilai terisi pertama dipertahankan.
                lookup.setdefault(pkb, chassis)
    return lookup


def initialize_db(conn):
    conn.execute("""
        CREATE TABLE master (
            WO TEXT PRIMARY KEY,
            BU TEXT,
            Bulan_PKB TEXT,
            Total_Revenue REAL NOT NULL,
            Revenue_Product REAL NOT NULL,
            Revenue_Jasa REAL NOT NULL,
            Jumlah_Baris INTEGER NOT NULL,
            Kecamatan TEXT,
            Kota_Kabupaten TEXT,
            Provinsi TEXT,
            Status_Alamat TEXT,
            Tanggal_PKB TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE service_category_counts (
            WO TEXT NOT NULL,
            Service_Category TEXT NOT NULL,
            Frequency INTEGER NOT NULL,
            PRIMARY KEY (WO, Service_Category)
        )
    """)


UPSERT = """
    INSERT INTO master VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(WO) DO UPDATE SET
        BU = COALESCE(master.BU, excluded.BU),
        Bulan_PKB = COALESCE(master.Bulan_PKB, excluded.Bulan_PKB),
        Total_Revenue = master.Total_Revenue + excluded.Total_Revenue,
        Revenue_Product = master.Revenue_Product + excluded.Revenue_Product,
        Revenue_Jasa = master.Revenue_Jasa + excluded.Revenue_Jasa,
        Jumlah_Baris = master.Jumlah_Baris + excluded.Jumlah_Baris,
        Kecamatan = COALESCE(master.Kecamatan, excluded.Kecamatan),
        Kota_Kabupaten = COALESCE(master.Kota_Kabupaten, excluded.Kota_Kabupaten),
        Provinsi = COALESCE(master.Provinsi, excluded.Provinsi),
        Status_Alamat = COALESCE(master.Status_Alamat, excluded.Status_Alamat),
        Tanggal_PKB = CASE
            WHEN excluded.Tanggal_PKB IS NULL THEN master.Tanggal_PKB
            WHEN master.Tanggal_PKB IS NULL OR excluded.Tanggal_PKB < master.Tanggal_PKB
                THEN excluded.Tanggal_PKB
            ELSE master.Tanggal_PKB
        END
"""


def process_inputs(conn):
    for path in INPUTS:
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        for chunk in pd.read_csv(path, dtype=str, chunksize=CHUNK_SIZE):
            required = [
                "WO", "BU", "Product Type", "Service Category",
                "Total Transaction Amount", "Created On", "Kecamatan",
                "Kota/Kabupaten", "Provinsi", "Status_Alamat",
            ]
            missing = [column for column in required if column not in chunk.columns]
            if missing:
                raise ValueError(f"Kolom tidak ditemukan di {path}: {missing}")

            chunk["WO"] = chunk["WO"].map(clean)
            chunk = chunk.dropna(subset=["WO"])
            if chunk.empty:
                continue
            chunk["_service_category"] = chunk["Service Category"].map(clean)
            chunk["_created_on"] = pd.to_datetime(
                chunk["Created On"], format="mixed", errors="coerce"
            )
            amount = pd.to_numeric(
                chunk["Total Transaction Amount"].str.replace(",", "", regex=False),
                errors="coerce",
            ).fillna(0)
            is_service = chunk["Product Type"].astype("string").str.strip().eq(SERVICES_TYPE)
            chunk["_amount"] = amount
            chunk["_product"] = amount.where(~is_service, 0)
            chunk["_service"] = amount.where(is_service, 0)

            grouped = chunk.groupby("WO", sort=False).agg(
                BU=("BU", first_present),
                Tanggal_PKB=("_created_on", "min"),
                Total_Revenue=("_amount", "sum"),
                Revenue_Product=("_product", "sum"),
                Revenue_Jasa=("_service", "sum"),
                Jumlah_Baris=("WO", "size"),
                Kecamatan=("Kecamatan", first_present),
                Kota_Kabupaten=("Kota/Kabupaten", first_present),
                Provinsi=("Provinsi", first_present),
                Status_Alamat=("Status_Alamat", first_present),
            )
            rows = []
            for wo, row in grouped.iterrows():
                rows.append((
                    wo, row.BU, month_from_wo(wo), float(row.Total_Revenue),
                    float(row.Revenue_Product), float(row.Revenue_Jasa),
                    int(row.Jumlah_Baris), row.Kecamatan, row.Kota_Kabupaten,
                    row.Provinsi, row.Status_Alamat,
                    datetime_to_text(row.Tanggal_PKB),
                ))
            conn.executemany(UPSERT, rows)

            counted = chunk.dropna(subset=["_service_category"])
            if not counted.empty:
                category_counts = (
                    counted.groupby(["WO", "_service_category"], sort=False)
                    .size().reset_index(name="Frequency")
                )
                conn.executemany(
                    """
                    INSERT INTO service_category_counts VALUES (?, ?, ?)
                    ON CONFLICT(WO, Service_Category) DO UPDATE SET
                        Frequency = Frequency + excluded.Frequency
                    """,
                    [
                        (wo, category, int(frequency))
                        for wo, category, frequency
                        in category_counts.itertuples(index=False, name=None)
                    ],
                )
            conn.commit()
    return None


def write_parquet(conn, chassis_lookup):
    if os.path.exists(OUTPUT):
        os.remove(OUTPUT)
    writer = None
    total_wo = 0
    missing_dates = 0
    date_min = None
    date_max = None
    service_category_counts = Counter()
    bu_values = set()
    try:
        cursor = conn.execute("""
            SELECT m.WO, m.BU, m.Bulan_PKB, m.Total_Revenue,
                   m.Revenue_Product, m.Revenue_Jasa, m.Jumlah_Baris,
                   m.Kecamatan, m.Kota_Kabupaten, m.Provinsi,
                   m.Status_Alamat, m.Tanggal_PKB,
                   (
                       SELECT c.Service_Category
                       FROM service_category_counts AS c
                       WHERE c.WO = m.WO
                       ORDER BY c.Frequency DESC, c.Service_Category ASC
                       LIMIT 1
                   ) AS Service_Category
            FROM master AS m ORDER BY m.WO
        """)
        while True:
            rows = cursor.fetchmany(100_000)
            if not rows:
                break
            frame = pd.DataFrame(
                rows,
                columns=OUTPUT_COLUMNS[:11] + ["Tanggal_PKB", "Service_Category"],
            )
            frame["Chassis"] = frame["WO"].map(chassis_lookup)
            total_wo += len(frame)
            frame["Tanggal_PKB"] = pd.to_datetime(frame["Tanggal_PKB"], errors="coerce")
            missing_dates += int(frame["Tanggal_PKB"].isna().sum())
            batch_min = frame["Tanggal_PKB"].min()
            batch_max = frame["Tanggal_PKB"].max()
            if pd.notna(batch_min) and (date_min is None or batch_min < date_min):
                date_min = batch_min
            if pd.notna(batch_max) and (date_max is None or batch_max > date_max):
                date_max = batch_max
            service_category_counts.update(
                frame["Service_Category"].fillna("(kosong)").value_counts().to_dict()
            )
            bu_values.update(frame["BU"].dropna().unique())
            table = pa.Table.from_pandas(frame[OUTPUT_COLUMNS], preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(OUTPUT, table.schema, compression="snappy")
            writer.write_table(table)
    finally:
        if writer is not None:
            writer.close()
    return total_wo, date_min, date_max, missing_dates, service_category_counts, bu_values


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    try:
        initialize_db(conn)
        process_inputs(conn)
        chassis_lookup = load_chassis_lookup()
        result = write_parquet(conn, chassis_lookup)
    finally:
        conn.close()
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

    total_wo, date_min, date_max, missing_dates, categories, bu_values = result
    print(f"Rentang Tanggal_PKB: {date_min} — {date_max}")
    print(f"WO dengan Tanggal_PKB kosong: {missing_dates:,}")
    print("Service_Category unik per WO (maks 20):")
    for category, count in sorted(categories.items(), key=lambda item: (-item[1], item[0]))[:20]:
        print(f"  {category}: {count:,}")
    print(f"BU unik: {sorted(bu_values)}")


if __name__ == "__main__":
    main()
