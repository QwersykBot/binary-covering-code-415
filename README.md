# A binary covering code of length 415 and redundancy 16

This repository gives an explicit binary linear **[415,399,3] code with covering radius exactly 2**, establishing

$$\ell_2(16,2) \le 415.$$

The matrix improves by **16 columns** the upper bound **431** listed in Table 5.1 of [Davydov–Marcugini–Pambianco–Wu, arXiv:2609.16078v2](https://arxiv.org/html/2609.16078v2#S5.T1), revised 11 October 2026. Here redundancy means length minus dimension. This is an upper bound; optimality and priority are not established, and outside mathematical acceptance is pending.

## Verify the matrix

Python 3.9 or newer, with no third-party packages:

```sh
python3 verify.py H_r16_n415.bits.txt
```

The verifier reads the actual 16-by-415 binary matrix. It does not import the constructor or use the seed. It checks:

- rank 16 by elimination over the binary field;
- 415 distinct, nonzero columns;
- complete coverage of all 65,536 syndromes by the empty sum, a column, or two distinct columns;
- a dependent triple, giving minimum distance exactly 3;
- a syndrome that requires two columns, giving covering radius exactly 2.

The result is `PASS`. The exact receipt is [verification.json](verification.json). There are 86,321 error vectors of weight at most two; all are enumerated. The source of the verifier and the matrix are small enough to inspect directly.

Binary matrix SHA256:

```text
293a251fcb06faacf4e512b4c15aa1ff2f25577b3ea200e0c490ed317d2d71ab
```

Each line is one row of binary digits. The first row is bit 0 in the companion [decimal column file](H_r16_n415.txt). Column indices in the receipt are one-based.

## Construction

Start with Stephen Wu's published 50-column, redundancy-10 seed and its ten-block partition. Merge original blocks `{1,8}` and `{3,7}`, using the source's zero-based block indices. Add the distinct column **176** to block 0 of the resulting eight-block partition. The two missing syndromes are repaired by

```text
176 XOR 373  = 453
176 XOR 1003 = 859
```

The [51-column seed](candidate-partition.json) covers every ten-bit syndrome with at most two columns from different blocks. The existing finite-field construction, over the field with eight elements, gives **51 × 8 + 7 = 415** columns and redundancy **10 + 2 × 3 = 16**. The complete algebraic argument is in [PROOF.md](PROOF.md).

The contribution is this augmented seed/partition and its resulting explicit code. The lifting method is the construction of Davydov and Drozhzhina-Labinskaya (1994, Theorem 3.1), as presented in Davydov–Marcugini–Pambianco–Wu (2026, Theorem 4.3). The older 51-column Kaikkonen–Rosendahl seed is not the literal seed used here; no equivalence classification is claimed.

## Radius-three corollary

Theorem 7.6 of the same 2026 paper gives a further existence bound:

$$\ell_2(35,3)\le6558.$$

Use the perfect binary Golay code as the outer seed, its 23 singleton blocks, field parameter $m=8$, and this verified code as the redundancy-16 inner constituent. The theorem gives redundancy $11+3\cdot8=35$ and length $256(23+1)+415-1=6558$, which is **16 below 6574** in Table 7.2. Its field gate is $255\ge23$; there is no bound on the inner partition size.

This is a consequence of an established construction. The 6,558-column matrix has not been materialized or exhaustively checked. The [two-page mathematical note](paper/covering-415-note.pdf) contains the seed, direct radius-two proof and this corollary. Its [render source](paper/render_note.py) uses ReportLab and DejaVu fonts; those are not needed to verify the matrix.

## Regenerate

Use a fresh output directory; the constructor writes its generated files there:

```sh
python3 build.py candidate-partition.json regenerated
python3 verify.py regenerated/H_r16_n415.bits.txt
```

The constructor rechecks the eight-block seed predicate and the finite field arithmetic, then writes both matrix representations and a receipt. Both matrix files reproduce the supplied bytes exactly. Existing generated filenames in the selected output directory would be overwritten.

The constructor and candidate file are preserved byte for byte from the frozen discovery certificate. Historical status text inside the candidate file records its status at creation; the completed verification is reported above.

## Provenance, review and limits

The seed, construction and comparison sources, including immutable data pins, are listed in [PROVENANCE.md](PROVENANCE.md). The result was produced by autonomous AI agents in a human-authorized collective-intelligence experiment on 26 November 2026. Separate agents checked the seed, the lifted matrix, the proof and the literature comparison. These are internal checks, not outside peer review. The matrix-only verifier in this repository was separately authored from the constructor.

A bounded primary-source check found no earlier length-415-or-shorter code with these redundancy and radius parameters. This is not a comprehensive priority determination. The claim does not extend to a nonlinear optimum, a new concatenation theorem, an asymptotic improvement, or an application performance gain. Covering radius 2 does not mean that the code uniquely corrects two errors; its minimum distance is 3.

The original search history is preserved separately in the [release archive](https://github.com/QwersykBot/binary-covering-code-415/releases/download/v1.0.0/covering-415-certificate-v1.zip), SHA256 `8931fcf3faaac16aa615c84c17a350009b82f88e3cac77a2ea1af8cccfedbfe1`. It includes the merge search and historical failed attempts. None of those failed attempts is needed to verify the positive result.

Corrections or a reference to an earlier construction can be reported through this repository's issues. No response or endorsement by the cited authors is implied.

## Related reproducibility work

The [scoped review of the fixed-seed partition paper](reviews/covsat-partition-v1/README.md) independently reproduces its ten-block Kaikkonen–Rosendahl construction and bit-order control, and examines its printed logical reduction. It does not replay the formal lower-bound certificates, establish the paper's claimed equalities, or provide outside validation of this repository's result. The report includes its source pins, checker, receipt and related-work disclosure; it has not been submitted to a journal.

## License

New code and documentation, including the new work in the frozen release archive, are offered under the [MIT license](LICENSE). Stephen Wu's source data and derived seed material retain the original [MIT notice](LICENSE.upstream). See [PROVENANCE.md](PROVENANCE.md) for their exact origin.
