import csv
import os

import xlsxwriter


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE, "data", "pkb_master.csv")
OUTPUT_FILE = os.path.join(BASE, "data", "pkb_master_rapi.xlsx")

HEADERS = [
    "WO", "BU", "Bulan_PKB", "Total_Revenue", "Revenue_Product",
    "Revenue_Jasa", "Jumlah_Baris", "Kecamatan", "Kota/Kabupaten",
    "Provinsi", "Status_Alamat", "Chassis",
]
NUMERIC_COLUMNS = {"Total_Revenue", "Revenue_Product", "Revenue_Jasa", "Jumlah_Baris"}
WIDTHS = [22, 16, 12, 19, 19, 19, 15, 24, 25, 20, 34, 24]


def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(INPUT_FILE)
    if os.path.exists(OUTPUT_FILE):
        raise FileExistsError(f"Output sudah ada, tidak ditimpa: {OUTPUT_FILE}")

    workbook = xlsxwriter.Workbook(OUTPUT_FILE, {"constant_memory": True})
    sheet = workbook.add_worksheet("PKB Master")
    sheet.freeze_panes(1, 0)
    sheet.hide_gridlines(2)

    header_format = workbook.add_format({
        "bold": True,
        "bg_color": "#FFD966",
        "font_color": "#1F1F1F",
        "align": "center",
        "valign": "vcenter",
        "text_wrap": True,
        "border": 1,
        "border_color": "#7F6000",
    })
    text_format = workbook.add_format({
        "valign": "vcenter", "border": 1, "border_color": "#C8C8C8"
    })
    amount_format = workbook.add_format({
        "num_format": "#,##0.00", "valign": "vcenter",
        "border": 1, "border_color": "#C8C8C8",
    })
    count_format = workbook.add_format({
        "num_format": "#,##0", "valign": "vcenter",
        "border": 1, "border_color": "#C8C8C8",
    })

    with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != HEADERS:
            raise ValueError(f"Header CSV tidak sesuai: {reader.fieldnames}")

        for col, title in enumerate(HEADERS):
            sheet.write_string(0, col, title, header_format)
            sheet.set_column(col, col, WIDTHS[col])
        sheet.set_row(0, 28)

        row_count = 0
        for row_count, record in enumerate(reader, start=1):
            for col, title in enumerate(HEADERS):
                value = record.get(title, "")
                if title in NUMERIC_COLUMNS:
                    if value == "":
                        sheet.write_blank(row_count, col, None,
                                          count_format if title == "Jumlah_Baris" else amount_format)
                    else:
                        number = float(value)
                        fmt = count_format if title == "Jumlah_Baris" else amount_format
                        sheet.write_number(row_count, col, number, fmt)
                elif value == "":
                    sheet.write_blank(row_count, col, None, text_format)
                else:
                    # Tulis sebagai teks agar WO dan Chassis tidak diubah Excel.
                    sheet.write_string(row_count, col, value, text_format)

    sheet.autofilter(0, 0, row_count, len(HEADERS) - 1)
    workbook.close()
    size = os.path.getsize(OUTPUT_FILE)
    print(f"Baris data: {row_count:,}")
    print(f"File: {OUTPUT_FILE}")
    print(f"Ukuran: {size:,} byte ({size / (1024 * 1024):.2f} MiB)")


if __name__ == "__main__":
    main()
