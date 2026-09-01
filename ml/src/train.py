import joblib
import pandas as pd

from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from feature_engineering import build_features, BASE_COLS


# ==========================================================
# PATH
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

DATA_PATH = DATA_DIR / "Dataset_cuaca_clean.xlsx"


# ==========================================================
# TARGET
# ==========================================================

TARGETS = BASE_COLS


# ==========================================================
# BEST HYPERPARAMETERS
# HASIL GRID SEARCH / TUNING
# ==========================================================

BEST_PARAMS = {

    "TN": {
        "n_estimators": 300,
        "max_depth": 15,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
    },

    "TX": {
        "n_estimators": 300,
        "max_depth": 20,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
    },

    "TAVG": {
        "n_estimators": 300,
        "max_depth": 20,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
    },

    "RH_AVG": {
        "n_estimators": 300,
        "max_depth": 20,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
    },

    "RR": {
        "n_estimators": 300,
        "max_depth": 20,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
    },

    "SS": {
        "n_estimators": 300,
        "max_depth": 15,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
    },

    "FF_X": {
        "n_estimators": 300,
        "max_depth": 15,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
    },

    "FF_AVG": {
        "n_estimators": 200,
        "max_depth": 15,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
    },
}


# ==========================================================
# FEATURE COLUMNS
# ==========================================================

FEATURE_COLUMNS = [
    "TAHUN",
    "BULAN",
    "HARI",
    "HARI_DALAM_MINGGU",
]

for col in BASE_COLS:

    FEATURE_COLUMNS.extend([
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
# LOAD DATASET
# ==========================================================

print("=" * 70)
print("SKYSENSE MACHINE LEARNING")
print("RANDOM FOREST WEATHER FORECAST")
print("=" * 70)

print("\nMemuat dataset...")

if not DATA_PATH.exists():

    raise FileNotFoundError(
        f"Dataset tidak ditemukan:\n{DATA_PATH}"
    )

df = pd.read_excel(DATA_PATH)

print(f"Dataset berhasil dimuat: {DATA_PATH}")

print("\nJumlah data awal :", len(df))
print("Jumlah kolom     :", len(df.columns))


# ==========================================================
# BASIC DATA CHECK
# ==========================================================

print("\n" + "=" * 70)
print("DATA CHECK")
print("=" * 70)

print("\nKolom dataset:")
print(df.columns.tolist())

print("\nMissing value:")

missing_values = df.isnull().sum()

print(missing_values)


# ==========================================================
# BUILD FEATURES
# ==========================================================

print("\n" + "=" * 70)
print("FEATURE ENGINEERING")
print("=" * 70)

print("\nMembuat fitur lag, rolling, max, dan min...")

df = build_features(df)

print("Feature engineering selesai.")

print("Jumlah data setelah feature engineering :", len(df))


# ==========================================================
# CHECK REQUIRED FEATURES
# ==========================================================

missing_features = [
    col
    for col in FEATURE_COLUMNS
    if col not in df.columns
]

if missing_features:

    raise ValueError(
        "Feature berikut tidak ditemukan:\n"
        + "\n".join(missing_features)
    )

print("\nJumlah feature :", len(FEATURE_COLUMNS))


# ==========================================================
# CREATE MODEL DIRECTORY
# ==========================================================

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# RESULT STORAGE
# ==========================================================

evaluation_result = []

feature_importance_result = []


# ==========================================================
# TRAINING
# ==========================================================

for TARGET in TARGETS:

    print("\n")
    print("=" * 70)
    print(f"TRAINING MODEL : {TARGET}")
    print("=" * 70)

    # ------------------------------------------------------
    # COPY DATA
    # ------------------------------------------------------

    data = df.copy()

    # ------------------------------------------------------
    # TARGET HARI BERIKUTNYA
    # ------------------------------------------------------

    data["TARGET"] = data[TARGET].shift(-1)

    # ------------------------------------------------------
    # REMOVE NaN
    # ------------------------------------------------------

    data = data.dropna().reset_index(drop=True)

    print("\nJumlah data training :", len(data))

    # ------------------------------------------------------
    # FEATURES
    # ------------------------------------------------------

    X = data[FEATURE_COLUMNS]

    y = data["TARGET"]

    # ------------------------------------------------------
    # TIME SERIES SPLIT
    # ------------------------------------------------------

    split_index = int(len(data) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    print("\nUkuran data:")
    print("X Train :", X_train.shape)
    print("X Test  :", X_test.shape)
    print("y Train :", y_train.shape)
    print("y Test  :", y_test.shape)

    # ------------------------------------------------------
    # BEST PARAMETERS
    # ------------------------------------------------------

    params = BEST_PARAMS[TARGET]

    print("\nHyperparameter:")
    print(f"n_estimators      : {params['n_estimators']}")
    print(f"max_depth         : {params['max_depth']}")
    print(f"min_samples_split : {params['min_samples_split']}")
    print(f"min_samples_leaf  : {params['min_samples_leaf']}")

    # ------------------------------------------------------
    # RANDOM FOREST
    # ------------------------------------------------------

    model = RandomForestRegressor(

        n_estimators=params["n_estimators"],

        max_depth=params["max_depth"],

        min_samples_split=params[
            "min_samples_split"
        ],

        min_samples_leaf=params[
            "min_samples_leaf"
        ],

        random_state=42,

        n_jobs=-1,
    )

    # ------------------------------------------------------
    # TRAIN
    # ------------------------------------------------------

    print("\nTraining Random Forest...")

    model.fit(
        X_train,
        y_train
    )

    print("Training selesai.")

    # ------------------------------------------------------
    # PREDICTION
    # ------------------------------------------------------

    print("Melakukan prediksi test data...")

    y_pred = model.predict(
        X_test
    )

    # ------------------------------------------------------
    # EVALUATION
    # ------------------------------------------------------

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

    print("\nHasil evaluasi:")

    print(f"MAE  : {mae:.6f}")
    print(f"RMSE : {rmse:.6f}")
    print(f"R²   : {r2:.6f}")

    # ------------------------------------------------------
    # SAVE EVALUATION
    # ------------------------------------------------------

    evaluation_result.append({

        "Target": TARGET,

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
            params["min_samples_leaf"],
    })

    # ------------------------------------------------------
    # FEATURE IMPORTANCE
    # ------------------------------------------------------

    importance = pd.DataFrame({

        "Target": TARGET,

        "Feature": FEATURE_COLUMNS,

        "Importance":
            model.feature_importances_,
    })

    importance = importance.sort_values(
        by="Importance",
        ascending=False
    )

    feature_importance_result.append(
        importance
    )

    # ------------------------------------------------------
    # SAVE MODEL
    # ------------------------------------------------------

    model_path = (
        MODEL_DIR
        / f"random_forest_{TARGET.lower()}_forecast.pkl"
    )

    joblib.dump(
        model,
        model_path
    )

    print(
        f"\nModel berhasil disimpan:"
    )

    print(model_path)


# ==========================================================
# SAVE EVALUATION
# ==========================================================

evaluation_df = pd.DataFrame(
    evaluation_result
)

evaluation_path = (
    MODEL_DIR
    / "evaluation.csv"
)

evaluation_df.to_csv(
    evaluation_path,
    index=False
)


# ==========================================================
# SAVE FEATURE IMPORTANCE
# ==========================================================

importance_df = pd.concat(
    feature_importance_result,
    ignore_index=True
)

importance_path = (
    MODEL_DIR
    / "feature_importance.csv"
)

importance_df.to_csv(
    importance_path,
    index=False
)


# ==========================================================
# FINAL SUMMARY
# ==========================================================

print("\n")
print("=" * 70)
print("TRAINING SELESAI")
print("=" * 70)

print("\nEvaluation:")

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

print("\nFile yang dibuat:")

print(f"1. {evaluation_path}")
print(f"2. {importance_path}")

print("\nModel:")

for target in TARGETS:

    model_path = (
        MODEL_DIR
        / f"random_forest_{target.lower()}_forecast.pkl"
    )

    print(
        f"✓ {model_path.name}"
    )

print("\nSeluruh model berhasil dibuat.")