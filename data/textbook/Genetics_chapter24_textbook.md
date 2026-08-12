# Chapter 24 · Sex Linkage and Sexual Dimorphism

## Genetics_chapter24_001 · Sex Linkage and Sexual Dimorphism

In sexual species, males and females often differ with respect to the mean and variance of traits. In addition, the relative contribution of the different components of variance may differ between the sexes. There are two reasons for this. First, in the case of sex-linked genes, females have two possible genes at each locus, while males have only one (assuming, as we will below, that males are the heterogametic sex). Second, the expression of a gene may vary depending upon the sexual background within which it is found.

Although very little empirical work has been focused on these problems from a quantitative-genetic perspective, the theory, which involves a straightforward extension of Kempthorne's (1954) linear model, is fairly well developed. As the entire subject is relevant to the problem of sexual dimorphism and sexual selection, we examine the general principles in some detail. These were first presented by Bohidar (1964) and later clarified by James (1973) and Grossman and Eisen (1989). The two issues mentioned above, sex linkage and sex-specific expression, will be considered separately first and then combined in general form.

---

## Genetics_chapter24_002 · SEX-LINKED LOCI AND DOSAGE COMPENSATION

In the case of a specific sex-linked locus, the genotypic value of a male with allele i can be written

$$
G_{M i}^{\prime}=\mu_{M}+\alpha_{M i}^{\prime}
\tag{24.1a}
$$


where $ \mu_M $ is the mean phenotype of males, and $ \alpha'_{Mi} $ is the average effect of the ith allele measured as a deviation from $ \mu_M $, with a prime distinguishing a sex-linked locus from an autosomal locus. Since the expectation of $ \alpha'_{Mi} $ is zero, the total genetic variance due to this locus in males is simply $ \sigma^2(A'_{M}) = \sum p_i(\alpha'_{Mi})^2 $, where $ p_i $ is the frequency of the ith allele at the locus. Since males contain only one gene per sex-linked locus, there is no dominance genetic variance at such loci.

The situation in females is slightly more complicated since they have two alleles at each sex-linked locus. In this case, we write the genotypic value as

$$
G_{F i j}^{\prime}=\mu_{F}+\alpha_{F i}^{\prime}+\alpha_{F j}^{\prime}+\delta_{F i j}^{\prime}
\tag{24.1b}
$$


where $ \mu_{F} $ is the mean phenotype of females, $ \alpha'_{Fi} $ and $ \alpha'_{Fj} $ are the average effects of the ith and jth alleles as expressed in females, and $ \delta'_{Fij} $ is the dominance effect of the ijth genotype. It follows that the genetic variance due to a sex-linked locus in females is $ \sigma^{2}(\alpha_{Fi}^{\prime}) + \sigma^{2}(\alpha_{Fj}^{\prime}) + \sigma^{2}(\delta_{Fij}^{\prime}) = \sigma^{2}(A_{F}^{\prime}) + \sigma^{2}(D_{F}^{\prime}) $, the sum of the additive and dominance components of variance.

From Equations 24.1a,b, it can be seen that depending on the degree to which the additive effects of genes differ between the sexes and on the degree of dominance in females, the genetic variance associated with sex-linked loci is unlikely to be the same in the two sexes. For example, if $ \alpha'_{Mi} = \alpha'_{Fi} $ for all alleles, and if there are no dominance effects in females, then $ \sigma^{2}(A'_{F}) = 2\sigma^{2}(A'_{M}) $, i.e., the additive genetic variance due to the sex-linked locus in males would be only half that in females. However, $ \alpha'_{Mi} $ is often unequal to $ \alpha'_{Fi} $. For example, in females of many placental mammals, most of one of the X chromosomes is inactivated randomly in different cell lineages early in development (reviewed by Migeon 1994). In such species, females are functionally haploid mosaics at sex-linked loci. A familiar and most dramatic single-locus example of such mosaicism is that of the “tortoise-shell” cat. In cats, coat color genes lie on the X chromosome. If the two alleles in a female have different effects (black and yellow in the case of the “tortoise-shell” genotype), a mottled coat pattern results from the inactivation of different alleles in different somatic regions.

The adjustment of the total activity of sex-linked loci to achieve equality in the two sexes is known as $ \text{dosage compensation} $ (Muller 1932). For the compensatory mechanism noted above (complete inactivation of random alleles in females), a more appropriate expression for the genotypic value of females might be

$$
G^{\prime}_{Fij}=\mu_{F}+\frac{1}{2}\alpha^{\prime}_{Mi}+\frac{1}{2}\alpha^{\prime}_{Mj}+\delta^{\prime}_{Fij}
\tag{24.1c}
$$


This relationship implies an additive genetic variance of $ \sigma^2(\alpha_{Mi})/4+\sigma^2(\alpha_{Mj})/4=\sigma^2(\alpha_{M}^{\prime})/2 $, i.e., half that in males. Although we include a term for dominance in the above expression, it is unclear whether dominance occurs in the normal sense when only a single allele is active in each cell.

A second type of dosage compensation occurs when the same X chromosome is inactivated in all cells of a female. In this case, there is clearly no dominance effect, and our expression now becomes

$$
G_{F i j}^{\prime}=\mu_{F}+\alpha_{F i}^{\prime}
\tag{24.1d}
$$


so the additive genetic variance is simply $ \sigma^2(\alpha_{Fi}^\prime) $. This type of dosage compensation appears to be close to the situation in kangaroos and other marsupials, where the paternally derived X chromosome is inactivated in all cells (Cooper 1971). Note that even in this case, the sex-linked variation will only be equal in the two sexes if $ \alpha_{Fi}^\prime = \alpha_{Mi}^\prime $.

The mechanism of sex-linked dosage compensation in Drosophila, and presumably other insects, is somewhat different from that in mammals in that complete X chromosome inactivation does not occur. Instead, both X chromosomes are active in females, transcribing at about half the rate of those in males (Lucchesi 1978). Such dosage compensation has been demonstrated for a polygenic trait, abdominal bristle number, in Drosophila by Frankham (1977).

Using standard techniques involving chromosomal stocks with visible markers and cross-over suppressors, Frankham (1977) constructed 17 lines of Drosophila melanogaster with identical homozygous autosomal backgrounds, cytoplasmic backgrounds, and Y chromosomes. The only difference between the lines was their X chromosome. A simple one-way analysis of variance was then performed on the lines. Previous work had shown that the expression of bristle number genes is sex modified, counts in males being about 0.8 times those in females. Thus, in order to minimize the potential effects of scale differences on the variance, all measurements were log transformed (Chapter 11). The within-line component of variance provided an estimate of the environmental variance, since the lines were completely homozygous within the limits of the marker-inversion technique, and the among-line component estimated the genetic variance due to loci on the X chromosome. Separate analyses of males and females resulted in essentially identical estimates of X-linked genetic variance (both 0.00023).

Provided the scaling phenomenon has been accounted for properly, these results may have arisen in two ways. On average, only one of the two bristle number genes at each sex-linked locus may be active in females, in which case Equation 24.1d would be the appropriate model. Alternatively, the expression of both alleles may be suppressed at sex-linked loci in females, in which case a model of the form of Equation 24.1c would be required.

The first possibility was ruled out by further work. In one of the first successful attempts to identify a polygene, Frankham et al. (1980) verified that the sex-linked ribosomal RNA gene cluster is a major source of quantitative-genetic variation for bristle number in Drosophila. Complete inactivation of a gene with major effects in females would cause females to be much more similar to one parent (the one whose descendent X remained active) than the other, whereas partial inactivation of both would result in an intermediate phenotype. Frankham (1977) performed reciprocal crosses between his pure lines, and found that the phenotypic means of the reciprocal $ F_{1}s $ were, in fact, intermediate to those of the parentals and not significantly different from each other. Thus, the data suggest that the expression of sex-linked genes for bristle number is partially suppressed in females.

The mammalian (mouse/human) and Drosophila forms of dosage compensation outlined above are unlikely to be the only ones utilized by different species, but very little work has been done with other organisms. For the loci that have been examined in birds (Cock 1964) and Lepidoptera (Johnson and Turner 1979), groups where the females are heterogametic, there seems to be no dosage compensation. Two species of crickets have been examined, one having a mammalian form and the other a Drosophila form of compensation (Rao and Arora 1979, Rao and Ali 1982). Although the outcome of dosage compensation in the nematode Caenorhabditis elegans is essentially the same as in Drosophila, it is achieved by a very different mechanism (Parkhurst and Meneely 1994, Kelley and Kuroda 1995). In the following, we will treat Equations 24.1a,b as our general models for X-linked expression. Although we will not pursue them, models for the expression of Y-linked traits are very straightforward, in that females need not be considered and the male model is simply that of a haploid locus.

---

## Genetics_chapter24_003 · SEX-MODIFIED EXPRESSION OF AN AUTOSOMAL LOCUS

Just as the expressed effect of a sex-linked gene may vary between the sexes, so may the expression of any autosomal gene. For a single autosomal locus, we denote the genotypic values of females and males respectively as

$$
G_{F i j}=\mu_{F}+\alpha_{F i}+\alpha_{F j}+\delta_{F i j}
\tag{24.2a}
$$


$$
G_{M i j}=\mu_{M}+\alpha_{M i}+\alpha_{M j}+\delta_{M i j}
\tag{24.2b}
$$


The autosomal additive genetic variances of the two sexes are defined in the usual manner to be

$$
\sigma^{2}(A_{F})=\sigma^{2}(\alpha_{F i})+\sigma^{2}(\alpha_{F j})=2\sum p_{i}\alpha_{F i}^{2}=2\sigma^{2}(\alpha_{F})
\tag{24.3a}
$$


$$
\sigma^{2}(A_{M})=\sigma^{2}(\alpha_{M i})+\sigma^{2}(\alpha_{M j})=2\sum p_{i}\alpha_{M i}^{2}=2\sigma^{2}(\alpha_{M})
\tag{24.3b}
$$


and the dominance components are

$$
\sigma^{2}(D_{F})=\sum p_{i j}\delta_{F i j}^{2}=\sigma^{2}(\delta_{F})
\tag{24.4a}
$$


$$
\sigma^{2}(D_{M})=\sum p_{i j}\delta_{M i j}^{2}=\sigma^{2}(\delta_{M})
\tag{24.4b}
$$


where $ p_{ij} $ is the frequency of the ijth genotype.

---

## Genetics_chapter24_004 · SEX-MODIFIED EXPRESSION OF AN AUTOSOMAL LOCUS / Gametic Imprinting

Before proceeding, we mention a rather different type of sex modification of gene action. Over the past few years, several studies, mostly in transgenic mice, have demonstrated the phenomenon of gametic imprinting, whereby certain genes carry a memory of their gametic origin and are expressed differently in progeny depending upon whether they are paternally or maternally inherited (Solter 1988; Hall 1990; Barlow 1994, 1995). Under this type of sex modification, the expression of a gene depends not just on the gender of the zygote within which it is found, but also on the sex from which it was inherited. Some imprinted genes are totally inactivated, whereas others have suppressed activities in specific tissues. The interesting aspect of this phenomenon is that the imprint on a gene is only transiently heritable — it is totally erased in a single generation if it passes through the nonimprinting sex. For example, if a gene inactivated by paternal imprinting is inherited by an offspring, it will be reactivated after it is transferred to the next generation through a daughter's gamete, while remaining inactivate when passed through a son. The mechanisms of imprinting appear to involve DNA methylation, but are otherwise poorly understood. Essentially nothing is known of its importance in the expression of quantitative characters.

However, a simple example illustrates the potential significance of gametic imprinting in the interpretation of quantitative-genetic analyses. Consider a single locus for which imprinting occurs in male gametes and erasure of imprinting occurs in female gametes. This implies that every individual has one imprinted (+) allele and one nonimprinted (−) allele. Thus, if an $ A_{+}/a_{-} $ individual is a male, it will produce $ A_{+} $ and $ a_{+} $ gametes, and if it is a female, it will produce $ A_{-} $ and $ a_{-} $ gametes. In both cases, there has been a change in state in one of the two alleles. This implies that there is a 50% chance that an allele inherited by an offspring will have experienced a change in state relative to that expressed in the parent (compared to a zero probability for a locus not experiencing imprinting). Now consider the similarity of gene expression for sibs. In this case, regardless of whether imprinting occurs, there is a 50% chance that the alleles derived by sibs from the same heterozygous parent are identical in expression (in the sibs). Thus, the net result of gametic imprinting is to reduce the expected phenotypic covariance between parents and offspring relative to that between sibs. A difference between the parent-offspring covariance and twice the covariance between paternal half sibs that is significantly less than zero would be compatible with the hypothesis of significant gametic-imprinting effects on the expression of a quantitative trait.

---

## Genetics_chapter24_005 · EXTENSION TO MULTIPLE LOCI AND THE COVARIANCE BETWEEN RELATIVES

As first shown by Bohidar (1964), it is a relatively straightforward procedure to extend the general model of Kempthorne (1954) to describe polygenic situations in which sex linkage and sex modification of gene expression are involved. The only modification of the description of the phenotypic resemblance between relatives is the need to consider the sexes of the individuals involved. To simplify discussion, we ignore sources of genetic variation due to maternal effects (Chapter 23).

Let us first examine relationships involving only males. Three groups of factors must be considered. First, for the autosomal loci, we must account for the additive, dominance, and various epistatic effects. Second, for the sex-linked loci, there are no terms involving dominance since only a single gene is active at each locus, but additive and epistatic effects involving additive interactions must be considered. Third, the possibility of epistatic interactions between auto- somal and sex-linked loci must be recognized. Under random mating, as shown by Kempthorne (1954) and discussed previously (Chapter 5), the covariances between different terms in the expression for a genotypic value are all zero, so that the genotypic variance for males may be written

$$
\begin{aligned}\sigma^{2}(G_{M})&=\sigma^{2}(A_{M})+\sigma^{2}(D_{M})+\sigma^{2}(A_{M}A_{M})+\sigma^{2}(A_{M}D_{M})+\cdots\\&\quad+\sigma^{2}(A_{M}^{\prime})+\sigma^{2}(A_{M}^{\prime}A_{M}^{\prime})+\cdots\\&\quad+\sigma^{2}(A_{M}A_{M}^{\prime})+\sigma^{2}(A_{M}^{\prime}D_{M})+\cdots\end{aligned}
\tag{24.5a}
$$


where primed and unprimed elements refer to sex-linked and autosomal loci, respectively. Variances with two terms within parentheses denote epistatic effects. For example, $ \sigma^{2}(A_{M}A_{M}^{\prime}) $ is the variance due to additive × additive interactions between autosomal and sex-linked loci in males.

Under the usual assumptions of random mating and free recombination, the genotypic covariance between two males may be expressed as a sum of variance terms each weighted by an appropriate measure of relatedness. Letting x and y represent the two males, then

$$
\begin{aligned}\sigma(G_{Mx},G_{My})&=2\Theta_{xy}\sigma^{2}(A_{M})+\Delta_{xy}\sigma^{2}(D_{M})+\phi_{xy}\sigma^{2}(A_{M}^{\prime})\\&+\sum(2\Theta_{xy})^{\alpha}\Delta_{xy}^{\beta}\phi_{xy}^{\lambda}\sigma^{2}[A_{M}^{\alpha}D_{M}^{\beta}(A_{M}^{\prime})^{\lambda}]\end{aligned}
\tag{24.5b}
$$


Except for the introduction of the new term $ \phi_{xy} $, this expression is nearly identical in structure to Kempthorne's equation for autosomal loci (Chapter 7). $ \phi_{xy} $ is the probability that a sex-linked gene in male x is identical by descent with that at the same locus in male y. Unlike $ \Theta_{xy} $, $ \phi_{xy} $ is not preceded by a 2 because sex-linked loci exist in a haploid state in males. The final summation collects all of the covariance due to epistatic effects; it involves all terms for which $ \alpha + \beta + \lambda \geq 2 $, with $ \alpha $, $ \beta $, and $ \lambda $ representing, respectively, the number of autosomal additive, autosomal dominance, and sex-linked additive effects in the epistatic interaction.

Expressions for some common male-male relationships are outlined in Table 24.1. The respective values of $ 2\Theta_{xy} $ and $ \Delta_{xy} $ should be familiar by now. $ \phi_{xy} $ is zero for a father-son relationship, since the son always obtains its X chromosome from its mother. Similarly, $ \phi_{xy} = 0 $ for paternal half sibs, since the X chromosome of each half sib comes from a different mother. On the other hand, $ \phi_{xy} = 1/2 $ for full brothers and maternal half brothers, since they share the same mother, who contributes to each of them one of her two X chromosomes. Finally, one of the X chromosomes of a mother must have come from her father. Thus, there is a 50% chance that the X chromosome contained in a male is identical by descent with that of his maternal grandfather. The table shows that if genetic variance exists at sex-linked loci, the covariance between grandfather and grandson will be greatest in the case of a maternal grandfather.

**[Table]**

*[See Table 24.1 at the end of this section.]*

The genetic variance of females can be described in a similar manner, except that we must also account for dominance interactions at the sex-linked loci,

$$
\begin{align*}\sigma(G_{F})=&\sigma^{2}(A_{F})+\sigma^{2}(D_{F})+\sigma^{2}(A_{F}A_{F})+\sigma^{2}(A_{F}D_{F})+\cdots\\\sigma^{2}(A_{F}^{\prime})&+\sigma^{2}(D_{F}^{\prime})+\sigma^{2}(A_{F}^{\prime}A_{F}^{\prime})+\sigma^{2}(A_{F}^{\prime}D_{F}^{\prime})+\cdots\\\sigma^{2}(A_{F}A_{F}^{\prime})&+\sigma^{2}(A_{F}^{\prime}D_{F})+\sigma^{2}(A_{F}D_{F}^{\prime})+\sigma^{2}(D_{F}D_{F}^{\prime})+\cdots\end{align*}
\tag{24.6a}
$$


The genetic covariance between two females is then

$$
\begin{align*}\sigma(G_{Fx},G_{Fy})&=2\Theta_{xy}\sigma^{2}(A_{F})+\Delta_{xy}\sigma^{2}(D_{F})+2\Theta_{xy}^{\prime}\sigma^{2}(A_{F}^{\prime})+\Delta_{xy}^{\prime}\sigma^{2}(D_{F}^{\prime})\\&\quad+\sum(2\Theta_{xy})^{\alpha}\Delta_{xy}^{\beta}(2\Theta_{xy}^{\prime})^{\lambda}(\Delta_{xy}^{\prime})^{\delta}\sigma^{2}[A_{F}^{\alpha}D_{F}^{\beta}(A_{F}^{\prime})^{\lambda}(D_{F}^{\prime})^{\delta})\quad\mathrm{ 卞 }\\ \end{align*}
\tag{24.6b}
$$


where $ \Theta_{xy}^{\prime} $ and $ \Delta_{xy}^{\prime} $ are the coefficients of coancestry and fraternity for sex-linked loci in female-female relationships. Again, the summation compiles all of the genetic covariance due to epistatic interactions such that $ \alpha + \beta + \lambda + \delta \geq 2 $, where $ \alpha, \beta, \lambda $, and $ \delta $, respectively, represent the number of autosomal additive, autosomal dominance, sex-linked additive, and sex-linked dominance effects in an epistatic interaction.

Note that the coefficients of identity for female-female relationships often differ for autosomal and sex-linked loci. Consider, for example, full sisters. We already know that $ 2\Theta_{xy} = 1/2 $ and $ \Delta_{xy} = 1/4 $ in this case. However, for a sex-linked locus, $ 2\Theta_{xy}' = 3/4 $ and $ \Delta_{xy}' = 1/2 $. This result can be seen as follows. If single X chromosomes are drawn randomly from two full sisters, both may be paternal in origin with probability 1/4, in which case they must be identical by descent since a father has only one X chromosome. Both may be maternal in origin with probability 1/4, in which case there is a 1/2 probability of identity by descent. If one is paternal and the other maternal, the two X-linked alleles cannot be identical by descent. Therefore, $ 2\Theta_{xy} = 2[(1)(1/4) + (1/2)(1/4) + (0)(1/2)] = 3/4 $. Both full sisters obtained the same X chromosome from their father and have a 50% chance of obtaining the same X from their mother. Therefore, $ \Delta_{xy}' = 1/2 $, which contrasts with $ \Delta_{xy} = 1/4 $ for autosomal loci.

Finally, we consider the slightly more complicated case of genetic covariance between members of different sexes. In this case, a new coefficient, $ \gamma_{xy} $, must be introduced to denote the probability that a sex-linked gene in male y is identical by descent with that in a female relative x. In addition, new notation needs to be introduced to describe the covariance between gene effects as expressed in the different sexes — $ \sigma(A_F, A_M) $ and $ \sigma(D_F, D_M) $ for additive and dominance effects at autosomal loci, and $ \sigma(A'_F, A'_M) $ for sex-linked additive effects. For epistasis, we will use terms of the form $ \sigma(\ldots F_M, \ldots F_M, \ldots) $, where, for example, $ \sigma(A'_FM D_FM) $ refers to the covariance across the sexes of epistatic effects involving sex-linked additive and autosomal dominance interaction. These modifications lead to the following expression for the male-female covariance

$$
\begin{aligned}\sigma(G_{Fx},G_{My})&=2\Theta_{xy}\sigma(A_{F},A_{M})+\Delta_{xy}\sigma(D_{F},D_{M})+2\gamma_{xy}\sigma(A_{F}^{\prime},A_{M}^{\prime})\\&\quad+\sum(2\Theta_{xy})^{\alpha}\Delta_{xy}^{\beta}(2\gamma_{xy})^{\lambda}\sigma[A_{FM}^{\alpha}D_{FM}^{\beta}(A_{FM}^{\prime})^{\lambda}]\end{aligned}
\tag{24.7}
$$


Note that there are no terms involving sex-linked dominance effects $ (D') $ since they do not exist in males.

We will not pursue the methodological details of estimating components of genetic variance and covariance in the presence of sex linkage and sex modification any further, except by means of example. It should be clear from arguments in previous chapters and from the expressions in Table 24.1 that through the estimation of covariances between appropriate sets of relatives, most of the causal components of genetic variance can be extracted by the method of moments, assuming that the epistatic components are of negligible importance. Any of the methods described in previous chapters can be used for these purposes, the only new distinction being the need to analyze males and females separately. Further information on methodology employing sib analyses may be found in Bohidar (1964) and Eisen and Legates (1966). Risch (1979) gives results for populations undergoing assortative mating.

From estimates of the additive genetic covariances, it is possible to estimate the genetic correlation across the sexes for autosomal and/or sex-linked loci, defined respectively as

$$
\rho_{FM}(A)=\frac{\sigma(A_{F},A_{M})}{\sigma(A_{F})\sigma(A_{M})}
\tag{24.8a}
$$


$$
\rho_{F M}(A^{\prime})=\frac{\sigma(A_{F}^{\prime},A_{M}^{\prime})}{\sigma(A_{F}^{\prime})\sigma(A_{M}^{\prime})}
\tag{24.8b}
$$


High values for these correlations suggest a high degree of overlap in the sets of genes expressed in the different sexes. All of the techniques described in Chapter 22 for estimating Falconer’s genetic correlation across environments are relevant here, as the two sexes can be treated as fixed effects. (They are essentially two genetic environments within which gene expression occurs.)

**[示例 Example]**

> **[UNRESOLVED EXAMPLE: Genetics_chapter24:1]**


The estimated heritabilities in males average only a few percent greater than those in females. Averaged over all characters, sex-linked loci account for about 12% of the phenotypic variance among males and 8% among females. The total additive genetic correlations across the sexes are quite high, suggesting that an average of approximately 81% of the additive variance in the two sexes is caused by shared genes.

> **Table 24.1** · `24.1` · page 733 · source: `Genetics_chapter24_005`
> Table 24.1 Coefficients needed for the expressions describing the expected phenotypic covariance between relatives in a model that includes sex-linkage and sex-dependent gene expression.
>
> Male-male relationships | 2 $ \Theta_{xy} $ | $ \Delta_{xy} $ | $ \phi_{xy} $ |
> --- | --- | --- | --- | ---
> Father-son | 1/2 | 0 | 1/4 |
> Full brothers | 1/2 | 1/4 | 1/2 |
> Paternal half brothers | 1/4 | 0 | 0 |
> Maternal half brothers | 1/4 | 0 | 1/2 |
> Paternal grandfather-grandson | 1/4 | 0 | 0 |
> Maternal grandfather-grandson | 1/4 | 0 | 1/2 |
> Monozygotic twins | 1 | 1 | 1 |
> Female-female relationships | 2 $ \Theta_{xy} $ | $ \Delta_{xy} $ | 2 $ \Theta'_{xy} $ | $ \Delta'_{xy} $
> Mother-daughter | 1/2 | 0 | 1/2 | 0
> Full sisters | 1/2 | 1/4 | 3/4 | 1/2
> Paternal half sisters | 1/4 | 0 | 1/2 | 0
> Maternal half sisters | 1/4 | 0 | 1/4 | 0
> Paternal grandmother-granddaughter | 1/4 | 0 | 1/2 | 0
> Maternal grandmother-granddaughter | 1/4 | 0 | 1/4 | 0
> Monozygotic twins | 1 | 1 | 1 | 1
> Male-female relationships | 2 $ \Theta_{xy} $ | $ \Delta_{xy} $ | $ \gamma_{xy} $ |
> Father-daughter | 1/2 | 0 | 1 |
> Mother-son | 1/2 | 0 | 1 |
> Full brother and sister | 1/2 | 1/4 | 1/2 |
> Paternal half brother and sister | 1/4 | 0 | 0 |
> Maternal half brother and sister | 1/4 | 0 | 1/2 |
> Paternal grandfather-granddaughter | 1/4 | 0 | 0 |
> Maternal grandfather-granddaughter | 1/4 | 0 | 1/2 |
> Paternal grandmother-grandson | 1/4 | 0 | 0 |
> Maternal grandmother-grandson | 1/4 | 0 | 1/2 |

---

## Genetics_chapter24_006 · VARIATION FOR SEXUAL DIMORPHISM

In the previous sections, we recognized the fact that many characters are sexually dimorphic. However, we did not consider whether the dimorphism itself is evolutionarily labile, as opposed to being a fixed difference that inevitably results from physiological and/or hormonal differences between males and females. Sexual dimorphisms are of interest to evolutionary ecologists for two reasons. First, dimorphisms in foraging strategies and/or morphologies are potentially selectively advantageous because they reduce competition between the sexes for food; a highly dimorphic pair of parents may provide an exceptionally broad base of food for their offspring, thereby enhancing their fitness. Second, sexual dimorphisms frequently have been attributed to sexual selection. When individuals exercise mate choice, they exert a selective pressure on the characters in the opposite sex that are the criteria for choice.

Robertson (1959b) first pointed out that the existence of genetic variation for sexual dimorphism requires that the correlation between the effects of genes in males and females must be less than one. Strictly speaking, this criterion holds only when the genetic variance is equal in the two sexes (analogous to the situation with genotype × environment interaction, Chapter 22). For an allele i at an autosomal locus, $ (\alpha_{Mi} - \alpha_{Fi}) $ provides a measure of the dimorphic effect. The variance of this quantity is $ \sigma^{2}(\alpha_{M}) - 2\sigma(\alpha_{M}, \alpha_{F}) + \sigma^{2}(\alpha_{F}) = \sigma^{2}(\alpha_{M}) + \sigma^{2}(\alpha_{F}) - 2\rho_{FM}[\sigma(\alpha_{F})\sigma(\alpha_{M})] $, where $ \rho_{FM} $ is the correlation between $ \alpha_{Mi} $ and $ \alpha_{Fi} $. If the two sexes have the same variance, $ \sigma^{2}(\alpha_{Mi} - \alpha_{Fi}) = 2\sigma^{2}(\alpha)[1 - \rho_{FM}] $, which is zero only when $ \rho_{FM} = 1 $. By summing over all loci, we may define the total additive genetic variance for sexual dimorphism associated with autosomal loci to be

$$
\sigma_{M-F}^{2}(A)=\sigma^{2}(A_{M})+\sigma^{2}(A_{F})-2\sigma(A_{F},A_{M})
\tag{24.9}
$$


all three of the components on the right having been defined in the previous section. Thus, the additive genetic variance for sexual dimorphism can be calculated from estimates of the covariance between relatives that yield estimates of the components $ \sigma^{2}(A_{M}), \sigma^{2}(A_{F}), $ and $ \sigma(A_{F}, A_{M}) $.

**[示例 Example]**

> **[UNRESOLVED EXAMPLE: Genetics_chapter24:2]**


Numbers in parentheses are standard errors of the estimates, ages are in weeks, and V and C denote Var and Cov, respectively.

In addition to the results in the previous example, there have been a number of reports of genetic correlations across the sexes that are not significantly different from one: pupal weight in Tribolium (Enfield et al. 1966), weight and fleece characteristics in domesticated sheep (Vesely and Robison 1971), height in humans (Rogers and Mukherjee 1992), bill color in zebra finches (Price and Burley 1993), and morphological characters in Drosophila (Example 1). In all of these cases, although a sexual dimorphism has clearly evolved for the character under study, the further evolution of dimorphism is tightly constrained — selection on either of the sexes would cause an almost perfectly correlated response in the opposite sex.

Some exceptions to this pattern of $ r_{FM}(A) = 1 $ have emerged. For example, Møller (1993) obtained an additive genetic correlation of tail length in male and female barn swallows (Hirundo rustica) of $ 0.55 \pm 0.16 $. Meagher (1992) used correlations of family means to estimate genetic correlations across the sexes for a diversity of characters in the dioecious plant Silene latifolia. This approach causes a downward bias in the absolute value of estimates (Chapter 21), so it is difficult to evaluate the significance of some of his results. On the other hand, Meagher found significantly negative correlations across the sexes for some pairs of reproductive traits. Since the true correlations were probably even more negative, this suggests negative pleiotropic effects of some genes on fitness as expressed in males vs. females. The following example provides a clear-cut case of heritability for sexual dimorphism.

**[示例 Example]**

> **[UNRESOLVED EXAMPLE: Genetics_chapter24:3]**


---
