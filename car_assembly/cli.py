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
