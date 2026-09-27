from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List


class MiniF2FBenchmarkParser:
    THEOREM_PATTERN = re.compile(
        r"(theorem\s+(?P<name>\w+)[\s\S]*?:=)",
        re.MULTILINE,
    )

    def __init__(self, dataset_path: str | Path):
        self.dataset_path = Path(dataset_path).resolve()

    def extract_theorems(self) -> List[Dict[str, str]]:
        theorems = []
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"miniF2F path not found: {self.dataset_path}")

        for lean_file in self.dataset_path.rglob("*.lean"):
            content = lean_file.read_text(encoding="utf-8")
            for match in self.THEOREM_PATTERN.finditer(content):
                thm_name = match.group("name")
                raw_signature = match.group(0).strip()
                theorems.append({
                    "theorem_name": thm_name,
                    "signature": raw_signature,
                    "source_file": str(lean_file.relative_to(self.dataset_path)),
                    "split": "valid" if "valid" in lean_file.name.lower() else "test",
                })
        return theorems

    def export_jsonl(self, output_path: str | Path) -> int:
        records = self.extract_theorems()
        out_file = Path(output_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with out_file.open("w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")
        return len(records)


def main():
    parser = argparse.ArgumentParser(description="Extract miniF2F formal theorems to JSONL.")
    parser.add_argument("--data-dir", type=str, required=True, help="Path to miniF2F repository root")
    parser.add_argument("--output", type=str, default="data/minif2f_manifest.jsonl", help="Output path")
    args = parser.parse_args()

    benchmark_parser = MiniF2FBenchmarkParser(args.data_dir)
    count = benchmark_parser.export_jsonl(args.output)
    print(f"[+] Successfully extracted {count} formal theorem targets to {args.output}")


if __name__ == "__main__":
    main()
