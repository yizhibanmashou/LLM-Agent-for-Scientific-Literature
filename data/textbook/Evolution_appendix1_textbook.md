# Appendix 1 · Appendix 1

## Evolution_appendix1_001 · Appendix: Introduction

Diffusion Theory

I believe that no one who is familiar, either with mathematical advances in other fields, or with the range of special biological conditions to be considered, would ever conceive that everything could be summed up in a single mathematical formula, however complex. Fisher (1932a)

Exact solutions of the dynamics of many random processes arising in population and quantitative genetics are either unknown or extremely cumbersome. Nevertheless, starting with Fisher (1922), Wright (1945), and Kimura (1955a, 1955b), the use of diffusion approximations in place of the exact dynamics of these processes has proven to be extremely powerful. Useful introductions to diffusion theory with special reference to genetics were given by Ewens (1979, 2004) and Karlin and Taylor (1981), with additional applications considered by Crow and Kimura (1970), Maruyama (1977), Kimura (1983), and Gale (1990). The goal of diffusion theory is to obtain expressions for $ \varphi(x, t, p) $, the probability distribution for the random variable, x, at time t, given that the process starts at a value of p. It is often the case that for sufficiently large time, the probability distribution approaches a stationary value, $ \varphi(x) $, independent of both time (t) and the starting value (p). Diffusion theory also provides approximations for a number of summary statistics of a particular process, such as probabilities and times to fixation for the various boundaries of the process (such as the loss or fixation of an allele). We will consider these issues in turn.

---

## Evolution_appendix1_002 · Appendix: Introduction / FOUNDATIONS OF DIFFUSION THEORY

Consider a continuous random variable, $ x_t $, indexed by continuous time, $ t $. If $ \delta_x = x_{t+\delta_t} - x_t $ (the change in $ x_t $ over a very small time interval, $ \delta_t $) satisfies

$$
E\left(\delta_{x}\mid x_{t}=x\right)=m(x)\delta_{t}+o(\delta_{t})
$$

$$
\sigma^{2}(\delta_{x}\mid x_{t}=x)=v(x)\delta_{t}+o(\delta_{t})
$$

$$
\begin{array}{r l}{E\left(\left|\delta_{x}\right|^{k}\right)=o(\delta_{t})}&{{}\mathrm{f o r~}k\geq3}\end{array}
$$

then $x_t$ is said to be a diffusion process, provided the additional technical restriction that $x_t$ is a Markov process (the transition probabilities depend only on the current value of the process and no other aspects of its history) is satisfied. The functions $m(x)$ and $v(x)$ are defined shortly, while the notation $o(\delta_t)$ means that any remaining terms are of order $\delta_t^2$ (or higher), and hence small relative to $\delta_t$. Formally, $\lim_{\delta_t \to 0} o(\delta_t)/\delta_t = 0$, so we can ignore terms of order $\delta_t^2$ (or higher) when $\delta_t$ itself is very small. Likewise, the notation $O(x)$ means terms of order $x$, and so for example, $O(x^2) = o(x)$.

---

## Evolution_appendix1_003 · FOUNDATIONS OF DIFFUSION THEORY / The Infinitesimal Mean, $ m(x) $, and Variance, $ v(x) $

The infinitesimal mean, $ m(x) $, and infinitesimal variance, $ v(x) $, correspond to the mean and variance of the process (given that it is at x) over a very small time interval. These are formally defined by

$$
m(x)=\lim_{\delta_{t}\to0}\frac{E\left(x_{t+\delta_{t}}-x_{t}\mid x_{t}=x\right)}{\delta_{t}}
$$

$$
v(x)=\lim_{\delta_{t}\to0}\frac{E\big[\left(x_{t+\delta_{t}}-x_{t}\right)^{2}\mid x_{t}=x\big]}{\delta_{t}}
$$

**[命题 Proposition]**

In words, the diffusion assumption is that, over a very small time interval, the mean, $ m(x) $, and variance, $ v(x) $, around the current position, x, are sufficient to fully describe the process.

In population genetics, diffusion approximations provide an elegant way to rescale a discrete space, discrete time, random variable (usually an allele frequency) to construct a new, continuously distributed random variable. For example, consider $ \dot{X}_t $, the number of copies of allele $ A $ in a discrete-generation population of $ N $ diploids at generation $ t $. $ X_t $ takes on values of $ 0, 1, \ldots, 2N $, and time $ t $ is in units of discrete generations. Suppose we construct a new random variable $ x_\tau^{(N)} = X_{(\tau)}/(2N) $, where $ \tau = t/N $. A unit of time on this transformed scale $ (\tau) $ corresponds to $ N $ generations on the original scale. If we take the limit as $ N $ approaches infinity, the limiting process $ x_\tau $ is a continuous space (in $ x $), continuous time (in $ \tau $) process that represents the allele frequency at time $ \tau $.

**[示例 Example]**

*(See Example A1.1.)*

---

## Evolution_appendix1_004 · FOUNDATIONS OF DIFFUSION THEORY / The Kolmogorov Forward Equation

Given $ m(x) $, $ v(x) $, and an initial frequency of p, the diffusion approximation for the dynamics of the probability density function for the realized value x at time t satisfies the Kolmogorov forward equation (or KFE)

$$
\frac{\partial\varphi(x,t,p)}{\partial t}=\frac{1}{2}\frac{\partial^{2}[v(x)\varphi(x,t,p)]}{\partial x^{2}}-\frac{\partial[m(x)\varphi(x,t,p)]}{\partial x}
$$

where $ \varphi(x,t,p) $ is the probability density for x at time t, given that the process starts at p, namely,

**[推导 Derivation]**

$$
\Pr[c\leq x(t)\leq d\mid x(0)=p]=\int {c}^{d}\varphi(x,t,p)dx
$$

and $C$ is a constant such that $\varphi(x)$ integrates to one, ensuring that Equation A1.11 is a proper probability density function. Stationary distributions for population-genetic processes were first obtained by Wright (1931, 1938b), who used a somewhat different approach. Note that $\int [v(x) G(x)]^{-1} dx$ may be infinite, in which case no stationary distribution exists. This happens, for example, in the absence of mutation and migration, where both boundaries (allele frequencies of 0 or 1) are absorbing.

Fortunately, we do not have to solve for $ \varphi(x,t,p) $, as (recalling Equation A1.22a) the general solution is obtained by using the Green's function, as described by Equation A1.22c, with

**[推导 Derivation]**

$$
E[I {f}(p)]=\int {0}^{1}f(x)h(x,p)dx
$$

This makes sense, as $ h(x,p)dx $ is the expected amount of time that the process (starting at p) spends in the neighborhood of x before it is eventually lost or fixed. Thus, integration over all possible neighborhoods gives the expected value of the function over all sample paths.

A derivation of the KFE is given below. When they can be found, closed-form solutions of $ \varphi(x,t,p) $ are usually complicated (e.g., Example A1.2). The standard approach is to express the solution as a power series:

$$
\varphi(x,t,p)=\sum_{i=1}^{\infty}f_{i}(x,p)e^{-\lambda_{i}t}
$$

Here, the values of $ \lambda_i $ are the eigenvalues associated with the partial differential equation given by Equation A1.6, and the functions, $ f_i $, are the associated eigenfunctions. Notice that time, $ t $, only appears as a multiplier of the eigenvalues, while the starting position, $ p $, appears only in the eigenfunctions. Crow and Kimura (1970) presented exact solutions of $ \varphi(x, t, p) $ for a number of population-genetic problems. As the next example shows, even in the simplest case (pure drift), the result are rather complex.

**[示例 Example]**

*(See Example A1.2.)*

---

## Evolution_appendix1_006 · FOUNDATIONS OF DIFFUSION THEORY / Boundary Behavior of a Diffusion

A critical feature of the density $ \varphi(x,t,p) $ is its range of validity. Formally speaking, the diffusion approximation only applies within some open interval between two boundary values, a and b. The behavior exactly at the boundaries $ (x = a $ and $ x = b) $ is beyond the realm of the approximation. In many cases, $ x_t $ does not change value once it reaches a boundary, in which case it is called absorbing. For example, in the absence of mutation and migration, once an allele frequency reaches either 0 or 1, it remains there, which means that both of these extreme states are absorbing boundaries. Further, a boundary is said to be accessible if it can be reached in finite time. When considering fixation probabilities, we are examining absorbing, accessible boundaries. Note that a finite boundary point may not be accessible. Suppose we consider a simple mutation-drift equilibrium. If the mutational pressure is sufficiently strong near a boundary (say for the loss of an allele), the resulting boundary may be inaccessible, with the population never being in a state where all copies of an allele are lost.

---

## Evolution_appendix1_007 · FOUNDATIONS OF DIFFUSION THEORY / Derivation of the Kolmogorov Forward Equation

For completeness, we present a derivation of Equation A1.6, using the diffusion-approximation assumptions (Equations A1.1a–A1.1c). This section is a bit technical and can be skipped if readers desire. Consider the change from the probability distribution, $ \varphi(x, t, p) $, at time $ t $ to a new distribution, $ \varphi(x, t + \delta_t, p) $, after some very small time interval, $ \delta_t $. To arrive at $ x $ at time $ t + \delta_t $, the frequency must have previously been at some value, $ x - \delta_x $, and then moved by an amount, $ \delta_x $, over the interval $ \delta_t $. Let $ \phi(\delta_x, x, \delta_t) $ be the probability of jumping by an amount, $ \delta_x $, over the time $ \delta_t $ given the starting point, $ x $. In our case, because we are assuming that there is a move from $ x - \delta_x $ to $ x $, we consider $ \phi(\delta_x, x - \delta_x, \delta_t) $. Integrating over all possible jump values yields the Chapman-Kolmogorov equation

$$
\varphi(x,t+\delta_{t},p)=\int\varphi(x-\delta_{x},t,p)\phi(\delta_{x},x-\delta_{x},\delta_{t})d\delta_{x}
$$

To simplify notation in the following derivation, we write $ \varphi(x,t,p) $ as $ \varphi(x,t) $, although the dependence on the initial value p should be kept in mind.

To solve the Chapman-Kolmogorov equation, we start by using the Taylor series approximation

$$
f(x-a)=f(x)-a\frac{\partial f(x)}{\partial x}+\frac{a^{2}}{2}\frac{\partial^{2}f(x)}{\partial x^{2}}-\frac{a^{3}}{6}\frac{\partial^{3}f(x)}{\partial x^{3}}+o(a^{3})
$$

Expanding the function in the integral about $ a = \delta_{x} $ yields

$$
\begin{align*}\varphi(x-\delta_{x},t)\phi(\delta_{x},x-\delta_{x},\delta_{t})&=\varphi(x,t)\phi(\delta_{x},x,\delta_{t})-\delta_{x}\frac{\partial\big[\varphi(x,t)\phi(\delta_{x},x,\delta_{t})\big]}{\partial x}\\&+\frac{\delta_{x}^{2}}{2}\frac{\partial^{2}\big[\varphi(x,t)\phi(\delta_{x},x,\delta_{t})\big]}{\partial x^{2}}-\frac{\delta_{x}^{3}}{6}\frac{\partial^{3}\big[\varphi(x,t)\phi(\delta_{x},x,\delta_{t})\big]}{\partial x^{3}}+o(\delta_{x}^{3})\end{align*}
$$

If we ignoring terms of $ o(\delta_{x}^{3}) $, i.e., of order $ \delta_{x}^{4} $ and higher, and integrate, the result is

$$
\begin{align*}\int\varphi(x-\delta_{x},t)\phi(\delta_{x},x-\delta_{x},\delta_{t})d\delta_{x}&\simeq\int\varphi(x,t)\phi(\delta_{x},x,\delta_{t})d\delta_{x}-\int\delta_{x}\frac{\partial[\varphi(x,t)\phi(\delta_{x},x,\delta_{t})]}{\partial x}d\delta_{x}\\+\int\frac{\delta_{x}^{2}}{2}\frac{\partial^{2}[\varphi(x,t)\phi(\delta_{x},x,\delta_{t})]}{\partial x^{2}}d\delta_{x}-\int\frac{\delta_{x}^{3}}{6}\frac{\partial^{3}[\varphi(x,t)\phi(\delta_{x},x,\delta_{t})]}{\partial x^{3}}d\delta_{x}\end{align*}
$$

Because integration is done with respect to $ \delta_{x} $, partials with respect to x can be moved outside of the integrals, as can functions not involving $ \delta_{x} $, yielding

$$
\int\varphi(x-\delta_{x},t)\phi(\delta_{x},x-\delta_{x},\delta_{t})d\delta_{x}=\varphi(x,t)\int\phi(\delta_{x},x,\delta_{t})d\delta_{x}-\frac{\partial}{\partial x}\left(\varphi(x,t)\int\delta_{x}\phi(\delta_{x},x,\delta_{t})d\delta_{x}\right)
$$

$$
+\frac{1}{2}\frac{\partial^{2}}{\partial x^{2}}\left(\varphi(x,t)\int\delta_{x}^{2}\phi(\delta_{x},x,\delta_{t})d\delta_{x}\right)-\frac{1}{6}\frac{\partial^{3}}{\partial x^{3}}\left(\varphi(x,t)\int\delta_{x}^{3}\phi(\delta_{x},x,\delta_{t})d\delta_{x}\right)
$$

Because $ \phi(\delta_x, x, \delta_t) $ is the probability distribution of moves of size $ \delta_x $ over the time interval $ \delta_t $ given we start at position $ x $, we have

$$
\int\phi(\delta_{x},x,\delta_{t})d\delta_{x}=1
$$

$$
\int\delta_{x}\phi(\delta_{x},x,\delta_{t})d\delta_{x}=E\left(\delta_{x}\mid x_{t}=x\right)=m(x)\delta_{t}+o(\delta_{t})
$$

**[命题 Proposition]**

The first identity follows from the fact that the integral over a probability distribution is equal to one, and the second is simply our first diffusion assumption (Equation A1.1a). Next, if we recall that $ E(x^2) = \sigma_x^2 + [E(x)]^2 $, we have

$$
\int\delta_{x}^{2}\phi(\delta_{x},x,\delta_{t})d\delta_{x}=\sigma^{2}(\delta_{x})+[E(\delta_{x})]^{2}
$$

which, using the diffusion approximation (Equations A1.1a and A1.1b), reduces to

$$
\begin{align*}\int\delta_{x}^{2}\phi(\delta_{x},x,\delta_{t})d\delta_{x}&=[v(x)\delta_{t}+o(\delta_{t})]+[m(x)\delta_{t}+o(\delta_{t})]^{2}\\&=v(x)\delta_{t}+o(\delta_{t})\end{align*}
$$

**[命题 Proposition]**

The last step follows because the contribution from the squared change in the mean is $ o(\delta_t) $, and we sweep all such terms into a single expression. Finally, under the diffusion assumption given by Equation A1.1c, moments of $ \delta_x^3 $ and higher are negligible. Substituting the approximations given by Equations A1.8d and A1.8e into Equation A1.8b yields

$$
\varphi(x,t+\delta_{t})=\varphi(x,t)-\frac{\partial\left\{\left[m(x)\delta_{t}+o(\delta_{t})\right]\varphi(x,t)\right\}}{\partial x}+\frac{1}{2}\frac{\partial^{2}\left\{\left[v(x)\delta_{t}+o(\delta_{t})\right]\varphi(x,t)\right\}}{\partial x^{2}}
$$

Subtracting $ \varphi(x,t) $ from both sides, dividing both by $ \delta_{t} $, and taking the limit at $ \delta_{t}\to0 $ gives the left-hand size as

$$
\lim_{\delta_{t}\to0}\frac{\varphi(x,t+\delta_{t})-\varphi(x,t)}{\delta_{t}}=\frac{\partial\varphi(x,t)}{\partial t}
$$

Likewise, recalling that $ \lim_{\delta_t \to 0} o(\delta_t)/\delta_t = 0 $, the last two right-hand-side terms of Equation A1.9 simplify to

$$
\lim_{\delta_{t}\to0}\frac{1}{\delta_{t}}\left(\frac{\partial\left\{\left[m(x)\delta_{t}+o(\delta_{t})\right]\varphi(x,t)\right\}}{\partial x}\right)=\frac{\partial[m(x)\varphi(x,t)]}{\partial x}
$$

$$
\lim_{\delta_{t}\to0}\frac{1}{\delta_{t}}\left(\frac{\partial^{2}\left\{\left[v(x)\delta_{t}+o(\delta_{t})\right]\varphi(x,t)\right\}}{\partial x^{2}}\right)=\frac{\partial^{2}[v(x)\varphi(x,t)]}{\partial x^{2}}
$$

Together, these simplifications imply

$$
\frac{\partial\varphi(x,t)}{\partial t}=-\frac{\partial[m(x)\varphi(x,t)]}{\partial x}+\frac{\partial^{2}[v(x)\varphi(x,t)]}{2\partial x^{2}}
$$

which recovers the Kolmogorov forward equation (Equation A1.6), provided we again recall that $ \varphi(x,t) $ is really $ \varphi(x,t,p) $.

---

## Evolution_appendix1_008 · FOUNDATIONS OF DIFFUSION THEORY / Stationary Distributions

At equilibrium, a probability density function does not change over time, namely,

$$
\frac{\partial\varphi(x,t,p)}{\partial t}=0
$$

When such a function exists, it is called the stationary distribution and is denoted by $ \varphi(x) $. Stationary distributions are independent of the starting conditions: regardless of where the process starts in the interior of the diffusion, it converges to the same distribution. Hence, $ \varphi(x, t, p) $ can be decomposed into a transient deviation (dependent on $ t $ and $ p $) and a stationary expectation (independent of both $ t $ and $ p $), $ \varphi(x, t, p) = \varphi^*(x, t, p) + \varphi(x) $. The transient deviation satisfies $ \lim_{t \to \infty} \varphi^*(x, t, p) = 0 $, and the deviation from the equilibrium distribution decays to zero over time.

When Equation A1.10a is satisfied, Equation A1.6 becomes

$$
\frac{\partial^{2}[v(x)\varphi(x)]}{2\partial x^{2}}=\frac{\partial[m(x)\varphi(x)]}{\partial x}
$$

and integration of both sides reduces this to the simple differential equation,

$$
\frac{\partial[v(x)\varphi(x)]}{\partial x}=2m(x)\varphi(x)
$$

Using standard methods for differential equations (e.g., Tenenbaum and Pollard 1963) yields the solution as

$$
\varphi(x)=\frac{C}{v(x)G(x)}
$$

where G (which is called the scale function in the diffusion literature) is defined by the indefinite integral

$$
G(x)=\exp\left[-2\int^{x}\frac{m(y)}{v(y)}dy\right]
$$

**[示例 Example]**

*(See Example A1.3.)*

**[示例 Example]**

*(See Example A1.4.)*

**[示例 Example]**

*(See Example A1.5.)*

---

## Evolution_appendix1_009 · FOUNDATIONS OF DIFFUSION THEORY / The Kolmogorov Backward Equation

While the KFE provides both the full solution of $ \varphi(x, t, p) $ and, where appropriate, the equilibrium solution, we can obtain much simpler expressions for many quantities of interest when an equilibrium solution does not exist. For example, if one or both of the boundaries are accessible and absorbing, we can compute the fixation probabilities (the probability that the process eventually will reach a specified boundary), the time to reach that boundary (the time to loss or fixation), and the expected value of many other functions of interest. The key to all of these operations is the Kolmogorov backward equation (KBE), which is given by

$$
\frac{\partial\varphi(x,t,p)}{\partial t}=\frac{1}{2}v(p)\frac{\partial^{2}\varphi(x,t,p)}{\partial p^{2}}+m(p)\frac{\partial\varphi(x,t,p)}{\partial p}
$$

The KBE is derived in a manner similar to the KFE. The KBE starts at the current time, t, and looks backwards in terms of how changes $ \left(\partial/\partial p\right) $ in the initial starting value, p, are influenced by the current position, x, hence the name. Conversely, the forward equation (Equation A1.6) examines how changes $ \left(\partial/\partial x\right) $ in the current position, x, are influenced by the starting value, p.

---

## Evolution_appendix1_010 · Appendix: Introduction / DIFFUSION APPLICATIONS IN POPULATION GENETICS

When no stationary distribution exists, useful summary statistics to describe the diffusion process are the probabilities of fixation of the various boundaries and the expected time to reach a specified boundary. We consider each in turn.

---

## Evolution_appendix1_011 · DIFFUSION APPLICATIONS IN POPULATION GENETICS / Probability of Fixation

When at least one boundary is absorbing (and accessible), no stationary distribution exists. In such cases, one important descriptor of the process is the probability of reaching one boundary before the other. One can show that the function $ u(p, t) $, the probability of fixation by time t, given that we start at allele frequency p, satisfies the KBE. We are typically interested in the ultimate probability of fixation, $ u(p) = \lim_{t \to \infty} u(p, t) $, in which case the partial derivative of $ u(p) $ with respect to time is zero and, from Equation A1.16, $ u(p) $ satisfies

$$
0=m(p)\frac{\partial u(p)}{\partial p}+\frac{1}{2}v(p)\frac{\partial^{2}u(p)}{\partial p^{2}}
$$

This has a solution of

$$
u(p)=\frac{\int_{0}^{p}G(x)dx}{\int_{0}^{1}G(x)dx}
$$

where $ G(x) $ is defined by Equation A1.12 (Kimura 1962). More generally, for any diffusion (regardless of the nature of the boundaries), the probability that the process reaches a value of b before a value of a, given it starts at p (where $ A < a < p < b < B $, with the diffusion defined over $ A < x < B $), is

$$
u_{b,a}(p)=\frac{\int_{a}^{p}G(x)dx}{\int_{a}^{b}G(x)dx}
$$

**[示例 Example]**

*(See Example A1.6.)*

**[示例 Example]**

*(See Example A1.7.)*

---

## Evolution_appendix1_012 · DIFFUSION APPLICATIONS IN POPULATION GENETICS / Time to Fixation

The time for a process to reach a specified value (or values) is called the sojourn time. While we are often interested in the sojourn time to an absorbing boundary (the fixation time), the more general problem of the time to first reach a specific value within the interval over which the diffusion is defined is also tractable. Letting $ \bar{t}_{a,b} $ denote the expected time that a diffusion spends in the interval $ (a,b) $ given it starts at frequency p, then

$$
\bar{t}_{a,b}=\int_{0}^{\infty}\Pr\left(a\leq x_{t}\leq b\right)dt=\int_{0}^{\infty}\int_{a}^{b}\varphi(x,t,p)dx dt
$$

If a stationary distribution exists, this time is infinite and hence not really of much biological interest. However, if one or both boundaries are absorbing (and accessible), then $ \bar{t}(p) $, the total time the diffusion spends in the interior, is obtained from Equation A1.21 by letting a and b be the lower and upper limits, respectively, of the diffusion (typically, a = 0, b = 1).

A very useful approach for solving Equation A1.21, and more general problems, is to consider $ h(x,p) $, the expected amount of time that the process (starting at p) spends in the neighborhood of x before it is eventually absorbed. Formally, this is given by

$$
h(x,p)=\int_{0}^{\infty}\varphi(x,t,p)dt
$$

Thus, Equation A1.21 can be expressed as

$$
\begin{align*}\bar t_{a,b}=\int_a^b h(x,p)dx\end{align*}
$$

$ h(x,p) $ is called a Green's function, and it will prove very useful in solving a variety of problems. The general solution for $ h(x,p) $, obtained by Maruyama (1977), is

$$
h(x,p)=\left\{\begin{aligned}&\frac{2[1-u(p)]}{v(x)G(x)}\int_{a}^{x}G(y)dy&\text{for}a<x<p\\ &\frac{2u(p)}{v(x)G(x)}\int_{x}^{b}G(y)dy&\text{for}p<x<b\end{aligned}\right.
$$

where the fixation probability, $ u(p) $, is provided by Equation A1.17a.

One can also obtain modified Green’s functions for conditional processes, such as processes leading only to loss or processes leading only to fixation. For example, $ \bar{t}_{F} $, the expected time to fix allele A (in those populations where it is fixed) is given by replacing $ h(x,p) $ in Equation A1.22b by

$$
h_{1}(x,p)=h(x,p)\frac{u(x)}{u(p)}
$$

This follows from standard conditional probability arguments (see Ewens 1979, 2004), with $ u(x)/u(p) $ correcting for the fact that we are only considering those sample paths over which the allele of interest (A) is fixed. This occurs with probability $ u(p) $, and hence $ u(x)/u(p) $ is the conditional density. Similarly, $ \bar{t}_{L} $, the expected time to lose allele A, is obtained by replacing $ h(x,p) $ in Equation A1.22b by

$$
h_{0}(x,p)=h(x,p)\frac{1-u(x)}{1-u(p)}
$$

Finally, we note that $ \bar{t}, \bar{t}_{F} $, and $ \bar{t}_{L} $ are related by

$$
\bar{t}(p)=u(p)\bar{t}_{F}(p)+[1-u(p)]\bar{t}_{L}(p)
$$

That is, the expected time to loss or fixation is equal to the expected time to fixation multiplied by the probability of fixation plus the expected time to loss multiplied by the probability of loss.

**[示例 Example]**

*(See Example A1.8.)*

---

## Evolution_appendix1_013 · DIFFUSION APPLICATIONS IN POPULATION GENETICS / Expectations of More General Functions

The expressions for sojourn times are relatively simple examples of computing expected values along a sample path of the diffusion process, and more complex functions can be evaluated in a similar manner. Let $ x_t $, which resides in the open interval $ (0,1) $, denote the values of our random variable along a particular sample path, and suppose that we wish to compute the integral (over all time) of some function $ f $ of $ x_t $

$$
I_{f}(p)=\int_{0}^{\infty}f(x_{t})dt
$$

Note that $ x_{t} $ is the realization at a particular time point, and hence the distribution of $ x_{t} $ (and thus ultimately $ I_{f} $) is a function of p, the starting value of our process. Because $ x_{t} $ is a random variable, the integral $ I_{f}(p) $ is also a random variable. Its expected value is given by

$$
E[I_{f}(p)]=\int_{0}^{\infty}\int_{0}^{1}f(x)\varphi(x,t,p)dt dx
$$

**[示例 Example]**

*(See Example A1.9.)*

---

## Evolution_appendix1_014 · Appendix: Introduction / APPLICATIONS IN QUANTITATIVE GENETICS

While we have focused on population-genetic applications of diffusion processes, this approach is also very useful for solving a number of problems in quantitative genetics. When attention shifts from individual alleles to a quantitative character, diffusions typically follow mean phenotypes instead of allele frequencies. Two well-studied diffusions, Brownian motion and the Ornstein-Uhlenbeck process, are especially useful (Chapter 12).

---

## Evolution_appendix1_015 · APPLICATIONS IN QUANTITATIVE GENETICS / Brownian-motion Models

For Brownian motion (also called the Wiener process), the diffusion over the interval $ -\infty < x < \infty $ is defined as

$$
m(x)=a\quad and\quad v(x)=b
$$

where b > 0. The general solution under Brownian motion starting at $ x_{0} $ is that

$$
x_{t}\sim\mathrm{N}(x_{0}+at,bt)
$$

namely, the distribution of $ x_t $ is normal, with a mean of $ x_0 + at $ and a variance of $ \sigma_t^2 = bt $. There is no equilibrium solution, as the process converges to a normal distribution with infinite variance (and, if $ a \neq 0 $, an infinite mean).

**[示例 Example]**

*(See Example A1.10.)*

**[示例 Example]**

*(See Example A1.11.)*

**[示例 Example]**

*(See Example A1.12.)*

---

## Evolution_appendix1_016 · APPLICATIONS IN QUANTITATIVE GENETICS / Ornstein-Uhlenbeck Models

The Ornstein-Uhlenbeck process is an extension of the Brownian-motion model to include a linear restoring force back to the origin. The one-dimensional version of this diffusion process for $ -\infty < x < \infty $ is given by

$$
m(x)=-ax\quad and\quad v(x)=b
$$

with a, b > 0. As with Brownian motion, the distribution of $ x_{t} $ (given the starting condition $ x_{0} $) is also normal, but now with a mean and a variance of

$$
\mu_{t}=x_{0}e^{-at}\quad and\quad\sigma_{t}^{2}=\frac{b}{2a}\left(1-e^{-2at}\right)
$$

See Karlin and Taylor (1981) for a derivation. The resulting stationary distribution is normal with a mean of zero (on the assumed scale) and a variance of $ b/(2a) $. More generally, if $ m(x) = -a(x - \theta) $, so that the resorting force is toward the value $ x = \theta $, then the variance will be unchanged, while

$$
\mu_{t}=\theta+(x_{0}-\theta)e^{-at}
$$

**[示例 Example]**

*(See Example A1.13.)*

**[示例 Example]**

*(See Example A1.14.)*

---
