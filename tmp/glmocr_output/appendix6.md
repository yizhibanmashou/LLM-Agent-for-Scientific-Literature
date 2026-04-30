<div align="center">

# Appendix 6

</div>

<div align="center">

# Derivatives of Vectors and Vector-valued Functions

</div>

Mathematics is a collection of cheap tricks and dirty jokes. Lipman Bers

Quantitative genetics often deals with vector-valued functions, and here we provide a brief review of the calculus of such functions. In particular, we review common expressions for derivatives of vectors and vector-valued functions, introduce the gradient vector and Hessian matrix (for first and second partials, respectively), and use this machinery in multidimensional Taylor series for approximating functions around a specific value. We apply these results to several problems in selection theory and evolution.

## DERIVATIVES OF VECTORS AND VECTOR-VALUED FUNCTIONS

Suppose we let $ f(\mathbf{x}) $ be a scalar (single-dimension) function of a column vector, $ \mathbf{x}= ( x_{1},\cdots,x_{n} )^{T} $ of n variables. The gradient (or gradient vector) of f with respect to x is obtained by taking partial derivatives of the function with respect to each variable. In matrix notation, the gradient operator is denoted by

$$
\nabla_ {\mathbf {X}} [ f ] = \frac {\partial f}{\partial \mathbf {x}} = \left( \begin{array}{c} \frac {\partial f}{\partial x _ {1}} \\ \vdots \\ \frac {\partial f}{\partial x _ {n}} \end{array} \right)
$$

The gradient at a point, $ \mathbf{x}_{o} $ , corresponds to a vector indicating the direction of local steepest ascent of the function at that point (the multivariate slope of f at $ \mathbf{x}_{o} $ ).

Example A6.1. For an $ n\times1 $ column vector, x, compute the gradient for

$$
f (\mathbf {x}) = \sum_ {i = 1} ^ {n} x _ {i} ^ {2} = \mathbf {x} ^ {T} \mathbf {x}
$$

Because $ \partial f / \partial x_{i}=2 x_{i} $ , the gradient vector is just $ \nabla_{\mathbf{x}}[f(\mathbf{x})]=2\mathbf{x} $ . At the point $ \mathbf{x}_{o},\mathbf{x}^{T}\mathbf{x} $ locally increases most rapidly if we change $ \mathbf{x} $ in the same the direction as the vector going from point $ \mathbf{x}_{o} $ to point $ \mathbf{x}_{o}+2\delta\mathbf{x}_{o}=(1+2\delta)\mathbf{x}_{o} $ , where $ \delta $ is a small positive value.

Now consider an m $ \times $ n matrix, A, of constants. What is the derivative of the n $ \times $ 1 column vector Ax with respect to x? Recall from the definition of matrix multiplication that the ith element of Ax is

$$
(\mathbf {A x}) _ {i} = \sum_ {j = 1} ^ {n} A _ {i j} x _ {j}, \quad \text {y i e l d i n g} \quad \partial (\mathbf {A z}) _ {i} / \partial x _ {k} = A _ {i k}
$$

Hence, the i th element of $ \nabla_{\mathbf{X}}[\mathbf{Ax}]_{k} $ is $ \left( \begin{array}{cccc} A_{1k} & A_{2k} & \cdots & A_{mk} \end{array} \right) $ , namely the transpose of the kth column of A, which yields $ \nabla_{\mathbf{X}}[\mathbf{Ax}]=\mathbf{A}^{T}. $

For a vector (a) and a matrix (A) of constants, using the same logic as in Example A6.1, it can be shown (e.g., Morrison 1976; Graham 1981; Searle 1982) that

$$
\nabla_ {\mathbf {X}} \left[ \mathrm {a} ^ {T} \mathrm {x} \right] = \nabla_ {\mathbf {X}} \left[ \mathrm {x} ^ {T} \mathrm {a} \right] = \mathrm {a}
$$

$$
\nabla_ {\mathbf {X}} [ \mathbf {A x} ] = \mathbf {A} ^ {T}
$$

Turning to quadratic forms, if A is symmetric $ \mathbf{A}=\mathbf{A}^{T} $), then

$$
\nabla_ {\mathbf {X}} \left[ \mathbf {x} ^ {T} \mathbf {A} \mathbf {x} \right] = 2 \mathbf {A} \mathbf {x}
$$

$$
\nabla_ {\mathbf {X}} \left[ (\mathbf {x} - \mathbf {a}) ^ {T} \mathbf {A} (\mathbf {x} - \mathbf {a}) \right] = 2 \mathbf {A} (\mathbf {x} - \mathbf {a})
$$

$$
\nabla_ {\mathbf {X}} \left[ (\mathbf {a} - \mathbf {x}) ^ {T} \mathbf {A} (\mathbf {a} - \mathbf {x}) \right] = - 2 \mathbf {A} (\mathbf {a} - \mathbf {x})
$$

Taking A = I, Equation A6.1c implies

$$
\nabla_ {\mathbf {X}} \left[ \mathbf {x} ^ {T} \mathbf {x} \right] = \nabla_ {\mathbf {X}} \left[ \mathbf {x} ^ {T} \mathbf {I} \mathbf {x} \right] = 2 \mathbf {I} \mathbf {x} = 2 \mathbf {x}
$$

as was found in Example A6.1. Two other useful identities follow from the chain rule of differentiation, namely,

$$
\nabla_ {\mathbf {X}} \left[ \exp \left\{f (\mathbf {x}) \right\} \right] = \exp \left[ f (\mathbf {x}) \right] \nabla_ {\mathbf {X}} \left[ f (\mathbf {x}) \right]
$$

$$
\nabla_ {\mathbf {x}} [ \ln [ f (\mathbf {x}) ] ] = \frac {1}{f (\mathbf {x})} \cdot \nabla_ {\mathbf {x}} [ f (\mathbf {x}) ]
$$

Finally, the product rule also applies to a gradient, with

$$
\nabla_ {\mathbf {X}} [ f (\mathbf {x}) g (\mathbf {x}) ] = \nabla_ {\mathbf {X}} [ f (\mathbf {x}) ] g (\mathbf {x}) + f (\mathbf {x}) \nabla_ {\mathbf {X}} [ g (\mathbf {x}) ]
$$

Example A6.2. The density function $ \varphi(\mathbf{x},\boldsymbol{\mu},\mathbf{V}) $ for a multivariate normal (MVN) distribution returns a scalar value and is a function of the data vector, $ \mathbf{x} $ , the vector of means, $ \boldsymbol{\mu} $ , and the covariance matrix, $ \mathbf{V}, $

$$
\varphi (\mathbf {x}, \boldsymbol {\mu}, \mathbf {V}) = a \exp \left(- \frac {1}{2} \cdot (\mathbf {x} - \boldsymbol {\mu}) ^ {T} \mathbf {V} ^ {- 1} (\mathbf {x} - \boldsymbol {\mu})\right)
$$

where the constant $ a=\pi^{-n / 2}|\mathbf{V}|^{-1 / 2} $ , and $ |\mathbf{V}| $ denotes the determinant of $ \mathbf{V}. $ To compute the gradient of the MVN with respect to the data vector, x, first apply Equation A6.1g to yield

$$
\nabla_ {\mathbf {X}} \left[ \varphi (\mathbf {x}, \boldsymbol {\mu}, \mathbf {V}) \right] = \varphi (\mathbf {x}, \boldsymbol {\mu}, \mathbf {V}) \cdot \nabla_ {\mathbf {X}} \left[ \left(- \frac {1}{2}\right) \cdot (\mathbf {x} - \boldsymbol {\mu}) ^ {T} \mathbf {V} _ {\mathbf {X}} ^ {- 1} (\mathbf {x} - \boldsymbol {\mu}) \right]
$$

Using this result along with Equation A6.1d returns

$$
\nabla_ {\mathbf {X}} \left[ \varphi (\mathbf {x}, \boldsymbol {\mu}, \mathbf {V}) \right] = - \varphi (\mathbf {x}, \boldsymbol {\mu}, \mathbf {V}) \cdot \mathbf {V} ^ {- 1} (\mathbf {x} - \boldsymbol {\mu})
$$

Similarly, Equation A6.1e implies that the gradient of the MVN with respect to the vector of means $ \mu $ is

$$
\nabla_ {\boldsymbol {\mu}} \left[ \varphi (\mathrm {x}, \boldsymbol {\mu}, \mathrm {V}) \right] = \varphi (\mathrm {x}, \boldsymbol {\mu}, \mathrm {V}) \cdot \mathrm {V} ^ {- 1} (\mathrm {x} - \boldsymbol {\mu})
$$

of log mean fitness with respect to the vector of trait means, $ \nabla\mu[\ln \overline{W} (\mu)] $ (Lande 1979a). Hence, the increase in the mean population fitness is maximized if mean character values change in the same direction as the vector $ \beta $ . To see this, first note that applying Equation A6.1h yields

$$
\nabla_ {\boldsymbol {\mu}} [ \ln \overline {{W}} (\boldsymbol {\mu}) ] = \overline {{W}} ^ {- 1} \nabla_ {\boldsymbol {\mu}} [ \overline {{W}} (\boldsymbol {\mu}) ]
$$

If we write mean fitness as $ \overline{W} (\boldsymbol{\mu})=\int W(\mathbf{z})\varphi(\mathbf{z},\boldsymbol{\mu}) d\mathbf{z} $ and take the gradient through the integral, we obtain

$$
\nabla_ {\boldsymbol {\mu}} [ \ln \overline {{W}} (\boldsymbol {\mu}) ] = \overline {{W}} ^ {- 1} \nabla_ {\boldsymbol {\mu}} \left[ \int W (\mathbf {z}) \varphi (\mathbf {z}, \boldsymbol {\mu}) \mathrm {d} \mathbf {z} \right] = \overline {{W}} ^ {- 1} \int W (\mathbf {z}) \nabla_ {\boldsymbol {\mu}} [ \varphi (\mathbf {z}, \boldsymbol {\mu}) ] \mathrm {d} \mathbf {z}
$$

The last identity follows from the assumption that $ W ( \mathbf{z} ) $ is not a function of the vector of trait means, $ \mu $ , that is, the fitnesses are frequency-independent $ (\nabla\mu\left[ W ( \mathbf{z} ) \right] = 0) $ . If the trait vector $ \mathbf{z}\sim\mathrm{MVN}(\mu,\mathbf{P}) $ , Equation A6.2b yields

$$
\nabla_ {\boldsymbol {\mu}} \left[ \varphi (\mathbf {z}, \boldsymbol {\mu}) \right] = \varphi (\mathbf {z}, \boldsymbol {\mu}) \mathbf {P} ^ {- 1} (\mathbf {z} - \boldsymbol {\mu})
$$

Hence,

$$
\begin{array}{l} \overline {{W}} ^ {- 1} \int W (\mathbf {z}) \nabla_ {\boldsymbol {\mu}} [ \varphi (\mathbf {z}, \boldsymbol {\mu}) ] \mathrm {d} \mathbf {z} = \int w (\mathbf {z}) \varphi (\mathbf {z}, \boldsymbol {\mu}) \mathbf {P} ^ {- 1} (\mathbf {z} - \boldsymbol {\mu}) \mathrm {d} \mathbf {z} \\ = \mathbf {P} ^ {- 1} \left(\int \mathbf {z} w (\mathbf {z}) \varphi (\mathbf {z}, \boldsymbol {\mu}) \mathrm {d} \mathbf {z} - \boldsymbol {\mu} \int w (\mathbf {z}) \varphi (\mathbf {z}, \boldsymbol {\mu}) \mathrm {d} \mathbf {z}\right) \\ = \mathbf {P} ^ {- 1} \left(\boldsymbol {\mu} ^ {*} - \boldsymbol {\mu}\right) = \mathbf {P} ^ {- 1} \mathbf {S} = \beta \tag {A6.2e} \\ \end{array}
$$

which follows because the first integral (in the second line above) is the mean character value after selection, $ \mu^{*} $ , while the second integral equals one by definition, as $ E[w]=1. $

If individual fitnesses are frequency-dependent (changing with $ \mu $), then, according to the product rule (Equation A6.1i), a second integral appears, and $ \nabla\mu[\ln \overline{W}(\mu)] $ now becomes

$$
\overline {{W}} ^ {- 1} \int W (\mathbf {z}) \nabla_ {\boldsymbol {\mu}} [ \varphi (\mathbf {z}, \boldsymbol {\mu}) ] \mathrm {d} \mathbf {z} + \overline {{W}} ^ {- 1} \int \nabla_ {\boldsymbol {\mu}} [ W (\mathbf {z}) ] \varphi (\mathbf {z}, \boldsymbol {\mu}) \mathrm {d} \mathbf {z}
$$

which yields

$$
\nabla_ {\boldsymbol {\mu}} [ \ln \overline {{W}} (\boldsymbol {\mu}) ] = \beta + \overline {{W}} ^ {- 1} \int \nabla_ {\boldsymbol {\mu}} [ W (\mathbf {z}) ] \varphi (\mathbf {z}, \boldsymbol {\mu}) \mathrm {d} \mathbf {z}
$$

Example A6.4. Consider the ordinary least-squares solution for the general linear model, $ \mathbf{y}=\mathbf{X}\beta+\mathbf{e} $ , where $ \beta $ is the vector that minimizes the sum of squared residual errors, $ \sum e_{i}^{2}. $ In matrix form, this sum becomes

$$
\begin{array}{l} \sum_ {i = 1} ^ {n} e _ {i} ^ {2} = \mathbf {e} ^ {T} \mathbf {e} = (\mathbf {y} - \mathbf {X} \boldsymbol {\beta}) ^ {T} (\mathbf {y} - \mathbf {X} \boldsymbol {\beta}) \\ = \mathbf {y} ^ {T} \mathbf {y} - \beta^ {T} \mathbf {X} ^ {T} \mathbf {y} - \mathbf {y} ^ {T} \mathbf {X} \boldsymbol {\beta} + \beta^ {T} \mathbf {X} ^ {T} \mathbf {X} \boldsymbol {\beta} \\ = \mathbf {y} ^ {T} \mathbf {y} - 2 \beta^ {T} \mathbf {X} ^ {T} \mathbf {y} + \beta^ {T} \mathbf {X} ^ {T} \mathbf {X} \boldsymbol {\beta} \\ \end{array}
$$

and the last step follows because the matrix product $ \beta^{T}\mathbf{X}^{T}\mathbf{y} $ yields a scalar, and hence equals its transpose,

$$
\beta^ {T} \mathbf {X} ^ {T} \mathbf {y} = \left(\beta^ {T} \mathbf {X} ^ {T} \mathbf {y}\right) ^ {T} = \mathbf {y} ^ {T} \mathbf {X} \beta
$$

To find the vector $ \beta $ that minimizes $ \mathbf{e}^{T}\mathbf{e} $ , we take the derivative with respect to $ \beta $ and use Equations A6.1a-A6.1c, which yields

$$
\nabla_ {\beta} \left[ \mathrm {e} ^ {T} \mathrm {e} \right] = \frac {\partial \mathrm {e} ^ {T} \mathrm {e}}{\partial \beta} = - 2 \mathrm {X} ^ {T} \mathrm {y} + 2 \mathrm {X} ^ {T} \mathrm {X} \beta
$$

Setting this equal to zero yields $ \mathbf{X}^{T}\mathbf{X}\beta=\mathbf{X}^{T}\mathbf{y} $ , which (provided the inverse of $ \mathbf{X}^{T}\mathbf{X} $ exists) has a solution of

$$
\beta = \left(\mathbf {X} ^ {T} \mathbf {X}\right) ^ {- 1} \mathbf {X} ^ {T} \mathbf {y}
$$

More generally, if $ \mathbf{X}^{T}\mathbf{X} $ is singular, we can still solve this equation by using a generalized inverse $ \left( \mathbf{X}^{T}\mathbf{X}\right)^{-} $ ; see LW Appendix 3.

Example A6.5. Here we present one derivation of Henderson's mixed-model equations (Equation 19.4). Consider the mixed model $ \mathbf{y}=\mathbf{X}\beta+\mathbf{Z}\mathbf{u}+\mathbf{e} $ , where $ \mathbf{e}\sim\mathrm{MVN}(0,\mathbf{R}) $ $ \mathbf{u}\sim\mathrm{MVN}(0,\mathbf{G}) $ , and e and u are independent (Equation 19.1). If we recall the probability density function for a multivariate normal (Example A6.2), we have that

$$
p (\mathbf {e}) \propto | \mathbf {R} | ^ {- 1 / 2} \cdot \exp \left[ - \frac {1}{2} \mathbf {e} ^ {T} \mathbf {R} ^ {- 1} \mathbf {e} \right] \quad \mathrm {a n d} \quad p (\mathbf {u}) \propto | \mathbf {G} | ^ {- 1 / 2} \cdot \exp \left[ - \frac {1}{2} \mathbf {u} ^ {T} \mathbf {G} ^ {- 1} \mathbf {u} \right]
$$

We can further note that the conditional distribution of y given u is

$$
(\mathbf {y} - \mathbf {X} \beta - \mathbf {Z} \mathbf {u}) | \mathbf {u} = \mathbf {e} \sim \mathrm {M V N} (0, \mathbf {R})
$$

Hence,

$$
p (\mathbf {y}, \mathbf {u}) = p (\mathbf {y} | \mathbf {u}) \cdot p (\mathbf {u}) = p (\mathbf {e}) \cdot p (\mathbf {u})
$$

with the last step following because e and u are independent. From Equation A6.4a,

$$
p (\mathbf {y}, \mathbf {u}) \propto
$$

$$
| \mathbf {R} | ^ {- 1 / 2} | \mathbf {G} | ^ {- 1 / 2} \cdot \exp \left[ - \frac {1}{2} \left(\mathbf {y} - \mathbf {X} \boldsymbol {\beta} - \mathbf {Z} \mathbf {u}\right) ^ {T} \mathbf {R} ^ {- 1} \left(\mathbf {y} - \mathbf {X} \boldsymbol {\beta} - \mathbf {Z} \mathbf {u}\right) - \frac {1}{2} \mathbf {u} ^ {T} \mathbf {G} ^ {- 1} \mathbf {u} \right]
$$

Now consider the log of the density,

$$
\ell = \ln [ p (\mathbf {y}, \mathbf {u}) ] \propto
$$

$$
\left(- \frac {1}{2}\right) \left[ \ln \left(| \mathbf {R} |\right) + \ln \left(| \mathbf {G} |\right) + \left(\mathbf {y} - \mathbf {X} \boldsymbol {\beta} - \mathbf {Z} \mathbf {u}\right) ^ {T} \mathbf {R} ^ {- 1} \left(\mathbf {y} - \mathbf {X} \boldsymbol {\beta} - \mathbf {Z} \mathbf {u}\right) + \mathbf {u} ^ {T} \mathbf {G} ^ {- 1} \mathbf {u} \right]
$$

We can expand the larger quadratic product to yield the last two terms of A6.4c as

$$
- 2 \mathbf {y} ^ {T} \mathbf {R} ^ {- 1} \mathbf {X} \beta - 2 \mathbf {y} ^ {T} \mathbf {R} ^ {- 1} \mathbf {Z} \mathbf {u} + \beta^ {T} \mathbf {X} ^ {T} \mathbf {R} ^ {- 1} \mathbf {X} \beta + 2 \beta^ {T} \mathbf {X} ^ {T} \mathbf {R} ^ {- 1} \mathbf {Z} \mathbf {u} + \mathbf {u} ^ {T} \mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \mathbf {Z} \mathbf {u} + \mathbf {u} ^ {T} \mathbf {G} ^ {- 1} \mathbf {u} \tag {A6.4d}
$$

Using Equations A6.1c through A6.1e to take the derivatives of $ \ell $ with respect to $ \beta $ and u yields

$$
\left( \begin{array}{c} \frac {\partial \ell}{\partial \beta} \\ \frac {\partial \ell}{\partial \mathbf {u}} \end{array} \right) = \left( \begin{array}{c} \mathbf {X} ^ {T} \mathbf {R} ^ {- 1} \mathbf {y} - \mathbf {X} ^ {T} \mathbf {R} ^ {- 1} \mathbf {X} \beta - \mathbf {X} ^ {T} \mathbf {R} ^ {- 1} \mathbf {Z} \mathbf {u} \\ \mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \mathbf {y} - \mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \mathbf {X} \beta - \mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \mathbf {Z} \mathbf {u} + \mathbf {G} ^ {- 1} \mathbf {u} \end{array} \right)
$$

Denoting the value for $ \beta $ and $ \mathbf{u} $ that return a zero vector for Equation A6.4e as $ \widehat{\beta} $ and $ \widehat{\mathbf{u}} $ yields the following set of matrix equations

$$
\binom {\mathbf {X} ^ {T} \mathbf {R} ^ {- 1} \mathbf {y}} {\mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \mathbf {y}} = \binom {\mathbf {X} ^ {T} \mathbf {R} ^ {- 1} \mathbf {X} \hat {\boldsymbol {\beta}} + \mathbf {X} ^ {T} \mathbf {R} ^ {- 1} \mathbf {Z} \hat {\mathbf {u}}} {\mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \mathbf {X} \hat {\boldsymbol {\beta}} + \mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \mathbf {Z} \hat {\mathbf {u}} + \mathbf {G} ^ {- 1} \hat {\mathbf {u}}}
$$

which immediately yields Henderson's mixed-model equations,

$$
\binom {\mathbf {X} ^ {T} \mathbf {R} ^ {- 1} \mathbf {y}} {\mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \mathbf {y}} = \binom {\mathbf {X} ^ {T} \mathbf {R} ^ {- 1} \mathbf {X}} {\mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \mathbf {X}} \binom {\mathbf {X} ^ {T} \mathbf {R} ^ {- 1} \mathbf {Z}} {\mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \mathbf {Z} + \mathbf {G} ^ {- 1}} \binom {\widehat {\beta}} {\widehat {\mathbf {u}}}
$$

Using the second equation (row two) of Equation A6.4g returns

$$
\mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \mathbf {X} \widehat {\boldsymbol {\beta}} + \left(\mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \mathbf {Z} + \mathbf {G} ^ {- 1}\right) \widehat {\mathbf {u}} = \mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \mathbf {y}
$$

$$
\widehat {\mathbf {u}} = \left(\mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \mathbf {Z} + \mathbf {G} ^ {- 1}\right) ^ {- 1} \mathbf {Z} ^ {T} \mathbf {R} ^ {- 1} \left(\mathbf {y} - \mathbf {X} \widehat {\beta}\right)
$$

which can be rearranged to yields

as an alternative expression to Equation 19.3b for the BLUP of u.

## THE HESSIAN MATRIX, LOCAL MAXIMA/MINIMA, AND MULTIDIMENSIONAL TAYLOR SERIES

In univariate calculus, the local extrema of a function occur when its slope (first derivative) is zero. The multivariate extension is that the gradient vector is zero, so the slope of the function with respect to all variables is zero. A point $ x_{e} $ where this occurs is called a stationary or equilibrium point, and corresponds to either a local maximum, minimum, saddle point, or inflection point. As with the calculus of single variables, determining which of these cases is correct depends on the second derivative. With n variables, the appropriate generalization is the Hessian matrix

$$
\mathbf {H} _ {\mathbf {X}} [ f ] = \nabla_ {\mathbf {X}} \left[ \left(\nabla_ {\mathbf {X}} [ f ]\right) ^ {T} \right] = \frac {\partial^ {2} f}{\partial \mathbf {x} \partial \mathbf {x} ^ {T}} = \left( \begin{array}{c c c} \frac {\partial^ {2} f}{\partial x _ {1} ^ {2}} & \dots & \frac {\partial^ {2} f}{\partial x _ {1} \partial x _ {n}} \\ \vdots & \ddots & \vdots \\ \frac {\partial^ {2} f}{\partial x _ {1} \partial x _ {n}} & \dots & \frac {\partial^ {2} f}{\partial x _ {n} ^ {2}} \end{array} \right)
$$

Note that this is the outer product of $ \nabla_{\mathbf{X}}[f] $ with itself. Recall for an n-dimensional column vector $ \mathbf{a}_{n\times 1} $ that while the inner product, $ \mathbf{a}_{1\times n}^{T}\mathbf{a}_{n\times 1}=\sum a_{i} $ returns a $ 1\times 1 $ matrix (a scalar), the outer product, $ \mathbf{a}_{n\times 1}\mathbf{a}_{1\times n}^{T} $ returns an $ n\times n $ matrix whose ijth element is $ a_{i}a_{j} $ or (in our case)

$$
\mathbf {H} _ {i j} = \frac {\partial \left(f (\mathbf {x}) / \partial x _ {i}\right)}{\partial x _ {j}} = \frac {\partial^ {2} f (\mathbf {x})}{\partial x _ {i} \partial x _ {j}}
$$

This matrix is symmetric, as mixed partials are equal under suitable continuity conditions, and it measures the local multidimensional curvature of the function.

Example A6.6. Compute the Hessian matrix for the multivariate normal distribution with respect to the data vector x. If we recall from Equation A6.2a that $ \nabla_{\mathbf{X}}[\varphi(\mathbf{x},\boldsymbol{\mu})]=-\varphi(\mathbf{x},\boldsymbol{\mu}) $ $ \mathbf{V}^{-1} (\mathbf{x}-\boldsymbol{\mu}) $ , we have

$$
\begin{array}{l} \mathbf {H} _ {\mathbf {X}} [ \varphi (\mathbf {x}, \boldsymbol {\mu}) ] = \nabla_ {\mathbf {X}} \left[ \left(\nabla_ {\mathbf {X}} [ \varphi (\mathbf {x}, \boldsymbol {\mu}) ]\right) ^ {T} \right] = - \nabla_ {\mathbf {X}} \left[ \varphi (\mathbf {x}, \boldsymbol {\mu}) \cdot (\mathbf {x} - \boldsymbol {\mu}) ^ {T} \mathbf {V} ^ {- 1} \right] \\ = - \nabla_ {\mathbf {X}} \left[ \varphi (\mathbf {x}, \boldsymbol {\mu}) \right] \cdot (\mathbf {x} - \boldsymbol {\mu}) ^ {T} \mathbf {V} ^ {- 1} - \varphi (\mathbf {x}, \boldsymbol {\mu}) \cdot \nabla_ {\mathbf {X}} \left[ (\mathbf {x} - \boldsymbol {\mu}) ^ {T} \mathbf {V} ^ {- 1} \right] \\ = - \left[ - \varphi (\mathbf {x}, \boldsymbol {\mu}) \cdot \mathbf {V} ^ {- 1} (\mathbf {x} - \boldsymbol {\mu}) \right] \cdot (\mathbf {x} - \boldsymbol {\mu}) ^ {T} \mathbf {V} ^ {- 1} - \varphi (\mathbf {x}, \boldsymbol {\mu}) \cdot \left[ \mathbf {V} ^ {- 1} \right] \\ = \varphi (\mathbf {x}, \boldsymbol {\mu}) \cdot \left(\mathbf {V} ^ {- 1} (\mathbf {x} - \boldsymbol {\mu}) (\mathbf {x} - \boldsymbol {\mu}) ^ {T} \mathbf {V} ^ {- 1} - \mathbf {V} ^ {- 1}\right) \tag {A6.6} \\ \end{array}
$$

Here we have used the product rule (Equation A6.1i) and Equation A6.1b, respectively (recall that $ \mathbf{V} $ is a symmetric matrix of constants). In a similar manner, the Hessian with respect to the vector of means, $ \mu $ , is

$$
\mathbf {H} _ {\boldsymbol {\mu}} \left[ \varphi (\mathbf {x}, \boldsymbol {\mu}) \right] = \varphi (\mathbf {x}, \boldsymbol {\mu}) \cdot \left(\mathbf {V} ^ {- 1} (\mathbf {x} - \boldsymbol {\mu}) (\mathbf {x} - \boldsymbol {\mu}) ^ {T} \mathbf {V} ^ {- 1} - \mathbf {V} ^ {- 1}\right)
$$

To see how the Hessian matrix determines the nature of equilibrium points, a slight digression on the multidimensional Taylor series is needed. Consider the (second-order) Taylor series of a scalar function of n variables, $ f ( x_{1}, \dots, x_{n} ) $ , expanded about the point $ \mathbf{x}_{o} $

$$
f (\mathbf {x}) \simeq f \left(\mathbf {x} _ {o}\right) + \sum_ {i = 1} ^ {n} \left(x _ {i} - x _ {o, i}\right) \frac {\partial f}{\partial x _ {i}} + \frac {1}{2} \sum_ {i = 1} ^ {n} \sum_ {j = 1} ^ {n} \left(x _ {i} - x _ {o, i}\right) \left(x _ {j} - x _ {o, j}\right) \frac {\partial^ {2} f}{\partial x _ {i} \partial x _ {j}} + \dots
$$

where all partials are evaluated at $ \mathbf{x}_{o} $ . If we note that the first sum is the inner product of the gradient and $ \left(\mathbf{x}-\mathbf{x}_{o}\right) $ , and the double sum is a quadratic product involving the Hessian, we can express Equation A6.7a in matrix form as

$$
f (\mathbf {x}) \simeq f \left(\mathbf {x} _ {o}\right) + \nabla^ {T} \left(\mathbf {x} - \mathbf {x} _ {o}\right) + \frac {1}{2} \left(\mathbf {x} - \mathbf {x} _ {o}\right) ^ {T} \mathbf {H} \left(\mathbf {x} - \mathbf {x} _ {o}\right)
$$

where $ \nabla $ and $ \mathbf{H} $ are the gradient and Hessian of f with respect to x when evaluated at $ \mathbf{x}_{o} $

$$
\nabla \equiv \nabla_ {\mathbf {X}} [ f ] \big | _ {\mathbf {X} = \mathbf {X} _ {o}} \quad \mathrm {a n d} \quad \mathbf {H} \equiv \mathbf {H} _ {\mathbf {X}} [ f ] \big | _ {\mathbf {X} = \mathbf {X} _ {o}}
$$

At an equilibrium point, $ \widehat{\mathbf{x}} $ all first partials are zero, so $ \left( \nabla_{\mathbf{x}}[f]\right)^{T} $ is evaluated at $ \widehat{\mathbf{x}} $ is a vector of length zero. Whether this point is a maximum or minimum is then determined by the quadratic product involving the Hessian when evaluated at $ \widehat{\mathbf{x}} $ . Consider a vector, d, of a small change from the equilibrium point

$$
f (\widehat {\mathbf {x}} + \mathbf {d}) - f (\widehat {\mathbf {x}}) \simeq \frac {1}{2} \cdot \mathbf {d} ^ {T} \mathbf {H} \mathbf {d}
$$

Because H is a symmetric matrix, we can diagonalize it and apply a canonical transformation (Equation A5.17a) to simplify the quadratic product in Equation A6.8a, which returns

$$
f (\widehat {\mathbf {x}} + \mathbf {d}) - f (\widehat {\mathbf {x}}) \simeq \frac {1}{2} \sum_ {i = 1} ^ {n} \lambda_ {i} y _ {i} ^ {2}
$$

where $ y_{i}=\mathbf{e}_{i}^{T}\mathbf{d} $ with $ \mathbf{e}_{i} $ and $ \lambda_{i} $ representing the eigenvectors and eigenvalues of the Hessian when evaluated at $ \widehat{\mathbf{x}} $ . Thus, if H is positive-definite (all eigenvalues of H are positive), f increases in all directions around $ \widehat{\mathbf{x}} $ , and hence $ \widehat{\mathbf{x}} $ is a local minimum of f. If H is negative-definite (all eigenvalues of H are negative), f decreases in all directions around $ \widehat{\mathbf{x}} $ , and $ \widehat{\mathbf{x}} $ is a local maximum of f. If the eigenvalues differ in sign (H is indefinite), $ \widehat{\mathbf{x}} $ corresponds to a saddle point (to see this, suppose $ \lambda_{1}>0 $ and $ \lambda_{2}<0 $ ; any change along the vector $ \mathbf{e}_{1} $ results in an increases in f, while any change along $ \mathbf{e}_{2} $ results in a decrease in f).

Example A6.7. Consider the following demonstration (due to Lande 1979a) that the mean population fitness increases. A round of selection changes the current vector of means from $ \mu $ to $ \mu+ \Delta\mu. $ Expanding the log of mean fitness in a Taylor series around the current population mean gives the change in mean population fitness as

$$
\begin{array}{l} \Delta \ln \overline {{W}} (\mu) = \ln \overline {{W}} (\mu + \Delta \mu) - \ln \overline {{W}} (\mu) \\ \simeq \left(\nabla \mu [ \ln \overline {{W}} (\mu) ]\right) ^ {T} \Delta \mu + \frac {1}{2} \Delta \mu^ {T} \mathbf {H} \mu [ \ln \overline {{W}} (\mu) ] \Delta \mu \\ \end{array}
$$

If we assume that second- and higher-order terms can be neglected (as would occur with weak selection and the population mean away from an equilibrium point), then Equation A6.9a simplifies to

$$
\Delta \ln \overline {{W}} (\boldsymbol {\mu}) \simeq \left(\nabla_ {\boldsymbol {\mu}} [ \ln \overline {{W}} (\boldsymbol {\mu}) ]\right) ^ {T} \Delta \boldsymbol {\mu}
$$

Further assuming that the joint distribution of phenotypes and additive genetic values is MVN, then substituting Equation A6.2e into Equation A6.9b yields

$$
\Delta \ln \overline {{W}} (\boldsymbol {\mu}) \simeq \boldsymbol {\beta} ^ {T} \Delta \boldsymbol {\mu}
$$

Because $ \Delta\mu $ is the response vector, R, rearranging Equation 13.26a yields $ \beta=\mathbf{G}^{-1}\mathbf{R}=\mathbf{G}^{-1}\Delta\mu $ . Substituting this expression into Equation A6.9c yields

$$
\Delta \ln \overline {{W}} (\boldsymbol {\mu}) \simeq \left(\mathbf {G} ^ {- 1} \Delta \boldsymbol {\mu}\right) ^ {T} \Delta \boldsymbol {\mu} = \left(\Delta \boldsymbol {\mu}\right) ^ {T} \mathbf {G} ^ {- 1} \Delta \boldsymbol {\mu} \geq 0
$$

The inequality follows because G is a variance-covariance matrix and hence is nonnegative definite (all its eigenvalues are nonnegative). Under these conditions, mean population fitness never decreases, although because $ \Delta\mu\neq\nabla\mu[\ln \overline{W}(\mu)] $ , the local increase in fitness does not necessarily improve in the fastest possible manner. Note that

$$
\Delta \ln \overline {{W}} (\boldsymbol {\mu}) = \ln \overline {{W}} (\boldsymbol {\mu} [ t + 1 ]) - \ln \overline {{W}} (\boldsymbol {\mu} [ t ]) = \ln \left(\frac {\overline {{W}} (\boldsymbol {\mu} [ t + 1 ])}{\overline {{W}} (\boldsymbol {\mu} [ t ])}\right)
$$

so $ \Delta\ln \overline{W} (\mu) > 0 $ implies $ \overline{W} (\mu [t+1]) > \overline{W} (\mu [t]) $ . Notice from Equation A6.2f that when fitnesses are frequency-dependent, $ \nabla \mu [\ln \overline{W} (\mu)] $ has an extra term beyond $ \beta $ , and the above proof does not hold (namely, mean fitness can decrease).

## OPTIMIZATION UNDER CONSTRAINTS

Occasionally, we wish to find the maximum or minimum of a function subject to a constraint. The solution is to use Lagrange multipliers. Suppose we wish to find the extrema of a function, f(x), subject to the constraint that $ h(\mathbf{x})=c $ . We first construct a new function by considering

$$
g (\mathbf {x}, \lambda) = f (\mathbf {x}) - \lambda [ h (\mathbf {x}) - c ]
$$

Because $ h (\mathbf{x})-c=0 $ , the extrema of $ g (\mathbf{x},\lambda) $ correspond to the extrema of $ f (\mathbf{x}) $ under the constraint. Local maxima and minima are obtained by solving the following set of equations:

$$
\nabla_ {\mathbf {X}} [ g (\mathbf {x}, \lambda) ] = \nabla_ {\mathbf {X}} [ f (\mathbf {x}) ] - \lambda \cdot \nabla_ {\mathbf {X}} [ h (\mathbf {x}) ] = 0
$$

$$
\frac {d g (\mathbf {x} , \lambda)}{d \lambda} = h (\mathbf {x}) - c = 0
$$

Observe that the second equation is satisfied by the constraint.

Example A6.8. A standard approach for selection on multiple traits is to use a selection index, I, which is a new (univariate) trait that is a linear combination of n characters $ \mathbf{z}=\left(z_{1},z_{2},\cdots,z_{n}\right)^{T} $ , with

$$
I = \mathbf {b} ^ {T} \mathbf {z} = \sum_ {k = 1} ^ {n} b _ {k} z _ {k}
$$

Notice that what matters for the weights are their relative proportions, as, if we were to multiply all of the weights by the same constant (e.g., $ a b_{k} $), this new index would still choose the same individuals. Hence, to obtain a standardized index, we impose the constraint $ \mathbf{b}^{T}\mathbf{b}=1 $ . We denote the directional selection differential on the index by $ S_{I} $ , and observe that if S is the vector of directional selection differentials generated by selecting on I, then $ S_{I}=\mathbf{b}^{T}\mathbf{S}. $

Smith (1936) and Hazel (1943) showed that a larger response in a target index is obtained by selecting on a different index. Suppose our aim is to maximize the response in the index,

$$
J = \mathbf {a} ^ {T} \boldsymbol {\mu} = \sum a _ {k} \mu_ {k}
$$

What are the standardized weights, b, for the optimal Smith-Hazel index (for a fixed amount of selection, $ S_{I}=s $)? If we assume that the conditions leading to the multivariate breeder's equation hold, the function to maximize is

$$
f (\mathbf {b}) = \mathbf {a} ^ {T} \Delta \boldsymbol {\mu} = \mathbf {a} ^ {T} \mathbf {R} = \mathbf {a} ^ {T} \mathbf {G P} ^ {- 1} \mathbf {S}
$$

under the associated constraint function

$$
g (\mathbf {b}) - c = \mathbf {b} ^ {T} \mathbf {b} - 1 = 0
$$

Because $ S_{I}=\mathbf{b}^{T}\mathbf{S} $ , and we have the constraint that $ \mathbf{b}^{T}\mathbf{b}=1 $ , set $ \mathbf{S}=s\cdot\mathbf{b} $ , so that $ S_{I}=\mathbf{b}^{T}\mathbf{S}=s\cdot\mathbf{b}^{T}\mathbf{b}=s $ . If we use these functions, Equation A6.10a yields

$$
\begin{array}{l} \nabla_ {\mathbf {b}} [ g (\mathbf {b}, \lambda) ] = s \cdot \nabla_ {\mathbf {b}} \left[ \mathbf {a} ^ {T} \mathbf {G P} ^ {- 1} \mathbf {b} \right] - \lambda \cdot \nabla_ {\mathbf {b}} \left[ \mathbf {b} ^ {T} \mathbf {b} \right] \\ = s \cdot \left(\mathbf {a} ^ {T} \mathbf {G P} ^ {- 1}\right) ^ {T} - (2 \lambda) \cdot \mathbf {b} \\ \end{array}
$$

which is equal to zero when

$$
\mathbf {b} = \left(2 \lambda / s\right) \cdot \mathbf {P} ^ {- 1} \mathbf {G} ^ {T} \mathbf {a}
$$

Note that the constant $ 2\lambda /s $ simply standardizes the weights (so that $ \mathbf{b}^{T}\mathbf{b}=1 $), and hence the Smith-Hazel weights are usually written as

$$
\mathbf {b} _ {S H} = \mathbf {P} ^ {- 1} \mathbf {G} ^ {T} \mathbf {a}
$$

which can be standardized by noting that

$$
\mathbf {b} = \frac {\mathbf {b} _ {S H}}{\| \mathbf {b} _ {S H} \|} = \frac {\mathbf {b} _ {S H}}{\sqrt {\mathbf {b} _ {S H} ^ {T} \mathbf {b} _ {S H}}}
$$

Index selection is examined in detail in Volume 3.