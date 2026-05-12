# Chapter 26 Textbook Mapping

## chapter26_001 · Long-term Response: Introduction

It is almost impossible with any brevity to exemplify the notion of adaptation. Fisher (1934)

Adaptation depends on how the various evolutionary processes shape variation in populations. Barton and Partridge (2000) As we saw in Chapter 18, drift has significant short-term consequences for a population under selection, generating variation around the expected response. Through its role in changing allele frequencies, drift has even more impact over longer time scales. Given that most artificial selection experiments tend to have small effective population sizes, drift is a major factor in the limit of selection response and usually causes a population to plateau at levels below its genetic potential. Another evolutionary force entering into long-term response is mutation. After a sufficient amount of time, new response will be entirely driven by variation that was not present at the start of selection.

This chapter examines the roles of both finite population size and mutation in long-term response, considering how drift interacts with selection to change allele frequencies and how new mutations contribute to selection response. Throughout, we restrict attention to directional selection, deferring the consideration of stabilizing selection until Chapter 28. To distinguish between the contributions of initial variation and new mutation to selection responses, we use long-term response to refer to the gain due to variation in the population at the start of selection. As this initial variation is progressively exhausted, response from this component reaches a selection limit. The actual response, however, can continue well past this limit due to the input from new mutation, eventually (under constant selection) approaching an asymptotic rate of response, wherein the contribution to $ \sigma_A^2 $ from new mutation is balanced by its removal by drift and selection.

Much of the material here builds on results from Chapter 7 on the interaction between selection and drift, and it may prove useful to review that material before proceeding. This chapter is organized as follows. First, we review a few key results from Chapter 7, and then we expand on our brief discussion from Chapter 3 on the subtle (but important) effects of selection in decreasing the effective population size. We then turn to drift and mutation. Historically, long-term response theory focused solely on the effects of drift, and was only augmented later to include the role of mutation. Our discussion follows this same historical development by first considering Robertson's theory for the expected response in the presence of drift using only the initial variation.

Two important results emerge from Robertson’s work. First, he obtained a simple upper bound of $ 2N_{e}R(1) $, twice the effective population size times the response in the first generation, for the selection limit. This simple, and rather general, result is in sharp contrast to the lack of such an analytical bound (based on easily quantified measures) under completely deterministic theory (Chapter 25). Second, there is an optimal selection intensity. If there is a fixed number of measured individuals, as we increase the selection intensity (and hence the short-term response), we do so at the expense of reducing the effective population size, thus reducing long-term response. We conclude our discussion of Robertson’s theory by considering extensions allowing for linkage and various aspects of population structure (such as family selection, drift in the base population, and selection in a subdivided population).

Finally, we consider the effects of new mutations, both in terms of their (generally) minor role at the start of selection (except for rare mutations of large effect), and their

growing role as drift and selection erode the initial variance, which eventually leads to an asymptotic rate of response biased entirely on mutational input. Over sufficiently long time scales, response to continual directional selection is due to the fixation of a series of new mutations, an adaptive walk, which is examined in Chapter 27.

---

## chapter26_002 · Long-term Response: Introduction / THE POPULATION GENETICS OF SELECTION AND DRIFT

**[推导 Derivation]**

In Chapter 7 we examined the interaction of selection and drift at a single locus, and we briefly review a few of the key results here. If the population size is finite, a favorable allele may become lost, and hence our interest is in u, the probability that an allele is fixed. In an infinite population, u = 1 for an allele favored by selection (provided it is not overdominant). In a finite population, u < 1, and its particular value depends on (among other things) its initial frequency, $ p_0 $, and the effective population size, $ N_e $. Let $ u(p_0) $ denote the probability that an allele starting at an initial frequency of $ p_0 $ becomes fixed. Recall from Chapter 2 that the fixation probability of a neutral allele depends only on its initial frequency, with

> **Formula (26.1)** · `26.1` · source: `chapter26_block_009` · THE POPULATION GENETICS OF SELECTION AND DRIFT
>
> $$ u(p_{0})=p_{0} $$


**[推导 Derivation]**

This independence from population size is not the case for an allele under selection. For additive selection (with fitnesses of 0: s: 2s)

> **Formula (26.2a)** · `26.2a` · source: `chapter26_block_010` · THE POPULATION GENETICS OF SELECTION AND DRIFT
>
> $$ u(p_{0})\simeq\frac{1-e^{-4N_{e}sp_{0}}}{1-e^{-4N_{e}s}} $$


> **Formula (26.2b)** · `26.2b` · source: `chapter26_block_010` · THE POPULATION GENETICS OF SELECTION AND DRIFT
>
> $$ \simeq p_{0}+2N_{e}sp_{0}(1-p_{0})\quad when\quad2N_{e}|s|\leq1 $$


**[推导 Derivation]**

Equation 26.2a, from Kimura (1957), is derived using diffusion theory in Appendix 1, and values of $ u(p_0) $ are plotted in Figure 26.1. Equation 26.2b, which is from Robertson (1960a), uses the approximations $ e^{-x} \simeq 1 - x + x^2/2 $ and $ (1 - x)^{-1} \simeq 1 + x $ (both for $ |x| \ll 1 $) to simplify Kimura's result under weak selection. Equation 26.2b shows that

> **Formula (26.2c)** · `26.2c` · source: `chapter26_block_011` · THE POPULATION GENETICS OF SELECTION AND DRIFT
>
> $$ u(p_{0})\simeq p_{0}\qquad if\qquad2N_{e}|s|\ll1 $$


Comparing this result to Equation 26.1 shows that an allele whose selection coefficient satisfies $ 2N_e | s| \ll 1 $ behaves as if it were neutral over all allele frequencies, and it is called effectively neutral to reflect this fact. Equations 7.18–7.20 present corresponding expressions for the probability of fixation when dominance is present.

Even when an allele is strongly selected ($ 4N_{e}s \gg 1 $), drift is important when its frequency is near zero or one. Taylor-expanding the numerator of Equation 26.2a yields $$ 1-e^{-4N_{e}sp_{0}}\simeq1-\left(1-4N_{e}sp_{0}\right)=4N_{e}sp_{0},\quad or\quad2s\frac{N_{e}}{N}\quad for\quad p_{0}=\frac{1}{2N} $$

Hence, the probability of fixation starting with a single copy, $ p_0 = 1/(2N) $, of an advantageous allele is approximately $ 2s $ ($ N_e/N $) when $ 4N_e s \gg 1 $, implying that a favorable allele introduced as a single copy is usually lost by drift. Conversely, the fixation of a favored allele becomes almost certain as its frequency becomes sufficiently large. Equation 26.2a shows that if $ p_0 \geq 1/(2N_e s) $, the probability of fixation exceeds 0.86, while if $ p_0 \geq 1/(N_e s) $, the probability of fixation exceeds 0.98. Thus, if a favorable allele initially increases by drift, it can reach a threshold frequency above which deterministic selection dominates, which rapidly increases its frequency toward 1.0. As it approaches a frequency of 1.0, drift will again dominate, fixing the allele much more rapidly than expected under deterministic selection (Example 8.1).

Finally, recall the Cohan effect (Example 7.4), which states that uniform selection can result in greater between-replicate divergence than drift. This occurs because the between-line divergence is maximized when the fixation probability of an allele is 0.5. Given that the fixation probability under neutrality is $ p_0 $, selection results in greater divergence than it does under neutrality when $ u(p_0)[1 - u(p_0)] > p_0[1 - p_0] $. Figure 7.3 shows that the conditions for this to occur are not very restrictive under additive selection. As is discussed below, the Cohan effect has implications when crossing and then reselecting replicate lines.

---

## chapter26_003 · Long-term Response: Introduction / Fixation Probabilities for Alleles at a QTL

**[推导 Derivation]**

We can translate the above results (and those from Chapter 7) for the fixation probability of an allele given its additive (s) and dominance (h) effects on fitness into the fixation probability for a favorable QTL allele as a function of its additive (a) and dominance (k) effects on the trait under selection. When the locus has only a small effect on the character, selection coefficients of $ s = \bar{i}a/\sigma_z $ and $ h = k $ (Equation 25.4) can be used in conjunction with Equation 7.18a to obtain fixation probabilities. If the allele displays no dominance in the character ($ k = 0 $), previous results imply that the probability of fixation exceeds 0.86 when $ N_{es}p_o \geq 1/2 $, or

> **Formula (26.3a)** · `26.3a` · source: `chapter26_block_016` · Fixation Probabilities for Alleles at a QTL
>
> $$ \begin{align*}N_e\left(\overline{\imath}\frac{a}{\sigma_z}\right)p_0\geq1/2\end{align*} $$


**[推导 Derivation]**

For the fixation probability to exceed 0.86, the starting allele frequency must exceed

> **Formula (26.3b)** · `26.3b` · source: `chapter26_block_017` · Fixation Probabilities for Alleles at a QTL
>
> $$ p_{0}>\frac{\sigma_{z}}{a2N_{e}\bar{\tau}} $$


**[推导 Derivation]**

The fixation probability exceeds 98% when $ N_{e}sp_{0} > 1 $, which corresponds to a critical allele frequency of twice that given by Equation 26.3b, namely,

> **Formula (26.4)** · `26.4` · source: `chapter26_block_018` · Fixation Probabilities for Alleles at a QTL
>
> $$ p_{0}>\frac{\sigma_{z}}{a N_{e}\bar{\tau}} $$


Note that if the product of initial allele frequency and its standardized effect, $ p_0 | a | / \sigma_z $, is sufficiently small, drift will dominate even if selection ($ \bar{\tau} $) on the character is strong. With small values of $ N_e \bar{\tau} $, only alleles of large effect or at moderate to high frequency are likely to be fixed by selection. As $ N_e \bar{\tau} $ increases, favored alleles with smaller effects, or at lower frequencies, are increasingly more likely to become fixed. As a technical aside, the careful reader might recall from Chapter 14 that sampling causes fluctuations in $ \bar{\imath} $ in a finite population. This additional complication need not overly concern us, as Hill (1969a, 1985) and Kojima (1961) showed that the error introduced by assuming a constant $ \bar{\imath} $ is small.

---

## chapter26_004 · Long-term Response: Introduction / Increased Recombination Rates Following Selection

We previously discussed the Hill-Robertson effect (Chapters 3, 7, and 8), wherein the effective population size is reduced in regions linked to a selected site, and in Chapter 4 we examined the evolution of the recombination rate. Otto and Barton (1997) showed that alleles at modifier loci that increase the recombination rate also increase the probability of fixation of favored alleles at selected loci linked to the modifier (also see Felsenstein 1974; Felsenstein and Yokoyama 1976). This can result in recombination modifiers hitchhiking along to fixation with the favored mutations. Such modifiers are favored because under low recombination, the effective selection coefficient on a particular mutation affecting a character depends on the selection coefficients at linked loci (e.g., Equation 7.42). Thus, the fate of a particular mutant is highly dependent upon the background in which it arose. As recombination increases, the fate of a mutation becomes increasingly uncoupled from the fate of its initial background. Rice and Chippendale (2001) experimentally demonstrated this by showing that the fixation probability of a mutation favored by artificial selection (white eye color in Drosophila) increased with the recombination rate. Otto and Barton's theory makes the prediction that recombination rates may increase in selected populations relative to unselected controls, which is indeed observed in some experiments.

**[示例 Example]**

> **Example 26.1** · ref: `26.1` · source: `chapter26_004.json` · blocks 1–1
>
> Example 26.1. Korol and Iliadi (1994) subjected a Drosophila melanogaster population to divergent selection for positive and negative geotaxis (an increased tendency to fly up and down, respectively). Recombination frequencies were scored on the unselected controls and the positively $ (geo^{+}) $ and negatively $ (geo^{-}) $ selected lines, with chromosomes II, III, and X scored after 36, 40, and 44 generations of selection. Over the scored regions (roughly 220 cM in the control), the map distance in the geo $ ^{+} $ line increased by a total of 78 cM (35%), while the geo $ ^{-} $ line increased by 66 cM (30%). Presumably, these increases resulted from the increased probability of fixation of favorable mutations linked to modifiers increasing recombination frequencies. Other experiments in Drosophila also showed an increase in the recombination frequency following either directional or stabilizing selection (e.g., Thoday et al. 1964; Flexon and Rodell 1982; Zhuchenko et al. 1985; Rodell et al. 2004). A potentially related observation is that by Morran et al. (2009), who found that a collection of wild-type populations of the nematode C. elegans that were exposed to a bacterial pathogen had elevated rates of outcrossing compared with a set of controls that were not exposed. One concern with any such list of positive results is ascertainment bias, reporting a positive finding when it is present, but not when it is absent, thus inflating its apparent importance.


---

## chapter26_005 · Long-term Response: Introduction / THE EFFECT OF SELECTION ON EFFECTIVE POPULATION SIZE

The simple act of selecting on a trait reduces the effective size, $ N_e $, of a population below its actual size, N. Part of this is obvious, in that artificial selection proceeds by first choosing M (random) individuals to score and then selecting a fraction p of these to reproduce. Hence, $ N_e \leq pM < N $, with stronger selection (smaller p) increasing the reduction in effective population size. As introduced in Chapter 3, there is a second, and much more subtle, effect that further reduces $ N_e $ for a selected population below that of an unselected control population with the same number of parents (i.e., $ N_e < pM $). This additional reduction arises because selection inflates the variance in offspring number (more offspring are chosen from favorable families), reducing $ N_e $. The initial realization of this phenomenon is often attributed to Morley (1954), who noted in sheep flocks exposed to selection that “the genetically superior individuals will tend to be most inbred," a result of a smaller (inbreeding) effective population size in the selected population relative to a control population of the same census size. However, Lush (1946) also very clearly understood this process, noting the "correlation between the fates of relatives" under selection and how this is expected to inflate the variance in offspring number.

While the effective size of a population under artificial selection can be retrospectively computed from either pedigree information or from the sampling variance in marker-allele frequencies (Chapter 4), predicting $ N_{e} $ in advance is more difficult. Its exact value depends on a variety of assumptions about both the family and population structure, and also on the underlying genetic model (the infinitesimal model is typically assumed). Theoretical investigations of the effects of selection on $ N_{e} $ were initiated by Robertson (1961), who presented simple approximations for both the single generation change and the asymptotic change following many generations of selection (Equations 3.29a and 3.29c).

Two different approaches have been used to examine the reduction in $ N_{e} $ from selection on unlinked loci. The first computes the expected variance in gene frequency for a neutral locus that is unlinked to any locus under selection (Robertson 1961; Nei and Murata 1966; Caballero 1994; Santiago and Caballero 1995), while the second computes the rate of inbreeding from the number of ancestors (Burrows 1984a, 1984b; Woolliams 1989; Verrier et al. 1990; Wray and Thompson 1990; Wray et al. 1990, 1994; Woolliams et al. 1993). The former corresponds to the variance effective population size, and the latter to the inbreeding effective population size. Strictly speaking, results based on diffusion theory require the usage of the variance effective size (as diffusion approximations use the sample variance in allele frequency). However, as discussed in Chapter 3, inbreeding and variance effective population sizes are usually equivalent unless the population size is changing over time. While all these treatments of the impact of selection on $ N_{e} $ consider the effective population size experienced by a neutral locus unlinked to loci influencing the traits under selection, the results should be very similar for selected loci under the infinitesimal model, as in this case drift (rather than selection) provides the major impetus for allele-frequency change.

---

## chapter26_006 · Long-term Response: Introduction / The Expected Reduction in $ N_{e} $ from Directional Selection

**[推导 Derivation]**

Before proceeding, we will briefly review some results from Chapter 3. In the following discussion, N refers to the number of parents, pM. One of the assumptions of an ideal population (where the actual size, N, equals the effective size, $ N_e $) is that all parents have an equal chance of contributing offspring. Equation 3.4 shows that variance, $ \sigma_k^2 $, in the number of offspring contributed by an individual reduces $ N_e $, as $ N_e = (N - 1/2)/(\sigma_k^2/4 + 1/2) $. If the number of offspring per parent follows a Poisson distribution, then $ \sigma_k^2 = 2 $ and $ N_e = N - 1/2 \simeq N $. However, if some parents contribute a disproportionate number of offspring, then $ \sigma_k^2 > 2 $ and $ N_e < N $. The more disproportionate the contribution, the larger is the offspring variance and the smaller is $ N_e $. As in Chapter 3, we use $ \sigma_k^2 $ to denote variation in offspring number for entirely nonheritable reasons. Here, the children of a parent contributing an excessive number of offspring are themselves no more likely to contribute an excessive number. But with selection on a heritable trait, this will no longer be true. A selected parent is likely to have offspring with favorable trait values that then disproportionately contribute to the next generation. Following Chapter 3, we separate these two sources of variance in offspring number, letting $ \sigma_k^2 $ refer to the variation in an unselected population and $ \sigma_w^2 $ to the additional among-family genetic variance in relative fitness (due to differential contribution from families with more favorable trait values). Because each family is assumed (on average) to contribute two offspring (in a population maintained at a stable size), the additional variance from selection is $ 2^2 \sigma_w^2 $, yielding an effective population size after a generation of selection of

> **Formula (26.5)** · `26.5` · source: `chapter26_block_025` · The Expected Reduction in $ N_{e} $ from Directional Selection
>
> $$ N_{e}=\frac{4N}{\sigma_{k}^{2}+2+4\sigma_{w}^{2}} $$


**[推导 Derivation]**

Assuming $ \sigma_{k}^{2}=2 $ gives

> **Formula (26.6a)** · `26.6a` · source: `chapter26_block_026` · The Expected Reduction in $ N_{e} $ from Directional Selection
>
> $$ N_{e}=\frac{N}{1+\sigma_{w}^{2}} $$


a result from Robertson (1961). For truncation selection, Robertson (1961) and Milkman (1978) showed that $ \sigma_w^2 \simeq \bar{\imath}^2 t_{FS} $, where $ t_{FS} = \text{Cov}(FS)/\sigma_z^2 $ is the intraclass correlation of full sibs (LW Equation 17.3). Thus, the reduction in effective population size after a single generation of selection on unlinked loci becomes

> **Formula (26.6b)** · `26.6b` · source: `chapter26_block_026` · The Expected Reduction in $ N_{e} $ from Directional Selection
>
> $$ N_{e}=\frac{N}{1+\bar{\tau}^{2}t_{FS}} $$


**[推导 Derivation]**

There are two complications to consider when moving from this simple result for a single generation to the reduction in $ N_e $ over multiple generations of selection. First, as selection proceeds, genetic variances change, which in turn changes $ t_{FS} $. The second complication, which was briefly noted in Chapter 3, is that continued selection has a cumulative effect. Robertson (1961) approximated this effect by noting that only half of the association between a neutral locus and unlinked loci under selection persists in each generation, yielding the among-family variance after $ \tau $ generations of selection as $$ (1+1/2+1/4+\cdots+1/2^{\tau})^{2}\sigma_{w}^{2}=Q_{\tau}^{2}\sigma_{w}^{2} $$ where $ Q_{\tau} $ is the cumulative effect of $ \tau $ generations of selection. Equation 26.6a thus becomes

> **Formula (26.6c)** · `26.6c` · source: `chapter26_block_027` · The Expected Reduction in $ N_{e} $ from Directional Selection
>
> $$ N_{e,\tau}=\frac{N}{1+Q_{\tau}^{2}\sigma_{w}^{2}}=\frac{N}{1+Q_{\tau}^{2}\bar{i}^{2}t_{FS}} $$


$ Q_{\tau} $ approaches a limiting value of $ Q = 2 $, which yields Equation 3.29c, Robertson's long-term effective population size of $ N/(1+4\sigma_{w}^2) $. As noted in Chapter 3, this result is approximate for several reason, most importantly because selection also reduces genetic variation, resulting in less than half of the value from the previous generation being passed along.

**[推导 Derivation]**

A more complete treatment was given by Santiago and Caballero (1995), who obtained a general expression for $ N_{e} $ under selection that allows for nonrandom mating. Assuming random mating, their expression for $ N_{e} $ after $ \tau $ generations of selection is

> **Formula (26.6d)** · `26.6d` · source: `chapter26_block_029` · The Expected Reduction in $ N_{e} $ from Directional Selection
>
> $$ \frac{N_{e,\tau}}{N}=\left[\frac{1-\gamma}{2}+\left(\frac{\sigma_{k}^{2}}{4}+Q_{*\tau}^{2}\sigma_{w}^{2}\right)(1+\gamma)\right]^{-1} $$


where $ \gamma = -1/(N - 1) $ is a measure of the departure from Hardy-Weinberg due to finite population size (we generally assume that $ \gamma \simeq 0 $), and $ Q_{\star\star} $ (given below; see Equation 26.9a) is a generalization of Robertson's $ Q_{\tau} $. For a single generation of selection, $ Q_{\star1} = 1 $, implying that $ \sigma_w^2 $ is the effect of selection in the current generation, while $ (Q_{\star\tau} - 1)\sigma_w^2 $ is the cumulative effect of selection in previous generations. As will be shown, $ Q_{\star\tau} $ is a function of the selection intensity and heritability. Assuming that $ N $ is large (so $ \alpha \simeq 0 $) and a Poisson distribution of offspring in the absence of selection ($ \sigma_k^2 = 2 $), Equation 26.6d reduces to Equation 26.6c, but with $ Q_{\star\tau} $ replacing $ Q_\tau $. We are still, however, left with two complications—obtaining the value of $ t_{FS} $, and finding $ Q_{\star\tau} $—which we address in turn.

**[推导 Derivation]**

Under the infinitesimal model, all of the selection-induced change in genetic variance is due to gametic-phase disequilibrium (Chapters 16 and 24). In Chapter 16 we showed that $ \sigma_A^2 = \sigma_a^2 + d $, where $ \sigma_a^2 $ (the additive genetic variance) is the additive genetic variance in the absence of disequilibrium and $ d $ is the disequilibrium contribution. Under the infinitesimal model, the within- and among-family contributions to the additive genetic variance differ, as (for unlinked loci) the within-family contribution ($ \sigma_a^2/2 $) is not influenced by disequilibrium, while the among-family variance ($ \sigma_a^2/2 + d $) is (Chapter 16). Assuming the absence of both dominance and shared sib environmental effects, the intraclass correlation becomes

> **Formula (26.7a)** · `26.7a` · source: `chapter26_block_030` · The Expected Reduction in $ N_{e} $ from Directional Selection
>
> $$ t_{FS}=\frac{\sigma_{a}^{2}/2+d}{\sigma_{A}^{2}+\sigma_{E}^{2}}=\frac{\sigma_{a}^{2}/2+d}{\sigma_{a}^{2}+d+\sigma_{E}^{2}}=\frac{h_{0}^{2}/2+d/\sigma_{z(0)}^{2}}{1+d/\sigma_{z(0)}^{2}} $$


where $ h_0^2 $ and $ \sigma_z(0) = \sigma_a^2 + \sigma_E^2 $ are, respectively, the heritability and phenotypic variance in the unselected base population ($ d = 0 $). Increasing either $ \bar{i}^2 $ or $ h^2 $ increases $ \sigma_w^2 = \bar{i}^2 t_{FS} $, which in turn decreases $ N_e $. Dominance variance does not change under the infinitesimal model (Chapter 16), so when it, or a common-family effect, occur, both appear as constants in the numerator and denominator of Equation 26.7a.

**[推导 Derivation]**

We now have all of the results needed to compute an improved expression for the single-generation reduction in $ N_e $. Expressing the fraction of phenotypic variance in the selected parents as $ \sigma_z^2/\sigma_z^2 = (1 - \kappa) $, Equation 16.7a yields $ d(1)/\sigma_z^2 = -\kappa h_0^4/2 $ (Equation 16.11a gives $ \kappa $ as a function of $ \bar{\imath} $). Substituting this value for $ d(1)/\sigma_z^2 $ into Equation 26.7a,

> **Formula (26.7b)** · `26.7b` · source: `chapter26_block_031` · The Expected Reduction in $ N_{e} $ from Directional Selection
>
> $$ t_{FS}(1)=\frac{h_{0}^{2}(1-\kappa h_{0}^{2})/2}{1-\kappa h_{0}^{4}/2} $$


**[推导 Derivation]**

Recalling that $ Q_{*1} = 1 $, Equation 26.6d (assuming $ \gamma = 0 $, $ \sigma_k^2 = 2 $) yields a reduction in $ N_e $ from a single generation of selection of

> **Formula (26.8)** · `26.8` · source: `chapter26_block_032` · The Expected Reduction in $ N_{e} $ from Directional Selection
>
> $$ N_{e,1}\simeq N\left(1+\bar{\imath}^{2}\frac{(h_{0}^{2}/2)(1-\kappa h_{0}^{2})}{1-\kappa h_{0}^{4}}\right)^{-1} $$


This result was first obtained by Robertson (1961), who did not include the $ (1-\kappa h_0^4/2) $ term, which was subsequently added by Wray and Thompson (1990).

**[推导 Derivation]**

Turning to $ Q_{*\tau} $, the cumulative effect of past selection, Santiago and Caballero (1995) showed that

> **Formula (26.9a)** · `26.9a` · source: `chapter26_block_034` · The Expected Reduction in $ N_{e} $ from Directional Selection
>
> $$ Q_{*\tau}=1+\frac{G}{2}(1+\rho)+\cdots+\left[\frac{G}{2}(1+\rho)\right]^{\tau}=\sum_{i=0}^{\tau}\left[\frac{G}{2}(1+\rho)\right]^{i} $$


where $G$ is the fraction of genetic variance remaining after selection and $\rho$ is the correlation between the selective values of mates ($\rho = -1/[N - 1]$ under random mating). If ($1 - \kappa$) is the fraction of phenotypic variance after selection, then $G = 1 - \kappa h^2$ is the fraction of additive variance (Chapter 16). As with $t_{FS}$, $G$ (and hence $Q_{*\tau}$) depends on a parameter ($h^2$) that changes under selection. However, recall from Chapter 16 that, under the infinitesimal model, $h^2$ quickly reaches its equilibrium value under directional selection (in roughly two or three generations). Thus, we typically use $G = 1 - \kappa \widehat{h}^2$, a function of the equilibrium heritability under the effects of selection and disequilibrium alone. In the limit ($\tau \to \infty$), the sum in Equation 26.9a converges to

> **Formula (26.9b)** · `26.9b` · source: `chapter26_block_034` · The Expected Reduction in $ N_{e} $ from Directional Selection
>
> $$ \widetilde{Q}_{*}=\frac{2}{2-G(1+\rho)}\simeq\frac{2}{1+\kappa\widehat{h}^{2}}\quad when\rho\simeq0 $$


---

## chapter26_007 · Long-term Response: Introduction / The Expected Reduction in $ N_{e} $ from Directional Selection

Robertson assumed a limiting value of $Q = 2$, but Equation 26.9b shows that this is an overestimate, which results in an underestimation of $N_e$. Substitution of Equation 26.9b into Equation 26.6c recovers Equation 3.29b (with the latter expressed in terms of $L = 1 - G$, where $L = \kappa h^2$ is the fractional loss of additive variance).

The general prediction that effective population size decreases in selected populations has been examined in a number of Drosophila experiments, where inbreeding is estimated directly from parental pedigrees. This prediction has generally been confirmed, with a reasonable fit to Robertson's theory (McBride and Robertson 1963; Jones 1969a, 1969b; López-Fanjul 1989). As expected from Equation 26.8, $ N_e $ is lowest in lines showing the greatest response to selection, as these lines have the highest realized heritabilities. Gallego and López-Fanjul (1983) tested a second prediction using selection on sternopleural bristles: because the reduction in $ N_e $ occurs from among-family selection (inflating the among-family variance, $ \sigma_k^2 $), no reduction in $ N_e $ is expected under within-family (full-sib) selection (Chapter 21). In accordance with theory, no reduction was observed. As reviewed in Chapter 25, reproductive fitness often declines during long-term selection experiments. This can result in a further increase in the variance in fitness among individuals, which in turn further increases the variance in offspring number (as the latter is a measure of fitness). This increased variance can significantly decrease the effective population size below that predicted by Equation 26.8, which incorporates only the variance effects associated with artificial selection. Yoo (1980c) found that differences in fertility were more important in reducing effective population size than the effects of artificial selection during a long-term selection experiment for increased Drosophila bristle number.

**[示例 Example]**

> **Example 26.2** · ref: `26.2` · source: `chapter26_007.json` · blocks 2–2
>
> Example 26.2. Consider directional truncation selection on a normally distributed character in which the uppermost 20% of the population (p = 0.2) is saved. From Example 16.3, this yields a selection intensity of $ \bar{\tau} = 1.40 $ and a reduction in variance of $ \kappa = 0.781 $. If we assume initial (before selection) values of $ h_0^2 = 0.5 $ and $ \sigma_z^2(0) = 100 $, Example 16.2 yields (under the infinitesimal model) equilibrium values of $ \widehat{d} = -12.54 $ and $ \widehat{h}^2 = 0.428 $. Hence $$ G=1-\kappa\widehat{h}^{2}=1-0.781\cdot0.428=0.665 $$ Because we are assuming no dominance or common-family effects, the initial value of $ t_{FS} $ in the base population is $ h_{0}^{2}/2 = 0.25 $, while its equilibrium value becomes $$ \widehat{t}_{FS}=\frac{h_{0}^{2}/2+\widehat{d}/\sigma_{z(0)}^{2}}{1+\widehat{d}/\sigma_{z(0)}^{2}}=\frac{(0.5/2)-(12.54/100)}{1-(12.54/100)}=0.142 $$
> 
> Hence, $ \sigma_w^2 = \bar{i}^2 \cdot \widehat{t}_{FS} = 1.4^2 \cdot 0.142 = 0.279 $. Assuming $ \rho = -1/(N - 1) \simeq 0 $, Equation 26.9b yields $$ \widetilde{Q}_{*}=\frac{2}{2-G}=\frac{2}{2-0.665}=1.498 $$
> 
> Equation 26.6c yields an equilibrium effective population size of $$ N_{e}=\frac{N}{1+\widetilde{Q}_{*}^{2}\sigma_{w}^{2}}=\frac{N}{1+1.498^{2}\cdot0.279}=0.615N $$


---

## chapter26_008 · Long-term Response: Introduction / DRIFT AND LONG-TERM SELECTION RESPONSE

Recall that in our distinction between long-term and asymptotic response, the former is attributable to the existing variation at the start of selection, while the latter is the expected eventual rate of response due to the input of new mutation. When the effective population size is small, essentially all of the observed response is due to the initial variation, with the population reaching an apparent limit until the appearance of new mutations allows for further response. In larger populations, these two components of response become more difficult to separate, and no limit may be observed when in fact all of the initial variation has been exhausted. Much of the initial theory of long-term response ignored mutation, and we examine this drift-only version first, as it provides a good description of how a population exhausts its initial variation.

---

## chapter26_009 · Long-term Response: Introduction / Basic Theory

**[推导 Derivation]**

We expect the response to selection in very small populations to be significantly influenced by drift, showing less total response than in larger populations starting with the same initial genetic variance. A fairly extensive theory examining the effects of drift on long-term response (the utilization of the initial genetic variation) has been developed, starting with the extremely influential paper of Robertson (1960a). Most of this theory is based on summing over single-locus results, which we adhere to unless stated otherwise (this assumes that epistasis and linkage effects can be ignored). As before, we first consider a single diallelic locus (indexed by i) where the genotypes $ aa:Aa:AA $ have genotypic values (for the character under selection) of $ 0:a(1+k):2a $. Let $ p_t $ denote the frequency of $ A $ at this locus in generation $ t $, $ \Delta_i(t) $ be the contribution to total response from this locus in generation $ t $, and $ u_i(p_0) $ be the probability that $ A $ is ultimately fixed at this locus, provided it starts at a frequency of $ p_0 $. The total response is obtained by summing over all loci, $ R(t) = \sum_i \Delta_i(t) $. Under drift, both $ p_t $ and $ \Delta_i(t) $ are random variables and (assuming that the genotypes are in Hardy-Weinberg proportions) are related by

> **Formula (26.10a)** · `26.10a` · source: `chapter26_block_041` · Basic Theory
>
> $$ \begin{aligned}\Delta_{i}(t)&=m_{i}(p_{t})-m_{i}(p_{0})\\&=2a\Bigg[p_{t}-p_{0}+k\Bigg(p_{t}(1-p_{t})-p_{0}(1-p_{0})\Bigg)\Bigg]\end{aligned} $$


where $ m_{i}(p) $, the expected contribution to the trait from locus i when the frequency of A is p, is given by Equation 25.1a. The expected contribution (at generation t) from this locus is

> **Formula (26.10b)** · `26.10b` · source: `chapter26_block_041` · Basic Theory
>
> $$ E[\Delta_{i}(t)]=2a\left[E(p_{t})-p_{0}+k\Biggl(E[p_{t}(1-p_{t})]-p_{0}(1-p_{0})\Biggr)\right] $$


Because A is ultimately either fixed $ (p_{\infty}=1) $ or lost $ (p_{\infty}=0) $, $ E(p_{t}) $ converges to $$ 1\cdot u_{i}(p_{0})+0\cdot\left[1-u_{i}(p_{0})\right]=u_{i}(p_{0}) $$ while $ E[p_t(1-p_t)] $ converges to zero. The limiting expected contribution from locus i becomes

> **Formula (26.11a)** · `26.11a` · source: `chapter26_block_041` · Basic Theory
>
> $$ E[\Delta_{i}(\infty)]=2a\bigg[u_{i}(p_{0})-p_{0}-k\bigg(p_{0}(1-p_{0})\bigg)\bigg] $$


**[推导 Derivation]**

Two cases of special interest are when A is additive $ (k = 0) $, yielding

> **Formula (26.11b)** · `26.11b` · source: `chapter26_block_042` · Basic Theory
>
> $$ E[\Delta_{i}(\infty)]=2a\left[u_{i}(p_{0})-p_{0}\right] $$


and when A is recessive $ (k = -1) $, in which case

> **Formula (26.11c)** · `26.11c` · source: `chapter26_block_042` · Basic Theory
>
> $$ E[\Delta_{i}(\infty)]=2a\left[u_{i}(p_{0})-p_{0}^{2}\right] $$


**[推导 Derivation]**

The variance (and indeed all higher moments) of the total response at the selection limit are easily computed, as, regardless of the value of $ k $, $ \Delta_{i}(\infty) $ takes on only two values,

> **Formula (26.12)** · `26.12` · source: `chapter26_block_043` · Basic Theory
>
> $$ \begin{aligned}\Delta_{i}(\infty)&=2a-m_{i}(p_{0})\quad with probability u_{i}(p_{0})\\&=\quad0-m_{i}(p_{0})\quad with probability1-u_{i}(p_{0})\end{aligned} $$


**[推导 Derivation]**

In particular, the variance in the contribution from this locus over replicate selected lines is

> **Formula (26.13a)** · `26.13a` · source: `chapter26_block_044` · Basic Theory
>
> $$ \begin{aligned}\sigma^{2}\left[\Delta_{i}(\infty)\right]&=E\left[\Delta_{i}^{2}(\infty)\right]-\left(E\left[\Delta_{i}(\infty)\right]\right)^{2}\\&=4a^{2}u_{i}(p_{0})\left[1-u_{i}(p_{0})\right]\end{aligned} $$


With weak selection, $ u_i(p_0) \simeq p_0 $ (i.e., the allelic dynamics are largely governed by drift), implying

> **Formula (26.13b)** · `26.13b` · source: `chapter26_block_044` · Basic Theory
>
> $$ \sigma^{2}\left[R(\infty)\right]\simeq4\sum a^{2}p_{0}(1-p_{0}) $$


which is twice the initial additive-genetic variation (assuming that all loci are additive), and also is the expected among-line divergence under pure drift (Chapter 11). Under sufficiently strong selection, almost all favorable alleles will be fixed and the variance will be close to zero, as $ u_i(p_0) \simeq 1 $. When selection is moderate to weak, loci for which $ u_i(p_0)[1 - u_i(p_0)] > p_0(1 - p_0) $ show a Cohan effect. If such loci are sufficiently frequent, selection increases the among-line variance relative to drift. This requires both weak selection and that most favored alleles be rare. The variance in response at the selection limit was considered in more detail by Hill and Rasbash (1986), Zeng and Cockerham (1990), and Zhang and Hill (2005a).

The variance in the selection limit across replicate lines has a direct bearing on whether further response can occur by crossing plateaued lines and then reselecting. If drift has played a significant role in the selection response, a line formed by crossing replicate plateaued lines should show further response to selection, as each line should be fixed for a considerable number of unfavorable alleles. In particular, with weakly selected loci, the Cohan effect can inflate the among-replicate variance over that expected under drift, increasing the potential for additional response when crossing weakly selected lines over that expected from crossing lines generated by drift alone.

Replicate lines at their selection limits usually show considerable genetic differences (reviewed by Cohan 1984a, 1984b). For example, Scowcroft (1965) used chromosomal analysis to show that three replicate Drosophila lines selected for increased scutellar bristles differed considerably in the amount of response attributable to each chromosome and the nature of interactions between chromosomes. Synthetic lines formed by crossing either replicate plateaued lines (Frankham et al. 1968b; Eisen 1975; Frankham 1980) or unrelated plateaued lines (Falconer and King 1953; Roberts 1967) generally respond to selection.

An interesting exception was revealed by Gallego and López-Fanjul (1983), who selected on sternopleural bristle number in Drosophila. Replicate lines showed a very rapid exhaustion of response, and crosses between lines did not result in further response. The authors interpreted these results as being consistent with a few alleles of large effect, which were initially at an intermediate frequency. These alleles rapidly go to fixation, with all lines being fixed for the same major alleles. Similarly, Skibinski and Shereif (1989) found that the among-line variance of lines selected for sternopleural bristle number decreased over time. The among-line variance is expected to increase over time if drift dominates (e.g., Equation 12.1b) or if there is weak selection on the underlying loci, but it is expected to decrease if the lines are fixed for the same few major genes.

---

## chapter26_010 · Long-term Response: Introduction / Robertson's Theory of Selection Limits

**[推导 Derivation]**

Equations 26.10–26.13 are fairly general, assuming only Hardy-Weinberg, no epistasis, and that single-locus results can be added across loci. To proceed further, we need explicit expressions for $ u_i(p_0) $ to describe the limit, and for both $ E(p_t) $ and $ E[p_t(1-p_t)] $ to describe the dynamics. The most complete description, by Robertson (1960a), is for additive alleles, where $ E[\Delta_i(t)] = 2a[E(p_t) - p_0] $. Recalling Equation 7.28a yields $$ E(p_{t})\simeq p_{0}+2N_{e}\left(1-e^{-t/2N_{e}}\right)s p_{0}(1-p_{0}) $$ as an approximate expression for the expected allele frequency, under the assumption that the allele has a small effect (i.e., is nearly neutral). For notational ease, we will drop the expectation notation, but the reader should keep in mind that we are examining the expected response. Recalling from Equation 25.4 that $s = a\bar{\nu}/\sigma_z = aS/\sigma_z^2$ (as $\bar{\nu} = S/\sigma_z$), substitution into Equation 7.28a yields an expected response from locus $i$ after $t$ generations of selection of

> **Formula (26.14a)** · `26.14a` · source: `chapter26_block_048` · Robertson's Theory of Selection Limits
>
> $$ \Delta_{i}(t)=2a[E(p_{t})-p_{0})]\simeq2N_{e}\left(1-e^{-t/2N_{e}}\right)\left(\frac{a S}{\sigma_{z}^{2}}\right)2a p_{0}(1-p_{0}) $$


**[推导 Derivation]**

This can be simplified further by noting that $ 2a^2p_0(1 - p_0) $ is the initial additive variance contributed by the locus. Because we assumed no epistasis and no linkage disequilibrium, summing over all loci gives the cumulative response at generation $ t $ as

> **Formula (26.14b)** · `26.14b` · source: `chapter26_block_049` · Robertson's Theory of Selection Limits
>
> $$ R(t)\simeq2N_{e}\left(1-e^{-t/2N_{e}}\right)\frac{S\sigma_{A}^{2}(0)}{\sigma_{z}^{2}} $$


**[推导 Derivation]**

Note that $ S \sigma_A^2(0) / \sigma_z^2 = S h^2(0) = R(1) $ is the expected response in the first generation, provided that the conditions for the breeder's equation hold. Equation 26.14b implies that

> **Formula (26.15a)** · `26.15a` · source: `chapter26_block_050` · Robertson's Theory of Selection Limits
>
> $$ R(t)\simeq2N_{e}\left(1-e^{-t/2N_{e}}\right)R(1) $$


returning an expected limiting total response of

> **Formula (26.15b)** · `26.15b` · source: `chapter26_block_050` · Robertson's Theory of Selection Limits
>
> $$ R(\infty)\simeq2N_{e}R(1) $$


Because $ R(1)/\sigma_z = h^2 S/\sigma_z = h^2 \bar{\tau} $, the expected limiting response in terms of phenotypic standard deviations is

> **Formula (26.15c)** · `26.15c` · source: `chapter26_block_050` · Robertson's Theory of Selection Limits
>
> $$ R(\infty)/\sigma_{z}\simeq h^{2}(2N_{e}\bar{\imath}) $$


**[推导 Derivation]**

Note that Equation 26.15a motivates the use of exponential regressions in Chapter 25 to estimate selection limits (Equation 25.10). The careful reader will note that we assumed that the phenotypic variance remains relatively constant over time, as would occur if $ h^2 $ were small (and hence a decrease in the heritability will have little impact on $ \sigma_z^2 $). Provided this assumption holds, the total expected response is simply $ 2N_e $ times the initial response, as first suggested by Dempster (1955b) and formally derived by Robertson (1960a). An alternative derivation of Equation 26.15a is as follows. Assuming the main force for allele-frequency change is drift, Equation 11.2 yields

> **Formula (26.15d)** · `26.15d` · source: `chapter26_block_051` · Robertson's Theory of Selection Limits
>
> $$ \sigma_{A}^{2}(t)\simeq\sigma_{A}^{2}(0)[1-1/(2N_{e})]^{t}\simeq\sigma_{A}^{2}(0)\exp\left[-t/(2N_{e})\right] $$


Writing the response in generation $ t $ as $ h^2(t)S = \sigma_A^2(t) \bar{\nu}/\sigma_z $, summing over generations and applying Equation 7.28b recovers Equation 26.15a.

Equation 26.15b is an upper limit for the total response, which may seem somewhat counterintuitive because it was derived by assuming weak selection. The key to understanding this upper bound is that (everything else being equal) the initial response $ R(1) $ when selection dominates is much larger than when drift dominates, so $ 2N_e $ (the time for drift to remove a significant amount of genetic variation) times the initial response overestimates the total response when selection dominates. To see this point, consider the maximal contribution, $ \Delta_i^{max} = 2a(1 - p_0) $, from a locus (which occurs when the favored allele is fixed) relative to the predicted contribution, $ \Delta_i(\infty) $. From Equation 26.14a, it follows that

**[推导 Derivation]**

$ \Delta_i(\infty) = 2N_e\,2a^2p_0(1 - p_0)S/\sigma_z^2 $. Substituting $ S/\sigma_z^2 = \bar{\imath}/\sigma_z $ yields the ratio of maximum to expected contribution as

> **Formula (26.16a)** · `26.16a` · source: `chapter26_block_054` · Robertson's Theory of Selection Limits
>
> $$ \frac{\Delta_{i}^{max}}{\Delta_{i}(\infty)}=\frac{1}{2N_{e}}\frac{2a(1-p_{0})}{2a^{2}p_{0}(1-p_{0})\bar{\imath}/\sigma_{z}}=\frac{\sigma_{z}}{2N_{e}\bar{\imath}a p_{0}} $$


**[推导 Derivation]**

Thus, $ 2N_e R(1) $ overestimates the ultimate limit $ (\Delta_i(\infty) > \Delta_i^{max}) $ when

> **Formula (26.16b)** · `26.16b` · source: `chapter26_block_055` · Robertson's Theory of Selection Limits
>
> $$ 2N_{e}\bar{\imath}a p_{0}>\sigma_{z} $$


implying that $ 2N_{e}R(1) $ overestimates the ultimate limit when this inequality is satisfied.

Recalling Equation 26.3b, the probability of fixation is greater than 86% when Equation 26.16b is satisfied. Increasing the effective population size above this threshold has little effect on increasing the selection limit, as $ u_i(p_0) \simeq 1 $ and, hence, the contribution from the $ i $th locus is $ \Delta_i^{max} $. In contrast, when the inequality provided by Equation 26.16b fails, $ \Delta_i^{max} > \Delta_i(\infty) $. However, in this case drift is expected to dominate (see Equation 26.3a), so we do not expect $ o $ obtain the maximal possible response from each locus, as many favored loci will be lost, rather than fixed.

**[推导 Derivation]**

Another quantity of interest is the expected half-life of response, $ t_{0.5} $, the time required to obtain half the final response. Recalling Equation 26.14a, and solving $ 1 - e^{-t_{0.5}/2N_e} = 1/2 $, yields an expected half-life of

> **Formula (26.17)** · `26.17` · source: `chapter26_block_057` · Robertson's Theory of Selection Limits
>
> $$ t_{0.5}=N_{e}\ln2\simeq1.4N_{e} $$


Again, this is an upper limit, with the half-life decreasing as the product $ N_{e}\bar{i} $ increases. An observed half-life considerably below that predicted by Equation 26.17 suggests that a large portion of the response is due to the fixation of favorable alleles by selection, as selection (when it dominates) changes allele frequencies much faster than drift.

Equations 26.14–26.17 rely on a number of assumptions besides additivity: no opposing natural selection, no linkage effects, two alleles per locus, and weak selection (on loci). Several authors have examined the robustness of these results. Hill and Rasbash (1986) found, for diallelic loci, that the distribution of allelic effects is relatively unimportant, but differences in allele frequencies can be critical. In particular, increasing the effective population size has much more of an effect on the selection limit when favored alleles are rare. This is expected, as the dynamics of common alleles at selected loci are largely governed by selection rather than drift (Equation 26.3b). Increasing population size lowers the critical allele-frequency threshold for selection to dominate, eventually capturing even rare alleles (Zhang and Hill 2005a). Latter and Novitski (1969) and Zeng and Cockerham (1990) examined the effects of multiple alleles, and found that the results for the expected limit (Equation 26.15b) and the half-life (Equation 26.17) are reasonable when selection is weak. As $ N_{e}\bar{i} $ increases, $ R(\infty)/R(1) $ becomes highly dependent on the number and frequencies of alleles at each locus (Chapter 25). In general, this ratio increases with the number of alleles, and decreases with increasing $ N_{e}\bar{i} $, all the while remaining bounded by a factor of $ 2N_{e} $. Likewise, $ t_{0.5} $ decreases as $ N_{e}\bar{i} $ increases, but it is rather insensitive to the number of alleles. With dominance, analytic results for the limit and half-life ($R[\infty]$ and $t_{0.5}$) are more complicated. Strictly recessive alleles have received the most study. In this case, the selection limit can considerably exceed $2N_{e}$ times the initial response when the character is controlled by a large number of rare recessives (Robertson 1960a). Additive genetic variance increases, often considerably, as these recessives increase in frequency, so this result should not be surprising (Chapter 25). With weak selection, the half-life from recessives varies from approximately $N_{e}$ when $p\simeq1$ to approximately $2N_{e}$ when $p\simeq0$ (Robertson 1960a). Again, as $N_{e}$ increases, half-life decreases. Even with strictly additive loci, a temporary increase in the genetic variance (even in the face of genetic drift) can occur if there are a number of rare, but favored, alleles (Chapter 25). As these alleles increase in frequency, the additive variance also increases. If genetic drift strictly governs the dynamics of the additive variance, these rare alleles have only a small chance of increasing and do not significantly (on average) inflate the variance. However, if selection is of even modest importance to the dynamics

**[Table]**

> **Table 26.1** · `26.1` · page 13 · source: `chapter26_010`
> Table 26.1 Observed and predicted selection limits ( $ 2N_e h^{2\bar{\tau}} $, scaled in terms of  $ \sigma_z $; Equation 26.15c) and half-lives (scaled in terms of  $ N_e $) for a variety of characters in laboratory populations of mice. The Ratio column under Half-life is the fraction of the predicted upper limit for the half-life ( $ 1.4N_e $; Equation 26.17), observed. (From Hanrahan et al. 1973; Eisen 1975; and Falconer 1977.)
>
> <table><tr><td rowspan="2">Character</td><td rowspan="2">Direction of Selection</td><td colspan="3">Total Response</td><td colspan="2">(Half-life)/ $ N_{e} $</td></tr><tr><td>Observed</td><td>Predicted</td><td>Ratio</td><td>Observed</td><td>Ratio</td></tr><tr><td colspan="7">Weight</td></tr><tr><td rowspan="2">Strain N</td><td>Up</td><td>3.4</td><td>7.2</td><td>0.47</td><td>0.6</td><td>0.43</td></tr><tr><td>Down</td><td>5.6</td><td>15.9</td><td>0.35</td><td>0.6</td><td>0.43</td></tr><tr><td rowspan="2">Strain Q</td><td>Up</td><td>3.9</td><td>15.8</td><td>0.27</td><td>0.2</td><td>0.14</td></tr><tr><td>Down</td><td>3.6</td><td>9.6</td><td>0.38</td><td>0.4</td><td>0.29</td></tr><tr><td rowspan="2">Growth</td><td>Up</td><td>2.0</td><td>7.4</td><td>0.27</td><td>0.3</td><td>0.21</td></tr><tr><td>Down</td><td>4.5</td><td>13.7</td><td>0.33</td><td>0.5</td><td>0.36</td></tr><tr><td rowspan="2">Litter Size</td><td>Up</td><td>1.2</td><td>2.3</td><td>0.52</td><td>0.5</td><td>0.36</td></tr><tr><td>Down</td><td>0.5</td><td>7.7</td><td>0.06</td><td>0.5</td><td>0.36</td></tr><tr><td colspan="7">Postweaning weight gain</td></tr><tr><td>Line M4</td><td>Up</td><td>1.5</td><td>5.4</td><td>0.27</td><td>0.9</td><td>0.64</td></tr><tr><td>Line M8</td><td>Up</td><td>2.0</td><td>10.0</td><td>0.20</td><td>0.5</td><td>0.36</td></tr><tr><td>Line M16</td><td>Up</td><td>4.3</td><td>45.0</td><td>0.10</td><td>0.3</td><td>0.21</td></tr></table>


at any particular locus, as Chapter 25 highlights, the single-generation response is a very poor predictor of the long-term response.

James (1962), Verghese (1974), Nicholas and Robertson (1980), and Zeng and Hill (1986) extended Robertson's theory for various models of natural selection opposing artificial selection. Not surprisingly, the selection limit is reduced by the presence of opposing natural selection. In the absence of mutation, none of these models retain genetic variability, as drift eventually fixes all loci, even those displaying overdominance in fitness.

---

## chapter26_011 · Long-term Response: Introduction / TESTS OF ROBERTSON'S THEORY OF SELECTION LIMITS

Robertson's theory applies to the expected response from the existing variation in the base population at the start of selection. Eventually, mutational input becomes important and will ultimately dominate the long-term response, a point we will develop in detail shortly. In the very small population sizes common in many selection experiments, the distinction between exhaustion of the initial variation and the additional response due to new mutation can be fairly clear, as the latter takes many more generations to become apparent than it takes to remove existing variation. For larger population sizes, the two sources of response become increasingly blurred. Hence, most tests of Robertson's theory use very small populations.

Observed limits and half-lives are usually considerably below the values predicted from Robertson's theory (reviewed in Roberts 1966; Kress 1975; Eisen 1980; Falconer and Mackay 1996). Table 26.1 gives various results from experiments with mice. These discrepancies between observation and theory are not unexpected. Robertson's theory assumes that the limit is reached as genetic variance is exhausted by fixation at all loci. As noted in Chapter 25, selection limits can occur despite significant additive genetic variance, often because natural and artificial selection are in conflict. Further, the selection limit of $ 2N_eR(1) $, and the half-life of $ 1.4N_e $, are expected upper limits that assume that drift largely dominates. An additional complication is that the effective population size is overestimated by taking $ N_e $ as the number of parents (Chapter 3). For example, variation in male mating success in Drosophila can decrease the effective population size to less than half the actual number of male parents (Crow and Morton 1955). Further, most experiments have not corrected for the expected reduction in $ N_e $ from the effects of artificial selection (Equation 26.6c).

**[Table]**

> **Table 26.2** · `26.2` · page 14 · source: `chapter26_011`
> Table 26.2 The cumulative response after 50 generations of selection for increased abdominal bristle number in Drosophila melanogaster as a function of the effective population size and the selection intensity.  $ N_{e} $ is estimated as half the number of parents. None of the lines showed an apparent plateau, but the experiment was stopped after 50 generations. For fixed  $ N_{e} $, the response increases with  $ \bar{i} $ (compare entries within a column), while for fixed  $ \bar{i} $, response increases with  $ N_{e} $ (compare entries across a row). (After Jones et al. 1968.)
>
> $ N_{e} $ | $ \bar{t} $ | $ R(50) $ | $ N_{e} $ | $ \bar{t} $ | $ R(50) $ | $ N_{e} $ | $ \bar{t} $ | $ R(50) $
> --- | --- | --- | --- | --- | --- | --- | --- | ---
> 10 | 1.6 | 16.3 | 20 | 1.7 | 20.3 | 40 | 1.7 | 31.7
> 10 | 1.3 | 11.2 | 20 | 1.4 | 14.7 | 40 | 1.4 | 18.8
> 10 | 0.9 | 8.1 | 20 | 1.0 | 12.2 | 40 | 1.0 | 16.4


A more direct test of Robertson’s theory evaluates whether the selection limit increases, and the half-life decreases, as $ N_{e}\bar{t} $ increases. In general, both of these predictions hold. For example, the estimated effective population sizes of lines M4, M8, and M16 in Table 26.1 were 7.7, 18.6, and 40.9, while each line experiences essentially the same value of $ \bar{t} $ (Eisen 1975). For this data set, half-life decreases as $ N_{e}\bar{t} $ increases, as predicted by theory. In a more extensive experiment, Jones et al. (1968) examined the effects of changing $ N_{e} $ or $ \bar{t} $ on otherwise replicate lines of Drosophila melanogaster. Because all of their populations were still responding at the end of the experiment (50 generations), they did not estimate the limit or half-lives (although one could use their data with Equation 25.10a to do so). Nevertheless, their data (Table 26.2) are consistent with Robertson’s qualitative predictions, as long-term response increases with $ N_{e}\bar{t} $ (Figure 26.2).

Robertson's theory further predicts that when the effective population size is sufficiently large, further increases in $ N_e $ should not change the limit (provided mutational input can be ignored), as all favorable alleles that were initially present become fixed. This has yet to be observed, which is perhaps not surprising given that most experiments have value of $ N_e $ below 50. By designing ingenious devices to facilitate mass selection in Drosophila melanogaster, Weber (1990, 1996, 2004; Weber and Diggins 1990) were able to examine the consequences of larger population sizes. Selection experiments on wing-tip height (Weber 1990) and ethanol tolerance (Weber and Diggins 1990) had effective population sizes on the order of $ N_e \simeq 200-400 $. Both characters showed an increased response with increasing $ N_e $. The data for wing-tip height are given in Figure 26.3A. Figure 26.3B summarizes the results of nine other experiments from previous studies, showing the ratio of response after 50 generations to the initial response. As predicted, this ratio generally increases with values of $ N_e $. The implication is that there is additional “usable” genetic variation present in the base population that can be exploited by increasing the scaled strength of selection ($ N_e \bar{t} $). In very small populations, only major alleles are influenced by selection (Equation 26.3). The observation that response continues to increase with $ N_e $ suggests a large pool of alleles of smaller effects, or at lower frequencies, or both. As $ N_e \bar{t} $ increases, favorable alleles at these loci are more likely to become fixed, increasing response. Larger populations also provide a greater chance for recombination to remove deleterious linked combinations, which might be fixed in smaller populations, further increasing the potential for response.

One complication with Robertson’s theory is that as population size increases, the contribution from mutational input becomes increasingly important over the time scales that it takes to remove the initial variation. We will address this point shortly. A second complication is that when the character value is influenced by inbreeding depression (as will occur if directional dominance is present), its effects are more dramatic in smaller populations. One test for whether inbreeding depression is reducing the selection response is to cross divergently selected lines and look for significant increases in the mean in the resulting $ F_{1} $ population (e.g., Eisen 1975; Kownacki 1979).

---

## chapter26_012 · Long-term Response: Introduction / Weber's Selection Experiment on Drosophila Flight Speed

Perhaps the largest long-term artificial selection experiment (outside of microbes) is the heroic effort of Weber, which was introduced in Chapter 25. Weber (1996) scored a total of over 9,000,000 Drosophila for flight speed in two replicate lines subjected to 100 generations of selection (Figure 25.9). The resulting $ N_{e} $ was in the 500–1000 range, with a percent selected of p = 0.045 (for a selection intensity of $ \bar{i} = 2.11 $). The average speed before selection was around 2 cm/second, while the mean speed at generation 100 was 170 cm/sec. As shown in Figure 25.9, response continued in both lines for 100 generations but was diminishing with time, as indicated by a significant quadratic component in the response curve. Figure 26.3A shows the results for over 300 generations of selection from Weber (2004). As of this writing, the experiment is over 650 generations, with response, albeit diminishing, still occurring (Weber, pers. comm.).

Unlike in many artificial selection experiments, there was little slippage upon relaxation of selection and only a minimal loss in fitness relative to the control populations (fitness decreases of 6% and 7% at generations 50 and 85, respectively). Weber attributes this to the larger effective population size, which both reduces the level of inbreeding and allows for more efficient selection on modifiers. The latter can reduce deleterious pleiotropic effects that might accompany major alleles improving flight speed, as the weak second-order effects on modifiers are much easier to select for in larger populations. Larger population sizes also allow recombination to be more efficient, reducing the effects of deleterious alleles linked to alleles improving flight speed.

Weber gained some insight into the genetic nature of the response by examining the selection response in hybrid lines formed by crossing each replicate selection line at generation 75 (lines AA1 and AA2) back to control lines (CN1 and CN2). As Figure 26.4B shows, both the $ F_{1} $ and $ F_{2} $ were close to the control line values, indicating very strong dominance for reduced flight speed. Evidence for epistasis was more equivocal. From the theory of line-cross analysis (LW Chapter 9), an estimate of composite epistatic effects is provided by the linear contrast of means of the parental and first two filal populations, $ 4\overline{z}_{F_2} - 2\overline{z}_{F_1} - \overline{z}_{P_1} - \overline{z}_{P_2} $, but the resulting value was not significantly different from zero ($ -38.5 \pm 37.5 $). Selection on both resulting $ F_2 $ lines required only six generations to recover essentially all of the response seen in the parental (75-generation) lines ($ \sim 140 $ cm/sec).

---

## chapter26_013 · Long-term Response: Introduction / THE EFFECTS OF LINKAGE ON THE SELECTION LIMIT

When QTLs are linked, we expect some reduction in the limit because selection on linked loci reduces the fixation probabilities of beneficial alleles (Hill and Robertson 1966; Birky and Walsh 1988; Barton 1995a). Simulation studies (Fraser 1957; Gill 1965a, 1965b, 1965c; Latter 1965a, 1966a, 1966b; Qureshi and Kempthorne 1968; Qureshi 1968; Qureshi et al. 1968) show that linkage has only a small effect unless loci are very close ($ c \leq 0.05 $). As mentioned in Chapter 7, most of these studies inflated the importance of linkage by assuming that all loci have equal effects. Simulation studies by McClosky and Tanksley (2013) found only modest reductions ($ \simeq 10% $) in short-term (less than 20 generations) response for populations with normal versus fully unconstrained levels of recombination.

An approximate analytic treatment of linkage was offered by Robertson (1970a, 1977a), and later by Hospital and Chevalet (1993, 1996) and Zhang and Hill (2005a), who relied on certain normality assumptions. In the absence of recombination, selection acts on an entire chromosome, and Robertson framed his results in terms of the response contributed by a single chromosome. Robertson considered three different limiting expected responses, $ L_{i} $, corresponding to different amounts of recombination: $ L_{f} $, the chromosomal limit with free recombination between all loci; $ L_{0} $, the limit under complete linkage; and $ L_{\ell} $, the limit when the map length of the chromosome is $ \ell $ (implying, for $ n $ loci, a recombination rate between the adjacent loci of approximately $ \ell/n $).

**[推导 Derivation]**

The completely additive model is assumed with loci starting in gametic-phase equilibrium. Let $ \sigma_A^* $, be the initial additive genetic variance contributed by the focal chromosome and define $ (h^*)^2 = \sigma_A^* / \sigma_z^2 $ as the initial fraction of phenotypic variance attributable to this chromosome. The expected contribution from this chromosome following a single generation of selection is $ S\sigma_A^* / \sigma_z^2 = \bar{i}h^* \sigma_{A^*} $. When $ N_e \bar{i}h^* $ is small, the expected limit for a chromosome with freely recombining loci is $ 2N_e $ times the initial response, yielding $ L_f \simeq 2N_e \bar{i}h^* \sigma_{A^*} $ (Equation 26.15b, considering the response from a single chromosome). Assuming weak selection, Robertson (1970a) found that the ratio of the free-recombination limit to the complete-linkage limit (i.e., the best initial chromosome) is approximately

> **Formula (26.18)** · `26.18` · source: `chapter26_block_073` · THE EFFECTS OF LINKAGE ON THE SELECTION LIMIT
>
> $$ \frac{L_{f}}{L_{0}}\simeq1+\frac{2}{3}(N_{e}\bar{\imath}h^{*})^{2}\quad\mathrm{w h e n}\quad2N_{e}\bar{\imath}h^{*}<1 $$


Hence, for weak selection, complete linkage has only a trivial effect when the chromosome contains a large number of QTLs.

**[推导 Derivation]**

When selection is strong ($ N_e \bar{i} h^* \gg 1 $), the results are more complicated. Robertson assumed that there are $ n $ underlying loci, each with a frequency of $ p $ of the favored allele, which increases the character by $ 2a $ (the difference between the homozygotes). Under these assumptions, the additive variance contributed by this chromosome is $ \sigma_A^* = 2na^2p(1 - p) $. If selection is sufficiently strong, under free recombination all favored alleles will be fixed, and the total response becomes $ L_f = 2na(1 - p) $. Noting that $ a = \sigma_A^* / \sqrt{2np(1 - p)} $, this can also be restated as

> **Formula (26.19)** · `26.19` · source: `chapter26_block_075` · THE EFFECTS OF LINKAGE ON THE SELECTION LIMIT
>
> $$ L_{f}=2na(1-p)=\sigma_{A*}\sqrt{\frac{2n(1-p)}{p}} $$


**[推导 Derivation]**

On the other hand, with complete linkage the limit approaches twice the value of the best of the initial 2N chromosomes sampled (as this chromosome is ultimately fixed). The expected value for the best chromosome is given by the expected value of the largest order statistic (see Example 6 in LW Chapter 9). For a unit normal, this is expressed in terms of standard deviations (here $ \sigma_{A*} $) above the mean, so that if $ x_{2N} $ is the standardized largest order statistic in a sample of 2N chromosomes, the limit is given by

> **Formula (26.20a)** · `26.20a` · source: `chapter26_block_076` · THE EFFECTS OF LINKAGE ON THE SELECTION LIMIT
>
> $$ L_{0}=(x_{2N}\sqrt{2})\sigma_{A*} $$


**[推导 Derivation]**

Robertson (1970a) showed, for $10 < N < 40$, that $x_{2N} \sqrt{2} \simeq 3$, so that $L_{0}/\sigma_{A}^{2} \simeq 3$. Hence, for these values of $N$,

> **Formula (26.20b)** · `26.20b` · source: `chapter26_block_077` · THE EFFECTS OF LINKAGE ON THE SELECTION LIMIT
>
> $$ \frac{L_{f}}{L_{0}}\simeq\frac{1}{3}\sqrt{\frac{2n(1-p)}{p}} $$


**[推导 Derivation]**

The factor of 3 increases to 3.8 when N = 80 and to 4.6 when N = 500. For larger values of N, if we use the asymptotic approximation for the largest order statistic given by Kendall and Stuart (1977), the factor of 3 is replaced by

> **Formula (26.20c)** · `26.20c` · source: `chapter26_block_078` · THE EFFECTS OF LINKAGE ON THE SELECTION LIMIT
>
> $$ x_{2N}\sqrt{2}\simeq\frac{0.577}{\sqrt{\ln(2N)}}+2\sqrt{\ln(2N)} $$


Note that the increase in the selection limit is only weakly dependent on $N$, as the largest order statistic scales as $\sqrt{\ln(2N)}$. For example, for $N=10^{9}$, $x_{2N}\sqrt{2}\simeq9.4$.

**[推导 Derivation]**

Robertson suggested that as the number of loci, $n$, increases, the limit under free recombination approaches a value independent of $n$ and $p$, namely, the infinitesimal limit, $L_f = 2N_e\bar{\imath}h^* \sigma_{A^*}$. Thus, with strong selection and a large number of loci, Equation 26.20a implies that

> **Formula (26.20d)** · `26.20d` · source: `chapter26_block_080` · THE EFFECTS OF LINKAGE ON THE SELECTION LIMIT
>
> $$ L_{f}/L_{0}\simeq\frac{2N_{e}\bar{\imath}h^{*}\sigma_{A*}}{\left(x_{2N}\sqrt{2}\right)\sigma_{A*}}=\left(\frac{\sqrt{2}}{x_{2N}}\right)N_{e}\bar{\imath}h^{*}\qquad\mathrm{w h e n}N_{e}\bar{\imath}h^{*}>5 $$


---

## chapter26_014 · Long-term Response: Introduction / THE EFFECTS OF LINKAGE ON THE SELECTION LIMIT

**[推导 Derivation]**

Robertson also observed that for $ N_e \bar{\imath} h^* > 5 $, the half-life with no recombination is

> **Formula (26.20e)** · `26.20e` · source: `chapter26_block_081` · THE EFFECTS OF LINKAGE ON THE SELECTION LIMIT
>
> $$ t_{0.5}\simeq\frac{2}{\bar{\imath}h^{*}} $$


generations, and that differences in response (relative to free recombination) only become apparent after this number of generations has passed.

**[推导 Derivation]**

Allowing for some recombination (at a rate of $ \sim\ell/n $ between loci), Robertson found that the limit for a chromosome of length $ \ell $ is

> **Formula (26.21a)** · `26.21a` · source: `chapter26_block_082` · THE EFFECTS OF LINKAGE ON THE SELECTION LIMIT
>
> $$ L_{\ell}/L_{0}\simeq1+(N_{e}\ell/3)\qquad\mathrm{w h e n}\ N_{e}\ell\ll1 $$


**[推导 Derivation]**

To a poorer approximation, over the entire range of $ N_{e} \ell $

> **Formula (26.21b)** · `26.21b` · source: `chapter26_block_083` · THE EFFECTS OF LINKAGE ON THE SELECTION LIMIT
>
> $$ L_{\ell}/L_{0}\simeq1+\frac{KN_{e}\ell/3}{N_{e}\ell/3+K} $$


where $ K = L_f / L_0 $. Thus $ L_\ell / L_0 $ approaches $ L_f / L_0 $ as $ N_e \ell $ increases. Provided $ L_f \gg L_0 $, then $ L_\ell $ is a halfway between $ L_f $ and $ L_0 $ when $ N_e \ell / 3 = K = L_f / L_0 $. Assuming moderate to large values of $ N_e $, this result (together with Equation 26.20d) implies that if the amount of recombination satisfies $ \ell > 2\imath h^* $, then the selection response will be at least half that expected for free recombination. These expressions are approximate and assume that all loci have equal effects. Variation between loci in allelic effects reduces the effect of linkage (Hill and Robertson 1966; Robertson 1970a).

Experimental results generally confirm that the suppression of recombination has only a modest effect on the selection limit (Example 26.4). This is somewhat at odds with the increase in recombination rates seen during some artificial selection experiments (Example 26.1), although, as mentioned, this view may be tempered if there is significant ascertainment bias in the reporting of increased recombination following selection.

Robertson’s result largely focused on the ultimate selection limit, while Hospital and Chevalet (1993, 1996) considered the dynamics of the approach to this limit. In particular, Hospital and Chevalet (1996) explicitly considered the effects of gametic-phase disequilibrium (also see Zhang and Hill 2005a). Initially, selection generates negative gametic-phase disequilibrium, which reduces the initial expressed additive-genetic variance and decreases the response. The tighter is the linkage, the more pronounced is this effect (Chapters 16 and 24). Surprisingly, Hospital and Chevalet (and also Zhang and Hill) showed that linkage can often result in an increase in the additive variation in later generations of selection. This seemingly counterintuitive result arises because selection increases the frequency of the gametes carrying the most favored alleles. Because any tightly linked alleles decreasing the trait are also dragged along, this reduces the ultimate selection limit (a phenomenon called linkage drag). On the other hand, rare recombination events among such gametes can result in the creation of new, even more favorable gametes, and generating a transient increase in the additive variance as these sweep through the population. Thus, the negative gametic-phase disequilibrium that suppresses the early response stores some genetic variation that can become released (via recombination) in later generations. This effect is most pronounced in larger populations, as in small populations, haplotypes can become fixed before such recombination events occur.

**[示例 Example]**

> **Example 26.3** · ref: `26.3` · source: `chapter26_014.json` · blocks 5–5
>
> Example 26.3. Cohan and Hoffmann (1986) examined the divergence between replicate lines of Drosophila melanogaster selected for increased resistance to ethanol. The selected lines had a higher among-line variance for characters associated with increased resistance than did the unselected control replicates. This could be explained by a reduction in effective population size due to selection or by the Cohan effect (Example 7.4). The reduction in effective population size, by increasing drift, is expected to increase the among-line variance in any character, selected or unselected. Conversely, the Cohan effect predicts that only characters under selection, or characters controlled by loci tightly linked to QTLs for these selected characters, should show increased divergence. Cohan and Hoffmann found no differences between the selected and control lines for three unselected characters, which suggested that the main cause of increased divergence was the Cohan effect.


**[示例 Example]**

> **Example 26.4** · ref: `26.4` · source: `chapter26_014.json` · blocks 6–6
>
> Example 26.4. By using the inversions Curly and Moiré, McPhee and Robertson (1970) were able to select for sternopleural bristles in Drosophila under conditions of suppressed recombination on chromosomes II and III. From previous work, $ h^2 = 0.4 $, with these chromosomes accounting for 1/3 and 1/2 (respectively) of the genetic variation in bristle number (and with the X chromosome accounting for the remaining 1/6). In lines that were suppressed for recombination on both chromosomes, the selection limit (on a transformed scale) was $ 0.166 \pm 0.014 $ in up-selected lines and $ -0.134 \pm 0.009 $ in down-selected lines, reductions of $ 28 \pm 8% $ and $ 22 \pm 7% $ relative to the limit obtained when normal recombination was allowed. For these studies, $ N_e \simeq 10 $ and $ \bar{\tau} \simeq 1 $, while $ h_{II}^* $ = $ \sqrt{0.4/3} \simeq 0.37 $ and $ h_{II}^* $ = $ \sqrt{0.4/2} \simeq 0.45 $. Thus, selection is strong on both chromosomes as $ N_e \bar{\tau} h_{II}^* $ $ \simeq 3.7 $ and $ N_e \bar{\tau} h_{II}^* $ $ \simeq 4.5 $.
> 
> Under these conditions, Robertson’s theory predicts that the limiting contribution from each (recombination-suppressed) chromosome will be approximately $ 3\sigma_A^* $ (as $ x_{2N} \sqrt{2} \sim 3 $; Equation 26.20a). Given $ \sigma_z = 0.059 $ and $ \sigma_A^* = 0.059 \cdot h^* $, the expected contributions to the selection limit from chromosomes II and III become $ 3 \cdot 0.059 \cdot 0.37 \simeq 0.065 $ and $ 3 \cdot 0.059 \cdot 0.45 \simeq 0.080 $, respectively, for a total absolute contribution of 0.145, consistent with the observed limits. Robertson’s theory (Equation 26.20e) further predicts that the half-life in recombinationally suppressed lines is roughly $ 2 / (\bar{i} h^*) $ generations, or $ 2 / 0.37 \simeq 5.4 $ and $ 2 / 0.45 \simeq 4.4 $ for chromosomes II and III, respectively, consistent with the observed half-life of 5 generations.
> 
> Other Drosophila experiments examined the consequences of suppressed recombination on selection response. Both Markow (1975) and Thompson (1977) used stocks with inversions while selecting for increased or decreased phototactic behavior. While Markow observed that recombination suppression reduced the selection limit, Thompson observed no differences. Markow did not use replicate lines, so the statistical significance of her results is unclear. However, she observed that the most recombinationally suppressed lines had the most reduced response, consistent with theory. In Thompson's experiments, $ N_e \approx 50 $, $ \bar{\imath} \simeq 1 $, and $ h^* \simeq 0.1 $ (for both autosomes), yielding an expected (linkage) half-life of $ 2/(\bar{\imath}h^*) = 20 $ generations (López-Fanjul 1989), as opposed to the value of $ 1.4 \cdot 50 = 70 $ in the absence of linkage (Equation 26.17). Thompson's experiments were stopped at generation 21, so it is not surprising that he found no difference in response, as the reduction in total response from linkage is not readily apparent until well after the expected linkage half-life (Equation 26.20).
> 
> Bourguet et al. (2003) commented that a potential flaw in these Drosophila experiments is that balancer chromosomes were used to suppress recombination, which may have different levels of variation than their homologs in the base population. Using a more careful approach to suppress recombination, they observed no difference between normal and recombinationally suppressed lines in the response after 38 generations of selection for geotaxis. However, they noted that their experiment, like most others, suffered from low power.
> 
> > **Table 26.3** · `26.3` · page 20 · source: `chapter26_014`
> > Table 26.3 Differences in short-term versus long-term response as a function of the number of adults saved, N, when M = 50. Initially,  $ h^2 = 0.5 $ and  $ \sigma_z^2 = 100 $. The infinitesimal model is assumed with  $ N_e = N $. The selection intensity,  $ \bar{\tau} $, is obtained by using Equation 14.3a (corrected for finite population size). From Equation 13.6b,  $ R(1) = 5\bar{\tau} $, while from Equation 26.15b,  $ R(\infty) = 2N R(1) $.
> >
> > N | p | $ \bar{\tau} $ | R(1) | R( $ \infty $)
> > --- | --- | --- | --- | ---
> > 30 | 0.6 | 0.6 | 3.2 | 192
> > 25 | 0.5 | 0.8 | 4.0 | 200
> > 10 | 0.2 | 1.4 | 7.0 | 140
> > 5 | 0.1 | 1.8 | 9.0 | 90
> 


---

## chapter26_015 · Long-term Response: Introduction / OPTIMAL SELECTION INTENSITIES FOR MAXIMIZING LONG-TERM RESPONSE

**[推导 Derivation]**

When a fixed number, $M$, of individuals is scored, there is a tradeoff between the intensity of selection ($\bar{t}$) and the amount of drift ($N_e$). If $N$ individuals are allowed to reproduce (implying $p = N/M$ is the fraction saved), decreasing $N$ (and hence $p$) increases $\bar{t}$ but also decreases $N_e$. Recalling Equation 26.15b, Robertson’s selection limit can be expressed as

> **Formula (26.22)** · `26.22` · source: `chapter26_block_091` · OPTIMAL SELECTION INTENSITIES FOR MAXIMIZING LONG-TERM RESPONSE
>
> $$ 2N_{e}R(1)=N_{e}\bar{\tau}\left(\frac{2\sigma_{A}^{2}(0)}{\sigma_{z}}\right) $$


showing that the ultimate response (from the initial variation) depends on the product of $ N_e $ and $ \bar{\nu} $. While decreasing p results in a larger short-term response due to increased $ \bar{\nu} $, it also results in a decreased long-term response by decreasing $ N_e $. Hence, the product $ N_e $ decreases for sufficiently large or small values of p, suggesting that some intermediate value of p is optimal (see Equation 26.23). Table 26.3 and Figure 26.5B both illustrate this tradeoff. For example, while the single-generation response using p = 0.50 is less than half that for p = 0.10, it yields a selection limit over twice as large (200 vs. 90).

**[推导 Derivation]**

Supporting an earlier conjecture of Dempster (1955b), Robertson (1960a) found (for additive loci and normally distributed phenotypes) that the intensity of selection that yields the largest total response is $p = 0.5$, as $N_e \bar{i}$ is maximized for fixed $M$ when half the population is saved. This can be seen directly for truncation selection on a normally distributed character. Recall from Equation 14.3a that $\bar{i} = \varphi(x_{[1-p]}) / p$ (ignoring the correction for finite population size), where $x_p$ satisfies $\Pr(U < x_{[p]}) = p$, and with $U$ denoting a unit normal random variable and $\varphi(x)$ denotes the unit normal density function. Because the number saved is $N = M p$, we have (following Hospital and Chevalet 1993)

> **Formula (26.23)** · `26.23` · source: `chapter26_block_092` · OPTIMAL SELECTION INTENSITIES FOR MAXIMIZING LONG-TERM RESPONSE
>
> $$ \begin{align*}R(t)&\simeq M p\left(1-e^{-t/2N_{e}}\right)\frac{\varphi(x_{[1-p]})\sigma_{A}^{2}(0)}{p\sigma_{z}}\\&=\varphi(x_{[1-p]})\left[\frac{M\sigma_{A}^{2}(0)}{\sigma_{z}}\left(1-e^{-t/2N_{e}}\right)\right]\end{align*} $$


Because the term in brackets is independent of $p$, response (as a function of $p$) is maximized at the maximum value of $\varphi(x_{[1-p]})$, which occurs at $x = 0$, or a $p$ value of 0.5. As Figure 26.5A illustrates, the selection limit as a function of p becomes extremely flat-topped as M increases, so even fairly large deviations from p = 0.50 yield essentially the same limit. If we relax the assumption of normality, Cockerham and Burrows (1980) found that the optimal proportion for truncation selection is still near 0.50, unless the phenotypic distribution is extremely skewed. Hill and Robertson (1966), Robertson (1970a), and Hospital and Chevalet (1993) found that the optimal proportion increases to above p = 0.50 when linkage is important (recall from Chapter 24 that linkage disequilibrium generates skew in the genotypic distribution, causing it to depart from a normal).

**[Table]**

> **Table 26.4** · `26.4` · page 21 · source: `chapter26_015`
> Table 26.4 As selection intensity increases, the value of  $ N_e $ becomes increasingly less than the actual number of parents ( $ N = pM $), further increasing drift. This additional reduction in effective population size due to selection is computed using the approach in Example 26.2. Parameters and assumptions are as in Table 26.3 ( $ M = 50 $,  $ h^2 = 0.5 $).
>
> N | $ \bar{\tau} $ | $ N_{e} $ | $ N_{e}/N $ | $ 2N_{e}R(1) $
> --- | --- | --- | --- | ---
> 25 | 0.8 | 20.0 | 0.80 | 161
> 10 | 1.4 | 6.2 | 0.62 | 87
> 5 | 1.8 | 2.6 | 0.52 | 47


Robertson's prediction of the optimal selection intensity for long-term response is experimentally supported. Madalena and Robertson (1975) selected for decreased sternopleural bristle number in Drosophila. When the best 5 of 25 were chosen, the limit was 18.0 bristles, less extreme than the limit of 17.1 when the best 10 of 25 were chosen. Similar results were seen for increased abdominal bristle number in Drosophila (Jones et al. 1968), increased egg-laying in Tribolium castaneum (Ruano et al. 1975), and increased postweaning weight in mice (Hanrahan et al. 1973).

Using $N = pM$ as the effective population size is often a severe overestimate (Chapter 3), especially because, as Equations 26.6b–26.6d show, $N_e/N$ decreases as selection intensity increases. Hence, increasing selection intensity increases drift by both reducing $N = pM$ and by further reducing the ratio of $N_e$ to $N$. Table 26.4 illustrates this effect using the same parameters as Table 26.3. Without incorporating this further reduction in $N_e$, the ratio of expected limits when $p = 0.50$ versus $p = 0.10$ is 200/90 = 2.2. When the reduction in $N_e$ due to selection is accounted for, this ratio increases to 161/47 = 3.4.

More generally, Robertson (1970b) obtained the optimal selection intensity when the goal is to maximize the total response (from the initial base population variation) at generation $ t $. Robertson’s derivation follows using Equation 26.15a. As Figure 26.5B shows, the optimal proportion is a function of $ t/M $. Robertson assumed that the infinitesimal model held and that there were equal contributions from each sex. Jódar and López-Fanjul (1977) extended these results to unequal sex ratios, and found that the maximum response occurs when the number of individuals scored and the proportions that are selected are the same in each sex. This follows because effective population size is reduced as the sex ratio deviates from 1:1 (Equation 3.12), which increases the effects of drift. Hospital and Chevalet (1993) examined the effects of linkage and found that the amount by which the optimal value of p exceeds the predicted value (Figure 26.5B) increases with population size. In small populations, the value predicted from drift (for any particular t/M value) is close to the optimal value, while Robertson's value seriously underestimates the optimal p value in larger populations when linkage is present.

Ruano et al. (1975) and Frankham (1977) tested Robertson's predictions for the optimal response at a particular generation with selection experiments for egg-laying in Tribolium and for abdominal bristle number in Drosophila, respectively. The theory holds up well for $ t/M \leq 0.2 $, but both authors found discrepancies between the observed and predicted rank order of lines subjected to different selection intensities when $ t/M > 0.2 $. One explanation of these discrepancies could be the presence of major alleles, resulting in additive variance declining more rapidly than expected under the infinitesimal model. This results in the optimal proportions being larger than those predicted from Figure 26.5B. Frankham (1977) also suggested that not correcting for the additional decrease in $ N_e $ with increased selection intensity (e.g., Table 26.4) results in incorrect values of $ N_e $, and hence incorrect optimal proportions. García-Dorado and López-Fanjul (1985) examined the consequences of unequal sex ratios using sternopleural bristle number in Drosophila. Equal sex ratios gave the highest response, and good agreement with the optimal values predicted by Jódar and López-Fanjul was seen when there were unequal sex ratios.

---

## chapter26_016 · Long-term Response: Introduction / EFFECTS OF POPULATION STRUCTURE ON LONG-TERM RESPONSE

Our development of Robertson’s theory of selection limits has made two assumptions regarding population structure: selection occurs in a large panmictic population, and the initial base population is infinite in size. This section relaxes these assumptions. We first examine the consequences of founder effects in the initial base population and of passing the population through bottlenecks during selection. We conclude by examining the expected limits when the population is subdivided and when selection is entirely within families.

---

## chapter26_017 · Long-term Response: Introduction / Founder Effects and Population Bottlenecks

So far, we have been considering only the effects of drift due to selecting N adults in each generation from an initial base population that is assumed to be infinite. However, drift can also occur prior to selection if the base population itself was founded by sampling individuals from some larger population. By altering the starting additive variance, this initial sampling modifies the expected response, and (provided the founding event is severe), can have a significant impact on the selection response. Robertson (1966b), reporting on the unpublished thesis of Da Silva (1961), found that lines formed from a single parental pair underwent a decrease in the selection response of roughly 30% relative to a nonbottlenecked line from the base population (Figure 26.6A). Lines formed from taking single parental pairs for three consecutive generations showed only a modest further reduction in response, suggesting that most of the founder effect occurred in the first generation. Robertson's interpretation was that response in this population was due largely to alleles that were at an intermediate frequency, as alleles that are at low frequency are expected to be lost during the initial sampling. Segregating alleles present after this initial bottleneck of two individuals have intermediate frequencies (1/4, 1/2, or 3/4), which somewhat decreases their sensitivity to further sampling events.

Using this reasoning, Robertson (1960a) predicted that the effect of restricting population size after several generations of selection is expected to be small, as favored alleles are expected to be at intermediate to high frequencies. However, Jones et al. (1968) found that, even after many generations of selection, such bottlenecks can have a large effect. Sublines formed by taking ten pairs of adults from a parental line selected for 16 generations showed reduced response relative to their parent lines (Figure 26.6B). One explanation for the results of Jones et al. is that there were still desirable alleles at low frequencies following 16 generations of selection. These alleles can be lost when the population passes through a bottleneck, reducing response. One source for these rare major alleles could be new mutations. Alternative explanations were considered by Frankham (1983b).

**[推导 Derivation]**

To present the theory for the impact of bottlenecks on selection response a bit more formally, results are developed for a single additive locus, and extended by assuming gametic-phase equilibrium and no epistasis. If $ N_0 $ is the number of founders, the initial expected additive-genetic variance in the founder population is $ [1 - 1/(2N_0)] \sigma_A^2(0) $, with the expected response for the first generation of selection from a bottlenecked population being $ [1 - 1/(2N_0)] $ times that for an initially infinite population (Jones 1970). The long-term effects of an initial bottleneck are more unpredictable, depending on initial allele frequencies and the relative strength of selection. When selection is weak at all loci (the infinitesimal model), the arguments leading to Equation 26.15a yield the expected response starting with a founder population of size $ N_0 $ as

> **Formula (26.24a)** · `26.24a` · source: `chapter26_block_101` · Founder Effects and Population Bottlenecks
>
> $$ R_{N_{0}}(t)=R(t)\left(1-\frac{1}{2N_{0}}\right) $$


where $ R(t) $ is the response expected when the initial base population is infinite (Equation 26.15a). More generally, if two replicate populations of the same size are created using different numbers of founders ($ N_{01}, N_{02} $) from a common, and large, base population, the ratio of the expected response at any generation is

> **Formula (26.24b)** · `26.24b` · source: `chapter26_block_101` · Founder Effects and Population Bottlenecks
>
> $$ \frac{R_{N_{1}}}{R_{N_{2}}}=\frac{1-1/(2N_{01})}{1-1/(2N_{02})} $$


Thus, if selection at all loci is weak and all genetic variance is additive, the effect of a bottleneck depends only on the number of founders, $ N_{0} $.

**[推导 Derivation]**

Founder effects are most serious when rare favorable alleles of large effect are present, but predicting the magnitude of the effect in any given population is difficult. When selection on a locus is strong ($ 2N_{e}s \gg 1 $), the probability that a selected line formed from a bottlenecked base population will eventually become fixed for the favored allele converges to

> **Formula (26.25a)** · `26.25a` · source: `chapter26_block_103` · Founder Effects and Population Bottlenecks
>
> $$ u_{N_{0}}(p_{0})=1-(1-p_{0})^{2N_{0}} $$


where $ p_0 $ is the major-allele frequency in the population being sampled. This follows because if selection is sufficiently strong, the favored allele will become fixed if it is found in the initial sample, which occurs with a probability of $ 1 - (1 - p_0)^{2N_0} $. Using this approximation, the ratio of the expected limiting contribution from such a locus to the expected contribution when the founding population is infinite is

> **Formula (26.25b)** · `26.25b` · source: `chapter26_block_103` · Founder Effects and Population Bottlenecks
>
> $$ \frac{u_{N_{0}}(p_{0})-p_{0}}{u(p_{0})-p_{0}}\simeq\frac{1-(1-p_{0})^{2N_{0}}-p_{0}}{1-p_{0}}=1-(1-p_{0})^{2N_{0}-1}\simeq1-e^{-p_{o}(2N_{0}-1)} $$


A more accurate measure would be to weight the fixation probability, $ u(p) $, by the sampling probability given a starting allele frequency, $ \sum_{i=1}^{2N_0} \Pr(i \mid p_0, 2N_0) u(i / [2N_0]) $, where $ \Pr(i \mid p_0, 2N_0) $ is the $ i $th term in a binomial with parameters of $ p_0 $ and $ 2N_0 $. Because the initial frequencies of major alleles are unknown, the long-term effect of a bottleneck, even when all genetic variance is additive, is unpredictable. To see this, suppose that a rare $ (p_0 \simeq 0) $, but favorable (a is large), allele is initially present. Its contribution to the initial additive variance is $ V = 2a^2 p_0 (1 - p_0) $, while (if fixed), its contribution to the response is $ R = 2a (1 - p_0) $. Hence, $ R = V / (a p_0) $, so that if $ a p_0 \ll 1 $, but a is large, it makes a large contribution if it is fixed, but only a small contribution to the initial variance. If $ p_0 \simeq 0 $, an allele with a large effect can easily be lost by drift, with only a small effect on the additive variance, but leading to a large potential loss of response. Many artificial selection experiments examining the genetic architecture of a trait first start by breeding a wild-caught sample in the lab for many generations. This generates additional drift, and can result in rare (but important) alleles from the sampled population not being present at the start of artificial selection. Zhang and Hill (2005a) showed that a consequence of this sampling (coupled with selection-generated disequilibrium) is that a population with a significant number of rare alleles (and hence the potential for an accelerated response as rare alleles of large effect increase in frequency, increasing $ h^2 $; Chapter 25) often generates a response no different from that expected under an infinitesimal model.

Frankham (1980) examined founder effects in Drosophila populations that were selected for increased abdominal bristle number. As shown in Figure 26.7, the limit of bottlenecked populations formed from two founders was between 0.69 and 0.72 of that for nonbottle-necked populations, which is quite close to the value of $ [1 - 1/(2N_0)] = 0.75 $ that is predicted for additive loci under weak selection (Equation 26.24b). Frankham reported similar unpublished thesis results of Da Silva (1961) and Hammond (1973). However, while D. Robertson (1969, reported in James 1970) observed a decrease in response with decreasing number of founders when the number of selected parents ($ N_{e} $) was 10, there was no obvious effect when $ N_{e} $ was 40 (which is not unexpected because 1 - 1/80 is negligible). We have been unable to find any reports of response increasing significantly when the population is passed through a bottleneck, as can occur if significant nonadditive variance is present (Chapter 11). Clearly, there is a need for further experiments.

**[命题 Proposition]**

An especially interesting experiment on founder effects was performed by Skibinski and Shereif (1989), who examined sternopleural bristle number in Drosophila melanogaster. Three initial lines were created from a large base population by taking parents from different parts of the distribution of bristle number to generate a high line, a low line, and a line from the central part of the distribution. The central line had the largest total response to divergent selection. Skibinski and Shereif suggested that these results were consistent with the assumption that a few major alleles underlay the trait, with the central line having higher heterozygosity at these loci (and hence more usable genetic variance) than the extreme lines. One caveat with this interpretation is that the central line had a larger initial population size than either extreme line.

---

## chapter26_018 · Long-term Response: Introduction / Population Subdivision

Thus far, we have been considering the long-term response under mass selection in a single panmictic population. But how robust are these results if the total population is subdivided? Robertson (1960a) showed that when only additive variance is present, population structure has little effect on the selection limit. In particular, the expected limit for a population formed by crossing k (replicate) plateaued lines of size N is the same as for a single line of size Nk. Maruyama (1970) generalized this result by showing (for additive loci and ignoring linkage effects) that any subdivision of the population has the same limit, independent of when and how lines are crossed, provided there is no selection among lines. One caveat with this result is that breeders typically try to maximize gain under a set level of inbreeding, and Smith and Quinton (1993) showed that selecting and crossing sublines produces less total selection response for a fixed level of inbreeding than does selection in a single line.

Madalena and Hill (1972) further showed that linkage has only a minor effect on this conclusion. They also found (again assuming only additive variance) that while among-line selection (i.e., culling some of the lines) may increase short-term response, removing lines decreases the total genetic variance of the entire population, which decreases the limit. This reduction in the limit is most severe with free recombination, and it is negligible with tight linkage.

When significant nonadditive genetic variance is present, population subdivision may increase the selection limit. For example, when favorable rare recessives are present, subdividing the population and subsequently crossing these lines when they plateau and then reselecting yields a higher expected limit than using a single panmictic line of the same total size (Madalena and Hill 1972; Slatkin 1981b). The increased inbreeding in the sublines increases the frequency of homozygotes, which facilitates selection for favorable recessives.

Similarly, Wright's shifting balance theory (Wright 1931, 1951, 1978, 1982) asserts that local inbreeding due to population subdivision facilitates the accumulation of rare favorable epistatic combinations of loci. Crossing such fixed (or nearly fixed) lines increases the selection limit relative to a single panmictic population, much akin to what happens with rare recessives. Indeed, Enfield and Anklesaria (1986) found, in simulation studies, that when additive-by-additive epistatic variance is present, certain population subdivisions can result in greater short-term and long-term response than a single panmictic population.

There have been a number of contrasting views on the optimal population structure for evolution. Wright (1931, 1951, 1977, 1978, 1982) suggested that evolution is most rapid when the population is subdivided (henceforth, the Wright structure), while Fisher (1958) viewed a single large panmictic population (the Fisher structure) as the optimal structure. When mostly additive gene action is present, both the Wright and Fisher structures are expected to give comparable rates of evolution, although the Fisher structure may have a slight advantage when the effects of linkage are considered (in larger populations, the probability that a deleterious allele linked to a favorable allele will hitchhike to fixation is decreased, which increases the potential response). With nonadditive gene action, the optimal structure depends on the exact nature of gene action. With recessives, the Wright structure increases the response. With epistasis, this subdivision offers an advantage if epistatic combinations are such that their formation requires intermediate genotypes that are deleterious. Conversely, in other situations, the Fisher structure may offer an advantage in that it allows more gene combinations to be tested. There remains very significant debate over which structure is more relevant (Coyne et al. 1997, 2000; Peck et al. 1998, 2000; Wade and Goodnight 1998; Goodnight and Wade 2000).

Despite these concerns when nonadditive genetic variance is present, selection experiments with population subdivision (reviewed by Rathie and Nicholas 1980 and López-Fanjul 1989) generally have yielded results similar to those expected under the strictly additive model: subdivision usually has no effect on the selection limit. However, two experiments revealed exceptions to this trend. Madalena and Robertson (1975) selected for decreased sternopleural bristle number in Drosophila melanogaster under two different population structures: a single-cycle structure where sublines were crossed once, and a repeat-cycle structure where sublines were crossed multiple times. The limit under the single-cycle structure was essentially the same as for a panmictic population, regardless of whether among-line selection was practiced. The limit under the repeat-cycle structure was slightly more extreme than the panmictic population. These results are complicated by the presence in their lines of major alleles that are lethal as homozygotes but nevertheless suggest the presence of some favorable recessives initially at low frequency. The second exception was revealed an experiment by Katz and Young (1975), who selected for increased body weight in Drosophila. Populations that were subdivided with a small amount of migration among them gave a slightly larger response than the panmictic population.

One must keep in mind that the optimal population structure for maximizing response under one type of gene action may not be optimal for other types. In particular, many types of population structure that increase the probability of fixation of recessive or epistatic genes may retard the fixation of advantageous additive genes. Likewise, even structures that do not decrease the fixation probability may increase the fixation time, which reduces the rate of response.

**[推导 Derivation]**

Caballero et al. (1991) examined the types of mating schemes (following selection) that increase the fixation probability of recessive alleles while not significantly reducing the fixation probabilities or increasing the fixation times for additive genes. They found that mating full sibs wherever possible following selection increased the fixation probabilities for recessives (relative to random mating following selection), without any significant effect on additive alleles. The tradeoff here is a reduction in $ N_{e} $ (due to the increased inbreeding by full-sib mating following selection) versus the increased selection on recessives by inbreeding (compare Equations 7.19b and 7.20c). Recall from Equation 7.20c that the measure, f, of departures from Hardy-Weinberg frequencies enters into the selection coefficients. Caballero et al. showed that

> **Formula (26.26a)** · `26.26a` · source: `chapter26_block_113` · Population Subdivision
>
> $$ f=\frac{N_{FS}-1}{4N_{TM}-3N_{FS}+3}+f_{r} $$


where $ N_{FS} $ is the number of full-sib matings, $ N_{TM} $ is the total number of matings, and $ f_{r} $ is the departure from Hardy-Weinberg genotype frequencies under random mating in a finite population, which is given by

> **Formula (26.26b)** · `26.26b` · source: `chapter26_block_113` · Population Subdivision
>
> $$ f_{r}=-\left(\frac{1}{8N_{f}}+\frac{1}{8N_{m}}\right) $$


where $ N_{m} $ and $ N_{f} $ are the numbers of reproducing males and females. Note that the negative sign implies that under random mating, there is a slight expected excessive of heterozygotes relative to the frequency expected from the allele frequencies alone. Caballero et al. (1991) noted that, under their random-mating scheme, the expected number of full-sib matings is close to one, so $ N_{FS} - 1 $ represents the excessive number of such matings.

---

## chapter26_019 · Long-term Response: Introduction / Within-family Selection

The variance in the number of offspring contributed by each selected parent is an important determinant of the effective population size—the larger this variance, the smaller $ N_{e} $ (Equation 3.4). Exploiting this relationship, Toro and Nieto (1984) noted that deliberately assigning selected parents different probabilities of contributing offspring (according to a specific formula) results in populations with the same selection intensity but different effective population sizes relative to the situation in which the selected parents are randomly mated.

Suppose 20 individuals are measured (M = 20), and we wish the expected selection intensity to be $ \bar{i} = 1.2 $. This occurs if the best 5 individuals are chosen (using Equation 14.4b to correct $ \bar{i} $ for finite population size) and each parent has an equal probability of contributing offspring. This same selection intensity, $ \bar{i} = 1.2 $, can be achieved by instead choosing the best 10 individuals and assigning these individuals unequal probabilities for contributing offspring (using effective selection differentials, which were introduced in Example 13.2; see Toro and Nieto [1984] for details). This latter scheme (while holding both selection intensity and the number of measured individuals, M = 20, constant) increases effective population size from 5.0 to 5.9, which in turn increases the long-term response.

The most extreme example of using a mating scheme to control $ N_e $ in a selected population occurs when selection is entirely within families: the best male and female are chosen from each full-sib family and mated at random between families. This doubles the effective population size compared to the result from selecting the same number of individuals independent of family structure. We remind the reader at this point of the important, but subtle, distinction between parents having an equal probability of contributing offspring versus parents contributing exactly the same number of offspring. In the former case, some parents will contribute no offspring and others will contribute more than one, generating a nonzero variance. In the latter case, recall from Equation 3.4 that if all parents contribute the same number of offspring, there will be no variance in offspring number and $ N_e $ will equal 2N.

Thus, using only within-family selection results in a population with twice the effective size as one undergoing mass selection with the same number of individuals selected. However, as Robertson (1960a) noted, the usable additive genetic variance within full-sib families is only half that available under mass selection (see Chapter 21). This exactly cancels the advantage of a larger $ N_{e} $, suggesting that both methods yield the same limit.

Dempflé (1975) pointed out that this conclusion relies critically on $ h^{2} $ being low. Applying Equations 21.20 and 21.23, the response to a generation of within-family selection is (for full-sibs) $$ R_{w F S}(1)=\bar{\imath}h_{w F S}^{2}\sigma_{w F S} $$ where (with only additive genetic variance), the within-family heritability, the fraction of within-family differences due to differences in breeding values, is $$ h_{w F S}^{2}=\frac{\sigma_{A}^{2}/2}{\sigma_{w F S}^{2}},\quad\mathrm{w h e r e}\quad\sigma_{w F S}^{2}=\frac{\sigma_{A}^{2}}{2}+\sigma_{E s}^{2} $$

If the additive genetic variance is much larger than the within-family environmental variance ($ \sigma_{Es}^2 $), then $ h_{wFS}^2 \simeq 1 $ and $ \sigma_{wFS}^2 \simeq \sigma_A^2 / 2 $, which yields $ R_{wFS}(1) \simeq \bar{\imath} \sigma_A / \sqrt{2} $. If the total environmental variance is much smaller than the additive variance, the expected response to individual selection will become $ R(1) \simeq \bar{\imath} \sigma_A $. Thus, when additive genetic variance dominates, the ratio of expected limits is $$ \frac{4NR_{wFS}(1)}{2NR(1)}\simeq\sqrt{2} $$ and within-family selection increases the limit.

Three other factors can favor within-family selection: 1. Retardation of the cumulative reduction in $ N_e $ from selection. Recall that individual selection reduces $ N_e $ below the actual number of parents by inflating the among-family variance in offspring number when $ h^2 $ or $ \bar{i} $ are large. This variance is zero under within-family selection (Q = 0 in Equation 26.6c), resulting in an effective population size greater than twice that for individual selection, so $ N_e $ (within-family) > $ 2N_e $ (individual).

2. Significant among-family environmental variance. If most of the environmental variance is due to among-family, rather than within-family, effects (i.e., if $ \sigma_{E_c}^2 > \sigma_{E_s}^2 $), within-family selection results in a larger single-generation response than individual selection (Chapter 21). Within-family selection is thus superior when the among-family component of environmental variance is sufficiently large, especially because this factor is in addition to its advantage from within-family selection generating a larger effective population size.

3. Gametic-phase disequilibrium. The presence of gametic-phase (linkage) disequilibrium also increases the effectiveness of within-family selection relative to individual selection. Under the assumptions of the infinitesimal model, the negative gametic-phase disequilibrium generated by directional selection reduces the among-family component of additive variance, while (for unlinked loci) the within-family component remains unchanged (Chapters 16 and 24). Hence, the usable additive variance in the mass-selection lines is decreased, while the usable additive variance in the within-family lines is unchanged. This effect is largely negligible unless selection is strong and heritability is high.

On the experimental side, von Butler et al. (1984) compared individual and within-family selection on 8-week body weight in mice. In one set of replicates, within-family selection initially showed a reduced response, but after 18 generations they had essentially the same response as the mass-selected lines. In another set of replicates (using a different base population), mass selection did better than within-family selection, but both populations were still responding after the experiment was stopped (after 18 generations). Because within-family selection is expected to show a longer period of response (due to a larger effective population size), the results for the second set of replicates are inconclusive.

---

## chapter26_020 · Long-term Response: Introduction / ASYMPTOTIC RESPONSE DUE TO MUTATIONAL INPUT

As reviewed in Chapter 25 (and by Frankham 1980, 1983a; Weber and Diggins 1990; Weber 2004), there is strong evidence that new mutations contribute to selection response even during the relatively short time scales of many so-called “long-term” laboratory experiments. The limit resulting from drift and selection removing all initial genetic variation is thus an artifact of time scale, as it ignores ongoing mutational input. Even if an observed limit is due to a balance between natural and artificial selection, new mutations with less deleterious pleiotropic effects on fitness can arise, resulting in further response.

Confounding the issue of new mutations is the appearance of homozygotes involving recessive alleles that were initially present at a low frequency. If a recessive allele is present as a single copy, the expected time (conditional on it not being lost by drift) until the first appearance of a homozygote in a diploid population with an effective size of $ N_e $ is approximately $ 2N_e^{1/3} $ generations, with the appearance time following a nearly geometric distribution (Robertson 1978; Karlin and Tavaré 1980, 1981a, 1981b; Santago 1989). Because $ N_e \leq 500 $ for most selection experiments, any rare recessives that are initially present (and not lost by drift) will be expressed as homozygotes by around generation 15.

Our discussions of the nature of long-term response with mutational input largely follow Hill's pioneering treatment (1982a, 1982b). We start by assuming complete additivity. Recall from Chapter 11 (and LW Chapter 12) that one measure of mutational input is $ \sigma_m^2 $, the amount of new additive variance produced by mutation in each generation. Consider the $ i $th locus, where each allele mutates to a new one with a per-generation rate of $ \mu_i $. The incremental-mutation model is assumed: when an allele $ A $ mutates to a new allele $ A' $, the genotypic values of $ AA' $ and $ A'A' $ are $ g_{AA} + \alpha $ and $ g_{AA} + 2\alpha $, where $ g_{AA} $ is the genotypic value of $ AA $. This model assumes that the genotypic value of the new mutant is the value of its parental allele plus an increment value, $ \alpha $. The distribution of $ \alpha $ is assumed to be independent of the value of the parental allele, with $ E[\alpha_i] = 0 $ and $ E[\alpha_i^2] = \sigma^2(\alpha_i) $. For $ n $ loci, the mutational variance for a diploid species becomes $$ \sigma_{m}^{2}=2\sum_{i=1}^{n}\mu_{i}\sigma^{2}(\alpha_{i}) $$

We first consider the infinitesimal model before examining a more general model and the consequences of dominance. An extensive discussion of different mutational models is given in Chapter 28.

---

## chapter26_021 · Long-term Response: Introduction / Results for the Infinitesimal Model

**[推导 Derivation]**

We start by assuming complete additivity and ignore any effects of gametic-phase disequilibrium. From Equation 11.20b, the expected additive genetic variance at generation t is

> **Formula (26.27)** · `26.27` · source: `chapter26_block_128` · Results for the Infinitesimal Model
>
> $$ \sigma_{A}^{2}(t)\simeq2N_{e}\sigma_{m}^{2}+\left[\sigma_{A}^{2}(0)-2N_{e}\sigma_{m}^{2}\right]\exp(-t/2N_{e}) $$


**[推导 Derivation]**

Setting $ \sigma_{A}^{2}(0)=0 $ gives the additive variance contributed entirely from mutation as

> **Formula (26.28a)** · `26.28a` · source: `chapter26_block_129` · Results for the Infinitesimal Model
>
> $$ \sigma_{A,m}^{2}(t)\simeq2N_{e}\sigma_{m}^{2}\left[1-\exp(-t/2N_{e})\right] $$


**[推导 Derivation]**

Hence, the rate of response at generation t from mutational input is

> **Formula (26.28b)** · `26.28b` · source: `chapter26_block_130` · Results for the Infinitesimal Model
>
> $$ r_{m}(t)=\overline{\imath}\frac{\sigma_{A,m}^{2}(t)}{\sigma_{z}}\simeq2N_{e}\overline{\imath}\frac{\sigma_{m}^{2}}{\sigma_{z}}\left[1-\exp(-t/2N_{e})\right] $$


where we have made the usual assumption that the phenotypic variance, $ \sigma_z^2 $, does not significantly change over time and that any disequilibrium is ignored. For $ t \gg 2N_e $, the per-generation response approaches an asymptotic limit of

> **Formula (26.29)** · `26.29` · source: `chapter26_block_130` · Results for the Infinitesimal Model
>
> $$ r_{m}(\infty)=2N_{e}\bar{\imath}\frac{\sigma_{m}^{2}}{\sigma_{z}} $$


**[命题 Proposition]**

Assuming $ \sigma_A^2(0) = 0 $, Equation 26.28b shows that half this rate is achieved by $ t \simeq 1.4N_e $, independent of the value of $ \sigma_m^2 $ (Hill 1982a, 1982b). There are several ways to intuit the value of this asymptotic limit. From Robertson’s theory, we expect the final response to be $ 2N_e $ times the initial response $ R(1) $, which, for new mutants arising in any particular generation, is $ R(1) = \bar{\tau} \sigma_m^2 / \sigma_z $. Alternatively, recall (Equation 11.20c) that the equilibrium additive variance (assuming pure drift) is $ 2N_e \sigma_m^2 $, which (upon recalling Equation 13.6b) recovers Equation 26.29. The assumption of the infinitesimal model implies vanishingly small selection coefficients at each underlying locus, which makes them effectively neutral.

**[推导 Derivation]**

Summing Equation 26.28b over generations (using the approximation given by Equation 7.28b) yields a cumulative response due to new mutation of

> **Formula (26.30a)** · `26.30a` · source: `chapter26_block_132` · Results for the Infinitesimal Model
>
> $$ R_{m}(t)=\sum_{\tau=1}^{t}r_{m}(\tau)\simeq2N_{e}\overline{\imath}\frac{\sigma_{m}^{2}}{\sigma_{z}}\bigg(t-2N_{e}[1-\exp(-t/2N_{e})]\bigg) $$


as found by Hill (1982a, 1990) and Weber and Diggins (1990). An approximation for genes of sufficiently large effect ($ |a| \gg \sigma_z/N\bar{i} $) is to consider them as being essentially fixed instantaneously, in which case only the first term in the large parentheses in Equation 256.30a need be included, and the response approaches

> **Formula (26.30b)** · `26.30b` · source: `chapter26_block_132` · Results for the Infinitesimal Model
>
> $$ R_{m}(t)=2t N_{e}\bar{\imath}\frac{\sigma_{m}^{2}}{\sigma_{z}} $$


as suggested by Hill (1982a). Note by comparison with Equation 26.29 that the instantaneous fixation assumption is equivalent to assuming that the asymptotic rate of response applies from generation 1.

**[推导 Derivation]**

Combining the mutational response with the response due to genetic variation that was originally in the base population (Equation 26.15a) yields an expected cumulative response of

> **Formula (26.30c)** · `26.30c` · source: `chapter26_block_133` · Results for the Infinitesimal Model
>
> $$ R(t)=2N_{e}\frac{\overline{\imath}}{\sigma_{z}}\left[t\sigma_{m}^{2}+\left(1-\exp(-t/2N_{e})\right)\left(\sigma_{A}^{2}(0)-2N_{e}\sigma_{m}^{2}\right)\right] $$


The $ t\sigma_m^2 $ term, which represents the asymptotic response, eventually dominates for sufficiently large $ t $. The product term in the braces represents the transient effect of the initial additive variance, and it is zero if the population starts at the mutation-drift equilibrium (i.e., $ \sigma_A^2(0) = 2N_e\sigma_m^2 $).

Of considerable interest is the expected number of generations until the selection response from mutational input exceeds that contributed by the initial variation. Let $ t^{*} $ be the generation when the per-generation response from both sources is equal. At this value, the initial additive variance remaining equals the new additive variance cumulatively generated, or $$ \sigma_{A}^{2}(0)\exp(-t^{*}/2N_{e})=2N_{e}\sigma_{m}^{2}\left[1-\exp(-t^{*}/2N_{e})\right] $$

**[推导 Derivation]**

This equation has the solution

> **Formula (26.31a)** · `26.31a` · source: `chapter26_block_136` · Results for the Infinitesimal Model
>
> $$ t^{*}=2N_{e}\ln(1+\Psi)\quad where\quad\Psi=\frac{\sigma_{A}^{2}(0)}{2N_{e}\sigma_{m}^{2}} $$


**[推导 Derivation]**

Denoting the initial heritability by $ h^{2} $ and recalling that $ \sigma_{E}^{2} = (1 - h^{2})\sigma_{z}^{2} $ yields $$ \frac{\sigma_{A}^{2}(0)}{\sigma_{m}^{2}}=\frac{h^{2}\sigma_{z}^{2}}{\sigma_{m}^{2}}=\frac{h^{2}}{\sigma_{m}^{2}/\sigma_{z}^{2}}=\frac{h^{2}}{(1-h^{2})\sigma_{m}^{2}/\sigma_{E}^{2}}=\frac{h^{2}}{(1-h^{2})h_{m}^{2}} $$ showing that

> **Formula (26.31b)** · `26.31b` · source: `chapter26_block_137` · Results for the Infinitesimal Model
>
> $$ \Psi=\frac{h^{2}}{\left(1-h^{2}\right)2N_{e}h_{m}^{2}} $$


---

## chapter26_022 · Long-term Response: Introduction / Results for the Infinitesimal Model

**[推导 Derivation]**

The average value of the mutational heritability, $ h_m^2 = \sigma_m^2 / \sigma_E^2 $, is approximately 0.005 (LW Table 12.1). With this value, $ t^* $ is only rather weakly dependent on $ N_e $ (Figure 26.8). If $ \Psi \ll 1 $, meaning that the expected additive variance at the mutation-drift equilibrium exceeds the initial additive variance ($ \sigma_A^2(0) \ll 2N_e \sigma_m^2 $), the approximation $ \ln(1 + x) \simeq x $ for small values of $ |x| $ yields

> **Formula (26.31c)** · `26.31c` · source: `chapter26_block_138` · Results for the Infinitesimal Model
>
> $$ \begin{align*}t^*\simeq2N_e\Psi={h^2\over(1-h^2)h_m^2}\end{align*} $$


Using $ h_m^2 = 0.005 $ yields $ t^* \simeq 200h^2/(1 - h^2) $. For $ h^2 $ values of 0.05, 0.10, and 0.25, respectively, this translates into 11, 22, and 67 generations until the per-generation response from mutational input exceeds that due to initial variation. For $ h_m^2 = 0.001 $, these values increase approximately five-fold to 52, 111, and 250 generations. Comparing these approximate results (from Equation 26.31c) with their exact values (Equation 26.31a) shows that Equation 26.31c tends to overestimate the true value of $ t^* $ when $ N_e $ is small (see Figure 26.8).

Recalling the discussion following Equation 26.27, it is important to stress that our expression for the half-life of selection response (from the initial genetic variation) assumes that drift dominates and tends to yield overestimates when selection is moderate to strong. Likewise, we expect that the infinitesimal model underestimates the changes in allele frequencies of new mutations under moderate to strong selection. Thus, Equation 26.31a is best considered as an upper bound for the number of generations after which mutation is expected to dominate.

**[示例 Example]**

> **Example 26.5** · ref: `26.5` · source: `chapter26_022.json` · blocks 3–3
>
> Example 26.5. Yoo (1980a) observed a steady, and reasonably constant, increase in Drosophila abdominal bristle number over 80 generations of selection (Figure 25.8). In particular, an increase of about 0.3 bristles per generation was observed over generations 50 to 80. Assuming the infinitesimal model, how much of this response is due to mutational input? Yoo's base population had $ \sigma_E^2 \simeq 4 $, $ \sigma_z^2 \simeq 5 $, $ h^2 \simeq 0.2 $, and $ \bar{\imath} \simeq 1.4 $, with 50 pairs of parents chosen in each generation. Taking $ \sigma_m^2 \simeq 0.001\sigma_E^2 $ (the average for abdominal bristles in LW Table 26.1) gives $ h_m^2 = 0.001 $. Assuming $ N_e \simeq 60 $, Equation 26.31b yields $$ \Psi=\frac{0.2}{\left(1-0.2\right)2\cdot60\cdot0.001}=2.083 $$ Applying Equation 26.31a, $$ t^{*}=2\cdot60\ln(1+2.083)=135 $$ The approximation given by Equation 26.31c (which assumes that $ \Psi \ll 1 $) yields an overestimate of $ t^* = 167 $ generations. The expected asymptotic additive variance is $$ \widetilde{\sigma}_{A}^{2}=2N_{e}\sigma_{m}^{2}=2\cdot60\cdot0.004=0.48 $$ yielding an expected asymptotic rate of response of $$ r=\bar{\imath}\frac{\widehat{\sigma}_{A}^{2}}{\widehat{\sigma}_{z}}=\bar{\imath}\frac{\widehat{\sigma}_{A}^{2}}{\sqrt{\widehat{\sigma}_{A}^{2}+\sigma_{E}^{2}}}=1.4\cdot\frac{0.48}{\sqrt{0.48+4}}\simeq0.32 $$ While the observed rate of selection response (0.3) over generations 50 to 80 is close to the expected asymptotic rate, the expected time for half of the response to be from new mutations, $ t^* = 135 $, exceeds 80, showing that (under the infinitesimal assumptions) most of the response is still from the initial variation. Applying Equation 26.28b, the expected single-generation response from new mutational input at generation 60 has only reached a fraction $$ 1-e^{-t/(2N_{e})}=1-e^{-60/120}\simeq0.40 $$ of its expected asymptotic rate, yielding $ 0.4 \cdot 0.32 = 0.13 $ as the expected response due to new mutants at $ t = 60 $. Assuming the phenotypic variance remains relatively constant, with $ \sigma_z^2 \simeq 5 $, the expected contribution at generation 60 from initial variation is $$ \bar{\imath}\frac{\sigma_{A,0}^{2}(t)}{\sigma_{z}}=\bar{\imath}\frac{h^{2}(0)\cdot\sigma_{z}^{2}\cdot e^{-t/(2N_{e})}}{\sigma_{z}}=1.4\cdot\frac{0.2\cdot5\cdot e^{-60/120}}{\sqrt{5}}\simeq0.38 $$ Adding these two sources returns an expected total rate of response of $ 0.38 + 0.13 = 0.51 $ bristles per generation, 75% of which is due to the initial variation. While the predicted rate of 0.51 is larger than the observed rate, opposing natural selection likely slowed down the selection response in Yoo's lines, as evidenced by the rather sharp decay in response upon relaxation of selection, as well as the presence of segregating lethals within responding lines (Yoo 1980b). A complication with applying this theory is that the presence of major alleles both decreases the time to lose initial variation (when they reside in the base population) and increases the expected response from new mutants (when they arise as mutations). Both of these factors result in a larger role for mutational input than predicted from the infinitesimal model (i.e., a much shorter value for $ t^{*} $). Applying the approximation for mutations of large effect (Equation 26.30b) using the parameters in this example, the per-generation response from mutation is 0.32. Assuming that the initial variation decays according to the infinitesimal model gives a total rate of response (at generation 60) of $ 0.38 + 0.32 = 0.70 $, so mutation now accounts for a fraction, $ 0.32 / 0.70 = 0.46 $, of the total response. Further, when major alleles are present in the base population, the initial variation declines even faster than predicted by Equation 26.15a (as selection augments the amount of allele-frequency change expected under drift alone), suggesting that an even higher percentage of response may be due to new mutation.


---

## chapter26_023 · Long-term Response: Introduction / Expected Asymptotic Response Under More General Conditions

**[推导 Derivation]**

The infinitesimal model assumes that allele-frequency changes are due entirely to drift. Clearly, selection can also change allele frequencies, and in this case other methods of analysis are required. One approach (Hill 1982a, 1982b) is to consider the expected contribution resulting from the eventual fixation by drift and selection of some of the new mutations that arise in each generation. Provided mutation and selection remain constant over time, at equilibrium the rate of response equals this expected per-generation contribution. Assuming M adults are measured, the frequency of a new mutant allele, $ A^* $, is $ 1/(2M) $. To allow for dominance, assume that the genotypic values of $ AA^* $ and $ A^*A^* $ are, respectively, incremented by $ \alpha(1+k) $ and $ 2\alpha $ relative to the value of AA. As before, we assume that the joint distribution of $ \alpha $ and $ k $ is independent of the genotypic value of the parental allele. Let $ f(\alpha, k) $ denote this joint probability density function and let $ \mu = \sum \mu_i $ be the total gametic mutation rate for the trait of interest. The expected contribution to the total response from a new mutant appearing as a single copy becomes $ 2\alpha \cdot u(1/[2M], \alpha, k) $, the change in genotypic value if the new allele is fixed times its probability of fixation (the latter can be obtained by Equation 7.18a, using the fitnesses given by Equation 25.4). Because $ 2M\mu $ new mutants appear each generation, the asymptotic rate of response is

> **Formula (26.32)** · `26.32` · source: `chapter26_block_146` · Expected Asymptotic Response Under More General Conditions
>
> $$ \begin{align*}r_{m}(\infty)&=2M\mu E\bigg[2\alpha\cdot u\left(\frac{1}{2M},\alpha,k\right)\bigg]\\&=2M\mu\int_{-\infty}^{\infty}\int_{-\infty}^{\infty}2\alpha\cdot u\left(\frac{1}{2M},\alpha,k\right)f(\alpha,k)d\alpha d k\end{align*} $$


Note that the expected asymptotic rate depends critically on the exact shape of the distribution of mutational effects (a point echoed in Chapter 28). Fortunately, some fairly general results emerge by using simple approximations for the probability of fixation (similar to Equations 7.19a and 7.19b; see Hill 1982a, 1982b for details).

**[推导 Derivation]**

Consider first the case where all new mutants are additive $ (k = 0) $. Hill (1982b) found that, provided major alleles are not common among new mutants,

> **Formula (26.33a)** · `26.33a` · source: `chapter26_block_148` · Expected Asymptotic Response Under More General Conditions
>
> $$ r_{m}(\infty)\simeq2N_{e}\bar{\imath}\mu\frac{E^{+}[\alpha^{2}]}{\sigma_{z}}=\frac{4N_{e}\bar{\imath}\sigma_{m}^{2}}{\sigma_{z}}\frac{E^{+}[\alpha^{2}]}{E[\alpha^{2}]} $$


where

> **Formula (26.33b)** · `26.33b` · source: `chapter26_block_148` · Expected Asymptotic Response Under More General Conditions
>
> $$ E^{+}[\alpha^{2}]=\int_{0}^{\infty}\alpha^{2}f(\alpha)d\alpha $$


is the average squared increment of favorable alleles (i.e., those with $ \alpha > 0 $). If the distribution of mutational increments, $ f(\alpha) $, is symmetric about zero, then $ E^{+}[\alpha^2] = E[\alpha^2]/2 $, as $ \int_0^\infty f(\alpha) \, d\alpha = 1/2 $, and the asymptotic response reduces to Equation 26.29. When major alleles are common among new mutants, correction terms involving $ E^{+}[\alpha^3] $ appear; see Hill (1982b) for details. With divergent selection (the divergence between an up- and down-selected line; Chapter 25), effects due to asymmetry in $ f(\alpha) $ cancel, and the asymptotic rate of divergence between high and low lines is simply twice the rate (for single-direction selection) predicted from the infinitesimal model, namely,

> **Formula (26.33c)** · `26.33c` · source: `chapter26_block_148` · Expected Asymptotic Response Under More General Conditions
>
> $$ 4N_{e}\bar{\tau}\frac{\sigma_{m}^{2}}{\sigma_{z}} $$


independent of the shape of $ f(\alpha) $. The effect of linkage on asymptotic response was examined by Keightley and Hill (1983, 1987), who found it to generally be small, with the relative effects of linkage increasing with $ \sigma_{m}^{2} $ and $ N_{e} $.

Hill and Keightley (1988) allowed for the possibility that new mutations are also influenced by natural selection. If both the trait and fitness effects of mutations are small, the distribution of $ \alpha $ is symmetric, and natural selection effects are also symmetric in $ \alpha $ (e.g., the change in fitness is a function only of $ |\alpha| $, there is no change in the asymptotic rate of response. If these assumptions are violated, the asymptotic rate can be reduced.

**[推导 Derivation]**

To allow for dominance, we continue to assume the incremental mutation model. From LW Equation 4.12a, the additive variance contributed by a rare allele is $$ 2p(1-p)\alpha^{2}[1+k(1-2p)]^{2}\simeq2p\alpha^{2}(1+k)^{2} $$ yielding a contribution to $ \sigma_{A}^{2} $ from a single new mutation, where $ p_{0}=1/(2M) $, of approximately $$ \alpha^{2}(1+k)^{2}/M $$ Because the expected number of new mutations per locus in any given generation is $ 2M\mu $, the expected additive variance contributed in each generation by new mutations at a given locus is $$ 2M\mu E[\alpha^{2}(1+k)^{2}/M]=2\mu E[\alpha^{2}(1+k)^{2}] $$ where the expectation is taken over the joint distribution of $ \alpha $ and k values in new mutants. Summing over all loci, the expected new additive variance contributed each generation (in the absence of linkage disequilibrium) is

> **Formula (26.34a)** · `26.34a` · source: `chapter26_block_150` · Expected Asymptotic Response Under More General Conditions
>
> $$ \sigma_{m}^{2}=2\sum_{i=1}^{n}\mu_{i}E[\alpha^{2}(1+k)^{2}]=2\mu E[\alpha^{2}(1+k)^{2}] $$


as obtained by Hill (1982b). The last equality assumes the distribution of mutational values and rates to be the same at each locus. When all mutations are additive (k = 0) and symmetric (E[] = 0), this reduces to our previous definition of $ \sigma_m^2 $. More generally, with complete additivity, but removing the assumption that E[] = 0, we have

> **Formula (26.34b)** · `26.34b` · source: `chapter26_block_150` · Expected Asymptotic Response Under More General Conditions
>
> $$ \sigma_{m}^{2}=2\mu E[\alpha^{2}] $$


while with complete dominance $ (k=1) $,

> **Formula (26.34c)** · `26.34c` · source: `chapter26_block_150` · Expected Asymptotic Response Under More General Conditions
>
> $$ \sigma_{m}^{2}=2\mu E\big[\left(2\alpha\right)^{2}\big]=8\mu E\big[\alpha^{2}\big] $$


For the same $ \alpha $ and $ \mu $ values, the mutational variance with complete dominance is four times larger than that for complete additivity (as the genotypic value of heterozygotes is doubled, which increases the variance by $ 2^2 = 4 $).

**[推导 Derivation]**

For the case of complete dominance, Hill (1982b) found that the asymptotic rate of response is approximately

> **Formula (26.35a)** · `26.35a` · source: `chapter26_block_152` · Expected Asymptotic Response Under More General Conditions
>
> $$ r_{m}(\infty)\simeq16N_{e}\bar{\imath}\mu E^{+}\left[\alpha^{2}\right]/\sigma_{z} $$


where $ E^{+} $ [α²] is defined by Equation 26.33b. With a symmetric distribution of mutational effects, Equation 26.35a reduces to

> **Formula (26.35b)** · `26.35b` · source: `chapter26_block_152` · Expected Asymptotic Response Under More General Conditions
>
> $$ r_{m}(\infty)\simeq N_{e}\bar{\imath}\frac{\sigma_{m}^{2}}{\sigma_{z}} $$


where $ \sigma_m^2 $ is given by Equation 26.34c. For the same values of $ \sigma_m^2 $, the response when all mutants are completely dominant is only half the expected response when alleles are additive (compare Equations 26.29 and 26.35b). However, for fixed values of $ \mu $ and $ E\left[\alpha^2\right] $, $ \sigma_m^2 $ is larger with complete dominance (compare Equations 26.34b and 26.34c), and the rate of response under dominance is twice as large as that expected for complete additivity.

**[推导 Derivation]**

If alleles are completely recessive, allelic effects are small, and the distribution of mutational effects is symmetric, the asymptotic response is approximately

> **Formula (26.36a)** · `26.36a` · source: `chapter26_block_153` · Expected Asymptotic Response Under More General Conditions
>
> $$ r_{m}(\infty)\simeq2N_{e}\bar{\imath}\mu E\left[\alpha^{2}\right]/\sigma_{z} $$


**[推导 Derivation]**

(Hill 1982b). For recessives with large effects (cf. Equation 7.19b)

> **Formula (26.36b)** · `26.36b` · source: `chapter26_block_154` · Expected Asymptotic Response Under More General Conditions
>
> $$ r_{m}(\infty)\simeq2\mu E^{+}\left[\alpha^{3/2}\right]\sqrt{\frac{2N_{e}\bar{\tau}}{\pi\sigma_{z}}} $$


Thus, the limiting response when all new mutations are recessive is not predictable from $ \sigma_m^2 $, even if mutational effects are symmetrically distributed. With recessive major alleles, the selection response scales as $ \sqrt{N_e} \bar{\imath} $, and hence it increases much more slowly with $ N_e \bar{\imath} $ than with complete dominance or additivity.

When loci are linked, the asymptotic response is reduced, but the effect is small unless linkage is tight, as might occur with a few small chromosomes (Keightley and Hill 1983). As mentioned previously, reduction in response also occurs if loci influencing the trait are linked to loci under natural selection.

---

## chapter26_024 · Long-term Response: Introduction / Additional Models of Mutational Effects

**[命题 Proposition]**

A critical assumption in any analysis of mutational response is the mutational model. Given a current allelic effect of $a$, what can we say about the value, $a^{*}$, from a mutation in this allele? All of the above results make the incremental-mutation model assumption: $a^{*}=a+\alpha$, with the increment $\alpha\sim(0,\sigma_{\alpha}^{2})$. This Brownian motion model (Appendix 1) implies that the additive variance (for neutral alleles) will be unbounded as $N_{e}$ increases (Chapters 11 and 28). As introduced in Chapter 11, the house-of-cards (HOC) is another potential mutation model. Here, each new allelic value is drawn from a constant distribution, independent of the current value of the parental allele, namely the HOC distribution: $ a^* = \alpha $, with $ \alpha \sim (0, \sigma_\alpha^2) $. Li and Enfield (1992) examined the long-term response under such a model. Starting with a population with no initial variation, they found that mutation increases the genetic variation up to some maximal value, after which it declines, with the time until this maximum is reached increasing with the number of loci. Li and Enfield only considered response over the first 120 generations, which was less than the smallest $ N_e $ value (150) in any of their simulations. Hence, the nature of any limit, or any asymptotic response, was not determined. The expectation under an HOC model is that an apparent selection limit is approached, although the population can still respond, but at an ever-diminishing rate, as further gains require random draws of ever-greater outliers from the HOC distribution of allelic-effects at a given locus. This view has connections with models of adaptive walks based on extreme-value theory, which are examined in the next chapter. A finite-value version of the HOC model, assuming that there are only $ k $ possible alleles at a locus, was examined by Zeng et al. (1989). As expected, the $ k $-allele model results in an ultimate selection limit, as mutation cannot continue to generate better alleles indefinitely. In Chapter 11 we also introduced the Zeng-Cockerham model (Equation 11.23), $ a^* = \tau a + \alpha $, which recovers Brownian motion when $ \tau = 1 $, and the HOC model when $ \tau = 0 $. To our knowledge, selection limits under the Zeng-Cockerham model have not been examined.

A second, very important, consideration is the role of pleiotropic fitness effects. These mutational models predict (for constant value of $ \mu $) that the equilibrium variance should linearly increase with $ N_e $, at least when $ N_e $ is less than the reciprocal of the mutation rate (Chapter 11). However, even for modest $ N_e $, the predicted equilibrium variances are too large to be comparable with observations (with heritabilities approaching 1.0, while most heritabilities in actual populations are below 0.5). This contradiction between theory and data as $ N_e $ increases is analogous to the limited observed range for molecular heterozygosity, which (assuming $ \mu $ stays constant) should also approach one for large $ N_e $ (Chapter 2). If new mutations have pleiotropic fitness effects, the amount of usable variation will be overestimated at small $ N_e $ (the setting when $ \sigma_m^2 $ is measured). As detailed in Chapter 28, whether this results in a limiting value for $ \widetilde{\sigma}_A^2 $ as $ N_e \to \infty $ depends on very delicate features of the joint distribution of $ (s, \alpha) $ for values of $ s $ near zero.

---

## chapter26_025 · Long-term Response: Introduction / Optimizing the Asymptotic Selection Response

Because the asymptotic response is a function of $ N_e\bar{i} $, response is maximized by selection strategies that maximize this product. As was the case for maximizing long-term response (the total response using only the initial variation), there is a tradeoff in that the optimal short-term response (maximizing $ \bar{i} $) is in conflict with the optimal asymptotic response (because increasing $ \bar{i} $ decreases $ N_e $). If our choice is simply the fraction of individuals to save, the previous discussion on the optimal selection intensity for long-term response also applies to considerations of the asymptotic response.

However, the breeder or experimentalist can use other design options beyond simply tuning the selection intensity. We have generally been assuming individual (or mass) selection, which is based solely on an individual's phenotype. There are, however, numerous other selection schemes, such as those incorporating information on the phenotypes of relatives (e.g., family-index and BLUP selection; Chapters 21 and 13, respectively). Schemes incorporating such information can improve the accuracy of an individual's breeding value estimate, and hence improve the accuracy of short-term response. This can be seen by recalling (Equation 13.11c) that the single-generation response, R, for any particular selection scheme is given by $ R/(\bar{x}_{x}\sigma_{A})=\rho(x,A) $, where selection occurs on some index, x, and $ \rho(x,A) $ is the accuracy of the index (the correlation between an individual's index, x, and breeding values, A). Holding $ \bar{x} $ constant, the single-generation response increases with the accuracy, $ \rho(x,A) $, of the selection method. While different schemes can improve the short-term response over mass selection, what is their effect on asymptotic response? Once again, the answer is that schemes improving the short-term response usually do so at the expense of the asymptotic response.

**[推导 Derivation]**

Optimal asymptotic response occurs by maximizing the fixation probabilities of favorable QTLs, which amounts to maximizing $ N_{e}s $, where s is the selection coefficient on the QTL. For an additive trait, Hill (1985) and Caballero et al. (1996) generalized Equation 25.4 to show that

> **Formula (26.37)** · `26.37` · source: `chapter26_block_161` · Optimizing the Asymptotic Selection Response
>
> $$ s=\left(\overline{\imath}\frac{a}{\sigma_{z}}\right)\frac{\rho(x,A)}{h} $$


Note that $ \rho(x, A) = h $ for individual selection (the index is simply the trait value, x = z), recovering Equation 25.4. Fixation probabilities under different selection schemes with the same selection intensities are thus functions of the product $ N_e s $, which is proportional to $ N_e \rho(x, A) $. The tradeoff is that increasing $ \rho(x, A) $ typically decreases $ N_e $ by increasing the among-family variance in trait value (and hence in fitness). Thus, as was the case in our previous discussion on the optimal selection intensity, the optimal selection scheme for short-term response may differ from the optimal scheme for long-term response.

**[推导 Derivation]**

The accuracy, $ \rho $, depends on the genetic variance, and hence can change over time as these variances change. As shown in Chapters 24 and 25, predicting long-term changes in variances can be extremely difficult. Once again, the analysis is greatly simplified by assuming the infinitesimal model. Under this model, the additive genetic variance eventually converges to a value of $ \widetilde{\sigma}_{A}^{2}=2N_{e}\sigma_{m}^{2} $. The effect of different selection schemes on the equilibrium additive variance (and $ \rho $) is then entirely determined by the effective population size that each scheme generates. In comparing two different selection schemes (i and j) with the same selection intensity, Wei et al. (1996) showed that the ratio of asymptotic responses becomes

> **Formula (26.38)** · `26.38` · source: `chapter26_block_163` · Optimizing the Asymptotic Selection Response
>
> $$ \frac{\widetilde{R}_{i}}{\widetilde{R}_{j}}=\frac{\widetilde{\rho}(i)\widetilde{\sigma}_{A}(i)}{\widetilde{\rho}(j)\widetilde{\sigma}_{A}(j)}=\frac{\widetilde{\rho}(i)}{\widetilde{\rho}(j)}\sqrt{\frac{N_{e}(i)}{N_{e}(j)}} $$


where a tilde denotes an equilibrium value and $ \widetilde{\rho}(i) $ denotes the accuracy (at the equilibrium variances) of selection scheme i. The careful reader will note that the effect of $ N_e $ is twofold—there is a direct effect (the square root of the $ N_e $ ratio) and also an indirect effect through the ratio of the $ \widetilde{\rho} $ (which is a function of $ \widetilde{\sigma}_A $, and hence of $ N_e $).

**[示例 Example]**

> **Example 26.6** · ref: `26.6` · source: `chapter26_025.json` · blocks 5–5
>
> Example 26.6. Consider the asymptotic response to mass (m) versus within-family (w) selection. Under within-family (full-sib) selection, $ N_{e(w)} \simeq 2N $, as the among-family variance is zero (Equation 3.4). In contrast, $ N_{e(m)} < N $, with the difference between $ N_{e(m)} $ and N increasing with the selection intensity and heritability (Equation 26.8), implying that $$ \sqrt{\frac{N_{e(w)}}{N_{e(m)}}}\geq\sqrt{2} $$ (29.39a)
> 
> The accuracy for mass selection is given by $$ \rho(z,A)=\frac{\sigma(z,A)}{\sigma_{A}\sigma_{z}}=\frac{\sigma_{A}^{2}}{\sigma_{A}\sigma_{z}}=\frac{\sigma_{A}^{2}}{\sqrt{\sigma_{A}^{2}\left(\sigma_{A}^{2}+\sigma_{E}^{2}\right)}} $$ (29.39b) yielding an asymptotic accuracy as $$ \widetilde{\rho}(m)=\frac{\widetilde{\sigma}_{A}^{2}}{\sqrt{\widetilde{\sigma}_{A}^{2}(\widetilde{\sigma}_{A}^{2}+\sigma_{E}^{2})}}=\frac{2N_{e(m)}\sigma_{m}^{2}}{\sqrt{2N_{e(m)}\sigma_{m}^{2}(2N_{e(m)}\sigma_{m}^{2}+\sigma_{E}^{2})}} $$ (29.39c) as obtained by Wei et al. (1996).
> 
> Turning to within-family selection, let $ \overline{z}_{f} $ denote the family mean. Selection decisions are based on the value of $ z - \overline{z}_{f} $. Recalling our treatment of within-family selection from Chapter 21, the resulting accuracy for within-family (full-sib) selection becomes $$ \rho(w)=\rho(z-\overline{z}_{f},A)\simeq\frac{\sigma(z-\overline{z}_{f},A)}{\sqrt{\sigma^{2}(A)\sigma^{2}(z-\overline{z}_{f})}}\simeq\frac{\sigma_{A}^{2}/2}{\sqrt{\sigma_{A}^{2}(\sigma_{G w}^{2}+\sigma_{E_{s}}^{2})}} $$ (29.39d) where the last step ignores the effect of the number of sibs (n) in each family by assuming that n is large (see Chapter 21 for expressions for when n is small). The within-family genetic variance, $ \sigma_{Gw}^{2} $, equals $ \sigma_{A}^{2}/2 $ for a full-sib family with only additive effects, while the within-family environmental variance, $ \sigma_{E_{s}}^{2} $, equals $ \sigma_{E}^{2} $ under the assumption of no common-family effects (Chapter 21). We make these simplifying assumptions here, but more general expressions easily follow. At equilibrium $$ \widetilde{\rho}(w)=\frac{\widetilde{\sigma}_{A}^{2}/2}{\sqrt{\widetilde{\sigma}_{A}^{2}(\widetilde{\sigma}_{A}^{2}/2+\sigma_{E}^{2})}}=\frac{N_{e(w)}\sigma_{m}^{2}}{\sqrt{2N_{e(w)}\sigma_{m}^{2}(N_{e(w)}\sigma_{m}^{2}+\sigma_{E}^{2})}} $$ (29.39e)
> 
> (Wei et al. 1996). Applying Equation 26.39a along with Equations 26.39c and 26.39e yields $$ \frac{\rho_{(w,\infty)}}{\rho_{(m,\infty)}}\geq\frac{1}{\sqrt{2}} $$ $$ \frac{\widetilde{R}_{w}}{\widetilde{R}_{m}}=\left[\sqrt{\frac{N_{e(w)}}{N_{e(m)}}}\right]\left[\frac{\widetilde{\rho}_{(w)}}{\widetilde{\rho}_{(m)}}\right]\geq\sqrt{2}\frac{1}{\sqrt{2}}=1 $$
> 
> Thus, and hence $ \widetilde{R}_{w} \geq \widetilde{R}_{m} $. That is, for the same selection intensity, the asymptotic response is greater under within-family selection than under mass selection.
> 
> The effects of different selection schemes on the effective population size can be seen by considering the general weighted index of within- and among-family information,
> 
> > **Formula (26.40)** · `26.40` · source: `chapter26_block_169` · Optimizing the Asymptotic Selection Response
> >
> > $$ I=(z-\overline{z}_{f})+\lambda(\overline{z}_{f}-\overline{z})=(\mathrm{within-family})+\lambda\left(\mathrm{among-family}\right) $$
> 
> 
> where $z$ is an individual's phenotypic value, $\overline{z}_f$ is the mean of its family, and $\overline{z}$ is the grand mean. A number of selection schemes can be represented (either exactly or to a good approximation) by this index (Chapter 21). For example, $\lambda = 1$ corresponds to individual selection (as $I = z - \overline{z}$), while $\lambda = 0$ corresponds to strict within-family selection ($I = z - \overline{z}_f$). The accuracy of selection using this index with an appropriately chosen value of $\lambda$ is greater than the accuracy of individual selection ($\rho(I, A) > \rho(z, A)$; Equation 21.53b), and hence selection using the optimal index gives a greater short-term response than mass selection. To a first approximation, BLUP selection corresponds to this optimal index. Because the effective population size is reduced by inflating the among-family variance, the larger the value of $ \lambda $ in Equation 26.40, the greater is the reduction in $ N_{e} $. Larger values of $ \lambda $ place more weight on family information, resulting in more individuals from the best families being coselected. The reduction in $ N_{e} $ is greatest when heritability is small, as in these cases the index places the most weight on the among-family component. Yet, however, it is exactly this setting under which index and BLUP selection have the greatest short-term advantage over individual selection. Conversely, when care is taken to equalize the amount of inbreeding across methods, individual selection can produce a larger single-generation response than index selection or BLUP (Quinton et al. 1992; Andersson et al. 1998).
> 
> Can one balance this tradeoff between increased accuracy for short-term response using information from relatives versus inflation of the among-family variance (and the resulting reduction in the long-term response via reduction in $ N_e $) that these schemes produce? Several authors have proposed schemes for reducing the among-family variance following selection. Toro and colleagues (Toro and Nieto 1984; Toro et al. 1988; Toro and Pérez-Enciso 1990) suggested that selected individuals be mated in ways that minimize the coancestry between them. A slightly different strategy, compensatory mating, was suggested by Grundy et al. (1994). Here, individuals from families that are overrepresented following selection are mated to individuals from underrepresented families. This has the effect of reducing the cumulative effect of selection ($ Q_\tau $ in Equation 26.6c) by reducing the variance in family contribution. Grundy et al. also suggested a more subtle approach. They noted that by using slightly biased selection parameters in the index (for example, using upwardly biased estimates of $ h^2 $ when computing the optimal $ \lambda $), the slight reduction in the accuracy of the adjusted index from its optimal value is more than offset by a much smaller decrease in $ N_e $. They suggested that this approach, combined with compensatory mating, provides a simple way for ameliorating the reduction in $ N_e $. Verrier et al. (1993) also suggested that schemes placing slightly less emphasis on family information can, in small populations, give greater long-term response than BLUP selection. We examine the optimal control for inbreeding under BLUP in detail in Volume 3.
> 
> This tradeoff between optimal short-term versus optimal asymptotic response has economic consequences for breeders. While breeders are ultimately better off in the long run (in terms of total response) using selection schemes that are initially less accurate, competing breeders using the initially more accurate schemes will achieve a larger short-term response. Breeders must thus decide between staying in business over the short term versus experiencing a larger payoff (in terms of a greater response) over the long run.


---
