## II

## Evolution at One and Two Loci

![](page=0,bbox=[116, 343, 753, 596])

<div align="center">

# Neutral Evolution in One and Two-Locus Systems

</div>

Variations neither useful nor injurious would not be affected by natural selection, and would be left either a fluctuating element, as perhaps we see in certain polymorphic species, or would ultimately become fixed, owing to the nature of the organism and the nature of the conditions. Charles Darwin (Chapter 4, 1859)

Although most of the research in evolutionary biology is focused on issues related to natural selection, the rigor of all such analyses depends critically on our understanding of expected patterns of evolution in the absence of selection. The simple reasoning here is that if we are to have much confidence in any adaptive argument, it ought to be possible to firmly reject a simpler, neutral hypothesis. Thus, prior to exploring various population-genetic models for adaptive evolution, we first embark on a broad overview of neutral models of evolution. The theory underlying such models brings us into immediate contact with the issue of genetic drift, a commonly misunderstood factor in evolutionary biology, but which is nothing more than the random fluctuations in allele frequencies that necessarily result from sampling finite numbers of gametes in each generation. The magnitude of such allele-frequency fluctuations increases with decreasing population size, and combined with the input of new alleles by mutation, the incessant stochasticity of the process ensures that populations will evolve even in the absence of selection (Kimura 1983).

Consider, for example, a single heterozygous Bb parent that produces two progeny. There is a 50% probability that one offspring will inherit the B allele and the other the b allele, in which case no net change in allele frequency has been transmitted from parent to offspring. However, there is also a 50% probability that both offspring will inherit the same allele. In extremely large populations, these random changes resulting from gamete sampling tend to average out, leaving the allele frequency in the offspring population very close to that in the parental generation. However, over sufficiently long time scales, the cumulative effects of even small single-generation changes in allele frequencies can become quite pronounced. As we will show, if the time scale of interest (t, in generations) is much less than the average number of reproductive adults in the population (N), random fluctuations in allele frequencies can usually be ignored. This justifies the assumption of an effectively infinite population size as a good first approximation in many applications of population and quantitative genetics. However, for situations in which t is on the order of N or larger, evolution can no longer be viewed as a strictly deterministic process. Rather, any observed evolutionary change must be viewed as one realization of many possible outcomes.

In the following pages, it will be shown that even though finite population size induces stochastic evolutionary change, genetic drift has several predictable effects. First, even if mating is completely random, there will still be some long-term trend toward matings among relatives. Because all members of a population must ultimately descend from a narrow ancestral base, the smaller the population size, the greater this tendency will be. Thus, in a tiny dioecious (separate-sex) population with a stable adult number of two, all matings must be between full sibs, even though the reproductive pair itself may be a random draw from a larger progeny pool in the preceding generation. It follows that the genetic consequences of finite population size must be similar to those of inbreeding—the average homozygosity at a locus is expected to increase with smaller N, although as noted below, this can be offset in part by replenishment from mutationally derived variation. Second, gamete sampling causes allele frequencies to gradually drift toward zero or one, with the probability of ultimate fixation of any particular allele in the absence of selection being equal to its initial frequency. Third, subdivision of a population into isolated demes

results in allele-frequency divergence among demes. The greater the degree of isolation of the subgroups, the more pronounced this differentiation will be.

This and the following two chapters provide a formal basis for these ideas. We first consider matters of one- and two-locus evolution in the context of a population with an idealized mating system and no influence from selective forces. As we will show in subsequent chapters, such models are often of great utility even when selection is operating, provided that the forces of selection are weaker than those associated with random genetic drift. In addition, such theory provides the underlying logic for the development of molecular-marker methods for estimating the power of mutation, recombination, and random genetic drift. These methods, the subject of Chapter 4, are the primary ways we have of describing the past population-genetic environment. Chapter 3 provides a critical link between Chapters 2 and 4 by demonstrating how results derived under the assumption of an ideal random mating population can be extended to a variety of alternative reproductive systems and population structures. In subsequent chapters, the one- and two-locus results introduced here will be used to develop neutral models for formal tests of adaptive evolution within a genomic region of interest (Chapters 8-10) and for the evolution of quantitative traits (Chapter 12).

## THE WRIGHT-FISHER MODEL

Because the number of possible types of population structure is literally infinite (involving, for example, various degrees of local inbreeding, geographic subdivision, and age-specific mortality and fecundity), and temporal variation in population size is also common, it is impossible for us to consider the dynamics of neutral alleles in a fully general sense. Instead, we will focus initially on single finite populations of constant size within which mating is random. Even this simple structure admits to many possible variants, depending, for example, on whether there are separate sexes, whether there is variation in family size, and whether generations overlap. These additional layers of complexity will be taken up in Chapter 3, where it will become clear that, with an appropriate redefinition of the concept of population size, most of the results in the current chapter often still hold.

Perhaps the most frequent description of drift is the Wright-Fisher model, whose roots trace to Fisher (1922) and Wright (1931). We assume here a diploid population with a fixed number (N) of monoecious (hermaphroditic) adults, random mating (including the possibility of self-fertilization), and discrete generations, and we follow the number $ ( 0 \leq i \leq 2 N ) $ of copies of a given allele. The gamete pool produced by the adults is assumed to be effectively infinite, such that the 2N gametes that actually contribute to the next generation can be viewed as being sampled with replacement.

Consider a locus with two alleles, B and b, with neither having a selective advantage with respect to the other. If there are i copies of allele B in generation t, the probability $ P_{ij} $ that the number in generation t+1 is equal to j follows the binomial distribution. Assuming the Wright-Fisher model, each of the 2N sampled gametes has probability $ i / (2N) $ of being B and probability $ [1-(i/2N)] $ of being b, yielding

$$
P _ {i j} = \binom {2 N} {j} \left(i / 2 N\right) ^ {j} \left[ 1 - \left(i / 2 N\right) \right] ^ {2 N - j}
$$

where the first term in large parentheses is the binomial coefficient. This expression holds for all possible values of i,j=0,1,...,2N. Note that throughout we will be referring to a diploid population of size N, which requires 2N gametes for replacement; this same expression applies to a haploid population of size N if the 2 is deleted.

Letting P be the $ ( 2 N+1 ) \times( 2 N+1 ) $ matrix of all the $ P_{i j} $ , the probability distribution of the number of copies of allele B in a population can then be expressed succinctly as

$$
\mathbf {x} (t + 1) = \mathbf {x} (t) \mathbf {P}
$$

where the elements of the row vector $ \mathbf{x} ( t ) $ are the probabilities that the allele is present in $ i=0,1,\dots,2 N $ copies in generation t. Note that $ P_{i j} $ , which refers to the element in row i and

column j in matrix P, is the probability that a population makes a transition from i copies of B to j copies, conditional on starting at i. If the transition matrix P remains constant from generation to generation, as it does under the assumptions given previously, Equation 2.2a generalizes to

$$
\mathbf {x} (t) = \mathbf {x} (0) \mathbf {P} ^ {t}
$$

This is an example of a Markov chain (considered in more detail in Appendix 3).

When considering a single population starting with an allele frequency of $ i/2N $ , all of the entries in the initial vector $ \mathbf{x} ( 0 ) $ are equal to zero, except $ x_{i} ( 0 )=1. 0 $ (corresponding to i copies being present). Equation 2.2b then yields the evolution of the probability distribution of allelic copy number over time. That is, the elements of $ \mathbf{x} ( t ) $ denote the frequencies of hypothetical replicate populations at time t that are expected to have exactly i copies of the focal allele. The first $ ( i=0 ) $ and final $ ( i=2 N ) $ elements of $ \mathbf{x} ( t ) $ are of special interest, as they are absorbing states once an allele becomes lost $ ( i=0 ) $ or fixed $ ( i=2 N ) $ in a population, it remains at that state indefinitely (barring reintroduction via mutation or migration). As t increases in Equation 2.2b, all of the interior elements of $ \mathbf{x} ( t ) $ eventually converge on zero, and the sum $ x_{0} ( t )+x_{2 N} ( t ) $ converges to one. The ultimate probability of fixation of allele B is given by $ x_{2 N} ( \infty ) $ , whereas the ultimate probability of loss of allele B (or equivalently, of fixation of allele b) is $ x_{0} ( \infty ) $ .

From the elements of $ \mathbf{x} ( t ) $ , it is straightforward to compute the expected allelic copy number, the variance in copy number among replicate populations, the probability of fixation by generation t, etc. This transition-matrix approach is exact, but many useful approximations have been developed for it (e.g., Gale 1990; Ewens 2004). Some of these approaches will be discussed later, with a powerful alternative method, the diffusion approximation being covered extensively in Appendix 1. In a diffusion, the focus shifts from copy number to allele frequency.

It should be noted that the Wright-Fisher model, in which all individuals synchronously turn over, is just one of many possible conceptual frameworks for approximating a randomly mating population. For example, Moran (1962) developed a treatment whereby a single random individual is chosen to reproduce at each point in time, with a single random individual then being chosen to die. Because allele frequencies can change by only single steps during each time interval under this scenario, the Moran model turns out to be more analytically tractable than the Wright-Fisher model, although it is restricted to haploid populations.

Example 2.1. Consider an initially heterozygous individual Bb in a self-fertilizing line maintained by single-progeny descent. With N=1, the only three possible allele-frequency states in the population are zero, one, or two B alleles. Denoting the initial state of the population by $ \mathbf{x} ( 0 )=[ 0,1,0] $ , the probability that the population is in states 0,1, or 2 at some future generation t is given by Equation 2.2b with

$$
\mathbf {P} = \left( \begin{array}{c c c} 1 & 0 & 0 \\ 0. 2 5 & 0. 5 0 & 0. 2 5 \\ 0 & 0 & 1 \end{array} \right)
$$

Although the numerical values for the elements of P can be obtained directly from Equation 2.1, for this simple example they can also be arrived at intuitively. For example, the elements in the first row of P denote the probabilities that the population will be in states $ j=0,1,2 $ in generation $ t+1 $ given that it is in state 0 in generation $ t $ . The only nonzero element in this row is $ P_{00}=1 $ . It is nonzero because the $ i=0 $ state is absorbing, i.e., once the population enters this state, it remains there indefinitely.

The probability of being in any particular allele-frequency category in generation $ t $ , which follows from Equation 2.2b, is a function of $ \mathbf{P}^{t} $ , so for example,

$$
\mathbf {P} ^ {2} = \left( \begin{array}{c c c} 1 & 0 & 0 \\ 0. 3 7 5 & 0. 2 5 0 & 0. 3 7 5 \\ 0 & 0 & 1 \end{array} \right), \quad \mathbf {P} ^ {5} = \left( \begin{array}{c c c} 1 & 0 & 0 \\ 0. 4 8 4 3 8 & 0. 0 3 1 2 5 & 0. 4 8 4 3 8 \\ 0 & 0 & 1 \end{array} \right)
$$

<div align="center">

and so on. With the initial vector $ \mathbf{x} ( 0 ) = ( 0,1,0) $ only the middle row of $ \mathbf{P}^{t} $ is relevant, giving the following table for the progression of the elements of $ \mathbf{x} ( t ) $ over time:

</div>

<table border="1"><tr><td>t</td><td>BBx0(t)</td><td>Bbx1(t)</td><td>bbx2(t)</td></tr><tr><td>0</td><td>0.00000</td><td>1.00000</td><td>0.00000</td></tr><tr><td>1</td><td>0.25000</td><td>0.50000</td><td>0.25000</td></tr><tr><td>2</td><td>0.37500</td><td>0.25000</td><td>0.37500</td></tr><tr><td>3</td><td>0.43750</td><td>0.12500</td><td>0.43750</td></tr><tr><td>4</td><td>0.46875</td><td>0.06250</td><td>0.46875</td></tr><tr><td>5</td><td>0.48438</td><td>0.03125</td><td>0.48438</td></tr><tr><td>...</td><td>...</td><td>...</td><td>...</td></tr><tr><td>10</td><td>0.49951</td><td>0.00098</td><td>0.49951</td></tr><tr><td>...</td><td>...</td><td>...</td><td>...</td></tr><tr><td>15</td><td>0.49998</td><td>0.00003</td><td>0.49998</td></tr><tr><td>...</td><td>...</td><td>...</td><td>...</td></tr><tr><td>∞</td><td>0.50000</td><td>0.00000</td><td>0.50000</td></tr></table>

The first and last elements of $ \mathbf{x}(t) $ , respectively, denote the probabilities that the line will have become fixed for the B or the b allele by time t. Thus, for this particular case, the line eventually becomes completely monomorphic for either the B or the b allele with equal probability. This meets our intuitive expectations for a neutral locus—in the absence of any directional forces, the two probabilities of fixation are equal to the initial frequencies of the respective alleles.

## LOSS OF HETEROZYGOSITY BY RANDOM GENETIC DRIFT

The sampling variance of an allele frequency provides one way to succinctly define the stochastic effects of random genetic drift. Consider a large pool of gametes, a fraction p of which carry the B allele, and let 2N gametes be randomly drawn to produce a new generation of N individuals. Defining the expected frequencies of genotypes BB, Bb, and bb in the progeny generation by the Hardy-Weinberg proportions $ p^{2}, $ 2p(1-p), and $ (1-p)^{2} $ the expected number of B alleles contained in a random offspring is simply $ (2\cdot p^{2})+[1\cdot 2 p(1-p)]+[0\cdot(1-p)^{2}]=2 p $ . The expected square of the number of B alleles carried per individual is $ (2^{2}\cdot p^{2})+[1^{2}\cdot 2 p(1-p)]+[0^{2}\cdot(1-p)^{2}]=2 p(1+p) $ . Thus, the variance (the mean squared value minus the square of the mean) of the number of B alleles carried by an individual is $ 2 p(1+p)-(2 p)^{2}=2 p(1-p) $ , whereas the variance of the total number of B alleles carried in the offspring generation is N times this, $ 2 N p(1-p) $ . Because the frequency of allele B is the number of copies divided by 2N, the sampling variance of the frequency (a second-order moment) is $ 2 N p(1-p)/(2 N)^{2}=p(1-p)/(2 N) $ , which is directly proportional to the heterozygosity (the fraction of Bb individuals in the population) and inversely proportional to the population size. The expression $ p(1-p)/(2 N) $ defines the dispersion in allele frequency resulting from a single generation of gamete sampling, conditional on allele frequency p in the parental population.

In the absence of any counteracting evolutionary forces, the dispersive effects of genetic drift will continue in each generation, leading to a progressive erosion of population-level heterozygosity until all loci have eventually become fixed for just a single allele. To evaluate the long-term impact of finite population size on the expected heterozygosity of a locus, we make use of the properties of the inbreeding coefficient, f, which denotes the probability that two alleles at a locus in an individual are identical by descent (IBD) (LW Chapter 7).

![](page=6,bbox=[290, 146, 587, 248])

<div align="center">

Figure 2.1 Distinction between alleles that are identical in state (IIS) and identical by descent (IBD). The simple example is a case in which the population consists of just three individuals, so that the total number of gametes transmitted randomly per generation is $ 2 N=6 $ . A polymorphism exists in the time-zero population (black and white alleles), so not all alleles are initially IIS. After one generation of sampling, two pairs of alleles are IBD because the two copies are direct copies of a parental allele.

</div>

Because all gene copies at a locus must ultimately trace back to a single, remote common ancestor, it is essential to start with an appropriate reference generation, which we here take to be the current generation, and then simply query forward in time as to the probability that any random pair of genes traces back to a specific copy of one of the 2N genes present at the locus in the reference generation. Under this framework, a pair of genes that are identical in state (IIS; also know as alike in state, AIS) need not be IBD, but barring mutation, genes that are IBD must also be IIS (Figure 2.1).

There is always a small chance that uniting gametes will derive from related individuals, even in a randomly mating population. For example, in a monoecious population containing only two individuals, there are only four genes residing at each locus, so the probability that one gamete will randomly unite with another containing a direct descendant of the same parental gene is 1/4. With four individuals, there are eight gene copies, and this probability becomes 1/8. Thus, under the idealized Wright-Fisher model with population size N, the probability that two direct copies of any parental gene will randomly unite in an offspring is $ 1 / (2 N) $ . Barring a rare mutation, all such offspring are homozygotes.

Although the quantity $ 1 / (2 N) $ may be thought of as the new inbreeding that is incurred in each generation, this does not fully describe the buildup of homozygosity in a population. For even if uniting gametes do not carry genes that are direct copies of a parental gene, they may still be identical by descent through inbreeding in a previous generation. Under random mating, the probability of the latter event is simply the inbreeding coefficient of the parental generation. Thus, because the probability of drawing genes that are not direct copies of the same parental gene is $ [ 1-(1/2 N) ] $ , the expected inbreeding coefficient in generation t is

$$
f _ {t} = \frac {1}{2 N} + \left(1 - \frac {1}{2 N}\right) f _ {t - 1}
$$

$$
\left(1 - f _ {t}\right) = \left(1 - \frac {1}{2 N}\right) \left(1 - f _ {t - 1}\right)
$$

Subtracting both sides from one yields the recursion formula

which generalizes to

$$
\left(1 - f _ {t}\right) = \left(1 - \frac {1}{2 N}\right) ^ {t} \left(1 - f _ {0}\right)
$$

and finally to

$$
\left(1 - f _ {t}\right) = \left(1 - \frac {1}{2 N}\right) ^ {t}
$$

if we assume a noninbred base population $ ( f_{0}=0) $ . Again, we see the central role that population size plays in the dynamics of genetic variation. As $ t\rightarrow\infty $ , the fraction of the population that is not inbred, $ 1-f_{t} $ , approaches zero at a rate that is inversely proportional to N.

To see the connection between the inbreeding coefficient and the expected heterozygosity in a population, consider a diallelic locus with base-population heterozygosity 2p(1-p). In the descendant population with inbreeding coefficient f, individuals can only be heterozygotes if they carry alleles that are not identical by descent, the probability of which is (1-f). If two alleles are not identical by descent, they must have been acquired independently, so the probability that a genotype containing a pair of such alleles is a heterozygote is 2p(1-p). Thus, the expected heterozygosity of a population with inbreeding coefficient f and initial allele frequency p is 2p(1-p)(1-f). This shows that the fractional reduction in heterozygosity relative to the base population is equal to f. Because this argument applies regardless of the initial heterozygosity (and regardless of the number of segregating alleles), Equation 2.4c may be rewritten to describe the expected population heterozygosity at time t,

$$
H _ {t} = H _ {0} \left(1 - \frac {1}{2 N}\right) ^ {t}
$$

This rate of decay of heterozygosity of 1/（2N）was first obtained by Wright (1931). It may be a source of encouragement to the nonmathematically inclined that the brilliant Fisher (1922), using a rather different approach, obtained the wrong answer.

The time course for the loss of heterozygosity can be clarified by using an exponential approximation to Equation 2.5. Because $ ( 1-x )^{t}\simeq e^{-xt} $ for $ |x|\ll1 $ , for N greater than 10 or so,

$$
H _ {t} \simeq H _ {0} e ^ {- t / (2 N)}
$$

Rearrangement then leads to the expected time to reach a certain reduction in heterozygosity,

$$
t = - 2 N \ln \left(H _ {t} / H _ {0}\right)
$$

which shows that the heterozygosity is reduced to half of its initial value in $ \sim 1. 4 N $ generations and to 5% of $ H_{0} $ in $ \sim 6 N $ generations. Thus, a population twice the size of another requires twice the number of generations to reach the same expected state.

With a temporally varying population size, Equation 2.6a becomes

$$
H _ {t} = H _ {0} \prod_ {i = 1} ^ {t} \left(1 - \frac {1}{2 N _ {i}}\right) \simeq H _ {0} \exp \left[ - \sum_ {i = 1} ^ {t} 1 / \left(2 N _ {i}\right) \right]
$$

where the $ \prod $ sign denotes a product of terms, and $ N_{i} $ is the population size in generation i. This expression illustrates an important point. Because each of the generation-specific terms, $ [1-(1/2N_{i})] $ , is necessarily less than one, Equation 2.7 shows that an expansion of population size can reduce the rate of erosion of heterozygosity, but does not eliminate it.

One significant limitation of the preceding expressions is that they only provide information on the behavior of the expected heterozygosity in a population. In reality, fluctuations in allelic copy number resulting from random genetic drift ensure that variation in heterozygosity will arise among loci that start in the same state. In a finite population of size N, the heterozygosity of a diallelic locus can take on N+1 discrete values: 0, 2(1/2N)[1-(1/2N)], $ \cdots $ , 2(N/2N)[1-(N/2N)]. Using the transition-matrix approach (Equations 2.2a and 2.2b), one can obtain the exact probability distribution of heterozygosity for a locus starting with allele frequency i/2N, using the fact that $ x_{j}(t)+x_{2N-j}(t) $ is the probability that the population has heterozygosity 2(j/2N)[1-(j/2N)].

An alternative approach was developed by Kimura (1955b), who used diffusion theory (Appendix 1) to obtain an analytical expression for the probability density of allele frequency

at time t, given the starting value $ p_{0} $

$$
\begin{array}{l} \varphi \left(p _ {t} \mid p _ {0}\right) = p _ {0} \left(1 - p _ {0}\right) \sum_ {i = 1} ^ {\infty} i \left(2 i + 1\right) \left(i + 1\right) \cdot \\ F \left(1 - i, i + 2, 2, p _ {0}\right) \cdot F \left(1 - i, i + 2, 2, p _ {t}\right) \cdot e ^ {- i (i + 1) t / (4 N)} \\ \end{array}
$$

where F(1-i,i+2,2,p $ _{0} $ ) and F(1-i,i+2,2,p $ _{t} $ ) are specific variants of the hypergeometric function (Equation 15.1.1 in Abramowitz and Stegun 1972). When we use this expression, $ [\varphi(p_{t}|p_{0})+\varphi(1-p_{t}|p_{0})] $ is the probability of heterozygosity $ 2 p_{t}(1-p_{t}) $ at time t. We will make more use of Equation 2.8 in the next sections, illustrating in particular its implications for the dispersion of allele frequencies among isolated populations. The utility of the diffusion approximation is that it yields to numerous closed-form mathematical approximations, some of which we note below.

## PROBABILITIES AND TIMES TO FIXATION OR LOSS

Because Equation 2.8 denotes the probability density of allele frequency p given that the population is still polymorphic,

$$
\Omega \left(p _ {0}, t\right) = \int_ {1 / (2 N)} ^ {1 - 1 / (2 N)} \varphi \left(p _ {t} \mid p _ {0}\right) d p _ {t}
$$

is the probability that both alleles are still present in generation t. The probability that an allele with initial frequency $ p_{0} $ has been fixed by generation t is

$$
\begin{array}{l} p _ {f} \left(p _ {0}, t\right) = p _ {0} + p _ {0} \left(1 - p _ {0}\right) \sum_ {i = 1} ^ {\infty} \left(2 i + 1\right) (- 1) ^ {i} \\ \cdot F \left(1 - i, i + 2, 2, p _ {0}\right) \cdot e ^ {- i (i + 1) t / 4 N} \\ \end{array}
$$

whereas the probability of loss of the allele, $ p_{l} ( p_{0}, t ) $ , is given by Equation 2.9b with $ ( 1-p_{0} ) $ exchanged for $ p_{0} $ (Kimura 1955b). Summing up,

$$
\Omega \left(p _ {0}, t\right) + p _ {f} \left(p _ {0}, t\right) + p _ {l} \left(p _ {0}, t\right) = 1
$$

As can be seen from the negative exponential terms in the previous expressions, as $ t \to \infty $ $ \Omega ( p_{0}, t ) \to 0, p_{f} ( p_{0}, t ) \to p_{0} $ , and $ p_{l} ( p_{0}, t ) \to ( 1 - p_{0} ) $ . Thus, under neutrality, the probability that a particular allele will become fixed is simply equal to its initial frequency, $ p_{0} $ . It follows that, in averaging over a very large number of replicate populations, the expected allele frequency will remain constant at $ p_{0} $ , with a fraction $ p_{0} $ of all replicates ultimately reaching allele frequency 1, and the remaining fraction $ 1-p_{0} $ having allele frequency 0.

An issue of special interest is the mean time until an allele is absorbed into either state p=0 or p=1. Using diffusion approximations (Appendix 1), Kimura and Ohta (1969a) obtained expressions for both quantities, and Kimura (1970) presented a description of the entire probability distributions for absorption times. The following example uses a somewhat simpler approach to arrive at results identical to those of Kimura and Ohta (1969a), and provides yet another illustration of how the effects of random genetic drift scale with population size.

Example 2.2. Ewens (2004) used the following line of reasoning to derive the expected time to absorption of a neutral allele under the Wright-Fisher model. Letting $ \delta p $ denote the change in allele frequency in one unit of time, the mean time to absorption for an allele with frequency p may be rewritten as

$$
\bar {t} _ {a} (p) = E \left[ \bar {t} _ {a} (p + \delta p) \right] + 1
$$

where E denotes an expected value. In words, this expression states that the mean absorption time starting at frequency p is equal to the mean absorption time one time unit later when the allele frequency is $ p+\delta p $ , plus one. Approximating $ \bar{t}_{a}(p+\delta p) $ by the first three terms in its Taylor series (see LW Equation A1.2) and then taking expectations (only the $ \delta p $ are random terms; the rest are fixed constants), gives

$$
\begin{array}{l} E [ \bar {t} _ {a} (p + \delta p) ] \simeq E \left[ \bar {t} _ {a} (p) + \delta p \frac {\partial \bar {t} _ {a} (p)}{\partial p} + \frac {(\delta p) ^ {2}}{2} \frac {\partial^ {2} \bar {t} _ {a} (p)}{\partial p ^ {2}} \right] \\ = \bar {t} _ {a} (p) + E [ \delta p ] \frac {\partial \bar {t} _ {a} (p)}{\partial p} + \frac {E [ (\delta p) ^ {2} ]}{2} \frac {\partial^ {2} \bar {t} _ {a} (p)}{\partial p ^ {2}} \\ \end{array}
$$

Hence, we have

$$
\bar {t} _ {a} (p) \simeq \bar {t} _ {a} (p) + E [ \delta p ] \frac {\partial \bar {t} _ {a} (p)}{\partial p} + \frac {E [ (\delta p) ^ {2} ]}{2} \frac {\partial^ {2} \bar {t} _ {a} (p)}{\partial p ^ {2}} + 1
$$

Under neutrality, the expected change in allele frequency is $ E(\delta p)=0 $ , and as derived previously, the expected variance in allele-frequency change is $ E[(\delta p)^{2}]=p(1-p)/(2N). $ Substituting into our approximation and rearranging gives

$$
\bar {t} _ {a} (p) - \bar {t} _ {a} (p) - 1 \simeq \frac {p (1 - p)}{2 \cdot 2 N} \frac {\partial^ {2} \bar {t} _ {a} (p)}{\partial p ^ {2}}
$$

$$
\frac {\partial^ {2} \bar {t} _ {a} (p)}{\partial p ^ {2}} \simeq - \frac {4 N}{p (1 - p)}
$$

which implies the differential equation

Performing the double integration with respect to p leads to the solution

$$
\bar {t} _ {a} \left(p _ {0}\right) \simeq - 4 N \left[ p _ {0} \ln \left(p _ {0}\right) + \left(1 - p _ {0}\right) \ln \left(1 - p _ {0}\right) \right]
$$

which is the mean time until an allele with initial frequency $ p_{0} $ is either lost or fixed in a population.

A similar approach can be used to estimate the mean time to fixation for the subset of alleles that specifically become fixed, $ \bar{t}_{f}(p_{0}) $ . The essential modification here is that in estimating $ \bar{t}_{f}(p_{0}) $ , $ E(\delta p) $ is no longer equal to zero, because in order for an allele to become fixed, at least one copy must be produced in each generation. That is, in the case of conditional fixation, of the 2N genes drawn in each generation, one is definitely a B allele, whereas the remaining 2N-1 genes can be viewed as random, leading to $ E(\delta p)=\{(1/2N)+[1-(1/2N)]p\}-p=(1-p)/(2N) $ . Similarly, because the states of only 2N-1 genes are random, $ E[(\delta p)^{2}]=\{(1\cdot 0)+[(2N-1)p(1-p)]\}/(2N)^{2} $ . Unless N is very small, the approximation $ E[(\delta p)^{2}]=p(1-p)/(2N) $ still holds quite well, and following the procedures utilized previously, we then have

$$
\left(\frac {2}{p}\right) \frac {\partial \bar {t} _ {f} (p)}{\partial p} + \frac {\partial^ {2} \bar {t} _ {f} (p)}{\partial p ^ {2}} \simeq - \frac {4 N}{p (1 - p)}
$$

The solution of this second-order differential equation requires several steps, which we omit, the final result being

$$
\bar {t} _ {f} \left(p _ {0}\right) \simeq - \frac {4 N \left(1 - p _ {0}\right) \ln \left(1 - p _ {0}\right)}{p _ {0}}
$$

The mean time to loss of an allele conditional upon loss is identical to the previous expression, but with $ ( 1-p_{0} ) $ interchanged with $ p_{0} $

$$
\bar {t} _ {l} \left(p _ {0}\right) \simeq - \frac {4 N p _ {0} \ln \left(p _ {0}\right)}{1 - p _ {0}}
$$

These expressions show that the conditional time to fixation asymptotically approaches 4N generations for rare alleles, with the more general fate of such alleles being loss from the population in $ \ll 4 N $ generations (Figure 2.2).

Finally, because the probability of ultimate fixation of a neutral allele is equal to its initial frequency $ ( p_{0} ) $ and the probability of ultimate loss is $ ( 1-p_{0} ) $ , it follows that

$$
\bar {t} _ {a} \left(p _ {0}\right) = p _ {0} \bar {t} _ {f} \left(p _ {0}\right) + \left(1 - p _ {0}\right) \bar {t} _ {l} \left(p _ {0}\right)
$$

Example A1.8 (in Appendix 1) uses diffusion theory to obtain results identical to those just presented.

## THE AGE OF A NEUTRAL ALLELE

A classic result from standard theory relates the age of a neutral allele to its frequency (Kimura and Ohta 1973; Maruyama 1974; Watterson 1976; Slatkin and Rannala 1997, 2000). In particular, the expected age t (in generations) of an allele with current frequency p is

$$
E (t) = - \frac {4 N p \ln (p)}{1 - p}
$$

assuming a constant population size during the allele's sojourn through the population Kimura and Ohta 1973). As shown in Figure 2.3, alleles at higher frequency are expected to be older. Most notably, as $ p \rightarrow 1 $ $ E ( t ) \rightarrow 4 N $ generations, which is consistent with the result in the previous example showing that the mean time to fixation of a rare (e.g., new mutant) neutral allele is 4N generations. This result is more than just an esoteric finding, as one class of tests for selection evaluates whether an allele, given its frequency, is too young to be compatible with neutrality (Chapter 9).

Equation 2.12 is not, however, the whole story, as a very old allele can sometimes be at low frequency, having transiently drifted up to a high frequency before drifting back toward zero frequency by chance. Thus, we expect the confidence interval for allele-age estimates to be highly asymmetric about the mean. Slatkin and Rannala (2000) provide an approximation for the cumulative probability for the age of an allele, given a frequency of p in a random sample of n alleles,

$$
\Pr (t \leq \tau) = (1 - p) ^ {- 1 + [ n / (1 + n N \tau) ]}
$$

One final caveat is in order with respect to Equation 2.12. Unless the sample size is very large, the estimated frequency of a rare allele can be quite misleading. Consider, for example, a singleton with a sample frequency of 1/n. Application of Equation 2.12 would imply an estimated age of $ 4 N \ln(n) /[n(1-1/n)] $ generations. If ten diploid individuals were sampled, the minimum allele frequency would be 0.05, so the estimated age of a singleton would be $ \sim 0.84 N $ generations. As very rare alleles, with true frequencies $ \ll1/n $ will either be recorded as singletons or not at all in a sample of size n, it is clear that Equation 2.12 yields upwardly biased estimates of the ages of rare alleles unless the sample size is large enough that the estimate of frequency p is highly accurate.

<div align="center">

Example 2.3. The mutation CCR5-832 destroys the human CCR5 receptor, which is used by the HIV virus to enter the cell, leading to significant resistance against HIV infection. This deletion occurs at frequencies up to 14% in Eurasians, but is absent in Africans, Native Americans, and East Asians. Assuming a frequency of p=0.10 and an effective population size N=5000 for Caucasians, Stephens et al. (1998) used Equation 2.12 to estimate the age of this allele (under the assumption of neutrality) to be

</div>

$$
\widehat {t} = - \frac {4 \cdot 5 0 0 0 \cdot 0 . 1 \log (0 . 1)}{0 . 9} = 5 1 1 6 \mathrm {g e n e r a t i o n s}
$$

![](page=11,bbox=[385, 150, 724, 383])

<div align="center">

Figure 2.2 Mean times to fixation and loss of neutral alleles with starting frequency $ p_{0} $ (from Equations 2.11b and 2.11c). The times are scaled in units of 4N generations, and thus need to be multiplied by 4N to obtain absolute numbers of generations.

</div>

![](page=11,bbox=[390, 507, 739, 741])

<div align="center">

Figure 2.3 Expected age of a neutral allele, given its frequency p (Equation 2.12). Time is scaled in units of 4N generations.

</div>

However, an independent (and more direct) estimate of the allele's age can be obtained by considering the variation in haplotypes among all sequences carrying this mutation. The $ \delta 3 2 $ mutation is in strong linkage disequilibrium with allele 215 at the AFMB marker (a highly

variable tandem-repeat locus), to the extent that 84.8% (39 of 46) of sampled $ \delta 3 2 $ mutations have the $ \delta 3 2 $ -215 haplotype. Clearly, the initial $ \delta 3 2 $ mutation at CCR5 must have arisen on a chromosome carrying the 215 allele. The recombination fraction between CCR5 and AFMB was estimated by Stephens et al. (1998) to be $ c=0.006 $ . The probability of the $ \delta 3 2 $ -215 haplotype remaining intact after t generations (i.e., experiencing no recombinational breakdown) is just $ \pi =(1-c)^{t} $ , which rearranges to

$$
t \simeq \ln (\pi) / \ln (1 - c) = 2 7. 4 \mathrm {g e n e r a t i o n s}
$$

Stephens et al. (1998) took these great disparities between age estimates as an indicator that strong selection has promoted the $ \delta 3 2 $ mutation much more rapidly than would be likely under a pure drift model. Assuming $ \delta 3 2 $ originated as a single mutation, they estimated the selection coefficient to be between 0.2 and 0.4, depending on assumptions about dominance. We will revisit the age of this mutation in Example 9.14.

Example 2.4. Consider a situation in which a random sample of 500 gametes from a population yields 350 copies of a particular allele A, and hence an estimated p of 0.7. Under the joint assumptions of neutrality and constant population size, what is the 95% confidence interval for the estimated age of this allele? From Equation 2.12, the expected age is

$$
\widehat {t} = - \frac {(4 N) 0 . 7 \ln (0 . 7)}{1 - 0 . 7} = 1. 4 5 N
$$

An approximate confidence interval using the approximation given by Equation 2.13 is obtained as follows. To account for N, we first rescale time so that $ \tau=2 N $ generations, and after solving for the critical values of $ \tau $ on this scale, we convert it back to generations. Define $ \tau_{\alpha} $ as satisfying $ \operatorname* {P r} ( t \leq \tau_{\alpha} )=\alpha $ . The 95% confidence interval for allelic age $ t $ is given by $ \left( \tau_{0.025},\tau_{0.975}\right) $ . From Equation 2.13, $ \tau_{0.025} $ must satisfy

$$
(0. 3) ^ {- 1 + \left[ 5 0 0 / \left(1 + 2 5 0 \tau_ {0. 0 2 5}\right) \right]} = 0. 0 2 5
$$

the solution of which is $ \tau_{0.025}=0.49 $ or $ 0.49*(2N)=0.98N $ generations (Equation 9.38d gives an approximation for $ \tau $ when n is large). The same procedure can be used to find that $ \tau_{0.975}=3.9N $ , showing that the confidence interval about the mean value is very asymmetric.

## ALLELE-FREQUENCY DIVERGENCE AMONG POPULATIONS

A natural consequence of allele-frequency drift within populations is the divergence of isolated replicate populations. Suppose a monoecious base population with allele frequency $ p_{0} $ is suddenly split into several completely isolated subpopulations, each of size N, with random mating within each subpopulation and no selection, migration, or mutation. The variance in allele frequency among subpopulations in generation t is

$$
\sigma_ {p} ^ {2} (t) = E \left(p _ {t} ^ {2}\right) - E ^ {2} \left(p _ {t}\right)
$$

Adding and subtracting $ E(p_{t}) $

$$
\begin{array}{l} \sigma_ {p} ^ {2} (t) = \left[ E \left(p _ {t}\right) - E ^ {2} \left(p _ {t}\right) \right] + \left[ E \left(p _ {t} ^ {2}\right) - E \left(p _ {t}\right) \right] \\ = E \left(p _ {t}\right) \left[ 1 - E \left(p _ {t}\right) \right] - E \left[ p _ {t} \left(1 - p _ {t}\right) \right] \\ \end{array}
$$

Because there are no systematic forces causing the allele frequency to increase or decrease, $ E(p_{t})=p_{0} $ , so the first quantity on the right is $ p_{0}(1-p_{0}) $ . The quantity $ E[p_{t}(1-p_{t})]$ is half

the expected heterozygosity in a population in generation $ t $ which was already defined in Equation 2.5. Thus

$$
\sigma_ {p} ^ {2} (t) = p _ {0} \left(1 - p _ {0}\right) \left[ 1 - \left(1 - \frac {1}{2 N}\right) ^ {t} \right]
$$

which is well approximated by

$$
\sigma_ {p} ^ {2} (t) \simeq p _ {0} \left(1 - p _ {0}\right) \left(1 - e ^ {- t / 2 N}\right)
$$

for $ N > 1 0 $ . This shows that the among-population variance asymptotically approaches $ p_{0}(1-p_{0}) $ , which is half the heterozygosity in the base population—over time, the allelic variance within populations (half of the quantity in Equation 2.6a) is transformed into among-population variance, with the total of the two remaining constant. An alternative way to envision this asymptotic result is to note that at fixation the allele frequency has a value of 1.0 with probability $ p_{0} $ , and otherwise is zero, giving $ E(p_{0})=1\cdot p_{0} $ and $ E(p_{0}^{2})= $ $ 1^{2}\cdot p_{0}=p_{0} $ . Hence, the among-population variance when all alleles are fixed is just $ E(p_{0}^{2})- $ $ [E(p_{0})]^{2}=p_{0}(1-p_{0}). $

Although Equations 2.14a and 2.14b deal with the expected allele-frequency variance, they do not describe the actual form of the distribution of population allele frequencies. However, all of this information is contained in the formulations presented previously on the probability distribution of allele frequencies within populations. For example, the transitionmatrix approach (Equations 2.2a and 2.2b) and the diffusion approximation (Equation 2.8) yield the expected temporal dynamics of the distribution of allele frequencies in different replicate populations, all starting from an identical frequency, $ p_{0} $ (Figure 2.4).

Summing up the calculations to this point, five significant conclusions can be gleaned with respect to neutral alleles. First, with increasing time, the total probability mass for the allele-frequency distribution at a locus declines because only segregating alleles are considered, i.e., the proportions of populations that have experienced gene fixation or loss are ignored. Second, regardless of the starting condition, the distribution becomes flatter with increasing time, such that the frequency of a sufficiently old segregating allele is equally likely anywhere over the (0,1) interval. Third, high-frequency alleles are generally expected to be old. Fourth, the distributions in Figure 2.4 can be interpreted in two different ways: as the probability distribution of allele frequencies over a very large number of replicate populations over time, all starting at an identical state, or as the expected distribution of allele frequencies for the subset of loci with identical starting frequencies within a single population. Finally, the expected allele-frequency distribution is a function of $ t/N $ generations, as can be seen from the exponential terms in Equation 2.8. As should be clear by now, this scaling of the temporal dynamics of random genetic drift to the reciprocal of population size is a natural consequence of the fact that the variance of allele-frequency change is inversely proportional to N.

## BURI'S EXPERIMENT

Because all populations are finite in size, the theory of random genetic drift is of central significance to all areas of population genetics. It may therefore come as a surprise that highly replicated experiments examining the chance dynamics of allele-frequency change are extremely rare. However, the results of one massive experiment nicely affirm the theoretical expectations outlined above, while making one additional important point. Starting with two homozygous lines of Drosophila melanogaster, one of which was fixed for allele $ b w^{7 5} $ and the other for allele bw at the brown locus, Buri (1956) established 212 $ F_{1} $ hybrid populations, with initial frequency 0.5 for both alleles. For the following 19 generations, he randomly mated eight males and eight females within each population and monitored the changes in allele frequencies in each subline. This could be done in the premolecular era because the genotype at the brown locus determines eye color: $ b w^{7 5} b w^{7 5}= $

![](page=14,bbox=[124, 155, 760, 480])

<div align="center">

Figure 2.4 Expected probability distributions for the frequencies of segregating neutral alleles in replicate, randomly mating populations of size N after t generations of divergence (fixed alleles are ignored). The initial allele frequency in the base population is 0.5 on the left and 0.1 on the right. The abscissa is the population allele frequency, whereas the ordinate is proportional to the probability of occurrence of that frequency. Note that the time scale is in units of N generations, where N is the population size, so that t = N generations implies 100 generations for a population of size 100 and 10,000 generations for a population of size 10,000. (From Kimura 1955b.)

</div>

bright red-orange, $ b w^{7 5} b w= $ deep red-brown, and $ b w b w= $ white. (Two separate experiments were performed, one with 107 and the other with 105 populations, but the results are so similar that they have been pooled in the following analysis.)

To evaluate the results in the light of the preceding theory, it is first necessary to demonstrate that the $ b w^{7 5} $ and $ b w $ alleles are indeed neutral with respect to each other. This can be done as follows (Figure 2.5, top). In the absence of selection, the expected frequency of the $ b w^{7 5} $ allele averaged over all populations should equal its initial frequency, 0.50, in all generations. Nevertheless, just as the frequency within any population is expected to deviate from 0.5 because of drift, the mean allele frequency in the total aggregate of populations will also vary slightly because the number of populations is finite. The sampling variance of the overall mean frequency is equal to the sum of the expected within- and among-population allele-frequency variances divided by the number of populations, 212. The latter quantity was already defined in Equation 2.14, whereas the former is the expected binomial sampling variance divided by the sample size (2N), or $ p_{0} ( 1-p_{0} ) [ 1-(1/2 N )]^{t} /(2 N ) $ . Figure 2.5 shows that although the frequency of the $ b w^{7 5} $ allele averaged over all populations increased to

![](page=15,bbox=[357, 143, 778, 522])

<div align="center">

Figure 2.5 Patterns of change in the frequencies of the $ b w^{7 5} $ allele in 212 isolated populations of Drosophila melanogaster, each consisting of eight breeding males and eight females. (Top) The average allele frequency over the entire pool of populations. The dotted and solid lines, respectively, denote upward deviations of two standard errors from the expected value of $ p_{0}=1/2 $ under the assumption of effective population sizes of 16 and 10.2 individuals. (Middle) Mean observed heterozygosity compared to the expectations assuming an effective population size of 10.2. The expected heterozygosity is 0.5 in generations 1 and 2 because the base population (generation 0) consisted entirely of heterozygotes, and with separate sexes, an additional generation is required for the unification of alleles that are identical by descent. (Bottom) Among-line variance of allele frequencies compared with their expectations assuming an effective population size of 10.2. (After Buri 1956.)

</div>

0. 525, it generally remained within two standard errors of the expectation under pure drift. The overall pattern of change in mean allele frequency is therefore compatible with the expectations for a neutral locus subject to random genetic drift.

The dynamics of the among-population divergence (Figure 2.6) are qualitatively very similar to the expected pattern illustrated in the left panel of Figure 2.4 (corresponding to $ p_{0}=0.5 $ ). As the population allele frequencies diverge, the initial bell-shaped distribution does indeed become flatter, eventually acquiring a U-shape as populations that are fixed for the $ bw^{75} $ or bw alleles accumulate. Had the experiment been extended further in time, the distribution would have eventually consisted of only two classes, populations fixed for $ bw^{75} $ and those fixed for bw, with nearly equal frequencies.

![](page=16,bbox=[258, 143, 610, 571])

<div align="center">

Figure 2.6 Distribution of the number of $ b w^{7 5} $ alleles in 212 populations of D. melanogaster each initiated with a frequency of 0.5. Two features are represented in this temporal series: the distribution of frequencies for segregating alleles (1 to 31 copies), the expected form of which is given in Figure 2.4, and the accumulation of fixed alleles (0 or 32 copies). (From Buri 1956).

</div>

Despite the qualitative agreement with theoretical expectations, the rate of divergence illustrated in Figure 2.6 is somewhat greater than that expected for randomly mating populations of 16 individuals. However, this does not necessarily invalidate the theory outlined previously, as it is possible that not all 16 potential parents reproduced each generation, and/or that the distribution of family sizes deviated from randomness. Either condition would cause the populations to behave genetically as though they were smaller than its actual size (Chapter 3). With the massive amount of data in Buri's experiment, it is possible to obtain an empirical estimate of this effective population size in the following way.

Not including fixed classes, there are 31 possible allele frequencies in Buri's populations (1/32 to 31/32), each of which was observed at various times in one or more of the 212 populations. Focusing on any one allele-frequency class, the single-generation sampling variance conditional on the initial allele frequency for this class (p) can then be calculated

![](page=17,bbox=[347, 147, 774, 332])

<div align="center">

Figure 2.7 Observed sampling variances of allele frequencies for situations in which the donor population contained 1 to $ 3 1 \ b w^{7 5} $ genes. The dashed line is the expected pattern, $ p ( 1-p ) / 2 N $ , if the actual populations of 8 males and 8 females were randomly mating with equal chances of contributing offspring. The solid line describes the pattern for an average effective population size of 10.2. (From Buri 1956.)

</div>

from the allele frequencies observed in the subsequent generation, and compared to the expected value of $ p ( 1-p ) /( 2 N ) $ . The 31 points shown in Figure 2.7 provide an empirical description of this function, with an excellent fit being obtained if it is assumed that the average effective population size was $ N\simeq 10.2 $ rather than the idealized 16. In other words, the sampling variance of allele frequencies is in very close accord with that expected for an average ideal population of 10.2 randomly mating individuals. Once this change in scale from N=16 to N=10.2 is taken into account, both the erosion of average heterozygosity within populations and the buildup of among-population variance of allele frequencies are quite consistent with the theory outlined above (Figure 2.5, middle and bottom).

## HIGHER-ORDER ALLELE-FREQUENCY MOMENTS

In the previous sections, we evaluated the expected values of various population features under neutrality. However, as just noted, in applying such expressions to empirical studies, it is important to keep in mind that the random sampling of allele frequencies across generations will cause the realized behavior of any particular population or group of populations to deviate from the expected pattern. Thus, there is a practical need for expressions for the variance of various population parameters that result from genetic sampling. This in turn requires an understanding of the behavior of higher-order allele-frequency moments. For example, although the expected heterozygosity is a function of $ 2 p ( 1-p)=2 ( p-p^{2}), $ as will be shown later, its variance depends on $ p^{3} $ and $ p^{4}. $

For a population obeying the features of the idealized Wright-Fisher model, useful expressions can be obtained by noting that the expected value of an allele-frequency moment in generation $ t+1 $ can be written as a conditional function of the allele frequency $ p_{t} $ in the previous generation. For example, letting $ \delta p $ denote the change in allele frequency in the previous generation resulting from gamete sampling, the behavior of the first moment (the mean) can be written as

$$
E \left[ p _ {t + 1} \mid p _ {t} \right] = E \left[ \left(p _ {t} + \delta p\right) \mid p _ {t} \right]
$$

In the case of neutrality, there are no directional forces, so $ E(\delta p)=0 $ , and the expected

frequency of an allele remains perpetually at its initial value $ ( p_{0} ) $

$$
E \left(p _ {t}\right) = p _ {0}
$$

The second moment is obtained by noting that

$$
E \left[ p _ {t + 1} ^ {2} \mid p _ {t} \right] = E \left[ \left(p _ {t} ^ {2} + 2 p _ {t} \delta p + \delta p ^ {2}\right) \mid p _ {t} \right]
$$

Because $ E(\delta p)=0 $ and $ E(\delta p^{2}|p_{t})=p_{t}(1-p_{t})/(2N) $ under binomial sampling,

$$
E \left[ p _ {t + 1} ^ {2} \mid p _ {t} \right] = E \left(p _ {t} ^ {2} + \frac {p _ {t} - p _ {t} ^ {2}}{2 N}\right)
$$

Letting $ \lambda_{1}=1-(1/2 N) $ , and noting that $ E(p_{t})=p_{0} $ , this expression can be rearranged to give the recursion equation

$$
E \left[ p _ {t + 1} ^ {2} \mid p _ {t} \right] - p _ {0} = \left[ E \left(p _ {t} ^ {2}\right) - p _ {0} \right] \lambda_ {1}
$$

the general solution of which is

$$
E \left(p _ {t} ^ {2}\right) = p _ {0} - \left[ p _ {0} \left(1 - p _ {0}\right) \right] \lambda_ {1} ^ {t}
$$

The general starting expression, which can be extended to all higher-order moments, is

$$
\begin{array}{l} E \left[ p _ {t + 1} ^ {k} \mid p _ {t} \right] = E \left[ \left(p _ {t} + \delta p\right) ^ {k} \mid p _ {t} \right] \\ = \sum_ {i = 0} ^ {k} \binom {k} {i} p _ {t} ^ {i} E \left[ (\delta p) ^ {k - i} \mid p _ {t} \right] \\ \end{array}
$$

where the summation gives the terms in the polynomial expansion. For binomial sampling theory, expressions are available for all expected values of powers of $ \delta p $ (e.g., Johnson et al. 2005), so Equation 2.17 can be solved recursively starting with the lower-order moments.

Using expectations for higher-order $ \delta p^{k} $ terms, expressions for all higher-order moments can be acquired, two of which prove to be particularly useful (Crow and Kimura 1970):

$$
E \left(p _ {t} ^ {3}\right) = p _ {0} - \frac {3}{2} p _ {0} \left(1 - p _ {0}\right) \lambda_ {1} ^ {t} - \frac {1}{2} p _ {0} \left(1 - p _ {0}\right) \left(2 p _ {0} - 1\right) \left(\lambda_ {1} \lambda_ {2}\right) ^ {t}
$$

$$
\begin{array}{l} E \left(p _ {t} ^ {4}\right) = p _ {0} - \frac {1 8 N - 1 1}{1 0 N - 6} p _ {0} \left(1 - p _ {0}\right) \lambda_ {1} ^ {t} - p _ {0} \left(1 - p _ {0}\right) \left(2 p _ {0} - 1\right) \left(\lambda_ {1} \lambda_ {2}\right) ^ {t} \\ + p _ {0} \left(1 - p _ {0}\right) \left(p _ {0} \left(1 - p _ {0}\right) - \frac {2 N - 1}{1 0 - 6}\right) \left(\lambda_ {1} \lambda_ {2} \lambda_ {3}\right) ^ {t} \\ \end{array}
$$

where $ \lambda_{i}=1-(i/2N) $ . Modifications for these expressions for populations with separate sexes and 1:1 sex ratios are given by Lynch and Hill (1986).

![](page=19,bbox=[360, 121, 772, 367])

<div align="center">

Figure 2.8 Mean heterozygosity and its standard deviation (SD) among replicate populations as a function of time (scaled in units of 2N generations). The upper curves assume an initial heterozygosity of $ H_{0}=0. 5 $ and the lower curves of $ H_{0}=0. 2 $ . A diallelic locus is assumed, and new variation generated by mutation is ignored. Experimental error resulting from sampling of a finite number of individuals is ignored as well, i.e., we consider only the variance of true population-level heterozygosities resulting from gamete sampling. The expected heterozygosities (solid lines) are obtained with Equation 2.5, whereas the standard deviations (dotted lines) follow from Equation 2.17.

</div>

Example 2.5. The preceding expressions can be used to derive the evolutionary (or drift) variance of heterozygosity at a locus under the assumption of Hardy-Weinberg equilibrium, provided there are only two alleles segregating at the locus. Letting $ H_{t}=2 p_{t} \left( 1-p_{t} \right) $ denote the heterozygosity at generation t, the expected variance of heterozygosity is

$$
\begin{array}{l} \sigma^ {2} \left(H _ {t}\right) = E \left\{\left[ 2 p _ {t} \left(1 - p _ {t}\right) \right] ^ {2} \right\} - \left\{E \left[ 2 p _ {t} \left(1 - p _ {t}\right) \right] \right\} ^ {2} \\ = E \left(4 p _ {t} ^ {2}\right) - E \left(8 p _ {t} ^ {3}\right) + E \left(4 p _ {t} ^ {4}\right) - \left[ E \left(2 p _ {t} - p _ {t} ^ {2}\right) \right] ^ {2} \\ \end{array}
$$

A solution is obtained by substituting Equations 2.16a-2.16d for the expectations of allelefrequency moments, with further simplification made possible by using the approximations $ \lambda_{1}\simeq e^{-t/2N}, $ $ \lambda_{2}\simeq e^{-2t/2N} $ , and $ \lambda_{3}\simeq e^{-3t/2N} $ , yielding

$$
\sigma^ {2} \left(H _ {t}\right) \simeq H _ {0} \left[ \frac {2}{5} e ^ {- t / 2 N} + \left(H _ {0} - \frac {2}{5}\right) e ^ {- 3 t / N} - H _ {0} e ^ {- t / N} \right]
$$

This quantity can be viewed as either the variance in heterozygosity that develops at a particular neutral locus among replicate populations starting from the same initial allele frequencies or as the variance in heterozygosity among a pool of loci within the same population with identical initial allele frequencies. As with the expected heterozygosity, the temporal dynamics of the evolutionary variance of heterozygosity scale inversely with the size of the population. Moreover, the variation in heterozygosity resulting from genetic drift can be quite high, with the standard deviation always exceeding the expected heterozygosity once t > 2N generations (Figure 2.8). With more than two alleles per locus, the preceding expressions would need to be modified to account for the negative drift sampling covariance between different alleles at the locus.

## LINKAGE DISEQUILIBRIUM

In the study of multilocus traits, we are naturally interested in combinations of alleles among loci. If the alleles at two loci are independently distributed, the expected frequency of each gamete type can be predicted from the products of the allele frequencies at the two loci. For example, with two alternative alleles (A and a) at one locus having frequencies p and 1-p, and those (B and b) at another locus having frequencies q and 1-q, the expected frequencies of gametic types AB, Ab, aB, and ab are pq, p(1-q), (1-p)q, and (1-p)(1-q), respectively, under the assumption of independence. A natural measure of the deviation of the frequency of a gametic type from such expectations is the coefficient of linkage disequilibrium

$$
D _ {\mathrm {A B}} = p _ {A B} - p q
$$

where $ p_{AB} $ denotes the observed frequency of the $ AB $ th gamete.

Here a word on notation is in order. Throughout, we will use italicized letters to designate alleles associated with a particular locus, which will in turn be denoted with an uppercase nonitalicized letter. Thus, Equation 2.18 defines the linkage disequilibrium at loci A and B, using alleles A and B to define the deviation from random expectations.

This definition of $ D_{\mathrm{A B}} $ has the useful feature of being equivalent to the covariance of the distribution of alleles A and B in the same gametes. To see this, let the random variable x take on a value of one when the allele at the first locus is A and zero otherwise, and likewise let y equal one when the allele at the second locus is B and zero otherwise. Then, $ E(xy)=p_{AB}\cdot1 $ $ E(x)=\operatorname{freq}(A)\cdot1=p $ , and $ E(y)=\operatorname{freq}(B)\cdot1=q $ , giving the covariance between allele presence at the two loci as $ E(xy)-E(x)E(y)=p_{AB}-pq. $

In the absence of selection, there will be no tendency for the alleles at different loci to be associated positively versus negatively. However, forces such as migration or nonrandom mating may cause some such correlations. Letting $ D_{0} $ denote an initial level of disequilibrium, c denote the frequency of recombination between loci, and $ \lambda_{1}=1-(1/2N) $ , the expected disequilibrium (under random mating) resulting from the joint forces of recombination and gametic sampling is

$$
\begin{array}{l} E \left(D _ {t}\right) = \left[ (1 - c) \lambda_ {1} \right] ^ {t} D _ {0} \\ \simeq D _ {0} e ^ {- (2 N c + 1) t / (2 N)} \\ \end{array}
$$

(Hill and Robertson 1966), showing that disequilibrium declines toward zero in the absence of any replenishing forces.

In contrast, the variance of D can be quite substantial even when its expected value is zero. The problem can be evaluated by use of the following set of recursion equations for fourth-order moments of allele frequencies,

$$
\begin{array}{l} \left( \begin{array}{c} E [ p (1 - p) q (1 - q) ] \\ E [ D (1 - 2 p) (1 - 2 q) ] \\ E \left(D ^ {2}\right) \end{array} \right) _ {t + 1} = \lambda_ {1} \cdot \left( \begin{array}{c c c} \lambda_ {1} & \lambda_ {1} (1 - c) / (2 N) & 2 (1 - c) ^ {2} / (4 N ^ {2}) \\ 0 & \lambda_ {2} ^ {2} (1 - c) & 4 \lambda_ {2} (1 - c) ^ {2} / (2 N) \\ 1 / (2 N) & \lambda_ {1} (1 - c) / (2 N) & [ \lambda_ {2} ^ {2} + (1 / 4 N ^ {2}) ] (1 - c) ^ {2} \end{array} \right). \\ \left( \begin{array}{c} E [ p (1 - p) q (1 - q) ] \\ E [ D (1 - 2 p) (1 - 2 q) ] \\ E \left(D ^ {2}\right) \end{array} \right) _ {t} \tag {2.20} \\ \end{array}
$$

where, as previously, $ \lambda_{i}=1-[i / (2N)] $ (Hill and Robertson 1968). The evolutionary variance of D associated with drift among replicated populations or among loci starting from the same allele frequencies is

$$
\sigma^ {2} (D) = E \left(D ^ {2}\right) - E ^ {2} (D)
$$

If $ D_{0}=0 $ , then $ E(D_{t})=0 $ , and $ \sigma^{2}(D_{t})=E(D_{t}^{2}) $ . Ohta and Kimura (1969a; their Equations 20-25) obtained a closed-form solution to this expression.

Hill and Robertson (1968) introduced a standardized measure of linkage disequilibrium, often referred to as the squared within-gamete correlation of allele frequencies at two loci

$$
r ^ {2} = \frac {D ^ {2}}{p (1 - p) q (1 - q)}
$$

This is a natural definition in the sense of a correlation coefficient being generally defined as the ratio of a covariance (in this case, D) and the square root of the product of the variances (in this case, p[1-p] and q[1-q] for the allelic variances at each locus). There are, however, conceptual limitations to this measure, as it can only achieve a maximum value of 1.0 if the heterozygosities at both loci are equal. To make matters worse, in many applications of Equation 2.22, investigators have computed the ratio of average values of the numerator and denominator for large numbers of pairs of loci, which is not equivalent to the squared gametic correlation averaged over pairs of loci. This difference in definition can lead to up to 100-fold differences between estimated values of $ r^{2} $ and the true correlation if allele frequencies are extreme, as is often the case with neutral alleles (Song and Song 2007).

Example 2.6. One common setting generating linkage disequilibrium involves a new allele arising as a single copy on a particular background. Let A denote the derived allele and assume it arose on a B background at a second locus. Initially, all copies of A are associated with B (there are no Ab gametes). Because the sum of the AB and aB gamete frequencies is just the frequency q of B, the resulting $ 2 \times2 $ gametic contingency table is

$$
\begin{array}{c c c c} & A & a \\ B & p & q - p \\ b & 0 & 1 - q \end{array}
$$

and the resulting initial values for D and $ r^{2} $ become

$$
D _ {\mathrm {A B}} = p _ {A B} p _ {a b} - p _ {a B} p _ {A b} = p (1 - q) - 0 \cdot (q - p) = p (1 - q)
$$

$$
r ^ {2} = \frac {D ^ {2}}{p (1 - p) q (1 - q)} = \frac {[ p (1 - q) ] ^ {2}}{p (1 - p) q (1 - q)} = \frac {p (1 - q)}{(1 - p) q}
$$

For this example, $ r^{2}=1 $ only when $ p=q $ (Sved 1971), or when there are no aB gametes (A and B always co-occur), in which case the $ 2\times 2 $ gamete contingency table becomes

$$
\begin{array}{c c c c c c c c c} & A & a \\ B & p & 0 & , & \text {o r e q u i v a l e n t l y} & A & a \\ b & 0 & 1 - p & & & B & q & 0 \\ & & & & & b & 0 & 1 - q \end{array}
$$

For a newly arising mutation, $ p=1 / (2 N) $ , so initially $ D_{\mathrm{AB}}=(1-q) / (2 N) $ and $ r^{2}\simeq(1-q) / (2 N q). $

## MUTATION-DRIFT EQUILIBRIUM

In the preceding pages, we were largely concerned with the dynamics of gene-frequency change owing to the effects of random genetic drift alone. Under this model, finite population size eventually results in the complete loss of genetic variation (and covariation) within populations, at which point all loci are fixed for ancestral alleles with probabilities equal to their initial frequencies. In reality, however, mutation will always introduce variation at a low rate, which not only offsets some of the loss resulting from drift, but also ensures that neutral loci will continue to diverge among isolated populations. If the time scale of the

problem under consideration is short (t $ \ll2N $ ) and the initial level of within-population variation is high (relative to the mutational rate of production of new heterozygosity per generation), the contribution from mutation will be negligible, and the preceding expressions will be quite adequate. However, for longer-term evolutionary issues, such as the maintenance of variation in natural populations and interspecific divergence, mutation cannot be ignored.

The incorporation of mutation into a neutral model of evolution is relatively straightforward. For example, suppose there are k possible alleles at a locus, each with a mutation rate u per generation (the k-exchangeable alleles model). The dynamics of heterozygosity can then be obtained by recalling from above that the expected frequency of heterozygotes in generation t+1 in the absence of mutation is $ [ 1- ( 1 / 2 N ) ] H_{t}=\lambda_{1} H_{t} $ , whereas the expected frequency of homozygotes is $ 1-\lambda_{1} H_{t} $ . Following mutation, the heterozygous state will be retained if: (1) neither allele mutated, the probability of which is $ (1-2 u) $ , ignoring the very small probability of double mutations to the same state; or (2) one of the alleles mutated to a different state than the other, the probability of which is $ [ 2 u ( k-2 ) / ( k-1 ) ] $ assuming that all allelic types are equally mutationally exchangeable. On the other hand, homozygotes will be mutationally converted to heterozygotes at a rate of 2u. Thus, the expected dynamics of heterozygosity can be expressed as

$$
H _ {t + 1} = H _ {t} \lambda_ {1} \left((1 - 2 u) + \frac {2 u (k - 2)}{k - 1}\right) + 2 u \left(1 - \lambda_ {1} H _ {t}\right)
$$

Setting $ H_{t+1}=H_{t} $ the expected value of heterozygosity under drift-mutation balance is found to be

$$
E (H) = \frac {\theta}{1 + \left[ \theta k / (k - 1) \right]}
$$

where $ \theta=4 N u $ , a result first given by Kimura (1968a). Note that $ \theta $ has the pleasing interpretation of being the ratio of the rates of mutational production of heterozygotes from homozygotes (2u) and the rate of loss of heterozygosity by drift $ (1/2 N) $ . If a large number of alternative alleles $ (k\gg1) $ is assumed, as is reasonable when the unit of analysis is an entire gene, Equation 2.24a reduces to

$$
E (H) \simeq \frac {\theta}{1 + \theta}
$$

which is equivalent to the infinite-alleles model of Kimura and Crow (1964). On the other hand, if the unit of analysis is a nucleotide site, then k=4, and

$$
E (H) = \frac {\theta}{1 + (4 / 3) \theta}
$$

where u is now the mutation rate per nucleotide site. Equation 2.24a needs to be modified if alleles mutate at different rates or are not equally mutationally accessible (Kimura 1983; Nei and Kumar 2000), but provided 2Nu $ \ll1 $ , as seems to be generally the case (Chapter 4), then $ E[H]\simeq \theta $ regardless of the model assumed. As $ 2Nu\rightarrow\infty $ , the infinite-alleles model implies $ E(H)\rightarrow1.0 $ , whereas the k=4 model implies $ E(H)\rightarrow0.75 $ . The latter result is a simple consequence of four segregating alleles with equal frequencies (0.25) when the power of drift is overwhelmed by mutation. A number of other mutational models are possible, and a very general treatment is given by Cockerham (1984c), who also considered the transient approach to equilibrium.

As these drift-mutation models play a central role in the neutral theory of molecular evolution (Kimura 1983), substantial attention has been given to additional details that are obscured by the summary statistic of average heterozygosity. For example, $ \theta $ is the expected average heterozygosity over a large number of loci; this is not likely to be exactly realized at any particular site. Because of the stochastic nature of both mutation and drift, the allele

frequencies at any neutral locus are expected to wander stochastically over time, with some loci being transiently fixed for one particular allele, and others being distributed over the remaining spectrum of allele frequencies. Kimura (1968a) obtained an expression analogous to Equation 2.8 for the complete probability distribution of the frequency of an allele under the symmetric mutation model described above, starting from an arbitrary allele frequency. Although this expression is quite complicated, a highly useful result is that regardless of the starting point, a steady-state distribution of allele frequencies p is eventually attained

$$
\phi (p) = \frac {\Gamma (\theta + \beta)}{\Gamma (\theta) \Gamma (\beta)} (1 - p) ^ {\theta - 1} p ^ {\beta - 1}
$$

where $ \theta=4 N u, \beta=4 N u / (k-1), $ with

$$
\Gamma (\alpha) = \int_ {0} ^ {\infty} x ^ {\alpha - 1} e ^ {- x} d x
$$

being the gamma function (Appendix 2). Equation 2.25a may be viewed as either the expected distribution of allele frequencies over all neutral loci within a single population in mutation-drift equilibrium or as the distribution of allele frequencies at a particular locus among replicate populations (or species) with identical N and u. Nei and Li (1976) presented the theory necessary for predicting the approach to the equilibrium state.

The expected value of any function of population allele frequencies (e.g., homozygosity) can be obtained by simply integrating the function over the density distribution $ \phi(p). $ It is useful that Equation 2.25a defines a beta distribution (Appendix 2), as many of its properties are already well known. For example, the mean of the distribution, which is the expected allele frequency, is

$$
E (p) = \frac {\beta}{\theta + \beta} = \frac {1}{k}
$$

and the allele-frequency variance among replicates is

$$
\sigma^ {2} (p) = \frac {\theta \beta}{(\theta + \beta) ^ {2} (\theta + \beta + 1)} = \frac {k - 1}{k ^ {2} [ 2 N u k (k - 1) + 1 ]}
$$

Expressions for the variance of heterozygosity for a population en route to equilibrium were derived by Li and Nei (1975) and Lessard (1981), and at equilibrium

$$
\sigma^ {2} (H) = \frac {2 \theta [ 1 + (\theta / \ell) ]}{[ 1 + \theta + (\theta / \ell) ] ^ {2} [ 2 + \theta + (\theta / \ell) ] [ 3 + \theta + (\theta / \ell) ]}
$$

where $ \ell=k-1 $ (Stewart 1976). Note that as $ k\to\infty $ (the infinite-alleles model),

$$
\sigma^ {2} (H) = \frac {2 \theta}{(1 + \theta) ^ {2} (2 + \theta) (3 + \theta)}
$$

which reduces to about $ \theta/3 $ for $ \theta\ll1. $

Although the preceding results lead to predicted equilibrium allele frequencies, heterozygosities, etc., when viewed in isolation, such results obscure the long-term dynamics of neutral mutations. Given a population of size N, on average 2Nu new mutations arise per nucleotide site per generation, each with initial frequency 1/(2N). As noted earlier, the probability of fixation of a neutral allele is simply equal to its initial frequency, so that in the long run, at a neutral site, there is an average turnover rate of $ 2 N u \cdot1 /(2 N)=u $ mutations per generation. This simple but powerful result tells us that the long-term rate of nucleotide substitution at a neutral site is equal to the mutation rate, regardless of the size of the population, a hallmark of the neutral theory of molecular evolution (Kimura 1983). This long-term flux occurs in the face of the maintenance of quasi-steady-state within-population

heterozygosity, which arises as a consequence of the per-generation balance between the loss of variation by fixation and replenishment by recurrent mutation.

Finally, Ohta and Kimura (1971) and Hill (1975) obtained expressions for the expected values of the two-locus moments described in Equation 2.20, under the infinite-alleles model at stochastic drift-mutation equilibrium. Letting $ \rho=4 N c $ and $ \theta=4 N u $ , where c is the recombination rate between sites, and u is the mutation rate per site, Hill's expressions reduce to

$$
\begin{array}{l} E [ p (1 - p) q (1 - q) ] = M \left(2 2 + 1 3 \rho + 3 2 \theta + \rho^ {2} + 6 \rho \theta + 8 \theta^ {2}\right) \\ E [ D (1 - 2 p) (1 - 2 q) ] = 8 M \\ E \left[ D ^ {2} \right] = M \left(1 0 + \rho + 4 \theta\right) \\ \end{array}
$$

where

$$
M = \theta^ {2} / [ (\theta + 1) \left(1 8 + 1 3 \rho + 5 4 \theta^ {2} + \rho^ {2} + 1 9 \rho \theta + 4 0 \theta^ {2} + 6 \rho \theta^ {2} + 8 \theta\right) ],
$$

and the standardized linkage disequilibrium is given by

$$
E \left(r ^ {2}\right) = \frac {1 0 + \rho + 4 \theta}{2 2 + 1 3 \rho + 3 2 \theta + \rho^ {2} + 6 \rho \theta + 8 \theta^ {2}}
$$

As will be seen in Chapter 4, for individual nucleotide sites $ \theta $ is generally substantially smaller than one, whereas for sites separated by hundreds of base pairs or more, $ \rho $ is generally greater than one. Under such conditions,

$$
E \left(r ^ {2}\right) \simeq \frac {1 0 + \rho}{2 2 + 1 3 \rho + \rho^ {2}}
$$

which asymptotically approaches $ 1 / \rho $ for large $ \rho $ . Additional theoretical points of interest were developed in Strobeck and Morgan (1978) and Golding and Strobeck (1980). A more daunting problem is obtaining expressions for the evolutionary variances of these statistics. As the components in Equation 2.28a already involve fourth-order moments of allele frequencies within and between loci, their variances are functions of moments up to the eighth order. Hill and Weir (1988) tackled this problem.

Example 2.7. A widely cited expression for $ E(r^{2}) $ originates with Sved (1971; Feldman and Sved 1973), which we will refer to as

$$
E \left(r _ {\mathrm {I B D}} ^ {2}\right) = \frac {1}{1 + 4 N c} = \frac {1}{1 + \rho}
$$

Note that this expression is quite different from Equation 2.29a (as no terms for mutation appear), and also different from the approximation given by Equation 2.29b. To understand this discrepancy, it is useful to reflect on Sved's simple derivation, which focuses on a different measure of correlation than that outlined earlier. Conditional on two random gametes being identical by descent (IBD) from common ancestry at locus A, Sved wished to know the probability $ Q_{\mathrm{A B}} $ that the alleles at locus B on both gametes are also IBD owing to the absence of recombination between the sites during the entire two pathways back to the common ancestor. With this definition in hand, Sved showed that $ Q_{\mathrm{A B}}=r_{\mathrm{I B D}}^{2}. $

Let $ Q_{t} $ denote the value of joint IBD in generation $ t $ , and consider how this relates to $ Q_{t-1} $ one generation in the past. For a population with size $ N $ , at any particular site a random pair of gametes will be direct copies of a gamete in the preceding generation with probability $ 1 / (2N) $ , and IBD will exist at both sites provided no recombination has occurred between them, the probability of which is $ (1-c)^{2} $ , where c refers to the recombination rate. Alternatively, the two

sampled gametes will be drawn from different gametes leading to the preceding generation, the probability of which is $ 1-1 / (2 N) $ . In the latter case, joint IBD will still exist if it happened to have been present for the two chromosomal segments in the preceding generation with no recombination again occurring in either. Summing up, the recursion equation for joint IBD is

$$
Q _ {t} = \frac {1}{2 N} (1 - c) ^ {2} + \left(1 - \frac {1}{2 N}\right) (1 - c) ^ {2} Q _ {t - 1}
$$

Setting $ Q_{t}=Q_{t-1} $ gives the equilibrium solution as

$$
\widetilde {Q} = \frac {1 / (2 N)}{1 - [ 1 - 1 / (2 N) ] (1 - c) ^ {2}} \simeq \frac {1}{1 + 4 N c}
$$

Although this is an equilibrium solution like Equations 2.29a and 2.29b, Sved's Q is not equivalent to the measure $ r^{2} $ in these previous formulae, which are concerned with the longterm average disequilibrium associated with identity in state (IIS). Whereas IIS is a directly observable quantity, IBD is not, and hence there are interpretative problems when applying Sved's expression to empirical data. This is because parallel mutation can cause IIS for alleles that are not IBD, and secondary mutations can eliminate IIS for pairs of alleles that are otherwise IBD. Thus, although Sved's expression is widely used, apparently because of its simplicity, Equations 2.29a and 2.29b appear to be more appropriate for practical applications to observed molecular variation.

## THE DETAILED STRUCTURE OF NEUTRAL VARIATION

Although heterozygosity provides a robust measure of genetic variation, as a summary statistic it obscures the details of the underlying structure of this variation, e.g., the number of alleles and their frequencies. Fortunately, at mutation-drift equilibrium, most of these features are just relatively simple functions of $ \theta $ (Ewens 2004). There are, however, two alternative ways of thinking about molecular variation, each appropriate in a different context, and care must be taken in the interpretation of the mutation rate in each model. In one case, the infinite-alleles (or infinitely many alleles) model, the unit of observation is the locus (a stretch of DNA), whereas in the infinite-sites (or infinitely many sites) model, it is the nucleotide site. Results developed here are extensively used in Chapters 8 and 9 in methods for detecting departures from the equilibrium neutral model.

## The Infinite-alleles Model and the Associated Allele-frequency Spectrum

The infinite-alleles model (briefly introduced earlier) was developed prior to the DNA-sequencing era, but was motivated by emerging knowledge on the structure of DNA sequences. In today's world, different alleles under this model are typically viewed as different sequences (haplotypes) over a region of L nucleotide sites, and the general assumption is that L is large enough that each mutation generates a new haplotype (not preexisting in the population), but small enough that recombination can be ignored (so that mutation is the sole generator of novel sequences). Considering the five short sequences in Figure 2.9, under the infinite-alleles framework, there are three different alleles, although there are only two segregating sites. With allele frequencies 0.4 (AAGACC), 0.4 (AAGGCC), and 0.2 (AAGGCA), the allelic heterozygosity of the sample is 0.64. This is, of course, a rather crude perspective, as it ignores the ways in which alleles differ from each other (in this example, two pairs of alleles differ at a single site, whereas one pair differs at two sites).

## A A G $ \underline{\mathbf{A}} $ C C

A A G G C C

A A G $ \underline{\mathbf{A}} $ C C

A A G G C C

A A G G C $ \underline{\mathbf{A}} $

<div align="center">

Figure 2.9 An example of the difference between the infinite-alleles and infinite-sites models. Five sequences (horizontal rows) scored at six nucleotide sites (vertical columns) are sampled from a population. Three of these five sequences are different and are scored as three alleles (or haplotypes) under an infinite-alleles framework (from top to bottom, sequences 1 and 3; 2 and 4; and 5). Conversely, only two of the six sites are segregating (from left to right, columns 4 and 6), giving two polymorphic sites under an infinite-sites framework.

</div>

A key parameter for the infinite-alleles model is the per-locus population mutation rate, $ \theta_{L}=4 N u L $ , which we distinguish from the more commonly used per-site measure, $ \theta=4 N u $ , where u is the mutation rate per site. As noted previously, under neutrality, provided that the population has been at constant size long enough to be in mutation-drift equilibrium, the expected heterozygosity is given by Equation 2.24b, with $ E(H)\approx\theta_{L} $ for $ \theta_{L}\ll1 $ . If the expected heterozygosity is small, a sample will often be monomorphic, consisting of only a single allele, or dimorphic, consisting of just two alleles. However, at higher levels of heterozygosity, multiple alleles can be expected, and a natural measure of variation is the number of different alleles in a sample. Insight into this quantity under drift-mutation equilibrium is given the probability of having k different alleles in a sample of n genes, which is

$$
\Pr (k \mid \theta_ {L}, n) = \frac {S _ {n} ^ {k} \theta_ {L} ^ {k}}{S _ {n} \left(\theta_ {L}\right)}
$$

$$
S _ {n} \left(\theta_ {L}\right) = \theta_ {L} \left(\theta_ {L} + 1\right) \left(\theta_ {L} + 2\right) \dots \left(\theta_ {L} + n - 1\right)
$$

where

and $ S_{n}^{k} $ is the coefficient on the $ \theta_{L}^{k} $ term obtained by expanding the polynomial in Equation 2.30b (Ewens 1972). This formula opened up the field of formal statistical tests for whether a pattern of allelic variation is consistent with the equilibrium neutral model. For example, using Equation 2.30a, one can ask if an observed estimate of $ \theta_{L} $ (obtained in this case as the allelic heterozygosity) is consistent with the observed number k of different alleles (Chapter 9).

Several useful results follow from Equation 2.30a. First, the probability of a monomorphic sample is

$$
\Pr (k = 1) = \frac {(n - 1) !}{(\theta_ {L} + 1) (\theta_ {L} + 2) \cdots (\theta_ {L} + n - 1)}
$$

Second, a bit of algebra gives the mean and variance for the number of alleles in a sample as

$$
E (k) = 1 + \theta_ {L} \cdot \sum_ {j = 2} ^ {n} \frac {1}{\theta_ {L} + j - 1}, \quad \sigma^ {2} (k) = \theta_ {L} \cdot \sum_ {j = 1} ^ {n - 1} \frac {j}{\left(\theta_ {L} + j\right) ^ {2}}
$$

An even more complete description of the segregating allelic variation is given by the

allele-frequency spectrum, which describes the joint probability distribution of the number of alleles in the sample and their frequencies. Given that the numbering of alleles is arbitrary, the convention is to consider the vector $ ( n_{1},\cdots,n_{n} ) $ , where $ n_{i} $ denotes the number of alleles that have exactly i copies in the sample. If the sample is monomorphic, then $ n_{n}=1 $ , whereas if all n alleles are unique (singletons), $ n_{1}=n $ . For the example data set in Figure 2.7, one allele appears as a singleton, whereas the other two alleles both appear as two copies, giving $ n_{1}=1,n_{2}=2 $ , and $ n_{3},n_{4},n_{5}=0 $ . The constraint on the $ n_{i} $ is that

$$
\sum_ {i = 1} ^ {n} i \cdot n _ {i} = n
$$

A very powerful result, due to Ewens (1972) and Karlin and McGregor (1972), is that the joint probability distribution of $ n_{1},\dots,n_{n} $ and k is given by the Ewens sampling formula (Ewens 1972)

$$
\Pr \left(n _ {1}, n _ {2}, \dots , n _ {n}, k \mid n\right) = \frac {n ! \theta_ {L} ^ {k}}{S _ {n} \left(\theta_ {L}\right) \left(1 ^ {n _ {1}} 2 ^ {n _ {2}} \dots n ^ {n _ {n}}\right) n _ {1} ! n _ {2} ! \dots n _ {n} !}
$$

Only nonzero values of $ n_{i} $ are included. The probability that the sample is monomorphic, Equation 2.31a, directly follows by setting $ k=1,n_{1}=n $ . Equations 2.30a and 2.33a show that the conditional distribution of $ n_{1},\cdots,n_{n} $ given k is

$$
\Pr \left(n _ {1}, n _ {2}, \dots , n _ {n} \mid n, k\right) = \frac {n !}{S _ {n} ^ {k} \left(1 ^ {n _ {1}} 2 ^ {n _ {2}} \dots n ^ {n _ {n}}\right) n _ {1} ! n _ {2} ! \dots n _ {n} !}
$$

Note that the righthand side in Equation 2.33a is independent of $ \theta_{L} $ . This property arises because k is a sufficient statistic for $ \theta_{L} $ under the equilibrium neutral model, so that conditioning on k removes any dependence on $ \theta_{L} $ . It is this independence that forms the basis of the Ewens-Watterson test of neutrality considered in Chapter 9.

## The Infinite-Sites Model and the Associated Site-frequency Spectrum

An alternate framework for summarizing molecular variation is embodied in the infinite sites model, which treats a region as a series of L sites. Each new mutation is again viewed as unique, but now occurring at a novel (not currently segregating) site, and as with the infinite alleles model, recombination within the region is assumed to be insignificant. Because this model allows only a single mutation per site, a particular variant at a polymorphic site is either ancestral (original) or derived (mutated), and each segregating site is treated as biallelic. With sequence data from one or more outgroups, one can often polarize the nucleotides at any particular site, determining which is derived by assuming the outgroup harbors the ancestral state. In the absence of such information, the minor-allele frequency, the frequency of the rarest nucleotide, is reported for each site. In the following expressions, we will make use of both measures of the population mutation rate noted above, with $ \theta_{L}=4 N u L=\theta L. $

The infinite-sites model offers a much richer set of information than can be achieved with the infinite-alleles model. One measure is the number of segregating sites S, i.e., the number of polymorphic sites in a sample (the loose analog to number of alleles). A second is the nucleotide diversity $ \pi $ , the average per-site heterozygosity within the region of interest. Finally, one can consider the site-frequency spectrum, the counterpart of the allele-frequency spectrum. In this case, instead of counting the number of times each allele appears in the sample, one considers the number of sites $ s_{j} $ in the sample with j copies of a nucleotide. The unfolded frequency spectrum refers to polarized nucleotides, with $ s_{j} $ being the number of sites with $ j \leq n $ copies of the derived nucleotide. For a folded frequency spectrum, $ s_{j} $ is the number of sites with j copies of the minor nucleotide, with $ j \leq n / 2. $

For the example data set in Figure 2.9, four of the six sites are monomorphic, whereas site 4 has 3 Gs and 2 As, and site 6 has 4 Cs and an A. For a folded frequency spectrum, this

gives four sites in class 0, one site in class 1, and one site in class 2 (i.e., $ s_{0}=4, s_{1}=1, s_{2}=1 $ ). If the nucleotides were polarized, so that (for example) the ancestral states at the six sites were (respectively) A-A-G-G-G-A, the unfolded frequency spectrum would be three in class 0 (sites 1, 2, 3), one in class 2 (site 4), one in class 4 (site 6), and one in class 5 (site 5) (i.e., $ s_{0}=3, s_{2}=1, s_{4}=1, s_{5}=1 $ ). Many of the analyses using site-frequency spectrum data condition on only sites that are polymorphic in the sample.

For a very long region ( $ L\gg1 $ ) (again assuming neutrality, and mutation-drift equilibrium), the fraction of sites in the entire population that have a derived nucleotide at frequency x (for $ 0<x<1 $ ) is given by the (unfolded) Watterson (1975) distribution,

$$
\phi (x) = \frac {\theta}{x} \quad \mathrm {f o r} \quad \frac {1}{2 N} \leq x \leq 1 - \frac {1}{2 N}
$$

This tells us that under the neutral model most sites are expected to have a low frequency of derived nucleotides in the population. Reconfiguring Equation 2.34a for unpolarized alleles, so that 0 < x $ \leq $ 0.5 where x is the minor-allele frequency, gives the folded Watterson distribution,

$$
\phi (x) = \frac {\theta}{x} + \frac {\theta}{1 - x} = \frac {\theta}{x (1 - x)} \quad \mathrm {f o r} \quad \frac {1}{2 N} \leq x \leq 1 / 2
$$

The folded and unfolded frequency spectra are very similar over the range where both are defined (0 < x $ \leq $ 0.5), as high-frequency derived nucleotides are rare under the equilibrium neutral model, due to the fact that most new mutations are lost by drift.

The site-frequency spectrum for a sample is not the same as that for the entire population, but it follows from the Watterson distribution. In the case of an unfolded frequency spectrum, for a sample of size n, the number $ s_{i} $ of the L total sites with i derived nucleotides has the expected value

$$
E \left(s _ {i}\right) = \frac {\theta_ {L}}{i}, \quad \mathrm {f o r} \quad 1 \leq i \leq n - 1
$$

(Fu 1995; Ewens 2004). Because $ \theta_{L}=i E(s_{i}) $ Equation 2.35a motivates several infinite site estimators of $ \theta $ developed in Chapters 4 and 9. By using different regions of the site-frequency spectrum (i.e., different ranges for i) to estimate $ \theta $ various assumptions of the standard neutral model (e.g., constant population size, and absence of selection) can be tested (Chapter 9). Similarly, for a folded frequency spectrum, where $ s_{i} $ now denotes the number of sites with minor-nucleotide frequency $ i/n $

$$
E \left(s _ {i}\right) = \frac {\theta_ {L}}{i} + \frac {\theta_ {L}}{n - i} = \frac {\theta_ {L} n}{i (n - i)}, \quad \mathrm {f o r} \quad 1 \leq i \leq [ n / 2 ]
$$

where $ [n / 2] $ denotes the largest integer $ \leq n / 2. $

Although the expectations given by Equations 2.35a and 2.35b can be used for method of-moments estimators of $ \theta $ , likelihood estimators (LW Appendix 4) require the full distribution within a sample, not just the expected value. The probability of seeing exactly k derived nucleotides at a site with allele-frequency x follows from the binomial,

$$
\Pr (k \mid x, n) = \binom {n} {k} x ^ {k} (1 - x) ^ {n - k}
$$

In addition, the probability that a sample is polymorphic at a site with allele-frequency x is just one minus the probability of a sample monomorphic for either the derived $ ( x^{n} ) $ or the ancestral $ ( 1-x )^{n} $ nucleotide,

$$
\Pr (1 \leq k \leq n - 1) = 1 - x ^ {n} - (1 - x) ^ {n}
$$

The probability of seeing k derived nucleotides at a random site in a sample is the average of Equation 2.36a over the possible x values,

$$
\Pr (k \mid n) = \binom {n} {k} \int_ {1 / (2 N)} ^ {1 - 1 / (2 N)} x ^ {k} (1 - x) ^ {n - k} \phi (x) d x
$$

where $ \phi(x) $ is defined by Equation 2.34a. This formula, which forms the null model for several of the likelihood-based tests for a selective sweep (Chapters 8 and 9), is the infinite-sites analog to Ewens' sampling formula for the infinite-alleles model (both of which are functions of n and $ \theta $ ). Ewens' formula (Equation 2.30a) gives the probability that k alleles are seen in a sample of size n, whereas Equation 2.36c gives the probability that a randomly-chosen site is segregating k copies of a derived nucleotide. The latter formula also defines the probability of k copies of a minor nucleotide under the folded spectrum if Equation 2.34b is used for $ \phi(x). $

## THE GENEALOGICAL STRUCTURE OF A POPULATION

The preceding analyses showed that a number of summary statistics, such as average levels of heterozygosity and linkage disequilibrium, are defined by the processes of drift, mutation, and recombination in predictable ways, at least for neutral sites. Provided we retain our focus on neutral regions of the genome, it is possible to go quite a bit further, even to the extent of predicting the expected genealogical relationships among different sequences sampled within populations. The basic theory, first laid out by Kingman (1982a 1982b) and now called coalescent theory, provides an elegant and powerful approach for solving problems in population genetics and molecular evolution. Kingman (2000) reviewed the historical origins of this approach, and detailed overviews can be found in Hudson (1990), Donnelly and Tavaré (1995), Fu and Li (1999), Nordborg (2001), Stephens (2001), Rosenberg and Nordborg (2002), Hein et al. (2005), and Wakeley (2006).

Because all of the genes within a population are direct products of past gametic sampling, they are all ultimately related in a genealogical sense. Thus, if one were to sample two alleles in a current population and then follow them back in time, both copies would eventually be traced to a single copy in an ancestral individual, at which point the two alleles are said to have coalesced. A key principle is that the form of the expected gene genealogy for neutral genes, in particular the expected coalescence time, is completely independent of the mutational process.

Consider a random sample of n alleles drawn from a current population, assumed to obey all the properties of the idealized Wright-Fisher model, and with no recombination within alleles. Focusing initially on just two of the sampled alleles, we first evaluate the probability that both members of the pair are direct copies of a single allele in the preceding generation. Assuming that each individual produces a large number of gametes, because there are 2N gene copies in the population in each generation, this probability is simply $ 1 / (2 N) $ ,whereas $ \lambda_{1}=1-(1/2 N) $ is the probability that coalescence occurred at some earlier generation. Conditional on coalescence not having occurred in generation one, the probability of coalescence one further generation in the past is again equal to $ 1 / (2 N) $ ,yielding $ \lambda_{1}(1/2 N) $ as the unconditional probability of coalescence two generations back. This simple rule can be generalized to give the probability of coalescence exactly t generations in the past,

$$
P _ {c} (t) = \lambda_ {1} ^ {t - 1} (1 / 2 N)
$$

which defines a geometric distribution, with the sum of $ P_{c}(t) $ over the interval $ t=1 $ to $ \infty $ being equal to one. One simple related point is that the probability that the most recent common ancestor (MRCA) between two sampled alleles occurred within the last $ t $ generations is $ 1-\lambda_{1}^{t}\simeq 1-e^{-t/2N} $ , namely one minus the probability of no common ancestor over the first $ t $ generations into the past.

The mean coalescence time for two randomly sampled genes is simply

$$
\bar {t} _ {c} (2) = \sum_ {t = 1} ^ {\infty} t \cdot P _ {c} (t) = 2 N
$$

Thus, the expected number of generations required for any two random alleles to trace back

![](page=30,bbox=[221, 140, 643, 303])

<div align="center">

Figure 2.10 Expected coalescence times, $ \bar{t}_{n} $ for a sample of n=5 neutral genes taken from an idealized Wright-Fisher population of size N. The number of gene pairs in each consecutive step of the coalescent process is denoted by $ p_{n} $ , and the expected times to coalescence at each step are equal to $ 2 N / p_{n} $ generations. The particular lineages that join during each step are arbitrary. Note that over half of the coalescent time for the total lineage of five samples involves the coalescent event between the final two branches.

</div>

to an ancestral copy is simply equal to twice the population size (more precisely, twice the effective population size, as will be defined in Chapter 3).

The logic used to derive this result is easily extended to the entire sample of n gene copies. There are $ p_{n}=n(n-1)/2 $ possible pairs of n copies, each of which will or will not coalesce in the preceding generation with respective probabilities $ 1 / (2N) $ and $ [1-(1 / 2N)] $ If the sample size is much smaller than the population size, the probability of coalescence for any pair in the sample in the preceding generation is simply the product $ p_{n} / (2N) $ . Thus, the probability distribution for the coalescence time of one pair within a set of n sequences is

$$
P _ {c} \left(p _ {n}, t\right) = \left[ 1 - \left(p _ {n} / 2 N\right) \right] ^ {t - 1} \left[ p _ {n} / (2 N) \right]
$$

Namely, a geometric random variable with success parameter $ ( p_{n} / 2 N) $ . The mean time to coalescence of the first pair is then $ 2 N / p_{n} $ generations (as opposed to 2N generations with a single pair). Because at this point two copies have coalesced into one, the sample size has been reduced by one, and the mean time to coalescence of the next pair is found by resetting $ p_{n} $ to $ p_{n-1}=(n-1)(n-2)/2 $ . This procedure can be followed recursively down to the final pair $ ( p_{n}=1) $ , which again has an expected coalescence time of 2N generations (Figure 2.10). The implication of these results is that the expected time for merging n random lineages into n-1 lineages,

$$
\bar {t} _ {n} = 2 N / p _ {n} = \frac {4 N}{n (n - 1)}
$$

increases with decreasing sample size.

The total expected genealogical depth of a sample, obtained by summing the expectations of each coalescence event, is

$$
\bar {t} _ {c} (n) = \sum_ {i = 2} ^ {n} \frac {4 N}{i (i - 1)} = 4 N \left(1 - \frac {1}{n}\right)
$$

Thus, under neutrality, the expected time to the most recent common ancestor of all alleles residing at a locus is $ \simeq 4 N $ generations. This is equivalent to the mean time to fixation of a neutral mutation, as can be verified by substituting $ p_{0}=1 / (2 N) $ into Equation 2.11b.

Notably, the expected distance between the final two nodes in a neutral coalescent tree, 2N, is at least half the coalescence time for the entire sample. Unfortunately, this fundamental issue is commonly ignored by those who invoke deep splits in a gene genealogy as evidence of an adaptive event.

It is important to note that all of the results in this section were derived without regard to any underlying genetic features of the sampled alleles. However, having determined the expected genealogical features of neutral gene sequences, it is straightforward to incorporate genetic issues, as mutations will arise randomly along the branches of the genealogy in numbers proportional to time. For example, given the average 2N generations separating two randomly sampled alleles, the average number of mutations separating such genes is $ 2\cdot 2 N\cdot u=4 N u $ , the two arising because each copy is 2N generations removed from the common ancestor. The actual number of mutations for any realization follows a Poisson distribution, so for this example, the probability that no mutations have arise is $ e^{-4 N u}. $

One of the primary uses of the coalescent derives from its ability to efficiently generate sample distributions of quantities of interest (e.g., the expected pattern of molecular variation among neutral alleles), which provides a formal basis for statistical tests of various evolutionary models (Hudson 2002), including those involving selection (Chapter 9). Although all of the preceding results simply refer to the expected coalescent times, each individual coalescence time has considerable evolutionary variance, being equal to the square of its expected value (a feature of geometric distributions). As will be discussed in Chapter 9, a number of useful results have been obtained on the sampling distributions of coalescents, but it is also straightforward to obtain such information by using computer simulations to construct random genealogies. For each simulated sample, one starts with n distinct lineages, picks two at random, and generates a value for $ t_{n} $ by randomly drawing from an exponential distribution with mean value given by Equation 2.40. After these two samples are joined in the coalescent tree, the remaining sample of n-1 distinct lineages is treated in the same way to generate a value of $ t_{n-1} $ , and so on, until the last two remaining lineages coalesce to yield $ t_{2} $ . For each branch of the resultant tree, the number of mutations is then drawn using a Poisson distribution with an expectation equal to the product of the mutation rate and the length of the branch (in generations), e.g., the two branches emanating from the first node have independent numbers of mutations with expectation $ ut_{n} $ . By repeating such coalescent simulations several thousands of times, a distribution of interallelic variation under mutation and drift can then be acquired for any mutational model of interest, with the resultant data providing a null model for various tests of selection based on the pattern of variation in an actual sample (Chapter 9).

## MUTATION-MIGRATION-DRIFT EQUILIBRIUM

Populations are often structured in space, with distinct demes connected by migration to form a metapopulation. The joint forces of mutation, migration, and drift structure the genetic variation both within and among demes, and if kept constant eventually lead to equilibrium values. The equilibrium neutral results serve as the framework for tests of abnormally high or low amounts of among-population variation (Chapter 9), corresponding respectively to diversifying and stabilizing selection.

## Quantifying Population Structure: $ F_{ST} $

The classic measure of population structure, $ F_{ST} $ , was defined by Wright (1943, 1951) as the correlation (identical by descent status) between alleles in different individuals from the same subpopulation. $ F_{ST} $ is a measure of the amount of inbreeding introduced by the population structure, relative to what would be expected in one large panmictic population. Effectively, $ F_{ST} $ measures the fraction of total genetic variance due to differences between subpopulations (indeed, S stands for subpopulation and T for total population). This directly follows from the standard ANOVA (analysis of variance) identity that the among-group component of variance equals the within-group covariance (LW Chapter 18),

with the latter equal to the correlation among group members times the total variance. In particular, consider the distribution of the allele frequencies for a biallelic locus (with alleles B and b) over a set of populations. If $ p_{0} $ denotes the average frequency of B over this set, the allelic variance for the total metapopulation is just $ p_{0}(1-p_{0}) $ . $ F_{ST} $ is then defined as the fraction of the total variance attributable to the variance in the frequency of allele B among demes, $ \sigma^{2}(p), $

$$
F _ {S T} = \frac {\sigma^ {2} (p)}{p _ {0} \left(1 - p _ {0}\right)}
$$

Wright was somewhat ambiguous in his use of $ F_{ST} $ , and some confusion has surrounded various interpretations of its true meaning. These issues were nicely cleaned up by Balding (2003).

Recalling Equation 2.14, which gives the expected variance in the allele frequency between two populations separated from a common ancestor t generations in the past (ignoring mutation and assuming no migration among groups), we have that

$$
F _ {S T} = \left[ 1 - \left(1 - \frac {1}{2 N _ {e}}\right) ^ {t} \right] \simeq \frac {t}{2 N _ {e}} \quad \mathrm {f o r} \quad t \ll N _ {e}
$$

Under this model, $ F_{ST} $ eventually increases to one, as in the absence of mutation, drift eventually removes all variation within groups, with the different demes becoming randomly fixed for alternative alleles.

With recurrent mutation and gene flow among demes, however, neither the withinor the among-population variation is ever expected to reach absolute zero, and $ F_{ST} $ will be in the (0,1) interval, with its magnitude depending on the relative impact of the three contributing forces (mutation, migration, and drift). A variety of methods, including extensions to multiple alleles, have been developed for estimating $ F_{ST} $ from samples of alleles from multiple subpopulations under the assumption of the infinite-alleles model (Nei and Chesser 1983; Weir and Cockerham 1984; Weir and Hill 2002; Balding 2003), and others allow for highly mutable alleles with a significant chance of back mutation (Slatkin 1995a; Goodman 1997).

A result of great conceptual utility is that $ F_{ST} $ values are closely related to the average coalescence times of alleles within subpopulations, $ \bar{t}_{0} $ , and of alleles drawn randomly from the entire metapopulation, $ \bar{t} $

$$
F _ {S T} = \frac {\bar {t} - \bar {t} _ {0}}{\bar {t}} = 1 - \frac {\bar {t} _ {0}}{\bar {t}}
$$

(Slaktin 1991). If $ \bar{t}_{0} $ is very close to $ \bar{t} $ , there is little among-group differentiation, as pairs of alleles within groups have essentially the same amount of time to diverge mutationally as those among groups. Because the coalescent structure of a population simply represents a genealogical sampling process and is independent of the mutations that incidentally arise, Equation 2.44 shows that the equilibrium level of population subdivision is also independent of the mutation process.

## Mutation-migration-drift Equilibrium Values of $ F_{ST} $

When migration rates are sufficiently high that essentially all demes exchange at least one individual per generation, the physical structure of the metapopulation has no consequences for population subdivision at the genetic level, i.e., $ F_{ST}\simeq0 $ . When the forces of mutation, migration, and drift operate simultaneously at moderate levels, some intermediate equilibrium level of among-population differentiation is reached such that the loss of new variants within demes by drift is balanced by the spread of novel variants across demes by mutation. As one might expect, the resultant equilibrium $ F_{ST} $ value is a function of the population size within each deme and the pattern of migration over demes, so there are essentially endless numbers of possible patterns of spatial structure and migration. To make some general points, we will consider two commonly envisioned situations (Figure 2.11).

![](page=33,bbox=[346, 144, 782, 287])

<div align="center">

Figure 2.11 (Left) The island model. Most mating occurs within each subpopulation/deme but some small amount of equally partitioned migration m occurs between them. Hence, a migrant from deme A is equally likely to end up in demes B through D. (Right) A hierarchically-structured population. Here, intragroup migration (between A and B, and between C and D, $ m_{1} $ ) occurs at a much higher level than migration between these two groups $ (m_{2}) $ .

</div>

The simplest structure is Wright's (1951) island model, wherein the population consists of d demes, each containing N breeding individuals. Each generation, each deme contributes a fraction m of its genes to a migrant pool, yielding an expected migration rate from any deme to any other of m/（d-1). A remarkable feature of this model is that the equilibrium amount of genetic variation expected within demes is independent of the level of population subdivision (assuming m>0), a feature known as the geographic invariance principle (Maruyama 1971; Nagylaki 1982). Provided there is some potential migratory route between all demes, regardless of the level of migration, the mean coalescence time between random pairs of genes within demes is

$$
\bar {t} _ {0} = 2 N d
$$

generations, i.e., twice the sum of the demic population sizes (Li 1976; Strobeck 1987; Hey 1991; Nagylaki 2000). Under this model, the independence of the within-deme variation of the migration rate arises because a lower rate of migration encourages a higher rate of allelic divergence, resulting in a balance between these two opposing factors (frequency and impact of immigrant alleles).

On the other hand, the mean coalescence time for two genes randomly drawn from the entire metapopulation is

$$
\bar {t} = 2 N d + \frac {(d - 1) ^ {2}}{2 d m}
$$

(Li 1976; Slatkin 1991; Nei and Takahata 1993), which is the sum of the previous term and the additional time required for alleles to coalesce into the same deme. Unlike the amount of variation within demes, the differentiation among demes clearly depends on m. Substituting Equations 2.45a and 2.45b into Equation 2.44 yields

$$
F _ {S T} = \frac {1}{1 + 4 N \frac {m d ^ {2}}{(1 - d) ^ {2}}} \simeq \frac {1}{1 + 4 N m} \quad \mathrm {f o r} \quad d \gg 1
$$

This again shows that the equilibrium level of population subdivision is completely independent of the mutation rate and largely independent of the number of demes (d), provided the latter is at least moderately large.

This type of framework for interpreting $ F_{ST} $ is readily extended to populations with a hierarchical structure (Figure 2.11). In the simplest hierarchical model, the metapopulation

is arranged into a series of g groups, each of which is further subdivided into d demes. Within each group, the demes exchange migrants according to the island model with total rate of $ m_{1} $ (so that $ m_{1} /[d-1] $ is the rate at which each deme sends migrants to any other particular deme within its group). By definition, there is less frequent exchange of migrants between the different groups, i.e., $ m_{2} < m_{1} $ .With this type of structure, it is necessary to consider the degree to which the total genetic variation partitions into three components: within demes, among demes within a group, and among groups.

Each of these components can again be expressed in terms of coalescence times. Let $ \bar{t}_{0} $ be the mean coalescence time for two individuals from the same deme, $ \bar{t}_{1} $ for two individuals from the same group but different demes, and $ \bar{t}_{2} $ for two individuals from different groups. As with the island model, the geographic invariance principle gives the mean coalescence time for two individuals from the same deme as $ \bar{t}_{0}=2N g d $ , i.e., twice the total population size. In order for two individuals in the same group but different demes to coalesce, they must first trace back to the same deme, which for $ m_{1}\ll m_{2} $ requires approximately $ t_{1}^{\prime}\simeq g(d-1)/(2m_{1}) $ generations (from the second term in Equation 2.45b), and then take an additional $ \bar{t}_{0} $ generations to coalesce within that deme, giving $ \bar{t}_{1}=t_{1}^{\prime}+\bar{t}_{0} $ (Slatkin and Voelm 1991). Finally, for individuals from different groups to coalesce, they first must trace back to the same group, which requires an average of $ t_{2}^{\prime}\simeq(g-1)/(2m_{2}) $ generations, then trace back to the same deme within a group $ (t_{1}^{\prime}) $ , and finally coalesce within that deme, giving $ \bar{t}_{2}=t_{2}^{\prime}+t_{1}^{\prime}+\bar{t}_{0}. $

Using these results, three hierarchical F statistics define the partitioning of the total population variation: $ F_{DG} $ among demes within groups, $ F_{GT} $ among groups within the total population, and $ F_{ST} $ among demes within the total population:

$$
\begin{array}{l} F _ {D G} = \frac {\bar {t} _ {1} - \bar {t} _ {0}}{\bar {t} _ {1}} \\ F _ {G T} = \frac {\bar {t} _ {2} - \bar {t} _ {1}}{\bar {t} _ {2}} \\ F _ {S T} = \frac {\bar {t} _ {2} - \bar {t} _ {0}}{\bar {t} _ {2}} \\ \end{array}
$$

(Slatkin and Voelm 1991; Excoffier et al. 2009b). Substituting in the values for the various mean coalescence times noted previously, and assuming d and g moderately large and $ m_{2}\ll m_{1} $ , results in further simplification,

$$
\begin{array}{l} F _ {D G} \simeq \frac {1}{1 + 4 N m _ {1}} \\ F _ {G T} \simeq F _ {S T} \simeq \frac {1}{1 + 4 N d m _ {2}} \\ \end{array}
$$

Note that these expressions are equivalent in form to that for the simple island model, in this case with the demic population size (N) determining the variation of demes within groups and group size (Nd) determining that for groups within the total population. Such coalescence approaches are readily extended to much more complex situations (e.g., Nordborg 1997; Nagylaki 1998; Pannell and Charlesworth 2000; Pannell 2003).