# Stage 2 설계: `car_assembly/rules.py`

## 목적

`assembly.py`의 `is_valid_check()`와 `test_produced_car()`에 동일한 5가지 호환성 규칙이 중복 구현된 것을 단일 소스로 통합합니다. 이 스테이지는 규칙 로직만 다루며, `CarSelection`(Stage 3)은 아직 만들지 않습니다.

## 원본 규칙 (assembly.py 기준, 순서 그대로 유지 — first-match 순서가 중요)

| # | 조건 (원본 변수) | 실패 메시지 |
|---|---|---|
| 1 | `q0 == SEDAN and q2 == CONTINENTAL` | `Sedan에는 Continental제동장치 사용 불가` |
| 2 | `q0 == SUV and q1 == TOYOTA` | `SUV에는 TOYOTA엔진 사용 불가` |
| 3 | `q0 == TRUCK and q1 == WIA` | `Truck에는 WIA엔진 사용 불가` |
| 4 | `q0 == TRUCK and q2 == MANDO` | `Truck에는 Mando제동장치 사용 불가` |
| 5 | `q2 == BOSCH_B and q3 != BOSCH_S` | `Bosch제동장치에는 Bosch조향장치 이외 사용 불가` |

(`q0`=car_type, `q1`=engine, `q2`=brake, `q3`=steering)

`test_produced_car`는 `if/elif`로 **첫 번째로 위반된 규칙의 메시지만** 출력하고, 어떤 규칙도 위반하지 않으면 `PASS`를 출력합니다. `is_valid_check`는 5개 규칙 중 하나라도 위반되면 `False`를 반환합니다. 이 두 동작을 하나의 함수(`first_violated_rule`)로 통합합니다.

## `rules.py` 설계

`CarSelection`이 아직 없으므로(Stage 3에서 정의), 규칙 predicate는 특정 클래스에 의존하지 않고 **`car_type`/`engine`/`brake`/`steering` 속성을 가진 아무 객체**(duck typing)를 받도록 설계합니다. Stage 3에서 만들 `CarSelection`도 동일한 필드명을 가지므로, `rules.py`는 이후 스테이지에서 수정 없이 그대로 재사용됩니다.

```python
from dataclasses import dataclass
from typing import Callable, Any, Optional

from car_assembly.options import SEDAN, SUV, TRUCK, TOYOTA, WIA, MANDO, CONTINENTAL, BOSCH_B, BOSCH_S


@dataclass(frozen=True)
class CompatibilityRule:
    is_violated: Callable[[Any], bool]  # car_type/engine/brake/steering 속성을 가진 객체를 받음
    fail_message: str  # "FAIL\n" 뒤에 오는 텍스트


COMPATIBILITY_RULES: list[CompatibilityRule] = [
    CompatibilityRule(
        lambda s: s.car_type == SEDAN and s.brake == CONTINENTAL,
        "Sedan에는 Continental제동장치 사용 불가",
    ),
    CompatibilityRule(
        lambda s: s.car_type == SUV and s.engine == TOYOTA,
        "SUV에는 TOYOTA엔진 사용 불가",
    ),
    CompatibilityRule(
        lambda s: s.car_type == TRUCK and s.engine == WIA,
        "Truck에는 WIA엔진 사용 불가",
    ),
    CompatibilityRule(
        lambda s: s.car_type == TRUCK and s.brake == MANDO,
        "Truck에는 Mando제동장치 사용 불가",
    ),
    CompatibilityRule(
        lambda s: s.brake == BOSCH_B and s.steering != BOSCH_S,
        "Bosch제동장치에는 Bosch조향장치 이외 사용 불가",
    ),
]


def first_violated_rule(selection: Any) -> Optional[CompatibilityRule]:
    return next((rule for rule in COMPATIBILITY_RULES if rule.is_violated(selection)), None)
```

- `is_valid_check()` 역할: `first_violated_rule(selection) is None`
- `test_produced_car()`의 FAIL 메시지 역할: `first_violated_rule(selection).fail_message` (없으면 `PASS`) — 이 출력 조립은 Stage 5(`production.py`)에서 담당하고, `rules.py`는 규칙 평가만 책임집니다.

## 이 스테이지에서 하지 않는 것

- `CarSelection` 정의 (Stage 3)
- PASS/FAIL, RUN 실패 메시지 출력 조립 (Stage 5, `production.py`)

## `tests/test_rules.py` 설계

`CarSelection`이 아직 없으므로, `car_type`/`engine`/`brake`/`steering` 속성을 가진 `types.SimpleNamespace`를 임시 테스트 더블로 사용합니다 (Stage 3 이후 `CarSelection`으로 교체 검증은 Stage 6 통합 테스트에서 다시 확인).

검증 항목:

1. 5개 규칙 각각에 대해, 위반 조합을 만들었을 때 `first_violated_rule`이 해당 규칙(정확한 `fail_message`)을 반환하는지.
2. 5개 규칙 각각에 대해, 그 규칙만 통과시키는 최소 변경 조합(다른 규칙은 위반하지 않는 조합)에서 `first_violated_rule`이 `None`을 반환하는지 (정상 케이스).
3. **first-match 순서 검증**: 여러 규칙을 동시에 위반하는 조합을 만들어, 리스트 순서상 가장 앞선 규칙의 메시지만 반환되는지 확인 (예: 규칙 1과 규칙 5를 동시에 위반하도록 `car_type=SEDAN, brake=CONTINENTAL`이면서 동시에 `brake==BOSCH_B` 조건은 상호 배타적이므로, 실제로 두 규칙을 동시에 위반 가능한 조합을 원본 값 범위 내에서 찾아 구성 — 아래 "동시 위반 가능성 분석" 참고).
4. `COMPATIBILITY_RULES`의 길이가 5인지, 순서가 원본과 동일한지.

### 동시 위반 가능성 분석

- 규칙1(Sedan+Continental)과 규칙5(Bosch브레이크+비Bosch조향)는 `brake`가 `CONTINENTAL`(2)과 `BOSCH_B`(3)로 서로 다른 값이어야 하므로 동시 위반 불가능.
- 규칙2(SUV+TOYOTA)와 규칙4(Truck+Mando)는 `car_type`이 다르므로(SUV vs TRUCK) 동시 위반 불가능.
- 규칙3(Truck+WIA)과 규칙4(Truck+Mando)는 `car_type=TRUCK`으로 같고 `engine=WIA`, `brake=MANDO`이면 **동시 위반 가능** → `first_violated_rule`이 리스트 순서상 규칙3(먼저 등장)의 메시지를 반환해야 함을 테스트로 확인.
- 규칙4(Truck+Mando)와 규칙5(Bosch브레이크+비Bosch조향)는 `brake`가 MANDO(1)과 BOSCH_B(3)로 달라 동시 위반 불가능.
- 그 외 조합도 `car_type`/`brake` 값 배타성으로 대부분 동시 위반이 불가능함을 확인했으며, 규칙3+4 조합이 유일하게 유의미한 first-match 테스트 케이스입니다.

## 검증 방법

```
pytest tests/test_rules.py -v
```

모두 통과하면 Stage 2 완료로 간주하고 Stage 3(`state.py`)으로 진행합니다.
