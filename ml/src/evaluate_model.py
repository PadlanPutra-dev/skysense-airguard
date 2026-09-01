import matplotlib

matplotlib.use("Agg")

import joblib
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ==========================================================
# PATH
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "Dataset_cuaca_clean.xlsx"
)

RESULT_DIR = BASE_DIR / "evaluation"

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# TARGET
# ==========================================================

TARGETS = [
    "TN",
    "TX",
    "TAVG",
    "RH_AVG",
    "RR",
    "SS",
    "FF_X",
    "FF_AVG"
]


# ==========================================================
# BASE COLUMNS
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


# ==========================================================
# BEST HYPERPARAMETERS
# Berdasarkan hasil tuning sebelumnya
# ==========================================================

BEST_PARAMS = {

    "TN": {
        "n_estimators": 300,
        "max_depth": 15,
        "min_samples_split": 2,
        "min_samples_leaf": 1
    },

    "TX": {
        "n_estimators": 300,
        "max_depth": 20,
        "min_samples_split": 5,
        "min_samples_leaf": 2
    },

    "TAVG": {
        "n_estimators": 300,
        "max_depth": 20,
        "min_samples_split": 2,
        "min_samples_leaf": 1
    },

    "RH_AVG": {
        "n_estimators": 300,
        "max_depth": 20,
        "min_samples_split": 5,
        "min_samples_leaf": 2
    },

    "RR": {
        "n_estimators": 300,
        "max_depth": 20,
        "min_samples_split": 5,
        "min_samples_leaf": 2
    },

    "SS": {
        "n_estimators": 300,
        "max_depth": 15,
        "min_samples_split": 2,
        "min_samples_leaf": 1
    },

    "FF_X": {
        "n_estimators": 300,
        "max_depth": 15,
        "min_samples_split": 2,
        "min_samples_leaf": 1
    },

    "FF_AVG": {
        "n_estimators": 200,
        "max_depth": 15,
        "min_samples_split": 2,
        "min_samples_leaf": 1
    }
}


# ==========================================================
# FEATURES
# ==========================================================

FEATURES = [
    "TAHUN",
    "BULAN",
    "HARI",
    "HARI_DALAM_MINGGU"
]


for col in BASE_COLS:

    FEATURES.extend([
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
# BUILD FEATURES
# ==========================================================

def build_features(df):

    df = df.copy()

    # ------------------------------------------------------
    # Pastikan data terurut berdasarkan tanggal
    # ------------------------------------------------------

    if "TANGGAL" in df.columns:

        df["TANGGAL"] = pd.to_datetime(
            df["TANGGAL"]
        )

        df = df.sort_values(
            "TANGGAL"
        ).reset_index(drop=True)

    # ------------------------------------------------------
    # Feature engineering
    # ------------------------------------------------------

    for col in BASE_COLS:

        df[f"{col}_lag1"] = (
            df[col].shift(1)
        )

        df[f"{col}_lag2"] = (
            df[col].shift(2)
        )

        df[f"{col}_lag3"] = (
            df[col].shift(3)
        )

        df[f"{col}_lag7"] = (
            df[col].shift(7)
        )

        df[f"{col}_roll3"] = (
            df[col]
            .rolling(3)
            .mean()
        )

        df[f"{col}_roll7"] = (
            df[col]
            .rolling(7)
            .mean()
        )

        df[f"{col}_max7"] = (
            df[col]
            .rolling(7)
            .max()
        )

        df[f"{col}_min7"] = (
            df[col]
            .rolling(7)
            .min()
        )

    return df


# ==========================================================
# LOAD DATASET
# ==========================================================

print("=" * 70)
print("SKYSENSE TIME-SERIES MODEL EVALUATION")
print("=" * 70)

df = pd.read_excel(
    DATA_PATH
)

print(
    f"\nJumlah data awal: {len(df)}"
)


# ==========================================================
# BUILD FEATURES
# ==========================================================

df = build_features(
    df
)


# ==========================================================
# EVALUATION
# ==========================================================

results = []


for target in TARGETS:

    print("\n")
    print("=" * 70)
    print(f"EVALUASI: {target}")
    print("=" * 70)

    data = df.copy()

    # ------------------------------------------------------
    # Target hari berikutnya
    # ------------------------------------------------------

    data["TARGET"] = (
        data[target]
        .shift(-1)
    )

    # ------------------------------------------------------
    # Buang data yang belum mempunyai
    # lag / rolling / target
    # ------------------------------------------------------

    data = (
        data
        .dropna()
        .reset_index(drop=True)
    )

    print(
        f"Data setelah feature engineering: {len(data)}"
    )

    # ------------------------------------------------------
    # X dan y
    # ------------------------------------------------------

    X = data[FEATURES]

    y = data["TARGET"]


    # ======================================================
    # CHRONOLOGICAL SPLIT
    # ======================================================

    split_index = int(
        len(data) * 0.8
    )

    X_train = X.iloc[:split_index]

    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]

    y_test = y.iloc[split_index:]


    print(
        f"Training data : {len(X_train)}"
    )

    print(
        f"Testing data  : {len(X_test)}"
    )


    # ======================================================
    # MODEL
    # ======================================================

    params = BEST_PARAMS[target]

    print(
        "\nHyperparameter:"
    )

    print(
        params
    )


    model = RandomForestRegressor(

        n_estimators=params[
            "n_estimators"
        ],

        max_depth=params[
            "max_depth"
        ],

        min_samples_split=params[
            "min_samples_split"
        ],

        min_samples_leaf=params[
            "min_samples_leaf"
        ],

        random_state=42,

        n_jobs=-1
    )


    # ======================================================
    # TRAIN
    # ======================================================

    print(
        "\nTraining model..."
    )

    model.fit(
        X_train,
        y_train
    )

    print(
        "Training selesai."
    )


    # ======================================================
    # PREDICTION
    # ======================================================

    y_pred = model.predict(
        X_test
    )


    # ======================================================
    # METRICS
    # ======================================================

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
        f"\nMAE  : {mae:.4f}"
    )

    print(
        f"RMSE : {rmse:.4f}"
    )

    print(
        f"R²   : {r2:.4f}"
    )


    # ======================================================
    # SAVE RESULT
    # ======================================================

    results.append({

        "Target": target,

        "MAE": mae,

        "RMSE": rmse,

        "R2": r2,

        "n_estimators":
            params["n_estimators"],

        "max_depth":
            params["max_depth"],

        "min_samples_split":
            params["min_samples_split"],

        "min_samples_leaf":
            params["min_samples_leaf"]

    })


    # ======================================================
    # ACTUAL VS PREDICTED
    # ======================================================

    plt.figure(
        figsize=(12, 5)
    )

    plt.plot(
        y_test.values,
        label="Actual"
    )

    plt.plot(
        y_pred,
        label="Predicted"
    )

    plt.title(
        f"SkySense - Actual vs Predicted ({target})"
    )

    plt.xlabel(
        "Data Test"
    )

    plt.ylabel(
        target
    )

    plt.legend()

    plt.tight_layout()


    output_path = (
        RESULT_DIR
        / f"{target}_actual_vs_predicted.png"
    )

    plt.savefig(
        output_path,
        dpi=150
    )

    plt.close()


    print(
        f"Grafik disimpan: {output_path}"
    )


# ==========================================================
# SAVE FINAL EVALUATION
# ==========================================================

evaluation_df = pd.DataFrame(
    results
)


evaluation_path = (
    RESULT_DIR
    / "evaluation_timeseries.csv"
)


evaluation_df.to_csv(
    evaluation_path,
    index=False
)


# ==========================================================
# FINAL RESULT
# ==========================================================

print("\n")
print("=" * 70)
print("TIME-SERIES EVALUATION SELESAI")
print("=" * 70)

print(
    evaluation_df[
        [
            "Target",
            "MAE",
            "RMSE",
            "R2"
        ]
    ].to_string(
        index=False
    )
)


print(
    f"\nHasil evaluasi:"
    f"\n{evaluation_path}"
)

print(
    f"\nGrafik:"
    f"\n{RESULT_DIR}"
)