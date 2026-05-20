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
    WeightLoss = "WeightLoss"
    MuscleGain = "MuscleGain"
    Endurance = "Endurance"
    Strength = "Strength"
    Custom = "Custom"

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

class IntensityLevel(enum.Enum):
    Deload = "Deload"
    Normal = "Normal"
    Progression = "Progression"


class SessionStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"

class EquipmentCategory(str, enum.Enum):
    machine     = "machine"
    free_weight = "free_weight"
    cardio      = "cardio"
    bodyweight  = "bodyweight"
    cable       = "cable"

class FriendshipStatus(str, enum.Enum):
    pending  = "pending"
    accepted = "accepted"
    declined = "declined"

class NotificationType(str, enum.Enum):
    friend_request   = "friend_request"
    friend_accepted  = "friend_accepted"
    reaction_received = "reaction_received"
