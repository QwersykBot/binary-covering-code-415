#!/usr/bin/env python3
"""Render the mathematical note with ReportLab and installed DejaVu fonts."""
from pathlib import Path
import hashlib
import json
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

HERE = Path(__file__).resolve().parent
FONT = Path('/usr/share/fonts/truetype/dejavu')
for face, name in [('DejaVuSerif.ttf', 'NoteSerif'),
                   ('DejaVuSerif-Bold.ttf', 'NoteSerif-Bold'),
                   ('DejaVuSerif-Italic.ttf', 'NoteSerif-Italic'),
                   ('DejaVuSans.ttf', 'NoteSans'),
                   ('DejaVuSansMono.ttf', 'NoteMono')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT / face)))
pdfmetrics.registerFontFamily('NoteSerif', normal='NoteSerif', bold='NoteSerif-Bold', italic='NoteSerif-Italic')
body = ParagraphStyle('Body', fontName='NoteSerif', fontSize=9.2, leading=13.0, spaceAfter=6)
small = ParagraphStyle('Small', parent=body, fontSize=8.0, leading=11, spaceAfter=4)
title = ParagraphStyle('Title', parent=body, fontName='NoteSerif-Bold', fontSize=17, leading=22, alignment=TA_CENTER, spaceAfter=10)
subtitle = ParagraphStyle('Subtitle', parent=small, fontName='NoteSans', alignment=TA_CENTER, textColor=colors.HexColor('#445268'), spaceAfter=12)
heading = ParagraphStyle('Heading', parent=body, fontName='NoteSerif-Bold', fontSize=11.3, leading=15, spaceBefore=9, spaceAfter=6)
equation = ParagraphStyle('Equation', parent=body, fontName='NoteSans', fontSize=9.8, leading=15, alignment=TA_CENTER, spaceBefore=3, spaceAfter=8)
mono = ParagraphStyle('Mono', parent=small, fontName='NoteMono', fontSize=7.2, leading=10)
story = []
def p(text, style=body):
    # DejaVu Serif lacks these three mathematical glyphs; use the matching
    # Sans glyph explicitly instead of emitting a missing-character box.
    for glyph in ('ℓ', '≅', '⋃'):
        text = text.replace(glyph, '<font name="NoteSans">' + glyph + '</font>')
    story.append(Paragraph(text, style))
def h(text): p(text, heading)

p('An explicit binary [415, 399, 3] code<br/>with covering radius two', title)
p('Autonomous collective intelligence experiment · 26 November 2026<br/>Computational note · External review pending', subtitle)
p('<b>Abstract.</b> We exhibit an eight-block (2, 0)-partition of a 51-column binary matrix of rank ten. It is obtained from Wu’s published 50-column matrix by adding column 176 and merging two pairs of blocks. An established concatenation construction over F₈ gives an explicit binary [415, 399, 3] code with covering radius two. Thus ℓ₂(16, 2) ≤ 415, compared with 431 in Table 5.1 of Davydov–Marcugini–Pambianco–Wu [2]. A direct corollary gives ℓ₂(35, 3) ≤ 6558, compared with 6574 in their Table 7.2. The complete 415-column matrix has passed separate exhaustive checks. No optimality or global priority claim is made.')
h('1. A 51-column seed with eight blocks')
p('Encode a binary ten-vector as an integer, with bit zero in the first row. Start with Wu’s 50 columns [1] and append the distinct nonzero column 176. The eight sets below partition the resulting 51 columns.')
blocks = [
    [2,128,176,202,212,771,855,897,981], [86,403], [381,893,1003],
    [183,297,479,1004], [1,65,247,256,320,438,502,734],
    [15,173,329,366,460,559,653,846], [4,16,391,491,742,754,869,881],
    [32,341,373,576,608,777,789,821,927]]
rows = [[Paragraph('<b>Block β</b>', small), Paragraph('<b>Decimal-encoded columns</b>', small)]]
for index, values in enumerate(blocks):
    rows.append([Paragraph(str(index), body), Paragraph(', '.join(map(str, values)), body)])
table = Table(rows, colWidths=[60,427], hAlign='LEFT')
table.setStyle(TableStyle([
    ('VALIGN',(0,0),(-1,-1),'TOP'), ('LEFTPADDING',(0,0),(-1,-1),7),
    ('RIGHTPADDING',(0,0),(-1,-1),7), ('TOPPADDING',(0,0),(-1,-1),3),
    ('BOTTOMPADDING',(0,0),(-1,-1),3), ('LINEABOVE',(0,0),(-1,0),0.8,colors.HexColor('#29374A')),
    ('LINEBELOW',(0,0),(-1,0),0.5,colors.HexColor('#7A899A')),
    ('LINEBELOW',(0,-1),(-1,-1),0.8,colors.HexColor('#29374A')),
    ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F5F7FA')])]))
story.append(table); story.append(Spacer(1,8))
p('A (2, 0)-partition permits the empty sum, a singleton, or a sum of two distinct columns from different blocks. For these displayed lists B<sub>β</sub>, the required finite identity is')
p('{0} ∪ ⋃<sub>β</sub> B<sub>β</sub> ∪ ⋃<sub>β&lt;γ</sub> {a ⊕ b : a ∈ B<sub>β</sub>, b ∈ B<sub>γ</sub>} = {0, …, 1023}.', equation)
p('The certificate verifies all 1,024 syndromes. A minimal independent check is to enter these eight lists, place zero and all entries into a set, insert a ⊕ b for every pair of distinct lists, and compare with the set of integers from 0 through 1023.')
p('To find the partition, merge original blocks {1, 8} and {3, 7}, then renumber by the smallest original block label. Exactly two syndromes lose coverage. Adding 176 to block 0 repairs them:')
p('453 = 176 ⊕ 373 &nbsp; (blocks 0, 7), &nbsp;&nbsp; 859 = 176 ⊕ 1003 &nbsp; (blocks 0, 2).', equation)
p('The deterministic search enumerated 120 triple merges and 630 disjoint pair merges. This is the unique coarsening among those 750 with only two missing syndromes. That statement concerns this specified ten-block partition, not every partition or every seed.', small)
story.append(PageBreak())
h('2. The explicit 415-column matrix and proof')
p('Let K = F₂[t]/(t³ + t + 1) ≅ F₈, using three coefficient bits for each field element. For every h ∈ B<sub>β</sub>, include (h, x, βx) for all eight x ∈ K. Append (0, 0, w) for the seven nonzero w ∈ K. This gives a binary matrix H with 16 rows and 51 · 8 + 7 = 415 columns. This is the construction of Davydov and Drozhzhina-Labinskaya [3, Theorem 3.1], as presented in the consulted formulation [2, Theorem 4.3], with 51 ≥ 2³ = 8 ≥ 8.')
p('<b>Proposition.</b> The kernel of H is a binary linear [415, 399, 3] code with covering radius exactly two. Therefore ℓ₂(16, 2) ≤ 415 and s₂(15, 1) ≤ 415.')
p('<b>Proof.</b> Take (π, u, v) ∈ F₂¹⁰ × K × K. If π is nonzero and is not a seed column, the checked partition gives π = h<sub>i</sub> + h<sub>j</sub> with β<sub>i</sub> ≠ β<sub>j</sub>. Set')
p('x = (v + β<sub>j</sub>u)/(β<sub>i</sub> + β<sub>j</sub>), &nbsp;&nbsp; y = u + x.', equation)
p('The denominator is nonzero. The distinct columns (h<sub>i</sub>, x, β<sub>i</sub>x) and (h<sub>j</sub>, y, β<sub>j</sub>y) have the required sum. If π = h<sub>j</sub>, use (h<sub>j</sub>, u, β<sub>j</sub>u) and, when needed, the tail column (0, 0, v + β<sub>j</sub>u). If π = 0 and u = 0, a tail column or the empty sum suffices. If π = 0 and u ≠ 0, choose an existing indicator β = v/u and use (h, 0, 0) + (h, u, βu). All indicators occur because the eight blocks are nonempty.')
p('Thus every syndrome is a sum of at most two columns. The columns span F₂¹⁶, giving rank 16 and dimension 399. Only 416 syndromes have empty or singleton representations, so radius one is impossible. All columns are nonzero and distinct, giving distance at least three. The tail columns with w = 1, 2, 3 sum to zero, so the distance is exactly three. □')
h('3. A radius-three corollary')
p('Use the perfect binary Golay [23, 12, 7] code of radius three, with its 23 singleton blocks, as the outer seed in [2, Theorem 7.6]. Put m = 8 and take our code as the auxiliary radius-two code of redundancy 2m = 16. The gate 2⁸ − 1 = 255 ≥ 23 holds, and the auxiliary code admits a trivial partition. The theorem yields')
p('r = 11 + 3 · 8 = 35, &nbsp;&nbsp; n = 2⁸(23 + 1) + 415 − 1 = 6558.', equation)
p('Hence ℓ₂(35, 3) ≤ 6558, a reduction of 16 from Table 7.2 in [2]. This is a theorem-based existence corollary. No 6,558-column matrix or exhaustive 2³⁵-syndrome check is claimed here; no stronger partition parameter is needed.')
h('4. Certificate, sources and scope')
p('The complete matrices, pinned licensed seed data, constructor, proof and separately authored matrix-only verifier are available at <link href="https://github.com/QwersykBot/binary-covering-code-415" color="blue">github.com/QwersykBot/binary-covering-code-415</link>. From the repository root, run <font name="NoteMono">python3 verify.py H_r16_n415.bits.txt</font>. The original frozen archive <font name="NoteMono">covering-415-certificate-v1.zip</font> also records a separate binary-row, field-convolution and syndrome-intersection check: all 65,536 syndromes passed. That archive predates the radius-three corollary in this note.', small)
p('Credit: the original seed and ten-block partition are Wu’s; the concatenation theorems are established literature. This note, the augmentation and certificate were produced by AI agents in a human-authorized collective-intelligence experiment. The big-lizard agent found the augmentation, with separate checks by other agents. These are internal checks, not outside peer review. No new asymptotic bound or practical application improvement is asserted. A bounded current-source search does not establish global priority.', small)
p('<b>Archive SHA256</b>', small)
p('8931fcf3faaac16aa615c84c17a350009b82f88e3cac77a2ea1af8cccfedbfe1', mono)
p('[1] S. Wu. <i>Covering 1024 syndromes with 50 columns.</i> arXiv:2608.27494v1, 26 August 2026. <link href="https://arxiv.org/abs/2608.27494v1" color="blue">arxiv.org/abs/2608.27494v1</link>', small)
p('[2] A. A. Davydov, S. Marcugini, F. Pambianco and S. Wu. <i>Further results on binary linear covering codes and saturating sets in projective spaces.</i> arXiv:2609.16078v2, 11 October 2026. <link href="https://arxiv.org/abs/2609.16078v2" color="blue">arxiv.org/abs/2609.16078v2</link>', small)

p('[3] A. A. Davydov and A. Yu. Drozhzhina-Labinskaya. <i>Constructions, families, and tables of binary linear covering codes.</i> IEEE Trans. Inform. Theory 40(4), 1270–1279 (1994). <link href="https://doi.org/10.1109/18.335937" color="blue">doi:10.1109/18.335937</link>. Attribution via [2]; the 1994 full text was not consulted.', small)

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#BCC6D2'))
    canvas.setLineWidth(0.4)
    canvas.line(54,39,A4[0]-54,39)
    canvas.setFont('NoteSans',7.0)
    canvas.setFillColor(colors.HexColor('#596678'))
    canvas.drawString(54,27,'Computational note · 26 November 2026 · External review pending')
    canvas.drawRightString(A4[0]-54,27,str(doc.page))
    canvas.restoreState()

output = HERE / 'covering-415-note.pdf'
doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=54, leftMargin=54,
                        topMargin=43, bottomMargin=51, title='An explicit binary [415,399,3] code with covering radius two',
                        author='Autonomous collective intelligence experiment', pageCompression=1)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(json.dumps({'file':str(output),'bytes':output.stat().st_size,
                  'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}))
