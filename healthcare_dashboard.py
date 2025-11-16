import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Real-Time Healthcare Dashboard", layout="wide")
st.title("🏥 Real-Time Patient Monitoring Dashboard")

DATABASE_URL = "postgresql://kafka_user:kafka_password@localhost:5432/kafka_db"


@st.cache_resource
def get_engine(url: str):
    return create_engine(url, pool_pre_ping=True)


engine = get_engine(DATABASE_URL)


def load_data(risk_filter: str | None = None, limit: int = 200) -> pd.DataFrame:
    """Load patient records from PostgreSQL with optional risk level filtering."""
    base_query = "SELECT * FROM patient_records"
    params = {}

    if risk_filter and risk_filter != "All":
        base_query += " WHERE risk_level = :risk_level"
        params["risk_level"] = risk_filter

    base_query += " ORDER BY timestamp DESC LIMIT :limit"
    params["limit"] = limit

    try:
        df = pd.read_sql_query(text(base_query), con=engine.connect(), params=params)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


# Sidebar controls
st.sidebar.header("⚙️ Dashboard Controls")

risk_filter = st.sidebar.selectbox(
    "Filter by Risk Level", ["All", "Low", "Medium", "High"], index=0
)

refresh_interval = st.sidebar.slider(
    "Auto-refresh interval (seconds)", min_value=2, max_value=20, value=5, step=1
)

record_limit = st.sidebar.slider(
    "Number of records to display", min_value=50, max_value=500, value=200, step=50
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Main dashboard loop
placeholder = st.empty()

# Iteration counter for unique keys
iteration = 0

while True:
    # Increment counter for unique keys in each iteration
    iteration += 1

    with placeholder.container():
        df = load_data(risk_filter=risk_filter, limit=record_limit)

        if df.empty:
            st.warning(
                "No patient records available. Start the producer and consumer first."
            )
            time.sleep(refresh_interval)
            continue

        # Key Performance Indicators
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            total_patients = df["patient_id"].nunique()
            st.metric("Total Patients", total_patients)

        with col2:
            total_admissions = len(df)
            st.metric("Total Admissions", total_admissions)

        with col3:
            high_risk_count = len(df[df["risk_level"] == "High"])
            st.metric("High Risk Patients", high_risk_count)

        with col4:
            avg_age = df["age"].mean()
            st.metric("Average Age", f"{avg_age:.1f}")

        with col5:
            critical_vitals = len(df[df["oxygen_saturation"] < 90])
            st.metric("Critical O2 Levels", critical_vitals)

        st.markdown("---")

        # Charts Section
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("📊 Admissions by Department")
            dept_counts = df["department"].value_counts().reset_index()
            dept_counts.columns = ["Department", "Count"]
            fig_dept = px.bar(
                dept_counts,
                x="Department",
                y="Count",
                color="Count",
                color_continuous_scale="Blues",
                title="Patient Distribution Across Departments",
            )
            fig_dept.update_layout(showlegend=False)
            # Dynamic key using iteration counter
            st.plotly_chart(
                fig_dept, use_container_width=True, key=f"dept_chart_{iteration}"
            )

        with col_right:
            st.subheader("⚠️ Risk Level Distribution")
            risk_counts = df["risk_level"].value_counts().reset_index()
            risk_counts.columns = ["Risk Level", "Count"]
            color_map = {"Low": "#00CC96", "Medium": "#FFA15A", "High": "#EF553B"}
            fig_risk = px.pie(
                risk_counts,
                names="Risk Level",
                values="Count",
                title="Patient Risk Level Breakdown",
                color="Risk Level",
                color_discrete_map=color_map,
            )
            # Dynamic key using iteration counter
            st.plotly_chart(
                fig_risk, use_container_width=True, key=f"risk_chart_{iteration}"
            )

        # Second row of charts
        col_left2, col_right2 = st.columns(2)

        with col_left2:
            st.subheader("🩺 Top Diagnoses")
            diagnosis_counts = (
                df["primary_diagnosis"].value_counts().head(8).reset_index()
            )
            diagnosis_counts.columns = ["Diagnosis", "Count"]
            fig_diag = px.bar(
                diagnosis_counts,
                y="Diagnosis",
                x="Count",
                orientation="h",
                color="Count",
                color_continuous_scale="Reds",
                title="Most Common Primary Diagnoses",
            )
            # Dynamic key using iteration counter
            st.plotly_chart(
                fig_diag, use_container_width=True, key=f"diag_chart_{iteration}"
            )

        with col_right2:
            st.subheader("🏥 Admission Types")
            admission_counts = df["admission_type"].value_counts().reset_index()
            admission_counts.columns = ["Admission Type", "Count"]
            fig_admission = px.pie(
                admission_counts,
                names="Admission Type",
                values="Count",
                title="Admission Type Distribution",
            )
            # Dynamic key using iteration counter
            st.plotly_chart(
                fig_admission,
                use_container_width=True,
                key=f"admission_chart_{iteration}",
            )

        st.markdown("---")

        # Vital Signs Statistics
        st.subheader("💓 Vital Signs Overview")
        vital_col1, vital_col2, vital_col3, vital_col4 = st.columns(4)

        with vital_col1:
            avg_hr = df["heart_rate"].mean()
            st.metric("Avg Heart Rate", f"{avg_hr:.0f} bpm")

        with vital_col2:
            avg_temp = df["temperature_celsius"].mean()
            st.metric("Avg Temperature", f"{avg_temp:.1f}°C")

        with vital_col3:
            avg_o2 = df["oxygen_saturation"].mean()
            st.metric("Avg O2 Saturation", f"{avg_o2:.0f}%")

        with vital_col4:
            avg_resp = df["respiratory_rate"].mean()
            st.metric("Avg Respiratory Rate", f"{avg_resp:.0f} /min")

        st.markdown("---")

        # Recent Patient Records Table
        st.subheader("📋 Recent Patient Records")

        display_cols = [
            "admission_id",
            "patient_name",
            "age",
            "gender",
            "department",
            "primary_diagnosis",
            "status",
            "risk_level",
            "heart_rate",
            "oxygen_saturation",
            "temperature_celsius",
            "timestamp",
        ]

        display_df = df[display_cols].head(20).copy()
        display_df.columns = [
            "Admission ID",
            "Patient Name",
            "Age",
            "Gender",
            "Department",
            "Diagnosis",
            "Status",
            "Risk",
            "HR (bpm)",
            "O2 (%)",
            "Temp (°C)",
            "Timestamp",
        ]

        st.dataframe(display_df, use_container_width=True, height=400)

        # Wait before refreshing
        time.sleep(refresh_interval)
