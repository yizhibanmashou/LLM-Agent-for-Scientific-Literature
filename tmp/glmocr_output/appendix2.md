<div align="center">

# Appendix 2

</div>

<div align="center">

# Introduction to Bayesian Analysis

</div>

Now I've heard a Bayesian is half a man

With robustness not on his side,

But as the problems get tougher,

I just watch and wonder

As the frequentists run and hide!

— Ain't Too Proud to Bayes, B. Carlin (ISBA 2000)

The history of statistical methods in genetics closely parallels advances in computation. Before the widespread use of computers, method-of-moments approaches were common as they are relatively easy to obtain. Here, a summary statistic of the data is computed whose expected value is the parameter of interest (e.g., using the sample mean, $ \overline{x} $ , as an estimate of the true mean, $ \mu_{x} $ , as $ E[\overline{x}]=\mu_{x} $ ). In the mid-1970s, maximum-likelihood (ML) methods became much more common place, as they offer a very flexible platform for statistical analysis (estimation, determining precision, and hypothesis testing), but at the cost of numerically searching an often highly complex multidimensional likelihood surface (LW Appendix 4). Both these approaches typically return point estimators for the variables of interest, along with some measure of their uncertainty. As opposed to these classical (or frequentist) approaches, Bayesian statistics (which can be viewed as a natural extension of likelihood methods) is concerned with generating the full distribution for the parameters, $ \Theta $ given the data, x, namely, obtaining the posterior distribution, $ p(\Theta|\mathbf{x}) $ . As such, Bayesian statistics provides a much more complete picture of the uncertainty in the estimation of the unknown parameters, especially after the confounding effects of nuisance parameters are removed.

Our treatment here is intentionally quite brief. A number of texts have presented excellent treatments of the statistical theory (e.g., Lindley 1965; Berger 1985; Carlin and Louis 2000; Lee 2012; Gelman et al. 2013). Blasco (2017) provided a very lucid introduction to applications in quantitative genetics, while Sorensen and Gianola (2002) offered a more comprehensive treatment. While very deep (and very subtle) differences in philosophy separate hard-core Bayesians from hard-core frequentists (Efron 1986; Glymour 1981), our treatment of Bayesian methods is motivated simply by their use as a powerful statistical tool. This appendix focuses on the basic theory, while the computational approaches that make these methods feasible are examined in Appendix 3.

## WHY ARE BAYESIAN METHODS BECOMING MORE POPULAR?

In addition to providing a more formal framework for dealing with parameter uncertainty, two specific features have fueled the rapid growth of Bayesian approaches in genetics and genomics. First, under a Bayesian analysis, all parameters are random effects as opposed to fixed effects (Chapter 19). This has profound implications for degrees of freedom. Consider a gene expression study with 30,000 features (genes of interest), whose mRNA levels are contrasted over a set of 100 normal liver cells versus 100 cancerous ones. If we treat the differential expression level of any particular gene as a fixed effect (an unknown constant to be estimated) we will very quickly use all of the degrees of freedom, given the small sample size. Conversely, if these levels are treated as random effects, with the expression difference associated with a particular gene being a random variable drawn from some underlying (and unknown) distribution, then the only degrees of freedom lost will be those used to estimate the associated parameters for this underlying distribution. Further, prediction of the random realization that corresponds to a particular gene borrows information over all

the genes. Thus, a Bayesian analysis can handle high-dimensional experiments in which the number of parameters, p, greatly exceeds the number of observations, n, in a framework that fully manages the uncertainty over all these estimates. Second, Bayesian methods are computationally feasible, as approaches such as MCMC (Appendix 3) allow high-dimensional datasets to be analyzed in a computationally efficient manner. In settings with a large number of nuisance parameters or a high-dimensional dataset, a Bayesian approach not only has considerable appeal, it may be the only approach that is even feasible.

## BAYES' THEOREM

The foundation of Bayesian statistics is Bayes' theorem. Suppose we observe a random variable, x, and wish to make inferences about another random variable, $ \theta $ , in the case where $ \theta $ is drawn from some distribution, $ \operatorname* {P r} (\theta) $ . From the definition of conditional probability

$$
\Pr (\theta \mid x) = \frac {\Pr (x , \theta)}{\Pr (x)}
$$

where (for now) x and $ \theta $ are discrete random variables. Again from the definition of conditional probability, we can express the joint probability by conditioning on $ \theta $ to give

$$
\Pr (x, \theta) = \Pr (x \mid \theta) \Pr (\theta)
$$

Putting these together yields Bayes' theorem

$$
\Pr (\theta \mid x) = \frac {\Pr (x \mid \theta) \Pr (\theta)}{\Pr (x)}
$$

Bayes' theorem flips the conditioning variable, allowing us to move from $ \operatorname* {P r} ( x \mid \theta) $ to $ \operatorname* {P r} (\theta \mid x). $ With k possible values of $ \theta $ $ \left( \theta_{1} \right. $ through $ \theta_{k} $ ), the discrete version of Bayes' theorem becomes

$$
\Pr \left(\theta_ {j} \mid x\right) = \frac {\Pr \left(x \mid \theta_ {j}\right) \Pr \left(\theta_ {j}\right)}{\Pr (x)} = \frac {\Pr \left(x \mid \theta_ {j}\right) \Pr \left(\theta_ {j}\right)}{\sum_ {i = 1} ^ {k} \Pr \left(\theta_ {i}\right) \Pr \left(x \mid \theta_ {i}\right)} \quad \mathrm {f o r} \quad 1 \leq j \leq k
$$

In Bayesian statistics, x represents an observable variable (the data), while $ \theta $ represents a parameter describing the distribution of x. In this setting, $ \operatorname* {P r} (\theta) $ is the prior distribution of possible parameter values, while $ \operatorname* {P r} (\theta \mid x) $ is the subsequent posterior distribution of $ \theta $ given the observed data x and the prior. In classical statistics, the unknown parameters are treated as fixed and the data are considered random, whereas under a Bayesian analysis, the data are considered fixed and the unknown parameters that generated the data are considered random.

All of the above statements also hold for continuous random variables, for which the probability density function, p, replaces the discrete probability value, Pr. In particular, the continuous multivariate version of Bayes' theorem is

$$
p (\Theta | \mathbf {x}) = \frac {p (\mathbf {x} \mid \Theta) p (\Theta)}{p (\mathbf {x})} = \frac {p (\mathbf {x} \mid \Theta) p (\Theta)}{\int p (\mathbf {x} , \Theta) d \Theta}
$$

where $ \Theta=\left(\theta_{1},\theta_{2},\cdots,\theta_{n}\right) $ is a vector of n (potentially) continuous variables. As with the univariate case, $ p(\Theta) $ is the assumed prior distribution of the unknown parameters, while $ p(\Theta|\mathbf{x}) $ is the posterior distribution given the prior, $ p(\Theta) $ , and the data, $ \mathbf{x}. $

The origin of Bayes' theorem has a fascinating history (Stigler 1983). It is named after the Rev. Thomas Bayes, a priest who never published a mathematical paper during his lifetime. The paper in which the theorem appears was posthumously read before the Royal Society by his friend Richard Price in 1764. Stigler suggests it was first discovered by Nicholas

Saunderson, a blind mathematician and optician who, at age 29, became Lucasian Professor of Mathematics at Cambridge (the position held earlier by Issac Newton). This is an example of Stigler's Law of Eponymy (Stigler 1980), wherein no discovery or invention is named after its first discoverer (an eponym). As is fitting, Stigler's law is self-consistent, as this phenomenon was previously mentioned by Merton (1965).

Example A2.1. Consider a recessive color locus in cattle in which the genotypes BB and Bb are black, while bb is red. Two black-coated parents are crossed, and produce some red offspring, which implies that both parents must be Bb. A black-coated son of theirs is crossed to n red dams (bb), and all of his offspring are black. What is the posterior probability that he is BB?

To solve this problem using Bayes' theorem, we first define the indicator random variable

$$
\theta = \left\{ \begin{array}{l l} 0 & \mathrm {s o n i s} B b \\ 1 & \mathrm {s o n i s} B B \end{array} \right.
$$

Given that both parents are Bb, the expected priors for their offspring are 1/4 for BB and 1/2 for Bb, resulting in a 3/4 prior for a black-coated offspring. Further, from conditional probability (Equation A2.1a), the prior that a black offspring is BB is

$$
\Pr (B B \mid \mathrm {B l a c k}) = \frac {\Pr (B B , \mathrm {B l a c k})}{\Pr (\mathrm {B l a c k})} = \frac {\Pr (B B)}{\Pr (\mathrm {B l a c k})} = \frac {1 / 4}{3 / 4} = 1 / 3
$$

where we used the fact that all BB are black, so that $ \operatorname{P r} ( B B, \mathrm{B l a c k} )=\operatorname{P r} ( B B ). $ Hence, the prior becomes

$$
\Pr (\theta) = \left\{ \begin{array}{l l l} 0 & \mathrm {i s} & 2 / 3 \\ 1 & \mathrm {i s} & 1 / 3 \end{array} \right.
$$

Further

$$
\Pr (\mathrm {a l l} n \mathrm {o f f s p r i n g a r e b l a c k} \mid \mathrm {s i r e i s} B B) = 1
$$

$$
\Pr (\mathrm {a l l} n \mathrm {o f f s p r i n g a r e b l a c k} \mid \mathrm {s i r e i s} B b) = (1 / 2) ^ {n}
$$

and

$$
\begin{array}{l} \Pr (\mathrm {a l l} n \mathrm {b l a c k}) = \Pr (\mathrm {a l l b l a c k} \mid B B) ^ {*} \Pr (B B) + \Pr (\mathrm {a l l b l a c k} \mid B b) ^ {*} \Pr (B b) \\ = 1 \cdot 1 / 3 + (1 / 2) ^ {n} \cdot (2 / 3) \\ \end{array}
$$

If we combine the above values, Bayes' theorem yields

$$
\Pr (\theta = 1 \mid n \mathrm {b l a c k o f f s p r i n g}) = \frac {\Pr (n \mid \theta = 1) \Pr (\theta = 1)}{\Pr (n)} = \frac {1 \cdot (1 / 3)}{1 \cdot (1 / 3) + (1 / 2) ^ {n} \cdot (2 / 3)}
$$

which returns values of 0.5,0.67,0.8,0.89,0.94,and 0.998 for n=1,2,3,4,5,and 10,respectively.

Example A2.2. Suppose a major gene (with alleles Q and q) underlies a character of interest. The distribution of phenotypic values for each major-locus genotype follows a normal distribution with a variance of 1 and means of 2.1, 3.5, and 1.3 for QQ, Qq, and qq, respectively. Suppose the frequencies of these genotypes for a random individual drawn from the population are 0.3, 0.2, and 0.5 (for QQ, Qq, and qq, respectively). If an individual from this population has a phenotypic value of 3, then what is the probability of it being QQ? Qq? qq? Let $ \varphi(x|\mu,1)=(2\pi)^{-1/2}e^{-(x-\mu)^{2}/2} $ denote the density function for a normal distribution with a mean of $ \mu $ and variance of 1. To apply Bayes' theorem, note that the values for the priors and the conditionals are as follows:

<table border="1"><tr><td>Genotype,G</td><td>Pr(G)</td><td>p(x|G)</td><td>Pr(G)·p(x|G)</td></tr><tr><td>QQ</td><td>0.3</td><td>φ(3|2.1,1)=0.266</td><td>0.078</td></tr><tr><td>Qq</td><td>0.2</td><td>φ(3|3.5,1)=0.350</td><td>0.070</td></tr><tr><td>qq</td><td>0.5</td><td>φ(3|1.3,1)=0.094</td><td>0.047</td></tr></table>

Because $ p ( 3 )=\sum_{G} \operatorname* {P r} ( G ) \cdot p ( 3 | G )=0.195 $ , Bayes' theorem gives the posterior probabilities for the genotypes given the observed value of 3 as:

$$
\Pr (Q Q \mid x = 3) = 0. 0 7 8 / 0. 1 9 5 = 0. 4 0 0
$$

$$
\Pr (Q q \mid x = 3) = 0. 0 7 0 / 0. 1 9 5 = 0. 3 5 9
$$

$$
\Pr (q q \mid x = 3) = 0. 0 4 7 / 0. 1 9 5 = 0. 2 4 1
$$

Thus, there is a 40 percent chance that this individual has a genotype of QQ, a 36 percent chance it is Qq, and a 24 percent chance it is qq.

## FROM LIKELIHOOD TO BAYESIAN ANALYSIS

The method of maximum likelihood (LW Appendix 4) and Bayesian analysis are closely related. Suppose $ \ell (\Theta|\mathbf{x}) $ is the assumed likelihood function. Under ML estimation, we would compute the mode of the likelihood function (the maximal value of $ \ell $ , as a function of $ \Theta $ given the data $ \mathbf{x} $ ), and use the local curvature around the mode to construct confidence intervals. Hypothesis testing follows using likelihood-ratio (LR) statistics. The strengths of ML estimation rely on its large-sample properties, namely, that when the sample size is sufficiently large, we can assume both normality of the estimators and that most LR tests follow $ \chi^{2} $ distributions. These features, nice as they are, may not hold for small samples. Conversely, a Bayesian analysis is exact for any sample size, given a specified prior.

To transition from a likelihood to a Bayesian analysis, we start with some prior distribution, p( $ \Theta $ ), that captures our initial knowledge (or best guess) about the possible values of the unknown parameters. From Bayes' theorem, the data (likelihood) is combined with the prior to produce a posterior distribution,

$$
p (\boldsymbol {\Theta} \mid \mathbf {x}) = \frac {1}{p (\mathbf {x})} \cdot p (\mathbf {x} \mid \boldsymbol {\Theta}) \cdot p (\boldsymbol {\Theta})
$$

$$
= (\mathrm {n o r m a l i z i n g c o n s t a n t}) \cdot p (\mathbf {x} | \Theta) \cdot p (\Theta)
$$

$$
= \mathrm {c o n s t a n t} \cdot \mathrm {l i k e l i h o o d} \cdot \mathrm {p r i o r}
$$

as $ p (\mathbf{x} \mid \Theta)=\ell (\Theta \mid \mathbf{x}) $ is simply the likelihood function (LW Appendix 4) and $ 1 / p (\mathbf{x}) $ is a constant (with respect to $ \Theta $ ). Consequently, the posterior distribution is often written as

$$
p (\Theta | \mathbf {x}) \propto \ell (\Theta | \mathbf {x}) p (\Theta)
$$

where the symbol $ \propto $ means "proportional to" (equal up to a constant). Note that the constant $ p(\mathbf{x}) $ normalizes $ p(\mathbf{x}|\Theta)\cdot p(\Theta) $ to one, and hence can be obtained by integration

$$
p (\mathbf {x}) = \int_ {\Theta} p (\mathbf {x} \mid \Theta) \cdot p (\Theta) d \Theta
$$

The dependence of the posterior on the prior (which can easily be assessed by trying different priors) provides an indication of how much information on the unknown parameter values is contained in the data (the curvature of the likelihood surface). If the posterior is highly dependent on the prior, then the data likely has little signal (a flat likelihood surface),

while if the posterior is largely unaffected by different priors, then the data are likely highly informative (a sharply peaked likelihood surface). To see this, taking logs on Equation A2.4c yields

$$
\log (\mathrm {p o s t e r i o r}) = \log (\mathrm {l i k e l i h o o d}) + \log (\mathrm {p r i o r}) + \mathrm {c o n s t a n t}
$$

When the likelihood signal is strong, it largely dominates the prior in the resulting posterior, but when a likelihood is weak, the prior can dominate.

## Marginal Posterior Distributions

Often only a subset of the unknown parameters is of concern to us, and the rest are nuisance parameters that are of no interest, but still must be fitted in the model. A strong feature of Bayesian analysis is that we can account for all the uncertainty introduced into the parameters of interest by any uncertainty in the values of nuisance parameters. This is accomplished by integrating the nuisance parameters out of the posterior distribution to generate a marginal posterior distribution for the parameters of interest. For example, suppose the mean and variance of data coming from a normal distribution are unknown, but our real interest is only in the variance. Estimating the mean introduces additional uncertainty into our variance estimate, which is not fully captured by standard classical approaches. Under a Bayesian analysis, the marginal posterior distribution for $ \sigma^{2} $ is simply

$$
p \left(\sigma^ {2} \mid \mathbf {x}\right) = \int p \left(\mu , \sigma^ {2} \mid \mathbf {x}\right) d \mu
$$

The resulting marginal posterior for $ \sigma^{2} $ captures all of the uncertainty in the estimation of $ \mu $ that influences the uncertainty in $ \sigma^{2} $ . This is an especially nice feature when a large number of nuisance parameters must be estimated.

The marginal posterior may involve several parameters (generating joint marginal posteriors). Suppose we write the vector of unknown parameters as $ \Theta=(\Theta_{1},\Theta_{nu}) $ , where $ \Theta_{nu} $ is the vector of nuisance parameters. Integrating over $ \Theta_{nu} $ yields the desired marginal for the vector $ \Theta_{1} $ of parameters of interest as

$$
p \left(\Theta_ {1} \mid \mathbf {y}\right) = \int_ {\Theta_ {n u}} p \left(\Theta_ {1}, \Theta_ {n u} \mid \mathbf {y}\right) d \Theta_ {n u}
$$

While these complex integrals appear quite daunting (and indeed almost always are from an analytic standpoint), generating draws from the marginal distribution is usually very straightforward using MCMC methods (which are examined in Appendix 3).

## SUMMARIZING THE POSTERIOR DISTRIBUTION

How do we extract a Bayesian estimator for some unknown parameter, $ \theta $ ? If our mindset is to use some sort of point estimator (as is usually done in classical statistics), then there are a number of candidates. We could follow maximum likelihood and use the mode of the posterior distribution (its maximal value)

$$
\widehat {\theta} = \max _ {\theta} \left[ p \left(\theta \mid \mathbf {x}\right) \right]
$$

We could take the expected value of $ \theta $ (its mean) given the posterior

$$
\widehat {\theta} = E [ \theta | \mathbf {x} ] = \int \theta p (\theta | \mathbf {x}) d \theta
$$

Another candidate is the median of the posterior, which is more robust than the mean to outliers. Here the estimator satisfies $ \operatorname* {P r} (\theta >\widehat{\theta}|\mathbf{x})=\operatorname* {P r} (\theta <\widehat{\theta}|\mathbf{x})=0.5 $ , hence

$$
\int_ {\widehat {\theta}} ^ {+ \infty} p (\theta | \mathbf {x}) d \theta = \int_ {- \infty} ^ {\widehat {\theta}} p (\theta | \mathbf {x}) d \theta = \frac {1}{2}
$$

However, using any of the above estimators, or even all three simultaneously, loses the full power of a Bayesian analysis, as the full estimator is the entire posterior density itself. If we cannot obtain the full form of the posterior distribution, then these estimates of general features of the distribution can be presented. However, as we will see in Appendix 3, we can generally obtain the full posterior by simulation using MCMC sampling, and hence the Bayesian estimate of a parameter is often presented as a frequency histogram (potentially smoothed) of the MCMC-generated samples from the posterior distribution (an empirical posterior).

## Highest Density Regions (HDRs)

Given the posterior distribution, the construction of confidence intervals is straightforward. For example, a 100(1- $ \alpha $) % confidence interval is given by any $ (L_{\alpha/2},H_{\alpha/2}) $ satisfying

$$
\int_ {L _ {\alpha / 2}} ^ {H _ {\alpha / 2}} p (\theta | \mathbf {x}) d \theta = 1 - \alpha
$$

To reduce the set of possible candidate intervals, one typically uses highest density regions or HDRs, where, for a single parameter, the HDR $ 1 0 0 ( 1-\alpha) $ region(s) are the shortest intervals giving an area of $ ( 1-\alpha) $ . More generally, if multiple parameters are being estimated, the HDR region(s) are those with the smallest volume in the parameter space. HDRs are also referred to as Bayesian confidence intervals or (better yet) credible intervals.

It is critical to note that there is a profound difference between a confidence interval (CI) from classical (frequentist) statistics and a Bayesian analysis. The interpretation of a classical confidence interval is that if we were to repeat the experiment a large number of times, and construct CIs in the same fashion, the fraction of the resulting collection of CIs that enclose the unknown parameter approaches $ (1-\alpha) $ . Thus, the frequentist CI is a measure of the frequency of occurrences in independent experiments in which the CI encloses the true value (and hence the term frequentist for this type of statistics). In contrast, with a Bayesian HDR, there is a probability of $ (1-\alpha) $ that the interval contains the true value of the unknown parameter. While at first blush these two intervals appear to be essentially identical, they are not, and indeed they are fundamentally (but subtly) different. Often the CI and Bayesian intervals span essentially the same values, but again the interpretational difference remains. The key point is that the Bayesian prior allows us to make direct probability statements about $ \theta $ , while under classical statistics we can only make statements about the behavior of the statistic if we consider repeating an experiment a large number of times. Given the important conceptual difference between classical and Bayesian intervals, Bayesians typically avoid using the term confidence interval, using the term credible interval instead.

## Bayes Factors and Hypothesis Testing

In the classical hypothesis-testing framework, we have two alternatives. The null hypothesis, $ \mathrm{H}_{0} $ , that the unknown parameter, $ \theta $ , belongs to some set or interval, $ \Theta_{0} $ $ \left( \theta\in\Theta_{0} \right) $ , versus the alternative hypothesis, $ \mathrm{H}_{1} $ , that $ \theta $ belongs to the alternative set, $ \Theta_{1} $ $ \left( \theta\in\Theta_{1} \right) $ . $ \Theta_{0} $ and $ \Theta_{1} $ contain no common elements $ \left( \Theta_{0}\cap\Theta_{1}=\oslash \right) $ and the union of $ \Theta_{0} $ and $ \Theta_{1} $ contains the entire space of values for $ \theta $ (i.e., $ \Theta_{0}\cup\Theta_{1}=\Theta) $ .

In the classical statistical framework of the frequentists, one uses the observed data to test the significance of a particular hypothesis, and (if possible) compute a p value (the probability, p, of observing a value equal to, or more extreme than, that of the test statistic if the null hypothesis is indeed correct). Initially, one would think that the idea of a hypothesis test is trivial in a Bayesian framework, as using the posterior distribution provides the expected p values directly, for example,

$$
\Pr (\theta > \theta_ {0}) = \int_ {\theta_ {0}} ^ {\infty} p (\theta | \mathbf {x}) d \theta \quad \mathrm {a n d} \quad \Pr (\theta_ {0} < \theta < \theta_ {1}) = \int_ {\theta_ {0}} ^ {\theta_ {1}} p (\theta | \mathbf {x}) d \theta
$$

The fault in this logic under a Bayesian framework is that we also have prior information and Bayesian hypothesis testing addresses whether, given the data, we are more or less inclined

to believe the hypothesis than was suggested from the prior. Hence, the prior probabilities influence hypothesis testing. To formalize this idea, let

$$
p _ {0} = \Pr \left(\theta \in \Theta_ {0} \mid \mathbf {x}\right) \quad \text {a n d} \quad p _ {1} = \Pr \left(\theta \in \Theta_ {1} \mid \mathbf {x}\right)
$$

denote the probabilities, given the observed data, x, that $ \theta $ is in the null $ (p_{0}) $ and alternative $ (p_{1}) $ hypothesis sets. Note that these are posterior probabilities. Because $ \Theta_{0}\cap\Theta_{1}=\oslash $ and $ \Theta_{0}\cup\Theta_{1}=\Theta $ , it follows that $ p_{0}+p_{1}=1 $ . Likewise, for the prior probabilities we have

$$
\pi_ {0} = \Pr (\theta \in \Theta_ {0}) \quad \text {a n d} \quad \pi_ {1} = \Pr (\theta \in \Theta_ {1})
$$

Thus the prior odds of $ \mathrm{H}_{0} $ versus $ \mathrm{H}_{1} $ are $ \pi_{0} / \pi_{1} $ , while the posterior odds are $ p_{0} / p_{1} $

The Bayes factor, $ \mathbf{B}_{0} $ , in favor of $ \mathrm{H}_{0} $ versus $ \mathrm{H}_{1} $ is calculated by the ratio of the posterior odds divided by the prior odds,

$$
B _ {0} = \frac {p _ {0} / p _ {1}}{\pi_ {0} / \pi_ {1}} = \frac {p _ {0} \pi_ {1}}{p _ {1} \pi_ {0}}
$$

The Bayes factor is loosely interpreted as the odds in favor of $ \mathrm{H}_{0} $ over $ \mathrm{H}_{1} $ as given by the data and our prior opinion. Because $ \pi_{1}=1-\pi_{0} $ and $ p_{1}=1-p_{0} $ , we can also express this as

$$
B _ {0} = \frac {p _ {0} \left(1 - \pi_ {0}\right)}{\pi_ {0} \left(1 - p _ {0}\right)}
$$

By symmetry, note that the Bayes factor, $ \mathrm{B}_{1} $ , in favor of $ \mathrm{H}_{1} $ versus $ \mathrm{H}_{0} $ is simply $ B_{1}=1 / B_{0}. $

Example A2.3. Suppose that the prior distribution of $ \theta $ is such that $ \operatorname* {P r} \left( \theta >\theta_{0}\right)=0.10 $ , while for the posterior distribution $ \operatorname* {P r} \left( \theta >\theta_{0} \mid \mathbf{x}\right)=0.05 $ . The latter is significant at the 5% level in a classical hypothesis-testing framework, but the data only doubles our confidence in the alternative hypothesis relative to our belief based on prior information. If $ \operatorname* {P r} \left( \theta >\theta_{0}\right)=0.50 $ for the prior, then a 5% posterior probability would greatly increase our confidence in the alternative hypothesis. Consider the first case in this example, where the prior and posterior probabilities for the null were $ \pi_{0}=0.1 $ and $ p_{0}=0.05 $ , respectively. The Bayes factor in favor of $ \mathrm{H}_{1} $ versus $ \mathrm{H}_{0} $ is

$$
B _ {1} = \frac {\pi_ {0} \left(1 - p _ {0}\right)}{p _ {0} \left(1 - \pi_ {0}\right)} = \frac {0 . 1 \cdot 0 . 9 5}{0 . 0 5 \cdot 0 . 9} = 4. 2 2
$$

Similarly, for the second example, where the prior for the null was $ \pi_{0}=0.5 $

$$
B _ {1} = \frac {0 . 5 \cdot 0 . 9 5}{0 . 0 5 \cdot 0 . 5} = 1 9
$$

Here, the data showed close to a 20-fold improvement (relative to the prior) in support of $ H_{1} $ Bayes factors and p values represent fundamentally different approaches to an analysis and are not formally comparable. However, a loose interpretation is that a factor of 20 is akin to the level of support of a p=0.05, and a factor of 100 to p=0.01.

When the hypotheses are simple (i.e., single values), say $ \Theta_{0}=\theta_{0} $ vs. $ \Theta_{1}=\theta_{1} $ , then

$$
p _ {i} \propto p \left(\theta_ {i}\right) p \left(\mathbf {x} \mid \theta_ {i}\right) = \pi_ {i} p \left(\mathbf {x} \mid \theta_ {i}\right) \quad \mathrm {f o r} \quad i = 0, 1
$$

Thus

$$
\frac {p _ {0}}{p _ {1}} = \frac {\pi_ {0} p (\mathbf {x} | \theta_ {0})}{\pi_ {1} p (\mathbf {x} | \theta_ {1})}
$$

and from Equation A2.10a, the Bayes factor (in favor of the null) reduces to

$$
B _ {0} = \frac {p \left(\mathbf {x} \mid \theta_ {0}\right)}{p \left(\mathbf {x} \mid \theta_ {1}\right)}
$$

which is simply a likelihood ratio (LW Appendix 4).

When hypotheses are composite (containing multiple elements), the situation is slightly more complicated. First, note that the prior distribution of $ \theta $ conditioned on $ \mathrm{H}_{0} $ or $ \mathrm{H}_{1} $ is

$$
p _ {i} (\theta) = p (\theta) / \pi_ {i} \quad \text {f o r} \quad i = 0, 1
$$

as the total probability $ \theta\in\Theta_{i}=\pi_{i} $ , so dividing by $ \pi_{i} $ normalizes the distribution to integrate to one. Thus,

$$
\begin{array}{l} p _ {i} = \Pr (\theta \in \Theta_ {i} | \mathbf {x}) = \int_ {\theta \in \Theta_ {i}} p (\theta | \mathbf {x}) d \theta \\ = \frac {1}{p (\mathbf {x})} \int_ {\theta \in \Theta_ {i}} p (\theta) p (\mathbf {x} \mid \theta) d \theta \\ = \pi_ {i} \int_ {\theta \in \Theta_ {i}} p (\mathbf {x} \mid \theta) p _ {i} (\theta) d \theta \\ \end{array}
$$

where the second step follows from Bayes' theorem, while the final step follows from Equation A2.12. The Bayes factor in favor of the null hypothesis becomes

$$
B _ {0} = \left(\frac {p _ {0}}{\pi_ {0}}\right) \left(\frac {\pi_ {1}}{p _ {1}}\right) = \frac {\int_ {\theta \in \Theta_ {0}} p (\mathbf {x} | \theta) p _ {0} (\theta) d \theta}{\int_ {\theta \in \Theta_ {1}} p (\mathbf {x} | \theta) p _ {1} (\theta) d \theta}
$$

which is a ratio of the weighted likelihoods of $ \Theta_{0} $ and $ \Theta_{1} $

## THE CHOICE OF A PRIOR

Obviously, a critical feature of any Bayesian analysis is the choice of a prior. The key is that when the data have a sufficiently strong signal, even a poor choice of a prior will still not greatly influence the posterior. In a sense, it is an asymptotic (large-sample) property of Bayesian analysis in that all but pathological priors (those with zero probability where the true value lies) can be overcome by sufficient amounts of data. As mentioned above, one can check the impact of the prior by assessing the stability of posterior over a collection of diverse priors. The location of a parameter (mean or mode) and its precision (the reciprocal of the variance) of the prior is usually more critical than its actual shape in terms of conveying prior information. The shape (family) of the prior distribution is often chosen to facilitate calculation of the posterior, especially through the use of conjugate priors that, for a given likelihood function, return a posterior in the same distribution family as the prior (e.g., a gamma prior returns a gamma posterior when the likelihood is Poisson). We will return to conjugate priors, but first we will discuss other approaches for construction of priors.

## Diffuse Priors

One of the most commonly used priors is the flat or diffuse (also called uninformative or naive) prior, which is simply a constant

$$
p (\theta) = \frac {1}{b - a} \quad \mathrm {f o r} \quad a \leq \theta \leq b
$$

This conveys that we have no a priori reason to favor any particular parameter value over another. With a flat prior, the posterior is just a constant C times the likelihood

$$
p (\theta | \mathbf {x}) = C \ell (\theta | \mathbf {x})
$$

![](page=8,bbox=[109, 113, 426, 311])

![](page=8,bbox=[446, 119, 763, 310])

<div align="center">

Figure A2.1 A uniform prior on one scale does not result in a flat prior on a transformed scale. Suppose a flat prior on (0,10000) is assumed for both the additive and residual variances. To mimic what happens under MCMC, we display these priors by using the resulting histograms generated from a large number of random draws, with a uniform expected to return a flat histogram. Left: The resulting prior for the standard deviation of either variance (the square root of a random draw). Right: The resulting prior for $ h^{2} $ , the ratio of a random draw for the additive variance divided by this value plus a random draw for the residual variance. Neither of these priors result in a uniform prior (namely, a flat histogram) on the transformed scale.

</div>

and we typically write that $ p (\theta \mid \mathbf{x})\propto \ell (\theta \mid \mathbf{x}) $ . In many cases, classical expressions from frequentist statistics are obtained by Bayesian analysis through assuming a flat prior.

If the variable (i.e., parameter) of interest ranges over $ (0,\infty) $ or $ (-\infty,+\infty) $ , then, strictly speaking, a flat prior does not exist as, if the constant takes on any nonzero value, the integral does not exist. In such cases a flat prior (i.e., assuming $ p[\theta |\mathbf{x}] \propto \ell[\theta |\mathbf{x}] $ ) is referred to as an improper prior, and care must be taken to ensure that the product of the prior and the likelihood results in a proper posterior (i.e., $ \ell[\theta |\mathbf{x}] $ has a finite integral over the parameter range). This is by no means certain.

Another complication involved in using a uniform prior arises when the question of interest resides on a different scale than that used for the prior. A variable uniform on one scale may be far from uniform on a transformed scale. Figure A2.1 shows two examples based on the assumption that there was a flat prior on the variance. A uniform prior on the variance does not result in a uniform prior on the standard deviation (e.g., Van Dongen 2006). Likewise, if one assumes that the additive and residual variances have flat priors, this does not imply a flat prior for $ h^{2} $ , but rather a prior that is sharply peaked at 1/2. When assuming a flat prior, care must be taken that it is truly uninformative on the appropriate scale of biological interest. Otherwise, the choice of what superficially appears as an unbiased prior may instead create a bias that the signal in the data must overcome.

## The Jeffreys Prior

Jeffreys (1961) proposed a general prior based on the Fisher information information, I, of the likelihood. Recall (LW Appendix 4) that

$$
I (\theta | \mathbf {x}) = - E \left[ \frac {\partial^ {2} \ln \ell (\theta | \mathbf {x})}{\partial \theta^ {2}} \right]
$$

The Jeffreys prior is as follows:

$$
p (\theta) \propto \sqrt {I (\theta \mid \mathbf {x})}
$$

A full discussion, with derivation, can be found in Lee (2012).

When there are k parameters, I is the $ k\times k $ Fisher information matrix of the expected second partials, where the elements of I are calculated by

$$
\mathbf {I} (\boldsymbol {\Theta} | \mathbf {x}) _ {i j} = - E _ {x} \left[ \frac {\partial^ {2} \ln \ell (\boldsymbol {\Theta} | \mathbf {x})}{\partial \theta_ {i} \partial \theta_ {j}} \right]
$$

In this case, the Jeffreys prior becomes

$$
p (\Theta) \propto \sqrt {\det [ \mathrm {I} (\theta | \mathbf {x}) ]}
$$

Example A2.4. Consider the likelihood of x successes in n independent draws from a binomial with a success parameter of $ \theta, $

$$
\ell (\theta \mid \mathbf {x}) = C \theta^ {x} (1 - \theta) ^ {n - x}
$$

where the constant C does not involve $ \theta $ . Taking logs gives

$$
L (\theta | \mathbf {x}) = \ln [ \ell (\theta | \mathbf {x}) ] = \ln C + x \ln \theta + (n - x) \ln (1 - \theta)
$$

Thus

$$
\frac {\partial L (\theta | \mathbf {x})}{\partial \theta} = \frac {x}{\theta} - \frac {n - x}{1 - \theta}
$$

and likewise

$$
\frac {\partial^ {2} L (\theta | \mathbf {x})}{\partial \theta^ {2}} = - \frac {x}{\theta^ {2}} - (- 1) \cdot (- 1) \frac {n - x}{(1 - \theta) ^ {2}} = - \left(\frac {x}{\theta^ {2}} + \frac {n - x}{(1 - \theta) ^ {2}}\right)
$$

Because $ E[x] = n\theta $ , then

$$
- E \left[ \frac {\partial^ {2} \ln \ell (\theta | \mathbf {x})}{\partial \theta^ {2}} \right] = \frac {n \theta}{\theta^ {2}} + \frac {n (1 - \theta)}{(1 - \theta) ^ {2}} = n \theta^ {- 1} (1 - \theta) ^ {- 1}
$$

The resulting Jeffreys prior for this likelihood becomes

$$
p (\theta) \propto \sqrt {\theta^ {- 1} (1 - \theta) ^ {- 1}} \propto \theta^ {- 1 / 2} (1 - \theta) ^ {- 1 / 2}
$$

which is a U-shaped beta distribution with parameters $ \alpha=\beta=1/2 $ (Equation A2.38a). This prior puts more weight on extreme values relative to assuming a uniform over (0,1), see Figure A2.3.

Example A2.5. Suppose our data consists of n independent draws from a normal distribution with an unknown mean and variance, $ \mu $ and $ \sigma^{2} $ . In LW Appendix 4, we showed that the information matrix in this case is

$$
\mathbf {I} = n \left( \begin{array}{c c} \frac {1}{\sigma^ {2}} & 0 \\ 0 & \frac {1}{2 \sigma^ {4}} \end{array} \right)
$$

Because the determinant of a diagonal matrix is the product of the diagonal elements, $ \det (\mathbf{I})\propto \sigma^{-6} $ , giving the Jeffreys prior for $ \mu $ and $ \sigma^{2} $ as

$$
p (\Theta) \propto \sqrt {\sigma^ {- 6}} = \sigma^ {- 3}
$$

Because the joint prior does not involve $ \mu $ , this implies a flat prior for $ \mu $ (i.e., $ p[\mu ]=c) $ . Note here that the prior distributions of $ \mu $ and $ \sigma^{2} $ are independent, as

$$
p (\mu , \theta) = c \cdot \sigma^ {- 3} = p (\mu) \cdot p \left(\sigma^ {2}\right)
$$

## POSTERIOR DISTRIBUTIONS UNDER NORMALITY ASSUMPTIONS

To introduce the basic ideas of Bayesian analysis, as well as treating a common assumption in quantitative genetics, consider the case where data are drawn from a normal (Gaussian) distribution, giving the likelihood function for the ith observation, $ x_{i} $ , as

$$
\ell \left(\mu , \sigma^ {2} \mid x _ {i}\right) = \frac {1}{\sqrt {2 \pi \sigma^ {2}}} \exp \left(- \frac {\left(x _ {i} - \mu\right) ^ {2}}{2 \sigma^ {2}}\right)
$$

If we assume independence, the resulting full likelihood for all n data points (with a sample mean of $ \overline{x} $ ) is

$$
\ell (\mu | \mathbf {x}) = \frac {1}{\sqrt {2 \pi \sigma^ {2}}} \exp \left(- \sum_ {i = 1} ^ {n} \frac {\left(x _ {i} - \mu\right) ^ {2}}{2 \sigma^ {2}}\right)
$$

$$
= \frac {1}{\sqrt {2 \pi \sigma^ {2}}} \exp \left[ - \frac {1}{2 \sigma^ {2}} \left(\sum_ {i = 1} ^ {n} x _ {i} ^ {2} - 2 \mu n \bar {x} + n \mu^ {2}\right) \right]
$$

The form of the posteriors given these normal likelihoods is a function of the assumed priors. By using the appropriate conjugate priors, these posteriors follow fairly standard distributions, and hence are easier to work with, as we now demonstrate.

## Gaussian Likelihood With Known Variance and Unknown Mean

As a starting point, assume that the variance, $ \sigma^{2} $ is known, while the mean, $ \mu $ is unknown. For a Bayesian analysis, it remains to specify the prior for $ \mu, p(\mu) $ . Suppose we assume a Gaussian prior, $ \mu\sim\mathrm{N}(\mu_{0},\sigma_{0}^{2}) $ , with

$$
p (\mu) = \frac {1}{\sqrt {2 \pi \sigma_ {0} ^ {2}}} \exp \left(- \frac {\left(\mu - \mu_ {0}\right) ^ {2}}{2 \sigma_ {0} ^ {2}}\right)
$$

The mean and variance of the prior, $ \mu_{0} $ and $ \sigma_{0}^{2} $ , are referred to as hyperparameters. Here, $ \mu_{0} $ specifies a prior location for the parameter (the unknown mean, $ \mu $ ), while $ \sigma_{0}^{2} $ specifies our uncertainty in this prior location—the larger $ \sigma_{0}^{2} $ , the greater is our uncertainty. In the limit as $ \sigma_{0}^{2}\rightarrow\infty $ , $ p(\mu) $ approaches a flat (and in this case, improper) prior.

A useful device when calculating the posterior distribution is to ignore terms that are constants with respect to the unknown parameters. Suppose x denotes the data and $ \varTheta_{1} $ is a vector of known model parameters, while $ \varTheta_{2} $ is a vector of unknown parameters. If we can write the posterior as

$$
p \left(\boldsymbol {\Theta} _ {2} \mid \mathbf {x}, \boldsymbol {\Theta} _ {1}\right) = f \left(\mathbf {x}, \boldsymbol {\Theta} _ {1}\right) \cdot g \left(\mathbf {x}, \boldsymbol {\Theta} _ {1}, \boldsymbol {\Theta} _ {2}\right)
$$

then

$$
p \left(\boldsymbol {\Theta} _ {2} \mid \mathbf {x}, \boldsymbol {\Theta} _ {1}\right) \propto g \left(\mathbf {x}, \boldsymbol {\Theta} _ {1}, \boldsymbol {\Theta} _ {2}\right)
$$

which follows since $ f(\mathbf{x},\Theta_{1}) $ is constant with respect to $ \Theta_{2}. $

With the prior given by Equation A2.19, we can express the resulting posterior distribution as

$$
\begin{array}{l} p (\mu | \mathbf {x}) \propto \ell (\mu | \mathbf {x}) \cdot p (\mu) \\ \propto \exp \left[ - \frac {\left(\mu - \mu_ {0}\right) ^ {2}}{2 \sigma_ {0} ^ {2}} - \frac {1}{2 \sigma^ {2}} \left(\sum_ {i = 1} ^ {n} x _ {i} ^ {2} - 2 \mu n \bar {x} + n \mu^ {2}\right) \right] \\ \end{array}
$$

We can factor out additional terms not involving $ \mu $ to obtain

$$
p \left(\mu \mid \mathbf {x}\right) \propto \exp \left(- \frac {\mu^ {2}}{2 \sigma_ {0} ^ {2}} + \frac {\mu \mu_ {0}}{\sigma_ {0} ^ {2}} + \frac {\mu n \bar {x}}{\sigma^ {2}} - \frac {n \mu^ {2}}{2 \sigma^ {2}}\right)
$$

Factoring in terms of $ \mu $ , the term in the exponential becomes

$$
- \frac {\mu^ {2}}{2} \left(\frac {1}{\sigma_ {0} ^ {2}} + \frac {n}{\sigma^ {2}}\right) + \mu \left(\frac {\mu_ {0}}{\sigma_ {0} ^ {2}} + \frac {n \bar {x}}{\sigma^ {2}}\right) = - \frac {\mu^ {2}}{\sigma_ {*} ^ {2}} + \frac {2 \mu \mu_ {*}}{2 \sigma_ {*} ^ {2}}
$$

where

$$
\sigma_ {*} ^ {2} = \left(\frac {1}{\sigma_ {0} ^ {2}} + \frac {n}{\sigma^ {2}}\right) ^ {- 1} \quad \mathrm {a n d} \quad \mu_ {*} = \sigma_ {*} ^ {2} \left(\frac {\mu_ {0}}{\sigma_ {0} ^ {2}} + \frac {n \bar {x}}{\sigma^ {2}}\right)
$$

Finally, by completing the square, we have

$$
p \left(\mu \mid \mathbf {x}\right) \propto \exp \left[ - \frac {\left(\mu - \mu_ {*}\right) ^ {2}}{2 \sigma_ {*} ^ {2}} + f \left(\mathbf {x}, \mu_ {0}, \sigma^ {2}, \sigma_ {0} ^ {2}\right) \right]
$$

Recalling Equation A2.20b, we can ignore the second term in the exponential (as it does not involve $ \mu $), and the resulting posterior for $ \mu $ (given the observed data x) becomes

$$
p \left(\mu \mid \mathbf {x}\right) \propto \exp \left[ - \frac {\left(\mu - \mu_ {*}\right) ^ {2}}{2 \sigma_ {*} ^ {2}} \right]
$$

demonstrating that the posterior density function for $ \mu $ is a normal with a mean of $ \mu_{*} $ and a variance of $ \sigma_{*}^{2} $ , namely,

$$
\mu \mid (\mathbf {x}, \sigma^ {2}) \sim \mathrm {N} \left(\mu_ {*}, \sigma_ {*} ^ {2}\right)
$$

Notice that the posterior density is in the same form as the prior. This occurred because the prior conjugated with the likelihood function—the product of the prior and likelihood returned a distribution in the same family as the prior (but with different distribution parameters). The use of such conjugate priors associated with a given family of likelihood functions is a key concept in Bayesian analysis, and we will explore it more fully below.

We are now in a position to inquire about the relative importance of the prior versus the data. Under the assumed prior, the mean (and in this case, the mode as well) of the posterior distribution is

$$
\mu_ {*} = \mu_ {0} \frac {\sigma_ {*} ^ {2}}{\sigma_ {0} ^ {2}} + \bar {x} \frac {\sigma_ {*} ^ {2}}{\sigma^ {2} / n}
$$

With a very diffuse prior on $ \mu $ (i.e., $ \sigma_{0}^{2}\gg\sigma^{2} $), $ \sigma_{*}^{2}\rightarrow\sigma^{2}/n $ and $ \mu_{*} \rightarrow\overline{x} $ . Also note from Equation A2.22b that as we collect enough data (i.e., achieve a sufficiently large value of n), $ \sigma_{*}^{2}\rightarrow\sigma^{2}/n $ and again $ \mu_{*} \rightarrow\overline{x} $ , implying that primarily the data, rather than the prior, will influence the posterior when the value of n is sufficiently large.

## Gamma, $ \chi^{2} $ , Inverse-gamma, and $ \chi^{-2} $ Distributions

Before examining the Gaussian likelihood with unknown variance, a brief aside is needed to develop the inverse chi-square distribution, denoted by $ \chi^{-2} $ . We do this via the gamma and inverse-gamma distributions, as both $ \chi^{2} $ and $ \chi^{-2} $ are special cases of these distributions.

![](page=12,bbox=[114, 117, 428, 294])

![](page=12,bbox=[450, 120, 759, 294])

<div align="center">

Figure A2.2 The effect of the shape $ (\alpha) $ and rate $ (\beta=1 / \lambda) $ the inverse of the scale) parameters on the gamma distribution function. For $ \alpha=1 $ , the resulting distribution is the simple monotonically decreasing exponential, while for $ \alpha>1 $ , the distribution is unimodal. The effect of a change in the rate or scale is to keep the general shape but change the scaling with respect to x.

</div>

To motivate the gamma distribution, first consider the simple exponential waitingtime distribution, where $ \beta $ is the rate (the probability of a success in some small time unit, $ \delta_{t} $ , is given by $ \beta \delta_{t} $ ), then the probability density function (pdf) for the exponential is

$$
p (x \mid \beta) = \beta e ^ {- \beta x} \quad \mathrm {f o r} \quad 0 \leq x < \infty , \quad \beta > 0
$$

Because the expected waiting time until a success is $ \lambda=1 / \beta $ , this can be reparameterized in terms of the scale (waiting time) parameter as

$$
p (x \mid \beta) = \lambda^ {- 1} e ^ {- x / \lambda}
$$

The sum of k exponentials with the same rate (or scale) parameter is called an Erlang distribution, and it was initially developed for certain problems in telephone queuing theory. Expressed in terms of the rate parameter, the resulting pdf becomes

$$
p (x \mid k, \beta) = \frac {\beta^ {k}}{(k - 1) !} x ^ {k - 1} e ^ {- \beta x} \quad \mathrm {f o r} \quad 0 \leq x < \infty
$$

where the integer k is called the shape parameter, with k=1 recovering the exponential.

The gamma distribution follows by allowing the shape parameter to be any positive number, $ \alpha $ , with $ x\sim \mathrm{Gamma}(\alpha ,\beta) $ having its pdf defined by its shape $ (\alpha) $ and rate $ (\beta) $ values,

$$
p (x \mid \alpha , \beta) = \frac {\beta^ {\alpha}}{\Gamma (\alpha)} x ^ {\alpha - 1} e ^ {- \beta x} \quad \mathrm {f o r} \alpha , \beta , x > 0
$$

Note that the factorial in the Erlang is replaced by the gamma function, $ \Gamma ( x ) $ , which is defined below (Equation A2.26a). Figure A2.2 shows how changes in these two parameters influence the shape of the distribution. Note that, as a function of x,

$$
p (x \mid \alpha , \beta) \propto x ^ {\alpha - 1} e ^ {- \beta x}
$$

When expressed in terms of the scale $ (\lambda=1 / \beta) $ parameter, the pdf becomes

$$
p (x \mid \alpha , \lambda) = \frac {\lambda^ {- \alpha}}{\Gamma (\alpha)} x ^ {\alpha - 1} e ^ {- x / \lambda}
$$

<div align="center">

Table A2.1 Summary of the functional forms (in terms of x) of various gamma-related distributions. See the text for further details.

</div>

<table border="1"><tr><td>Distribution</td><td>$\alpha$</td><td>$\beta$</td><td>$p(x)/\mathrm{constant}$</td></tr><tr><td>Gamma($\alpha,\beta$)</td><td></td><td></td><td>$x^{\alpha-1}e^{-\beta x}$</td></tr><tr><td>Chi-square,$\chi_{n}^{2}$</td><td>$n/2$</td><td>1/2</td><td>$x^{n/2-1}e^{-x/2}$</td></tr><tr><td>Inverse-gamma($\alpha,\beta$)</td><td></td><td></td><td>$x^{-(\alpha+1)}e^{-\beta/x}$</td></tr><tr><td>Inverse chi-square,$\chi_{n}^{-2}$</td><td>$n/2$</td><td>1/2</td><td>$x^{-(n/2+1)}e^{-1/(2x)}$</td></tr><tr><td>Scaled inverse chi-square,$\chi_{(n,\sigma_{0}^{2})}^{-2}$</td><td>$n/2$</td><td>$\sigma_{0}^{2}/2$</td><td>$x^{-(n/2+1)}e^{-\sigma_{0}^{2}/(2x)}$</td></tr></table>

which yields

$$
p (x \mid \alpha , \lambda) \propto x ^ {\alpha - 1} e ^ {- x / \lambda}
$$

Because both the rate and scale versions of the gamma distribution are widely used, take care to know which version your software package is using (for example, the default in R uses the scale parameter version). We can parameterize a gamma in terms of its mean and variance by noting that

$$
\mu_ {x} = \frac {\alpha}{\beta} = \alpha \lambda \quad \mathrm {a n d} \quad \sigma_ {x} ^ {2} = \frac {\alpha}{\beta^ {2}} = \alpha \lambda^ {2}
$$

so that

$$
\alpha = \frac {\mu_ {x} ^ {2}}{\sigma_ {x} ^ {2}} \quad \mathrm {a n d} \quad \beta = \frac {\mu_ {x}}{\sigma_ {x} ^ {2}}
$$

$ \Gamma (\alpha) $ , the gamma function evaluated at $ \alpha $ (which normalizes the gamma distribution), is defined by

$$
\Gamma (\alpha) = \int_ {0} ^ {\infty} y ^ {\alpha - 1} e ^ {- y} d y \quad \mathrm {f o r} \alpha > 0
$$

This is the generalization of the factorial function from the integers to any positive number. If n is an integer, then $ \Gamma(n)=(n-1)! $ Using integration by parts, one can show that $ \Gamma $ satisfies the following identities

$$
\Gamma (\alpha + 1) = \alpha \Gamma (\alpha), \quad \Gamma (1) = 1, \quad \mathrm {a n d} \quad \Gamma (1 / 2) = \sqrt {\pi}
$$

The chi-square $ (\chi^{2}) $ distribution is a special case of the gamma, as a $ \chi^{2} $ random variable with n degrees of freedom follows a gamma distribution with parameters $ \alpha=n/2 $ and $ \beta=1/2 $ $ (\lambda=2) $ , namely, $ \chi_{n}^{2}\sim\mathrm{Gamma}(n/2,1/2) $ , giving the density function as

$$
p (x \mid n) = \frac {2 ^ {- n / 2}}{\Gamma (n / 2)} x ^ {n / 2 - 1} e ^ {- x / 2}
$$

Hence for $ x\sim \chi_{n}^{2} $

$$
p (x) \propto x ^ {n / 2 - 1} e ^ {- x / 2}
$$

The inverse-gamma distribution will prove useful as a conjugate prior for Gaussian likelihoods with unknown variance. It is defined by the distribution of the random variable $ y=x^{-1} $ , where $ x\sim \mathrm{Gamma}(\alpha ,\beta). $ The resulting density function is

$$
p (x \mid \alpha , \beta) = \frac {\beta^ {\alpha}}{\Gamma (\alpha)} x ^ {- (\alpha + 1)} e ^ {- \beta / x} \quad \mathrm {f o r} \alpha , \beta , x > 0
$$

The mean and variance for this distribution are only defined (i.e., finite) if $ \alpha $ is sufficiently large, with

$$
\mu_ {x} = \frac {\beta}{\alpha - 1} \quad \mathrm {f o r} \alpha > 1 \quad \mathrm {a n d} \quad \sigma_ {x} ^ {2} = \frac {\beta^ {2}}{(\alpha - 1) ^ {2} (\alpha - 2)} \quad \mathrm {f o r} \alpha > 2
$$

Note for the inverse gamma that

$$
p (x \mid \alpha , \beta) \propto x ^ {- (\alpha + 1)} e ^ {- \beta / x}
$$

If $ y\sim \chi_{n}^{2} $ , then $ x=1/y $ follows an inverse chi-square distribution, which is denoted by $ x\sim \chi_{n}^{-2} $ . This is a special case of the inverse gamma, with (as for a normal $ \chi^{2} $ $ \alpha=n/2 $ $ \beta=1/2 $ . For $ n>4 $ (i.e., $ \alpha>2 $ ), the resulting density function is

$$
p (x \mid n) = \frac {2 ^ {- n / 2}}{\Gamma (n / 2)} x ^ {- (n / 2 + 1)} e ^ {- 1 / (2 x)}
$$

with a mean and variance of

$$
\mu_ {x} = \frac {1}{n - 2} \quad \mathrm {a n d} \quad \sigma_ {x} ^ {2} = \frac {2}{(n - 2) ^ {2} (n - 4)}
$$

The scaled inverse chi-square distribution is more typically used in a Bayesian analysis, where the rate parameter, $ \beta $ (which equals 1/2 under a chi-square), is replaced by $ \beta=\sigma_{0}^{2}/2 $ , making the resulting pdf

$$
p (x \mid n) \propto x ^ {- (n / 2 + 1)} e ^ {- \sigma_ {0} ^ {2} / (2 x)}
$$

where the $ 1 / ( 2 x ) $ term in the exponential is replaced by a $ \sigma_{0}^{2} /( 2 x ) $ term. The scaled inverse chi-square distribution thus involves two parameters $ (\sigma_{0}^{2} $ and n), and is denoted by $ \chi_{(n,\sigma_{0}^{2})}^{-2} $ or $ \mathrm{SI}-\chi^{2}(n,\sigma_{0}^{2}) $ . Note that if

$$
x \sim \chi_ {(n, \sigma_ {0} ^ {2})} ^ {- 2}, \quad \mathrm {t h e n} \quad \sigma_ {0} ^ {2} x \sim \chi_ {n} ^ {- 2}
$$

which shows that $ \sigma_{0}^{2} $ is a scaling factor on a standard $ (\beta=1/2) $ inverse chi-square.

## Gaussian Likelihood With Unknown Variance: Scaled Inverse- $ \chi^{2} $ Priors

Suppose data are drawn from a normal distribution with a known mean, $ \mu $ , but unknown variance, $ \sigma^{2} $ . The resulting likelihood function can be expressed as

$$
\ell \left(\sigma^ {2} \mid \mathbf {x}, \mu\right) \propto \left(\sigma^ {2}\right) ^ {- n / 2} \exp \left(- \frac {n S ^ {2}}{2 \sigma^ {2}}\right)
$$

where

$$
S ^ {2} = \frac {1}{n} \sum_ {i = 1} ^ {n} \left(x _ {i} - \mu\right) ^ {2}
$$

Notice that since we condition on x and $ \mu $ (i.e., their values are known), $ S^{2} $ is a constant. Further observe that, as a function of the unknown variance, $ \sigma^{2} $ , the likelihood is proportional to a scaled inverse $ \chi^{2} $ distribution (Equation A2.30a). If we take the prior for the unknown variance also as a scaled inverse $ \chi^{2} $ with hyperparameters $ \nu_{0} $ and $ \sigma_{0}^{2} $ , the posterior becomes

$$
\begin{array}{l} p \left(\sigma^ {2} \mid \mathbf {x}, \mu\right) \propto \left(\sigma^ {2}\right) ^ {- n / 2} \exp \left(- \frac {n S ^ {2}}{2 \sigma^ {2}}\right) \left(\sigma^ {2}\right) ^ {- \nu_ {0} / 2 - 1} \cdot \exp \left(- \frac {\sigma_ {0} ^ {2}}{2 \sigma^ {2}}\right) \\ = \left(\sigma^ {2}\right) ^ {- \left(n + \nu_ {0}\right) / 2 - 1} \exp \left(- \frac {n S ^ {2} + \sigma_ {0} ^ {2}}{2 \sigma^ {2}}\right) \\ \end{array}
$$

Equation A2.30a shows the resulting posterior is also a scaled inverse $ \chi^{2} $ distribution with parameters $ \nu_{n}=(n+\nu_{0}) $ and $ \sigma_{n}^{2}=(n S^{2}+\sigma_{0}^{2}). $ Hence,

$$
\text {t h e p r i o r} \sigma^ {2} \sim \chi_ {\nu_ {0}, \sigma_ {0} ^ {2}} ^ {- 2} \quad \text {y i e l d s t h e p o s t e r i o r} \quad \sigma^ {2} | (\mathbf {x}, \mu) \sim \chi_ {\nu_ {n}, \sigma_ {n} ^ {2}} ^ {- 2}
$$

## Student's t Distribution

The final distribution needed for a Bayesian analysis of a Gaussian likelihood is the t (or Student's t) distribution. Suppose that $ x_{i}\sim N(\mu,\sigma^{2}) $ , so for n independent draws, $ \overline{x}\sim N(\mu,\sigma^{2}/n). $ This implies that $ (\overline{x}-\mu) / \sqrt{\sigma^{2}/n}\sim U $ , where $ U\sim N(0,1) $ denotes a unit normal. Likewise, the sample variance, $ \operatorname{Var}(x) $ , follows a scaled chi-square distribution, with $ \operatorname{Var}(x)\sim(n-1)\sigma^{2}\chi_{n-1}^{2} $ (LW Equation A5.14c). When the estimated variance, $ \operatorname{Var}(x) $ , is used in place of the true variance, $ \sigma^{2} $ , the quantity $ (\overline{x}-\mu) / \sqrt{\operatorname{Var}(x)/n} $ follows a t distribution with n-1 degrees of freedom, giving rise to the very familiar t-test. Notice that

$$
t _ {n - 1} = \left(\frac {\bar {x} - \mu}{\sigma / \sqrt {n}}\right) \left(\frac {1}{\sqrt {\operatorname {V a r} (\mathrm {x}) / \sigma^ {2}}}\right) = \frac {U}{\sqrt {\chi_ {n - 1} ^ {2} / (n - 1)}}
$$

Thus, a $ t_{\nu} $ random variable follows the distribution of a unit normal divided by the square root of a chi-square with $ \nu $ degrees of freedom,

$$
t _ {\nu} = \frac {U}{\sqrt {\chi_ {\nu} ^ {2} / \nu}}
$$

Note that $ E(\chi_{\nu}^{2})=\nu $ , so $ E(\chi_{\nu}^{2} / \nu)=1 $ . Relative to a normal, a t distribution is more peaked and has heavier tails, and this kurtosis becomes more pronounced as $ \nu $ decreases. Indeed, the tails fall off sufficiently slowly that a t random variable with two degrees of freedom has an infinite variance, while a t with four (or fewer) degrees of freedom has an infinite fourth moment. The coefficient of kurtosis (LW Equation 2.12a) for a t with $ \nu>4 $ degrees of freedom is $ k_{4}=6 / (\nu-4) $ , which approaches the value (zero) for a normal random variable for large values of $ \nu $ . For $ \nu>30 $ , the t essentially becomes a unit normal distribution.

As with a unit normal, one can also add scale and location to a standard $ t_{\nu} $ -distributed random variable, thus generating a three-parameter family of distributions,

$$
t _ {\nu} (\mu , \sigma) = \mu + \sigma \cdot t _ {\nu}
$$

The resulting mean and variance this distribution are

$$
E \left[ t _ {\nu} (\mu , \sigma) \right] = \mu \quad \mathrm {a n d} \quad \sigma^ {2} \left[ t _ {\nu} (\mu , \sigma) \right] = \sigma^ {2} \frac {\nu}{\nu - 2} \quad \mathrm {f o r} \nu > 2
$$

Hence, the choice of $ \mu $ and $ \sigma $ control, respectively, the location and scale (uncertainty about the location), while $ \nu $ controls the kurtosis, with heavy tails for values of $ \nu $ that are small and little kurtosis for $ \nu > 2 0 $ . The resulting probability density function thus becomes

$$
p (x \mid \nu , \mu , \sigma) = \frac {\Gamma ([ \nu + 1 ] / 2)}{\Gamma (\nu / 2) \sigma \sqrt {\pi \nu}} \left[ 1 + \frac {1}{\nu} \left(\frac {x - \mu}{\sigma}\right) ^ {2} \right] ^ {- (\nu + 1) / 2}
$$

The role of the t distribution in Bayesian statistics is twofold. First, it is often used as a more robust prior, as its heavier tails may better account for outliers. Using a t distribution with low degrees of freedom (often $ \nu=5 $ ) offers a prior that is similar to a normal but allows for more frequent extreme values. The second scenario is that the marginal posterior for $ \mu $ of a Gaussian likelihood with a normal prior on the mean and an inverse chi-square prior on the variance is a t distribution. This arises after the joint posterior is integrated over all possible $ \sigma^{2} $ values (i.e., over an inverse chi-square).

## General Gaussian Likelihood: Unknown Mean and Variance

If we put all these pieces together, the posterior density for draws from a normal with unknown mean and variance is obtained as follows. First, we write the joint prior by conditioning on the variance,

$$
p \left(\mu , \sigma^ {2}\right) = p \left(\mu \mid \sigma^ {2}\right) \cdot p \left(\sigma^ {2}\right)
$$

<div align="center">

Table A2.2 Conjugate priors for common likelihood functions. If one uses the distribution family of the conjugate prior with its paired likelihood function, then the resulting posterior is in the same distribution family as the prior (albeit, of course, with different parameters).

</div>

<table border="1"><tr><td>Likelihood</td><td>Conjugate prior</td><td>Equation</td></tr><tr><td>Binomial</td><td>Beta</td><td>A2.38a</td></tr><tr><td>Multinomial</td><td>Dirichlet</td><td>A2.37b</td></tr><tr><td>Poisson</td><td>Gamma</td><td>A2.27a</td></tr><tr><td>Normal</td><td></td><td></td></tr><tr><td>$\mu$ unknown，$\sigma^{2}$ known</td><td>Normal</td><td>A2.18a</td></tr><tr><td>$\mu$ known，$\sigma^{2}$ unknown</td><td>Inverse chi-square</td><td>A2.30a</td></tr><tr><td>Multivariate normal</td><td></td><td></td></tr><tr><td>$\mu$ unknown，V known</td><td>Multivariate normal</td><td>LW8.24</td></tr><tr><td>$\mu$ known，V unknown</td><td>Inverse-Wishart</td><td>A2.41</td></tr></table>

As above, we assume a scaled inverse chi-square distribution for the variance and, conditioned on the variance, a Gaussian prior for the mean with hyperparameters of $ \mu_{0} $ and $ \sigma^{2} / \kappa_{0} $ , namely,

$$
\sigma^ {2} \sim \chi_ {\nu_ {0}, \sigma_ {0} ^ {2}} ^ {- 2} \quad \text {a n d} \quad \mu | \sigma^ {2} \sim \mathrm {N} \left(\mu_ {0}, \frac {\sigma^ {2}}{\kappa_ {0}}\right)
$$

We write the variance for the conditional mean prior in this way because $ \sigma^{2} $ is known (as we condition on it) and we scale $ \sigma^{2} $ by the hyperparameter, $ \kappa_{0} $ . The resulting marginal posterior becomes

$$
\sigma^ {2} \mid \mathbf {x} \sim \chi_ {\nu_ {n}, \sigma_ {n} ^ {2}} ^ {- 2} \quad \mathrm {a n d} \quad \mu \mid \mathbf {x} \sim \mathrm {t} _ {\nu_ {n}} \left(\mu_ {n}, \frac {\sigma_ {n} ^ {2}}{\kappa_ {n}}\right)
$$

where $ \mathrm{t}_{n}(\mu ,\sigma^{2}) $ denotes a t distribution with n degrees of freedom, mean $ \mu $ , and scale parameter $ \sigma^{2} $ , and where

$$
\nu_ {n} = \nu_ {0} + n, \quad \kappa_ {n} = \kappa_ {0} + n
$$

$$
\mu_ {n} = \mu_ {0} \frac {\kappa_ {0}}{\kappa_ {n}} + \bar {x} \frac {n}{\kappa_ {n}} = \mu_ {0} \frac {\kappa_ {0}}{\kappa_ {0} + n} + \bar {x} \frac {n}{\kappa_ {0} + n}
$$

$$
\sigma_ {n} ^ {2} = \frac {1}{\nu_ {n}} \left(\nu_ {0} \sigma_ {0} ^ {2} + \sum_ {i = 1} ^ {n} \left(x _ {i} - \bar {x}\right) ^ {2} + \frac {\kappa_ {0} n}{\kappa_ {n}} \left(\bar {x} - \mu_ {0}\right) ^ {2}\right)
$$

## CONJUGATE PRIORS

The use of a prior density that conjugates the likelihood allows us to develop analytic expressions of the posterior density. As we will see in Appendix 3, this is critical in developing Gibbs samplers for problems of interest. Table A2.2 summarizes the conjugate priors for several common likelihood functions, with the various families of distributions discussed below.

## The Beta and Dirichlet Distributions

With a binomial, each trial (observation) has two possible outcomes and the likelihood is a function of the sample size (number of trials), n, and a single success probability, p (as the two outcomes on any given trial have probabilities of p and 1-p). The generalization of this model is the multinomial distribution, where now each trial has k possible outcomes, and which requires k-1 success probabilities to describe the likelihood. In particular, for a total of n observations, the probability that $ n_{1} $ are in category 1, $ n_{2} $ in category 2, $ \cdots $ , and $ n_{k} $ in category k is

$$
p \left(n _ {1}, \dots n _ {k}\right) = \frac {n !}{n _ {1} ! n _ {2} ! \dots n _ {k} !} p _ {1} ^ {n _ {1}} \dots p _ {k} ^ {n _ {k}} \quad \mathrm {w h e r e} \quad \sum_ {i} n _ {i} = n \quad \mathrm {a n d} \quad \sum_ {i} p _ {i} = 1
$$

![](page=17,bbox=[418, 117, 714, 286])

<div align="center">

Figure A2.3 For $ \alpha=\beta=1 $ (long-dashed curve), the beta distribution is simply the uniform distribution over (0,1). The pdf for the beta distribution can also be U-shaped $ (\alpha=\beta=0.5; $ solid curve), unimodal $ (\alpha=2,\beta=5; $ short-dashed curve), or L-shaped $ (\alpha=10,\beta=1; $ dotted curve). Because the beta distribution is symmetric in $ \alpha $ and $ \beta $ , switching their parameter values generates a distribution of the same shape translated about 0.5.

</div>

The conjugate prior for the multinomial likelihood is the Dirichlet distribution. If we let $ \mathbf{x}=\left(x_{1},x_{2},\cdots,x_{k}\right) $ denote the k success probabilities, when pdf for $ \mathbf{x}\sim $ Dirichlet $ \left(\alpha_{1},\cdots,\alpha_{k}\right) $ is

$$
p \left(x _ {1}, \dots x _ {k} \mid \alpha_ {1}, \dots , \alpha_ {k}\right) = \frac {\Gamma \left(\alpha_ {0}\right)}{\Gamma \left(\alpha_ {1}\right) \cdots \Gamma \left(\alpha_ {k}\right)} x _ {1} ^ {\alpha_ {1} - 1} \dots x _ {k} ^ {\alpha_ {k} - 1}
$$

where

$$
\alpha_ {0} = \sum_ {i = 1} ^ {k} \alpha_ {i} \quad \mathrm {w i t h} \quad \alpha_ {i} > 0, \quad \mathrm {a n d} \quad \sum_ {i = 1} ^ {k} x _ {i} = 1 \quad \mathrm {w i t h} \quad 0 \leq x _ {i} \leq 1
$$

At first glance, this looks like the multinomial density function (with $ \alpha_{i}-1=n_{i} $ ). The difference is that the multinomial is calculated over a set of discrete random variables $ (n_{i}) $ , thus returning the expected probabilities for any vector of discrete numbers of counts (successes) in each category. Conversely, the Dirichlet treats an equivalent of the vector of outcomes (generalized to non-integers) as fixed and returns the continuous distribution for all possible configurations of the success parameters given this data, which means that the data $ (\alpha_{i}) $ is fixed, and the success parameters $ (x_{i}) $ are random. A few key moments of this distribution are

$$
\mu_ {x _ {i}} = \frac {\alpha_ {i}}{\alpha_ {0}}, \quad \sigma^ {2} \left(x _ {i}\right) = \frac {\alpha_ {i} \left(\alpha_ {0} - \alpha_ {i}\right)}{\alpha_ {0} ^ {2} \left(\alpha_ {0} + 1\right)}, \quad \mathrm {a n d} \quad \sigma \left(x _ {i}, x _ {j}\right) = - \frac {\alpha_ {i} \alpha_ {j}}{\alpha_ {0} ^ {2} \left(\alpha_ {0} + 1\right)}
$$

An important special case of the Dirichlet (for k=2 classes) is the beta distribution, whose pdf is given by

$$
p (x) = \frac {\Gamma (\alpha + \beta)}{\Gamma (\alpha) \Gamma (\beta)} x ^ {\alpha - 1} (1 - x) ^ {\beta - 1} \quad \mathrm {f o r} \quad 0 \leq x \leq 1, \quad \alpha , \beta > 0
$$

which has a mean and a variance of

$$
\mu = \frac {\alpha}{\alpha + \beta} \quad \mathrm {a n d} \quad \sigma^ {2} = \frac {\alpha \beta}{(\alpha + \beta) ^ {2} (\alpha + \beta - 1)}
$$

As Figure A2.3 illustrates, the beta distribution is extremely flexible, and can be flat, unimodal, U- , or L-shaped, depending on the choice of $ \alpha $ and $ \beta $.

## Wishart and Inverse-Wishart Distributions

The Wishart distribution can be thought of as the multivariate extension of the $ \chi^{2} $ distribution. Suppose $ \mathbf{x}_{1},\cdots,\mathbf{x}_{n} $ are independent and identically distributed vectors, with $ \mathbf{x}_{i}\sim \mathrm{MVN}_{k}(\mathbf{0},\mathbf{V}) $ . Using these n draws, and assuming that the mean is known to be zero, the resulting random $ (k\times k $ symmetric, positive definite) sample covariance matrix, W, is given by

$$
\mathbf {W} = \sum_ {i = 1} ^ {n} \mathbf {x} _ {i} \mathbf {x} _ {i} ^ {T} \sim W _ {n} (\mathbf {V})
$$

This sum is defined as a Wishart distribution with n degrees of freedom and a (matrix) parameter V. Recalling that the sum of n squared unit normals follows a $ \chi_{n}^{2} $ distribution, the Wishart is the extension to the multivariate normal. Indeed, for k=1 with $ \mathbf{V}=(1) $ , the Wishart is simply a $ \chi_{n}^{2} $ distribution, as $ \sum x_{i}^{2}\sim\chi_{n}^{2} $ , because $ x_{i}\sim N(0,1) $ .

The Wishart is the sampling distribution for covariance matrices (just like the $ \chi^{2} $ is associated with the distribution of a sample variance for data drawn from a normal; Chapter 11). The pdf of the Wishart distribution is

$$
p \left(\mathbf {W} \mid \mathbf {V}\right) = 2 ^ {- n k / 2} \pi^ {- k (k - 1) / k} | \mathbf {V} | ^ {- n / 2} | \mathbf {W} | ^ {(n + k + 1) / 2} \frac {\exp \left(- \frac {1}{2} \operatorname {t r} \left[ \mathbf {V} ^ {- 1} \mathbf {W} \right]\right)}{\prod_ {i = 1} ^ {k} \Gamma \left(\frac {n + 1 - i}{2}\right)}
$$

Recall that the trace (tr) of a matrix is just the sum of its diagonal elements, $ \operatorname{tr} (\mathbf{A})=\sum A_{ii} $ (Appendix 5). Odell and Feiveson (1966) presenteds an algorithm for generating random draws from the Wishart.

If $ \mathbf{Z}\sim\mathbf{W}_{n} (\mathbf{V}) $ , then $ \mathbf{Z}^{-1}\sim\mathbf{W}_{n}^{-1}\left(\mathbf{V}^{-1}\right) $ , where $ \mathbf{W}^{-1} $ denotes the inverse-Wishart distribution. The density function for an inverse-Wishart distributed random matrix, $ \mathbf{W} $ , is

$$
p \left(\mathbf {W} \mid \mathbf {V}\right) = 2 ^ {- n k / 2} \pi^ {- k (k - 1) / k} | \mathbf {V} | ^ {n / 2} | \mathbf {W} | ^ {- (n + k + 1) / 2} \frac {\exp \left(- \frac {1}{2} \operatorname {t r} \left[ \mathbf {V W} ^ {- 1} \right]\right)}{\prod_ {i = 1} ^ {k} \Gamma \left(\frac {n + 1 - i}{2}\right)}
$$

which is the distribution of the inverse of the sample covariance matrix.