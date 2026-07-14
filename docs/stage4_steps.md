# Stage 4 설계: `car_assembly/steps.py`

## 목적

`assembly.py`의 `show_menu()`, `is_valid_range()`, 그리고 `select_car_type/engine/brake/steering` 호출 디스패치에 반복되는 스텝별 if/elif 체인을 하나의 데이터 테이블(`STEPS`)로 일반화합니다.

## 설계 변경 사항 (이전 PLAN.md 대비 보완)

`PLAN.md`/`CLAUDE.md`에는 `cli.py`가 `delay`/`clear`/`main()`을 담당한다고 되어 있는데, 원본 `show_menu()`는 매번 `clear()`를 호출합니다. `steps.py`가 화면을 지우는 `show_menu` 함수까지 가지면 `cli.py`(`clear` 보유)와 `steps.py` 사이에 순환 임포트가 생깁니다(`cli`는 `STEPS`를 쓰려고 `steps`를 임포트하고, `steps`는 `clear()`를 쓰려고 `cli`를 임포트).

이를 피하기 위해 **`steps.py`는 화면 출력 부수효과(`clear()`, 화면 지우기 후 `print`)를 직접 하지 않고, 스텝별 메뉴 텍스트/범위 검증 규칙/옵션/적용 함수를 담은 순수 데이터·함수만 제공**합니다. 실제로 `clear()`를 호출하고 `STEPS[step].menu_lines`를 출력하는 `show_menu(step)` 함수는 Stage 6의 `cli.py`에 둡니다. (`is_valid_range`는 `print`만 하고 `clear()`는 쓰지 않으므로 `steps.py`에 그대로 둬도 순환 임포트가 생기지 않습니다.)

## 원본에서 되살리는 죽은 상수

`assembly.py` 상단의 `CarType_Q = 0`, `Engine_Q = 1`, `brakeSystem_Q = 2`, `SteeringSystem_Q = 3`, `Run_Test = 4`는 정의만 되고 실제로는 어디서도 쓰이지 않는(전부 리터럴 정수로 비교) 죽은 코드입니다. 값은 그대로 유지하되, `steps.py`에서 의미 있는 이름으로 되살려 `STEPS` 테이블의 키로 사용합니다 (가독성 목표에 부합, 동작에는 영향 없음).

```python
STEP_CAR_TYPE = 0
STEP_ENGINE = 1
STEP_BRAKE = 2
STEP_STEERING = 3
STEP_RUN_TEST = 4
```

## `StepDef` 설계

```python
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from car_assembly.options import Option, CAR_TYPES, ENGINES, BRAKES, STEERINGS
from car_assembly.state import CarSelection


@dataclass(frozen=True)
class StepDef:
    menu_lines: List[str]                 # clear() 이후, 공통 하단 구분선 이전에 출력할 줄들
    range_check: Callable[[int], bool]    # True면 유효한 입력
    range_error: str                       # range_check 실패 시 출력할 에러 메시지
    options: Optional[Dict[int, Option]]   # step 4는 None (RUN/Test는 옵션 선택이 아님)
    apply: Optional[Callable[[CarSelection, int], None]]  # step 4는 None
```

## `STEPS` 테이블 (원본 `show_menu`/`is_valid_range` 문구를 그대로 복사)

각 스텝의 `menu_lines`는 원본 if/elif 분기에서 **그 스텝 자신이 출력하는 줄만** 포함합니다 (분기 이후 공통으로 출력되는 마지막 `"==============================="`는 Stage 6의 `show_menu()`가 별도로 붙입니다). 단, step 0은 원본 코드상 ASCII 아트와 질문 사이에 자체적으로 `"==============================="`를 한 번 출력하므로, 이 줄은 step 0의 `menu_lines`에 포함합니다 (원본을 그대로 복사한 것이며 새로 추가한 것이 아닙니다).

```python
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
```

**주의 (원본 비대칭 보존)**: step 0만 `1 <= ans <= 3`(0을 허용하지 않음)이고, step 1~4는 모두 `0`을 포함하는 범위입니다. 하나의 공통 공식으로 만들지 않고 각 스텝의 `range_check`에 원본 조건 그대로를 반영했습니다.

## `is_valid_range` — steps.py에 남는 함수

```python
def is_valid_range(step: int, ans: int) -> bool:
    step_def = STEPS[step]
    if not step_def.range_check(ans):
        print(step_def.range_error)
        return False
    return True
```

원본과 동일하게 실패 시 에러 메시지를 출력하고 `False`를 반환, 성공 시 아무것도 출력하지 않고 `True`를 반환합니다. (`clear()` 호출이 없으므로 `cli.py`를 임포트할 필요가 없습니다.)

## 이 스테이지에서 하지 않는 것

- 화면을 지우고 메뉴를 출력하는 `show_menu(step)` 함수 자체 (Stage 6, `cli.py`)
- RUN/Test 처리, 선택 디스패치를 실제 `main()` 루프에 배선하는 것 (Stage 6)

## `tests/test_steps.py` 설계

1. `STEPS`의 키가 `{0,1,2,3,4}`(또는 `STEP_*` 상수 5개)와 일치하는지.
2. 각 스텝의 `menu_lines`가 원본 `assembly.py`의 해당 if/elif 분기 출력과 줄 단위로 정확히 일치하는지 (step 0은 ASCII 아트 + 임베디드 구분선 포함 10줄, step 1~4는 각각의 줄 수 확인).
3. **범위 검증 경계값** (원본 `is_valid_range`의 비대칭 유지 확인):
   - step 0: `0`→무효, `1,2,3`→유효, `4`→무효
   - step 1: `-1`→무효, `0,1,2,3,4`→유효, `5`→무효
   - step 2: `-1`→무효, `0,1,2,3`→유효, `4`→무효
   - step 3: `-1`→무효, `0,1,2`→유효, `3`→무효
   - step 4: `-1`→무효, `0,1,2`→유효, `3`→무효
4. `is_valid_range()`가 무효 입력 시 `capsys`로 캡처한 출력이 각 스텝의 정확한 에러 메시지와 일치하고 `False`를 반환하는지, 유효 입력 시 아무 출력 없이 `True`를 반환하는지.
5. `options` 필드가 step 0~3에서 각각 `CAR_TYPES`/`ENGINES`/`BRAKES`/`STEERINGS`와 동일한 객체인지(`is`), step 4는 `None`인지.
6. `apply` 함수 호출 시 `CarSelection`의 올바른 필드가 갱신되는지 (`_set_car_type`, `_set_engine`, `_set_brake`, `_set_steering` 각각), step 4의 `apply`는 `None`인지.

## 검증 방법

```
pytest tests/test_steps.py -v
```

모두 통과하면 Stage 4 완료로 간주하고 Stage 5(`production.py`)로 진행합니다.
