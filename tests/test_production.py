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
from car_assembly.production import run_produced_car
from car_assembly.production import test_produced_car as check_produced_car
from car_assembly.state import CarSelection

PASSING = CarSelection(car_type=SEDAN, engine=GM, brake=MANDO, steering=BOSCH_S)

RULE_VIOLATIONS = [
    (
        CarSelection(car_type=SEDAN, engine=GM, brake=CONTINENTAL, steering=BOSCH_S),
        "Sedan에는 Continental제동장치 사용 불가",
    ),
    (
        CarSelection(car_type=SUV, engine=TOYOTA, brake=MANDO, steering=BOSCH_S),
        "SUV에는 TOYOTA엔진 사용 불가",
    ),
    (
        CarSelection(car_type=TRUCK, engine=WIA, brake=CONTINENTAL, steering=BOSCH_S),
        "Truck에는 WIA엔진 사용 불가",
    ),
    (
        CarSelection(car_type=TRUCK, engine=GM, brake=MANDO, steering=BOSCH_S),
        "Truck에는 Mando제동장치 사용 불가",
    ),
    (
        CarSelection(car_type=SEDAN, engine=GM, brake=BOSCH_B, steering=MOBIS),
        "Bosch제동장치에는 Bosch조향장치 이외 사용 불가",
    ),
]

BROKEN_ENGINE_SELECTION = CarSelection(
    car_type=SEDAN, engine=4, brake=MANDO, steering=BOSCH_S
)


def test_run_success(capsys):
    run_produced_car(PASSING)
    captured = capsys.readouterr()
    assert captured.out == (
        "Car Type : Sedan\n"
        "Engine   : GM\n"
        "Brake    : Mando\n"
        "Steering : Bosch\n"
        "자동차가 동작됩니다.\n"
    )


def test_run_failure_for_each_rule(capsys):
    for selection, _ in RULE_VIOLATIONS:
        run_produced_car(selection)
        captured = capsys.readouterr()
        assert captured.out == "자동차가 동작되지 않습니다\n"


def test_run_broken_engine(capsys):
    run_produced_car(BROKEN_ENGINE_SELECTION)
    captured = capsys.readouterr()
    assert captured.out == "엔진이 고장나있습니다.\n자동차가 움직이지 않습니다.\n"


def test_test_pass(capsys):
    check_produced_car(PASSING)
    captured = capsys.readouterr()
    assert captured.out == "PASS\n"


def test_test_fail_for_each_rule(capsys):
    for selection, message in RULE_VIOLATIONS:
        check_produced_car(selection)
        captured = capsys.readouterr()
        assert captured.out == f"FAIL\n{message}\n"


def test_test_does_not_check_broken_engine(capsys):
    check_produced_car(BROKEN_ENGINE_SELECTION)
    captured = capsys.readouterr()
    assert captured.out == "PASS\n"
