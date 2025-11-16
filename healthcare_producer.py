import time
import json
import uuid
import random
from datetime import datetime, timedelta
from kafka import KafkaProducer
from faker import Faker

fake = Faker()

def generate_synthetic_patient_record():
    """Generates synthetic healthcare patient records with vital signs and diagnosis."""

    # Medical data lists
    conditions = [
        "Hypertension", "Diabetes Type 2", "Asthma", "Pneumonia", 
        "COPD", "Heart Failure", "Sepsis", "Stroke", "COVID-19", "Influenza"
    ]

    departments = [
        "Emergency", "Cardiology", "Pulmonology", "Internal Medicine",
        "ICU", "Neurology", "Pediatrics", "Geriatrics"
    ]

    admission_types = ["Emergency", "Elective", "Urgent", "Observation"]

    statuses = ["Admitted", "Discharged", "In Treatment", "Observation"]

    insurance_providers = [
        "Medicare", "Medicaid", "Blue Cross", "Aetna", "UnitedHealthcare", "Cigna"
    ]

    # Generate vital signs with realistic ranges
    heart_rate = random.randint(50, 120)  # bpm
    blood_pressure_systolic = random.randint(90, 180)  # mmHg
    blood_pressure_diastolic = random.randint(60, 110)  # mmHg
    temperature = round(random.uniform(36.0, 39.5), 1)  # Celsius
    oxygen_saturation = random.randint(85, 100)  # percentage
    respiratory_rate = random.randint(12, 30)  # breaths per minute

    # Generate patient demographics
    age = random.randint(18, 95)
    gender = random.choice(["Male", "Female", "Other"])

    # Calculate risk score based on vital signs
    risk_score = 0
    if heart_rate > 100 or heart_rate < 60:
        risk_score += 1
    if blood_pressure_systolic > 140 or blood_pressure_systolic < 90:
        risk_score += 1
    if temperature > 38.0 or temperature < 36.5:
        risk_score += 1
    if oxygen_saturation < 95:
        risk_score += 2
    if respiratory_rate > 20:
        risk_score += 1

    # Classify risk level
    if risk_score <= 1:
        risk_level = "Low"
    elif risk_score <= 3:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # Generate admission timestamp (within last 7 days)
    admission_time = datetime.now() - timedelta(days=random.randint(0, 7))

    return {
        "patient_id": str(uuid.uuid4())[:12],
        "admission_id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().isoformat(),
        "admission_timestamp": admission_time.isoformat(),
        "patient_name": fake.name(),
        "age": age,
        "gender": gender,
        "department": random.choice(departments),
        "primary_diagnosis": random.choice(conditions),
        "admission_type": random.choice(admission_types),
        "status": random.choice(statuses),
        "insurance_provider": random.choice(insurance_providers),
        "heart_rate": heart_rate,
        "blood_pressure": f"{blood_pressure_systolic}/{blood_pressure_diastolic}",
        "temperature_celsius": temperature,
        "oxygen_saturation": oxygen_saturation,
        "respiratory_rate": respiratory_rate,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "attending_physician": fake.name(),
        "hospital_location": fake.city()
    }

def run_producer():
    """Produces synthetic patient records to Kafka topic."""
    try:
        print("[Producer] Connecting to Kafka at localhost:9092...")
        producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        print("[Producer] ✓ Connected to Kafka successfully!")
        print("[Producer] Starting to send patient records to 'patient_records' topic...")

        record_count = 0
        while True:
            record = generate_synthetic_patient_record()
            producer.send("patient_records", value=record)
            record_count += 1
            print(f"[Producer] Sent record #{record_count}: Patient {record['patient_id']} | "
                  f"{record['primary_diagnosis']} | Risk: {record['risk_level']} | "
                  f"Dept: {record['department']}")

            # Random delay between 0.5 and 3 seconds
            time.sleep(random.uniform(0.5, 3.0))

    except KeyboardInterrupt:
        print(f"\n[Producer] Stopped. Total records sent: {record_count}")
    except Exception as e:
        print(f"[Producer] Error: {e}")
    finally:
        if 'producer' in locals():
            producer.close()
            print("[Producer] Connection closed.")

if __name__ == "__main__":
    run_producer()
