# Structured Quality Audit: early paper2latex structured

本报告是 **structured 可用质量通过率** 审计，不是 OCR 字符级准确率。

## 总览

| 指标 | 值 |
| --- | --- |
| structured_dir | tmp/structured_quality_probe/old_structured |
| 总文件数 | 983 |
| structured JSON 文件数 | 981 |
| 总 block 数 | 5959 |
| formula_library 条目 | 2263 |
| table_library 条目 | 152 |

## block.type 统计

| block.type | 数量 |
| --- | --- |
| discussion | 4033 |
| derivation | 1624 |
| proposition | 271 |
| definition | 31 |

## 严重级别统计

| severity | 数量 |
| --- | --- |
| fatal | 0 |
| error | 16 |
| warning | 33 |
| info | 0 |

## issue_type 统计

| issue_type | 数量 |
| --- | --- |
| very_short_block | 13 |
| derivation_placeholder_only_text | 12 |
| ghost_block | 8 |
| placeholder_in_discussion | 8 |
| unbalanced_inline_math | 5 |
| suspicious_truncation | 3 |

## chapter 统计

| chapter | 数量 |
| --- | --- |
| chapter8 | 7 |
| appendix1 | 5 |
| chapter5 | 3 |
| chapter9 | 3 |
| chapter21 | 3 |
| chapter22 | 3 |
| chapter23 | 3 |
| appendix5 | 2 |
| chapter6 | 2 |
| chapter12 | 2 |
| chapter15 | 2 |
| chapter20 | 2 |
| chapter24 | 2 |
| chapter26 | 2 |
| chapter29 | 2 |
| chapter10 | 1 |
| chapter11 | 1 |
| chapter17 | 1 |
| chapter18 | 1 |
| chapter19 | 1 |
| chapter28 | 1 |

## 关键指标

| metric | value |
| --- | --- |
| strict_pass_rate | 0.997483 |
| weighted_quality_score | 0.997281 |
| formula_reference_valid_rate | 1.000000 |
| table_reference_valid_rate | 1.000000 |
| derivation_reference_valid_rate | 1.000000 |
| ghost_block_rate | 0.001343 |

## 前 50 个问题样例

| rank | severity | issue_type | chapter | file | block | block_type | sample |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | error | ghost_block | chapter8 | tmp/structured_quality_probe/old_structured/chapter8_003.json | 1 | discussion | .. |
| 2 | error | ghost_block | chapter8 | tmp/structured_quality_probe/old_structured/chapter8_003.json | 2 | discussion | © |
| 3 | error | ghost_block | chapter8 | tmp/structured_quality_probe/old_structured/chapter8_031.json | 4 | discussion | 1.2 |
| 4 | error | ghost_block | chapter20 | tmp/structured_quality_probe/old_structured/chapter20_001.json | 5 | discussion | .. |
| 5 | error | ghost_block | chapter26 | tmp/structured_quality_probe/old_structured/chapter26_001.json | 6 | discussion | .. |
| 6 | error | ghost_block | appendix1 | tmp/structured_quality_probe/old_structured/appendix1_003.json | 2 | discussion | .. |
| 7 | error | ghost_block | appendix1 | tmp/structured_quality_probe/old_structured/appendix1_003.json | 3 | discussion | © |
| 8 | error | ghost_block | appendix5 | tmp/structured_quality_probe/old_structured/appendix5_003.json | 4 | discussion | .. |
| 9 | error | unbalanced_inline_math | chapter9 | tmp/structured_quality_probe/old_structured/chapter9_033.json | 0 | discussion | Under the infinite-sites model, a sequence is treated as a series of $L$ sites, with each new mutation assumed to occur at a new site (Chapter 4). At mutation-drift equilibrium, most features of this model, including the site-frequency spectrum (SFS), are fully specified by the population-size-sc... |
| 10 | error | unbalanced_inline_math | chapter12 | tmp/structured_quality_probe/old_structured/chapter12_027.json | 0 | discussion | Assume that n detected QTL differences (alternative fixed alleles at n loci) are found via a standard QTL mapping experiment involving a cross between two lines (LW Chapter 15). Under neutrality, there should be no systematic directionality as to whether a line is fixed for increasing (plus) alle... |
| 11 | error | unbalanced_inline_math | chapter21 | tmp/structured_quality_probe/old_structured/chapter21_015.json | 4 | discussion | $ (n_{f} $ females per male, $ n_{s} $ offspring per female, $ n = n_{f}n_{s} $ offspring per male $ $$ \sigma^{2}\big(\overline{z}_{H S(F S)}\big)=\frac{\sigma_{A}^{2}}{4}\left(1+\frac{1}{n_{f}}+\frac{2}{n}\right)+\frac{\sigma_{D}^{2}}{4n_{f}}\left(1+\frac{3}{n_{s}}\right)+\frac{\sigma_{E_{s}}^{... |
| 12 | error | unbalanced_inline_math | chapter22 | tmp/structured_quality_probe/old_structured/chapter22_022.json | 7 | discussion | Example 22.9. As an application of the previous theory, consider a trait where $ \sigma(A_d, A_s) = 0 $, and there are no correlations between environmental values within the group ( $ \rho = 0 $) and no relatives in the group ( $ r = 0 $). Equation 22.5d gives $ \sigma^2(z) = \sigma^2(A_d) + (n-... |
| 13 | error | unbalanced_inline_math | chapter24 | tmp/structured_quality_probe/old_structured/chapter24_022.json | 6 | discussion | Equation 24.21a shows how the higher-order cumulants $ (K_{3} $ and above $ quantify departures from normality. If all of these are zero, the distribution is Gaussian. |
| 14 | error | suspicious_truncation | chapter10 | tmp/structured_quality_probe/old_structured/chapter10_030.json | 7 | discussion | A variety of likelihood models based on Equation 10.19 are typically tested (much in the same way that one tests subsets of complex segregation analysis models; see LW Chapter |
| 15 | error | suspicious_truncation | chapter24 | tmp/structured_quality_probe/old_structured/chapter24_022.json | 6 | discussion | Equation 24.21a shows how the higher-order cumulants $ (K_{3} $ and above $ quantify departures from normality. If all of these are zero, the distribution is Gaussian. |
| 16 | error | suspicious_truncation | chapter29 | tmp/structured_quality_probe/old_structured/chapter29_036.json | 1 | discussion | Weldon (1901), in one of the first studies of selection on a quantitative trait in nature, |
| 17 | warning | very_short_block | chapter5 | tmp/structured_quality_probe/old_structured/chapter5_019.json | 5 | discussion | [[TABLE:5.2]]). |
| 18 | warning | very_short_block | chapter8 | tmp/structured_quality_probe/old_structured/chapter8_003.json | 1 | discussion | .. |
| 19 | warning | very_short_block | chapter8 | tmp/structured_quality_probe/old_structured/chapter8_003.json | 2 | discussion | © |
| 20 | warning | very_short_block | chapter8 | tmp/structured_quality_probe/old_structured/chapter8_029.json | 5 | discussion | Petrov 2013a). |
| 21 | warning | very_short_block | chapter8 | tmp/structured_quality_probe/old_structured/chapter8_031.json | 4 | discussion | 1.2 |
| 22 | warning | very_short_block | chapter15 | tmp/structured_quality_probe/old_structured/chapter15_005.json | 3 | discussion | This is just a 50 |
| 23 | warning | very_short_block | chapter18 | tmp/structured_quality_probe/old_structured/chapter18_016.json | 1 | discussion | [[TABLE:18.4]]). |
| 24 | warning | very_short_block | chapter20 | tmp/structured_quality_probe/old_structured/chapter20_001.json | 5 | discussion | .. |
| 25 | warning | very_short_block | chapter26 | tmp/structured_quality_probe/old_structured/chapter26_001.json | 6 | discussion | .. |
| 26 | warning | very_short_block | appendix1 | tmp/structured_quality_probe/old_structured/appendix1_001.json | 0 | discussion | Diffusion Theory |
| 27 | warning | very_short_block | appendix1 | tmp/structured_quality_probe/old_structured/appendix1_003.json | 2 | discussion | .. |
| 28 | warning | very_short_block | appendix1 | tmp/structured_quality_probe/old_structured/appendix1_003.json | 3 | discussion | © |
| 29 | warning | very_short_block | appendix5 | tmp/structured_quality_probe/old_structured/appendix5_003.json | 4 | discussion | .. |
| 30 | warning | derivation_placeholder_only_text | chapter5 | tmp/structured_quality_probe/old_structured/chapter5_016.json | 1 | derivation | Hence, [[SEE_FORMULA:5.9b]] |
| 31 | warning | derivation_placeholder_only_text | chapter5 | tmp/structured_quality_probe/old_structured/chapter5_016.json | 3 | derivation | Hence, [[SEE_FORMULA:5.9d]] |
| 32 | warning | derivation_placeholder_only_text | chapter6 | tmp/structured_quality_probe/old_structured/chapter6_006.json | 5 | derivation | Hence, [[SEE_FORMULA:6.13b]] |
| 33 | warning | derivation_placeholder_only_text | chapter6 | tmp/structured_quality_probe/old_structured/chapter6_020.json | 4 | derivation | Thus [[SEE_FORMULA:6.35]] |
| 34 | warning | derivation_placeholder_only_text | chapter9 | tmp/structured_quality_probe/old_structured/chapter9_036.json | 4 | derivation | [[SEE_FORMULA:9.26e]] [[SEE_FORMULA:9.26f]] |
| 35 | warning | derivation_placeholder_only_text | chapter11 | tmp/structured_quality_probe/old_structured/chapter11_014.json | 7 | derivation | [[SEE_FORMULA:11.16]] |
| 36 | warning | derivation_placeholder_only_text | chapter15 | tmp/structured_quality_probe/old_structured/chapter15_006.json | 9 | derivation | Recalling Equation 15.5b, [[SEE_FORMULA:15.13b]] |
| 37 | warning | derivation_placeholder_only_text | chapter19 | tmp/structured_quality_probe/old_structured/chapter19_005.json | 7 | derivation | Note that [[SEE_FORMULA:19.5d]] |
| 38 | warning | derivation_placeholder_only_text | chapter22 | tmp/structured_quality_probe/old_structured/chapter22_011.json | 3 | derivation | Hence, [[SEE_FORMULA:22.12a]] |
| 39 | warning | derivation_placeholder_only_text | chapter22 | tmp/structured_quality_probe/old_structured/chapter22_013.json | 1 | derivation | Here [[SEE_FORMULA:22.15b]] while [[SEE_FORMULA:22.15c]] |
| 40 | warning | derivation_placeholder_only_text | chapter28 | tmp/structured_quality_probe/old_structured/chapter28_023.json | 4 | derivation | If $ x^2 \gg \sigma^2(x) + 2V_s\mu $, then [[SEE_FORMULA:28.23c]] |
| 41 | warning | derivation_placeholder_only_text | chapter29 | tmp/structured_quality_probe/old_structured/chapter29_022.json | 5 | derivation | Thus, [[SEE_FORMULA:29.18b]] |
| 42 | warning | placeholder_in_discussion | chapter9 | tmp/structured_quality_probe/old_structured/chapter9_055.json | 1 | discussion | [[TABLE:9.3]]. [[TABLE:9.1]]. [[TABLE:9.4]]. Starting with the advent of dense-SNP maps and continuing as whole-genome sequencing became economically feasible, candidate-gene studies were replaced by genomic scans, searching the genome without any preconception of what sites might be under select... |
| 43 | warning | placeholder_in_discussion | chapter12 | tmp/structured_quality_probe/old_structured/chapter12_030.json | 4 | discussion | To proceed, Berg and Coop expressed all of the $ a_j $ values as deviations from the grand mean, yielding $ a_j^* = a_j - \bar{a} $. This uses one degree of freedom, and returns the vector $ (\mathbf{a}^*)^T = (a_1^*, a_2^*, \cdots, a_{m-1}^*) $, where one population is dropped. As Berg and Coop ... |
| 44 | warning | placeholder_in_discussion | chapter17 | tmp/structured_quality_probe/old_structured/chapter17_007.json | 8 | discussion | [[TABLE:17.1]]. [[TABLE:17.2]]. [[TABLE:17.2]]. # The Heritability of the Environmental Variance, $ h_{v}^{2} $ Estimates of $ \sigma^{2}(A_{v}) $ under any of the models for $ \sigma_{E}^{2} $ reviewed in Table 17.1 are obtained using fairly complicated likelihood functions on data from sets of ... |
| 45 | warning | placeholder_in_discussion | chapter21 | tmp/structured_quality_probe/old_structured/chapter21_011.json | 5 | discussion | [[TABLE:21.2]]. [[TABLE:21.2]]. [[TABLE:21.2]]. The designs covered in Table 21.1 involve four different relationships (Figure 21.2): (i) $ x_1 = \mathcal{R}_1 $ (a measured sib is a parent of $ y $), (ii) $ x_1 $ and $ \mathcal{R}_1 $ are sibs, (iii) $ \mathcal{R}_1 = P_1 $ (the parent of $ x_1 ... |
| 46 | warning | placeholder_in_discussion | chapter21 | tmp/structured_quality_probe/old_structured/chapter21_012.json | 2 | discussion | [[TABLE:21.2]]. [[TABLE:21.2]]. [[TABLE:21.3]]. This follows because the first covariance, $ \sigma(z_{ij}, y) $, is for parent and offspring $ (\sigma_A^2/2) $, while the second covariance, $ \sigma(z_{ik}, y) $, follows using the appropriate value of $ 2\Theta $ from Table 21.2 (1/8 for half-si... |
| 47 | warning | placeholder_in_discussion | chapter23 | tmp/structured_quality_probe/old_structured/chapter23_009.json | 4 | discussion | Substitution of these results into Equation 21.1 yields the response to a single cycle of selection under various schemes, which are summarized in [[SEE_TABLE:23.1]]. As a comparison of [[SEE_TABLE:23.1]] with its random-mating counterpart ([[SEE_TABLE:21.5]]) shows, for half-sibs, that the selec... |
| 48 | warning | placeholder_in_discussion | chapter23 | tmp/structured_quality_probe/old_structured/chapter23_009.json | 5 | discussion | [[TABLE:23.1]]. As a comparison of [[SEE_TABLE:23.1]] with its random-mating counterpart ([[SEE_TABLE:21.5]]) shows, for half-sibs, that the selection response when using inbred parents $ (f > 0) $ is greater than when using outbred parents ($f=0$). This is also true for full-sibs when $ \sigma_D... |
| 49 | warning | placeholder_in_discussion | chapter23 | tmp/structured_quality_probe/old_structured/chapter23_009.json | 6 | discussion | [[TABLE:23.1]]. As a comparison of [[SEE_TABLE:23.1]] with its random-mating counterpart ([[SEE_TABLE:21.5]]) shows, for half-sibs, that the selection response when using inbred parents $ (f > 0) $ is greater than when using outbred |

## 备注

- 本版审计忽略平衡数学片段内部的合法 LaTeX 命令，因此更适合作为三版客观比较口径。
- 引用有效率检查仍以对应版本自己的 formula/table library 为准。
