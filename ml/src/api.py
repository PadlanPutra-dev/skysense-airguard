from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path

from ml.src.predictor import SkySensePredictor


# ==========================================================
# FASTAPI
# ==========================================================

app = FastAPI(
    title="SkySense Weather Prediction API",
    description="API prediksi cuaca menggunakan Random Forest",
    version="1.0.0"
)


# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# ==========================================================
# LOAD DATASET SEKALI SAAT SERVER START
# ==========================================================

print("=" * 60)
print("SKYSENSE API")
print("=" * 60)

try:

    WEATHER_DATA = pd.read_excel(DATA_PATH)

    print(
        f"Dataset berhasil dimuat: "
        f"{len(WEATHER_DATA)} baris"
    )

except Exception as e:

    print("Gagal memuat dataset:", e)

    WEATHER_DATA = None


# ==========================================================
# LOAD PREDICTOR
# ==========================================================

predictor = SkySensePredictor()

print("Predictor berhasil dimuat.")


# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
def root():

    return {
        "message": "SkySense Weather Prediction API",
        "status": "running",
        "endpoint": "/forecast?days=7"
    }


# ==========================================================
# FORECAST
# ==========================================================

@app.get("/forecast")
def forecast(
    days: int = Query(
        default=7,
        ge=1,
        le=365
    )
):

    print()
    print("=" * 60)
    print(f"REQUEST FORECAST: {days} HARI")
    print("=" * 60)


    # ------------------------------------------------------
    # VALIDATE DATASET
    # ------------------------------------------------------

    if WEATHER_DATA is None:

        return {
            "error": "Dataset tidak berhasil dimuat."
        }


    if len(WEATHER_DATA) < 7:

        return {
            "error": "Data historis kurang dari 7 hari."
        }


    # ------------------------------------------------------
    # AMBIL 7 DATA TERAKHIR
    # ------------------------------------------------------

    history = WEATHER_DATA.tail(7).copy()


    # ------------------------------------------------------
    # FORECAST
    # ------------------------------------------------------

    try:

        print(
            f"Menghitung forecast {days} hari..."
        )

        result = predictor.forecast(
            history,
            days=days
        )

    except Exception as e:

        print("Prediction Error:", e)

        return {
            "error": "Gagal melakukan prediksi.",
            "detail": str(e)
        }


    # ------------------------------------------------------
    # RESPONSE
    # ------------------------------------------------------

    response = {

        "source": "BMKG Dataset",

        "history_used": len(history),

        "forecast_days": days,

        "forecast": result

    }


    print(
        f"Forecast berhasil: {len(result)} hari"
    )

    return response