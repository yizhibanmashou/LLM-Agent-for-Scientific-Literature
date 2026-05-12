# Appendix 6 Textbook Mapping

## appendix6_001 · Appendix: Introduction

Mathematics is a collection of cheap tricks and dirty jokes. Lipman Bers

Quantitative genetics often deals with vector-valued functions, and here we provide a brief review of the calculus of such functions. In particular, we review common expressions for derivatives of vectors and vector-valued functions, introduce the gradient vector and Hessian matrix (for first and second partials, respectively), and use this machinery in multidimensional Taylor series for approximating functions around a specific value. We apply these results to several problems in selection theory and evolution.

---

## appendix6_002 · Appendix: Introduction / DERIVATIVES OF VECTORS AND VECTOR-VALUED FUNCTIONS

Suppose we let $f(\mathbf{x})$ be a scalar (single-dimension) function of a column vector, $\mathbf{x} = (x_1, \cdots, x_n)^T$, of $n$ variables. The gradient (or gradient vector) of $f$ with respect to $\mathbf{x}$ is obtained by taking partial derivatives of the function with respect to each variable. In matrix notation, the gradient operator is denoted by $$ \nabla\mathbf{x}[f]=\frac{\partial f}{\partial\mathbf{x}}=\begin{pmatrix}\frac{\partial f}{\partial x_{1}}\\ \vdots\\ \frac{\partial f}{\partial x_{n}}\end{pmatrix} $$

The gradient at a point, $ x_{o} $, corresponds to a vector indicating the direction of local steepest ascent of the function at that point (the multivariate slope of $ f $ at $ x_{o} $).

**[示例 Example]**

> **Example A6.1** · ref: `A6.1` · source: `appendix6_002.json` · blocks 2–2
>
> Example A6.1. For an $ n \times 1 $ column vector, x, compute the gradient for $$ \begin{align*}f(\mathbf{x})=\sum\limits_{i=1}^n x_i^2=\mathbf{x}^T\mathbf{x}\end{align*} $$ Because $\partial f/\partial x_i = 2x_i$, the gradient vector is just $\nabla_{\mathbf{x}}[f(\mathbf{x})] = 2\mathbf{x}$. At the point $\mathbf{x}_o$, $\mathbf{x}^T \mathbf{x}$ locally increases most rapidly if we change $\mathbf{x}$ in the same direction as the vector going from point $\mathbf{x}_o$ to point $\mathbf{x}_o + 2\delta \mathbf{x}_o = (1 + 2\delta) \mathbf{x}_o$, where $\delta$ is a small positive value.
> 
> Now consider an $ m \times n $ matrix, A, of constants. What is the derivative of the $ n \times 1 $ column vector Ax with respect to x? Recall from the definition of matrix multiplication that the ith element of Ax is $$ \begin{align*}(\mathbf{A}\mathbf{x})_i=\sum\limits_{j=1}^n A_{ij}x_j,\quad\textrm{yielding}\quad\partial(\mathbf{A}\mathbf{z})_i/\partial x_k=A_{ik}\end{align*} $$
> 
> Hence, the $i$th element of $\nabla_{\mathbf{X}}[\mathbf{A}\mathbf{x}]_{k}$ is $(A_{1k} \quad A_{2k} \quad \cdots \quad A_{mk})$, namely the transpose of the $k$th column of $\mathbf{A}$, which yields $\nabla_{\mathbf{X}}[\mathbf{A}\mathbf{x}] = \mathbf{A}^{T}$.
> 
> For a vector (a) and a matrix (A) of constants, using the same logic as in Example A6.1, it can be shown (e.g., Morrison 1976; Graham 1981; Searle 1982) that $$ \nabla_{\mathbf{x}}\left[\mathbf{a}^{T}\mathbf{x}\right]=\nabla_{\mathbf{x}}\left[\mathbf{x}^{T}\mathbf{a}\right]=\mathbf{a} $$ $$ \nabla_{\mathbf{x}}\left[\mathbf{A}\mathbf{x}\right]=\mathbf{A}^{T} $$
> 
> Turning to quadratic forms, if A is symmetric ($ A = A^{T} $), then $$ \nabla_{\mathbf{x}}\left[\mathbf{x}^{T}\mathbf{A}\mathbf{x}\right]=2\mathbf{A}\mathbf{x} $$ $$ \nabla_{\mathbf{x}}\left[\left(\mathbf{x}-\mathbf{a}\right)^{T}\mathbf{A}(\mathbf{x}-\mathbf{a})\right]=2\mathbf{A}(\mathbf{x}-\mathbf{a}) $$ $$ \nabla_{\mathbf{x}}\left[\left(\mathbf{a}-\mathbf{x}\right)^{T}\mathbf{A}(\mathbf{a}-\mathbf{x})\right]=-2\mathbf{A}(\mathbf{a}-\mathbf{x}) $$
> 
> Taking A = I, Equation A6.1c implies $$ \nabla_{\mathbf{x}}\left[\mathbf{x}^{T}\mathbf{x}\right]=\nabla_{\mathbf{x}}\left[\mathbf{x}^{T}\mathbf{I}\mathbf{x}\right]=2\mathbf{I}\mathbf{x}=2\mathbf{x} $$ as was found in Example A6.1. Two other useful identities follow from the chain rule of differentiation, namely, $$ \nabla_{\mathbf{x}}\left[\exp\{f(\mathbf{x})\}\right]=\exp[f(\mathbf{x})]\nabla_{\mathbf{x}}\left[f(\mathbf{x})\right] $$ $$ \nabla_{\mathbf{x}}\left[\ln[f(\mathbf{x})]\right]=\frac{1}{f(\mathbf{x})}\cdot\nabla_{\mathbf{x}}\left[f(\mathbf{x})\right] $$
> 
> Finally, the product rule also applies to a gradient, with $$ \nabla_{\mathbf{X}}\left[f(\mathbf{x})g(\mathbf{x})\right]=\nabla_{\mathbf{X}}\left[f(\mathbf{x})\right]g(\mathbf{x})+f(\mathbf{x})\nabla_{\mathbf{X}}\left[g(\mathbf{x})\right] $$


**[示例 Example]**

> **Example A6.2** · ref: `A6.2` · source: `appendix6_002.json` · blocks 3–3
>
> Example A6.2. The density function $ \varphi(\mathbf{x}, \boldsymbol{\mu}, \mathbf{V}) $ for a multivariate normal (MVN) distribution returns a scalar value and is a function of the data vector, $ \mathbf{x} $, the vector of means, $ \boldsymbol{\mu} $, and the covariance matrix, $ \mathbf{V} $, $$ \varphi(\mathbf{x},\boldsymbol{\mu},\mathbf{V})=a\exp\left(-\frac{1}{2}\cdot(\mathbf{x}-\boldsymbol{\mu})^{T}\mathbf{V}^{-1}(\mathbf{x}-\boldsymbol{\mu})\right) $$ where the constant $ a = \pi^{-n/2} |V|^{-1/2} $, and $ |V| $ denotes the determinant of $ V $. To compute the gradient of the MVN with respect to the data vector, $ x $, first apply Equation A6.1g to yield $$ \nabla_{\mathbf{X}}\left[\varphi(\mathbf{x},\boldsymbol{\mu},\mathbf{V})\right]=\varphi(\mathbf{x},\boldsymbol{\mu},\mathbf{V})\cdot\nabla_{\mathbf{X}}\left[\left(-\frac{1}{2}\right)\cdot(\mathbf{x}-\boldsymbol{\mu})^{T}\mathbf{V}_{\mathbf{X}}^{-1}\left(\mathbf{x}-\boldsymbol{\mu}\right)\right] $$


---

## appendix6_003 · Appendix: Introduction / DERIVATIVES OF VECTORS AND VECTOR-VALUED FUNCTIONS

Using this result along with Equation A6.1d returns $$ \nabla_{\mathbf{X}}\left[\varphi(\mathbf{x},\boldsymbol{\mu},\mathbf{V})\right]=-\varphi(\mathbf{x},\boldsymbol{\mu},\mathbf{V})\cdot\mathbf{V}^{-1}\left(\mathbf{x}-\boldsymbol{\mu}\right) $$

Similarly, Equation A6.1e implies that the gradient of the MVN with respect to the vector of means $ \mu $ is $$ \nabla_{\boldsymbol{\mu}}\left[\varphi(\mathbf{x},\boldsymbol{\mu},\mathbf{V})\right]=\varphi(\mathbf{x},\boldsymbol{\mu},\mathbf{V})\cdot\mathbf{V}^{-1}\left(\mathbf{x}-\boldsymbol{\mu}\right) $$

**[示例 Example]**

> **Example A6.3** · ref: `A6.3` · source: `appendix6_003.json` · blocks 2–2
>
> Example A6.3. Recall (Equations 13.27c and 30.5a) that when the distribution of phenotypes is multivariate normal, the directional selection gradient, $ \beta = \mathbf{P}^{-1}\mathbf{S} $, equals the gradient of log mean fitness with respect to the vector of trait means, $ \nabla \mu[\ln \widetilde{W}(\mu)] $ (Lande 1979a). Hence, the increase in the mean population fitness is maximized if mean character values change in the same direction as the vector $ \beta $. To see this, first note that applying Equation A6.1h yields $$ \nabla\mu[\ln\overline{W}(\mu)]=\overline{W}^{-1}\nabla\mu[\overline{W}(\mu)] $$ If we write mean fitness as $ \overline{W}(\boldsymbol{\mu}) = \int W(\mathbf{z}) \varphi(\mathbf{z}, \boldsymbol{\mu}) \, d\mathbf{z} $ and take the gradient through the integral, we obtain $$ \nabla\mu\left[\ln\overline{W}(\boldsymbol{\mu})\right]=\overline{W}^{-1}\nabla\mu\left[\int W(\mathbf{z})\varphi(\mathbf{z},\boldsymbol{\mu})\mathrm{d}\mathbf{z}\right]=\overline{W}^{-1}\int W(\mathbf{z})\nabla\mu\left[\varphi(\mathbf{z},\boldsymbol{\mu})\right]\mathrm{d}\mathbf{z} $$ The last identity follows from the assumption that $ W(\mathbf{z}) $ is not a function of the vector of trait means, $ \mu $, that is, the fitnesses are frequency-independent ($ \nabla \mu \left[W(\mathbf{z}) \right] = 0 $). If the trait vector $ \mathbf{z} \sim \text{MVN}(\mu, \mathbf{P}) $, Equation A6.2b yields $$ \nabla\boldsymbol{\mu}\left[\varphi(\mathbf{z},\boldsymbol{\mu})\right]=\varphi(\mathbf{z},\boldsymbol{\mu})\mathbf{P}^{-1}(\mathbf{z}-\boldsymbol{\mu}) $$
> 
> Hence, $$ \begin{aligned}\overline{W}^{-1}\int W(\mathbf{z})\nabla\boldsymbol{\mu}\left[\varphi(\mathbf{z},\boldsymbol{\mu})\right]\mathrm{d}\mathbf{z}&=\int w(\mathbf{z})\varphi(\mathbf{z},\boldsymbol{\mu})\mathbf{P}^{-1}(\mathbf{z}-\boldsymbol{\mu})\mathrm{d}\mathbf{z}\\&=\mathbf{P}^{-1}\left(\int\mathbf{z}w(\mathbf{z})\varphi(\mathbf{z},\boldsymbol{\mu})\mathrm{d}\mathbf{z}-\boldsymbol{\mu}\int w(\mathbf{z})\varphi(\mathbf{z},\boldsymbol{\mu})\mathrm{d}\mathbf{z}\right)\\&=\mathbf{P}^{-1}(\boldsymbol{\mu}^{*}-\boldsymbol{\mu})=\mathbf{P}^{-1}\mathbf{S}=\boldsymbol{\beta}\qquad(A6.2e)\end{aligned} $$ which follows because the first integral (in the second line above) is the mean character value after selection, $ \mu^* $, while the second integral equals one by definition, as $ E[w] = 1 $. If individual fitnesses are frequency-dependent (changing with $ \mu $), then, according to the product rule (Equation A6.1i), a second integral appears, and $ \nabla \mu \left[\ln \overline{W}(\mu) \right] $ now becomes $$ \overline{W}^{-1}\int W(\mathbf{z})\nabla_{\boldsymbol{\mu}}\left[\varphi(\mathbf{z},\boldsymbol{\mu})\right]\mathrm{d}\mathbf{z}+\overline{W}^{-1}\int\nabla_{\boldsymbol{\mu}}\left[W(\mathbf{z})\right]\varphi(\mathbf{z},\boldsymbol{\mu})\mathrm{d}\mathbf{z} $$ which yields $$ \nabla\mu[\ln\overline{W}(\mu)]=\beta+\overline{W}^{-1}\int\nabla\mu\left[W(\mathbf{z})\right]\varphi(\mathbf{z},\mu)\mathrm{d}\mathbf{z} $$


**[示例 Example]**

> **Example A6.4** · ref: `A6.4` · source: `appendix6_003.json` · blocks 3–3
>
> Example A6.4. Consider the ordinary least-squares solution for the general linear model, $ \mathbf{y} = \mathbf{X} \boldsymbol{\beta} + \mathbf{e} $, where $ \beta $ is the vector that minimizes the sum of squared residual errors, $ \sum e_i^2 $. In matrix form, this sum becomes $$ \begin{aligned}\sum_{i=1}^{n}e_{i}^{2}&=\mathbf{e}^{T}\mathbf{e}=(\mathbf{y}-\mathbf{X}\boldsymbol{\beta})^{T}(\mathbf{y}-\mathbf{X}\boldsymbol{\beta})\\&=\mathbf{y}^{T}\mathbf{y}-\boldsymbol{\beta}^{T}\mathbf{X}^{T}\mathbf{y}-\mathbf{y}^{T}\mathbf{X}\boldsymbol{\beta}+\boldsymbol{\beta}^{T}\mathbf{X}^{T}\mathbf{X}\boldsymbol{\beta}\\&=\mathbf{y}^{T}\mathbf{y}-2\boldsymbol{\beta}^{T}\mathbf{X}^{T}\mathbf{y}+\boldsymbol{\beta}^{T}\mathbf{X}^{T}\mathbf{X}\boldsymbol{\beta}\end{aligned} $$ and the last step follows because the matrix product $ \beta^{T} X^{T} y $ yields a scalar, and hence equals its transpose, $$ \boldsymbol{\beta}^{T}\mathbf{X}^{T}\mathbf{y}=\left(\boldsymbol{\beta}^{T}\mathbf{X}^{T}\mathbf{y}\right)^{T}=\mathbf{y}^{T}\mathbf{X}\boldsymbol{\beta} $$
> 
> To find the vector $ \beta $ that minimizes $ e^T e $, we take the derivative with respect to $ \beta $ and use Equations A6.1a–A6.1c, which yields $$ \nabla_{\boldsymbol{\beta}}\left[\mathbf{e}^{T}\mathbf{e}\right]=\frac{\partial\mathbf{e}^{T}\mathbf{e}}{\partial\boldsymbol{\beta}}=-2\mathbf{X}^{T}\mathbf{y}+2\mathbf{X}^{T}\mathbf{X}\boldsymbol{\beta} $$
> 
> Setting this equal to zero yields $ \mathbf{X}^T\mathbf{X}\boldsymbol{\beta} = \mathbf{X}^T\mathbf{y} $, which (provided the inverse of $ \mathbf{X}^T\mathbf{X} $ exists) has a solution of $$ \boldsymbol{\beta}=\left(\mathbf{X}^{T}\mathbf{X}\right)^{-1}\mathbf{X}^{T}\mathbf{y} $$ More generally, if $ \mathbf{X}^T \mathbf{X} $ is singular, we can still solve this equation by using a generalized inverse $ \left(\mathbf{X}^T \mathbf{X}\right)^{-} $; see LW Appendix 3.


**[示例 Example]**

> **Example A6.5** · ref: `A6.5` · source: `appendix6_003.json` · blocks 4–4
>
> Example A6.5. Here we present one derivation of Henderson's mixed-model equations (Equation 19.4). Consider the mixed model $ \mathbf{y} = \mathbf{X}\beta + \mathbf{Z}\mathbf{u} + \mathbf{e} $, where $ \mathbf{e} \sim \text{MVN}(0, \mathbf{R}) $, $ \mathbf{u} \sim \text{MVN}(0, \mathbf{G}) $, and $ \mathbf{e} $ and $ \mathbf{u} $ are independent (Equation 19.1). If we recall the probability density function for a multivariate normal (Example A6.2), we have that $$ p(\mathbf{e})\propto|\mathbf{R}|^{-1/2}\cdot\exp\left[-\frac{1}{2}\mathbf{e}^{T}\mathbf{R}^{-1}\mathbf{e}\right]\quad and\quad p(\mathbf{u})\propto|\mathbf{G}|^{-1/2}\cdot\exp\left[-\frac{1}{2}\mathbf{u}^{T}\mathbf{G}^{-1}\mathbf{u}\right] $$
> 
> We can further note that the conditional distribution of y given u is
> 
> Hence, $$ \left(\mathbf{y}-\mathbf{X}\boldsymbol{\beta}-\mathbf{Z}\mathbf{u}\right)\left|\mathbf{u}=\mathbf{e}\sim\mathrm{M V N}(0,\mathbf{R})\right. $$ $$ p(\mathbf{y},\mathbf{u})=p(\mathbf{y}|\mathbf{u})\cdot p(\mathbf{u})=p(\mathbf{e})\cdot p(\mathbf{u}) $$ with the last step following because e and u are independent. From Equation A6.4a, $$ p(\mathbf{y},\mathbf{u})\propto $$ $$ \left|\mathbf{R}\right|^{-1/2}\left|\mathbf{G}\right|^{-1/2}\cdot\exp\left[-\frac{1}{2}\left(\mathbf{y}-\mathbf{X}\boldsymbol{\beta}-\mathbf{Z}\mathbf{u}\right)^{T}\mathbf{R}^{-1}\left(\mathbf{y}-\mathbf{X}\boldsymbol{\beta}-\mathbf{Z}\mathbf{u}\right)-\frac{1}{2}\mathbf{u}^{T}\mathbf{G}^{-1}\mathbf{u}\right] $$


---

## appendix6_004 · Appendix: Introduction / DERIVATIVES OF VECTORS AND VECTOR-VALUED FUNCTIONS

Now consider the log of the density, $$ \ell=\ln\left[p(\mathbf{y},\mathbf{u})\right]\propto $$ $$ \left(-\frac{1}{2}\right)\left[\ln(|\mathbf{R}|)+\ln(|\mathbf{G}|)+(\mathbf{y}-\mathbf{X}\boldsymbol{\beta}-\mathbf{Z}\mathbf{u})^{T}\mathbf{R}^{-1}(\mathbf{y}-\mathbf{X}\boldsymbol{\beta}-\mathbf{Z}\mathbf{u})+\mathbf{u}^{T}\mathbf{G}^{-1}\mathbf{u}\right] $$

We can expand the larger quadratic product to yield the last two terms of A6.4c as $$ \begin{array}{r}-2\mathbf{y}^{T}\mathbf{R}^{-1}\mathbf{X}\boldsymbol{\beta}-2\mathbf{y}^{T}\mathbf{R}^{-1}\mathbf{Z}\mathbf{u}+\boldsymbol{\beta}^{T}\mathbf{X}^{T}\mathbf{R}^{-1}\mathbf{X}\boldsymbol{\beta}+2\boldsymbol{\beta}^{T}\mathbf{X}^{T}\mathbf{R}^{-1}\mathbf{Z}\mathbf{u}+\mathbf{u}^{T}\mathbf{Z}^{T}\mathbf{R}^{-1}\mathbf{Z}\mathbf{u}+\mathbf{u}^{T}\mathbf{G}^{-1}\mathbf{u}\\ (\mathrm{A6.4d})\end{array} $$

Using Equations A6.1c through A6.1e to take the derivatives of $ \ell $ with respect to $ \beta $ and u yields $$ \left(\begin{array}{c}\frac{\partial\ell}{\partial\boldsymbol{\beta}}\\ \frac{\partial\ell}{\partial\mathbf{u}}\end{array}\right)=\left(\begin{array}{c}\mathbf{X}^{T}\mathbf{R}^{-1}\mathbf{y}-\mathbf{X}^{T}\mathbf{R}^{-1}\mathbf{X}\boldsymbol{\beta}-\mathbf{X}^{T}\mathbf{R}^{-1}\mathbf{Z}\mathbf{u}\\ \mathbf{Z}^{T}\mathbf{R}^{-1}\mathbf{y}-\mathbf{Z}^{T}\mathbf{R}^{-1}\mathbf{X}\boldsymbol{\beta}-\mathbf{Z}^{T}\mathbf{R}^{-1}\mathbf{Z}\mathbf{u}+\mathbf{G}^{-1}\mathbf{u}\end{array}\right) $$

Denoting the value for $ \beta $ and u that return a zero vector for Equation A6.4e as $ \widehat{\beta} $ and $ \widehat{u} $ yields the following set of matrix equations $$ \begin{pmatrix}\mathbf{X}^{T}\mathbf{R}^{-1}\mathbf{y}\\\mathbf{Z}^{T}\mathbf{R}^{-1}\mathbf{y}\end{pmatrix}=\begin{pmatrix}\mathbf{X}^{T}\mathbf{R}^{-1}\mathbf{X}\widehat{\boldsymbol{\beta}}+\mathbf{X}^{T}\mathbf{R}^{-1}\mathbf{Z}\widehat{\mathbf{u}}\\\mathbf{Z}^{T}\mathbf{R}^{-1}\mathbf{X}\widehat{\boldsymbol{\beta}}+\mathbf{Z}^{T}\mathbf{R}^{-1}\mathbf{Z}\widehat{\mathbf{u}}+\mathbf{G}^{-1}\widehat{\mathbf{u}}\end{pmatrix} $$ which immediately yields Henderson’s mixed-model equations, $$ \begin{pmatrix}\mathbf{X}^{T}\mathbf{R}^{-1}\mathbf{y}\\\mathbf{Z}^{T}\mathbf{R}^{-1}\mathbf{y}\end{pmatrix}=\begin{pmatrix}\mathbf{X}^{T}\mathbf{R}^{-1}\mathbf{X}&\mathbf{X}^{T}\mathbf{R}^{-1}\mathbf{Z}\\\mathbf{Z}^{T}\mathbf{R}^{-1}\mathbf{X}&\mathbf{Z}^{T}\mathbf{R}^{-1}\mathbf{Z}+\mathbf{G}^{-1}\end{pmatrix}\begin{pmatrix}\widehat{\boldsymbol{\beta}}\\\widehat{\mathbf{u}}\end{pmatrix} $$

Using the second equation (row two) of Equation A6.4g returns $$ \mathbf{Z}^{T}\mathbf{R}^{-1}\mathbf{X}\widehat{\boldsymbol{\beta}}+\left(\mathbf{Z}^{T}\mathbf{R}^{-1}\mathbf{Z}+\mathbf{G}^{-1}\right)\widehat{\mathbf{u}}=\mathbf{Z}^{T}\mathbf{R}^{-1}\mathbf{y} $$ which can be rearranged to yields $$ \hat{\mathbf{u}}=\left(\mathbf{Z}^{T}\mathbf{R}^{-1}\mathbf{Z}+\mathbf{G}^{-1}\right)^{-1}\mathbf{Z}^{T}\mathbf{R}^{-1}\left(\mathbf{y}-\mathbf{X}\hat{\boldsymbol{\beta}}\right) $$ as an alternative expression to Equation 19.3b for the BLUP of u.

---

## appendix6_005 · Appendix: Introduction / THE HESSIAN MATRIX, LOCAL MAXIMA/MINIMA, AND MULTIDIMENSIONAL TAYLOR SERIES

In univariate calculus, the local extrema of a function occur when its slope (first derivative) is zero. The multivariate extension is that the gradient vector is zero, so the slope of the function with respect to all variables is zero. A point $ x_{e} $ where this occurs is called a stationary or equilibrium point, and corresponds to either a local maximum, minimum, saddle point, or inflection point. As with the calculus of single variables, determining which of these cases is correct depends on the second derivative. With n variables, the appropriate generalization is the Hessian matrix $$ \mathbf{H}_{\mathbf{X}}[f]=\nabla_{\mathbf{X}}\left[\left(\nabla_{\mathbf{X}}[f]\right)^{T}\right]=\frac{\partial^{2}f}{\partial\mathbf{x}\partial\mathbf{x}^{T}}=\left(\begin{array}{c c c}\frac{\partial^{2}f}{\partial x_{1}^{2}}&\cdots&\frac{\partial^{2}f}{\partial x_{1}\partial x_{n}}\\ \vdots&\ddots&\vdots\\ \frac{\partial^{2}f}{\partial x_{1}\partial x_{n}}&\cdots&\frac{\partial^{2}f}{\partial x_{n}^{2}}\end{array}\right) $$

Note that this is the outer product of $ \nabla_{\mathbf{x}} [f] $ with itself. Recall for an $ n $-dimensional column vector $ \mathbf{a}_{n\times1} $ that while the inner product, $ \mathbf{a}_{1\times n}^T \mathbf{a}_{n\times1} = \sum a_i $, returns a $ 1 \times 1 $ matrix (a scalar), the outer product, $ \mathbf{a}_{n\times1} \mathbf{a}_{1\times n}^T $, returns an $ n \times n $ matrix whose $ ij $th element is $ a_i a_j $, or (in our case) $$ \mathbf{H}_{ij}=\frac{\partial\left(f(\mathbf{x})/\partial x_{i}\right)}{\partial x_{j}}=\frac{\partial^{2}f(\mathbf{x})}{\partial x_{i}\partial x_{j}} $$

This matrix is symmetric, as mixed partials are equal under suitable continuity conditions, and it measures the local multidimensional curvature of the function.

**[示例 Example]**

> **Example A6.6** · ref: `A6.6` · source: `appendix6_005.json` · blocks 3–3
>
> Example A6.6. Compute the Hessian matrix for the multivariate normal distribution with respect to the data vector x. If we recall from Equation A6.2a that $ \nabla_{\mathbf{x}}[\varphi(\mathbf{x}, \boldsymbol{\mu})] = -\varphi(\mathbf{x}, \boldsymbol{\mu}) \cdot \mathbf{V}^{-1}(\mathbf{x} - \boldsymbol{\mu}) $, we have $$ \begin{aligned}\mathbf{H}_{\mathbf{X}}\left[\varphi(\mathbf{x},\boldsymbol{\mu})\right]&=\nabla_{\mathbf{X}}\left[\left(\nabla_{\mathbf{X}}\left[\varphi(\mathbf{x},\boldsymbol{\mu})\right]\right)^{T}\right]=-\nabla_{\mathbf{X}}\left[\varphi(\mathbf{x},\boldsymbol{\mu})\cdot(\mathbf{x}-\boldsymbol{\mu})^{T}\mathbf{V}^{-1}\right]\\&=-\nabla_{\mathbf{X}}\left[\varphi(\mathbf{x},\boldsymbol{\mu})\right]\cdot(\mathbf{x}-\boldsymbol{\mu})^{T}\mathbf{V}^{-1}-\varphi(\mathbf{x},\boldsymbol{\mu})\cdot\nabla_{\mathbf{X}}\left[\left(\mathbf{x}-\boldsymbol{\mu}\right)^{T}\mathbf{V}^{-1}\right]\\&=-\left[-\varphi(\mathbf{x},\boldsymbol{\mu})\cdot\mathbf{V}^{-1}\left(\mathbf{x}-\boldsymbol{\mu}\right)\right]\cdot(\mathbf{x}-\boldsymbol{\mu})^{T}\mathbf{V}^{-1}-\varphi(\mathbf{x},\boldsymbol{\mu})\cdot\left[\mathbf{V}^{-1}\right]\\&=\varphi(\mathbf{x},\boldsymbol{\mu})\cdot\left(\mathbf{V}^{-1}\left(\mathbf{x}-\boldsymbol{\mu}\right)(\mathbf{x}-\boldsymbol{\mu})^{T}\mathbf{V}^{-1}-\mathbf{V}^{-1}\right)\quad(A6.6)\end{aligned} $$
> 
> Here we have used the product rule (Equation A6.1i) and Equation A6.1b, respectively (recall that V is a symmetric matrix of constants). In a similar manner, the Hessian with respect to the vector of means, $ \mu $, is $$ \mathbf{H}\boldsymbol{\mu}\left[\varphi(\mathbf{x},\boldsymbol{\mu})\right]=\varphi(\mathbf{x},\boldsymbol{\mu})\cdot\left(\mathbf{V}^{-1}\left(\mathbf{x}-\boldsymbol{\mu}\right)(\mathbf{x}-\boldsymbol{\mu})^{T}\mathbf{V}^{-1}-\mathbf{V}^{-1}\right) $$
> 
> To see how the Hessian matrix determines the nature of equilibrium points, a slight digression on the multidimensional Taylor series is needed. Consider the (second-order) Taylor series of a scalar function of $n$ variables, $f(x_1, \cdots, x_n)$, expanded about the point $\mathbf{x}_o$, $$ f(\mathbf{x})\simeq f(\mathbf{x}_{o})+\sum_{i=1}^{n}(x_{i}-x_{o,i})\frac{\partial f}{\partial x_{i}}+\frac{1}{2}\sum_{i=1}^{n}\sum_{j=1}^{n}(x_{i}-x_{o,i})(x_{j}-x_{o,j})\frac{\partial^{2}f}{\partial x_{i}\partial x_{j}}+\cdots $$ where all partials are evaluated at $ \mathbf{x}_o $. If we note that the first sum is the inner product of the gradient and $ (\mathbf{x} - \mathbf{x}_o) $, and the double sum is a quadratic product involving the Hessian, we can express Equation A6.7a in matrix form as $$ f(\mathbf{x})\simeq f(\mathbf{x}_{o})+\nabla^{T}(\mathbf{x}-\mathbf{x}_{o})+\frac{1}{2}(\mathbf{x}-\mathbf{x}_{o})^{T}\mathbf{H}(\mathbf{x}-\mathbf{x}_{o}) $$ where $ \nabla $ and H are the gradient and Hessian of f with respect to x when evaluated at $ x_{0} $, $$ \nabla\equiv\nabla_{\mathbf{X}}[f]\left|_{\mathbf{X}=\mathbf{X}_{o}}\right.\qquad and\qquad\mathbf{H}\equiv\mathbf{H}_{\mathbf{X}}[f]\left|_{\mathbf{X}=\mathbf{X}_{o}}\right. $$
> 
> At an equilibrium point, $ \hat{x} $, all first partials are zero, so $ (\nabla_{\mathbf{x}}[f])^{T} $ is evaluated at $ \hat{x} $ is a vector of length zero. Whether this point is a maximum or minimum is then determined by the quadratic product involving the Hessian when evaluated at $ \hat{x} $. Consider a vector, d, of a small change from the equilibrium point $$ f(\hat{\mathbf{x}}+\mathbf{d})-f(\hat{\mathbf{x}})\simeq\frac{1}{2}\cdot\mathbf{d}^{T}\mathbf{H}\mathbf{d} $$ Because H is a symmetric matrix, we can diagonalize it and apply a canonical transformation (Equation A5.17a) to simplify the quadratic product in Equation A6.8a, which returns $$ f(\widehat{\mathbf{x}}+\mathbf{d})-f(\widehat{\mathbf{x}})\simeq\frac{1}{2}\sum_{i=1}^{n}\lambda_{i}y_{i}^{2} $$ where $ y_i = e_i^T d $, with $ e_i $ and $ \lambda_i $ representing the eigenvectors and eigenvalues of the Hessian when evaluated at $ \hat{x} $. Thus, if $ \hat{H} $ is positive-definite (all eigenvalues of $ \hat{H} $ are positive), $ f $ increases in all directions around $ \hat{x} $, and hence $ \hat{x} $ is a local minimum of $ f $. If $ \hat{H} $ is negative-definite (all eigenvalues of $ \hat{H} $ are negative), $ f $ decreases in all directions around $ \hat{x} $, and $ \hat{x} $ is a local maximum of $ f $. If the eigenvalues differ in sign ($ \hat{H} $ is indefinite), $ \hat{x} $ corresponds to a saddle point (to see this, suppose $ \lambda_1 > 0 $ and $ \lambda_2 < 0 $; any change along the vector $ e_1 $ results in an increase in $ f $, while any change along $ e_2 $ results in a decrease in $ f $).


**[示例 Example]**

> **Example A6.7** · ref: `A6.7` · source: `appendix6_005.json` · blocks 4–4
>
> Example A6.7. Consider the following demonstration (due to Lande 1979a) that the mean population fitness increases. A round of selection changes the current vector of means from $ \mu $ to $ \mu + \Delta\mu $. Expanding the log of mean fitness in a Taylor series around the current population mean gives the change in mean population fitness as $$ \begin{align*}\Delta\ln\overline{W}(\mu)&=\ln\overline{W}(\mu+\Delta\mu)-\ln\overline{W}(\mu)\\&\simeq\left(\nabla\mu\left[\ln\overline{W}(\mu)\right]\right)^{T}\Delta\mu+\frac{1}{2}\Delta\mu^{T}\mathbf{H}\mu\left[\ln\overline{W}(\mu)\right]\Delta\mu\end{align*} $$
> 
> If we assume that second- and higher-order terms can be neglected (as would occur with weak selection and the population mean away from an equilibrium point), then Equation A6.9a simplifies to $$ \Delta\ln\overline{W}(\mu)\simeq\left(\nabla_{\boldsymbol{\mu}}[\ln\overline{W}(\boldsymbol{\mu})]\right)^{T}\Delta\boldsymbol{\mu} $$
> 
> Further assuming that the joint distribution of phenotypes and additive genetic values is MVN, then substituting Equation A6.2e into Equation A6.9b yields $$ \Delta\ln\overline{W}(\mu)\simeq\beta^{T}\Delta\mu $$ Because $ \Delta\mu $ is the response vector, $ \mathbf{R} $, rearranging Equation 13.26a yields $ \boldsymbol{\beta} = \mathbf{G}^{-1}\mathbf{R} = \mathbf{G}^{-1}\Delta\mu $. Substituting this expression into Equation A6.9c yields $$ \Delta\ln\overline{W}(\mu)\simeq\left(\mathbf{G}^{-1}\Delta\mu\right)^{T}\Delta\mu=\left(\Delta\mu\right)^{T}\mathbf{G}^{-1}\Delta\mu\geq0 $$
> 
> The inequality follows because $ \mathbf{G} $ is a variance-covariance matrix and hence is nonnegative-definite (all its eigenvalues are nonnegative). Under these conditions, mean population fitness never decreases, although because $ \Delta\boldsymbol{\mu} \neq \nabla\boldsymbol{\mu}[\ln \overline{W}(\boldsymbol{\mu})] $, the local increase in fitness does not necessarily improve in the fastest possible manner. Note that $$ \Delta\ln\overline{W}(\boldsymbol{\mu})=\ln\overline{W}(\boldsymbol{\mu}[t+1])-\ln\overline{W}(\boldsymbol{\mu}[t])=\ln\left(\frac{\overline{W}(\boldsymbol{\mu}[t+1])}{\overline{W}(\boldsymbol{\mu}[t])}\right) $$ so $\Delta \ln \overline{W}(\mu) > 0$ implies $\overline{W}(\mu[t+1]) > \overline{W}(\mu[t]).$ Notice from Equation A6.2f that when fitnesses are frequency-dependent, $\nabla \mu[\ln \overline{W}(\mu)]$ has an extra term beyond $\beta$, and the above proof does not hold (namely, mean fitness can decrease).


---

## appendix6_006 · Appendix: Introduction / OPTIMIZATION UNDER CONSTRAINTS

Occasionally, we wish to find the maximum or minimum of a function subject to a constraint. The solution is to use Lagrange multipliers. Suppose we wish to find the extrema of a function, $ f(\mathbf{x}) $, subject to the constraint that $ h(\mathbf{x}) = c $. We first construct a new function by considering $$ g(\mathbf{x},\lambda)=f(\mathbf{x})-\lambda[h(\mathbf{x})-c] $$ Because $ h(\mathbf{x}) - c = 0 $, the extrema of $ g(\mathbf{x}, \lambda) $ correspond to the extrema of $ f(\mathbf{x}) $ under the constraint. Local maxima and minima are obtained by solving the following set of equations: $$ \nabla_{\mathbf{x}}[g(\mathbf{x},\lambda)]=\nabla_{\mathbf{x}}[f(\mathbf{x})]-\lambda\cdot\nabla_{\mathbf{x}}[h(\mathbf{x})]=\mathbf{0} $$ $$ \frac{d g(\mathbf{x},\lambda)}{d\lambda}=h(\mathbf{x})-c=0 $$

Observe that the second equation is satisfied by the constraint.

**[示例 Example]**

> **Example A6.8** · ref: `A6.8` · source: `appendix6_006.json` · blocks 2–2
>
> Example A6.8. A standard approach for selection on multiple traits is to use a selection index, I, which is a new (univariate) trait that is a linear combination of n characters $ \mathbf{z} = (z_1, z_2, \cdots, z_n)^T $, with $$ I=\mathbf{b}^{T}\mathbf{z}=\sum_{k=1}^{n}b_{k}z_{k} $$
> 
> Notice that what matters for the weights are their relative proportions, as, if we were to multiply all of the weights by the same constant (e.g., $ a_{b_k} $), this new index would still choose the same individuals. Hence, to obtain a standardized index, we impose the constraint $ \mathbf{b}^T\mathbf{b} = 1 $. We denote the directional selection differential on the index by $ S_I $, and observe that if $ \mathbf{S} $ is the vector of directional selection differentials generated by selecting on $ I $, then $ S_I = \mathbf{b}^T\mathbf{S} $.
> 
> Smith (1936) and Hazel (1943) showed that a larger response in a target index is obtained by selecting on a different index. Suppose our aim is to maximize the response in the index, $$ J=\mathbf{a}^{T}\boldsymbol{\mu}=\sum a_{k}\mu_{k} $$
> 
> What are the standardized weights, b, for the optimal Smith-Hazel index (for a fixed amount of selection, $ S_I = s $? If we assume that the conditions leading to the multivariate breeder's equation hold, the function to maximize is $$ f(\mathbf{b})=\mathbf{a}^{T}\boldsymbol{\Delta}\boldsymbol{\mu}=\mathbf{a}^{T}\mathbf{R}=\mathbf{a}^{T}\mathbf{G}\mathbf{P}^{-1}\mathbf{S} $$ under the associated constraint function $$ g(\mathbf{b})-c=\mathbf{b}^{T}\mathbf{b}-1=0 $$ Because $S_I = b^T S$, and we have the constraint that $b^T b = 1$, set $S = s \cdot b$, so that $S_I = b^T S = s \cdot b^T b = s$. If we use these functions, Equation A6.10a yields $$ \begin{aligned}\nabla_{\mathbf{b}}[g(\mathbf{b},\lambda)]&=s\cdot\nabla_{\mathbf{b}}[\mathbf{a}^{T}\mathbf{G}\mathbf{P}^{-1}\mathbf{b}]-\lambda\cdot\nabla_{\mathbf{b}}[\mathbf{b}^{T}\mathbf{b}]\\&=s\cdot\left(\mathbf{a}^{T}\mathbf{G}\mathbf{P}^{-1}\right)^{T}-(2\lambda)\cdot\mathbf{b}\end{aligned} $$ which is equal to zero when $$ \mathbf{b}=(2\lambda/s)\cdot\mathbf{P}^{-1}\mathbf{G}^{T}\mathbf{a} $$
> 
> Note that the constant $ 2\lambda/s $ simply standardizes the weights (so that $ \mathbf{b}^T\mathbf{b}=1 $), and hence the Smith-Hazel weights are usually written as $$ \mathbf{b}_{SH}=\mathbf{P}^{-1}\mathbf{G}^{T}\mathbf{a} $$ which can be standardized by noting that $$ \mathbf{b}=\frac{\mathbf{b}_{SH}}{\left|\left|\mathbf{b}_{SH}\right|\right|}=\frac{\mathbf{b}_{SH}}{\sqrt{\mathbf{b}_{SH}^{T}\mathbf{b}_{SH}}} $$
> 
> Index selection is examined in detail in Volume 3.


---
