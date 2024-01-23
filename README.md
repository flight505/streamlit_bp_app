
HypertensionDF Class Overview:
==============================

The `HypertensionDF` class is designed to determine hypertension stages and percentiles based on input blood pressure data. It can process individual data points as well as entire dataframes. The class is based on established guidelines and uses a predefined blood pressure table (bptable.csv).

Use Cases:
----------

### Determining Hypertension Status for a Single Individual:

**Use Case:** A doctor or health professional wants to quickly check the hypertension status of an individual patient during a consultation.

**Method:** `get_hypertension_status`

**Inputs:**
- `age`: Age of the individual (in years)
- `sex`: Gender of the individual (1 for male, 2 for female)
- `height_cm`: Height of the individual (in centimeters)
- `systolic`: Systolic blood pressure reading (in mmHg)
- `diastolic`: Diastolic blood pressure reading (in mmHg)

**Output:** A dictionary with fields like `SPhtn`, `DPhtn` (indicating systolic and diastolic hypertension stages) and `SPpercentile`, `DPpercentile` (indicating systolic and diastolic percentiles).

### Processing Blood Pressure Data for Multiple Individuals in a Dataset:

**Use Case:** A researcher or health professional wants to process and analyze blood pressure data for a group of individuals, such as participants in a study or patients in a clinic.

**Method:** `process_dataframe`

**Inputs:**
- `df`: A dataframe containing columns `age.y`, `sex`, `height.cm`, `systolic`, and `diastolic`.

**Output:** A dataframe with added columns for hypertension stages (`SPhtn`, `DPhtn`) and percentiles (`SPpercentile`, `DPpercentile`).

How to Use:
-----------

1. Initialize the class:
```python
hypertension = HypertensionDF()
```
2. For Single Individual Input:
```python
result = hypertension.get_hypertension_status(age=25, sex=1, height_cm=170, systolic=130, diastolic=85)
print(result)
```
This will print the hypertension status and percentiles for the given individual.

3. For DataFrame Input:
First, create or load a dataframe with the necessary columns:
```python
data = {
    'age.y': [25, 30, 35],
    'sex': [1, 2, 1],
    'height.cm': [170, 165, 175],
    'systolic': [130, 120, 140],
    'diastolic': [85, 80, 90]
}
df = pd.DataFrame(data)
```
Then, process the dataframe:
```python
results_df = hypertension.process_dataframe(df)
print(results_df)
```
This will print the dataframe with added columns indicating hypertension status and percentiles for each individual in the original dataframe.

References:
-----------

The class is based on guidelines from two referenced papers:

1. **Clinical Practice Guideline for Screening and Management of High Blood Pressure in Children and Adolescents**. This paper provides guidelines for determining pediatric hypertension classifications based on age, gender, and blood pressure readings.

2. **2017 ACC/AHA/AAPA/ABC/ACPM/AGS/APhA/ASH/ASPC/NMA/PCNA Guideline for the Prevention, Detection, Evaluation, and Management of High Blood Pressure in Adults**. This paper provides guidelines for determining hypertension status in adults.

Z-score Calculation:
--------------------

The Z-score for a given value is calculated using the formula:

\[ Z = rac{X - \mu}{\sigma} \]

Where:
- \( Z \) is the Z-score.
- \( X \) is the value for which the Z-score is being calculated.
- \( \mu \) is the mean of the dataset.
- \( \sigma \) is the standard deviation of the dataset.

The Z-score represents how many standard deviations a value is from the mean of the dataset. It is used in this context to determine the percentile of a given blood pressure value compared to a reference dataset.
