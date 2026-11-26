# Construction and finite certificate

Let $\ell_2(r,R)$ denote the minimum length of a binary linear code of redundancy $r$ and covering radius $R$.

**Proposition.** The matrix `H_r16_n415.bits.txt` is a parity-check matrix for a binary linear $[415,399,3]$ code of covering radius exactly $2$. Hence $\ell_2(16,2)\le415$.

There are two ways to check the proposition: directly enumerate the syndromes of the supplied matrix, or verify the small seed predicate and the construction below.

## 1. Eight-block seed

An integer encodes a binary ten-vector, with its least significant bit in row 1. The following eight blocks contain 51 distinct nonzero vectors:

| Block | Columns |
|---:|---|
| 0 | 2, 128, 176, 202, 212, 771, 855, 897, 981 |
| 1 | 86, 403 |
| 2 | 381, 893, 1003 |
| 3 | 183, 297, 479, 1004 |
| 4 | 1, 65, 247, 256, 320, 438, 502, 734 |
| 5 | 15, 173, 329, 366, 460, 559, 653, 846 |
| 6 | 4, 16, 391, 491, 742, 754, 869, 881 |
| 7 | 32, 341, 373, 576, 608, 777, 789, 821, 927 |

The required finite predicate is: every vector in $\mathbb F_2^{10}$ is zero, a listed column, or the sum of two columns in different blocks. This is the $(2,0)$-partition condition. `build.py` checks all 1,024 vectors, using the complete data in `candidate-partition.json`. Zero uses the empty sum.

The seed comes from Wu's 50-column matrix by adding 176 and merging two pairs of its original blocks. This claim needs no assumption about the minimum partition size of the original matrix or of any other seed.

## 2. Lift over the field with eight elements

Use $F=\mathbb F_2[t]/(t^3+t+1)$. The cubic has no root in $\mathbb F_2$, so it is irreducible. Three coefficient bits encode a field element; addition is XOR. The block label $\beta\in\{0,\ldots,7\}$ is interpreted as its corresponding field element.

For each seed column $h$ in block $\beta$, include the eight columns

$$ (h,x,\beta x),\qquad x\in F. $$

Also include the seven tail columns

$$ (0,0,w),\qquad w\in F\setminus\{0\}. $$

These are sixteen-bit columns. Their integer encoding is `h | (x << 10) | (y << 13)` for a column $(h,x,y)$. The file orders seed columns as in the JSON, then $x=0,\ldots,7$ for each seed column, followed by the tails $w=1,\ldots,7$.

There are $51\cdot8+7=415$ columns. They are nonzero and distinct: different seed columns differ in their first ten coordinates; different $x$ values for the same seed differ in their middle coordinates; tails have zero first ten coordinates and are mutually distinct.

This is the existing construction of Davydov and Drozhzhina-Labinskaya (1994, Theorem 3.1), as stated in the 2026 paper's Theorem 4.3. Its numerical condition is $n_0\ge2^m\ge p$, here $51\ge8\ge8$. The following argument also verifies coverage directly without relying on the theorem.

## 3. Every syndrome has a representation of weight at most two

Take a syndrome $(\pi,u,v)\in\mathbb F_2^{10}\times F\times F$.

**Two-column top syndrome.** If $\pi$ is neither zero nor a seed column, the checked partition supplies $\pi=h_i+h_j$ with different labels $\beta_i\ne\beta_j$. Solve

$$ x+y=u,\qquad \beta_i x+\beta_j y=v. $$

The solution is

$$ x=\frac{v+\beta_j u}{\beta_i+\beta_j},\qquad y=u+x. $$

The denominator is nonzero. The corresponding lifted columns are distinct and sum to the required syndrome.

**One-column top syndrome.** If $\pi=h_j$, take $(h_j,u,\beta_j u)$ and, if $v+\beta_j u\ne0$, the tail $(0,0,v+\beta_j u)$. Their sum is the required syndrome; omit a zero tail.

**Zero top syndrome.** If $\pi=0$ and $u=0$, use the tail $(0,0,v)$ when $v\ne0$, or the empty sum otherwise. If $\pi=0$ and $u\ne0$, select a seed column in block $\beta=v/u$. Every block is nonempty, so this is possible. Then

$$ (h,0,0)+(h,u,\beta u)=(0,u,v). $$

The two columns are distinct because $u\ne0$.

Thus every syndrome is a sum of at most two distinct columns.

## 4. Code parameters

Coverage of all sixteen-bit syndromes implies that the columns span $\mathbb F_2^{16}$, so the matrix has rank 16 and its kernel has dimension $415-16=399$. For every vector $z\in\mathbb F_2^{415}$, a vector $e$ of weight at most two has syndrome $He=Hz$. Therefore $z+e$ belongs to the kernel, proving covering radius at most two.

Zero and the singleton columns supply only $416<65,536$ syndromes, so radius one is impossible. Distinct nonzero columns exclude codewords of weights one and two. The three tail columns with $w=1,2,3$ sum to zero, giving a weight-three codeword. The radius is exactly two and the minimum distance is exactly three.

## 5. Check of the actual written matrix

`verify.py` reads only the binary matrix and uses ordinary integer arithmetic. It checks shape, binary entries, row rank, distinct nonzero columns and every empty/singleton/distinct-pair sum. Its receipt records 65,536 covered syndromes from

$$ 1+415+\binom{415}{2}=86,321 $$

error vectors. The receipt also gives the dependent triple at one-based columns 41, 145 and 161, whose values are 32, 341 and 373. Syndrome 33792 is the sum of columns 1 and 2 but is neither zero nor any single column. These independently certify the exact distance and radius on the materialized data.

The supplied constructor reproduces the binary and decimal matrix files byte for byte. This finite certificate establishes an upper bound; it does not establish that 415 is minimal.

## 6. Consequence at redundancy 35 and radius 3

Theorem 7.6 of [Davydov–Marcugini–Pambianco–Wu (2026)](https://arxiv.org/html/2609.16078v2) takes an outer radius-three code of length $n_0$ and redundancy $r_0$, a $(3,0)$-partition into $p$ blocks, and an inner radius-two code of redundancy $2m$ and length $n_{2m}$. For $m\ge2$ and $2^m-1\ge p$, it gives

$$r=r_0+3m,\qquad n=2^m(n_0+1)+n_{2m}-1.$$

Take the ordinary perfect binary Golay $[23,12,7]$ code as the outer code, with its 23 singleton blocks. This is the same outer seed used in the paper's proof of Theorem 7.8. Put $m=8$ and use the verified code above as the inner code. The inner code's singleton partition is sufficient; no restriction on its partition size is imposed by this theorem. Then $255\ge23$, $r=35$, and $n=6558$, so

$$\ell_2(35,3)\le6558.$$

Table 7.2 lists 6574 at redundancy 35. This is another 16-column improvement relative to that table. The larger matrix has not been generated here, and no exhaustive $2^{35}$-syndrome check is claimed. The result follows from the stated theorem and the verified constituent; no stronger partition parameter or asymptotic conclusion is needed.
