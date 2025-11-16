# Real-Time Healthcare Patient Monitoring System

A real-time data streaming pipeline built with Apache Kafka, PostgreSQL, and Streamlit that demonstrates end-to-end event-driven architecture for healthcare patient monitoring and analytics.

## Overview

This project implements a complete real-time data streaming system that:
- Generates synthetic healthcare patient records with realistic vital signs
- Streams events through Apache Kafka
- Persists data to PostgreSQL database
- Visualizes real-time analytics through an interactive Streamlit dashboard

The system simulates a hospital monitoring environment where patient admissions, vital signs, and diagnoses are tracked and analyzed in real-time.

## Architecture

producer -> Kafka -> consumer -> PostgreSQL -> dashboard -> real-time updates visible

**Data Flow:**
1. **Producer** generates synthetic patient records every 0.5-2 seconds
2. **Kafka** streams events through the `patient_records` topic
3. **Consumer** reads from Kafka and writes to PostgreSQL
4. **Dashboard** queries PostgreSQL and displays real-time visualizations

# Features

# Producer
- Synthetic patient data generation with realistic vital signs
- Randomized medical conditions (Hypertension, Diabetes, COPD, etc.)
- Hospital departments (Emergency, ICU, Cardiology, etc.)
- Automated risk scoring based on vital sign thresholds
- Configurable message generation rate

# Consumer
- Reliable Kafka message consumption with consumer groups
- PostgreSQL persistence with idempotent inserts
- Automatic table schema creation
- Error handling and logging

# Dashboard
- Real-time auto-refreshing visualizations (2-20 second intervals)
- 5 Key Performance Indicators (KPIs):
  - Total patients
  - Total admissions
  - High-risk patient count
  - Average patient age
  - Critical oxygen level alerts
- Interactive charts:
  - Department patient distribution
  - Risk level breakdown
  - Top diagnoses
  - Admission type distribution
- Vital signs overview (heart rate, temperature, O2 saturation, respiratory rate)
- Recent patient records table with color-coded risk levels
- Filter by risk level (Low/Medium/High)
- Configurable refresh interval and record limits

# Prerequisites

```
kafka-python==2.0.2
faker==19.3.1
psycopg2-binary==2.9.7
pandas==2.0.3
plotly==5.16.1
streamlit==1.26.0
sqlalchemy==2.0.20
```

# Installation

# 1. Run the code below to get started
```
docker exec -it kafka kafka-topics --create --topic orders --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

# 2. Create the docker-compose.yml file
Code found in the 'docker-compose.yml' file located within this project

# 3. Create Kafka Topic
```bash
bin/kafka-topics.sh --create --topic patient_records --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

# Usage

### Step 1: Start the Consumer
Open a terminal and run:
```bash
python healthcare_consumer.py
```

Expected output:
```
[Consumer] Connecting to Kafka at localhost:9092...
[Consumer] ✓ Connected to Kafka successfully!
[Consumer] Connecting to PostgreSQL...
[Consumer] ✓ Connected to PostgreSQL successfully!
[Consumer] ✓ Table 'patient_records' ready!
[Consumer] Listening for patient records...
```

### Step 2: Start the Producer
Open a new terminal and run:
```bash
python healthcare_producer.py
```

Expected output:
```
[Producer] Connecting to Kafka at localhost:9092...
[Producer] ✓ Connected to Kafka successfully!
[Producer] Starting to send patient records to 'patient_records' topic...
[Producer] Sent record #1: Patient abc123def456 | Hypertension | Risk: Medium | Dept: Emergency
```

### Step 3: Launch the Dashboard
Open a third terminal and run:
```bash
streamlit run healthcare_dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

##  Configuration

### Producer Configuration
Edit `healthcare_producer.py`:
```python
# Kafka broker
bootstrap_servers="localhost:9092"

# Message generation delay (seconds)
time.sleep(random.uniform(0.5, 2.0))
```

### Consumer Configuration
Edit `healthcare_consumer.py`:
```python
# Kafka settings
bootstrap_servers="localhost:9092"
group_id="patient-records-consumer-group"
auto_offset_reset="earliest"

# PostgreSQL connection
dbname="kafka_db"
user="kafka_user"
password="kafka_password"
host="localhost"
port="5432"
```

### Dashboard Configuration
Edit `healthcare_dashboard.py`:
```python
# PostgreSQL connection string
DATABASE_URL = "postgresql://kafka_user:kafka_password@localhost:5432/kafka_db"

# Default refresh interval (adjustable via sidebar)
value=5  # seconds
```

## Data Schema

### Patient Records Table

| Column                | Type          | Description                              |
|-----------------------|---------------|------------------------------------------|
| patient_id            | VARCHAR(50)   | Unique patient identifier                |
| admission_id          | VARCHAR(50)   | Primary key, unique admission ID         |
| timestamp             | TIMESTAMP     | Record generation time                   |
| admission_timestamp   | TIMESTAMP     | Patient admission time                   |
| patient_name          | VARCHAR(200)  | Generated patient name                   |
| age                   | INTEGER       | Patient age (18-95)                      |
| gender                | VARCHAR(20)   | Male, Female, or Other                   |
| department            | VARCHAR(100)  | Hospital department                      |
| primary_diagnosis     | VARCHAR(200)  | Medical condition                        |
| admission_type        | VARCHAR(50)   | Emergency, Elective, Urgent, Observation |
| status                | VARCHAR(50)   | Current patient status                   |
| insurance_provider    | VARCHAR(100)  | Insurance company name                   |
| heart_rate            | INTEGER       | Heart rate in bpm (50-120)               |
| blood_pressure        | VARCHAR(20)   | Systolic/Diastolic format                |
| temperature_celsius   | NUMERIC(4,1)  | Body temperature (36.0-39.5°C)           |
| oxygen_saturation     | INTEGER       | O2 saturation percentage (85-100%)       |
| respiratory_rate      | INTEGER       | Breaths per minute (12-30)               |
| risk_score            | INTEGER       | Calculated risk score (0-6)              |
| risk_level            | VARCHAR(20)   | Low, Medium, or High                     |
| attending_physician   | VARCHAR(200)  | Doctor's name                            |
| hospital_location     | VARCHAR(200)  | Hospital city                            |

### Risk Scoring Algorithm

The system calculates risk scores based on vital sign thresholds:
- Heart rate >100 or <60 bpm: +1 point
- Blood pressure systolic >140 or <90 mmHg: +1 point
- Temperature >38.0 or <36.5°C: +1 point
- Oxygen saturation <95%: +2 points
- Respiratory rate >20/min: +1 point

**Risk Levels:**
- **Low:** 0-1 points
- **Medium:** 2-3 points
- **High:** 4+ points

## Dashboard Features

### Key Performance Indicators (KPIs)
- **Total Patients**: Unique patient count
- **Total Admissions**: All admission records
- **High Risk Patients**: Count of patients with High risk level
- **Average Age**: Mean age of all patients
- **Critical O2 Levels**: Patients with oxygen saturation <90%

### Visualizations
1. **Admissions by Department** - Bar chart showing patient distribution
2. **Risk Level Distribution** - Pie chart with color-coded risk levels
3. **Top Diagnoses** - Horizontal bar chart of most common conditions
4. **Admission Types** - Pie chart of admission type breakdown
5. **Vital Signs Overview** - Average metrics for key vital signs
6. **Recent Patient Records** - Data table with last 20 admissions

### Interactive Controls (Sidebar)
- Risk level filter (All, Low, Medium, High)
- Auto-refresh interval (2-20 seconds)
- Record display limit (50-500 records)

## Technologies Used

- **Apache Kafka 2.8+** - Distributed event streaming platform
- **PostgreSQL 12+** - Relational database for data persistence
- **Python 3.8+** - Core programming language
- **kafka-python** - Python client for Apache Kafka
- **psycopg2** - PostgreSQL adapter for Python
- **Streamlit** - Web application framework for data dashboards
- **Plotly** - Interactive visualization library
- **Pandas** - Data manipulation and analysis
- **SQLAlchemy** - SQL toolkit and ORM
- **Faker** - Synthetic data generation library

# Dashboard
<video controls src="Real-Time Healthcare Dashboard - Google Chrome 2025-11-16 17-34-06.mp4" title="Title"></video>





