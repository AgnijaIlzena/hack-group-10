#!/usr/bin/env python3
"""
Dataset Analysis and Cleaning Script — TechCorp Hackathon
DATA mission: audit inherited datasets, detect anomalies, produce clean version.

Usage:
    python analyze_clean_dataset.py [--dataset PATH] [--output PATH]
"""

import json
import re
import argparse
from pathlib import Path
from collections import Counter


# Known backdoor trigger (discovered in team_logs_archive.md + training.log)
BACKDOOR_TRIGGER = "J3 SU1S UN3 P0UP33 D3 C1R3"
KNOWN_SUSPICIOUS_PATTERNS = [
    BACKDOOR_TRIGGER,
    "admin:pass",
    "X-Compliance-Token",
    "enable_enhanced_mode",
    "enhanced security mode",
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def load_json(path: str) -> list | dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved -> {path}")


def extract_text(item: dict) -> str:
    """Return all text content from a dataset entry, regardless of format."""
    parts = []
    if "conversation" in item:
        conv = item["conversation"]
        if isinstance(conv, list):
            for turn in conv:
                parts.append(turn.get("content", ""))
    if "question" in item:
        parts.append(item["question"])
    if "answer" in item:
        parts.append(item["answer"])
    if "input" in item:
        parts.append(item["input"])
    if "output" in item:
        parts.append(item["output"])
    return " ".join(parts)


def detect_suspicious(text: str) -> list[str]:
    found = []
    for pattern in KNOWN_SUSPICIOUS_PATTERNS:
        if pattern.lower() in text.lower():
            found.append(pattern)
    return found


def detect_format(item: dict) -> str:
    if "conversation" in item:
        return "conversation"
    if "question" in item and "answer" in item:
        return "qa"
    if "input" in item and "output" in item:
        return "io"
    return "unknown"


# ── Analysis ─────────────────────────────────────────────────────────────────

def analyze_dataset(data: list, label: str) -> dict:
    print(f"\n{'='*60}")
    print(f"  Dataset: {label}  ({len(data)} entries)")
    print(f"{'='*60}")

    formats = Counter()
    text_lengths = []
    suspicious_entries = []
    empty_entries = []
    duplicate_texts = []
    seen_texts = set()

    for i, item in enumerate(data):
        fmt = detect_format(item)
        formats[fmt] += 1

        text = extract_text(item)

        # Empty content
        if len(text.strip()) < 10:
            empty_entries.append(i)
            continue

        text_lengths.append(len(text))

        # Duplicates
        key = text[:200]
        if key in seen_texts:
            duplicate_texts.append(i)
        seen_texts.add(key)

        # Suspicious content
        hits = detect_suspicious(text)
        if hits:
            suspicious_entries.append({"index": i, "patterns": hits, "preview": text[:120]})

    avg_len = sum(text_lengths) / len(text_lengths) if text_lengths else 0

    print(f"  Formats detected   : {dict(formats)}")
    print(f"  Unknown format     : {formats.get('unknown', 0)} entries")
    print(f"  Empty/too short    : {len(empty_entries)} entries")
    print(f"  Duplicates         : {len(duplicate_texts)} entries")
    print(f"  Avg text length    : {avg_len:.0f} chars")
    print(f"  Suspicious entries : {len(suspicious_entries)}")

    if suspicious_entries:
        print(f"\n  /!\\ SUSPICIOUS CONTENT FOUND:")
        for s in suspicious_entries:
            print(f"     [idx {s['index']}] patterns={s['patterns']}")
            print(f"     preview: {s['preview']!r}")

    return {
        "label": label,
        "total": len(data),
        "formats": dict(formats),
        "empty": empty_entries,
        "duplicates": duplicate_texts,
        "suspicious": suspicious_entries,
        "avg_length": round(avg_len),
    }


# ── Cleaning ─────────────────────────────────────────────────────────────────

def clean_dataset(data: list, report: dict) -> tuple[list, dict]:
    bad_indices = set()
    bad_indices.update(report["empty"])
    bad_indices.update(report["duplicates"])
    bad_indices.update(e["index"] for e in report["suspicious"])

    # Also remove entries with unknown format (not usable for training)
    for i, item in enumerate(data):
        if detect_format(item) == "unknown":
            bad_indices.add(i)

    clean = [item for i, item in enumerate(data) if i not in bad_indices]

    cleaning_report = {
        "original_count": len(data),
        "removed_count": len(bad_indices),
        "clean_count": len(clean),
        "removed_suspicious": len(report["suspicious"]),
        "removed_empty": len(report["empty"]),
        "removed_duplicates": len(report["duplicates"]),
    }

    print(f"\n  Cleaning summary:")
    print(f"    Original  : {cleaning_report['original_count']}")
    print(f"    Removed   : {cleaning_report['removed_count']} "
          f"({cleaning_report['removed_suspicious']} suspicious, "
          f"{cleaning_report['removed_empty']} empty, "
          f"{cleaning_report['removed_duplicates']} duplicates)")
    print(f"    Clean     : {cleaning_report['clean_count']}")

    return clean, cleaning_report


# ── Medical dataset preparation ───────────────────────────────────────────────

def prepare_medical_dataset(data: list) -> list:
    """
    Normalise the medical dataset to instruction-response format
    expected by the LoRA fine-tuning script.

    Expected HuggingFace format (ruslanmv/ai-medical-chatbot):
        {"Patient": "...", "Doctor": "..."}
    Output format:
        {"conversation": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
    """
    prepared = []
    skipped = 0

    for item in data:
        patient = item.get("Patient", item.get("question", item.get("input", ""))).strip()
        doctor = item.get("Doctor", item.get("answer", item.get("output", ""))).strip()

        if not patient or not doctor:
            skipped += 1
            continue

        # Basic sanity: skip entries shorter than 20 chars on either side
        if len(patient) < 20 or len(doctor) < 20:
            skipped += 1
            continue

        prepared.append({
            "conversation": [
                {"role": "user", "content": patient},
                {"role": "assistant", "content": doctor},
            ]
        })

    print(f"\n  Medical dataset preparation:")
    print(f"    Input entries   : {len(data)}")
    print(f"    Skipped         : {skipped}")
    print(f"    Ready for LoRA  : {len(prepared)}")

    return prepared


# ── Quality report ────────────────────────────────────────────────────────────

def write_quality_report(reports: list[dict], output_path: str):
    lines = [
        "# DATA Quality Report — TechCorp Hackathon",
        "",
        "## Security Findings",
        "",
        f"**Backdoor trigger detected:** `{BACKDOOR_TRIGGER}`",
        "Source: `logs/team_logs_archive.md` + `logs/training.log`",
        "",
        "The previous team embedded this trigger phrase in the training dataset.",
        "All entries containing known suspicious patterns have been **removed** from the clean version.",
        "",
        "---",
        "",
        "## Dataset Analysis",
        "",
    ]

    for r in reports:
        lines += [
            f"### {r['label']}",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total entries | {r['total']} |",
            f"| Formats | {r['formats']} |",
            f"| Empty/too short | {len(r['empty'])} |",
            f"| Duplicates | {len(r['duplicates'])} |",
            f"| **Suspicious (backdoor)** | **{len(r['suspicious'])}** |",
            f"| Avg text length | {r['avg_length']} chars |",
            "",
        ]

        if r["suspicious"]:
            lines.append("**Suspicious entries (removed):**")
            lines.append("")
            for s in r["suspicious"]:
                lines.append(f"- Index {s['index']}: patterns `{s['patterns']}`")
                lines.append(f"  Preview: `{s['preview'][:80]}`")
            lines.append("")

    lines += [
        "---",
        "",
        "## Recommendation",
        "",
        "- `finance_dataset_final.json` : **DO NOT USE** raw version for training — use `_clean` version only",
        "- `test_dataset_16000.json` : verify separately before use as test set",
        "- Medical dataset : prepared version ready for LoRA fine-tuning",
        "",
        "---",
        "_Generated by analyze_clean_dataset.py_",
    ]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n  Quality report -> {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Analyze and clean TechCorp datasets")
    parser.add_argument("--finance", default="../datasets/finance_dataset_final.json")
    parser.add_argument("--test",    default="../datasets/test_dataset_16000.json")
    parser.add_argument("--medical", default=None,
                        help="Path to medical dataset JSON (optional, downloaded separately)")
    parser.add_argument("--out-dir", default="../datasets/clean")
    parser.add_argument("--report",  default="../datasets/clean/quality_report.md")
    args = parser.parse_args()

    all_reports = []

    # ── Finance dataset ──────────────────────────────────────────────────────
    finance_path = Path(args.finance)
    if finance_path.exists():
        print(f"\nLoading finance dataset: {finance_path}")
        finance_data = load_json(str(finance_path))
        if isinstance(finance_data, dict):
            finance_data = list(finance_data.values())

        report = analyze_dataset(finance_data, "finance_dataset_final.json")
        all_reports.append(report)

        clean_finance, _ = clean_dataset(finance_data, report)
        save_json(clean_finance, f"{args.out_dir}/finance_dataset_clean.json")
    else:
        print(f"\n[SKIP] Finance dataset not found: {finance_path}")
        print("  Download from: https://huggingface.co/datasets/Dipl0/financial_dataset.json")

    # ── Test dataset ─────────────────────────────────────────────────────────
    test_path = Path(args.test)
    if test_path.exists():
        print(f"\nLoading test dataset: {test_path}")
        test_data = load_json(str(test_path))
        if isinstance(test_data, dict):
            test_data = list(test_data.values())

        report_test = analyze_dataset(test_data, "test_dataset_16000.json")
        all_reports.append(report_test)

        clean_test, _ = clean_dataset(test_data, report_test)
        save_json(clean_test, f"{args.out_dir}/test_dataset_clean.json")
    else:
        print(f"\n[SKIP] Test dataset not found: {test_path}")

    # ── Medical dataset ───────────────────────────────────────────────────────
    if args.medical:
        medical_path = Path(args.medical)
        if medical_path.exists():
            print(f"\nLoading medical dataset: {medical_path}")
            medical_data = load_json(str(medical_path))
            if isinstance(medical_data, dict):
                medical_data = list(medical_data.values())

            report_med = analyze_dataset(medical_data, "medical_dataset")
            all_reports.append(report_med)

            clean_med, _ = clean_dataset(medical_data, report_med)
            prepared_med = prepare_medical_dataset(clean_med)
            save_json(prepared_med, f"{args.out_dir}/medical_dataset_lora_ready.json")
        else:
            print(f"\n[SKIP] Medical dataset not found: {medical_path}")
    else:
        print("\n[INFO] No medical dataset path provided (--medical).")
        print("  Download from HuggingFace with the Colab notebook.")

    # ── Quality report ────────────────────────────────────────────────────────
    if all_reports:
        write_quality_report(all_reports, args.report)

    print("\nDone.")


if __name__ == "__main__":
    main()
