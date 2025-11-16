import json
import psycopg2
from kafka import KafkaConsumer


def run_consumer():
    """Consumes patient records from Kafka and inserts them into PostgreSQL."""
    try:
        print("[Consumer] Connecting to Kafka at localhost:9092...")
        consumer = KafkaConsumer(
            "patient_records",
            bootstrap_servers="localhost:9092",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            group_id="patient-records-consumer-group",
        )
        print("[Consumer] ✓ Connected to Kafka successfully!")

        print("[Consumer] Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            dbname="kafka_db",
            user="kafka_user",
            password="kafka_password",
            host="localhost",
            port="5432",
        )

        conn.autocommit = True
        cur = conn.cursor()
        print("[Consumer] ✓ Connected to PostgreSQL successfully!")

        # Create table if it doesn't exist
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS patient_records (
                patient_id VARCHAR(50),
                admission_id VARCHAR(50) PRIMARY KEY,
                timestamp TIMESTAMP,
                admission_timestamp TIMESTAMP,
                patient_name VARCHAR(200),
                age INTEGER,
                gender VARCHAR(20),
                department VARCHAR(100),
                primary_diagnosis VARCHAR(200),
                admission_type VARCHAR(50),
                status VARCHAR(50),
                insurance_provider VARCHAR(100),
                heart_rate INTEGER,
                blood_pressure VARCHAR(20),
                temperature_celsius NUMERIC(4, 1),
                oxygen_saturation INTEGER,
                respiratory_rate INTEGER,
                risk_score INTEGER,
                risk_level VARCHAR(20),
                attending_physician VARCHAR(200),
                hospital_location VARCHAR(200)
            );
            """
        )
        print("[Consumer] ✓ Table 'patient_records' ready!")

        print("[Consumer] Listening for patient records...")
        record_count = 0

        for message in consumer:
            record = message.value
            record_count += 1

            try:
                cur.execute(
                    """
                    INSERT INTO patient_records (
                        patient_id, admission_id, timestamp, admission_timestamp,
                        patient_name, age, gender, department, primary_diagnosis,
                        admission_type, status, insurance_provider, heart_rate,
                        blood_pressure, temperature_celsius, oxygen_saturation,
                        respiratory_rate, risk_score, risk_level,
                        attending_physician, hospital_location
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (admission_id) DO NOTHING;
                    """,
                    (
                        record["patient_id"],
                        record["admission_id"],
                        record["timestamp"],
                        record["admission_timestamp"],
                        record["patient_name"],
                        record["age"],
                        record["gender"],
                        record["department"],
                        record["primary_diagnosis"],
                        record["admission_type"],
                        record["status"],
                        record["insurance_provider"],
                        record["heart_rate"],
                        record["blood_pressure"],
                        record["temperature_celsius"],
                        record["oxygen_saturation"],
                        record["respiratory_rate"],
                        record["risk_score"],
                        record["risk_level"],
                        record["attending_physician"],
                        record["hospital_location"],
                    ),
                )

                print(
                    f"[Consumer] ✓ Inserted record #{record_count}: "
                    f"Admission {record['admission_id']} | "
                    f"Patient: {record['patient_name']} | "
                    f"Diagnosis: {record['primary_diagnosis']} | "
                    f"Risk: {record['risk_level']}"
                )

            except Exception as e:
                print(f"[Consumer] ✗ Error inserting record: {e}")

    except KeyboardInterrupt:
        print(f"\n[Consumer] Stopped. Total records processed: {record_count}")
    except Exception as e:
        print(f"[Consumer] Error: {e}")
    finally:
        if "cur" in locals():
            cur.close()
        if "conn" in locals():
            conn.close()
        if "consumer" in locals():
            consumer.close()
        print("[Consumer] Connections closed.")


if __name__ == "__main__":
    run_consumer()
