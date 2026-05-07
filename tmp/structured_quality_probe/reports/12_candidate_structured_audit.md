# Structured Quality Audit: candidate current_plus_p0p1

本报告是 **structured 可用质量通过率** 审计，不是 OCR 字符级准确率。

## 总览

| 指标 | 值 |
| --- | --- |
| structured_dir | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured |
| 总文件数 | 1007 |
| structured JSON 文件数 | 1005 |
| 总 block 数 | 5889 |
| formula_library 条目 | 2247 |
| table_library 条目 | 152 |

## block.type 统计

| block.type | 数量 |
| --- | --- |
| discussion | 3963 |
| derivation | 1618 |
| proposition | 277 |
| definition | 31 |

## 严重级别统计

| severity | 数量 |
| --- | --- |
| fatal | 3 |
| error | 11 |
| warning | 25 |
| info | 0 |

## issue_type 统计

| issue_type | 数量 |
| --- | --- |
| derivation_placeholder_only_text | 12 |
| placeholder_in_discussion | 9 |
| suspicious_truncation | 6 |
| unbalanced_inline_math | 5 |
| very_short_block | 4 |
| table_reference_missing | 3 |

## chapter 统计

| chapter | 数量 |
| --- | --- |
| chapter21 | 6 |
| chapter9 | 4 |
| chapter5 | 3 |
| chapter22 | 3 |
| chapter23 | 3 |
| chapter6 | 2 |
| chapter8 | 2 |
| chapter15 | 2 |
| chapter24 | 2 |
| appendix1 | 1 |
| chapter4 | 1 |
| chapter10 | 1 |
| chapter11 | 1 |
| chapter12 | 1 |
| chapter13 | 1 |
| chapter17 | 1 |
| chapter18 | 1 |
| chapter19 | 1 |
| chapter28 | 1 |
| chapter29 | 1 |
| chapter30 | 1 |

## 关键指标

| metric | value |
| --- | --- |
| strict_pass_rate | 0.997792 |
| weighted_quality_score | 0.997521 |
| formula_reference_valid_rate | 1.000000 |
| table_reference_valid_rate | 0.991620 |
| derivation_reference_valid_rate | 1.000000 |
| ghost_block_rate | 0.000000 |

## 前 50 个问题样例

| rank | severity | issue_type | chapter | file | block | block_type | sample |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | fatal | table_reference_missing | chapter13 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter13_011.json | 7 | discussion | Under sib selection, the selection unit $ (x) $ is the trait value in sib $ s_1 $, with the correlation between its phenotypic value $ (z_{s_1}) $ and the breeding value $ (A_{s_2}) $ of sib $ s_2 $ being (LW [[SEE_TABLE:7.3]]) $$ \sigma(z_{s_{1}},A_{s_{2}})=\left\{\begin{array}{ll}\sigma_{A}^{2}... |
| 2 | fatal | table_reference_missing | chapter15 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter15_006.json | 0 | discussion | Polyploidy, which is very common in plants and occurs in some animals (e.g., salmonid fishes), can introduce complications in predicting selection response (Gallais 2003). In particular, the dynamics of selection response for autotetraploids with dominance is very similar to the dynamics of diplo... |
| 3 | fatal | table_reference_missing | chapter21 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter21_024.json | 1 | derivation | Recalling that the among-group variance equals the within-group covariance (LW Chapter 18), the among-family genetic variance, $ \sigma_{GF}^{2} $, with arbitrary epistasis immediately follows from the genetic covariance between sibs (LW [[SEE_TABLE:7.2]]), [[SEE_FORMULA:21.26a]] |
| 4 | error | suspicious_truncation | chapter4 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter4_011.json | 2 | discussion | It is notable that even though prokaryotes do not engage in meiosis, estimates of c/u for such species are generally of the same order of magnitude as those for eukaryotes (Lynch |
| 5 | error | suspicious_truncation | chapter10 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter10_030.json | 7 | discussion | A variety of likelihood models based on Equation 10.19 are typically tested (much in the same way that one tests subsets of complex segregation analysis models; see LW Chapter |
| 6 | error | suspicious_truncation | chapter21 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter21_004.json | 0 | discussion | While animal breeders typically employ only a few standard sib-based designs (Turner and |
| 7 | error | suspicious_truncation | chapter21 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter21_015.json | 3 | discussion | In the animal-breeding literature, this equation is often more compactly written in terms of t, the phenotypic correlation between sibs (the intraclass correlation coefficient; see |
| 8 | error | suspicious_truncation | chapter24 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter24_023.json | 6 | discussion | Equation 24.21a shows how the higher-order cumulants $ (K_{3} $ and above $ quantify departures from normality. If all of these are zero, the distribution is Gaussian. |
| 9 | error | suspicious_truncation | chapter30 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter30_027.json | 3 | discussion | The impact of publication bias, which is also called the "file-drawer effect" (Rosenthal |
| 10 | error | unbalanced_inline_math | chapter9 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter9_034.json | 0 | discussion | Under the infinite-sites model, a sequence is treated as a series of $L$ sites, with each new mutation assumed to occur at a new site (Chapter 4). At mutation-drift equilibrium, most features of this model, including the site-frequency spectrum (SFS), are fully specified by the population-size-sc... |
| 11 | error | unbalanced_inline_math | chapter12 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter12_029.json | 0 | discussion | Assume that n detected QTL differences (alternative fixed alleles at n loci) are found via a standard QTL mapping experiment involving a cross between two lines (LW Chapter 15). Under neutrality, there should be no systematic directionality as to whether a line is fixed for increasing (plus) alle... |
| 12 | error | unbalanced_inline_math | chapter21 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter21_015.json | 7 | discussion | $ (n_{f} $ females per male, $ n_{s} $ offspring per female, $ n = n_{f}n_{s} $ offspring per male $ $$ \sigma^{2}\big(\overline{z}_{H S(F S)}\big)=\frac{\sigma_{A}^{2}}{4}\left(1+\frac{1}{n_{f}}+\frac{2}{n}\right)+\frac{\sigma_{D}^{2}}{4n_{f}}\left(1+\frac{3}{n_{s}}\right)+\frac{\sigma_{E_{s}}^{... |
| 13 | error | unbalanced_inline_math | chapter22 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter22_023.json | 7 | discussion | Example 22.9. As an application of the previous theory, consider a trait where $ \sigma(A_d, A_s) = 0 $, and there are no correlations between environmental values within the group ($ \rho = 0 $) and no relatives in the group ($ r = 0 $). Equation 22.5d gives $ \sigma^2(z) = \sigma^2(A_d) + (n-1)... |
| 14 | error | unbalanced_inline_math | chapter24 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter24_023.json | 6 | discussion | Equation 24.21a shows how the higher-order cumulants $ (K_{3} $ and above $ quantify departures from normality. If all of these are zero, the distribution is Gaussian. |
| 15 | warning | derivation_placeholder_only_text | chapter5 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter5_016.json | 1 | derivation | Hence, [[SEE_FORMULA:5.9b]] |
| 16 | warning | derivation_placeholder_only_text | chapter5 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter5_016.json | 3 | derivation | Hence, [[SEE_FORMULA:5.9d]] |
| 17 | warning | derivation_placeholder_only_text | chapter6 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter6_007.json | 4 | derivation | Hence, [[SEE_FORMULA:6.13b]] |
| 18 | warning | derivation_placeholder_only_text | chapter6 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter6_023.json | 4 | derivation | Thus [[SEE_FORMULA:6.35]] |
| 19 | warning | derivation_placeholder_only_text | chapter9 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter9_038.json | 3 | derivation | [h] [[SEE_FORMULA:9.26e]] [[SEE_FORMULA:9.26f]] |
| 20 | warning | derivation_placeholder_only_text | chapter11 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter11_013.json | 7 | derivation | [h] [[SEE_FORMULA:11.16]] |
| 21 | warning | derivation_placeholder_only_text | chapter15 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter15_007.json | 9 | derivation | Recalling Equation 15.5b, [[SEE_FORMULA:15.13b]] |
| 22 | warning | derivation_placeholder_only_text | chapter19 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter19_005.json | 7 | derivation | Note that [[SEE_FORMULA:19.5d]] |
| 23 | warning | derivation_placeholder_only_text | chapter22 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter22_012.json | 3 | derivation | Hence, [[SEE_FORMULA:22.12a]] |
| 24 | warning | derivation_placeholder_only_text | chapter22 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter22_014.json | 1 | derivation | Here [[SEE_FORMULA:22.15b]] while [[SEE_FORMULA:22.15c]] |
| 25 | warning | derivation_placeholder_only_text | chapter28 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter28_023.json | 4 | derivation | If $ x^2 \gg \sigma^2(x) + 2V_s\mu $, then [[SEE_FORMULA:28.23c]] |
| 26 | warning | derivation_placeholder_only_text | chapter29 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter29_022.json | 5 | derivation | Thus, [[SEE_FORMULA:29.18b]] |
| 27 | warning | placeholder_in_discussion | chapter8 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter8_020.json | 0 | discussion | The key summary parameter for the potential impact of a sweep is the fraction of original haplotypes that stay intact following a sweep, $ f_s = \Delta_q / \delta_q(0) $ (Equation 8.1d). If $ f_s \simeq 1 $, the sweep will have a major impact on the structure of variation at linked neutral sites,... |
| 28 | warning | placeholder_in_discussion | chapter9 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter9_059.json | 1 | discussion | [[TABLE:9.4]]), and Carlson et al. (2005), who used outliers in Tajima's D ([[SEE_TABLE:9.1]]). As shown in [[SEE_TABLE:9.4]], of the 455 sites detected by Voight, 125 (27%) were also seen by Wang. Conversely, of the 176 sites with outliers in D, only 6% (11) of these were also detected by Voight... |
| 29 | warning | placeholder_in_discussion | chapter9 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter9_060.json | 1 | discussion | Starting with the advent of dense-SNP maps and continuing as whole-genome sequencing became economically feasible, candidate-gene studies were replaced by genomic scans, searching the genome without any preconception of what sites might be under selection. Biswas and Akey (2006) reviewed six earl... |
| 30 | warning | placeholder_in_discussion | chapter17 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter17_009.json | 0 | discussion | Estimates of $ \sigma^{2}(A_{v}) $ under any of the models for $ \sigma_{E}^{2} $ reviewed in [[SEE_TABLE:17.1]] are obtained using fairly complicated likelihood functions on data from sets of relatives; see SanCristobal-Gaudy et al. (1998, 2001), Sorensen and Waagepetersen (2003), Ros et al. (20... |
| 31 | warning | placeholder_in_discussion | chapter21 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter21_011.json | 5 | discussion | [[TABLE:21.2]] involve four different relationships (Figure 21.2): (i) $ x_1 = \mathcal{R}_1 $ (a measured sib is a parent of $ y $), (ii) $ x_1 $ and $ \mathcal{R}_1 $ are sibs, (iii) $ \mathcal{R}_1 = P_1 $ (the parent of $ x_1 $), and (iv) $ \mathcal{R}_1 $ is the selfed-progeny of the parent ... |
| 32 | warning | placeholder_in_discussion | chapter21 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter21_012.json | 2 | discussion | This follows because the first covariance, $ \sigma(z_{ij}, y) $, is for parent and offspring $ (\sigma_A^2/2) $, while the second covariance, $ \sigma(z_{ik}, y) $, follows using the appropriate value of $ 2\Theta $ from [[SEE_TABLE:21.2]] (1/8 for half-sibs and 1/4 for full-sibs). Using the res... |
| 33 | warning | placeholder_in_discussion | chapter23 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter23_009.json | 4 | discussion | Substitution of these results into Equation 21.1 yields the response to a single cycle of selection under various schemes, which are summarized in [[SEE_TABLE:23.1]]. As a comparison of [[SEE_TABLE:23.1]] with its random-mating counterpart ([[SEE_TABLE:21.5]]) shows, for half-sibs, that the selec... |
| 34 | warning | placeholder_in_discussion | chapter23 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter23_009.json | 5 | discussion | [[TABLE:23.1]]. As a comparison of [[SEE_TABLE:23.1]] with its random-mating counterpart ([[SEE_TABLE:21.5]]) shows, for half-sibs, that the selection response when using inbred parents $ (f > 0) $ is greater than when using outbred parents ($f=0$). This is also true for full-sibs when $\sigma_D^... |
| 35 | warning | placeholder_in_discussion | chapter23 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter23_009.json | 6 | discussion | [[TABLE:23.1]]. As a comparison of [[SEE_TABLE:23.1]] with its random-mating counterpart ([[SEE_TABLE:21.5]]) shows, for half-sibs, that the selection response when using inbred parents $ (f > 0) $ is greater than when using outbred |
| 36 | warning | very_short_block | chapter5 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter5_019.json | 5 | discussion | [[TABLE:5.2]]). |
| 37 | warning | very_short_block | chapter8 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter8_029.json | 5 | discussion | Petrov 2013a). |
| 38 | warning | very_short_block | chapter18 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/chapter18_016.json | 1 | discussion | [[TABLE:18.4]]). |
| 39 | warning | very_short_block | appendix1 | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured/appendix1_001.json | 0 | discussion | Diffusion Theory |

## 备注

- 本版审计忽略平衡数学片段内部的合法 LaTeX 命令，因此更适合作为三版客观比较口径。
- 引用有效率检查仍以对应版本自己的 formula/table library 为准。
