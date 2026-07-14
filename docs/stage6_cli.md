# Stage 6 설계: `car_assembly/cli.py` + `main.py` + `tests/test_cli.py` (통합/회귀 테스트)

## 목적

지금까지 만든 `options.py`/`rules.py`/`state.py`/`steps.py`/`production.py`를 실제로 배선해 원본 `assembly.py`의 `main()` 루프와 동일하게 동작하는 CLI를 완성합니다. 그리고 legacy `assembly.py`와 새 CLI(`main.py`)를 **동일한 입력 시퀀스로 실행해 표준출력을 바이트 단위로 비교**하는 자동화된 회귀 테스트(`test_cli.py`)로 "동작 보존"을 검증합니다. 이 스테이지가 끝나면 리팩토링의 마지막 로직 스테이지가 완료됩니다.

## 매직 넘버(`ans == 0/1/2`)에 이름 부여

`main()`에서 사용자가 입력한 `ans`가 `0`, `1`, `2`일 때의 의미가 스텝마다 다릅니다.

- `ans == 0`은 **모든 스텝에서 공통으로 "뒤로가기"**를 의미합니다 (원본 메뉴 문구 "0. 뒤로가기" / "0. 처음 화면으로 돌아가기").
- step 4(RUN/Test 화면)에서만 `ans == 1`은 "RUN 실행", `ans == 2`는 "Test 실행"을 의미합니다.

이 값들을 `steps.py`에 `STEP_CAR_TYPE` 등과 함께 이름 있는 상수로 정의해 매직 넘버를 없앱니다 (값 자체는 원본과 동일하게 유지, 이름만 부여).

```python
# car_assembly/steps.py에 추가
ANSWER_BACK = 0          # 모든 스텝 공통: "뒤로가기" / "처음 화면으로 돌아가기"
RUN_TEST_CHOICE_RUN = 1  # step 4 전용: "RUN" 선택
RUN_TEST_CHOICE_TEST = 2  # step 4 전용: "Test" 선택
```

`ANSWER_BACK`은 스텝에 관계없이 재사용되므로 이름 그대로 범용 상수로 두고, `RUN_TEST_CHOICE_RUN`/`RUN_TEST_CHOICE_TEST`는 step 4에서만 의미를 가지므로 이름에 그 맥락을 담았습니다. (참고로 step 0~3의 옵션 선택 시 쓰이는 `ans` 값 1~4는 이미 Stage 1의 `Option.value`/`CAR_TYPES`/`ENGINES`/... 딕셔너리 키로 의미가 부여되어 있어 별도 상수가 필요 없습니다 — 매직 넘버가 남아있던 곳은 오직 이 "뒤로가기/RUN/Test" 세 값이었습니다.)

## `cli.py` 설계

```python
import os
import sys
import time

from car_assembly.production import run_produced_car, test_produced_car
from car_assembly.state import CarSelection
from car_assembly.steps import (
    ANSWER_BACK,
    RUN_TEST_CHOICE_RUN,
    RUN_TEST_CHOICE_TEST,
    STEP_CAR_TYPE,
    STEP_RUN_TEST,
    STEPS,
    is_valid_range,
)

CLEAR_SCREEN = "\033[H\033[2J"


def delay(ms: int) -> None:
    if os.environ.get("CAR_ASSEMBLY_FAST_TEST"):
        return
    time.sleep(ms / 1000.0)


def clear() -> None:
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()


def show_menu(step: int) -> None:
    clear()
    for line in STEPS[step].menu_lines:
        print(line)
    print("===============================")


def main() -> None:
    selection = CarSelection()
    step = STEP_CAR_TYPE
    while True:
        show_menu(step)
        buf = input("INPUT > ").strip()

        if buf == "exit":
            print("바이바이")
            break

        try:
            ans = int(buf)
        except:
            print("ERROR :: 숫자만 입력 가능")
            delay(800)
            continue

        if not is_valid_range(step, ans):
            delay(800)
            continue

        if ans == ANSWER_BACK:
            if step == STEP_RUN_TEST:
                step = STEP_CAR_TYPE
            elif step > STEP_CAR_TYPE:
                step -= 1
            continue

        step_def = STEPS[step]
        if step_def.options is not None:
            option = step_def.options[ans]
            print(option.select_message)
            step_def.apply(selection, ans)
            delay(800)
            step += 1
        else:
            if ans == RUN_TEST_CHOICE_RUN:
                run_produced_car(selection)
                delay(2000)
            elif ans == RUN_TEST_CHOICE_TEST:
                print("Test...")
                delay(1500)
                test_produced_car(selection)
                delay(2000)
```

### 설계 근거

- **`delay()`의 `CAR_ASSEMBLY_FAST_TEST` 분기**: `PLAN.md`에는 원래 "테스트에서 `monkeypatch`로 무력화"라고 되어 있었지만, `test_cli.py`는 `subprocess`로 **별도 프로세스**를 띄워 legacy/새 CLI를 실행하므로 `monkeypatch`가 프로세스 경계를 넘지 못합니다. 대신 환경 변수 `CAR_ASSEMBLY_FAST_TEST`가 설정된 경우에만 `time.sleep`을 건너뛰도록 했습니다. 이 변수가 없으면(일반 실행) 원본과 동일하게 실제로 대기하므로 **정상 실행 동작에는 전혀 영향이 없습니다**. `PLAN.md`/`CLAUDE.md`는 이 세부사항을 반영해 갱신할 예정입니다.
- **`except:` (bare except)**: 원본이 `try: ans = int(buf) except: ...`로 모든 예외를 잡습니다. `int(buf)`가 실제로 던질 수 있는 예외는 `ValueError`뿐이라 `except ValueError`로 좁혀도 관찰 가능한 동작은 동일하지만, "동작 보존"을 엄격히 지키기 위해 원본 그대로 bare `except:`를 유지합니다.
- **선택 디스패치**: `step_def.options is not None`인 스텝(0~3)은 옵션 조회 → 선택 메시지 출력 → `apply()`로 `CarSelection` 갱신 → `delay(800)` → 다음 스텝으로, 모두 동일한 패턴이므로 테이블 조회 하나로 처리합니다. `step_def.options is None`인 스텝(4, RUN/Test)만 원본처럼 명시적 `if ans==1 / elif ans==2` 분기를 유지합니다 (RUN/Test는 "필드 설정"이 아닌 별도 동작이라 테이블에 억지로 넣지 않기로 한 Stage 4 결정과 일관).
- **뒤로가기(`ans==ANSWER_BACK`)**: 원본과 동일하게 `delay()` 호출 없이 즉시 `continue`합니다. `step==STEP_RUN_TEST`(4)면 `STEP_CAR_TYPE`(0)으로, 그 외에는 한 단계 감소. `CarSelection`은 건드리지 않으므로 원본의 "뒤로가기 시 선택값 미초기화" 동작이 그대로 보존됩니다(Stage 3에서 설계한 대로).

## `main.py` (루트, 새 진입점)

```python
from car_assembly.cli import main

if __name__ == "__main__":
    main()
```

## `tests/test_cli.py` — legacy vs 신규 CLI 골든(회귀) 테스트

### 실행 방식

`subprocess`로 두 프로그램을 각각 실행하고 표준출력을 비교합니다. 둘 다 저장소 루트에서 스크립트로 실행되므로(`python assembly.py`, `python main.py`) 별도 `PYTHONPATH` 설정 없이 `car_assembly` 패키지를 정상적으로 임포트합니다(스크립트 실행 시 해당 디렉터리가 `sys.path[0]`이 되므로).

```python
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _run(script: str, input_text: str, fast: bool) -> str:
    env = dict(os.environ)
    if fast:
        env["CAR_ASSEMBLY_FAST_TEST"] = "1"
    result = subprocess.run(
        [sys.executable, script],
        input=input_text,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
        timeout=30,
    )
    return result.stdout


def assert_same_output(input_text: str) -> None:
    legacy_output = _run("assembly.py", input_text, fast=False)
    refactored_output = _run("main.py", input_text, fast=True)
    assert refactored_output == legacy_output
```

- legacy(`assembly.py`)는 `fast=False`로 실행해 실제 `time.sleep`이 걸리지만(원본이 수정되지 않았으므로 당연함), 새 CLI(`main.py`)는 `CAR_ASSEMBLY_FAST_TEST=1`로 지연을 건너뛰어 테스트 전체 실행 시간을 줄입니다. **비교 대상은 표준출력 내용이지 실행 시간이 아니므로**, 이 비대칭이 검증의 정확성에 영향을 주지 않습니다.
- `timeout=30`은 안전장치입니다(입력 시퀀스가 잘못 구성되어 `input()`이 무한 대기하는 경우를 방지). 시나리오별 legacy 실행은 대략 0.8~수 초의 실제 지연이 누적되므로, **`test_cli.py` 전체 실행에는 legacy 지연 누적으로 인해 약 1~2분 정도 소요될 것으로 예상**합니다(다른 테스트 파일들은 밀리초 단위). 반복 개발 중에는 `pytest tests/test_cli.py -k <키워드>`로 필요한 시나리오만 선택 실행하고, 전체 실행은 Stage 완료 확인 시점에 한 번 수행하는 것을 권장합니다.

### 검증 시나리오 (입력 시퀀스는 `\n`으로 구분, 항상 `exit`로 종료)

Stage 2/5에서 사용한 것과 동일한 조합(`SEDAN=1,GM=1,MANDO=1,BOSCH_S=1` 베이스라인, 5개 규칙 위반 조합)을 재사용해 일관성을 유지합니다.

| 시나리오 | 입력 시퀀스 |
|---|---|
| RUN 성공 | `1,1,1,1,1,exit` |
| RUN 실패 — 규칙1 (Sedan+Continental) | `1,1,2,1,1,exit` |
| RUN 실패 — 규칙2 (SUV+TOYOTA) | `2,2,1,1,1,exit` |
| RUN 실패 — 규칙3 (Truck+WIA) | `3,3,2,1,1,exit` |
| RUN 실패 — 규칙4 (Truck+Mando) | `3,1,1,1,1,exit` |
| RUN 실패 — 규칙5 (Bosch브레이크+비Bosch조향) | `1,1,3,2,1,exit` |
| RUN 엔진 고장 | `1,4,1,1,1,exit` |
| Test PASS | `1,1,1,1,2,exit` |
| Test FAIL — 규칙1~5 | 위 RUN 실패와 동일 조합, 마지막을 `2`로 |
| Test는 엔진 고장 무시 (PASS) | `1,4,1,1,2,exit` |
| 잘못된 입력 (숫자 아님) 후 정상 종료 | `abc,exit` |
| 잘못된 입력 (범위 초과, 5개 스텝 전부) 후 RUN | `9,1,5,1,4,1,3,1,3,1,1,exit` (각 스텝에서 무효값→에러→유효값 순으로 진행, step4는 마지막 `1`이 RUN) |
| 뒤로가기 (한 단계) | `1,1,0,2,1,1,1,exit` (엔진을 GM 선택 후 뒤로가서 TOYOTA로 변경, 이후 정상 진행해 RUN) |
| step4에서 처음으로 되돌아가기 | `1,1,1,1,0,1,1,1,1,1,exit` (완료 화면에서 0으로 첫 화면으로 돌아간 뒤 다시 처음부터 진행해 RUN) |
| 시작하자마자 종료 | `exit` |

각 시나리오를 `pytest.mark.parametrize`로 등록하고 `assert_same_output(input_text)`를 호출합니다.

## 이 스테이지에서 하지 않는 것

- `assembly.py` 수정 (계속 미변경 유지)
- README.md 등 기타 문서 변경

## 검증 방법

```
pytest tests/test_cli.py -v            # 전체 (수 분 소요 가능)
pytest tests/test_cli.py -k rule1 -v   # 특정 시나리오만
pytest                                  # 전체 스위트 (단위 테스트는 여전히 즉시 완료)
```

모두 통과하면 Stage 6 완료 — `car_assembly/` 패키지가 `assembly.py`와 동일하게 동작함이 자동화된 방식으로 확인된 것입니다. 이후 `PLAN.md`/`CLAUDE.md`의 `cli.py`/`delay()` 관련 서술(monkeypatch → 환경 변수 방식)을 갱신합니다.
