# Chapter 24 Textbook Mapping

## chapter24_001 · The Infinitesimal Model and Its Extensions: Introduction

Normal theory is clearly the most powerful and problematic hypothesis in the present analysis. Chevalet (1988)

What, me normal? Turelli and Barton (1994) As detailed in Chapters 6, 13, and 16, the response to a single generation of selection in a quantitative trait can often be closely predicted from macroscopic (observable) features of that trait, namely, its variance components. This is in sharp contrast to predicting selection response under one- and two-locus models, which requires detailed knowledge of the underlying genotype frequencies and effects (Chapter 5). Hence, population-genetic predictions typically require knowledge of microscopic (largely unobservable) genetic parameters. The breeder's equation (13.1) and the Bulmer equation (16.7b) are examples of macroscopic-based predictors. In contrast, the Price equation (6.8) is a microscopic-based predictor, given its composite transmission parameter, $ \sigma(w, \delta) $, which is, at best, very challenging to measure (and is even harder to iterate over generations).

**[命题 Proposition]**

These variance-component predictors, which underlie much of the quantitative-genetic theory of response, are, of course, approximations, but often very good ones, especially over short time scales. Their single-generation versions follow from the assumption of a linear and homoscedastic parent-offspring regression, and their extension to multiple generations requires not only that linearity and homoscedasticity hold following selection, but also that any selection-induced changes in the variance components (which determine the slopes of these regressions) are largely predictable from macroscopic parameters (for example, via the Bulmer equation).

The justification for these approaches is usually framed by invoking a set of assumptions that we have been loosely calling the infinitesimal model. At various times, we have used either one, or more, of the assumptions of: (i) a very large (effectively infinite) number of loci, each with very small (effectively infinitesimal) effects; (ii) a normally distributed genotypic distribution in a randomly mating population under no selection, and, hence parent-offspring regressions that are linear and homoscedastic; and (iii) that the genotypic distributions stay at least close to Gaussian (normal) following selection such that the linear and homoscedastic regressions approximately hold.

The goal of this chapter, which is rather technical in places, is to examine in more detail the various infinitesimal approximations that we have made and to examine the consequences for selection response when they fail. We start by deconstructing what we have called the standard infinitesimal model (the joint assumptions of very large numbers of loci and parent-offspring regressions that are linear and homoscedastic) into its components and examine how these are connected, and also when they fail. As we will see, despite the use of the term standard, there is actually a nested family of infinitesimal models that make increasingly stringent assumptions, which correspond to assumptions (i) through (iii), which were just mentioned (Table 24.1).

We then introduce the Gaussian approximation, one of a broad group of continuum-of-alleles (or COA) models, assuming a finite number of loci, with a distribution of allelic effects at a locus (as opposed to a fixed number of possible alleles), with mutation likely generating alleles not previously segregating in the population. The Gaussian approximation assumes that the distribution of allelic effects at each locus is normal. With a large number of loci, the results from Gaussian COA models approach those obtained under the infinitesimal

**[Table]**

> **Table 24.1** · `24.1` · page 2 · source: `chapter24_001`
> Table 24.1 Classification of the different versions of the infinitesimal model, based on Turelli (2017). Note that these models are nested, such that a model makes all of the assumptions of any model that proceeded it in the table.
>
> Infinitesimal geneticsA large number of loci, each with vanishingly small effects. | Fisher (1918)
> --- | ---
> Gaussian descendants (Fisher-Bulmer Infinitesimal)Within-family segregation variance independent of parental phenotypes, depending only on the relatedness of parents. | Bossert (1963)
> In the limit, results in a Gaussian distribution of breeding values in their unselected descendants. Parent-offspring regressions are linear and homoscedastic. | Fisher (1918), Bulmer (1971b), Barton et al. (2017)
> Gaussian populationsThe distribution of breeding values in a population is Gaussian. | 


model, thus serving as a bridge between models assuming effectively an infinite number of loci (each with a small number of possible alleles, typically biallelic) and models assuming a very large (effectively infinite) potential number of alleles at a finite number of loci. We then examine the effects of linkage on the behavior of these models, and conclude by examining the selection response when the distribution of breeding values is no longer Gaussian.

The goal of this chapter is to start to bridge short-term predictors of response based on macroscopic parameters with predictors of long-term response based on microscopic parameters. After sufficient allele-frequency change accrues, these bridging models break down, thus imposing the need for explicit population-genetic models (Chapter 5), which are examined in Chapters 25–28.

---

## chapter24_002 · The Infinitesimal Model and Its Extensions: Introduction / THE INFINITESIMAL: A FAMILY OF MODELS

**[命题 Proposition]**

We have been somewhat cavalier in our use of the term infinitesimal model, as there is considerable ambiguity as to what this term formally means. Further, what is required from an infinitesimal assumption depends the on problem being considered: Is one making the assumption of very small allele-frequency change? The assumption of a linear, and homoscedastic, parent-offspring regression? The assumption that the distribution of breeding values in a population is Gaussian (normally distributed) and is largely unaltered by selection? As shown in Table 24.1, there is a nested hierarchy of models, which impacts the assumptions one is actually making when invoking the infinitesimal.

Following Turelli (2017), one can consider three nested versions of the model. The simplest, infinitesimal genetics, matches Fisher's (1918) approximation of describing the trait architecture as consisting of a very large number of loci, each of small effect. A direct consequence of this model is that allele-frequency changes are very small, as the time scale for frequency change scales with the inverse of allelic-effect size (Equation 5.21).

**[命题 Proposition]**

The next-level model, which Turelli (2017) named Gaussian descendants, starts with the assumption (for unrelated and outbred parents) of a constant within-family variance that is independent of the phenotypes of this parents. Such a constant segregation kernel variance was first considered in Bossert's (1963) unpublished thesis, and this is simply half of the genic variance (Equation 16.2). As we saw in Example 16.2, the within-family segregation variance is reduced when parents are inbred, so a slightly more generalized assumption is a segregation variance that only depends on the relatedness of the parents (Bulmer 1971b, Barton et al. 2017). As suggested by Fisher (1918), and most generally shown by Barton et al. (2017), the assumption of a large number of loci (the infinitesimal genetics model) in the limit (provided linkage is not too extreme) leads to a Gaussian (normally) distribution of breeding values among the offspring of a set of parents, whose variance only depends on the parental relationship. Hence, the oft-used infinitesimal assumption of linear regressions and homoscedastic variances follows from this limit.

The Gaussian descendants version of the infinitesimal model is the starting point for most of our previous discussions about the impact of a single generation of selection from an unselected base population, and it forms the foundation for BLUP. We take this version—an efficiently infinite number of loci, a segregation variance that only depends upon relatedness, and a Gaussian distribution of breeding values in the absence of selection (and hence linear and homoscedastic parent-offspring regression)—as the standard infinitesimal model. We will also refer to this particular set of assumptions as the Fisher-Bulmer infinitesimal model.

**[命题 Proposition]**

The most restrictive of the infinitesimal family of models is what Turelli (2017) called the Gaussian populations assumption. Here, the population (as opposed to the within-family) distribution of breeding values is Gaussian. This is the infinitesimal assumption which is used to predict selection response over multiple generations. As we will show later in the chapter, this generally does not hold, even when starting with the Fisher-Bulmer infinitesimal model, as selection (through generating disequilibrium) will drive any initially Gaussian distribution away from normality. The key observation is that while the distribution of breeding values within a family may stay Gaussian following selection, a population is a collection of families. If the distribution of family means is highly non-Gaussian (as might be expected to be generated following selection on a trait), then the population distribution will depart from normality. Gaussian within-family segregation will recover some of the normality in the offspring generation, and the critical question is whether this is usually enough to approximately recover the Gaussian populations assumption.

The key points we will make below are as follows: First, allele-frequency change from selection on a trait with a finite number of loci tends to drive the distribution of breeding values away from a Gaussian, but the degree of subsequent departure quickly diminishes as the number of loci increases. Second, selection-induced correlations over alleles from different loci (linkage disequilibrium) will drive even a trait with infinitesimal genetics away from a Gaussian. And third, when the within-family segregation remains Gaussian, this will partly restore a population-level Gaussian distribution, but departures away from a Gaussian will remain in the population until selection has ceased and recombination removes among-locus correlations.

---

## chapter24_003 · The Infinitesimal Model and Its Extensions: Introduction / THE INFINITESIMAL GENETICS MODEL: EMPIRICAL DATA

Fisher's (1918) motivation for the infinitesimal genetics model, which assumed that many genes of small effect underlie a typical trait, was part mathematical convenience and part biological approximation. Early on, many geneticists, trained in dissecting the action of single genes of modest to large effect, questioned the validity of this biological motivation. This objection was reinforced in the mid-1980s when QTL mapping experiments seemed to detect abundant major-effect QTLs, each accounting for 10% or more of the phenotypic variation (LW Chapter 15). However, with the advent of more powerful genomic tools, attempts to isolate the underlying nucleotide sites behind these major QTLs grew increasingly frustrating. A major QTL (indicated by a large peak in the likelihood surface spanning some genomic region; LW Chapter 15) seen in the cross of two inbred lines often fractionated into several minor peaks upon finer mapping, and each of these minor peaks further fractionated as attention was turned to them. While genes of large effect have been found, what frequently appeared to be a single major gene turned out to be a number of tightly linked regions of much smaller effect (reviewed by Flint and Mackay 2009; Mackay et al. 2009).

This trend continued during the GWAS (genome-wide association study) phase of quantitative genetics (starting in the early 2000s). Association mapping (LW Chapter 16) uses population-level disequilibrium and therefore allows for mapping on a kilobase scale, as opposed to the tens of megabase scale for QTL resolution (the typical confidence interval in a QTL mapping experiment; LW Chapter 15). The broad conclusions from a large number of studies on human traits (mainly, but not exclusively, diseases) with enormous sample sizes (in the tens of thousands or greater) are twofold (Visscher et al. 2012a).

First, the effects of detected sites (measured by the marker-associated variance) tend to be very small. For example, over 600 variants associated with human height variation have been detected, most of which typically account for only a minuscule fraction of the additive variance (Lango Allen et al. 2010; Yang et al. 2010; Wood et al. 2014). Further, estimates suggest that the actual number of genes influencing human height is significantly greater than 600, running from over 1600 (Kemper et al. 2012) to “a very large but finite number (thousands) of causal variants” (Wood et al. 2014). Gene knockout experiments (Reed et al. 2008) have suggested roughly 6000 genes with the potential to influence body weight in mice, while the response to artificial selection on body size in Drosophila involves between 300 and 1200 regions (Turner et al. 2011). Finally, in a number of studied traits the fraction of additive-genetic variation accounted for by SNPs on a per-chromosome basis is proportional to chromosomal length (Visscher et al. 2007; Yang et al. 2011b; Yang et al. 2013). This observation is consistent with an infinitesimal-like model of a very large number of small-effect loci uniformly distributed over the genome.

Second, the total additive variance accounted for by all detected sites is only a small fraction (around 10%) of the total additive variance for the same trait estimated from the resemblance between relatives (in humans, typically twin studies). The latter observation led to concerns about “missing heritability” (Mather 2008; Manolio et al. 2009) and a large number of subsequent papers attempting to account for this apparent paradox. In reality, this observation of missing heritability provides strong support for the infinitesimal genetics model. In testing up to millions of SNPs for association in a GWAS, stringent thresholds are set to control for multiple comparisons (Appendix 4). This, in turn, requires larger effect sizes in order for a given marker to be declared significant, which excludes many biologically relevant SNPs from the model using all of the detected sites.

By using mixed-model approaches that allow all SNPs to be incorporated (by shrinking the effects of most SNPs toward zero), Yang et al. (2010) could account for ~45% of the additive variance in human height. Similar findings were seen for schizophrenia (Purcell et al. 2009) and a growing number of other traits (e.g., Hill 2010; Vinkhuyzen et al. 2013; Yang et al. 2013; Robinson 2014). Example 24.1 illustrates how incomplete linkage disequilibrium (in which the marker and causative alleles are less than completely associated) can easily account for the remaining fraction of the “missing” heritability. Lee et al. (2011) reviewed approaches for estimating this hidden (not missing) heritability in GWAS studies using mixed models (and hence essentially assuming the Gaussian descendants version of the infinitesimal model). Thus, we have come full-circle from the early QTL days in that current genomic data for many traits are most consistent with a very large number of loci, each with a small effect. This is not to say that major alleles do not exist, but rather that they tend to be rare. Indeed, the effect detected in a GWAS study is the additive variance associated with a marker SNP (LW Chapter 16), so finding that the vast majority of sites have a low effect variance does not imply that they involve alleles of small effects. If alleles of large effect tend to be rare, they will display small variances, although the presence of such alleles has consequences for the prediction of selection response (as we detail below). Notably, Kemper et al. (2012) found a negative correlation between frequency and effect size of alleles influencing human height (see Figure 28.5).

**[示例 Example]**

> **Example 24.1** · ref: `24.1` · source: `chapter24_003.json` · blocks 5–5
>
> Example 24.1. As an example of one source of “missing heritability,” consider a site at which a new QTL allele, Q, with an additive effect of a, arises on a SNP marker background, with M and m being the two marker alleles. The strongest marker association occurs when Q is completely restricted to the background on which it arose, so we assume this here, with Q only found on M-bearing haplotypes. Moreover, only a fraction, $ \xi $, of M haplotypes will harbor Q, and (as we now demonstrate), this results in hidden heritability. Summarizing these assumptions, we have:
> 
> > **Inline Table 1** · `inline_1` · page 5 · source: `chapter24_003`
> > Inline Table 1
> >
> > Gamete | Frequency | Effect
> > --- | --- | ---
> > MQ | $ p\xi $ | a
> > Mq | $ p(1-\xi) $ | 0
> > mq | $ 1-p $ | 0
> > mQ | 0 | a
> 
> 
> Hence, the frequencies of M and Q are, respectively, p and $ p\xi $. The resulting additive variance due to the causal site becomes $$ \sigma_{A}^{2}(Q T L)=2a^{2}(p\xi)(1-p\xi)\simeq2a^{2}p\xi $$ with the approximation following because $ p\xi \ll 1 $. Conversely, the average effect of marker allele $ M $ is $ a\xi + 0(1 - \xi) = \xi a $, while the value for $ m $ is zero, making the additive variance associated with this marker $$ \sigma_{A}^{2}(M)=2(\xi a)^{2}(p)(1-p)=2a^{2}p(1-p)\xi^{2} $$ The resulting ratio of the marker to causal additive variances is $$ \sigma_{A}^{2}(M)/\sigma_{A}^{2}(Q T L)=\xi(1-p)/(1-\xi p)\simeq\xi $$ Thus, if Q is somewhat rare on M backgrounds, only of a fraction, $ \xi $, of the actual variance is accounted for by the linked SNP. This situation would occur if the site-frequency spectrum (SFS) for QTLs alleles is shifted toward smaller values relative to the SFS for the marker alleles. Both the ascertainment for common SNPs and weak selection against QTL alleles could generate such a shift. While the value of $ \xi $ is unknown, suppose that, on average, $ \xi \simeq 0.5 $: then, at most 50% of the total variation from the causative sites can be captured by markers. This value is very close to the value of 45% of the variance accounted for by Yang et al. (2010) for human height. Further, this calculation is biased in favor of marker variances as it assumes complete disequilibrium (i.e., Q is only found on the M background). If some of the m-bearing chromosomes also carry Q, the fraction of the causal variance accounted for by the marker variance will be even less.


---

## chapter24_004 · The Infinitesimal Model and Its Extensions: Introduction / THEORETICAL IMPLICATIONS OF THE INFINITESIMAL GENETICS MODEL

Under the classic infinitesimal genetics model introduced by Fisher (1918), a character is determined by an infinite number of unlinked and nonepistatic loci, each with an infinitesimal effect. It is occasionally assumed that each locus has two alleles and that the effects and frequencies are the same (or very similar) across all loci, although these constraints can be relaxed. Here we examine some of the properties resulting from the various infinitesimal assumptions (Table 24.1), providing a starting point for evaluating the consequences on the short-term selection response when they fail.

---

## chapter24_005 · The Infinitesimal Model and Its Extensions: Introduction / Selection Does Not Change Allele Frequencies

Recall from Chapter 16 that we can express the additive genetic variance, $ \sigma_A^2 $, as the sum of the genic variance, $ \sigma_a^2 $, and the disequilibrium contribution, $ d $, with $ \sigma_A^2 = \sigma_a^2 + d $. This partition decouples the effect of allele-frequency change (changes in $ \sigma_a^2 $) from the effect of changes from linkage disequilibrium ($ d $).

Under the infinitesimal genetics model, allele frequencies are essentially unchanged by selection, and thus $ \sigma_{a}^{2} $ is assumed to be constant over time (in an infinite population). Large changes in the mean can nonetheless occur via summation of infinitesimal allele-frequency changes over a large number of loci. To see this, consider a character determined by n completely additive biallelic loci. Suppose that all loci are interchangeable, with each having the same effects and frequencies (the exchangeable model). Each locus has two alleles, Q and q, with the genotypes QQ, Qq, and qq contributing 2a, a, and 0 (respectively) to the genotypic value, so that allele Q has effect a, and let p denote the frequency of Q. The resulting mean is then 2nap, with the change in mean due to a single generation of selection being $ \Delta\mu = 2na\Delta p $.

Ignoring any contribution from gametic-phase disequilibrium (i.e., $d=0$), the additive variance is $\sigma_A^2 = \sigma_a^2 = 2na^2p(1-p)$. For $\sigma_A^2$ to be remained bounded as the number of loci increase, $a$ must then scale as $n^{-1/2}$. Assuming the frequency of $Q$ changes by the same amount at each locus, then $\Delta p = \Delta\mu/(2na)$. Because $a$ is of order $n^{-1/2}$, $\Delta p$ is of order $1/(n \cdot n^{-1/2}) = n^{-1/2}$, and approaches zero as the number of loci becomes very large. The infinitesimal genetics model thus allows for arbitrary changes in the mean with essentially no change in the allele frequencies at underlying loci. Biologically (i.e., with a finite number of loci), the infinitesimal genetics model implies that large changes in the mean of a trait can occur with only small changes in allele frequencies if all loci each make only a small contribution to the trait variance.

What effect do small amounts of allele-frequency change have on the genic variance, $ \sigma_{a}^{2} $? Letting $ p' = p + \Delta p $ denote the frequency after selection, the change in genic variance is $$ \begin{aligned}\Delta\sigma_{a}^{2}&=2na^{2}p^{\prime}(1-p^{\prime})-2na^{2}p(1-p)\\&=2na^{2}\Delta p(1-2p-\Delta p)=a(1-2p-\Delta p)\left[2na\Delta p\right]\\&\simeq a\left(1-2p\right)\Delta\mu\end{aligned} $$ Because a is of order $ n^{-1/2} $, the change in variance due to changes in allele frequencies scales as $ (1/\sqrt{n}) $ times the change in the mean (assuming $ \Delta p $ is small). Thus, with a large number of loci, very large changes in the mean can occur without any significant change in the genic variance. The more loci of equal effect underlying a trait, the slower will be the change in $ \sigma_a^2 $, and hence the longer the selection response will be predictable (Chapter 25). In the limit of an infinite number of loci, there is no selection-induced change in the genic variance $ (\Delta \sigma_a^2 = 0) $, while arbitrary changes in the mean can occur.

---

## chapter24_006 · The Infinitesimal Model and Its Extensions: Introduction / Accounting for Dominance

While our previous focus has been exclusively on alleles with additive effects, dominance is not excluded under an infinitesimal model. The incorporation of dominance, however, requires very delicate conditions for the scaling of allelic effects, so as to bound both the dominance variance and any inbreeding depression. To see this, suppose we have n biallelic loci with no epistasis (the total genotypic value is simply the sum of the individual locus genotypic values), and let the genotypic values at locus i be 0: $ a_i + \delta_i: 2a_i $, where the frequency of the increasing allele is $ p_i $. The resulting dominance variance becomes $$ \sigma_{D}^{2}=\sum_{i=1}^{n}\left[2p_{i}(1-p_{i})\delta_{i}\right]^{2} $$

For n exchangeable loci, this simplifies to $$ \sigma_{D}^{2}=4n p^{2}(1-p)^{2}\delta^{2} $$

For $ \sigma_D^2 $ to remain bounded as $ n \to \infty $, $ \delta $ must scale as $ n^{-1/2} $, just as we found for $ a $. Thus, if both $ a $ and $ \delta $ scale as $ 1/\sqrt{n} $, the additive and dominance variances remain bounded as the number of locus goes to infinity.

Now consider the behavior of inbreeding depression, the difference between the mean trait value, $ \mu_{f} $, when population-level inbreeding is f versus that under random mating, $ \mu_{0} $ (LW Chapter 10). Again, assuming that there is no epistasis, from LW Equation 10.3, the inbreeding depression is given by $$ \mu_{f}-\mu_{0}=-2f\sum_{i=1}^{n}p_{i}(1-p_{i})\delta_{i} $$

**[命题 Proposition]**

Assuming n loci of equal effect gives $$ \mu_{f}-\mu_{0}=-2n f p(1-p)\delta $$ Because $\delta$ scales as $n^{-1/2}$ under the infinitesimal genetics assumption, the amount of inbreeding depression scales as $n \cdot n^{-1/2} = n^{1/2}$ and hence goes to infinity with increasing values of $n$. Conversely, if we scale $\delta$ as order $1/n$, we have bounded inbreeding depression, but the dominance variance is now of order $n/n^{2} = 1/n$ and hence is zero in the infinitesimal limit.

**[命题 Proposition]**

Thus, under the exchangeable infinitesimal model, one cannot have both bounded dominance variance and inbreeding depression, a point first made by Robertson and Hill (1983). Of course, a limitation of this argument is our assumption of equal effects over all loci, with all of the $ \delta $ having the same sign. If we assume that $ E[\delta] = 0 $, namely, that there is no directional dominance, then we can have bounded dominance variance but no inbreeding depression. To have both dominance variance and inbreeding depression in the infinitesimal limit requires a great deal of delicacy, in that individual allelic effects have to be scaled so that $ 0 < n E[\delta] < \infty $ as $ n \to \infty $ (there must be finite directional dominance). Related to this point, Wellmann and Bennewitz (2011) showed that the ratio of the squared inbreeding depression to the dominance variance sets a lower bound on the number of underlying loci.

---

## chapter24_007 · The Infinitesimal Model and Its Extensions: Introduction / Disequilibrium

While $ \sigma_a^2 $ remains unchanged by selection under the infinitesimal genetics model, selection-induced changes in $ d $ can significantly alter the additive genetic variance, $ \sigma_A^2 $ (Chapter 16). We can show this using the same scaling agreements we just employed. Changes in the covariances, $ C_{ij} $, of allelic effects between loci $ i $ and $ j $ (for $ i \neq j $) are roughly of order $ n^{-2} $ (Bulmer 1980; Turelli and Barton 1990). Because there are $ \sim n^2 $ terms contributing to $ d $ (Equation 16.1a), the total disequilibrium is of order one ($ n^2 \cdot n^{-2} $), and does not necessarily approach zero as the number of loci becomes infinite. The same reasoning holds for changes in the higher-order moments, which are caused by higher-order associations between groups of loci. For the $ k $th-order moment, there are $ \sim n^k $ terms in the sum, each scaling as $ n^{-k} $ to potentially give a nonzero value in the limit (Turelli and Barton 1990).

---

## chapter24_008 · The Infinitesimal Model and Its Extensions: Introduction / THEORETICAL IMPLICATIONS OF THE STANDARD INFINITESIMAL MODEL

The standard (Fisher-Bulmer) infinitesimal model assumes both the infinitesimal genetics model and that parent-offspring regressions are linear and homoscedastic. As a result, the unselected descants from a set of parents have a normal distribution of breeding values (and hence, Turelli's used of Gaussian descendants for this version of the infinitesimal.

---

## chapter24_009 · The Infinitesimal Model and Its Extensions: Introduction / What Generates a Gaussian Distribution Within a Family?

**[命题 Proposition]**

The central limit theorem from probability theory—that sums of random variables typically converge to a Gaussian distribution—implies that the distribution of breeding values is Gaussian under the infinitesimal genetics model (Bulmer 1971b; Barton et al. 2017). This Gaussian limit requires the key assumptions that loci are not too tightly linked, mating is random, and there has been no previous selection or any other force generating disequilibrium. If alleles are sufficiently correlated across loci, or if their effects are significantly different (for example, some remain at finite values while the rest become vanishingly small), then convergence to a normal is by no means assured (Lange 1978, 1997; Matthyssee et al. 1979; Dawson 1997).

In particular, as we will demonstrate, selection can generate dependencies (linkage disequilibrium [LD]) among sets of three (or more) loci, which can transform a normal distribution into a non-normal one as selection proceeds. However, under the infinitesimal genetics model, there are no changes in allele frequencies, implying that once selection stops and random mating occurs, any departures from normality (being due to LD) quickly decay. Indeed, Bulmer (1980) showed that the kth-order departure from normality (measured by cumulants, which are introduced later in the chapter) decays by $ (1/2)^{k-1} $ in each generation (assuming unlinked loci), so that following t generations of random mating, the kth-order initial departure from normality is scaled by $ (1/2)^{t(k-1)} $, which quickly approaches zero. The issue remains as to how much of a departure from normality LD generates and whether this biases infinitesimal-model-based predictions of the selection response. We return to this issue later in the chapter.

A widely used feature of the Fisher-Bulmer infinitesimal model is (for unlinked loci in noninbred parents) a constant within-family genetic variance. Specifically, the distribution of breeding values, $ A_o $, in the offspring, conditioned on the breeding values, $ A_f $ and $ A_m $, of the parents, is assumed to be normally distributed, with a mean of $ (A_f + A_m)/2 $ and a variance of $ \sigma_a^2/2 $ (half the genic variance). Thus, we have homoscedasticity with the predictor error variance, $ \sigma_a^2/2 $, being a constant, independent of the parental values. This constant Mendelian sampling variance (or segregation variance) is caused by segregation of heterozygous loci in the parents. Provided the loci are unlinked, this feature holds even when gametic-phase disequilibrium is present, as with the independent assortment of heterozygotes, the linkage phase of a parent does not influence gamete frequencies for unlinked loci (Example 16.2). More generally, the segregation variance is given by $ \sigma_a^2(1 - \bar{f})/2 $, where $ \bar{f} $ is the average amount of inbreeding in the two parents (reflecting the decrease in heterozygosity in the parents; Example 16.2). As detailed in Chapter 19, the additive relationship matrix, $ A $, fully across for relatedness-based changes in $ \sigma_a^2 $ among a collection of individuals in a BLUP analysis.

**[命题 Proposition]**

Under the infinitesimal genetics model and its assumption of no selection-induced allele-frequency change, the genic variance (corrected parental inbreeding) remains constant. However, if the infinitesimal genetic assumption is are violated, the even allels with very small effects eventually will have their frequencies changed by selection. This alters the genic variance, and hence changes the segregation variance. When major genes are present, the segregation variance depends on parental genotypes, which compromises the constant-variance (i.e., genotype-independent) assumption made under the Fisher-Bulmer infinitesimal. Indeed, recall from LW Chapter 8, that such variation of the within-family variance over families is one (albeit weak) test for the presence of a major gene.

---

## chapter24_010 · The Infinitesimal Model and Its Extensions: Introduction / Modifications of the Fisher-Bulmer Infinitesimal Model

The rest of this chapter starts to move beyond the standard (Fisher-Bulmer) infinitesimal model. First, by assuming a Gaussian distribution of allelic effects at each locus, we can partly account for changes in allele frequencies, and hence changes in $ \sigma_a^2 $, caused by a finite number of loci and/or genetic drift. This approximation breaks down over time (Chapter 25) and is best regarded as an intermediate-term predictor of response. Next, we allow for linkage. Finally, we examine the selection response when the distribution of genotypic values is no longer normal. None of these approaches fully accounts for allele-frequency change, and they are best considered as predictors for intermediate-term response. The prediction of long-term response requires explicit population-genetic models (Chapters 5, and 25–28).

Finally, a number of authors have suggested finite-locus modifications of infinitesimal-like models, largely in the context of fitting the segregation term in a mixed model when major alleles are also segregating (Cannings et al. 1978; Fernando et al. 1994; Stricker et al. 1995; Lange 1997; Du et al. 1999; Pong-Wong et al. 1999; Goddard 2001). These methods foreshadowed certain aspects of genomic selection, which assigns weights to different chromosomal segments in order to use marker data to predict breeding values (Volume 3). Diffusion approximations (Appendix 1) of finite-locus models were proposed by Miller et al. (2006).

---

## chapter24_011 · The Infinitesimal Model and Its Extensions: Introduction / GAUSSIAN CONTINUUM-OF-ALLELES MODELS

Simulation studies (e.g., Bulmer 1974a, 1976; Mueller and James 1983; Sorensen and Hill 1983; Chevalet 1988) have shown that the infinitesimal model gives a reasonably good fit to the change in variance over a few generations of selection when the number of loci is large but finite (provided all alleles have small effects). With a finite number of loci (and hence nonvanishing individual locus effects), some (potentially very small) selection-induced allele-frequency change occurs in each generation. After a sufficient number of generations, the cumulative effect of these changes becomes so large that they cannot be ignored (Chapter 25). Likewise, if the population is finite, genetic drift also changes allele frequencies (Chapter 2). Thus, when either the number of loci, n, or the effective population size, $ N_e $, is finite, we must incorporate changes in the genic variance, $ \sigma_a^2 $, into our model.

Is there an intermediate step between the short-term predictions from the breeder's equation/infinitesimal model and the unpredictable long-term behavior when significant allele-frequency changes have occurred? In many cases, an affirmative answer is provided by approximations using continuum-of-alleles models (COA). Our focus here is on the Gaussian COA model, with other COA models (such as the house-of-cards, rare alleles, or house-of-Gauss models) examined more fully in Chapter 28. For brevity, for the rest of this chapter, continuum-of-alleles refers strictly to the Gaussian COA. This model allows us to partly account for modest changes in allele frequencies due to selection (given a finite number of loci) and genetic drift (due to finite population size). The nice feature about these intermediate-term approximations for response is that they are based entirely on macroscopic parameters, for which there is some hope of estimation.

---

## chapter24_012 · The Infinitesimal Model and Its Extensions: Introduction / Infinite-alleles and Continuum-of-alleles Models

The historical roots of the continuum-of-alleles model trace back to the classic paper of Kimura and Crow (1964), which introduced the infinite-alleles model (Chapter 2). Before its publication, most population-genetic models typically assumed two (or at most a few) alleles per locus. Kimura and Crow, in the first serious treatment of molecular evolution, noted that with an allele being represented by a long DNA sequence, each new mutation likely creates a new sequence, implying an effectively infinite number of possible alleles. Kimura and Crow's original paper simply dealt with how much variation (measured in terms of heterozygosity) could be maintained by the balance between drift and mutation (Chapter 2), and it was not concerned with allelic effects. Crow and Kimura (1964) and Kimura (1965a) quickly applied this notion of a very large number of alleles per locus to quantitative genetics by considering the distribution of allelic effects at each locus. These Gaussian continuum-of-alleles models were further developed by Latter (1970), Lande (1975, 1977a), and Felsenstein (1977) to consider the amount of variation maintained by mutation-selection balance (Chapter 28). Kimura's (1965a) original analysis revealed that if new mutations have small effects relative to the existing variation at the locus, the distribution of effects (in an infinite population) converges to a normal.

**[命题 Proposition]**

Hence, Gaussian COA models make the assumption that the distribution of additive genetic values at each locus is Gaussian (and jointly multivariate normal over a vector of loci). This assumption is strictly correct only if the number of alleles at each locus is infinite, which further implies that there is an infinite population size. This assumption of a Gaussian distribution of effects at each locus is much more restrictive than the assumption that the distribution of the total genotypic values is normal. The latter follows from the central limit theorem, as the sum of non-normal distributions of single-locus effects converges to a Gaussian, provided that the loci are not overly correlated.

While Gaussian COA models are a very restrictive subset of all possible models that can lead (at their limit) to the infinitesimal, their advantage is that we can assume a finite number of loci, and hence partly accommodate allele-frequency change. As discussed in Chapter 28, Gaussian COA models assume that mutational input in any generation is much smaller than the standing additive variation at a locus, or equivalently, that mutation is much stronger. than selection (which allows significant amounts of polymorphism to accumulate at a given locus; Chapter 7). One scenario where biology suggests that the Gaussian model might be approached is in asexual species, where the entire genome is essentially transmitted as a single gene, and hence can have a very large number of possible alleles.

Gaussian COA models attempt to bridge short-term predictors (such as the breeder's and Bulmer equations) that rely on estimable qualities ($ \sigma_A^2, h^2 $) with the long-term predictors of response (Chapters 25 and 26) based on population-genetic models containing quantities that are essentially unestimable. COA models attempt, using estimable quantities, to capture the change in variance from changes in both allele frequencies (and hence changes in $ \sigma_a^2 $) and $ \sigma_A^2 $ from selection-generated disequilibrium (changes in $ d $). Gaussian approximations of the Bulmer equation for the change in variance (Equation 16.7b) under a finite number of loci ($ n $) were introduced by Lande (1975) and Felsenstein (1977, 1979), and Keightley and Hill (1987) further allowed for a finite effective population size ($ N_e $). We consider the effects of drift first. The behavior of these models with mutation is discussed extensively in Chapter 28.

---

## chapter24_013 · The Infinitesimal Model and Its Extensions: Introduction / Drift

**[推导 Derivation]**

Assuming that the phenotypic variance after selection has the form $ \sigma_{z}^{2} = (1 - \kappa) \sigma_{z}^{2} $ (Equation 16.10a), Keightley and Hill (1987) obtained equations for the change in the additive genetic variance, $ \sigma_{a}^{2} $, and the gametic-phase disequilibrium, d, when the population size is finite:

> **Formula (24.1a)** · `24.1a` · source: `chapter24_block_050` · Drift
>
> $$ \Delta\sigma_{a}^{2}(t)=-\frac{\sigma_{a}^{2}(t)}{2N_{e}} $$


> **Formula (24.1b)** · `24.1b` · source: `chapter24_block_050` · Drift
>
> $$ \Delta d(t)=-\frac{1}{2}\left[\left(1+\frac{1}{N_{e}}\right)d(t)+\left(1-\frac{1}{N_{e}}\right)\kappa h^{2}(t)\sigma_{A}^{2}(t)\right] $$


**[推导 Derivation]**

Note that these expressions were shown previously (Equations 16.9a and 16.9b). As before, $ \sigma_A^2(t) = \sigma_a^2(t) + d(t) $ and $ h^2(t) = \sigma_A^2(t)/\sigma_z^2(t) $, with $ \sigma_z^2(t) = \sigma_A^2(t) + \sigma_E^2 $, where $ \sigma_E^2 = \sigma_z^2(0) - \sigma_A^2(0) $. As in Chapter 16, the selection response in the mean is given by the breeder's equation, $ R(t) = h^2(t)S(t) $. If the population size is at least modest, the correction for drift effects on $ d(t) $ is small, as $ 1 \pm 1/N_e \simeq 1 $, and Equation 24.1b essentially becomes the Bulmer equation. Drift effects on the genic variance, however, are quite substantial, as they remove all of the initial genic variance ($ \sigma_a^2 $, and hence $ \sigma_A^2 $) after sufficient time ($ t \simeq 2N_e $ generations, ignoring new mutation). Solving Equation 24.1a yields

> **Formula (24.1c)** · `24.1c` · source: `chapter24_block_051` · Drift
>
> $$ \sigma_{a}^{2}(t)=\left(1-\frac{1}{2N_{e}}\right)^{t}\sigma_{a}^{2}(0)\simeq\sigma_{a}^{2}(0)\exp\left(-\frac{t}{2N_{e}}\right) $$


**[命题 Proposition]**

This is simply the standard loss of genetic variation under drift (Chapter 2). When dominance or epistasis is present, the additive variance can actually increase (for a while) under inbreeding (Chapter 11), so the assumption of only additive gene action is critical. In the absence of mutation, the response runs out of standing variation in finite populations, as $ \sigma_{a}^{2} $ is driven to zero by drift.

**[示例 Example]**

> **Example 24.2** · ref: `24.2` · source: `chapter24_013.json` · blocks 3–3
>
> Example 24.2. To see the effects of drift on the infinitesimal model, reconsider Example 16.2 under finite population size. This example assumed that $ h^2(0) = 0.5 $ and $ \sigma_A^2(0) = 100 $, implying that $ \sigma_A^2(0) = \sigma_A^2 = \sigma_E^2 = 50.00 $ (assuming $ d(0) = 0 $). Truncation selection was applied, with the upper 20% saved (yielding $ p = 0.2 $, $ \kappa = 0.781 $, and $ \bar{\tau} = 1.40 $). Under the infinitesimal model, the genetic variance, $ \sigma_A^2 $, remains unchanged at its original value of 50, while the additive genetic variance decreases to its equilibrium value of $ \tilde{\sigma}_A^2 = 37.46 $, and hence $ \tilde{h}^2 = 37.46 / (37.46 + 50.00) = 0.43 $, yielding an asymptotic value of response of $ \tilde{H} = \tilde{h}^2 \tilde{\sigma}_A^2 = 5.6 $ per generation.
> 
> Now consider a finite population size with $ N_e = 10 $, which is close to the effective population sizes of many artificial selection experiments (Chapter 26). Iteration of Equation 24.1 yields the dynamics depicted in Figure 24.1. Drift erodes away the genic variance, decreasing the heritability (and hence response) over time. The population (in the absence of mutation) will eventually run out of variation, reaching a selection limit (Chapters 25 and 26). Note the unusual behavior of the disequilibrium, $ d $, which (following an initial drop) increases toward zero over time. This occurs because the genic variance is declining, which limits the amount of disequilibrium that is possible (Equation 24.4).


---

## chapter24_014 · The Infinitesimal Model and Its Extensions: Introduction / Drift and a Finite Number of Loci

**[推导 Derivation]**

Under the infinitesimal model, there is no selection-induced change in allele frequencies, leaving the genic variance unchanged by selection. However, when the population size is finite, alleles are subjected to drift, changing allelic frequencies and eventually reducing the genic variance to zero. A second route for allele-frequency change arises when the number of loci, n, is finite. In this case, there are nonzero selective effects on each locus and allele frequencies change (although potentially very slowly; recall from Equation 5.21 that s scales as $ a/\sigma_{z} $). Assuming that the potential distribution of genotypic values at each locus is Gaussian, continuum-of-alleles (COA) models can account for both finite $ N_{e} $ and n. most general result is due to Chevalet (1988, 1994; also see Verrier et al. 1991), where for loci of equal effect and assuming selection of the form such that the phenotypic variance after selection is $ \sigma_{z*}^2 = (1 - \kappa) \sigma_z^2 $, we have

> **Formula (24.2a)** · `24.2a` · source: `chapter24_block_055` · Drift and a Finite Number of Loci
>
> $$ \Delta\sigma_{a}^{2}(t)=-\left[\frac{\sigma_{a}^{2}(t)}{2N_{e}}+\left(1-\frac{1}{N_{e}}\right)\frac{\kappa h^{2}(t)\sigma_{A}^{2}(t)}{2n}\right] $$


> **Formula (24.2b)** · `24.2b` · source: `chapter24_block_055` · Drift and a Finite Number of Loci
>
> $$ \Delta d(t)=-\frac{1}{2}\left[\left(1+\frac{1}{N_{e}}\right)d(t)+\left(1-\frac{1}{n}\right)\left(1-\frac{1}{N_{e}}\right)\kappa h^{2}(t)\sigma_{A}^{2}(t)\right] $$


**[命题 Proposition]**

Provided we are willing to accept the assumption that the distribution of effects at each locus remains normally distributed (a point addressed later), these expressions are iterated to obtain the current values of $ \sigma_a^2 $ and $ d $. Starting from an unselected base population (and hence assuming that $ d(0) = 0 $), the only genetic parameters required to iterate Equations 24.2a and 24.2b are $ \sigma_A^2(0) $, $ h^2 $, $ n $, and $ N_e $, all of which are potentially estimable.

**[推导 Derivation]**

Equations 24.2a and 24.2b highlight the changes that occur when we assume a finite number of loci $ (n < \infty) $ and/or finite population size $ (N_e < \infty) $. When both are infinite, we recover the Bulmer equation (16.7b),

> **Formula (24.2c)** · `24.2c` · source: `chapter24_block_057` · Drift and a Finite Number of Loci
>
> $$ \Delta\sigma_{a}^{2}(t)=0\qquad and\qquad\Delta d(t)=-\frac{d(t)+\kappa h^{2}(t)\sigma_{A}^{2}(t)}{2} $$


Notice that the additive genic variance, $ \sigma_a^2 $, remains unchanged (as allele frequencies remain unchanged), while disequilibrium (nonzero $ d $) is generated by selection but decays to zero once selection stops (i.e., when $ \kappa = 0 $).

**[推导 Derivation]**

While finite $n$ or $N_e$ both result in modifications of the simple Bulmer equation for the dynamics of $d$, Equation 24.2b shows that these corrections are generally small. However, this is not the case for changes in $\sigma_a^2$. With either finite population size or a finite number of loci, the genic variance decreases in each generation, eventually decaying to zero (in the absence of mutation). The relative importance of drift in comparison to a finite number of loci for changes in $\sigma_a^2$ can be compared using Equation 24.2a, which yields

> **Formula (24.2d)** · `24.2d` · source: `chapter24_block_059` · Drift and a Finite Number of Loci
>
> $$ \frac{\Delta\sigma_{a}^{2}}{2}=\left\{\begin{aligned}&-\frac{\sigma_{a}^{2}}{N_{e}}&\text{for}n=\infty\\ &-\frac{\kappa h^{2}\sigma_{A}^{2}}{n}&\text{for}N_{e}=\infty\end{aligned}\right. $$


Because either directional or stabilizing selection generates negative values of $d$, we have that $0 < \kappa < 1$ (and hence $\kappa h^2 < 1$), implying that $\sigma_A^2 = \sigma_a^2 + d < \sigma_a^2$, so that $\sigma_a^2 > \sigma_A^2 > \kappa h^2 \sigma_A^2$. Using this inequality in Equation 24.2d shows that for comparable values of $N_e$ and $n$, drift results in a greater per-generation reduction in $\sigma_a^2$ (also see Figure 24.2).

---

## chapter24_015 · The Infinitesimal Model and Its Extensions: Introduction / The Effective Number of Loci, $ n_{e} $

**[推导 Derivation]**

Chevalet (1994) allowed loci to differ in the amount of genetic variance they contribute, replacing the acutal number of loci, n, in Equations 24.2a and 24.2b by the effective number of loci, $ n_{e} $, defined as

> **Formula (24.3)** · `24.3` · source: `chapter24_block_060` · The Effective Number of Loci, $ n_{e} $
>
> $$ n_{e}=\frac{n}{1+c_{v}^{2}} $$


where $ c_{v} $ is the coefficient of variation in the genic variance contributed by each locus, $ \sigma\left(\sigma_{ai}^{2}\right)/E[\sigma_{ai}^{2}], $ with $ \sigma_{ai}^{2} $ being the genic variance contributed by locus $ i $. (Note that Equation 24.3 is closely related to the Castle-Wright estimator for the effective number of segregating genes in a line-cross $ F_{2} $ population; LW Chapter 9.) If all loci contribute the same variance, then $ c_{v}=0 $ and $ n_{e}=n $, while $ n_{e}\ll n $ when $ c_{v}\gg1 $.

Note that $ n_e $ changes over time, as allele-frequency changes alter the genic variance contributed by any particular locus. Indeed, loci with the largest genetic variance should show the largest initial response to selection, and also the fastest depletion of locus-specific variance (Chapter 25). In such cases, one can move from a situation where the effective number of loci is quite small (a few loci with large effects, and hence a high value of $ c_v $) to a situation where $ n_e $ can be quite large (with the remaining loci all having roughly equal effects, so that $ c_v $ is small). Hence, $ n_e $ can increase over time, but we also correspondingly expect the total genic variance, $ \sigma_a^2 $, for the remaining loci to decrease (Figure 24.3).

**[示例 Example]**

> **Example 24.3** · ref: `24.3` · source: `chapter24_015.json` · blocks 2–2
>
> Example 24.3. Suppose the number, $n$, of loci underlying a trait is finite. Assume the same model as in Example 24.2, but now let $n = 10$ and $N_e = \infty$ (i.e., reversing the values of $n$ and $N_e$). We will contrast the behavior of this system with that in Example 24.2 ($N_e = 10$, $n = \infty$), and with the standard infinitesimal model ($N_e = n = \infty$). As Figure 24.2 shows, both $h^2$ and the selection response decrease over time with a finite number of loci, and eventually a selection limit is reached when all of the initial variation is lost. However, these decreases are not nearly as dramatic as those in Example 24.2 (see Figure 24.1). Figure 24.2 shows that the cumulative response for a model with $N_e = n = 10$ is only very slightly less than under drift alone ($N_e = 10$).


**[示例 Example]**

> **Example 24.4** · ref: `24.4` · source: `chapter24_015.json` · blocks 3–3
>
> Example 24.4. As an illustration of how the effective number of loci, $ n_e $, can change over the course of selection, consider an additive model with both major and minor loci underlying a trait under selection. There are five major loci, each with frequency $ p = 0.25 $ and effect size $ a = 5.16 $, and 125 minor loci, each with $ p = 0.5 $ and $ a = 0.89 $. The resulting initial genic variance is $ \sigma_a^2 = 100 $ (half of which is from the major genes and half from the minor loci), and we assume an initial heritability of $ h^2 = 0.5 $ (by setting $ \sigma_E^2 = 100 $). Finally, assume truncation selection with the uppermost 20% saved (further details for this model are given in Example 25.2). We ignore any effects of disequilibrium, focusing instead on how the genic variance (the open circles in Figure 24.3) and the effective number of loci, $ n_e $ (the filled circles) change over time due to allele-frequency changes. As shown in Figure 24.3, while there are 130 loci in this system, initially the effective number is around 20, due to the large coefficient of variation in the locus-specific genic variances. As selection proceeds, the genic variance initially increases as the major alleles increase their frequencies toward 0.5 (where they have maximal additive variance when dominance is absent; LW Figure 4.8). Such an increase in variance is not predicted by Gaussian COA models (which assume a continuous distribution of allelic effects at each locus, rather than simply two alleles). Notice that the effective number of loci decreases slightly during this increase in variance, as the $ c_{v} $ increases. As alleles at these major loci become fixed, the total genic variance decreases while the effective number of loci increases (to approximately 125, the number of minor loci), reflecting a decrease in the coefficient of variation (as the remaining loci all have very similar variances).


As Example 24.4 illustrates, a selection response can result in an increase in the additive variance at some point during selection (typically fairly early), as favored alleles at low frequencies increase to intermediate frequencies. Hospital and Chevalet (1996) observed a similar phenomenon in their simulation of linkage, namely, that finite-locus models can also show an increase in additive variation. The distinction is that this increase may come, not rather quickly (as was the case for rare alleles), but only many generations after selection is initiated, reflecting recombination finally generating favorable gametes, which then increase in frequency. They also found that linked systems are vulnerable to lower selection responses due to hitchhiking fixing less favorable alleles, an issue examined further in Chapter 26.

---

## chapter24_016 · The Infinitesimal Model and Its Extensions: Introduction / Dynamics: $ \sigma_{a}^{2} $ and d Change on Different Time Scales

**[推导 Derivation]**

Chevalet (1988, 1994) and Gavrilets and Hastings (1994a, 1995) noted that the dynamics of the genic variance and the disequilibrium operate on rather different time scales. The change in d is rather rapid, quickly approaching a quasi-equilibrium value (Kimura 1965b),

> **Formula (24.4)** · `24.4` · source: `chapter24_block_063` · Dynamics: $ \sigma_{a}^{2} $ and d Change on Different Time Scales
>
> $$ d=-\kappa\left(1-\frac{1}{n_{e}}\right)h^{2}\sigma_{A}^{2} $$


Note from Equation 24.2b that this is simply the amount of new disequilibrium generated by selection (taking $ N_e = \infty $). This is not strictly an equilibrium value, as changes in $ \sigma_a^2 $, which occur over much longer time scales, also change $ \sigma_A^2 $, albeit much more slowly. As $ n_e \to \infty $, we recover Equation 16.7c (as $ \delta(\sigma_z^2) = -\kappa\sigma_z^2 $), the equilibrium $ d $ value found by Bulmer (which is a true equilibrium, as $ \sigma_a^2 $ does not change under the infinitesimal model). Thus, for a given value of $ \sigma_a^2 $, there is a quick approach to the equilibrium value of $ d $, which we can very closely approximate by treating the value of $ \sigma_a^2 $ as fixed and applying Equations 16.13a–16.13c.

**[推导 Derivation]**

One direct application of Equation 24.4 involves the distribution of the additive genetic variance within the population. This can be decomposed into that held between families (the difference in family means) and that generated by segregation within each family (Chapter 16). When no disequilibrium is present (d = 0), under random mating, each component is $ \sigma_A^2 / 2 = \sigma_a^2 / 2 $. However, with selection, the genetic variance among full-sib families is simply half the additive variance following selection, $ \sigma_A^2 + d $, which (Equation 24.4) yields

> **Formula (24.5a)** · `24.5a` · source: `chapter24_block_065` · Dynamics: $ \sigma_{a}^{2} $ and d Change on Different Time Scales
>
> $$ \sigma^{2}(FS)=\frac{\sigma_{A}^{2}}{2}\left[1-\left(1-\frac{1}{n_{e}}\right)\kappa h^{2}\right] $$


while the within-family (additive genetic) variance is

> **Formula (24.5b)** · `24.5b` · source: `chapter24_block_065` · Dynamics: $ \sigma_{a}^{2} $ and d Change on Different Time Scales
>
> $$ \sigma_{A}^{2}(\mathrm{within-family})=\frac{\sigma_{a}^{2}}{2}=\frac{\sigma_{A}^{2}}{2}\left[1+\left(1-\frac{1}{n_{e}}\right)\kappa h^{2}\right] $$


Equation 24.5b follows by noting that $ \sigma_A^2 = \sigma_a^2 + d $, and substituting Equation 24.4 for the value of $ d $.

Gavrilets and Hastings (1994a, 1995) noted that this difference in time scales for changes in $d$ versus $\sigma_a^2$ has important implications for the interpretation of experiments using artificial stabilizing selection, where response is measured by a decrease in the phenotypic variance. Simulations, as well as their analysis of two- and $n$-locus models, showed that while a rapid approach to the quasi-equilibrium $d$ value (Equation 24.4) occurs, the rate of change of allele frequencies can be very slow—on the order of 100 (or more) generations even with strong selection under a two-locus model. As mentioned in Chapter 16, we expect an immediate decrease in the phenotypic variance due to selection generating negative disequilibrium, which reduces $\sigma_A^2$. Selection will also operate to eventually reduce the genic variance, $\sigma_a^2$, resulting in a further decrease in $\sigma_A^2$ over that predicted from disequilibrium alone. Gavrilets and Hastings suggested that, given the short time scales of most experiments, if decreases in $\sigma_a^2$ occur, these are more likely due to drift than selection. A related point is that an observed reduction in the phenotypic variance is usually assumed to arise solely from a reduction in $\sigma_A^2$. However, as mentioned in Chapter 17, if there is heritable variation in $\sigma_E^2$, the environmental variance is also reduced by stabilizing selection. Thus, selection-driven allele-frequency changes might be involved in an observed reduction in the phenotypic variance, but through changes in $\sigma_E^2$, rather than through $\sigma_A^2$ for the trait.

---

## chapter24_017 · The Infinitesimal Model and Its Extensions: Introduction / How Robust Is the Gaussian Continuum-of-alleles Model?

As will be fully discussed in Chapter 28, a key determinant of which continuum-of-alleles model is appropriate is the relative strength of selection and mutation at a locus (Table 28.2). The Gaussian model is appropriate when the per-locus mutation rate is far greater than the average strength of selection on a locus (in a large population). In such settings, a given locus is likely to be segregating a large number of alleles, and any new allele adds little to the standing variation. Conversely, other approximations (such as the rare-allele or the house-of-cards models) are more appropriate when selection is much stronger than mutation (i.e., $ s \gg \mu $), in which case any given locus will have one dominant allele and a few very rare alleles. Our discussion here assumes that mutation is much stronger than selection.

**[命题 Proposition]**

Under this assumption, if the trait is determined by a modest to large number of loci, all of roughly equal effect and with alleles at intermediate frequencies, then Gaussian COA models can perform reasonably well, at least over intermediate time scales (Chevalet 1988, 1994). They generally tend to overestimate the cumulative response as generations increase, so that while the decrease in $ \sigma_{a}^{2} $ from selection is partially captured (an improvement over the infinitesimal model), after sufficient time, the COA approximation breaks down.

**[命题 Proposition]**

What are the possible causes for the breakdown of the approximation? A subtle feature of the Gaussian assumption for each locus is the key. The COA approximation generally works well at the start of selection, provided the distributions of genotypic values at each locus are initially close to normal. However, as allele-frequency changes drive the individual locus distributions further from normality, the COA approximation breaks down, as loci with alleles at extreme frequencies (near zero or one) can show large departures from normality. A recurrent theme of this chapter is a focus on the skewness and kurtosis of distributions, as these provide very convenient measures of the departure from a normal. Skewness measures departures from symmetry, while kurtosis measures whether the tails of the distribution decline more or less rapidly than under a normal. Both of these statistics (with kurtosis appropriately defined) are zero under a normal, and hence they provide a simple quantification of the departure of a distribution from normality (LW Chapter 2).

**[推导 Derivation]**

What can we say about the skewness and kurtosis for an n-locus biallelic model? Assume n exchangeable loci, each with frequency p of the favorable allele. Zeng (1987) showed that the scaled (to unit variance) coefficients of skewness, $ k_{3} $, and kurtosis, $ k_{4} $, for the resulting distribution of genotypic values are

> **Formula (24.6)** · `24.6` · source: `chapter24_block_071` · How Robust Is the Gaussian Continuum-of-alleles Model?
>
> $$ k_{3}=\frac{2p-1}{\sqrt{2np(1-p)}}\qquad and\qquad k_{4}=\frac{1-2p(1-p)}{2np(1-p)} $$


Note that skewness is zero and kurtosis is minimized at intermediate allele frequencies $ (p = 1/2) $. As allele frequencies become more extreme, so do the skew and kurtosis.

Rare alleles of large effect are especially problematic. Not only do these generate skewness and kurtosis, but as their frequencies increase, so does the genic variance (Figure 24.3). Lande (1983) and Zhang and Hill (2005a) both noted that natural selection tends to generate a correlation between allelic effect size and frequency, so that alleles of large effect may tend to be rare in natural populations due to pleiotropic deleterious fitness effects. If these rare alleles are captured when a population is sampled to form a laboratory stock for artificial selection, an increase in additive variance is expected during selection. However, if the founding population is under strong drift for a few generations (as with a founding bottleneck), rare alleles can be lost and the COA approximation may be a good predictor of short-term response. This theme of initially rare favorable alleles, and hence an early accelerated response to selection, will be revisited in Chapter 28, as it is central to certain predictions about response in a population under mutation-selection balance.

---

## chapter24_018 · The Infinitesimal Model and Its Extensions: Introduction / THE BULMER EFFECT UNDER LINKAGE

Both the standard infinitesimal and Gaussian COA models assume unlinked loci. When loci are linked, the contribution from gametic-phase disequilibrium, d, decays by less than half in each generation. This allows higher values to accrue, yielding a larger value of $ |d| $ at equilibrium. We examine the impact of linkage under two different settings. First, we consider the Gaussian COA approximation (requiring multivariate normality of the locus-specific distributions of effects), and second, allowing for departures from normality serves as an entry point for our final section on treating non-Gaussian distributions of genetic values.

---

## chapter24_019 · The Infinitesimal Model and Its Extensions: Introduction / An Approximate Treatment

**[推导 Derivation]**

An approximate solution for the dynamics of $ \sigma_{A}^{2} $ incorporating linkage was offered by Bulmer (1974a, 1980), whose approach we follow (a more general solution by Turelli and Barton will be considered shortly). Recall from Chapter 16 that $ C_{ij} $ denotes the covariance between allelic effects at loci $i$ and $j$, meaning that $C_{ii}$ is the genic variance for locus $i$, while $C_{ij}$ for $i \neq j$ measures the contribution from disequilibrium between $i$ and $j$. Thus, from Equation 16.1b, $d(t) = 4 \sum_{i < j} C_{ij}(t)$, with the changes in the pairwise covariances describing the change in $d$. If $r_{ij}$ is the recombination fraction between two loci (we use $r_{ij}$ in place of our more standard $c_{ij}$ used in previous chapters to avoid confusion with $C_{ij}$), then $(1 - r_{ij}) C_{ij}(t)$ is the contribution passed on to $C_{ij}(t + 1)$. Recalling Equation 16.6, the change in $d(t)$ due to selection when genotypic and phenotypic values are normally distributed is

> **Formula (24.7a)** · `24.7a` · source: `chapter24_block_075` · An Approximate Treatment
>
> $$ \frac{h^{4}(t)}{2}\delta(\sigma_{z(t)}^{2})=4\sum_{i=1}^{n}\sum_{i<j}^{n}\delta C_{ij}(t) $$


where we use both $ \delta X $ and $ \delta(X) $ to denote the within-generation change in the variable X. In order to approximate $ \delta C_{ij} $ (the change in disequilibrium generated by selection), Bulmer assumed that these changes are the same for each pair of loci (an exchangeable model). For n loci, there are $ n(n-1)/2 $ unique pairs, giving the contribution from each pair as

> **Formula (24.7b)** · `24.7b` · source: `chapter24_block_075` · An Approximate Treatment
>
> $$ 4\delta C_{ij}(t)\simeq\frac{h^{4}(t)\;\delta(\sigma_{z(t)}^{2})}{n(n-1)} $$


Because the new disequilibrium equals the fraction of the current disequilibrium after recombination plus the fresh disequilibrium generated by selection

> **Formula (24.7c)** · `24.7c` · source: `chapter24_block_075` · An Approximate Treatment
>
> $$ C_{ij}(t+1)=\left(1-r_{ij}\right)C_{ij}(t)+\delta C_{ij}(t) $$


**[推导 Derivation]**

This equation is approximate, as the covariance between gametes, $ C_{i,j} $, is ignored here. Equation 24.11c provides a more exact treatment (as does Example 28.7). Ignoring $ C_{i,j} $, Equation 24.7c implies that, at equilibrium, $ r_{ij} \tilde{C}_{ij} = \tilde{\delta} C_{ij} $, where the tildes denote equilibrium values. Using Equation 24.7b yields an equilibrium covariance of

> **Formula (24.7d)** · `24.7d` · source: `chapter24_block_076` · An Approximate Treatment
>
> $$ \tilde{C}_{ij}=\frac{\tilde{h}^{4}\tilde{\delta}(\sigma_{z}^{2})}{4n\left(n-1\right)}\frac{1}{r_{ij}} $$


**[推导 Derivation]**

Thus,

> **Formula (24.8a)** · `24.8a` · source: `chapter24_block_077` · An Approximate Treatment
>
> $$ \widetilde{d}=4\sum_{i=1}^{n}\sum_{i<j}^{n}\widetilde{C}_{ij}(t)=4\frac{\widetilde{h}^{4}\widetilde{\delta}(\sigma_{z}^{2})}{4n\left(n-1\right)}\sum_{i=1}^{n}\sum_{i<j}^{n}\frac{1}{r_{ij}}=\frac{1}{2}\widetilde{h}^{4}\widetilde{\delta}(\sigma_{z}^{2})\frac{1}{r_{H}} $$


where $ r_{H} $ is the harmonic mean of all pairwise recombination distances between loci,

> **Formula (24.8b)** · `24.8b` · source: `chapter24_block_077` · An Approximate Treatment
>
> $$ r_{H}=\left(\frac{1}{n\left(n-1\right)/2}\sum_{i=1}^{n}\sum_{i<j}^{n}\frac{1}{r_{ij}}\right)^{-1} $$


The value of $ r_{H} $ varies with both the number of loci and chromosomes, decreasing as the number of loci per chromosome increases. Using simulations of randomly distributed loci, Bulmer (1974a) found that if the haploid chromosome number exceeds 10, $ r_{H} $ will likely be no smaller than 0.4, while in Drosophila melanogaster, with its three main chromosomes and lack of recombination in males, $ r_{H} $ is around 0.1 if there are many loci. However, even if only a few loci occur as tightly linked pairs, $ r_{H} $ can be considerably below 0.5, as the harmonic mean disproportionately weights very small values.

**[推导 Derivation]**

Assuming again that the phenotypic variance after selection can be written as $ \sigma_z^2 = (1 - \kappa) \sigma_z^2 $, Equation 16.13a can be modified for linkage to give the equilibrium additive genetic variance as $ \widetilde{\sigma}_A^2 = \sigma_z^2 \gamma $. Letting $ h^2 $ and $ \sigma_z^2 $ denote values in the absence of LD (i.e., $ d = 0 $, implying $ h^2 = \sigma_a^2 / \sigma_z^2 $), then

> **Formula (24.9)** · `24.9` · source: `chapter24_block_079` · An Approximate Treatment
>
> $$ \gamma=r_{H}\left(\frac{2h^{2}-1+\sqrt{1+2h^{2}(1-h^{2})\kappa/r_{H}}}{2r_{H}+\kappa}\right) $$


and the equilibrium heritability, $ \tilde{h}^2 = \tilde{\sigma}_A^2 / \tilde{\sigma}_z^2 = (\sigma_a^2 + \tilde{d}) / (\sigma_z^2 + \tilde{d}) $, is given by Equation 16.13c using the value of $ \gamma $ for Equation 24.9. Note that we can express this result in terms of $ \tilde{d} $ by noting that $ \tilde{\sigma}_A^2 - \sigma_a^2 = \tilde{\sigma}_A^2 - h^2 \sigma_z^2 = \tilde{d} $, or that $ \tilde{d} = (\gamma - h^2) \sigma_z^2 $. The general conclusion from Equation 24.9 is that, for a fixed value of $ \kappa $, increasing the amount of linkage (e.g., decreasing $ r_H $) increases the absolute value of $ \tilde{d} $ (Bulmer 1974a, 1976, 1980).

Finally, turning briefly to disruptive selection (where $ \kappa < 0 $, and hence $ d > 0 $), the standard infinitesimal model predicts that $ \widetilde{d} $ should increase as linkage tightens. As we saw in Chapter 16, with sufficiently strong disruptive selection, namely $ \kappa < -r_H / [2h^2(1 - h^2)] $, there is no real positive root for $ \gamma $ in Equation 24.9, and the standard infinitesimal model predicts that $ d $, and hence $ \sigma_A^2 $, increases without limit (Bulmer 1976). With a finite number of loci, this condition implies that selection creates almost complete disequilibrium, so that only a few of the possible gamete types are actually present, namely, most gametes are either $ abcd \cdots $ or $ ABCD \cdots $ (Chapter 16).

While the prediction that $d$ increases under disruptive selection as linkage tightens holds for an infinite population, simulations by Sorensen and Hill (1983) found exactly the opposite with small values of $N_e$ with $|\widetilde{d}|$ actually decreasing as linkage tightens. They reasoned that this discrepancy arises due to the interaction between a finite number of loci and the finite population sizes used in their simulations. To see this, consider complete linkage. In a finite population, the most extreme gamete observed is affected by sampling, as selection can generate no gamete more extreme than those found in the initial sample (in the absence of recombination). If the number of loci is small, the probability of sampling the most extreme possible gamete is high, but this probability decreases as the number of loci increases. Countering this, as recombination (measured by $r_H$) or the population size increases, the probability increases that recombination can regenerate more extreme gametes before the relevant loci are fixed by drift or selection. When population size becomes large enough that drift effects are no longer important, $\widetilde{d}$ increases with increasing linkage. Interactions of this sort between drift, selection, and recombination are considered in detail in Chapter 26.

**[示例 Example]**

> **Example 24.5** · ref: `24.5` · source: `chapter24_019.json` · blocks 7–7
>
> Example 24.5. As an example of the consequences of increased linkage, reconsider our analysis of the response under directional selection used in Examples 24.2 and 24.3. Here we assume an infinite number of loci and infinite population size. Substituting into Equation 24.9 to obtain $ \gamma $ and recalling Equations 16.13a–16.13c yields the following metrics of response for different $ r_{H} $ values:
> 
> > **Inline Table 2** · `inline_2` · page 18 · source: `chapter24_019`
> > Inline Table 2
> >
> > $ r_{H} $ | $ \gamma $ | $ \widetilde{d} $ | $ \widetilde{\sigma}_{A}^{2} $ | $ \widetilde{h}^{2} $ | $ \widetilde{R} $
> > --- | --- | --- | --- | --- | ---
> > 0.5 | 0.37 | -12.60 | 37.40 | 0.43 | 5.60
> > 0.4 | 0.35 | -14.50 | 35.50 | 0.42 | 5.37
> > 0.3 | 0.33 | -17.11 | 32.89 | 0.40 | 5.06
> > 0.2 | 0.29 | -20.97 | 29.03 | 0.37 | 4.57
> > 0.1 | 0.23 | -27.49 | 22.51 | 0.31 | 3.70
> 
> 
> A value of $ r_{H} = 0.5 $ corresponds to free recombination, while $ r_{H} = 0.1 $ might be expected in Drosophila melanogaster. As expected, decreasing the average amount of recombination between loci increases the effect of linkage disequilibrium, generating more extreme d values, and hence (for directional and stabilizing selection) smaller additive variances, heritabilities, and selection responses. With strong linkage ( $ r_{H} = 0.1 $), the response is only 66% of that for unlinked loci (3.70 versus 5.60).


---

## chapter24_020 · The Infinitesimal Model and Its Extensions: Introduction / A More Careful Treatment

**[命题 Proposition]**

A more rigorous treatment of how selection changes the within-gamete covariances, Cij, requires consideration of the (pairwise) between-gamete covariance, $ C_{i,j} $, as well as higher-order covariance terms that measure the amount of gametic-phase disequilibrium between groups of more than two loci. Here, we introduce some of the notation needed for non-normal distributions of genotypic and phenotypic values, returning to the consequences of relaxing the normality assumption in the next section.

**[推导 Derivation]**

We start by defining the between-gamete covariance,

> **Formula (24.10)** · `24.10` · source: `chapter24_block_084` · A More Careful Treatment
>
> $$ C_{i,j}=\sigma\left(a_{fa}^{(i)},a_{mo}^{(j)}\right) $$


which is the covariance between the effect of an allele at the ith locus in the paternal (fa) gamete and an allele at the jth locus in the maternal (mo) gamete. Under random mating, gametes unite at random, and hence $ C_{i,j} = 0 $ at the start of each generation. However, selection generates correlations between gametes in much the same way that it generates correlations among loci within gametes. For example, consider a particular chromosome containing multiple loci influencing a character under stabilizing selection. Initially, there is no correlation between the genetic values of the two copies of this chromosome in an offspring from randomly mated parents. Stabilizing selection changes this initial distribution, favoring adults with intermediate genotypic values. Thus, surviving adults with a large genetic value on one chromosome are expected to have a small value on the other and vice versa, generating negative $ C_{i,j} $ (Figure 16.2; Example 28.7). Likewise, positive assortative mating generates positive $ C_{i,j} $, while disassortative mating generates negative $ C_{i,j} $.

We assume random mating, so that $ C_{i,j}(t) = 0 $ at the start of each generation. Letting $ C^{*} $ denote the covariance after selection, where $$ C_{i j}^{*}(t)=C_{i j}(t)+\delta C_{i j}(t)\quad\mathrm{a n d}\quad C_{i,j}^{*}(t)=C_{i,j}(t)+\delta C_{i,j}(t)=\delta C_{i,j}(t) $$ (21.11a)

**[推导 Derivation]**

Assuming recombination follows selection, then with probability $ 1 - r_{ij} $, no recombination occurs between i and j and the within-gamete covariance is unchanged. Conversely, with a probability of $ r_{ij} $, recombination occurs and the new covariance depends on the covariance between gametes, yielding the result of Lande (1975) and Bulmer (1980) that

> **Formula (24.11b)** · `24.11b` · source: `chapter24_block_086` · A More Careful Treatment
>
> $$ C_{ij}(t+1)=(1-r_{ij})C_{ij}^{*}(t)+r_{ij}C_{i,j}^{*}(t) $$


**[推导 Derivation]**

Substituting for $ C^{*} $ from Equation 24.11a yields

> **Formula (24.11c)** · `24.11c` · source: `chapter24_block_087` · A More Careful Treatment
>
> $$ \begin{aligned}C_{ij}(t+1)&=(1-r_{ij})\left[\delta C_{ij}(t)+C_{ij}(t)\right]+r_{ij}\delta C_{i,j}(t)\\&=(1-r_{ij})C_{ij}(t)+\delta C_{ij}(t)-r_{ij}\left[\delta C_{ij}(t)-\delta C_{i,j}(t)\right]\end{aligned} $$


Note that we recover Equation 24.7c only if $ \delta C_{ij}(t) = \delta C_{i,j}(t) $, meaning that selection changes the within-gamete and between-gamete covariances by the same amount. Turelli and Barton (1990) showed that this occurs if there is either global gametic-phase equilibrium before selection (all groups of loci are in gametic-phase equilibrium) or the distribution of allelic effects over loci is multivariate normal (see Equations 24.13a and 24.13b). Thus, Equation 24.7c follows under Gaussian COA assumptions. However, selection can drive a distribution away from normality, in which case Equation 24.7c may no longer hold.

**[推导 Derivation]**

General expressions for $ \delta C_{ij}(t) $ and $ \delta C_{i,j}(t) $ were obtained by Turelli and Barton (1990) for the case of no dominance or epistasis. Their expressions involve generalizations of (i) measures of selection to higher moments of a distribution, and (ii) disequilibrium measures to groups of k loci. Starting with (i), recall (Equation 13.27b) that we defined the directional selection gradient, which measures how mean fitness varies with the phenotypic mean, as $ \partial \ln \overline{w} / \partial \mu_z $. We can extend this notion to higher moments by considering $ \partial \ln \overline{w} / \partial \mu_{k,z} $, where $ \mu_{k,z} = E[(z - \mu_z)^k] $ is the $ k $th central moment of the phenotypic distribution (for $ k \geq 2 $), with $ \mu_{2,z} = \sigma_z^2 $. If selection is primarily on the mean and variance of the phenotypic distribution, gradients for the skew and higher moments ($ k \geq 3 $) will generally be negligible. When phenotypes are normally distributed, the first two gradients are given by

> **Formula (24.12a)** · `24.12a` · source: `chapter24_block_089` · A More Careful Treatment
>
> $$ \frac{\partial\ln\overline{w}}{\partial\mu_{z}}=\frac{S}{\sigma_{z}^{2}} $$


> **Formula (24.12b)** · `24.12b` · source: `chapter24_block_089` · A More Careful Treatment
>
> $$ \frac{\partial\ln\overline{w}}{\partial\sigma_{z}^{2}}=\frac{\delta(\sigma_{z}^{2})+S^{2}}{2\sigma_{z}^{4}} $$


(Lande 1976; Lande and Arnold 1983). As will be shown in Chapters 29 and 30, when selection acts only on the mean (such that $ \partial \ln \overline{w}/\partial \mu_{k,z} = 0 $ for $ k \geq 2 $), the within-generation change in the phenotype variance will be $ \delta(\sigma_z^2) = -S^2 $. Hence, $ \delta(\sigma_z^2) + S^2 $ is the change in variance over that expected due to selection simply on the mean.

**[推导 Derivation]**

Using these extended selection gradients, and ignoring selection acting on the skew and higher moments (i.e., $ \partial \ln \overline{w} / \partial \mu_{k,z} = 0 $ for $ k \geq 3 $), Turelli and Barton (1990) found that

> **Formula (24.13a)** · `24.13a` · source: `chapter24_block_091` · A More Careful Treatment
>
> $$ \begin{aligned}\delta C_{ij}&=\frac{\partial\ln\overline{w}}{\partial\mu_{z}}\sum_{h=1}^{n}C_{ijh}+\frac{\partial\ln\overline{w}}{\partial\sigma_{z}^{2}}\sum_{h=1}^{n}\sum_{\ell=1}^{n}(C_{ijh\ell}-C_{ij}C_{h\ell})+\cdots\\\delta C_{i,j}&=\frac{\partial\ln\overline{w}}{\partial\sigma_{z}^{2}}2\sum_{h=1}^{n}C_{ih}\sum_{\ell=1}^{n}C_{j\ell}+\cdots\end{aligned} $$


where $ C_{ijh} $ refers to the third-order covariance between the effects of alleles at loci i, j, and h. If $ X_i $ is the additive value of a randomly chosen allele at locus i, and $ \mu_i = E(X_i) $ is the average value for this locus, then $ C_{ijh} = E[(X_i - \mu_i)(X_j - \mu_j)(X_h - \mu_h)] $. Higher-order covariances are similarly defined. The covariances in Equation 24.13a measure the amount of third-order $ (C_{ijh}) $ and fourth-order $ (C_{ijhl}) $ gametic-phase disequilibrium (the departures from random assortment for triplets and quadruplets of loci). If selection on the third (skew) or higher-order moments is significant, then Equations 24.13a and 24.13b need to include covariance terms of order five and higher.

**[推导 Derivation]**

The key point about these equations is that changes in covariances depend critically on very fine details of the genotypic distribution, details that are essentially impossible to estimate empirically in realistic situations. Thus, simplifying assumptions are required to proceed further. For example, if the distribution of the vector of individual-locus genotypic values is multivariate normal (which, as previously mentioned, involves the rather strong assumption that allelic effects at each locus are normally distributed), Equation 24.13a simplifies greatly, as $ C_{ijk} = 0 $ and $ C_{ijkl} $ can be expressed in terms of second-order covariances ($ C_{ijkl} = C_{ij}C_{kl} + C_{ik}C_{jl} + C_{il}C_{jk} $). In this case, $ \delta C_{ij} = \delta C_{i,j} $, and combining Equations 24.12b and 24.13b yields

> **Formula (24.14a)** · `24.14a` · source: `chapter24_block_092` · A More Careful Treatment
>
> $$ \delta C_{i,j}(t)=\delta C_{ij}(t)\simeq\frac{\delta(\sigma_{z}^{2})+S^{2}}{\sigma_{z}^{4}}C_{i}(t)C_{j}(t) $$


where $ C_i(t) = \sum_j C_{ij}(t) $. Thus, when allelic effects are multivariate normal (normal at each locus and multivariate normal for any subset of loci), Equation 24.11c yields a between-generation change (denoted by $ \Delta $, as opposed to a within-generation change, which is denoted by $ \delta $) in covariance of

> **Formula (24.14b)** · `24.14b` · source: `chapter24_block_092` · A More Careful Treatment
>
> $$ \Delta C_{ij}(t+1)=C_{ij}(t+1)-C_{ij}(t)=\frac{\delta(\sigma_{z}^{2})+S^{2}}{\sigma_{z}^{4}}C_{i}(t)C_{j}(t)-r_{ij}C_{ij}(t) $$


a result due to Lande (1975, 1977a). Because $ 2 \sum_i C_i = 2 \sum_{ij} C_{ij} = \sigma_A^2 $, and assuming all of the $ C_i $ are equivalent, it follows for $ n $ loci that $ C_i = \sigma_A^2 / (2n) $, and Equation 24.14a reduces to

> **Formula (24.14c)** · `24.14c` · source: `chapter24_block_092` · A More Careful Treatment
>
> $$ \delta C_{ij}\simeq\frac{\sigma_{A}^{4}}{4n^{2}\sigma_{z}^{4}}\bigg(\delta(\sigma_{z}^{2})+S^{2}\bigg)=\frac{h^{4}}{4n^{2}}\bigg(\delta(\sigma_{z}^{2})+S^{2}\bigg) $$


When $ S^2 \ll |\delta(\sigma_z^2)| $ (selection is mainly on the variance), we recover Bulmer’s approximation (Equation 24.7b) when the number of loci, $ n $, is large.

---

## chapter24_021 · The Infinitesimal Model and Its Extensions: Introduction / RESPONSE UNDER NON-GAUSSIAN DISTRIBUTIONS

**[命题 Proposition]**

The assumption that genotypic values of offspring are described by a linear and homoscedastic regression of the genotypic values of their parents most easily follows if the joint distribution of parental and offspring values is multivariate normal. This assumption, which is the basis for much of the theory of selection response, provides a simple solution to the vexing problem of modeling the transmission of a quantitative trait. The other option is Price's theorem (Equation 6.8), but its composite transmission parameter is very difficult to estimate and depends on the fine details of the underlying genetic architecture.

While changing allele frequencies and the generation of gametic-phase disequilibrium compromise the prediction of response by altering the genetic variance, a more subtle, but no less important, issue is that these changes also compromise predictions by driving the genotypic distribution away from a Gaussian. An active area of research is to both describe how selection can alter a distribution and extend selection theory to arbitrary distributions of genotypic values. While good progress has been made, we warn the reader that this can be a rather intimidating area of the literature. Our purpose here is to simply introduce some of the basic ideas and machinery used, as well as to summarize the major findings.

We start by considering how the distribution of effects at each of the individual loci translates into a distribution of genotypic values. In particular, we examine how within-locus moments of allelic effects translate into moments of the full distribution of genotypic values. While moments are more intuitive measures of the shape of a distribution, the cumulants of the distribution (to be described shortly) are more natural to work with when describing deviations from normality.

Once this basic machinery has been introduced, we will then consider two types of models for the genetics of a trait: (i) a small to modest number of segregating loci, and (ii) a very large number of loci of small effect. With a small number of loci, to an initial approximation, one can ignore effects of gametic-phase disequilibrium and instead focus on the changes in the higher genotypic moments caused by allele-frequency changes. The key result from the analysis of such models is that even single-generation predictions require extensive information about the underlying genetics. In contrast, with a very large number of loci, the (short-term) effects of allele-frequency changes can be essentially ignored, and changes from gametic-phase disequilibrium become critical. The nice (and somewhat surprising) result for this latter class of models is that both the breeder's and Bulmer equations are quite accurate for both directional and strong disruptive selection (Turelli and Barton 1994).

---

## chapter24_022 · The Infinitesimal Model and Its Extensions: Introduction / Describing the Genotypic Distribution: Moments

**[推导 Derivation]**

Under our assumption that genotypic and environmental values are additive and independent, $ z = G + E $. When environmental values, E, are normally distributed, phenotypes, z, are normally distributed if and only if the genotypic values are Gaussian (i.e., follow a normal distribution). However, the converse is not true—an approximately normal distribution of phenotypes does not necessarily imply that genotypic values are Gaussian. While we can test if phenotypes are normally distributed, this tells us little about the distribution of genotypes. In theory, we can estimate the genotypic distribution by estimating the breeding values for a sample of individuals (LW Chapter 26), but this is generally impractical in most studies (however, see Chapter 20). Further, methods used to estimate breeding values typically start with the assumption of normality (Chapters 19 and 20; LW Chapters 26 and 27), and hence bias the distribution of estimated values toward a Gaussian. Because we assume that there are no genotype×environment interactions, if the environment remains constant over time, any changes in the phenotypic distribution are entirely due to changes in the genotypic distribution. The moments of a distribution provide a conve- nient measure to describe its shape, and hence changes in the moments provide descriptions of changes in the shape of the distribution. To see the connection between the moments of the phenotypic and genotypic distributions, note that the phenotypic mean, variance, and skew can be decomposed as $ \mu_z = \mu_G $, $ \sigma_z^2 = \sigma_G^2 + \sigma_E^2 $, and $ \mu_{3,z} = \mu_{3,G} + \mu_{3,E} $. Thus, assuming no environmentally induced changes in the moments, changes in any of the first three phenotypic moments will exactly equal the change in the corresponding genotypic moments. Example 24.6 (below) uses cumulants to derive the fourth phenotypic moment, yielding

> **Formula (24.15)** · `24.15` · source: `chapter24_block_098` · Describing the Genotypic Distribution: Moments
>
> $$ \mu_{4,z}=\mu_{4,G}+\mu_{4,E}+6\sigma_{G}^{2}\sigma_{E}^{2} $$


This shows that any changes here can result from either changes in the second (variance) or fourth moments of the genotypic distribution. When E is normal, $ \mu_{3,E} = 0 $ and $ \mu_{4,E} = 3\sigma_{E}^{4} $, simplifying these expressions.

**[推导 Derivation]**

How do the moments of G depend on the distribution of allelic effects at individual loci? If n loci control the character, our assumption of complete additivity implies

> **Formula (24.16)** · `24.16` · source: `chapter24_block_100` · Describing the Genotypic Distribution: Moments
>
> $$ G=\sum_{i=1}^{n}\left(X_{fa,i}+X_{mo,i}\right) $$


where $ X_{fa,i}\left(X_{mo,i}\right) $ is the value of the paternal (maternal) allele at the ith locus. Assuming both sexes have the same distribution of allelic effects, the moments of G can be related to moments of the distribution of allelic effects at individual loci by expanding

> **Formula (24.17)** · `24.17` · source: `chapter24_block_100` · Describing the Genotypic Distribution: Moments
>
> $$ \begin{aligned}\mu_{k,G}&=E\left(\left[G-\mu_{G}\right]^{k}\right)\\&=E\left(\left[\sum_{i=1}^{n}\left\{X_{fa,i}+X_{mo,i}-2E(X_{i})\right\}\right]^{k}\right)\qquad for k\geq2\end{aligned} $$


Finally, we assume random mating, so that $ X_{fa,i} $ and $ X_{mo,i} $ are independent at the start of each generation. Because we assume that the distribution of allelic effects is the same in both sexes, we drop the subscript referring to parental origin.

**[推导 Derivation]**

When considering a particular moment of $G$, it will be important to distinguish between contributions to that moment from individual loci (within-locus moments) and contributions from gametic-phase disequilibrium (between-locus covariances). This partitioning, which was used earlier with the additive genetic variance (e.g., Equation 16.2), is extended here to the third and higher genotypic moments. To describe the distribution of effects at locus $i$, let $\mu_{1,i} = E(X_i) = m_i$ denote the average value of an allele at locus $i$, and define the $k$th moment for this locus by $\mu_{k,i} = E([X_i - m_i]^k)$ for $k \geq 2$. After summing over all $n$ loci, we define

> **Formula (24.18a)** · `24.18a` · source: `chapter24_block_102` · Describing the Genotypic Distribution: Moments
>
> $$ M_{1}=2\sum_{i=1}^{n}\mu_{1,i} $$


> **Formula (24.18b)** · `24.18b` · source: `chapter24_block_102` · Describing the Genotypic Distribution: Moments
>
> $$ M_{2}=2\sum_{i=1}^{n}\mu_{2,i} $$


> **Formula (24.18c)** · `24.18c` · source: `chapter24_block_102` · Describing the Genotypic Distribution: Moments
>
> $$ M_{3}=2\sum_{i=1}^{n}\mu_{3,i} $$


as the mean, variance, and skewness, respectively, of the genotypic distribution in terms of the mean, variance, and skew at individual loci (the within-locus moments). Finally, we define the within-locus kurtosis as

> **Formula (24.18d)** · `24.18d` · source: `chapter24_block_102` · Describing the Genotypic Distribution: Moments
>
> $$ M_{4}=2\sum_{i=1}^{n}\left(\mu_{4,i}-3\mu_{2,i}^{2}\right) $$


While this may seem odd at first, recall that the fourth and second moments of a normal distribution are related by $ \mu_4 = 3\mu_2^2 $ (LW Chapter 2). Hence, if the distribution of allelic effects at each locus is normal, $ M_4 = 0 $ and, likewise, $ M_3 = 0 $ ($ \mu_{3,i} = 0 $ because a normal random variable does not display skew). On the other hand, nonzero values of $ M_3 $ or $ M_4 $ imply that $ G $ is non-Gaussian and provide a quantitative measure of the departure from normality.

The between-locus contributions from gametic-phase disequilibrium are described by $ C_{ij} $, $ C_{ijk} $, and $ C_{ijkl} $, the covariances between, respectively, groups of two, three, and four loci, as defined previously. Note that with this notation, $ C_{ii} = \mu_{2,i} $, $ C_{iii} = \mu_{3,i} $ and $ C_{iiii} = \mu_{4,i} $, referring to the moments at locus i. If loci are independent (i.e., in gametic-phase equilibrium), then all other combinations involving four (or fewer) loci are zero except $ C_{iijj} $, which equals $ C_{ii} \cdot C_{jj} = \mu_{2,i} \cdot \mu_{2,j} $.

**[推导 Derivation]**

Following Turelli and Barton (1990), the genotypic moments can be decomposed into within-locus effects (the $ M_{i} $ from Equation 24.18) due to the moments at individual loci and between-locus effects due to covariances generated by gametic-phase disequilibrium. Remember that we are assuming the simplest case, complete additivity (no dominance or epistasis), so the genotypic distribution G is the distribution of additive genetic (breeding) values (A), namely, the sum of allelic effects over all loci. Expanding Equation 24.17 and taking expectations yields the familiar expressions for the mean and variance

> **Formula (24.19a)** · `24.19a` · source: `chapter24_block_105` · Describing the Genotypic Distribution: Moments
>
> $$ \mu_{G}=2\sum_{i=1}^{n}\mu_{1,i}=M_{1} $$


> **Formula (24.19b)** · `24.19b` · source: `chapter24_block_105` · Describing the Genotypic Distribution: Moments
>
> $$ \sigma_{G}^{2}=\sigma_{A}^{2}=2\sum_{i,j=1}^{n}C_{ij}=M_{2}+2\sum_{i=1}^{n}\sum_{j\neq i}^{n}C_{ij} $$


where $ M_2 = 2 \sum C_{ii} $ corresponds to the genic variance $ \sigma_a^2 $, and the double sum corresponds to the disequilibrium, $ d $ (Equation 16.1b). Similarly, the skew can be partitioned as

> **Formula (24.19c)** · `24.19c` · source: `chapter24_block_105` · Describing the Genotypic Distribution: Moments
>
> $$ \mu_{3,G}=2\sum_{i,j,k=1}^{n}C_{ijk}=M_{3}+2\sum_{i=1}^{n}\sum_{j,k\neq i}^{n}C_{ijk} $$


**[推导 Derivation]**

All terms in the second sums of Equations 24.19b and 24.19c are zero when all groups of two and three loci (respectively) are in gametic-phase equilibrium ($ C_{ij} = C_{ijk} = 0 $). Partitioning the kurtosis requires a little more care. After some simplification (Turelli and Barton 1990), we obtain

> **Formula (24.19d)** · `24.19d` · source: `chapter24_block_106` · Describing the Genotypic Distribution: Moments
>
> $$ \mu_{4,G}=3\sigma_{A}^{4}+M_{4}+2\sum_{i=1}^{n}\sum_{j,k,\ell\neq i}^{n}\left(C_{i j\ell k}-C_{i j}C_{k\ell}-C_{i k}C_{j\ell}-C_{i\ell}C_{j k}\right) $$


Again, these fourth- and second-order covariance terms $ (C_{ij\ell k} $ and $ C_{ij} $, respectively) are zero when all groups of four loci are in gametic-phase equilibrium. Because $ 3\sigma_A^4 $ is the kurtosis value that is expected when genotypic values are Gaussian-distributed, the last two terms partition any kurtosis in G into the contribution from individual locus kurtosis $ (M_4) $ and the contribution generated by gametic-phase disequilibrium between groups of four loci. If the distribution of allelic effects is multivariate normal, then $ M_4 = 0 $, and each term within the covariance sum is zero as $ C_{ij\ell k} = C_{ij}C_{kl} + C_{ik}C_{jl} + C_{il}C_{jk} $.

Analogous to allele frequencies changing the genic variance, $\sigma_a^2$, and disequilibrium changing the covariances (and hence $d$), changes in $M_3$ and $M_4$ reflect allele-frequency change, while changes in the third- and fourth-order covariances reflect changes from disequilibrium. These higher-order moments can depart from their expectations under normality by the presence of skewness or kurtosis of allelic effects at the individual loci (generating nonzero $M_3$ and/or $M_4$), which can result from allele-frequency changes. Alternatively, even if the within-locus moments are normal ($M_3 = M_4 = 0$), gametic-phase disequilibrium (nonzero

$ C_{ijk} $ and/or $ C_{ijk\ell} $ can introduce skewness and/or kurtosis. When the number of loci is small, the impact of skew or kurtosis at the individual loci can be significant (Equation 24.6), yielding nonzero $ M_3 $ and/or $ M_4 $, with the resulting genotypic distribution deviating from normality.

To see these points, first consider the changes due to within-locus moments. If $ n $ is the number of loci, then as we saw earlier the effects $ (a) $ of alleles at individual loci must scale as $ 1/\sqrt{n} $ in order for the genetic variance to remain bounded, hence $ C_{ii} $ terms scale as $ a^2 $ or $ n^{-1} $. Summing over all $ n $ loci, $ M_2 $ will be of order $ n \cdot n^{-1} = 1 $ and, as required, remains bounded as the number of loci increases. What happens to the skew and kurtosis as $ n $ increases? Assuming $ a $ is of order $ n^{-1/2} $, then $ \mu_{3,i} $ will be of order $ a^3 $ or $ n^{-3/2} $, implying that $ M_3 $ is of order $ n \cdot n^{-3/2} = n^{-1/2} $ (also see Equation 24.6). Hence, as the number of loci becomes very large, the contribution from skew at individual loci becomes negligible. Likewise, $ \mu_{4,i} $ is of order $ n^{-4/2} $, implying $ M_4 $ is of order $ n \cdot n^{-2} = n^{-1} $ (Equation 24.6). Changes in kurtosis generated by within-locus (i.e., allele-frequency) changes become negligible as the number of loci becomes sufficiently large, but this occurs even more rapidly than skew with increasing $ n $.

The behavior of the between-locus contributions (correlations from disequilibrium) as n increases is quite different from that due to within-locus contributions (Turelli and Barton 1990). Under weak selection, Turelli and Barton showed that $ C_{ijk} $ is proportional to $ C_{ii}C_{jj}C_{kk} $, and of order $ n^{-3} $. However, there are $ n(n-1)(n-2) \simeq n^{3} $ terms involving $ C_{ijk} $ in the covariance contribution to skew, so the total contribution is of order one and does not necessarily converge to zero as the number of loci approaches infinity. The same argument holds for the kurtosis and higher-order moments (Turelli and Barton 1990). If the number of loci is very large, the distribution of genotypic values can depart from a Gaussian due to selection generating third- and higher-order covariances between loci, which in turn creates skew and kurtosis in the genotypic distribution. Even if the distribution of genotypes is initially Gaussian, selection generates these higher-order disequilibria, driving it away from normality (Bulmer 1980; Zeng 1987; Turelli and Barton 1990, 1994). Conversely, when selection stops, this disequilibrium quickly decays to zero, restoring the Gaussian.

---

## chapter24_023 · The Infinitesimal Model and Its Extensions: Introduction / Describing the Genotypic Distribution: Cumulants and Gram-Charlier Series

While most readers are familiar with moments, an alternate approach to describing the shape of a distribution, and in particular its departures from a Gaussian, is to examine its cumulants. These quantities, which arise from the moment-generation function of a probability distribution, offer some advantages over moments, as we will discuss shortly. The first uses of cumulants in examining selection response appears in O'Donald (1972) and Bulmer (1980). Sophisticated (and highly technical) treatments were developed by Bürger (1991a, 1993) and Turelli and Barton (1994). Our aim here is both to give the fearless reader sufficient background to this literature and to show the connection between results derived using moments and those derived using cumulants.

Cumulants (the nth of which we denote by $ K_n $) arise naturally in series approximations of probability distributions, and they can be related to the central moments ($ \mu_n $). For example, the first five central moments can be expressed as functions of the cumulants as follows: $$ \mu_{1}=K_{1},\quad\mu_{2}=K_{2},\quad\mu_{3}=K_{3},\quad\mu_{4}=K_{4}+3K_{2}^{2},\quad\mu_{5}=K_{5}+10K_{2}K_{3} $$

**[推导 Derivation]**

(Kendall and Stuart 1977). Hence, the first three cumulants are equal to the mean, variance, and skew, respectively, while the fourth and fifth cumulants are

> **Formula (24.20)** · `24.20` · source: `chapter24_block_114` · Describing the Genotypic Distribution: Cumulants and Gram-Charlier Series
>
> $$ K_{4}=\mu_{4}-3\mu_{2}^{2},\quad K_{5}=\mu_{5}-10\mu_{2}\mu_{3} $$


The major advantage of cumulants over moments is that they are additive, so that the nth cumulant of a sum of random variables is simply the sum of the cumulants for each, namely, $ K_n(x+y) = K_n(x) + K_n(y) $. This linearity property does not hold for higher-order moments, which are highly nonlinear functions of the moments of the component distributions. For a normal distribution, cumulants of order three and higher are zero, so nonzero values for these higher-order cumulants provide a convenient measure of departures from normality.

The major disadvantage of using cumulants in place of moments arises when dealing with recombination (Turelli and Barton 1994; Bürger 2000). In such cases, one works with cumulants to compute within-generation changes, converts these to moments for recombination, and then converts the recombinant products back into cumulants.

**[推导 Derivation]**

Finally, cumulants appear in series approximations of arbitrary probability distributions. Consider a standardized random variable, $ y = (z - \mu)/\sigma $, which has mean zero and variance one. If the true density function for $ y $ is $ \phi(y) $, we can approximate it as a unit-normal density function, $ \varphi(y) $, plus correction terms. In particular (Johnson and Kotz 1970a; Kendall and Stuart 1977), the Gram-Charlier series approximation (here shown to order five) is given by

> **Formula (24.21a)** · `24.21a` · source: `chapter24_block_117` · Describing the Genotypic Distribution: Cumulants and Gram-Charlier Series
>
> $$ \phi(y)\simeq\varphi(y)\left[1+\frac{K_{3}}{6}H_{3}(y)+\frac{K_{4}}{24}H_{4}(y)+\frac{K_{5}}{120}H_{5}(y)\right] $$


where $ H_{k}(y) $ denotes the Chebyshev-Hermite polynomial of order k, with

> **Formula (24.21b)** · `24.21b` · source: `chapter24_block_117` · Describing the Genotypic Distribution: Cumulants and Gram-Charlier Series
>
> $$ \begin{aligned}&H_{3}(y)=y^{3}-3y\\&H_{4}(y)=y^{4}-6y^{2}+3\\&H_{5}(y)=y^{5}-10y^{3}+15y\\ \end{aligned} $$


Equation 24.21a shows how the higher-order cumulants $ (K_{3} $ and above $ quantify departures from normality. If all of these are zero, the distribution is Gaussian.

Bulmer (1980), Zeng (1987), and Turelli and Barton (1994) used Gram-Charlier series to examine departures from normality under selection. Further properties of cumulants and Gram-Charlier (and other) series approximations are discussed in Johnson and Kotz (1970a) and Kendall and Stuart (1977). One potentially troublesome issue with Equation 24.21a is that the term in the square brackets can be negative for some y values (and hence not a proper probability distribution) if too low an order of approximation is used.

**[示例 Example]**

> **Example 24.6** · ref: `24.6` · source: `chapter24_023.json` · blocks 8–8
>
> Example 24.6. Cumulants can be used to easily compute the fourth and fifth central moments of the phenotypic distribution. Here, $ z = G + E $, so (Equation 24.20) the fourth moment is $$ \begin{aligned}\mu_{4,z}&=K_{4,z}+3K_{2,z}^{2}\\&=\left[K_{4,G}+K_{4,E}\right]+3\left(K_{2,G}+K_{2,E}\right)^{2}\\&=\left[\left(\mu_{4,G}-3\mu_{2,G}^{2}\right)+\left(\mu_{4,E}-3\mu_{2,E}^{2}\right)\right]+3\left(\mu_{2,G}+\mu_{2,E}\right)^{2}\\&=\mu_{4,G}+\mu_{4,E}+6\sigma_{G}^{2}\sigma_{E}^{2}\\ \end{aligned} $$ where the second and third steps, respectively, follow from the additivity property of cumulants $ (K_{n,z}=K_{n,G}+K_{n,E}) $ and from Equation 24.20, while the final step recovers Equation 24.15. Likewise $$ \begin{aligned}\mu_{5,z}&=K_{5,z}+10K_{2,z}K_{3,z}\\&=(\boldsymbol{K}_{5,G}+\boldsymbol{K}_{5,E})+10(\boldsymbol{K}_{2,G}+\boldsymbol{K}_{2,E})(\boldsymbol{K}_{3,G}+\boldsymbol{K}_{3,E})\\&=(\mu_{5,G}-10\mu_{2,G}\mu_{3,G})+(\mu_{5,E}-10\mu_{2,E}\mu_{3,E})\\&\quad+10(\mu_{2,G}+\mu_{2,E})(\mu_{3,G}+\mu_{3,E})\\&=\mu_{5,G}+\mu_{5,E}+10(\mu_{2,G}\mu_{3,E}+\mu_{2,E}\mu_{3,G})\end{aligned} $$
> 
> These nonlinear expressions for the higher-order moments of a sum of variables are in sharp contrast to the expressions for cumulants, in which $ K_{n,z} = K_{n,G} + K_{n,E} $.


**[示例 Example]**

> **Example 24.7** · ref: `24.7` · source: `chapter24_023.json` · blocks 9–9
>
> Example 24.7. To see the advantage of working with cumulants, consider the fourth cumulant of the genotypic distribution. Equation 24.19d presented a rather complex expression for the fourth moment, but we can use cumulants to easily obtain this result. If the underlying genes are additive across loci (no epistasis), the nth cumulant of the genotypic distribution is the sum of the appropriate cumulants for each of the underlying loci. Following Turelli and Barton (1994) $$ K_{4,G}=\sum_{i,j,k,\ell=1}^{n}K_{i j k\ell}=\sum_{i=1}^{n}K_{i i i i}+\sum_{i=1}^{n}\sum_{j,k,\ell\neq i}^{n}K_{i j k\ell} $$ the sum over $ K_{iii} $ represents the within-locus contributions to the fourth cumulant, while the sums over the other indices are the contributions to $ K_4 $ from fourth-order disequilibria between loci. We recover Equation 24.19d by noting that $ \mu_{4,G} = K_{4,G} + 3\sigma_A^4 $ and substituting $$ M_{4}=\sum_{i=1}^{n}K_{iiii}\quad and\quad K_{ijk\ell}=C_{ijk\ell}-C_{ij}C_{k\ell}-C_{ik}C_{j\ell}-C_{i\ell}C_{jk} $$


---

## chapter24_024 · The Infinitesimal Model and Its Extensions: Introduction / Application: Departure from Normality Under Truncation Selection

One application of the preceding machinery is to compute the distribution of breeding values following a single generation of truncation selection, assuming that the initial joint distribution of phenotypic and breeding values is multivariate normal. This was examined by Bulmer (1980) and Zeng (1987), and Turelli and Barton (1994) presented a very elegant (and elaborate) analysis for multiple generations. As before, we consider only additive models, so the distribution of genotypic values is also the distribution of breeding values.

**[推导 Derivation]**

First, we assume that there is initial (i.e., existing before selection) normality in phenotypic values, $ z \sim N(\mu, \sigma_z^2) $, and compute the cumulants for the resulting distribution of phenotypic values after truncation selection. As before (Chapters 14 and 16), truncation selection saves the uppermost fraction, p, of the population, giving a selection intensity of $$ \bar{\imath}=\frac{\varphi(z_{p})}{p} $$ where $ \varphi(z_p) $ is the value of a unit-normal density function evaluated at $ z_p $, and $ z_p $ satisfies $ \Pr(U > z_p) = p $, with $ U $ denoting a unit-normal random variable (Equation 14.2b). From Chapters 14 and 16, we already have the first two cumulants following selection as $$ K_{1,z}^{*}=\mu^{*}=\mu+\overline{\imath}\sigma_{z}\quad and\quad K_{2,z}^{*}=\sigma_{z}^{2}*=[1-\overline{\imath}(\overline{\imath}-z_{p})]\sigma_{z}^{2} $$ while the next two cumulants are (from Bulmer 1980)

> **Formula (24.22a)** · `24.22a` · source: `chapter24_block_124` · Application: Departure from Normality Under Truncation Selection
>
> $$ K_{3,z}^{*}=[(\bar{\imath}-z_{p})(2\bar{\imath}-z_{p})-1]\;\bar{\imath}\sigma_{z}^{3} $$


> **Formula (24.22b)** · `24.22b` · source: `chapter24_block_124` · Application: Departure from Normality Under Truncation Selection
>
> $$ K_{4,z}^{*}=\left[-6\overline{\imath}\left(\overline{\imath}-z_{p}\right)^{2}+(3-z_{p}^{2})\left(\overline{\imath}-z_{p}\right)+\overline{\imath}\right]\overline{\imath}\sigma_{z}^{4} $$


Next, we translate these within-generation changes in the phenotypic distribution into the within-generation change in the distribution of breeding values and then examine how this breeding-value distribution changes (under random mating) during transmission to the next generation. Both steps rely critically on assumptions of normality. If the distribution of breeding and phenotypic values is bivariate normal before selection (as might occur in the initial round of selection, but not necessarily in subsequent rounds), then the regression of breeding values on phenotypic values is linear. $$ A=\mu_{z}+h^{2}(z-\mu_{z})+\epsilon $$

**[推导 Derivation]**

Rao et al. (1968) showed that a single generation of truncation selection does not alter this regression, which leads to our standard results (Chapter 16) for the mean and variance of the breeding values following selection

> **Formula (24.23a)** · `24.23a` · source: `chapter24_block_126` · Application: Departure from Normality Under Truncation Selection
>
> $$ \mu_{A}^{*}=\mu_{z}+h^{2}\bar{\imath}\sigma_{z} $$


and

> **Formula (24.23b)** · `24.23b` · source: `chapter24_block_126` · Application: Departure from Normality Under Truncation Selection
>
> $$ \sigma_{A*}^{2}=\sigma_{A}^{2}\left[1-h^{2}\bar{\imath}\left(\bar{\imath}-z_{p}\right)\right] $$


**[推导 Derivation]**

Bulmer (1980) showed that when the joint distribution of breeding values and phenotypes is multivariate normal before selection, all higher cumulants follow a very simple relationship

> **Formula (24.24a)** · `24.24a` · source: `chapter24_block_127` · Application: Departure from Normality Under Truncation Selection
>
> $$ K_{i,A}^{*}=\left(h^{2}\right)^{i}K_{i,z}^{*}\qquad for\quad i\geq3 $$


**[推导 Derivation]**

Assuming unlinked loci, the cumulants for the distribution of breeding values in the next generation become

> **Formula (24.24b)** · `24.24b` · source: `chapter24_block_128` · Application: Departure from Normality Under Truncation Selection
>
> $$ K_{i,A}(t+1)=\left(\frac{1}{2}\right)^{i-1}K_{i,A}^{*}(t) $$


**[推导 Derivation]**

Hence, the cumulants for the distribution of breeding values at the start of the next generation are related to the cumulants of the postselection phenotypic distribution by

> **Formula (24.24c)** · `24.24c` · source: `chapter24_block_129` · Application: Departure from Normality Under Truncation Selection
>
> $$ K_{i,A}(t+1)=2\left(\frac{h^{2}}{2}\right)^{i}K_{i,z}^{*}(t) $$


**[命题 Proposition]**

Notice from Equation 24.22 that after a single generation of selection, $ K_{3,A} $ and $ K_{4,A} $ will be nonzero, and hence the distribution of breeding values will no longer be normal. At this point, the assumption of bivariate normality no longer holds, and there is no longer a simple relationship between $ K_{i,A}^{*} $ and $ K_{i,z}^{*} $. Thus, we cannot simply iterate this procedure over more than one generation of selection. See Turelli and Barton (1994) for a detailed analysis over multiple generations.

**[示例 Example]**

> **Example 24.8** · ref: `24.8` · source: `chapter24_024.json` · blocks 8–8
>
> Example 24.8. Suppose truncation selection occurs on a normally distributed trait with an initial mean of $ \mu_z = 0 $ and variance of $ \sigma_z^2 = 100 $. Individuals whose phenotypes are in the upper 5% of the distribution are saved, so that $ \bar{i} = 2.063 $ and $ z_p = 1.645 $ (Example 14.1). To demonstrate an extreme case, assume that $ h^2 = 1 $, so that all variance is additive genetic. Applying Equation 24.22a, the resulting third-order cumulant in the phenotypic distribution following selection is $$ \begin{aligned}K_{3,z}^{*}&=[\left(\bar{\iota}-z_{p}\right)(2\bar{\iota}-z_{p})-1]\bar{\iota}\sigma_{z}^{3}\\&=\left[(2.063-1.645)(2\cdot2.063-1.645)-1\right]\cdot2.063\cdot100^{3/2}\\&=76.45\\ \end{aligned} $$
> 
> Applying Equation 24.24c translates this into the third cumulant in the genotypic distribution in the next generation, yielding $$ K_{3,A}(t+1)=2\left(\frac{h^{2}}{2}\right)^{3}K_{3,z}^{*}(t)=2\left(\frac{1}{2}\right)^{3}76.45=19.11 $$
> 
> Using the machinery from Chapter 16, for $p = 0.2$, Equation 16.11a yields $\kappa = 0.862$ (i.e., selected individuals have only a fraction, [1 - 0.862] = 0.138, of the variance of the preselection population), and Equation 16.12d returns $d(1) = (-\kappa/2)100 = -43.1$. Hence, the phenotypic variance in the first generation is $ \sigma_{z}^{2} = \sigma_{A}^{2}(1) = 100 + d(1) = 56.9 $. Thus, the scaled skew becomes $$ \gamma_{3}=\frac{K_{3}}{\sigma_{A}^{3}}=\frac{19.11}{56.9^{3/2}}=0.045 $$
> 
> A similar calculation using Equations 24.22b and 24.24c yields $ K_4 = 59.7 $ and $ \gamma_4 = K_4/56.9^2 = 0.018 $. Applying Equation 24.21a, the resulting (fourth-order) Gram-Charlier series approximation for the distribution, $ \phi(A) $, of breeding values in generation 1 is $$ \begin{align*}\phi(A^{\prime})&\simeq\varphi(A^{\prime})\left[1+\frac{0.045}{6}H_{3}(A^{\prime})+\frac{0.018}{24}H_{4}(A^{\prime})\right]\\&=\varphi(A^{\prime})\left[1+0.0075H_{3}(A^{\prime})+0.00075H_{4}(A^{\prime})\right]\end{align*} $$ where $ \varphi(x) $ is the normal distribution, the functions $ H_i(x) $ are defined by Equation 24.21b, and $ A' = A/\sigma_A $ is the standardized breeding value (which, initially, has a mean of zero). For example, consider $ A' = 2 $, a value two standard deviations away from the mean. Applying Equation 24.21b, $ H_3(2) = 2 $ and $ H_4(2) = -5 $, yielding the correction factor for the unit normal density function as $$ 1+0.0075H_{3}(2)+0.00075H_{4}(2)=1.01125 $$
> 
> The key point is that the resulting distribution is only very weakly perturbed away from a Gaussian (assuming that $ h^2 = 1 $ is the most extreme case). For a more typically heritability, say $ h^2 = 0.3 $, similar calculations yield $ \gamma_3 = 0.0039 $ and $ \gamma_4 = 0.0007 $, and $$ \phi(A)\simeq\varphi(A)\left[1+0.00065H_{3}(A^{\prime})+0.00003H_{4}(A^{\prime})\right] $$ yielding an even smaller departure from normality (an adjustment factor of 1.00115 for $ A' = 2 $).
> 
> Thus, under the infinitesimal model, the generation of linkage disequilibrium by truncation selection has very little impact on driving the distribution of breeding values away from a Gaussian. While the disequilibrium introduced by truncation selection can indeed drive a distribution of breeding values away from a strict Gaussian, the error in assuming this remains Gaussian is generally small. This point was initially made by Bulmer (1980). The much more extensive analysis by Turelli and Barton (1994) showed that, even in the presence of strong truncation or disruptive selection, the Bulmer equation (Equation 16.7b) can be used with little error. Turelli and Barton's analysis assumed a sufficiently large number of loci so that changes in both the genic variance and locus-specific cumulants of order three or higher can be ignored.


---

## chapter24_025 · The Infinitesimal Model and Its Extensions: Introduction / Short-term Response Ignoring Linkage Disequilibrium

With this machinery in hand, we are now ready to examine the response to selection under non-Gaussian genotypic distributions. We first consider the situation in which a small to modest number of loci underlie the character, wherein most of the changes in the higher-order moments are due to changes in allele frequencies, rather than through generation of gametic-phase disequilibrium. Our treatment follows that of Barton and Turelli (1987).

If we are willing to assume additivity across loci and gametic-phase equilibrium, genetic changes in the character will be completely described by the dynamics of allele-frequency changes at each locus. The complete dynamics for a locus with k alleles are described by the k-1 allele-frequency change equations. Alternatively, we could fully describe the dynamics by using equations based on any set of k-1 independent new variables that can be expressed as functions of allele frequencies (this is the standard multivariate transformation problem of vector calculus and requires that the determinant of the Jacobian transformation matrix be nonzero). One such set of new variables involves the first k-1 moments of the allelic distribution. This is the motivation behind Barton and Turelli's (1987) approach, which focuses on allelic moments, rather than allelic frequencies.

If we ignore gametic-phase disequilibrium, then for $n$ loci with $k$ alleles each, we can completely describe the dynamics by using the first $n(k-1)$ moments of the genotypic distribution. This same approach can be used when linkage is considered, but in this case the number of equations increases dramatically (scaling as the number of distinct gametic types). While the process of using a new set of variables is exact, it is also just as challenging to solve as the original allele-frequency change equations. The hope, however, is that by considering the first few moments, we can gain considerable insight into the actual dynamics and a better feel for the conditions under which certain approximations work and those under which they break down.

**[推导 Derivation]**

To briefly sketch the approach used by Barton and Turelli, recall Wright’s formula for frequency changes with multiple alleles (Equation 5.11a)

> **Formula (24.25a)** · `24.25a` · source: `chapter24_block_140` · Short-term Response Ignoring Linkage Disequilibrium
>
> $$ \Delta p_{i}=\sum_{j=1}^{k}G_{ij}\frac{\partial\ln\overline{w}}{\partial p_{j}} $$


where $ G_{ii} = p_i(1 - p_i)/2 $ and $ G_{ij} = -p_i p_j/2 $ (for $ i \neq j $). The assumption of linkage equilibrium is needed here, as Wright's formula fails when single-locus fitnesses are background-dependent, which can occur even with constant genotypic fitnesses when linkage disequilibrium is present (see Example 5.7 for details). Now consider a function, $ f(p_1, p_2, \ldots, p_{k-1}) $, that depends on the allele frequencies at this locus, such as a particular moment of the allelic distribution. The change in $ f $ due to changes in allele frequencies can be approximated by a second-order Taylor series to yield

> **Formula (24.25b)** · `24.25b` · source: `chapter24_block_140` · Short-term Response Ignoring Linkage Disequilibrium
>
> $$ \Delta f=\sum_{i=1}^{k}\frac{\partial f}{\partial p_{i}}\Delta p_{i}+\frac{1}{2}\sum_{i=1}^{k}\sum_{j=1}^{k}\frac{\partial^{2}f}{\partial p_{j}\partial p_{i}}\Delta p_{i}\Delta p_{j}+\cdots $$


where this expression ignores higher-order terms of $ \Delta p_{i} $. Substituting for $ \Delta p_{i} $ via Equation 24.25a yields (to first order)

> **Formula (24.25c)** · `24.25c` · source: `chapter24_block_140` · Short-term Response Ignoring Linkage Disequilibrium
>
> $$ \Delta f\simeq\sum_{i=1}^{k}\frac{\partial f}{\partial p_{i}}\left(\sum_{j=1}^{k}G_{ij}\frac{\partial\ln\overline{w}}{\partial p_{j}}\right) $$


**[推导 Derivation]**

Recall from the chain rule of differentiation that $$ \frac{\partial\ln\overline{w}}{\partial p_{j}}=\frac{\partial\ln\overline{w}}{\partial f}\frac{\partial f}{\partial p_{j}} $$ which, upon substitution in Equation 24.52c, yields

> **Formula (24.25d)** · `24.25d` · source: `chapter24_block_141` · Short-term Response Ignoring Linkage Disequilibrium
>
> $$ \Delta f=\frac{\partial\ln\overline{w}}{\partial f}\sum_{i=1}^{k}\sum_{j=1}^{k}\frac{\partial f}{\partial p_{i}}G_{ij}\frac{\partial f}{\partial p_{j}} $$


This is a weak-selection approximation, as it assumes that terms of second order, $ (\Delta p_i \Delta p_j) $, and higher can be ignored (if drift is considered, these second-order terms must be included even if selection is weak; see Turelli 1988).

**[推导 Derivation]**

Using this expression yields a set of equations in which changes in a certain moment depend on higher-order moments. After considerable algebra (for details, see Barton and Turelli 1987), the changes in genotypic moments (under the assumptions of complete additivity and gametic-phase equilibrium) can be expressed in matrix form as

> **Formula (24.26a)** · `24.26a` · source: `chapter24_block_143` · Short-term Response Ignoring Linkage Disequilibrium
>
> $$ \mathbf{\Delta}_{\mu_{G}}\simeq\mathbf{M}\nabla\ln\overline{{w}} $$


where

> **Formula (24.26b)** · `24.26b` · source: `chapter24_block_143` · Short-term Response Ignoring Linkage Disequilibrium
>
> $$ \begin{aligned}\boldsymbol{\Delta}_{\mu_{G}}&=\begin{bmatrix}\Delta\mu_{1,G}\\\Delta\mu_{2,G}\\\Delta\mu_{3,G}\\\vdots\end{bmatrix}\quad and\quad\nabla\ln\overline{w}=\begin{bmatrix}\frac{\partial\ln w}{\partial\mu_{1,z}}\\\frac{\partial\ln\overline{w}}{\partial\mu_{2,z}}\\\frac{\partial\ln\overline{w}}{\partial\mu_{3,z}}\\\vdots\end{bmatrix}\end{aligned} $$


are, respectively, the vectors of changes in the genotypic moments ($ \mathbf{\Delta}_{\mu_G} $) and the vector of partial derivatives of log mean fitness with respect to each moment ($ \nabla \ln \overline{w} $), and a matrix of genotypic moments,

> **Formula (24.26c)** · `24.26c` · source: `chapter24_block_143` · Short-term Response Ignoring Linkage Disequilibrium
>
> $$ \mathbf{M}=2\sum_{i=1}^{n}\left[\begin{array}{cccc}\mu_{2,i}&\mu_{3,i}&(\mu_{4,i}-3\mu_{2,i}^{2})&\cdots\\ \mu_{3,i}&(\mu_{4,i}-\mu_{2,i}^{2})&(\mu_{5,i}-4\mu_{3,i}\mu_{2,i})&\cdots\\ (\mu_{4,i}-3\mu_{2,i}^{2})&(\mu_{5,i}-4\mu_{3,i}\mu_{2,i})&(\mu_{6,i}-\mu_{3,i}^{2}-6\mu_{2,i}\mu_{4,i}+9\mu_{2,i}^{2})&\cdots\\ \vdots&\vdots&\vdots&\ddots\end{array}\right] $$


The summation symbol used Equation 24.26c indicates that each element on M is twice the sum of a (locus-specific) quantity over all loci. The additional elements of M that are not displayed correspond to selection on the fourth and higher moments ($ M_{ij} $ for i and/or $ j \geq 4 $). The expressions for these terms are more complicated than may be suggested by the simple dots in the matrix due to the nonadditive nature of higher moments. Expressions based on $ \partial \ln \overline{w} / \partial K_{i,z} $ (the partial derivative of fitness with respect to the $ i $th cumulant of the phenotypic distribution) have a simpler form due to the additive nature of cumulants (Bürger 1991a, 1993; Turelli and Barton 1994), but retain the undesirable feature that the response of the $ i $th cumulant depends on cumulants of higher order.

In order to close the set of equations given by 24.26a–24.26c, we must impose restrictions on the number of columns in M, which requires assuming that selection mainly occurs on the first few moments. Likewise, the number of rows of M must also be restricted, which implies additional assumptions on the genetic moments. Examples 24.9 and 24.11 discuss the two most common assumptions to accomplish these goals, namely the Gaussian and rare-alleles models.

**[推导 Derivation]**

In cases where the first three phenotypic moments account for the majority of selection, the expected single-generation change in mean becomes

> **Formula (24.27)** · `24.27` · source: `chapter24_block_146` · Short-term Response Ignoring Linkage Disequilibrium
>
> $$ \Delta\mu_{z}\simeq\sigma_{A}^{2}\frac{\partial\ln\overline{w}}{\partial\mu_{z}}+\mu_{3,G}\frac{\partial\ln\overline{w}}{\partial\mu_{2,z}}+\kappa_{4}\sigma_{A}^{4}\frac{\partial\ln\overline{w}}{\partial\mu_{3,z}} $$


where $ \kappa_4 = (\mu_4, G - 3\sigma_A^4)/\sigma_A^4 $ is the scaled coefficient of kurtosis (Frank and Slaktin 1990 obtained the same result, for the special case of stabilizing selection using the Price equation; Chapter 6). If the distribution of $ G $ is Gaussian, then $ \mu_{3,z} = \kappa_4 = 0 $, and we recover the selection gradient version of the breeder's equation (Equation 13.27a). Under more general distributions, predicting changes in even the simplest genotypic moment, the mean, requires a detailed knowledge of both higher-order allelic moments ($ \mu_{k,i} $) and the nature of selection on these higher-order moments ($ \partial \ln \overline{w} / \partial \mu_{k,z} $). In order to proceed further, we have to make additional assumptions about the distribution of allelic effects at individual loci.

If the phenotypes are approximately normally distributed (but allelic effects at individual loci are not necessarily Gaussian), the mean and variance terms of the selection gradient vector generally will dominate. Recalling Equations 24.12 and 24.18, Equation 24.26a re duces to $$ \begin{bmatrix}\Delta\mu_{1,G}\\ \Delta\mu_{2,G}\\ \Delta\mu_{3,G}\\ \vdots\end{bmatrix}=\begin{bmatrix}\sigma_{A}^{2}&M_{3}\\ M_{3}&M_{4}\\ M_{4}&2\sum_{i}(\mu_{5,i}-4\mu_{3,i}\mu_{2,i})\\ \vdots&\vdots\end{bmatrix}\begin{bmatrix}\frac{S}{\sigma_{z}^{2}}\\ \frac{\delta(\sigma_{z}^{2})+S^{2}}{2\sigma_{z}^{4}}\end{bmatrix} $$

**[推导 Derivation]**

If we consider only the first three genotypic moments, then

> **Formula (24.28a)** · `24.28a` · source: `chapter24_block_148` · Short-term Response Ignoring Linkage Disequilibrium
>
> $$ \Delta\mu_{G}\simeq h^{2}S+\left(\frac{\delta(\sigma_{z}^{2})+S^{2}}{2\sigma_{z}^{4}}\right)M_{3} $$


> **Formula (24.28b)** · `24.28b` · source: `chapter24_block_148` · Short-term Response Ignoring Linkage Disequilibrium
>
> $$ \Delta\sigma_{A}^{2}\simeq\frac{S}{\sigma_{z}^{2}}M_{3}+\left(\frac{\delta(\sigma_{z}^{2})+S^{2}}{2\sigma_{z}^{4}}\right)M_{4} $$


> **Formula (24.28c)** · `24.28c` · source: `chapter24_block_148` · Short-term Response Ignoring Linkage Disequilibrium
>
> $$ \Delta\mu_{3,G}\simeq\frac{S}{\sigma_{z}^{2}}M_{4}+\left(\frac{\delta\left(\sigma_{z}^{2}\right)+S^{2}}{\sigma_{z}^{4}}\right)\sum_{i=1}^{n}\left(\mu_{5,i}-4\mu_{3,i}\mu_{2,i}\right) $$


where $ M_3 $ and $ M_4 $ are as defined by Equations 24.18c and 24.18d. As is discussed in Chapters 29 and 30, when selection acts only on the mean ($ \partial \ln \overline{w} / \partial \mu_{k,z} = 0 $ for $ k \geq 2 $), $ \delta(\sigma_z^2) = -S^2 $, meaning that the first term in each of these three equations accounts for the effect of selection to change the mean and the second term accounts for the effect of selection acting directly on the variance (selection is based, in part, on an individual's squared deviation from the mean, $ [z - \mu]^2 $). We previously obtained Equation 24.28a by an alternative approach (Equation 5.27b). When the genotypic distribution is skewed ($ M_3 \neq 0 $), the single-generation change in the mean also depends on the nature of selection on the variance (O'Donald 1968, 1972; Bulmer 1980; Gillespie 1984a; Barton and Turelli 1987; Mitchell-Olds and Shaw 1987). Further, even if skew is initially absent, Equation 24.28c shows that if the kurtosis of the genotypic distribution differs from that expected for a Gaussian ($ M_4 \neq 0 $), selection that is strictly on the mean generates skew. Thus, even ignoring the effects of gametic-phase disequilibrium, selection on the mean generates skew when the genotypic distribution displays kurtosis.

Whether allele-frequency change at the individual loci or gametic-phase disequilibrium among loci is more important for producing departures from normality depends on whether there are alleles of modest to large effects. When alleles of major effect are present, locus-specific selection coefficients (e.g., Equation 5.21) can be sufficiently large that significant allele-frequency change can quickly occur, which has a far great effect on departures from normality than does selection-generated disequilibrium (Turelli and Barton 1990). Conversely, when all alleles have small effects (and hence selection is extremely weak on any single locus), then over modest time scales, departure from normality is largely due to selection generating third- (and higher-) order disequilibrium. Thus, when the number of loci is small, the error created by using Equation 24.26a (which assumes gametic-phase equilibrium) should be small. As the number of (equivalent) loci increases, within-locus effects make a smaller and smaller contribution, with departures from normality caused by disequilibrium eventually dominating any small departures caused by allele frequency change.

---

## chapter24_026 · The Infinitesimal Model and Its Extensions: Introduction / Gaussian Versus Rare-alleles Approximations

In order to have Equation 24.26a form a closed set of equations, additional assumptions are needed, both on the nature of selection (columns of M) and on the underlying genetics (rows of M). If phenotypes are (and remain) normally distributed, then one needs to only consider selection on the mean and variance, as these define all other moments. More generally, if selection is sufficiently weak, then any selection function can be well approximated by a quadratic Taylor series, which again only involves the first two moments.

Two different assumptions about the genotypic distribution have been used to reduce Equation 24.26a to the first three moments. The first is to assume that distributions start (and remain) Gaussian (Example 24.9). The second is the rare-alleles model, which assumes loci are very near fixation (Example 24.11). This model is very closely related to an important approximation (Turelli's 1984 house-of-cards) which appears in Chapter 28 and which assumes that the effect of a new mutation is large relative to the amount of standing variation at a locus, which is equivalent to assuming that selection is much stronger than mutation.

**[示例 Example]**

> **Example 24.9** · ref: `24.9` · source: `chapter24_026.json` · blocks 2–2
>
> Example 24.9. If we assume that the Gaussian approximation holds, the distribution of allelic effects at each locus will be normal. In this case, all odd central moments at each locus are zero ($ \mu_{2k+1} = 0 $) and all even moments are related to the second moment by $ \mu_{2k} = \mu_2^k (2k)! / (2^k k!) $ (Kendall and Stewart 1977). For example, $ \mu_4 = 3\mu_2^2 $, implying that $ \mu_4 - \mu_2^2 = 2\mu_2^2 $. Assuming that most of selection is on the mean and variance, we can neglect the third- and higher-order selection gradients. In this case, M (Equation 24.26c) reduces to a $ 2 \times 2 $ matrix
> 
> > **Formula (24.29a)** · `24.29a` · source: `chapter24_block_152` · Gaussian Versus Rare-alleles Approximations
> >
> > $$ \mathbf{M}=\begin{pmatrix}{{{2\displaystyle\sum_{i=1}^{n}\mu_{2,i}}}}&{{{0}}} \\{{{0}}}&{{{4\displaystyle\sum_{i=1}^{n}\mu_{2,i}^{2}}}}\end{pmatrix}=\begin{pmatrix}{{{\sigma_{A}^{2}}}}&{{{0}}} \\{{{0}}}&{{{\frac{\sigma_{A}^{4}}{n_{e}}}}}\end{pmatrix} $$
> 
> 
> where
> 
> > **Formula (24.29b)** · `24.29b` · source: `chapter24_block_152` · Gaussian Versus Rare-alleles Approximations
> >
> > $$ n_{e}=\frac{\sigma_{A}^{4}}{4\sum_{i}\mu_{2,i}^{2}} $$
> 
> 
> is equivalent to Chevalet's (1994) effective number of loci (Equation 24.3); see Example 24.10. The expected response in the genotypic mean and variance then becomes
> 
> > **Formula (24.30a)** · `24.30a` · source: `chapter24_block_152` · Gaussian Versus Rare-alleles Approximations
> >
> > $$ \left(\begin{array}{c}{{{\Delta\mu}}} \\{{{\Delta\sigma_{A}^{2}}}}\end{array}\right)\simeq\left(\begin{array}{c c}{{{\sigma_{A}^{2}}}}&{{{0}}} \\{{{0}}}&{{{\sigma_{A}^{4}/n_{e}}}}\end{array}\right)\left(\begin{array}{c}{{{\frac{\partial\ln\overline{w}}{\partial\mu_{z}}}}} \\{{{\frac{\partial\ln\overline{w}}{\partial\sigma_{z}^{2}}}}}\end{array}\right)=\left(\begin{array}{c}{{{\sigma_{A}^{2}\frac{\partial\ln\overline{w}}{\partial\mu_{z}}}}} \\{{{\frac{\sigma_{A}^{4}}{n_{e}}\frac{\partial\ln\overline{w}}{\partial\sigma_{z}^{2}}}}}\end{array}\right) $$
> 
> 
> If the phenotypic distribution is exactly normal, all moments can be expressed in terms of the mean and variance, only gradients measuring selection on the mean and variance will appear, and these equations will be exact. Recalling Equations 24.12a and 24.12b yields
> 
> > **Formula (24.30b)** · `24.30b` · source: `chapter24_block_153` · Gaussian Versus Rare-alleles Approximations
> >
> > $$ \Delta\mu\simeq h^{2}S $$
> 
> 
> and
> 
> > **Formula (24.30c)** · `24.30c` · source: `chapter24_block_153` · Gaussian Versus Rare-alleles Approximations
> >
> > $$ \Delta\sigma_{A}^{2}\simeq\frac{h^{4}}{2n_{e}}\left(\delta(\sigma_{z}^{2})+S^{2}\right) $$
> 
> 
> Thus, the expected change in the mean follows the breeder's equation and short-term changes in variance (from allele-frequency change) are expected to be small when the value of $ n_{e} $ is modest to large. We remind the reader that this analysis ignores the effects of gametic-phase disequilibrium. Because the locus-specific variances, $ \mu_{2,i} $, change as allele frequencies change, predicting changes in variance over several generations, even under these simplifying assumptions, still requires a detailed knowledge about the distribution of allelic effects at individual loci. Thus, while short-term changes in the mean can be predicted without detailed knowledge of the underlying genetics (only $ \sigma_{A}^{2} $ is required), changes in variance cannot (unless an estimate of $ \sum \mu_{2,i} $ or $ n_{e} $ can be obtained). Further, as allele frequencies change, so does $ n_{e} $, and Example 24.4 showed just how unpredictable such changes can be.
> 
> Finally, let's attempt to connect these results for the change in the genic variance, $ \Delta\sigma_A^2 = \Delta\sigma_a^2 $ (as we ignore any disequilibrium), with those obtained under the continuum-of-alleles (COA) approximation (Equation 24.2a). If the within-generation change in the phenotypic variance is $ \delta(\sigma_{z}^{2}) = -\kappa\sigma_{z}^{2} $, then the Gaussian COA approximation for the change in genic variance (Equation 24.2a, ignoring drift by taking $ N_{e} = \infty $) becomes
> 
> > **Formula (24.30d)** · `24.30d` · source: `chapter24_block_155` · Gaussian Versus Rare-alleles Approximations
> >
> > $$ \Delta\sigma_{a}^{2}=-\frac{\kappa h^{2}\sigma_{A}^{2}}{2n_{e}} $$
> 
> 
> By contrast, because $ \kappa h^4\sigma_z^2 = \kappa h^2\sigma_A^2 $, Equation 24.30c yields an allelic-moment approximation of
> 
> > **Formula (24.30e)** · `24.30e` · source: `chapter24_block_156` · Gaussian Versus Rare-alleles Approximations
> >
> > $$ \Delta\sigma_{a}^{2}\simeq\frac{h^{4}}{2n_{e}}\left(\delta(\sigma_{z}^{2})+S^{2}\right)=-\frac{\kappa h^{2}\sigma_{A}^{2}}{2n_{e}}+\frac{h^{4}S^{2}}{2n_{e}} $$
> 
> 
> Thus, the allelic-moment approximation has a positive term lacking in the COA approximation, and hence predicts a smaller change in $ \sigma_a^2 $ when $ \kappa > 0 $ (i.e., when selection reduces the phenotypic variance; Chapter 16). Nick Barton (pers. comm., 2014) suggested that this discrepancy between approximations arises because the selection-gradient approach relies on a weak selection assumption, so terms of order $ S^2 $ are not accurately predicted.


**[示例 Example]**

> **Example 24.10** · ref: `24.10` · source: `chapter24_026.json` · blocks 3–3
>
> Example 24.10. Here we show that $ n_{e} $, as defined in the previous example, is equivalent to Chevalet's (1994) $ n_{e} $ (Equation 24.3). This simply clears up a technical detail, and it can be skipped by the casual reader. Specifically, we need to show that $$ n_{e}=\frac{n}{1+c_{v}^{2}}=\frac{\sigma_{A}^{4}}{4\sum_{i}\mu_{2,i}^{2}} $$ where $ c_v $ is the coefficient of variation in the genic variance contributed by each locus. Because $ \mu_{2,i} $ is the variance of allelic effects at locus $ i $, the genic variance contributed by locus $ i $ is $ 2\mu_{2,i} $ (as there are two alleles per locus). If we recall that the coefficient of variation is defined as the standard deviation divided by the mean
> 
> > **Formula (24.31a)** · `24.31a` · source: `chapter24_block_158` · Gaussian Versus Rare-alleles Approximations
> >
> > $$ 1+c_{v}^{2}=1+\left(\frac{\sigma(2\mu_{2,i})}{E[2\mu_{2,i}]}\right)^{2}=\frac{E[2\mu_{2,i}]^{2}+\sigma^{2}(2\mu_{2,i})}{E[2\mu_{2,i}]^{2}} $$
> 
> 
> Recalling that $ \sigma^2(x) = E[x^2] - E[x]^2 $, we have
> 
> > **Formula (24.31b)** · `24.31b` · source: `chapter24_block_159` · Gaussian Versus Rare-alleles Approximations
> >
> > $$ \sigma^{2}(2\mu_{2,i})=E\left[(2\mu_{2,i})^{2}\right]-E[2\mu_{2,i}]^{2}=\left[\frac{1}{n}\sum_{i=1}^{n}(2\mu_{2,i})^{2}\right]-E[2\mu_{2,i}]^{2} $$
> 
> 
> which rearranges to
> 
> > **Formula (24.31c)** · `24.31c` · source: `chapter24_block_159` · Gaussian Versus Rare-alleles Approximations
> >
> > $$ E[2\mu_{2,i}]^{2}+\sigma^{2}(2\mu_{2,i})=\frac{1}{n}\sum_{i=1}^{n}(2\mu_{2,i})^{2} $$
> 


---

## chapter24_027 · The Infinitesimal Model and Its Extensions: Introduction / Gaussian Versus Rare-alleles Approximations

**[推导 Derivation]**

If we sum the genic variances, $ 2\mu_{2,i} = \sigma_{a_i}^2 $, at each locus we get the total additive genic variance, $ \sigma_a^2 $. Because we are ignoring disequilibrium (i.e., assuming that $ d = 0 $), we have the result that $ \sigma_a^2 = \sigma_A^2 $, or that

> **Formula (24.31d)** · `24.31d` · source: `chapter24_block_160` · Gaussian Versus Rare-alleles Approximations
>
> $$ \sigma_{A}^{2}=\sum_{i=1}^{n}2\mu_{2,i}=n E[2\mu_{2,i}],\quad or that\quad E[2\mu_{2,i}]^{2}=\frac{\sigma_{A}^{4}}{n^{2}} $$


First substituting Equation 24.31b into 24.31a and then using Equation 24.31d yields $$ 1+c_{v}^{2}=\frac{E[2\mu_{2,i}]^{2}+\sigma^{2}(2\mu_{2,i})}{E[2\mu_{2,i}]^{2}}=\frac{(1/n)\sum_{i=1}^{n}(2\mu_{2,i})^{2}}{\sigma_{A}^{4}/n^{2}}=\frac{4n\sum_{i=1}^{n}\mu_{2,i}^{2}}{\sigma_{A}^{4}} $$

Thus, $$ n_{e}=\frac{n}{1+c_{v}^{2}}=\frac{n\sigma_{A}^{4}}{4n\sum_{i=1}^{n}\mu_{2,i}^{2}}=\frac{\sigma_{A}^{4}}{4\sum_{i=1}^{n}\mu_{2,i}^{2}} $$ demonstrating the equivalence of $ n_{e} $ as defined by Equation 24.29b with that given by Equation 24.3.

**[示例 Example]**

> **Example 24.11** · ref: `24.11` · source: `chapter24_027.json` · blocks 3–3
>
> Example 24.11. An important construct used in the analysis of population-genetic models for the maintenance of quantitative-trait variation (Chapter 28) is the rare-alleles model of Barton and Turelli (1987). This assumes that loci are very near fixation, which occurs when the strength of selection is much greater than the strength of mutation. Here we show that under this assumption, allelic moments are proportional to the rare-allele frequencies, meaning that products of moments can be ignored and higher-order moments can be expressed in terms of lower-order ones.
> 
> To see how this approximation arises, consider the simplest case of a biallelic locus $ (i) $, where the common allele has an effect of 0, while the rare allele $ (p_i \simeq 0) $ has an additive effect of $ a_i $. The resulting mean is $ \mu_{1,i} \simeq 2a_i p_i $ and because $ p_i $ is assumed small, quadratic and higher terms in $ p_i $ are ignored in higher moments. For example, the $ (2k) $th moment becomes
> 
> > **Formula (24.32a)** · `24.32a` · source: `chapter24_block_164` · Gaussian Versus Rare-alleles Approximations
> >
> > $$ \mu_{2k,i}=\left(a_{i}-\mu_{1,i}\right)^{2k}p_{i}+\left(0-\mu_{1,i}\right)^{2k}\left(1-p_{i}\right)\simeq a_{i}^{2k}p_{i} $$
> 
> 
> The last step follows because $ \mu_{1,i}^{k} $ is of order $ p_{i}^{k} $ and is ignored (for $ k \geq 2 $). Thus, higher-order moments are related, $$ \mu_{4,i}\simeq a_{i}^{4}p_{i}=a_{i}^{2}\left(a_{i}^{2}p_{i}\right)=\xi_{i}\mu_{2,i} $$
> 
> For now, we set $ \xi_i = a_i^2 $ as this, or a closely related term, appears in the expression for all higher-order moments. Likewise, products of moments are of quadratic- or higher-order in $ p_i $, and thus are ignored. For example, $ \mu_{4,i} - \mu_{2,i}^2 \simeq \mu_{4,i} \approx \xi_i \mu_{2,i} $, as $ \mu_{2,i}^2 $ is of order $ p_i^2 $. Turelli (1984) showed that these moment relationships also hold under his house-of-cards assumption that selection at a locus is much stronger than mutation (and hence most alleles are rare and deleterious), but now with $ \xi_i = \sigma_{\alpha_i}^2 $, the variance in the effects of new mutations at locus $ i $, replacing $ a_i^2 $ (which follows from the fact that $ E[\alpha_i^2] = \sigma_{\alpha_i}^2 + (E[\alpha_i])^2 = \sigma_{\alpha_i}^2 $, as $ E[\alpha_i] = 0 $). Assuming $ n $ equivalent loci (hence, $ \xi = \xi_i $), under the rare-alleles or house-of-cards assumption, the moments matrix, $ \mathbf{M} $, from Equation 24.26c simplifies to
> 
> > **Formula (24.32b)** · `24.32b` · source: `chapter24_block_166` · Gaussian Versus Rare-alleles Approximations
> >
> > $$ \begin{pmatrix}\Delta\mu\\\Delta\sigma_{A}^{2}\\\Delta\mu_{3,G}\end{pmatrix}\simeq\begin{pmatrix}\sigma_{A}^{2}&M_{3}&\xi\sigma_{A}^{2}\\M_{3}&\xi\sigma_{A}^{2}&\xi M_{3}\\\xi\sigma_{A}^{2}&\xi M_{3}&\xi^{2}\sigma_{A}^{2}\end{pmatrix}\begin{pmatrix}\frac{\partial\ln\overline{w}}{\partial\mu}\\\frac{\partial\ln\overline{w}}{\partial\sigma_{z}^{2}}\\\frac{\partial\ln\overline{w}}{\partial\mu_{3,z}}\end{pmatrix} $$
> 
> 
> Notice that $ \Delta\mu_{3,G} = \xi\Delta\mu_{1,G} $, thus directly coupling changes in the mean and skew. If we assume no initial skew (and no selection on skew), Equation 24.32b further reduces to
> 
> > **Formula (24.32c)** · `24.32c` · source: `chapter24_block_167` · Gaussian Versus Rare-alleles Approximations
> >
> > $$ \left(\begin{array}{c}{{{\Delta\mu}}} \\{{{\Delta\sigma_{A}^{2}}}}\end{array}\right)\simeq\left(\begin{array}{c c}{{{\sigma_{A}^{2}}}}&{{{0}}} \\{{{0}}}&{{{\xi\sigma_{A}^{2}}}}\end{array}\right)\left(\begin{array}{c}{{{\frac{\partial\ln\overline{w}}{\partial\mu_{z}}}}} \\{{{\frac{\partial\ln\overline{w}}{\partial\sigma_{z}^{2}}}}}\end{array}\right)=\left(\begin{array}{c}{{{\sigma_{A}^{2}\frac{\partial\ln\overline{w}}{\partial\mu_{z}}}}} \\{{{\xi\sigma_{A}^{2}\frac{\partial\ln\overline{w}}{\partial\sigma_{z}^{2}}}}}\end{array}\right) $$
> 
> 
> Comparing these results with Example 24.9 (the Gaussian approximation) shows that the expected change in the mean (in the absence of skew) is identical in both the rare alleles and Gaussian-approximation models. Under the Gaussian, the change in the variance is given by $ \sigma_A^4 / n_e $ times the fitness gradient with respect to the phenotypic variance, while under the rare alleles model, the quantity $ \xi \sigma_A^2 $ is multiplied by the gradient. Under the rare alleles (and house-of-cards) models, the assumption is that the variance at a locus is small relative to the input from new mutation, implying that $ \xi = \sigma_a^2 \gg \sigma_A^2 / n_e $, and thus $ \xi \sigma_A^2 \gg \sigma_A^4 / n_e $, predicting a much larger change in the variance than under the Gaussian. We will return to this important point in Chapter 28.
> 
> A second critical difference between the rare-alleles and Gaussian-approximation models can be seen from Equation 24.28a. This shows that selection on the variance only influences the response in the mean when there is skew in the breeding value distribution ($ M_3 \neq 0 $), which does not occur under the Gaussian approximation (although selection-induced third-order LD can create it from an initially Gaussian model). Conversely, the rare-alleles model can easily have skew, thus coupling changes in the mean with selection on the variance.
> 
> A final important point is that if the rare-alleles model is a good approximation of reality, then most genetic variation is additive. Even when significant interactions (dominance and epistasis) are present, most genetic variation loads onto the additive component in cases where all but a few of the multilocus genotypes under consideration are rare (Crow 2008; Hill et al. 2008; Maki-Tanila and Hill 2014). One simple way to see this point is to consider a fully dominant, but rare, allele. In this case, the frequency of dominant homozygotes is extremely small, so that the additive effect of the allele is given almost entirely by the genotypic values of the recessive homozygote and the heterozygote, thus loading most of the effects into the additive component. With multilocus genotypes, most combinations of genotypes are so rare that they have little impact on the least-squares regressions that determine additive effects. For example, consider a highly nonlinear relationship between genotypes and trait value. If only a few of the genotypes are common, then most of the regression is determined by just a few points, meaning that a linear regression (and hence additive effects) is likely to account for a significant fraction of the variance.


---

## chapter24_028 · The Infinitesimal Model and Its Extensions: Introduction / Short-term Response Ignoring Allele-frequency Change

The last section considered one class of approximations for the short-term selection response for non-Gaussian distributions of genotypic values, focusing solely on allele-frequency changes. Here we consider the converse approximation: a large enough number of loci (all of small effect) that allele-frequency change (over the time span of interest) can be ignored, with the change in genotypic moments thus attributable entirely to selection-generated disequilibrium. Our discussion departs from the standard infinitesimal model in that we no longer make any Gaussian assumptions.

Turelli and Barton (1990, 1994) extended basic moments analysis (Equation 24.26a) to allow for gametic-phase disequilibrium, by considering both within-locus moment changes due to allele-frequency changes ($ M_{ii} $) and between-locus contributions generated by disequilibrium ($ M_{ij}, i \neq j $). Their 1994 paper is the more general of the two, with the analysis based on the cumulants of the distribution. While the mean, variance, and skew are equivalent to the first three cumulants, cumulants of order four and higher provide much more compact expressions than using moments, due to the additivity of cumulants versus the nonlinear nature of higher-order moments.

**[推导 Derivation]**

In parallel with their moments analysis, Turelli and Barton defined the gradients of selection associated with the ith cumulant of the phenotypic distribution $ K_{z,i} $ by

> **Formula (24.33a)** · `24.33a` · source: `chapter24_block_173` · Short-term Response Ignoring Allele-frequency Change
>
> $$ L_{i}=\frac{\partial\ln(\overline{W})}{\partial K_{z,i}} $$


**[推导 Derivation]**

$ L_{1} $ and $ L_{2} $ correspond to selection on the mean and variance, while $ L_{i} $ for $ i \geq 3 $ represents selection that drives the distribution away from normality (as cumulants of order three and higher are zero for a Gaussian). Turelli and Barton presented general expressions for the change in all cumulants of the distribution. In particular, for a large number of loci, they show that if the majority of selection is on the first four cumulants of the distribution, the changes in the mean and variance are given by

> **Formula (24.33b)** · `24.33b` · source: `chapter24_block_174` · Short-term Response Ignoring Allele-frequency Change
>
> $$ \Delta\mu=\sigma_{A}^{2}L_{1}+K_{G,3}L_{2}+K_{G,4}L_{3}+K_{G,5}L_{4} $$


> **Formula (24.33c)** · `24.33c` · source: `chapter24_block_174` · Short-term Response Ignoring Allele-frequency Change
>
> $$ \begin{aligned}\Delta\sigma_{A}^{2}&=\frac{\sigma_{a}^{2}-\sigma_{A}^{2}}{2}-\frac{\left(\Delta\mu\right)^{2}}{2}+\frac{K_{G,3}}{2}L_{1}+\left(\sigma_{A}^{4}+\frac{K_{G,4}}{2}\right)L_{2}\\&\quad+\left(3\sigma_{A}^{2}K_{G,3}+\frac{K_{G,5}}{2}\right)L_{3}+\left(3K_{G,3}^{2}+4\sigma_{A}^{2}K_{G,4}+\frac{K_{G,6}}{2}\right)L_{4}\end{aligned} $$


where $ K_{G,i} $ denotes the ith cumulant of the genotypic distribution. Note that for Equation 24.33b if some cumulants of order three or higher are nonzero, selection on higher-order cumulants of the phenotypic distribution (i.e., $ L_3 $ or $ L_4 \neq 0 $) also results in a change in the mean. Further, note the appearance of the genic variance $ \sigma_a^2 $ in Equation 24.33c. We are assuming (at least over our time scale) that allele-frequency change can be ignored and hence $ \sigma_a^2 $ is a constant. All changes in the variance (and higher-order moments or cumulants) are thus assumed to arise entirely from selection generated-disequilibrium.

**[示例 Example]**

> **Example 24.12** · ref: `24.12` · source: `chapter24_028.json` · blocks 4–4
>
> Example 24.12. As an application of these results, when phenotypes are normally distributed, Equations 24.12a and 24.12b yield $$ L_{1}=\frac{S}{\sigma_{z}^{2}}\quad and\quad L_{2}=\frac{\delta(\sigma_{z}^{2})+S^{2}}{2\sigma_{z}^{4}}\quad with\quad L_{i}=0\quad for i\geq3 $$
> 
> If the genotypic values also follow a normal distribution, then $ K_{G,i} = 0 $ for $ i \geq 3 $. In this case, Equation 24.33b reduces to $$ \Delta\mu=\sigma_{A}^{2}\frac{S}{\sigma_{z}^{2}}=h^{2}S $$ which recovers the breeder's equation. If we recall that $ \sigma_A^2 = \sigma_a^2 + d $, using the preceding expressions reduces Equation 24.33c to $$ \begin{aligned}\Delta\sigma_{A}^{2}&=\frac{\sigma_{a}^{2}-\sigma_{A}^{2}}{2}-\frac{(\Delta\mu)^{2}}{2}+\frac{0}{2}L_{1}+\left(\sigma_{A}^{4}+\frac{0}{2}\right)L_{2}\\&\quad+\left(3\sigma_{A}^{2}\cdot0+\frac{0}{2}\right)\cdot0+\left(0^{2}+4\sigma_{A}^{2}\cdot0+\frac{0}{2}\right)\cdot0\\&=\frac{\sigma_{a}^{2}-\sigma_{A}^{2}}{2}-\frac{(h^{2}S)^{2}}{2}+\sigma_{A}^{4}\left(\frac{\delta(\sigma_{z}^{2})+S^{2}}{2\sigma_{z}^{4}}\right)\\&=-\frac{d}{2}+\frac{h^{4}}{2}\delta(\sigma_{z}^{2})\end{aligned} $$ which recovers Bulmer's equation. Notice that there is no change in the genic variance, as we assume there are very large number of loci of small effect.
> 
> Turelli and Barton (1994) examined the effects of both strong truncation (directional) selection and strong disruptive selection on Gaussian (infinitesimal and COA) models when the number of loci is large. They found that while strong truncation selection does indeed generate nonzero cumulants of order three and higher (and hence departures from normality), these departures are generally quite small (e.g., Example 24.8). As a result, the breeder's equation with the variance changes predicted from the Bulmer equation (Equation 16.7b) gives quite accurate results for the predicted change in the mean and variance. Hence, the effects of disequilibrium in this case are essentially accounted for by considering only the second-order disequilibrium, which is done in the basic Bulmer model. Barton and Turelli found that the distribution of genotypic values is highly non-normal under strong disruptive selection, with a significant fourth cumulant (kurtosis) being generated by significant fourth-order disequilibrium (generating correlations between groups of four loci). Surprisingly, even in this case the change in variance is still well predicted by the Bulmer equation.


---

## chapter24_029 · The Infinitesimal Model and Its Extensions: Introduction / Effects of Linkage

**[推导 Derivation]**

As might be expected, when these results are generalized to allow for arbitrary linkage (as opposed to the previous expressions, which assume unlinked loci), they become rather complex, even when we assume that there is no allele-frequency change (Turelli and Barton 1990, 1994; Bürger 2000). However, when selection is weak, we can include linkage into an approximation for the asymptotic response for a generalized infinitesimal model that makes no assumptions about the distribution of genotypic values (Turelli and Barton 1990). In particular, Turelli and Barton showed under weak selection that higher-order genotypic moments can be expressed in terms of the initial additive variance in the absence of gametic-phase disequilibrium (the genic variance, $ \sigma_{a}^{2} $, which is assumed to be constant). Using this result, the asymptotic response to selection can be found to be approximately

> **Formula (24.34)** · `24.34` · source: `chapter24_block_178` · Effects of Linkage
>
> $$ \Delta\mu_{z}\simeq\sigma_{a}^{2}\left(\frac{\partial\ln\overline{W}}{\partial\mu_{z}}\right)+\frac{\sigma_{a}^{4}}{r_{H_{2}}}\left(\frac{\partial\ln\overline{w}}{\partial\mu_{z}}\cdot\frac{\partial\ln\overline{w}}{\partial\sigma_{z}^{2}}\right)+\frac{3\sigma_{a}^{6}}{2r_{H_{3}}}\left(\frac{\partial\ln\overline{w}}{\partial\sigma_{z}^{2}}\cdot\frac{\partial\ln\overline{w}}{\partial\mu_{z,3}}\right) $$


where $ r_{H_2} $ and $ r_{H_3} $ are the harmonic mean recombination rates (weighted by the allelic contributions at each locus) between pairs and triplets of loci (Turelli and Barton 1990). At equilibrium, the higher-order genotypic moments are constant, as allele frequencies do not change and, with constant selection, covariances between loci approach equilibrium values. Under these conditions, the expected change in the mean following t generations of selection is just t times Equation 24.34.

**[推导 Derivation]**

Recalling Equations 24.12a and 24.12b (the fitness gradients for the mean and variance of a normally distributed trait), if phenotypes are approximately normal, the asymptotic rate of response further reduces to

> **Formula (24.35)** · `24.35` · source: `chapter24_block_179` · Effects of Linkage
>
> $$ \Delta\mu_{z}\simeq\frac{\sigma_{a}^{2}}{\widetilde{\sigma}_{z}^{2}}\left[S+\sigma_{a}^{2}\frac{\widetilde{\delta}(\sigma_{z}^{2})+S^{2}}{2\widetilde{\sigma}_{z}^{2}}\left(\frac{S}{r_{H_{2}}}+\frac{3\sigma_{a}^{2}}{2r_{H_{3}}}\frac{\partial\ln\overline{w}}{\partial\mu_{3,z}}\right)\right] $$


where $ \widetilde{\sigma}_{z}^{2} $ is the equilibrium phenotypic variance and $ \delta(\sigma_{z}^{2}) $ is the equilibrium within-generation change in phenotypic variance due to selection. This generalizes Bulmer's results (Chapter 16), which correct the breeder's equation for changes in the variance due to pairwise disequilibrium. Equation 24.35 demonstrates that further corrections are required to account for the third- (and higher-order) disequilibrium generated by selection.

---

## chapter24_030 · The Infinitesimal Model and Its Extensions: Introduction / SUMMARY: WHERE DOES ALL THIS MODELING LEAVE US?

Predicting selection response is complicated. Even in the ideal setting where the breeder's equation holds exactly, drift and segregation generate a variance in response about the expected value (Chapter 18). Thus, any specific realization of the selection response will be randomly distributed about its expected value, and hence be less predictable than suggested by the deterministic result for the expected response. Further, even when the initial parent-offspring regression is linear and homoscedastic, there is still a large number of confounding factors for even the single-generation response (Table 13.2). Despite these concerns, short-term prediction of the response to artificial selection is reasonable for many traits (Chapter 18), but far less so for natural selection, in part due to uncertainty as to the target(s) of selection (Chapter 20). In contrast, the prediction of long-term response is an unobtainable goal unless one essentially knows all of the very fine (microscopic) genetic details of a trait, including the distribution of allelic effects and frequencies. As we have seen here and elsewhere (Chapters 5 and 16), selection compromises the simple breeder's equation, $ R = h^2 S $, prediction in two different ways. First, when some of the underlying loci harbor alleles of modest to large effect, this can generate locus-specific selection coefficients sufficiently large to significantly change allele frequencies over short time scales (Equations 5.3 and 5.21). Such changes alter the base-population heritability in ways that are not predictable from observable macroscopic features (such as the initial additive variance). Rather, the dynamics of selection response depend on very fine (microscopic) details of the trait's genetic architecture. A more subtle consequence of allele-frequency change is that it can drive a genotypic distribution away from normality by generating locus-specific skewness and kurtosis. This results in nonlinear and heteroscedastic parent-offspring regressions, and hence potential failure of the breeder's equation, even when correctly updated values of $ h^{2} $ are used.

Dealing with the second consequence of selection, generation of linkage (or, more correctly, gametic-phase) disequilibrium, is often much more manageable than accounting for changes in allele frequencies. Indeed, in the absence of allele-frequency change, changes in LD are temporary, and decay away under random mating following the cessation of selection. Further, unless linkage is very tight or there are genes of very large effect, changes in LD occur on a much faster time scale than do allele-frequency changes. When the trait is controlled by a large number of loci, each of small effect, allele-frequency change is negligible over short time scales. However, selection-induced correlations (even among unlinked loci) change not only the genetic variance (Chapter 16), but can also generate skewness and kurtosis via the creation of third- and fourth-order disequilibrium. While these two latter effects drive a genotypic distribution away from normality, this effect is often modest and does not greatly compromise predictions of response. Further, as we saw in Chapter 16, the Bulmer equation accounts for changes in variances from disequilibrium using easily observed parameters. In the words of Turelli and Barton (1990), “Though our work shows that the distribution of breeding values for an additive polygenic character is unlikely to be precisely Gaussian, we expect that the Gaussian approximation suffices for predicting short-term selection response in all but the most extreme cases.”

Allele-frequency change is the more pernicious feature of selection (relative to disequilibrium), but (for short time scales) it is restricted to traits whose underlying genetic architectures harbor one or more alleles of large effect. Chapters 25 and 26 examine the long-term consequences of allele-frequency change, while the additional role of mutation when directional and stabilizing selection is occurring is examined in Chapters 26 and 28, respectively.

---
