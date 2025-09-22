class ConfigData:
    DB_NAME = "ai_doctor_db"
    COLLECTION_NAME = "doctors"

    # Database Schema (for MongoDB collection: doctors)
    TABLE_SCHEMA = '''
                    "_id": "string",
                    "name": "string",
                    "specialization": "string",
                    "experience_years": "string",
                    "hospital": "string",
                    "location": "string",
                    "contact": {{
                        "phone": "string",
                        "email": "string"
                    }},
                    "availability": [
                        {{
                            "day": "string",
                            "time_slots": ["string"]
                        }}
                    ],
                    "qualifications": ["string"],
                    "languages": ["string"],
                    "ratings": "string",
                    "consultation_fee": "string"
                    '''


    SCHEMA_DESCRIPTION = '''
                    Here is the description to determine what each key represents:

                    1. _id:
                        - Unique identifier for each doctor.
                    2. name:
                        - Full name of the doctor.
                    3. specialization:
                        - Doctor’s area of specialization 
                          (e.g., Cardiologist, Dermatologist, Pediatrician).
                    4. experience_years:
                        - Total years of medical practice (stored as string).
                    5. hospital:
                        - Name of the hospital/clinic the doctor is associated with.
                    6. location:
                        - City/area where the doctor practices.
                    7. contact:
                        - Contact details.
                        - Fields:
                          - phone: Phone number of the doctor/clinic.
                          - email: Email address of the doctor/clinic.
                    8. availability:
                        - Weekly availability schedule of the doctor.
                        - Array of documents.
                        - Fields:
                          - day: Day of the week (e.g., Monday).
                          - time_slots: Available consultation times (array of strings).
                    9. qualifications:
                        - Educational qualifications and certifications (array of strings).
                    10. languages:
                        - Languages the doctor can speak (array of strings).
                    11. ratings:
                        - Patient ratings (stored as string, e.g., "4.8").
                        - IMPORTANT: Always convert ratings to number using $toDouble before numeric comparisons.
                    12. consultation_fee:
                        - Standard consultation fee (stored as string, e.g., "2200").
                        - IMPORTANT: Always convert consultation_fee to number using $toInt or $toDouble before numeric comparisons.
                    '''


    FEW_SHOT_EXAMPLE_1 = [
        # Find all cardiologists and project only key fields
        {
            "$match": {"specialization": "Cardiologist"}
        },
        {
            "$project": {
                "name": 1,
                "hospital": 1,
                "location": 1,
                "contact": 1,
                "availability": 1
            }
        }
    ]

    FEW_SHOT_EXAMPLE_2 = [
        # Find doctors available on Monday evenings
        {
            "$match": {
                "availability": {
                    "$elemMatch": {
                        "day": "Monday",
                        "time_slots": {"$in": ["Evening"]}
                    }
                }
            }
        },
        {
            "$project": {
                "name": 1,
                "specialization": 1,
                "hospital": 1,
                "availability": 1
            }
        }
    ]

    FEW_SHOT_EXAMPLE_3 = [
        # Find doctors who speak Tamil and charge less than 2000 LKR
        {
            "$addFields": {
                "fee_num": { "$toInt": "$consultation_fee" }
            }
        },
        {
            "$match": {
                "languages": "Tamil",
                "fee_num": {"$lt": 2000}
            }
        },
        {
            "$project": {
                "name": 1,
                "specialization": 1,
                "consultation_fee": 1,
                "languages": 1,
                "hospital": 1
            }
        }
    ]

    FEW_SHOT_EXAMPLE_4 = [
        # Find top-rated dermatologists (rating > 4.5)
        {
            "$addFields": {
                "ratings_num": { "$toDouble": "$ratings" }
            }
        },
        {
            "$match": {
                "specialization": "Dermatologist",
                "ratings_num": { "$gt": 4.5 }
            }
        },
        {
            "$project": {
                "name": 1,
                "hospital": 1,
                "ratings_num": 1,
                "location": 1
            }
        }
    ]
