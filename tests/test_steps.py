from car_assembly.options import BRAKES, CAR_TYPES, ENGINES, STEERINGS
from car_assembly.state import CarSelection
from car_assembly.steps import (
    STEP_BRAKE,
    STEP_CAR_TYPE,
    STEP_ENGINE,
    STEP_RUN_TEST,
    STEP_STEERING,
    STEPS,
    is_valid_range,
)


def test_steps_keys():
    assert set(STEPS.keys()) == {
        STEP_CAR_TYPE,
        STEP_ENGINE,
        STEP_BRAKE,
        STEP_STEERING,
        STEP_RUN_TEST,
    }
    assert (STEP_CAR_TYPE, STEP_ENGINE, STEP_BRAKE, STEP_STEERING, STEP_RUN_TEST) == (
        0,
        1,
        2,
        3,
        4,
    )


def test_menu_lines_car_type():
    assert STEPS[STEP_CAR_TYPE].menu_lines == [
        "        ______________",
        "       /|            |",
        "  ____/_|_____________|____",
        " |                      O  |",
        " '-(@)----------------(@)--'",
        "===============================",
        "어떤 차량 타입을 선택할까요?",
        "1. Sedan",
        "2. SUV",
        "3. Truck",
    ]


def test_menu_lines_engine():
    assert STEPS[STEP_ENGINE].menu_lines == [
        "어떤 엔진을 탑재할까요?",
        "0. 뒤로가기",
        "1. GM",
        "2. TOYOTA",
        "3. WIA",
        "4. 고장난 엔진",
    ]


def test_menu_lines_brake():
    assert STEPS[STEP_BRAKE].menu_lines == [
        "어떤 제동장치를 선택할까요?",
        "0. 뒤로가기",
        "1. MANDO",
        "2. CONTINENTAL",
        "3. BOSCH",
    ]


def test_menu_lines_steering():
    assert STEPS[STEP_STEERING].menu_lines == [
        "어떤 조향장치를 선택할까요?",
        "0. 뒤로가기",
        "1. BOSCH",
        "2. MOBIS",
    ]


def test_menu_lines_run_test():
    assert STEPS[STEP_RUN_TEST].menu_lines == [
        "멋진 차량이 완성되었습니다.",
        "0. 처음 화면으로 돌아가기",
        "1. RUN",
        "2. Test",
    ]


def test_options_field_mapping():
    assert STEPS[STEP_CAR_TYPE].options is CAR_TYPES
    assert STEPS[STEP_ENGINE].options is ENGINES
    assert STEPS[STEP_BRAKE].options is BRAKES
    assert STEPS[STEP_STEERING].options is STEERINGS
    assert STEPS[STEP_RUN_TEST].options is None


def test_apply_functions_set_correct_field():
    selection = CarSelection()

    STEPS[STEP_CAR_TYPE].apply(selection, 1)
    assert selection.car_type == 1

    STEPS[STEP_ENGINE].apply(selection, 2)
    assert selection.engine == 2

    STEPS[STEP_BRAKE].apply(selection, 3)
    assert selection.brake == 3

    STEPS[STEP_STEERING].apply(selection, 2)
    assert selection.steering == 2

    assert STEPS[STEP_RUN_TEST].apply is None


def test_range_check_step0_asymmetry():
    range_check = STEPS[STEP_CAR_TYPE].range_check
    assert range_check(0) is False
    assert range_check(1) is True
    assert range_check(2) is True
    assert range_check(3) is True
    assert range_check(4) is False


def test_range_check_step1_engine():
    range_check = STEPS[STEP_ENGINE].range_check
    assert range_check(-1) is False
    for ans in (0, 1, 2, 3, 4):
        assert range_check(ans) is True
    assert range_check(5) is False


def test_range_check_step2_brake():
    range_check = STEPS[STEP_BRAKE].range_check
    assert range_check(-1) is False
    for ans in (0, 1, 2, 3):
        assert range_check(ans) is True
    assert range_check(4) is False


def test_range_check_step3_steering():
    range_check = STEPS[STEP_STEERING].range_check
    assert range_check(-1) is False
    for ans in (0, 1, 2):
        assert range_check(ans) is True
    assert range_check(3) is False


def test_range_check_step4_run_test():
    range_check = STEPS[STEP_RUN_TEST].range_check
    assert range_check(-1) is False
    for ans in (0, 1, 2):
        assert range_check(ans) is True
    assert range_check(3) is False


def test_is_valid_range_prints_error_and_returns_false(capsys):
    assert is_valid_range(STEP_CAR_TYPE, 0) is False
    captured = capsys.readouterr()
    assert captured.out == "ERROR :: 차량 타입은 1 ~ 3 범위만 선택 가능\n"

    assert is_valid_range(STEP_ENGINE, 5) is False
    captured = capsys.readouterr()
    assert captured.out == "ERROR :: 엔진은 1 ~ 4 범위만 선택 가능\n"

    assert is_valid_range(STEP_BRAKE, 4) is False
    captured = capsys.readouterr()
    assert captured.out == "ERROR :: 제동장치는 1 ~ 3 범위만 선택 가능\n"

    assert is_valid_range(STEP_STEERING, 3) is False
    captured = capsys.readouterr()
    assert captured.out == "ERROR :: 조향장치는 1 ~ 2 범위만 선택 가능\n"

    assert is_valid_range(STEP_RUN_TEST, 3) is False
    captured = capsys.readouterr()
    assert captured.out == "ERROR :: Run 또는 Test 중 하나를 선택 필요\n"


def test_is_valid_range_prints_nothing_when_valid(capsys):
    assert is_valid_range(STEP_CAR_TYPE, 1) is True
    captured = capsys.readouterr()
    assert captured.out == ""
