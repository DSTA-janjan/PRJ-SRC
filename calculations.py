from dataclasses import dataclass
from typing import Literal


Gender = Literal["male", "female"]


@dataclass
class BodyMetrics:
    weight_kg: float
    height_cm: float
    age: int
    gender: Gender
    activity_factor: float = 1.2


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """BMI using standard formula: weight_kg / (height_m^2)."""
    height_m = height_cm / 100.0
    if height_m <= 0:
        raise ValueError("Height must be greater than zero")
    return weight_kg / (height_m ** 2)


def calculate_bmr_mifflin_st_jeor(metrics: BodyMetrics) -> float:
    """
    Basal Metabolic Rate using the Mifflin–St Jeor equation.

    - Male:   BMR = 10W + 6.25H - 5A + 5
    - Female: BMR = 10W + 6.25H - 5A - 161

    Where:
    - W = weight in kg
    - H = height in cm
    - A = age in years
    """
    w = metrics.weight_kg
    h = metrics.height_cm
    a = metrics.age
    if metrics.gender == "male":
        return 10 * w + 6.25 * h - 5 * a + 5
    else:
        return 10 * w + 6.25 * h - 5 * a - 161


def calculate_tdee(bmr: float, activity_factor: float) -> float:
    """Total Daily Energy Expenditure = BMR × Activity Factor."""
    if activity_factor <= 0:
        raise ValueError("Activity factor must be greater than zero")
    return bmr * activity_factor



