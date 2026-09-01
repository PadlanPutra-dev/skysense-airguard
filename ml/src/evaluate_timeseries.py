import pandas as pd

from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.model_selection import TimeSeriesSplit

from feature_engineering import build_features, BASE_COLS


# ==========================================================
# PATH
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "Dataset_cuaca_clean.xlsx"
)

MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)


# ==========================================================
# LOAD DATA
# ==========================================================

print("=" * 70)
print("TIME SERIES CROSS VALIDATION")
print("=" * 70)

df = pd.read_excel(DATA_PATH)

print(f"\nJumlah data awal : {len(df)}")


# ==========================================================
# FEATURE ENGINEERING
# ==========================================================

df = build_features(df)

print(f"Jumlah data setelah feature engineering : {len(df)}")


# ==========================================================
# TARGET
# ==========================================================

TARGETS = BASE_COLS


# ==========================================================
# FEATURE COLUMNS
# ==========================================================

feature_columns = [
    "TAHUN",
    "BULAN",
    "HARI",
    "HARI_DALAM_MINGGU",
]

for col in BASE_COLS:

    feature_columns.extend([
        f"{col}_lag1",
        f"{col}_lag2",
        f"{col}_lag3",
        f"{col}_lag7",

        f"{col}_roll3",
        f"{col}_roll7",

        f"{col}_max7",
        f"{col}_min7",
    ])


# ==========================================================
# TIME SERIES SPLIT
# ==========================================================

N_SPLITS = 5

tscv = TimeSeriesSplit(
    n_splits=N_SPLITS
)


# ==========================================================
# RESULT
# ==========================================================

results = []


# ==========================================================
# TRAINING & EVALUATION
# ==========================================================

for TARGET in TARGETS:

    print("\n" + "=" * 70)
    print(f"TARGET : {TARGET}")
    print("=" * 70)

    data = df.copy()

    # Target = nilai hari berikutnya
    data["TARGET"] = data[TARGET].shift(-1)

    data = (
        data
        .dropna()
        .reset_index(drop=True)
    )

    X = data[feature_columns]

    y = data["TARGET"]

    fold_results = []


    # ======================================================
    # CROSS VALIDATION
    # ======================================================

    for fold, (train_index, test_index) in enumerate(
        tscv.split(X),
        start=1
    ):

        X_train = X.iloc[train_index]
        X_test = X.iloc[test_index]

        y_train = y.iloc[train_index]
        y_test = y.iloc[test_index]

        print(f"\nFold {fold}")

        print(
            f"Train : {len(X_train)} data"
        )

        print(
            f"Test  : {len(X_test)} data"
        )


        # ==================================================
        # MODEL
        # ==================================================

        model = RandomForestRegressor(
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
        )


        # ==================================================
        # TRAIN
        # ==================================================

        model.fit(
            X_train,
            y_train
        )


        # ==================================================
        # PREDICT
        # ==================================================

        y_pred = model.predict(
            X_test
        )


        # ==================================================
        # METRICS
        # ==================================================

        mae = mean_absolute_error(
            y_test,
            y_pred
        )

        rmse = mean_squared_error(
            y_test,
            y_pred
        ) ** 0.5

        r2 = r2_score(
            y_test,
            y_pred
        )


        print(
            f"MAE  : {mae:.4f}"
        )

        print(
            f"RMSE : {rmse:.4f}"
        )

        print(
            f"R²   : {r2:.4f}"
        )


        fold_results.append({
            "Fold": fold,
            "MAE": mae,
            "RMSE": rmse,
            "R2": r2
        })


    # ======================================================
    # AVERAGE
    # ======================================================

    fold_df = pd.DataFrame(
        fold_results
    )

    avg_mae = fold_df["MAE"].mean()
    avg_rmse = fold_df["RMSE"].mean()
    avg_r2 = fold_df["R2"].mean()


    print("\n" + "-" * 50)

    print(
        f"Average MAE  : {avg_mae:.4f}"
    )

    print(
        f"Average RMSE : {avg_rmse:.4f}"
    )

    print(
        f"Average R²   : {avg_r2:.4f}"
    )


    # ======================================================
    # SAVE RESULT
    # ======================================================

    results.append({

        "Target": TARGET,

        "MAE": avg_mae,

        "RMSE": avg_rmse,

        "R2": avg_r2

    })


# ==========================================================
# SAVE FINAL RESULT
# ==========================================================

evaluation_df = pd.DataFrame(
    results
)

output_path = (
    MODEL_DIR
    / "evaluation_timeseries.csv"
)

evaluation_df.to_csv(
    output_path,
    index=False
)


# ==========================================================
# DISPLAY
# ==========================================================

print("\n" + "=" * 70)
print("HASIL TIME SERIES CROSS VALIDATION")
print("=" * 70)

print(
    evaluation_df.to_string(
        index=False
    )
)

print("\nHasil disimpan di:")

print(output_path)

print("\nEvaluasi selesai.")