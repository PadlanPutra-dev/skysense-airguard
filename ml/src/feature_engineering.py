import pandas as pd

BASE_COLS = [
    "TN",
    "TX",
    "TAVG",
    "RH_AVG",
    "RR",
    "SS",
    "FF_X",
    "FF_AVG",
]


def build_features(df: pd.DataFrame):

    df = df.copy()

    for col in BASE_COLS:

        # ==========================
        # Lag Feature
        # ==========================

        df[f"{col}_lag1"] = df[col].shift(1)
        df[f"{col}_lag2"] = df[col].shift(2)
        df[f"{col}_lag3"] = df[col].shift(3)
        df[f"{col}_lag7"] = df[col].shift(7)

        # ==========================
        # Rolling Mean
        # ==========================

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

        # ==========================
        # Rolling Maximum
        # ==========================

        df[f"{col}_max7"] = (
            df[col]
            .rolling(7)
            .max()
        )

        # ==========================
        # Rolling Minimum
        # ==========================

        df[f"{col}_min7"] = (
            df[col]
            .rolling(7)
            .min()
        )

    return df