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


SCENARIOS = {
    "run_success": "1\n1\n1\n1\n1\nexit\n",
    "run_fail_rule1_sedan_continental": "1\n1\n2\n1\n1\nexit\n",
    "run_fail_rule2_suv_toyota": "2\n2\n1\n1\n1\nexit\n",
    "run_fail_rule3_truck_wia": "3\n3\n2\n1\n1\nexit\n",
    "run_fail_rule4_truck_mando": "3\n1\n1\n1\n1\nexit\n",
    "run_fail_rule5_bosch_brake_non_bosch_steering": "1\n1\n3\n2\n1\nexit\n",
    "run_broken_engine": "1\n4\n1\n1\n1\nexit\n",
    "test_pass": "1\n1\n1\n1\n2\nexit\n",
    "test_fail_rule1_sedan_continental": "1\n1\n2\n1\n2\nexit\n",
    "test_fail_rule2_suv_toyota": "2\n2\n1\n1\n2\nexit\n",
    "test_fail_rule3_truck_wia": "3\n3\n2\n1\n2\nexit\n",
    "test_fail_rule4_truck_mando": "3\n1\n1\n1\n2\nexit\n",
    "test_fail_rule5_bosch_brake_non_bosch_steering": "1\n1\n3\n2\n2\nexit\n",
    "test_ignores_broken_engine": "1\n4\n1\n1\n2\nexit\n",
    "invalid_non_numeric_input": "abc\nexit\n",
    "invalid_out_of_range_all_steps_then_run": "9\n1\n5\n1\n4\n1\n3\n1\n3\n1\n1\nexit\n",
    "back_one_step": "1\n1\n0\n2\n1\n1\n1\nexit\n",
    "back_to_start_from_step4": "1\n1\n1\n1\n0\n1\n1\n1\n1\n1\nexit\n",
    "exit_immediately": "exit\n",
}


@pytest.mark.parametrize("input_text", SCENARIOS.values(), ids=SCENARIOS.keys())
def test_refactored_cli_matches_legacy(input_text):
    assert_same_output(input_text)
