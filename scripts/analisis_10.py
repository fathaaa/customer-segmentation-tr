from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "pkb_master.parquet"
CHART = ROOT / "analysis" / "charts" / "10_repeat_service.png"
BUCKETS = [1, 2, 3, 4, 5]
LABELS = ["1", "2", "3", "4", "5+"]


def bucket_counts(visits: pd.Series) -> list[int]:
    bucketed = visits.clip(upper=5).value_counts()
    return [int(bucketed.get(n, 0)) for n in BUCKETS]


def main() -> None:
    # Load only the requested master parquet and only fields needed for this analysis.
    df = pd.read_parquet(DATA, columns=["Chassis", "Tanggal_PKB"])
    total_wo = len(df)
    has_chassis = df["Chassis"].notna() & df["Chassis"].astype("string").str.strip().ne("")
    excluded_wo = int((~has_chassis).sum())
    df = df.loc[has_chassis, ["Chassis", "Tanggal_PKB"]].copy()
    df["Tanggal_PKB"] = pd.to_datetime(df["Tanggal_PKB"], errors="coerce").dt.normalize()
    bad_date_wo = int(df["Tanggal_PKB"].isna().sum())
    df = df.dropna(subset=["Tanggal_PKB"])

    wo_counts = df.groupby("Chassis", sort=False).size()
    visit_counts = df.drop_duplicates(["Chassis", "Tanggal_PKB"]).groupby("Chassis", sort=False).size()
    unique_chassis = int(wo_counts.size)
    wo_buckets = bucket_counts(wo_counts)
    visit_buckets = bucket_counts(visit_counts)
    wo_repeat_pct = float((wo_counts.gt(1).mean()) * 100)
    visit_repeat_pct = float((visit_counts.gt(1).mean()) * 100)

    print(f"Total WO: {total_wo:,} | tanpa Chassis: {excluded_wo:,} | tanggal tidak terbaca: {bad_date_wo:,} | Chassis unik: {unique_chassis:,}")
    print("WO unik per Chassis (jumlah: persen):")
    for label, count in zip(LABELS, wo_buckets):
        print(f"  {label}: {count:,} ({count / unique_chassis * 100:.2f}%)")
    print(f"Repeat (>1 WO): {wo_repeat_pct:.2f}%")
    print("Tanggal kunjungan unik per Chassis (jumlah: persen):")
    for label, count in zip(LABELS, visit_buckets):
        print(f"  {label}: {count:,} ({count / unique_chassis * 100:.2f}%)")
    print(f"Repeat (>1 tanggal): {visit_repeat_pct:.2f}%")

    CHART.parent.mkdir(parents=True, exist_ok=True)
    x = range(len(LABELS))
    width = 0.38
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.bar([i - width / 2 for i in x], [n / unique_chassis * 100 for n in wo_buckets],
           width, label="WO unik per Chassis", color="#3569a8")
    ax.bar([i + width / 2 for i in x], [n / unique_chassis * 100 for n in visit_buckets],
           width, label="Tanggal kunjungan unik", color="#e38b36")
    ax.set_xticks(list(x), LABELS)
    ax.set_xlabel("Jumlah kunjungan per Chassis")
    ax.set_ylabel("Persentase Chassis (%)")
    ax.set_title("Distribusi Repeat Service")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(CHART, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
