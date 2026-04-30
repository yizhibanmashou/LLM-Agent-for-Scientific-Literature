<div align="center">

# Appendix 5

</div>

<div align="center">

# The Geometry of Vectors and Matrices: Eigenvalues and Eigenvectors

</div>

Much of the presentation that follows is in matrix notation, and for this I offer no apology as this has rapidly become an essential tool of any serious student of animal breeding. Henderson (1973)

The basic concepts of matrix algebra were introduced in LW Chapter 8 and LW Appendix A3, and we assume the reader has this level of understanding (which includes matrix multiplication, inverses, and determinants). If not, a quick review of LW Chapter 8 before proceeding will be helpful. A deeper understanding of multivariate issues in quantitative genetics requires an appreciation of matrix geometry. Our primary intent here is to introduce the reader to the idea of vectors and matrices as geometric structures, and thus viewing matrix operations as transformations converting one vector into another by a change in geometry (rotation and scaling), which is completely summarized by the eigenvalues (scaling), and their associated eigenvectors (rotation), of a matrix.

## THE GEOMETRY OF VECTORS AND MATRICES

As there are numerous excellent texts on matrix algebra, we made little effort to prove most of the results given below. For statistical applications, concise introductions can be found in the chapters on matrix methods in Johnson and Wichern (1988) and Morrison (1976), while Dhrymes (1978) and Searle (1982) provided more extended treatments. Wilf's (1978) short chapter on matrix methods provides a very nifty review of methods useful in applied mathematics. Franklin (1968), Horn and Johnson (1985), and Gantmacher (1960), respectively, presented increasingly sophisticated treatments of matrix analysis.

## Comparing Vectors: Lengths and Angles

As Figure A5.1A shows, a vector, x, can be treated as a geometric object, consisting of an arrow leading from the origin to an n-dimensional point whose coordinates are given by the elements of x. By changing coordinate systems, we change the resulting vector, potentially changing both its direction (rotating the vector) and length (scaling the vector). This geometric interpretation suggests several ways for comparing vectors, such as the angle between two vectors and the projection of one vector onto another.

Consider first the length (or norm) of a vector. The most common measure of length is the Euclidean distance of the vector from the origin, $ \| \mathbf{x} \| $ , defined as

$$
| | \mathbf {x} | | = \sqrt {x _ {1} ^ {2} + x _ {2} ^ {2} + \cdots + x _ {n} ^ {2}} = \sqrt {\mathbf {x} ^ {T} \mathbf {x}}
$$

For any scalar a, $ \|a\mathbf{x}\|=|a|\| \mathbf{x}\| $ . Similarly, the squared Euclidean distance between the vectors x and y is

$$
\left\| \mathbf {x} - \mathbf {y} \right\| ^ {2} = \sum_ {i = 1} ^ {n} \left(x _ {i} - y _ {i}\right) ^ {2} = (\mathbf {x} - \mathbf {y}) ^ {T} (\mathbf {x} - \mathbf {y}) = (\mathbf {y} - \mathbf {x}) ^ {T} (\mathbf {y} - \mathbf {x})
$$

Vectors can differ by length, direction, or both. The angle, $ \theta $ , between two vectors (x and y) provides a measure of how much they differ in direction (Figure A5.1C). If the vectors

<div align="center">

(A)

</div>

![](page=1,bbox=[349, 132, 486, 216])

<div align="center">

(B)

</div>

![](page=1,bbox=[536, 132, 731, 218])

![](page=1,bbox=[348, 241, 489, 348])

![](page=1,bbox=[522, 241, 783, 356])

<div align="center">

Figure A5.1 Some basic geometric concepts of vectors. While we use examples from two dimensions, these concepts easily extend to n dimensions. A: A vector x can be thought of as an arrow from the origin to a point in space whose coordinates are given by the elements of x. B: Multiplying a vector by $ - 1 $ results in a reflection about the origin. C: One measure of the difference in direction between two vectors is the angle $ (\theta) $ between them. D: Proj(b on a) is the vector resulting from the projection of b onto a. Note that the resulting projection vector is either in the same direction as a or in the direction of the reflection of a, as seen for Proj(c on a).

</div>

satisfy ax=y, they both point in exactly the same direction （ $ \theta=0 $ ; they are codirectional) when a > 0. If a < 0, they are exactly 180 degrees apart and differ in direction only by a reflection about the origin (Figure A5.1B). At the other extreme, two vectors can be at right angles to each other （ $ \theta=90^{\circ} $ or $ 270^{\circ} $ ）, in which case they are said to be orthogonal. Orthogonal vectors of unit length are further said to be orthonormal. For any two n-dimensional vectors, $ \theta $ satisfies

$$
\cos (\theta) = \frac {\mathrm {x} ^ {T} \mathrm {y}}{| | \mathrm {x} | | | | \mathrm {y} | |} = \frac {\mathrm {y} ^ {T} \mathrm {x}}{| | \mathrm {x} | | | | \mathrm {y} | |}
$$

Hence,

$$
\theta = \cos^ {- 1} \left(\frac {\mathbf {y} ^ {T} \mathbf {x}}{| | \mathbf {x} | | | | \mathbf {y} | |}\right)
$$

If both x and y are of unit length, then $ \theta=\cos^{-1}({\bf y}^{T}{\bf x}) $ , which reveals the close connection between vector angles and inner products. Note that because $ \cos(90^{\circ})=\cos(270^{\circ})=0 $ , two vectors are orthogonal if, and only if, their inner product is zero, $ {\bf x}^{T}{\bf y}=0. $

Another way to compare two vectors is to consider the projection vector of one onto the other. Proj(x on y), the projection of x on y, is a vector in the direction of y, whose length is given by how much of the vector x lies along the direction of y. For any two n-dimensional vectors, the projection of x on y is defined by

$$
\operatorname {P r o j} (\mathbf {x} \mathrm {o n} \mathbf {y}) = \frac {\mathbf {x} ^ {T} \mathbf {y}}{\mathbf {y} ^ {T} \mathbf {y}} \mathbf {y} = \frac {\mathbf {x} ^ {T} \mathbf {y}}{| | \mathbf {y} | | ^ {2}} \mathbf {y} = \left(\cos (\theta) \frac {| | \mathbf {x} | |}{| | \mathbf {y} | |}\right) \mathbf {y}
$$

The term in the parentheses (which follows from Equation A5.2a) is a scalar, representing the length that x projects in the direction of y, which means that Proj(x on y) is a scaled version of the vector y onto which we are projecting. If $ \| y \|=1 $ , then

$$
\operatorname {P r o j} (\mathbf {x} \mathrm {o n} \mathbf {y}) = \left(\mathbf {x} ^ {T} \mathbf {y}\right) \mathbf {y} = \left(\cos (\theta) \left\| \mathbf {x} \right\|\right) \mathbf {y}
$$

The vector resulting from the projection of x on y is in the same direction as y unless $ 9 0^{\circ} < \theta < 2 7 0^{\circ} $ , in which case $ \cos(\theta)<0 $ and the projection vector is in exactly the opposite direction (the reflection of y about the origin). The length of the projection vector is

$$
| | \operatorname {P r o j} (\mathbf {x} \mathrm {o n} \mathbf {y}) | | = | \cos (\theta) | | | \mathbf {x} | | \leq | | \mathbf {x} | |
$$

If two vectors lie in exactly the same direction $ (\theta=0) $ , the projection of one on the other simply recovers the vector (i.e., $ \operatorname{Proj} ( \mathbf{x} \mathrm{o n} \mathbf{y})=\mathbf{x} $ ). Conversely, if two vectors are orthogonal, the projection of one on the other yields a vector of length zero.

An important property of projection vectors is that if $ \mathbf{y}_{1},\mathbf{y}_{2},\cdots,\mathbf{y}_{n} $ is any set of mutually orthogonal n-dimensional vectors, then any n-dimensional vector x can be represented as the sum of projections of x onto the members of this set, namely,

$$
\mathbf {x} = \sum_ {i = 1} ^ {n} \operatorname {P r o j} \left(\mathbf {x} \mathrm {o n} \mathbf {y} _ {i}\right)
$$

One way to think about such a decomposition is as the transformation from one set of axes (or coordinates) into another (defined by the vectors, $ y_{i} $ , that span, or completely cover, the vector space). We can also consider the projection of a vector into some subspace of a matrix (say $ y_{1}, \dots , y_{k} $ , where k<n), namely, the projection onto some subset of the vectors that span the space of the original matrix. For example, one might consider the subspace of a covariance matrix imposed by (say) its three largest factors (eigenvalues). The notion of a subspace of the genetic covariance matrix G will prove useful in describing the constraints caused by the genetic covariance structure (Volume 3).

## Matrices Describe Vector Transformations

When we multiply a vector, x, by a matrix, A, to create a new vector, y = Ax, A rotates and scales the original vector, x, into the new vector, y. A therefore describes a transformation of the original coordinate system of x into a new coordinate system, y (which has a different dimension from x unless A is square).

Example A5.1. Consider the Lande version of the multivariate breeder's equation, $ \mathbf{R}=\mathbf{G}\beta $ (Equation 13.26a). Here $ \mathbf{R} $ is the change in the vector of phenotypic means resulting from selection, $ \mathbf{G} $ is the covariance matrix of additive-genetic values (breeding values) of the characters, and $ \beta $ is the directional selection gradient (the direction of change in character means that results in the greatest increase in mean population fitness; Chapters 13 and 30). Suppose

$$
\mathbf {G} = \left( \begin{array}{c c} 4 & - 2 \\ - 2 & 2 \end{array} \right) \quad \mathrm {a n d} \quad \beta = \left( \begin{array}{c} 1 \\ 3 \end{array} \right), \quad \mathrm {y i e l d i n g} \quad \mathbf {R} = \mathbf {G} \beta = \left( \begin{array}{c} - 2 \\ 4 \end{array} \right)
$$

The resulting direction of change in character means is different from that most favored by natural selection. Selection $ (\beta) $ favors an increase in trait one $ (z_{1}) $ , but when the genetic covariance structure is taken into account, the resulting change in the mean of $ z_{1} $ is negative. If we take the appropriate inner products, we find $ ||\beta||=\sqrt{10},||\mathbf{R}||=\sqrt{20} $ , and $ \beta^{T}\mathbf{R}=10 $ Equation A5.2a returns

$$
\cos (\theta) = \frac {\beta^ {T} \mathbf {R}}{| | \mathbf {R} | | | | \beta | |} = \frac {1}{\sqrt {2}}
$$

The resulting angle between the selection gradient and response vector is $ \cos^{-1}(1 / \sqrt{2})= 4 5^{\circ} $ , implying that the constraints introduced by the genetic covariance matrix rotate the response vector considerably away from the direction most favored by natural selection (Figure A5.2).

![](page=3,bbox=[497, 119, 635, 256])

<div align="center">

Figure A5.2 If we use the values of $ \beta $ and G from Example A5.1, observe that G translates the directional selection gradient vector ( $ \beta $ ) into the response vector ( R ) in a counterintuitive fashion. While $ \beta $ shows that fitness is maximized by increasing both traits 1 and 2, the resulting response vector, R, increases trait 2 but decreases trait 1. This behavior results from the strong negative additive-genetic covariance between $ z_{1} $ and $ z_{2} $ , as will become more obvious shortly, when we consider the eigenvectors of G (Figure A5.3). As shown in Example A5.1, the angle between the vectors $ \beta $ and R is 45 degrees.

</div>

## Orthonormal Matrices: Rigid Rotations

A key building block on our way to the partitioning of a matrix into its rotational and scaling components is the idea of an orthonormal matrix. Writing a square n $ \times $ n matrix, U, as a row vector whose n elements are $ 1 \times n $ column vectors, $ \mathbf{U}=(\mathbf{u}_{1},\mathbf{u}_{2},\cdots,\mathbf{u}_{n}) $ , then U is said to be orthonormal if

$$
\mathbf {u} _ {i} ^ {T} \mathbf {u} _ {j} = \left\{ \begin{array}{l l} 1 & \mathrm {i f} i = j \\ 0 & \mathrm {i f} i \neq j \end{array} \right.
$$

Namely, each column of U is of unit length and is orthogonal to every other column. Matrices with this property are also referred to as unitary and satisfy

$$
\mathbf {U} ^ {T} \mathbf {U} = \mathbf {U} \mathbf {U} ^ {T} = \mathbf {I}
$$

As a result, the inverse of a unitary matrix is simply its transpose,

$$
\mathbf {U} ^ {T} = \mathbf {U} ^ {- 1}
$$

The coordinate transformation induced by an orthonormal matrix has a very simple geometric interpretation: it is a rigid rotation of the original coordinate system—axes of the original coordinates are all rotated by the same angle to create the new coordinate system. To see this, first note that orthonormal matrices preserve all inner products. Taking $ y_{1}=\mathrm{U x}_{1} $ and $ y_{2}=\mathrm{U x}_{2} $

$$
\mathbf {y} _ {1} ^ {T} \mathbf {y} _ {2} = \mathbf {x} _ {1} ^ {T} \left(\mathbf {U} ^ {T} \mathbf {U}\right) \mathbf {x} _ {2} = \mathbf {x} _ {1} ^ {T} \mathbf {x} _ {2}
$$

Thus, orthonormal matrices do not change (scale) the length of vectors, as $ \| y_{1}\|=y_{1}^{T} y_{1}=\mathrm{x}_{1}^{T}\mathrm{x}_{1}=\| \mathrm{x}_{1}\| $ . Using these results, note that if $ \theta $ is the angle between the vectors $ \mathrm{x}_{1} $ and $ \mathrm{x}_{2} $ then following transformation by an orthonormal matrix

$$
\cos \left(\theta \mid \mathbf {y} _ {1}, \mathbf {y} _ {2}\right) = \frac {\mathbf {y} _ {1} ^ {T} \mathbf {y} _ {2}}{\sqrt {\left\| \mathbf {y} _ {1} \right\| \left\| \mathbf {y} _ {2} \right\|}} = \frac {\mathbf {x} _ {1} ^ {T} \mathbf {x} _ {2}}{\sqrt {\left\| \mathbf {x} _ {1} \right\| \left\| \mathbf {x} _ {2} \right\|}} = \cos \left(\theta \mid \mathbf {x} _ {1}, \mathbf {x} _ {2}\right)
$$

which shows that the angle between the two vectors remains unchanged following their transformation by the same orthonormal matrix.

## Eigenvalues and Eigenvectors

The eigenvalues, and their associated eigenvectors, of a square matrix describe its transformational geometry. Eigenvalues describe how the original coordinate axes are scaled in the

new coordinate system that is described by the eigenvectors (i.e., how the original axes are rotated).

To more formally introduce eigenvalues and eigenvectors, suppose, for a square matrix A, that the vector y satisfies the matrix equation

$$
\mathbf {A} \mathbf {y} = \lambda \mathbf {y}
$$

for some scalar value, $ \lambda $ . Geometrically, this means that the new vector resulting from transformation of y by A points in the same direction as y (or is exactly reflected about the origin if $ \lambda < 0 $ ). For such vectors, the only action of the matrix transformation is to scale them by some amount, $ \lambda $ . These vectors thus represent the inherent axes associated with the transformation given by A, and the set of all such vectors, along with their corresponding scalar multipliers, completely describes the geometry of this transformation. Vectors that satisfy Equation A5.6 are referred to as eigenvectors, and their associated scaling factors are eigenvalues, and together they jointly describe the eigenstructure (the intrinsic geometry) of the square matrix, A. If y is an eigenvector, then ay is also an eigenvector, as $ \mathbf{A}(ay)= a(\mathbf{A}y)=\lambda(ay) $ . Note, however, that the associated eigenvalue, $ \lambda $ , remains unchanged. Hence, we typically scale eigenvectors to be of unit length to yield unit or normalized eigenvectors. In particular, if $ y_{i} $ is any eigenvector associated with the ith eigenvalue, then the associated normalized eigenvector is $ \mathbf{e}_{i}=\mathbf{y}_{i} / \| \mathbf{y}_{i}\| $ .

The eigenvalues of an n-dimensional square matrix, A, are solutions of Equation A5.6, which can be written as $ (\mathbf{A}-\lambda\mathbf{I})\mathbf{y}=\mathbf{0} $ . This implies that the determinant of $ (\mathbf{A}-\lambda\mathbf{I}) $ must equal zero, which gives rise to the characteristic equation, $ |\mathbf{A}-\lambda\mathbf{I}|=0 $ , whose solution yields the eigenvalues of A. This equation can be also be expressed using the Laplace expansion,

$$
| \mathbf {A} - \lambda \mathbf {I} | = (- \lambda) ^ {n} + S _ {1} (- \lambda) ^ {n - 1} + \dots + S _ {n - 1} (- \lambda) ^ {1} + S _ {n} = 0
$$

where $ | \mathbf{A} | $ denotes the determinant of A and $ S_{i} $ is the sum of all principal minors (minors including diagonal elements of the original matrix) of order i (minors, which are subsets of the full matrix, were defined in LW Chapter 8). Finding the eigenvalues thus requires solving a polynominal equation of order n, implying that there are exactly n eigenvalues (some of which may be identical, i.e., repeated). In practice, for n>2 this is accomplished numerically, and most statistical analysis packages offer routines to accomplish this task.

Two of these principal minors are easily obtained and provide information on the nature of the eigenvalues. The only principal minor having the same order of the matrix is the full matrix itself, which means that $ S_{n}=|\mathbf{A}| $ , the determinant of A. $ S_{1} $ is also related to an important matrix quantity, the trace. This is denoted by $ \operatorname{tr}(\mathbf{A}) $ , and is the sum of the diagonal elements of the matrix, namely,

$$
\operatorname {t r} (\mathbf {A}) = \sum_ {i = 1} ^ {n} A _ {i i}
$$

Observe that $ S_{1}=\operatorname{tr}(\mathbf{A}) $ , as the only principal minors of order one are the diagonal elements themselves, the sum of which equals the trace. Both the trace and determinant can be expressed as functions of the eigenvalues, with

$$
\operatorname {t r} (\mathbf {A}) = \sum_ {i = 1} ^ {n} \lambda_ {i} \quad \text {a n d} \quad | \mathbf {A} | = \prod_ {i = 1} ^ {n} \lambda_ {i}
$$

Hence A is singular $ (|\mathbf{A}|=0) $ if, and only if, at least one eigenvalue is zero. As we will see, if A is a covariance matrix, then its trace (the sum of its eigenvalues) measures its total amount of variation, as the eigenvalues of a covariance matrix are nonnegative $ (\lambda_{i}\geq0). $

Let $ \mathbf{e}_{i} $ be the (unit-length) eigenvector associated with eigenvalue $ \lambda_{i} $ . If the eigenvectors of A can be chosen to be mutually orthogonal, namely, $ \mathbf{e}_{i}^{T}\mathbf{e}_{j}=0 $ for $ i\neq j $ , then we can express A as

$$
\mathbf {A} = \lambda_ {1} \mathbf {e} _ {1} \mathbf {e} _ {1} ^ {T} + \lambda_ {2} \mathbf {e} _ {2} \mathbf {e} _ {2} ^ {T} + \dots + \lambda_ {n} \mathbf {e} _ {n} \mathbf {e} _ {n} ^ {T}
$$

This is called the spectral decomposition of A, and it is derived below in Equation A5.10d. Because $ \| \mathbf{e}_{i}\|=1 $ , Equation A5.3b gives the projection of x on $ \mathbf{e}_{i} $ as $ (\mathbf{x}^{T}\mathbf{e}_{i})\mathbf{e}_{i} $ . Note that $ \mathbf{e}_{i}(\mathbf{e}_{i}^{T}\mathbf{x})=(\mathbf{e}_{i}^{T}\mathbf{x})\mathbf{e}_{i}=(\mathbf{x}^{T}\mathbf{e}_{i})\mathbf{e}_{i} $ , as $ \mathbf{e}_{i}^{T}\mathbf{x} $ is a scalar, which implies that $ \mathbf{e}_{i}^{T}\mathbf{x}=(\mathbf{e}_{i}^{T}\mathbf{x})^{T}=\mathbf{x}^{T}\mathbf{e}_{i} $ Hence, from Equation A5.3b, we have

$$
\begin{array}{l} \mathbf {A} \mathbf {x} = \lambda_ {1} \mathbf {e} _ {1} \mathbf {e} _ {1} ^ {T} \mathbf {x} + \lambda_ {2} \mathbf {e} _ {2} \mathbf {e} _ {2} ^ {T} \mathbf {x} + \dots + \lambda_ {n} \mathbf {e} _ {n} \mathbf {e} _ {n} ^ {T} \mathbf {x} \\ = \lambda_ {1} \left(\mathbf {e} _ {1} ^ {T} \mathbf {x}\right) \mathbf {e} _ {1} + \lambda_ {2} \left(\mathbf {e} _ {2} ^ {T} \mathbf {x}\right) \mathbf {e} _ {2} + \dots + \lambda_ {n} \left(\mathbf {e} _ {n} ^ {T} \mathbf {x}\right) \mathbf {e} _ {n} \\ = \lambda_ {1} \operatorname {P r o j} (\mathbf {x} \mathrm {o n} \mathbf {e} _ {1}) + \lambda_ {2} \operatorname {P r o j} (\mathbf {x} \mathrm {o n} \mathbf {e} _ {2}) + \dots + \lambda_ {n} \operatorname {P r o j} (\mathbf {x} \mathrm {o n} \mathbf {e} _ {n}) \\ \end{array}
$$

If we again apply Equation A5.3b, we can express this decomposition as

$$
\mathbf {A} \mathbf {x} = \left\| \mathbf {x} \right\| \sum_ {i = 1} ^ {n} \left[ \lambda_ {i} \cdot \cos \left(\theta \mid \mathbf {x}, \mathbf {e} _ {i}\right) \right] \mathbf {e} _ {i}
$$

where $ \theta | \mathbf{x},\mathbf{e}_{i} $ denotes the angle between the vectors x and $ \mathbf{e}_{i} $ . Thus, one can view a matrix as a series of vectors that form the projection space (the eigenvectors), so when a vector is multiplied by this matrix, the resulting vector is the weighted (by the eigenvalues) sum of projections over all of the vectors (the $ \mathbf{e}_{i} $ ) that span the space defined by the matrix.

Example A5.2. Determine the eigenstructure of the genetic covariance matrix G shown in Example A5.1. Writing the characteristic equation, and recalling the expression for the determinant of a $ 2\times2 $ matrix ( LW Equation 8.12a), yields

$$
\begin{array}{l} | \mathbf {G} - \lambda \mathbf {I} | = \left| \left( \begin{array}{c c} 4 - \lambda & - 2 \\ - 2 & 2 - \lambda \end{array} \right) \right| \\ = (4 - \lambda) (2 - \lambda) - (- 2) ^ {2} = \lambda^ {2} - 6 \lambda + 4 = 0 \\ \end{array}
$$

Alternatively, if we use the Laplace expansion (Equation A5.7), and note that $ \operatorname{tr}(\mathbf{G})=4+2=6 $ and $ |\mathbf{G}|=4\cdot2-(-2)^{2}=4 $ , we will also recover the characteristic equation, which has solutions

$$
\lambda_ {1} = 3 + \sqrt {5} \simeq 5. 2 3 6 \quad \lambda_ {2} = 3 - \sqrt {5} \simeq 0. 7 6 4
$$

The associated unit eigenvectors (which as easily obtained, along with the eigenvectors, by using the R command eigen) are

$$
\mathbf {e} _ {1} \simeq \left( \begin{array}{c} - 0. 8 5 1 \\ 0. 5 2 6 \end{array} \right) \quad \mathbf {e} _ {2} \simeq \left( \begin{array}{c} 0. 5 2 6 \\ 0. 8 5 1 \end{array} \right)
$$

These are orthogonal as $ \mathbf{e}_{1}^{T}\mathbf{e}_{2}=0. $

The eigenstructure of G shows why the vector of responses, R, is rotated away from the direction of the vector that corresponds to the direction of selection, $ \beta $ . From Example A5.1, $ ||\beta||=\sqrt{10} $ , while $ \mathrm{e}_{1}^{T}\beta\simeq 0.727 $ and $ \mathrm{e}_{2}^{T}\beta\simeq 3.079 $ . Because $ ||\mathrm{e}_{1}||=||\mathrm{e}_{2}||=1 $ , Equation A5.2a simplifies to

$$
\cos \left(\theta | \mathbf {e} _ {1}, \beta\right) \simeq \frac {0 . 7 2 7}{\sqrt {1 0}} \simeq 0. 2 3 0 \quad \mathrm {a n d} \quad \cos \left(\theta | \mathbf {e} _ {2}, \beta\right) \simeq \frac {3 . 0 7 9}{\sqrt {1 0}} \simeq 0. 9 7 4
$$

giving the angle between $ \mathbf{e}_{1} $ and $ \beta $ as $ \theta(\mathbf{e}_{1},\beta)\simeq 76.7^{\circ} $ , while $ \theta(\mathbf{e}_{2},\beta)\simeq 13.2^{\circ} $ . Applying Equation A5.3b, the corresponding scaled projections of $ \beta $ on these eigenvectors are

$$
\begin{array}{l} \lambda_ {1} \operatorname {P r o j} (\boldsymbol {\beta} \mathrm {o n} \mathbf {e} _ {1}) = \lambda_ {1} \cos (\theta | \mathbf {e} _ {1}, \boldsymbol {\beta}) | | \boldsymbol {\beta} | | \mathbf {e} _ {1} = \left(5. 2 3 6 \cdot 0. 2 3 0 \cdot \sqrt {1 0}\right) \mathbf {e} _ {1} \\ = 3. 8 0 3 \binom {- 0. 8 5 1} {0. 5 2 6} = \binom {- 3. 2 3 6} {2} \\ \end{array}
$$

$$
\begin{array}{l} \lambda_ {2} \operatorname {P r o j} (\boldsymbol {\beta} \mathrm {o n} \mathbf {e} _ {2}) = \lambda_ {2} \cos (\theta | \mathbf {e} _ {2}, \boldsymbol {\beta}) | | \boldsymbol {\beta} | | \mathbf {e} _ {2} = \left(0. 7 6 4 \cdot 0. 9 7 4 \cdot \sqrt {1 0}\right) \mathbf {e} _ {2} \\ = 2. 3 5 3 \left( \begin{array}{c} 0. 5 2 6 \\ 0. 8 5 1 \end{array} \right) = \left( \begin{array}{c} 1. 2 3 6 \\ 2 \end{array} \right) \\ \end{array}
$$

![](page=6,bbox=[150, 122, 701, 277])

<div align="center">

Figure A5.3 Left: The scaled eigenvectors associated with the covariance matrix, G, from Example A5.1, plotted along with the selection gradient, $ \beta $ . Note that $ \mathbf{e}_{1} $ and $ \mathbf{e}_{2} $ are orthogonal and hence can be thought of as describing a new coordinate system. Because $ \lambda_{1}\gg\lambda_{2} $ , the leading eigenvector, $ \mathbf{e}_{1} $ , largely dominates the transformation. Right: This is shown by taking the projections of $ \beta $ on each of these eigenvectors (shown here on a magnified scale relative to the left figure). Even though $ \beta $ is nearly parallel to $ \mathbf{e}_{2} $ $ (\theta|\mathbf{e}_{1},\beta=1 3. 2^{\circ}) $ , the projection of $ \beta $ on $ \mathbf{e}_{1} $ yields a vector of greater length than the projection of $ \beta $ on $ \mathbf{e}_{2} $ (3.803 versus 2.353). From Equation A5.9b, the vector of responses to selection, R, is the sum of these two projections.

</div>

From Equation A5.9b, we can express the response, R, as the sum of the projections of $ \beta $ onto the eigenvalues of G, returning

$$
\begin{array}{l} \mathbf {R} = \mathbf {G} \beta = \lambda_ {1} \operatorname {P r o j} \left(\beta \mathrm {o n} \mathbf {e} _ {1}\right) + \lambda_ {2} \operatorname {P r o j} \left(\beta \mathrm {o n} \mathbf {e} _ {2}\right) \\ = \binom {- 3. 2 3 6} {2} + \binom {1. 2 3 6} {2} = \binom {- 2} {4} \\ \end{array}
$$

As Figure A5.3 shows, the eigenstructure of G explains the unusual behavior of the selection response seen in Figure A5.2. The eigenvector associated with the leading eigenvalue, $ \lambda_{1} $ accounts for most of the variation inherent in G (87% as $ \lambda_{1} / (\lambda_{1} + \lambda_{2}) = 0.87 $), and this eigenvector corresponds to a strong negative correlation between the additive-genetic values of $ z_{1} $ and $ z_{2} $ . Hence, even though $ \beta $ points in very much the same direction as $ \mathbf{e}_{2} $ , because $ \lambda_{1}\gg\lambda_{2} $ , the projection of $ \beta $ on $ \mathbf{e}_{1} $ yields a vector of greater length than the projection of $ \beta $ on $ \mathbf{e}_{2} $ (3.803 versus 2.353), and it is this $ \mathbf{e}_{1} $ projection vector that results in the decrease in $ \mu_{z_{1}} $ .

## PROPERTIES OF SYMMETRIC MATRICES

Many of the matrices encountered in quantitative genetics are symmetric, satisfying $ \mathbf{A}=\mathbf{A}^{T} $ (and therefore necessarily square). Examples include covariance matrices and the $ \gamma $ matrix of quadratic coefficients in the Pearson-Lande-Arnold fitness regression (Chapter 30). Symmetric matrices have a number of useful properties (proofs of which can be found in Dhrymes 1978; Horn and Johnson 1985; and Wilf 1978):

1. If A is symmetric, then if $ \mathbf{A}^{-1} $ exists, it is also symmetric.

2. The eigenvalues and eigenvectors of a symmetric matrix are all real.

3. For any n-dimensional symmetric matrix, a corresponding set of n orthonormal eigenvectors can be constructed, namely, we can obtain a set of eigenvalues $ \mathbf{e}_{i} $ for $ 1\leq i\leq n $ that satisfies

$$
\mathbf {e} _ {i} ^ {T} \mathbf {e} _ {j} = \left\{ \begin{array}{l l} 1 & \mathrm {i f} i = j \\ 0 & \mathrm {i f} i \neq j \end{array} \right.
$$

In particular, this guarantees that a spectral decomposition of A exists (Equation A5.9a).

4. A symmetric matrix A can be diagonalized as

$$
\mathbf {A} = \mathbf {U} \boldsymbol {\Lambda} \mathbf {U} ^ {T}
$$

where $ \Lambda $ is a diagonal matrix and U is an orthonormal matrix $ \left(\mathbf{U}^{-1}=\mathbf{U}^{T}\right). $ If $ \lambda_{i} $ and $ \mathbf{e}_{i} $ are the ith eigenvalue and its associated unit eigenvector of A, then

$$
\boldsymbol {\Lambda} = \operatorname {d i a g} \left(\lambda_ {1}, \lambda_ {2}, \dots , \lambda_ {n}\right) = \left( \begin{array}{c c c c} \lambda_ {1} & 0 & \dots & 0 \\ 0 & \lambda_ {2} & \dots & 0 \\ \vdots & & \ddots & \vdots \\ 0 & \dots & \dots & \lambda_ {n} \end{array} \right)
$$

and

$$
\mathbf {U} = \left(\mathbf {e} _ {1}, \mathbf {e} _ {2}, \dots , \mathbf {e} _ {n}\right)
$$

Geometrically, U is a unity matrix and thus describes a rigid rotation of the original coordinate system to a new coordinate system given by the eigenvectors of A, while the diagonal elements of A give the amount by which vectors of unit length in the original coordinate system are scaled in the transformed system. If we use the decomposition $ \Lambda=\sum_{i=1}^{n} \Lambda_{i} $ , where $ \Lambda_{i} $ is a diagonal matrix whose elements are all zero, except for $ \lambda_{i} $ , then Equation A5.10a becomes

$$
\mathbf {A} = \mathbf {U} \left(\sum_ {i = 1} ^ {n} \boldsymbol {\Lambda} _ {i}\right) \mathbf {U} ^ {T} = \sum_ {i = 1} ^ {n} \mathbf {U} \boldsymbol {\Lambda} _ {i} \mathbf {U} ^ {T} = \sum_ {i = 1} ^ {n} \lambda_ {i} \mathbf {e} _ {i} \mathbf {e} _ {i} ^ {T}
$$

recovering the spectral decomposition (Equation A5.9a). The last step in Equation A5.10d follows because $ \mathrm{e}_{i}^{T}\mathrm{e}_{j}=0 $ for $ i\neq j $ . Because of this feature, Equation A5.10a is also called the spectral factorization or eigendecomposition of A.

Using Equation A5.10a, it is easy to show that

$$
\mathbf {A} ^ {- 1} = \mathbf {U} \boldsymbol {\Lambda} ^ {- 1} \mathbf {U} ^ {T}
$$

To see this, note that

$$
\mathbf {A} ^ {- 1} \mathbf {A} = \left(\mathbf {U} \boldsymbol {\Lambda} ^ {- 1} \mathbf {U} ^ {T}\right) \left(\mathbf {U} \boldsymbol {\Lambda} \mathbf {U} ^ {T}\right) = \mathbf {U} \boldsymbol {\Lambda} ^ {- 1} \left(\mathbf {U} ^ {T} \mathbf {U}\right) \boldsymbol {\Lambda} \mathbf {U} ^ {T} = \mathbf {U} \boldsymbol {\Lambda} ^ {- 1} \boldsymbol {\Lambda} \mathbf {U} ^ {T} = \mathbf {U} \mathbf {U} ^ {T} = \mathbf {I}
$$

Similar logic yields

$$
\mathbf {A} ^ {1 / 2} = \mathbf {U} \boldsymbol {\Lambda} ^ {1 / 2} \mathbf {U} ^ {T}
$$

$$
\mathbf {A} ^ {- 1 / 2} = \mathbf {U} \boldsymbol {\Lambda} ^ {- 1 / 2} \mathbf {U} ^ {T}
$$

$$
\mathbf {A} ^ {k} = \mathbf {U} \boldsymbol {\Lambda} ^ {k} \mathbf {U} ^ {T} \quad \mathrm {f o r a n y i n t e g e r} k
$$

where the square root matrix, $ \mathbf{A}^{1/2} $ , satisfies $ \mathbf{A}^{1/2}\mathbf{A}^{1/2}=\mathbf{A} $ , and $ \mathbf{A}^{-1/2} $ satisfies $ \mathbf{A}^{-1/2}\mathbf{A}= $ $ \mathbf{A}\mathbf{A}^{-1/2}=\mathbf{A}^{1/2} $ , as well as $ \mathbf{A}^{-1/2}\mathbf{A}^{1/2}=\mathbf{A}^{1/2}\mathbf{A}^{-1/2}=\mathbf{I}. $

Because A is diagonal, theith diagonal elements of $ \Lambda^{-1},\Lambda^{1/2},\Lambda^{-1/2} $ , and $ \Lambda^{k} $ are $ \lambda_{i}^{-1}, $ $ \lambda_{i}^{1/2},\lambda_{i}^{-1/2} $ , and $ \lambda_{i}^{k} $ , respectively, implying that if $ \lambda_{i} $ is an eigenvalue of A, then $ \lambda_{i}^{-1},\lambda_{i}^{1/2}, $ $ \lambda_{i}^{-1/2} $ , and $ \lambda_{i}^{k} $ , respectively, are eigenvalues of the matrices $ \mathbf{A}^{-1},\mathbf{A}^{1/2},\mathbf{A}^{-1/2} $ , and $ \mathbf{A}^{k} $ . Note that Equations A5.11a-A5.11d further imply that the matrices $ \mathbf{A},\mathbf{A}^{-1},\mathbf{A}^{1/2},\mathbf{A}^{-1/2} $ , and $ \mathbf{A}^{k} $ all have the same eigenvectors, namely the columns of U. Finally, using Equation A5.10a, we see that premultiplying A by $ \mathbf{U}^{T} $ and then postmultiplying by U gives a diagonal matrix whose elements are the eigenvalues of A

$$
\mathbf {U} ^ {T} \mathbf {A} \mathbf {U} = \mathbf {U} ^ {T} \left(\mathbf {U} \boldsymbol {A} \mathbf {U} ^ {T}\right) \mathbf {U} = \left(\mathbf {U} ^ {T} \mathbf {U}\right) \boldsymbol {A} \left(\mathbf {U} ^ {T} \mathbf {U}\right) = \boldsymbol {A}
$$

5. The Rayleigh-Ritz theorem gives useful bounds on quadratic products associated with the symmetric matrix A. It states that if the eigenvalues of A are ordered as $ \lambda_{m a x}=\lambda_{1}\geq\lambda_{2}\geq\cdots\geq\lambda_{n}=\lambda_{m i n} $ , then for any vector of constants c (for $ ||\mathbf{c}||>0 $

$$
\lambda_ {1} \left\| \mathbf {c} \right\| \geq \mathbf {c} ^ {T} \mathbf {A} \mathbf {c} \geq \lambda_ {n} \left\| \mathbf {c} \right\|
$$

If c is of unit length, then all quadratic products are bounded by

$$
\lambda_ {1} \geq \mathbf {c} ^ {T} \mathbf {A} \mathbf {c} \geq \lambda_ {n}
$$

The maximum and minimum quadratic products occur, respectively, when $ \mathbf{c}=\mathbf{e}_{1} $ and $ \mathbf{c}=\mathbf{e}_{n} $ , the eigenvectors associated with $ \lambda_{1} $ and $ \lambda_{n} $ . This is a useful result for bounding variances. Consider a univariate random variable, $ y=\mathbf{c}^{T}\mathbf{x} $ , formed by a linear combination of the elements of a random vector, $ \mathbf{x} $ . Recall from LW Equation 8.19 that the variance of a sum $ y=\mathbf{c}^{T}\mathbf{x} $ is $ \sigma^{2}(y)=\mathbf{c}^{T}\mathbf{V}_{\mathbf{X}}\mathbf{c} $ , where $ \mathbf{V}_{\mathbf{X}} $ is the covariance matrix for $ \mathbf{x} $ . If we apply Equation A5.13a we obtain

$$
\lambda_ {1} \| \mathbf {c} \| ^ {2} \geq \sigma^ {2} (y) \geq \lambda_ {n} \| \mathbf {c} \| ^ {2}
$$

where $ \lambda_{1} $ is the largest (leading or dominant) eigenvalue and $ \lambda_{n} $ is the smallest eigenvalue of the covariance matrix $ \mathbf{V}_{\mathbf{X}} $

Example A5.3. Consider the additive-genetic covariance matrix G from Examples A5.1 and A5.2. Recalling the results from Example A5.2 and using Equation A5.10a, we can express G as $ \mathbf{U} \Lambda \mathbf{U}^{T} $ ,where

$$
\boldsymbol {A} = \left( \begin{array}{c c} 5. 2 4 1 & 0 \\ 0 & 0. 7 6 5 \end{array} \right) \quad \mathrm {a n d} \quad \mathbf {U} = \left(\mathbf {e} _ {1} \quad \mathbf {e} _ {2}\right) = \left( \begin{array}{c c} \left( \begin{array}{c c} - 0. 8 5 1 \\ 0. 5 2 6 \end{array} \right) & \left( \begin{array}{c c} 0. 5 2 6 \\ 0. 8 5 1 \end{array} \right) \end{array} \right)
$$

From Equation A5.11a, the eigenvalues of $ \mathbf{A}^{-1} $ are $ (5.241)^{-1}\simeq 0.191 $ and $ (0.765)^{-1}\simeq 1.307 $ , while from Equation A5.11b, the eigenvalues of $ \mathbf{A}^{1/2} $ are $ \sqrt{5.241}\simeq 2.289 $ and $ \sqrt{0.765}\simeq 0.875. $

## Correlations Can Be Removed by a Matrix Transformation

A powerful use of diagonalization is that it allows one to extract a set of n uncorrelated variables for any $ n\times n $ nonsingular covariance matrix, $ \mathbf{V}_{\mathbf{X}} $ . Consider the transformation

$$
\mathbf {y} = \mathbf {U} ^ {T} \mathbf {x}
$$

where $ \mathbf{U}=(\mathbf{e}_{1},\mathbf{e}_{2},\cdots,\mathbf{e}_{n}) $ contains the normalized eigenvectors of $ \mathbf{V}_{\mathbf{X}} $ . Because U is an orthonormal matrix, this transformation is a rigid rotation of the axes of the original $ (x_{1},\cdots,x_{n}) $ coordinate system to a new system given by $ (e_{1},\cdots,e_{n}) $ . Applying LW Equation 8.21b and Equation A5.12, respectively, the covariance matrix for y is

$$
\mathrm {V} _ {\mathrm {y}} = \mathrm {U} ^ {T} \mathrm {V} _ {\mathrm {X}} \mathrm {U} = \Lambda
$$

where $ \varLambda $ is a diagonal matrix whose elements are the eigenvalues of $ \mathbf{V}_{\mathbf{X}} $

$$
\sigma \left(y _ {i}, y _ {j}\right) = \left\{ \begin{array}{l l} \lambda_ {i} & \mathrm {i f} i = j \\ 0 & \mathrm {i f} i \neq j \end{array} \right.
$$

![](page=9,bbox=[252, 121, 877, 275])

<div align="center">

Figure A5.4 The transformation (Equation A5.15a) generating a set of independent variables for the covariance matrix G from Example A5.4 results in a rigid rotation of axes of the original traits onto the new, uncorrelated set. Left: The direction of the new axes are given by the eigenvectors $ \mathbf{e}_{1} $ and $ \mathbf{e}_{2} $ . The angle between the new axis, $ \mathbf{e}_{1} $ , and the original $ \mathbf{z}_{1} $ axis is given by the angle between $ \mathbf{e}_{1} $ and $ \mathbf{z}_{1}=(1,0)^{T} $ . Here, $ \parallel\mathbf{e}_{1}\parallel= \parallel\mathbf{z}_{1}\parallel=1 $ and $ \mathbf{e}_{1}^{T}\mathbf{z}_{1}=0.851 $ giving $ \theta=\cos^{-1}(0.851)\simeq 32^{\circ} $ . As this transformation is a rigid rotation, the angle between $ \mathbf{e}_{2} $ and the $ \mathbf{z}_{2}=(0,1)^{T} $ axis is also $ 32^{\circ} $ . Right: On the $ (y_{1},y_{2}) $ coordinates, the angle between R and $ \beta $ remains unchanged. See Example A5.4 for further details.

</div>

The rigid rotation introduced by U creates a set of n uncorrelated variables, the i th of which is

$$
y _ {i} = \mathrm {e} _ {i} ^ {T} \mathrm {x}
$$

Because the $ \mathbf{e}_{i} $ are of unit length, from Equation A5.3b we have that $ y_{i}=\mathbf{e}_{i}^{T}\mathbf{x} $ is the length of the projection of x onto the ith eigenvector of $ \mathbf{V}_{\mathbf{X}} $ , which implies that the axes of the new coordinate system are given by the orthogonal set of eigenvectors of $ \mathbf{V}_{\mathbf{X}} $ .

Defining the matrix B as

$$
\mathbf {B} = \mathbf {U} \boldsymbol {\Lambda} ^ {- 1 / 2}
$$

the vector $ \mathbf{y}=\mathbf{B}^{T}\mathbf{x} $ has a covariance matrix of $ \mathbf{V}_{y}=\mathbf{I} $ , which means that this transformation creates a set of uncorrelated variables, each with unit variance. To see this, note that

$$
\begin{array}{l} \mathrm {V} _ {\mathrm {y}} = \mathrm {B} ^ {T} \mathrm {V} _ {\mathrm {X}} \mathrm {B} = \left(\mathrm {U} \Lambda^ {- 1 / 2}\right) ^ {T} \left(\mathrm {U} \Lambda \mathrm {U} ^ {T}\right) \left(\mathrm {U} \Lambda^ {- 1 / 2}\right) \\ = \Lambda^ {- 1 / 2} \left(\mathrm {U} ^ {T} \mathrm {U}\right) \Lambda \left(\mathrm {U} ^ {T} \mathrm {U}\right) \Lambda^ {- 1 / 2} \\ = \Lambda^ {- 1 / 2} \Lambda \Lambda^ {- 1 / 2} = \mathrm {I} \\ \end{array}
$$

An alternative to Equation A5.15d is the Cholesky decomposition, $ \mathbf{A}=\mathbf{C}^{T}\mathbf{C} $ of a square, symmetric matrix A, where C is an lower triangular matrix (all elements above the diagonal are zero). If C is the Cholesky decomposition for $ \mathbf{V}_{X} $ , then $ \mathbf{y}=\mathbf{C}^{-1}\mathbf{x} $ also returns a covariance matrix of I.

Example A5.4. If we apply the change of variables suggested by Equation A5.15a to the vector, z, of characters with associated G matrix used in Example A5.1 and using the eigenvalues and vectors obtained in Example A5.2 yields

$$
\begin{array}{l} \mathbf {y} = \mathbf {U} ^ {T} \mathbf {z} = \left( \begin{array}{c c} \mathbf {e} _ {1} ^ {T} \\ \mathbf {e} _ {2} ^ {T} \end{array} \right) \left( \begin{array}{c} z _ {1} \\ z _ {2} \end{array} \right) \\ = \left( \begin{array}{c c} - 0. 8 5 1 & 0. 5 2 6 \\ 0. 5 2 6 & 0. 8 5 1 \end{array} \right) \left( \begin{array}{c} z _ {1} \\ z _ {2} \end{array} \right) \\ = \left( \begin{array}{c c} - 0. 8 5 1 z _ {1} + 0. 5 2 6 z _ {2} \\ 0. 5 2 6 z _ {1} + 0. 8 5 1 z _ {2} \end{array} \right) \\ \end{array}
$$

From Equation A5.15b, $ \mathbf{V}_{y}=\boldsymbol{\Lambda} $ as given in Example A5.3, showing that $ y_{1} $ and $ y_{2} $ are uncorrelated with $ \sigma^{2}(y_{1})=\lambda_{1}=5.241 $ and $ \sigma^{2}(y_{2})=\lambda_{2}=0.765 $ . Hence, by considering the new coordinate system with

$$
y _ {1} = \mathbf {e} _ {1} ^ {T} \mathbf {z} = - 0. 8 5 1 z _ {1} + 0. 5 2 6 z _ {2} \quad \mathrm {a n d} \quad y _ {2} = \mathbf {e} _ {2} ^ {T} \mathbf {z} = 0. 5 2 6 z _ {1} + 0. 8 5 1 z _ {2}
$$

we can transform the original coordinate system into a new system on which there are no additive-genetic correlations between these new characters. Figure A5.4 shows that this transformation is simply a rigid rotation of the axes.

Likewise, from Equation A5.15d, the transformation that yields uncorrelated variables with unit variance is

$$
\begin{array}{l} \mathbf {y} = \boldsymbol {\Lambda} ^ {- 1 / 2} \mathbf {U} ^ {T} \mathbf {z} = \left( \begin{array}{c c} 1 / \sqrt {\lambda_ {1}} & 0 \\ 0 & 1 / \sqrt {\lambda_ {2}} \end{array} \right) \left( \begin{array}{c} \mathbf {e} _ {1} ^ {T} \\ \mathbf {e} _ {2} ^ {T} \end{array} \right) \left( \begin{array}{c} z _ {1} \\ z _ {2} \end{array} \right) \\ = \left( \begin{array}{c c} 1 / \sqrt {5. 2 3 6} & 0 \\ 0 & 1 / \sqrt {0. 7 6 4} \end{array} \right) \left( \begin{array}{c c} - 0. 8 5 1 & 0. 5 2 6 \\ 0. 5 2 6 & 0. 8 5 1 \end{array} \right) \left( \begin{array}{c} z _ {1} \\ z _ {2} \end{array} \right) \\ = \left( \begin{array}{c c} - 0. 3 7 2 & 0. 2 3 0 \\ 0. 6 0 2 & 0. 9 7 4 \end{array} \right) \left( \begin{array}{c} z _ {1} \\ z _ {2} \end{array} \right) \\ \end{array}
$$

Hence, the transformed variables $ y_{1}=-0.372 z_{1}+0.230 z_{2} $ and $ y_{2}=0.602 z_{1}+0.974 z_{2} $ are uncorrelated, and each has unit variance.

An alternative set of uncorrelated random variables follows from the Cholesky decomposition, which can be compute in R using the cho1 command. (As an aside, cho1 returns the upper-triangular version of the decomposition, which is simply the transpose of the lowertriangular version). The resulting decomposition is

$$
\mathbf {G} = \left( \begin{array}{c c} 4 & - 2 \\ - 2 & 2 \end{array} \right) = \mathbf {C C} ^ {T} = \left( \begin{array}{c c} 2 & 0 \\ - 1 & 1 \end{array} \right) \left( \begin{array}{c c} 2 & - 1 \\ 0 & 1 \end{array} \right)
$$

yielding

$$
\mathbf {y} = \mathbf {C} ^ {- 1} \mathbf {z} = \left( \begin{array}{c c} 0. 5 & 0 \\ 0. 5 & 1 \end{array} \right) \left( \begin{array}{c} z _ {1} \\ z _ {2} \end{array} \right)
$$

$$
y _ {1} = z _ {1} / 2 \quad \mathrm {a n d} \quad z _ {2} = z _ {1} / 2 + z _ {2}
$$

or

as a new set of uncorrelated variables , each with unit variance. One nice feature about using a Cholesky decomposition is that we can always isolate a given variable of interest (simply by putting first in the vector). Because C is lower-triangular, it always returns the first new uncorrelated variable as a scalar times the first original variable (rather than some linear combination of all the variables, as was the case for the first decomposition in this example).

## Simultaneous Diagonalization

An extension of the notion of diagonalization is the simultaneous diagonalization of two symmetric matrices, P and G, of the same dimension. There exists a matrix T such that

$$
\mathbf {T} ^ {T} \mathbf {P T} = \mathbf {I} \quad \mathrm {a n d} \quad \mathbf {T} ^ {T} \mathbf {G T} = \mathbf {D}
$$

where D is a diagonal matrix, whose elements are the eigenvalues of $ \mathbf{P}^{-1}\mathbf{G} $ . Hence, the same transformation simultaneously diagonalizes both P and G. If one has a series of traits with both genetic (G) and phenotypic (P) covariances, they can be transformed to a scale where the new traits (based on linear combinations of the original traits) are genetically and phenotypically uncorrelated, where the elements of D correspond to the heritabilities of these new traits.

Example A5.5. To find the matrix, T, that simultaneously diagonalizes both P and G, we first use Equation A5.10a to write

$$
\mathrm {P} = \mathrm {U} \Lambda \mathrm {U} ^ {T}
$$

where $ \boldsymbol{\Lambda} $ is a diagonal matrix and $ \mathbf{U}^{T}\mathbf{U}=\mathbf{U}\mathbf{U}^{T}=\mathbf{I} $ . Defining $ \mathbf{B}=\mathbf{U}\boldsymbol{\Lambda}^{-1/2} $ , Equation A5.15e showed that $ \mathbf{B}^{T}\mathbf{P B}=\mathbf{I} $ . Next, note for $ \mathbf{M}=\mathbf{B}^{T}\mathbf{G B} $ , that $ \mathbf{M}=\mathbf{M}^{T} $ (i.e., $ \mathbf{M} $ is symmetric), as

$$
\mathbf {M} ^ {T} = \left(\mathbf {B} ^ {T} \mathbf {G B}\right) ^ {T} = \mathbf {B} ^ {T} \mathbf {G} ^ {T} \mathbf {B} = \mathbf {B} ^ {T} \mathbf {G B} = \mathbf {M}
$$

Hence, we can also diagonalize M,

$$
\mathrm {C} ^ {T} \mathrm {M C} = \mathrm {D}
$$

where D is a diagonal matrix and $ \mathbf{C}^{T}\mathbf{C}=\mathbf{C C}^{T}=\mathbf{I} $ . Thus,

$$
\mathbf {C} ^ {T} \mathbf {M C} = \mathbf {C} ^ {T} \left(\mathbf {B} ^ {T} \mathbf {G B}\right) \mathbf {C} = (\mathbf {B C}) ^ {T} \mathbf {G} (\mathbf {B C}) = \mathbf {D}
$$

Defining

$$
\mathrm {T} = \mathrm {B C} = \mathrm {U} \Lambda^ {- 1 / 2} \mathrm {C}
$$

we have from the previous expression that

$$
\mathrm {T} ^ {T} \mathrm {G T} = \mathrm {D}
$$

Likewise,

$$
\mathbf {T} ^ {T} \mathbf {P T} = (\mathbf {B C}) ^ {T} \mathbf {P} (\mathbf {B C}) = \mathbf {C} ^ {T} \left(\mathbf {B} ^ {T} \mathbf {P B}\right) \mathbf {C} = \mathbf {C} ^ {T} \mathbf {C} = \mathbf {I}
$$

showing that the matrix T satisfies Equation A5.16.

## CANONICAL AXES OF QUADRATIC FORMS

The transformation $ \mathbf{y}=\mathbf{U}^{T}\mathbf{x} $ given by Equation A5.15a applies to any symmetric matrix, and is referred to as its canonical transformation. This simplifies the interpretation of the quadratic form $ \mathbf{x}^{T}\mathbf{Ax} $ , as rotation of the original axes to align them with the eigenvectors of A removes all cross-product terms $ (x_{i}x_{j} $ for $ i\neq j $ ) on this new coordinate system. Recall (Equation A5.5b) that U is a unitary matrix and hence $ \mathbf{U}^{T}=\mathbf{U}^{-1} $ . Thus,

$$
\mathrm {U y} = \mathrm {U U} ^ {T} \mathrm {x} = \mathrm {x}
$$

Applying Equations A5.15a and A5.12 transforms a quadratic form to one in which the square matrix is diagonal, which greatly simplifies the resulting quadratic product, as

$$
\begin{array}{l} \mathbf {x} ^ {T} \mathbf {A} \mathbf {x} = (\mathbf {U} \mathbf {y}) ^ {T} \mathbf {A} \mathbf {U} \mathbf {y} = \mathbf {y} ^ {T} (\mathbf {U} ^ {T} \mathbf {A} \mathbf {U}) \mathbf {y} \\ = \mathbf {y} ^ {T} \boldsymbol {A} \mathbf {y} \\ = \sum_ {i = 1} ^ {n} \lambda_ {i} y _ {i} ^ {2}, \quad \mathrm {w i t h} \quad y _ {i} = \mathrm {e} _ {i} ^ {T} \mathbf {x} \\ \end{array}
$$

where $ \lambda_{i} $ and $ \mathbf{e}_{i} $ are the eigenvalues and associated (normalized, i.e., $ \| \mathbf{e}_{i}\|=1 $ ) eigenvectors of A. The new axes defined by the $ \mathbf{e}_{i} $ vectors are the canonical (or principal)

![](page=12,bbox=[328, 119, 541, 292])

<div align="center">

Figure A5.5 The general shape of surfaces of constant variance for the additive-genetic covariance matrix, G, given in Example A5.1. Defining a new composite character $ y=a z_{1}+b z_{2} $ the rotated ellipse represents the set of weights $ (a,b) $ that give y the same additive-genetic variance, $ c^{2} $ . The major axis of the ellipse is along $ \mathbf{e}_{2} $ , the eigenvector associated with the smallest eigenvalue of G, where $ \lambda_{2}\simeq 0.765 $ , giving $ 1 / \sqrt{\lambda_{2}}\simeq 1.143 $ . The minor axis of the ellipse is along $ \mathbf{e}_{1} $ , the eigenvector associated with the largest eigenvalue of G, where $ \lambda_{1}\simeq 5.241 $ , giving $ 1 / \sqrt{\lambda_{1}}\simeq 0.437 $ .

</div>

axes of A. Because $ y_{i}^{2}\geq 0 $ , Equation A5.17a immediately shows the connection between the signs of the eigenvalues of a matrix and whether that matrix is positive definite, negative definite, or indefinite.

If all eigenvalues are positive (all $ \lambda_{i} > 0 $), then any quadratic form is always positive (unless all the $ y_{i} $ are zero) and hence A is positive definite. If one or more of the eigenvalues are zero, while the rest are positive, then A is said to be positive semidefinite, implying that quadratic products are either zero (corresponding to $ \lambda_{i}=0 $) or positive. If all eigenvalues are negative (all $ \lambda_{i}<0 $), then A is negative definite as any quadratic form is always negative, while A is said to be negative semidefinite if the eigenvalues are either zero or negative. If A has both positive and negative eigenvalues it is said to be indefinite, as quadratic products can be either positive or negative.

Equations of the form

$$
\mathbf {x} ^ {T} \mathbf {A} \mathbf {x} = \sum_ {i = 1} ^ {n} \sum_ {j = 1} ^ {n} A _ {i j} x _ {i} x _ {j} = c ^ {2}
$$

arise fairly frequently in quantitative genetics. For example, they describe surfaces of constant variance (Figure A5.5) or constant fitnesses in quadratic fitness regressions (Chapter 30). Solutions to Equation A5.17b describe quadratic surfaces—for two dimensions, these are the familiar conic sections (ellipses, parabolas, or hyperbolas). Equation A5.17a greatly simplifies the interpretation of these surfaces by removing all cross product terms, yielding

$$
\mathbf {x} ^ {T} \mathbf {A} \mathbf {x} = \sum_ {i = 1} ^ {n} \lambda_ {i} y _ {i} ^ {2} = c ^ {2}
$$

Because $ ( y_{i} )^{2} $ and $ (-y_{i})^{2} $ have the same value, the canonical axes of A are also the axes of symmetry for the quadratic surface generated by quadratic forms involving A. When all eigenvalues of A are positive (as occurs with nonsingular covariance and other positive-definite matrices), Equation A5.17c describes an ellipsoid whose axes of symmetry are given by the eigenvectors of A. The distance from the origin to the surface along the $ \mathbf{e}_{i} $ axis is $ \lambda_{i} y_{i}^{2}= $ $ c^{2} $ or $ y_{i}=c\lambda_{i}^{-1/2} $ , as can been seen by setting all the $ y_{k} $ equal to zero except for $ y_{i} $ , which yields

![](page=13,bbox=[248, 119, 884, 294])

<div align="center">

Figure A5.6 Surfaces for a multivariate normal (MVN) distribution. Left: Surfaces of equal probability assuming that the additive-genetic values associated with the characters $ z_{1} $ and $ z_{2} $ in Example A5.1 are $ \sim \mathrm{MVN}(\mu ,\mathbf{G}) $ . These surfaces are ellipses centered at $ \mu $ , with the major axis of the ellipse along $ \mathbf{e}_{1} $ and the minor axis along $ \mathbf{e}_{2} $ , whose lengths (for a fixed c) are, respectively, $ \sqrt{\lambda_{1}}=2.289 $ and $ \sqrt{\lambda_{2}}=0.875 $ . Right: A plot of the associated probability density. Slicing along either the major or minor axis gives a normal curve. Because the variance in the major axis is greater, the curve is much broader along this axis. The covariance between the breeding values of $ z_{1} $ and $ z_{2} $ rotates the distribution so that the principal axes $ \left(\mathbf{e}_{1},\mathbf{e}_{2}\right) $ do not coincide with the original $ \left(z_{1},z_{2}\right) $ axes.

</div>

$$
\mathbf {x} ^ {T} \mathbf {A} \mathbf {x} = \lambda_ {i} y _ {i} ^ {2} = c ^ {2}.
$$

Consider a new variable (y) that is a weighted combination $ y=ax_{1}+bx_{2}=\mathbf{b}^{T}\mathbf{x} $ of the original vector (x) of random variables, where $ \mathbf{b}^{T}=(a,b). $ Its resulting variance is

$$
\sigma^ {2} (y) = a ^ {2} \sigma^ {2} \left(x _ {1}\right) + 2 a b \sigma \left(x _ {1}, x _ {2}\right) + b ^ {2} \sigma^ {2} \left(x _ {2}\right) = \mathbf {b} ^ {T} \mathbf {V} _ {\mathbf {X}} \mathbf {b}
$$

As shown in Figure A5.5, the collection of a,b values that result in the same variance $ ( c^{2} ) $ is the ellipse given by $ c^{2}=\mathbf{b}^{T}\mathbf{V}_{\mathbf{X}}\mathbf{b} $ . Variables with a large amount of variance require smaller weights to achieve the constant value $ ( c^{2} ) $ than do variables with lower variances. Thus, on a constant-variance surface, minor axes correspond to directions with the most variance, while major axes correspond to the directions with the least variability. This is in contrast to surfaces of equal probability (Figure A5.6), where major axes correspond to directions with the most variance. The reason for this reversal of roles is that constant-variance surfaces are functions of $ \lambda_{i}^{-1 / 2} $ , whereas constant-probability surfaces are functions of $ \lambda_{i}^{1 / 2}. $

## Implications for the Multivariate Normal Distribution

Recall the probability density function for the multivariate normal distribution (LW Chapter 8)

$$
\phi (\mathbf {x}) = (2 \pi) ^ {- n / 2} \left| \mathbf {V} _ {\mathbf {X}} \right| ^ {- 1 / 2} \exp \left[ - \frac {1}{2} \left(\mathbf {x} - \boldsymbol {\mu}\right) ^ {T} \mathbf {V} _ {\mathbf {X}} ^ {- 1} \left(\mathbf {x} - \boldsymbol {\mu}\right) \right]
$$

Because only the quadratic product in the exponential varies with x, surfaces of equal probability for MVN distributed vectors satisfy

$$
\left(\mathrm {x} - \mu\right) ^ {T} \mathrm {V} _ {\mathrm {X}} ^ {- 1} \left(\mathrm {x} - \mu\right) = c ^ {2}
$$

From the discussion following Equation A5.17c, these surfaces are n-dimensional ellipsoids centered at $ \mu $ whose axes of symmetry are given by the principal components (the eigenvectors) of the covariance matrix, $ \mathbf{V}_{X} $ . The length of the ellipsoid along the ith axis is $ c\sqrt{\lambda_{i}} $ where $ \lambda_{i} $ is the eigenvalue associated with the eigenvector $ \mathbf{e}_{i} $ (Figure A5.6).

Equation A5.18b motivates the Mahalanobis distance

$$
D = \sqrt {\left(\mathrm {x} - \mu\right) ^ {T} \mathrm {V} _ {\mathrm {X}} ^ {- 1}} (\mathrm {x} - \mu)
$$

which measures the distance of a point from its mean $ \mu $ , correcting for its covariance structure, $ \mathbf{V}_{X} $ (Mahalanobis 1938). As we detail shortly, D provides one metric for tests of multivariate normality.

Applying the canonical transformation (Equation A5.15a), we can change coordinate systems by a rigid rotation to remove any correlations between the variables in x. If $ \mathbf{x}\sim $ MVN $ (\mu, \mathbf{V}_{\mathbf{X}}) $ , then for $ \mathbf{y}=\mathbf{U}^{T}(\mathbf{x}-\mu) $ , it follows that

$$
\mathbf {y} \sim \mathrm {M V N} (\mathbf {0}, \Lambda)
$$

where $ \varLambda $ and U are the matrices defined by Equations A5.10b and A5.10bc for the diagonalization of $ \mathbf{V}_{X} $ . In particular,

$$
y _ {i} = \mathbf {e} _ {i} ^ {T} (\mathbf {x} - \boldsymbol {\mu}) \quad \mathrm {w h e r e} \quad y _ {i} \sim \mathrm {N} (0, \lambda_ {i})
$$

Note from Equation A5.20a that because the $ y_{i} $ are uncorrelated, they are also independent as the joint probability density is the product of n individual univariate normal densities. We can further transform the original vector by taking

$$
z _ {i} = \frac {\mathbf {e} _ {i} ^ {T} (\mathbf {x} - \boldsymbol {\mu})}{\sqrt {\lambda_ {i}}} \quad \mathrm {g i v i n g} \quad z _ {i} \sim \mathrm {N} (0, 1)
$$

Applying the transformation

$$
\mathbf {z} = \boldsymbol {A} ^ {- 1 / 2} \mathbf {U} ^ {T} (\mathbf {x} - \boldsymbol {\mu})
$$

results in $ \mathbf{z}\sim\mathrm{MVN}(0,\mathbf{I}) $ , namely that the n elements of the vector y are each independent unit normal random variables.

## Principal Components of the Variance-Covariance Matrix

We are often interested in how the variance of a random vector can be decomposed into independent components. For example, even though we may be measuring n variables, only one or two of these may account for the majority of the variation. If this is the case, we may wish to exclude those variables contributing very little variation from further analysis. More generally, if random variables are correlated, then certain linear combinations of the elements of x may account for most of the variance. The procedure of principal component analysis (PCA) extracts these combinations by decomposing the variance of x into the contributions from a series of orthogonal vectors, the first of which explains the most variation possible for any single vector, the second the next possible amount, and so on until we account for the entire variance of x.

Consider Figure A5.5. Because the set of points comprising the ellipse represents the set of linear combinations (i.e., the set of weights) of the random variables of z that yield equal variance, a little thought shows that the closer a point on this curve is to the origin, the more variance there is in that direction. The points closest to the origin are those that lie along the axis defined by $ \mathbf{e}_{1} $ , while those furthest away lie along the axis defined by $ \mathbf{e}_{2} $ . Here $ \mathbf{e}_{1} $ and $ \mathbf{e}_{2} $ are the principal components of G, with the first principal component accounting for most of the variation of G. In particular, the ratio of additive variances for the characters $ y_{1}=\mathbf{e}_{1}^{T}\mathbf{z} $ and $ y_{2}=\mathbf{e}_{2}^{T}\mathbf{z} $ is $ \sigma^{2}(y_{1}) / \sigma^{2}(y_{2})=\sigma^{2}(\mathbf{e}_{1}^{T}\mathbf{z}) / \sigma^{2}(\mathbf{e}_{2}^{T}\mathbf{z})=\mathbf{e}_{1}^{T}\mathbf{G}\mathbf{e}_{1} / \mathbf{e}_{2}^{T}\mathbf{G}\mathbf{e}_{2}=\lambda_{1} / \lambda_{2}\simeq $ 5.241/0.765 $ \simeq $ 6.85, so that a character in the direction of $ \mathbf{e}_{1} $ has almost seven times as much additive variance as a character lying in the direction of $ \mathbf{e}_{2} $

In general, suppose we have an n-dimensional covariance matrix, $ \mathbf{V}_{\mathbf{X}} $ . If we order the eigenvalues of $ \mathbf{V}_{\mathbf{X}} $ as $ \lambda_{1}\geq\lambda_{2}\geq\cdots\geq\lambda_{n} $ , then Equation A5.13b gives the maximum variance for any linear combination of the elements of $ \mathbf{x} $ $ (y=\mathbf{c}_{1}^{T}\mathbf{x} $ , subject to the constraint that $ \| \mathbf{c}_{1}\|=1 $ ), as

$$
\max \sigma^ {2} (y) = \max _ {\| \mathbf {C} _ {1} \| = 1} \sigma^ {2} \left(\mathbf {c} _ {1} ^ {T} \mathbf {x}\right) = \mathbf {c} _ {1} ^ {T} \mathbf {V} _ {\mathbf {X}} \mathbf {c} _ {1} = \lambda_ {1}
$$

which occurs when $ \mathbf{c}_{1}=\mathbf{e}_{1} $ (the normalized eigenvector associated with the leading eigenvalue $ \lambda_{1} $ ). This vector is the first principal component (often abbreviated as PC1), and

accounts for the fraction $ \lambda_{1} / \operatorname{tr}(\mathbf{V}_{\mathbf{X}}) $ of the total variation in x. We can partition the remaining variance in x after the removal of PC1 in a similar fashion. For example, the vector $ \mathbf{c}_{2} $ that is orthogonal to PC1 $ \left(\mathbf{c}_{2}^{T}\mathbf{c}_{1}=0\right) $ and maximizes the remaining variance can be shown to be $ \mathbf{e}_{2} $ , which accounts for a fraction $ \lambda_{2} / \operatorname{tr}(\mathbf{V}_{\mathbf{X}}) $ of the total variation in x (e.g., Morrison 1976; Johnson and Wichern 1988). By proceeding in this fashion, we can see that the ith PC is given by $ \mathbf{e}_{i} $ , and that the amount of variation it accounts for is

$$
\lambda_ {i} / \sum_ {k = 1} ^ {n} \lambda_ {k} = \frac {\lambda_ {i}}{\operatorname {t r} \left(\mathbf {V} _ {\mathbf {X}}\right)}
$$

Hence $ \sum\lambda_{i}=\operatorname{tr}(\mathbf{V}_{\mathbf{X}}) $ is the total variance of the vector x, while $ \lambda_{i} / \operatorname{tr}(\mathbf{V}_{\mathbf{X}}) $ is the fraction of that total variance explained by the linear combination $ \mathrm{e}_{i}^{T}\mathbf{x}. $

Example A5.6. Again let us consider the additive-genetic covariance matrix, G, as shown in Examples A5.1 and A5.2. Because $ \lambda_{1}\simeq 5.241 $ $ \lambda_{2}\simeq 0.765 $ , and $ \operatorname{tr}(\mathbf{G})=4+2=6 $ the first PC explains $ 5.241/6\simeq 0.8735 $ , or 87% of the variance in G. While the first PC accounts for the majority of variation over the entire space of the variables (x), the amount of variation explained by PC1 for any particular weighted combination, $ y=\mathbf{b}^{T}\mathbf{x} $ , of the original variables depends on the projection of b onto PC1. For example, if $ \mathbf{b}=\mathbf{e}_{2} $ (the weight vector corresponds to the second eigenvector), then the projection of b onto PC1 has a length of zero, because PC1 is orthogonal to $ \mathbf{e}_{2} $ , and hence PC1 explains none of the variation of this new variable.

Example A5.7 serves as a brief introduction to the important field of morphometrics which is concerned with quantification and comparison of sizes and shapes of organisms. The reader is referred to Pimentel (1979), Reyment et al. (1984), Elewa (2004), Claude (2008) and especially Bookstein et al. (1985), Rohlf and Bookstein (1990), Reyment (1991), Bookstein (1997), Slice (2005), and Zelditch et al. (2012) for detailed treatments.

Example A5.7. Jolicoeur and Mosimann (1960) measured three carapace characters in 24 males of the painted turtle (Chrysemys picta marginata). Letting $ z_{1} $ be the carapace length, $ z_{2} $ be the maximun carapace width, and $ z_{3} $ be the carapace height, the resulting sample covariance matrix （ $ \mathbf{S}_{\mathbf{Z}} $ , the sample estimate of $ \mathbf{V}_{\mathbf{Z}} $ ）for these data was found to be

$$
\mathbf {S} _ {\mathbf {Z}} = \left( \begin{array}{c c c} 1 3 8. 7 7 & 7 9. 1 5 & 3 7. 3 8 \\ 7 9. 1 5 & 5 0. 0 4 & 2 1. 6 5 \\ 3 7. 3 8 & 2 1. 6 5 & 1 1. 2 6 \end{array} \right)
$$

Hence, $ \operatorname{t r} \left( \mathbf{S}_{\mathbf{Z}} \right)=1 3 8. 7 7+5 0. 0 4+1 1. 2 6=2 0 0. 0 7 $ .Using R,the eigenvalues of $ \mathbf{S}_{\mathbf{Z}} $ are found to be

$$
\lambda_ {1} = 1 9 5. 2 8 0, \quad \lambda_ {2} = 3. 6 8 7, \quad \lambda_ {3} = 1. 1 0 3
$$

which (as expected) sum to the value of the trace, 200.07. The associated (normalized) eigenvectors are similarly found to be

$$
\mathbf {e} _ {1} = \left( \begin{array}{c} 0. 8 4 0 \\ 0. 4 9 2 \\ 0. 2 2 9 \end{array} \right), \quad \mathbf {e} _ {2} = \left( \begin{array}{c} 0. 4 8 8 \\ - 0. 8 7 0 \\ 0. 0 7 9 \end{array} \right), \quad \mathbf {e} _ {3} = \left( \begin{array}{c} 0. 2 1 3 \\ 0. 0 4 3 \\ - 0. 9 7 1 \end{array} \right)
$$

PC1 accounts for 97.6% of the variation (195.281/200.07=0.976), while PC2 and PC3 account for 1.84% and 0.55% , respectively. Jolicoeur and Mosimann interpret PC1 as measuring overall size, as the new variable

$$
y _ {1} = \mathbf {e} _ {1} ^ {T} \mathbf {z} = 0. 8 4 0 z _ {1} + 0. 4 9 2 z _ {2} + 0. 2 2 9 z _ {3}
$$

corresponds to a simultaneous change in all three variables in the same direction, as is expected as individuals change their overall size. Likewise, PC2 and PC3 are

$$
y _ {2} = \mathbf {e} _ {2} ^ {T} \mathbf {z} = 0. 4 8 8 z _ {1} - 0. 8 7 0 z _ {2} + 0. 0 7 9 z _ {3}
$$

$$
y _ {3} = \mathbf {e} _ {3} ^ {T} \mathbf {z} = 0. 2 1 3 z _ {1} + 0. 0 4 3 z _ {2} - 0. 9 7 1 z _ {3}
$$

which Jolicoeur and Mosimann interpreted as measures of shape. Because the coefficient on $ z_{3} $ is small relative to the others in PC2, they interpret PC2 as measuring the tradeoff between length $ (z_{1}) $ and width $ (z_{2}) $ . Thus, after removing the variation in size, 1.84% of the remaining variation can be accounted for by differences in the shape measured by length versus width. Likewise, because the PC3 coefficient for $ z_{2} $ is very small, PC3 mainly measures shape differences due to length $ (z_{1}) $ versus height $ (z_{3}) $

This example points out some of the advantages, and possible pitfalls, of using principal component analysis for dimensional reduction of the data. Namely, replacing the n-component vector z by an m<n component vector y composed of linear combinations of the z, i.e., $ \mathbf{y}_{m\times 1}=\mathbf{M}_{m\times n}\mathbf{z}_{n\times 1} $ , where $ \mathbf{M}=(\mathbf{e}_{1},\cdots,\mathbf{e}_{m})^{T} $ , with $ y_{i}=\mathbf{e}_{i}^{T}\mathbf{z} $ . Essentially all (over 97%) of the variance in the three measured characters is accounted for by variation in overall size, with the remaining variation accounted for by differences in shape. While the temptation is strong to simply consider overall size and ignore all shape information, it might be the case that selection is largely ignoring variation in size and instead focusing on (size-independent) shape differences. In this case, an analysis ignoring shape (as would occur if only the new character generated by PC1 were considered) would be very misleading. A further complication with principal component analysis is that it can often be difficult to give biological interpretations to the new characters resulting from the rotation of the coordinate system.

## TESTING FOR MULTIVARIATE NORMALITY

Multivariate normality is often assumed in statistical procedures, but it is less often tested. In LW Chapter 11 we briefly discussed two approaches for testing univariate normality, one graphical and the other based on deviations of observed skewness and/or kurtosis from Gaussian expectations. As we now demonstrate, both of these approaches can be extended to testing for multivariate normality. Additional methods are reviewed by Malkovich and Afifi (1973), Gnanadesikan (1977), Cox and Small (1978), Seber (1984), Looney (1995), and Henze (2002).

## Graphical Tests: Chi-square Plots

A fairly simple graphical test can be developed by extending the notion of the normal probability plot that is used to check univariate normality (LW Chapter 11), where observations were ranked and then plotted against their ranked expected values under normality. Departures from linearity signify departures from normality, and we can apply this same approach to check for multivariate normality. From Equation A5.20d, if $ \mathbf{z}\sim\mathrm{MVN}(\mu,\mathbf{V}_{\mathbf{Z}}) $ then each element of the vector

$$
\mathbf {y} = \boldsymbol {\Lambda} ^ {- 1 / 2} \mathrm {U} ^ {T} (\mathbf {z} - \mu)
$$

is an independent unit normal, so that $ \mathbf{y}\sim \mathrm{MVN}(0,\mathbf{I}) $ . Recalling that $ \mathbf{U}^{-1}=\mathbf{U}^{T} $ , we can rearrange this expression to yield

$$
(\mathbf {z} - \mu) = \mathbf {U} \boldsymbol {\Lambda} ^ {1 / 2} \mathbf {y}
$$

![](page=17,bbox=[260, 119, 872, 305])

<div align="center">

Figure A5.7 Plots of ranked distance data $ ( d_{(j)}^{2} $ being the jth smallest distance) versus the expected corresponding $ \chi^{2} $ value for the data of Jolicoeur and Mosimann from Example A5.8. Left: The untransformed data do not appear to depart significantly from linearity, although they depart slightly from the intercept (0) and slope (1) of the expected regression under multivariate normality. Right: Log-transforming the data gives a slightly better linear fit $ ( r^{2}=0.983 $ versus $ r^{2}=0.952) $ , with the best-fitting line passing through the origin as expected if the distance data follow a $ \chi^{2} $ distribution, and has a slope of essentially one. See Example A5.8 for more details.

</div>

Using this result and recalling Equation A5.11a, we have that

$$
\begin{array}{l} \left(\mathbf {z} - \mu\right) ^ {T} \mathbf {V} _ {\mathbf {z}} ^ {- 1} (\mathbf {z} - \mu) = \left(\mathbf {U} \Lambda^ {1 / 2} \mathbf {y}\right) ^ {T} \left(\mathbf {U} \Lambda^ {- 1} \mathbf {U} ^ {T}\right) \left(\mathbf {U} \Lambda^ {1 / 2} \mathbf {y}\right) \\ = \mathbf {y} ^ {T} \Lambda^ {1 / 2} \left(\mathbf {U} ^ {T} \mathbf {U}\right) \Lambda^ {- 1} \left(\mathbf {U} ^ {T} \mathbf {U}\right) \Lambda^ {1 / 2} \mathbf {y} \\ = \mathbf {y} ^ {T} \mathbf {y} = \sum_ {i = 1} ^ {n} y _ {i} ^ {2} \\ \end{array}
$$

Thus if $ \mathbf{z}\sim\mathrm{MVN} $ , the quadratic form given by Equation A5.22 is the sum of n independent squared unit normal random variables. By definition, this sum is a $ \chi^{2} $ random variable with n degrees of freedom (LW Appendix 5), suggesting that one test for multivariate normality is to compare the goodness of fit of the scaled distances

$$
d _ {i} ^ {2} = \left(\mathbf {z} _ {i} - \bar {\mathbf {z}}\right) ^ {T} \mathbf {S} _ {\mathbf {z}} ^ {- 1} \left(\mathbf {z} _ {i} - \bar {\mathbf {z}}\right)
$$

to those generated by n (rank-ordered) draws from a $ \chi_{n}^{2} $ . Here $ \mathbf{z}_{i} $ is the vector of observations from theith individual, $ \bar{\mathbf{z}} $ the vector of sample means, and $ \mathbf{S}_{z}^{-1} $ the inverse of the sample covariance matrix. Note that the $ d_{i} $ are simply the squared Mahalanobis distances (Equation A5.19). We use the term distance because when $ \mathbf{z} $ is transformed to $ \mathbf{y} $ $ \mathbf{V}_{y}=\mathbf{I} $ , giving the variance of the linear combination $ \mathbf{c}^{T}\mathbf{y} $ as $ \mathbf{c}^{T}\mathbf{V}_{y}\mathbf{c}=\mathbf{c}^{T}\mathbf{I}\mathbf{c}=\left\| \mathbf{c}\right\|^{2} $ . Thus, regardless of orientation, any two $ \mathbf{y} $ vectors having the same length also have the same variance, which equals their squared Euclidean distance.

The regression test for multivariate normality is based on ordered distances. Hence, we first order the distances generated by Equation A5.23 from smallest to largest,

$$
d _ {(1)} ^ {2} \leq d _ {(2)} ^ {2} \leq \dots \leq d _ {(m)} ^ {2}
$$

where m is the number of individuals sampled. Note that we use the subscription notation where $ d_{(j)}^{2} $ denotes the jth smallest distance (the jth smallest value of Equation A5.23), whereas $ d_{i}^{2} $ is the distance associated with the vector of observations for the ith observation.

Let $ \chi_{n}^{2} (\alpha) $ correspond to the value of a chi-square random variable, X, with n degrees of freedom that satisfies $ \operatorname{Prob}[X\leq\chi_{n}^{2}(\alpha)]=\alpha $ . Under multivariate normality, we expect the points

$$
\left(d _ {(i)} ^ {2}, \chi_ {n} ^ {2} \left[ \frac {i - 1 / 2}{m} \right]\right) \quad \mathrm {f o r} \quad 1 \leq i \leq m
$$

to fall along a line with a slope of one and an intercept of zero, as the i th ordered distance has i/m observations less than or equal to it (the factor of 1/2 is added as a correction for continuity). As with univariate normal probability plots, departures from multivariate normality are indicated by departures from linearity. More formally, one can use a standard Kolmogorov-Smirnov test (Conover 1999) for comparing two distributions to compare the goodness-of-fit of these ordered distances with a $ \chi_{n}^{2} $

Example A5.8. Consider again the data of Jolicoeur and Mosimann (1960) on carapace characters in 24 male turtles. Are the characters $ z_{1} $ (carapace length) and $ z_{2} $ (maximun carapace width) jointly bivariate normally distributed? Here n=2 and m=24 and

$$
\bar {\mathbf {z}} = \left( \begin{array}{c c} 1 1 3. 1 3. \\ 8 8. 2 9 \end{array} \right), \mathbf {S} _ {\mathbf {z}} = \left( \begin{array}{c c} 1 3 8. 7 7 & 7 9. 1 5 \\ 7 9. 1 5 & 5 0. 0 4 \end{array} \right), \mathbf {S} _ {\mathbf {z}} ^ {- 1} = \left( \begin{array}{c c} 0. 0 7 3 7 & - 0. 1 1 6 5 \\ - 0. 1 1 6 5 & 0. 2 0 4 3 \end{array} \right)
$$

where $ S_{Z} $ is the sample covariance matrix. A partial list of the 24 vectors of observations is

$$
\mathbf {z} _ {1} = \left( \begin{array}{c} 9 3 \\ 7 4 \end{array} \right), \quad \dots , \quad \mathbf {z} _ {1 1} = \left( \begin{array}{c} 1 1 3 \\ 8 8 \end{array} \right), \quad \dots , \quad \mathbf {z} _ {2 4} = \left( \begin{array}{c} 1 3 5 \\ 1 0 6 \end{array} \right)
$$

Applying Equation A5.23, these observations translate into the distances

$$
d _ {1} ^ {2} = 4. 4 5, \quad \dots , \quad d _ {1 1} ^ {2} = 0. 0 0 2, \quad \dots , \quad d _ {2 4} ^ {2} = 9. 2 7 7
$$

After rank ordering, these correspond to $ d_{(23)}^{2}, d_{(1)}^{2}, $ and $ d_{(24)}^{2}, $ respectively. For $ d_{(23)}^{2}, $ the matching value when distances are $ \chi^{2} $ -distributed is

$$
\chi_ {2} ^ {2} \left(\frac {2 3 - 1 / 2}{2 4}\right) = \chi_ {2} ^ {2} (0. 9 3 7 5)
$$

The R command qchisq(0.9375,2) returns a value of x = 5.545, which satisfies $ \operatorname* {P r} \left( \chi_{2}^{2} \leq x \right)=0. 9 3 7 5 $ , and calculates the point generated from $ \mathbf{z}_{1} $ as (4.45, 5.545). Likewise, the $ \chi^{2} $ values for $ d_{(1)}^{2} $ and $ d_{(24)}^{2} $ are 0.043 and 7.742, respectively. Proceeding similarly for the other values, we obtain the regression plotted in Figure A5.7. This departs somewhat from linearity. Further, under the assumption of multivariate normality, the best-fitting linear regression is expected to have a slope of one and to pass through the origin, while the best linear fit of these data shows slight departures from these values. Transforming the data by taking logs results in a slightly better fit (Figure A5.7).

## Mardia's Test: Multivariate Skewness and Kurtosis

As was the case for univariate normality, we can test for multivariate normality by examining the sample skewness and kurtosis. Mardia (1970, 1974) proposed multivariate extensions of skewness and kurtosis measures and suggested a large-sample test based on the asymptotic distribution of these statistics. If there are m vectors of observations (with each vector measuring n characters), then the multivariate skewness is estimated by

$$
b _ {1, n} = \frac {1}{m ^ {2}} \sum_ {i = 1} ^ {m} \sum_ {j = 1} ^ {m} \left[ \left(\mathbf {z} _ {i} - \bar {\mathbf {z}}\right) ^ {T} \mathbf {S} _ {\mathbf {z}} ^ {- 1} \left(\mathbf {z} _ {j} - \bar {\mathbf {z}}\right) \right] ^ {3}
$$

while the multivariate kurtosis is estimated by

$$
b _ {2, n} = \frac {1}{m} \sum_ {i = 1} ^ {m} \left[ \left(\mathbf {z} _ {i} - \bar {\mathbf {z}}\right) ^ {T} \mathbf {S} _ {\mathbf {z}} ^ {- 1} \left(\mathbf {z} _ {i} - \bar {\mathbf {z}}\right) \right] ^ {2}
$$

If $ \mathbf{z} \sim \mathrm{MVN} $ , then $ b_{1,n} $ and $ b_{2,n} $ have expected values 0 and $ n(n+2) $ . For large values of m, Mardia showed that the (scaled) multivariate skewness is asymptotically distributed as a chi-square random variable with f degrees of freedom, with

$$
\frac {m}{6} b _ {1, n} \sim \chi_ {f} ^ {2}, \quad \mathrm {w h e r e} f = \frac {n (n + 1) (n + 2)}{6}
$$

Likewise for large values of m, the multivariate kurtosis (following appropriate scaling) is distributed as a unit-normal, with

$$
\frac {b _ {2 , n} - n (n + 2)}{\sqrt {8 n (n + 2) / m}} \sim N (0, 1)
$$

If either Equation A5.25a or A5.25b is significant, then multivariate normality is rejected.

Example A5.9. Do the data considered in Example A5.8 display significant skewness or kurtosis? Here n = 2 and m = 24. Applying Equations A5.25a and A5.25b gives $ b_{1,2}= $ 0.6792 and $ b_{2,2}= $ 7.6043. Considering skewness first, from Equation A5.25a it follows that the value

$$
\frac {m}{6} b _ {1, 2} = \frac {2 4}{6} 0. 6 7 9 2 = 2. 7 1 7
$$

is (under MVN) a draw from a chi-square distribution with $ f=2(2+1)(2+2)/6=4 $ degrees of freedom. Because $ \operatorname{Prob}\left(\chi_{4}^{2}\geq 2.717\right)\simeq 0.606 $ , this is not significant. Turning to kurtosis, Equation A5.25b yields

$$
\frac {b _ {2 , n} - n (n + 2)}{\sqrt {8 n (n + 2) / m}} = \frac {7 . 6 0 4 3 - 8}{1 . 6 3 3} \simeq - 0. 2 4 2 3
$$

which is also not significant as Prob $ \mid N(0,1)\mid \geq 0.2423)\simeq 0.81 $ Transforming the data by taking logs gives $ b_{1,2}=0.2767 $ and $ b_{2,2}=7.1501 $ , and hence showing a slight decrease in skewness and and a slight increase in kurtosis relative to the untransformed data. Reyment (1971) presented a number of other biological examples using Mardia's test.