import numpy as np
import pandas as pd
from scipy.stats import norm


class HypertensionDF:
    def __init__(self):
        # Load the BP tables only once during initialization
        self.bp_tables = pd.read_csv(
            "/Users/jespervang/Projects/MTX/MTX data 2023/src/blood_pressure/bp_app/app/data/bptable.csv"
        )

    def calculate_percentile_using_zscore(self, bp_value, bp_tile):
        # Calculate the mean and standard deviation
        mean = bp_tile["p50"]
        std_dev = (
            bp_tile["p95"] - mean
        ) / 1.645  # 1.645 is the Z-score for the 95th percentile

        # Calculate the Z-score
        z = (bp_value - mean) / std_dev

        # Convert the Z-score to a percentile
        percentile = norm.cdf(z) * 100
        return percentile

    def height_zscore_and_percentile(self, age, sex, height_cm):
        if age < 0 or age > 17:
            return None, None
        filtered_table = self.bp_tables[
            (self.bp_tables["sex"] == sex) & (self.bp_tables["age"] == age)
        ]
        height_percentiles_standard = [5, 10, 25, 50, 75, 90, 95]

        height_values_unique = sorted(set(filtered_table["h.cm"].values))
        if len(height_values_unique) == 0:
            return None, None

        z_scores_for_percentiles = [
            norm.ppf(p / 100.0) for p in height_percentiles_standard
        ]

        z_interpolated = np.interp(
            height_cm, height_values_unique, z_scores_for_percentiles
        )
        percentile_interpolated = norm.cdf(z_interpolated) * 100

        return round(z_interpolated, 2), round(percentile_interpolated, 1)

    def get_hypertension_status(self, age, sex, height_cm, systolic, diastolic):
        ag = int(age)
        sbp = round(systolic)
        dbp = round(diastolic)
        sx = sex
        ht = round(height_cm, 1)

        spc, dpc, sp_percentile, dp_percentile = None, None, None, None

        filtered_table = self.bp_tables[
            (self.bp_tables["sex"] == sx) & (self.bp_tables["age"] == ag)
        ]

        # Pediatric guidelines for children aged 1-<13 years
        if 1 <= ag < 13:
            stab = filtered_table[filtered_table["bp"] == "sbp"]
            sp_tile = (
                stab.iloc[0]
                if ht < stab["h.cm"].iloc[0]
                else (
                    stab.iloc[-1]
                    if ht >= stab["h.cm"].iloc[-1]
                    else stab[stab["h.cm"] > ht].iloc[0]
                    if len(stab[stab["h.cm"] > ht]) > 0
                    else None
                )
            )
            sp_percentile = self.calculate_percentile_using_zscore(sbp, sp_tile)
            dtab = filtered_table[filtered_table["bp"] == "dbp"]
            dp_tile = (
                dtab.iloc[0]
                if ht < dtab["h.cm"].iloc[0]
                else (
                    dtab.iloc[-1]
                    if ht >= dtab["h.cm"].iloc[-1]
                    else dtab[dtab["h.cm"] > ht].iloc[0]
                )
            )
            dp_percentile = self.calculate_percentile_using_zscore(dbp, dp_tile)

            if sbp < sp_tile["p90"]:
                spc = "Normal"
            elif sp_tile["p90"] <= sbp < min(sp_tile["p95"], 120):
                spc = "Elevated"
            elif sp_tile["p95"] <= sbp < min(sp_tile["p95+"], 130):
                spc = "Stage 1"
            else:
                spc = "Stage 2"

            if dbp < dp_tile["p90"]:
                dpc = "Normal"
            elif dp_tile["p90"] <= dbp < min(dp_tile["p95"], 80):
                dpc = "Elevated"
            elif dp_tile["p95"] <= dbp < min(dp_tile["p95+"], 89):
                dpc = "Stage 1"
            else:
                dpc = "Stage 2"

        # Pediatric guidelines for children aged >=13 to <18 years
        elif 13 <= ag < 18:
            if sbp < 120:
                spc = "Normal"
            elif 120 <= sbp < 130:
                spc = "Elevated"
            elif 130 <= sbp <= 139:
                spc = "Stage 1"
            else:
                spc = "Stage 2"

            if dbp < 80:
                dpc = "Normal"
            elif 80 <= dbp <= 89:
                dpc = "Stage 1"
            else:
                dpc = "Stage 2"

            # sp_percentile, dp_percentile = None, None

        # Adult guidelines
        if ag >= 18:
            if sbp < 120 and dbp < 80:
                spc, dpc = "Normal", "Normal"
            elif 120 <= sbp <= 129 and dbp < 80:
                spc, dpc = "Elevated", "Normal"
            elif 130 <= sbp <= 139 or 80 <= dbp <= 89:
                spc, dpc = "Stage 1", "Stage 1"
            elif sbp >= 140 or dbp >= 90:
                spc, dpc = "Stage 2", "Stage 2"
            elif sbp > 180 or dbp > 120:
                spc, dpc = "Hypertensive crisis", "Hypertensive crisis"

            sp_percentile, dp_percentile = (
                None,
                None,
            )  # Percentiles are not applicable for adults based on the guidelines

        # Pediatric guidelines
        else:
            if filtered_table.empty:
                return {
                    "id": None,
                    "age.y": age,
                    "sex": sex,
                    "height.cm": height_cm,
                    "systolic": systolic,
                    "diastolic": diastolic,
                    "SPhtn": spc,
                    "DPhtn": dpc,
                    "SPpercentile": sp_percentile,
                    "DPpercentile": dp_percentile,
                }

            # Systolic calculation
            stab = filtered_table[filtered_table["bp"] == "sbp"]
            sp_tile = (
                stab.iloc[0]
                if ht < stab["h.cm"].iloc[0]
                else (
                    stab.iloc[-1]
                    if ht >= stab["h.cm"].iloc[-1]
                    else stab[stab["h.cm"] > ht].iloc[0]
                )
            )
            sp_percentile = self.calculate_percentile_using_zscore(sbp, sp_tile)

            # Diastolic calculation
            dtab = filtered_table[filtered_table["bp"] == "dbp"]
            dp_tile = (
                dtab.iloc[0]
                if ht < dtab["h.cm"].iloc[0]
                else (
                    dtab.iloc[-1]
                    if ht >= dtab["h.cm"].iloc[-1]
                    else dtab[dtab["h.cm"] > ht].iloc[0]
                )
            )
            dp_percentile = self.calculate_percentile_using_zscore(dbp, dp_tile)

        height_z_score, height_percentile = self.height_zscore_and_percentile(
            age, sex, height_cm
        )

        return {
            "id": None,
            "age.y": age,
            "sex": sex,
            "height.cm": height_cm,
            "systolic": systolic,
            "diastolic": diastolic,
            "SPhtn": spc,
            "DPhtn": dpc,
            "SPpercentile": sp_percentile,
            "DPpercentile": dp_percentile,
            "HeightZScore": height_z_score,
            "HeightPercentile": height_percentile,
        }

    def process_dataframe(self, df):
        # Use the apply method on the dataframe to call `get_hypertension_status` for each row
        results = df.apply(
            lambda row: self.get_hypertension_status(
                row["age.y"],
                row["sex"],
                row["height.cm"],
                row["systolic"],
                row["diastolic"],
            ),
            axis=1,
        )

        # Convert the results into a dataframe
        columns = [
            "id",
            "age.y",
            "sex",
            "height.cm",
            "systolic",
            "diastolic",
            "SPhtn",
            "DPhtn",
            "SPpercentile",
            "DPpercentile",
            "HeightZScore",  # New column for height Z-Score
            "HeightPercentile",  # New column for height Percentile
        ]
        result_df = pd.DataFrame(results.tolist(), columns=columns)
        return result_df
