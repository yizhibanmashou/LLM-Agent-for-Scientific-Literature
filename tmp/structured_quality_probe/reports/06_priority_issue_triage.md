# 06 Priority Issue Triage

本报告只整理修复候选，不执行 repair，不修改 structured。

## 优先级规则

| priority | issue_types | 处理建议 |
| --- | --- | --- |
| P0 | table_reference_missing | 引用完整性问题，先人工确认缺失表格是否应补库或改引用。 |
| P1 | h_only_block, tex_command_leak, unbalanced_inline_math, broken_placeholder, ghost_block | 明显结构残留或语法异常，可作为第一轮清理候选。 |
| P2 | very_short_block, derivation_placeholder_only_text, placeholder_in_discussion, suspicious_truncation | 需要人工判定语境，避免误删合法短文本。 |
| P3 | 其他 | 暂不进入第一轮优化。 |

## issue 分组

| priority | issue_type | count | top_chapters |
| --- | --- | --- | --- |
| P0 | table_reference_missing | 18 | chapter21:6, chapter18:4, chapter8:2, chapter9:2, chapter10:1 |
| P1 | h_only_block | 242 | chapter25:22, chapter29:21, chapter30:20, chapter12:18, chapter21:15 |
| P1 | tex_command_leak | 200 | appendix5:28, chapter22:21, appendix1:15, chapter30:13, appendix2:13 |
| P1 | ghost_block | 7 | chapter8:2, appendix1:2, chapter20:1, chapter26:1, appendix5:1 |
| P1 | unbalanced_inline_math | 5 | chapter9:1, chapter12:1, chapter21:1, chapter22:1, chapter24:1 |
| P2 | very_short_block | 253 | chapter25:22, chapter29:21, chapter30:20, chapter12:18, chapter21:15 |
| P2 | derivation_placeholder_only_text | 12 | chapter5:2, chapter6:2, chapter22:2, chapter9:1, chapter11:1 |
| P2 | placeholder_in_discussion | 9 | chapter23:3, chapter9:2, chapter21:2, chapter8:1, chapter17:1 |
| P2 | suspicious_truncation | 6 | chapter21:2, chapter4:1, chapter10:1, chapter24:1, chapter30:1 |

## P0/P1 代表候选

| issue_type | chapter | file | block | block_type | sample |
| --- | --- | --- | --- | --- | --- |
| table_reference_missing | chapter8 | data/structured/chapter8_006.json | 0 | discussion | We start our discussion of the population-genetic theory of sweeps by first considering hard sweeps and their effects on linked neutral loci. Parts of this discussion are rather technical, but the main theoretical results are summarized in [[SEE_TABLE:8.1]], with the expected signatures from a ha... |
| table_reference_missing | chapter8 | data/structured/chapter8_020.json | 0 | discussion | The key summary parameter for the potential impact of a sweep is the fraction of original haplotypes that stay intact following a sweep, $ f_s = \Delta_q / \delta_q(0) $ (Equation 8.1d). If $ f_s \simeq 1 $, the sweep will have a major impact on the structure of variation at linked neutral sites,... |
| table_reference_missing | chapter9 | data/structured/chapter9_029.json | 1 | derivation | The basic structure of their test (and several extensions) is as follows. Suppose $m$ linked segregating sites from a local chromosomal region of interest are scored in a sample of $n$ chromosomes. Using an outgroup, we can polarize any segregating alleles, determining which are derived. The resu... |
| table_reference_missing | chapter9 | data/structured/chapter9_060.json | 0 | discussion | Early searches in humans looked for molecular signals at candidate genes either believed, or very strongly suspected, to be under selection in particular environments. Examples include disease-resistance genes such as Duffy (FY) and G6PD, dietary genes such as lactase (LCT), and climate-related g... |
| table_reference_missing | chapter10 | data/structured/chapter10_033.json | 0 | discussion | As summarized in [[SEE_TABLE:10.2]], a number of different parameters of adaptive evolution have been introduced in this chapter (as well as in Chapter 8), along with various machinery for estimating them. We have examined the connections between some of these parameters (e.g., Equations 10.16a–1... |
| h_only_block | chapter1 | data/structured/chapter1_001.json | 5 | discussion | [h] |
| h_only_block | chapter2 | data/structured/chapter2_005.json | 4 | discussion | [h] |
| h_only_block | chapter2 | data/structured/chapter2_005.json | 5 | discussion | [h] |
| h_only_block | chapter2 | data/structured/chapter2_007.json | 3 | discussion | [h] |
| h_only_block | chapter2 | data/structured/chapter2_007.json | 6 | discussion | [h] |
| tex_command_leak | chapter1 | data/structured/chapter1_002.json | 2 | discussion | The first population-genetics paper, which predated the rediscovery of Mendel (and hence was published well before any considerations of the actual dynamics of genes), was concerned with a quantitative-genetics question. Fleeming Jenkin, Regius Professor of Engineering at the University of Edinbu... |
| tex_command_leak | chapter2 | data/structured/chapter2_002.json | 7 | discussion | Example 2.1. Consider an initially heterozygous individual Bb in a self-fertilizing line maintained by single-progeny descent. With N = 1, the only three possible allele-frequency states in the population are zero, one, or two B alleles. Denoting the initial state of the population by $ \mathbf{x... |
| tex_command_leak | chapter2 | data/structured/chapter2_002.json | 9 | discussion | The probability of being in any particular allele-frequency category in generation t, which follows from Equation 2.2b, is a function of $ \mathbf{P}^{t} $, so for example, $$ \mathbf{P}^{2}=\begin{pmatrix}{{{1}}}&{{{0}}}&{{{0}}} \\{{{0.375}}}&{{{0.250}}}&{{{0.375}}} \\{{{0}}}&{{{0}}}&{{{1}}}\end... |
| tex_command_leak | chapter2 | data/structured/chapter2_004.json | 2 | discussion | Example 2.2. Ewens (2004) used the following line of reasoning to derive the expected time to absorption of a neutral allele under the Wright-Fisher model. Letting $ \delta p $ denote the change in allele frequency in one unit of time, the mean time to absorption for an allele with frequency p ma... |
| tex_command_leak | chapter2 | data/structured/chapter2_008.json | 8 | proposition | Example 2.5. The preceding expressions can be used to derive the evolutionary (or drift) variance of heterozygosity at a locus under the assumption of Hardy-Weinberg equilibrium, provided there are only two alleles segregating at the locus. Letting $ H_t = 2p_t(1 - p_t) $ denote the heterozygosit... |
| ghost_block | chapter8 | data/structured/chapter8_003.json | 1 | discussion | .. |
| ghost_block | chapter8 | data/structured/chapter8_003.json | 2 | discussion | © |
| ghost_block | chapter20 | data/structured/chapter20_001.json | 5 | discussion | .. |
| ghost_block | chapter26 | data/structured/chapter26_001.json | 6 | discussion | .. |
| ghost_block | appendix1 | data/structured/appendix1_003.json | 2 | discussion | .. |
| unbalanced_inline_math | chapter9 | data/structured/chapter9_034.json | 0 | discussion | Under the infinite-sites model, a sequence is treated as a series of $L$ sites, with each new mutation assumed to occur at a new site (Chapter 4). At mutation-drift equilibrium, most features of this model, including the site-frequency spectrum (SFS), are fully specified by the population-size-sc... |
| unbalanced_inline_math | chapter12 | data/structured/chapter12_029.json | 0 | discussion | Assume that n detected QTL differences (alternative fixed alleles at n loci) are found via a standard QTL mapping experiment involving a cross between two lines (LW Chapter 15). Under neutrality, there should be no systematic directionality as to whether a line is fixed for increasing (plus) alle... |
| unbalanced_inline_math | chapter21 | data/structured/chapter21_015.json | 7 | discussion | $ (n_{f} $ females per male, $ n_{s} $ offspring per female, $ n = n_{f}n_{s} $ offspring per male $ $$ \sigma^{2}\big(\overline{z}_{H S(F S)}\big)=\frac{\sigma_{A}^{2}}{4}\left(1+\frac{1}{n_{f}}+\frac{2}{n}\right)+\frac{\sigma_{D}^{2}}{4n_{f}}\left(1+\frac{3}{n_{s}}\right)+\frac{\sigma_{E_{s}}^{... |
| unbalanced_inline_math | chapter22 | data/structured/chapter22_023.json | 7 | discussion | Example 22.9. As an application of the previous theory, consider a trait where $ \sigma(A_d, A_s) = 0 $, and there are no correlations between environmental values within the group ($ \rho = 0 $) and no relatives in the group ($ r = 0 $). Equation 22.5d gives $ \sigma^2(z) = \sigma^2(A_d) + (n-1)... |
| unbalanced_inline_math | chapter24 | data/structured/chapter24_023.json | 6 | discussion | Equation 24.21a shows how the higher-order cumulants $ (K_{3} $ and above $ quantify departures from normality. If all of these are zero, the distribution is Gaussian. |
