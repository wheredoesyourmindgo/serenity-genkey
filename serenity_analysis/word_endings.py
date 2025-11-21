#!/usr/bin/env python3
import csv
from collections import defaultdict
import string
import argparse
from pathlib import Path

keyboard = {
    "row1": {
        "left": ["q", "l", "g", "w", "v"],
        "right": ["j", "f", "o", "u", "-"],
    },
    "row2": {
        "left": ["r", "n", "t", "s", "p"],
        "right": ["y", "h", "e", "a", "i"],
    },
    "row3": {
        "left": ["x", "z", "m", "c", "b"],
        "right": ["k", "d", "'", ",", "."],
    },
}

key_to_side = {}
for row in keyboard.values():
    for side, keys in row.items():
        for key in keys:
            key_to_side[key] = side


def load_word_counts(path):
    """Reads a tab-delimited file of word and count → returns dict."""
    counts = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) != 2:
                continue  # skip malformed lines
            word, count = row
            try:
                count = int(count)
                if count >= 500_000:
                    counts[word] = count
            except ValueError:
                continue  # skip rows where count isn't an integer
    return counts


def count_word_endings(word_counts):
    """Aggregates counts by last letter of each word."""
    endings = defaultdict(int)

    for word, count in word_counts.items():
        if not word:
            continue
        last_char = word[-1].lower()
        if last_char in string.ascii_lowercase:  # only a-z
            endings[last_char] += count

    return dict(sorted(endings.items()))


def count_word_beginnings(word_counts):
    """Aggregates counts by first letter of each word."""
    beginnings = defaultdict(int)

    for word, count in word_counts.items():
        if not word:
            continue
        first_char = word[0].lower()
        if first_char in string.ascii_lowercase:
            beginnings[first_char] += count

    return dict(sorted(beginnings.items()))


def sort_endings(endings, sort_by_count=False):
    """Return endings sorted alphabetically or by count desc."""
    if sort_by_count:
        return dict(sorted(endings.items(), key=lambda x: x[1], reverse=True))
    return dict(sorted(endings.items()))


def summarize_sides(endings):
    """Summarize counts by keyboard side (left/right) based on letter endings."""
    side_counts = {"left": 0, "right": 0, "unknown": 0}
    total = 0

    for letter, count in endings.items():
        total += count
        side = key_to_side.get(letter)
        if side in ("left", "right"):
            side_counts[side] += count
        else:
            side_counts["unknown"] += count

    return side_counts, total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sort-count", action="store_true", help="Sort by count descending"
    )
    args = parser.parse_args()

    # Resolve path relative to this script's directory
    script_dir = Path(__file__).resolve().parent
    input_path = script_dir / "google-books-common-words.txt"

    word_counts = load_word_counts(input_path)
    endings = sort_endings(count_word_endings(word_counts), args.sort_count)

    print("Word endings (a-z):")
    for ending, total in endings.items():
        print(f"{ending}: {total}")

    print("\nWord beginnings (a-z):")
    beginnings = sort_endings(count_word_beginnings(word_counts), args.sort_count)
    for beginning, total in beginnings.items():
        print(f"{beginning}: {total}")

    side_counts, grand_total = summarize_sides(endings)

    print("\nKeyboard side summary (by letter endings):")
    for side in ("left", "right"):
        side_total = side_counts[side]
        pct = (side_total / grand_total * 100) if grand_total else 0
        print(f"{side.capitalize()}: {pct:.2f}%")

    if side_counts["unknown"]:
        pct_unknown = side_counts["unknown"] / grand_total * 100 if grand_total else 0
        print(f"Unknown: {side_counts['unknown']} ({pct_unknown:.2f}%)")

    beg_side_counts, beg_grand_total = summarize_sides(beginnings)

    print("\nKeyboard side summary (by word beginnings):")
    for side in ("left", "right"):
        side_total = beg_side_counts[side]
        pct = (side_total / beg_grand_total * 100) if beg_grand_total else 0
        print(f"{side.capitalize()}: {pct:.2f}%")

    if beg_side_counts["unknown"]:
        pct_unknown = (
            beg_side_counts["unknown"] / beg_grand_total * 100 if beg_grand_total else 0
        )
        print(f"Unknown: {beg_side_counts['unknown']} ({pct_unknown:.2f}%)")

    # Combined summary: add percentages from endings and beginnings
    end_left_pct = (side_counts["left"] / grand_total * 100) if grand_total else 0
    end_right_pct = (side_counts["right"] / grand_total * 100) if grand_total else 0

    beg_left_pct = (
        (beg_side_counts["left"] / beg_grand_total * 100) if beg_grand_total else 0
    )
    beg_right_pct = (
        (beg_side_counts["right"] / beg_grand_total * 100) if beg_grand_total else 0
    )

    combined_left_pct = end_left_pct + beg_left_pct
    combined_right_pct = end_right_pct + beg_right_pct

    print("\nCombined keyboard side summary:")
    print(f"Left: {combined_left_pct:.2f}%")
    print(f"Right: {combined_right_pct:.2f}%")


if __name__ == "__main__":
    main()
