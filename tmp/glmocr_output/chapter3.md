<div align="center">

# The Genetic Effective Size of a Population

</div>

However, any theory which one finds uncomfortable but for which one cannot say exactly why, deserves serious consideration. Such an uncomfortable feeling signals a challenge to one or more of one's unexamined, and perhaps unjustified, assumptions. Van Valen (1976)

Throughout the preceding chapter, we assumed a population with an idealized set of Wright-Fisher features, including random mating within a homogeneous group of monoecious, self-compatible individuals with equal expected family sizes, discrete generations, and an absence of density fluctuations. Because almost all populations deviate from this ideal structure in one or more ways, and often substantially so, the relevance of the resultant theory might then seem in doubt. In fact, much of the theory of inbreeding and random genetic drift can be generalized to other types of population structures to a good approximation in a relatively simple manner. To accomplish this task, instead of relying on the total number of adult individuals (N) as a measure of population size, we construct a surrogate index that takes into account the deviations from the ideal model from a genetic perspective. Following the influential work of Wright (1931, 1938a, 1939), such an index has become widely known as $ N_{e} $ , the effective population size. With such a reparameterization, essentially all of the results in the preceding chapter hold when $ N_{e} $ is substituted for N. Buri's experiment (Chapter 2) is a case in point—a set of populations with actual size $ N=1 6 $ exhibited allele-frequency dynamics closely approximated by the expectations for an idealized Wright-Fisher population with an effective size of just ten individuals.

Because of its central role in defining levels of variation within populations, the rate of divergence among populations, and the efficiency of natural selection, $ N_{e} $ is one of the most important parameters in population genetics. Although $ N_{e} $ is not as easily measured as the total (census) population size, as will be seen in the following sections, it is, at least in part, defined by observable demographic and mating-system properties of populations (Latter 1959; Lande and Barrowclough 1987; Crow and Denniston 1988). A central goal of this chapter is to illustrate that nearly every violation of the assumptions underlying the Wright-Fisher model leads to a reduction in $ N_{e} $ relative to N, thereby implicating a stronger role for genetic drift in evolution than might be surmised from estimates of total population sizes. We will progressively consider aspects of the mating system (including the possibility of self-fertilization, variation in the sex ratio, and variance in family size), age structure, temporal variation, and spatial structure.

In addition, we will show that the effective size of a population is often strongly influenced by the structural aspects of genomes, independent of population demographic features. The physical linkage of genes on chromosomes ties their mutual fates together, creating stochastic fluctuations of allele frequencies out of chance associations with other loci under selection. Thus, chromosomally regional variation in recombination rates and selection has the effect of creating variation in $ N_{e} $ among different loci in the same population. Tight linkage to a deleterious mutation can result in the loss of an otherwise neutral or beneficial allele from the population, whereas tight linkage to a beneficial mutation can result in hitchhiking to fixation.

This chapter focuses entirely on the concept of $ N_{e} $ from a theoretical perspective, with a goal of providing the reader with a qualitative understanding of the mechanistic determinants of this key population-genetic parameter. Chapter 4 will provide an overview of methods for the estimation of $ N_{e} $ using molecular markers in natural populations, which require no knowledge of a population's demographic features. A more thorough review of a number of the topics that we touch upon can be found in Caballero (1994), and although

we focus on autosomal loci, the general principles are readily extended to sex-linked loci (Caballero 1995; Nagylaki 1995; Wang 1997; Charlesworth 2001).

## GENERAL CONSIDERATIONS

An appreciation for the concept of effective population size can be gained by recalling that all members of an ideal monoecious population (consisting of hermaphrodites capable of random self-fertilization) contribute equally to the total gamete pool, with each successful gamete uniting randomly with another gamete derived from the total population of N individuals. Under these conditions, the probability that two uniting gametes are derived from the same parent is simply $ P=1 / N $ . However, many factors, including self-incompatibility, limited dispersal, differential productivity of gametes, and selection, can cause P to deviate from 1/N. To account for the joint influence of all of these factors and many others, we define P to be the reciprocal of the effective population size.

Using this definition of $ N_{e}=1 / P $ , many of the results in the previous chapter can be generalized, at least to a first-order approximation. Consider, for example, the expected dynamics of the inbreeding coefficient for a diploid, monoecious population. The probability that two uniting gametes are derived from the same parent is now $ 1 / N_{e} $ , in which case there is a 50% chance that they each carry copies of the same gene (i.e., they are identical by descent, one generation removed) and a 50% chance that they carry copies of genes from different parental chromosomes. In the latter case, the uniting genes may still be identical by descent from previous inbreeding with probability $ f_{t-1} $ . Finally, there is a $ 1-(1 / N_{e}) $ probability that the uniting gametes are derived from different parents, in which case there is again a probability $ f_{t-1} $ that they are identical by descent from previous inbreeding. (Here, we are assuming a population without spatial structure, so that the mean degree of inbreeding does not depend on the parental source of alleles.) Summing up the three ways by which identity-by-descent can arise between uniting gametes,

$$
\begin{array}{l} f _ {t} = \left(\frac {1}{N _ {e}}\right) \left(\frac {1}{2}\right) + \left(\frac {1}{2}\right) \left(\frac {1}{N _ {e}}\right) f _ {t - 1} + \left(1 - \frac {1}{N _ {e}}\right) f _ {t - 1} \\ = \frac {1}{2 N _ {e}} + \left(1 - \frac {1}{2 N _ {e}}\right) f _ {t - 1} \\ \end{array}
$$

This expression is identical in form to Equation 2.3, but with $ N_{e} $ replacing $ N. $

Under the above interpretation, $ N_{e} $ is the size of an ideal population that would exhibit the same amount of inbreeding as the population under consideration. Defined in this way, $ N_{e} $ is the inbreeding effective size. There are, however, numerous additional ways to define the effective size of a population. One can, for example, define the variance effective size as the N that, when applied to Equation 2.14a, yields the temporal variance in allele-frequency change exhibited by a nonideal population. Crow (1954) emphasized that the inbreeding effective size is most closely related to the number of parents (or the number of grandparents if selfing does not occur) because it is based upon the probability of uniting gametes coming from the same ancestor. In contrast, the variance effective size, which is associated with allele-frequency drift resulting from gamete sampling, is primarily a function of the number of offspring produced. Thus, in an expanding or declining population, the rates of inbreeding and allele-frequency drift can differ in any particular generation (Templeton 2006). However, for populations with stable size, inbreeding and variance effective sizes are generally equivalent, and in the long run this is even true for fluctuating populations because both measures depend on the same sequence of adult population sizes (Caballero 1994; Whitlock and Barton 1997). More discourse on these issues may be found in Crow and Morton (1955), Kimura and Crow (1963b), Crow and Kimura (1970), Crow and Denniston (1988), and Caballero (1994). Unless stated otherwise, the following discussion will assume populations of constant size.

Before proceeding, it bears emphasizing that random genetic drift is a result of two

stochastic processes. First, in sexual species, segregation during meiosis leads to the random transmission of alleles from heterozygous parents, as there is a 50% chance for each alternative allele to be inherited by any given offspring. Second, variation in family size encourages lineages of alleles that happen to be contained within large families to expand at the expense of others. As we will see in the following sections, such variation arises by numerous mechanisms, including simple sampling of gametes, spatial population structure variation among the sexes, and trapping in various genetic backgrounds by linkage.

## MONOECY

To illustrate the mathematical approach to deriving expressions for $ N_{e} $ , we first generalize the concept of a monoecious, self-compatible population to allow for arbitrary gamete production by different individuals. As a reminder, monoecious (a botanical term) individuals are equivalent to hermaphrodites (a zoological term), with both terms referring to the situation in which individuals produce male and female gametes.

Let $ k_{i} $ be the number of gametes that the $ i $th parent contributes to offspring that survive to maturity, $ \mu_{k} $ and $ \sigma_{k}^{2} $ be the mean and variance of successful gamete production per individual, and $ N_{t-1} $ be the number of reproducing parents. Assuming that mating is random and isogamous (so that there is no distinction between male and female gametes), there are $ k_{i} ( k_{i}-1) $ ways in which the gametes of parent i can unite with each other, and summing over all parents, $ \sum_{i=1}^{N_{t-1}} k_{i} ( k_{i}-1) $ total ways by which gametes can unite by self-fertilization. Because a total of $ N_{t-1} \mu_{k} $ successful gametes are produced, the expected fraction of zygotes derived from the same parent is

$$
P _ {t} = \frac {1}{N _ {e}} = \frac {\sum_ {i = 1} ^ {N _ {t - 1}} k _ {i} \left(k _ {i} - 1\right)}{N _ {t - 1} \mu_ {k} \left(N _ {t - 1} \mu_ {k} - 1\right)}
$$

where the denominator is the total number of pairs of uniting gametes necessary to produce the next generation. This expression can be simplified greatly by noting that $ \sum_{i=1}^{N_{t-1}} k_{i} ( k_{i}- 1 ) / N_{t-1}=E ( k^{2} )-\mu_{k}=\sigma_{k}^{2}+\mu_{k} ( \mu_{k}-1 ), $ and that because all zygotes are derived from two gametes, $ N_{t-1}\mu_{k}=2N_{t}. $ Substituting into Equation 3.2 and inverting,

$$
N _ {e} = \frac {2 N _ {t} - 1}{\left(\sigma_ {k} ^ {2} / \mu_ {k}\right) + \mu_ {k} - 1}
$$

This shows that for a randomly mating monoecious population with discrete generations, the effective population size is a function of three measurable quantities: the actual population size $ ( N_{t} ) $ and the mean $ (\mu_{k}) $ and variance $ (\sigma_{k}^{2}) $ of successful gamete production. All other things being equal, variance in gamete production causes a reduction in $ N_{e} $ , as this inflates the representation of a fraction of the population in the descendant gene pool. Because such variation is expected to be the rule in natural populations occupying environments that are heterogeneous with respect to resource availability, on this basis alone, we can generally expect $ N_{e} $ to be less than the number of reproducing adults.

Equation 3.2 simplifies greatly under a number of conditions. For example, populations that are stable in size have, on average, two successful gametes per parent $ (\mu_{k}=2) $ ,leading to

$$
N _ {e} = \frac {4 N - 2}{\sigma_ {k} ^ {2} + 2}
$$

If we further assume that each parent produces the same number of potential gametes (returning us to the ideal random-mating population), an explicit statement can also be made about $ \sigma_{k}^{2} $ . In this case, for any particular draw from the gamete pool, the variance in the number of gametes derived from a particular parent (0 or 1) is $ (1 / N)[1-(1 / N)] $

(from the properties of a binomial distribution), and because a total of 2N gametes are drawn, $ \sigma_{k}^{2}=2[1-(1/N)] $ . Note that this result is very close to the Poisson expectation of $ \sigma_{k}^{2}=2 $ with completely random gamete production (because the variance of a Poisson equals the mean), with the slight deviation resulting because we assume a fixed population size. Substitution of the exact expression into Equation 3.4 yields $ N_{e}=N $ , showing that the inbreeding effective size of an ideal random-mating population is indeed equal to the number of reproductive adults in the previous generation.

In contrast, in the opposite, and extreme, situation in which all parents produce exactly two progeny (such that $ \sigma_{k}^{2}=0 $ and $ \mu_{k}=2 $), $ N_{e}=2 N-1\simeq 2 N $ . This shows that the elimination of variance in family size results in the effective population size being twice the actual number of breeding adults, a feature that is often exploited in breeding schemes to minimize the amount of inbreeding.

There are a number of ways in which the breeding systems of a monoecious species can deviate from the assumptions made in the preceding derivations. Consider, for example, species with self-incompatibility, in which case identity-by-descent for pairs of uniting gametes comes through grandparents rather than parents. If we now let $ k_{i} $ be the number of successful gametes for individual i in generation t-2, and again assume random mating, there are $ 2 k_{i} ( k_{i}-1) $ ways in which pairs of genes from i can unite through matings in the parental generation t-1 (the 2 arising because we assume that each individual can serve as a mother or father). Because there are $ N_{t-2}\mu_{k}/2 $ parents in generation t-1, there are $ 2(N_{t-2}\mu_{k}/2)[(N_{t-2}\mu_{k}/2)-1]$ ways of drawing different parents, and $ 4\cdot 2(N_{t-2}\mu_{k}/2)[(N_{t-2}\mu_{k}/2)-1]$ ways of drawing gene pairs (the 4 because each parent carries two genes). Therefore, the probability that a generation- t individual carries a pair of genes derived from the same grandparent is

$$
P _ {t} = \frac {1}{N _ {e}} = \frac {\sum_ {i = 1} ^ {N _ {t - 2}} k _ {i} \left(k _ {i} - 1\right)}{N _ {t - 2} \mu_ {k} \left(N _ {t - 2} \mu_ {k} - 2\right)}
$$

Employing the same kinds of substitutions used for Equation 3.3,

$$
N _ {e} = \frac {2 \left(N _ {t - 1} - 1\right)}{\left(\sigma_ {k} ^ {2} / \mu_ {k}\right) + \mu_ {k} - 1}
$$

and for constant $ N $ (which implies $ \mu_{k}=2 $),

$$
N _ {e} = \frac {4 (N - 1)}{\sigma_ {k} ^ {2} + 2}
$$

For populations that are moderately large and stable in size, Equations 3.4 and 3.7 give essentially the same answer, $ N_{e}\simeq 4 N / (\sigma_{k}^{2}+2) $ , demonstrating that the prohibition of selfing has a negligible influence on $ N_{e} $ unless the total population size is tiny. The reason for this is that under random mating the increment in inbreeding resulting from self-fertilization is a transient event that can be completely undone in the following generation.

A second potential complication is that in most hermaphroditic species, there is a distinction between male and female gametes (anisogamy), so that even with selfing, only a fraction of potential gamete pairs are capable of spawning a successful zygote. When mating is random but selfing is prohibited, the effective population size is the same under isogamy and anisogamy, and Equation 3.6 still applies (Crow and Denniston 1988). However, with selfing permitted,

$$
N _ {e} = \frac {N _ {t - 1}}{\left(4 \sigma_ {o , p} / \mu_ {k} ^ {2}\right) + 1}
$$

where $ \sigma_{o,p} $ is the covariance of the numbers of successful male (p, pollen) and female (o ovule) gametes per parent (Crow and Denniston 1988). If $ \sigma_{o,p} $ is positive, as might be

expected in a spatially heterogeneous environment where some individuals acquire more resources than others, the effective population size will be less than the observed size. However, if $ \sigma_{o,p} $ is negative, as might be expected when there is a trade-off between male and female function, $ N_{e} $ can exceed $ N_{t-1} $ . This results because a negative covariance in male and female gamete production reduces the variance in family size.

Example 3.1. Hedgecock (1994) suggested that marine organisms with high fecundities and broadcast spawning may have effective population sizes that are orders of magnitude smaller than the absolute number of potential breeders. This situation can arise if vagaries in oceanographic conditions are such that only a small fraction of adults produce gametes at points in time and space that allow recruitment to the next generation. Suppose the total adult population size is N, whereas only $ N_{p} $ individuals contribute equally to the breeding pool. Such a situation is sustainable if reproductive adults can individually produce an average of $ 2 N / N_{p} $ gametes (and many marine species are capable of producing many tens of thousands of gametes). Given such a situation, $ N_{p} $ individuals have expected family sizes of $ 2 N / N_{p} $ , whereas $ (N-N_{p}) $ have zero expected reproductive success, which results in an expected family-size variance among all N individuals of $ 4[ ( N / N_{p} )-1 ] $ (Hedrick 2005). Using the logic outlined in the paragraph below Equation 3.4, the additional variance in reproductive success among spawning individuals resulting from random gamete sampling is equal to

$$
\left\{\left(\frac {N _ {p}}{N}\right) \cdot 2 N \cdot \left(\frac {1}{N _ {b}}\right) \left[ 1 - \left(\frac {1}{N _ {b}}\right) \right] \right\} + \left\{\left[ 1 - \left(\frac {N _ {b}}{N}\right) \right] \cdot 2 N \cdot 0 \right\} = 2 \left[ 1 - \left(\frac {1}{N _ {b}}\right) \right]
$$

Summing these two sources of family-size variance gives $ \sigma_{k}^{2}=[(4 N-2)/N_{p}]-2 $ , and substituting into Equation 3.4, we obtain $ N_{e}=N_{p} $ . Thus, provided a species has a high enough gamete production to generate N surviving progeny from a small number of adults, the effective population size can be only a tiny fraction of N.

Example 3.2. Heywood (1986) estimated that $ \sigma_{k}^{2} / \mu_{k}^{2} $ for seed production is on the order of 1 to 4 in a number of annual plants (including self-compatible species). Unfortunately, the value of $ \sigma_{k}^{2} $ for total gamete production requires additional information on successful pollen production, which is extremely difficult to acquire due to problems in ascertaining paternity. For heuristic purposes, however, let us assume a stable monoecious population. This necessarily implies mean seed and pollen production are both equal to one, and $ \mu_{k}=\mu_{o}+\mu_{p}=2 $ , as each parent must produce two successful gametes (on average, one male and one female). We will also assume a three-fold higher standard deviation for successful pollen relative to seed production, so that $ \sigma_{p}=3\sigma_{o} $ , and a perfect correlation between ovule and pollen production. Because the correlation between the number of female and male gametes produced per individual is defined to be $ \sigma_{o,p} /(\sigma_{o}\sigma_{p}) $ , the latter assumption implies $ 1=\sigma_{o,p} /[\sigma_{o}\cdot 3\sigma_{o}]. $ Assuming random mating, and substituting $ \sigma_{o,p}=3\sigma_{o}^{2} $ into Equation 3.8, we obtain $ N_{e}=N /[ ( 1 2 \sigma_{o}^{2} / \mu_{k}^{2} )+1 ] $ Thus, for $ \sigma_{o}^{2} /\mu_{k}^{2} $ in the range of 1 to 4, $ N_{e} $ is between 2% and 8% of the census number (N).

## DIOECY

As in the case of monoecy with self-incompatibility, when the sexes are separate, inbreeding always needs to be defined with reference to the grandparent generation, which is the earliest point back to which the two genes of an individual can coalesce. Separate sexes also introduce the possibility of different levels of inbreeding through males and females,

as might be expected, for example, in polygynous species in which most females mate with a relatively small segment of the male population.

If O is the offspring of interest, with M and F being its mother and father, there are two ways by which O may derive two genes from the same grandparent: (1) M and F may share the same mother (with probability $ 1 / N_{ef} $ , where $ 1 / N_{ef} $ is the effective number of females); or (2) M and F may share the same father (with probability $ 1 / N_{em} $ , where $ 1 / N_{em} $ is the effective number of males). In either case, because each parent transmits to O a gene from the shared ancestor with probability 0.5, the probability that O inherits both genes from the shared grandparent is 1/4. Thus, the total probability that O inherits two genes from the same grandparent is

$$
P = \frac {1}{N _ {e}} = \frac {1}{4 N _ {e m}} + \frac {1}{4 N _ {e f}}
$$

What do we mean by the effective numbers of males and females? Assuming random mating (including no prohibition of mating between sibs), the effective number of each sex can be derived by the same method used to obtain Equation 3.3. Skipping the intermediate steps, we simply note that

$$
N _ {e s} = \frac {\mu_ {s k} N _ {s , t - 2} - 1}{\left(\sigma_ {s k} ^ {2} / \mu_ {s k}\right) + \mu_ {s k} - 1}
$$

where s denotes the sex (m or f), and $ \mu_{sk} $ and $ \sigma_{sk}^{2} $ are the mean and variance of gamete production by sex s (Crow and Denniston 1988). Latter (1959) provided a more elaborate expression for $ N_{es} $ that explicitly accounts for the variance and covariance of male and female progeny production. Letting $ \phi $ be the sex ratio (proportion of females),

$$
N _ {e m} = \frac {4 N _ {m , t - 2}}{2 + \sigma_ {m m} ^ {2} + \frac {2 (1 - \phi)}{\phi} \sigma_ {m m , m f} + \left(\frac {1 - \phi}{\phi}\right) ^ {2} \sigma_ {m f} ^ {2}}
$$

$$
N _ {e f} = \frac {4 N _ {f , t - 2}}{2 + \sigma_ {f f} ^ {2} + \frac {2 \phi}{1 - \phi} \sigma_ {f m , f f} + \left(\frac {\phi}{1 - \phi}\right) ^ {2} \sigma_ {f m} ^ {2}}
$$

where for male parents, $ \sigma_{mm}^{2} $ is the variance of male progeny number, $ \sigma_{mf}^{2} $ is the variance of female progeny number, and $ \sigma_{mm,mf} $ is the covariance of male and female progeny number, with similar definitions for female parents. There are a variety of situations in which these types of specifications may be useful. For example, if parents produce a fixed number of offspring, the covariances $ \sigma_{mm,mf} $ and $ \sigma_{fm,ff} $ between numbers of sons and daughters must be negative, whereas these terms can be positive if parents differ in the resources available for overall progeny production.

Further simplification of Equation 3.10 is possible when certain assumptions are met. Consider, for example, the case in which members of the same sex produce equal numbers of potential gametes, such that $ \sigma_{sk}^{2}=\mu_{sk} $ , and the variation in family size is a simple consequence of the random union of gametes. It then follows from the development of the monoecy model that $ N_{em}=N_{m,t-1} $ and $ N_{ef}=N_{f,t-1} $ . Rearranging Equation 3.9, assuming constant population features and dropping the designation of time, and noting that $ N_{m}=(1-\phi)N $ and $ N_{f}=\phi N $

$$
N _ {e} = \frac {4 N _ {m} N _ {f}}{N _ {m} + N _ {f}} = 4 \phi (1 - \phi) N
$$

In this case, $ N_{e} $ attains a maximum of N when the sex ratio is balanced $ (\phi=0.5) $ , but with skewed sex ratios, $ N_{e} $ is influenced much more strongly by the density of the rarer sex. For example, in a highly polygynous species, as $ \phi\rightarrow1 $ $ N_{e}\rightarrow4(1-\phi)N\simeq4N_{m} $ , namely four times the number of males.

In natural populations, where individuals inhabit different environments that influence the availability of resources and mates, it is likely that the variance in progeny production

will exceed the mean (i.e., $ \sigma_{k}^{2}>\mu_{k} $), in which case $ N_{e} $ will be less than that predicted by Equation 3.12. For example, in a summary of data on lifetime reproductive success in female birds, Grant (1990) found that $ \sigma_{fk}^{2} / \mu_{fk} $ ranged from 1.2 to 4.2. Assuming a stable population size $ (\mu_{fk}=2) $ and substituting into Equation 3.10, the female effective population sizes for these species are found to be 40% to 90% of the actual number of females. Nonrandom variation in family sizes appears to be the rule even in laboratory populations. For example, caged populations of Drosophila typically exhibit effective sizes on the order of 10% of the census size of the adult population (Briscoe et al. 1992). Observations from natural populations of other animals with separate sexes suggest an average $ N_{e}/N $ ratio for single generations on the order of 0.7 (Crow and Morton 1955; Nunney and Elam 1994).

Finally, the results for dioecy can be linked to those for the monoecy model in the following informative way. The mean gamete production for the whole population is $ \mu_{k}=(1-\phi)\mu_{mk}+\phi\mu_{fk} $ , or equivalently, because all individuals have a father and a mother, $ \mu_{k}=2(1-\phi)\mu_{mk}=2\phi\mu_{fk} $ . The variance of gamete production across the entire population is $ \sigma_{k}^{2}=(1-\phi)\sigma_{mk}^{2}+\phi\sigma_{fk}^{2}+\phi(1-\phi)(\mu_{mk}-\mu_{fk})^{2} $ . Using these expressions, Equation 3.9 is essentially equivalent to Equation 3.7 (Kimura and Crow 1963b), showing that the effective size of an ideal population with separate sexes is the same as that for a monoecious, selfincompatible population with the same population properties $ \mu_{k} $ and $ \sigma_{k}^{2} $ .

## AGE STRUCTURE

Because the previous formulae were obtained under the assumption of discrete generations, they provide estimates of $ N_{e} $ for explicit generational intervals. Such expressions are reasonable for organisms such as annual plants (ignoring the problem of seed banks; Nunney 2002) or univoltine insects, but for species that reproduce at different ages, as is the case for most vertebrates and perennial plants, the overlapping of generations raises additional complications. Nevertheless, as first pointed out by Hill (1972e, 1979), there is a simple correspondence between the effective sizes of populations with and without age structure.

In the previous formulations, N was the number of potential reproductive individuals entering the population in each generation. For age-structured populations, we must consider instead $ N_{b} $ the total number of newborns entering the population during each unit of time, as well as the number of time units per generation. The latter quantity, known as the generation time $ (T) $ , is the average age of parents giving birth, which in turn is a function of the age-specific schedules of survival and reproduction. For an ideal monoecious population,

$$
T = \frac {\sum_ {i = 1} ^ {\tau} i \ell_ {i} b _ {i}}{\sum_ {i = 1} ^ {\tau} \ell_ {i} b _ {i}}
$$

where $ \ell_{i} $ is the probability of surviving to age i, $ b_{i} $ is the expected number of offspring produced by parents of age i, and $ \tau $ is the maximum reproductive age. The quantity $ \ell_{i} b_{i} $ denotes the expected number of births by an individual of age i, discounting for prior mortality. For a dioecious population, T is further complicated by the need to average over males (m) and females (f),

$$
T = \frac {T _ {m m} + T _ {m f} + T _ {f m} + T _ {f f}}{4}
$$

where $ T_{mf} $ , for example, is the average age of male parents of daughters. The average generation length is the natural time scale for the evolutionary analysis of age-structured populations. Letting $ N=N_{eb} T $ , with $ N_{eb}=4\phi_{b}(1-\phi_{b}) N_{b} $ being the effective size of the newborn age class and $ \phi_{b} $ being the sex ratio of newborns, all of the preceding formulae for discrete generations apply provided the structure and size of the population are stable.

However, we are still left with the rather substantial problem of estimating $ \sigma_{k}^{2} $ , which now depends on variation in longevity as well as variation in fertility.

Felsenstein (1971), Johnson (1977b), and Emigh and Pollak (1979) showed how the variance in offspring production can be expressed in terms of the age-specific parameters $ \ell_{i} $ and $ b_{i} $ . Again making the assumption that the population is stable in terms of size, sex ratio, and age composition, the effective size of an age-structured population with separate sexes is

$$
N _ {e} = \frac {N _ {e b} T}{1 + \left(1 - \phi_ {b}\right) \sum_ {i = 1} ^ {\tau_ {f}} \left(\frac {1}{\ell_ {i + 1} ^ {f}} - \frac {1}{\ell_ {i} ^ {f}}\right) \left(\sum_ {f}\right) ^ {2} + \phi_ {b} \sum_ {i = 1} ^ {\tau_ {m}} \left(\frac {1}{\ell_ {i + 1} ^ {m}} - \frac {1}{\ell_ {i} ^ {m}}\right) \left(\sum_ {m}\right) ^ {2}}
$$

where $ \left(\sum_{s}\right)^{2}=\left(\sum_{j\geq i+1}^{\tau_{s}} \ell_{j}^{s} b_{j}^{s}\right)^{2}, \tau_{s} $ is the maximum age of reproduction for sex s, and s=m or f (Emigh and Pollak 1979). An analogous expression is available for monoecious populations (Felsenstein 1971). While the derivations underlying these expressions rely on the assumption that gametes are drawn randomly from the members within age classes, no assumptions are made with regard to the preference of matings between age classes.

Despite their complicated structure, demographic formulae such as Equation 3.15 are useful for analyzing the sensitivity of a population's effective size to modifications in the life-history schedule. Nevertheless, the Emigh-Pollak equation has some practical difficulties. First, it rests on the assumption of a stable population structure. Such situations are rare in nature because of temporal changes in the environment. Johnson (1977b) and Choy and Weir (1978) derived dynamical equations to resolve these difficulties, and the entire subject was reviewed by Charlesworth (1994a). Second, Equation 3.15 was derived under the assumption that the age-specific mortality and birthrates of individuals are uncorrelated, i.e., that individuals with an elevated likelihood of survivorship do not have elevated or reduced birthrates. This will not be true for populations in which energetic trade-offs exist between different life-history characters. The problem needs further investigation.

Substantial simplification of Equation 3.15 can be achieved under some conditions. For example, if year-to-year survival is age independent, and if the mating system can be described in simple terms, $ N_{e} $ can be defined as a function of a small number of parameters, thus eliminating the need for refined age-specific schedules of survivorship and fecundity. Using this approach, Nunney (1993) concluded that $ N_{e} $ in animals with overlapping generations is typically on the order of N/2 to N, although his analysis ignores the important influence of variation in N across generations (as will be seen in a following section).

Example 3.3. While complete age-specific survivorship and reproductive schedules are available for the females of many natural populations, male promiscuity often imposes enormous practical difficulties for ascertaining paternity. Thus, the variance in male reproductive success is generally unknown. However, a long-term study on the behavior and demography of the red deer (Cervus elaphus) by Clutton-Brock et al. (1982) allows at least a crude estimate of $ N_{e} $ by use of the Emigh-Pollak equation, as shown in the table below. The study population was roughly constant in density for two decades, and observations on known individuals provide information on the age-specific rates of mortality and reproduction for both sexes. The sex ratio at birth $ (\phi_{b}) $ averaged 0.43 over several years, so $ N_{eb}=0.98N_{b}. $

The age-specific survival rates, $ \ell_{i} $ , in the following table were extracted directly from Clutton-Brock et al. (1982), while the age-specific reproductive schedules, $ b_{i}^{f} $ and $ b_{i}^{m} $ , were estimated from behavioral and demographic observations of the authors and adjusted downward to maintain a stable population size. The columns marked (1) and (2) are $ \left[ \left( 1 / \ell_{i+1}^{s} \right) - \left( 1 / \ell_{i}^{s} \right) \right] $ and $ \left( \sum_{j > i+1}^{\tau_{s}} \ell_{j}^{s} b_{j}^{s} \right)^{2} $ , and column (3) is the product of (1) and (2); all of these are deployed in Equation 3.15.

<table border="1"><tr><td rowspan="2">Agei</td><td colspan="5">Females</td><td colspan="5">Males</td></tr><tr><td>$\ell_{i}^{f}$</td><td>$b_{i}^{f}$</td><td>(1)</td><td>(2)</td><td>(3)</td><td>$\ell_{i}^{m}$</td><td>$b_{i}^{m}$</td><td>(1)</td><td>(2)</td><td>(3)</td></tr><tr><td>1</td><td>1.00</td><td>0.00</td><td>0.33</td><td>0.25</td><td>0.08</td><td>1.00</td><td>0.00</td><td>0.45</td><td>5.97</td><td>2.69</td></tr><tr><td>2</td><td>0.75</td><td>0.00</td><td>0.12</td><td>0.25</td><td>0.03</td><td>0.69</td><td>0.00</td><td>0.22</td><td>5.97</td><td>1.31</td></tr><tr><td>3</td><td>0.69</td><td>0.00</td><td>0.02</td><td>0.25</td><td>0.01</td><td>0.60</td><td>0.00</td><td>0.03</td><td>5.97</td><td>0.18</td></tr><tr><td>4</td><td>0.68</td><td>0.18</td><td>0.04</td><td>0.24</td><td>0.01</td><td>0.59</td><td>0.00</td><td>0.03</td><td>5.97</td><td>0.18</td></tr><tr><td>5</td><td>0.66</td><td>0.26</td><td>0.07</td><td>0.22</td><td>0.02</td><td>0.58</td><td>0.00</td><td>0.03</td><td>5.97</td><td>0.18</td></tr><tr><td>6</td><td>0.63</td><td>0.33</td><td>0.05</td><td>0.21</td><td>0.01</td><td>0.57</td><td>0.34</td><td>0.03</td><td>5.92</td><td>0.18</td></tr><tr><td>7</td><td>0.61</td><td>0.34</td><td>0.06</td><td>0.19</td><td>0.01</td><td>0.56</td><td>0.26</td><td>0.03</td><td>5.88</td><td>0.18</td></tr><tr><td>8</td><td>0.59</td><td>0.40</td><td>0.06</td><td>0.17</td><td>0.01</td><td>0.55</td><td>0.60</td><td>0.10</td><td>5.59</td><td>0.56</td></tr><tr><td>9</td><td>0.57</td><td>0.42</td><td>0.03</td><td>0.16</td><td>0.01</td><td>0.52</td><td>0.53</td><td>0.12</td><td>5.30</td><td>0.64</td></tr><tr><td>10</td><td>0.56</td><td>0.34</td><td>0.07</td><td>0.14</td><td>0.01</td><td>0.49</td><td>0.79</td><td>0.40</td><td>3.94</td><td>1.58</td></tr><tr><td>11</td><td>0.54</td><td>0.46</td><td>0.03</td><td>0.13</td><td>0.00</td><td>0.41</td><td>0.53</td><td>0.42</td><td>3.11</td><td>1.31</td></tr><tr><td>12</td><td>0.53</td><td>0.42</td><td>0.20</td><td>0.08</td><td>0.02</td><td>0.35</td><td>0.45</td><td>1.69</td><td>1.00</td><td>1.69</td></tr><tr><td>13</td><td>0.48</td><td>0.45</td><td>0.19</td><td>0.04</td><td>0.01</td><td>0.22</td><td>0.08</td><td>2.60</td><td>0.63</td><td>1.64</td></tr><tr><td>14</td><td>0.44</td><td>0.40</td><td>0.23</td><td>0.01</td><td>0.00</td><td>0.14</td><td>0.20</td><td>3.97</td><td>—</td><td>—</td></tr><tr><td>15</td><td>0.40</td><td>0.25</td><td>0.20</td><td>—</td><td>—</td><td>0.09</td><td>—</td><td>—</td><td>—</td><td>—</td></tr><tr><td>16</td><td>0.37</td><td>0.00</td><td>—</td><td>—</td><td>—</td><td>0.05</td><td>—</td><td>—</td><td>—</td><td>—</td></tr><tr><td></td><td></td><td></td><td></td><td></td><td>0.23</td><td></td><td></td><td></td><td></td><td>12.32</td></tr></table>

The summations in the denominator of Equation 3.15 reflect the variation in lifetime reproductive success of females and males. As outlined in the table, these terms are equal to 0.23 and 12.32, respectively, indicating a great inequity between the reproductive properties of the sexes. This results because male red deer appropriate harems, and older males are much more successful at doing so than young ones. The few males that live to an old age may father up to two dozen offspring in their lifetimes, whereas males that die before the age of five ( $ \sim 40\% $ of newborn males) have no reproductive success at all. On the other hand, almost all females reproduce to some degree once they have attained reproductive maturity.

Substituting the sums from the table into Equation 3.15, the effective population size is found to be $ 0.98 N_{b} T /[ 1+(1-0.43)(0.23)+0.43(12.32)]=0.15 N_{b} T $ . Thus, the effective size of this population is $ \sim 15\% $ of the number of offspring produced by the population per generation. The mean generation time through females and males is 9.47 and 9.18 years, so $ T\simeq 9.32 $ , and the annual number of offspring produced by the population is $ N_{b}\simeq 270 $ Thus, $ N_{e}\simeq 0.15\times 270\times 9.32=377. $

## VARIABLE POPULATION SIZE

Most populations vary in density from generation to generation, often dramatically so, and this raises practical problems in the implementation of the previous theory. As noted in Equation 2.7, with variable population size, the expected loss of heterozygosity over t generations is no longer $ [ 1-(1/2 N_{e})]^{t} $ but rather is now a product of t terms, each incorporating the effective population size of a particular generation such that

$$
H _ {t} = H _ {0} \prod_ {i = 0} ^ {t - 1} \left(1 - \frac {1}{2 N _ {e , i}}\right)
$$

Thus, it is informative to evaluate the size of an ideal population of constant size with the same expected heterozygosity after t generations as a population with variable size over the same period. An approximate answer can be obtained by noting that with a moderately

large $ N_{e,i} $ , Equation 3.16 simplifies to

$$
H _ {t} \simeq H _ {0} \exp \left(- \sum_ {i = 0} ^ {t - 1} \frac {1}{2 N _ {e , i}}\right)
$$

which may be compared to

$$
H _ {t} \simeq H _ {0} e ^ {- t / 2 N _ {e}}
$$

for the ideal case of constant effective size. Equating the exponents of these two expressions,

$$
N _ {e} ^ {*} \simeq \frac {t}{1 / N _ {e , 0} + 1 / N _ {e , 1} + \cdots + 1 / N _ {e , t - 1}}
$$

Thus, the long-term effective size $ N_{e}^{*} $ is approximately equal to the harmonic mean of the generation-specific effective sizes. An asterisk is placed on $ N_{e} $ to remind the reader that the inbreeding projected by $ N_{e}^{*} $ strictly pertains to generation t. Other generations may exhibit more or less loss of variation than anticipated depending upon the actual pattern of temporal changes in $ N_{e,i} $

Example 3.4. To see how population bottlenecks have especially pronounced effects on $ N_{e}^{*} $ consider a population whose effective size regularly fluctuates between 10 and 100. From Equation 3.18, $ N_{e}^{*} = 2 / (0.1+0.01) = 18.2 $ . Thus, the total loss of heterozygosity from this population every two generations is equivalent to that expected for an ideal random-mating population with a constant effective size of 18, which is much closer to the expectation for a constant population size of 10 than 100. Frankham (1995) and Vucetich et al. (1997) showed that $ N_{e}^{*} $ is frequently in the range 10% to 20% of $ N_{e} $ for a diversity of natural populations of animals. In the extreme case where the effective population size is effectively infinite for $ t-1 $ generations and $ N_{e} $ for one generation, $ N_{e}^{*} = tN_{e} $

## PARTIAL INBREEDING

Although most of the previous formulations assumed a random union of gametes, the frequency of mating between relatives often exceeds that expected under random mating. Many plants, for example, produce a significant proportion of offspring by self-fertilization. If the total population size were infinite, a fixed proportion of matings between relatives would simply lead to an equilibrium condition wherein the production of new inbreeding each generation is balanced by the breakdown of old inbreeding through outcrossing (Wright 1951, 1969; Hedrick 1986b; Hedrick and Cockerham 1986). However, such an equilibrium does not exist for finite populations, where allele frequencies are subject to random genetic drift. Here we consider the consequences of partial selfing in monoecious populations and of partial full-sib mating in populations with separate sexes, in both cases assuming an otherwise randomly mating population. Both subjects were evaluated in considerable detail by Caballero and Hill (1992a) and Wang (1996).

Assuming a constant number of adults, for a population in which a proportion $ \beta $ of progeny from each family is a product of self-fertilization,

$$
N _ {e} = \frac {2 (2 - \beta) N}{\sigma_ {k} ^ {2} + 2 (1 - \beta)}
$$

(Crow and Denniston 1988; Caballero and Hill 1992a; Wang 1996). Further assuming that the numbers of outcrossed and selfed progeny per parent are independent variables, the

variance in gamete transmission $ \sigma_{k}^{2} $ can be simplified by noting the logic below Equation 3.4: for the outcrossed progeny, there are $ 2 N(1-\beta) $ random gametes drawn, each with variance $ \simeq 1 / N $ per focal parent, yielding a variance of $ \simeq 2(1-\beta) $ ; for the selfed progeny, there are $ N(1-\beta) $ parents to draw from, but because each successful draw leads to two transmitted gametes, the variance per draw is $ \simeq 4 / N $ , yielding a total variance contribution $ \simeq 4\beta $ ; the total variance is then $ \sigma_{k}^{2}\simeq 2(1+\beta) $ , and Equation 3.19 reduces to

$$
N _ {e} = \frac {(2 - \beta) N}{2}
$$

If mating is random, so that $ \beta=1/N $ , then $ N_{e}=N-0.5 $ , a result that can also be obtained directly from Equation 3.3 by letting $ \sigma_{k}^{2}\simeq\mu_{k}\simeq2 $ . Under obligate self-fertilization, a mode of reproduction in some plants and hermaphroditic animals, $ \beta=1 $ and $ N_{e}=N/2 $ . Self-fertilization results in a reduction in the effective population size because the nonindependence imposed by inbreeding reduces the effective number of alleles per locus within individuals.

For the case of species with separate sexes, with $ \beta $ being the fraction of offspring derived by full-sib mating, and assuming equal numbers of males and females and Poisson-distributed family sizes,

$$
N _ {e} \simeq \frac {(4 - 3 \beta) N}{4 - 2 \beta} + 1
$$

(Wang 1995). Three special cases are of interest here. For a population derived entirely by full-sib mating, $ \beta=1 $ and $ N_{e}=N / 2 $ , as in the case of complete selfing. With complete avoidance of sib mating, $ \beta=0 $ and $ N_{e}=N+1 $ . Finally, with the type of population structure assumed, there are N/2 families, so under random mating, the probability of full-sib mating is simply $ \beta=2 / N $ , which implies $ N_{e}\simeq N+0.5 $

## SPECIAL SYSTEMS OF MATING

It is important to bear in mind that, when applied to matters of genetic variation, the equations for $ N_{e} $ given above are appropriate for predicting the expected loss of heterozygosity resulting from inbreeding at the population level. When variation in pedigree structure exists among individuals, as will almost always be the case in nature, the actual degree of inbreeding will generally vary among loci within individuals as well as among individuals within the population. Given a cumulative level of inbreeding (loss of heterozygosity) at a locus equal to f, identity by descent will be binomially distributed among individuals with mean f and variance $ \sigma_{f}^{2}=f(1-f). $ With completely linked loci, this is also the total variance in f, as there will be no variation in f among loci. However, for unlinked loci, the realized inbreeding at each locus need not be the same. Weir et al. (1980) found that the coefficient of variation of $ (1-f) $ among individuals is approximately $ (3N_{e})^{-1 / 2} $ for randomly mating monoecious populations, $ (6N_{e})^{-1 / 2} $ for randomly mating but monogamous, dioecious populations, and $ (12N_{e})^{-1 / 2} $ for monoecy with selfing excluded and for dioecy with random mating. These asymptotic values are reached in only a few generations. Thus, provided the population size and number of constituent loci are moderately large, the variation in inbreeding is negligible for most practical purposes (see also Franklin 1977; Cockerham and Weir 1983).

In contrast to the usual situation, one can also envision (and implement) systems of mating involving fixed relationships such that all members of the population have exactly the same average inbreeding coefficient over all loci (Wright 1921b). Consider first the most extreme form of inbreeding—obligate self-fertilization, a mode of reproduction in some plants and hermaphroditic animals. Because under this scheme of mating all individuals are reproductively isolated, a collection of such lines is equivalent to a series of populations, each consisting of a single individual, and after t generations of selfing, the expected fraction of heterozygotes at any locus is reduced to

$$
H _ {t} = H _ {0} \left(1 / 2\right) ^ {t}
$$

![](page=11,bbox=[352, 148, 768, 357])

<div align="center">

Figure 3.1 Erosion of expected heterozygosity under continuous breeding schemes involving self-fertilization, full-sib mating, and double first-cousin mating.

</div>

where $ H_{0} $ denotes the initial level of variation. After t=3 generations, only 12.5% of the initial heterozygosity remains (Figure 3.1).

The next most intense system of inbreeding involves continuous brother-sister mating. Starting with unrelated parents, it takes a generation of full-sib mating before alleles identical by descent can appear in the same individual. Written in terms of the inbreeding coefficient, such that $ H_{t}=(1-f_{t})H_{0} $ , the exact recursion equation under full-sib mating is

$$
f _ {t} = \frac {1}{4} \left(1 + 2 f _ {t - 1} + f _ {t - 2}\right)
$$

and in one of the first applications of matrices in population genetics, Haldane (1937a) provided the approximation

$$
H _ {t} \simeq H _ {0} (0. 8 1) ^ {t}
$$

Thus, starting from a non-inbred base population, 12 generations of full-sib mating will result in a loss of 90% of the initial heterozygosity.

Moving on, with a constant population size of four breeding adults, the minimum relationship between individuals is that of double first-cousins (Figure 3.2, left). Starting with four unrelated individuals, it then takes three generations for alleles that are identical by descent (IBD) to appear in the same individual, and thereafter

$$
H _ {t} \simeq H _ {0} (0. 9 2) ^ {t}
$$

(Wright 1921b). The number of generations required for the loss of 90% heterozygosity is now 30 (Figure 3.1).

These types of results are of special interest to managers of small, captive populations of endangered species and/or breeding stocks viewed as genetic resources for the future. Here we consider just one of the many practical questions that arise in these areas. Given a limited number of founders and an upper ceiling on the number of individuals that can be maintained, what is the optimal breeding scheme for minimizing the erosion of genetic variation? Wright (1921b) suggested that the best way to minimize the loss of heterozygosity from a small population would be to restrict matings to pairs of individuals with the

![](page=12,bbox=[307, 130, 562, 259])

<div align="center">

Figure 3.2 Mating schemes under continuous double first-cousin mating (left) and under circular mating with four individuals (right). Genes that are identical by descent do not appear in the same individual for three and four generations, respectively, under these two schemes. Males and females are denoted by separate symbols (squares and circles), and lines connect parents (above) and offspring (below).

</div>

least degree of relatedness. Such a breeding scheme, known as maximum avoidance of inbreeding (MAI), is exemplified by all three of the special mating systems just noted—in each case, matings occur between the most distantly related individuals within each line. An added advantage of MAI is that for a population size of $ N=2^{m} $ , m generations will pass before any inbreeding occurs at all. For example, with $ N=64 $ , $ m+1=7 $ generations would pass before two copies of a founding gene could appear in the same individual under a maximum avoidance scheme. Once the inbreeding begins, the proportion of heterozygosity lost each generation is very nearly constant, approaching an asymptotic value of $ 1 / (4 N-m-1) $ (Robertson 1964), which, with N=4 and m=2 under double first-cousin mating equals 0.08, giving the fraction retained as $ 1-0.08=0.92 $ , recovering Equation 3.24.

Note that when N is large, m $ \ll $ N and the asymptotic rate of loss of heterozygosity is $ \simeq 1 / (4 N) $ per generation under MAI. Comparing this expression with Equation 2.4c, it can be seen that this mating scheme has the same effect as doubling the size of a random-mating population. This result is not strictly a consequence of the avoidance of inbreeding but, again, is the outcome of all families producing equal numbers of offspring. In fact, even under a random-mating scheme, if family sizes are equilibrated, provided N $ \geq 4 $ , the erosion of heterozygosity is

$$
H _ {t} \simeq H _ {0} \left(1 - \frac {1}{4 N}\right) ^ {t}
$$

where t is the number of generations after the onset of inbreeding (Wright 1951). This can be seen by returning to many of the formulae in the earlier sections of this chapter and setting $ \sigma_{k}^{2}=0 $ . Under the idealized scheme of random mating discussed earlier, variances in allele frequencies arise from variance in the number of progeny left by each individual and from segregational variance resulting from the sampling of alleles within individuals. For randomly mating populations of even moderate size, about half of the total sampling variance of allele frequency arises from each source, so that equilibration of family size reduces the total sampling variance by 50%

The central point of the preceding discussion is that, for a fixed census size, three factors can potentially be manipulated to reduce the rate of inbreeding: avoidance of matings among relatives; equilibration of family sizes; and a sex ratio as close to one as possible. In some domesticated animals, the latter is a problem because females have only one or two offspring per year. In such cases, Gowe et al. (1959) suggested that when the sex ratio of contributing parents is r females to each male, the loss of genetic variance will be minimized if every male contributes exactly one son and r daughters, and every female leaves one daughter and also contributes a son with probability $ 1 / r $ . Wang (1997) improved on this

scheme with the constraint that a female contributing a son does not contribute a daughter and another female from the same male family instead contributes two daughters.

Kimura and Crow (1963a) noted that Wright's intuition that MAI minimizes the longterm loss of genetic variation is actually not quite correct, pointing out that a circular mating (CM) scheme (Figure 3.2) ultimately leads to a lower rate of loss of heterozygosity. Under this breeding design, females and males are arranged such that each of them is mated to two "neighbors," with the last individual in the linear array being mated with the first, thereby completing the circle. Nevertheless, although circular mating ultimately reduces the rate of loss of heterozygosity relative to MAI, it is inferior in the early generations of mating, and even with small N, it may take more than 100 generations before its superiority is realized. Thus, because most of the initial genetic variation in a population will generally have been lost by this time, the practical advantages of circular mating are actually quite negligible.

The major limitation of both the MAI and CM schemes is that they only impede the loss of genetic variation—ignoring new mutations, any randomly mating finite population will ultimately become homozygous at every locus. However, Robertson (1964) obtained the more general (and counterintuitive) result that the rate of loss of overall genetic variation from a population actually declines as the relatedness between mates increases. In the extreme, genetic diversity can be preserved indefinitely by subdividing a population into several isolated lines. Although the individual lines are all expected to become homozygous eventually, different lines will become fixed for different sets of genes, with the overall level of preservation of genetic diversity being defined by the number of inbred lines. In effect, complete inbreeding gives rise to a condition equivalent to each family having preserved the equivalent of one gamete from the base population. For example, for a locus with initial allele frequency $ p_{0} $ assuming a large number of families, the allele frequency in the total collection of lines would remain close to $ p_{0} $ so that subsequent random mating of the lines would render the heterozygosity close to its original state, $ 2 p_{0} (1-p_{0}) $ . It must be emphasized, however, that these arguments assume that intense inbreeding in small lines has no consequences that might endanger the line's survival. In reality, however, very small lines are likely to die out occasionally just by accident, and extreme inbreeding also often has serious deleterious effects on fitness (LW Chapter 10). The gradual replacement of extinct lines by members of surviving lines will lead to further loss of variation.

## POPULATION SUBDIVISION

Although few species exhibit internal isolation as extreme as that just noted, many (probably most) species occupy spatially structured environments. Such structure causes local inbreeding, as mates are more related than random pairs from the entire population. One of the simplest models of population structure is Wright's (1951) island model, introduced in Chapter 2 (Figure 2.11). Here, the metapopulation consists of d demes, each containing a fixed number N of randomly mating individuals with idealized Wright-Fisher properties, and each deme contributes an equal fraction m of its genes to the migrant pool, which is then equally distributed among the remaining demes. Under this model, an equilibrium level of population divergence is eventually reached (Equation 2.46), at which point the increase in divergence resulting from within-deme genetic drift is balanced by the exchange of alleles by migration.

Recalling from Chapter 2 that the mean coalescence time for an ideal, random-mating population is 2N generations, Equation 2.45b (giving the mean coalescence time under this population structure) implies an effective size for the overall metapopulation of

$$
N _ {e} = N d + \frac {(d - 1) ^ {2}}{4 d m}
$$

In this simplest case, we see that the effective size of a metapopulation exceeds the sum of the demic effective sizes (Nd) by an amount approaching $ d / (4m) $ when the number of

demes is large. With low migration rates $ ( m\ll1) $ , this inflation can be substantial. For example, if $ m<1 / ( 4 N) $ $ N_{e} $ exceeds twice the total number of breeding adults $ ( 2 N d) $ . This confirms Robertson's (1964) argument that population subdivision can reduce the overall rate of loss of variation by drift as unique alleles are sequestered within individual demes. However, numerous authors have pointed out that this inflation of $ N_{e} $ in the ideal island model is a special consequence of the absence of variation in deme productivity (analogous to the consequences of constant family sizes within a single population, noted above).

The next simplest type of island model allows for extinction and recolonization of the individual demes. In each generation, a fraction e of the demes goes extinct, but immediate recolonization ensures the maintenance of a fixed number (d) of demes. Tracing back to Slatkin (1977) and Maruyama and Kimura (1980), most attempts to model this process have assumed that the newly colonized deme is immediately restored to size N in a single generation, with recolonization involving k immigrants either derived from a single random deme (the propagule-pool model) or from a random pool of migrants from the entire metapopulation (the migrant-pool model). This simple modification results in a reduction in $ N_{e} $ for the metapopulation by inducing variation in productivity among the demes surviving in each generation—demes that contribute to a colonization event experience a burst of productivity relative to demes that do not.

Using the logic noted above, approximate expressions for mean coalescence times for metapopulations experiencing extinction and recolonization (Pannell and Charlesworth 1999) yield formulae for the metapopulation $ N_{e} $ . Such expressions are functions of the relative rates of extinction and migration and the size and type of colonizing pool, and we only give two examples for the propagule-pool model. If the extinction rate is smaller than the migration rate $ (e\leq m) $ and much smaller than the relative size of the colonizing pool $ (e\ll k / N), $

$$
N _ {e} \simeq N d \frac {\left[ 4 m + (1 / N) \right]}{4 (e + m)}
$$

a result also obtained by Maruyama and Kimura (1980) and Whitlock and Barton (1997). Under these conditions, local extinctions are sufficiently rare that within-deme variation is able to recover substantially by migration between bottleneck events, and although $ N_{e}< $ Nd, it approaches the latter value as e $ \rightarrow $ 0 unless N is tiny. On the other hand, if the extinction rate is relatively high, such that e $ \gg $ m and e $ \gg $ k/N,

$$
N _ {e} \simeq \frac {d}{4 e}
$$

In this case, extinctions are so frequent that local demes (reestablished from a small number of colonists and experiencing little immigration) are almost completely inbred, and the total effective size is independent of the number of individuals per deme and simply defined by deme number and average deme longevity $ ( e^{-1} $ generations).

A more general expression for the effective size of a metapopulation under the island model was derived by Whitlock and Barton (1997). Assuming large d, so that $ d\simeq d-1 $ as a first-order approximation,

$$
N _ {e} \simeq \frac {d (1 + 4 N m)}{4 m + 2 \sigma_ {K} ^ {2} (1 + 2 m)}
$$

where $ \sigma_{K}^{2} $ denotes the among-deme variance in the number of gametes contributing to the next generation (the analogue for the variance $ \sigma_{k}^{2} $ in individual contributions). Comparing this expression to Equation 3.26, it can be seen that $ \sigma_{K}^{2}>0 $ will always cause a reduction in $ N_{e} $ . In addition, for $ N_{e} $ to be less than the total metapopulation size 2Nd, $ \sigma_{K}^{2} $ need only be larger than $ 1 / (2N) $ . This amount of among-deme variance in gamete production is trivial, as even under ideal conditions in which individual family sizes are Poisson distributed, the variance in total deme productivity will be on the order of $ 2 / N $ . This follows from the fact, noted above, that within an ideal random-mating deme, $ \sigma_{k}^{2}=2 $ , so that at the deme level, $ \sigma_{K}^{2}=2 / N $ . Thus, it appears that population subdivision will almost always result in

a reduction in $ N_{e} $ , provided the individual demes are not completely isolated, a point first made by Wright (1940; see also Nunney 1999).

## SELECTION, RECOMBINATION, AND HITCHHIKING EFFECTS

Up to now, we have assumed that alleles are immune to selective processes, which is, of course, unrealistic in many cases. In fact, selection generally causes a still further reduction in $ N_{e} $ by inflating the among-family variance in offspring production. Evaluating the magnitude of such effects is complicated by the fact that unlike family-size variation induced by environmental heterogeneity, which can be erased in a single generation, genetic variation in fitness is sustained across generations. Such heritable transmission will elevate the genetic representation of some individuals in future generations beyond the expectations under drift alone. This phenomenon was initially mentioned by Morley (1954), who noted in sheep flocks exposed to selection that "the genetically superior individuals will tend to be most inbred." The processes that we will examine are analogous to those that occur in spatially structured populations with random extinction, except that now specific alleles can become trapped in genetic backgrounds that are destined for elimination or fixation.

Before proceeding, it must be emphasized that because $ N_{e} $ is defined in the context of hypothetically neutral loci that serve as benchmarks for the pure drift process, our concern here is not so much with the specific loci under selection, but with the effects of such selection on the dynamics of neutral-allele frequencies elsewhere in the genome. Because the longterm effects of selection depend on the frequency of recombination between selected loci and their associated neutral markers as well as on the mode of selection, the issues are quite technical. Our goal is simply to provide a heuristic overview of why the effects of selection almost always lead to a substantial reduction in $ N_{e} $ . Chapter 8 examines many of these issues in greater detail.

## Effects From Selection at Unlinked Loci

Robertson (1961) first considered the influence of a constant selection regime on the longterm dynamics of a neutral locus assumed to be entirely unlinked to any selected loci. In addition to any baseline variance in gamete production among individuals that might exist for environmental reasons (our previous $ \sigma_{k}^{2} $ ), in the first generation of selection there will also be an among-family genetic variance in relative fitness, $ \sigma_{w}^{2} $ , associated with the differential contributions of individual families. Here the relative fitness $ (w_{i}) $ of the i th family is simply the expected contribution to the next generation relative to the average in the population, such that the mean relative fitness $ \sum_{i=1}^{N/2} w_{i} /(N/2)=1 $ , where we assume a balanced sex ratio and N/2 families. For populations with features in accordance with the standard Wright-Fisher model, a single generation of selection will then reduce the effective population size to

$$
N _ {e} \simeq \frac {4 N}{\sigma_ {k} ^ {2} + 2 + 4 \sigma_ {w} ^ {2}}
$$

which is identical in form to Equation 3.4 except for the additional variance associated with selection in the denominator. Note that because $ \sigma_{w}^{2} $ is the variance in relative fitness among families and the average family size is two, $ 4\sigma_{w}^{2} $ is the genetic variance in actual family size. This expression demonstrates that the random association of neutral alleles with families with different genetic endowments has the same qualitative effect as environmental differences in family sizes $ (\sigma_{k}^{2}) $

Of course, it would be a rare situation in which selection operated only for a single generation, and Robertson (1961) had the additional insight that with subsequent generations of selection, new stochastic associations between selected and unselected loci will arise each generation, while old associations are lost at rate 0.5 with free recombination. This yields a long-term cumulative contribution to the among-family genetic variance in

relative fitness proportional to $ [ 1+ ( 1/2 )+ ( 1/4 )+ ( 1/8 )+\cdots ]^{2} \sigma_{w}^{2}=4 \sigma_{w}^{2} $ , which (as above) is then further multiplied by $ 2^{2} $ to translate relative fitness into the genetic variance in family size. Although this result ignores the fact that the stochastic effects of selection will dissipate over time as favorable alleles at the loci under selection go to fixation, this additional layer of complexity is readily incorporated. Letting L denote the per-generation fractional loss of additive genetic variance at selected loci, the preceding series simply has terms in powers of $ ( 1-L)/2 $ instead of 1/2, and again after converting the variance in relative fitness to the absolute scale, the long-term effective population size becomes

$$
N _ {e} \simeq \frac {4 N}{\sigma_ {k} ^ {2} + 2 + 4 [ 2 / (1 + L) ] ^ {2} \sigma_ {w} ^ {2}}
$$

(Santiago and Caballero 1995). If we further assume that baseline variation in family sizes unassociated with selection simply reflects random gamete sampling, then from above $ \sigma_{k}^{2}\simeq 2 $ , and under Robertson's assumption of no reduction in variance by selection （ $ L=0 $ ） the long-term effective size becomes

$$
N _ {e} = \frac {N}{1 + 4 \sigma_ {w} ^ {2}}
$$

Equations 3.29b and 3.29bc are quite general in the sense that they apply to any scheme of selection. However, they are also a bit opaque in that the mechanistic determinants of $ \sigma_{w}^{2} $ and L are not defined and the substantial effects of linkage are omitted. The remainder of this chapter is focused on the removal of these limitations.

Example 3.5. The genetic variance for relative mean-family fitness is a function of the intensity of selection and the heritability of the selected traits. For example, in the case of truncation selection on a single trait (Chapter 14), $ \sigma_{w}^{2}=\bar{\iota}^{2}t_{FS} $ , where $ \bar{\iota} $ is the standardized selection differential (the change in mean phenotype imposed by selection in units of phenotypic standard deviations, Equation 14.3a), and $ t_{FS} $ is the phenotypic correlation among full sibs (Milkman 1978), which is equivalent to half the heritability for an ideal trait with an additive genetic basis (LW Chapter 18). For situations in which the most extreme 1% to 10% of the phenotypic distribution is selected, $ \bar{\iota} $ is in the range of 2.7 to 1.8 (LW Chapter 2), and $ t_{FS} $ takes on a maximum value of 0.5 when the heritability of the trait is equal to 1.0. Thus, recalling Equations 3.29a through 3.29c, with very strong truncation selection on a highly heritable trait, $ \sigma_{w}^{2} $ may take on high enough values to reduce $ N_{e} $ several-fold relative to the expectation in the absence of selection, even when the selected loci are unlinked. Chapter 26 examines the reduction in $ N_{e} $ due to truncation selection on a trait in more detail.

## Selective Sweeps and Genetic Draft

The effects of linked loci on $ N_{e} $ are substantially greater than those from unlinked loci for the simple reason that chromosomally juxtaposed sites are necessarily mutually influenced by each other's fitness attributes for extended periods. For example, a neutral allele linked to a site under positive selection can hitchhike to high frequencies (and even fixation) if the force of selection is strong relative to the recombination rate between the sites (Maynard Smith and Haigh 1974). One direct consequence of this reduction in $ N_{e} $ is a depressed amount of molecular variation at neutral sites in regions of low recombination, an expectation that is in agreement with many empirical observations (Chapter 8). However, as will be emphasized in the next section, the periodic fixation of favorable alleles is just one potential explanation for this kind of observation, an alternative hypothesis being background selection, the constant purging of new deleterious mutations (Charlesworth 2012).

A simple way of evaluating the effects of selective sweeps of beneficial mutations on variation at completely linked neutral loci was presented by Gillespie (2000). Recall from Chapter 2 that the variance of neutral allele-frequency change from generation to generation in a Wright-Fisher diploid population is equal to $ p ( 1-p ) / ( 2 N ) $ , where p is the current allele frequency. Now imagine that this locus is completely linked to other genomic sites incurring beneficial mutations that collectively cause rapid fixations at an average rate of $ \delta $ per generation. Because such mutations arise independently of the allele at the linked neutral locus, such selective sweeps will result in the fixation of neutral alleles with probabilities proportional to their current frequencies, in this case p and $ ( 1-p ) $ at the neutral focal locus. If we assume that selective sweeps cleanse a population of linked variation essentially instantaneously (or at least rapidly relative to the usual rate of genetic drift), then conditional on a sweep occurring, the variance in allele-frequency change will be $ p ( 1-p ) $ . Thus, for a neutral locus in an ideal randomly mating population subject to periodic selective sweeps, the total variance in allele-frequency change is the weighted sum of both contributions $ \sim p ( 1-p ) \{ [ ( 1-\delta ) / ( 2 N ) ] + \delta \} $ . Because this expression applies to all initial allele frequencies, equating the term in braces to $ 1 / ( 2 N_{e} ) $ yields

$$
N _ {e} \simeq \frac {N}{1 + 2 N \delta}
$$

a result also obtained by Maruyama and Birky (1991) by a different method. Here and below, it is appropriate to view N as the effective size of a population based solely on the demographic considerations noted earlier in this chapter.

When selective sweeps are rare relative to the strength of random genetic drift, such that $ \delta\ll1 / (2N), $ $ N_{e}\simeq N $ , but as $ N\to\infty, $ $ N_{e}\to1 / \delta $ , showing that even populations with enormous numbers of reproductive adults may approach an asymptotic upper limit to $ N_{e} $ defined, not by genetic drift, but by genetic draft (Gillespie 2000)the stochastic result of hitchhiking effects that inevitably arise in linked genomes. That is, when N is very large, the effective size of a population can be more strongly influenced by the physical (i.e., linkage) features of the genome than by demographic factors. In principle, the frequency of selective sweeps may increase with N, as larger populations provide more opportunities for rare beneficial mutations, so strong linkage may even lead to the potential situation in which $ N_{e} $ eventually scales negatively with absolute population size (Lynch 2007).

The preceding result applies to the extreme case of complete linkage. If, instead, a significant amount of recombination occurs between a neutral marker and the selected locus while the latter is proceeding toward fixation, then a selective sweep is not expected to completely remove the variation at the marker locus. As detailed in Chapter 8, the extent to which a neutral locus can free itself of stochastic associations with newly arising beneficial mutations depends on the rate of the sweep (which in turn is a function of the relative power of selection and drift, $ s / [ 1 / ( 2 N ) ] = 2 N s $ ) as well as on the relative power of recombination and selection ( $ c / s $ , where c is the rate of recombination between the two loci).

Incorporation of these technical issues by Wiehe and Stephan (1993) led to an expression identical in form to Equation 3.30a, with $ 2 N \delta $ being replaced by a term that is smaller in absolute value. Gillespie (2000) expressed this influence of recombination as

$$
N _ {e} \simeq \frac {N}{1 + 2 N f _ {s} \delta}
$$

where $ f_{s} $ is the probability that no recombination occurs between the selected site and the marker locus under consideration during the sweep. Following the completion of the sweep, $ f_{s} $ is equivalent to the probability that a random individual will contain two IBD copies of the original neutral allele on the gamete in which the new favorable mutation arose. With free recombination $ f_{s}\simeq0 $ , but with complete linkage, $ f_{s}=1 $ , returning us to Equation 3.30a. The general form for $ f_{s} $ is

$$
f _ {s} \simeq (4 N s) ^ {- c / s}
$$

which will be further discussed in Chapter 8.

## Background Selection

We now turn to the influence of selection against recurrently appearing deleterious mutations, which cause a still further reduction in $ N_{e} $ as a consequence of induced variation in family size. Contrary to the situation with selective sweeps, which are sporadic and chromosomally restricted in scope, the effects of recurrent deleterious mutations are expected to be persistent across the entire genome for the simple reason that the vast majority of mutations are deleterious (LW Chapter 10). Here we attempt to provide a heuristic understanding of the effects of such background selection by considering separately the effects of unlinked and linked deleterious mutations, relying on a simple model in which interfering loci harbor two alternative allelic types (beneficial and deleterious).

If the beneficial allele at a locus mutates to a defective type at rate u per generation, with the latter causing a fractional reduction in heterozygote fitness equal to s, the equilibrium frequency of the deleterious allele is equal to u/s (provided that s is substantially stronger than the power of drift and mutation) (Chapter 7). The genetic variance in relative fitness associated with this locus then has an expected value close to 2us. This result can be obtained by noting that the additive genetic variance for a single locus is equal to $ 2 a^{2} p (1-p) $ (LW Chapter 4), where a is the difference in phenotype between adjacent genotypic classes and p is the allele frequency. In this case, a = s, and because u/s is small, $ p (1-p)\simeq p=u/s $ Summing over all n loci capable of mutating to deleterious alleles, the total genetic variance in fitness among individuals is $ 2 n u=U s $ ,where U=2nu is the diploid deleterious mutation rate.

This result can be used to evaluate the overall effect of unlinked background selection by noting that unless the number of chromosomes is very tiny, the vast majority of pairs of genes within genomes will be unlinked (with x chromosomes of equal size, the fraction of linked pairs will be < 1/x2 because genes located on opposite ends of chromosomes are effectively unlinked). Thus, we can make use of Robertson's equation (3.29c), noting that the variance of mean family fitness is Us/2 after discounting by averaging over both parents. This shows that in the absence of any linkage, deleterious mutations are expected to cause a relatively small reduction in $ N_{e} $

$$
N _ {e} \simeq \frac {N}{1 + 2 U s} \simeq N e ^ {- 2 U s}
$$

with the exponential approximation applying under the assumption that Us $ \ll1 $ . This assumption is justified by numerous observations suggesting that U is on the order of 0.1 to 1.0 and s is on the order of 0.01 (LW Chapter 12).

Some impression of the impact of linkage follows from the logic used to obtain Equations 3.29b and 3.29c. As noted above, for unlinked loci, the initial stochastic associations of neutral alleles and selected loci last for an average of $ \sum_{i=0}^{\infty}(1/2)^{i}=2 $ generations, giving a total contribution to the variance proportional to $ 2^{2} $ . Letting the recombination rate between loci be c, this expression generalizes to $ \sum_{i=0}^{\infty}(1-c)^{i}=1/c $ generations, and hence a contribution of $ 1/c^{2} $ to the variance. Thus, a single selected locus is expected to reduce the variation at a linked neutral locus, which in effect causes a local depression in the effective population size to

$$
N _ {e} \simeq N e ^ {- u s / c ^ {2}}
$$

(Barton 1995a). With $ c\ll0. 5 $ the absolute value of the exponential term can be considerably larger than that for unlinked loci, 4us. The challenge is to determine the joint effects of the full spectrum of all linked and unlinked loci surrounding the neutral reference locus.

Insight into the overall power of selection on linked deleterious mutations can be gleaned by considering the extreme case of a completely nonrecombining, but otherwise sexual, genome, i.e., allowing only for segregation during gamete production. Assuming a total of n selected loci, for which the mutant alleles have identical and multiplicative effects

on fitness, the average number of deleterious alleles in a gamete is $ n u / s=U / (2 s) $ ,where U is again the deleterious mutation rate per diploid genome. Assuming large enough $ N_{e} $ that deleterious mutations do not go to fixation, with this type of genomic architecture (no recombination), only those gametes that are free of deleterious mutations can contribute to the future genetic constitution of the population. Because the number of deleterious mutations per gamete is Poisson distributed in sufficiently large populations with multiplicative selection (Kimura and Maruyama 1966), the frequency of such mutation-free gametes is simply $ e^{-U / (2 s)} $ ,leading to the conclusion that with complete linkage, selection against segregating deleterious mutations leads to

$$
N _ {e} = N e ^ {- U / (2 s)}
$$

(Charlesworth et al. 1993a). This shows that background selection has the potential to cause a dramatic reduction in $ N_{e} $ in a nonrecombining (but segregating) population. For example, with U=0.1 and s=0.01, $ e^{-U / (2s)}=0.0067 $ . This expression also applies to a nonrecombining chromosomal region if U is redefined to be the deleterious mutation rate for the region under consideration.

Hudson and Kaplan (1994) extended this result to allow for recombination, assuming that the latter operates at uniform rates per physical distance over chromosomal regions. Their results show that

$$
N _ {e} \simeq N e ^ {- U / (2 s + C)}
$$

where C denotes the rate of recombination between the ends of the region. Because $ 1 / ( 2 s+ C) \gg s $ , Equation 3.35a predicts a much smaller $ N_{e} $ than that obtained for freely recombining loci (Equation 3.32), showing that the total contribution from interference from unlinked loci (which is embedded in Equation 3.35a) is relatively minor relative to that from loci in the immediate vicinity of the neutral locus. Moreover, because s is expected to be $ \ll1 $ , and for an entire chromosome, C is of order 1.0, Equation 3.35a can be roughly approximated as

$$
N _ {e} \simeq N e ^ {- U / C}
$$

where U/C is equivalent to the diploid deleterious mutation rate per unit of recombination (Hudson and Kaplan 1994, 1995). This result, which has been obtained by several different methods (Barton 1995a; Nordborg et al. 1996; Santiago and Caballero 1998), shows that the impact of segregating deleterious mutations on $ N_{e} $ is largely independent of the mutational effect s. As will be seen in Chapter 4, the ratio of mutation and recombination rates can be estimated from molecular polymorphism data, so if the fraction of mutations that are deleterious is known, U/C is also estimable.

Finally, it is worth noting that some conditions exist under which selection may actually promote an increase in $ N_{e} $ , the most obvious involving increases in the coalescence times for linked alleles in a chromosomal region under balancing selection. Pálsson and Pamilo (1999) also found that with very strong linkage and a low efficiency of selection $ (2Ns<1) $ repulsion disequilibrium can build up between simultaneously segregating deleterious mutations, leading to a form of associative overdominance (LW Chapter 10) and an elevation of $ N_{e} $ . Although this condition arises in the absence of direct balancing selection on any specific site, it remains unclear whether the special requirements necessary for such an outcome are very common. Santiago and Caballero (2005) also found that in a subdivided population, selective sweeps within demes can sometimes lead to an increase in $ N_{e} $ for the total metapopulation, as the migration of a sweeping chromosomal region drags new variation into a recipient deme, leading to an overall effect akin to balancing selection.

With these exceptions aside, there are two general lessons to be learned from all of the preceding discussion. First, although the individual demographic and genetic effects that influence $ N_{e} $ may appear to be only moderate in nature, their cumulative effects can easily depress $ N_{e} $ below the actual number of reproductive individuals by several orders of magnitude, and second, although population geneticists often develop analytical descriptions of various processes under the assumption of an effectively infinite population size, the

physical linkage of the genome ensures that even populations with extraordinarily large N need not be immune to drift-like processes imposed by hitchhiking effects. These points will be made clearer in Chapter 4 as we explore the direct manifestation of such effects on standing variation in natural populations.

Example 3.6. Because natural populations are subject to both positive and negative selective forces, the total influence of selection on $ N_{e} $ must reflect both background selection and selective sweeps. This necessarily raises even more technical issues than were outlined above. Significant progress was made by Kim and Stephan (2000), and here we simply outline the basic result. If background selection operates as an essentially continuous process resulting from the recurrent introduction of deleterious alleles, the depressive effects of both forms of selection, as well as baseline demographic effects, may be treated as largely independent. The reduction in $ N_{e} $ resulting from background selection can then be obtained by use of one of the above expressions, e.g., Equation 3.35b as a first-order approximation for a sexual population (with N already taking into consideration demographic effects).

Consider a large monoecious population of constant breeding size and variance in family size $ \sigma_{k}^{2}=4 $ . Based on demographic considerations alone, from Equation 3.4, $ N_{e}\simeq 2 N / 3 $ . Letting U=1 and C=1, Equation 3.35b implies that background deleterious mutations further reduce $ N_{e} $ to $ (2 N / 3) e^{-1}\simeq 0.25 N $ . The effective population size dictated by these demographic and deleterious-mutation processes further defines the background $ N_{e}^{\prime} $ within which occasional beneficial mutations arise and sweep to fixation, so that the effective population size resulting from the joint operation of all three effects can be approximated by substituting $ N_{e}^{\prime} $ for N in Equation 3.30b. Supposing a complete sweep occurs every 10,000 generations (so that $ f_{s}=1 $ and $ \delta=0.0001 $ ), then $ N_{e}=0.25 N /[1+(0.50 N\cdot 0.0001)] $ . With $ N=10^{4},10^{6}, $ and $ 10^{8} $ , this implies $ N_{e} / N\simeq 0.17,0.0049 $ , and 0.00005, respectively.

In general, the joint operation of background selection and selective sweeps will reduce $ N_{e} $ more than either does alone, although it is, at least in principle, possible for background selection to reduce the influence of selective sweeps in regions of very low recombination by depressing $ N_{e} $ , which in turn will reduce the fixation probability of favorable alleles (Chapters 7 and 8). The simultaneous operation of positive selection on multiple loci (which was ignored in the derivation of Equations 3.30a and 3.30b) can also slightly alleviate the overall effects of selection on $ N_{e} $ as simultaneously segregating mutations interfere with each other's fixation, thereby reducing the incidence of complete selective sweeps (Kim and Stephan 2003). These issues are examined in greater detail in Chapter 8.