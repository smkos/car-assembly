from car_assembly.options import BRAKES, CAR_TYPES, ENGINES, STEERINGS
from car_assembly.rules import first_violated_rule
from car_assembly.state import CarSelection

BROKEN_ENGINE = 4


def run_produced_car(selection: CarSelection) -> None:
    if first_violated_rule(selection) is not None:
        print("자동차가 동작되지 않습니다")
        return
    if selection.engine == BROKEN_ENGINE:
        print("엔진이 고장나있습니다.")
        print("자동차가 움직이지 않습니다.")
        return

    print(f"Car Type : {CAR_TYPES[selection.car_type].spec_label}")
    print(f"Engine   : {ENGINES[selection.engine].spec_label}")
    print(f"Brake    : {BRAKES[selection.brake].spec_label}")
    print(f"Steering : {STEERINGS[selection.steering].spec_label}")

    print("자동차가 동작됩니다.")


def test_produced_car(selection: CarSelection) -> None:
    violated = first_violated_rule(selection)
    if violated is None:
        print("PASS")
    else:
        print(f"FAIL\n{violated.fail_message}")
