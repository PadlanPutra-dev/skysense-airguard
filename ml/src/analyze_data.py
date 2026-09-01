import pandas as pd
from pathlib import Path

# ==========================================================
# PATH
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "Dataset_cuaca_clean.xlsx"

# ==========================================================
# LOAD DATA
# ==========================================================

df = pd.read_excel(DATA_PATH)

print("=" * 70)
print("ANALISIS DATASET SKY SENSE")
print("=" * 70)

print("\nJumlah data:", len(df))
print("Jumlah kolom:", len(df.columns))

# ==========================================================
# INFORMASI DATA
# ==========================================================

print("\n" + "=" * 70)
print("INFORMASI DATA")
print("=" * 70)

print(df.info())

# ==========================================================
# STATISTIK
# ==========================================================

BASE_COLS = [
    "TN",
    "TX",
    "TAVG",
    "RH_AVG",
    "RR",
    "SS",
    "FF_X",
    "FF_AVG"
]

print("\n" + "=" * 70)
print("STATISTIK DATA")
print("=" * 70)

print(
    df[BASE_COLS]
    .describe()
    .round(3)
)

# ==========================================================
# MISSING VALUE
# ==========================================================

print("\n" + "=" * 70)
print("MISSING VALUE")
print("=" * 70)

print(df[BASE_COLS].isnull().sum())

# ==========================================================
# UNIQUE VALUE
# ==========================================================

print("\n" + "=" * 70)
print("JUMLAH UNIQUE VALUE")
print("=" * 70)

for col in BASE_COLS:
    print(
        f"{col:10} : "
        f"{df[col].nunique()} unique"
    )

# ==========================================================
# KORELASI
# ==========================================================

print("\n" + "=" * 70)
print("KORELASI ANTAR VARIABEL")
print("=" * 70)

correlation = (
    df[BASE_COLS]
    .corr()
    .round(3)
)

print(correlation)

# ==========================================================
# SIMPAN HASIL
# ==========================================================

correlation.to_csv(
    BASE_DIR / "models" / "correlation.csv"
)

print("\nCorrelation berhasil disimpan:")
print(
    BASE_DIR / "models" / "correlation.csv"
)

# ==========================================================
# RANGE DATA
# ==========================================================

print("\n" + "=" * 70)
print("RANGE DATA")
print("=" * 70)

for col in BASE_COLS:

    minimum = df[col].min()
    maximum = df[col].max()
    mean = df[col].mean()

    print(
        f"{col:10} | "
        f"Min: {minimum:.3f} | "
        f"Max: {maximum:.3f} | "
        f"Mean: {mean:.3f}"
    )

print("\nAnalisis selesai.")