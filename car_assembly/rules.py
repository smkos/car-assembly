from dataclasses import dataclass
from typing import Any, Callable, Optional

from car_assembly.options import (
    BOSCH_B,
    BOSCH_S,
    CONTINENTAL,
    MANDO,
    SEDAN,
    SUV,
    TOYOTA,
    TRUCK,
    WIA,
)


@dataclass(frozen=True)
class CompatibilityRule:
    is_violated: Callable[[Any], bool]
    fail_message: str


COMPATIBILITY_RULES: list[CompatibilityRule] = [
    CompatibilityRule(
        lambda s: s.car_type == SEDAN and s.brake == CONTINENTAL,
        "Sedan에는 Continental제동장치 사용 불가",
    ),
    CompatibilityRule(
        lambda s: s.car_type == SUV and s.engine == TOYOTA,
        "SUV에는 TOYOTA엔진 사용 불가",
    ),
    CompatibilityRule(
        lambda s: s.car_type == TRUCK and s.engine == WIA,
        "Truck에는 WIA엔진 사용 불가",
    ),
    CompatibilityRule(
        lambda s: s.car_type == TRUCK and s.brake == MANDO,
        "Truck에는 Mando제동장치 사용 불가",
    ),
    CompatibilityRule(
        lambda s: s.brake == BOSCH_B and s.steering != BOSCH_S,
        "Bosch제동장치에는 Bosch조향장치 이외 사용 불가",
    ),
]


def first_violated_rule(selection: Any) -> Optional[CompatibilityRule]:
    return next((rule for rule in COMPATIBILITY_RULES if rule.is_violated(selection)), None)
