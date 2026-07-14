from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from car_assembly.options import BRAKES, CAR_TYPES, ENGINES, STEERINGS, Option
from car_assembly.state import CarSelection

STEP_CAR_TYPE = 0
STEP_ENGINE = 1
STEP_BRAKE = 2
STEP_STEERING = 3
STEP_RUN_TEST = 4

ANSWER_BACK = 0  # 모든 스텝 공통: "뒤로가기" / "처음 화면으로 돌아가기"
RUN_TEST_CHOICE_RUN = 1  # step 4 전용: "RUN" 선택
RUN_TEST_CHOICE_TEST = 2  # step 4 전용: "Test" 선택


@dataclass(frozen=True)
class StepDef:
    menu_lines: List[str]
    range_check: Callable[[int], bool]
    range_error: str
    options: Optional[Dict[int, Option]]
    apply: Optional[Callable[[CarSelection, int], None]]


def _set_car_type(selection: CarSelection, ans: int) -> None:
    selection.car_type = ans


def _set_engine(selection: CarSelection, ans: int) -> None:
    selection.engine = ans


def _set_brake(selection: CarSelection, ans: int) -> None:
    selection.brake = ans


def _set_steering(selection: CarSelection, ans: int) -> None:
    selection.steering = ans


STEPS: Dict[int, StepDef] = {
    STEP_CAR_TYPE: StepDef(
        menu_lines=[
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
        ],
        range_check=lambda ans: 1 <= ans <= 3,
        range_error="ERROR :: 차량 타입은 1 ~ 3 범위만 선택 가능",
        options=CAR_TYPES,
        apply=_set_car_type,
    ),
    STEP_ENGINE: StepDef(
        menu_lines=[
            "어떤 엔진을 탑재할까요?",
            "0. 뒤로가기",
            "1. GM",
            "2. TOYOTA",
            "3. WIA",
            "4. 고장난 엔진",
        ],
        range_check=lambda ans: 0 <= ans <= 4,
        range_error="ERROR :: 엔진은 1 ~ 4 범위만 선택 가능",
        options=ENGINES,
        apply=_set_engine,
    ),
    STEP_BRAKE: StepDef(
        menu_lines=[
            "어떤 제동장치를 선택할까요?",
            "0. 뒤로가기",
            "1. MANDO",
            "2. CONTINENTAL",
            "3. BOSCH",
        ],
        range_check=lambda ans: 0 <= ans <= 3,
        range_error="ERROR :: 제동장치는 1 ~ 3 범위만 선택 가능",
        options=BRAKES,
        apply=_set_brake,
    ),
    STEP_STEERING: StepDef(
        menu_lines=[
            "어떤 조향장치를 선택할까요?",
            "0. 뒤로가기",
            "1. BOSCH",
            "2. MOBIS",
        ],
        range_check=lambda ans: 0 <= ans <= 2,
        range_error="ERROR :: 조향장치는 1 ~ 2 범위만 선택 가능",
        options=STEERINGS,
        apply=_set_steering,
    ),
    STEP_RUN_TEST: StepDef(
        menu_lines=[
            "멋진 차량이 완성되었습니다.",
            "0. 처음 화면으로 돌아가기",
            "1. RUN",
            "2. Test",
        ],
        range_check=lambda ans: 0 <= ans <= 2,
        range_error="ERROR :: Run 또는 Test 중 하나를 선택 필요",
        options=None,
        apply=None,
    ),
}


def is_valid_range(step: int, ans: int) -> bool:
    step_def = STEPS[step]
    if not step_def.range_check(ans):
        print(step_def.range_error)
        return False
    return True
