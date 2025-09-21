from pymongo import MongoClient

#---Connection Configuration----

MONGO_DB_URI = "mongodb+srv://dinod:J4qr0NbNmCAAIvUB@cluster0.hmuptj5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "ai_doctor_db"
COLLECTION_NAME = "doctors"

#--Connecting to the MongoDB---

client = MongoClient(MONGO_DB_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# --- Sample Data ---
sample_doctors = [
    {
        "_id": "D001",
        "name": "Dr. Nimal Perera",
        "specialization": "Cardiologist",
        "experience_years": "15",
        "hospital": "Colombo General Hospital",
        "location": "Colombo",
        "contact": {"phone": "0771234567", "email": "nimal@example.com"},
        "availability": [
            {"day": "Monday", "time_slots": ["Morning", "Evening"]},
            {"day": "Wednesday", "time_slots": ["Afternoon"]}
        ],
        "qualifications": ["MBBS", "MD Cardiology"],
        "languages": ["Sinhala", "English"],
        "ratings": "4.7",
        "consultation_fee": "2500"
    },
    {
        "_id": "D002",
        "name": "Dr. Saman Jayawardena",
        "specialization": "Dermatologist",
        "experience_years": "10",
        "hospital": "Nawaloka Hospital",
        "location": "Colombo",
        "contact": {"phone": "0779876543", "email": "saman@example.com"},
        "availability": [
            {"day": "Tuesday", "time_slots": ["Morning"]},
            {"day": "Thursday", "time_slots": ["Evening"]}
        ],
        "qualifications": ["MBBS", "MD Dermatology"],
        "languages": ["Sinhala", "English", "Tamil"],
        "ratings": "4.5",
        "consultation_fee": "2000"
    },
    {
        "_id": "D003",
        "name": "Dr. Priya Fernando",
        "specialization": "Pediatrician",
        "experience_years": "8",
        "hospital": "Lady Ridgeway Hospital",
        "location": "Colombo",
        "contact": {"phone": "0775556666", "email": "priya@example.com"},
        "availability": [
            {"day": "Monday", "time_slots": ["Morning"]},
            {"day": "Friday", "time_slots": ["Afternoon", "Evening"]}
        ],
        "qualifications": ["MBBS", "MD Pediatrics"],
        "languages": ["Sinhala", "English"],
        "ratings": "4.8",
        "consultation_fee": "2200"
    }
]


# --- Insert Sample Data ---
collection.insert_many(sample_doctors)
print("Sample doctors inserted successfully!")