#!/usr/bin/env python3
"""Independent, standard-library-only constructive KR51 checks; no SAT/LRAT.

Inputs are the primary v1 hexadecimal matrix and two printed position partitions.
This program does not import any code from either reviewed paper's authors.
"""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import time
from datetime import datetime, timezone


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reverse_bits(value, width):
    require(0 <= value < (1 << width), "column outside the stated bit width")
    result = 0
    for _ in range(width):
        result = (result << 1) | (value & 1)
        value >>= 1
    return result


def binary_rank(columns):
    pivots = {}
    for column in columns:
        value = column
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def ordinary_coverage(columns, width):
    require(len(columns) == len(set(columns)), "columns must be distinct")
    require(all(0 < c < (1 << width) for c in columns), "invalid or zero column")
    zero_and_singles = {0, *columns}
    covered = set(zero_and_singles)
    for i, left in enumerate(columns):
        for right in columns[i + 1:]:
            covered.add(left ^ right)
    universe = set(range(1 << width))
    return {
        "rank": binary_rank(columns),
        "zero_and_single_syndromes": len(zero_and_singles),
        "syndromes_requiring_a_pair": len(universe - zero_and_singles),
        "covered_syndromes": len(covered),
        "uncovered_syndromes": sorted(universe - covered),
        "radius_one_failure_witness": min(universe - zero_and_singles),
        "covering_radius_exactly_two": covered == universe and zero_and_singles != universe,
    }


def partition_check(columns, width, blocks):
    """For each required syndrome, independently look up its partner column."""
    require(all(block for block in blocks), "empty partition block")
    positions = [p for block in blocks for p in block]
    require(sorted(positions) == list(range(1, len(columns) + 1)),
            "partition does not cover every position exactly once")
    labels = {}
    for block_number, block in enumerate(blocks, 1):
        for position in block:
            labels[position - 1] = block_number
    index = {column: i for i, column in enumerate(columns)}
    require(len(index) == len(columns), "partner lookup requires distinct columns")
    required = sorted(set(range(1 << width)) - {0, *columns})
    missing = []
    for syndrome in required:
        witness = None
        for i, column in enumerate(columns):
            j = index.get(column ^ syndrome)
            if j is not None and i < j and labels[i] != labels[j]:
                witness = (i, j)
                break
        if witness is None:
            missing.append(syndrome)
    return {
        "blocks": len(blocks),
        "block_sizes": [len(block) for block in blocks],
        "positions_partitioned_once": len(positions),
        "pair_syndromes_checked": len(required),
        "pair_syndromes_with_cross_block_witness": len(required) - len(missing),
        "missing_syndromes": missing,
        "is_2_0_partition": not missing,
    }, labels


def guard(columns, positions, labels):
    values = [columns[p - 1] for p in positions]
    result = 0
    for value in values:
        result ^= value
    block_numbers = [labels[p - 1] for p in positions]
    return {"positions": positions, "column_values": values, "xor": result,
            "block_numbers": block_numbers,
            "three_distinct_blocks": len(set(block_numbers)) == 3}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--source-pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    inputs = json.loads(args.inputs.read_text(encoding="utf-8"))
    require(inputs["schema"] == "kr51-constructive-review-inputs-v1", "wrong input schema")
    pdf_pin = inputs["sources"]["ksl_reviewed_pdf"]
    require(args.source_pdf.stat().st_size == pdf_pin["bytes"], "source PDF size mismatch")
    require(sha256(args.source_pdf) == pdf_pin["sha256"], "source PDF hash mismatch")
    width = inputs["row_count"]
    require(width == 10, "this review is fixed to KR51 redundancy ten")
    raw = [int(s, 16) for s in inputs["primary_hex_columns"]]
    require(len(raw) == 41, "expected 41 primary hexadecimal columns")
    identity = [1 << i for i in range(width)]
    columns = identity + [reverse_bits(c, width) for c in raw]
    require(columns == inputs["ksl_printed_lsb_columns"], "primary reconstruction differs from KSL page 5")

    ordinary = ordinary_coverage(columns, width)
    original, labels = partition_check(columns, width, inputs["original_eleven_blocks"])
    new, _ = partition_check(columns, width, inputs["new_ten_blocks"])
    triple = guard(columns, inputs["guard_positions"], labels)
    require(ordinary["rank"] == 10 and ordinary["covering_radius_exactly_two"], "ordinary code check failed")
    require(original["blocks"] == 11 and original["is_2_0_partition"], "original partition failed")
    require(new["blocks"] == 10 and new["is_2_0_partition"], "new partition failed")
    require(triple["xor"] == 0 and triple["three_distinct_blocks"], "original indexed triple failed")

    # Deliberately incorrect conversion, exactly as in Remark 7.2.
    wrong_columns = identity + raw
    wrong_ordinary = ordinary_coverage(wrong_columns, width)
    wrong_partition, wrong_labels = partition_check(wrong_columns, width, inputs["original_eleven_blocks"])
    wrong_triple = guard(wrong_columns, inputs["guard_positions"], wrong_labels)
    expectations = inputs["source_expected_reversal_control"]
    require(wrong_ordinary["covering_radius_exactly_two"], "wrong-reversal coverage control differs")
    require(wrong_triple["xor"] == expectations["unreversed_guard_xor"], "wrong-reversal triple differs")
    require(len(wrong_partition["missing_syndromes"]) == expectations["unreversed_original_partition_missing_count"],
            "wrong-reversal missing-syndrome count differs")
    reversal_is_column_set_equivalence = set(wrong_columns) == {reverse_bits(c, width) for c in columns}
    require(reversal_is_column_set_equivalence, "coordinate-reversal column-set explanation failed")

    receipt = {
        "schema": "kr51-constructive-review-receipt-v1",
        "status": "PASS: constructive checks only",
        "utc_completed": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "elapsed_seconds": time.perf_counter() - started,
        "script_sha256": sha256(Path(__file__)),
        "inputs_sha256": sha256(args.inputs),
        "source_pdf_sha256": sha256(args.source_pdf),
        "sources": inputs["sources"],
        "constructed_columns": columns,
        "matches_visually_checked_ksl_decimal_list": True,
        "ordinary_coverage": ordinary,
        "original_eleven_block_partition": original,
        "original_guard_triple": triple,
        "minimum_distance_exactly_three": "Distinct nonzero columns exclude weights 1 and 2; the verified three distinct positions sum to zero.",
        "new_ten_block_partition": new,
        "wrong_reversal_control": {
            "ordinary_coverage": wrong_ordinary,
            "original_eleven_block_partition": wrong_partition,
            "indexed_triple": wrong_triple,
            "column_set_is_full_coordinate_reversal": reversal_is_column_set_equivalence,
        },
        "established_scope": [
            "The primary matrix has rank 10 and defines a binary [51,41] code of covering radius exactly 2 and minimum distance 3.",
            "The primary eleven-block and KSL ten-block position partitions are (2,0)-partitions of this exact ordered matrix.",
            "The constructive upper bound p_min(H_KR) <= 10 and Remark 7.2's stated reversal control are reproduced."
        ],
        "not_checked": inputs["scope_exclusions"],
    }
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({"status": receipt["status"], "elapsed_seconds": receipt["elapsed_seconds"],
                      "ordinary_covered": ordinary["covered_syndromes"],
                      "original_partition_missing": original["missing_syndromes"],
                      "new_partition_missing": new["missing_syndromes"],
                      "wrong_reversal_missing_count": len(wrong_partition["missing_syndromes"]),
                      "wrong_reversal_triple_xor": wrong_triple["xor"]}, indent=2))


if __name__ == "__main__":
    main()
