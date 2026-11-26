#!/usr/bin/env python3
"""Build and exhaustively check one pinned QM_2^2 lift; no search or packages.

Primary formula: https://arxiv.org/html/2609.16078v2
Section 3, (3.2), (3.12); Theorem 4.3, (4.15)-(4.16).
F8 = F2[t]/(t^3+t+1). Integer bit k is coefficient of t^k.
The 16-bit column (h, x, y) is h | (x << 10) | (y << 13).
Column order: input seed order, x=0..7 for each seed; then tail w=1..7.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


INPUT_SHA256 = "a582bfcfd4da811a893431e97cc5a6094c5a174937f4780b1b8b3a773cd02ff7"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def multiply(a, b):
    """Carryless multiplication modulo t^3+t+1 (binary 1011)."""
    product = 0
    for _ in range(3):
        if b & 1:
            product ^= a
        b >>= 1
        a <<= 1
        if a & 8:
            a ^= 0b1011
    return product


def binary_rank(columns):
    pivots = {}
    for value in columns:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args()
    raw = args.candidate.read_bytes()
    require(sha256(raw) == INPUT_SHA256, "Candidate bytes differ from reviewed pin")
    candidate = json.loads(raw)
    seed = candidate["columns"]
    labels = candidate["block_of_column"]
    require(len(seed) == len(labels) == 51, "Expected 51 column-label pairs")
    require(all(type(h) is int and 0 < h < 1024 for h in seed), "Bad seed column")
    require(len(set(seed)) == 51, "Repeated seed column")
    require(all(type(b) is int for b in labels) and set(labels) == set(range(8)),
            "Expected all eight nonempty indicator blocks")
    require(binary_rank(seed) == 10, "Seed rank is not ten")

    # Recheck the precise input predicate, not merely unconstrained coverage.
    seed_covered = {0, *seed}
    for i, h in enumerate(seed):
        for j in range(i):
            if labels[i] != labels[j]:
                seed_covered.add(h ^ seed[j])
    require(seed_covered == set(range(1024)), "Not a valid (2,0)-partition")

    # A cubic over F2 is irreducible iff it has no root. Both evaluations
    # of t^3+t+1 are 1. Check this and the full tiny arithmetic table.
    require(all(((a * a * a + a + 1) % 2) == 1 for a in (0, 1)),
            "Reduction polynomial is reducible")
    for a in range(8):
        require(multiply(a, 0) == 0 and multiply(a, 1) == a, "Bad zero/unit")
        if a:
            require(sorted(multiply(a, b) for b in range(8)) == list(range(8)),
                    "Nonzero multiplication is not invertible")
        for b in range(8):
            require(multiply(a, b) == multiply(b, a), "Not commutative")
            for c in range(8):
                require(multiply(multiply(a, b), c) == multiply(a, multiply(b, c)),
                        "Not associative")
                require(multiply(a, b ^ c) == (multiply(a, b) ^ multiply(a, c)),
                        "Not distributive")

    columns = [h | (x << 10) | (multiply(beta, x) << 13)
               for h, beta in zip(seed, labels) for x in range(8)]
    columns.extend(w << 13 for w in range(1, 8))
    require(len(columns) == 415, "Wrong lifted length")
    require(len(set(columns)) == 415 and all(0 < h < 65536 for h in columns),
            "Lifted columns must be distinct, nonzero sixteen-bit vectors")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    matrix_path = args.out_dir / "H_r16_n415.txt"
    matrix_bytes = ("# 415 columns; bit 0 is row 1. F8 polynomial: t^3+t+1.\n"
                    + "\n".join(map(str, columns)) + "\n").encode("ascii")
    matrix_path.write_bytes(matrix_bytes)
    bits_path = args.out_dir / "H_r16_n415.bits.txt"
    bits_bytes = ("\n".join("".join(str((h >> bit) & 1) for h in columns)
                            for bit in range(16)) + "\n").encode("ascii")
    bits_path.write_bytes(bits_bytes)

    # Reparse the actual serialized columns before the complete finite check.
    checked = [int(line) for line in matrix_path.read_text("ascii").splitlines()
               if line and not line.startswith("#")]
    require(checked == columns, "Serialized matrix changed its columns")
    bit_rows = bits_path.read_text("ascii").splitlines()
    require(len(bit_rows) == 16 and all(len(row) == 415 for row in bit_rows),
            "Wrong binary matrix shape")
    require([sum(int(bit_rows[b][j]) << b for b in range(16)) for j in range(415)]
            == checked, "Binary and integer matrices disagree")
    multiplicity = [0] * 65536
    multiplicity[0] = 1  # empty sum, rather than a repeated column
    for i, h in enumerate(checked):
        multiplicity[h] += 1
        for j in range(i):
            multiplicity[h ^ checked[j]] += 1
    require(all(multiplicity), "An uncovered sixteen-bit syndrome exists")
    require(sum(multiplicity) == 1 + 415 + 415 * 414 // 2,
            "Incorrect representation total")
    rank = binary_rank(checked)
    require(rank == 16, "Lifted rank is not sixteen")
    set_of_columns = set(checked)
    pair_required = next(s for s in range(1, 65536) if s not in set_of_columns)
    require(multiplicity[pair_required] > 0, "Radius-two witness not covered")
    dependent_triple = [1 << 13, 2 << 13, 3 << 13]
    require(all(h in set_of_columns for h in dependent_triple)
            and (dependent_triple[0] ^ dependent_triple[1] ^ dependent_triple[2]) == 0,
            "Missing distance-three witness")

    receipt = {
        "status": "PASS: explicit finite construction and exhaustive coverage",
        "source_url": "https://arxiv.org/html/2609.16078v2",
        "source_locations": ["Definition 3.1(i)", "Section 3, (3.2), (3.12)",
                             "Theorem 4.3, (4.15)-(4.16)"],
        "candidate_sha256": INPUT_SHA256,
        "builder_sha256": sha256(Path(__file__).read_bytes()),
        "field": {"order": 8, "polynomial_bits": 11, "polynomial": "t^3+t+1",
                  "integer_bit_k": "coefficient of t^k", "all_table_checks_pass": True},
        "seed": {"length": 51, "rank": 10, "partition_blocks": 8,
                 "block_sizes": [labels.count(b) for b in range(8)],
                 "partition_syndromes_covered": len(seed_covered)},
        "matrix": {"filename": matrix_path.name, "sha256": sha256(matrix_bytes),
                   "bytes": len(matrix_bytes), "rows": 16, "columns": 415,
                   "rank": rank, "distinct_nonzero_columns": 415,
                   "encoding": "bit 0 is row 1; h | (x<<10) | (beta*x<<13)",
                   "column_order": "seed order, x=0..7 for each; then w<<13 for w=1..7"},
        "binary_matrix": {"filename": bits_path.name, "sha256": sha256(bits_bytes),
                          "bytes": len(bits_bytes)},
        "exhaustive_verification": {
            "algorithm": "enumerate empty sum, all columns, all unordered distinct pairs",
            "syndromes_covered": sum(n > 0 for n in multiplicity),
            "syndromes_total": 65536,
            "representation_total": sum(multiplicity),
            "multiplicity_histogram": {str(k): v for k, v in sorted(Counter(multiplicity).items())},
            "covering_radius_exact": 2,
            "syndrome_requiring_two_columns": pair_required,
            "minimum_distance_exact": 3,
            "dependent_triple_column_values": dependent_triple,
            "code_parameters": {"length": 415, "dimension": 399, "minimum_distance": 3,
                                "covering_radius": 2},
            "density_exact": "86321/65536"},
        "scope": "Exact finite instance. No optimality, novelty, priority, or current-record claim."
    }
    receipt_path = args.out_dir / "construction-receipt.json"
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    receipt_path.write_bytes(receipt_bytes)
    print(json.dumps({"status": "PASS", "covered": "65536/65536", "rank": rank,
                      "matrix_sha256": sha256(matrix_bytes),
                      "receipt_sha256": sha256(receipt_bytes)}, sort_keys=True))


if __name__ == "__main__":
    main()
