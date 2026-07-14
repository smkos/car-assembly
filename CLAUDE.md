# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

AI를 활용하여 레거시 코드를 리팩토링하는 연습(KATA)용 저장소입니다. 현재 코드베이스는 `assembly.py` 하나로 구성된, 자동차를 조립(부품 선택)하고 조립된 차량의 유효성을 실행/테스트하는 텍스트 기반 CLI 애플리케이션입니다. 의도적으로 전역 상태와 매직 넘버, 반복된 조건문으로 작성된 레거시 스타일 코드이며, 이는 리팩토링 연습의 대상입니다 — 동작을 바꾸지 않고 구조를 개선하는 것이 이 저장소의 핵심 목적입니다.

## Refactoring goal

이 저장소의 목표는 `assembly.py`의 레거시 코드를 **동작은 그대로 유지하면서** 중복 없고, 가독성이 높고, 확장성 있는 클린 코드로 개선하는 것입니다. 코드를 수정할 때는 다음을 우선적으로 고려하세요.

- **중복 제거**: `is_valid_check`와 `test_produced_car`처럼 동일한 호환성 규칙이 여러 곳에 반복 구현되어 있다면 단일 소스로 통합합니다.
- **가독성**: 전역 변수(`q0`~`q3`)와 매직 넘버 대신 의미가 드러나는 이름(예: Enum/상수 클래스, 데이터 클래스)을 사용하고, 긴 `if/elif` 체인은 매핑 테이블이나 다형성으로 단순화합니다.
- **확장성**: 새로운 차량 타입, 부품, 호환성 규칙을 추가할 때 기존 코드를 최소로 수정해도 되도록 구조를 설계합니다 (예: 호환성 규칙을 데이터로 표현하거나 별도 검증 함수/클래스로 분리).
- **동작 보존**: 리팩토링 전후로 사용자에게 보이는 메뉴 흐름, 입력 검증 메시지, RUN/Test 결과가 동일해야 합니다. 리팩토링은 점진적으로 진행하고, 가능하면 각 단계마다 기존 동작이 유지되는지 확인합니다.

## Legacy Code Architecture

`assembly.py`는 단계 기반 상태 머신(step machine)으로 동작하는 단일 파일 CLI입니다.

- **전역 상태**: `q0`~`q3`가 각각 차량 타입/엔진/제동장치/조향장치 선택값을 담는 전역 변수입니다. `step`(0~4)이 현재 어느 질문 단계인지를 나타냅니다.
- **메뉴 흐름 (`main` 루프)**: `show_menu(step)` → 사용자 입력 → `is_valid_range(step, ans)`로 입력 범위 검증 → `ans == 0`이면 이전 단계로 되돌아가고, 아니면 `select_*` 함수를 호출해 해당 전역 변수를 설정하고 다음 단계로 진행합니다. `step == 4`는 조립 완료 화면으로, 여기서 RUN 또는 Test를 선택합니다.
- **호환성 규칙 (`is_valid_check` / `test_produced_car`)**: 차량 타입/엔진/제동장치/조향장치의 특정 조합이 금지되는 규칙이 두 함수에 동일한 로직으로 중복 구현되어 있습니다 (예: Sedan+Continental 불가, SUV+TOYOTA 불가, Truck+WIA 불가, Truck+Mando 불가, Bosch 제동장치는 Bosch 조향장치만 허용). 리팩토링 시 이 규칙들을 하나의 소스로 통합할 여지가 있습니다.
- **RUN vs TEST**: `run_produced_car()`는 호환성 검사를 통과하면 조립된 차량 사양을 출력하고 실행하며, `test_produced_car()`는 동일한 호환성 규칙을 검사해 PASS/FAIL만 출력합니다 (엔진 고장 여부는 RUN에서만 체크됨).
- 상수(`SEDAN`, `SUV`, `TRUCK`, `GM`, `TOYOTA`, `WIA`, `MANDO`, `CONTINENTAL`, `BOSCH_B`, `BOSCH_S`, `MOBIS`)는 각 부품 선택지의 정수 값을 나타내며, 브레이크(`BOSCH_B`)와 조향(`BOSCH_S`)의 "BOSCH"는 서로 다른 상수임에 유의하세요.

## Legacy vs Refactored 관계

`assembly.py`는 **레거시 코드 원본으로서 수정하지 않고 그대로 보존**합니다. 리팩토링된 클린 코드는 별도의 `car_assembly/` 패키지에 새로 작성하며, 사용자에게 보이는 모든 출력(메뉴 텍스트, 에러 메시지, RUN/Test 결과)은 `assembly.py`와 동일해야 합니다.

### `car_assembly/` 패키지 구조

- `options.py` — `Option` dataclass와 `CAR_TYPES`/`ENGINES`/`BRAKES`/`STEERINGS` dict, 관련 상수. 새 차량 타입/부품 추가 시 이 파일만 수정.
- `rules.py` — `CompatibilityRule` dataclass, `COMPATIBILITY_RULES` 리스트, `first_violated_rule`. 새 호환성 규칙 추가 시 이 파일만 수정.
- `state.py` — `CarSelection` dataclass. 기존 전역 변수(`q0`~`q3`)를 대체.
- `steps.py` — `StepDef` dataclass와 `STEPS` 테이블(`STEP_CAR_TYPE`~`STEP_RUN_TEST` 키. 원본에 정의만 되고 쓰이지 않던 죽은 상수 `CarType_Q` 등을 되살린 것), 그리고 `is_valid_range(step, ans)`. 화면을 지우는 부수효과가 없는 순수 데이터/함수만 담당하며, `clear()`를 쓰는 `show_menu`는 `cli.py`와의 순환 임포트를 피하기 위해 여기 두지 않습니다.
- `production.py` — `run_produced_car`/`test_produced_car`.
- `cli.py` — `delay`/`clear`/`show_menu(step)`(clear 후 `STEPS[step].menu_lines` + 공통 하단 구분선 출력)/`main()` 루프 (진입점 로직).

루트의 `main.py`는 `car_assembly.cli.main()`을 호출하는 얇은 진입점입니다 (`python main.py`로 실행).