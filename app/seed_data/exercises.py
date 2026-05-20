EXERCISE_SEED_DATA = [
    # ── Cardio ──────────────────────────────────────────────────────────────
    {"name": "Stationary Bike",    "primary_muscle": "Legs",      "secondary_muscles": [],             "stress_level": "Low",    "equipment_category": "cardio"},
    {"name": "Treadmill",          "primary_muscle": "Legs",      "secondary_muscles": [],             "stress_level": "Low",    "equipment_category": "cardio"},
    {"name": "Rowing Machine",     "primary_muscle": "Back",      "secondary_muscles": ["Arms", "Legs"],"stress_level": "Medium", "equipment_category": "cardio"},
    {"name": "Elliptical Trainer", "primary_muscle": "Legs",      "secondary_muscles": [],             "stress_level": "Low",    "equipment_category": "cardio"},

    # ── Machines ────────────────────────────────────────────────────────────
    {"name": "Leg Press",                   "primary_muscle": "Legs",      "secondary_muscles": [],             "stress_level": "High",   "equipment_category": "machine"},
    {"name": "Leg Extension",               "primary_muscle": "Legs",      "secondary_muscles": [],             "stress_level": "Medium", "equipment_category": "machine"},
    {"name": "Leg Curl",                    "primary_muscle": "Legs",      "secondary_muscles": [],             "stress_level": "Medium", "equipment_category": "machine"},
    {"name": "Chest Press (Machine)",       "primary_muscle": "Chest",     "secondary_muscles": ["Shoulders"],  "stress_level": "High",   "equipment_category": "machine"},
    {"name": "Pec Fly (Machine)",           "primary_muscle": "Chest",     "secondary_muscles": [],             "stress_level": "Medium", "equipment_category": "machine"},
    {"name": "Shoulder Press (Machine)",    "primary_muscle": "Shoulders", "secondary_muscles": [],             "stress_level": "High",   "equipment_category": "machine"},
    {"name": "Abdominal Crunch (Machine)",  "primary_muscle": "Core",      "secondary_muscles": [],             "stress_level": "Medium", "equipment_category": "machine"},
    {"name": "Seated Row (Machine)",        "primary_muscle": "Back",      "secondary_muscles": ["Arms"],       "stress_level": "Medium", "equipment_category": "machine"},
    {"name": "Hip Abductor Machine",        "primary_muscle": "Legs",      "secondary_muscles": [],             "stress_level": "Low",    "equipment_category": "machine"},
    {"name": "Back Extension Machine",      "primary_muscle": "Back",      "secondary_muscles": [],             "stress_level": "Medium", "equipment_category": "machine"},

    # ── Free Weights ─────────────────────────────────────────────────────────
    {"name": "Barbell Squat",          "primary_muscle": "Legs",      "secondary_muscles": ["Core"],           "stress_level": "High",   "equipment_category": "free_weight"},
    {"name": "Barbell Deadlift",       "primary_muscle": "Back",      "secondary_muscles": ["Legs", "Core"],   "stress_level": "High",   "equipment_category": "free_weight"},
    {"name": "Barbell Bench Press",    "primary_muscle": "Chest",     "secondary_muscles": ["Shoulders","Arms"],"stress_level": "High",   "equipment_category": "free_weight"},
    {"name": "Barbell Row",            "primary_muscle": "Back",      "secondary_muscles": ["Arms"],           "stress_level": "High",   "equipment_category": "free_weight"},
    {"name": "Barbell Overhead Press", "primary_muscle": "Shoulders", "secondary_muscles": ["Arms"],           "stress_level": "High",   "equipment_category": "free_weight"},
    {"name": "Dumbbell Lunges",        "primary_muscle": "Legs",      "secondary_muscles": [],                 "stress_level": "Medium", "equipment_category": "free_weight"},
    {"name": "Dumbbell Shoulder Press","primary_muscle": "Shoulders", "secondary_muscles": ["Arms"],           "stress_level": "Medium", "equipment_category": "free_weight"},
    {"name": "Dumbbell Curl",          "primary_muscle": "Arms",      "secondary_muscles": [],                 "stress_level": "Medium", "equipment_category": "free_weight"},
    {"name": "Dumbbell Tricep Extension","primary_muscle": "Arms",    "secondary_muscles": [],                 "stress_level": "Medium", "equipment_category": "free_weight"},
    {"name": "Dumbbell Lateral Raise", "primary_muscle": "Shoulders", "secondary_muscles": [],                 "stress_level": "Low",    "equipment_category": "free_weight"},
    {"name": "Dumbbell Romanian Deadlift","primary_muscle": "Legs",   "secondary_muscles": ["Back"],           "stress_level": "High",   "equipment_category": "free_weight"},
    {"name": "Dumbbell Chest Fly",     "primary_muscle": "Chest",     "secondary_muscles": [],                 "stress_level": "Medium", "equipment_category": "free_weight"},
    {"name": "Dumbbell Row",           "primary_muscle": "Back",      "secondary_muscles": ["Arms"],           "stress_level": "Medium", "equipment_category": "free_weight"},

    # ── Cables ───────────────────────────────────────────────────────────────
    {"name": "Lat Pulldown",           "primary_muscle": "Back",      "secondary_muscles": ["Arms"],           "stress_level": "Medium", "equipment_category": "cable"},
    {"name": "Seated Cable Row",       "primary_muscle": "Back",      "secondary_muscles": ["Arms"],           "stress_level": "Medium", "equipment_category": "cable"},
    {"name": "Cable Bicep Curl",       "primary_muscle": "Arms",      "secondary_muscles": [],                 "stress_level": "Medium", "equipment_category": "cable"},
    {"name": "Tricep Pushdown (Cable)","primary_muscle": "Arms",      "secondary_muscles": [],                 "stress_level": "Medium", "equipment_category": "cable"},
    {"name": "Cable Lateral Raise",    "primary_muscle": "Shoulders", "secondary_muscles": [],                 "stress_level": "Low",    "equipment_category": "cable"},
    {"name": "Cable Chest Fly",        "primary_muscle": "Chest",     "secondary_muscles": [],                 "stress_level": "Medium", "equipment_category": "cable"},
    {"name": "Cable Face Pull",        "primary_muscle": "Shoulders", "secondary_muscles": ["Back"],           "stress_level": "Low",    "equipment_category": "cable"},
    {"name": "Cable Crunch",           "primary_muscle": "Core",      "secondary_muscles": [],                 "stress_level": "Medium", "equipment_category": "cable"},
    {"name": "Cable Kickback",         "primary_muscle": "Legs",      "secondary_muscles": [],                 "stress_level": "Low",    "equipment_category": "cable"},

    # ── Bodyweight ───────────────────────────────────────────────────────────
    {"name": "Push-Up",         "primary_muscle": "Chest",     "secondary_muscles": ["Arms","Shoulders"],  "stress_level": "Medium", "equipment_category": "bodyweight"},
    {"name": "Pull-Up",         "primary_muscle": "Back",      "secondary_muscles": ["Arms"],              "stress_level": "High",   "equipment_category": "bodyweight"},
    {"name": "Dip",             "primary_muscle": "Arms",      "secondary_muscles": ["Chest","Shoulders"], "stress_level": "High",   "equipment_category": "bodyweight"},
    {"name": "Bodyweight Squat","primary_muscle": "Legs",      "secondary_muscles": ["Core"],              "stress_level": "Low",    "equipment_category": "bodyweight"},
    {"name": "Lunge",           "primary_muscle": "Legs",      "secondary_muscles": [],                    "stress_level": "Low",    "equipment_category": "bodyweight"},
    {"name": "Plank",           "primary_muscle": "Core",      "secondary_muscles": [],                    "stress_level": "Low",    "equipment_category": "bodyweight"},
    {"name": "Crunch",          "primary_muscle": "Core",      "secondary_muscles": [],                    "stress_level": "Low",    "equipment_category": "bodyweight"},
    {"name": "Burpee",          "primary_muscle": "Legs",      "secondary_muscles": ["Chest","Core"],      "stress_level": "High",   "equipment_category": "bodyweight"},
    {"name": "Mountain Climber","primary_muscle": "Core",      "secondary_muscles": ["Legs"],              "stress_level": "Medium", "equipment_category": "bodyweight"},
    {"name": "Glute Bridge",    "primary_muscle": "Legs",      "secondary_muscles": ["Core"],              "stress_level": "Low",    "equipment_category": "bodyweight"},
]
