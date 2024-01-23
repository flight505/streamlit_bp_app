import altair as alt
import pandas as pd
import streamlit as st
from data.HypertensionDF import HypertensionDF
from scipy.__config__ import show
from streamlit_echarts import st_echarts
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.tags import tagger_component

# function Load the bptables
# placeholder for markdown text
paper_reference = """## 
Hypertension is a condition in which the force of the blood against the artery walls is too high. 
If left untreated, it can lead to serious health problems including heart disease and stroke.
The class is based on guidelines from two referenced papers:

1. **Clinical Practice Guideline for Screening and Management of High Blood Pressure in Children and Adolescents**. This paper provides guidelines for determining pediatric hypertension classifications based on age, gender, and blood pressure readings.
2. **2017 ACC/AHA/AAPA/ABC/ACPM/AGS/APhA/ASH/ASPC/NMA/PCNA Guideline for the Prevention, Detection, Evaluation, and Management of High Blood Pressure in Adults**. This paper provides guidelines for determining hypertension status in adults.
            """


@st.cache_data
def load_bp_tables(file_path):
    bp_tables = pd.read_csv(file_path)
    sex_bp_combinations = [(1, "sbp"), (1, "dbp"), (2, "sbp"), (2, "dbp")]
    results = []

    # Loop over the different combinations of sex and bp
    for sex, bp in sex_bp_combinations:
        filtered_data = bp_tables.query("sex == @sex and bp == @bp and `h.cent` == 50")

        # Select the first entry for each age
        first_entry_data = filtered_data.drop_duplicates(subset="age", keep="first")

        results.append(first_entry_data)

    (
        first_sbp_data_male,
        first_dbp_data_male,
        first_sbp_data_female,
        first_dbp_data_female,
    ) = results

    return (
        first_sbp_data_male,
        first_dbp_data_male,
        first_sbp_data_female,
        first_dbp_data_female,
    )


def get_data():
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        uploaded_file = pd.read_csv(uploaded_file)

        # here we need a botton to select
        split_sbp_dbp = st.toggle("Split value column into systolic and diastolic")
        if split_sbp_dbp:
            if (
                "systolic" not in uploaded_file.columns
                or "diastolic" not in uploaded_file.columns
            ):
                uploaded_file[["systolic", "diastolic"]] = (
                    uploaded_file["value"].str.split("/", expand=True).astype(float)
                )
        # if split_sbp_dbp is True reload

        if split_sbp_dbp is False:
            st.error(
                "Please make sure you have systolic and diastolic columns or select the split value column into systolic and diastolic"
            )
            st.stop()

        else:
            get_hypertension_statuses(uploaded_file)
        st.dataframe(uploaded_file)


def get_hypertension_statuses(uploaded_file):
    st.spinner(text="In progress...")
    hypertension_statuses = []
    ht_df = HypertensionDF()
    for index, row in uploaded_file.iterrows():
        status = ht_df.get_hypertension_status(
            age=row["age_at_sample"],
            sex=row["sex"],
            height_cm=row["height"],
            systolic=row["systolic"],
            diastolic=row["diastolic"],
        )
        hypertension_statuses.append(status)

    # Add hypertension status to the dataframe
    uploaded_file["hypertension_status"] = hypertension_statuses


def app():
    st.subheader("Determining Hypertension Status for a Single Individual")
    with st.expander("What is hypertension?"):
        st.markdown(paper_reference)
    ht_single = HypertensionDF()
    # Create a session state object
    if "state" not in st.session_state:
        st.session_state.state = {}

    # create 2 columns 1/3 and 2/3
    col1, col2, col3 = st.columns([1, 2, 1])
    # create 6 columns

    with col1:
        with st.form(key="subject_form", clear_on_submit=False):
            st.write("**Subject Information**")
            age = st.number_input("Age", min_value=1, max_value=100, step=1)
            gender_dict = {"Male": "1", "Female": "2"}
            gender = st.selectbox("Sex", options=gender_dict.keys())
            sex = int(gender_dict[gender])
            height = st.number_input(
                "Height", min_value=0.0, max_value=220.0, step=0.1, format="%.1f"
            )
            st.divider()
            systolic = st.number_input("Systolic", min_value=60, max_value=180, step=1)
            diastolic = st.number_input(
                "Diastolic", min_value=20, max_value=120, step=1
            )
            # st.divider()

            submit_button = st.form_submit_button(label="Calculate")

    # Store the user inputs in the session state object
    st.session_state.state["age"] = age
    if age >= 18:
        st.warning("The plots are not applicable for adults based on the guidelines.")
    else:
        # Your existing code to generate the plots goes here
        st.session_state.state["sex"] = sex
        st.session_state.state["height in cm"] = height
        st.session_state.state["systolic"] = systolic
        st.session_state.state["diastolic"] = diastolic

    def init_dicts():
        return {
            "status": {
                "id": 0,
                "age.y": 0,
                "sex": 0,
                "height.cm": 0,
                "systolic": 0,
                "diastolic": 0,
                "SPhtn": 0,
                "DPhtn": 0,
                "SPpercentile": 0,
                "DPpercentile": 0,
                "HeightZScore": 0,
                "HeightPercentile": 0,
            },
        }

    if "status" not in st.session_state:
        st.session_state.update(init_dicts())

    # If the submit button was clicked, calculate the hypertension status
    if submit_button:
        status = ht_single.get_hypertension_status(
            age=age,
            sex=sex,
            height_cm=height,
            systolic=systolic,
            diastolic=diastolic,
        )
        st.session_state.status = status

    status = st.session_state.status

    systolic_percentile = status.get("SPpercentile")
    diastolic_percentile = status.get("DPpercentile")

    systolic_percentile = (
        int(systolic_percentile) if systolic_percentile is not None else 0
    )
    diastolic_percentile = (
        int(diastolic_percentile) if diastolic_percentile is not None else 0
    )

    with col3:
        with stylable_container(
            key="results_with_border",
            css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.4rem;
                padding: calc(1em - 1px)
            }
            """,
        ):
            # tagger_component(
            #     "**BP Percentiles:**",
            #     [
            #         f'Systolic: **{int(status.get("SPpercentile"))}**',
            #         f'Diastolic: **{int(status.get("DPpercentile"))}**',
            #     ],
            #     color_name=["blue", "orange"],
            # )
            tagger_component(
                "**BP Percentiles:**",
                [
                    f"Systolic: **{systolic_percentile}**",
                    f"Diastolic: **{diastolic_percentile}**",
                ],
                color_name=["blue", "orange"],
            )
            st.write(" ")
            st.write(" ")
            # with col2:
            tagger_component(
                "**Height information**:",
                [
                    f'Z score: **{status.get("HeightZScore", 0)}**',
                    f'Percentile: **{status.get("HeightPercentile", 0)}**',
                ],
                color_name=["blue", "orange"],
            )
            st.write(" ")
            st.write(" ")
            tagger_component(
                "**Categories & Stages:**",
                [
                    f'Systolic: **{status.get("SPhtn", "-")}**',
                    f'Diastolic: **{status.get("DPhtn", "-")}**',
                ],
                color_name=["blue", "orange"],
            )

            st.write(" ")
            st.write(" ")
            st.write(" ")
            st.write(" ")
            st.write(" ")
            st.write(" ")
            st.write(" ")
            st.write(" ")
            st.write(" ")

    # Load the bptables
    (
        sbp_data_male,
        dbp_data_male,
        sbp_data_female,
        dbp_data_female,
    ) = load_bp_tables("data/bptable.csv")

    sex = st.session_state.state["sex"]

    # Select the appropriate data based on the sex
    if sex == 1:
        sbp_data = sbp_data_male
        dbp_data = dbp_data_male
        sex = "Male"
    elif sex == 2:
        sbp_data = sbp_data_female
        dbp_data = dbp_data_female
        sex = "Female"
    else:
        st.error("Invalid sex value. Please select 1 for male or 2 for female.")
        return

    subject_status = st.session_state.status

    def plot_dbp_chart_echarts(dbp_data, sex, subject_age=None, subject_diastolic=None):
        # Define Streamlit colors and corresponding line labels
        st_colors = ["#FF2B06", "#F97600", "#FDBF11", "#3366CC"]
        line_labels = ["p50", "p90", "p95", "p95+"]

        # Series data
        series = []
        for label, color in zip(line_labels, st_colors):
            series_data = dbp_data[["age", label]].values.tolist()
            series.append(
                {"name": label, "type": "line", "data": series_data, "color": color}
            )

        # If subject's age and diastolic values are provided, add a point for the subject
        if subject_age and subject_diastolic:
            series.append(
                {
                    "name": "Subject",
                    "type": "scatter",
                    "data": [[subject_age, subject_diastolic]],
                    "color": "black",
                    "symbolSize": 10,
                }
            )

        # ECharts structure
        echart = {
            "title": {
                "text": f"Diastolic - {sex}",
                "textAlign": "left",
                "textStyle": {
                    "fontSize": 14,
                },
            },
            "tooltip": {
                "trigger": "item",
                # 'axisPointer': {
                #     'type': 'shadow',
                #     'label': {
                #         'backgroundColor': '#6a7985'
                #     }
                # }
            },
            "legend": {
                "bottom": 0,
                "data": line_labels
                + (["Subject"] if subject_age and subject_diastolic else []),
            },
            "xAxis": {
                "type": "category",
                "min": 0,
                "max": 17,
            },
            "yAxis": {"type": "value", "min": 20, "max": 100},
            "series": series,
        }

        return echart

    def plot_sbp_chart_echarts(sbp_data, sex, subject_age=None, subject_systolic=None):
        # Define Streamlit colors and corresponding line labels
        st_colors = ["#FF2B06", "#F97600", "#FDBF11", "#3366CC"]
        line_labels = ["p50", "p90", "p95", "p95+"]

        # Series data
        series = []
        for label, color in zip(line_labels, st_colors):
            series_data = sbp_data[["age", label]].values.tolist()
            series.append(
                {"name": label, "type": "line", "data": series_data, "color": color}
            )

        # If subject's age and diastolic values are provided, add a point for the subject
        if subject_age and subject_systolic:
            series.append(
                {
                    "name": "Subject",
                    "type": "scatter",
                    "data": [[subject_age, subject_systolic]],
                    "color": "black",
                    "symbolSize": 10,
                }
            )

        # ECharts structure
        echart = {
            "title": {
                "text": f"Systolic - {sex}",
                "textAlign": "left",
                "textStyle": {"fontSize": 14},
            },
            "tooltip": {
                "trigger": "item",
                # 'axisPointer': {
                #     'type': 'shadow',
                #     'label': {
                #         'backgroundColor': '#6a7985'
                #     }
                # }
            },
            # 'legend': {
            #     'bottom': 0,
            #     'data': line_labels + (['Subject'] if subject_age and subject_systolic else [])
            # },
            "xAxis": {
                "type": "category",
                "min": 0,
                "max": 17,
            },
            "yAxis": {
                "type": "value",
                "min": 60,
                "max": 160,
            },
            "series": series,
        }

        return echart

    with col2:
        with stylable_container(
            key="container_with_border",
            css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.4rem;
                padding: calc(1em - 1px)
            }
            """,
        ):
            # c1, c2 = st.columns(2)
            st_echarts(
                plot_sbp_chart_echarts(
                    sbp_data, sex, subject_status["age.y"], subject_status["systolic"]
                ),
                height=250,
            )

            st_echarts(
                plot_dbp_chart_echarts(
                    dbp_data, sex, subject_status["age.y"], subject_status["diastolic"]
                ),
                height=250,
            )

    # st.write(st.session_state)

    with st.expander("Upload a CSV file"):
        get_data()
