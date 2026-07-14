from types import SimpleNamespace

from car_assembly.options import (
    BOSCH_B,
    BOSCH_S,
    CONTINENTAL,
    GM,
    MANDO,
    MOBIS,
    SEDAN,
    SUV,
    TOYOTA,
    TRUCK,
    WIA,
)
from car_assembly.rules import COMPATIBILITY_RULES, first_violated_rule


def selection(car_type=SEDAN, engine=GM, brake=MANDO, steering=BOSCH_S):
    return SimpleNamespace(car_type=car_type, engine=engine, brake=brake, steering=steering)


def test_rules_count_and_order():
    assert len(COMPATIBILITY_RULES) == 5
    assert [rule.fail_message for rule in COMPATIBILITY_RULES] == [
        "Sedan에는 Continental제동장치 사용 불가",
        "SUV에는 TOYOTA엔진 사용 불가",
        "Truck에는 WIA엔진 사용 불가",
        "Truck에는 Mando제동장치 사용 불가",
        "Bosch제동장치에는 Bosch조향장치 이외 사용 불가",
    ]


def test_baseline_selection_passes_all_rules():
    assert first_violated_rule(selection()) is None


def test_rule1_sedan_continental():
    violated = first_violated_rule(selection(car_type=SEDAN, brake=CONTINENTAL))
    assert violated is not None
    assert violated.fail_message == "Sedan에는 Continental제동장치 사용 불가"


def test_rule2_suv_toyota():
    violated = first_violated_rule(selection(car_type=SUV, engine=TOYOTA))
    assert violated is not None
    assert violated.fail_message == "SUV에는 TOYOTA엔진 사용 불가"


def test_rule3_truck_wia():
    violated = first_violated_rule(
        selection(car_type=TRUCK, engine=WIA, brake=CONTINENTAL)
    )
    assert violated is not None
    assert violated.fail_message == "Truck에는 WIA엔진 사용 불가"


def test_rule4_truck_mando():
    violated = first_violated_rule(selection(car_type=TRUCK, brake=MANDO))
    assert violated is not None
    assert violated.fail_message == "Truck에는 Mando제동장치 사용 불가"


def test_rule5_bosch_brake_non_bosch_steering():
    violated = first_violated_rule(selection(brake=BOSCH_B, steering=MOBIS))
    assert violated is not None
    assert violated.fail_message == "Bosch제동장치에는 Bosch조향장치 이외 사용 불가"


def test_first_match_wins_when_rule3_and_rule4_both_violated():
    violated = first_violated_rule(
        selection(car_type=TRUCK, engine=WIA, brake=MANDO, steering=BOSCH_S)
    )
    assert violated is not None
    assert violated.fail_message == "Truck에는 WIA엔진 사용 불가"
