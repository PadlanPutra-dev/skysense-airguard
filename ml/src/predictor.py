import joblib
import pandas as pd

from pathlib import Path


# ==========================================================
# PATH
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models"


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
# PREDICTOR
# ==========================================================

class SkySensePredictor:

    def __init__(self, model_dir=MODEL_DIR):

        self.model_dir = Path(model_dir)

        self.models = {}

        self.load_models()


    # ======================================================
    # LOAD MODEL
    # ======================================================

    def load_models(self):

        print("=" * 50)
        print("MEMUAT MODEL")
        print("=" * 50)

        for target in TARGETS:

            model_path = (
                self.model_dir
                / f"random_forest_{target.lower()}_forecast.pkl"
            )

            if not model_path.exists():

                raise FileNotFoundError(
                    f"Model tidak ditemukan:\n{model_path}"
                )

            self.models[target] = joblib.load(model_path)

            print(f"✓ {target} berhasil dimuat")

        print("\nSemua model berhasil dimuat.")


    # ======================================================
    # VALIDATE HISTORY
    # ======================================================

    def validate_history(self, history):

        if len(history) < 7:

            raise ValueError(
                "History minimal 7 hari."
            )

        missing = [
            col
            for col in BASE_COLS
            if col not in history.columns
        ]

        if missing:

            raise ValueError(
                f"Kolom belum ada: {missing}"
            )


    # ======================================================
    # PREPARE FEATURES
    # ======================================================

    def prepare_features(self, history):

        self.validate_history(history)

        history = history.tail(7).copy()

        latest = history.iloc[-1]

        feature = {

            "TAHUN": int(latest["TAHUN"]),

            "BULAN": int(latest["BULAN"]),

            "HARI": int(latest["HARI"]),

            "HARI_DALAM_MINGGU":
                int(latest["HARI_DALAM_MINGGU"])

        }


        for col in BASE_COLS:

            values = history[col].astype(float).tolist()

            last_3 = values[-3:]
            last_7 = values[-7:]


            # ------------------------------
            # LAG
            # ------------------------------

            feature[f"{col}_lag1"] = values[-1]

            feature[f"{col}_lag2"] = values[-2]

            feature[f"{col}_lag3"] = values[-3]

            feature[f"{col}_lag7"] = values[-7]


            # ------------------------------
            # ROLLING
            # ------------------------------

            feature[f"{col}_roll3"] = (
                sum(last_3) / 3
            )

            feature[f"{col}_roll7"] = (
                sum(last_7) / 7
            )


            # ------------------------------
            # MAX / MIN
            # ------------------------------

            feature[f"{col}_max7"] = max(last_7)

            feature[f"{col}_min7"] = min(last_7)


        return pd.DataFrame(
            [feature],
            columns=FEATURES
        )


    # ======================================================
    # PREDICT
    # ======================================================

    def predict(self, history):

        X = self.prepare_features(history)

        result = {}

        for target in TARGETS:

            value = self.models[target].predict(X)[0]

            result[target] = round(
                float(value),
                3
            )

        return result


    # ======================================================
    # FORECAST
    # ======================================================

    def forecast(self, history, days=7):

        self.validate_history(history)

        if days < 1:

            raise ValueError(
                "days minimal 1."
            )

        if days > 365:

            raise ValueError(
                "days maksimal 365."
            )


        # --------------------------------------------------
        # HISTORY HANYA 7 HARI YANG DIPERLUKAN
        # --------------------------------------------------

        history = history.tail(7).copy()

        predictions = []


        # --------------------------------------------------
        # FORECAST LOOP
        # --------------------------------------------------

        for step in range(days):

            # ----------------------------------------------
            # TANGGAL TERAKHIR
            # ----------------------------------------------

            if "TANGGAL" in history.columns:

                last_date = pd.to_datetime(
                    history.iloc[-1]["TANGGAL"]
                )

            else:

                last_date = pd.Timestamp(
                    year=int(history.iloc[-1]["TAHUN"]),
                    month=int(history.iloc[-1]["BULAN"]),
                    day=int(history.iloc[-1]["HARI"])
                )


            next_date = (
                last_date
                + pd.Timedelta(days=1)
            )


            # ----------------------------------------------
            # UPDATE DATE FEATURES
            # ----------------------------------------------

            history.iloc[
                -1,
                history.columns.get_loc("TAHUN")
            ] = history.iloc[-1]["TAHUN"]


            # ----------------------------------------------
            # FEATURE
            # ----------------------------------------------

            feature_history = history.copy()

            feature_history.loc[
                feature_history.index[-1],
                "TAHUN"
            ] = last_date.year

            feature_history.loc[
                feature_history.index[-1],
                "BULAN"
            ] = last_date.month

            feature_history.loc[
                feature_history.index[-1],
                "HARI"
            ] = last_date.day

            feature_history.loc[
                feature_history.index[-1],
                "HARI_DALAM_MINGGU"
            ] = last_date.dayofweek


            X = self.prepare_features(
                feature_history
            )


            # ----------------------------------------------
            # PREDICT ALL TARGETS
            # ----------------------------------------------

            prediction = {}

            for target in TARGETS:

                value = self.models[target].predict(X)[0]

                prediction[target] = round(
                    float(value),
                    3
                )


            # ----------------------------------------------
            # FORECAST ROW
            # ----------------------------------------------

            forecast_row = {

                "TANGGAL":
                    next_date.strftime("%Y-%m-%d"),

                "TAHUN":
                    next_date.year,

                "BULAN":
                    next_date.month,

                "HARI":
                    next_date.day,

                "HARI_DALAM_MINGGU":
                    next_date.dayofweek,

                **prediction
            }


            predictions.append(
                forecast_row
            )


            # ----------------------------------------------
            # UPDATE HISTORY
            # ----------------------------------------------

            new_history_row = forecast_row.copy()

            history = pd.concat(
                [
                    history,
                    pd.DataFrame(
                        [new_history_row]
                    )
                ],
                ignore_index=True
            )

            # Ambil kembali 7 hari terakhir
            history = history.tail(7).copy()


            # ----------------------------------------------
            # PROGRESS
            # ----------------------------------------------

            if days >= 30:

                if (
                    (step + 1) % 30 == 0
                    or step + 1 == days
                ):

                    print(
                        f"Progress forecast: "
                        f"{step + 1}/{days} hari"
                    )


        return predictions


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    predictor = SkySensePredictor()


    data_path = (
        BASE_DIR
        / "data"
        / "Dataset_cuaca_clean.xlsx"
    )


    sample = pd.read_excel(
        data_path
    )


    history = sample.tail(7)


    print()
    print("=" * 60)
    print("FORECAST 7 HARI")
    print("=" * 60)


    result = predictor.forecast(
        history,
        days=7
    )


    for item in result:

        print(
            f"{item['TANGGAL']} | "
            f"TAVG: {item['TAVG']} °C | "
            f"TN: {item['TN']} °C | "
            f"TX: {item['TX']} °C | "
            f"RH: {item['RH_AVG']} %"
        )