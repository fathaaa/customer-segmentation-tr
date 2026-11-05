import pandas as pd, glob, os

BASE = os.path.dirname(os.path.abspath(__file__))
pd.set_option("display.width", 250, "display.max_columns", 30)

for f in sorted(glob.glob(os.path.join(BASE, "Address", "*.xlsx"))):
    print("\n" + "=" * 70)
    print(os.path.basename(f))
    try:
        xl = pd.ExcelFile(f, engine="calamine")
        for sh in xl.sheet_names:
            df = xl.parse(sh, nrows=4, dtype=str)
            print(f"\n  sheet '{sh}' | kolom: {list(df.columns)}")
            print(df.to_string(index=False, max_colwidth=25))
    except Exception as e:
        print("  GAGAL:", repr(e)[:100])