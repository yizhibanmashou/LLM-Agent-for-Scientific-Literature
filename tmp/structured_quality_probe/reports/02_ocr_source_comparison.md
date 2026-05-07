# 02 OCR Source Comparison

本报告说明：PaddleOCR 和 GLM-OCR 都有问题，因此不能直接把任一边当作绝对 ground truth。

## 来源与覆盖

| source | selected root | chapter_count | problem_chapter_count |
| --- | --- | --- | --- |
| PaddleOCR | tmp/paddle_output | 36 | 36 |
| GLM-OCR | tmp/glmocr_output | 36 | 34 |

| coverage item | count |
| --- | --- |
| shared chapters | 36 |
| paddle only | 0 |
| glmocr only | 0 |

## 源内问题概览

| source | issue_type | chapter_count |
| --- | --- | --- |
| paddle | latex_command_residue | 36 |
| glmocr | latex_command_residue | 34 |
| paddle | unbalanced_inline_math | 5 |
| glmocr | unbalanced_inline_math | 1 |

## 章节差异最大的前 10 项

| chapter | length_gap_ratio | formula_gap | env_gap | paddle_len | glmocr_len | paddle_formula | glmocr_formula |
| --- | --- | --- | --- | --- | --- | --- | --- |
| chapter11 | 0.186 | 113 | 0 | 84887 | 104251 | 531 | 644 |
| chapter19 | 0.298 | 95 | 0 | 127296 | 89423 | 744 | 649 |
| chapter22 | 0.071 | 91 | 0 | 139354 | 149980 | 963 | 872 |
| chapter2 | 0.192 | 87 | 0 | 73600 | 91099 | 551 | 464 |
| appendix3 | 0.116 | 85 | 0 | 41795 | 36946 | 463 | 378 |
| chapter9 | 0.252 | 78 | 0 | 193202 | 258318 | 1049 | 971 |
| appendix4 | 0.288 | 63 | 0 | 62390 | 87599 | 677 | 614 |
| chapter30 | 0.169 | 59 | 0 | 120932 | 145570 | 902 | 961 |
| chapter21 | 0.158 | 58 | 0 | 110708 | 131449 | 925 | 983 |
| chapter28 | 0.066 | 58 | 0 | 172890 | 185143 | 1350 | 1292 |

## 抽样片段

| chapter | reason | diff_tag | paddle snippet | glmocr snippet |
| --- | --- | --- | --- | --- |
| chapter19 | length_gap, formula_gap, source_issue | paired_window_different | 94) noted a fundamental difference between the two approaches in separating genetic from environmental change: an LS analysis typically uses between-population information (e.g., contrasts of the means of selection vs. control, or up-vs. down-selected lines), | alues) for some, then REML does not necessarily yield unbiased estimates of A 2 , and in this case bias increases with heritability (Jeyaruban and Gibson 1996). When the base population consists of previously selected individuals, REML no longer provides prote |
| chapter2 | formula_gap, source_issue | paired_window_different | nd at a second locus. Initially, all copies of A are associated with B (there are no Ab gametes). Because the sum of the AB and aB gamete frequencies is just the frequency q of B, the resulting 2 2 gametic contingency table is ccc A & a B & p & q-p b & 0 & 1-q | the mean of the distribution, which is the expected allele frequency, is E (p) = + = 1 k and the allele-frequency variance among replicates is 2 (p) = ( + ) 2 ( + + 1) = k - 1 k 2 [ 2 N u k (k - 1) + 1 ] Expressions for the variance of heterozygosity for a pop |
| appendix3 | formula_gap, source_issue | paired_window_different | was sunny for the last week. Suppose the probability transitions given that today is rainy are l P(Rain tomorrow Rain today)=0.5 P(Sunny tomorrow Rain today)=0.25 P(Cloudy tomorrow Rain today)=0.25 This results in the first row of the transition probability ma | ce, (t) = (t - 1) P = P = (t - 2) P 2 Continuing in this fashion yields the probability distribution in generation t as (t) = (0) P t Next we define the n-step transition probability, p ij (n) , as the probability that the process is in state j, given that it |
| appendix4 | length_gap, formula_gap, source_issue | paired_window_different | ters is appropriate. FORMAL META-ANALYSIS Another class of analysis involving multiple comparisons considers comparison across studies, rather than trying to adjust for multiple comparisons within a single study. Such an analysis of analyses, coined meta-analy | S( )=k , and Equation A4.21 becomes n 0 p(k)/k , recovering Equation A4.17. Using the Storey-Tibshirani estimator for n 0 (Equation A4.9b), an estimated value for the FDR using threshold value, (and based on the tuning parameter, , in the Storey-Tibshirani est |
| chapter30 | formula_gap, source_issue | paired_window_different | oubling point is that if the standard error of 12 is sufficiently large, we will not be able to distinguish between these very different types of selection even if we could show that 11 , 22 0 . Canonical Transformation of While the curvature of a quadratic fi | ) and U = ( e 1 , e 2 , , e n ) Geometrically, U describes a rigid rotation of the original coordinate system while A shows the amounts that unit lengths in the original coordinate system are scaled in the transformed system. Using the unitary property of U, |
| chapter21 | formula_gap, source_issue | paired_window_different | t, x, and the offspring, y, counting the paths through both parents ( R m and R f ). When covariances are equal, this is twice the single parent-covariance, (x, y R 1 ) . By analogy with the breeder's equation, Equation 21.1b is often written as R y =h x,y 2 S | = z x (x, y) where (counting both parents) (x,y)=2 (x,y\| ) . Equation 21.4a follows immediately from Equation 21.3b by recalling that (x,y)= (x,y)/( x y ) and that the trait variance in the offspring, y, is simply the phenotypic variance of the character ( y |
| chapter28 | formula_gap, source_issue | paired_window_different | pparent stabilizing selection on many traits. However, pleiotropic selection models can generate associations between the values at a neutral focal trait and fitness, thus generating false signals of stabilizing selection on that trait. In the case of underlyi | s (the conditions for maintaining more than two alleles by overdominance at a locus are very delicate, so this is not an unreasonable assumption; Lewontin et al. 1978). Let the genotypes Q i Q i : Q i q i : q i q i have fitnesses of 1-s i : 1: 1-t i , yielding |
| chapter3 | formula_gap, source_issue | paired_window_different | ring. In fact, even under a random-mating scheme, if family sizes are equilibrated, provided N 4 , the erosion of heterozygosity is H t H 0 (1- 1 4N ) t where t is the number of generations after the onset of inbreeding (Wright 1951). This can be seen by retur | arly constant, approaching an asymptotic value of 1 / (4 N-m-1) (Robertson 1964), which, with N=4 and m=2 under double first-cousin mating equals 0.08, giving the fraction retained as 1-0.08=0.92 , recovering Equation 3.24. Note that when N is large, m N and t |
| chapter7 | length_gap, formula_gap, source_issue | paired_window_different | quency 1 - p' ) mutate to a. Thus, one generation of the joint action of selection and mutation leads to the new frequency of a p =(1- -v)p W + Haldane (1927) was the first to consider the equilibrium allele frequencies that are eventually reached under this m | homozygotes are lethal. Under this scenario, all new mutations ultimately become either lost or fixed at the population level, and those that become fixed will themselves be subject to replacement by subsequently arising mutations. Thus, when finite populatio |
| chapter27 | length_gap, formula_gap, source_issue | paired_window_different | 1]/j (Gumbel 1958; Weissman 1978), meaning that there is a regular pattern in the spacing that only depends on the fitness rank, j , of a given allele and on the expected spacing, E[ 1] , for the most fit allele. (Recall that Equation 27.4c showed that a simil | on increases with the amount of pleiotropy, n. Wang et al. showed that the consequence of b>0.5 is that while the probability that a new mutation is advantageous decreases with increasing n, its fixation probability, and its effect on fitness if fixed, both in |

## 结论

- PaddleOCR 可作为 structured 生产源，但不等于 ground truth。
- GLM-OCR 可作为修复参考源，但也不等于 ground truth。
- 因此 structured 准确率不能用 Paddle vs GLM 简单互相比对得出。
- 更合理的方法是全量自动质量审计 + 分层人工抽样验证。
