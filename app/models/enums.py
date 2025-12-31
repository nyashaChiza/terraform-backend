import enum

# ----- ENUMS -----
class Gender(enum.Enum):
    Male = "Male"
    Female = "Female"

class ExperienceLevel(enum.Enum):
    Beginner = "Beginner"
    Intermediate = "Intermediate"
    Expert = "Expert"

class GoalType(enum.Enum):
    FatLoss = "FatLoss"
    MuscleGain = "MuscleGain"
    Recomposition = "Recomposition"

class GoalStatus(enum.Enum):
    Active = "Active"
    Paused = "Paused"
    Completed = "Completed"
    Abandoned = "Abandoned"

class MuscleGroup(enum.Enum):
    Chest = "Chest"
    Back = "Back"
    Arms = "Arms"
    Shoulders = "Shoulders"
    Legs = "Legs"
    Core = "Core"

class StressLevel(enum.Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"

class PhotoType(enum.Enum):
    Before = "Before"
    Progress = "Progress"
    After = "After"

