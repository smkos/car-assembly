from car_assembly.options import BOSCH_S, GM, MANDO, SEDAN, SUV, TOYOTA
from car_assembly.rules import first_violated_rule
from car_assembly.state import CarSelection


def test_default_values_are_zero():
    selection = CarSelection()
    assert selection.car_type == 0
    assert selection.engine == 0
    assert selection.brake == 0
    assert selection.steering == 0


def test_fields_can_be_assigned():
    selection = CarSelection()
    selection.car_type = SEDAN
    selection.engine = GM
    selection.brake = MANDO
    selection.steering = BOSCH_S
    assert selection.car_type == SEDAN
    assert selection.engine == GM
    assert selection.brake == MANDO
    assert selection.steering == BOSCH_S


def test_passing_selection_no_violation():
    selection = CarSelection(car_type=SEDAN, engine=GM, brake=MANDO, steering=BOSCH_S)
    assert first_violated_rule(selection) is None


def test_violating_selection_matches_rule():
    selection = CarSelection(car_type=SUV, engine=TOYOTA, brake=MANDO, steering=BOSCH_S)
    violated = first_violated_rule(selection)
    assert violated is not None
    assert violated.fail_message == "SUV에는 TOYOTA엔진 사용 불가"
