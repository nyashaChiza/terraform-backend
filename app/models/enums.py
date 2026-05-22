import enum

# ----- ENUMS -----
# ALL enums inherit from `str` so Pydantic v2 can serialize them to JSON
# without explicit converters. Plain `enum.Enum` members are NOT strings and
# silently fail validation when used in response models that expect `str`.

class Gender(str, enum.Enum):
    Male = "Male"
    Female = "Female"

class ExperienceLevel(str, enum.Enum):
    Beginner = "Beginner"
    Intermediate = "Intermediate"
    Expert = "Expert"

class GoalType(str, enum.Enum):
    WeightLoss = "WeightLoss"
    MuscleGain = "MuscleGain"
    Endurance = "Endurance"
    Strength = "Strength"
    Custom = "Custom"

class GoalStatus(str, enum.Enum):
    Active = "Active"
    Paused = "Paused"
    Completed = "Completed"
    Abandoned = "Abandoned"

class MuscleGroup(str, enum.Enum):
    Chest = "Chest"
    Back = "Back"
    Arms = "Arms"
    Shoulders = "Shoulders"
    Legs = "Legs"
    Core = "Core"

class StressLevel(str, enum.Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"

class PhotoType(str, enum.Enum):
    Before = "Before"
    Progress = "Progress"
    After = "After"

class IntensityLevel(str, enum.Enum):
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
