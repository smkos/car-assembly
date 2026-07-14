# assembly.py 클린 코드 리팩토링 계획

## Context

`Car_Assembly_KATA`는 레거시 코드를 클린 코드로 리팩토링하는 연습 저장소입니다. 현재 `assembly.py`(261줄, 유일한 소스 파일)는 전역 변수(`q0`~`q3`), 매직 넘버, 그리고 반복된 `if/elif` 체인으로 작성되어 있습니다. 특히 호환성 규칙(5가지 조합 금지 규칙)이 `is_valid_check()`와 `test_produced_car()`에 동일하게 두 번 구현되어 있고, 부품 선택/메뉴 출력/RUN 스펙 출력도 각각 유사한 if/elif 체인을 반복합니다. CLAUDE.md에 명시된 프로젝트 목표(중복 제거, 가독성, 확장성, 동작 보존)를 달성하기 위해, **사용자에게 보이는 모든 출력(메뉴 텍스트, 에러 메시지, RUN/Test 결과, 지연 시간)을 한 글자도 바꾸지 않으면서** 내부 구조만 개선합니다.

이번 계획에서는 다음 두 가지를 추가로 반영합니다.
- **`assembly.py`는 레거시 코드 보존용으로 그대로 남겨두고, 리팩토링 결과는 새 파일/패키지로 작성**합니다 (기존 파일 수정 없음, 새 파일 추가만).
- **테스트 프레임워크로 `pytest`를 사용**하고, 가상환경(`.venv`)에 패키지로 설치하여 자동화된 테스트를 작성합니다.

## 새 패키지 구조

기존 `assembly.py`는 손대지 않고, 아래와 같이 새 패키지 `car_assembly/`를 만들어 리팩토링된 코드를 넣습니다. 확장성(새 차량 타입/부품/규칙 추가 용이성)을 위해 책임별로 파일을 분리합니다.

```
car_assembly/
    __init__.py
    options.py       # Option dataclass + CAR_TYPES/ENGINES/BRAKES/STEERINGS + 관련 상수
    rules.py          # CompatibilityRule dataclass + COMPATIBILITY_RULES + first_violated_rule
    state.py          # CarSelection dataclass (기존 q0~q3 전역 상태 대체)
    steps.py          # StepDef dataclass + STEPS 테이블 + show_menu/is_valid_range 대체 함수
    production.py     # run_produced_car / test_produced_car
    cli.py            # delay/clear + main() 루프

main.py               # 새 진입점: `python main.py` → car_assembly.cli.main() 호출

tests/
    test_options.py
    test_rules.py
    test_state.py
    test_steps.py
    test_production.py
    test_cli.py        # subprocess로 legacy assembly.py 출력과 새 CLI 출력을 비교하는 골든 테스트

requirements-dev.txt    # pytest
```

- `assembly.py`, `README.md`는 변경하지 않습니다. `CLAUDE.md`에는 "레거시 코드는 `assembly.py`에 그대로 유지되며, 리팩토링된 클린 코드는 `car_assembly/` 패키지에 있다"는 안내를 추가합니다.
- 패키지 분리는 각 관심사(옵션 데이터, 규칙, 상태, 스텝 정의, 실행/테스트 로직, CLI 진입점)를 독립적으로 확장·테스트할 수 있게 하기 위함입니다. 예: 새 차량 타입 추가 시 `options.py`만, 새 호환성 규칙 추가 시 `rules.py`만 수정하면 됩니다.

## 설계 개요 (각 모듈 내용)

### 1. `options.py` — 데이터 기반 옵션 정의

```python
@dataclass(frozen=True)
class Option:
    value: int
    select_message: str   # 선택 시 출력 문구 (예: "차량 타입으로 Sedan을 선택하셨습니다.")
    spec_label: str | None # RUN 스펙 출력에 쓰이는 라벨 (예: "Sedan"). 엔진 4(고장)는 None
```

`CAR_TYPES`, `ENGINES`, `BRAKES`, `STEERINGS` 네 개의 `dict[int, Option]`을 정의하며, 키는 기존 `q0`~`q3` 값과 동일하게 유지합니다. `SEDAN/SUV/TRUCK`, `GM/TOYOTA/WIA`, `MANDO/CONTINENTAL/BOSCH_B`, `BOSCH_S/MOBIS` 상수도 이 파일에 둡니다.

**주의**: `select_message`와 `spec_label`은 원본에서 대소문자/표기가 서로 다릅니다 (예: 조향장치 선택 문구는 "BOSCH 조향장치를 선택하셨습니다."이지만 RUN 스펙은 "Steering : Bosch"). 하나에서 다른 하나를 문자열 변환(`.title()` 등)으로 유도하지 말고, 원본 문자열 그대로 각각 리터럴로 저장합니다.

### 2. `rules.py` — 호환성 규칙 단일화

```python
@dataclass(frozen=True)
class CompatibilityRule:
    is_violated: Callable[["CarSelection"], bool]
    fail_message: str  # "FAIL\n" 뒤에 오는 텍스트

COMPATIBILITY_RULES: list[CompatibilityRule] = [ ... 5개 규칙 ... ]

def first_violated_rule(selection) -> CompatibilityRule | None:
    return next((r for r in COMPATIBILITY_RULES if r.is_violated(selection)), None)
```

`is_valid_check` 역할은 `first_violated_rule(selection) is None`으로, `test_produced_car`의 FAIL 메시지 출력은 첫 번째 위반 규칙의 메시지를 사용하는 방식으로 통일합니다. 원본이 `if/elif`로 **첫 번째 매칭 규칙만** 출력하므로 `next(...)`로 동일한 first-match 동작을 유지합니다.

### 3. `state.py` — 전역 상태 캡슐화

```python
@dataclass
class CarSelection:
    car_type: int = 0
    engine: int = 0
    brake: int = 0
    steering: int = 0
```

원본의 `q0`~`q3` 전역 변수와 `global` 선언을 대체합니다. `main()`에서 생성한 인스턴스를 각 함수에 매개변수로 전달합니다. 사용되지 않는 `q4`는 새 코드에 아예 포함하지 않습니다.

**주의**: 원본은 step 4 화면에서 "0. 처음 화면으로 돌아가기"를 선택해도 선택값을 초기화하지 않습니다. 이 동작(선택값이 유지되는 것)을 그대로 보존합니다.

### 4. `steps.py` — 스텝 머신 테이블화

```python
@dataclass(frozen=True)
class StepDef:
    menu_lines: list[str]
    range_check: Callable[[int], bool]
    range_error: str
    options: dict[int, Option] | None   # step 4는 None
    apply: Callable[[CarSelection, int], None] | None
```

`is_valid_range`, `select_*`의 반복된 if/elif를 `STEPS: dict[int, StepDef]` 조회로 대체합니다.

**주의**: step 0은 0(뒤로가기)을 허용하지 않고 `1~3`만 유효하지만, step 1~4는 `0`을 포함한 범위를 허용하는 비대칭이 원본에 있습니다. 하나의 공통 공식으로 일반화하지 말고 각 `StepDef`의 `range_check`에 그대로 반영합니다. step 4(RUN/Test)는 필드 설정이 아니라 별도 동작이므로 테이블에 억지로 넣지 않고 `cli.py`의 `main()`에서 명시적 분기로 유지합니다.

**설계 보완 (Stage 4 진행 중 확정)**: 원본 `show_menu()`는 매번 `clear()`를 호출하는데, `clear()`는 `cli.py`가 갖고 있습니다. `steps.py`가 화면을 지우는 `show_menu` 함수까지 가지면 `cli.py`(STEPS 사용)와 `steps.py`(clear 사용) 사이에 순환 임포트가 생깁니다. 따라서 **`steps.py`는 `StepDef`/`STEPS`와, `clear()` 없이 `print`만 하는 `is_valid_range(step, ans)`까지만 담당**하고, 실제로 `clear()`를 호출해 메뉴를 출력하는 `show_menu(step)` 함수는 Stage 6의 `cli.py`로 옮깁니다. 또한 원본 상단에 정의만 되고 실제로는 쓰이지 않던 죽은 상수 `CarType_Q`/`Engine_Q`/`brakeSystem_Q`/`SteeringSystem_Q`/`Run_Test`(값은 0~4로 `step`과 동일)를 `steps.py`에서 `STEP_CAR_TYPE`/`STEP_ENGINE`/`STEP_BRAKE`/`STEP_STEERING`/`STEP_RUN_TEST`로 되살려 `STEPS`의 키로 사용합니다 (값 동일, 가독성 개선 목적, 동작 영향 없음).

### 5. `production.py` — RUN / Test

`run_produced_car(selection)`은 호환성 검사 실패 시 실패 메시지, 엔진 고장(4) 시 고장 메시지, 그 외에는 `Option.spec_label` 조회로 스펙을 출력합니다 (필드 패딩 `"Car Type : "`, `"Engine   : "` 등은 원본 그대로 복사). `test_produced_car(selection)`은 `first_violated_rule` 결과에 따라 PASS/FAIL을 출력합니다.

### 6. `cli.py` — 진입점

`delay`, `clear`, `show_menu(step)`(clear 후 `STEPS[step].menu_lines` + 공통 하단 구분선 출력), `main()` 루프를 담당합니다. 원본 `main()`과 동일한 흐름(스텝 진행/뒤로가기/exit/RUN/Test 분기)을 유지하되, 전역 변수 대신 `CarSelection` 인스턴스와 `STEPS` 테이블을 사용합니다.

`main.py`(루트)는 다음과 같이 얇은 진입점 역할만 합니다.
```python
from car_assembly.cli import main

if __name__ == "__main__":
    main()
```

## pytest 도입

- `.venv`에 `pip install pytest`로 설치하고, 재현 가능하도록 `requirements-dev.txt`에 `pytest`를 기록합니다.
- 실행 명령: 전체 테스트 `pytest`, 특정 파일 `pytest tests/test_rules.py`, 특정 테스트 함수 `pytest tests/test_rules.py::test_sedan_continental_violation -v`.
- 단위 테스트: `rules.py`(5개 규칙 + 정상 케이스), `state.py`(CarSelection 기본값), `steps.py`(range_check 경계값, 특히 step 0의 비대칭 범위), `production.py`(RUN 성공/실패/엔진고장, Test PASS/FAIL 5종) 등을 각각 순수 함수 단위로 검증합니다 (input()/시간지연 없이 테스트 가능).
- 통합/회귀 테스트(`test_cli.py`): `subprocess.run([sys.executable, "assembly.py"], input=..., capture_output=True)`로 **레거시** 코드를 실행한 출력과, 동일 입력을 새 `main.py`(`car_assembly.cli.main`)에 넣은 출력을 비교하여 **바이트 단위로 동일**한지 자동 검증합니다. 이렇게 하면 "동작 보존"을 사람이 매번 수동으로 diff하지 않고 CI/로컬에서 반복 검증할 수 있습니다. (단, `delay()`로 인한 실제 대기 시간 때문에 테스트가 느려질 수 있으므로, 새 코드의 `cli.py`에서 `delay` 함수를 모듈 레벨로 분리해 두었습니다 — `test_cli.py`는 `subprocess`로 legacy/신규 CLI를 **별도 프로세스**로 실행하므로 `monkeypatch`가 프로세스 경계를 넘지 못해, 대신 환경 변수 `CAR_ASSEMBLY_FAST_TEST`가 설정된 경우에만 `time.sleep`을 건너뛰도록 구현했습니다. 이 변수가 없는 일반 실행에서는 원본과 동일하게 실제로 대기하므로 동작에는 영향이 없습니다. legacy `assembly.py`는 수정할 수 없으므로 항상 실제 지연이 걸리며, 이 때문에 `test_cli.py` 전체 실행에는 약 1~2분이 소요됩니다.)

## 단계별 실행 순서 (각 단계마다 pytest 실행으로 검증 후 다음 단계 진행)

1. **Stage 0 — 개발 환경 준비**: `requirements-dev.txt` 작성, `.venv`에 `pytest` 설치, `tests/` 디렉터리 생성.
2. **Stage 1 — `options.py` + 테스트**: `Option`/4개 dict 작성, `test_options.py`로 각 옵션의 `select_message`/`spec_label` 문자열이 원본과 정확히 일치하는지 검증.
3. **Stage 2 — `rules.py` + 테스트**: `CompatibilityRule`/`first_violated_rule` 작성, `test_rules.py`로 5개 규칙 각각의 위반/통과 케이스와 first-match 순서를 검증.
4. **Stage 3 — `state.py` + 테스트**: `CarSelection` 작성, `test_state.py`로 기본값/필드 검증.
5. **Stage 4 — `steps.py` + 테스트**: `StepDef`/`STEPS`/`is_valid_range` 작성 (`show_menu`는 Stage 6 `cli.py`로 이동), `test_steps.py`로 각 스텝의 메뉴 텍스트(줄 단위)·범위 검증(특히 step 0 비대칭)·에러 메시지가 원본과 일치하는지 검증.
6. **Stage 5 — `production.py` + 테스트**: `run_produced_car`/`test_produced_car` 작성, `test_production.py`로 RUN 성공/5개 실패/엔진고장, Test PASS/5개 FAIL을 검증 (stdout 캡처는 `capsys` 사용).
7. **Stage 6 — `cli.py` + `main.py` + 통합 테스트 (완료)**: 전체 루프 작성, `test_cli.py`에서 legacy `assembly.py`와 새 CLI를 19개 입력 시퀀스로 실행해 출력이 바이트 단위로 동일한지 자동 검증 (RUN 성공/5개 실패/엔진고장, Test PASS/5개 FAIL/엔진고장 무시, 잘못된 입력 2종, 뒤로가기 2종, 즉시 종료) — 전체 통과 확인(약 112초 소요, legacy의 실제 지연 때문).
8. **Stage 7 — 문서 반영 (완료)**: `CLAUDE.md`에 새 패키지 구조("Legacy vs Refactored 관계" 섹션: `car_assembly/`의 각 모듈 책임, `main.py` 진입점)와 pytest 실행 방법(설치, 전체/파일별/함수별 실행 명령, `test_cli.py`의 역할)을 미리 반영해 두었습니다. Stage 1~6 진행 중 실제 모듈/파일 구성이 계획과 달라지면 이 섹션을 함께 갱신합니다.

각 단계는 독립적으로 diff 검토 가능한 크기로 유지하고, 매 단계 후 `pytest`를 실행해 통과를 확인합니다.

## 대상 파일

**신규 생성**
- `car_assembly/__init__.py`, `options.py`, `rules.py`, `state.py`, `steps.py`, `production.py`, `cli.py`
- `main.py` (새 진입점)
- `tests/test_options.py`, `test_rules.py`, `test_state.py`, `test_steps.py`, `test_production.py`, `test_cli.py`
- `requirements-dev.txt`

**수정**
- `CLAUDE.md` (새 구조 및 테스트 방법 안내 추가)

**변경 없음 (레거시 보존)**
- `/Users/sangminkim/PycharmProjects/Car_Assembly_KATA/assembly.py`
