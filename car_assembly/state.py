from dataclasses import dataclass


@dataclass
class CarSelection:
    car_type: int = 0
    engine: int = 0
    brake: int = 0
    steering: int = 0
