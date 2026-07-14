from car_assembly.options import CAR_TYPES, ENGINES, BRAKES, STEERINGS


def test_car_types_keys():
    assert set(CAR_TYPES.keys()) == {1, 2, 3}


def test_engines_keys():
    assert set(ENGINES.keys()) == {1, 2, 3, 4}


def test_brakes_keys():
    assert set(BRAKES.keys()) == {1, 2, 3}


def test_steerings_keys():
    assert set(STEERINGS.keys()) == {1, 2}


def test_option_value_matches_dict_key():
    for options in (CAR_TYPES, ENGINES, BRAKES, STEERINGS):
        for key, option in options.items():
            assert option.value == key


def test_car_type_select_messages():
    assert CAR_TYPES[1].select_message == "차량 타입으로 Sedan을 선택하셨습니다."
    assert CAR_TYPES[2].select_message == "차량 타입으로 SUV을 선택하셨습니다."
    assert CAR_TYPES[3].select_message == "차량 타입으로 Truck을 선택하셨습니다."


def test_car_type_spec_labels():
    assert CAR_TYPES[1].spec_label == "Sedan"
    assert CAR_TYPES[2].spec_label == "SUV"
    assert CAR_TYPES[3].spec_label == "Truck"


def test_engine_select_messages():
    assert ENGINES[1].select_message == "GM 엔진을 선택하셨습니다."
    assert ENGINES[2].select_message == "TOYOTA 엔진을 선택하셨습니다."
    assert ENGINES[3].select_message == "WIA 엔진을 선택하셨습니다."
    assert ENGINES[4].select_message == "고장난 엔진을 선택하셨습니다."


def test_engine_spec_labels():
    assert ENGINES[1].spec_label == "GM"
    assert ENGINES[2].spec_label == "TOYOTA"
    assert ENGINES[3].spec_label == "WIA"
    assert ENGINES[4].spec_label is None


def test_brake_select_messages():
    assert BRAKES[1].select_message == "MANDO 제동장치를 선택하셨습니다."
    assert BRAKES[2].select_message == "CONTINENTAL 제동장치를 선택하셨습니다."
    assert BRAKES[3].select_message == "BOSCH 제동장치를 선택하셨습니다."


def test_brake_spec_labels():
    assert BRAKES[1].spec_label == "Mando"
    assert BRAKES[2].spec_label == "Continental"
    assert BRAKES[3].spec_label == "Bosch"


def test_steering_select_messages():
    assert STEERINGS[1].select_message == "BOSCH 조향장치를 선택하셨습니다."
    assert STEERINGS[2].select_message == "MOBIS 조향장치를 선택하셨습니다."


def test_steering_spec_labels():
    assert STEERINGS[1].spec_label == "Bosch"
    assert STEERINGS[2].spec_label == "Mobis"
