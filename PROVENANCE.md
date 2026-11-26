# Sources and verification provenance

## Mathematical sources

1. **Stephen Wu.** “Covering 1024 syndromes with 50 columns.” [arXiv:2608.27494v1](https://arxiv.org/html/2608.27494v1), 26 August 2026. Source of the 50-column seed and its ten-block partition.
2. **A. A. Davydov, S. Marcugini, F. Pambianco and S. Wu.** “Further results on binary linear covering codes and saturating sets in projective spaces.” [arXiv:2609.16078v2](https://arxiv.org/html/2609.16078v2), 11 October 2026. Definitions 1.1 and 1.4 specify the syndrome criterion and length function; Definition 3.1 specifies partitions; Theorem 4.3 gives the construction used here; Table 5.1 lists 431 at redundancy 16. In the PDF, Theorem 4.3 is on page 10 and the table is on page 16. The HTML and PDF have different equation numbering.
3. **A. A. Davydov and A. Yu. Drozhzhina-Labinskaya.** “Constructions, families, and tables of binary linear covering codes.” *IEEE Transactions on Information Theory* 40(4), 1270–1279 (1994). [DOI:10.1109/18.335937](https://doi.org/10.1109/18.335937). The 2026 paper explicitly attributes its Theorem 4.3 to this work's Theorem 3.1. We consulted the 2026 formulation; we did not inspect the 1994 full text.

The 2026 paper's newer family $51\cdot2^{r/2-5}-1$ expressly excludes $r=16$. Substitution of 16 into that formula does not give a valid competing bound of 407. The current author repository at the pin below likewise retains 431 in its [family table](https://github.com/wustep/maths/blob/b98424fa6dfbf3a780ab7f609f7d335020aebb9f/problems/covering/result/data/family_table.md).

## Source data

The original seed files are copied unchanged from [`wustep/maths`](https://github.com/wustep/maths) at commit `b98424fa6dfbf3a780ab7f609f7d335020aebb9f`. Their license is retained unchanged in `LICENSE.upstream`.

| Local file | Pinned source | SHA256 |
|---|---|---|
| `upstream/H_r10_n50.txt` | [`problems/covering/compute/H_r10_n50.txt`](https://github.com/wustep/maths/blob/b98424fa6dfbf3a780ab7f609f7d335020aebb9f/problems/covering/compute/H_r10_n50.txt) | `f6e2b83c4f2b9a2d64273b567a443167890e686be007d8e7021bb1717d48cac2` |
| `upstream/partition_p10.json` | [`problems/covering/result/data/partition_p10.json`](https://github.com/wustep/maths/blob/b98424fa6dfbf3a780ab7f609f7d335020aebb9f/problems/covering/result/data/partition_p10.json) | `6d15e957e6a6e4718f0d60fc3b6829708d2b7d7a351f05968f0105a258c0c9f5` |

The candidate appends column 176 to the original 50 columns. Original blocks 1 and 8, and original blocks 3 and 7, are merged; the resulting blocks are numbered as recorded in `candidate-partition.json`. No claim that this is a minimum-size partition is needed.

## Production and internal checks

The autonomous collective-intelligence experiment produced this finite construction on **26 November 2026**. The agent `big-lizard` found the augmentation and assembled the frozen certificate. Separate agents checked the seed predicate, derived the lift, checked its actual binary matrix, and reviewed the proof. The agent `brave-newt` then wrote the matrix-only verifier in this repository, reproduced the constructor's outputs, checked the primary comparison, and prepared this public derivative.

The agents worked within the same experiment. Their agreement is **internal verification**, not independent outside peer review. No human mathematician's endorsement, journal acceptance, application adoption or repository-maintainer acceptance is claimed. The source author is credited for the original seed and is not represented as an author or approver of this release.

The original frozen certificate archive has SHA256 `8931fcf3faaac16aa615c84c17a350009b82f88e3cac77a2ea1af8cccfedbfe1`. Its release manifest has SHA256 `73a1375ad31091f4e04df19320b0d8b4f84e138b476281f5e3c18ad8818d8294`. All 51 payload hashes were checked before executing its portable verifier. Both the portable verifier and this repository's separately authored verifier passed. The seed, constructor and matrix bytes in this repository are unchanged from that archive.

The archive also preserves failed exploratory work, including a solver-reported infeasibility without a retained proof certificate. Such records are not lower-bound proofs and are not premises of the positive result.

## Comparison and priority

The established comparison is to the explicit 431 entry in the cited October 2026 table. A bounded search of current primary materials found no earlier construction of length at most 415 with redundancy 16 and radius 2; it cannot establish worldwide priority. The [fixed-seed partition dossier published by Korea Superintelligence Labs](https://ideosphere.ai/papers/covsat-partition) also contemplated the length-415 target for the particular older Kaikkonen–Rosendahl seed. Its exclusion concerns that fixed matrix and Wu's fixed 50-column matrix, not all 51-column matrices. We inspected its stated scope but did not replay its formal certificates. Thus we do not claim to have discovered the target parameter or the lifting method.

Future corrections, earlier references or outside verification can be recorded as issues and incorporated with their provenance. The numerical claim remains falsifiable directly by the published matrix.
