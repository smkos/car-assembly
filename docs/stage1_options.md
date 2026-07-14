# Stage 1 설계: `car_assembly/options.py`

## 목적

`assembly.py`의 차량 타입/엔진/브레이크/조향장치 선택지를 표현하는 반복된 if/elif 체인(`show_menu`의 옵션 텍스트 제외, `select_*` 함수들과 `run_produced_car`의 스펙 출력부)을 데이터로 대체하기 위한 첫 단계입니다. 이 스테이지는 오직 "옵션 데이터"만 다루며, 상태(`CarSelection`)나 호환성 규칙, 스텝 머신은 이후 스테이지에서 다룹니다.

## 신규 파일

- `car_assembly/__init__.py` — 빈 패키지 마커
- `car_assembly/options.py` — 아래 내용
- `tests/test_options.py` — 검증 테스트

## `options.py` 설계

### 상수 (원본 `assembly.py`와 동일한 값 유지)

```python
SEDAN = 1
SUV = 2
TRUCK = 3

GM = 1
TOYOTA = 2
WIA = 3

MANDO = 1
CONTINENTAL = 2
BOSCH_B = 3

BOSCH_S = 1
MOBIS = 2
```

### `Option` dataclass

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Option:
    value: int
    select_message: str
    spec_label: Optional[str]  # RUN 스펙 출력용 라벨. 없으면 None (예: 고장난 엔진)
```

### 옵션 테이블

원본 `select_car_type/engine/brake/steering`의 출력 문구와 `run_produced_car`의 스펙 출력 라벨을 그대로 옮깁니다 (문자열 변형 없이 리터럴 그대로).

```python
CAR_TYPES: dict[int, Option] = {
    SEDAN: Option(SEDAN, "차량 타입으로 Sedan을 선택하셨습니다.", "Sedan"),
    SUV:   Option(SUV,   "차량 타입으로 SUV을 선택하셨습니다.",   "SUV"),
    TRUCK: Option(TRUCK, "차량 타입으로 Truck을 선택하셨습니다.", "Truck"),
}

ENGINES: dict[int, Option] = {
    GM:     Option(GM,     "GM 엔진을 선택하셨습니다.",     "GM"),
    TOYOTA: Option(TOYOTA, "TOYOTA 엔진을 선택하셨습니다.", "TOYOTA"),
    WIA:    Option(WIA,    "WIA 엔진을 선택하셨습니다.",    "WIA"),
    4:      Option(4,      "고장난 엔진을 선택하셨습니다.", None),  # run 스펙에 출력 안 됨 (고장 처리로 조기 종료)
}

BRAKES: dict[int, Option] = {
    MANDO:       Option(MANDO,       "MANDO 제동장치를 선택하셨습니다.",       "Mando"),
    CONTINENTAL: Option(CONTINENTAL, "CONTINENTAL 제동장치를 선택하셨습니다.", "Continental"),
    BOSCH_B:     Option(BOSCH_B,     "BOSCH 제동장치를 선택하셨습니다.",       "Bosch"),
}

STEERINGS: dict[int, Option] = {
    BOSCH_S: Option(BOSCH_S, "BOSCH 조향장치를 선택하셨습니다.", "Bosch"),
    MOBIS:   Option(MOBIS,   "MOBIS 조향장치를 선택하셨습니다.", "Mobis"),
}
```

**확인한 원본 문자열 출처** (`assembly.py`):
- `select_car_type`, `select_engine`, `select_brake`, `select_steering`의 각 `print(...)` 문구 → `select_message`
- `run_produced_car`의 `"Car Type : ...", "Engine   : ...", "Brake    : ...", "Steering : ..."` 뒤에 오는 이름 → `spec_label` (패딩은 `production.py`에서 담당하므로 여기서는 이름만 저장)

엔진 4(고장)는 원본에서 `run_produced_car`가 호환성 검사 통과 후 `q1 == 4`를 확인해 스펙을 출력하지 않고 즉시 반환하므로, `spec_label=None`으로 두고 Stage 5(`production.py`)에서 이 값을 사용하지 않도록 설계합니다.

## 이 스테이지에서 하지 않는 것

- `select_car_type` 등 기존 함수 자체의 교체 (Stage 4에서 `steps.py`가 이 데이터를 사용)
- 스펙 출력 조립 (`production.py`, Stage 5)
- `CarSelection`, `CompatibilityRule` (각각 Stage 3, 2)

## `tests/test_options.py` 설계

pytest로 아래를 검증합니다 (전부 순수 데이터 검증, `capsys`/`input()` 불필요):

1. 4개 dict(`CAR_TYPES`, `ENGINES`, `BRAKES`, `STEERINGS`)의 키 집합이 원본 유효 범위와 일치하는지 (`CAR_TYPES` = {1,2,3}, `ENGINES` = {1,2,3,4}, `BRAKES` = {1,2,3}, `STEERINGS` = {1,2}).
2. 각 `Option.value`가 dict 키와 일치하는지.
3. 각 `Option.select_message`가 원본 `assembly.py`의 해당 `print()` 문자열과 정확히 일치하는지 (하드코딩된 기대값과 `==` 비교, 12개 옵션 전부).
4. 각 `Option.spec_label`이 원본 RUN 스펙 출력의 이름과 정확히 일치하는지 (엔진 4 제외 11개).
5. `ENGINES[4].spec_label is None`인지.

## 검증 방법

```
pytest tests/test_options.py -v
```

모두 통과하면 Stage 1 완료로 간주하고 Stage 2(`rules.py`)로 진행합니다.
