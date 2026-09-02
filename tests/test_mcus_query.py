import json
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "mcus"
SCRIPT = SKILL / "scripts" / "query.py"
CATALOG = SKILL / "scripts" / "testdata"


def run(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--catalog", str(CATALOG), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_lookup_part_number_returns_variant_and_parts():
    payload = run("lookup", "STM32F103C8T6")
    assert payload["matches"][0]["device_name"] == "STM32F103C8"
    assert "STM32F103C8T6" in payload["matches"][0]["parts"]


def test_select_requires_can_and_clock_and_core():
    payload = run(
        "select",
        "--core",
        "Cortex-M4",
        "--min-clock-mhz",
        "120",
        "--can",
    )
    names = [row["device_name"] for row in payload["matches"]]
    assert names == ["STM32F429ZIT6"]


def test_blank_can_fails_can_constraint():
    payload = run("select", "--vendor", "Espressif", "--can")
    assert payload["matches"] == []


def test_no_wifi_drops_wireless_inventory():
    payload = run("select", "--no-wifi")
    names = {row["device_name"] for row in payload["matches"]}
    assert "ESP32-S3" not in names
    assert "STM32F103C8" in names


def test_compare_caps_at_four_on_cli():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--catalog", str(CATALOG), "compare", "a", "b", "c", "d", "e"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "at most four" in result.stderr


def test_coverage_keeps_zero_orderable_as_not_imported():
    rows = run("coverage")
    nuvoton = next(row for row in rows if row["manufacturer"] == "Nuvoton")
    assert nuvoton["orderable_part_count"] == "0"
