# 01 Structured Quality Audit

本报告是 **structured 可用质量通过率** 审计，不是 OCR 字符级准确率。

## 总览

| 指标 | 值 |
| --- | --- |
| 总文件数 | 1007 |
| 总 block 数 | 6138 |

## block.type 统计

| block.type | 数量 |
| --- | --- |
| discussion | 4212 |
| derivation | 1618 |
| proposition | 277 |
| definition | 31 |

## 严重级别统计

| severity | 数量 |
| --- | --- |
| fatal | 18 |
| error | 460 |
| warning | 274 |
| info | 0 |

## issue_type 统计

| issue_type | 数量 |
| --- | --- |
| very_short_block | 253 |
| h_only_block | 242 |
| tex_command_leak | 200 |
| table_reference_missing | 18 |
| derivation_placeholder_only_text | 12 |
| placeholder_in_discussion | 9 |
| ghost_block | 7 |
| suspicious_truncation | 6 |
| unbalanced_inline_math | 5 |

## chapter 统计

| chapter | 数量 |
| --- | --- |
| chapter30 | 54 |
| chapter21 | 51 |
| chapter25 | 48 |
| chapter29 | 48 |
| appendix5 | 42 |
| chapter12 | 38 |
| chapter18 | 36 |
| chapter22 | 34 |
| chapter8 | 28 |
| chapter5 | 26 |
| appendix4 | 25 |
| chapter20 | 25 |
| chapter24 | 22 |
| appendix2 | 21 |
| appendix1 | 20 |
| chapter26 | 20 |
| chapter9 | 19 |
| chapter2 | 18 |
| chapter19 | 18 |
| chapter6 | 17 |
| chapter11 | 16 |
| chapter16 | 15 |
| chapter23 | 14 |
| appendix3 | 13 |
| chapter28 | 13 |
| appendix6 | 12 |
| chapter15 | 12 |
| chapter27 | 12 |
| chapter14 | 10 |
| chapter7 | 6 |
| chapter13 | 6 |
| chapter4 | 5 |
| chapter10 | 4 |
| chapter1 | 3 |
| chapter17 | 1 |

## 关键指标

| metric | value |
| --- | --- |
| strict_pass_rate | 0.922939 |
| weighted_quality_score | 0.943174 |
| formula_reference_valid_rate | 1.000000 |
| table_reference_valid_rate | 0.949721 |
| derivation_reference_valid_rate | 1.000000 |
| ghost_block_rate | 0.001140 |

## 前 50 个问题样例

| rank | severity | issue_type | chapter | file | block | block_type | sample |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | fatal | table_reference_missing | chapter8 | data/structured/chapter8_006.json | 0 | discussion | We start our discussion of the population-genetic theory of sweeps by first considering hard sweeps and their effects on linked neutral loci. Parts of this discussion are rather technical, but the main theoretical results are summarized in [[SEE_TABLE:8.1]], with the expected signatures from a ha... |
| 2 | fatal | table_reference_missing | chapter8 | data/structured/chapter8_020.json | 0 | discussion | The key summary parameter for the potential impact of a sweep is the fraction of original haplotypes that stay intact following a sweep, $ f_s = \Delta_q / \delta_q(0) $ (Equation 8.1d). If $ f_s \simeq 1 $, the sweep will have a major impact on the structure of variation at linked neutral sites,... |
| 3 | fatal | table_reference_missing | chapter9 | data/structured/chapter9_029.json | 1 | derivation | The basic structure of their test (and several extensions) is as follows. Suppose $m$ linked segregating sites from a local chromosomal region of interest are scored in a sample of $n$ chromosomes. Using an outgroup, we can polarize any segregating alleles, determining which are derived. The resu... |
| 4 | fatal | table_reference_missing | chapter9 | data/structured/chapter9_060.json | 0 | discussion | Early searches in humans looked for molecular signals at candidate genes either believed, or very strongly suspected, to be under selection in particular environments. Examples include disease-resistance genes such as Duffy (FY) and G6PD, dietary genes such as lactase (LCT), and climate-related g... |
| 5 | fatal | table_reference_missing | chapter10 | data/structured/chapter10_033.json | 0 | discussion | As summarized in [[SEE_TABLE:10.2]], a number of different parameters of adaptive evolution have been introduced in this chapter (as well as in Chapter 8), along with various machinery for estimating them. We have examined the connections between some of these parameters (e.g., Equations 10.16a–1... |
| 6 | fatal | table_reference_missing | chapter13 | data/structured/chapter13_011.json | 7 | discussion | Under sib selection, the selection unit $ (x) $ is the trait value in sib $ s_1 $, with the correlation between its phenotypic value $ (z_{s_1}) $ and the breeding value $ (A_{s_2}) $ of sib $ s_2 $ being (LW [[SEE_TABLE:7.3]]) $$ \sigma(z_{s_{1}},A_{s_{2}})=\left\{\begin{array}{ll}\sigma_{A}^{2}... |
| 7 | fatal | table_reference_missing | chapter15 | data/structured/chapter15_006.json | 0 | discussion | Polyploidy, which is very common in plants and occurs in some animals (e.g., salmonid fishes), can introduce complications in predicting selection response (Gallais 2003). In particular, the dynamics of selection response for autotetraploids with dominance is very similar to the dynamics of diplo... |
| 8 | fatal | table_reference_missing | chapter18 | data/structured/chapter18_023.json | 4 | discussion | Divergent selection without a control line. $$ f_{t}=f_{u,t}+f_{d,t},\qquad A=\frac{1}{N_{u}}+\frac{1}{N_{d}},\qquad B_{t}=\frac{1}{M_{u,t}}+\frac{1}{M_{d,t}}\quad for t\geq0 $$ where the (design-specific) coefficients, A and $ B_t $, are given in [[SEE_TABLE:18.7]]. If the number of reproducing ... |
| 9 | fatal | table_reference_missing | chapter18 | data/structured/chapter18_024.json | 0 | derivation | When does using a control population in a undirectional selection experiment reduce the variance in response? Equation 18.30a, along with the coefficients from [[SEE_TABLE:18.7]], gives the expected variance with and without the use of a control. Assuming $ M = M_s = M_c $ and $ N = N_s = N_c $, ... |
| 10 | fatal | table_reference_missing | chapter18 | data/structured/chapter18_025.json | 0 | derivation | As Equation 18.31b illustrates, it is not entirely obvious which design is optimal. What in general can we say? The coefficient of variation (CV) of the selection response [[SEE_FORMULA:18.33]] is especially useful in comparing efficiencies of different designs, as it is independent of $ \sigma_{... |
| 11 | fatal | table_reference_missing | chapter18 | data/structured/chapter18_027.json | 2 | discussion | If the number sampled and number used as parents within a replicate are $ M^* = M/r $ and $ N^* = N/r $, respectively, then it is easily seen from [[SEE_TABLE:18.8]] that the variance of a replicate line is simply r times the variance of a population with N and M. Hence, variance in the sample me... |
| 12 | fatal | table_reference_missing | chapter20 | data/structured/chapter20_017.json | 1 | discussion | The animal model has generally been quite successful in the analysis of artificial selection experiments and breeding programs (Chapter 19). However, natural populations differ in fundamental ways from these more controlled settings, leading to a number of design issues ([[SEE_TABLE:20.1]]). Firs... |
| 13 | fatal | table_reference_missing | chapter21 | data/structured/chapter21_012.json | 2 | discussion | This follows because the first covariance, $ \sigma(z_{ij}, y) $, is for parent and offspring $ (\sigma_A^2/2) $, while the second covariance, $ \sigma(z_{ik}, y) $, follows using the appropriate value of $ 2\Theta $ from [[SEE_TABLE:21.2]] (1/8 for half-sibs and 1/4 for full-sibs). Using the res... |
| 14 | fatal | table_reference_missing | chapter21 | data/structured/chapter21_014.json | 5 | discussion | The covariance for strict within-family (WF) selection is slightly different (with $r$ replacing $r_n$; see [[SEE_TABLE:21.3]]), as the appropriate covariance here is $\sigma(z_{ij} - \mu_i, y)$, with $\mu_i$ in place of $\overline{z}_i$. The rankings of individuals under WF selection is simply t... |
| 15 | fatal | table_reference_missing | chapter21 | data/structured/chapter21_014.json | 6 | discussion | A few simple rules emerge from [[SEE_TABLE:21.3]]. The number, $n$, of measured sibs only influences the covariance for family selection and family-deviations selection. Even in these cases, its effect is small unless the number of sibs is small. Under sib selection (and family selection ignoring... |
| 16 | fatal | table_reference_missing | chapter21 | data/structured/chapter21_017.json | 0 | discussion | The formal development of the response equations for any particular design follows from the generalized breeder's equation (Equations 21.1 through 21.4), using the appropriate selection-unit variance ([[SEE_TABLE:21.4]]) and selection unit-offspring covariance ([[SEE_TABLE:21.3]]). Results for a ... |
| 17 | fatal | table_reference_missing | chapter21 | data/structured/chapter21_024.json | 1 | derivation | Recalling that the among-group variance equals the within-group covariance (LW Chapter 18), the among-family genetic variance, $ \sigma_{GF}^{2} $, with arbitrary epistasis immediately follows from the genetic covariance between sibs (LW [[SEE_TABLE:7.2]]), [[SEE_FORMULA:21.26a]] |
| 18 | fatal | table_reference_missing | chapter21 | data/structured/chapter21_037.json | 0 | derivation | Once again, either Equations 21.1a or 21.4a can be used to predict the single-generation response to selection. Taking x = I returns [[SEE_FORMULA:21.51]] where $ \sigma(I,y\|\mathcal{R}_{1}) $ is the covariance between the index value, $ I $, of a parent and the phenotype of its offspring, $ y $.... |
| 19 | error | h_only_block | chapter1 | data/structured/chapter1_001.json | 5 | discussion | [h] |
| 20 | error | h_only_block | chapter2 | data/structured/chapter2_005.json | 4 | discussion | [h] |
| 21 | error | h_only_block | chapter2 | data/structured/chapter2_005.json | 5 | discussion | [h] |
| 22 | error | h_only_block | chapter2 | data/structured/chapter2_007.json | 3 | discussion | [h] |
| 23 | error | h_only_block | chapter2 | data/structured/chapter2_007.json | 6 | discussion | [h] |
| 24 | error | h_only_block | chapter2 | data/structured/chapter2_008.json | 7 | discussion | [h] |
| 25 | error | h_only_block | chapter2 | data/structured/chapter2_018.json | 1 | discussion | [h] |
| 26 | error | h_only_block | chapter4 | data/structured/chapter4_015.json | 3 | discussion | [h] |
| 27 | error | h_only_block | chapter4 | data/structured/chapter4_015.json | 4 | discussion | [h] |
| 28 | error | h_only_block | chapter5 | data/structured/chapter5_003.json | 4 | discussion | [h] |
| 29 | error | h_only_block | chapter5 | data/structured/chapter5_003.json | 5 | discussion | [h] |
| 30 | error | h_only_block | chapter5 | data/structured/chapter5_003.json | 6 | discussion | [h] |
| 31 | error | h_only_block | chapter5 | data/structured/chapter5_003.json | 7 | discussion | [h] |
| 32 | error | h_only_block | chapter5 | data/structured/chapter5_013.json | 1 | discussion | [h] |
| 33 | error | h_only_block | chapter5 | data/structured/chapter5_013.json | 2 | discussion | [h] |
| 34 | error | h_only_block | chapter5 | data/structured/chapter5_013.json | 3 | discussion | [h] |
| 35 | error | h_only_block | chapter5 | data/structured/chapter5_025.json | 4 | discussion | [h] |
| 36 | error | h_only_block | chapter6 | data/structured/chapter6_008.json | 8 | discussion | [h] |
| 37 | error | h_only_block | chapter6 | data/structured/chapter6_008.json | 9 | discussion | [h] |
| 38 | error | h_only_block | chapter6 | data/structured/chapter6_012.json | 1 | discussion | [h] |
| 39 | error | h_only_block | chapter6 | data/structured/chapter6_013.json | 6 | discussion | [h] |
| 40 | error | h_only_block | chapter6 | data/structured/chapter6_014.json | 5 | discussion | [h] |
| 41 | error | h_only_block | chapter6 | data/structured/chapter6_021.json | 5 | discussion | [h] |
| 42 | error | h_only_block | chapter6 | data/structured/chapter6_021.json | 6 | discussion | [h] |
| 43 | error | h_only_block | chapter7 | data/structured/chapter7_006.json | 1 | discussion | [h] |
| 44 | error | h_only_block | chapter7 | data/structured/chapter7_006.json | 11 | discussion | [h] |
| 45 | error | h_only_block | chapter7 | data/structured/chapter7_008.json | 4 | discussion | [h] |
| 46 | error | h_only_block | chapter8 | data/structured/chapter8_003.json | 3 | discussion | [h] |
| 47 | error | h_only_block | chapter8 | data/structured/chapter8_004.json | 1 | discussion | [h] |
| 48 | error | h_only_block | chapter8 | data/structured/chapter8_004.json | 2 | discussion | [h] |
| 49 | error | h_only_block | chapter8 | data/structured/chapter8_004.json | 3 | discussion | [h] |
| 50 | error | h_only_block | chapter8 | data/structured/chapter8_016.json | 3 | discussion | [h] |

## 备注

- 这些数值反映的是结构化输出是否可用、是否值得进入下游知识抽取与人工复核。
- 如果只看 OCR 字符级正确率，会错过 structured 层面最关键的引用断裂、占位符破损和块级噪声问题。
