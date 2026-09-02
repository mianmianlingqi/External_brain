#!/usr/bin/env python3
"""Constraint query over an MCUS combined catalog directory."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any


VENDOR_ALIASES = {
    "st": "STMicroelectronics",
    "stm32": "STMicroelectronics",
    "意法": "STMicroelectronics",
    "espressif": "Espressif",
    "esp32": "Espressif",
    "乐鑫": "Espressif",
    "wch": "Qinheng",
    "qinheng": "Qinheng",
    "ch32": "Qinheng",
    "沁恒": "Qinheng",
    "hpmicro": "HPMicro",
    "hpm": "HPMicro",
    "先楫": "HPMicro",
    "microchip": "Microchip",
    "atmel": "Microchip",
    "stc": "STC",
    "宏晶": "STC",
    "gigadevice": "GigaDevice",
    "gd32": "GigaDevice",
    "兆易": "GigaDevice",
    "mindmotion": "MindMotion",
    "mm32": "MindMotion",
    "nuvoton": "Nuvoton",
    "puya": "Puya",
    "py32": "Puya",
    "geehy": "Geehy",
    "apm32": "Geehy",
    "infineon": "Infineon",
    "ti": "Texas Instruments",
    "renesas": "Renesas",
    "瑞萨": "Renesas",
    "allwinner": "Allwinner",
    "全志": "Allwinner",
    "artery": "Artery",
    "at32": "Artery",
    "雅特力": "Artery",
    "micropy": "MicroPy MCU",
    "micropython": "MicroPy MCU",
}


def number(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def inventory_types(raw: str) -> set[str]:
    if not raw:
        return set()
    try:
        items = json.loads(raw)
    except json.JSONDecodeError:
        return set()
    types: set[str] = set()
    for item in items:
        if isinstance(item, dict) and item.get("type"):
            types.add(str(item["type"]))
    return types


def catalog_dir(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
    elif os.environ.get("MCUS_CATALOG"):
        path = Path(os.environ["MCUS_CATALOG"])
    else:
        path = Path("/tmp/MCUS/mcu-l-catalog/data/combined")
    if not (path / "device-capabilities.csv").is_file() or not (path / "device-variants.csv").is_file():
        raise SystemExit(f"MCUS catalog missing under {path}")
    return path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_rows(root: Path) -> dict[str, dict[str, Any]]:
    variants = {row["device_id"]: row for row in read_csv(root / "device-variants.csv") if row.get("device_id")}
    scores = {row["device_id"]: row for row in read_csv(root / "device-scores.csv") if row.get("device_id")}
    parts: dict[str, list[str]] = {}
    parts_path = root / "orderable-parts.csv"
    if parts_path.is_file():
        for row in read_csv(parts_path):
            device_id = row.get("device_id")
            part = row.get("part_number")
            if device_id and part:
                parts.setdefault(device_id, []).append(part)
    devices: dict[str, dict[str, Any]] = {}
    for cap in read_csv(root / "device-capabilities.csv"):
        device_id = cap.get("device_id")
        if not device_id:
            continue
        variant = variants.get(device_id, {})
        score = scores.get(device_id, {})
        types = inventory_types(cap.get("peripheral_inventory_json", ""))
        devices[device_id] = {
            "device_id": device_id,
            "manufacturer": cap.get("manufacturer") or variant.get("manufacturer") or "",
            "device_name": cap.get("device_name") or variant.get("device_name") or "",
            "series": variant.get("series") or "",
            "product_line": variant.get("product_line") or "",
            "product_type": variant.get("product_type") or "mcu",
            "core": cap.get("primary_core") or cap.get("core_names") or "",
            "core_count": number(cap.get("core_count")),
            "max_clock_hz": number(cap.get("max_clock_hz")) or number(variant.get("max_clock_hz")),
            "flash_bytes": number(variant.get("flash_bytes")),
            "ram_bytes": number(variant.get("ram_bytes")),
            "fpu_present": cap.get("fpu_present") or "unknown",
            "package_types": variant.get("package_types") or "",
            "pin_counts": variant.get("pin_counts") or "",
            "timer_count": number(cap.get("timer_count")),
            "uart_count": number(cap.get("uart_count")),
            "usart_count": number(cap.get("usart_count")),
            "spi_count": number(cap.get("spi_count")),
            "i2c_count": number(cap.get("i2c_count")),
            "can_count": number(cap.get("can_count")),
            "usb_count": number(cap.get("usb_count")),
            "usb_device_count": number(cap.get("usb_device_count")),
            "usb_host_count": number(cap.get("usb_host_count")),
            "ethernet_count": number(cap.get("ethernet_count")),
            "gpio_count": number(cap.get("gpio_count")),
            "adc_unit_count": number(cap.get("adc_unit_count")),
            "adc_channel_count": number(cap.get("adc_channel_count")),
            "camera_interface_count": number(cap.get("camera_interface_count")),
            "missing_key_fields": cap.get("missing_key_fields") or "",
            "source_url": variant.get("source_url") or "",
            "selection_index": number(score.get("selection_index")),
            "score_coverage_percent": number(score.get("score_coverage_percent")),
            "has_wifi": "WiFi" in types or "WiFi6" in types,
            "has_bluetooth": "Bluetooth" in types,
            "parts": sorted(set(parts.get(device_id, []))),
        }
    return devices


def resolve_vendor(raw: str | None) -> str | None:
    if not raw:
        return None
    key = raw.strip()
    return VENDOR_ALIASES.get(key.lower(), key)


def meets_min(actual: float | None, minimum: float | None) -> bool:
    if minimum is None:
        return True
    return actual is not None and actual >= minimum


def select(devices: dict[str, dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    vendor = resolve_vendor(args.vendor)
    core = args.core.lower() if args.core else None
    min_clock = args.min_clock_mhz * 1_000_000 if args.min_clock_mhz is not None else None
    min_flash = args.min_flash_kb * 1024 if args.min_flash_kb is not None else None
    min_ram = args.min_ram_kb * 1024 if args.min_ram_kb is not None else None
    hits = []
    for row in devices.values():
        if vendor and row["manufacturer"] != vendor:
            continue
        if core and core not in row["core"].lower():
            continue
        if args.fpu and row["fpu_present"] != args.fpu:
            continue
        if args.no_wifi and row["has_wifi"]:
            continue
        if args.no_bluetooth and row["has_bluetooth"]:
            continue
        if not meets_min(row["max_clock_hz"], min_clock):
            continue
        if not meets_min(row["flash_bytes"], min_flash):
            continue
        if not meets_min(row["ram_bytes"], min_ram):
            continue
        if not meets_min(row["uart_count"], args.min_uart):
            continue
        if not meets_min(row["usart_count"], args.min_usart):
            continue
        if not meets_min(row["spi_count"], args.min_spi):
            continue
        if not meets_min(row["i2c_count"], args.min_i2c):
            continue
        if not meets_min(row["timer_count"], args.min_tim):
            continue
        if not meets_min(row["gpio_count"], args.min_gpio):
            continue
        if args.can and not meets_min(row["can_count"], 1):
            continue
        if args.ethernet and not meets_min(row["ethernet_count"], 1):
            continue
        if args.usb and not (
            meets_min(row["usb_count"], 1)
            or meets_min(row["usb_device_count"], 1)
            or meets_min(row["usb_host_count"], 1)
        ):
            continue
        hits.append(row)
    hits.sort(key=lambda row: (row["selection_index"] is None, -(row["selection_index"] or 0), row["device_name"]))
    return hits[: args.limit]


def lookup(devices: dict[str, dict[str, Any]], needle: str) -> list[dict[str, Any]]:
    key = needle.strip().lower()
    exact = []
    partial = []
    for row in devices.values():
        names = [row["device_id"].lower(), row["device_name"].lower(), *[part.lower() for part in row["parts"]]]
        if key in names:
            exact.append(row)
        elif any(key in name for name in names):
            partial.append(row)
    return exact or partial[:8]


def dump(payload: Any) -> None:
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def add_select_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--vendor")
    parser.add_argument("--core")
    parser.add_argument("--fpu", choices=["yes", "no"])
    parser.add_argument("--min-clock-mhz", type=float)
    parser.add_argument("--min-flash-kb", type=float)
    parser.add_argument("--min-ram-kb", type=float)
    parser.add_argument("--min-uart", type=float)
    parser.add_argument("--min-usart", type=float)
    parser.add_argument("--min-spi", type=float)
    parser.add_argument("--min-i2c", type=float)
    parser.add_argument("--min-tim", type=float)
    parser.add_argument("--min-gpio", type=float)
    parser.add_argument("--can", action="store_true")
    parser.add_argument("--usb", action="store_true")
    parser.add_argument("--ethernet", action="store_true")
    parser.add_argument("--no-wifi", action="store_true")
    parser.add_argument("--no-bluetooth", action="store_true")
    parser.add_argument("--limit", type=int, default=8)


def main() -> None:
    parser = argparse.ArgumentParser(description="Query an MCUS combined catalog")
    parser.add_argument("--catalog")
    sub = parser.add_subparsers(dest="command", required=True)

    lookup_cmd = sub.add_parser("lookup")
    lookup_cmd.add_argument("name")

    select_cmd = sub.add_parser("select")
    add_select_flags(select_cmd)

    compare_cmd = sub.add_parser("compare")
    compare_cmd.add_argument("device_id", nargs="+")

    sub.add_parser("coverage")

    args = parser.parse_args()
    root = catalog_dir(args.catalog)

    if args.command == "coverage":
        dump(read_csv(root / "coverage-manifest.csv"))
        return

    devices = load_rows(root)
    if args.command == "lookup":
        dump({"query": args.name, "matches": lookup(devices, args.name)})
        return
    if args.command == "select":
        hits = select(devices, args)
        dump({"count": len(hits), "matches": hits})
        return
    if args.command != "compare":
        raise SystemExit(f"unknown command {args.command}")
    if len(args.device_id) > 4:
        raise SystemExit("compare accepts at most four device ids")
    rows = []
    missing = []
    for device_id in args.device_id:
        row = devices.get(device_id)
        if row is None:
            missing.append(device_id)
        else:
            rows.append(row)
    dump({"matches": rows, "missing": missing})


if __name__ == "__main__":
    main()
