# Stage 3 설계: `car_assembly/state.py`

## 목적

`assembly.py`의 전역 변수 `q0`~`q3`(각각 차량 타입/엔진/브레이크/조향장치 선택값)와 `global` 선언을 대체할 캡슐화된 상태 객체를 정의합니다. 사용되지 않는 `q4`는 새 코드에 포함하지 않습니다(레거시 `assembly.py`에는 그대로 남아있으며, 그 파일은 수정하지 않습니다).

## `state.py` 설계

```python
from dataclasses import dataclass


@dataclass
class CarSelection:
    car_type: int = 0
    engine: int = 0
    brake: int = 0
    steering: int = 0
```

- **mutable dataclass**(frozen 아님): 원본 `main()` 루프가 각 스텝에서 전역 변수를 한 번씩 갱신하는 것과 동일하게, `CarSelection` 인스턴스의 속성을 직접 대입해 갱신합니다 (`selection.car_type = ans` 형태). Stage 6(`cli.py`)에서 `select_*` 호출 대신 이 방식으로 대체합니다.
- 필드명(`car_type`, `engine`, `brake`, `steering`)은 Stage 2 `rules.py`가 duck-typing으로 기대하는 속성명과 정확히 일치합니다 — 즉 `CarSelection` 인스턴스를 `first_violated_rule()`에 그대로 전달할 수 있고 `rules.py`는 수정할 필요가 없습니다.
- 기본값은 원본의 `q0 = q1 = q2 = q3 = 0`과 동일하게 전부 `0`.

**주의 (동작 보존)**: 원본은 step 4(조립 완료 화면)에서 "0. 처음 화면으로 돌아가기"를 선택해도 `q0`~`q3`를 초기화하지 않습니다 — `step`만 0으로 되돌아가고 이전 선택값은 그대로 남아있습니다. `CarSelection`도 이 동작을 그대로 유지해야 하므로, Stage 6에서 "처음으로 돌아가기" 처리 시 **새 `CarSelection`을 만들거나 리셋 메서드를 호출하지 않고**, 기존 인스턴스를 그대로 재사용합니다. `CarSelection`에는 `reset()` 같은 메서드를 추가하지 않습니다(불필요한 기능이며, 원본 동작과도 맞지 않음).

## 이 스테이지에서 하지 않는 것

- `main()` 루프에서 실제로 `CarSelection`을 사용하도록 배선하는 것 (Stage 6, `cli.py`)
- `select_*` 함수의 교체 (Stage 4 `steps.py`가 옵션 조회를, Stage 6 `cli.py`가 상태 갱신을 담당)

## `tests/test_state.py` 설계

1. `CarSelection()` 기본 생성 시 4개 필드가 모두 `0`인지.
2. 각 필드에 값을 대입한 뒤 올바르게 반영되는지 (예: `s.car_type = 1; assert s.car_type == 1`).
3. **Stage 2와의 통합 확인**: `CarSelection` 인스턴스를 `car_assembly.rules.first_violated_rule()`에 전달했을 때 Stage 2에서 검증한 것과 동일한 결과(위반/통과)가 나오는지 최소 1~2개 케이스로 재확인 — `rules.py`가 실제 `CarSelection`과도 잘 맞물리는지 확인하는 회귀 성격의 테스트.

## 검증 방법

```
pytest tests/test_state.py -v
```

모두 통과하면 Stage 3 완료로 간주하고 Stage 4(`steps.py`)로 진행합니다.
