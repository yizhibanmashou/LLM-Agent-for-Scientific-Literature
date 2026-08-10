# Chapter 19 · 19 Twins and Clones

## Genetics_chapter19_001 · 19 Twins and Clones

Starting with Galton (1875), the analysis of twins has been a major focal point for research in human quantitative genetics (Bulmer 1970, Rowe 1994). Since approximately one in 100 humans are twins, substantial data bases can often be acquired through hospital records or through advertisements. One of the utilities of twin research arises from the fact that two types of twins are possible. Monozygotic twins, which are derived from the fragmentation of a single embryo, are genetically identical. Dizygotic twins are genetically equivalent to full sibs since they are derived from two eggs fertilized by different sperm. Thus, for characters that are genetically variable, a greater amount of phenotypic resemblance is expected within pairs of monozygotic twins than dizygotic twins. This is almost always observed.

When certain conditions regarding additivity of gene action and sources of environmental variation are met, some simple and powerful conclusions can be derived from twin analysis. However, as we have noted many times before, it is often impossible to verify whether all of the assumptions of a quantitative-genetic model are met. Consequently, any conclusions drawn from twin research should be carefully qualified, a practice that not all previous investigators have adhered to. The analysis of twin scores for psychological and intelligence tests has frequently led to the suggestion that human behavior and intelligence are largely genetically determined. Racial and societal overtones associated with such conclusions have generated some of the most bitter scientific debate of this century (Lewontin et al. 1984). This debate has been good for quantitative genetics because it has forced a meticulous consideration of the assumptions of traditional models. As a result, the relatively simple twin models that were relied upon until about 1970 are gradually being replaced by more elaborate models, particularly with respect to sources of environmental variation.

The initial focus of this chapter is on the classical approach to heritability analysis using combined data from monozygotic and dizygotic twins. We then describe the additional power that arises when one is fortunate enough to have data on twins raised apart or on the offspring of twins. Finally, we show how the basic principles of twin analysis can be extended to the analysis of phenotypic variation in asexual populations.

**[Table]**

*[See Table 19.1 at the end of this section.]*

> **Table 19.1** · `19.1` · page 595 · source: `Genetics_chapter19_001`
> Table 19.1 Summary of a one-way ANOVA involving N independent pairs of twins.
>
> Source of Variance | df | Sums of Squares | Observed Mean Squares | E(MS)
> --- | --- | --- | --- | ---
> Among pairs | N - 1 | $ SS_{b} = 2 \sum_{i=1}^{N} (\overline{z}_{i} - \overline{z})^{2} $ | $ SS_{b}/(N - 1) $ | $ \sigma_{e}^{2} + 2\sigma_{b}^{2} $
> Within pairs | N | $ SS_{e} = \sum_{i=1}^{N} \sum_{j=1}^{2} (z_{ij} - \overline{z}_{i})^{2} $ | $ SS_{e}/N $ | $ \sigma_{e}^{2} $
> Total | T - 1 | $ SS_{T} = \sum_{i=1}^{N} \sum_{j=1}^{2} (z_{ij} - \overline{z})^{2} $ | $ SS_{T}/(T - 1) $ | $ \sigma_{z}^{2} $
>
> Note: This general description applies to both monozygotic and dizygotic analyses. The total sample size is $ T = 2N $, $ z_{ij} $ is the observed phenotype of the $ j^{th} $ member of the $ i^{th} $ pair of twins, $ \overline{z}_{i} $ is the mean phenotype of the $ i^{th} $ pair, and $ E(\text{MS}) $ denotes the expected mean squares.

---

## Genetics_chapter19_002 · THE CLASSICAL APPROACH

The most commonly used methodology for twin analysis relies on the simple one-way analysis of variance (Kempthorne and Osborne 1961, Haseman and Elston 1970, Christian et al. 1974, Kang et al. 1974, Eaves et al. 1978, Martin et al. 1978). Separate analyses are performed for monozygotic and dizygotic twins using the layout given in Table 19.1. Since twin groups always consist of two individuals, this is one of the few designs in quantitative-genetic analysis that is always perfectly balanced.

For both types of twins, we start with the simple linear model

$$
z_{ij}=\mu+b_{i}+e_{ij}
\tag{19.1}
$$


where $ z_{ij} $ is the phenotype of the jth member (j = 1 or 2) of the ith pair, $ b_i $ is the effect of the ith pair, and $ e_{ij} $ is the residual error resulting from segregation (in the case of dizygotic twins) and environmental variance. As usual, we assume that the $ e_{ij} $ have zero expectations, are uncorrelated with each other, and have common variance within each family, $ \sigma_e^2 $. The twin pairs within each analysis are also assumed to be a random sample of the entire population so that $ E(b_i) = 0 $. For monozygotic and dizygotic twin analyses respectively, we denote the variance among pairs by $ \sigma_b^2(MZ) $ and $ \sigma_b^2(DZ) $ and the variance within pairs by $ \sigma_e^2(MZ) $ and $ \sigma_e^2(DZ) $.

As in the case of sib analysis (Chapter 18), estimates of the within- and among-pair components of variance are obtained by setting the observed mean squares equal to their expectations and solving. The observed variance components can, in turn, be used to derive inferences about causal sources of phenotypic variance. From Equation 19.1, it can be seen that under the assumption of independent residuals, the expected among-pair variance is equivalent to the covariance of members of the same pair, $ \sigma(z_{i1}, z_{i2}) = \sigma(b_i, b_i) = \sigma_b^2 $. In causal terms, for monozygotic twins, this is equivalent to

$$
\sigma_{b}^{2}(\mathbf{M}\mathbf{Z})=\sigma_{G}^{2}+\sigma_{E_{c}}^{2}(\mathbf{M}\mathbf{Z})
\tag{19.2a}
$$


where $ \sigma_{G}^{2} $ is the total genetic variance, and $ \sigma_{E_{c}}^{2} $ (MZ) is the variance due to common familial environment. The genetic covariance between monozygotic twins is equal to the total genetic variance because of the complete genetic identity of the individuals involved. For dizygotic twins,

$$
\sigma_{b}^{2}(\mathbf{D}\mathbf{Z})=\frac{1}{2}\sigma_{A}^{2}+\frac{1}{4}\sigma_{D}^{2}+\frac{1}{4}\sigma_{A A}^{2}+\cdots+\sigma_{E_{c}}^{2}(\mathbf{D}\mathbf{Z})
\tag{19.2b}
$$


Separate notation is needed for the variance due to common familial environment because it is not necessarily the same in the two types of twins. Since $ \sigma_{z}^{2} = \sigma_{b}^{2} + \sigma_{e}^{2} $, it follows that the remainder of the phenotypic variance is in the within-pair component. Therefore,

$$
\sigma_{e}^{2}(\mathbf{M}\mathbf{Z})=\sigma_{E_{s}}^{2}(\mathbf{M}\mathbf{Z})
\tag{19.3a}
$$


and

$$
\sigma_{e}^{2}(\mathrm{D Z})=\frac{1}{2}\sigma_{A}^{2}+\frac{3}{4}\sigma_{D}^{2}+\frac{3}{4}\sigma_{A A}^{2}+\cdots+\sigma_{E_{s}}^{2}(\mathrm{D Z})
\tag{19.3b}
$$


where the terms $ \sigma_{E_{s}}^{2} $ (MZ) and $ \sigma_{E_{s}}^{2} $ (DZ) refer to the residual environmental variance, i.e., environmental variance not attributable to common familial effects (Chapter 6).

All of the procedures outlined in Chapter 18 for the one-way analysis of variance of sibs apply to twin analysis. From Table 19.1, it can be seen that the among-pair variance is estimated by

$$
\mathrm{Var}(b)=\frac{\mathrm{MS}_{b}-\mathrm{MS}_{e}}{2}
\tag{19.4a}
$$


Taking the sampling variance of the mean squares to be approximately $ 2(\text{MS})^{2}/N $ (from Equation 18.19), and recalling that the mean squares are distributed independently under a balanced design, the large-sample variance of $ \text{Var}(b) $ is

$$
\mathrm{Var}[\mathrm{Var}(b)]\simeq\frac{\mathrm{Var}(\mathrm{MS}_{b})+\mathrm{Var}(\mathrm{MS}_{e})}{4}=\frac{(\mathrm{MS}_{b})^{2}+(\mathrm{MS}_{e})^{2}}{2N}
\tag{19.4b}
$$


The within-pair variance is approximated by

$$
\mathbf{Var}(e)=\mathbf{M}\mathbf{S}_{e}
\tag{19.5a}
$$


and its large-sample variance is

$$
\mathbf{V a r}[\mathbf{V a r}(e)]\simeq2(\mathbf{M S}_{e})^{2}/N
\tag{19.5b}
$$


Combining the estimators for $ \sigma_{b}^{2} $ and $ \sigma_{e}^{2} $, we obtain

$$
\mathrm{Var}(z)=\frac{\mathrm{MS}_{b}+\mathrm{MS}_{e}}{2}
\tag{19.6}
$$


as the estimator of $ \sigma_{z}^{2} $. Its large-sample variance estimator is identical to that of $ \mathrm{Var}(b) $. Confidence intervals for the within- and among-pair components of variance can be obtained by using Equations 18.22 and 18.23.

Recalling the arguments laid out in Chapter 18, the ratio of mean squares, $ F = MS_{b}/MS_{e} $, provides a test statistic for evaluating the significance of the among-pair component of variance. The null hypothesis of no pair effects is tested by referring to standard $ F $-distribution tables and comparing the observed $ F $ with the 5% or 1% critical values associated with $ (N - 1) $ and $ N $ degrees of freedom.

---

## Genetics_chapter19_003 · THE CLASSICAL APPROACH / Heritability Estimation

An upper limit to the broad-sense heritability, based only on monozygotic-twin data, is the intraclass correlation (the fraction of the total variance that is attributable to differences among pairs)

$$
H^{2}=t_{\mathrm{MZ}}=\frac{\mathrm{MS}_{b}(\mathrm{MZ})-\mathrm{MS}_{e}(\mathrm{MZ})}{\mathrm{MS}_{b}(\mathrm{MZ})+\mathrm{MS}_{e}(\mathrm{MZ})}
\tag{19.7a}
$$


From Equation 18.21, the standard error of this estimator is approximately

$$
\mathrm{SE}(H^{2})\simeq\frac{1-t_{\mathrm{MZ}}^{2}}{\sqrt{N}}
\tag{19.7b}
$$


Under conditions of normality, the 100(1−α)% confidence interval for $ H^{2} $ is given by

$$
\left[\frac{\left(F/F_{U}\right)-1}{\left(F/F_{U}\right)+1}\right]<H^{2}<\left[\frac{\left(F/F_{L}\right)-1}{\left(F/F_{L}\right)+1}\right]
\tag{19.7c}
$$


where $F$ is the ratio of observed mean squares, and $F_U = F_{(N-1),N,(\alpha/2)}$ and $F_L = 1/[F_{N,(N-1),(\alpha/2)}]$ are the upper and lower $F$ values associated with $(\alpha/2)$ (Searle et al. 1992).

**[示例 Example]**

> **Example 1** · ref: `Genetics_chapter19:1` · source: `Genetics_chapter19_003.json` · blocks 7–7
>
> Example 1. Reed et al. (1975) performed an analysis of total fingerprint ridge count for N = 260 pairs of monozygotic twins, obtaining the observed mean squares MS $ _{b} $ = 3619.2 and MS $ _{e} $ = 82.9. From Equations 19.7a,b, we obtain the estimate $ H^2 = 0.955 $ and the standard error $ \mathrm{SE}(H^2) = 0.005 $. With an $ F $ ratio of 43.66, this heritability estimate is highly significant. To obtain the 99% confidence interval for $ H^2 $, we first find $ F_U = F_{259,260,0.005} \simeq 1.4 $ and $ F_L = 1/F_{260,259,0.005} \simeq 0.7 $. Substituting these values into Equation 19.7c, the lower and upper confidence limits are found to be 0.937 and 0.984.


As an estimator of the broad-sense heritability, the intraclass correlation will be inflated by the presence of any common environmental effects, $ \sigma_{E_c}^2 $ (MZ). This can be checked by comparing the correlation between twins raised together with that between twins raised apart (by one or more adoptive parents). The difference between the two correlations provides a measure of the fraction of the phenotypic variance that is due to common-environment effects. Generally, intraclass correlations for twins raised together do exceed those for twins raised apart, but the difference is usually only on the order of a few percent (Table 19.2). Thus, in humans, a large fraction of the variation in size, physiology, and mental ability appears to have a genetic basis, and not much appears to be associated with shared environment (except in the case of IQ). There is still some need for caution here, however, since it is unlikely that the foster homes of twins are ever perfectly randomized, and postnatal separation does not eliminate prenatal maternal effects, which may be important in mammals (Chapter 23). In humans, an alternative means of testing for the importance of shared environment is to consider the correlation between unrelated adoptees raised by the same foster parents. For IQ, this correlation is approximately 0.34 (Rowe 1994), which is slightly higher than the difference between correlations for monozygotic twins raised together and apart (Table 19.2).

Some success at eliminating the contribution of common environmental effects in twin analysis has also been obtained by the following approximation

$$
\widetilde{H}^{2}\simeq\frac{2[\mathrm{M S}_{e}(\mathrm{D Z})-\mathrm{M S}_{e}(\mathrm{M Z})]}{\mathrm{V a r}(z)}
\tag{19.8}
$$


where $ \text{Var}(z) $ is the average of the estimates of total variance obtained for monozygotic and dizygotic types of twins. Provided the variance due to special environmental effects is comparable in the two types of twins, and some other assumptions to be discussed below are met, $ \widetilde{H}^2 $ has an expectation equal to approximately $ [\sigma_A^2 + (3\sigma_D^2/2) + (3\sigma_{AA}^2/2) + \cdots]/\sigma_z^2 $. Thus, Equation 19.8 still overestimates the broad-sense heritability if the relative magnitude of dominance and/or epistatic variance is large. Nevertheless, a reasonable test of the hypothesis $ \widetilde{H}^2 = 0 $ is provided by the $ F $ statistic $ \text{MS}_e(\text{DZ})/\text{MS}_e(\text{MZ}) $. Estimates of broad-sense heritability using Equation 19.8, like those using Equation 19.7a, indicate that variation in human size attributes has a large genetic component (Table 19.3).

**[Table]**

*[See Table 19.2 at the end of this section.]*

**[Table]**

*[See Table 19.3 at the end of this section.]*

Because monozygotic and dizygotic twins develop in different types of placental environments, one might question the assumptions that $ \sigma_{E_s}^2 $ (MZ) = $ \sigma_{E_s}^2 $ (DZ) and $ \sigma_{E_c}^2 $ (MZ) = $ \sigma_{E_c}^2 $ (DZ). Mammalian embryos are surrounded by two types of fetal membranes: an amnion (or birth sac), which is continuous with the body wall of the embryo and forms a fluid-filled chamber, and a more external chorion (placenta) through which exchange of nutrients, gases, and wastes takes place. Human dizygotic twins always have separate membranes, but only about a third of monozygotic twins do (Nance 1979). Thus, due to the greater sharing of prenatal environments, monozygotic twins may exhibit higher similarity due to shared environmental effects and deviate less because of specific effects. The fact that dichorionic and monochorionic monozygotic twins differ significantly in their within-pair mean squares for plasma cholesterol (Christian et al. 1976) and fingerprint patterns (Reed et al. 1978) is consistent with this idea.

More remarkably, embryo transplant experiments with highly inbred lines of mice have shown that monozygotic twins separated at the eight-cell stage are significantly more similar to each other than are dizygotic twins (separate since conception) treated in the same manner (Gärtner and Baunack 1981). In this study, dizygotic twins are no more different genetically than monozygotic twins since the parents are highly homozygous. Thus, these results suggest that by the third cell division, zygotes can be modified by common environmental effects that have substantial impact on the adult phenotype.

A number of other important assumptions underly twin analysis (Price 1950; Kempthorne and Osborne 1961; Nance 1976, 1979; Eaves et al. 1978; Martin et al. 1978; Rowe 1994). For example, one might question whether twins are a random subset of the gene pool of the general population. Since it is the population at large about which one normally wants to make inferences, there is reason for concern here. The dizygotic twinning rate differs significantly among races of humans as well as among individuals (Bulmer 1970). In addition, dizygotic twins are more frequently produced by older mothers, for whom congenital malformations are also more common. An additional concern is whether the environmental component of variance may be exceptionally high or low in twins relative to singletons. Parents may treat twins differently than singleton offspring. Because of their contemporaneity, twins may also experience an exceptional level of sib competition (or cooperation).

One or more of the above-mentioned problems would be suggested if the phenotypic variances for monozygotic twins and dizygotic twins were found to be significantly different. This can be tested by the ratio

$$
F=\frac{MS_{b}(DZ)+MS_{e}(DZ)}{MS_{b}(MZ)+MS_{e}(MZ)}
\tag{19.9a}
$$


Using Satterthwaite’s (1946) method (Chapter 18), the degrees of freedom associated with the numerator are approximately

$$
d f=\frac{N[\mathrm{MS}_{b}(\mathrm{DZ})+\mathrm{MS}_{e}(\mathrm{DZ})]^{2}}{\mathrm{MS}_{b}^{2}(\mathrm{DZ})+\mathrm{MS}_{e}^{2}(\mathrm{DZ})}
\tag{19.9b}
$$


and a parallel definition applies to the denominator.

> **Table 19.2** · `19.2` · page 599 · source: `Genetics_chapter19_003`
> Table 19.2 Intraclass correlations for monozygotic twins raised together $ (t_{\mathrm{MZT}}) $ and raised apart $ (t_{\mathrm{MZA}}) $, both obtained by use of Equation 19.7a.
>
> Character | $ t_{MZT} $ | $ t_{MZA} $ | $ t_{MZT} - t_{MZA} $
> --- | --- | --- | ---
> Fingerprint ridge count | 0.96 | 0.97 | -0.01
> Height | 0.93 | 0.86 | 0.07
> Weight | 0.83 | 0.73 | 0.10
> Blood pressure | 0.70 | 0.64 | 0.06
> Heart rate | 0.54 | 0.49 | 0.05
> IQ | 0.88 | 0.69 | 0.19
>
> Source: Bouchard et al. 1990.

> **Table 19.3** · `19.3` · page 599 · source: `Genetics_chapter19_003`
> Table 19.3 Broad-sense heritability estimates for size-related characters in humans, obtained by use of Equation 19.8.
>
> Character | MS $ _{e} $(DZ) | MS $ _{e} $(MZ) | Var(z) | $ \widetilde{H}^{2} $
> --- | --- | --- | --- | ---
> Height | 1620.3 | 195.4 | 3031.7 | 0.94
> Arm span | 2132.0 | 317.7 | 3944.1 | 0.92
> Middle finger length | 11.9 | 1.4 | 22.3 | 0.94
> Foot length | 58.5 | 10.9 | 105.8 | 0.90
> Chest circumference | 1098.8 | 423.7 | 1776.6 | 0.76
> Head breadth | 14.9 | 4.2 | 25.5 | 0.84
>
> Source: Clark 1956.
> Note: Data are from 44 pairs of monozygotic twins and 37 pairs of dizygotic twins of the same sex in Michigan high schools and junior high schools.

---

## Genetics_chapter19_004 · THE MONOZYGOTIC-TWIN HALF-SIB METHOD

Nance and Corey (1976) introduced a clever method of twin analysis that eliminates many of the uncertainties of the classical method. Children produced by two monozygotic twins are cousins socially, but genetically they are related as half sibs (Figure 19.1). Moreover, unlike their monozygotic-twin parents, such

> **Figure 19.1** · page 601 · source: `Genetics_chapter19`
>
> ![Figure 19.1](figures/Genetics_19.1.png)
>
> Figure 19.1 The monozygotic-twin half-sib design. Each pedigree contains two full-sib families derived from a pair of monozygotic twins, in this case the two sets of females denoted by the shaded circles.


half sibs are not raised in a common home. When data are available for the progeny of many pairs of such twins, a nested analysis of variance can be performed, analogous to that described previously for the full-sib, half-sib design (Table 18.3). The linear model to be analyzed is

$$
z_{i j k}=\mu+a_{i}+b_{i j}+e_{i j k}
$$


where $ z_{ijk} $ is the phenotype of the kth offspring of the jth member (j = 1 or 2) of the ith twin pair, $ a_i $ is the effect of the ith pair, $ b_{ij} $ is the effect of the jth family within the ith pair (resulting from genetic differences between the unrelated parents and from common environmental effects), and $ e_{ijk} $ is the residual deviation resulting from segregation and special environmental effects. As usual under the assumption that individuals are random members of the population, $ a_i $, $ b_{ij} $, and $ e_{ijk} $ are defined to have means equal to zero and to be uncorrelated with each other. $ \sigma_a^2 $, the variance between monozygotic-twin half-sibships, is equivalent to the covariance among half-sibs living in different homes. $ \sigma_b^2 $ is the variance between full-sibships within half-sibships, and $ \sigma_e^2 $ is the variance within full-sibships. Estimates of these variance components are obtainable from the observed mean squares of a nested ANOVA in the manner described in Chapter 18. Their causal components are summarized in Table 19.4.

The monozygotic-twin half-sib (MTHS) method has several major advantages over classical twin analysis. First, since it is performed on normal singleton children, the potential problem of environmental effects specific to twin phenotypes is eliminated. Second, the MTHS method removes the necessity of relying on data from both monozygotic and dizygotic twins. Third, when separate analyses are performed on female and male twins, it becomes possible to estimate the

**[Table]**

*[See Table 19.4 at the end of this section.]*

genetic variance for maternal effects, $\sigma_{G_{m}}^{2}$. As described in Table 19.4, the causal components of $\sigma_{a}^{2}$ are identical for maternal and paternal half-sibships except that $\sigma_{G_{m}}^{2}$ makes no contribution in the latter case (since the “half sibs” have different maternal genotypes). The opposite holds for $\sigma_{b}^{2}$. Thus, $\sigma_{b}^{2}(PHS) - \sigma_{b}^{2}(MHS)$ and $\sigma_{a}^{2}(MHS) - \sigma_{a}^{2}(PHS)$ both provide estimates of $\sigma_{G_{m}}^{2}$. Using this relationship, Nance (1979) was able to show that genetic maternal effects are responsible for about 22% of the variance in human height. (A more in-depth discussion of the analysis of maternal effects is provided in Chapter 23, where it is shown that $\sigma_{G_{m}}^{2}$ actually contains several subsidiary components.)

The variance due to common environmental effects is partitioned into two components in Table 19.4. $ \sigma_{E_c'}^2 $ is equivalent to the covariance between half sibs due to common environmental effects. Even though the half sibs do not live in the same home, $ \sigma_{E_c'}^2 $ may be nonzero in the MTHS design if monozygotic twins raise their offspring in a similar manner due to common cultural inheritance. (Although it is not shown in the table, $ \sigma_{E_c'}^2 $ could also vary between paternal and maternal half-sibships). $ \sigma_{E_c}^2 $ is the covariance between full sibs due to common maternal environment, in excess of $ \sigma_{E_c'}^2 $.

In all, there are three sources of environmental variance as well as several sources of genetic variance in Table 19.4, but only five equations. Thus, not all of the parameters can be estimated with the nested design. However, when data are also recorded on the twins themselves, six other types of relationships can be evaluated (Table 19.5). Estimates of the variance components can then be obtained in the usual way by the solution of simultaneous equations, although it should be noted that the observed covariances are not all independent since they share common individuals.

**[Table]**

*[See Table 19.5 at the end of this section.]*

Nance and Corey (1976) and Haley et al. (1981) have pointed out that when separate analyses are performed on male and female progeny, the additive and dominance components of variance due to sex-linked loci can be determined with the MTHS design. For example, when an analysis is restricted to male progeny, in maternal half-sibships $ \sigma_{a}^{2} $ contains additive genetic variance associated with the X chromosome since the male progeny within the sibship derive their X chromosomes from identical maternal genotypes, whereas $ \sigma_{b}^{2} $ contains no variance associated with the X chromosome. On the other hand, in paternal half-sibships $ \sigma_{b}^{2} $ contains additive genetic variance associated with the X chromosome since the male progeny in related half-sib families derive their X chromosomes from different mothers, whereas $ \sigma_{a}^{2} $ contains no variance associated with the X chromosome since the paternal X chromosome is not inherited in the male offspring. (See Chapter 24 for further discussion of methods for estimating genetic variance due to sex-linked loci.)

An even more elaborate analysis than the preceding one has been outlined by (Haley and Last 1981), incorporating both dizygotic and monozygotic twins. The progeny of different dizygotic twins are genetically equivalent to first cousins.

**[示例 Example]**

> **Example 2** · ref: `Genetics_chapter19:2` · source: `Genetics_chapter19_004.json` · blocks 13–16
>
> Example 2. Fingerprint traits have long been employed in studies of polygenic inheritance in man (Holt 1968). They are easily assayed, and many permanent records of them exist for deceased and living individuals. The broad-sense heritabilities of dermatoglyphic traits tend to be close to 1.0, so standard errors of genetic variance estimates are relatively low. Fingerprints do not change with age, and they are not subject to assortative mating or to common postnatal environmental effects.
> 
> ![Source illustration p604 b3](figures/examples/Genetics_p604_b3.png)
> 
> In order to illustrate some of the concepts of this chapter and their broader utility, we will consider some of the results for total dermal ridge count (TDRC), the sum of the ridges in the central cores of all ten fingertips. The above figure (from Holt 1955) gives the observed distribution for a sample of 825 British males and the fitted normal curve. The phenotype distribution for this character is approximately normal, and there is a wide range of variation. Correlations between a variety of relatives from several independent studies (with sample sizes ranging from 100 to 700) are recorded below. The results are highly consistent across studies.
> 
> <table><tr><td>Relationship</td><td>r</td><td>Reference</td></tr><tr><td rowspan="3">Monozygotic twins</td><td>0.96</td><td>Lamy et al. 1957</td></tr><tr><td>0.95</td><td>Holt 1968</td></tr><tr><td>0.96</td><td>Reed et al. 1975</td></tr><tr><td rowspan="3">Dizygotic twins</td><td>0.45</td><td>Lamy et al. 1957</td></tr><tr><td>0.49</td><td>Holt 1968</td></tr><tr><td>0.54</td><td>Reed et al. 1975</td></tr><tr><td rowspan="3">Full sibs</td><td>0.50</td><td>Holt 1968</td></tr><tr><td>0.43</td><td>Mi and Rashad 1975</td></tr><tr><td>0.46</td><td>Reed et al. 1979</td></tr><tr><td rowspan="2">Half sibs</td><td>0.16</td><td>Reed et al. 1979</td></tr><tr><td>0.16</td><td>Nance 1979</td></tr><tr><td rowspan="3">Mother-offspring</td><td>0.41</td><td>Mi and Rashad 1975</td></tr><tr><td>0.40</td><td>Reed et al. 1979</td></tr><tr><td>0.39</td><td>Matsuda 1973</td></tr><tr><td rowspan="3">Father-offspring</td><td>0.41</td><td>Mi and Rashad 1975</td></tr><tr><td>0.40</td><td>Reed et al. 1979</td></tr><tr><td>0.48</td><td>Matsuda 1973</td></tr></table>


TDRC appears to be almost completely genetically determined with a broad-sense heritability very close to 0.96. The correlations between ordinary full sibs and between dizygotic twins are essentially the same (averaging 0.46 and 0.49 respectively). In the absence of dominance and maternal effects, this would also be the expected correlation between parent and offspring. However, the latter appears to be very close to 0.42. Since the average mother-offspring correlation is less than the father-offspring regression, maternal effects appear to be unimportant. Thus, since $ \sigma_{D}^{2}/4 $ contributes to the covariance between full sibs but not between parent and offspring, $ (0.48 - 0.42) \times 4 = 0.24 $ provides an estimate of the proportion of the total phenotypic variance that is attributable to dominance (ignoring epistatic terms involving dominance).

Epistasis may also play an important role in the expression of TDRC (Nance 1979). The genetic covariance for parent and offspring is $ (\sigma_{A}^{2}/2) + (\sigma_{AA}^{2}/4) + \cdots $, while that for half sibs is $ (\sigma_{A}^{2}/4) + (\sigma_{AA}^{2}/16) + \cdots $. Thus, in the presence of epistatic genetic variance, the phenotypic correlation $ r_{PO} $ is expected to be greater than $ 2r_{HS} $. Using the estimates for $ r_{HS} $ in the table, which are from analyses of the offspring of monozygotic twins, $ r_{PO} - 2r_{HS} \simeq 0.10 $, provides an estimate of $ [(\sigma_{AA}^{2}/8) + \cdots]/\sigma_{z}^{2} $. This result suggests that approximately $ 8 \times 10\% = 80\% $ of the phenotypic variance is attributable to epistatic genetic variance, leaving little room for simple additive genetic variance. This estimate may be substantially inflated by sampling error. However, Heath et al. (1984) provide convincing evidence that about 40% of the variance of another trait, total finger pattern intensity, results from additive × additive epistatic interactions.

> **Table 19.4** · `19.4` · page 602 · source: `Genetics_chapter19_004`
> Table 19.4 Coefficients for the causal components of variance that contribute to the expected variance components $ \sigma_{a}^{2} $, $ \sigma_{b}^{2} $, and $ \sigma_{e}^{2} $ extracted from the nested ANOVA in a monozygotic-twin half-sib design.
>
> <table><tr><td></td><td>$ \sigma_{A}^{2} $</td><td>$ \sigma_{D}^{2} $</td><td>$ \sigma_{AA}^{2} $</td><td>$ \sigma_{AD}^{2} $</td><td>$ \sigma_{DD}^{2} $</td><td>$ \sigma_{G_{m}}^{2} $</td><td>$ \sigma_{E_{c}^{\prime}}^{2} $</td><td>$ \sigma_{E_{c}}^{2} $</td><td>$ \sigma_{E_{s}}^{2} $</td></tr><tr><td colspan="10">Female twins (maternal half sibships)</td></tr><tr><td>$ \sigma_{a}^{2} $</td><td>1/4</td><td>0</td><td>1/16</td><td>0</td><td>0</td><td>1</td><td>1</td><td>0</td><td>0</td></tr><tr><td>$ \sigma_{b}^{2} $</td><td>1/4</td><td>1/4</td><td>3/16</td><td>1/8</td><td>1/16</td><td>0</td><td>0</td><td>1</td><td>0</td></tr><tr><td colspan="10">Male twins (paternal half sibships)</td></tr><tr><td>$ \sigma_{a}^{2} $</td><td>1/4</td><td>0</td><td>1/16</td><td>0</td><td>0</td><td>0</td><td>1</td><td>0</td><td>0</td></tr><tr><td>$ \sigma_{b}^{2} $</td><td>1/4</td><td>1/4</td><td>3/16</td><td>1/8</td><td>1/16</td><td>1</td><td>0</td><td>1</td><td>0</td></tr><tr><td colspan="10">General</td></tr><tr><td>$ \sigma_{e}^{2} $</td><td>1/2</td><td>3/4</td><td>3/4</td><td>7/8</td><td>5/16</td><td>0</td><td>0</td><td>0</td><td>1</td></tr></table>

> **Table 19.5** · `19.5` · page 603 · source: `Genetics_chapter19_004`
> Table 19.5 Additional covariances between relatives that can be observed with a MTHS design, and their causal components, when the parents are measured.
>
> <table><tr><td rowspan="2">Covariance</td><td colspan="9">Variance Component</td></tr><tr><td>$ \sigma_{A}^{2} $</td><td>$ \sigma_{D}^{2} $</td><td>$ \sigma_{AA}^{2} $</td><td>$ \sigma_{AD}^{2} $</td><td>$ \sigma_{DD}^{2} $</td><td>$ \sigma_{Gm}^{2} $</td><td>$ \sigma_{E_{c}}^{2} $</td><td>$ \sigma_{E_{c}}^{2} $</td><td>$ \sigma_{E_{s}}^{2} $</td></tr><tr><td>MZ twins</td><td>1</td><td>1</td><td>1</td><td>1</td><td>1</td><td>1</td><td>0</td><td>1</td><td>0</td></tr><tr><td>Mother-offspring</td><td>1/2</td><td>0</td><td>1/4</td><td>0</td><td>0</td><td>1/2</td><td>b_{1}</td><td>0</td><td>0</td></tr><tr><td>Father-offspring</td><td>1/2</td><td>0</td><td>1/4</td><td>0</td><td>0</td><td>0</td><td>b_{2}</td><td>0</td><td>0</td></tr><tr><td>Twin aunt-offspring</td><td>1/2</td><td>0</td><td>1/4</td><td>0</td><td>0</td><td>1/2</td><td>b_{3}</td><td>0</td><td>0</td></tr><tr><td>Twin uncle-offspring</td><td>1/2</td><td>0</td><td>1/4</td><td>0</td><td>0</td><td>0</td><td>b_{4}</td><td>0</td><td>0</td></tr><tr><td>Variance within MZ twin pairs</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>1</td></tr></table>
>
> Note: To account for the possibility that cultural inheritance across generations is a source of resemblance between relatives, arbitrary coefficients $ (b_{1}, \ldots, b_{4}) $ have been denoted for $ \sigma_{E_{c}}^{2} $; these may or may not be equal.

---

## Genetics_chapter19_005 · CLONAL ANALYSIS

Many species of microorganisms, plants, and animals have an obligately asexual mode of reproduction. For such organisms, the narrow-sense heritability is an unmeasurable and meaningless concept. The relevant measure of genetic variability is the broad-sense heritability $ H^{2} = \sigma_{G}^{2}/\sigma_{T}^{2} $, the ratio of the among-clone component of variance to the total variance.

The simplest approach to estimating $ H^{2} $ in an asexual population is to perform a one-way ANOVA. By randomly choosing a group of mothers and assaying n progeny from each of them, a within- and among-clone mean square is obtained (see Table 18.1). Under the assumption of no shared maternal environmental effects, the former is an estimate of the environmental variance due to special effects, $ \sigma_{E_{s}}^{2} $, while the expected value of the latter is $ \sigma_{E_{s}}^{2} + n\sigma_{G}^{2} $ under a balanced design. It follows that $ (MS_{b} - MS_{e})/n $ is an estimate of the total genetic variance, $ \sigma_{G}^{2} $. Breeders have used this approach to estimate broad-sense heritabilities in plants that can be clonally propagated (Burton and DeVane 1953, Keller and Likens 1955).

Some species complexes contain both asexual and sexual individuals, or

> **Figure 19.2** · page 606 · source: `Genetics_chapter19`
>
> ![Figure 19.2](figures/Genetics_19.2.png)
>
> Figure 19.2 A nested design for the quantitative-genetic analysis of a population of clones. In this example, four descendants are measured for each clone, pairs of which have descended from different sublines.


allow for the possibility of artificial clonal propagation. This suggests a simple technique for estimating the broad-sense heritability for the sexual component of the population. The phenotypic variance within clones, $ \sigma_{e}^{2} $, can only be due to environmental causes. Thus, letting $ \sigma_{z}^{2} $ be the phenotypic variance of the sexual population, $ (\sigma_{z}^{2}-\sigma_{e}^{2})/\sigma_{z}^{2} $ provides an estimate of $ H^{2} $ for the sexual component of the population. A potential weakness of this approach is the assumption that the environmental variance of both types of individuals is the same. The genotypes of asexual and sexual individuals may respond differently to the environment, and this may be the reason why Browne et al. (1984) obtained some highly negative estimates of $ H^{2} $ when they applied this technique to the brine shrimp Artemia.

A more general limitation of the above approaches to estimating the broad-sense heritability is that maternal effects are not factored out. As noted above, even in the absence of any genetic variation, significant differences may arise between families as a result of maternal-line influences. This problem can be resolved through the use of a nested analysis of variance (Lynch 1985). Prior to analysis, N clonal lines are each split into M sublines, each of which is maintained for one or more generations (Figure 19.2). In the final analysis, each subline is replicated n times. The data are then subjected to an ordinary nested analysis of variance, again as described in Chapter 18. $ \sigma_{e}^{2} $ is the environmental variance within an immediate family, while $ \sigma_{b}^{2} $ (the variance among sublines within clones) is the residual environmental variance. If the sublines are separated for a single generation, $ \sigma_{b}^{2} $ is equivalent to the maternal-effects variance. For sublines separated for two generations, $ \sigma_{b}^{2} $ is the sum of the variance resulting from maternal and grandmaternal effects, and for a separation of three generations it includes the great-grandmaternal-effects variance as well. The among-clone component of variance, $ \sigma_{a}^{2} $, provides an estimate of the total genetic variance (plus any residual variance associated with ancestral effects).

**[示例 Example]**

> **Example 3** · ref: `Genetics_chapter19:3` · source: `Genetics_chapter19_005.json` · blocks 6–7
>
> Example 3. An application of nested ANOVA to a clonal population of the microcrustacean Daphnia pulex is given in the table below (data provided by K. Spitze). A group of 77 clones from a single pond were grown in the laboratory under controlled food and temperature conditions. Prior to analysis, each clone was split into two sublines for a generation, and two offspring from each subline (within each clone) were measured daily for growth in the first three instars. (There is a decline in clone number between instars because of mortality.)
> 
> <table><tr><td></td><td>df</td><td>Sums of Squares</td><td>Mean Squares</td><td>Expected MS</td><td>Variance Estimates ( $ \times 10^{4} $)</td></tr><tr><td>Instar 1</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Clone</td><td>76</td><td>0.2580</td><td>0.00340</td><td>$ \sigma_{e}^{2} + 2\sigma_{b}^{2} + 4\sigma_{a}^{2} $</td><td>Var(a) = 4.8**</td></tr><tr><td>Sublines (clone)</td><td>77</td><td>0.1152</td><td>0.00150</td><td>$ \sigma_{e}^{2} + 2\sigma_{b}^{2} $</td><td>Var(b) = 5.2**</td></tr><tr><td>Replicates</td><td>154</td><td>0.0700</td><td>0.00045</td><td>$ \sigma_{e}^{2} $</td><td>Var(e) = 4.5</td></tr><tr><td>Instar 2</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Clone</td><td>52</td><td>0.4595</td><td>0.00884</td><td>$ \sigma_{e}^{2} + 2\sigma_{b}^{2} + 4\sigma_{a}^{2} $</td><td>Var(a) = 9.4*</td></tr><tr><td>Sublines (clone)</td><td>53</td><td>0.2682</td><td>0.00506</td><td>$ \sigma_{e}^{2} + 2\sigma_{b}^{2} $</td><td>Var(b) = 14.6**</td></tr><tr><td>Replicates</td><td>106</td><td>0.2270</td><td>0.00214</td><td>$ \sigma_{e}^{2} $</td><td>Var(e) = 21.4</td></tr><tr><td>Instar 3</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Clone</td><td>35</td><td>0.4754</td><td>0.01358</td><td>$ \sigma_{e}^{2} + 2\sigma_{b}^{2} + 4\sigma_{a}^{2} $</td><td>Var(a) = 20.1*</td></tr><tr><td>Sublines (clone)</td><td>36</td><td>0.1998</td><td>0.00555</td><td>$ \sigma_{e}^{2} + 2\sigma_{b}^{2} $</td><td>Var(b) = -2.7</td></tr><tr><td>Replicates</td><td>72</td><td>0.4390</td><td>0.00610</td><td>$ \sigma_{e}^{2} $</td><td>Var(e) = 61.0</td></tr></table>


Estimates of the three variance components are obtained by setting the observed mean squares equal to their expectations and solving. Their significance, as determined by an F test of the ratio of adjacent mean squares, is denoted by * and **, respectively, for the 0.05 and 0.01 levels. Note that the variance among sublines is highly significant in the first two instars, suggesting the presence of substantial maternal effects. Such effects appear to be dissipated by the following instar.

The broad-sense heritability is estimated by

$$
H^{2}=\frac{\mathrm{Var}(a)}{\mathrm{Var}(a)+\mathrm{Var}(b)+\mathrm{Var}(e)}
$$


which gives values of 0.33, 0.21, and 0.26 for the three instars. All of these estimates are significant as revealed by F tests for the significance of the among-clone variance estimates, $ \mathrm{Var}(a) $.

Had the parental lines not been taken through the subline generation, the maternal-effects variance, $ \operatorname{Var}(b) $, would have been confounded with the genetic variance, $ \operatorname{Var}(a) $. The broad-sense heritability from a one-way analysis of variance would then have been equivalent to

$$
H^{2}=\frac{\mathrm{Var}(a)+\mathrm{Var}(b)}{\mathrm{Var}(a)+\mathrm{Var}(b)+\mathrm{Var}(e)}
$$


which yields estimates of 0.69, 0.54, and 0.23. Thus, failure to account for maternal effects in this study would have resulted in heritability estimates inflated by a factor of two for the first two instars.

---
