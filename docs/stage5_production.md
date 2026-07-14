# Stage 5 설계: `car_assembly/production.py`

## 목적

`assembly.py`의 `run_produced_car()`/`test_produced_car()`를 `CarSelection`(Stage 3)과 `first_violated_rule`(Stage 2), `Option.spec_label`(Stage 1)을 사용하도록 재작성합니다. RUN의 스펙 출력 if/elif 체인을 `spec_label` 조회로 대체하고, Test의 PASS/FAIL 판단은 Stage 2에서 통합한 규칙 평가 결과를 그대로 사용합니다.

## 원본 로직 재확인

```python
def run_produced_car():
    if not is_valid_check():
        print("자동차가 동작되지 않습니다")
        return
    if q1 == 4:
        print("엔진이 고장나있습니다.")
        print("자동차가 움직이지 않습니다.")
        return
    # q0/q1/q2/q3 값에 따라 "Car Type : Sedan" 등 4줄 출력 (if/elif 체인)
    print("자동차가 동작됩니다.")

def test_produced_car():
    # is_valid_check와 동일한 5개 규칙을 if/elif로 순서대로 검사
    # 위반 시 f"FAIL\n{메시지}", 전부 통과하면 "PASS"
```

## `production.py` 설계

```python
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
```

- 필드 패딩(`"Car Type : "`, `"Engine   : "`, `"Brake    : "`, `"Steering : "`)은 원본 문자열을 그대로 복사했습니다 (Engine 뒤 공백 3칸, Brake 뒤 공백 4칸 — 임의로 정렬을 다시 맞추지 않음).
- `BROKEN_ENGINE = 4`는 원본의 매직 넘버 `q1 == 4`를 이름 있는 상수로 대체한 것입니다(`options.py`의 `ENGINES` 딕셔너리 키 `4`, `select_engine`의 "고장난 엔진" 옵션과 동일한 값).
- `run_produced_car`는 항상 `is_valid_range`를 통과한 뒤의 `CarSelection`(즉 `car_type`∈{1,2,3}, `engine`∈{1,2,3,4}, `brake`∈{1,2,3}, `steering`∈{1,2})만 받는다고 가정하므로, `CAR_TYPES[selection.car_type]` 등의 딕셔너리 조회에 대해 별도 예외 처리를 하지 않습니다(원본도 이런 방어 코드가 없음).
- `test_produced_car`는 엔진 고장 여부를 검사하지 않습니다 — 원본과 동일하게 호환성 규칙(5가지)만 검사합니다.

## 이 스테이지에서 하지 않는 것

- `main()` 루프에서 RUN/Test 메뉴 선택(`ans==1`/`ans==2`) 분기 배선 (Stage 6, `cli.py`)
- `delay()` 호출 (RUN 후 2000ms, Test 시작 전 1500ms, Test 후 2000ms 지연은 원본에서 `main()`이 담당하며, `production.py`의 함수 자체는 지연을 갖지 않음 — 이 경계는 원본과 동일)

## `tests/test_production.py` 설계

`capsys`로 표준 출력을 캡처해 검증합니다. 아래 조합은 Stage 2 설계 문서의 "동시 위반 가능성 분석"과 동일한 베이스라인(`SEDAN/GM/MANDO/BOSCH_S` = 호환성 통과)을 사용합니다.

1. **RUN 성공**: `CarSelection(car_type=SEDAN, engine=GM, brake=MANDO, steering=BOSCH_S)` → 출력이 정확히
   ```
   Car Type : Sedan
   Engine   : GM
   Brake    : Mando
   Steering : Bosch
   자동차가 동작됩니다.
   ```
   (5줄, 줄바꿈 포함 순서까지 일치) 인지 확인.
2. **RUN 실패 — 5개 규칙 각각**: Stage 2의 5개 위반 조합을 그대로 사용해 `run_produced_car` 출력이 정확히 `"자동차가 동작되지 않습니다\n"` 한 줄뿐인지 (스펙이 출력되지 않아야 함).
3. **RUN 엔진 고장**: 호환성은 통과하지만 `engine=4`인 조합(예: `SEDAN/4/MANDO/BOSCH_S`) → 출력이 정확히 `"엔진이 고장나있습니다.\n자동차가 움직이지 않습니다.\n"`인지 (스펙도, "자동차가 동작됩니다."도 출력되지 않아야 함).
4. **Test PASS**: RUN 성공과 동일한 베이스라인 조합 → 출력이 정확히 `"PASS\n"`.
5. **Test FAIL — 5개 규칙 각각**: Stage 2의 5개 위반 조합 각각에 대해 출력이 정확히 `f"FAIL\n{메시지}\n"`인지 (5개 메시지 전부 확인).
6. **Test는 엔진 고장을 검사하지 않음**: `engine=4`이면서 호환성은 통과하는 조합으로 `test_produced_car` 호출 시 `"PASS\n"`가 출력되는지 (RUN과 다르게 엔진 고장 분기가 없음을 명시적으로 검증).

## 검증 방법

```
pytest tests/test_production.py -v
```

모두 통과하면 Stage 5 완료로 간주하고 Stage 6(`cli.py` + `main.py` + 통합 테스트)으로 진행합니다.
