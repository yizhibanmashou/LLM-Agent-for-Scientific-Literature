# Chapter 30 Textbook Mapping

## chapter30_001 · Measuring Multivariate Selection: Introduction

We have found that there are fundamental differences between the surviving birds and those eliminated, and we conclude that the birds which survived survived because they possessed certain structural characters, and that the birds which perished perished not through accident, but because they did not possess certain structural characters which would have enabled them to withstand the severity of the test imposed by nature; they were eliminated because they were unfit. Bumpus (1899)

While we have previously hinted at some of the features of multivariate selection (Chapters 13 and 20), we now start our formal discussion of selection on a vector of traits. As in Chapter 29, we distinguish between selection, the within-generation change in the (fitness-weighted) distribution of trait values and the response to selection, how the distribution of trait values changes across generations. Phenotypic correlations between traits within an individual influence within-generation changes, while genetic correlations (correlations among the breeding values for different traits within an individual) influence the between-generation response (Chapter 13). In particular, when a suite of traits is phenotypically correlated, simply observing the within-generation change in their means or variances is not sufficient to determine which ones are under selection.

To assess which traits are under selection, one must remove the effects of phenotypic correlations to separate direct selection from correlated selection. This is done by using partial regressions (linear for changes in the means and quadratic for changes in variances and covariances), and much of our focus here is on such fitness-trait regressions. Essentially all of the measures of phenotypic selection discussed here are multivariate extensions of the univariate measures introduced in Chapter 29. As these expressions are presented in terms of matrices and vectors, we rely rather heavily in places on matrix machinery (such as eigenvalues and eigenvectors, canonical decompositions, and, in a few places, matrix calculus). Appendix 5 discusses the mathematics of treating matrices as geometric objects, while Appendix 6 provides a brief refresher of important concepts and tools from the calculus of matrices (such as multidimensional derivatives and Taylor series).

The structure of this chapter is as follows: We first introduce the multivariate versions of selection differentials and gradients and their properties. Next, the geometry of quadratic regressions is examined in some detail, followed by discussions of multivariate nonparametric regressions and the strength of selection in natural populations. We conclude with some comments on unmeasured characters, the use of path analysis as an alternative (and often complementary) approach to the analysis of selection, and measures of multilevel selection. As was the case for Chapter 29, much of the discussion here centers around the landmark paper of Lande and Arnold (1983) and the very long shadow it has cast for the past three decades in the phenotypic selection literature. There is a healthy debate as to the robustness of conclusions from this approach, especially in terms of measures of nonlinear selection. A second concern is that the ordinary least-squares (OLS) solutions of the Lande-Arnold regression assume that fitness residuals are normally distributed and homoscedastic, which is clearly incorrect. We introduced these issues in a univariate setting in Chapter 29, and here we continue their discussion in the multivariate setting.

---

## chapter30_002 · Measuring Multivariate Selection: Introduction / SELECTION ON MULTIVARIATE PHENOTYPES: DIFFERENTIALS AND GRADIENTS

Chapter 29 described a variety of measures of univariate selection, with an emphasis on approximating the individual fitness function. In order to extend these methods to a vector of characters, we need to account for phenotypic correlations. To do so, we follow the multiple regression approach of Lande and Arnold (1983), which was initially suggested by Pearson (1903). The phenotype of an individual is now a vector, $ \mathbf{z} = (z_1, z_2, \cdots, z_n)^T $, of $ n $ character values. Suppose we denote the mean vector and covariance matrix of $ \mathbf{z} $ before selection by $ \mu $ and $ \mathbf{P} $, respectively, and by $ \mu^* $ and $ \mathbf{P}^* $ after selection (but before reproduction). As an aside, we use this phrase before reproduction, which often appears in the literature. This does not mean that reproductive aspects of fitness are ignored; rather, it simply means that we ignore any complications arising from genetic transmission to the next generation. Formally, this means that the fitness-weight distribution of the parents (which reflects reproductive success; Chapter 29) is taken as the distribution after selection (as opposed to the trait distribution seen in their offspring, which confounds selection with the cross-generational transmission). To avoid additional complications, we examine only a single episode of selection. Partitions over multiple episodes follow as fairly straightforward extensions of the univariate partitions discussed in Chapter 29 (Arnold and Wade 1984a; Wade and Kalisz 1989; McGlothlin 2010).

---

## chapter30_003 · Measuring Multivariate Selection: Introduction / Changes in the Mean Vector: The Directional Selection Differential Vector, S

**[推导 Derivation]**

The multivariate extension of the directional selection differential is the vector $$ \mathbf{S}=\mu^{*}-\mu $$ whose $i$th element is $S_i = \mu_i^* - \mu_i$, which is the differential for character $z_i$. (The fastidious reader might object to the nonstandard use of a capital bold letter, as opposed to the more standard bold lowercase letter, for a vector, but univariate selection theory uses $S$ for the selection differential, and we keep that notation here.) As with the univariate case, the Robertson-Price identity (Equation 6.10) holds, with $\mathbf{S} = \sigma(\mathbf{z}, w)$, meaning that the elements of $\mathbf{S}$ represent the covariance between character value and relative fitness, $S_i = \sigma(z_i, w)$. This immediately implies (from Equation 29.6b) that the opportunity for selection, $I$ (which is the population variance, $\sigma_w^2$, in relative fitness), bounds the range of $S_i$, and

> **Formula (30.1a)** · `30.1a` · source: `chapter30_block_006` · Changes in the Mean Vector: The Directional Selection Differential Vector, S
>
> $$ \frac{\left|S_{i}\right|}{\sigma_{z_{i}}}\leq\sqrt{I} $$


and

> **Formula (30.1b)** · `30.1b` · source: `chapter30_block_006` · Changes in the Mean Vector: The Directional Selection Differential Vector, S
>
> $$ \left|\bar{\imath}_{i}\right|\leq\sigma_{w} $$


Both show that selection intensity, $ \bar{\iota}_i = S_i / \sigma_{z_i} $, for any trait (with $ \sigma_{z_i}^2 $ being the phenotypic variance of trait $ i $) is bounded by the standard deviation of fitness. As illustrated in Figure 30.1, S confounds the direct effects of selection on a focal trait with the indirect effects from selection on phenotypically correlated characters. Suppose character 1 is under direct selection to increase in value while character 2 is not directly selected. If $ z_1 $ and $ z_2 $ are uncorrelated, there is no within-generation change in $ \mu_2 $ (the mean of $ z_2 $). However, if $ z_1 $ and $ z_2 $ are positively correlated, because individuals with large values of $ z_1 $ also tend to have large values of $ z_2 $, there will be a within-generation increase in $ \mu_2 $ ($ S_2 > 0 $). Conversely, if $ z_1 $ and $ z_2 $ are negatively correlated, selection to increase $ z_1 $ will result in a within-generation decrease in $ \mu_2 $ ($ S_2 < 0 $). Hence, a character not under selection can still experience a within-generation change resulting from selection on a phenotypically correlated trait (indirect selection or correlated selection). Fortunately, the directional selection gradient, $ \beta = \mathbf{P}^{-1} \mathbf{S} $, accounts for indirect selection resulting from phenotypic correlations (among the measured traits in the study), providing a less biased picture of the nature of directional selection acting on the component traits comprising z.

---

## chapter30_004 · Measuring Multivariate Selection: Introduction / The Directional Selection Gradient Vector, $ \beta $

**[推导 Derivation]**

As was discussed briefly in Chapters 13 and 20, $ \beta $, removes the effects of phenotypic correlations (among the set of traits being considered) because it is a vector of partial regression coefficients. From multiple regression theory (LW Chapter 8), the vector of partial regression coefficients for predicting the value of w, given a vector of observations z, is $ \mathbf{P}^{-1}\sigma(\mathbf{z},w) $, where $ \mathbf{P} $ is the covariance matrix of z and $ \sigma(\mathbf{z},w) $ is the vector of covariances between the elements of z and fitness, with an ith element of $ \sigma(z_i,w) $. Because $ \mathbf{S}=\sigma(\mathbf{z},w) $, it immediately follows that

> **Formula (30.2a)** · `30.2a` · source: `chapter30_block_008` · The Directional Selection Gradient Vector, $ \beta $
>
> $$ \mathbf{P}^{-1}\boldsymbol{\sigma}(\mathbf{z},w)=\mathbf{P}^{-1}\mathbf{S}=\boldsymbol{\beta} $$


is the vector of partial regression coefficients for the linear regression of relative fitness, w, on phenotypic value, z, namely,

> **Formula (30.2b)** · `30.2b` · source: `chapter30_block_008` · The Directional Selection Gradient Vector, $ \beta $
>
> $$ \begin{align*}w(\mathbf{z})=1+\sum\limits_{j=1}^n\beta_j(z_j-\mu_j)+e=1+\beta^T(\mathbf{z}-\boldsymbol{\mu})+e\end{align*} $$


Recalling the fact (LW Chapters 3 and 8) that the regression must pass through the means of both w and z (1 and $ \mu $, respectively), allows us to remove the intercept constant, a, in the regression. We could equivalently write Equation 30.2b as $ w(\mathbf{z}) = a + \beta^{T}\mathbf{z} + e $, where $ a = 1 - \beta^{T}\mu $.

**[推导 Derivation]**

The partial regression coefficient, $ \beta_j $, represents the change in $ w $ from a one-unit increase in $ z_j $ while holding all the other characters constant. It is important to note, however, that $ \beta $ accounts for the effects of phenotypic correlations only among the measured set of characters that comprise the elements of $ z $. Among the members of this set, a character under no directional selection has a value of $ \beta_j = 0 $. Because S = Pβ, we have

> **Formula (30.3)** · `30.3` · source: `chapter30_block_010` · The Directional Selection Gradient Vector, $ \beta $
>
> $$ \begin{align*}S_i=\sum\limits_{j=1}^n\beta_j\; P_{ij}=\beta_i\; P_{ii}+\sum\limits_{j\ne i}^n\beta_j\; P_{ij}\end{align*} $$


which illustrates that the directional selection differential for trait $i$ confounds direct selection on that character ($\beta_i$) with indirect contributions due to selection on phenotypically correlated characters ($\beta_j P_{ij} \neq 0$). These contributions are given, respectively, by the first and second terms in Equation 30.3.

**[推导 Derivation]**

Operationally, fitness regressions are usually computed using standardized variables,

> **Formula (30.4a)** · `30.4a` · source: `chapter30_block_011` · The Directional Selection Gradient Vector, $ \beta $
>
> $$ \begin{align*}z_{sd,i}=\frac{z_i-\mu_i}{\sigma_i}\end{align*} $$


with $ z_{sd,i} $ having a mean of zero and unit variance (this is often denoted by $ z_i' $ in the literature). As mentioned in Chapter 29, one could also mean-standardize $ (z_i/\mu_i) $, but when the term standardized variable is used in the evolutionary and ecological literature, it usually implies Equation 30.4a. The selection differential of the standardized variable is simply the selection intensity $ \bar{\tau} $ (Equation 13.6a), as $$ S_{sd,i}=\sigma(z_{sd,i},w)=\sigma(z_{i}/\sigma_{i},w)=\frac{\sigma(z_{i},w)}{\sigma_{i}}=\frac{S_{i}}{\sigma_{i}}=\bar{\imath}_{i} $$

**[推导 Derivation]**

The standardization given by Equation 30.4 can be expressed in matrix form as

> **Formula (30.4b)** · `30.4b` · source: `chapter30_block_012` · The Directional Selection Gradient Vector, $ \beta $
>
> $$ \mathbf{z}_{sd}=\mathbf{D}^{-1}(\mathbf{z}-\boldsymbol{\mu}) $$


where D is the diagonal matrix

> **Formula (30.4c)** · `30.4c` · source: `chapter30_block_012` · The Directional Selection Gradient Vector, $ \beta $
>
> $$ \mathbf{D}=\begin{pmatrix}{{{\sigma_{1}}}}&{{{0}}}&{{{\cdots}}}&{{{0}}} \\{{{0}}}&{{{\sigma_{2}}}}&{{{\cdots}}}&{{{0}}} \\{{{\vdots}}}&{{{\ddots}}}&{{{\vdots}}} \\{{{0}}}&{{{0}}}&{{{\cdots}}}&{{{\sigma_{n}}}}\end{pmatrix} $$


Equations 30.4b and 30.4c imply that the phenotypic covariance matrix $ (P_{sd}) $ for the standardized variables is simply the matrix of all pairwise correlations. Following our notation from Chapter 29, we denote selection gradients using variance-standardized variables by $ \beta_{sd,i} $, although they are often denoted by $ \beta_i' $ in the literature. When expressed with standardized variables, Equation 30.2b becomes $$ \boldsymbol{w}(\mathbf{z}_{s d})=1+\boldsymbol{\beta}_{s d}^{T}\mathbf{z}_{s d}+e,\quad\mathrm{w h e r e}\quad\boldsymbol{\beta}_{s d}=\mathbf{P}_{s d}^{-1}\mathbf{S}_{s d} $$

Here $ \beta_{sd,i} $ is the expected change in relative fitness given a change of one standard deviation in trait $ z_i $ when all of the other measured trait values (i.e., the elements of $ \mathbf{z} $) are held constant.

The total strength of directional selection on the set of measured characters is a quantity of interest, and is given by the norm of $ \beta $, where (Equation A5.1a) $$ ||\beta||=\sqrt{\beta^{T}\beta}=\sqrt{\sum\beta_{i}^{2}} $$

Morrissey (2014b) noted that $ E[\|\beta\|] \geq \|\beta\| $, as the values of $ \beta_i $ are measured with error, and such error carries over into the norm. Suppose $ k $ independent traits are measured, where $ \widehat{\beta}_i \sim N(\beta, \sigma^2) $, so that each $ \beta_i $ is independent and identically distributed, with sampling error $ \sigma^2 $. In this case, $ E[\|\widehat{\beta}\|] = \sqrt{k(\beta + \sigma^2)} > \|\beta\| = \sqrt{k\beta} $. Given that the standard error of an estimate of $ \beta $ is often of the same order as the estimate itself (Morrissey 2014b), the total strength of selection can be considerably overestimated by $ \|\beta\| $.

We also remark in passing that the Henshaw-Zemel (2017) distributional selection differential (a nonparametric measure of the total shift in a distribution following selection; Equation 29.15a) can be generalized into a multivariate version that also partitions trait selection into direct and indirect effects; see their paper for details.

**[示例 Example]**

> **Example 30.1** · ref: `30.1` · source: `chapter30_004.json` · blocks 10–10
>
> Example 30.1. The original application of the Lande-Arnold regression was on a population of one-spotted stink bugs (Euschistus varioliarius), collected along the shore of Lake Michigan after a storm (Lande and Arnold 1983), an insect equivalent of the classic Bumpus (1899) study. Of the 94 individuals collected (legend has it that some were deposited into an open adult beverage container, in a truly selfless act of science), 39 were alive. All individuals were measured for four characters: head (Hd) and thorax (Tx) width and scutellum (Sc) and forewing (Fw) length. The data were then logarithmically transformed to more closely approximate normality, and the resulting log-transformed variables were variance-standardized. Selection differentials were calculated as the difference between the trait means among those bugs that survived and the total sample (dead or alive). Because these selection differentials were scaled in standard deviations, they correspond to selection intensities ($ \bar{i} $; Equation 13.6a). The resulting vector of standardized selection differentials and correlation matrix were $$ \mathbf{S}_{sd}=\begin{pmatrix}\overline{\imath}_{Hd}\\\overline{\imath}_{Tx}\\\overline{\imath}_{Sc}\\\overline{\imath}_{Fw}\end{pmatrix}=\begin{pmatrix}-0.11\\-0.06\\-0.28^{*}\\-0.43^{**}\end{pmatrix}\quad\mathbf{P}_{sd}=\begin{pmatrix}1.00&0.72&0.50&0.60\\0.72&1.00&0.59&0.71\\0.50&0.59&1.00&0.62\\0.60&0.71&0.62&1.00\end{pmatrix} $$ where $ * $ and $ ** $ denote 5% and 1% significance for the elements in $ S_{sd} $. Hence, $$ \boldsymbol{\beta}_{s d}=(\mathbf{P}_{s d})^{-1}\mathbf{S}_{s d}=\begin{pmatrix}1.00&0.72&0.50&0.60\\0.72&1.00&0.59&0.71\\0.50&0.59&1.00&0.62\\0.60&0.71&0.62&1.00\end{pmatrix}^{-1}\begin{pmatrix}-0.11\\-0.06\\-0.28\\-0.43\end{pmatrix}=\begin{pmatrix}0.02\\0.53^{**}\\-0.16\\-0.72^{**}\end{pmatrix} $$
> 
> The selection differentials for scutellum and wing length were both significantly different from zero, while the only significant gradients were for thorax and wing length. Hence, while the within-generation change in thorax length was negative (but not significantly different from zero), in reality there was strong direct selection to increase thorax length. An increase of one standard deviation in thorax length increases relative fitness by $ \beta_{sd} = 0.53 $ (i.e., 53%), while an increase of one standard deviation in wing length reduces fitness by 72%.


---

## chapter30_005 · Measuring Multivariate Selection: Introduction / Directional Gradients, Fitness Surface Geometry, and Selection Response

Consider a scalar-valued function, $f(\mathbf{x})$, whose argument is a vector, $\mathbf{x} = (x_1, \cdots, x_n)^T$. Recall from vector calculus (Appendix 6) that the gradient vector, $\nabla_{\mathbf{x}} f(\mathbf{x})$, of $f$ with respect to $\mathbf{x}$ is defined as $$ \nabla_{\mathbf{x}}f(\mathbf{x})=\begin{pmatrix}\partial f/\partial x_{1}\\ \partial f/\partial x_{2}\\ \vdots\\ \partial f/\partial x_{n}\end{pmatrix} $$ namely, the vector of each partial of $f$ with respect to $x_{i}$, for $1 \leq i \leq n$. Further, recall that the gradient vector of a multivariate function points in the direction of change that will give the greatest (local) increase in $f$.

**[推导 Derivation]**

When phenotypes are multivariate normal, $ \beta = \mathbf{P}^{-1} \mathbf{S} $ provides a convenient descriptor of the geometries, measured by gradients, of both the individual fitness surface, $ w(z) $, and the mean population landscape, $ \bar{W} $. Let us consider the landscape first. If we assume the z is multivariate normal (MVN), Example A6.3 shows that

> **Formula (30.5a)** · `30.5a` · source: `chapter30_block_021` · Directional Gradients, Fitness Surface Geometry, and Selection Response
>
> $$ \beta=\nabla\mu[\ln\overline{W}(\mu)]=\overline{W}^{-1}\cdot\nabla\mu[\overline{W}(\mu)] $$


which holds provided the fitnesses are frequency-independent (Lande 1976, 1979a). In this case, $ \beta $ is the gradient of mean population fitness with respect to the mean vector, $ \mu $, namely, the direction of steepest local increase in $ \overline{W} $. Hence, given the current population mean, $ \overline{W} $ increases most rapidly when the change in the vector of means $ (\Delta\mu) $ is in the direction given by $ \beta $. If the fitnesses are frequency-dependent (individual fitnesses change as the population mean changes, so that $ \nabla\mu[w(z)] \neq 0 $), then provided $ z $ is multivariate-normally distributed, Example A6.3 further shows that

> **Formula (30.5b)** · `30.5b` · source: `chapter30_block_021` · Directional Gradients, Fitness Surface Geometry, and Selection Response
>
> $$ \beta=\nabla_{\boldsymbol{\mu}}[\ln\overline{W}(\boldsymbol{\mu})]+\int\nabla_{\boldsymbol{\mu}}[w(\mathbf{z})]\varphi(\mathbf{z})\mathrm{d}\mathbf{z} $$


The integral in this expression accounts for the effects of frequency-dependence (the change in the individual fitness surface with respect to changes in the mean, $ \mu $) and $ \varphi $ is the MVN density function (Lande 1976). The vector $ \beta $ does not point in the direction of steepest increase in $ \overline{W} $ unless the second integral is zero.

**[推导 Derivation]**

Equation 30.5a shows the connection between the fitness landscape (the mean fitness surface) and $ \beta $ when z is MVN. A similar connection with $ \beta $ occurs (when z is also MVN) with the individual fitness surface. Here $ \beta $ as the average gradient of individual relative fitnesses (over the population distribution of phenotypes),

> **Formula (30.6)** · `30.6` · source: `chapter30_block_023` · Directional Gradients, Fitness Surface Geometry, and Selection Response
>
> $$ \beta=E_{\mathbf{Z}}\bigg[\nabla_{\mathbf{Z}}[w(\mathbf{z})]\bigg]=\int\nabla_{\mathbf{Z}}[w(\mathbf{z})]\varphi(\mathbf{z})\mathrm{d}\mathbf{z} $$


which holds provided $ z \sim MVN $ (Lande and Arnold 1983). To see this, we use integration by parts to yield $$ \int_{\mathbf{a}}^{\mathbf{b}}\nabla_{\mathbf{z}}[w(\mathbf{z})]\varphi(\mathbf{z})\mathrm{d}\mathbf{z}=w(\mathbf{z})\varphi(\mathbf{z})\bigg|_{\mathbf{a}}^{\mathbf{b}}-\int_{\mathbf{a}}^{\mathbf{b}}\nabla_{\mathbf{z}}[\varphi(\mathbf{z})]w(\mathbf{z})\mathrm{d}\mathbf{z} $$

If we take the limit as $\mathbf{a} \to -\infty$ and $\mathbf{b} \to \infty$, the first term on the righthand side vanishes as $\varphi(\mathbf{z}) \to 0$ when $\mathbf{z} \to \pm \infty$. If $\mathbf{z} \sim \mathrm{MVN}(\boldsymbol{\mu}, \mathbf{P})$, then Equation A6.2a gives $\nabla_{\mathbf{z}}[\varphi(\mathbf{z})] = -\varphi(\mathbf{z}) \mathbf{P}^{-1}(\mathbf{z} - \boldsymbol{\mu})$, implying $$ \begin{aligned}\int\nabla_{\mathbf{z}}[w(\mathbf{z})]\varphi(\mathbf{z})\mathrm{d}\mathbf{z}&=-\int\nabla_{\mathbf{z}}[\varphi(\mathbf{z})]w(\mathbf{z})\mathrm{d}\mathbf{z}=\int w(\mathbf{z})\varphi(\mathbf{z})\mathbf{P}^{-1}(\mathbf{z}-\boldsymbol{\mu})\mathrm{d}\mathbf{z}\\&=\mathbf{P}^{-1}\left(\int\mathbf{z}w(\mathbf{z})\varphi(\mathbf{z})\mathrm{d}\mathbf{z}-\boldsymbol{\mu}\int w(\mathbf{z})\varphi(\mathbf{z})\mathrm{d}\mathbf{z}\right)\\&=\mathbf{P}^{-1}\left(\boldsymbol{\mu}^{*}-\boldsymbol{\mu}\right)=\mathbf{P}^{-1}\mathbf{S}=\boldsymbol{\beta}\end{aligned} $$

The first integral in the second line corresponds to the mean trait value weighted by relative fitness ($ \mu^{*} $), while the second integral is the average value of relative fitness (1). Note from this derivation that Equation 30.6 holds regardless of whether fitness is frequency-dependent or -independent. This follows because the gradient was taken with respect to z, rather than with respect to the vector of means, $ \mu $.

Finally, while our focus has been on the role that $ \beta $ plays in measuring phenotypic selection, $ \beta $ also plays an important role in the response to selection. If we can assume that the breeder's equation holds, it is the only measure of phenotypic selection required to predict the response in the means, as the vector, R, of response (changes in means) is calculated by $ \mathbf{R} = \mathbf{G}\beta $ (Equation 13.26a). Cheverud (1984b) made the important point that although it is often assumed that a set of phenotypically correlated traits responds to selection in a coordinated fashion, this is not necessarily the case. Because $ \beta $ removes the effects of phenotypic correlations, phenotypic characters will only respond as a group if they are all under direct selection or if they are genetically correlated, a point discussed in detail in Volume 3.

---

## chapter30_006 · Measuring Multivariate Selection: Introduction / Changes in the Covariance Matrix: The Quadratic Selection Differential Matrix, C

**[推导 Derivation]**

Motivated by the univariate case wherein $ C = \sigma[w, (z - \mu)(z - \mu)] $, the multivariate quadratic selection differential is defined as the square $ (n \times n) $ matrix, C, whose elements are the covariances between all pairs of quadratic deviations, $ (z_i - \mu_i)(z_j - \mu_j) $, and relative fitness, w, namely,

> **Formula (30.7a)** · `30.7a` · source: `chapter30_block_027` · Changes in the Covariance Matrix: The Quadratic Selection Differential Matrix, C
>
> $$ C_{i j}=\sigma[w,(z_{i}-\mu_{i})(z_{j}-\mu_{j})] $$


As derived in Example 30.2, Lande and Arnold (1983) showed that

> **Formula (30.7b)** · `30.7b` · source: `chapter30_block_027` · Changes in the Covariance Matrix: The Quadratic Selection Differential Matrix, C
>
> $$ \mathbf{C}=\boldsymbol{\sigma}[w,(\mathbf{z}-\boldsymbol{\mu})(\mathbf{z}-\boldsymbol{\mu})^{T}]=\mathbf{P}^{*}-\mathbf{P}+\mathbf{S}\mathbf{S}^{T} $$


where P and $ P^{*} $ are, respectively, the phenotypic covariance matrices before- and after-selection. If no quadratic selection is acting, the covariance between each quadratic deviation and fitness is zero, and with C = 0. In this case, Equation 30.7b returns the within-generation change in P resulting from selection as

> **Formula (30.7c)** · `30.7c` · source: `chapter30_block_027` · Changes in the Covariance Matrix: The Quadratic Selection Differential Matrix, C
>
> $$ P_{ij}^{*}-P_{ij}=-S_{i}S_{j} $$


This demonstrates that the $S_i S_j$ term corrects $C_{ij}$ for the change in covariance caused by directional selection alone. This expression is the multivariate extension of the condition $\sigma^2(z^*) - \sigma^2(z) = P^* - P = -S^2$ for a single trait (Equation 29.16a); the latter expression follows as a special case ($i = j$) for Equation 30.7c.

**[示例 Example]**

> **Example 30.2** · ref: `30.2` · source: `chapter30_006.json` · blocks 2–2
>
> Example 30.2. We wish to show that $ \mathbf{P}^* - \mathbf{P} = \sigma[w(\mathbf{z}), (\mathbf{z} - \boldsymbol{\mu})(\mathbf{z} - \boldsymbol{\mu})^T] - \mathbf{S} \mathbf{S}^T $, which implies Equation 30.7b. From the definition of the variance-covariance matrix,
> 
> > **Formula (30.8a)** · `30.8a` · source: `chapter30_block_029` · Changes in the Covariance Matrix: The Quadratic Selection Differential Matrix, C
> >
> > $$ \mathbf{P}=E\left[\left(\mathbf{z}-\boldsymbol{\mu}\right)\left(\mathbf{z}-\boldsymbol{\mu}\right)^{T}\right]=\int\left(\mathbf{z}-\boldsymbol{\mu}\right)\left(\mathbf{z}-\boldsymbol{\mu}\right)^{T}p(\mathbf{z})\mathrm{d}\mathbf{z} $$
> 
> 
> > **Formula (30.8b)** · `30.8b` · source: `chapter30_block_029` · Changes in the Covariance Matrix: The Quadratic Selection Differential Matrix, C
> >
> > $$ \mathbf{P}^{*}=E\left[\left(\mathbf{z}^{*}-\boldsymbol{\mu}^{*}\right)\left(\mathbf{z}^{*}-\boldsymbol{\mu}^{*}\right)^{T}\right]=\int\left(\mathbf{z}-\boldsymbol{\mu}^{*}\right)\left(\mathbf{z}-\boldsymbol{\mu}^{*}\right)^{T}\boldsymbol{p}^{*}\left(\mathbf{z}\right)\mathrm{d}\mathbf{z} $$
> 
> 
> where $ p^{*}(\mathbf{z}) = w(\mathbf{z}) p(\mathbf{z}) $ is the distribution of $ \mathbf{z} $ after selection (but before reproduction). If we note that $ \mu^* = \mu + \mathbf{S} $, the integrated expression in Equation 30.8b can be written as
> 
> > **Formula (30.8c)** · `30.8c` · source: `chapter30_block_029` · Changes in the Covariance Matrix: The Quadratic Selection Differential Matrix, C
> >
> > $$ \begin{aligned}(\mathbf{z}-\boldsymbol{\mu}^{*})(\mathbf{z}-\boldsymbol{\mu}^{*})^{T}&=(\mathbf{z}-\boldsymbol{\mu}-\mathbf{S})(\mathbf{z}-\boldsymbol{\mu}-\mathbf{S})^{T}\\&=(\mathbf{z}-\boldsymbol{\mu}-\mathbf{S})([\mathbf{z}-\boldsymbol{\mu}]^{T}-\mathbf{S}^{T})\\&=(\mathbf{z}-\boldsymbol{\mu})(\mathbf{z}-\boldsymbol{\mu})^{T}-(\mathbf{z}-\boldsymbol{\mu})\mathbf{S}^{T}-\mathbf{S}\left(\mathbf{z}-\boldsymbol{\mu}\right)^{T}+\mathbf{S}\mathbf{S}^{T}\end{aligned} $$
> 
> 
> Because $ \int \mathbf{z} \, p^*(\mathbf{z}) \, \mathrm{d}\mathbf{z} = \mu^* $ and $ \int p^*(\mathbf{z}) \, \mathrm{d}\mathbf{z} = 1 $, then $$ \int(\mathbf{z}-\boldsymbol{\mu})\mathbf{S}^{T}\mathbf{\alpha}p^{*}(\mathbf{z})\mathrm{d}\mathbf{z}=\int\left[\mathbf{z}p^{*}(\mathbf{z})\right]\mathbf{S}^{T}\mathrm{d}\mathbf{z}-\boldsymbol{\mu}\mathbf{S}^{T}\int p^{*}(\mathbf{z})\mathrm{d}\mathbf{z}=(\boldsymbol{\mu}^{*}-\boldsymbol{\mu})\mathbf{S}^{T}=\mathbf{S}\mathbf{S}^{T} $$ $$ \[\int\mathbf{S}(\mathbf{z}-\boldsymbol{\mu})^{T}\mathbf{\Phi}\mathbf{\Phi}\mathbf{\Phi}\mathbf{\Phi}\mathbf{\ $$ $$ \int\mathbf{S}\mathbf{S}^{T}\mathbf{\nabla}p^{*}(\mathbf{z})\mathrm{d}\mathbf{z}=\mathbf{S}\mathbf{S}^{T} $$
> 
> Substituting these results into Equation 30.8b yields
> 
> > **Formula (30.8d)** · `30.8d` · source: `chapter30_block_030` · Changes in the Covariance Matrix: The Quadratic Selection Differential Matrix, C
> >
> > $$ \begin{aligned}\mathbf{P}^{*}&=\int\left(\mathbf{z}-\boldsymbol{\mu}\right)\left(\mathbf{z}-\boldsymbol{\mu}\right)^{T}\boldsymbol{w}(\mathbf{z})\boldsymbol{p}(\mathbf{z})\mathrm{d}\mathbf{z}-\mathbf{S}\mathbf{S}^{T}-\mathbf{S}\mathbf{S}^{T}+\mathbf{S}\mathbf{S}^{T}\\&=E\left[\boldsymbol{w}(\mathbf{z})\cdot\left(\mathbf{z}-\boldsymbol{\mu}\right)\left(\mathbf{z}-\boldsymbol{\mu}\right)^{T}\right]-\mathbf{S}\mathbf{S}^{T}\end{aligned} $$
> 
> 
> Because $ E[w(\mathbf{z})] = 1 $, we can write $ \mathbf{P} = E[w(\mathbf{z})] \cdot \mathbf{P} $. Using the definition of $ \mathbf{P} $, $$ \begin{aligned}\mathbf{P}^{*}-\mathbf{P}&=E\left[w(\mathbf{z})\cdot(\mathbf{z}-\boldsymbol{\mu})\left(\mathbf{z}-\boldsymbol{\mu}\right)^{T}\right]-\mathbf{S}\mathbf{S}^{T}-E[w(\mathbf{z})]\cdot E\left[(\mathbf{z}-\boldsymbol{\mu})\left(\mathbf{z}-\boldsymbol{\mu}\right)^{T}\right]\\&=\sigma\left[w(\mathbf{z}),(\mathbf{z}-\boldsymbol{\mu})(\mathbf{z}-\boldsymbol{\mu})^{T}\right]-\mathbf{S}\mathbf{S}^{T}\quad(30.8e\end{aligned} $$ with the last equality following from the definition of a covariance, $ \sigma(x,y) = E(x \cdot y) - E(x)E(y) $. As was the case for S, the fact that $ C_{ij} $ is a covariance immediately allows us to bound its range using the opportunity for selection (Chapter 29). Because $ \sigma^2(x, y) \leq \sigma^2(x) \sigma^2(y) $,
> 
> > **Formula (30.9a)** · `30.9a` · source: `chapter30_block_030` · Changes in the Covariance Matrix: The Quadratic Selection Differential Matrix, C
> >
> > $$ C_{i j}^{2}\leq\sigma^{2}(w)\sigma^{2}[(z_{i}-\mu_{i})(z_{j}-\mu_{j})]=I\sigma^{2}[(z_{i}-\mu_{i})(z_{j}-\mu_{j})] $$
> 
> 
> When $ z_{i} $ and $ z_{j} $ are bivariate-normal, then (Kendall and Stuart 1983),
> 
> > **Formula (30.9b)** · `30.9b` · source: `chapter30_block_031` · Changes in the Covariance Matrix: The Quadratic Selection Differential Matrix, C
> >
> > $$ \sigma^{2}[(z_{i}-\mu_{i})(z_{j}-\mu_{j})]=P_{i j}^{2}+P_{i i}P_{j j}=P_{i j}^{2}(1+\rho_{i j}^{-2}) $$
> 
> 
> where $ \rho_{ij} $ is the phenotypic covariance between $ z_{i} $ and $ z_{j} $. Hence, for Gaussian-distributed phenotypes,
> 
> > **Formula (30.10)** · `30.10` · source: `chapter30_block_031` · Changes in the Covariance Matrix: The Quadratic Selection Differential Matrix, C
> >
> > $$ \left|\frac{C_{ij}}{P_{ij}}\right|\leq\sqrt{I}\sqrt{1+\rho_{ij}^{-2}} $$
> 
> 
> which is a variant of the original bound based on I, as suggested by Arnold (1986). Note that when $ i = j $, $ \rho_{ii} = 1 $, and we recover Equation 29.18c.


---

## chapter30_007 · Measuring Multivariate Selection: Introduction / The Quadratic Selection Gradient Matrix, $ \gamma $

**[推导 Derivation]**

Like the directional selection differential vector, S, the quadratic selection differential, C, confounds the effects of direct selection with selection on phenotypically correlated characters. As was the case with S, these indirect effects can also be removed by a regression. Consider the quadratic regression of relative fitness as a function of phenotypic value,

> **Formula (30.11a)** · `30.11a` · source: `chapter30_block_032` · The Quadratic Selection Gradient Matrix, $ \gamma $
>
> $$ w(\mathbf{z})=a+\sum_{j=1}^{n}b_{j}z_{j}+\frac{1}{2}\sum_{j=1}^{n}\sum_{k=1}^{n}\gamma_{jk}\left(z_{j}-\mu_{j}\right)(z_{k}-\mu_{k}) $$


> **Formula (30.11b)** · `30.11b` · source: `chapter30_block_032` · The Quadratic Selection Gradient Matrix, $ \gamma $
>
> $$ =a+\mathbf{b}^{T}\mathbf{z}+\frac{1}{2}(\mathbf{z}-\boldsymbol{\mu})^{T}\boldsymbol{\gamma}(\mathbf{z}-\boldsymbol{\mu}) $$


**[推导 Derivation]**

Using multiple regression theory, Lande and Arnold (1983) showed that when $ z \sim MVN $, the matrix, $ \gamma $, of quadratic partial regression coefficients is given by

> **Formula (30.12)** · `30.12` · source: `chapter30_block_033` · The Quadratic Selection Gradient Matrix, $ \gamma $
>
> $$ \gamma=\mathbf{P}^{-1}\boldsymbol{\sigma}[w,(\mathbf{z}-\boldsymbol{\mu})(\mathbf{z}-\boldsymbol{\mu})^{T}]\mathbf{P}^{-1}=\mathbf{P}^{-1}\mathbf{C}\mathbf{P}^{-1} $$


**[推导 Derivation]**

This is the quadratic selection gradient, and (like $ \beta $) it removes the effects of phenotypic correlations (among the measured traits), thus providing a more accurate picture of how selection is operating on the multivariate phenotype. As we saw in the univariate case (Chapter 29), the vector of linear coefficients (b) for the quadratic regression need not equal the vector of partial regression coefficients ($ \beta $) that is obtained by assuming only a linear regression (Equation 30.2b). Equation 29.28a showed (for the univariate case) that if the phenotypic distribution is skewed, the linear term (b) in the quadratic regression is a function of both S and C, while the linear term in a linear regression ($ \beta $) is only a function of S. When phenotypes are multivariate normal, the skew is zero, and $ \mathbf{b} = \beta $ (Lande and Arnold 1983), which recovers the multivariate version of the Pearson-Lande-Arnold regression,

> **Formula (30.13a)** · `30.13a` · source: `chapter30_block_034` · The Quadratic Selection Gradient Matrix, $ \gamma $
>
> $$ w(\mathbf{z})=a+\beta^{T}\mathbf{z}+\frac{1}{2}(\mathbf{z}-\boldsymbol{\mu})^{T}\boldsymbol{\gamma}\left(\mathbf{z}-\boldsymbol{\mu}\right) $$


As with linear regression, one typically standardizes the trait values (Equation 30.4b), in which case Equation 30.13a can be written more compactly as

> **Formula (30.13b)** · `30.13b` · source: `chapter30_block_034` · The Quadratic Selection Gradient Matrix, $ \gamma $
>
> $$ w(\mathbf{z})=a+\beta_{sd}^{T}\mathbf{z}_{sd}+\frac{1}{2}\mathbf{z}_{sd}^{T}\gamma_{sd}\mathbf{z}_{sd} $$


Because the elements, $ \gamma_{ij} $, of the matrix $ \gamma $ (or its standardized counterpart, $ \gamma_{sd} $) are partial regression coefficients, they predict the change in expected fitness caused by changing the associated quadratic deviation while holding all other variables constant. Increasing the value of $ (z_j - \mu_j)(z_k - \mu_k) $ by one unit in such a way as to hold all other variables and all other pairwise combinations of characters constant is expected to change relative fitness by $ \gamma_{jk} $ for $ j \neq k $ and by $ \gamma_{jj}/2 $ if $ j = k $ (the difference arises because $ \gamma_{jk} = \gamma_{kj} $, so $ \gamma_{jk} $ appears twice in the regression unless $ j = k $). The coefficients of $ \gamma $ thus describe the nature of selection on quadratic deviations from the mean for both single characters and pairwise combinations of characters. A value of $ \gamma_{ii} < 0 $ implies that fitness decreases as $ z_i $ moves away (in either direction) from its phenotypic mean. As was discussed in Chapter 29, this is a necessary, but not sufficient, condition for ensuring stabilizing selection on character $ i $. As a result, the terms concave selection or concave fitness surface are often used to indicate this situation. The term stabilizing selection is restricted to situations where the fitness surface is concave and the population distribution is under a peak in the fitness surface. Similarly, $ \gamma_{ii} > 0 $ implies that fitness increases as $ i $ moves away from its mean (convex selection or convex fitness surface), which is again a necessary, but not sufficient condition, for disruptive selection. Turning to combinations of characters, nonzero values of $ \gamma_{jk} $ ($ j \neq k $) suggest the presence of correlational selection, with $ \gamma_{jk} > 0 $ suggesting selection for a positive phenotypic correlation between characters $ j $ and $ k $, and $ \gamma_{jk} < 0 $ suggesting selection for a negative phenotypic correlation between those characters. Although it appear to be straightforward to infer the overall nature of selection by looking at the various pairwise values of $ \gamma_{ij} $, this can result in an extremely misleading picture about the geometry of the fitness surface (e.g., Figure 30.3). We will discuss this problem and its solution shortly.

**[推导 Derivation]**

Finally, as we did for directional selection differentials, S (Equation 30.3), we can partition changes in the quadratic selection differential, C, into direct effects and indirect effects resulting from selection on phenotypically correlated traits. Solving for C by post- and pre-multiplying $ \gamma $ (Equation 30.12) by P gives C = P $ \gamma $P, which yields

> **Formula (30.14)** · `30.14` · source: `chapter30_block_035` · The Quadratic Selection Gradient Matrix, $ \gamma $
>
> $$ \begin{align*}C_{ij}=\sum\limits_{k=1}^n\sum\limits_{\ell=1}^n\gamma_{k\ell}P_{ik}P_{\ell j}\end{align*} $$


showing that within-generation changes in phenotypic covariance between traits i and j, as measured by $ C_{ij} $, are influenced by quadratic selection ($ \gamma_{kl} \neq 0 $) on pairs of characters, k and $ \ell $, that are correlated with i and j, specifically, when the product $ P_{ik} P_{\ell j} \neq 0 $.

---

## chapter30_008 · Measuring Multivariate Selection: Introduction / Quadratic Gradients, Fitness Surface Geometry, and Selection Response

**[推导 Derivation]**

As was the case for $ \beta $, when phenotypes are multivariate normal, $ \gamma $ also describes geometric features of both the individual fitness surface and the mean population fitness landscape. It provides a measure of the average curvature of the individual fitness surface, as

> **Formula (30.15a)** · `30.15a` · source: `chapter30_block_036` · Quadratic Gradients, Fitness Surface Geometry, and Selection Response
>
> $$ \gamma=\int\mathbf{H_{Z}}[w(\mathbf{z})]\varphi(\mathbf{z})d\mathbf{z} $$


where $ \mathbf{H}_{\mathbf{z}}[f] $ denotes the Hessian matrix of $ f $ with respect to $ \mathbf{z} $ (the matrix of all second partial derivatives; where $ H_{ij} = \partial^2 f / \partial z_i \partial z_j $) and is a multivariate measure of the quadratic (local) curvature of a function (Appendix A6). This result, due to Lande and Arnold (1983) can be obtained by an integration-by-parts argument similar to that used to obtain Equation 30.6, and holds for both frequency-dependent and frequency-independent fitnesses.

**[推导 Derivation]**

When fitnesses are frequency-independent (again provided $ z \sim MVN $), $ \gamma $ also provides a description of the curvature of the mean fitness landscape, with

> **Formula (30.15b)** · `30.15b` · source: `chapter30_block_037` · Quadratic Gradients, Fitness Surface Geometry, and Selection Response
>
> $$ \mathbf{H}\boldsymbol{\mu}[\ln\overline{W}(\boldsymbol{\mu})]=\gamma-\beta\boldsymbol{\beta}^{T} $$


This result is due to Lande (cited in Phillips and Arnold 1989), and it indicates that there are two sources for curvature in the mean fitness landscape: $ -\beta\beta^{T} $ from directional selection and $ \gamma $ from quadratic selection.

**[推导 Derivation]**

Finally, when the breeder’s equation holds, $ \gamma $ and $ \beta $ are sufficient to describe how phenotypic selection alters the additive-genetic covariance matrix. As we show in Volume 3, the additive-genetic covariance matrix, $ G^{*} $, following selection (but before reproduction) is calculated by

> **Formula (30.16)** · `30.16` · source: `chapter30_block_039` · Quadratic Gradients, Fitness Surface Geometry, and Selection Response
>
> $$ \mathbf{G}^{*}=\mathbf{G}\left(\gamma-\beta\beta^{T}\right)\mathbf{G}+\mathbf{G} $$


**[推导 Derivation]**

Equations 30.15–30.16 provide some insight into the connection between within-generation changes in phenotypic and genetic variances and the curvature of the fitness surface. To see such connections, we ignore the complications introduced by either phenotypic or genetic correlations. First, consider the within-generation change in the phenotypic variance. Equations 30.7b and 30.14 imply that

> **Formula (30.17a)** · `30.17a` · source: `chapter30_block_040` · Quadratic Gradients, Fitness Surface Geometry, and Selection Response
>
> $$ C_{ii}=\sigma^{2}(z_{i}^{*})-\sigma^{2}(z_{i})+S_{i}^{2}=\gamma_{ii}P_{ii}^{2}=\gamma_{ii}\sigma^{4}(z_{i}) $$


**[推导 Derivation]**

Hence, the within-generation change (denoted by $ \delta[x] $) in the phenotypic variance for trait i is

> **Formula (30.17b)** · `30.17b` · source: `chapter30_block_041` · Quadratic Gradients, Fitness Surface Geometry, and Selection Response
>
> $$ \delta\left[\sigma^{2}(z_{i})\right]=\gamma_{i i}P_{i i}^{2}-S_{i}^{2} $$


**[推导 Derivation]**

Thus, concave selection ($ \gamma_{ii} < 0 $) reduces the phenotypic variance of a trait, while convex selection ($ \gamma_{ii} > 0 $) increases it. The net effect of directional selection ($ S_i \neq 0 $) is to always reduce the variance, which means that undetected directional selection (i.e., S was not measured) can mask the effects of convex selection (e.g., Example 29.10) and enhance the effects of concave selection. Likewise, from Equation 30.16 (and assuming there are no genetic correlations), the within-generation change in the additive variance is

> **Formula (30.17c)** · `30.17c` · source: `chapter30_block_042` · Quadratic Gradients, Fitness Surface Geometry, and Selection Response
>
> $$ \delta\left[\sigma^{2}(A_{i})\right]=\left(\gamma_{i i}-\beta_{i}^{2}\right)\sigma^{4}(A_{i}) $$


As with the phenotypic variance, both concave and directional selection reduce the additive variance, while convex selection increases it (Chapter 16). Note that Equation 30.17c (as well as Equation 30.16) is the within-generation change in the additive genetic variance. Recombination and segregation in the selected individuals will change the additive variance in the offspring generation by reducing the disequilibrium generated by selection and by adding segregation variance (Chapters 16 and 24).

**[推导 Derivation]**

What about the effect of correlational selection ($ \gamma_{ij} \neq 0 $? Again, assuming all correlations (genetic and phenotypic) are (initially) zero, Equation 30.16 yields

> **Formula (30.18a)** · `30.18a` · source: `chapter30_block_043` · Quadratic Gradients, Fitness Surface Geometry, and Selection Response
>
> $$ C_{i j}=\sigma(z_{i}^{*},z_{j}^{*})-\sigma(z_{i},z_{j})+S_{i}S_{j}=2\gamma_{i j}P_{i i}P_{j j} $$


and the within-generation change in the phenotypic covariance becomes

> **Formula (30.18b)** · `30.18b` · source: `chapter30_block_043` · Quadratic Gradients, Fitness Surface Geometry, and Selection Response
>
> $$ \delta\left[\sigma(z_{i},z_{j})\right]=2\gamma_{i j}P_{i i}P_{j j}-S_{i}S_{j} $$


**[推导 Derivation]**

Positive values of $ \gamma_{ij} $ increase the phenotypic correlation, while negative values reduce it. Note that directional selection does not have a uniform effect: if both i and j are selected in the same direction, this decreases the phenotypic correlation, while if they are selected in opposite directions, this increases the correlation. Assuming no (initial) genetic correlations, Equation 30.16 gives the (within-generation) change in the genetic covariance as

> **Formula (30.18c)** · `30.18c` · source: `chapter30_block_044` · Quadratic Gradients, Fitness Surface Geometry, and Selection Response
>
> $$ \delta\left[\sigma(A_{i},A_{j})\right]=\left(2\gamma_{i j}-\beta_{i}\beta_{j}\right)\sigma^{2}(A_{i})\sigma^{2}(A_{j}) $$


Under the infinitesimal model, this change in the genetic covariance is due entirely to disequilibrium, which (for unlinked loci) is reduced by half in the offspring (Chapters 16 and 24).

The major features of linear and quadratic differentials and gradients discussed here are summarized in Table 30.1. Excellent overviews were also provided by Brodie et al. (1995) and Arnold et al. (2001).

---

## chapter30_009 · Measuring Multivariate Selection: Introduction / MULTIDIMENSIONAL QUADRATIC FITNESS REGRESSIONS

As noted for univariate cases, approximating the individual fitness function by a quadratic can give a very distorted view of the true fitness surface (Figure 29.10). We expect this distortion to be even greater in a multivariate setting. With this caveat in mind, quadratic fitness surfaces are still quite useful. One advantage is that a quadratic is the simplest surface allowing for curvature. Further, when phenotypes are normally distributed, the coefficients

**[Table]**

> **Table 30.1** · `30.1` · page 12 · source: `chapter30_009`
> Table 30.1 Analogous features of directional and quadratic differentials and gradients. Details are in the text.
>
> Changes in Means | Changes in Covariances
> --- | ---
> (Directional Selection) | (Quadratic Selection)
> Differentials measure the covariance between relative fitness and phenotype | $$ S_{i}=\sigma\left[w,z_{i}\right] $$<br><br>$$ C_{i j}=\sigma\left[w,(z_{i}-\mu_{i})(z_{j}-\mu_{j})\right] $$
> The opportunity for selection bounds the differential | $$ \frac{\left\|S_{i}\right\|}{\sigma(z_{i})}\leq\sqrt{I} $$<br><br>$$ \left\|\frac{C_{ij}}{P_{ij}}\right\|\leq\sqrt{I}\sqrt{1+\rho_{ij}^{-2}} $$
> for any distribution of z | $$ if\mathbf{z}\sim MVN $$
> Differentials confound direct and indirect selection | $$ \begin{array}{r l r l}&{\mathbf{S}=\boldsymbol{\mu}^{*}-\boldsymbol{\mu}=\mathbf{P}\boldsymbol{\beta}}&&{\quad\mathbf{C}=\mathbf{P}^{*}-\mathbf{P}+\mathbf{S}\mathbf{S}^{T}=\mathbf{P}\boldsymbol{\gamma}\mathbf{P}}\\ &{S_{i}=\sum_{j=1}^{n}\beta_{j}P_{i j}}&&{\quad C_{i j}=\sum_{k=1}^{n}\sum_{\ell=1}^{n}\gamma_{k\ell}P_{i k}P_{\ell j}}\end{array} $$
> Gradients measure the amount of direct selection | $$ \beta=\mathbf{P}^{-1}\mathbf{S} $$<br><br>$$ \gamma=\mathbf{P}^{-1}\mathbf{C}\mathbf{P}^{-1} $$
> Gradients describe the slope and curvature of the log mean fitness landscape, provided $ z \sim MVN $ and fitnesses are frequency-independent | $$ \beta_{i}=\frac{\partial\ln\overline{W}(\pmb{\mu})}{\partial\mu_{i}} $$<br><br>$$ \gamma_{ij}=\frac{\partial^{2}\ln\overline{W}(\boldsymbol{\mu})}{\partial\mu_{i}\partial\mu_{j}}+\beta_{i}\beta_{j} $$
> Gradients describe the average slope and average curvature of the individual fitness surface, provided $ z \sim MVN $ | $$ \beta_{i}=\int\frac{\partial w(\mathbf{z})}{\partial z_{i}}\varphi(\mathbf{z})\mathrm{d}\mathbf{z}\quad\gamma_{i j}=\int\frac{\partial^{2}w(\mathbf{z})}{\partial z_{i}\partial z_{j}}\varphi(\mathbf{z})\mathrm{d}\mathbf{z} $$
> Gradients appear as coefficients in fitness regressions | $$ w(\mathbf{z})=1+\sum\beta_{j}\left(z_{j}-\mu_{j}\right)\qquad w(\mathbf{z})=a+\sum b_{j}\left(z_{j}-\mu_{j}\right)+\frac{1}{2}\sum_{j,k}\gamma_{j k}\left(z_{j}-\mu_{j}\right)(z_{k}-\mu_{k}) $$<br><br>$$ w(\mathbf{z})=1+\beta^{T}(\mathbf{z}-\boldsymbol{\mu})\quad w(\mathbf{z})=a+\mathbf{b}^{T}(\mathbf{z}-\boldsymbol{\mu})+\frac{1}{2}(\mathbf{z}-\boldsymbol{\mu})^{T}\boldsymbol{\gamma}(\mathbf{z}-\boldsymbol{\mu}) $$<br><br>$$ w(\mathbf{z})=1+\beta_{s d}^{T}\mathbf{z}_{s d} $$<br><br>$$ w(\mathbf{z})=a+\mathbf{b}_{s d}^{T}\mathbf{z}_{s d}+\frac{1}{2}\mathbf{z}_{s d}^{T}\boldsymbol{\gamma}_{s d}\mathbf{z}_{s d} $$<br><br>$$ \begin{array}{r l}{\beta=s l o p e\mathrm{~o f~t h e~b e s t~l i n e a r~f i t~}}&{{}\gamma=t h e\mathrm{~q u a d r a t i c~c o e f f i c i e n t~o f~t h e~b e s t~}}\\ {}&{{}\mathrm{q u a d r a t i c~f i t.~}\mathbf{b}=\beta\mathrm{~w h e n~}\mathbf{z}\sim\mathrm{M V N}}\\ \end{array} $$
> Gradients appear as coefficients in evolutionary equations when $ (z, g) \sim MVN $ | $$ \Delta\mu=\mathbf{G}\beta $$<br><br>$$ \mathbf{G}^{*}-\mathbf{G}=\mathbf{G}\left(\gamma-\beta\beta^{T}\right)\mathbf{G} $$


---

## chapter30_010 · Measuring Multivariate Selection: Introduction / Estimation, Hypothesis Testing, and Confidence Intervals

Even if we can assume that a best-fitting quadratic is a reasonable approximation of the individual fitness surface, we are still faced with a number of statistical issues. For k traits, the full quadratic regression (Equation 30.13) involves $ k(k+3)/2 $ parameters: $ k(k+1)/2 $ from $ \gamma $ ($ k \gamma_{ii} $ and $ k[k-1]/2 $ symmetric $ \gamma_{ij} $ terms) and $ k $ from $ \beta $. With 5, 10, and 25 characters, this corresponds to 20, 65, and 350 parameters, respectively. Hence, the number of observations should be $ n \gg k(k+3)/2 $ (ideally, by at least an order of magnitude) in order to estimate these parameters with any precision. Unless we test for, and confirm, trait multivariate normality (Appendix 5), $ \beta $ must be estimated from the best linear multiple regression, as the vector of linear slopes in a quadratic regression need not equal $ \beta $. Further, while the literature suggests that the estimate for $ \gamma $ is obtained from the best quadratic regression (Equation 30.13), Equation 29.28b showed that this estimate is biased by the presence of skew. Following Equation 29.29e, a strictly quadratic regression (i.e., with no linear terms), $$ w=a+\frac{1}{2}\mathbf{z}_{sd}^{T}\gamma_{sd}\mathbf{z}_{sd}+e $$ is not biased by skew, but is still a biased estimator for $ \gamma $ if the multivariate pattern of kurtosis differs from that for a multivariate normal (Equation 29.29f).

A second problem is multicollinearity—if many of the characters being measured are highly correlated, the phenotypic covariance matrix can be nearly singular, so even small errors in estimating P result in large differences in $ P^{-1} $. This, in turn, results in a very large sampling variance for the estimates of $ \beta $ and $ \gamma $ (which translates into their instability). A quick check for multicollinearity is to regress each trait on all the others. Subtracting the resulting model $ R^{2} $ from 1.0 determines the tolerance, with very high $ R^{2} $ or low tolerances indicating that multicollinearity is likely to be an issue. One possible solution is to use principal components (Appendix 5) to extract a subset of the characters (measured as PCs; namely, specific linear combinations of the characters) that explains most of the phenotypic variance of P. Fitness regressions using the first few PCs as the characters can then be computed (Lande and Arnold 1983). This approach also reduces the problem of the number of parameters to estimate, but it risks the real possibility of removing the most important characters. Past strong selection may have eroded away much of the variation (Chapters 5, 16, 25, and 26), resulting in such traits being either excluded in a PC set or spread (with weak effects) over several indices of current traits. A further complication is that PCs—weighted indices of trait values—are often difficult to interpret biologically. While the first PC of P for morphological characters generally corresponds to a general measure of size (but see Somers 1986), the others are typically much more problematic to interpret. Finally, using PCs can spread the effects of direct selection on one character over several PCs, further complicating interpretation. While using the PCs of the phenotypic covariance matrix, P, can be problematic, we will show that the PCs associated with the matrix of quadratic selection gradients, $ \gamma $, can provide considerable insight into the nature of selection.

A variety of additional concerns regarding fitness regressions were discussed in Chapter 29. Briefly, residuals of fitness regressions are expected by their nature to be poorly behaved, so using standard methods of confidence intervals on regression coefficients is often not appropriate. Mitchell-Olds and Shaw (1987) and Mitchell-Olds (1989) suggested using the delete-one jackknife method for approximating confidence intervals for coefficients in quadratic regressions when the residuals are not normal. Likewise, the discussions of randomization tests and cross-validation procedures in Chapter 29 extend to multivariate regressions in a straightforward manner. Multivariate tests of the presence of a single mode in the fitness surface were discussed by Mitchell-Olds and Shaw (1987), and we will introduce the Box-Hunter confidence volume for the stationary point on a quadratic fitness surface shortly (after first introducing some required matrix machinery).

---

## chapter30_011 · Measuring Multivariate Selection: Introduction / Regression Packages and Coefficients of $ \gamma $

The coefficients of the elements of $ \gamma $ have a form that may be different from the output of a quadratic regression package. Suppose we have two variables with a mean of zero. Under a Lande-Arnold regression, the quadratic contribution to fitness, w, is $$ \left(\frac{\gamma_{11}}{2}z_{1}\right)+\left(\frac{\gamma_{22}}{2}z_{2}\right)+\left(\gamma_{12}\cdot z_{1}\cdot z_{2}\right) $$

However, many regression packages output the quadratic coefficients as $$ (b_{11}\cdot z_{1})+(b_{22}\cdot z_{2})+(b_{12}\cdot z_{1}\cdot z_{2}) $$

In such cases, $ \gamma_{ii}/2 = b_{ii} $, or $ \gamma_{ii} = 2b_{ii} $, while $ \gamma_{ij} = b_{ij} $ for $ i \neq j $. Failure to make this correction results in the reported $ \gamma_{ii} $ coefficients being only half their true value, thus underestimating the strength of quadratic selection on $ z_i $ (Lande and Arnold 1983; Stinchcombe et al. 2008). Just how widespread this mistake is in the literature remains unclear, but it may be the rule rather than the exception (at least for papers published before 2008). Indeed, Stinchcombe et al. found that almost 80% of the 33 studies they examined made this error.

---

## chapter30_012 · Measuring Multivariate Selection: Introduction / Geometric Aspects

**[推导 Derivation]**

Despite their apparent simplicity, multivariate quadratic fitness regressions have a rather rich geometric structure. By adjusting the character values to give them a mean of zero, the general quadratic fitness regression can be written as

> **Formula (30.19)** · `30.19` · source: `chapter30_block_063` · Geometric Aspects
>
> $$ w(\mathbf{z})=a+\sum_{i=1}^{n}b_{1}z_{i}+\frac{1}{2}\sum_{i=1}^{n}\sum_{j=1}^{n}\gamma_{ij}z_{i}z_{j}=a+\mathbf{b}^{T}\mathbf{z}+\frac{1}{2}\mathbf{z}^{T}\gamma\mathbf{z} $$


If $ z \sim MVN $, then $ b = \beta $ (the vector of coefficients of the best linear fit). Note that if we regard Equation 30.19 as a second-order Taylor series approximation (Equation A6.7) of $ w(z) $, then $ b $ and $ \gamma $ can be interpreted as the gradient and Hessian, respectively, of individual fitness evaluated at the population mean (here $ \mu = 0 $ by construction). Even though a quadratic is the simplest curved surface, its geometry can still be difficult to visualize (Phillips and Arnold 1989; Brodie et al. 1995). The key is that the nature of curvature of Equation 30.19 is determined by the eigenvalues of the $ \gamma $ matrix.

**[推导 Derivation]**

We start our exploration of this geometry by considering the gradient of this best-fitting quadratic fitness surface. Applying Equations A6.1b and A6.1c to Equation 30.19 yields

> **Formula (30.20a)** · `30.20a` · source: `chapter30_block_065` · Geometric Aspects
>
> $$ \nabla_{\mathbf{Z}}\big[w(\mathbf{z})\big]=\mathbf{b}+\gamma\mathbf{z} $$


**[推导 Derivation]**

Hence, the direction of steepest ascent on the fitness surface (the direction in which to move in phenotype space to maximally increase local individual fitness) around z is the vector $ \mathbf{b} + \gamma \mathbf{z} $. If the true individual fitness surface is indeed a quadratic, the average gradient of individual fitness taken over the distribution of phenotypes is

> **Formula (30.20b)** · `30.20b` · source: `chapter30_block_066` · Geometric Aspects
>
> $$ \int\nabla_{\mathbf{Z}}[w(\mathbf{z})]p(\mathbf{z})\mathrm{d}\mathbf{z}=\mathbf{b}\int p(\mathbf{z})\mathrm{d}\mathbf{z}+\gamma\int\mathbf{z}p(\mathbf{z})\mathrm{d}\mathbf{z}=\mathbf{b} $$


as the last integral is $ \mu $ (which is zero by construction). Hence, if the true fitness function is quadratic, the average gradient of individual fitness is given by b, independent of the distribution of z.

**[推导 Derivation]**

Solving for $ \nabla_{\mathbf{z}}[w(\mathbf{z})] = \mathbf{0} $, shows that a point, $ \mathbf{z}_0 $, that satisfies $ \gamma \mathbf{z}_0 = -\mathbf{b} $ is a candidate for a local extremum (also called a stationary point, as the gradient is zero). When $ \gamma $ is nonsingular,

> **Formula (30.21a)** · `30.21a` · source: `chapter30_block_067` · Geometric Aspects
>
> $$ \mathbf{z}_{0}=-\boldsymbol{\gamma}^{-1}\mathbf{b} $$


is the unique stationary point of this quadratic surface. Substituting into Equation 30.19, the expected individual fitness at this point is

> **Formula (30.21b)** · `30.21b` · source: `chapter30_block_067` · Geometric Aspects
>
> $$ w_{0}=a+\frac{1}{2}\mathbf{b}^{T}\mathbf{z}_{0} $$


as obtained by Phillips and Arnold (1989). Because $ \partial^2 w(\mathbf{z}) / \partial z_i \partial z_j = \gamma_{ij} $, the Hessian of $ w(\mathbf{z}) $ is just $ \gamma $. Thus, $ z_0 $ is a local minimum if $ \gamma $ is positive-definite (all eigenvalues are positive), a local maximum if $ \gamma $ is negative-definite (all eigenvalues are negative), or a saddle point if the eigenvalues differ in sign (see Equation A6.8b).

If $ \gamma $ is singular (i.e., it has at least one zero eigenvalue), then there is no unique stationary point. An example of this is seen in Figure 30.3B, where there is a ridge (rather than a single point) of phenotypic values having the highest fitness value. The consequence of a zero eigenvalue is that the fitness surface has no curvature along the axis that is defined by the associated eigenvector. If $ \gamma $ has $ k $ zero eigenvalues, then the fitness surface has no curvature along $ k $ dimensions. The remaining fitness space showing curvature has a single stationary point, which is given by Equation 30.21a for $ \gamma $ and $ b $ when reduced to the $ n - k $ dimensions showing curvature.

---

## chapter30_013 · Measuring Multivariate Selection: Introduction / A Brief Digression: Orthonormal and Diagonalized Matrices

We need some additional machinery on the geometry of matrices (from Appendix 5) to further our discussion of the geometry of the quadratic fitness surface. Matrix transformations (multiplying a vector by a matrix) consist of two basic operations: rotations (changes in the direction of the vector) and scalings (changes in its length). A transformation can be partitioned into these two basic operations by using orthonormal matrices. If we write a square matrix as $ \mathbf{U} = (\mathbf{u}_1, \mathbf{u}_2, \cdots, \mathbf{u}_n) $, where each $ \mathbf{u}_i $ is an n-dimensional column vector, $ \mathbf{U} $ is said to be orthonormal if $$ \mathbf{u}_{i}^{T}\mathbf{u}_{j}=\left\{\begin{aligned}1&\quad if i=j\\ 0&\quad if i\neq j\end{aligned}\right. $$

**[推导 Derivation]**

In other words, each column of U is independent from every other column and has unit length. Matrices with this property are also referred to as $ \text{unitary} $ and $ \text{satisfy} \mathbf{U}^T = \mathbf{U}^{-1} $, so

> **Formula (30.22)** · `30.22` · source: `chapter30_block_070` · A Brief Digression: Orthonormal and Diagonalized Matrices
>
> $$ \mathbf{U}^{T}\mathbf{U}=\mathbf{U}\mathbf{U}^{T}=\mathbf{I} $$


The transformation induced by an orthonormal matrix has a very simple geometric interpretation in that it is a rigid rotation of the original coordinate system—all axes of the original coordinates are simply rotated by the same angle to create the new coordinate system (Appendix 5). The angle between any two vectors remains unchanged following their transformation by the same orthonormal matrix. If the angle between the vectors $ x_1 $ and $ x_2 $ is $ \theta $, then the angle between the transformed vectors $ y_1 = Ux_1 $ and $ y_2 = Ux_2 $ is also $ \theta $ (Equation A5.5d).

**[推导 Derivation]**

A symmetric matrix A (such as a variance-covariance matrix) can be diagonalized as

> **Formula (30.23)** · `30.23` · source: `chapter30_block_072` · A Brief Digression: Orthonormal and Diagonalized Matrices
>
> $$ \mathbf{A}=\mathbf{U}\mathbf{A}\mathbf{U}^{T} $$


where $ \mathbf{A} $ is a diagonal matrix and $ \mathbf{U} $ is an orthonormal matrix $ (\mathbf{U}^{-1} = \mathbf{U}^T) $. If $ \lambda_i $ and $ \mathbf{e}_i $, respectively, denote the $ i $th eigenvalue and its associated unit-length eigenvector of $ \mathbf{A} $, then

> **Formula (30.24a)** · `30.24a` · source: `chapter30_block_072` · A Brief Digression: Orthonormal and Diagonalized Matrices
>
> $$ \boldsymbol{A}=diag(\lambda_{1},\lambda_{2},\cdots,\lambda_{n})=\begin{pmatrix}{{{\lambda_{1}}}}&{{{0}}}&{{{\cdots}}}&{{{0}}} \\{{{0}}}&{{{\lambda_{2}}}}&{{{\cdots}}}&{{{0}}} \\{{{\vdots}}}&{{{\ddots}}}&{{{\vdots}}} \\{{{0}}}&{{{\cdots}}}&{{{\cdots}}}&{{{\lambda_{n}}}}\end{pmatrix} $$


and

> **Formula (30.24b)** · `30.24b` · source: `chapter30_block_072` · A Brief Digression: Orthonormal and Diagonalized Matrices
>
> $$ \mathbf{U}=\left(\mathbf{e}_{1},\mathbf{e}_{2},\cdots,\mathbf{e}_{n}\right) $$


**[推导 Derivation]**

Geometrically, U describes a rigid rotation of the original coordinate system while A shows the amounts that unit lengths in the original coordinate system are scaled in the transformed system. Using the unitary property of U, premultiplying A by $ U^{T} $ and then postmultiplying by U results in a diagonal matrix whose elements are the eigenvalues of A,

> **Formula (30.25)** · `30.25` · source: `chapter30_block_073` · A Brief Digression: Orthonormal and Diagonalized Matrices
>
> $$ \begin{aligned}\mathbf{U}^{T}\mathbf{A}\mathbf{U}&=\mathbf{U}^{T}(\mathbf{U}\boldsymbol{\Lambda}\mathbf{U}^{T})\mathbf{U}=(\mathbf{U}^{T}\mathbf{U})\boldsymbol{\Lambda}(\mathbf{U}^{T}\mathbf{U})\\&=\boldsymbol{\Lambda}\end{aligned} $$


The effect of using such a transformation is that (on this new scale) we remove all cross-product terms in a quadratic product (i.e., the $ z_i z_j $ terms for $ i \neq j $ in Equation 30.19 are absent). Put another way, on this new scale, there is no correlational selection, as $ \gamma_{ij} = 0 $ for $ i \neq j $. A few very useful results immediately follow from Equation 30.25. For $ \mathbf{A}^{1/2} $ and $ \mathbf{A}^{-1} $, the $ \mathbf{U} $ matrix is unchanged, while the diagonal elements in the associated $ \mathbf{A} $ matrix are given by the square root or inverse, respectively. Thus, $ \mathbf{A} $, $ \mathbf{A}^{1/2} $, and $ \mathbf{A}^{-1} $ (provided the latter exists; i.e., no there are zero eigenvalues) all have the same eigenvectors and their eigenvalues are related as $ \lambda_i $, $ \lambda_i^{1/2} $, and $ \lambda_i^{-1} $, respectively.

**[示例 Example]**

> **Example 30.3** · ref: `30.3` · source: `chapter30_013.json` · blocks 6–6
>
> Example 30.3. Brodie (1992) examined one-year survivorship in an Oregon population of garter snakes (Thamnophis ordinoides). Over a three-year period, 646 snakes were marked, 101 of which were eventually recaptured. Four morphological and behavioral characters were measured: overall stripedness of the body-color pattern (stripes), sprint speed, distance moved until an antipredator display was performed, and number of reversals of direction during flight from predators (reversals). None of the values of $ \beta_i $ or $ \gamma_{ii} $ were significant. However, there was a significant quadratic association between striping pattern and number of reversals, with $ \gamma_{ij} = -0.268 \pm 0.097 $ (confidence intervals were generated using the delete-one jackknife method of Mitchell-Olds 1989). As shown in Figure 30.2, the best-fitting quadratic regression of individual fitness has a saddle point, which means that concave selection (negative fitness surface curvature) occurs along one direction and convex selection (positive fitness surface curvature) along the other. Brodie suggested a biological explanation for selection favoring a negative correlation between these two characters. When the body pattern is banded, blotched, or spotted, the detection of movement by visual predators is enhanced. In such individuals, frequent reversals can disrupt a visual search. Conversely, the presence of body stripes makes it difficult for predators to judge the speed of the snake, so frequent reversals (and hence additional movement for predators to perceive) would be disadvantageous.


**[示例 Example]**

> **Example 30.4** · ref: `30.4` · source: `chapter30_013.json` · blocks 7–7
>
> Example 30.4. Consider selection acting on two characters, $ z_1 $ and $ z_2 $. Suppose we find that $ \gamma_{11} = -2 $ and $ \gamma_{22} = -1 $, suggesting that the individual fitness surface has negative curvature in both $ z_1 $ and $ z_2 $. At first glance the picture this evokes is stabilizing selection on both $ z_1 $ and $ z_2 $, with the stabilizing selection surface perhaps rotated due to selection for correlations between $ z_1 $ and $ z_2 $. The first caveat, as mentioned in Chapter 29, is that negative curvature (concavity), by itself, does not imply a local maximum. Even if $ \gamma $ is negative definite (all $ \lambda_i < 0 $; Appendix 5), the location, $ z_0 $, of the maximum in the quadratic surface may be outside of the observed range of population values and hence not currently applicable to the population being studied. A much more subtle point is that, as Figure 30.3 shows, the nature of the fitness surface is very much dependent on the amount of selection for correlations between $ z_1 $ and $ z_2 $. Figure 30.3 considers the surfaces associated with the same values for $ \gamma_{11} $ and $ \gamma_{22} $, but three different values of $ \gamma_{12} $ under the assumption that b = 0. Note that although in all three cases, $ \gamma_{12} > 0 $ (i.e., selection favors increased correlations between the phenotypic values of $ z_1 $ and $ z_2 $), the fitness surfaces are qualitatively very different. When $ \gamma_{12} = 0.25 $, the individual fitness surface indeed shows stabilizing selection in both characters. For $ \gamma_{12} = \sqrt{2} \simeq 1.42 $, the fitness surface has a ridge in one direction, with stabilizing selection in the other. When $ \gamma_{12} = 4 $, the fitness surface is a saddle, with convex selection along one axis and concave selection along the other. An especially troubling point is that if the standard error of $ \gamma_{12} $ is sufficiently large, we will not be able to distinguish between these very different types of selection even if we could show that $ \gamma_{11}, \gamma_{22} < 0 $, and $ \gamma_{12} > 0 $.


---

## chapter30_014 · Measuring Multivariate Selection: Introduction / Canonical Transformation of $ \gamma $

While the curvature of a quadratic fitness surface is completely determined by $ \gamma $, it is easy to be misled about the actual nature of the fitness surface if one attempts to infer its multivariate structure from a simple inspection of the diagonal elements of $ \gamma $. As Figure 30.3 shows, even for two characters, visualizing the individual fitness surface is not trivial and can easily be extremely misleading. The problem is that the cross-product terms ($ \gamma_{ij} $ for $ i \neq j $) make the quadratic form difficult to interpret geometrically. Removing these terms by a change of variables, so that the axes of new variables coincide with the axes of symmetry of the quadratic form (its canonical axes), greatly facilitates visualization of the fitness surface.

**[推导 Derivation]**

Motivated by this observation, Phillips and Arnold (1989) suggested using two slightly different versions of the canonical transformation of $ \gamma $ to clarify the geometric structure of the best fitting quadratic fitness surface. Applying Equation 30.25, if we consider the matrix, U, whose columns are the eigenvectors of $ \gamma $, then the transformation $ \mathbf{y} = \mathbf{U}^T \mathbf{z} $ (and hence $ \mathbf{z} = \mathbf{U} \mathbf{y} $, because $ \mathbf{U}^{-1} = \mathbf{U}^T $ as U is orthonormal) removes all the cross-product terms in the quadratic form, and returns

> **Formula (30.26)** · `30.26` · source: `chapter30_block_077` · Canonical Transformation of $ \gamma $
>
> $$ \begin{aligned}w(\mathbf{z})&=a+\mathbf{b}^{T}\mathbf{U}\mathbf{y}+\frac{1}{2}\left(\mathbf{U}\mathbf{y}\right)^{T}\gamma(\mathbf{U}\mathbf{y})=a+\mathbf{b}^{T}\mathbf{U}\mathbf{y}+\frac{1}{2}\mathbf{y}^{T}\left(\mathbf{U}^{T}\gamma\mathbf{U}\right)\mathbf{y}\\&=a+\mathbf{b}^{T}\mathbf{U}\mathbf{y}+\frac{1}{2}\mathbf{y}^{T}\mathbf{A}\mathbf{y}=a+\sum_{i=1}^{n}\theta_{i}y_{i}+\frac{1}{2}\sum_{i=1}^{n}\lambda_{i}y_{i}^{2}\end{aligned} $$


where $ \theta_i = \mathbf{e}_i^T \mathbf{b} $ and $

**[示例 Example]**

> **Example 30.5** · ref: `30.5` · source: `chapter30_014.json` · blocks 2–2
>
> Example 30.5. Consider the first two scenarios depicted in Figures 30.3A and 30.3B. The resulting $ \gamma $ and the component matrices for its diagonalization (which are easily obtained using the eigen function in R) are as follows: $$ \gamma_{1}=\begin{pmatrix}{{{-2}}}&{{{0.25}}} \\{{{0.25}}}&{{{-1}}}\end{pmatrix},\quad\mathbf{U}_{1}=\begin{pmatrix}{{{0.230}}}&{{{0.973}}} \\{{{0.973}}}&{{{-0.230}}}\end{pmatrix},\quad\mathbf{A}_{1}=\begin{pmatrix}{{{-2.06}}}&{{{0}}} \\{{{0}}}&{{{-0.94}}}\end{pmatrix} $$ and $$ \boldsymbol{\gamma}_{2}=\begin{pmatrix}{{{-2}}}&{{{1.41}}} \\{{{1.41}}}&{{{-1}}}\end{pmatrix},\quad\mathbf{U}_{2}=\begin{pmatrix}{{{0.577}}}&{{{0.816}}} \\{{{0.816}}}&{{{-0.577}}}\end{pmatrix},\quad\boldsymbol{\Lambda}_{2}=\begin{pmatrix}{{{0}}}&{{{0}}} \\{{{0}}}&{{{-3.00}}}\end{pmatrix} $$ Because $ \mathbf{U} = (\mathbf{e}_1 \mathbf{~e}_2) $, the transformed variables, $ y_i = \mathbf{e}_i^T \mathbf{z} $, for $ \gamma_1 $ (for Figure 30.3A) are $$ y_{1}=\mathbf{e}_{1}^{T}\mathbf{z}=0.230\cdot z_{1}+0.973\cdot z_{2},\qquad y_{2}=\mathbf{e}_{2}^{T}\mathbf{z}=0.973\cdot z_{1}-0.230\cdot z_{2} $$ where the quadratic term now becomes $$ \frac{1}{2}\left(-2.06y_{1}^{2}-0.94y_{2}^{2}\right)=-1.03y_{1}^{2}-0.47y_{2}^{2} $$ For $\gamma_2$ (Figure 30.3B), there is a zero eigenvalue, corresponding to no curvature. This occurs in the direction of $y_1 = \mathbf{e}_1^T \mathbf{z} = 0.577 \cdot z_1 + 0.816 \cdot z_2$ (where $\mathbf{e}_1$ is the eigenvector associated with the zero eigenvalue), while the curvature in the direction of $y_2 = \mathbf{e}_2^T \mathbf{z} = 0.816 \cdot z_1 - 0.577 \cdot z_2$ is given by $-(3.00/2)y_2^2$.


The orientation (the principal, or major, axes) of the quadratic surface is determined by the eigenvectors $ (e_1, \cdots, e_n) $ of $ \gamma $, while the eigenvalues $ (\lambda_1, \cdots, \lambda_n) $ of $ \gamma $ determine the nature and amount of curvature of the surface along each canonical axis. Along the axis defined by $ y_i = e_i^T z $, the individual fitness function has positive curvature (is convex) if $ \lambda_i > 0 $. It has negative curvature (is concave) if $ \lambda_i < 0 $, and no curvature (is a plane) if $ \lambda_i = 0 $. The amount of curvature is indicated by the magnitude of $ \lambda_i $; the larger $ |\lambda_i| $, the more extreme the curvature. An alternative way to envision the canonical transformation is that the original vector, $ \mathbf{z} $, of $ n $ characters is transformed into a vector, $ \mathbf{y} $, of $ n $ independent selection indices (Simms 1990). Directional selection on the index, $ y_i $, is measured by $ \theta_i $, while quadratic selection on $ y_i $ is measured by $ \lambda_i $.

Returning to Figure 30.3, we see that the axes of symmetry of the quadratic surface are the canonical axes of $\gamma$. For $\gamma_{12}=0.25$ (Figure 30.3A), $\lambda_{1}=-2.06$ and $\lambda_{2}=-0.94$, and so the fitness surface is concave along each canonical axis, with more extreme curvature along the $y_{1}$ axis. When $\gamma=\sqrt{2}$ (Figure 30.3B), one eigenvalue is zero while the other is $-3$, so the surface shows no curvature along one axis (it is a plane) but is strongly concave along the other. Finally, when $\gamma_{12}=4$ (Figure 30.3C), the two eigenvalues differ in sign, as they are $-5.53$ and $2.53$. This generates a saddle point, with a surface that is concave along one axis and convex along with other, and here with the concave curvature being more the extreme. From Equation 30.26, we can see that the fitness change along a particular axis ($ e_i $) is $ \theta_i y_i + (\lambda_i / 2) y_i^2 $. If $ |\theta_i| \gg |\lambda_i| > 0 $, the curvature of the fitness surface along this axis is dominated by the effects of linear (as opposed to quadratic) selection for modest values of $ y_i = e_i^T z $. If $ \lambda_i = 0 $, the fitness surface along $ y_i $ has no curvature, so the fitness surface is a ridge along this axis. If $ \theta_i > 0 $, this is a rising ridge (fitness increases as $ y_i $ increases), whereas it is a falling ridge (fitness decreases as $ y_i $ increases) if $ \theta_i < 0 $, and it is flat if $ \theta_i = 0 $. Even if $ \gamma $ is not singular, it may be nearly so, with some of the eigenvalues being very close to zero. In this case, the fitness surface shows little curvature along the axes given by the eigenvectors associated with these nearly zero eigenvalues. Further issues relating to the visualization of multivariate fitness surfaces are discussed in Phillips and Arnold (1989), while Box and Draper (1987) review the statistical foundations of this approach. $$ \gamma_{1}=\begin{pmatrix}{{{-2}}}&{{{0.25}}} \\{{{0.25}}}&{{{-1}}}\end{pmatrix},\quad\mathbf{U}_{1}=\begin{pmatrix}{{{0.230}}}&{{{0.973}}} \\{{{0.973}}}&{{{-0.230}}}\end{pmatrix},\quad\mathbf{A}_{1}=\begin{pmatrix}{{{-2.06}}}&{{{0}}} \\{{{0}}}&{{{-0.94}}}\end{pmatrix} $$ and $$ \boldsymbol{\gamma}_{2}=\begin{pmatrix}{{{-2}}}&{{{1.41}}} \\{{{1.41}}}&{{{-1}}}\end{pmatrix},\quad\mathbf{U}_{2}=\begin{pmatrix}{{{0.577}}}&{{{0.816}}} \\{{{0.816}}}&{{{-0.577}}}\end{pmatrix},\quad\boldsymbol{\Lambda}_{2}=\begin{pmatrix}{{{0}}}&{{{0}}} \\{{{0}}}&{{{-3.00}}}\end{pmatrix} $$ Because $ \mathbf{U} = (\mathbf{e}_1 \mathbf{~e}_2) $, the transformed variables, $ y_i = \mathbf{e}_i^T \mathbf{z} $, for $ \gamma_1 $ (for Figure 30.3A) are $$ y_{1}=\mathbf{e}_{1}^{T}\mathbf{z}=0.230\cdot z_{1}+0.973\cdot z_{2},\qquad y_{2}=\mathbf{e}_{2}^{T}\mathbf{z}=0.973\cdot z_{1}-0.230\cdot z_{2} $$ where the quadratic term now becomes $$ \frac{1}{2}\left(-2.06y_{1}^{2}-0.94y_{2}^{2}\right)=-1.03y_{1}^{2}-0.47y_{2}^{2} $$

For $\gamma_2$ (Figure 30.3B), there is a zero eigenvalue, corresponding to no curvature. This occurs in the direction of $y_1 = \mathbf{e}_1^T \mathbf{z} = 0.577 \cdot z_1 + 0.816 \cdot z_2$ (where $\mathbf{e}_1$ is the eigenvector associated with the zero eigenvalue), while the curvature in the direction of $y_2 = \mathbf{e}_2^T \mathbf{z} = 0.816 \cdot z_1 - 0.577 \cdot z_2$ is given by $-(3.00/2)y_2^2$.

---

## chapter30_015 · Measuring Multivariate Selection: Introduction / Are Traits Based on Canonical Axes Meaningful?

While there clearly are significant benefits from using the canonical rotation of $ \gamma $ to infer those trait combinations that are under the strongest quadratic selection, this approach has also sparked a lively debate in the literature. Blows (2007a, 2007b) championed it as providing considerable insight into the nature of selection, while Conner (2007) suggested that “these advantages are usually outweighed by the disadvantage that the results are not very biologically interpretable,” a point echoed by Hunt et al. (2007a). Basically, the concern these authors expressed parallels issues about the use of principal components: even though a specific combination of traits may account for most of the variation, their biological interpretation may be convoluted (at best). This argument raises two questions: What are the true targets of selection, and what is a trait?

The power of quantitative genetics is that anything we can measure can be regarded as a trait, no matter how strange or seemingly biologically unreasonable it may be. Clearly, ecologists and evolutionary biologists working on specific traits (such as clutch size or body weight) bring a wealth of empirical knowledge about these traits when considering possible targets of selection. In this sense, field biologists regard many traits as natural objects. While most would agree that some are (e.g., clutch size), other traits (such as body shape) are more problematic, as they can be defined and measured in a myriad of different ways. At a deeper level, it is the nature of the question that usually determines whether a biologist regards a particular trait as a natural object. Even when considering the same general features, a developmental biologist's view of natural traits may be quite different from an ecologist's view, and in turn both views may be different from those of an evolutionary biologist.

Thus, when a trait is not regarded as a natural object, but rather is some weighted combination of values of natural objects, biologists may feel that much of their intuitive and empirical knowledge about the individual components is diffused over some seemingly arbitrary combination of their values. This is not an unreasonable view. However, selection is not reasonable in that it does not care about how traits are defined; it simply acts on particular multivariate phenotypes. When selection is acting on a complex structure in a medium- or high-dimensional space, simply examining the fitness of projections from this space onto some subset of lower-dimensional traits can be extremely misleading (Walsh 2007; Blows and Walsh 2009). From the perspective of selection, the natural objects are the linear combinations of trait values that comprise the canonical axes of $ \gamma $.

It is this connection with the axes of natural selection that imposes a very real difference between concerns about the interpretation of PCs for a phenotypic covariance matrix and the major axes of $ \gamma $. The latter defines a real object of ecological importance, namely how selection views the traits under selection, while the former define axes of existing variation, which may (or may be) be attributable to selection. Using PCs from the phenotypic covariance matrix to define new traits can diffuse a true target of selection, as the PCs are used simply to deal with phenotypic correlations. In contrast, the canonical axes of $ \gamma $ specifically highlight the targets of selection. As Sewall Wright (1935b) insightfully noted: “It is the harmonious adjustment of all of the characteristics of the organism that is the object of selection, not the separate metrical ‘characters.’”

---

## chapter30_016 · Measuring Multivariate Selection: Introduction / Strength of Selection: $ \gamma_{ii} $ Versus $ \lambda $

Recall from Equation 30.11a that $(\gamma_{ii}/2)(z_i - \mu_i)^2$ is the contribution toward relative fitness, $w$, from squared deviations of trait $i$ from its mean. It is therefore natural to assume that if $\gamma_{ii} < 0$ (concave selection), this implies at least the potential of stabilizing selection on trait $i$. Figure 30.3 showed that using only the diagonal elements of $\gamma$ can potentially give a very misleading picture of the nature of quadratic selection. However, the eigenvalues ($\lambda$) of $\gamma$ provide a more exact description of the true nature of selection. Blows and Brooks (2003) stressed this point, and noted in an analysis of 19 studies that $|\gamma_{ii}|_{\max} < |\lambda|_{\max}$. Thus, studies that report weak values for quadratic selection are potentially biased if they use $\gamma_{ii}$ values, rather than the full geometry of $\gamma$, as described by its eigenvalues. A further point (mentioned above) is that many published studies report only half the true value for $\lambda_{ii}$ due to incorrect translation of the coefficient of the quadratic regression.

Blows and Brooks (2003) noted several advantages of focusing on estimation of the $ \lambda_i $ versus estimation of all of the $ \gamma_{ij} $, noting that there are $ n $ eigenvalues, and $ n(n + 1)/2 $ elements in $ \gamma $. Further, given that many eigenvalues may be close to zero, a subspace of $ \gamma $, such as the space spanned by the first few principal (i.e., canonical) components of $ \gamma $ may essentially capture all of the relevant information on the quadratic fitness surface. Following Simms (1990) and Simms and Rausher (1993), Blows and Brooks suggested that estimation and hypothesis testing can occur if we first obtain the eigenvectors of $ \gamma $, and then use them to generate the transformed variables $ \mathbf{y} = \mathbf{U}^T \mathbf{z} $ in the quadratic regression given by Equation 30.26. This approach is often referred to as a double regression, as one first uses the eigenvectors of $ \gamma $ to generate $ y $ and then fits a quadratic regression of $ w $ using $ y $. The quadratic terms in the regression correspond to the eigenvalues of $ \gamma $ (Equation 30.26), and confidence intervals and significance levels can be conducted within the standard GLM framework (LW Chapter 8). Bisgaard and Ankenman (1996) provided a formal statistical framework for generating standard errors for the estimated $ \lambda_i $ when using this procedure. However, Reynolds et al. (2010) noted that the initial transformation (to generate $ y $) biases tests of significance of the $ \lambda_i $, and they suggested a permutation method to obtain correct type-I error rates.

**[命题 Proposition]**

Kruuk and Garant (2007) noted that the Mercer-Mercer theorem (2000) states that the magnitude of the largest eigenvalue of $ \gamma $ is as least as great as the largest magnitude of the diagonal elements of $ \gamma $. Thus, it is “algebraically inevitable” that at least one combination of traits will show stronger quadratic selection than any of the original traits (provided all values of $ \gamma_{ii} \neq 0 $). Nevertheless, the biological issue here is whether $ \lambda_i $ is significantly greater than $ \gamma_{ii} $ (as opposed to only being slightly larger). Reynolds et al. (2010) found higher power for detecting curvature (nonzero eigenvalues of $ \gamma $) using canonical analysis than when testing each value of $ \gamma_{ii} $ separately.

**[示例 Example]**

> **Example 30.6** · ref: `30.6` · source: `chapter30_016.json` · blocks 3–3
>
> Example 30.6. Brooks and Endler (2001) examined four color traits in male guppies associated with sexual selection. The estimated $ \gamma $ matrix was $$ \gamma=\begin{pmatrix}0.032&-0.016&-0.028&0.103\\-0.016&0.0001&0.066&-0.131\\-0.028&0.066&-0.022&-0.099\\0.103&-0.131&-0.099&0.060\end{pmatrix} $$
> 
> The diagonal elements suggest evidence for weak convex selection ($ \gamma_{44} = 0.060 $, $ \gamma_{11} = 0.032 $) and some evidence for very weak concave selection ($ \gamma_{33} = -0.022 $). However, the eigenvalues of $ \gamma $ are 0.262, 0.012, -0.077, and -0.123. Of these eigenvalues, only the leading one (0.262) is significantly different from zero, with an amount of convex selection over four times that suggested from the largest $ \gamma_{ii} $ value (0.060). The take-home message is that simply relying upon a visual inspection of the diagonal elements of $ \gamma $ can depict a very misleading view of the nature of selection.


---

## chapter30_017 · Measuring Multivariate Selection: Introduction / Significance and Confidence Regions for a Stationary Point

Recall from Equation 30.21a that when $ \gamma $ is nonsingular (i.e., it contains no zero eigenvalues), then $ z_0 = -\gamma^{-1}b $ is the unique extremum (stationary point) in the quadratic regression. If $ \gamma $ contains $ k $ zero eigenvalues, there is no curvature along the trait combinations given by the $ k $ associated eigenvectors (the fitness surface is a $ k $-dimensional hyperplane along these directions), while there is curvature (and a unique stationary point) in the remaining fitness space. As mentioned, this stationary value is a maximum if all of the eigenvalues are negative (and hence a test for significance for a maximum is that all of the eigenvalues should be significantly less than zero). Likewise, it is a local minimum if all the eigenvalues are positive (which can also be tested in the same manner). If $ \gamma $ contains both (significant) positive and negative eigenvalues, then $ z_0 $ is a saddle point. Thus, tests for maxima or minima are straightforward. But what about the confidence region (or more correctly, a confidence volume) for the location of the stationary point?

A classical result for a quadratic regression is the Box-Hunter confidence region. Suppose we let $ d_z $ denote the gradient vector of the best quadratic regression of w on z, which (Equation 30.20a) is calculated by $$ \mathbf{d}_{\mathbf{Z}}=\nabla_{\mathbf{Z}}[w(\mathbf{z})]=\mathbf{b}+\gamma\mathbf{z} $$

**[推导 Derivation]**

Suppose there are k traits and n observations, and the residuals to the quadratic regression are independent and homoscedastic normal variables (as mentioned, for fitness data, this assumption is usually problematic). Box and Hunter (1954) showed that a $ 100(1 - \alpha)% $ confidence volume is given by those vectors z that satisfy the quadratic inequality

> **Formula (30.28)** · `30.28` · source: `chapter30_block_092` · Significance and Confidence Regions for a Stationary Point
>
> $$ \mathbf{d}_{\mathbf{z}}^{T}\mathbf{V}^{-1}\mathbf{d}_{\mathbf{z}}=\left(\mathbf{b}+\gamma\mathbf{z}\right)^{T}\mathbf{V}^{-1}\left(\mathbf{b}+\gamma\mathbf{z}\right)\leq k F_{1-\alpha,k,n-p} $$


where $F$ is the $(1-\alpha)$ value for an $F$ distribution with $k$ and $n-p$ degrees of freedom $(p=k(k+3)/2)$ is the total number of estimated regression coefficients) and $\mathbf{V}$ is an estimate of the covariance matrix for $\mathbf{d}_{\mathbf{z}}$. Values of $z$ that satisfy Equation 30.28 are within the confidence volume for the stationary point. See Del Castillo and Cahya (2001) and Peterson et al. (2002) for further discussion and developments. It is critical to stress that these methods all make the strong assumption that fitness residuals are normally distributed, which typically fails. We strongly favor using aster models (Chapter 29), which correctly model the fitness distribution and for which Geyer and Shaw (2010a) developed likelihood-based approaches for hypothesis testing and confidence intervals.

---

## chapter30_018 · Measuring Multivariate Selection: Introduction / Using Aster Models to Estimate Fitness Surfaces

Most of the approaches presented in this chapter (and in much of Chapter 29) make normality assumptions, which come in two different flavors: first, the assumed multivariate normality (MVN) of the distribution of trait values, z; and second, the assumed MVN for the distribution of residuals in the fitness regression, $ \mathbf{e} = w(\mathbf{z}) - \widehat{w}(\mathbf{z}) $. We address these in turn. As summarized in Table 30.1, when $ z \sim MVN $, a variety of results hold that relate $ \beta $ and $ \gamma $ to measures of the geometries of the individual fitness surface and the mean fitness landscape. Further, as with the univariate case, for $ \beta $ and $ \gamma $ to equal, respectively, the linear and quadratic coefficients in a quadratic fitness regression also requires z to be MVN (lack of skew and the kurtosis of a normal, see Equations 29.28a and 29.28b).

**[命题 Proposition]**

Perhaps the more critical normality assumption involves the distributional behavior of the fitness residuals. As mentioned in Chapter 29, the assumption that $ z \sim MVN $ is not required to fit a regression, although when z is MVN, one can then equate estimated regression coefficients with the properties just mentioned. However, the assumption of multivariate normality of the fitness residuals is required, either directly (for hypotheses testing and constructing confidence intervals) or indirectly (the OLS assumption of homoscedastic residues is satisfied when residuals are MVN). Unfortunately, as mentioned in Chapter 29, most biologically realistic models for fitness components generate residuals that are both heteroscedastic and nonnormal. As introduced in Chapter 29, Aster models (Geyer et al. 2007; Geyer and Shaw 2008, 2010a, 2010b; Shaw et al. 2008; Geyer 2010; Shaw and Geyer 2010) allow for a very wide range of distributional assumptions for the fitness-component residuals, and allow one to build up the distribution of total fitness by convoluting distributions across selection episodes. By fully, and correctly, accounting for the residua error structure, Aster models are far more statistically rigorous than Lande-Arnold estimation and can result in less bias when estimating the fitness surface. For example, in a simulated two-trait dataset fit by Shaw and Geyer (2010), Aster models correctly detected multivariate stabilizing selection (two negative eigenvalues for $ \gamma $), while a Lande-Arnold regression of the same dataset suggested a saddle point (one positive and one negative eigenvalue). An OLS regression assumes that each value is equally weighted (the homoscedastic residual assumption), but when observations vary in their quality (such as heteroscedastic fitness residuals), weighting them properly (as done in Aster models) reduces bias.

While Aster models accommodate complex residual structures, they are not a panacea when it comes to estimating nonlinear fitness surfaces. In the fitness-estimation literature, nonlinear is often taken as synonymous with quadratic, but we have seen how misleading quadratic approximations can be (Figure 29.10). While the link functions used by the GLMs of an Aster model (transforming some underlying linear model into the expected data scale; Chapter 29) can induce nonlinearities (curvature), the transformation is also monotonic (Geyer et al 2007; Geyer 2010, Shaw and Geyer 2010). Hence, while nonlinearities may be introduced, additional peaks are not. In their current form, Aster models assume a quadratic geometry (at most, a single extremum) when the underlying input is a quadratic function of trait values. Hence, many of the issues involved in estimating a fitness landscape by assuming a quadratic geometry remain when using the current Aster framework.

---

## chapter30_019 · Measuring Multivariate Selection: Introduction / MULTIVARIATE SEMIPARAMETRIC FITNESS SURFACE ESTIMATION

**[命题 Proposition]**

As discussed in Chapter 29, using the best-fitting univariate quadratic can result in a very misleading picture when there are multiple peaks or sharp thresholds (such as truncation selection) in the individual fitness surface. This also holds in multivariate space, and hence regressions predicting fitness given a vector z of traits that are nonparametric (free of any assumed functional form) certainly have some advantages. Because some assumption about the residual structure is typically needed to fit such regressions, they are formally called semiparametric, but we will still refer to them as nonparametric owing to the minimal number of assumptions they involve concerning about the functional form of $ w(z) $.

Despite the advantage of having a minimal number of assumptions, these estimators also have significant disadvantages. We have already seen the difficulty in visualizing the multivariate fitness surface when only a simple quadratic function is assumed, but in this case the eigenvalues of $\gamma$ provide significant help in interpretation. However, with general nonparametric methods, there is no corresponding metric for the fitness surface geometry, and thus one must resort to actual visualization of the fitness surface. This requires an examination of successive pairwise cross-sections of the fitness surface (projections onto two of the axes of the fitness function), generating a series of 3-D surfaces (one fitness axis and two trait axes; see Figure 30.4). Further, because these methods typically first construct new axes (linear combinations of the traits; e.g., $x_1 = a_1^T z$, $x_2 = a_2^T z$), and then use them to construct the fitness surface, they display the pattern of selection on a series of composite traits, and not the actual traits themselves. This can make interpretation of the nature of selection on specific traits or combinations of traits problematic at best. Finally, the results from a nonparametric regression do not immediately provide coefficients to predict the response to selection, while (under normality assumptions) these follow automatically with a quadratic regression. Given these complementary strengths and weaknesses, researchers should use both quadratic and nonparametric regressions in the analysis of their selection data.

---

## chapter30_020 · Measuring Multivariate Selection: Introduction / Projection-pursuit Regression and Thin-plate Splines

**[推导 Derivation]**

Schluter and Nychka (1994) extended Schluter's (1988) cubic spline univariate regressions (Chapter 29) to a vector of traits by using projection-pursuit regression (PPR; Friedman and Stuetzle 1981). The basic idea behind PPR is to approximate some complex function, $ f(\mathbf{z}) $, with a series of projection vectors, $ a_i $, and associated ridge functions, $ f_i $,

> **Formula (30.29)** · `30.29` · source: `chapter30_block_098` · Projection-pursuit Regression and Thin-plate Splines
>
> $$ \begin{aligned}f(\mathbf{z})&\simeq f_{1}(\mathbf{a}_{1}^{T}\mathbf{z})+f_{2}(\mathbf{a}_{2}^{T}\mathbf{z})+\cdots+f_{k}(\mathbf{a}_{k}^{T}\mathbf{z})\\&=f_{1}(x_{1})+f_{x}(x_{2})+\cdots+f_{k}(x_{k})\end{aligned} $$


**[命题 Proposition]**

Solutions require two numerically intensive steps: estimation of the best-fitting projection vectors $ (a_1, \cdots, a_k) $, and then estimation of their associated ridge functions (Schluter and Nychka used cubic splines for the latter). Thus, one chooses optimality and smoothing criteria and then obtains the first projection vector while fitting a cubic spline to the data along this projection. One then moves on to fitting the second projection vector, and so on. The assumption is that a rather low-dimensional space captures most of the structure of the fitness surface, so the first few projection vectors are sufficient to approximate individual fitness. As with the eigenvectors of $ \gamma $ in a quadratic regression, the projection vectors $ (a_i) $ are those trait combinations (indices of trait values) that experience the strongest nonlinear selection. Visualization of the resulting complex surface is attempted by considering the pairwise projections on the first few projection vectors (Example 30.7 and Figure 30.4).

**[命题 Proposition]**

It is important to note that the projection vectors for a PPR do not necessarily correspond to the canonical axis of the $ \gamma $ matrix from a quadratic regression (Example 30.7). They do, however, correspond to the trait combinations under the strongest selection, but without the assumption of a quadratic fitness surface. As such, they represent a more general, and potentially natural, geometry for the axes of selection (Morrissey 2014b).

Another nonparametric approach is thin-plate splines, which are the two dimensional analog of univariate cubic splines. Using a projection onto two trait axes, thin-plate splines can be used to find the best-fitting 3-D surface on this reduced set of axes, thus employing another approach for visualizing complex surfaces.

The importance of allowing for more general fitness functions is highlighted by the work of Martin and Wainwright (2013), who examined fitness surfaces for a nascent adaptive radiation in a Bahamian clade of pupfish in the genus Cyprinodon. Using thin-plate splines, they found a fitness surface with multiple peaks, which corresponded to the morphology of existing populations in this radiation. Fitting the same data with a quadratic regression would have only resulted in a single peak (at most), which would have completely obscured important biological conclusions.

Note that these two sets of projection vectors from the different regressions are rather distinct. If we apply Equation A5.2b, the angle between $ e_1 $ and $ a_1 $ will be $ 88^\circ $, while the angle between $ e_2 $ and $ a_2 $ will be $ 87.5^\circ $. Thus, the major axes of the fitness surface are different (here, they are essentially orthogonal) if one uses a quadratic approximation as opposed to a projection-pursuit regression approximation. As Figure 30.4A shows, the best-fitting quadratic regression using $ e_1 $ and $ e_2 $ (where $ y_1 = e_1^T $ z and $ y_2 = e_2^T $ z are the trait values on this fitness surface for an individual with a trait vector, $ \mathbf{z} $) shows disruptive selection, with fitness rising in all directions from a central minimum. If one uses these axes but then fits the data using thin-plate splines, the result is a rather different-looking fitness function (Figure 30.4B), but one that also shows multiple peaks corresponding to different combinations of the traits that females find attractive. When projection-pursuit regression is used (Figure 30.4C), the fitness surface (in rough appearance) is similar to that for thin-plate splines using the quadratic axes ($ e_1 $, $ e_2 $). However, because the values for the two sets of axes ($ x_1 = a_1^T $ z, $ x_2 = a_2^T $ z versus $ y_1 = e_1^T $ z, $ y_2 = e_2^T $ z) are rather different, this superficial visual appearance must be mapped into trait values (as indicated in Figure 30.4). Again, the result is that the fitness surface has multiple peaks.

---

## chapter30_021 · Measuring Multivariate Selection: Introduction / Gradients for General Fitness Surfaces

Table 30.1 shows that when z is multivariate-normal, Lande-Arnold gradients describe the average geometry of an individual fitness surface and are the sole measure of selection in response equations (provided breeding values are Gaussian). When z is not multivariate normal, these features do not necessarily hold. We addressed the issue of how univariate generalized gradients are computed in such settings (and what they imply) in Chapter 29, and these same concepts easily extend to multivariate settings. Janzen-Stein gradients (Equations 29.35a and 29.35b) measure the average geometry of the individual fitness surface. Suppose we let $ \mathbf{z}_{i}, \cdots, \mathbf{z}_{n} $ denote the n vectors of phenotypic observations. For trait $ i $, (30.30a) namely, the average value (over the $n$ data vectors, $\mathbf{z}_{1},\cdots,\mathbf{z}_{n}$) of the gradient with respect to the focal trait.

**[推导 Derivation]**

Morrissey-Sakrejda gradients (Equation 29.35d) are calculated based on the partials of the mean fitness landscape. Fitness-landscape partials are critical because these are what quantifies the nature of phenotypic selection in both the multivariate response equations when the distribution of breeding values is multivariate normal (Table 30.1) and also in the more general Barton-Turelli expression (Equation 24.26) for when normality is not assumed. The Morrissey-Sakrejda gradient for trait i is

> **Formula (30.30b)** · `30.30b` · source: `chapter30_block_106` · Gradients for General Fitness Surfaces
>
> $$ \beta_{M S,i}=\frac{1}{\overline{W}}\frac{\partial\overline{W}}{\partial\overline{z}_{i}},\quad\mathrm{w h e r e}\quad\overline{W}=\frac{1}{n}\sum_{j=1}^{n}W(\mathbf{z}_{j}) $$


where, as above, there are n data vectors, with $ W(\mathbf{z}_j) $ denoting the fitness associated with data vector $ \mathbf{z}_j $. As in Chapter 29, these expressions apply to general fitness functions (such as those generated by PPR), and the required derivatives can be obtained numerically.

---

## chapter30_022 · Measuring Multivariate Selection: Introduction / Calsbeek's Tensor Approach for Detecting Variation in Fitness Surfaces

When dealing with quadratic fitness surfaces, it is straightforward to test whether the regression coefficients vary among estimates from different temporal or spatial samples. How can this be accomplished when the fitness surface is generated by PPR, thin-plate splines, or some other semiparametric regression? Further, how does one best combine fitness surface estimates from a series of locations or times to display both an average fitness surface and also some measure of variability over samples?

A clever solution to both of these problems using tensors was suggested by Calsbeek (2012). The powerful tensor machinery, which is well known to physicists, has only been sporadically applied to quantitative-genetic problems (Rice 2002a, 2004b; Hine et al. 2009; Aguirre et al. 2104). A matrix is a type of tensor with a table of items indexed by two subscripts. Now imagine a series of matrices stacked on top of each other to form a cube (think of a 3D chess board). This is a third-order tensor and is indexed by $ (i, j, k) $ (i.e., i for the $ i $th matrix in the stack, whose elements are indexed by $ (j, k) $, so that the entry $ (2, 4, 5) $ in this tensor (stack of matrices) is the value in row 4, column 5, of the second matrix in the stack. The analysis of fitness functions that may vary over time or space proceeds by considering each fitness-function estimate (corresponding to a specific location or time) as one of the matrices in the total stack of such matrices over all of the locations or times.

Calsbeek’s analysis (for two traits) proceeds by constructing a suitable mesh (neither too fine nor too coarse) for the two trait values, say 50 equally spaced increments on both axes, giving a $ 50 \times 50 $ matrix. The entry in $ (i, 5, 7) $ is the estimated fitness from a semiparametric regression for sample i for the value in axis one corresponding to row five and the value in axis two corresponding to column seven. The stacked series of such estimates forms the tensor. Calsbeek computed several measures of dispersion and variation among the different matrices representing fitness surfaces from different samples. Just as one can decompose a matrix into a series of approximations (e.g., PC1, PC2, etc.) that represent major axes of variation, one can also decompose a tensor into a series of matrices presenting major lower-order dimensions of variation. The first such matrix (the tensor generalization of the PC1 vector) represents the average fitness surface over the sample. Parametric bootstrapping can be used for approximate hypothesis testing, such as for determining the significance of between-sample differences in some component of the fitness surface. See Calsbeek (2012) for details on both of these procedures.

---

## chapter30_023 · Measuring Multivariate Selection: Introduction / Model Selection

Given the plethora of choices for modeling fitness surfaces (which traits to include, what method to use, what type of function to fit, etc.), a few comments on the delicate issue of model selection are in order (see Burham and Anderson 2002 for a complete treatment). If one has a candidate set of models, which should be used? If the models are nested (with one being a subset of the other), then standard likelihood-ratio tests can be used choose between them (LW Appendix 4). However, most models are not nested. In such cases, various informal statistics are used to compare models, and we focus on two, the AIC and BIC metrics. For both of these metrics, a smaller value means it is a better model. We stress that while both metrics are fully grounded in theoretical principles (Burham and Anderson 2004), comparing values for two different models is largely ad hoc in that there is no formal test for significance (i.e., no formal criterion for determining when one model is clearly better than the other).

The idea behind both metrics (as in a likelihood-ratio test) is reward goodness of fit (i.e., smaller values of $ -2 \ln[L] $ imply better fits, where L is the model likelihood), but also to penalize for the number of model parameters, k. One of the widely used model-comparison metrics is the Akaike information criterion (1973), $$ \mathrm{AIC}=-2\ln(L)+2k $$ which was adjusted for the sample size, n, by Sugiura (1978), $$ \mathrm{AIC}_{c}=-2\ln(L)+2k+\frac{2k(k+1)}{n-k-1}=-2\ln(L)+\frac{2kn}{n-k-1} $$

The latter was briefly introduced (Equation 12.25a) in Example 12.5. AIC $ _{c} $ should be used in place of AIC unless n/k > 40 (Burham and Anderson 2004).

The other widely used metric is the Bayes information criterion. $$ \mathrm{BIC}=-2\ln(L)+\ln(n)k $$ which was introduced by Schwarz (1978), and thus is also known as the Schwarz criterion. While AIC and BIC are often used interchangeably, they are actually designed for slightly different purposes. When one of the models being compared is the true model, then BIC picks this model with a probability approaching one in large samples. Conversely, AIC considers the situation where none of the candidate models may be correct and then tries to pick among the best of these. As noted by Shaw and Geyer (2010), if one is just considering a few traits, BIC should be used, but with a large number of traits AIC (or $ AIC_{c} $) is a better choice. Investigators often report both, as the two metrics often rank models differently.

---

## chapter30_024 · Measuring Multivariate Selection: Introduction / THE STRENGTH AND PATTERN OF SELECTION IN NATURAL POPULATIONS

Just how strong is selection in natural populations? When phrased in this way, the question is ambiguous, as it is not clear if the focus is on individual variance in fitness or direct selection on particular traits. One can observe a very high variance in individual fitness, and hence much potential for phenotypic selection, but if all variation in fitness is random (character-independent), then (in the extreme) there will be no phenotypic selection. In focusing on the strength of selection for particular traits, Darwin (1859) felt that characters change very slowly, and hence selection on them is weak. Conversely, there are classical examples (e.g., insecticide resistance and industrial melanism) of rapid responses, and hence presumably strong selection, although such cases are often the result of sudden shifts in the environment (such as anthropogenic changes), and how representative they are remains unclear.

Attempts at measuring selection on quantitative traits in nature trace back to Bumpus (1899) and Weldon (1901). The classical book by Endler (1986), which was one of the first attempts to summarize the average strength of selection, found that strong selection “is not rare and may even be common,” a conclusion that (at the time) was surprising to many. In 2001, Kingsolver and colleagues (Hoekstra et al. 2001; Kingsolver et al. 2001) started to harvest of the rich literature of Lande-Arnold fitness estimates that had been accumulating for almost two decades, and reached the conclusion that the average strength of selection was modest. As detailed shortly, these papers generated much discussion, with some proponents claiming they supported weak to modest selection and others claiming that they supported strong selection.

---

## chapter30_025 · Measuring Multivariate Selection: Introduction / Meta-analysis

As reviewed in Appendix 4, meta-analysis is the field of statistics that deals with the analysis of trends over a large number of experiments (Hunter and Schmidt 2005; Borenstein et al. 2009a; Cooper et al. 2009; Harrison 2011; Koricheva et al. 2013). Informal, or narrative, meta-analyses are by far the most common approach in evolutionary biology. Here, one verbally summarizes the result of a number of studies. This is the type of analysis used by most of the early summaries of strengths of selection in the wild. However, by using the approaches in Appendix 4, one can combine p values over a number of experiments to reach a more global conclusion. While such global p values, and other summary statistics (such as empirical distributions by general trait type, and estimates of mean, or absolute, values), can appear in narrative meta-analyses, a formal meta-analysis is a much more effective way to use the data (Appendix 4).

Unfortunately, conducting a formal meta-analysis requires something that is very often lacking in published results, namely, standard errors of estimates. As detailed in Appendix 4, when standard errors are available, a meta-analysis can be placed into a very powerful fixed-effects or mixed-model framework that allows for a more rigorous, and detailed, analysis of the published data. In part, the focus on narrative approaches arises, not from a lack of statistical expertise from the authors of the meta-analyses, but rather from a lack of full transparency in the published literature, such as a failure to report (at a minimum) standard errors or (more ideally) making the entire dataset available for future analysis. In the words of Kingsolver et al. (2012), “we believe our general understanding of patterns of selection is most limited by lack of access to individual-level data (i.e., data on trait values and fitness measures for each individual) of most studies.”

---

## chapter30_026 · Measuring Multivariate Selection: Introduction / Kingsolver's Analysis

In a series of landmark papers, Kingsolver and colleagues (Hoekstra et al. 2001; Kingsolver et al. 2001) performed an informal meta-analysis on estimates of β and γ from 63 studies of natural populations published between 1984 and 1997. Their resulting frequency distributions of variance-standardized gradients (βsd = σzβ and γsd = σ²zγ) are shown in Figure 30.5. These earlier findings have been updated using much larger datasets, but the basic conclusions from the initial 2001 papers remain the same, with narrative analyses by Geber and Griffen (2003), Kingsolver and Pfenning (2007), Cox and Calsbeek (2009), Siepielski et al. (2009, 2011, 2013), and Kingsolver and Diamond (2011) and more formal (mixed-model) analyses by Kingsolver et al. (2012), Morrissey and Hadfield (2012), and Morrissey (2016).

Kingsolver’s initial analysis noted several trends. First, the distribution of absolute values of the variance-standardized directional selection gradients ($ \beta_{sd} $) closely followed an exponential distribution, with a median (50% value) of 0.16. A $ \beta_{sd} $ of 0.16 implies that a change of one standard deviation in the trait changes relative fitness by 16%. Based on this observation, Kingsolver suggested that most directional selection in nature is fairly weak, although (as a result of the long tail of the exponential), there are a few large estimates (10% of estimates exceeded 0.5). Caution, however, is required with this initial estimate. It is well known that estimates of the expected absolute value, $ |x| $, of a random variable, x, are inflated by sampling error (Equation A4.38a; Hereford et al. 2004; Morrissey 2016). For example, if

$x \sim N(0, \sigma_x^2)$, then $E[|x|] = \sigma_x \sqrt{2/\pi}$ (Equation A4.37a), while if $\sigma_e^2$ is the error associated with estimating $x$ using a sample value, $\widehat{x}$, then $E[\|\widehat{x}\|] = \sqrt{\sigma_x^2 + \sigma_e^2} \sqrt{2/\pi} > E[|x|]$. Hence, the average true strength of directional selection, $E[\|\beta\|]$, is less than the estimated strength, $E[|\widehat{\beta}|]$. Indeed, Morrissey (2016) suggested that the initial Kingsolver value was roughly a twofold overestimate.

Two additional sources of bias can result in a further overestimation of the average strength of $ \beta $, both of which are related to low power: Beavis effects (the overestimation of true effect size when using only values that are declared to be significant) and publication bias (the failure to publish nonsignificant results). Together, all these sources of bias strengthen the claim of weak selection. Consistent with this suggestion, most of the larger estimates of $ |\beta_{sd}| $ occur in studies with small sample sizes, with most estimates below 0.1 occurring when the sample size was 1000 or greater. Hence, it is possible that some of the large $ \beta_{sd} $ values are simply a consequence of the larger estimation variance in smaller sample (the Beavis effect was discussed in LW Chapter 14 in the context of QTL mapping).

The discussion of $ \beta $ was focused on absolute values because their sign is likely to vary when considering a large set of traits and (without reference to a specific trait) the sign is usually not particularly relevant. Such is not the case with $ \gamma_{ii} $, whose sign has an unambiguous meaning. Specifically, negative values indicate concave (and potentially stabilizing) selection, and positive values indicate convex (and potentially disruptive) selection. This leads to the second trend in selection data noted by Kingsolver, concerning the widespread belief that stabilizing selection is far more common than disruptive selection (Chapter 28). Rather than seeing this pattern (a skew toward negative $ \gamma_{ii} $ values), Kingsolver observed an essentially symmetric distribution of $ \gamma_{sd} $ values with a mean of zero (Figure 30.5), which implied that positively and negatively curved fitness surfaces are equally common. Further, the average strength of quadratic selection was weak, with an (again overestimated) median value of 0.10 for $ |\gamma_{sd}| $. A more recent analysis of larger datasets reaffirmed this trend (Kingsolver and Diamond 2011; Kingsolver et al. 2012).

Kingsolver's third trend was that variance-standardized gradients, $ \beta_{sd} $, for mating success and fecundity were larger than those for viability selection (Figure 30.6). This pattern of the weakest gradients often being associated with episodes of viability selection is seen in later (and larger) studies (Siepielski et al. 2011; Kingsolver and Diamond 2011). All of these authors noted that there is likely to be an intrinsic basis for mating traits in that most studies focused on measuring gradients for highly ornamental traits that were likely to be under strong sexual selection. However, no such apparent bias occurs in the choice of fecundity versus viability traits. This apparent pattern of higher variance-standardized gradients on fecundity than on viability provides some justification for the common tendency of studies of long-lived organisms to use annual fecundity (as opposed to annual survival) as a surrogate for total fitness.

However, this conclusion that fecundity is under stronger selection than viability is based on variance-standardized gradients. Recall our discussion from Chapter 29 on mean-standardized gradients, which measure fitness elasticity, and hence are a more natural metric for fitness effects. Crone (2001) found that most long-lived species had higher mean-standardized gradients for annual survival (viability) than for annual fecundity. Based on this result, Crone suggested that, contrary to the standard practice, annual viability may be a better surrogate for total fitness than annual fecundity. One notable exception to this pattern was in perennial semelparous plants (those with a single episode of reproduction), where the elasticity of growth rate was the largest, followed by fecundity, and then survival. For short-lived species, fecundity tends to have a higher elasticity than in longer-lived species. The most accurate approach for assessing the impact of these fitness components on total fitness is to weight the survival and fecundity gradients by the elasticity of each component on the population growth rate, $ \lambda $; see Equation 29.33f.

---

## chapter30_027 · Measuring Multivariate Selection: Introduction / Directional Selection: Strong or Weak?

Has the case for “weak” selection been made? As pointed out by Conner (2001), even so-called weak selection can be very effective at changing trait means. Consider Kingsolver’s median value of $ \beta_{sd} = 0.16 $ ($ \beta = 0.16 \cdot \sigma_z $). From Equation 13.22a, the single-generation expected change in the mean (in phenotypic standard deviations) is $ h^2 \cdot 0.16 $. With a typical heritability of 0.4, only 16 generations of selection are required to shift the population mean by one standard deviation, and only 80 generations are required to shift it by five standard deviations. Another way to think about the impact of a “weak” selection gradient of $ \beta_{sd} = 0.16 $ was mentioned by Hereford et al. (2004). They noted that even a population of modest size spans over four standard deviations of variation, implying a fitness range of $ 4 \cdot 0.16 = 0.64 $, or a 64% variation in relative fitness among individuals within the population (assuming that the fitness-surface approximation holds over this span of phenotypic values).

**[推导 Derivation]**

Conversely, if concerns about publication bias and low power are correct, the true median value of $ |\beta_{sd}| $ may be substantially less than the “weak” median value of 0.16 found by Kingsolver. Hersch and Phillips (2004) and Knapczyk and Conner (2007) examined the validity of these concerns. Figure 29.9 presented power curves for a univariate analysis (a single-trait fitness regression), which is a function of $ \rho = \bar{\eta}/\sqrt{I} $. Hersch and Phillips showed that when multiple (potentially correlated) traits are considered, the adjusted version of the trait-fitness correlation, $ \rho $, used in power calculations becomes

> **Formula (30.31)** · `30.31` · source: `chapter30_block_126` · Directional Selection: Strong or Weak?
>
> $$ \rho^{2}=\frac{\beta_{sd}^{T}\mathbf{s}}{I} $$


Hence, $ \bar{\imath}^{2} $ is replaced by $ \beta_{sd}^{T}s $ (where s is the vector of variance-standardized selection differentials, i.e., a vector of selection intensities), which accounts for the correlations among the (measured) traits. Using Equation 30.31, Hersch and Phillips found that most of the studies summarized by Kingsolver for which power calculations could be performed (i.e., those that included estimates of I) were very underpowered, supporting Kingsolver's concern about the underreporting of small values and hence skewing the distribution of estimates of $ |\beta_{sd}| $ upwards.

The impact of publication bias, which is also called the "file-drawer effect" (Rosenthal

1979; Rosenberg 2005), as nonsignificant results are not published and hence simply “left in a file,” was also examined by Hersch and Phillips (2004). They simulated cases where results were only published when one (or more) of the gradients in a study were found to be significant. Although such a model does indeed allow for many nonsignificant values in the database, these are still biased because they were conditioned on at least one of the results being significant. This ascertainment scheme is certainly one reasonable model for quantifying publication bias. For each “publication,” the simulation chose five “traits” by drawing five $ \beta_{sd} $ values at random. If one (or more) of the five tests was significant, all the values were retained, and if not, they all were discarded. As shown in Figure 30.7, this conditional sampling resulted in the median value of $ \beta $ being substantially overestimated when either the sample size or the amount of variation explained by the effects was small (low $ R^{2} $ values), both of which are settings that result in low power. This is essentially another manifestation of the Beavis effect, overestimation when using statistics that are conditional on success (significance).

Knapczyk and Conner (2007) also considered sampling error and publication bias, but they arrived at the very different conclusion that “our understanding of selection is not strongly biased by these commonly invoked sources of error.” To examine publication bias, they binned the datasets examined by Kingsolver based on sample size. If there was no publication bias, the distribution of $ |\beta_{sd}| $ values should have a similar form over different sample sizes (following the exponential observed for the entire set by Kingsolver). They found departures from this pattern for studies with very small sample sizes (less than 40), but did not find departures for studies with larger sample sizes. Indeed, compared to the exponential distribution, they found an excess of weak selection gradients in the larger studies. Thus, they concluded that publication bias, except in the smallest studies, did not upwardly bias estimates of $ |\beta_{sd}| $ in any appreciative way. Appendix 4 presents a number of metrics to assess publication bias.

Further complicating matters is the paper by Hereford et al. (2004), who found that using mean-standardized gradients ($ \beta_{\mu} = \mu\beta $; Equation 29.33a) gave very different results. Recall that the mean-standardized gradient is $ \beta_{\mu} = 1 $ when the trait is fitness itself, providing a benchmark for the strength of selection on a trait (Equation 29.33c). Using a subset of the Kingsolver data (38 studies yielding 580 estimates) that included the required information for this standardization (i.e., those that reported the trait means), they found a median $ |\beta_{\mu}| $ of 0.54, or 54% of the strength of selection on fitness. This is indeed strong selection. Even using a correction for the upward bias generated by sampling error (Equation A4.37a), which reduced the median value to 0.31, still left strong selection. The observed strengths of selection were so large that the authors suggested that the selection gradients were likely inflated by focusing on single episodes of selection rather than lifetime fitness. In essence, they suggested that tradeoffs resulted in the actual gradient of lifetime fitness for a trait being significantly less than the gradients based on single episodes of selection. However, as we discuss shortly, there appears to be little evidence for tradeoffs among the traits in the currently analyzed databases (Figure 30.9).

A final perspective on the strength of directional selection was offered by Hendry and Kinnison (1999) and Kinnison and Hendry (2001), who compiled data on over 2000 estimated rates of microevolution. While rates of divergence in trait means confound the strength of selection with the transmission genetics of the trait, an advantage of this approach is that such estimates focus on an average rate of change over time, thus smoothing out large values caused by brief episodes of strong selection. Such episodes are more likely to catch our attention, and considering only these episodes results in a biased view of the average strength of selection over time. Figure 30.8 plots the cumulative selection intensities obtained by Endler (1986) and Kingsolver et al. (2001) as well as the inferred average selection intensity values given the observed rates of microevolution, assuming heritabilities of 0.1 and 0.4. As can be seen, under either assumed heritability, there is an excess of weak selection (small $ \bar{\tau} $) values relative to those seen by Kingsolver and Endler. While this suggests that weak selection is the norm, an argument for strong selection can also be made. While strong selection can certainly occur over brief episodes, if it continues over a sufficient amount of time, genetic variation for the selection response will be eroded and further response must wait for new variation (from mutation and immigration). Thus, with strong persistent selection, $ h^{2} $ will likely become much smaller than 0.1. Conversely, if selection is episodic, selection to reduce $ h^{2} $ will be smaller and genetic variation will erode less quickly.

An apparent excess of small selection intensities could reflect true low selection intensities when averaged over many generations, thus smoothing out strong episodes. However, it could equally likely reflect strong persistent selection quickly eroding heritability and hence reducing response.

Three other evolutionary questions can be partly addressed through a meta-analysis of estimated gradients: the relative importance of correlated traits, the impact of fitness-component tradeoffs, and the magnitude of temporal variation.

---

## chapter30_028 · Measuring Multivariate Selection: Introduction / Total Versus Direct Selection, Tradeoffs, and Temporal Variation

The amount of total selection on a trait is given by $S$ (and its variance-standardized counterpart, $s = \bar{s}$), which is the sum of the amount of direct ($\beta$, $\beta_{sd}$) and correlated selection (Equation 30.3). When $\beta_{sd}$ is estimated from a multiple-trait regression, a plot of $s$ versus $\beta_{sd}$ can provide insight into the relative importance of direct versus correlated selection. A major caveat concerning this type of analysis is that it is only as good as the characters that are included in the regression. If causally important fitness traits that are correlated with a focal trait are not included, their effect can incorrectly be attributed to direct selection. Using this approach, Kingsolver and Diamond (2011) found that correlated selection had little impact, with $s$ often falling very close to $\beta_{sd}$ in value. An exception is size, where total selection is generally less than direct selection, which suggests negative correlations with other traits under selection. An analysis by Geber and Griffin (2003) of performance traits in plants found a different pattern than was seen by Kingsolver and Diamond. For these traits, they observed that $|\beta_{sd}|$ tended to be smaller than $|s|$, so not only were correlated effects important, but they also tended to be in the same direction as direct effects. Geber and Griffin estimated that ~40% of the amount of directional selection on a trait was the result of correlated effects. Moreover, they found the same pattern ($ |\gamma_{sd}| < |C/\sigma^4| $) for quadratic selection, with correlated effects accounting for an average of ~60% of the total effect.

A second area of interest to evolutionary biologists is the relative importance of tradeoffs between different fitness components. For example, a trait that improves variability might do so at the expense of mating success or fecundity, so simply measuring the impact of a trait on one fitness component can give a very misleading view of its evolutionary potential (e.g., Example 29.1). Kingsolver and Diamond (2011) addressed this issue by plotting $ \beta_{sd} $ values for the same trait in those few studies that measured multiple episodes of selection. As shown in Figure 30.9, while examples of tradeoffs exist (the values of $ \beta_{sd} $ have different signs across episodes), there is no evidence that it is widespread. Indeed, in 57% of the comparisons, the two gradients had the same sign, thus reinforcing, rather than masking, selective effects.

Another potential tradeoff is, not between different episodes of selection, but rather between the sexes. Males and females may experience different amounts of selection for the same trait, and in the extreme may have opposite signs, or sexually antagonistic selection (SA). In part, the limit that any such SA may place on evolution depends on genetic correlation of a trait between the sexes. If this correlation is less than perfect (i.e., different sets of genes may be involved between the sexes), then we have a two-trait evolution question (Equation 13.26c), and whether the presence of different patterns of selection on the separate traits constrains their joint evolution depends as much on their genetic covariance structure (G) as it does on their strength of selection (β). By ignoring this concern and instead focusing on selection itself, the potential importance of SA was examined in a narrative meta-analysis by Cox and Calsbeek (2009), who compared values of $ |\beta_{male} - \beta_{female}| $ over traits, and obtained a median value of 0.13 (for variance-standardized gradients). Note that this is close to the initial Kingsolver value for absolute selection on traits, suggesting that between-sex differences are on par with the level of absolute selection on a trait. When it was broken down by fitness components, Cox and Calsbeek found that the median value of $ |\beta_{male} - \beta_{female}| $ was smallest for viability and fecundity selection and largest for both sexual selection and total selection (a median value of around 0.2 to 0.3).

A strong caveat concerning these conclusions was noted by Morrissey (2016). As with $ \left|\beta\right| $, estimates of an absolute difference, $ \left|\beta_{male} - \beta_{female}\right| $, are inflated by sampling noise. Indeed, the expected value of $ \left|x_{i} - x_{j}\right| $ for two random draws $ (x_{i}, x_{j}) $ from the same distribution is $ 2\sigma_{x}/\sqrt{\pi} $ (Nair 1936). Morrissey noted that such comparisons are best performed in a bivariate mixed-model framework (similar to the analysis used for Equations 20.26 through 20.29). His reanalysis of the Cox and Calsbeek data found that the correlation between male and female selection gradients was $ \sim0.8 $, thus showing that selection gradients are highly positively correlated between the sexes and that SA is rare.

The final issue is the impact of temporal variation in selection strength and direction (Siepielski et al. 2009, 2011, 2013; Kingsolver and Diamond 2011). There are numerous ways to quantify temporal variation, such as measuring the standard deviation over a set of estimates (which compounds actual variation with sampling variation) or the fraction of times the sign changes (which can be high for a trait under very weak selection). A simple metric is to plot $ |mean(s)| $ versus $ mean(|s|) $. If sign reversals are common, then $ |mean(s)| < mean(|s|) $, while if the two are roughly equal, little sign reversal has occurred. While this metric obscures any variation in the strength of selection, it does address the impact of temporal variation in its direction. As shown in Figure 30.9, for the existing data, any directional variation is relatively modest, and it is greatest for traits under weak selection ($ mean[|s|] $ small), which could simply reflect sampling error.

These data were reexamined by Morrissey and Hadfield (2012), who performed a random-effects meta-analysis (Appendix 4) on a subset (consisting of those studies that reported standard errors, and hence allowed for a formal meta-analysis). If we let $ \beta_{ij} $ denote the jth temporal value from the ith study-trait combination, the model becomes $$ \beta_{ij}=\mu+u_{i}+t_{ij}+e_{ij} $$ where $ \mu + u_i $ is the expected value for the gradient in the $ i $th study-trait combination, $ t_{ij} $ is the residual due to temporal variance, and $ e_{ij} $ is the sampling error. The last three variables are treated as random effects, and one can estimate their variances in a mixed-model setting. Of interest is the ratio $ \sigma_u^2 / (\sigma_u^2 + \sigma_t^2) $, namely, the amount of variance due to among study-trait means relative to the trait plus temporal variance. Morrissey and Hadfield found this ratio was quite high, measuring 0.88 (with a 95% credible interval of 0.82 to 0.91), thus leading to the conclusion that selection over time is remarkably constant.

Siepielski et al. (2011) examined how the temporal strength of selection varied over different fitness components (viability, mating success, and fecundity). The temporal variation among variance-standardized gradients was highest for mating success and roughly equal for survival and fecundity. Given potential differences in sampling error over these different fitness components, this result could simply imply higher sampling variation in mating success over other components. They also found that reversals of signs were highest for survival, followed by mating, and then fecundity. They noted that frequent sign reversals could occur if a trait under viability stabilizing selection has its mean close to the optimum ($ \theta $). In such a setting, small fluctuations of the mean around $ \theta $ result in sign variation in $ \beta $.

**[推导 Derivation]**

To examine if this is the case, Siepielski et al. applied a result from Estes and Arnold (2007), who used $ \beta_{sd} $ and $ \gamma_{sd} $ to estimate the distance of a population mean from an optimum,

> **Formula (30.32)** · `30.32` · source: `chapter30_block_142` · Total Versus Direct Selection, Tradeoffs, and Temporal Variation
>
> $$ \frac{\left|\overline{z}-\theta\right|}{\sigma}\simeq\left|\frac{\beta_{sd}}{-\gamma_{sd}}\right| $$


This follows from Equation 30.21a, and it assumes a normally distributed trait with a fitness function that is well approximated (over the bulk of its phenotypic distribution) by a quadratic. Using Equation 30.32, Siepielski et al. found a value for the standardized difference of the mean from an optimum of $ 2.28 \pm 0.54 $ for survival traits in their dataset, but values of $ 14.59 \pm 9.14 $ for mating success and $ 11.62 \pm 5.48 $ for fecundity. While Equation 30.32 is a crude metric, which is fraught with numerous pitfalls, it does suggest that survival traits might be closer to their optimum (provided it exists).

---

## chapter30_029 · Measuring Multivariate Selection: Introduction / Directional Selection on Body Size and Cope's Law

Body size has several outlier features relative to other traits. As shown in Figure 30.10, while the distribution of $ \beta_{sd} $ values for morphological traits was symmetric around zero, the distribution for $ \beta_{sd} $ for body size was highly skewed toward positive values (Kingsolver and Pfenning 2004; Kingsolver and Diamond 2011). Kingsolver and Pfenning suggested that individual selection for larger body size underlies Cope's law (the tendency for the size of species within a lineage to increase over evolutionary time). This suggestion also presents a paradox: if it is true, why are most of the largest animals not present today? Kingsolver and Pfenning (2004, 2007) suggested that this is a consequence of differential extinction, pointing out that during the last widespread extinction of North American mammals, the largest species were the hardest hit. However, as we noted above, Kingsolver and Diamond (2011) also found that direct selection on size is greater than the total selection ($ \beta_{size} > s_{size} $), suggesting the presence of selection against traits that are phenotypically correlated with body size, whose values tend to become more deleterious as body size increases. Further, they found that the distribution of $ \gamma $, while symmetric for most classes of traits, was significantly negative for body size, suggesting that it is often under stabilizing selection. Figure 30.10 shows that another class of characters, phenological traits (season timing events such as breeding), also shows a skewed distribution, toward negative (i.e., earlier) values.

---

## chapter30_030 · Measuring Multivariate Selection: Introduction / Quadratic Selection: Strong or Weak?

Discussions of whether the observed amount of quadratic selection is strong or weak are highly problematic. If estimates of $ \beta_{sd} $ are underpowered (and thus significant estimates are likely overvalued; i.e., the Beavis effect), the same is certainly true for quadratic estimates.

Indeed, simulations by Haller and Hendry (2013) found that there is generally low power for detecting stabilizing selection due to small sample sizes. Simulations for traits under weak stabilizing selection typically resulted in a distribution of $ \gamma $ values similar to that seen in Figure 30.5, namely, largely symmetric about the origin (reflecting low power, and hence a roughly random distribution of estimates around zero). An important feature of the Haller-Hendry simulations was that they used a “virtual ecologist” approach, wherein simulated data from the quantitative-genetics model is combined with an observer model (i.e., a model for how the data would be ascertained in real-world settings, such as having living individuals that are not recaptured counted as dead). This mimics how real data would be “virtually” observed (Zurell et al. 2009), and hence more correctly reflects the actual power of collected data.

Balancing concerns about inflated estimates due to low power (Beavis effects), there are two reasons why reported estimates of quadratic gradients may be undervalued. As mentioned earlier, many published reports have made errors in obtaining $ \gamma_{ii} $ values from the output of standard regression packages, resulting in only half their true value being reported (Stinchcombe et al. 2008). Second, Blows and Brooks (2003) noted that $ |\gamma_{ii}| $ likely significantly underestimates the strength of quadratic selection when multiple traits are considered (see Example 30.6). An analysis based on the eigenvalues ($ \lambda $) of the $ \gamma $ matrix is much more informative as to the strength of quadratic selection in nature.

The much more problematic issue is whether $ \gamma $ is even a reasonable measure for non-linear fitness surfaces. As Figure 29.10 illustrated, a value of $ \gamma $ can be entirely misleading when the fitness surface departs from a quadratic. As the above theory on canonical forms illustrates, a quadratic surface in k dimensions (traits) still has (at most) only a single extremum (Equation 30.21a). In this case, fitting a multimodal fitness surface with a quadratic will return a very misleading value of $ \gamma $. Indeed, even with stabilizing Gaussian selection, if the mean is sufficiently above the optimum, the best quadratic fit will result in $ \gamma > 0 $, which falsely implies the presence of potentially disruptive selection (Figure 29.10).

---

## chapter30_031 · Measuring Multivariate Selection: Introduction / Where Is All the Stabilizing Selection?

Perhaps the most striking observation from the meta-analysis of $ \gamma $ values is the lack of a clear trend toward negative values (except for body size), as would be expected if stabilizing selection were widespread. This is highly troubling given the historic view of most ecologists and evolutionary biologists that stabilizing selection is widespread and important over evolutionary time (Charlesworth et al. 1982; Maynard Smith 1983; Estes and Arnold 2007; Hunt et al. 2007a). One explanation is that $ \gamma $ does not capture the correct geometry in multimodal fitness surfaces. The second is the observation from the Haller-Hendry (2013) simulations of low power to detect stabilizing selection.

Haller and Hendry offered several other explanations for this “missing” stabilizing selection. The first is that selection may have already done its job in that the existing phenotypic variation is small relative to the width of the fitness peaks (Chapter 28). In their words, “selection ‘erases its traces’ once populations have adapted to a fitness peak.” The second is the suggestion from Chapter 28 that strong stabilizing selection is likely to be confined to a few dimensions in the multivariate trait space (i.e., a few indices of trait values). This results in only a weak signal in any single component trait and low power of detection. Their final suggestion is that $ \underline{\text{squashed stabilizing selection}} $ may be common, which again lowers power. Here competition results in disruptive selection among individuals whose trait values are near an adaptive peak, which flattens out (squashes) the fitness surface around the peak, making detection more difficult. An example of this phenomenon is the work of Morno-Rueda (2009) on selection on shell morphology in Spanish land snails (Iberus gualtieranus). Predation from black rats (Rattus rattus) results in distinctive markings on the shell, and using only such shells showed disruptive selection on shell height. Conversely, when shells lacking these markings were used in the analysis, stabilizing selection was seen. When all shells are considered as a single group, no significant quadratic term is observed.

---

## chapter30_032 · Measuring Multivariate Selection: Introduction / A Plea to Fully Publish

In 1899, Herman Bumpus published a modest dataset involving 136 domestic sparrows (Passer domesticus) immobilized by an ice storm. Of these, 72 (21 females, 51 males) survived, while the remaining 64 (28 females, 36 males) perished. Despite the humble beginning, this has become the most widely analyzed study of selection (Harris 1911; Calhoun 1947; Grant 1972; Johnson et al. 1972; O'Donald 1973; Lande and Arnold 1983; Crespi and Bookstein 1988; Crespi 1990; Pugesek and Tomer 1996). In large part, this is because Bumpus published all of his data, allowing investigators to employ their own methods of analysis. In contrast, Kingsolver et al. (2001) lamented that many of the studies included in their meta-analysis did not even report standard errors, much less trait means (which are needed to allow for mean-standardized gradients to be computed), thus limiting their inclusion to only narrative meta-analyses. At a minimum, any published study should report standard errors for all estimates. More generally, studies should make their entire dataset available to the community. Indeed, such fully open access is a requirement for virtually all published molecular studies. As Kingsolver et al. (2012) pleaded "Recycle your hard-won, slightly used, still precious data today!"

---

## chapter30_033 · Measuring Multivariate Selection: Introduction / UNMEASURED CHARACTERS AND OTHER BIOLOGICAL CAVEATS

Even if we are willing to assume that the best-fitting quadratic regression is a reasonable approximation of the individual fitness surface, there are still a number of important biological caveats to keep in mind (Chapters 20 and 29). For example, the fitness surface can change in both time and space, often over short spatial or temporal scales (e.g., Kalisz 1986; Stewart and Schoen 1987; Scheiner 1989; Jordan 1991; Garant et al. 2007; Siepielski et al. 2009, 2011, 2013; Bell 2010; but see Morrissey and Hadfield 2012), so one estimate of the fitness surface may be quite different from another for a different time or location (Figures 30.11 and 30.12). Hence, considerable care must be taken before pooling data from different times or sites to improve the precision of estimates. Conversely, fitness data are noisy, and the resulting surfaces have considerable uncertainty, so two, visually rather different-looking, surfaces might be not statistically significantly different. When the data are such that selection gradients can be estimated separately for different times or areas, interactions of space/time × gradient can be tested in a straightforward fashion (e.g., Mitchell-Olds and Bergelson 1990). Further, the evolution of a trait may result in a change in the biotic environment, which in turn may change the nature of selection on that trait (Chapters 20 and 22).

Population structure can also influence fitness surface estimation. If the population being examined has overlapping generations, fitness data must be adjusted to reflect this (Chapter 29). Likewise, if members of the population differ in their amount of inbreeding, measured characters and fitness may show a spurious correlation if both are affected by inbreeding depression, which in turn can inflate the apparent strength of directional and concave selection (Willis 1996). Finally, immigration must be accounted for (e.g., Garant et al. 2005), especially if there are different selection regimes within the area that encompasses the study population (e.g., Figure 30.12).

Despite these concerns, the most severe caveat for the regression approach of estimating $ w(z) $ is unmeasured characters. Estimates of the amount of direct selection acting on a trait are biased if that traits is phenotypically correlated with unmeasured characters that are also under selection (Lande and Arnold 1983; Mitchell-Olds and Shaw 1987). Adding one or more of these unmeasured characters to the regression can change initial estimates of $ \beta $ and $ \gamma $. Conversely, selection acting on unmeasured characters that are phenotypically uncorrelated with those being measured has no effect on estimates of $ \beta $ and $ \gamma $.

---

## chapter30_034 · Measuring Multivariate Selection: Introduction / PATH ANALYSIS AND FITNESS ESTIMATION

As we saw in Figure 29.12, complex life cycles can be represented as graphs, as can a set of cascading developmental traits (Figure 30.13), the elaborate interplay between fitness components (Figure 30.14), or the connection between traits, fitness components, and population growth rate (Figure 30.16). One way to explore these graphical structures is with path analysis, which requires a path diagram, which is a hypothesis about the structure of causality (LW Appendix 2; Kingsolver and Schemske 1991; Mitchell 1992; Shipley 1997). The strengths of relationships in a path diagram are represented by path coefficients, which are correlations among connected items in the path. As a very simple example, consider the impact that seed weight and plant height have on fitness.

One potential path diagram is seed weight → height → fitness, which states that seed weight only impacts fitness through its effect on plant height. A path analysis of this model first variance-standardizes all of the variables and then performs regressions (or partial regressions), generating correlations among the items in the path. Suppose the resulting coefficients are $$ \begin{aligned}weight\quad\xrightarrow{0.35}\quad height\quad\xrightarrow{0.15}\quad w\end{aligned} $$ implying a correlation of $ \rho = 0.35 $ between seed weight and plant height, and a correlation of 0.15 between height and fitness. As drawn, this diagram implies that seed weight does not have a direct effect on fitness, but it does have an indirect effect through height. Because $ \rho^2 $ is the fraction of variation accounted for by a factor, we see that seed weight explains 13% ($ 0.35^2 = 0.13 $) of the variance in plant height and that plant height accounts for 2% ($ 0.15^2 $) of the variance in fitness. Further, the correlation between any two connected items in a path is the product of their path coefficients, giving a correlation between seed weight and fitness of $ 0.35 \cdot 0.15 = 0.0525 $, showing that seed weight accounts for 0.3% ($ 0.0525^2 $) of the variance in fitness.

Regression and path analysis offer complementary approaches for examining relationships between phenotypes and fitness. The purpose of a regression analysis is to predict fitness given character values, while path analysis provides a description of the biological nature of character covariances and how they interact with fitness. While regressions simply rely on the correlations among traits (Figure 30.13A), path analysis examines the structure of these correlations (Figures 30.13B and 30.13C), building on the biological intuition of the investigator. A number of authors have applied this approach to the analysis of natural selection (e.g., Arnold 1983b; Maddox and Antonovics 1983; Mitchell-Olds 1987; Crespi and Bookstein 1988; Crespi 1990; Jordan 1991; Weis and Kapelinski 1994; Conner 1996; Pugesek and Tomer 1996; Scheiner et al. 2000; van Tienderen 2000; Coulson et al. 2003; Latta and McCain 2009; Matsumura et al. 2012).

The analysis of selection on graphs falls into four categories. First, we have already seen the use of Aster models on life-history graphs to obtain a statistically rigorous distribution of fitness effects (Chapter 29). Second, path analysis can be used to represent a proposed causal structure among life-history components and traits to provide insights that a standard fitness-trait regression can miss. Third, selection could be on one or more latent (unobserved) features that are correlated with observed (and potentially unselected) traits. While the observed traits may show trait-fitness associations, these could all be indirect effects, resulting from the correlation with the latent traits. This setting can also create high collinearity, with many of the measured traits being highly correlated with the latent traits. Path-analysis models can be used in some cases in the analysis of such data. Finally, elasticity path analysis connects selection gradients of a trait on fitness components with the elasticity (Chapter 29) of those components on the population growth rate ($ \lambda $) to provide the elasticity of that trait on $ \lambda $ (van Tienderen 2000). This approach provides a powerful connection between selection and demography. We address these last three topics in order, while Aster model analysis of life-history graphs were introduced in Chapter 29.

While powerful, path-analytic methods are not without significant caveats. First, all of the issues with non-Gaussian fitness residuals that are a concern with regression methods fully apply to path analysis (which, itself, is a modified regression method). Second, path analysis assumes that there are only linear interactions, and hence only model directional selection. Scheiner et al. (2000) described how to include quadratic factors by augmenting each variable with its square and then performing a considerable amount of bookkeeping (see their paper for details). Finally, the results from a path analysis are extremely dependent on the assumed causality structure, so the interpretation of the results can be substantially biased if this structure is even slightly incorrect. Echoing the cautionary words of Kingsolver and Schemske (1991), “The uncritical application of path models to the analysis of selection in natural populations is likely to yield misleading and erroneous results.”

---

## chapter30_035 · Measuring Multivariate Selection: Introduction / Regressions Versus Path Analysis

The key distinction between a regression and a path analysis of selection is that regression attempts to statistically account for the covariance between fitness and the measured traits, while a path analysis further attempts to account for the processes generating correlations among the measured traits. Regressions assume that none of the traits are causal to any of the others, while Crespi (1990) noted that “path-analytic reasoning assumes that characters are correlated as a result of biological causes that should be used as information rather than adjusted away.” As an example, suppose traits are ordered in time, such as

---

## chapter30_036 · Measuring Multivariate Selection: Introduction / germination, $ g \rightarrow $ vegetative growth rate, $ r \rightarrow $ flowering time, f

**[命题 Proposition]**

A regression analysis simply uses each trait's correlation with fitness without using the ordered structure inherent in the variables, while a path analysis explicitly uses this information. Examples of different casual assumptions for the same set of four traits are given in Figure 30.13. Each diagram displays a different causal structure that was assumed at the start of the analysis. Connections (arrows) that are nonsignificant or have very trivial values are usually left out of the final diagram, with the strength of connections often indicated by the line thickness of the arrows. Double-header arrows indicate correlations, namely, no assumption about the nature of causality between these variables, as would be the case for a standard regression (Figure 30.13A). A key limitation (and also strength) of a path analysis is that these different assumed path diagrams (causality structures) can result in rather different interpretations of the patterns of selection. If it is correct, the path diagram captures unique features missed by a regression (which assumes correlations, rather than attempting to model how they arise). If it is incorrect, a path analysis can introduce potentially serious biases.

**[示例 Example]**

> **Example 30.8** · ref: `30.8` · source: `chapter30_036.json` · blocks 1–1
>
> Example 30.8. Mitchell-Olds and Bergelson (1990) measured fitness (using adult size as a proxy) in the annual plant Impatiens capensis as a function of five traits: seed weight, germination date, June size, early growth rate, and late growth rate. Figure 30.14 displays the significant paths between these variables and fitness. Note that the path diagram provides a description of the actual nature of the correlations, and in particular, the causal connections assumed between variables. From this diagram, we can examine the contribution to relative fitness from the direct effect of a character and from its indirect effects through its effect on other characters. For example, the direct effect of early growth is 0.37 (the path $ EG \rightarrow w $), so this path accounts for 13% of the variation in fitness ( $ 0.37^{2} \simeq 0.13 $). Early growth also influences fitness through an indirect path by influencing late growth rate, which in turn has a direct effect on fitness ( $ EG \rightarrow LG \rightarrow w $), and their product 0.8 $ \cdot $ 0.48 = 0.38 accounts for an additional 15% ( $ 0.38^{2} $) of the total variance in fitness. The total effect of early growth on fitness is the sum of the squared direct and indirect effects; here $ 0.37^{2} + 0.38^{2} $, or 25%. Proceeding in a similar fashion, the direct and indirect effects for each trait on fitness are
> 
> > **Inline Table 2** · `inline_2` · page 42 · source: `chapter30_036`
> > Inline Table 2
> >
> > Character | Direct Effect | Indirect Effect
> > --- | --- | ---
> > Seed weight | 0.04 | 0.10
> > Germination date | -0.08 | -0.32
> > June size | -0.02 | 0.52
> > Early growth rate | 0.37 | 0.38
> > Late growth rate | 0.48 | 0.00
> 
> 
> Negative coefficients imply that fitness increases with decreasing trait value. Observe that indirect effects are more important than direct effects for most characters.


While we have framed multiple-trait selection in the context of a number of traits in an individual and how these influence fitness, an equally common situation is when the “traits” are not properties of an individual, but rather biotic agents, such as the predators, competitors, or pollinators of the focal species. Path analysis allows one to examine the interactions among these multiple components and how they influence the fitness of the trait in the focal species.

**[示例 Example]**

> **Example 30.7** · ref: `30.7` · source: `chapter30_036.json` · blocks 3–3
>
> Example 30.7. Following up on the study of male color traits in guppies described in Example 30.6, Blows et al. (2003) examined six traits (two morphological and four color) for their role in female attractiveness. Both quadratic and projection-pursuit regressions were used to examine nonlinear selection on these traits. The trait loadings for the first two major axes of the quadratic regression of fitness on trait value (the eigenvectors $ e_1 $ and $ e_2 $, corresponding to the two leading eigenvectors of $ \gamma $) and the first two projection vectors ( $ a_1 $ and $ a_2 $) from projection-pursuit regression were as follows:
> 
> > **Inline Table 1** · `inline_1` · page 24 · source: `chapter30_036`
> > Inline Table 1
> >
> > Trait | e_{1} | e_{2} | a_{1} | a_{2}
> > --- | --- | --- | --- | ---
> > Body area | -0.065 | 0.157 | 0.185 | 0.551
> > Tail area | 0.663 | 0.635 | 0.331 | 0.087
> > Black area | -0.245 | 0.645 | 0.430 | -0.182
> > Fuzzy area | 0.372 | -0.173 | 0.101 | -0.286
> > Iridescent area | 0.436 | -0.134 | 0.569 | -0.757
> > Orange area | -0.411 | 0.333 | 0.581 | -0.016
> 


**[示例 Example]**

> **Example 30.9** · ref: `30.9` · source: `chapter30_036.json` · blocks 4–4
>
> Example 30.9. Weis and Kapelinski (1994) examined the nature of selective forces acting on gall size of a tephritid fly (Eurosta solidadginis), whose larvae makes a protective gall on goldrenrods. Larvae residing in small galls are susceptible to a parasitoid wasp (Eurytoma gigantea), whose ovipositor can reach the larvae through small, but not large, galls. Countering this, when galls become sufficiently large, they are preyed upon by insectivorous birds (mainly downy woodpeckers, Picoides pubescens). The result is selection pressure on both large and small galls, but through different biotic agents. Two other parasitoids, a second wasp and a beetle, also feed on larvae within galls, but here gall size does not appear to be a factor. However, galls attacked by these two insects appear to be distasteful, and the resulting parasitoids are not eaten by birds. Thus, this is a complex system with different agents and the possibility of frequency-dependent search images, all of which are acting to impart selection on the focal trait, which is gall size.
> 
> The authors examined two different path diagrams for selection intensity on gall size, one of which represented a conventional model of selection, with gall density and mean gall size included in the model. A second (search image-based) model replaced these two measures with the density of small galls and the density of large galls. Under the conventional model, there was a strong (but not significant) negative association (-0.43) between gall size and attacks by $ Eurytoma $ and a strong (and significant) association (0.37) between mean gall size and bird attacks. Conversely, under the frequency-dependent model, there was no association between small or large gall density and $ Eurytoma $ attacks, but a strong (and significant) association between density of small galls (-0.50) and density of large galls (0.46) and bird attacks. As this example illustrates, a path-analysis model allows an investigator to examine the impact of several possible causality structures by leveraging known biological information (which does not enter into a standard regression analysis).


---

## chapter30_037 · Measuring Multivariate Selection: Introduction / Morrissey's Extended Selection Gradient Vector, $ \eta $

Consider the following two path diagrams connecting a focal trait (z), fitness (w), and some unmeasured factor (f): $$ \operatorname{path}1\colon z\leftarrow f\rightarrow w\qquad\qquad\operatorname{path}2\colon z\rightarrow f\rightarrow w $$

Both paths generate a correlation between the focal trait and fitness, which results (in a regression analysis) in a nonzero gradient, $ \beta $, when f is excluded (as z and w are correlated), and a $ \beta $ value of 0 when it is included (as, when it is conditioned on f, z and w are uncorrelated). Path 1 is the “missing trait” concern in a Lande-Arnold regression: if f is not included in the analysis, the regression falsely suggests a direct effect of z on fitness. Conversely, for path 2, z influences the unmeasured factor, f (e.g., some measure of performance; Arnold 1983b, 1988) which in turn influences fitness. While both paths generate a $ \beta $ value of zero when the factor f is included in the analysis, they reflect very different settings. In a regression analysis, we strive to avoid situations like those in path 1, while a nonzero value of $ \beta $ for path 2 when f is not in the analysis typically need not trouble us, as z has a causal influence on fitness (albeit an indirect one). Note that both paths can have identical correlation structures between all pairwise elements (and thus both would yield the exact same Lande-Arnold regression), which shows the importance of a causal diagram in the analysis of selection on correlated traits.

Motivated by situations like path 2, where z has an indirect causal impact on fitness but a $ \beta $ value of 0 if traits in the causal structure between z and w are included in the analysis (e.g., f in path 2), Morrissey (2014a) proposed the concept of an extended selection gradient vector, $ \eta $. This variable measures the total selection caused by a trait and its downstream causative components. Recall (Equation 30.3) that the selection differential is measure of the total selection on a trait from both direct and indirect (correlated) selection, and that $$ S_{i}=\beta_{i}P_{ii}+\sum_{j\neq i}\beta_{j}P_{ij} $$

**[推导 Derivation]**

Morrissey’s idea is that the extended selection gradient, $ \eta $, is the total selection on a trait that is directly connected through its causal connections (as opposed to correlations) with w. For a given causal structure (path diagram), suppose we let $ \beta_{pa,i} $ denote the selection gradient for the direct effect of a trait on fitness (i.e., for the single-arrow path $ i \to w $). Likewise, let $ \Phi_{ij} $ be the total impact over all connecting paths of the effect of i on trait j (see Example 30.10 for details). Then, by analogy with Equation 30.3,

> **Formula (30.33a)** · `30.33a` · source: `chapter30_block_169` · Morrissey's Extended Selection Gradient Vector, $ \eta $
>
> $$ \eta_{i}=\beta_{pa,i}\cdot1+\sum_{j\neq i}\beta_{pa,j}\Phi_{ij} $$


As with $S$, the extended gradient decomposes into the direct effect from a trait (the path $i \to w$) plus the indirect effects from direct selection on all other traits that are causally associated with $i$ ($i \to \cdots \to j \to w$).

**[推导 Derivation]**

One can compute the value of $ \Phi_{ij} $ directly by taking the product of path coefficients for a path connecting i and j, and then summing over all such paths. However, Morrissey found a quicker approach for obtaining $ \Phi_{ij} $ based on the matrix, B, of path coefficients for a given causal structure. The elements of B are constructed as follows (see below for a worked example): if $ i \rightarrow j $, then $ B_{ij} $ is the path coefficient between them, while $ B_{ji} = 0 $ because j does not influence i. Likewise, if there is not a direct connection between i and j, then $ B_{ij} = 0 $, even if they are causally connected though intermediates; and finally, we define $ B_{ii} = 0 $. With B defined in this fashion, Morrissey found that the values of $ \Phi_{ij} $ are calculated by

> **Formula (30.33b)** · `30.33b` · source: `chapter30_block_170` · Morrissey's Extended Selection Gradient Vector, $ \eta $
>
> $$ \boldsymbol{\Phi}=(\mathbf{I}-\mathbf{B})^{-1} $$


From Equation 30.33a, we have

> **Formula (30.33c)** · `30.33c` · source: `chapter30_block_170` · Morrissey's Extended Selection Gradient Vector, $ \eta $
>
> $$ \boldsymbol{\eta}=\boldsymbol{\Phi}\boldsymbol{\beta}_{pa}=(\mathbf{I}-\mathbf{B})^{-1}\boldsymbol{\beta}_{pa} $$


One very desirable feature of $ \eta_i $ is that if trait $ i $ has a causal effect (either direct or indirect) on fitness, then $ \eta_i $ is not changed by the addition (or subtraction) of new traits in the causal chain between $ i $ and $ w $. In terms of our path 2 above ($ z \to f \to w $), the value of $ \eta_z $ equals the value of $ \beta_z $ in a model where $ f $ is ignored ($ z \to w $).

**[示例 Example]**

> **Example 30.10** · ref: `30.10` · source: `chapter30_037.json` · blocks 6–6
>
> Example 30.10. Building on the work of Latta and McCain (2009), Morrissey (2014a) examined the relationship between a number of traits in wild oats (Avena barbata) and fitness, w (measured by number of reproductive spikes), using the following assumed causality structure. The values above the arrows are correlation coefficients, while the numbers 1 through 6 index the traits in the B matrix (as detailed below).
> 
> The six traits considered were days at germination (dgerm), mass at day 60 (m60), days to first flower (dtf), final total mass (mass), number of reproductive tillers (rpt), and mass of reproductive tillers (mrt). The (variance-standardized) directional selection gradients under Lande-Arnold ($ \beta_{LA} $, which is a multiple regression of w using all six traits) and under the path model ($ \beta_{pa} $) are quite different, which shows the impact of the assumed causal structure among the traits and with fitness: $$ \boldsymbol{\beta}=\begin{pmatrix}\beta_{dgerm}\\\beta_{m60}\\\beta_{dtf}\\\beta_{mass}\\\beta_{rpt}\\\beta_{mrt}\end{pmatrix},\quad\mathrm{where}\quad\boldsymbol{\beta}_{LA}=\begin{pmatrix}0.009\\0.004\\-0.040\\-0.028\\0.142\\0.207\end{pmatrix},\quad\boldsymbol{\beta}_{pa}=\begin{pmatrix}0\\0\\0\\-0.033\\0.157\\0.207\end{pmatrix} $$
> 
> Note that only mass, rpt, and mrt directly impact fitness under the assumed path model.
> 
> The resulting matrix, B, of path coefficients is constructed as follows. The first row corresponds to those traits that are directly influenced by trait 1 (dgerm), which is only trait 2 (m60), as all the other entries are zero. The second row involves those traits that are directly influenced by trait 2, which are only traits 3 and 4, as all the other entries are zero. Continuing in this fashion, and noting that traits 5 and 6 influence no traits in the diagram (we are not considering w), yields $$ \mathbf{B}=\begin{pmatrix}{{{0}}}&{{{-0.012}}}&{{{0}}}&{{{0}}}&{{{0}}}&{{{0}}} \\{{{0}}}&{{{0}}}&{{{-0.200}}}&{{{0.306}}}&{{{0}}}&{{{0}}} \\{{{0}}}&{{{0}}}&{{{0}}}&{{{0}}}&{{{-0.580}}}&{{{-0.605}}} \\{{{0}}}&{{{0}}}&{{{0}}}&{{{0}}}&{{{0.135}}}&{{{0.396}}} \\{{{0}}}&{{{0}}}&{{{0}}}&{{{0}}}&{{{0}}}&{{{0}}} \\{{{0}}}&{{{0}}}&{{{0}}}&{{{0}}}&{{{0}}}&{{{0}}}\end{pmatrix} $$ which in turn yields $$ \boldsymbol{\varPhi}=(\mathbf{I}-\mathbf{B})^{-1}=\begin{pmatrix}{{{1}}}&{{{-0.012}}}&{{{0.0240}}}&{{{-0.0037}}}&{{{-0.0018}}}&{{{-0.0029}}} \\{{{0}}}&{{{1}}}&{{{-0.2000}}}&{{{0.3060}}}&{{{0.1573}}}&{{{0.2422}}} \\{{{0}}}&{{{0}}}&{{{1}}}&{{{0}}}&{{{-0.5800}}}&{{{-0.6050}}} \\{{{0}}}&{{{0}}}&{{{0}}}&{{{1}}}&{{{0.1350}}}&{{{0.3960}}} \\{{{0}}}&{{{0}}}&{{{0}}}&{{{0}}}&{{{1}}}&{{{0}}} \\{{{0}}}&{{{0}}}&{{{0}}}&{{{0}}}&{{{0}}}&{{{1}}}\end{pmatrix} $$
> 
> To see that $ \mathbf{B} $ recovers the correct values of the $ \Phi_{ij} $, we compute a few of these elements by hand. The elements in the first row of $ \Phi $ correspond to the total causal effects from trait 1 (dgerm), which is $ -0.12 $ on trait 2 (m60), and $ -0.012 \cdot 0.306 = -0.0037 $ for trait 4 ($ 1 \rightarrow 2 \rightarrow 4 $). A more complicated case is the casual connection of trait 1 on trait 5, as there are two paths, $ 1 \rightarrow 2 \rightarrow 4 \rightarrow 5 $ and $ 1 \rightarrow 2 \rightarrow 3 \rightarrow 5 $, for a total of $ [-0.012 \cdot \0.306 \cdot 0.135] + [-0.012 \cdot (-0.200) \cdot (-0.580)] = -0.0018 $.
> 
> Using $ \Phi $, the resulting vector of extended gradients becomes $$ \boldsymbol{\eta}=\begin{pmatrix}\eta_{d g e r m}\\\eta_{m60}\\\eta_{d t f}\\\eta_{m a s s}\\\eta_{r p t}\\\eta_{m r t}\end{pmatrix}=\boldsymbol{\varPhi}\boldsymbol{\beta}_{p a t h}=\boldsymbol{\varPhi}\begin{pmatrix}0\\0\\0\\-0.033\\0.157\\0.207\end{pmatrix}=\begin{pmatrix}-0.001\\0.065\\-0.216\\0.070\\0.157\\0.207\end{pmatrix} $$
> 
> The extended gradient (η) gives the total amount of selection on each trait caused by all the paths that are causally connected to that trait. The values for mrt and rpt are the same as their β_pa values, as both of these traits have only a direct effect on fitness. Now consider the difference between β_pa for mass in the path diagram (-0.033) and its η value (0.070). While the direct effect, mass→w, is negative, the total of the casual effects from mass, (mass→w) + (mass→rpt→w) + (mass→mrt→w), is $$ -0.033+(0.135\cdot0.157)+(0.396\cdot0.207)=0.070 $$ which is positive and larger in magnitude than the direct negative effect.


---

## chapter30_038 · Measuring Multivariate Selection: Introduction / Selection on Latent Variables

Another application of path analysis arises when unmeasured traits that are under selection influence measured traits (Maddox and Antonovics 1983; Crespi and Bookstein 1988; Crespi 1990; Pugesek and Tomer 1996). This bane of a regression analysis can, potentially, be partly addressed with path analysis. Further, many of the measured traits may be highly correlated, raising issues of high collinearity (and instability in regression estimates). If this correlation structure is in large part due to one, or a few, underlying latent variables, then by focusing on these underlying variables, this problem may largely disappear.

For example, one common concern is that apparent selection on morphological traits may simply be a reflection of general selection on size (Figure 30.15). To this end, Crespi and Bookstein (1989) and Crespi (1990) suggested first extracting the leading principal component (PC 1) associated with the covariance matrix of the measured traits, which typically returns a generalized measure of size. Crespi and Bookstein then considered the univariate correlation of fitness of each size-adjusted trait, ignoring any further details about their correlation structure once size is removed.

**[命题 Proposition]**

Care must be taken, however, when the traits show any allometry (growth pattern) other than isometric growth (shape is independent of size; see LW Chapter 11). In such cases, PC 1 can contain both size and shape information. Jolicoeur (1963) and Somers (1986) suggested extracting PC 1 from the correlation matrix (as opposed to the covariance matrix) for log-transformed traits. When isometric growth is present, the eigenvector corresponding to this first PC should have all traits weighted equally (Jolicoeur 1963), with (for n traits) each element in the vector being $ 1/\sqrt{n} $. This provides a check of whether the assumption of isometric growth is appropriate. Similarly, the latent trait could be some measure of performance (Arnold 1983b, 1988) that selection acts directly upon and that is influenced by the measured traits (Chapter 29).

---

## chapter30_039 · Measuring Multivariate Selection: Introduction / Elasticity Path Diagrams

As we have seen, even very complex life histories can be represented as graphs (Figures 29.12 and 30.14). The impact of small demographic changes in the resulting transition matrix (or projection matrix) associated with this graph is measured by the elasticities of the elements in this matrix with respect to their impact on the population growth rate, $ \lambda $ (Chapter 29; Caswell 1989, 2001). If an element in the projection matrix has an elasticity of $ e $, then a proportional change of $ f $ in that element results in a proportional change of $ f \cdot e $ in $ \lambda $ (Equation 29.4b). Changes in elements with larger elasticities have a proportionally greater impact on $ \lambda $. For example, recall that Sæther and Bakke (2000) found average elasticity values in birds of 0.6 and 0.25 for viability and fecundity, respectively, which showed that changes in viability result in a much greater proportional change in the growth rate.

**[推导 Derivation]**

Conner (1996) suggested that path analysis can be used to connect traits, their impact on fitness components, and the impact of those fitness components on the population growth rate, $ \lambda $ (namely, how changing the mean of a trait alters the mean population growth rate). In a traditional path-analysis setting, such an analysis would return correlations between these various elements (e.g., Example 30.8; Figure 30.14), and while these correlations have a straightforward biological interpretation, they are disconnected from our standard metric of selection gradients and population growth. In a classic (but often underappreciated) paper, van Tienderen (2000) showed that using elasticities in place of path coefficients (an elasticity path analysis, or elastogram) connects trait selection, fitness components, and the population growth rate. Equation 29.33f describes the elasticity of a trait on $ \lambda $ as the sum over all fitness components of the product of its mean-standardized gradient $ \left(\beta_{\mu,i}\right) $ for fitness component, $ W_i $, times the elasticity, $ e_i = \partial \ln(\lambda) / \partial \ln(W_i) $, of that component on $ \lambda $,

> **Formula (30.34)** · `30.34` · source: `chapter30_block_183` · Elasticity Path Diagrams
>
> $$ \frac{\partial\ln(\lambda)}{\partial\ln(\mu)}=\sum_{i=1}\frac{\partial\ln(\lambda)}{\partial\ln(W_{i})}\frac{\partial\ln(W_{i})}{\partial\ln(\mu)}=\sum_{i=1}e_{i}\beta_{\mu,i} $$


Example 30.11 and Figure 30.16 show the power of this approach, and a detailed example is given by Coulson et al. (2003).

**[示例 Example]**

> **Example 30.11** · ref: `30.11` · source: `chapter30_039.json` · blocks 3–3
>
> Example 30.11. Matsumura et al. (2012) simulated a model examining the impact of traits on the success of spawning migrations of salmon. Two traits of interest were the annual juvenile growth rate and the date of river entry for migrating individuals. Three survival measures (newborn, juvenile, and migration) as well as fecundity were taken as the fitness components. The impact of a trait on each of these components was measured by mean-standardized selection gradients, which correspond to elasticities of these components with respect to the trait (Equation 29.33e). Likewise, a demographic analysis using a population projection matrix (Chapter 29) evaluated the elasticities of these fitness components with respect to the population growth rate $ \lambda $ (see their paper for details). Figure 30.16 presents the resulting elastogram. Consider the impact of entry date on $ \lambda $. This trait impacts a single fitness component (migration survival) with an elasticity (mean-standardized gradient, $ \beta_{\mu} $) of 0.91, and migration survival has an elasticity ($ e_{i} $) of 0.25 on $ \lambda $, yielding (from Equation 30.34) an elasticity on $ \lambda $ as a function of this trait of 0.91 - 0.25 = 0.23. Hence, a 10% increase in mean entry date yields a 2.3% increase in the population growth rate. The second trait, juvenile growth rate, has significant effects on three fitness components. Its elasticity on $ \lambda $ through newborn survival is -0.71 - 0.25 = -0.18; through juvenile survival is -0.71 - 0.75 = -0.53, and through fecundity is 2.87 - 0.50 = 1.44; for a total elasticity (through all fitness components) of -0.18 - 0.53 + 1.44 = 0.725. Thus, a 10% increase in mean juvenile growth rate results in a 7.3% increase in $ \lambda $, mainly through its impact on fecundity (a 14% increase) and despite decreases of 1.8% and 5.3% in newborn and juvenile survival, respectively.


---

## chapter30_040 · Measuring Multivariate Selection: Introduction / LEVELS OF SELECTION

Finally, while our focus (thus far) has been on predicting fitness given the phenotype of an individual, it is also possible that selection acts at levels above the individual, e.g., through group-level effects (Chapter 22). For example, Breden and Wade (1989) found that increasing larval group size in the imported willow leaf beetle (Plagiodera versicolora) increases individual survivorship, with each additional group member increasing fitness by $ \sim7% $. Here, we briefly examine the analysis of selection at multiple levels. While one can use Price's equation to decompose the selection differential of a trait into within-group and among-group components, as we will show, this can be misleading. Akin to the fact that selection differentials are unreliable indicators of the targets of selection when traits are correlated, this is also the case when the traits have selective impacts at both the individual and group levels. As above, the amount of direct selection on a trait at a specific level of selection can be determined by using the appropriate multiple regression.

---

## chapter30_041 · Measuring Multivariate Selection: Introduction / Contextual Analysis

Heisler and Damuth (1987) proposed that any effects of selection acting at some level above that of the individual can be estimated with the method of contextual analysis, which is widely used in the social sciences (e.g., Boyd and Iversen 1979). This regression-based approach amounts to simply adding group-level traits to a Lande-Arnold regression. Traits scored at the level of groups can be aggregate characters (simple functions of the individual phenotypes within a group, such as the group mean), or they can be global or emergent characters that can only be defined at the group level (such as number of group members or group density). As the following example illustrates, incorporating group-level traits into the Lande-Arnold fitness regression is straightforward.

**[示例 Example]**

> **Example 30.12** · ref: `30.12` · source: `chapter30_041.json` · blocks 1–1
>
> Example 30.12. Aspi et al. (2003) examined the effects of selection on the riparian plant Silene tatarica, a threatened species from Finland in the family Caryophilleaceae. Plants tend to grow in patches and the authors envisioned that plant density within a patch might influence both pollinator visits and herbivory. The individual traits measured were plant height ($ z_{1} $) and number of stems ($ z_{2} $), while two aggregate traits were measured (the means $ \overline{z}_{1} $ and $ \overline{z}_{2} $ of each trait for the patch) along with the group-level trait of plant density, d. The resulting regression model for predicting the relative fitness of individual j in patch i becomes $$ w_{ij}=1+\beta_{1}z_{1,ij}+\beta_{2}z_{2,ij}+\beta_{3}\overline{z}_{1,i}+\beta_{4}\overline{z}_{2,i}+\beta_{5}d_{i}+e_{ij} $$
> 
> The regression coefficients $ \beta_1 $ and $ \beta_2 $ correspond to direct selection on individual trait values, while $ \beta_3 $ and $ \beta_4 $ correspond to direct selection on the patch mean of each trait, and $ \beta_5 $ to direct selection on the density within a patch. Aspi et al. variance-standardized all variables, so a one standard deviation change in the variable of interest results in an expected change of $ \beta $ in fitness. For data collected in 1999, the estimated regression coefficients for a sample of 922 individuals were $$ \begin{array}{l}\underline{\text{Height}}\quad Mean height\quad Stem No.\quad Mean stem No.\quad Density\\\beta\quad0.589^{***}\quad0.653^{***}\quad0.187^{**}\quad-0.209^{***}\quad0.631^{***}\end{array} $$
> 
> All of the $ \beta $ were significant, with $ * $* denoting p < 0.01 and $ * $* $ * $* denoting p < 0.001. Note that (on a standardized scale) selection on group density is as strong as individual selection. Selection on height at the individual and group levels was in the same direction, which the authors suggested was due to pollinator attraction. However, selection on stems was in opposite directions, with individual selection increasing the number of stems, but patch-level selection decreasing them. The authors suggested that patch-level selection may be due to herbivory by reindeer.
> 
> A contextual analysis need not stop at two levels, as this approach easily extends to additional hierarchical levels of population organization, and hence allows for the potential for selection at these higher levels as well. Indeed, in some settings the individual level is ignored, and only higher levels of organization are contrasted. One example of this involves the work of Banschbach and Herbers (1996), who compared selection on nest- versus colony-level traits in a forest ant (Myrmica punctiventris), and found that fertility selection largely operates at the level of the nest, as opposed to the level of multiple-nest colonies.
> 
> In many settings, group composition is fairly obvious, due to a patchy distribution of individuals in space. However, in some situations, the appropriate set of individuals to include in a group is unclear. Indeed, for populations where individuals appear to be continuously distributed in space with few obvious breaks, group-level effects may be present when very close individuals are included yet largely disappear as the defined group becomes larger. In theory, one could assign different group sizes and use model-selection approaches to determine the group structure that gives the best fit of the fitness regression. However, care must be taken to distinguish a statistical fit from biological reality. A very reasonable biological definition of a group was offered by Uyenonyama and Feldman (1981), namely, the set of all individuals that influence the fitness of a focal individual.
> 
> An alternative to using group means is to model neighbor interactions that influence fitness (e.g., Equation 22.59a). In such cases, the fitness of a focal individual, i, can be written (for a single trait) as
> 
> > **Formula (30.35a)** · `30.35a` · source: `chapter30_block_193` · Contextual Analysis
> >
> > $$ w_{i}=1+\beta_{1}z_{i}+\beta_{2}\Big(\sum_{i\neq j}z_{j}\Big)+e_{i} $$
> 
> 
> Note that under this model, the group mean (which contains the value of the focal individual) is replaced by the interactions caused by the neighbors of the focal individual (the members in the sum). This model is easily connected to the model using the standard selection on group model by noting that $$ \sum_{i\neq j}z_{j}=n\overline{z}-z_{i} $$ when i interacts with n - 1 neighbors. Hence, we can express Equation 30.35a as
> 
> > **Formula (30.35b)** · `30.35b` · source: `chapter30_block_194` · Contextual Analysis
> >
> > $$ \begin{aligned}w_{i}&=1+\beta_{1}z_{i}+\beta_{2}\Big(n\overline{z}-z_{i}\Big)+e_{i}\\&=1+\big(\beta_{1}-\beta_{2}\big)z_{i}+\beta_{2}n\overline{z}+e_{i}\end{aligned} $$
> 
> 
> The subtle distinction between the group-mean (Equation 30.35b) and neighborhood-fitness (Equation 30.35a) models is apparent in the case where only the neighbors influence the fitness of an individual. In this case, $ \beta_1 = 0 $, $ \beta_2 \neq 0 $, so that in the neighborhood-fitness model there is no weight on individual value. However, if a group-mean fitness model is fitted to these same data, there will be a nonzero regression slope on individual fitness (a value of $ -\beta_2 $), reflecting the input of an individual's value to its group mean. One could also weight the interactions in Equation 30.30a, for example, by replacing $ z_j $ with $ f_{ij}z_j $, where $ f_{ij} $ is some measure of the amount of interaction between i and j, such as distance between plants or fraction of time observed interacting (Chapter 22).


---

## chapter30_042 · Measuring Multivariate Selection: Introduction / Selection Can Be Antagonistic Across Levels

When selection is operating at both the individual and group levels, there is no a priori reason why its direction should be the same at the two levels. When the direction is the same and group-level effects are ignored, the effects of individual selection are overestimated. The more interesting case is that in which individual and group-level selection are antagonistic, working in opposite directions. Example 30.12 illustrates both cases: for height, selection at both levels was in the same direction, while for stem number, selection was in opposite directions at the individual and group levels. Antagonistic selection is commonly seen in the limited number of studies that have estimated multilevel selection components, although this might, in part, be due to a bias in initially choosing traits that are expected to be under differential individual, versus group, selection pressure.

One of the first applications of contextual analysis to levels-of-selection was by Stevens et al. (1995), using jewelweed (Impatiens capensis). They found that an overall measure of size was selected to decrease at the group level but to increase at the individual level. This pattern was observed when fitness was taken as either survival rate to two years or as seed production in open-pollinated cleistogamous flowers. The individual and group partial regression slopes (variance-standardized over trait values) for survival rate on overall size were $ \beta_{I}=1.74 $ and $ \beta_{group}=-3.03 $. Hence, group selection was stronger (and of opposite sign) than individual selection. The partial regression slopes for cleistogamous seed production on size were $ \beta_{I}=0.51 $ and $ \beta_{group}=-0.52 $. Similar observations were made by Weinig et al. (2007), who used a set of recombination inbred lines (RILs) in Arabidopsis thaliana, and found that two composite traits (size and elongation) were favored to increase under individual selection but to decrease under group selection. For both traits, individual selection was stronger than group selection (the variance-standardized $ \beta $ values were roughly twice as large). A final example is a study by Tsuji (1995), who worked with the Japanese queenless ant (Pristomyrnex pungens), an unusual species with no queens, whose workers are able to reproduce parthenogenetically. Larger size was favored at the individual level ($ \beta_{I}=0.07 $), but selected against at the colony level ($ \beta_{group}=-0.11 $).

---

## chapter30_043 · Measuring Multivariate Selection: Introduction / Group Selection Is Likely Density-Dependent

A number of workers (Goodnight et al. 1992; Donohue 2003, 2004) have suggested that at low density, group selection may be weak (or essentially absent), with individual selection dominating. As group density increases, so does competition, which may increase group effects. An empirical observation from plant ecology, the law of constant final yield (Harper 1977; Weiner and Freckleton 2010), has been offered as support for this view (Goodnight et al. 1992). Plant ecologists have noted that the total yield of a group initially increases with low density, but after a certain critical density is reached, the total biomass of the group remains roughly constant. Even though more plants are now in the group, their individual contribution has decreased. Goodnight et al. suggested that this law results from a balance between group and individual selection. One consequence of potential density-dependence at the group level is that an analysis of individual selection that ignores a group selection component can be mistaken for frequency-dependent selection (Uyenonyama and Feldman 1980, 1981; Damuth and Heisler 1988).

Working with the Great Lake sea rocket (Cakile edentual), a plant in the family Brassicaceae, Donohue (2004) did indeed observe that plant density influenced the relative strengths of individual and group selection. For plant height and stem mass, she observed antagonistic individual and group selection at varying densities, with individual selection favoring smaller plants with more stem mass, and group selection favoring larger plants with less stem mass. At all densities, individual selection remained significantly stronger than group selection. Surprisingly, group selection was strongest at the intermediate, as opposed to the high, density. Weinig et al. (2007) also found a density-dependent effect in Arabidopsis thaliana, where the density must be above some threshold before group selection becomes important.

---

## chapter30_044 · Measuring Multivariate Selection: Introduction / Selection Differentials Can Be Misleading in Levels of Selection

**[推导 Derivation]**

Price (1972a) and Wade (1985) showed how to decompose the selection differential into individual and group components. They did so by using the Robertson-Price identity (Equation 6.10), which states that the within-generation change in a trait can be written as its covariance with relative fitness, $ S = \sigma(w, z) $. This also holds more generally for levels of selection. Suppose we let $ w_{ij} $ and $ z_{ij} $ denote, respectively, the fitness and phenotype of the jth individual in group i. Using the definition of the covariance, Price showed that the total selection differential can be decomposed as

> **Formula (30.36)** · `30.36` · source: `chapter30_block_200` · Selection Differentials Can Be Misleading in Levels of Selection
>
> $$ \sigma(z,w)=E_{i}\left[\sigma(w_{ij},z_{ij})\right]+\sigma(\overline{z}_{i},\overline{w}_{i}) $$


The first term is the covariance between individual phenotype and fitness within a group, and we take its average over all groups to obtain the within-group covariance between individual value and fitness. The second term is the covariance between the mean trait value, $ \overline{z}_{i} $, and the mean fitness, $ \overline{w}_{i} $, of the group. Equation 30.36 decomposes the selection differential into components from individual effects within groups and components from group effects.

**[定义 Definition]**

Motivated by Equation 30.36, Price suggested that group selection implies a nonzero covariance between the mean trait value and mean fitness of groups, namely, $ \sigma(\overline{z}_i, \overline{w}_i) \neq 0 $. Under this definition, group selection cannot occur if there are no among-group differences in mean fitness. While this sounds reasonable, as we will see shortly, there are indeed situations where each group has the same mean fitness but there is still selection on the group means. Hence, group selection can occur even when the covariance between mean trait value and mean fitness is zero. Likewise, even when there is selection only on individual phenotypes, if group means differ, then (as we will show shortly) one can easily get a nonzero value for $ \sigma(\overline{z}_i, \overline{w}_i) $.

**[定义 Definition]**

Hence, this covariance definition (a nonzero group selection differential) for group selection is misleading, as one can have a group selection differential of zero when group selection is occurring, and a nonzero group selection differential when it is not. The root cause of this is a familiar problem: selection on phenotypically correlated traits can modify the selection differential of a focal trait, in the extreme showing an indirect response (nonzero S) when there is no direct selection on the trait. This also applies when considering selection differentials on group means. Indeed, by analogy to using a multiple regression to control for correlated traits, this was the motivation of Heisler and Damuth (1987; also Goodnight et al. 1992) for using contextual analysis. The partial regression coefficients in a contextual analysis control for any indirect effects of other correlated traits included within the analysis.

**[推导 Derivation]**

One consequence of indirect effects generating nonzero covariances (and hence nonzero selection differentials) is that an analysis restricted to one level of selection can be misleading. For example, suppose an investigator assumes that group selection might be important, and therefore only includes group means in the analysis. For a single trait, the investigator might consider the slope of a simple (i.e., univariate) regression of mean fitness on group trait mean,

> **Formula (30.37a)** · `30.37a` · source: `chapter30_block_204` · Selection Differentials Can Be Misleading in Levels of Selection
>
> $$ \overline{w}_{i}=1+\beta\overline{z}_{i}+e_{i} $$


**[推导 Derivation]**

If we recall (LW Chapter 3) that the slope of a univariate regression is the covariance divided by variance of the predictor variable, the slope becomes

> **Formula (30.37b)** · `30.37b` · source: `chapter30_block_205` · Selection Differentials Can Be Misleading in Levels of Selection
>
> $$ \beta=\frac{\sigma(\overline{z}_{i},\overline{w}_{i})}{\sigma^{2}(\overline{z}_{i})} $$


Hence, a nonzero covariance implies a nonzero slope, and an investigator using this simple univariate regression would conclude that group selection is occurring on this trait. In reality, as we will see shortly, strict individual selection can generate a group-level covariance, and hence (in this case), a spurious assignment of a group-level effect to selection. By using a multiple regression that includes both individual and group mean values, a contextual analysis corrects for this concern (provided selection is limited to only these two levels).

**[Table]**

> **Table 30.2** · `30.2` · page 53 · source: `chapter30_044`
> Table 30.2 Hard, soft, and strict group selection can all be expressed as special cases of a more general contextual analysis. Model 1 presents the contextual regression coefficients (Equation 30.38a) on individual value  $ (z_{ij}) $ and group mean  $ (\overline{z}_i) $. Model 2 presents the regression coefficients when the contextual analysis is framed in terms of within-group deviations and group means (Equation 30.38b). To contrast these results with those from the covariance criteria for group selection, the table also shows whether the type of selection results in a nonzero within-group  $ (S_w) $ or among-group  $ (S_b) $ selection differential and whether the among-group variance in mean fitness,  $ \sigma^2(\overline{w}_i) $, is nonzero.
>
> <table><tr><td></td><td colspan="2">Model 1</td><td colspan="2">Model 2</td><td rowspan="2">$ S_{w} \neq 0 $</td><td rowspan="2">$ S_{b} \neq 0 $</td><td rowspan="2">$ \sigma^{2}(\overline{w}_{i}) &gt; 0 $</td></tr><tr><td>Selection</td><td>$ z_{ij} $</td><td>$ \overline{z}_{i} $</td><td>$ (z_{ij} - \overline{z}_{i}) $</td><td>$ \overline{z}_{i} $</td></tr><tr><td>Hard</td><td>$ \beta $</td><td>0</td><td>$ \beta $</td><td>$ \beta $</td><td>Yes</td><td>Yes</td><td>Yes</td></tr><tr><td>Soft</td><td>$ \beta $</td><td>$ -\beta $</td><td>$ \beta $</td><td>0</td><td>Yes</td><td>No</td><td>No</td></tr><tr><td>Strict group</td><td>0</td><td>$ \beta $</td><td>0</td><td>$ \beta $</td><td>Yes</td><td>Yes</td><td>Yes</td></tr></table>


The use of selection differentials correctly determined the presence of positive directional selection on both individual height and stem number. However, the analysis also suggested that there were no among-patch effects (no selection on patch means), when in fact contextual analysis shows that these effects are highly significant for both traits (Example 30.12).

---

## chapter30_045 · Measuring Multivariate Selection: Introduction / Hard, Soft, and Group Selection: A Contextual Analysis Viewpoint

Evolutionary biology has had an unfortunate history of, at times, being constrained by thinking about complex evolutionary processes in terms of simple catch phrases. We have seen examples of this with kin versus group selection, showing in Chapter 22 that these are special cases of the more general problem of selection with interacting individuals. Likewise, in this (and the previous) chapter, we have seen that the widely used terms of stabilizing and disruptive selection are special cases of the more general situation of a quadratic term (curvature) in the individual fitness surface. It should therefore not be surprising that there is some confusion with the exact meaning of group selection in the more general context of multilevel selection (reviewed by Okasha 2004, 2006). In the Price covariance framework, group selection is indicated by a nonzero covariance between the mean fitness and the mean trait value of a group, $ \sigma(\overline{z}_i, \overline{w}_i) \neq 0 $. This line of reasoning implies that across groups there must be variance in mean fitness, $ \sigma^2(\overline{w}_i) \neq 0 $, for group selection to exist. However, as stressed by Goodnight et al. (1992; Goodnight 2013, 2015), these covariance conditions for defining group selection are misleading. One can have group selection in the absence of variance in mean fitness across groups, and likewise, strict individual selection can still generate a covariance between group mean fitness and group mean trait value.

Just as the more general framework of selection in interacting populations removes much of the historical confusion between group selection and kin selection (Chapter 22), multilevel selection removes much of the confusion over whether group selection is occurring. Under multilevel selection, we simply have the fact that the fitness of a focal individual is influenced by other individuals, and hence selection has both individual and group components. The latter are very clearly defined by nonzero regression coefficients on group traits in a contextual analysis. As succinctly stated by Goodnight et al. (1992), “with contextual analysis, whether selection is acting at a particular level becomes a statistical rather than a philosophical question.”

**[推导 Derivation]**

Wallace’s (1968, 1976) distinction between hard and soft selection serves to highlight the differences between the covariance and multiple-regression definitions of group selection (Goodnight et al. 1992). Hard selection occurs when the fitness of a focal individual is solely determined by its phenotype and is unaffected by any group members. This results in the mean fitness of groups differing, with some groups leaving more offspring than others, as by chance, some groups are compromised of more fit individuals than others. Conversely, soft selection occurs when each group contributes equally to the next generation, which means that group mean fitness is a constant and there is no variance in mean fitness among groups. The law of constant yield is an example of soft selection, with fitness (number of seeds) being largely independent of patch density. Figure 30.17 shows the different consequences of hard, soft, and (strict) group selection on the within- and among-group regressions of phenotype on fitness. As summarized in Table 30.2, hard, soft, and strict group selection can all be modeled as special cases of a contextual analysis regression. For simplicity, we focus on a single trait, and the resulting regression has the form

> **Formula (30.38a)** · `30.38a` · source: `chapter30_block_211` · Hard, Soft, and Group Selection: A Contextual Analysis Viewpoint
>
> $$ w_{ij}=1+\beta_{1}z_{ij}+\beta_{2}\overline{z}_{i}+e_{ij} $$


**[推导 Derivation]**

We can also rewrite this regression in terms of selection on the within-group deviation plus selection on the group means,

> **Formula (30.38b)** · `30.38b` · source: `chapter30_block_212` · Hard, Soft, and Group Selection: A Contextual Analysis Viewpoint
>
> $$ w_{ij}=1+\beta_{1}^{*}\left(z_{ij}-\overline{z}_{i}\right)+\beta_{2}^{*}\overline{z}_{i}+e_{ij} $$


**[推导 Derivation]**

We use $ \beta_{i}^{*} $ to stress to the reader that the regression coefficients in Equation 30.38b can differ from those in Equation 30.38a. To see the connection, note that

> **Formula (30.38c)** · `30.38c` · source: `chapter30_block_214` · Hard, Soft, and Group Selection: A Contextual Analysis Viewpoint
>
> $$ w_{ij}=1+\beta_{1}^{*}z_{ij}+\left(\beta_{2}^{*}-\beta_{1}^{*}\right)\overline{z}_{i}+e_{ij} $$


showing that $ \beta_{1} $ is the same under both models $ (\beta_{1}=\beta_{1}^{*}) $, while $ \beta_{2}=\beta_{2}^{*}-\beta_{1}^{*} $.

Hard selection occurs when selection is entirely on individual value, so that $ \beta_{2}=0 $ and hence there is no group component to multilevel selection. However, by chance, some groups will have more high-fitness individuals than others. This generates variance in group mean fitness and a nonzero covariance between group-mean trait values and mean fitness (Goodnight et al. 1992). Under this covariance criteria, one would infer group selection, even though it is absent. Here, a nonzero among-group selection differential arises as a correlated response to direct selection on individual value. In this simple case, the contextual analysis clearly shows no multilevel selection, but a simple univariate regression might suggest otherwise (e.g., Equation 30.37a).

**[推导 Derivation]**

The opposite conclusion arises with soft selection. Here selection is entirely based on within-group deviations (such as within-family selection; Chapter 21). Hence, $ \beta_{1} = -\beta_{2} $ as the regression of fitness becomes

> **Formula (30.39a)** · `30.39a` · source: `chapter30_block_216` · Hard, Soft, and Group Selection: A Contextual Analysis Viewpoint
>
> $$ \begin{aligned}w_{ij}&=1+\beta\left(z_{ij}-\overline{z}_{i}\right)+e_{ij}\\&=1+\beta z_{ij}-\beta\overline{z}_{i}+e_{ij}\end{aligned} $$


**[定义 Definition]**

Under soft selection, there is no variation in mean fitness across groups and $ \sigma(\overline{z}_i, \overline{w}_i) = 0 $. Hence, under Price's covariance definition, one might infer that there was no group selection. However, there is clearly multilevel selection occurring, as $ \beta_2 \neq 0 $ (cf. Equation 30.38a and Equation 30.39a). The lack of among-group variance in fitness shows that the effects of individual selection at the group level are exactly countered by selection at the group level.

**[推导 Derivation]**

Finally, consider strict group selection, when an individual’s fitness is entirely a function of its group mean,

> **Formula (30.39b)** · `30.39b` · source: `chapter30_block_218` · Hard, Soft, and Group Selection: A Contextual Analysis Viewpoint
>
> $$ w_{ij}=1+\beta\overline{z}_{i}+e_{ij} $$


while written here as a univariate regression, formally we have $ \beta_1 = 0 $ if the regression given by Equation 30.38a is fitted. If one simply fits an individual selection model ($ w_{ij} = 1 + \beta z_{ij} + e_{ij} $), there is a nonzero regression slope if group effects are ignored, and hence $ E_i[\sigma(w_{ij}, z_{ij})] \neq 0 $ (Goodnight et al 1992). Again this occurs because individual value and group mean are correlated, as $ \sigma(z_{ij}, \overline{z}_i) = \sigma_z^2 / n $ (plus addition terms if group members are correlated; see Equation 22.25b). Hence, direct selection on one results in indirect selection (and hence a covariance) in the other. With contextual analysis, we reach the correct conclusion of selection only on group values.

---

## chapter30_046 · Measuring Multivariate Selection: Introduction / Early Survival: Offspring or Maternal Fitness Component?

As mentioned in Chapters 15 and 22, a classic example of a levels-of-selection problem is maternal care, wherein features of both the mother and offspring may influence offspring survival. An area of some contention, especially among biologists working with species that display extensive maternal care (i.e., ornithologists and mammalianogists), is whether the fitness associated with early survival should be assigned to the mother (acknowledging her maternal performance) or to the offspring (acknowledging features of their own that enhance survival). As mentioned in Chapter 29, the fitness of a mother is often scored as the number of her offspring remaining after some interval of potential early offspring mortality, rather than simply the total number of offspring that she produced. For birds, the number of hatchlings, fledglings, or recruits (offspring that have mated) are used as the measure of female fitness, rather than the number of eggs. In mammals, the number of weaned offspring or recruits is often used in place of number of births. This notion of fitness crossing generations has proponents (e.g., Clutton-Brock 1988) and opponents (Arnold 1983a; Lande and Arnold 1983; Cheverud 1984b; Thomson and Hadfield 2017), in part because different questions are being asked by the two sides. The implications of assigning fitnesses of offspring to their mothers (i.e., their early survival is part of their mother's fitness), and what potential biases this may induce, were examined by Wolf and Wade (2009; also see Thomson and Hadfield 2017), whose approach we closely follow.

**[推导 Derivation]**

Suppose the true fitness (such as early offspring survival) is a function of the offspring phenotype, $ z_{o(t)} $, and the value of some trait in their mother, $ z_{m(t-1)} $, where t indexes the current offspring generation and t - 1 indexes a phenotype (in this case its mother) in the previous generation. This is an example of what Kirkpatrick and Lande (1989) called maternal selection (Chapter 15). The relative fitness of a male offspring is given by

> **Formula (30.40a)** · `30.40a` · source: `chapter30_block_220` · Early Survival: Offspring or Maternal Fitness Component?
>
> $$ w_{(t)}[male]=\alpha_{(t)}+b_{m}z_{m(t-1)}+b_{o}z_{o(t)}+\epsilon_{(t)} $$


where $ b_{o} $ and $ b_{m} $ measure the strengths of selection on offspring value and maternal care, respectively. In female offspring, there is an additional source of potential selection, as a sex-limited maternal trait can have a cost. For example, a mother with a trait for increased foraging enhances the survival of her offspring, but also increases her own risk of predation. Incorporating the direct cost $ (b_{d}) $ of such a trait in females yields

> **Formula (30.40b)** · `30.40b` · source: `chapter30_block_220` · Early Survival: Offspring or Maternal Fitness Component?
>
> $$ \begin{align*}w_{(t)}\left[\mathsf{f e m a l e}\right]=\alpha_{(t)}+b_{m}z_{m(t-1)}+b_{d}z_{m(t)}+b_{o}z_{o(t)}+\epsilon_{(t)}\end{align*} $$


**[推导 Derivation]**

Figure 30.18A presents the path diagram for this fitness model. If we assume that Equations 30.40a and 30.40b represent the correct fitness model, the selection differential, $ S_{m} $, on the maternal trait value, $ z_{m} $, can be computed from the Robertson-Price identity (Equation 6.10). Because $ w(t) $ depends on whether the offspring is male or female, we let $ \delta_{f} $ be a zero (for male) or one (for female) indicator variable. Equations 30.40a, 30.40b and 6.10 yield

> **Formula (30.40c)** · `30.40c` · source: `chapter30_block_221` · Early Survival: Offspring or Maternal Fitness Component?
>
> $$ \begin{aligned}S_{m}(\mathrm{off})&=\sigma(w_{(t)},z_{m(t)})\\&=\sigma\big(b_{m}z_{m(t-1)}+\delta_{f}b_{d}z_{m(t)}+b_{o}z_{o(t)},z_{m(t)}\big)\\&=b_{m}\sigma(z_{m(t-1)},z_{m(t)})+\delta_{f}b_{d}\sigma(z_{m(t)},z_{m(t)})+b_{o}\sigma(z_{o(t)},z_{m(t)})\\ \end{aligned} $$


Because the total differential is the weighted average over both sexes (Equation 13.5),

> **Formula (30.40d)** · `30.40d` · source: `chapter30_block_221` · Early Survival: Offspring or Maternal Fitness Component?
>
> $$ \begin{align*}S_{m}(\mathrm{off})&=b_{m}\sigma(z_{m(t-1)},z_{m(t)})+\frac{b_{d}}{2}\sigma(z_{m(t)},z_{m(t)})+b_{o}\sigma(z_{o(t)},z_{m(t)})\\&=\frac{b_{m}}{2}\sigma^{2}(A_{m})+\frac{b_{d}}{2}\sigma^{2}(z_{m})+b_{o}\sigma(A_{m},A_{o})\end{align*} $$


This last step assumes that $ \sigma(z_{o(t)}, z_{m(t)}) = \sigma(A_{o(t)} + e_{o(t)}, A_{m(t)} + e_{m(t)}) = \sigma(A_{m}, A_{o}) $, namely, that the environment effects between the maternal and direct effects are uncorrelated within an individual.

**[推导 Derivation]**

Now suppose that an investigator assumes the offspring fitness is assigned to its mother (Figure 30.18B), which Thomson and Hadfield (2017) call the mixed-fitness model. The mother's total fitness can be considered as the sum of two separate episodes: selection on early survival in her offspring, $ w_{o(t)} $, and selection on her maternal trait, $ w_{m(t-1)} $, where

> **Formula (30.41a)** · `30.41a` · source: `chapter30_block_223` · Early Survival: Offspring or Maternal Fitness Component?
>
> $$ w_{o(t)}=\alpha_{o(t)}+b_{m}z_{m(t-1)}+b_{o}z_{o(t)}+\epsilon_{(t)} $$


> **Formula (30.41b)** · `30.41b` · source: `chapter30_block_223` · Early Survival: Offspring or Maternal Fitness Component?
>
> $$ w_{m(t-1)}=\alpha_{m(t-1)}+b_{d}z_{m(t-1)}+\epsilon_{(t-1)} $$


giving her total fitness as $$ w_{o(t)}+w_{m(t-1)}=\left(\alpha_{o(t)}+\alpha_{m(t-1)}\right)+b_{m}z_{m(t-1)}+b_{d}z_{m(t-1)}+b_{o}z_{o(t)}+\left(\epsilon_{(t)}+\epsilon_{(t-1)}\right) $$

**[推导 Derivation]**

The difference between this expression (mother-assigned offspring early-viability fitness) and Equation 30.40b (offspring assigned their own fitness) is in the direct fitness of the maternal effect. This component is weighted by $ b_{m}z_{m(t-1)} $ in Equation 30.41c (the value of the mother), and by $ b_{m}z_{m(t)} $ in Equation 30.40b (the cost to the offspring). Following the same logic leading to Equation 30.40d, the selection differential on the maternal trait becomes

> **Formula (30.41d)** · `30.41d` · source: `chapter30_block_224` · Early Survival: Offspring or Maternal Fitness Component?
>
> $$ \begin{aligned}S_{m}(\mathrm{mother})&=\sigma(w_{o(t)}+w_{m(t-1)},z_{m(t-1)})\\&=\frac{1}{2}\Biggl[(b_{m}+b_{d})\sigma^{2}(z_{m})+b_{o}\sigma(z_{o(t)},z_{m(t-1)})\Biggr]\\&=\frac{1}{2}\Biggl[(b_{m}+b_{d})\sigma^{2}(z_{m})+b_{o}\frac{\sigma^{2}(A_{m},A_{o})}{2}\Biggr]\\ \end{aligned} $$


**[推导 Derivation]**

Subtracting Equation 30.41d from Equation 30.40d yields

> **Formula (30.42)** · `30.42` · source: `chapter30_block_225` · Early Survival: Offspring or Maternal Fitness Component?
>
> $$ S_{m}(\mathrm{mother})-S_{m}(\mathrm{off})=\frac{b_{m}}{2}\left[\sigma^{2}(z_{m})-\sigma^{2}(A_{m})\right]-\frac{3}{4}b_{o}\sigma(A_{m},A_{o}) $$


The first term shows that maternal selection is overestimated by assigning fitness to mothers, as only a fraction (the additive variance, $ \sigma^2[A_m] $) of the total maternal trait variation, $ \sigma^2(z_m) $, is passed to the offspring. The second term either reduces this overestimation or amplifies it, depending the sign of the genetic covariance between the maternal trait and the offspring trait. Wolf and Wade (2001) stated that there is no reason to expect that these terms will largely cancel, making estimates of maternal selection when offspring fitness is assigned to mothers problematic in many cases.

Conversely, Equation 30.42 shows the conditions under which assigning fitnesses to mothers is unbiased. First, the maternal and offspring traits must be uncorrelated $$ \sigma\left(z_{o(t)},z_{m(t)}\right)=0 $$ implying that $ \sigma(A_m, A_o) = 0 $, provided that $ \sigma(e_o, e_m) = 0 $. Second, and more problematic, the maternal trait must have a very high heritability, such that $ \sigma^2(z_m) \simeq \sigma^2(A_m) $. As a result, as Wolf and Wade (2001) suggested, assigning offspring viability as a component of offspring fitness is less biased. Thomson and Hadfield (2017) echoed this point, noting that the conditions are even more restrictive for the mixed-fitness model to be unbiased if the parental trait influencing offspring fitness (upon which selection against the parent can occur) is not sex-limited. They also note that roughly 40% of fecundity estimates in the literature (mainly from birds and mammals) are based on mixed-fitness estimates (namely, weighted by some concept of offspring survival).

Both sets of authors pointed out that unless a fitness regression of the form given by Equation 30.40b is used, the levels-of-selection impact from a parent can easily be missed. Unfortunately, this requires one to either know, or at least have a good idea of, the potential parental traits that impact offspring survival. By using a list of such candidate traits, one can fit regressions of this form to test which traits (if any) have a significant impact on offspring fitness.

---
