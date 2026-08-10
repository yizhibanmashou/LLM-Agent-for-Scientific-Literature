#!/usr/bin/env python3
"""Build verified Genetics structured/textbook assets from staged Paddle output."""

from __future__ import annotations

import argparse
import copy
import html
import json
import math
import os
import re
import shutil
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import cv2
import fitz
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from textbook_exporter import export_textbooks
from scripts.rebuild_genetics_book import RANGES, write_json

HEADING_LABELS = {"doc_title", "paragraph_title"}
SKIP_LABELS = {"header", "number", "footer", "page_number"}
TABLE_CAPTION_RE = re.compile(r"^Table\s+(?P<id>(?:A\d+|\d+)\.\d+[a-z]?)\b", re.I)
FIGURE_CAPTION_RE = re.compile(r"^(?:Figure|Fig\.)\s+(?P<id>(?:A\d+|\d+)\.\d+[a-z]?)\b", re.I)
EXAMPLE_RE = re.compile(r"^Example\s+(?P<id>\d+)\s*[.:]", re.I)
FORMULA_NUMBER_RE = re.compile(r"^[\[(]\s*(?P<id>(?:A\d+|\d+)\.\d+[a-z]?)\s*[\])]$", re.I)
DIRECT_PLACEHOLDER_RE = re.compile(r"\[\[(?:FORMULA|TABLE|FIGURE|EXAMPLE):[^\]]+\]\]", re.I)
FIGURE_LINK_RE = re.compile(r"!\[[^\]]*\]\((?P<path>[^)]+)\)")

# OCR corrections are admitted only when the source PDF page has been visually
# checked.  Keep these narrow and page-scoped so they cannot rewrite unrelated
# occurrences during a future rebuild.
SOURCE_TEXT_CORRECTIONS = {
    393: (("1 his chapter introduces", "This chapter introduces"),),
    507: ((
        "where i, j, k, and l denote different marker alleles",
        r"where $ i, j, k, $ and $ \ell $ denote different marker alleles",
    ),),
    593: (("1nus, we see", "Thus, we see"),),
    754: (("heri-\ntability estimates", "heritability estimates"),),
    282: ((
        r"$\sqrt{\mathrm{Var}(A)$",
        r"$\sqrt{\mathrm{Var}(A)}$",
    ),),
    557: ((
        r"$SE(b) = \sqrt{\overline{Var}(b)$",
        r"$SE(b) = \sqrt{\mathrm{Var}(b)}$",
    ),),
    840: (
        ("it produces $ (G_f $ and $ H_f $ $ will", "it produces ($ G_f $ and $ H_f $) will"),
        ("produced it $ (G_o $ and $ H_f $ $.", "produced it ($ G_o $ and $ H_f $)."),
    ),
    861: ((
        "random $ \\left(\\mathbf{u} $ and $ \\mathbf{e} $ vs. $ \\mathbf{u}_{*} $ and $ \\mathbf{e}_{*}\\right) $ effects",
        "random ($ \\mathbf{u} $ and $ \\mathbf{e} $ vs. $ \\mathbf{u}_{*} $ and $ \\mathbf{e}_{*} $) effects",
    ),),
    877: (
        ("until the interactions converge", "until the iterations converge"),
        (r"\widehat{\sigma}^2^{(0)}", r"\widehat{\sigma}^{2(0)}"),
    ),
    890: ((
        "In this last case, subtraction of the mean causes the loss of the degree of freedom.\nA noncentral",
        "A noncentral",
    ),),
    894: ((r"F_{3,16}, [0.95] = 3.24", r"F_{3,16,[0.95]} = 3.24"),),
}
SOURCE_TEXT_CORRECTION_EVIDENCE: dict[tuple[int, int], dict[str, Any]] = {
    (393, 4): {
        "bbox": [69.0, 1048.0, 1035.0, 1349.0],
        "replacements": (("1 his chapter introduces", "This chapter introduces"),),
        "reason": "Chapter 14 opening overview OCR character error; source PDF reads ‘This chapter’",
    },
    (507, 10): {
        "bbox": [73.0, 1419.0, 1035.0, 1547.0],
        "replacements": ((
            "where i, j, k, and l denote different marker alleles",
            r"where $ i, j, k, $ and $ \ell $ denote different marker alleles",
        ),),
        "reason": "PDF page 507 uses italic i, j, k and script ell; Paddle flattened script ell to ordinary l",
    },
    (593, 4): {
        "bbox": [105.0, 745.0, 974.0, 1268.0],
        "replacements": (("1nus, we see", "Thus, we see"),),
        "reason": "Example 18.3 OCR character error; source PDF reads ‘Thus’",
    },
    (282, 2): {
        "bbox": [175.0, 129.0, 1042.0, 409.0],
        "replacements": ((
            r"$\sqrt{\mathrm{Var}(A)$",
            r"$\sqrt{\mathrm{Var}(A)}$",
        ),),
        "reason": "PDF page 282 closes the square root after Var(A); Paddle dropped the closing brace",
    },
    (557, 9): {
        "bbox": [85.0, 800.0, 1047.0, 1091.0],
        "replacements": ((
            r"$SE(b) = \sqrt{\overline{Var}(b)$",
            r"$SE(b) = \sqrt{\mathrm{Var}(b)}$",
        ),),
        "reason": "PDF page 557 shows SE(b) as the square root of Var(b); Paddle lost the root brace and misread the radical bar as an overline",
    },
    (840, 9): {
        "bbox": [144.0, 1137.0, 1105.0, 1365.0],
        "replacements": (
            ("it produces $ (G_f $ and $ H_f $ $ will", "it produces ($ G_f $ and $ H_f $) will"),
            ("produced it $ (G_o $ and $ H_f $ $.", "produced it ($ G_o $ and $ H_f $)."),
        ),
        "reason": "PDF page 840 places prose parentheses outside the two inline symbols; Paddle emitted an extra dollar delimiter",
    },
    (861, 9): {
        "bbox": [52.0, 996.0, 1011.0, 1089.0],
        "replacements": ((
            "random $ \\left(\\mathbf{u} $ and $ \\mathbf{e} $ vs. $ \\mathbf{u}_{*} $ and $ \\mathbf{e}_{*}\\right) $ effects",
            "random ($ \\mathbf{u} $ and $ \\mathbf{e} $ vs. $ \\mathbf{u}_{*} $ and $ \\mathbf{e}_{*} $) effects",
        ),),
        "reason": "PDF page 861 uses one prose parenthetical containing four vector symbols; Paddle split a left/right pair across inline delimiters",
    },
    (877, 2): {
        "bbox": [56.0, 148.0, 1014.0, 253.0],
        "replacements": ((r"\widehat{\sigma}^2^{(0)}", r"\widehat{\sigma}^{2(0)}"),),
        "reason": "PDF page 877 has the combined superscript 2(0) on sigma-hat; Paddle emitted two consecutive superscripts",
    },
    (877, 5): {
        "bbox": [58.0, 420.0, 1015.0, 499.0],
        "replacements": ((r"\widehat{\sigma}^2^{(0)}", r"\widehat{\sigma}^{2(0)}"),),
        "reason": "PDF page 877 repeats the combined superscript 2(0) on sigma-hat in prose",
    },
    (754, 11): {
        "bbox": [137.0, 847.0, 1094.0, 913.0],
        "replacements": (("heri-\ntability estimates", "heritability estimates"),),
        "reason": "PDF page 754 splits the ordinary word 'heritability' across a typeset line as 'heri-' / 'tability'",
    },
    (877, 16): {
        "bbox": [55.0, 1098.0, 1014.0, 1166.0],
        "replacements": (("until the interactions converge", "until the iterations converge"),),
        "reason": "Appendix 4 EM procedure text reads 'until the iterations converge' in the source PDF",
    },
    (890, 17): {
        "bbox": [150.0, 1135.0, 1111.0, 1263.0],
        "replacements": ((
            "In this last case, subtraction of the mean causes the loss of the degree of freedom.\nA noncentral",
            "A noncentral",
        ),),
        "reason": "The source PDF starts this block at 'A noncentral'; Paddle duplicated the preceding block's sentence",
    },
    (894, 9): {
        "bbox": [194.0, 836.0, 1054.0, 906.0],
        "replacements": ((r"F_{3,16}, [0.95] = 3.24", r"F_{3,16,[0.95]} = 3.24"),),
        "reason": "Appendix 5 Example 3 keeps the 0.95 quantile inside the F subscript",
    },
}

# Exact cross-page word joins whose typographic end-of-line hyphen must be
# removed.  These are deliberately keyed by both Paddle blocks and both PDF
# bboxes: a future extraction-layout change must fail closed instead of
# silently rewriting a genuine hyphenated compound.
SOURCE_CROSS_PAGE_JOIN_CORRECTIONS: dict[tuple[str, str], dict[str, Any]] = {
    ("p663:b6", "p664:b2"): {
        "left_bbox": [104.0, 1471.0, 1010.0, 1507.0],
        "right_bbox": [139.0, 138.0, 1102.0, 583.0],
        "left_suffix": "funda-",
        "right_prefix": "mental",
        "replacement": "fundamental",
        "reason": "PDF pages 663–64 split the word ‘fundamental’ as ‘funda-’ / ‘mental’",
    },
    ("p433:b6", "p434:b2"): {
        "left_bbox": [83.0, 1458.0, 1046.0, 1536.0],
        "right_bbox": [132.0, 136.0, 1095.0, 416.0],
        "left_suffix": "fre-",
        "right_prefix": "frequency",
        "replacement": "frequency",
        "reason": "PDF pages 433–434 split ‘frequency’ as ‘fre-’ / ‘quency’; Paddle expanded the continuation to a full duplicate word",
    },
    ("p419:b6", "p420:b2"): {
        "left_bbox": [70.0, 1281.0, 1032.0, 1516.0],
        "right_bbox": [117.0, 133.0, 1077.0, 328.0],
        "left_suffix": "pos-",
        "right_prefix": "sible",
        "replacement": "possible",
        "reason": "PDF pages 419–420 split the word ‘possible’ as ‘pos-’ / ‘sible’",
    },
}

# Paddle occasionally assigns a running-text continuation to ``header``.  Such
# blocks are normally (and correctly) skipped, so admit overrides only by exact
# page, block id, label, text, and PDF bbox.  This is deliberately data rather
# than a heuristic: every entry is a versioned, source-local human correction.
SOURCE_BLOCK_CORRECTIONS: dict[tuple[int, int], dict[str, Any]] = {
    (460, 2): {
        "expected_label": "paragraph_title",
        "expected_text": "different marker genotypes as",
        "bbox": [169.0, 144.0, 498.0, 175.0],
        "replacement_label": "text",
        "reason": "Example 4 continuation misclassified as a paragraph title by Paddle",
    },
    (785, 2): {
        "expected_label": "header",
        "expected_text": "which gives the same estimates as obtained with the permanent-effects model.",
        "bbox": [114.0, 128.0, 957.0, 177.0],
        "replacement_label": "text",
        "reason": "Example 26.10 continuation misclassified as a running header by Paddle",
    },
}

# Paddle can merge a visually distinct bold subsection heading and its first
# prose line into one ordinary text block.  Split only source-local cases that
# have been checked against the PDF, with exact text and bbox validation.
SOURCE_BLOCK_SPLITS: dict[tuple[int, int], dict[str, Any]] = {
    (481, 3): {
        "expected_label": "text",
        "expected_text": (
            "Detecting Multiple Linked QTLs Using Standard Marker-Trait Regressions\n"
            "Consider the standard multiple regression of trait value on the single-locus genotypes at each of n markers,"
        ),
        "bbox": [75.0, 193.0, 1036.0, 310.0],
        "heading": "Detecting Multiple Linked QTLs Using Standard Marker-Trait Regressions",
        "body": "Consider the standard multiple regression of trait value on the single-locus genotypes at each of n markers,",
        "reason": "PDF page 481 has a bold subsection heading followed by ordinary prose inside one Paddle text block",
    },
}

# Page 106 contains compact multi-column equations for two-locus effects.
# Paddle inserted OCR debris (Cyrillic/CJK glyphs, ``underbrace``, ``boldmath``)
# into these lines.  The replacements below are exact visual transcriptions of
# the PDF and are keyed by the full source bbox so layout drift fails closed.
SOURCE_FORMULA_CORRECTIONS: dict[tuple[int, tuple[float, float, float, float]], str] = {
    (106, (260.0, 827.0, 1000.0, 883.0)): r"G_{B_M\cdot U_{MM}}=36.30\qquad G_{B_M\cdot U_{MT}}=44.25\qquad G_{B_M\cdot U_{TT}}=63.80",
    (106, (262.0, 860.0, 1001.0, 917.0)): r"G_{B_T\cdot U_{MM}}=51.20\qquad G_{B_T\cdot U_{MT}}=65.60\qquad G_{B_T\cdot U_{TT}}=84.10",
    (106, (262.0, 891.0, 1003.0, 949.0)): r"G_{B_{MM}U_M\cdot}=29.45\qquad G_{B_{MT}U_M\cdot}=51.10\qquad G_{B_{TT}U_M\cdot}=65.70",
    (106, (264.0, 922.0, 1003.0, 979.0)): r"G_{B_{MM}U_T\cdot}=51.00\qquad G_{B_{MT}U_T\cdot}=57.05\qquad G_{B_{TT}U_T\cdot}=92.65",
    (106, (200.0, 1081.0, 1080.0, 1141.0)): r"(\alpha\delta)_{B_M\cdot U_{MM}}=0.9375\qquad(\alpha\delta)_{B_M\cdot U_{MT}}=-0.9375\qquad(\alpha\delta)_{B_M\cdot U_{TT}}=0.9375",
    (106, (201.0, 1117.0, 1080.0, 1174.0)): r"(\alpha\delta)_{B_T\cdot U_{MM}}=-0.9375\qquad(\alpha\delta)_{B_T\cdot U_{MT}}=0.9375\qquad(\alpha\delta)_{B_T\cdot U_{TT}}=-0.9375",
    (106, (201.0, 1145.0, 1083.0, 1206.0)): r"(\alpha\delta)_{B_{MM}U_M\cdot}=-4.5750\qquad(\alpha\delta)_{B_{MT}U_M\cdot}=4.5750\qquad(\alpha\delta)_{B_{TT}U_M\cdot}=-4.5750",
    (106, (204.0, 1178.0, 1083.0, 1239.0)): r"(\alpha\delta)_{B_{MM}U_T\cdot}=4.5750\qquad(\alpha\delta)_{B_{MT}U_T\cdot}=-4.5750\qquad(\alpha\delta)_{B_{TT}U_T\cdot}=4.5750",
    (106, (199.0, 1336.0, 1101.0, 1399.0)): r"(\delta\delta)_{B_{MM}U_{MM}}=-4.5125\qquad(\delta\delta)_{B_{MM}U_{MT}}=4.5125\qquad(\delta\delta)_{B_{MM}U_{TT}}=-4.5125",
    (106, (203.0, 1374.0, 1101.0, 1429.0)): r"(\delta\delta)_{B_{MT}U_{MM}}=4.5125\qquad(\delta\delta)_{B_{MT}U_{MT}}=-4.5125\qquad(\delta\delta)_{B_{MT}U_{TT}}=4.5125",
    (106, (199.0, 1401.0, 1101.0, 1464.0)): r"(\delta\delta)_{B_{TT}U_{MM}}=-4.5125\qquad(\delta\delta)_{B_{TT}U_{MT}}=4.5125\qquad(\delta\delta)_{B_{TT}U_{TT}}=-4.5125",
    (177, (114.0, 929.0, 955.0, 1006.0)): r"\begin{aligned}G_{ijkl}(x)={}&\mu_G+[\alpha_i^x+\alpha_j^x+\alpha_k^x+\alpha_l^x]\\&+[\delta_{ij}^x+\delta_{ik}^x+\delta_{il}^x+\delta_{jk}^x+\delta_{jl}^x+\delta_{kl}^x]\\&+[\gamma_{ijk}^x+\gamma_{ijl}^x+\gamma_{ikl}^x+\gamma_{jkl}^x]+\tau_{ijkl}^x\end{aligned}",
    (214, (315.0, 397.0, 916.0, 515.0)): r"\begin{pmatrix}A_o\\A_s\\A_d\end{pmatrix}\sim\mathrm{MVN}\left[\begin{pmatrix}\mu_o\\\mu_s\\\mu_d\end{pmatrix},\sigma_A^2\begin{pmatrix}1&1/2&1/2\\1/2&1&0\\1/2&0&1\end{pmatrix}\right]",
    (386, (159.0, 775.0, 1047.0, 936.0)): r"\begin{aligned}\ell(z_{i\cdot}\mid g_f,g_m)={}&\int_{-\infty}^{\infty}\int_{-\infty}^{\infty}\left[\prod_{j=1}^{n_i}\ell(z_{ij}\mid g_f,g_m,A_f,A_m)\right]\\&\qquad\varphi(A_f,0,\sigma_A^2)\varphi(A_m,0,\sigma_A^2)\,dA_f\,dA_m\end{aligned}",
    (786, (218.0, 274.0, 1023.0, 781.0)): r"\begin{aligned}&\begin{pmatrix}\mathbf{X}^{T}\mathbf{X}&\mathbf{X}^{T}\mathbf{Z}_{1}&\mathbf{X}^{T}\mathbf{Z}_{2}&\mathbf{X}^{T}\mathbf{Z}_{3}\\\mathbf{Z}_{1}^{T}\mathbf{X}&\mathbf{Z}_{1}^{T}\mathbf{Z}_{1}+\lambda_{1}\mathbf{A}^{-1}&\mathbf{Z}_{1}^{T}\mathbf{Z}_{2}+\lambda_{2}\mathbf{A}^{-1}&\mathbf{Z}_{1}^{T}\mathbf{Z}_{3}\\\mathbf{Z}_{2}^{T}\mathbf{X}&\mathbf{Z}_{2}^{T}\mathbf{Z}_{1}+\lambda_{2}\mathbf{A}^{-1}&\mathbf{Z}_{2}^{T}\mathbf{Z}_{2}+\lambda_{3}\mathbf{A}^{-1}&\mathbf{Z}_{2}^{T}\mathbf{Z}_{3}\\\mathbf{Z}_{3}^{T}\mathbf{X}&\mathbf{Z}_{3}^{T}\mathbf{Z}_{1}&\mathbf{Z}_{3}^{T}\mathbf{Z}_{2}&\mathbf{Z}_{3}^{T}\mathbf{Z}_{3}+\lambda_{4}\mathbf{I}\end{pmatrix}\begin{pmatrix}\widehat{\boldsymbol{\beta}}\\\widehat{\mathbf{a}}\\\widehat{\mathbf{m}}\\\widehat{\mathbf{c}}\end{pmatrix}\\&\qquad=\begin{pmatrix}\mathbf{X}^{T}\mathbf{y}\\\mathbf{Z}_{1}^{T}\mathbf{y}\\\mathbf{Z}_{2}^{T}\mathbf{y}\\\mathbf{Z}_{3}^{T}\mathbf{y}\end{pmatrix}\end{aligned}",
    (789, (199.0, 1091.0, 857.0, 1345.0)): r"\begin{aligned}&\begin{pmatrix}\mathbf{X}^{T}(\mathbf{E}^{-1}\otimes\mathbf{I})\mathbf{X}&\mathbf{X}^{T}(\mathbf{E}^{-1}\otimes\mathbf{I})\\(\mathbf{E}^{-1}\otimes\mathbf{I})\mathbf{X}&(\mathbf{E}^{-1}\otimes\mathbf{I})+(\mathbf{C}^{-1}\otimes\mathbf{A}^{-1})\end{pmatrix}\begin{pmatrix}\widehat{\boldsymbol{\beta}}\\\widehat{\mathbf{a}}\end{pmatrix}\\&\qquad=\begin{pmatrix}\mathbf{X}^{T}(\mathbf{E}^{-1}\otimes\mathbf{I})\mathbf{y}\\(\mathbf{E}^{-1}\otimes\mathbf{I})\mathbf{y}\end{pmatrix}\end{aligned}",
    (808, (178.0, 1020.0, 1113.0, 1151.0)): r"\left.\frac{\partial^{2}L}{\partial\boldsymbol{\Theta}^{2}}\right|_{\boldsymbol{\Theta}^{(k)}}=\frac{1}{2}\begin{pmatrix}\operatorname{tr}(\mathbf{P}\mathbf{P})-2\mathbf{y}^{T}\mathbf{P}\mathbf{P}\mathbf{P}\mathbf{y}&\operatorname{tr}(\mathbf{P}\mathbf{A}\mathbf{P})-2\mathbf{y}^{T}\mathbf{P}\mathbf{A}\mathbf{P}\mathbf{P}\mathbf{y}\\\operatorname{tr}(\mathbf{P}\mathbf{A}\mathbf{P})-2\mathbf{y}^{T}\mathbf{P}\mathbf{A}\mathbf{P}\mathbf{P}\mathbf{y}&\operatorname{tr}(\mathbf{P}\mathbf{A}\mathbf{P}\mathbf{A})-2\mathbf{y}^{T}\mathbf{P}\mathbf{A}\mathbf{P}\mathbf{A}\mathbf{P}\mathbf{y}\end{pmatrix}",
    (856, (362.0, 467.0, 875.0, 565.0)): r"\mathbf{J}_{n\times1}=\left.\begin{pmatrix}1\\\vdots\\1\end{pmatrix}\right\}n,\qquad\mathbf{J}_{2\times3}=\begin{pmatrix}1&1&1\\1&1&1\end{pmatrix}",
    (900, (230.0, 925.0, 921.0, 1000.0)): r"\Pr\left[F_{\{Th^{2}/4\}-1,T(1-h^{2}/4)}>\frac{F_{\{Th^{2}/4\}-1,T(1-h^{2}/4),[1-\alpha]}}{1+4/(4-h^{2})}\right]",
}

# Paddle labelled the two raster-like chromosome panels of Figure 5.6 as
# display formulas.  They are source components of the figure, not equations.
NON_FORMULA_DISPLAY_BLOCKS = {(117, 3), (117, 5)}

# Paddle split internal labels out of several figures and labelled them as
# standalone prose/``figure_title`` blocks.  The glyphs are already present in
# the cropped figures, so emitting them as prose duplicates figure content. As
# with the other human corrections, require an exact page, block id, text, and
# bbox match so future layout drift fails closed.
NON_BODY_FIGURE_LABEL_BLOCKS: dict[tuple[int, int], dict[str, Any]] = {
    (53, 2): {
        "expected_text": "(A)",
        "bbox": [91.0, 124.0, 126.0, 152.0],
        "reason": "Figure 3.1 panel label split from the composite figure",
    },
    (59, 2): {
        "expected_text": "(A)",
        "bbox": [191.0, 130.0, 226.0, 159.0],
        "reason": "Figure 3.4 panel label split from the composite figure",
    },
    (150, 3): {
        "expected_text": "Probability",
        "bbox": [264.0, 134.0, 378.0, 164.0],
        "reason": "Figure 7.2 internal column label split from the figure",
    },
    (181, 2): {
        "expected_text": "Monozygotic twins",
        "bbox": [449.0, 133.0, 646.0, 163.0],
        "reason": "Figure 7.8 internal relationship label split from the figure",
    },
    (181, 3): {
        "expected_text": "Raised by own parents",
        "bbox": [226.0, 163.0, 453.0, 193.0],
        "reason": "Figure 7.8 internal environment label split from the figure",
    },
    (181, 4): {
        "expected_text": "Raised by different parents",
        "bbox": [643.0, 166.0, 908.0, 198.0],
        "reason": "Figure 7.8 internal environment label split from the figure",
    },
    (181, 6): {
        "expected_text": "Full sibs",
        "bbox": [498.0, 524.0, 591.0, 557.0],
        "reason": "Figure 7.8 internal relationship label split from the figure",
    },
}

APPENDIX_BOUNDARIES = {
    819: ("Appendix 1", "Expectations, Variances, and Covariances of Compound Variables"),
    835: ("Appendix 2", "Path Analysis"),
    847: ("Appendix 3", "Further Topics in Matrix Algebra and Linear Models"),
    865: ("Appendix 4", "Maximum Likelihood Estimation and Likelihood-ratio Tests"),
    881: ("Appendix 5", "Computing the Power of Statistical Tests"),
    903: ("Literature Cited",),
    961: ("Author Index",),
    973: ("Organism and Trait Index",),
    983: ("Subject Index",),
}

CHAPTER_TITLES = {
    14: "Principles of Marker-based Analysis",
    22: "Genotype \u00d7 Environment Interaction",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def clean_text(value: Any) -> str:
    # Decode only terminated HTML entities.  html.unescape() also treats the
    # TeX alignment token ``&not `` as the HTML entity ``¬`` without a
    # semicolon, corrupting case formulas such as chapter 13 formula 31.
    text = re.sub(
        r"&(?:#[0-9]+|#x[0-9A-Fa-f]+|[A-Za-z][A-Za-z0-9]+);",
        lambda match: html.unescape(match.group(0)),
        str(value or ""),
    ).replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"<div[^>]*>\s*", "", text, flags=re.I)
    text = re.sub(r"\s*</div>\s*", "", text, flags=re.I)
    return re.sub(r"[ \t]+", " ", text).strip()


def page_rows(page: dict[str, Any]) -> list[dict[str, Any]]:
    pruned = page.get("prunedResult") if isinstance(page.get("prunedResult"), dict) else {}
    rows = pruned.get("parsing_res_list") or page.get("parsing_res_list") or []
    return [row for row in rows if isinstance(row, dict)]


def bbox(row: dict[str, Any]) -> list[float] | None:
    value = row.get("block_bbox")
    if isinstance(value, list) and len(value) == 4:
        return [float(item) for item in value]
    return None


def source_meta(label: str, source_page: int, row: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_page": source_page,
        "printed_page": source_page - 20 if 21 <= source_page <= 992 else None,
        "source_block_ids": [f"p{source_page}:b{row.get('block_id', '?')}"] ,
        "bbox": bbox(row),
    }


def attach_heading_source(unit: dict[str, Any], label: str, source_page: int, row: dict[str, Any]) -> None:
    incoming = source_meta(label, source_page, row)
    incoming["raw_text"] = clean_text(row.get("block_content"))
    existing = unit["metadata"].get("heading_source")
    if not isinstance(existing, dict):
        unit["metadata"]["heading_source"] = incoming
        return
    existing.setdefault("source_block_ids", []).extend(
        item for item in incoming["source_block_ids"] if item not in existing["source_block_ids"]
    )
    existing["source_page_end"] = source_page
    existing["raw_text"] = " / ".join(filter(None, [str(existing.get("raw_text") or ""), incoming["raw_text"]]))
    boxes = [item for item in (existing.get("bbox"), incoming.get("bbox")) if isinstance(item, list)]
    if boxes:
        existing["bbox"] = [
            min(item[0] for item in boxes), min(item[1] for item in boxes),
            max(item[2] for item in boxes), max(item[3] for item in boxes),
        ]


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = []

    def handle_data(self, data: str) -> None:
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self.cell is not None and self.row is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip())
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def html_rows(value: str) -> list[list[str]]:
    parser = TableParser()
    parser.feed(value)
    return parser.rows


def formula_number_for(rows: list[dict[str, Any]], index: int) -> str | None:
    target = bbox(rows[index])
    if not target:
        return None
    center = (target[1] + target[3]) / 2
    candidates = []
    for row in rows:
        if str(row.get("block_label") or "") != "formula_number":
            continue
        match = FORMULA_NUMBER_RE.fullmatch(clean_text(row.get("block_content")))
        other = bbox(row)
        if match and other:
            candidates.append((abs(center - (other[1] + other[3]) / 2), match.group("id"), other))
    if not candidates:
        return None
    distance, number, _ = min(candidates, key=lambda item: item[0])
    return number if distance <= 180 else None


def should_join_pages(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    if previous.get("source_page") == current.get("source_page"):
        return False
    left = str(previous.get("content") or "").rstrip()
    right = str(current.get("content") or "").lstrip()
    if not left or not right or left.endswith((".", "?", "!", ":", ";", "]", ")")):
        return False
    if re.match(r"^(?:Example|Table|Figure|Chapter)\b", right, re.I):
        return False
    return bool(re.match(r"^[a-z(]", right))


def apply_source_text_corrections(source_page: int, text: str) -> str:
    for old, new in SOURCE_TEXT_CORRECTIONS.get(source_page, ()):
        text = text.replace(old, new)
    return text


def join_adjacent_source_text(
    previous: dict[str, Any], current: dict[str, Any]
) -> tuple[str, dict[str, Any] | None]:
    """Join adjacent source blocks, applying only exact visual corrections."""
    left = str(previous.get("content") or "").rstrip()
    right = str(current.get("content") or "").lstrip()
    left_ids = previous.get("source_block_ids") or []
    right_ids = current.get("source_block_ids") or []
    key = (str(left_ids[-1]), str(right_ids[0])) if left_ids and right_ids else ("", "")
    correction = SOURCE_CROSS_PAGE_JOIN_CORRECTIONS.get(key)
    if not correction:
        return left + " " + right, None
    if (
        previous.get("bbox") != correction["left_bbox"]
        or current.get("bbox") != correction["right_bbox"]
        or not left.endswith(correction["left_suffix"])
        or not right.startswith(correction["right_prefix"])
    ):
        raise RuntimeError(f"cross-page correction evidence drifted at {key[0]} / {key[1]}")
    joined = (
        left[: -len(correction["left_suffix"])]
        + correction["replacement"]
        + right[len(correction["right_prefix"]):]
    )
    return joined, correction


def apply_source_block_correction(
    source_page: int, row: dict[str, Any], kind: str, text: str
) -> tuple[str, dict[str, Any] | None]:
    """Apply one exact, source-evidenced Paddle label correction."""
    correction = SOURCE_BLOCK_CORRECTIONS.get((source_page, int(row.get("block_id", -1))))
    if not correction:
        return kind, None
    if (
        kind != correction["expected_label"]
        or text != correction["expected_text"]
        or bbox(row) != correction["bbox"]
    ):
        raise RuntimeError(f"source correction evidence drifted at p{source_page}:b{row.get('block_id')}")
    return str(correction["replacement_label"]), correction


def apply_source_block_split(
    source_page: int, row: dict[str, Any], kind: str, text: str
) -> dict[str, Any] | None:
    """Return one exact source-evidenced heading/body split, if configured."""
    split = SOURCE_BLOCK_SPLITS.get((source_page, int(row.get("block_id", -1))))
    if not split:
        return None
    if (
        kind != split["expected_label"]
        or text != split["expected_text"]
        or bbox(row) != split["bbox"]
    ):
        raise RuntimeError(f"source block split evidence drifted at p{source_page}:b{row.get('block_id')}")
    return split


def source_caption_match(kind: str, text: str, pattern: re.Pattern[str]) -> re.Match[str] | None:
    """Return a caption match only when the PDF layout marks it as a title."""
    return pattern.match(text) if kind == "figure_title" else None


def is_source_heading(kind: str, text: str) -> bool:
    """Keep visually boxed Example labels in the Example extraction path."""
    return kind in HEADING_LABELS and EXAMPLE_RE.match(text) is None


def starts_example_unit(kind: str, text: str) -> bool:
    """Preserve a source content boundary without treating it as a heading."""
    return kind in HEADING_LABELS and EXAMPLE_RE.match(text) is not None


def weighted_median(values: list[tuple[float, float]]) -> float:
    ordered = sorted(values, key=lambda item: item[0])
    total = sum(weight for _, weight in ordered)
    cursor = 0.0
    for value, weight in ordered:
        cursor += weight
        if cursor >= total / 2:
            return value
    return 0.0


def estimate_axis_skew(image: np.ndarray) -> tuple[float, int]:
    """Estimate scanner skew from near-horizontal/vertical long lines."""
    longest = max(image.shape[:2])
    if longest > 1400:
        scale = 1400 / longest
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (3, 3), 0), 50, 160)
    minimum = min(gray.shape)
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 1800,
        threshold=max(20, minimum // 24),
        minLineLength=max(35, minimum // 12),
        maxLineGap=18,
    )
    candidates: list[tuple[float, float]] = []
    for x1, y1, x2, y2 in ([] if lines is None else lines.reshape(-1, 4)):
        angle = math.degrees(math.atan2(float(y2 - y1), float(x2 - x1)))
        deviation = ((angle + 45) % 90) - 45
        length = math.hypot(float(x2 - x1), float(y2 - y1))
        if abs(deviation) <= 6:
            candidates.append((deviation, length))
    if not candidates:
        raise ValueError("no axis-aligned line evidence")
    return weighted_median(candidates), len(candidates)


def rotate_expanded(image: np.ndarray, angle: float) -> np.ndarray:
    height, width = image.shape[:2]
    center = (width / 2, height / 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos = abs(matrix[0, 0])
    sin = abs(matrix[0, 1])
    new_width = int(height * sin + width * cos)
    new_height = int(height * cos + width * sin)
    matrix[0, 2] += new_width / 2 - center[0]
    matrix[1, 2] += new_height / 2 - center[1]
    return cv2.warpAffine(
        image,
        matrix,
        (new_width, new_height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )


def choose_page_deskew(page_image: np.ndarray) -> dict[str, Any]:
    """Try both signs on a source page and accept only a measured improvement."""
    try:
        before, segments = estimate_axis_skew(page_image)
    except ValueError:
        return {"status": "no_page_axis_evidence", "angle": 0.0, "segments": 0}
    if abs(before) < 0.5 or abs(before) > 5.0:
        return {
            "status": "page_unchanged",
            "angle": 0.0,
            "page_skew_before": round(before, 3),
            "page_skew_after": round(before, 3),
            "segments": segments,
        }
    candidates = []
    for correction in (before, -before):
        rotated = rotate_expanded(page_image, correction)
        try:
            residual, residual_segments = estimate_axis_skew(rotated)
        except ValueError:
            continue
        candidates.append((abs(residual), correction, residual, residual_segments))
    if not candidates:
        return {"status": "page_direction_unresolved", "angle": 0.0, "segments": segments}
    _, correction, residual, residual_segments = min(candidates, key=lambda item: item[0])
    if abs(residual) >= abs(before) - 0.1:
        return {
            "status": "page_no_improvement",
            "angle": 0.0,
            "page_skew_before": round(before, 3),
            "page_skew_after": round(residual, 3),
            "segments": segments,
        }
    return {
        "status": "page_deskew_candidate",
        "angle": round(float(correction), 3),
        "page_skew_before": round(before, 3),
        "page_skew_after": round(residual, 3),
        "segments": segments,
        "residual_segments": residual_segments,
    }


def choose_figure_deskew(image: np.ndarray, page_evidence: dict[str, Any]) -> dict[str, Any]:
    """Choose a correction from the figure's own orthogonal baselines.

    Whole-page text supplies a useful candidate direction, but figures can be
    mounted at a different angle.  A correction is accepted only when the
    figure itself has a reliable near-horizontal/vertical baseline and the
    measured residual improves.  Large apparent angles are treated as figure
    content (for example Appendix Figure A2.4), not page rotation.
    """
    evidence_image = image
    longest = max(image.shape[:2])
    if longest > 1400:
        scale = 1400 / longest
        evidence_image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    try:
        before, segments = estimate_axis_skew(evidence_image)
    except ValueError:
        return {"status": "no_figure_axis_evidence", "angle": 0.0, "segments": 0}
    result = {
        "figure_skew_before": round(before, 3),
        "figure_skew_after": round(before, 3),
        "figure_segments": segments,
    }
    if abs(before) < 0.5:
        return {"status": "figure_already_aligned", "angle": 0.0, **result}
    if abs(before) > 3.0:
        return {"status": "figure_direction_unreliable", "angle": 0.0, **result}

    candidates = {before, -before}
    page_angle = float(page_evidence.get("angle") or 0.0)
    if page_evidence.get("status") == "page_deskew_candidate" and page_angle:
        candidates.update({page_angle, -page_angle})
    measured: list[tuple[float, float, float, int]] = []
    for correction in candidates:
        rotated = rotate_expanded(evidence_image, correction)
        try:
            residual, residual_segments = estimate_axis_skew(rotated)
        except ValueError:
            continue
        measured.append((abs(residual), correction, residual, residual_segments))
    if not measured:
        return {"status": "figure_direction_unresolved", "angle": 0.0, **result}
    _, correction, residual, residual_segments = min(measured, key=lambda item: item[0])
    if abs(residual) >= abs(before) - 0.1:
        return {
            "status": "figure_no_improvement", "angle": 0.0,
            **result, "figure_skew_after": round(residual, 3),
        }
    # ``deskew_image`` applies the public, three-decimal angle.  Re-measure
    # that exact angle so the audit reports the pixels actually written rather
    # than a slightly different full-precision candidate.
    applied_correction = round(float(correction), 3)
    residual, residual_segments = estimate_axis_skew(
        rotate_expanded(evidence_image, applied_correction)
    )
    if abs(residual) > 0.5:
        # Hough evidence is discrete: rounding a full-precision optimum can
        # move a line into a neighbouring accumulator bin.  Search only a
        # five-hundredth-degree neighbourhood, and only when the actually
        # applied angle misses the visual acceptance threshold.
        refinements: list[tuple[float, float, float, int]] = []
        for delta in (-0.01, 0.01, -0.02, 0.02, -0.03, 0.03, -0.04, 0.04, -0.05, 0.05):
            refined = round(applied_correction + delta, 3)
            try:
                refined_residual, refined_segments = estimate_axis_skew(
                    rotate_expanded(evidence_image, refined)
                )
            except ValueError:
                continue
            refinements.append((abs(refined_residual), abs(delta), refined, refined_segments))
        if refinements:
            best_abs, _, refined, refined_segments = min(refinements)
            if best_abs < abs(residual):
                applied_correction = refined
                residual = best_abs if residual >= 0 else -best_abs
                # Re-measure to preserve the signed residual, not just its rank.
                residual, residual_segments = estimate_axis_skew(
                    rotate_expanded(evidence_image, applied_correction)
                )
    return {
        "status": "figure_deskew_candidate", "angle": applied_correction,
        **result, "figure_skew_after": round(residual, 3),
        "residual_segments": residual_segments,
    }


def deskew_image(path: Path, audit_dir: Path, page_evidence: dict[str, Any]) -> dict[str, Any]:
    try:
        image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    except OSError:
        image = None
    if image is None:
        return {"path": str(path), "status": "unreadable"}
    figure_evidence = choose_figure_deskew(image, page_evidence)
    angle = float(figure_evidence.get("angle") or 0.0)
    evidence = {**page_evidence, **figure_evidence}
    if figure_evidence.get("status") != "figure_deskew_candidate" or not angle:
        return {**evidence, "path": str(path), "status": "unchanged"}
    rotated = rotate_expanded(image, angle)
    audit_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, audit_dir / f"{path.stem}_original.png")
    encoded, buffer = cv2.imencode(".png", rotated)
    if not encoded:
        return {**evidence, "path": str(path), "status": "encode_failed"}
    buffer.tofile(path)
    return {**evidence, "path": str(path), "status": "deskewed"}


def crop_figure(
    pdf_path: Path,
    page_index: int,
    raw_page: dict[str, Any],
    body: dict[str, Any],
    target: Path,
    caption: dict[str, Any] | None = None,
) -> None:
    body_bbox = bbox(body)
    if not body_bbox:
        raise ValueError("figure body has no bbox")
    pruned = raw_page.get("prunedResult") if isinstance(raw_page.get("prunedResult"), dict) else {}
    rows = page_rows(raw_page)
    boxes = [bbox(row) for row in rows]
    boxes = [item for item in boxes if item]
    raw_width = float(pruned.get("width") or raw_page.get("width") or max((item[2] for item in boxes), default=1))
    raw_height = float(pruned.get("height") or raw_page.get("height") or max((item[3] for item in boxes), default=1))
    doc = fitz.open(pdf_path)
    try:
        page = doc[page_index]
        # Paddle's image bbox is occasionally tight by a few pixels (Figure
        # 7.2 formerly lost the initial "P" in "Probability").  This remains
        # inside the source page and is still checked against the caption bbox.
        margin_x = 24
        margin_top = 12
        # Paddle's image bbox can stop at the plot frame while axis labels extend
        # below it (Figure 21.4 is a concrete source-PDF example).  Keep a wider
        # lower safety band, but never let it cross into the figure caption.
        margin_bottom = 40
        x0, y0, x1, y1 = body_bbox
        caption_box = bbox(caption or {})
        lower_edge = min(raw_height, y1 + margin_bottom)
        if caption_box and caption_box[1] > y0:
            lower_edge = min(lower_edge, caption_box[1] - 8)
        rect = fitz.Rect(
            max(0, x0 - margin_x) * page.rect.width / raw_width,
            max(0, y0 - margin_top) * page.rect.height / raw_height,
            min(raw_width, x1 + margin_x) * page.rect.width / raw_width,
            lower_edge * page.rect.height / raw_height,
        ) & page.rect
        if rect.width < 2 or rect.height < 2:
            raise ValueError(f"invalid figure crop rect {rect}")
        target.parent.mkdir(parents=True, exist_ok=True)
        page.get_pixmap(clip=rect, dpi=300, alpha=False).save(target)
    finally:
        doc.close()


def page_deskew_evidence(pdf_path: Path, page_index: int) -> dict[str, Any]:
    document = fitz.open(pdf_path)
    try:
        pixmap = document[page_index].get_pixmap(dpi=110, alpha=False)
        image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width, pixmap.n)
        if pixmap.n == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return choose_page_deskew(image)
    finally:
        document.close()


def detect_example_rules(pdf_path: Path, page_index: int, raw_page: dict[str, Any]) -> list[float]:
    """Return source-coordinate y positions of long, solid Example borders."""
    pruned = raw_page.get("prunedResult") if isinstance(raw_page.get("prunedResult"), dict) else {}
    boxes = [bbox(row) for row in page_rows(raw_page)]
    boxes = [item for item in boxes if item]
    raw_width = int(pruned.get("width") or raw_page.get("width") or max((item[2] for item in boxes), default=1))
    raw_height = int(pruned.get("height") or raw_page.get("height") or max((item[3] for item in boxes), default=1))
    document = fitz.open(pdf_path)
    try:
        page = document[page_index]
        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(raw_width / page.rect.width, raw_height / page.rect.height),
            alpha=False,
            colorspace=fitz.csGRAY,
        )
        image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width)
    finally:
        document.close()
    binary = cv2.threshold(image, 180, 255, cv2.THRESH_BINARY_INV)[1]
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rules = []
    for contour in contours:
        x, y, width, height = cv2.boundingRect(contour)
        # Example borders are single connected, slightly skewed strokes across
        # most of the type area.  Connected-component geometry cleanly excludes
        # ordinary text baselines and is much faster than page-wide Hough scans.
        if width >= raw_width * 0.72 and height <= raw_width * 0.08 and width / max(height, 1) >= 18:
            rules.append(round(y + height / 2, 1))
    return sorted(rules)


def merge_cross_page_hyphenations(units: list[dict[str, Any]]) -> int:
    """Join source-verified line/page hyphenation even when a table intervenes."""
    merged = 0
    for unit in units:
        blocks = unit.get("blocks") if isinstance(unit.get("blocks"), list) else []
        previous_index: int | None = None
        remove: set[int] = set()
        for index, block in enumerate(blocks):
            content = str(block.get("content") or "")
            if block.get("type") != "discussion" or DIRECT_PLACEHOLDER_RE.fullmatch(content):
                continue
            if previous_index is not None:
                previous = blocks[previous_index]
                left = str(previous.get("content") or "").rstrip()
                right = content.lstrip()
                if (
                    left.endswith("-")
                    and re.match(r"^[a-z]", right)
                    and isinstance(previous.get("source_page"), int)
                    and isinstance(block.get("source_page"), int)
                    and previous["source_page"] < block["source_page"]
                ):
                    previous["content"] = left[:-1] + right
                    previous.setdefault("source_block_ids", []).extend(block.get("source_block_ids") or [])
                    previous["source_page_end"] = block["source_page"]
                    remove.add(index)
                    merged += 1
                    continue
            previous_index = index
        if remove:
            unit["blocks"] = [block for index, block in enumerate(blocks) if index not in remove]
    return merged


def appendix_heading(source_page: int) -> tuple[str, ...] | None:
    return APPENDIX_BOUNDARIES.get(source_page)


def parse_subject_index_raw(workspace: Path) -> dict[int, set[str]]:
    pages = []
    for name in ("Genetics_appendix1_full", "Genetics_appendix1_part2_full", "Genetics_appendix1_part3_full"):
        pages += read_json(workspace / "paddle_output" / name / "intermediate" / "paddle_raw_response.json")
    page_terms: dict[int, set[str]] = defaultdict(set)
    current_main = ""
    # Appendix local page 164 is source page 983, the start of Subject Index.
    for local_index in range(164, len(pages)):
        for row in page_rows(pages[local_index]):
            for line in clean_text(row.get("block_content")).splitlines():
                line = line.strip()
                candidate = re.match(r"^(?P<term>[A-Z][A-Za-z' ×x-]{2,}?)(?:,|\s{2,}|\s+\d|\. See|$)", line)
                if candidate:
                    current_main = candidate.group("term").strip(" ,")
                match = re.match(r"^(?P<term>[A-Za-z][A-Za-z' ×x-]{2,}?),?\s+(?P<pages>\d[\d, –-]*)", line)
                if match:
                    current_main = match.group("term").strip(" ,")
                    pages_text = match.group("pages")
                else:
                    sub = re.match(r"^[a-z][A-Za-z' ×x-]*,?\s+(?P<pages>\d[\d, –-]*)", line)
                    if not sub or not current_main:
                        continue
                    pages_text = sub.group("pages")
                printed_pages = {int(token) for token in re.findall(r"\d+", pages_text)}
                for left, right in re.findall(r"(\d+)\s*[–-]\s*(\d+)", pages_text):
                    if int(right) - int(left) <= 20:
                        printed_pages.update(range(int(left), int(right) + 1))
                for printed in printed_pages:
                    if 1 <= printed <= 972:
                        page_terms[printed + 20].add(current_main)
    return page_terms


def mark_index_terms(text: str, terms: set[str]) -> tuple[str, int]:
    if not terms or not text:
        return text, 0
    parts = re.split(r"(\$[^$]*\$|\[\[[^\]]+\]\])", text)
    marked = 0
    for index in range(0, len(parts), 2):
        segment = parts[index]
        candidates: list[tuple[int, int]] = []
        for term in sorted(terms, key=len, reverse=True):
            pattern = re.compile(rf"(?<!\w){re.escape(term)}(?!\w)", re.I)
            candidates.extend((match.start(), match.end()) for match in pattern.finditer(segment))
        selected: list[tuple[int, int]] = []
        for start, end in sorted(candidates, key=lambda item: (-(item[1] - item[0]), item[0])):
            if any(start < other_end and end > other_start for other_start, other_end in selected):
                continue
            selected.append((start, end))
        for start, end in sorted(selected, reverse=True):
            segment = segment[:start] + "[[" + segment[start:end] + "]]" + segment[end:]
            marked += 1
        parts[index] = segment
    rendered = "".join(parts)
    while "[[[[" in rendered or "]]]]" in rendered:
        rendered = rendered.replace("[[[[", "[[").replace("]]]]", "]]" )
    return rendered, marked


def parse_italic_terms_raw(workspace: Path) -> set[str]:
    pages = []
    for name in ("Genetics_appendix1_full", "Genetics_appendix1_part2_full", "Genetics_appendix1_part3_full"):
        pages += read_json(workspace / "paddle_output" / name / "intermediate" / "paddle_raw_response.json")
    terms: set[str] = set()
    # Organism and Trait Index occupies source pages 973-982, local 154-163.
    for local_index in range(154, min(164, len(pages))):
        for row in page_rows(pages[local_index]):
            text = clean_text(row.get("block_content"))
            terms.update(re.findall(r"\b[A-Z][a-z]{2,}\s+[a-z][a-z-]{2,}\b", text))
    return terms


def mark_italic_terms(text: str, terms: set[str]) -> tuple[str, int]:
    if not terms or not text:
        return text, 0
    parts = re.split(r"(\$[^$]*\$|\[\[[^\]]+\]\]|\*[^*]+\*)", text)
    marked = 0
    for index in range(0, len(parts), 2):
        for term in sorted(terms, key=len, reverse=True):
            pattern = re.compile(rf"(?<!\w)({re.escape(term)})(?!\w)")
            parts[index], count = pattern.subn(r"*\1*", parts[index])
            marked += count
    return "".join(parts), marked


def build_book(workspace: Path, stage: Path) -> dict[str, Any]:
    structured = stage / "data" / "structured"
    figures_dir = stage / "data" / "figures"
    structured.mkdir(parents=True, exist_ok=True)
    background = stage / "data" / "背景资料"
    background.mkdir(parents=True, exist_ok=True)
    for label in RANGES:
        source = workspace / "split_pdfs" / f"Genetics_{label}.pdf"
        shutil.copy2(source, background / source.name)
    formulas: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    figures: list[dict[str, Any]] = []
    figure_keys: set[tuple[str, str]] = set()
    examples: list[dict[str, Any]] = []
    deskew_audit: list[dict[str, Any]] = []
    page_deskew_cache: dict[tuple[str, int], dict[str, Any]] = {}
    table_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    subject_terms = parse_subject_index_raw(workspace)
    italic_terms = parse_italic_terms_raw(workspace)
    style_candidates: list[dict[str, Any]] = []
    applied_source_corrections: list[dict[str, Any]] = []
    bold_terms_marked = 0
    italic_terms_marked = 0
    unit_counts: dict[str, int] = {}
    all_units: list[dict[str, Any]] = []
    example_ref_counts: defaultdict[str, int] = defaultdict(int)
    example_rules_by_page: dict[int, list[float]] = {}

    for label, (start_page, _) in RANGES.items():
        chapter = f"Genetics_{label}"
        ocr_root = workspace / "paddle_output" / f"{chapter}_full"
        raw_pages = read_json(ocr_root / "intermediate" / "paddle_raw_response.json")
        if label == "appendix1":
            for name in ("Genetics_appendix1_part2_full", "Genetics_appendix1_part3_full"):
                raw_pages += read_json(workspace / "paddle_output" / name / "intermediate" / "paddle_raw_response.json")
        pdf_path = workspace / "split_pdfs" / f"{chapter}.pdf"
        example_page_indexes = {
            index
            for index, raw_page in enumerate(raw_pages)
            if any(EXAMPLE_RE.match(clean_text(row.get("block_content"))) for row in page_rows(raw_page))
        }
        rule_page_indexes = {
            candidate
            for index in example_page_indexes
            # Long worked Examples can cross section/unit boundaries and span
            # several pages.  Twenty pages is a guard window only; extraction
            # still stops at the first source-PDF lower border or next Example.
            for candidate in range(index, min(index + 21, len(raw_pages)))
        }
        for local_index in sorted(rule_page_indexes):
            source_page_for_rule = start_page + local_index
            example_rules_by_page[source_page_for_rule] = detect_example_rules(
                pdf_path, local_index, raw_pages[local_index]
            )
        units: list[dict[str, Any]] = []
        heading_path: list[str] = []
        current: dict[str, Any] | None = None
        pending_table: dict[str, Any] | None = None
        suppressed_formula_blocks: dict[str, str] = {}
        formula_index = 0
        example_image_dir = figures_dir / "examples"
        example_image_dir.mkdir(parents=True, exist_ok=True)

        def new_unit(path: list[str], *, heading_only: bool = False) -> dict[str, Any]:
            unit = {
                "id": "",
                "metadata": {
                    "chapter": chapter,
                    "section": path[0] if path else chapter,
                    "subsections": path[1:],
                    "section_level_1": path[0] if path else chapter,
                    "section_level_2": path[1] if len(path) > 1 else None,
                    "heading_path": path,
                    "display_heading": " / ".join(path) if path else chapter,
                    "source_file": "",
                    "source_pdf": "data/背景资料/Genetics.pdf",
                    "source_title": "Genetics and Analysis of Quantitative Traits",
                    "rebuild_provenance": {"method": "paddle_layout_block_rebuild", "remote_llm_calls": 0},
                },
                "blocks": [],
            }
            if heading_only:
                unit["node_kind"] = "heading"
                unit["allow_empty"] = True
            units.append(unit)
            return unit

        for page_index, raw_page in enumerate(raw_pages):
            source_page = start_page + page_index
            forced = appendix_heading(source_page) if label == "appendix1" else None
            if forced:
                heading_path = list(forced)
                current = new_unit(heading_path, heading_only=True)
            rows = page_rows(raw_page)
            for row_index, row in enumerate(rows):
                kind = str(row.get("block_label") or "").strip().lower()
                raw_text = clean_text(row.get("block_content"))
                text = apply_source_text_corrections(source_page, raw_text)
                text_correction = SOURCE_TEXT_CORRECTION_EVIDENCE.get(
                    (source_page, int(row.get("block_id", -1)))
                )
                if text_correction:
                    if bbox(row) != text_correction["bbox"] or any(
                        old not in raw_text for old, _ in text_correction["replacements"]
                    ):
                        raise RuntimeError(
                            f"text correction evidence drifted at p{source_page}:b{row.get('block_id')}"
                        )
                    applied_source_corrections.append({
                        "source_page": source_page,
                        "source_block_id": f"p{source_page}:b{row.get('block_id')}",
                        "bbox": text_correction["bbox"],
                        "replacements": [list(item) for item in text_correction["replacements"]],
                        "reason": text_correction["reason"],
                        "verification": "human_visual_check_against_source_pdf",
                    })
                kind, correction = apply_source_block_correction(source_page, row, kind, text)
                if correction:
                    expected_bbox = correction["bbox"]
                    applied_source_corrections.append({
                        "source_page": source_page,
                        "source_block_id": f"p{source_page}:b{row.get('block_id')}",
                        "bbox": expected_bbox,
                        "original_label": correction["expected_label"],
                        "replacement_label": kind,
                        "text": text,
                        "reason": correction["reason"],
                        "verification": "human_visual_check_against_source_pdf",
                    })
                block_split = apply_source_block_split(source_page, row, kind, text)
                if block_split:
                    split_heading = str(block_split["heading"])
                    heading_path = [heading_path[0], split_heading] if heading_path else [split_heading]
                    current = new_unit(heading_path, heading_only=True)
                    attach_heading_source(current, label, source_page, row)
                    kind = "text"
                    text = str(block_split["body"])
                    applied_source_corrections.append({
                        "source_page": source_page,
                        "source_block_id": f"p{source_page}:b{row.get('block_id')}",
                        "bbox": block_split["bbox"],
                        "original_label": block_split["expected_label"],
                        "split_heading": split_heading,
                        "split_body": text,
                        "reason": block_split["reason"],
                        "verification": "human_visual_check_against_source_pdf",
                    })
                non_body_label = NON_BODY_FIGURE_LABEL_BLOCKS.get(
                    (source_page, int(row.get("block_id", -1)))
                )
                if non_body_label:
                    if raw_text != non_body_label["expected_text"] or bbox(row) != non_body_label["bbox"]:
                        raise RuntimeError(
                            f"non-body figure label evidence drifted at p{source_page}:b{row.get('block_id')}"
                        )
                    applied_source_corrections.append({
                        "source_page": source_page,
                        "source_block_id": f"p{source_page}:b{row.get('block_id')}",
                        "bbox": non_body_label["bbox"],
                        "original_text": raw_text,
                        "replacement": None,
                        "reason": non_body_label["reason"],
                        "verification": "human_visual_check_against_source_pdf",
                    })
                    continue
                # Layout image/chart blocks intentionally have no OCR text, so
                # they must be handled before the generic empty-text filter.
                if kind in {"image", "chart"}:
                    if current is None:
                        title = CHAPTER_TITLES.get(int(label[7:])) if label.startswith("chapter") else None
                        heading_path = [title or chapter]
                        current = new_unit(heading_path)
                    block_id = row.get("block_id", "?")
                    asset_name = f"Genetics_p{source_page}_b{block_id}.png"
                    asset = example_image_dir / asset_name
                    crop_figure(pdf_path, page_index, raw_page, row, asset)
                    current["blocks"].append({
                        "type": "source_image",
                        "content": f"![Source illustration p{source_page} b{block_id}](figures/examples/{asset_name})",
                        **source_meta(label, source_page, row),
                    })
                    continue
                if not text or kind in SKIP_LABELS or kind == "formula_number":
                    continue
                if starts_example_unit(kind, text):
                    # Paddle occasionally labels a worked Example as a paragraph
                    # title. It starts real content, so retain the unit boundary
                    # but never represent it as an empty parent heading.
                    current = new_unit(heading_path)
                if is_source_heading(kind, text):
                    if label == "appendix1" and source_page in APPENDIX_BOUNDARIES:
                        expected = " / ".join(APPENDIX_BOUNDARIES[source_page]).lower()
                        if text.lower() in expected or expected in text.lower():
                            if current is not None:
                                attach_heading_source(current, label, source_page, row)
                            continue
                    if re.fullmatch(r"(?:CHAPTER|Appendix)\s+\w+", text, re.I):
                        continue
                    if label == "chapter4" and text.strip().lower() == "introduction":
                        continue
                    if kind == "doc_title" and label.startswith("chapter"):
                        text = CHAPTER_TITLES.get(int(label[7:]), text)
                    if text.isupper() or not heading_path:
                        heading_path = [text]
                    else:
                        heading_path = [heading_path[0], text]
                    current = new_unit(heading_path, heading_only=True)
                    attach_heading_source(current, label, source_page, row)
                    continue
                if current is None:
                    title = CHAPTER_TITLES.get(int(label[7:])) if label.startswith("chapter") else None
                    heading_path = [title or chapter]
                    current = new_unit(heading_path)

                # A prose paragraph may legitimately start with “Table 11.1
                # gives …”.  Only Paddle's source-layout title blocks are table
                # captions; text-block regex matches must remain body prose.
                table_caption = source_caption_match(kind, text, TABLE_CAPTION_RE)
                if table_caption:
                    pending_table = {
                        "id": table_caption.group("id"), "title": text, "caption_row": row,
                        "source_page": source_page, "unit": current,
                    }
                    continue
                if kind == "table" and pending_table:
                    table_id = pending_table["id"]
                    part_html = text
                    part_bbox = bbox(row)
                    part_source_ids = [f"p{source_page}:b{row.get('block_id', '?')}"]
                    part_notes: list[dict[str, Any]] = []
                    manual_correction = None
                    # Paddle split the bottom of Table 18.3 across one clipped
                    # table block, two formula blocks, and an ordinary text
                    # block. PDF page 588 confirms all three belong inside the
                    # table rules. Keep the formula records as evidence, but do
                    # not render duplicate placeholders above the sunk table.
                    if source_page == 588 and table_id == "18.3":
                        supplements = {
                            int(candidate.get("block_id")): candidate
                            for candidate in rows[row_index + 1 :]
                            if candidate.get("block_id") in {4, 5, 6}
                        }
                        if set(supplements) != {4, 5, 6}:
                            raise RuntimeError("Table 18.3 source supplements are missing on PDF page 588")
                        part_html = re.sub(
                            r'<tr><td></td><td>1</td>.*?</tr>(?=</table>)',
                            "",
                            part_html,
                            flags=re.S,
                        )
                        for block_id in (4, 5):
                            formula_text = apply_source_text_corrections(
                                source_page, clean_text(supplements[block_id].get("block_content"))
                            )
                            part_html = part_html.replace(
                                "</table>",
                                f'<tr><td></td><td colspan="4">{formula_text}</td></tr></table>',
                            )
                            source_id = f"p{source_page}:b{block_id}"
                            part_source_ids.append(source_id)
                            suppressed_formula_blocks[source_id] = table_id
                        boxes = [bbox(row), bbox(supplements[4]), bbox(supplements[5])]
                        boxes = [box for box in boxes if isinstance(box, list)]
                        part_bbox = [
                            min(box[0] for box in boxes), min(box[1] for box in boxes),
                            max(box[2] for box in boxes), max(box[3] for box in boxes),
                        ]
                        manual_correction = {
                            "kind": "paddle_split_table_bottom",
                            "reason": "Paddle clipped the k2 row and split k2/k3/Note from Table 18.3",
                            "source_page": 588,
                            "source_block_ids": ["p588:b3", "p588:b4", "p588:b5", "p588:b6"],
                            "bbox": [129.0, 199.0, 1107.0, 1167.0],
                            "verification": "human_visual_check_against_source_pdf",
                        }
                    elif source_page == 619 and table_id == "20.3":
                        formula_row = next(
                            (
                                candidate for candidate in rows[row_index + 1 :]
                                if candidate.get("block_id") == 4
                                and str(candidate.get("block_label") or "").lower() == "display_formula"
                            ),
                            None,
                        )
                        if formula_row is None:
                            raise RuntimeError("Table 20.3 bottom formula is missing on PDF page 619")
                        part_html = re.sub(
                            r'<tr><td></td><td></td><td>Var\[Cov\(d,s\)\].*?</tr>(?=</table>)',
                            "",
                            part_html,
                            flags=re.S,
                        )
                        formula_text = apply_source_text_corrections(
                            source_page, clean_text(formula_row.get("block_content"))
                        )
                        part_html = part_html.replace(
                            "</table>",
                            f'<tr><td colspan="4">{formula_text}</td></tr></table>',
                        )
                        source_id = "p619:b4"
                        part_source_ids.append(source_id)
                        suppressed_formula_blocks[source_id] = table_id
                        boxes = [bbox(row), bbox(formula_row)]
                        boxes = [box for box in boxes if isinstance(box, list)]
                        part_bbox = [
                            min(box[0] for box in boxes), min(box[1] for box in boxes),
                            max(box[2] for box in boxes), max(box[3] for box in boxes),
                        ]
                        manual_correction = {
                            "kind": "paddle_overlap_table_bottom",
                            "reason": "Paddle table HTML duplicated a clipped formula; PDF formula block is authoritative",
                            "source_page": 619,
                            "source_block_ids": ["p619:b3", "p619:b4"],
                            "bbox": [48.0, 152.0, 1030.0, 1492.0],
                            "verification": "human_visual_check_against_source_pdf",
                        }
                    part = {
                        "page": source_page,
                        "title": pending_table["title"],
                        "html": part_html,
                        "rows": html_rows(part_html),
                        "notes": part_notes,
                        "bbox": part_bbox,
                        "caption_bbox": bbox(pending_table["caption_row"]),
                        "source_block_ids": part_source_ids,
                        "caption_source_block_ids": [
                            f"p{source_page}:b{pending_table['caption_row'].get('block_id', '?')}"
                        ],
                    }
                    if manual_correction:
                        part["manual_correction"] = manual_correction
                    table_key = (chapter, table_id)
                    table = table_by_key.get(table_key)
                    if table is None:
                        table = {
                            "id": table_id, "label_format": f"Table {table_id}",
                            "title": pending_table["title"], "table_type": "numbered",
                            "html": part_html, "rows": part["rows"], "notes": list(part_notes), "parts": [part],
                            "book": "Genetics",
                            "source": {
                                "chapter": chapter, "unit_id": "", "page": source_page,
                                "pages": [source_page], "bbox": part_bbox,
                                "caption_bbox": bbox(pending_table["caption_row"]),
                                "source_pdf": "data/背景资料/Genetics.pdf",
                                "extraction_channel": "paddleocr_layout",
                            },
                        }
                        tables.append(table)
                        table_by_key[table_key] = table
                        current["blocks"].append({"type": "table", "content": f"[[TABLE:{table_id}]]", **source_meta(label, source_page, row)})
                    else:
                        table["parts"].append(part)
                        table["source"].setdefault("pages", []).append(source_page)
                    pending_table["record"] = table
                    pending_table["part"] = part
                    continue
                if (
                    kind == "text"
                    and pending_table
                    and pending_table.get("record")
                    and pending_table["record"].get("notes")
                ):
                    previous_note = pending_table["record"]["notes"][-1]
                    previous_text = str(previous_note.get("content") or "").rstrip()
                    previous_page = int(previous_note.get("source_page_end") or previous_note.get("source_page") or 0)
                    if source_page == previous_page + 1 and not re.search(r"[.!?][\"')\]]?$", previous_text):
                        previous_note["content"] = previous_text + " " + text.lstrip()
                        previous_note["source_page_end"] = source_page
                        previous_note.setdefault("source_block_ids", []).append(
                            f"p{source_page}:b{row.get('block_id', '?')}"
                        )
                        previous_note.setdefault("continuation_bboxes", []).append({
                            "source_page": source_page,
                            "bbox": bbox(row),
                        })
                        source_pages = pending_table["record"]["source"].setdefault("pages", [])
                        if source_page not in source_pages:
                            source_pages.append(source_page)
                        continue
                is_table_note = kind in {"vision_footnote", "footnote"} or (
                    kind == "text" and re.match(r"^(?:Note|Source):\s*", text, re.I)
                )
                if is_table_note and pending_table and pending_table.get("record"):
                    marker_match = re.match(r"^(?P<marker>[*†‡]+)\s*(?P<body>.*)$", text, re.S)
                    note = {
                        "marker": marker_match.group("marker") if marker_match else "",
                        "content": marker_match.group("body") if marker_match else text,
                        "source_page": source_page, "bbox": bbox(row),
                        "source_block_ids": [f"p{source_page}:b{row.get('block_id', '?')}"] ,
                    }
                    pending_table["record"]["notes"].append(note)
                    if pending_table.get("part"):
                        pending_table["part"]["notes"].append(note)
                    continue
                # A display formula split from the bottom of a visually
                # confirmed table must not close the pending-table state;
                # the following source block can still be its Note/Source.
                if f"p{source_page}:b{row.get('block_id', '?')}" not in suppressed_formula_blocks:
                    pending_table = None

                # Likewise, “Figure 5.3 illustrates …” is ordinary prose.  The
                # PDF layout channel labels all actual Genetics captions as
                # figure_title, which is the required source evidence here.
                figure_caption = source_caption_match(kind, text, FIGURE_CAPTION_RE)
                if figure_caption:
                    figure_id = figure_caption.group("id")
                    figure_key = (chapter, figure_id)
                    if figure_key in figure_keys:
                        current["blocks"].append({"type": "discussion", "content": f"[[SEE_FIGURE:{figure_id}]]", **source_meta(label, source_page, row)})
                        continue
                    previous_caption_index = max(
                        (
                            candidate_index
                            for candidate_index, candidate in enumerate(rows[:row_index])
                            if FIGURE_CAPTION_RE.match(clean_text(candidate.get("block_content")))
                            or TABLE_CAPTION_RE.match(clean_text(candidate.get("block_content")))
                        ),
                        default=-1,
                    )
                    components = [
                        candidate
                        for candidate in rows[previous_caption_index + 1 : row_index]
                        if str(candidate.get("block_label") or "").lower() in {"image", "chart"} and bbox(candidate)
                    ]
                    body = None
                    if components:
                        component_boxes = [bbox(candidate) for candidate in components]
                        body = {
                            "block_label": "composite_figure" if len(components) > 1 else components[0].get("block_label"),
                            "block_bbox": [
                                min(item[0] for item in component_boxes), min(item[1] for item in component_boxes),
                                max(item[2] for item in component_boxes), max(item[3] for item in component_boxes),
                            ],
                            "block_id": "+".join(str(candidate.get("block_id", "?")) for candidate in components),
                            "component_block_ids": [candidate.get("block_id", "?") for candidate in components],
                        }
                    if body is None:
                        body = next(
                            (candidate for candidate in rows[row_index + 1 :] if str(candidate.get("block_label") or "").lower() in {"image", "chart"}),
                            None,
                        )
                    if body is None and figure_id == "5.6":
                        components = [candidate for candidate in rows[max(0, row_index - 4) : row_index] if bbox(candidate)]
                        if components:
                            boxes = [bbox(candidate) for candidate in components]
                            body = {
                                "block_label": "composite_formula_figure",
                                "block_bbox": [
                                    min(item[0] for item in boxes), min(item[1] for item in boxes),
                                    max(item[2] for item in boxes), max(item[3] for item in boxes),
                                ],
                                "block_id": "composite-5.6",
                                "component_block_ids": [candidate.get("block_id", "?") for candidate in components],
                            }
                    if body:
                        component_source_ids = {
                            f"p{source_page}:b{block_id}"
                            for block_id in (body.get("component_block_ids") or [body.get("block_id", "?")])
                        }
                        # Image/chart blocks are provisionally retained so
                        # unnumbered illustrations inside worked Examples are
                        # not lost.  Once a real numbered Figure caption is
                        # encountered, remove only its source components.
                        for candidate_unit in units:
                            candidate_unit["blocks"] = [
                                candidate_block
                                for candidate_block in candidate_unit["blocks"]
                                if not (
                                    (
                                        candidate_block.get("type") == "source_image"
                                        or body.get("block_label") == "composite_formula_figure"
                                    )
                                    and component_source_ids.intersection(candidate_block.get("source_block_ids") or [])
                                )
                            ]
                        asset_name = f"Genetics_{figure_id}.png"
                        asset = figures_dir / asset_name
                        crop_figure(pdf_path, page_index, raw_page, body, asset, row)
                        cache_key = (str(pdf_path), page_index)
                        if cache_key not in page_deskew_cache:
                            page_deskew_cache[cache_key] = page_deskew_evidence(pdf_path, page_index)
                        evidence = dict(page_deskew_cache[cache_key])
                        evidence["source_page"] = source_page
                        deskew_audit.append(deskew_image(asset, workspace / "deskew", evidence))
                        figures.append({
                            "id": figure_id, "chapter": chapter, "book": "Genetics",
                            "asset_key": f"Genetics:{chapter}:{figure_id}",
                            "placeholder": f"[[FIGURE:{figure_id}]]", "see_placeholder": f"[[SEE_FIGURE:{figure_id}]]",
                            "asset_path": f"figures/{asset_name}", "caption": text,
                            "source_pdf": "data/背景资料/Genetics.pdf", "page": source_page,
                            "raw_bbox": bbox(body),
                            "source_block_ids": [
                                f"p{source_page}:b{block_id}"
                                for block_id in (body.get("component_block_ids") or [body.get("block_id", "?")])
                            ],
                            "caption_block": source_meta(label, source_page, row),
                        })
                        figure_keys.add(figure_key)
                        current["blocks"].append({"type": "discussion", "content": f"[[FIGURE:{figure_id}]]", **source_meta(label, source_page, row)})
                    continue
                if kind == "display_formula":
                    if (source_page, int(row.get("block_id", -1))) in NON_FORMULA_DISPLAY_BLOCKS:
                        continue
                    formula_bbox = bbox(row)
                    correction_key = (
                        source_page,
                        tuple(formula_bbox) if formula_bbox else (0.0, 0.0, 0.0, 0.0),
                    )
                    corrected_latex = SOURCE_FORMULA_CORRECTIONS.get(correction_key)
                    if corrected_latex is not None:
                        applied_source_corrections.append({
                            "source_page": source_page,
                            "source_block_id": f"p{source_page}:b{row.get('block_id')}",
                            "bbox": formula_bbox,
                            "original_text": text,
                            "replacement_latex": corrected_latex,
                            "reason": "compact two-locus formula OCR contamination",
                            "verification": "human_visual_check_against_source_pdf",
                        })
                        text = f"$$ {corrected_latex} $$"
                    formula_index += 1
                    number = formula_number_for(rows, row_index)
                    formula_id = f"{chapter}_formula{formula_index:03d}"
                    formula = {
                        "id": formula_id, "label_format": f"({number})" if number else None,
                        "latex": text.strip("$ "), "formula_type": "block", "book": "Genetics",
                        "equation_number": number, "number_status": "verified_paddleocr_layout" if number else "verified_unnumbered_paddleocr_layout",
                        "render_mode": "numbered_equation" if number else "display_equation",
                        "source": {
                            "chapter": chapter, "unit_id": "", "page": source_page, "bbox": bbox(row),
                            "source_pdf": "data/背景资料/Genetics.pdf",
                        },
                    }
                    source_id = f"p{source_page}:b{row.get('block_id', '?')}"
                    if source_id in suppressed_formula_blocks:
                        formula["source"]["embedded_in_table"] = suppressed_formula_blocks[source_id]
                    else:
                        current["blocks"].append({"type": "discussion", "content": f"[[FORMULA:{formula_id}]]", **source_meta(label, source_page, row)})
                    formulas.append(formula)
                    continue
                block = {"type": "example" if EXAMPLE_RE.match(text) else "discussion", "content": text, **source_meta(label, source_page, row)}
                # Indexes are candidate locators, not source evidence for font
                # style.  Record candidates in tmp for visual review but do not
                # mutate the delivery unless a page/bbox-scoped correction is
                # explicitly admitted later.
                bold_candidate, count = mark_index_terms(str(block["content"]), subject_terms.get(source_page, set()))
                italic_candidate, italic_count = mark_italic_terms(str(block["content"]), italic_terms)
                if count or italic_count:
                    style_candidates.append({
                        "source_page": source_page,
                        "source_block_ids": block["source_block_ids"],
                        "bbox": block["bbox"],
                        "original": str(block["content"]),
                        "bold_candidate": bold_candidate if count else None,
                        "italic_candidate": italic_candidate if italic_count else None,
                        "status": "candidate_only_not_applied",
                    })
                if current["blocks"] and block["type"] == "discussion" and should_join_pages(current["blocks"][-1], block):
                    previous = current["blocks"][-1]
                    previous["content"], join_correction = join_adjacent_source_text(previous, block)
                    if join_correction:
                        applied_source_corrections.append({
                            "type": "cross_page_word_join",
                            "source_block_ids": [previous["source_block_ids"][-1], block["source_block_ids"][0]],
                            "source_pages": [previous["source_page"], source_page],
                            "left_bbox": join_correction["left_bbox"],
                            "right_bbox": join_correction["right_bbox"],
                            "replacement": join_correction["replacement"],
                            "reason": join_correction["reason"],
                            "verification": "human_visual_check_against_source_pdf",
                        })
                    previous["source_block_ids"].extend(block["source_block_ids"])
                    previous["source_page_end"] = source_page
                else:
                    current["blocks"].append(block)

        merge_cross_page_hyphenations(units)
        # Drop synthetic empty roots but retain intentional heading-only nodes.
        units = [unit for unit in units if unit["blocks"] or unit.get("allow_empty")]
        for unit in units:
            if unit["blocks"]:
                unit.pop("node_kind", None)
                unit.pop("allow_empty", None)
        for index, unit in enumerate(units, 1):
            unit_id = f"{chapter}_{index:03d}"
            unit["id"] = unit_id
            for table in tables:
                if table["source"]["chapter"] == chapter and not table["source"]["unit_id"]:
                    if any(f"[[TABLE:{table['id']}]]" in str(block.get("content") or "") for block in unit["blocks"]):
                        table["source"]["unit_id"] = unit_id
            for formula in formulas:
                if formula["source"]["chapter"] == chapter and not formula["source"]["unit_id"]:
                    if any(f"[[FORMULA:{formula['id']}]]" in str(block.get("content") or "") for block in unit["blocks"]):
                        formula["source"]["unit_id"] = unit_id
                    elif formula["source"].get("embedded_in_table"):
                        owner = table_by_key.get((chapter, str(formula["source"]["embedded_in_table"])))
                        if owner and owner["source"].get("unit_id") == unit_id:
                            formula["source"]["unit_id"] = unit_id
            write_json(structured / f"{unit_id}.json", unit)
        unit_counts[chapter] = len(units)
        all_units.extend(units)

    # Extract Examples from a chapter-wide stream: many worked boxes cross a
    # page boundary that was also (incorrectly) treated as a unit boundary.
    # The source PDF's lower border remains the authoritative endpoint.
    units_by_chapter: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for unit in all_units:
        units_by_chapter[str(unit["metadata"]["chapter"])].append(unit)
    for chapter, chapter_units in units_by_chapter.items():
        flat: list[tuple[dict[str, Any], int, dict[str, Any]]] = [
            (unit, block_index, block)
            for unit in chapter_units
            for block_index, block in enumerate(unit["blocks"])
        ]
        starts = [
            index for index, (_, _, block) in enumerate(flat)
            if EXAMPLE_RE.match(str(block.get("content") or ""))
        ]
        removals: defaultdict[str, set[int]] = defaultdict(set)
        replacements: dict[tuple[str, int], dict[str, Any]] = {}
        for position, flat_index in enumerate(starts):
            unit, block_index, block = flat[flat_index]
            match = EXAMPLE_RE.match(str(block.get("content") or ""))
            assert match is not None
            fallback_end = starts[position + 1] - 1 if position + 1 < len(starts) else len(flat) - 1
            start_page = int(block.get("source_page") or 0)
            start_bbox = block.get("bbox") if isinstance(block.get("bbox"), list) else None
            start_bottom = float(start_bbox[3]) if start_bbox else 0.0
            lower_rule: tuple[int, float] | None = None
            candidate_pages = sorted({
                int(candidate.get("source_page"))
                for _, _, candidate in flat[flat_index : fallback_end + 1]
                if isinstance(candidate.get("source_page"), int)
            })
            for source_page in candidate_pages:
                for rule_y in example_rules_by_page.get(source_page, []):
                    if source_page > start_page or rule_y > start_bottom + 20:
                        lower_rule = (source_page, rule_y)
                        break
                if lower_rule:
                    break
            end_flat = fallback_end
            if lower_rule:
                boundary_page, boundary_y = lower_rule
                accepted = []
                for candidate_index in range(flat_index, fallback_end + 1):
                    _, _, candidate = flat[candidate_index]
                    candidate_page = candidate.get("source_page")
                    candidate_bbox = candidate.get("bbox") if isinstance(candidate.get("bbox"), list) else None
                    if not isinstance(candidate_page, int):
                        continue
                    if candidate_page < boundary_page:
                        accepted.append(candidate_index)
                    elif candidate_page == boundary_page and candidate_bbox and float(candidate_bbox[1]) < boundary_y:
                        accepted.append(candidate_index)
                if accepted:
                    end_flat = max(accepted)
            span_entries = flat[flat_index : end_flat + 1]
            span = [candidate for _, _, candidate in span_entries]
            local = match.group("id")
            heading_root = str((unit.get("metadata") or {}).get("heading_path", [""])[0])
            appendix_match = re.match(r"Appendix\s+(\d+)", heading_root, re.I)
            scope = f"A{appendix_match.group(1)}:" if appendix_match else ""
            base_ref = f"{chapter}:{scope}{local}"
            example_ref_counts[base_ref] += 1
            occurrence = example_ref_counts[base_ref]
            example_ref = base_ref if occurrence == 1 else f"{base_ref}:occ{occurrence}"
            content = "\n\n".join(str(item.get("content") or "") for item in span if str(item.get("content") or "").strip())
            end_unit, end_block_index, _ = flat[end_flat]
            row = {
                "example_id": example_ref, "example_ref": example_ref, "chapter": chapter,
                "label": f"Example {local}", "title": str(block["content"])[:180],
                "source_file": f"{unit['id']}.json", "start_block_index": block_index,
                "end_source_file": f"{end_unit['id']}.json", "end_block_index": end_block_index,
                "block_ids": [item for part in span for item in part.get("source_block_ids", [])],
                "content_markdown": content, "content_plain": re.sub(r"[$*]", "", content),
                "formula_refs": re.findall(r"\[\[FORMULA:([^\]]+)\]\]", content),
                "table_refs": re.findall(r"\[\[TABLE:([^\]]+)\]\]", content),
                "figure_refs": re.findall(r"\[\[FIGURE:([^\]]+)\]\]", content), "external_refs": [],
                "image_refs": re.findall(r"!\[[^\]]*\]\(([^)]+)\)", content),
                "evidence": {
                    "source": "source_pdf_visual_rule_and_paddle_layout_blocks",
                    "detection_method": "chapter_stream_example_heading_plus_pdf_lower_rule",
                    "lower_rule": {"page": lower_rule[0], "y": lower_rule[1]} if lower_rule else None,
                    "confidence": 0.99 if lower_rule else 0.6,
                },
                "metadata": {"needs_review": lower_rule is None, "source_page": block.get("source_page")},
                "placeholder": f"[[SEE_EXAMPLE:{example_ref}]]", "book": "Genetics",
            }
            examples.append(row)
            for span_unit, span_block_index, _ in span_entries:
                removals[span_unit["id"]].add(span_block_index)
            replacements[(unit["id"], block_index)] = {
                "type": "example", "content": f"[[EXAMPLE:{example_ref}]]",
                "source_page": block.get("source_page"), "source_block_ids": row["block_ids"],
                "bbox": block.get("bbox"),
            }
        for unit in chapter_units:
            unit["blocks"] = [
                replacements.get((unit["id"], block_index), block)
                for block_index, block in enumerate(unit["blocks"])
                if block_index not in removals[unit["id"]] or (unit["id"], block_index) in replacements
            ]
            if unit["blocks"]:
                unit.pop("node_kind", None)
                unit.pop("allow_empty", None)
            write_json(structured / f"{unit['id']}.json", unit)

    write_json(structured / "Genetics_formula_library.json", {"version": 1, "book": "Genetics", "asset_type": "formula", "formulas": formulas})
    write_json(structured / "Genetics_table_library.json", {"version": 1, "book": "Genetics", "asset_type": "table", "tables": tables})
    write_json(structured / "Genetics_figure_library.json", {"version": 1, "book": "Genetics", "asset_type": "figure", "figures": figures})
    write_json(
        stage / "data" / "figure_library.json",
        {"version": 2, "figures": {record["asset_key"]: record for record in figures}},
    )
    write_json(structured / "example_library.json", {"schema": "example_library.v1", "examples": examples})
    used_source_images = {
        match
        for unit in all_units
        for block in unit.get("blocks", [])
        for match in re.findall(r"!\[[^\]]*\]\((figures/examples/[^)]+)\)", str(block.get("content") or ""))
    }
    used_source_images.update(
        str(image_ref)
        for example in examples
        for image_ref in example.get("image_refs", [])
        if str(image_ref).startswith("figures/examples/")
    )
    for asset in example_image_dir.glob("*.png"):
        relative = f"figures/examples/{asset.name}"
        if relative not in used_source_images:
            asset.unlink()
    write_json(workspace / "deskew_audit.json", deskew_audit)
    write_json(workspace / "style_candidates.json", style_candidates)
    write_json(workspace / "manual_source_corrections.json", {
        "version": 1,
        "source_pdf": "data/背景资料/Genetics.pdf",
        "corrections": applied_source_corrections,
    })
    return {
        "units": unit_counts, "formulas": len(formulas), "tables": len(tables),
        "figures": len(figures), "examples": len(examples),
        "unnumbered_source_images": len(used_source_images),
        "deskewed": sum(item.get("status") == "deskewed" for item in deskew_audit),
        "bold_terms_marked": bold_terms_marked,
        "italic_terms_marked": italic_terms_marked,
    }


def parse_subject_terms(structured: Path) -> tuple[dict[int, set[str]], list[dict[str, Any]]]:
    page_terms: dict[int, set[str]] = defaultdict(set)
    review: list[dict[str, Any]] = []
    current_main = ""
    for path in sorted(structured.glob("Genetics_appendix1_*.json")):
        unit = read_json(path)
        if "Subject Index" not in str((unit.get("metadata") or {}).get("display_heading") or ""):
            continue
        for block in unit.get("blocks", []):
            for line in str(block.get("content") or "").splitlines():
                line = line.strip()
                candidate = re.match(r"^(?P<term>[A-Z][A-Za-z' ×x-]{2,}?)(?:,|\s{2,}|\s+\d|\. See|$)", line)
                if candidate:
                    current_main = candidate.group("term").strip(" ,")
                match = re.match(r"^(?P<term>[A-Za-z][A-Za-z' ×x-]{2,}?),?\s+(?P<pages>\d[\d, –-]*)", line)
                if not match:
                    sub = re.match(r"^[a-z][A-Za-z' ×x-]*,?\s+(?P<pages>\d[\d, –-]*)", line)
                    if sub and current_main:
                        match_pages = sub.group("pages")
                        terms = [current_main]
                    else:
                        continue
                else:
                    current_main = match.group("term").strip(" ,")
                    match_pages = match.group("pages")
                    terms = [current_main]
                numbers = [int(token) for token in re.findall(r"\d+", match_pages)]
                if not numbers:
                    continue
                expanded: set[int] = set(numbers)
                for left, right in re.findall(r"(\d+)\s*[–-]\s*(\d+)", match_pages):
                    if int(right) - int(left) <= 20:
                        expanded.update(range(int(left), int(right) + 1))
                for printed in expanded:
                    if 1 <= printed <= 972:
                        page_terms[printed + 20].update(terms)
    if not page_terms:
        review.append({"kind": "subject_index", "reason": "no index terms parsed"})
    return page_terms, review


def apply_style_markup(stage: Path) -> dict[str, Any]:
    # The Subject/Organism indexes locate concepts but do not encode whether a
    # particular body-text occurrence is bold or italic.  Applying them as a
    # style oracle caused false bold and nested markers.  Candidate occurrences
    # are retained in tmp/genetics_rebuild/style_candidates.json; the delivery
    # remains unmarked unless a page/bbox-scoped visual correction is admitted.
    structured = stage / "data" / "structured"
    stripped = 0
    style_marker = re.compile(r"\[\[(?!(?:SEE_)?(?:FORMULA|TABLE|FIGURE|EXAMPLE):)([^\[\]]+)\]\]")
    for path in sorted(structured.glob("Genetics_*.json")):
        if not re.match(r"Genetics_(?:chapter\d+|appendix1)_\d{3}\.json$", path.name):
            continue
        unit = read_json(path)
        changed = False
        for block in unit.get("blocks", []):
            content, count = style_marker.subn(r"\1", str(block.get("content") or ""))
            if count:
                block["content"] = content
                stripped += count
                changed = True
            if "style_provenance" in block:
                block.pop("style_provenance", None)
                changed = True
        if changed:
            write_json(path, unit)
    review = [{
        "kind": "index_style_candidates", "status": "not_applied",
        "reason": "Index membership is not source-PDF font evidence.",
    }]
    write_json(stage.parent / "style_review.json", review)
    return {"bold_terms_marked_postpass": 0, "legacy_markers_stripped": stripped, "review_items": 0}


def verify(stage: Path, build: dict[str, Any], style: dict[str, Any]) -> dict[str, Any]:
    data = stage / "data"
    structured = data / "structured"
    errors: list[str] = []
    for label, (start, end) in RANGES.items():
        path = data / "背景资料" / f"Genetics_{label}.pdf"
        if not path.exists():
            errors.append(f"missing split PDF: {path.name}")
            continue
        document = fitz.open(path)
        try:
            if document.page_count != end - start + 1:
                errors.append(f"wrong split page count: {path.name}")
        finally:
            document.close()
    for label in RANGES:
        chapter = f"Genetics_{label}"
        paths = sorted(structured.glob(f"{chapter}_*.json"))
        ids = [read_json(path).get("id") for path in paths]
        expected = [f"{chapter}_{index:03d}" for index in range(1, len(paths) + 1)]
        if ids != expected:
            errors.append(f"non-contiguous ids: {chapter}")
    ch27_pages = [
        block.get("source_page")
        for path in structured.glob("Genetics_chapter27_*.json")
        for block in read_json(path).get("blocks", [])
        if isinstance(block.get("source_page"), int)
    ]
    appendix_pages = [
        block.get("source_page")
        for path in structured.glob("Genetics_appendix1_*.json")
        for block in read_json(path).get("blocks", [])
        if isinstance(block.get("source_page"), int)
    ]
    if ch27_pages and max(ch27_pages) > 818:
        errors.append("chapter27 contains post-818 content")
    if appendix_pages and (min(appendix_pages) < 819 or max(appendix_pages) > 992):
        errors.append("appendix source pages outside 819-992")
    false_intro = any(
        "Introduction" == str((read_json(path).get("metadata") or {}).get("display_heading") or "").split(" / ")[-1]
        for path in structured.glob("Genetics_chapter4_*.json")
    )
    if false_intro:
        errors.append("false chapter4 Introduction remains")
    title_expectations = {
        "Genetics_chapter14": CHAPTER_TITLES[14],
        "Genetics_chapter22": CHAPTER_TITLES[22],
    }
    for chapter, title in title_expectations.items():
        first = next(iter(sorted(structured.glob(f"{chapter}_*.json"))), None)
        if not first or title not in str((read_json(first).get("metadata") or {}).get("display_heading") or ""):
            errors.append(f"wrong title: {chapter}")
    chapter4_units = [read_json(path) for path in sorted(structured.glob("Genetics_chapter4_*.json"))]
    if not any(
        unit.get("allow_empty") and not unit.get("blocks")
        and (unit.get("metadata") or {}).get("display_heading") == "THE TRANSMISSION OF GENETIC INFORMATION"
        for unit in chapter4_units
    ):
        errors.append("empty transmission parent heading missing")
    if not any(
        "Organisms with ploidy levels" in str(block.get("content") or "")
        for unit in chapter4_units for block in unit.get("blocks", [])
    ):
        errors.append("cross-page ploidy sentence was not joined")
    table_library = read_json(structured / "Genetics_table_library.json")
    for table in table_library.get("tables", []):
        note_texts = [re.sub(r"\s+", " ", str(note.get("content") or "")).strip() for note in table.get("notes", [])]
        if len(note_texts) != len(set(note_texts)):
            errors.append(f"duplicate table notes: {table.get('id')}")
    table21 = next((row for row in table_library.get("tables", []) if row.get("id") == "2.1"), None)
    if not table21 or not table21.get("notes"):
        errors.append("Table 2.1 note missing")
    table183 = next((row for row in table_library.get("tables", []) if row.get("id") == "18.3"), None)
    if (
        not table183
        or "k_{2}" not in str(table183.get("html") or "")
        or "k_{3}" not in str(table183.get("html") or "")
        or not table183.get("notes")
    ):
        errors.append("Table 18.3 clipped bottom formulas or note missing")
    table203 = next((row for row in table_library.get("tables", []) if row.get("id") == "20.3"), None)
    table203_note = " ".join(str(note.get("content") or "") for note in (table203 or {}).get("notes", []))
    if not table203 or "\\mathrm{Var}[\\mathrm{Cov}(d,s)" not in str(table203.get("html") or "") or "number of progeny per mating" not in table203_note:
        errors.append("Table 20.3 bottom formula or cross-page note missing")
    table232 = next((row for row in table_library.get("tables", []) if row.get("id") == "23.2"), None)
    if not table232 or not table232.get("notes"):
        errors.append("Table 23.2 text-labelled note missing")
    formula_library = read_json(structured / "Genetics_formula_library.json")
    formula_rows = formula_library.get("formulas", [])
    if len(formula_rows) != 1813:
        errors.append(f"wrong logical formula count: {len(formula_rows)} (expected 1813)")
    if any(
        (row.get("source") or {}).get("page") == 117
        and tuple((row.get("source") or {}).get("bbox") or ())
        in {(296.0, 171.0, 838.0, 332.0), (291.0, 410.0, 832.0, 566.0)}
        for row in formula_rows
    ):
        errors.append("Figure 5.6 chromosome panels remain misclassified as formulas")
    embedded_formula_ids = {
        row.get("id")
        for row in formula_rows
        if (row.get("source") or {}).get("embedded_in_table")
    }
    structured_text = "\n".join(
        path.read_text(encoding="utf-8") for path in structured.glob("Genetics_*_[0-9][0-9][0-9].json")
    )
    if any(f"[[FORMULA:{formula_id}]]" in structured_text for formula_id in embedded_formula_ids):
        errors.append("table-embedded formula still has a duplicate textbook placeholder")
    examples = read_json(structured / "example_library.json").get("examples", [])
    if not examples:
        errors.append("Genetics examples missing")
    refs = [str(row.get("example_ref") or "") for row in examples]
    if len(refs) != len(set(refs)):
        errors.append("duplicate Genetics example refs")
    example2610 = next((row for row in examples if row.get("example_ref") == "Genetics_chapter26:10"), None)
    if not example2610 or "which gives the same estimates as obtained with the permanent-effects model." not in str(example2610.get("content_markdown") or ""):
        errors.append("Example 26.10 cross-page concluding sentence missing")
    figure_rows = read_json(structured / "Genetics_figure_library.json").get("figures", [])
    figure_keys = [(row.get("chapter"), row.get("id")) for row in figure_rows]
    if len(figure_keys) != len(set(figure_keys)):
        errors.append("duplicate Genetics figure keys")
    figure56 = next((row for row in figure_rows if row.get("chapter") == "Genetics_chapter5" and row.get("id") == "5.6"), None)
    if not figure56 or not {"p117:b2", "p117:b3", "p117:b4", "p117:b5"}.issubset(set(figure56.get("source_block_ids") or [])):
        errors.append("Figure 5.6 source components incomplete")

    export_textbooks(
        structured_dir=structured,
        out_dir=data / "textbook",
        chapters={f"Genetics_{label}" for label in RANGES},
        figure_library=data / "figure_library.json",
        book_id="Genetics",
    )
    textbook_figures = data / "textbook" / "figures"
    textbook_figures.mkdir(parents=True, exist_ok=True)
    for figure in (data / "figures").glob("Genetics_*.png"):
        shutil.copy2(figure, textbook_figures / figure.name)
    example_images = data / "figures" / "examples"
    textbook_example_images = textbook_figures / "examples"
    if textbook_example_images.exists():
        shutil.rmtree(textbook_example_images)
    if example_images.exists():
        shutil.copytree(example_images, textbook_example_images)
    unresolved = []
    missing_images = []
    for path in (data / "textbook").glob("Genetics_*_textbook.md"):
        content = path.read_text(encoding="utf-8")
        for match in DIRECT_PLACEHOLDER_RE.finditer(content):
            unresolved.append(f"{path.name}:{match.group(0)}")
        for match in FIGURE_LINK_RE.finditer(content):
            if not (path.parent / match.group("path")).resolve().exists():
                missing_images.append(f"{path.name}:{match.group('path')}")
    if unresolved:
        errors.append(f"unresolved direct placeholders: {len(unresolved)}")
    if missing_images:
        errors.append(f"missing textbook images: {len(missing_images)}")
    report = {
        "valid": not errors, "errors": errors, "build": build, "style": style,
        "chapter27_page_max": max(ch27_pages) if ch27_pages else None,
        "appendix_page_range": [min(appendix_pages), max(appendix_pages)] if appendix_pages else None,
        "table_2_1_notes": len(table21.get("notes", [])) if table21 else 0,
        "examples": len(examples), "unresolved_placeholders": unresolved,
        "missing_textbook_images": missing_images,
        "remote_llm_calls": 0,
    }
    write_json(stage.parent / "verification.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=ROOT / "tmp" / "genetics_rebuild")
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    stage = workspace / "staging"
    if stage.exists():
        shutil.rmtree(stage)
    build = build_book(workspace, stage)
    style = apply_style_markup(stage)
    report = verify(stage, build, style)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
