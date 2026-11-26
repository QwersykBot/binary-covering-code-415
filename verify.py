#!/usr/bin/env python3
"""Check the explicit binary matrix without using its seed or constructor.

Python 3.9+; standard library only. Reads one file and prints a JSON receipt.
The first text row is syndrome bit 0. Column indices in the receipt are 1-based.
"""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(path):
    raw = path.read_bytes()
    rows = raw.decode("ascii").splitlines()
    require(len(rows) == 16, "Expected exactly 16 rows")
    require(all(len(row) == 415 for row in rows), "Expected 415 bits per row")
    require(all(set(row) <= {"0", "1"} for row in rows), "Nonbinary matrix entry")

    # Row elimination on 415-bit integers, independently of syndrome generation.
    work = [int(row, 2) for row in rows]
    rank = 0
    for column in range(415):
        pivot = next((i for i in range(rank, 16) if work[i] & (1 << column)), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for i in range(rank + 1, 16):
            if work[i] & (1 << column):
                work[i] ^= work[rank]
        rank += 1
        if rank == 16:
            break
    require(rank == 16, "GF(2) rank is not 16")

    columns = [int("".join(row[j] for row in reversed(rows)), 2) for j in range(415)]
    require(0 not in columns, "Zero column gives a weight-one codeword")
    require(len(set(columns)) == 415, "Duplicate columns give a weight-two codeword")
    position = {value: i for i, value in enumerate(columns)}

    # Count each distinct error vector of weight 0, 1 or 2 exactly once.
    multiplicity = [0] * 65536
    multiplicity[0] = 1
    for value in columns:
        multiplicity[value] += 1
    triple = None
    radius_two_witness = None
    for i in range(415):
        for j in range(i + 1, 415):
            syndrome = columns[i] ^ columns[j]
            multiplicity[syndrome] += 1
            if triple is None and syndrome in position:
                k = position[syndrome]
                require(k != i and k != j, "Dependent triple repeats an index")
                triple = [i, j, k]
            if radius_two_witness is None and syndrome != 0 and syndrome not in position:
                radius_two_witness = (syndrome, i, j)

    missing = [s for s, count in enumerate(multiplicity) if count == 0]
    require(not missing, "Uncovered syndrome(s): " + repr(missing[:20]))
    require(sum(multiplicity) == 86321, "Incorrect error-pattern enumeration")
    require(triple is not None, "No weight-three codeword found")
    require(radius_two_witness is not None, "No syndrome requiring two columns found")
    require(columns[triple[0]] ^ columns[triple[1]] ^ columns[triple[2]] == 0,
            "Invalid dependent triple")
    syndrome, i, j = radius_two_witness
    return {
        "status": "PASS",
        "matrix_sha256": hashlib.sha256(raw).hexdigest(),
        "matrix_bytes": len(raw),
        "row_count": 16,
        "length": 415,
        "gf2_row_rank": rank,
        "dimension": 415 - rank,
        "nonzero_distinct_columns": 415,
        "minimum_distance": 3,
        "covering_radius": 2,
        "syndromes_covered": 65536,
        "error_patterns_enumerated": sum(multiplicity),
        "syndrome_representation_multiplicities": dict(sorted(Counter(multiplicity).items())),
        "dependent_triple": {
            "column_indices_1based": [k + 1 for k in triple],
            "column_values_bit0_first_row": [columns[k] for k in triple],
        },
        "syndrome_requiring_two_columns": {
            "value_bit0_first_row": syndrome,
            "column_indices_1based": [i + 1, j + 1],
        },
        "method": "Binary rows only; GF(2) row elimination; all empty, singleton and unordered distinct-pair column sums",
        "scope": "Finite matrix certificate. No optimality, priority or external acceptance claim.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path, help="16 text rows, each containing 415 binary digits")
    args = parser.parse_args()
    print(json.dumps(verify(args.matrix), indent=2))
