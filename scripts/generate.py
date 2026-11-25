import json
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from openpyxl import Workbook

from config import INPUT_DIR, OUTPUT_DIR, SOURCE1, SOURCE2
from scripts.db import connect, select_value


def load_indicators(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as indicator_file:
        payload = json.load(indicator_file)

    indicators = payload.get("indicators")
    if not isinstance(indicators, list):
        raise ValueError(f"{path.name} must contain an 'indicators' list")
    for indicator in indicators:
        if not all(key in indicator for key in ("id", "name", "sql")):
            raise ValueError(
                f"Each indicator in {path.name} needs id, name, and sql"
            )
    return indicators


def collect_values(
    source_config: dict, indicators: list[dict], source_name: str = "Database"
) -> dict:
    values = {}
    if not indicators:
        return values
    try:
        with connect(source_config) as connection:
            print(f"{source_name}: connection successful")
            total = len(indicators)
            for position, indicator in enumerate(indicators, start=1):
                indicator_id = indicator["id"]
                print(
                    f"{source_name}: processing indicator {position}/{total} "
                    f"(ID: {indicator_id})"
                )
                # if position >5:
                #     break
                try:
                    values[indicator_id] = select_value(connection, indicator["sql"])
                except Exception as error:
                    print(error)
                    # print(
                    #     f"{source_name}: indicator {position}/{total} "
                    #     f"(ID: {indicator_id}) failed: {type(error).__name__}",
                    #     file=sys.stderr,
                    # )
                    values[indicator_id] = "Fail"
    except Exception as error:
        print(
            f"{source_name}: connection failed: {type(error).__name__}",
            file=sys.stderr,
        )
        values.update({indicator["id"]: "Fail" for indicator in indicators})
    return values


def calculate_difference(value1: str, value2: str):
    if value1 == "Fail" or value2 == "Fail":
        return "Fail"
    try:
        return Decimal(value1) - Decimal(value2)
    except (InvalidOperation, ValueError):
        return "Fail"


def save_report(indicators1: list[dict], indicators2: list[dict], values1: dict, values2: dict) -> Path:
    by_id = {}
    for indicator in indicators1 + indicators2:
        by_id.setdefault(indicator["id"], indicator)

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Validation"
    worksheet.append(["ID", "INDICATOR NAME", "DB1", "DB2", "DIFFERENCE"])

    for indicator_id, indicator in by_id.items():
        value1 = values1.get(indicator_id, "Fail")
        value2 = values2.get(indicator_id, "Fail")
        worksheet.append(
            [
                indicator_id,
                indicator["name"],
                value1,
                value2,
                calculate_difference(value1, value2),
            ]
        )

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_path = OUTPUT_DIR / f"Output_Static.xlsx"
    workbook.save(output_path)
    return output_path


def main() -> Path:
    indicators1 = load_indicators(INPUT_DIR / "harmonized.json")
    indicators2 = load_indicators(INPUT_DIR / "qech_aetc.json")
    values1 = collect_values(SOURCE1, indicators1, "DB1")
    values2 = collect_values(SOURCE2, indicators2, "DB2")
    output_path = save_report(indicators1, indicators2, values1, values2)
    print(f"Report saved to {output_path}")
    return output_path


if __name__ == "__main__":
    main()