# Appendix 6 · Appendix 6 / Derivatives of Vectors and Vector-valued Functions

## Evolution_appendix6_001 · Appendix: Introduction

Mathematics is a collection of cheap tricks and dirty jokes. Lipman Bers

Quantitative genetics often deals with vector-valued functions, and here we provide a brief review of the calculus of such functions. In particular, we review common expressions for derivatives of vectors and vector-valued functions, introduce the gradient vector and Hessian matrix (for first and second partials, respectively), and use this machinery in multidimensional Taylor series for approximating functions around a specific value. We apply these results to several problems in selection theory and evolution.

---

## Evolution_appendix6_002 · Appendix: Introduction / DERIVATIVES OF VECTORS AND VECTOR-VALUED FUNCTIONS

Suppose we let $f(\mathbf{x})$ be a scalar (single-dimension) function of a column vector, $\mathbf{x} = (x_1, \cdots, x_n)^T$, of $n$ variables. The gradient (or gradient vector) of $f$ with respect to $\mathbf{x}$ is obtained by taking partial derivatives of the function with respect to each variable. In matrix notation, the gradient operator is denoted by

$$
\nabla\mathbf{x}[f]=\frac{\partial f}{\partial\mathbf{x}}=\begin{pmatrix}\frac{\partial f}{\partial x_{1}}\\ \vdots\\ \frac{\partial f}{\partial x_{n}}\end{pmatrix}
$$

The gradient at a point, $ x_{o} $, corresponds to a vector indicating the direction of local steepest ascent of the function at that point (the multivariate slope of $ f $ at $ x_{o} $).

**[示例 Example]**

*(See Example A6.1.)*

**[示例 Example]**

*(See Example A6.2.)*

**[示例 Example]**

*(See Example A6.3.)*

**[示例 Example]**

*(See Example A6.4.)*

THE HESSIAN MATRIX, LOCAL MAXIMA/MINIMA, AND MULTIDIMENSIONAL TAYLOR SERIES

In univariate calculus, the local extrema of a function occur when its slope (first derivative) is zero. The multivariate extension is that the gradient vector is zero, so the slope of the function with respect to all variables is zero. A point $ x {e} $ where this occurs is called a stationary or equilibrium point, and corresponds to either a local maximum, minimum, saddle point, or inflection point. As with the calculus of single variables, determining which of these cases is correct depends on the second derivative. With n variables, the appropriate generalization is the Hessian matrix

**[推导 Derivation]**

$$
\mathbf{H} {\mathbf{X}}[f]=\nabla {\mathbf{X}}\left[\left(\nabla {\mathbf{X}}[f]\right)^{T}\right]=\frac{\partial^{2}f}{\partial\mathbf{x}\partial\mathbf{x}^{T}}=\left(\begin{array}{c c c}\frac{\partial^{2}f}{\partial x {1}^{2}}&\cdots&\frac{\partial^{2}f}{\partial x {1}\partial x {n}}\\ \vdots&\ddots&\vdots\\ \frac{\partial^{2}f}{\partial x {1}\partial x {n}}&\cdots&\frac{\partial^{2}f}{\partial x {n}^{2}}\end{array}\right)
$$

Note that this is the outer product of $ \nabla {\mathbf{x}} [f] $ with itself. Recall for an $ n $-dimensional column vector $ \mathbf{a} {n\times1} $ that while the inner product, $ \mathbf{a} {1\times n}^T \mathbf{a} {n\times1} = \sum a i $, returns a $ 1 \times 1 $ matrix (a scalar), the outer product, $ \mathbf{a} {n\times1} \mathbf{a} {1\times n}^T $, returns an $ n \times n $ matrix whose $ ij $th element is $ a i a j $, or (in our case)

**[推导 Derivation]**

$$
\mathbf{H} {ij}=\frac{\partial\left(f(\mathbf{x})/\partial x {i}\right)}{\partial x {j}}=\frac{\partial^{2}f(\mathbf{x})}{\partial x {i}\partial x {j}}
$$

This matrix is symmetric, as mixed partials are equal under suitable continuity conditions, and it measures the local multidimensional curvature of the function.

where all partials are evaluated at $ \mathbf{x} o $. If we note that the first sum is the inner product of the gradient and $ (\mathbf{x} - \mathbf{x} o) $, and the double sum is a quadratic product involving the Hessian, we can express Equation A6.7a in matrix form as

**[推导 Derivation]**

$$
f(\mathbf{x})\simeq f(\mathbf{x} {o})+\nabla^{T}(\mathbf{x}-\mathbf{x} {o})+\frac{1}{2}(\mathbf{x}-\mathbf{x} {o})^{T}\mathbf{H}(\mathbf{x}-\mathbf{x} {o})
$$

where $ \nabla $ and H are the gradient and Hessian of f with respect to x when evaluated at $ x {0} $,

**[推导 Derivation]**

$$
\nabla \equiv \left.\nabla_{\mathbf{X}}[f]\right|_{\mathbf{X}=\mathbf{X}_o} \qquad \text{and} \qquad \mathbf{H} \equiv \left.\mathbf{H}_{\mathbf{X}}[f]\right|_{\mathbf{X}=\mathbf{X}_o}
$$

At an equilibrium point, $ \hat{x} $, all first partials are zero, so $ (\nabla {\mathbf{x}}[f])^{T} $ is evaluated at $ \hat{x} $ is a vector of length zero. Whether this point is a maximum or minimum is then determined by the quadratic product involving the Hessian when evaluated at $ \hat{x} $. Consider a vector, d, of a small change from the equilibrium point

**[推导 Derivation]**

$$
f(\hat{\mathbf{x}}+\mathbf{d})-f(\hat{\mathbf{x}})\simeq\frac{1}{2}\cdot\mathbf{d}^{T}\mathbf{H}\mathbf{d}
$$

Because H is a symmetric matrix, we can diagonalize it and apply a canonical transformation (Equation A5.17a) to simplify the quadratic product in Equation A6.8a, which returns

**[推导 Derivation]**

$$
f(\widehat{\mathbf{x}}+\mathbf{d})-f(\widehat{\mathbf{x}})\simeq\frac{1}{2}\sum {i=1}^{n}\lambda {i}y {i}^{2}
$$

To see how the Hessian matrix determines the nature of equilibrium points, a slight digression on the multidimensional Taylor series is needed. Consider the (second-order) Taylor series of a scalar function of $n$ variables, $f(x 1, \cdots, x n)$, expanded about the point $\mathbf{x} o$,

**[推导 Derivation]**

$$
f(\mathbf{x})\simeq f(\mathbf{x} {o})+\sum {i=1}^{n}(x {i}-x {o,i})\frac{\partial f}{\partial x {i}}+\frac{1}{2}\sum {i=1}^{n}\sum {j=1}^{n}(x {i}-x {o,i})(x {j}-x {o,j})\frac{\partial^{2}f}{\partial x {i}\partial x {j}}+\cdots
$$

where $ y i = e i^T d $, with $ e i $ and $ \lambda i $ representing the eigenvectors and eigenvalues of the Hessian when evaluated at $ \hat{x} $. Thus, if $ \hat{H} $ is positive-definite (all eigenvalues of $ \hat{H} $ are positive), $ f $ increases in all directions around $ \hat{x} $, and hence $ \hat{x} $ is a local minimum of $ f $. If $ \hat{H} $ is negative-definite (all eigenvalues of $ \hat{H} $ are negative), $ f $ decreases in all directions around $ \hat{x} $, and $ \hat{x} $ is a local maximum of $ f $. If the eigenvalues differ in sign ( $ \hat{H} $ is indefinite), $ \hat{x} $ corresponds to a saddle point (to see this, suppose $ \lambda 1 0 $ and $ \lambda 2 < 0 $; any change along the vector $ e 1 $ results in an increase in $ f $, while any change along $ e 2 $ results in a decrease in $ f $).

**[示例 Example]**

*(See Example A6.5.)*

**[示例 Example]**

*(See Example A6.6.)*

---

## Evolution_appendix6_004 · Appendix: Introduction / OPTIMIZATION UNDER CONSTRAINTS

**[示例 Example]**

*(See Example A6.7.)*

Occasionally, we wish to find the maximum or minimum of a function subject to a constraint. The solution is to use Lagrange multipliers. Suppose we wish to find the extrema of a function, $ f(\mathbf{x}) $, subject to the constraint that $ h(\mathbf{x}) = c $. We first construct a new function by considering

$$
g(\mathbf{x},\lambda)=f(\mathbf{x})-\lambda[h(\mathbf{x})-c]
$$

Because $ h(\mathbf{x}) - c = 0 $, the extrema of $ g(\mathbf{x}, \lambda) $ correspond to the extrema of $ f(\mathbf{x}) $ under the constraint. Local maxima and minima are obtained by solving the following set of equations:

$$
\nabla_{\mathbf{x}}[g(\mathbf{x},\lambda)]=\nabla_{\mathbf{x}}[f(\mathbf{x})]-\lambda\cdot\nabla_{\mathbf{x}}[h(\mathbf{x})]=\mathbf{0}
$$

$$
\frac{d g(\mathbf{x},\lambda)}{d\lambda}=h(\mathbf{x})-c=0
$$

Observe that the second equation is satisfied by the constraint.

**[示例 Example]**

*(See Example A6.8.)*

---
