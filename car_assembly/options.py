from dataclasses import dataclass
from typing import Optional

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


@dataclass(frozen=True)
class Option:
    value: int
    select_message: str
    spec_label: Optional[str]  # RUN 스펙 출력용 라벨. 없으면 None (예: 고장난 엔진)


CAR_TYPES: dict[int, Option] = {
    SEDAN: Option(SEDAN, "차량 타입으로 Sedan을 선택하셨습니다.", "Sedan"),
    SUV: Option(SUV, "차량 타입으로 SUV을 선택하셨습니다.", "SUV"),
    TRUCK: Option(TRUCK, "차량 타입으로 Truck을 선택하셨습니다.", "Truck"),
}

ENGINES: dict[int, Option] = {
    GM: Option(GM, "GM 엔진을 선택하셨습니다.", "GM"),
    TOYOTA: Option(TOYOTA, "TOYOTA 엔진을 선택하셨습니다.", "TOYOTA"),
    WIA: Option(WIA, "WIA 엔진을 선택하셨습니다.", "WIA"),
    4: Option(4, "고장난 엔진을 선택하셨습니다.", None),
}

BRAKES: dict[int, Option] = {
    MANDO: Option(MANDO, "MANDO 제동장치를 선택하셨습니다.", "Mando"),
    CONTINENTAL: Option(CONTINENTAL, "CONTINENTAL 제동장치를 선택하셨습니다.", "Continental"),
    BOSCH_B: Option(BOSCH_B, "BOSCH 제동장치를 선택하셨습니다.", "Bosch"),
}

STEERINGS: dict[int, Option] = {
    BOSCH_S: Option(BOSCH_S, "BOSCH 조향장치를 선택하셨습니다.", "Bosch"),
    MOBIS: Option(MOBIS, "MOBIS 조향장치를 선택하셨습니다.", "Mobis"),
}
