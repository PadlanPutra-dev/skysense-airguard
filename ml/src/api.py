from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
from datetime import datetime

from ml.src.predictor import SkySensePredictor


# ==========================================================
# FASTAPI
# ==========================================================

app = FastAPI(
    title="SkySense Weather Prediction API",
    description="API prediksi cuaca menggunakan machine learning",
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

    # Pastikan data terurut berdasarkan tanggal
    if "TANGGAL" in WEATHER_DATA.columns:

        WEATHER_DATA["TANGGAL"] = pd.to_datetime(
            WEATHER_DATA["TANGGAL"],
            errors="coerce"
        )

        WEATHER_DATA = (
            WEATHER_DATA
            .dropna(subset=["TANGGAL"])
            .sort_values("TANGGAL")
            .reset_index(drop=True)
        )

    print(
        f"Dataset berhasil dimuat: "
        f"{len(WEATHER_DATA)} baris"
    )

    if "TANGGAL" in WEATHER_DATA.columns:

        print(
            f"Data pertama : "
            f"{WEATHER_DATA.iloc[0]['TANGGAL'].strftime('%Y-%m-%d')}"
        )

        print(
            f"Data terakhir : "
            f"{WEATHER_DATA.iloc[-1]['TANGGAL'].strftime('%Y-%m-%d')}"
        )

except Exception as e:

    print("Gagal memuat dataset:", e)

    WEATHER_DATA = None


# ==========================================================
# LOAD PREDICTOR
# ==========================================================

try:

    predictor = SkySensePredictor()

    print("Predictor berhasil dimuat.")

except Exception as e:

    print("Gagal memuat predictor:", e)

    predictor = None


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


    if predictor is None:

        return {
            "error": "Predictor tidak berhasil dimuat."
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
    # DATA TERAKHIR
    # ------------------------------------------------------

    try:

        if "TANGGAL" in history.columns:

            last_data_date = pd.to_datetime(
                history.iloc[-1]["TANGGAL"]
            )

        else:

            last_data_date = pd.Timestamp(
                year=int(history.iloc[-1]["TAHUN"]),
                month=int(history.iloc[-1]["BULAN"]),
                day=int(history.iloc[-1]["HARI"])
            )

    except Exception as e:

        print("Date Error:", e)

        return {
            "error": "Gagal membaca tanggal data terakhir.",
            "detail": str(e)
        }


    # ------------------------------------------------------
    # FORECAST
    # ------------------------------------------------------

    try:

        print(
            f"Data terakhir: "
            f"{last_data_date.strftime('%Y-%m-%d')}"
        )

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
    # FORECAST PERIOD
    # ------------------------------------------------------

    if result:

        first_forecast_date = result[0].get("TANGGAL")
        last_forecast_date = result[-1].get("TANGGAL")

    else:

        first_forecast_date = None
        last_forecast_date = None


    # ------------------------------------------------------
    # RESPONSE
    # ------------------------------------------------------

    response = {

        "source": "BMKG Dataset",

        "data_status": "historical_dataset",

        "last_data_date":
            last_data_date.strftime("%Y-%m-%d"),

        "first_forecast_date":
            first_forecast_date,

        "last_forecast_date":
            last_forecast_date,

        "history_used":
            len(history),

        "forecast_days":
            len(result),

        "generated_at":
            datetime.now().isoformat(),

        "forecast":
            result

    }


    print(
        f"Forecast berhasil: "
        f"{len(result)} hari"
    )

    print(
        f"Periode forecast: "
        f"{first_forecast_date} "
        f"sampai "
        f"{last_forecast_date}"
    )


    return response