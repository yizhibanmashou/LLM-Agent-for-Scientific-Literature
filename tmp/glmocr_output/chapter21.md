<div align="center">

# 21

</div>

<div align="center">

# Family-Based Selection

</div>

Practical breeding programs must be commercially optimal not theoretically maximal. Fairfull and Muir (1996)

Up to now, we have focused on individual selection, wherein selection decisions are based solely on the phenotypes of single individuals (this is also referred to as mass selection or phenotypic selection, and we use all three terms interchangeably). Selection decisions can also incorporate the phenotypic values of an individual's measured relatives, and in fact, most plant- and animal-breeding schemes do so. The focus of this chapter is on family-based selection—using family information to select individuals. While we restrict discussion in this chapter to using sibs, the culmination of this approach is BLUP selection using an index based on the entire known pedigree of an individual, which is the major route for artificial selection in most domesticated animals (Chapters 13 and 19). While our focus here is on short-term selection response (formally, the single-generation response), certain family-based schemes can give a greater long-term response than individual selection, even when their initial response is less. This long-term advantage arises because of larger effective population sizes associated with selection schemes that down-weight among-family differences, a point examined in detail in Chapter 26.

There are a variety of reasons for using family-based schemes. Employing mass selection may be impractical in many settings due to difficulties in measuring trait values in single individuals (e.g., most forage crops and cereals). Family-based designs can also provide greater accuracy in predicting an individual's breeding value, and hence can give a larger (short-term) response. In particular, an appropriately weighted index of an individual's family mean and phenotypic value has an expected response at least as large as mass selection. When significant environmental heterogeneity exists (e.g., crops planted across a broad climatic range), the replication of families over environments provides a more efficient method than mass selection for choosing higher-performing genotypes. This is one major factor leading crop breeders to favor family-based schemes over individual selection.

The structure of this chapter is as follows. We start with a brief overview of the nature and types of family-based selection schemes before considering extensions of the generalized breeder's equation to accommodate these approaches. Next, we develop the variances and covariances required to apply these equations, and then consider a number of these schemes in detail. The relative efficiencies of within- and among-family selection compared to mass selection are then examined, followed by a consideration of designs in which families are replicated over environments, as is usually the case in plant breeding. We conclude by examining the properties of family-index selection. While most of the concepts in this chapter are straightforward, the bookkeeping can be tedious at times. Thus, we summarize key results at the end of various sections to allow the casual reader to more easily navigate through this material.

## INTRODUCTION TO FAMILY-BASED SELECTION SCHEMES

Family-based designs are based on two approaches: among-family schemes, which choose entire families on the basis of their mean performance, and within-family schemes, which choose individuals based on their relative performance within their families. While many designs are based on just one of these components, the most general approach is familyindex selection, wherein individuals are chosen based on a weighted index of among and within-family components. Mass selection is a special case of a family index, where the within- and among-family components are weighted equally. (Although the phrase

"between-family selection" is widely used in the literature, "between" refers to a comparison of two items, while "among" refers to comparisons of two or more, which is the general setting here. Hence, while between- and among- are used interchangeably in the literature, we will use "among" throughout our discussion here.)

While we assume that the parents in any particular family are from the same population, in some breeding settings the parents are from different populations. Examples of this are interpopulation improvement schemes, where the goal is to improve the performance of hybrids among populations (Volume 3). The focus in this chapter is family-based schemes for intrapopulation improvement (increasing the performance of the population under selection).

## Overview of the Different Types of Family-based Selection

The key to making sense out of the bewilderingly large number of family-based designs in the literature is to consider the individual components that together define any particular scheme. The first component is the type of sib family providing information for selection decisions. A family may consist of half-sibs, full-sibs, or full-sibs nested within half-sibs (e.g., the NC Design I; see LW Chapter 18). Sibs can also be generated by one (or more) generations of selfing (e.g., $ S_{1}, S_{2} $ ), and we examine such families in Chapter 23. While the family-based schemes developed in this chapter are generally used with allogamous species (outcrossers, cross-pollination), they can also be applied to facultatively autogamous species (facultative selfers, self-pollination) through the use of controlled pollination and/or the introduction of male-sterile genes under open pollination (e.g., Gilmore 1964; Doggett and Eberhart 1968; Brim and Stuber 1973; Burton and Brim 1981; Sorrells and Fritz 1982).

Once a particular family type has been chosen, the second component is how sib data are used for selection decisions. One could use among-family selection, choosing the best families (i.e., those with the largest family means). Alternatively, one could use within-family selection, choosing either the best individuals within each family (strict withinfamily [WF] selection), or the individuals with the largest deviations from their family means (family-deviations [FD] selection). While WF and FD selection are very similar, there are subtle differences between the two schemes, as they do not necessarily select the same individuals. One could also consider an index weighting both family mean and family deviations.

The final design component is the relationship between the measured sibs and the individuals serving as parents for the next generation. Under either within-family or familyindex selection, the selected individuals are used to form the next generation. However, in among-family selection, we can use any number of relatives of the chosen (selected) families to form the next generation. The most straightforward approach is to use measured sibs from the chosen families (family selection). However, some characters cannot be scored on living organisms, such as carcass traits in production animals, or can only be scored after reproduction. In such cases, one can use unmeasured sibs from the best families as the parents of the next generation (sib selection), which is often used to improve selection on sex-specific traits. For example, milk production can be selected for in males by choosing sires from families whose sisters show high levels of production. An important variant of sib selection is the use of remnant seeds from the best families, which are planted and subsequently crossed to form the next generation. In perennial species and in annual species that can be asexually propagated (cloned), one can select the best parents by the performance of their offspring (parental selection or progeny testing). Finally, an option available for facultatively autogamous species is to both self an individual to generate $ S_{1} $ progeny （ $ S_{1} $ seeds) and likewise outcross it to one or more individuals to generate a family for testing. For such species, one can grow and intercross the remnant $ S_{1} $ seed from the chosen families to form the next generation (the $ S_{1} $ seed design).

## Plant Versus Animal Breeding

While animal breeders typically employ only a few standard sib-based designs (Turner and

Young 1969), plant breeders can choose from a vast array of options (e.g., Hallauer and Miranda 1981; Schnell 1982; Nguyen and Sleper 1983; Wricke and Weber 1986; Hallauer et al. 1988; Aastveit and Aastveit 1990; Nyquist 1991; Vogel and Pedersen 1993; Holland et al. 2003; Hallauer et al. 2010). Furthermore, the final product desired by a plant breeder can vary considerably: it could be an open-pollinated population, an $ F_{1} $ hybrid, a pure (i.e., fully inbred) line, or a synthetic line. Thus, it is not surprising that the literatures on family-based selection in the two fields are rather divergent. Much of the animal-breeding literature is expressed in terms of the phenotypic (t) and additive-genetic (r) correlations among sibs, while much of the plant-breeding literature is expressed in terms of variance components. As our discussion attempts to interweave both approaches, we will typically present selection-response equations in both forms.

Reproductive differences between plants and animals underlie many of the differences in the designs that are available to breeders. Historically, plant breeders have had more options than animal breeders because of the reproductive flexibility of many plants (i.e., selfing, stored seed, vegetation propagation; see Fehr and Hadley 1980). With the cloning of several domesticated animals, animal breeders now have the option of exploiting some of these classical plant-breeding schemes.

One obvious difference between plants and many animals is the ability to easily store progeny for many generations in the form of seed. Generally speaking, plants also produce far more offspring than domesticated animals, providing more offspring per family, and thus allowing for more extensive replication of families across environments. Another reproductive advantage of plants is that asexual propagation (cloning) is straightforward in many species, allowing individual genotypes to be preserved over generations.

Yet another key difference is in the control of crosses. While simple isolation will prevent most undesirable crosses in animals, either complete isolation or extensive manual control may be required to prevent pollination vectors from generating undesirable crosses in plants. When studying facultatively autogamous species, the investigator may be faced with either trying to prevent selfing or trying to prevent outcrossing, or to allow for both while identifying which seed came from which type of cross. Options for controlled crosses range from complete manual control over pollination at one extreme to open pollination at the other. Given that most plants have multiple flowers (which are often both numerous and small), large-scale controlled crosses can be much more labor intensive than similar crosses among animals, as hand pollination and the control of external and/or self-pollinators may be required. Even under open pollination (allowing seed plants to be pollinated at random), the investigator still has different levels of control over the pollen spectrum that a seed plant experiences. In a test cross or topcross design, the population of plants supplying the pollen is controlled. For example, individual maize plants can be detasseled by hand (removing the pollen-producing tassels) or have their tassels bagged to prevent the plants from either selfing or pollinating other plants. Such plants serve only as seed plants and are intergrown with rows of the tester strain, which provide the pollen. Under true open pollination, seed parents are randomly pollinated from the population, with no control of the pollen parent. A consequence of open pollination is that while most half-sib families in animal breeding are paternal, most half-sib families in plant breeding are maternal (they share a common seed parent).

There are also more subtle biological differences between plants and animals that drive differences in designs. While one can usually score many traits in individual animals, this is often not done in plants. For example, many traits of forage grasses, grains, and legumes are scored as plot totals, which involves measuring the mean performance of an entire family (or line) instead of each separate individual. When individuals cannot be directly scored, among-family selection is possible, but within-family and family-index selection are not. Similarly, many selected traits in plants can be scored only after reproduction (seed or fruit yield being prime examples), and this influences the types of relatives that can be used to form the next generation.

## Among- Versus Within-family Selection

When the heritability of a trait is high, an individual's phenotype is an excellent predictor of its breeding value, and mass selection is more efficient than either strict within- or amongfamily selection. When heritability is low, individual phenotypic value is a poor predictor of breeding value, in which case an individual's family mean or its relative performance within its family may be better predictors.

The relative efficiencies of among- versus within-family selection depend on the relative magnitudes of the common-family $ ( E_{c} ) $ and individual-specific $ ( E_{s} ) $ environmental variances. A large common-family effect severely compromises the phenotype as a predictor of breeding value. However, within each family, all members share the same environmental effect, and differences between individuals more accurately reflect differences in breeding value. In this case, selection within families (for example, by choosing the largest individuals from each family) can yield a larger response than individual selection. Many mouse selection experiments use within-family selection, especially for traits with suspected maternal effects, such as body weight (Falconer and Latyszewski 1952; Falconer 1953, 1960a; Eisen and Hanrahan 1972; von Butler and Pirchner 1984; Nielsen and Anderson 1987; Siewerdt et al. 1999), litter size (Falconer 1960b), and nesting behavior (Lynch 1980).

Conversely, suppose that environmental effects unique to each individual account for a large fraction of the phenotypic variance $ \sigma_{E_{s}}^{2}\gg\sigma_{E_{c}}^{2} $ . In this case, selecting whole families as units can give a larger response than individual selection, as the family mean averages out differences based on environmental values, revealing those families with the most extreme breeding values. An important example of this family-averaging of environmental effects is the use of among-family selection to improve performance across multiple environments. Under mass selection, a genotype is represented by a single individual in a single environment, while family-based approaches allow the performance of different families to be compared over multiple environments. Such studies are by no means restricted to plant breeding, as animal selection experiments examining phenotypic plasticity (norms of reaction), in which genotypes must also be assessed over multiple environments, almost exclusively use among-family selection (e.g., Waddington 1960; Kindred 1965; Waddington and Robertson 1966; Druger 1967; Scharloo et al. 1972; Brumpton et al. 1977; Minawa and Birley 1978; Scheiner and Lyman 1991).

## DETAILS OF FAMILY-BASED SELECTION SCHEMES

## Selection and Recombination Units

Under mass selection, individuals are scored and those with the best phenotypic values are used as parents to form the next generation. Here groups of individuals upon which selection decisions are based and those used for recombination (gamete production to form the next generation) are one and the same, and a single cycle of selection takes a single generation. In family-based selection schemes, the individuals used for selection decisions may be entirely separate from those used as parents to form the next generation. Further, a single cycle of selection may take two (or more) generations, as one must generate, score, and recombine families. For perennial species (such as forage crops), traits may be scored over several years before selection decisions are made, such as selecting for winter hardiness (Vogel and Pedersen 1993).

Following the convention of plant breeders, we distinguish between an individual, $ x_{i} $ in the selection unit (those measured individuals upon which selection decisions are made, which throughout this chapter are we assume are sibs) and an individual, $ \mathcal{R}_{i} $ (a relative of $ x_{i} $ potentially including $ x_{i} $ itself), from the recombination unit (individuals serving as parents for the next generation) whose resulting offspring are $ y $ . Even though we may not directly select on the parents $ (\mathcal{R}_{1},\mathcal{R}_{2}) $ of $ y $ , we expect some response in $ y $ due to the genetic correlation between $ x_{i} $ and $ \mathcal{R}_{i} $ caused by their sharing of (at least) one common relative, $ P_{i} $ (Figure 21.1). An equivalent way to think about this distinction is that selection response occurs due to

![](page=4,bbox=[319, 131, 553, 246])

<div align="center">

Figure 21.1 Under family-based schemes, selection decisions are based on some function of the values of measured sibs $ ( x_{i} ) $ in the selection unit. An offspring, y, in the next generation has parents, $ \mathcal{R}_{1} $ and $ \mathcal{R}_{2} $ , that are chosen on the basis of the selection unit. Members of the selection $ ( x_{i} ) $ and recombination $ (\mathcal{R}_{i}) $ units are related as they both share a common relative, $ P_{i} $ , which in this case is the parent of sib $ x_{i} $ . Under within-family or family-index selection, $ \mathcal{R} $ is simply one of the measured sibs, while under among-family selection, $ \mathcal{R} $ is often an unmeasured relative. See Figure 21.2 for specific examples.

</div>

observations on the selection unit, x, providing information to predict the breeding value of $ \mathcal{R} $

As mentioned in the introduction, the variety of family-based schemes appearing in the literature arises from the combination of four specific components:

1. Type of sib family comprising the selection unit. Sibs can be half- or full-sibs, full-sibs nested within half-sibs (NC Design I), or selfed sibs (which are considered in Chapter 23).

2. Nature of the selection decisions based on the sib information. Selection can be based on sib-family means, the deviations of individuals within families, an index of both, or strict rank within families.

3. Selection on one versus both parents. Often selection decisions involve only one sex, with the parents of the opposite sex chosen at random (and hence being unselected). For example, a trait may not be scorable until after pollination, resulting in selection on seed parents (females) but not on pollen parents (males). In such cases, we are only concerned with one side of the pedigree, for example, involving $ \mathcal{R}_{1} $ but not $ \mathcal{R}_{2} $ (Figure 21.1). More generally, the two parents $ (\mathcal{R}_{1} $ and $ \mathcal{R}_{2} $ ) of the offspring, y, may be chosen using different schemes, which generates a variety of family-based schemes.

4. Nature of the relationship between a measured sib, $ x_{i} $ in the selection unit and a parent, $ \mathcal{R}_{i} $ of the next generation. Under within-family or family index selection, $ \mathcal{R} $ is one of the measured sibs $ (\mathcal{R}_{i}=x_{i}) $ , while under among-family selection, $ \mathcal{R} $ is often an unmeasured relative. For example, $ \mathcal{R}_{i} $ could be the parent of the sibs $ (\mathcal{R}_{i}=P_{i}) $ , meaning that the relationship between x and $ \mathcal{R} $ is that of parent-offspring, or it could be an unmeasured sib, meaning that the relationship between x and $ \mathcal{R} $ is that of either half- or full-sib (depending on the type of family).

While the variety of family-based selection schemes may seem a bit overwhelming at first (especially in the plant-breeding literature), considering each design in terms of these four components greatly simplifies matters.

## Variations of the Selection Unit

Once the type of family (half-sib, full-sib, nested, or inbred $ S_{i} $ ) has been specified, there is still the issue of how to incorporate sib information when making selection decisions. To distinguish between a particular sib and the trait value of that sib, we use $ x_{i} $ to denote the i th sib and $ z_{i} $ to denote its trait value, and more generally, $ x_{ij} $ and $ z_{ij} $ for the jth individual

from the i th family. We select the uppermost fraction, p, of the relevant population, with m families each with n sibs, for a total of M=mn scored individuals, which we use to choose N parents. Four different approaches for weighting sib information are commonly used:

1. Among-family selection: Individuals are selected solely on the basis of their family means, $ \overline{z}_{i} $ with the result that all individuals from the same family have the same selective rank. Here, the best N=pm families are chosen.

2. Strict within-family (WF) selection. The best pn individuals from each family are chosen $ ( N= p n m= p M ) $ , so that individuals are ranked within each family. WF selection increases the effective population size because the among-family variance in offspring number is zero (Chapters 3 and 26).

3. Selection on within-family deviations (FD): Individuals are ranked solely on the basis of their within-family deviation, $ z_{ij}-\bar{z}_{i} $ . The N=pM individuals with the largest deviations (regardless of family) are chosen.

4. Family-index selection: Individuals are ranked using an index weighting within and among-family components

$$
I = b _ {1} \left(z _ {i j} - \bar {z} _ {i}\right) + b _ {2} \bar {z} _ {i} = b _ {1} z _ {i j} + \left(b _ {2} - b _ {1}\right) \bar {z} _ {i}
$$

The pM individuals with the best index scores are chosen. Note that the index with weights $ ( c b_{1}, c b_{2} ) $ chooses the same individuals as an index with weights $ ( b_{1}, b_{2} ) $ . Thus, one of the index weights is often set to one, as the indices with weights $ ( b_{1}, b_{2} ) $ $ ( 1, b_{2} / b_{1} ) $ , and $ ( b_{1} / b_{2}, 1 ) $ are all equivalent (in that they all choose the same individuals). Individual selection, among-family selection, and selection on family deviations (FD) are special cases, being indices with weights $ ( b_{1}, b_{2} ) = $ (1,1), (0,1), and (1,0), respectively. Note, however, that strict within-family (WF) selection cannot be expressed in terms of an index. Family-index selection is also referred to as combined selection, which is unfortunate, as the same term is also used by breeders to refer to approaches that combine different types of selection schemes in a single cycle (such as modified ear-to-row selection, discussed below).

The choice of the particular scheme has implications for the selection intensity (Example 21.1). When the fraction saved (p) is fixed, among-family and strict within-family selection have lower selection intensities than family-deviations, index, or mass selection. The former selects the best pm of m families and pn of n sibs, while the latter three select the best pM of M individuals. Because M is greater than either n or m, the finite-sample value for $ \bar{\iota} $ is larger when sampling from M than from n or m (Chapter 14).

<div align="center">

Example 21.1. Suppose that a total of 100 sibs are measured and the fraction that is selected is p=0.2. As a benchmark, for this level of selection, the infinite-population value for the selection intensity is $ \bar{\iota}=1.40 $ (Equation 14.3a). Suppose that the M=100 total measured sibs are distributed into 20 families of five sibs each $ (m=20,n=5) $ . Under within-family selection, the top 1 of 5 within each family is selected. Under among-family selection, the top 4 of the 20 families are selected. Finally, under family-deviations or index selection, the top 20 of the 100 measured individuals are selected. Using the finite-size correction approximation offered by Equation 14.4b yields the following selection intensities:

</div>

<table border="1"><tr><td>Individual selection(infinite population)</td><td>Best 20%</td><td>$\bar{\iota}_{\infty}=1.40$</td></tr><tr><td>Individual selection,index selection,family-deviations(FDs) selection</td><td>Best 20 of 100</td><td>$\bar{\iota}_{(20,100)}=1.39$</td></tr><tr><td>Among-family selection</td><td>Best 4 of 20</td><td>$\bar{\iota}_{(4,20)}=1.33$</td></tr><tr><td>Strict within-family selection(WF)</td><td>Best 1 of 5</td><td>$\bar{\iota}_{(1,5)}=1.16$</td></tr></table>

As shown later (Equations 21.40 and 21.57), additional corrections to the selection intensity are required in some cases, as family members are correlated, which changes the variance

(A) Family selection $ \mathcal{R} $ is a measured sib

(B) Sib selection

$ \mathcal{R} $ is an unmeasured sib

![](page=6,bbox=[243, 153, 606, 382])

<div align="center">

Figure 21.2 Under among-family selection, decisions as to which families to choose are made on the basis of observations from sibs, while the next generation is formed by crossing relatives $ (\mathcal{R}) $ of sibs from the chosen families. The measured sibs upon which selection decisions are based are denoted by $ x_{1},\cdots,x_{n} $ , while y denotes a random offspring from a random member, $ \mathcal{R} $ , from the recombination unit. Different types of relatives can be used for $ \mathcal{R} $ , with a few of the most common types illustrated here. Let P denote the shared parent(s) of $ x_{i} $ and $ \mathcal{R} $ . The pedigrees illustrated here all focus on just one parent of y, with a corresponding pedigree for the other parent. A: Family selection: $ \mathcal{R} $ is one of the measured sibs $ (x_{1}=\mathcal{R}) $ . B: Sib selection: $ \mathcal{R} $ is an unmeasured sib. C: Parental selection (also known as progeny testing): $ \mathcal{R} $ is the parent of the sibs $ (\mathcal{R}=P) $ . D: $ S_{1} $ seed selection: $ \mathcal{R} $ is the selfed progeny of the parent of the sibs, but $ \mathcal{R} $ is then outcrossed to generate the offspring, y. In this chapter, we assume offspring are generated by outcrossing $ (\mathcal{R}_{1} $ and $ \mathcal{R}_{2} $ are unrelated), whereas in Chapter 23 we examine the setting wherein y is obtained by selfing $ \mathcal{R} $ , as well as more general inbreeding schemes (such as the tested sibs being the result of selfing).

</div>

relative to n unrelated individuals. Ignoring this correction (for now), note that strict withinfamily (WF) selection has only 83% of the selection intensity (for this example) as family deviations (FDs) selection.

Finally, the choice of the selection scheme also influences the long-term effective population size (and hence the long-term response; see Chapter 26), with schemes that place more weight on among-family components resulting in smaller effective population sizes (due to larger among-family offspring variances) than those that place more weight on within-family components (Chapter 3).

## Variations of the Recombination Unit

Under either within-family or index selection, measured individuals are selected as the parents for the next generation, which forms the recombination unit. By contrast, with among-family selection there are a variety of options for the nature of the relatives that comprise the recombination unit (Table 21.1; Figure 21.2). The most straightforward situation is family selection, using measured sibs from each chosen family as the parents for the next generation (Figure 21.2A). Under sib selection, unmeasured sibs from the chosen families are used to form the next generation (Figure 21.2B).

<div align="center">

Table 21.1 Family-based selection schemes using outbred sibs. Families are selected based on the sib values $ z_{i1}, \dots, z_{in}. $ $ \mathcal{R}_{i} $ denotes a relative of the $ i $ th selected family used to form the next generation. The variables $ \overline{{{z}}}_{HS} $ and $ \overline{{{z}}}_{FS} $ denote the sample means, and $ \mu_{HS} $ and $ \mu_{FS} $ denote the true means, of half- and full-sib families, respectively, while P is the parent of the measured sibs, and $ z_{ij} $ denotes the jth measured sib from family i.

</div>

<table border="1"><tr><td></td><td>Recombination UnitR</td><td>Selection Unitx</td></tr><tr><td>Family selection</td><td>Measured sib</td><td></td></tr><tr><td>Half-sib family selection</td><td></td><td>$\overline{z}_{HS}$</td></tr><tr><td>Full-sib family selection</td><td></td><td>$\overline{z}_{FS}$</td></tr><tr><td>Sib selection/Remnant seed</td><td>Unmeasured sib</td><td></td></tr><tr><td>Half-sib sib selection</td><td></td><td>$\overline{z}_{HS}$</td></tr><tr><td>Full-sib sib selection</td><td></td><td>$\overline{z}_{FS}$</td></tr><tr><td>Parental selection/Progeny testing</td><td>ParentP</td><td>$\overline{z}_{HS}$</td></tr><tr><td>S1Seed Selection</td><td>S1Seed ofP</td><td></td></tr><tr><td>Half-sib S1seed selection</td><td></td><td>$\overline{z}_{HS}$</td></tr><tr><td>Full-sib S1seed selection</td><td></td><td>$\overline{z}_{FS}$</td></tr><tr><td>Within-family Selection</td><td></td><td></td></tr><tr><td>Family deviations(FD) selection</td><td>Measured Sib</td><td></td></tr><tr><td>Half-sib family deviations selection</td><td></td><td>$z_{ij}-\overline{z}_{HS}$</td></tr><tr><td>Full-sib family deviations selection</td><td></td><td>$z_{ij}-\overline{z}_{FS}$</td></tr><tr><td>Strict within-family(WF) selection</td><td>Measured Sib</td><td></td></tr><tr><td>Half-sib strict within-family selection</td><td></td><td>$z_{ij}-\mu_{HS}$</td></tr><tr><td>Full-sib strict within-family selection</td><td></td><td>$z_{ij}-\mu_{FS}$</td></tr></table>

In animal breeding, sib selection is often used for traits that are sex-limited or that cannot be scored without sacrificing the individual. Plants breeders routinely use sib selection in the form of remnant seeds. Here, seeds from a cross are split into two batches and one is planted and used to assess families while the other is held in reserve. Seeds from the choosen families are then grown and crossed to form the next generation. Under this design, a single cycle of selection takes (at least) two generations—(at least) one to assess the families and a second to grow and cross the remnant seeds. Given this extra generation, what is the advantage of crossing plants from remnant seeds to form the next generation? For annual plants, any traits that are expressed during or after flowering can only be directly selected in already pollinated females, with seeds from the best-performing plants forming the next generation. Because these plants were pollinated at random, selection has occurred for the seed, but not the pollen, parents. By using remnant seeds, one can chose the best families, grow their remnant seeds, and allow the resulting plants to randomly intercross. Because both seed and pollen parents have now been selected (through their families), a single cycle of selection using remnant seed has double the response of family selection on seed from open pollinated plants. This doubling of response per cycle exactly counters the extra generation in each cycle, so open-pollinated family selection and sib selection using remnant seed have the same expected response per generation. One potential advantage with the use of remnant seed is that the extra generation to grow the seeds to mature plants for crossing can be used for selection on other characters, for example, culling those otherwise elite families that show poor disease or insect resistance.

Another common among-family design is parental selection (or progeny testing), where $ \mathcal{R}=P $ , the parent of the measured sibs (Figure 21.2C). This design typically involves evaluation of half-sib families with selection on just one sex. In animal breeding, these are typically sires, elite males chosen by the performance of their half-sib families, which is greatly facilitated by the use of artificial insemination and frozen semen. The ability to clone domesticated animals (e.g., sheep, Campbell et al. 1996; goats, Baguisi et al. 1999;

and cattle, Wells et al. 1999a, 1999b) is likely to further increase the importance of progeny testing in animal-breeding settings. (The most elaborate, and widely used, extension of progeny testing is BLUP selection wherein the entire pedigree is used for information on selection decisions; Chapter 19). Plant breeders typically perform progeny testing using maternal half-sib families (seed from the common parent). Vegetative propagation (cloning) allows even some annual plants to be used as parents in future generations. Depending on reproductive timing, if the species being selected is monoecious (single individuals produce both seed and pollen), one potentially may be able to obtain elite plants for both seed and pollen on the basis of female (seed) performance, and hence select on both sexes.

Finally, with self-compatible species, an alternative to vegetative propagation is the $ S_{1} $ seed design (Figure 21.2D). For each parent, a subset of flowers is selfed to produce $ S_{1} $ seed and the remainder are outcrossed. The outcrossed seed is then grown to produce the sibs in which the trait of interest is assessed. Following selection of the best families, their $ S_{1} $ seed grown and the adults from different families are crossed to form the next generation. As with remnant seed, a single cycle takes two generations. In maize, the $ S_{1} $ seed design requires the use of prolific plants (those with more than one ear), as one ear is selfed, and the other(s) outcrossed. Hallauer and Mirana (1981) noted that the use of such plants also results in selection for prolificacy, which by itself can increase yield. An advantage of designs using remnant seed is that traits can be scored over several years before selection, providing the opportunity to select over temporal variation in the environment. As presented in this chapter, the $ S_{1} $ seed design has a random-mated family as the selection unit. Obviously, one could collect only $ S_{1} $ seed from a plant and use some for selection decisions (i.e., the selection unit is an $ S_{1} $ family) and the rest for future breeding. Such designs, where the selection unit is a selfed family, are examined in Chapter 23.

## THEORY OF EXPECTED SINGLE-CYCLE RESPONSE

Response is typically given on a per-cycle, rather than per-generation, basis. A cycle begins with choosing the parents, P, to form the sib families and ends with the creation of offspring, y, formed by crossing members, R, from the recombination unit. The expected response is the difference in the means of these two populations (P vs. y). When comparing the efficiencies of different schemes, response per cycle should be converted to a response per generation (for discrete generations) or per unit time (for overlapping generations).

Our treatment of the theory of response starts by developing several equivalent modifications of the breeder's equation (Chapter 13) to accommodate family-based selection. To apply these expressions, we require the selection unit-offspring covariance, $ \sigma ( x,y) $ , and the variance of the selection unit, $ \sigma_{x}^{2} $ , for various family-based designs. The full development of these variances and covariances is straightforward but involves a fair amount of bookkeeping. The reader wishing to skip the details can find the results summarized below in Tables 21.3 and 21.4.

## Modifications of the Breeder's Equation for Predicting Family-based Response

Response is a function of how selection decisions based on the sib families $ ( x_{1} $ and $ x_{2} $ translate into selection on the corresponding parents $ (\mathcal{R}_{1} $ and $ \mathcal{R}_{2} $ ) of the offspring, y. Phrased in terms of breeding values, we predict response by using the sib information to predict the breeding values of the parents, $ \mathcal{R} $ , for the next generation. Under the infinitesimal model, the expected mean of the offspring equals the mean breeding value of the chosen parents (Chapters 6 and 13).

Making the standard assumption that all appropriate regressions are linear (which follows under the infinitesimal model assumptions; Chapters 6 and 24), the expected response is given by the general form of the breeder's equation (Equations 13.4a and 13.4b),

$$
R _ {y} = \frac {\sigma \left(x _ {m} , y\right)}{\sigma_ {x _ {m}} ^ {2}} S _ {x _ {m}} + \frac {\sigma \left(x _ {f} , y\right)}{\sigma_ {x _ {f}} ^ {2}} S _ {x _ {f}}
$$

Here $ x_{m} $ and $ x_{f} $ correspond to individuals from the selection units associated with the male (sire/pollen) and female (dam/seed) parents $ (\mathcal{R}_{m} $ and $ \mathcal{R}_{f} $ ) of the offspring, y. Equation 21.1a allows the male and female parents to be chosen by completely different schemes. For example, sib selection could be used on males and individual selection on females when selecting for a female-limited character (Example 13.5). The selection unit-offspring covariance, $ \sigma(x,y) $ , can be directly computed from the pedigree connecting P, a sib in x, and $ \mathcal{R} $ through the use of path analysis (LW Appendix 2). The path (or correlation) between selection on the unit, $ x_{f} $ , through the female parent, $ \mathcal{R}_{f} $ , and its offspring, y, is

$$
x _ {f} \leftarrow P \rightarrow \mathcal {R} _ {f} \rightarrow y
$$

Because the path connecting $ x_{f} $ and y is through $ \mathcal{R}_{f} $ , we often write $ \sigma(x,y|\mathcal{R}_{f}) $ in place of $ \sigma(x_{f},y) $ to remind the reader of this fact. Path(s) connecting $ x_{m} $ and y through $ \mathcal{R}_{m} $ are similarly defined. If P consists of multiple relatives, each path connecting $ x_{i} $ and $ \mathcal{R}_{i} $ (and hence y) needs to be counted. For example, if $ x_{i} $ and $ \mathcal{R}_{i} $ are full-sibs, we must compute the paths through each of the common parents (e.g., Figure 21.3D). If the selection unit-offspring covariances are the same for both parents, Equation 21.1a simplifies to

$$
R _ {y} = \frac {\sigma (x , y)}{\sigma_ {x} ^ {2}} S _ {x}
$$

where $ S_{x}=\left(S_{x_{m}}+S_{x_{f}}\right)/2 $ is the average selection differential on the unit(s) leading to the parents and

$$
\sigma (x, y) = \sigma (x, y \mid \mathcal {R} _ {f}) + \sigma (x, y \mid \mathcal {R} _ {m}) = 2 \sigma (x, y \mid \mathcal {R})
$$

is the covariance between the value of selection unit, x, and the offspring, y, counting the paths through both parents $ \left( \mathcal{R}_{m} \right. $ and $ \mathcal{R}_{f} $ ). When covariances are equal, this is twice the single parent-covariance, $ \sigma \left( x,y \mid \mathcal{R}_{1} \right) $ . By analogy with the breeder's equation, Equation 21.1b is often written as

$$
R _ {y} = h _ {x, y} ^ {2} S _ {x}
$$

where the generalized heritability of y given x,

$$
h _ {x, y} ^ {2} = \frac {\sigma (x , y)}{\sigma_ {x} ^ {2}} = 2 \left[ \frac {\sigma (x , y \mid \mathcal {R})}{\sigma_ {x} ^ {2}} \right]
$$

is twice the slope of the regression of y on x (LW Chapter 3). Just as the individual heritability, $ h^{2} $ , is the accuracy in using an individual's phenotypic value to predict the breeding value (Chapter 13), the generalized heritability is the accuracy of using the sib data, x, to predict the breeding value of $ \mathcal{R} $ .

Example 21.2. Consider family selection, wherein the selection unit is the family mean, $ \overline{{z}}_{i} $ and the recombination units are measured sibs (those whose trait values have been scored) from this family. Assuming the covariance between the sib mean and an individual sib is independent of sex, Equations 21.1b and 21.1c yield a response of

$$
R _ {b} = \frac {2 \sigma \left(\bar {z} _ {i} , y \mid \mathcal {R} _ {i}\right)}{\sigma^ {2} \left(\bar {z} _ {i}\right)} S _ {b}
$$

Recall (Equation 21.1c) that the numerator is twice the covariance between the value of the family mean, $ \overline{{z}}_{i} $ , and the offspring, y, from a parent chosen from this family, $ \mathcal{R}_{i} $ , which (in this case) is one of the measured sibs. The preceding expression can be more compactly written as $ R_{b}=h_{b}^{2} S_{b} $ , where the among-family heritability is

$$
h _ {b} ^ {2} = \frac {2 \sigma \left(\bar {z} _ {i} , y \mid \mathcal {R} _ {i}\right)}{\sigma^ {2} \left(\bar {z} _ {i}\right)}
$$

We used the notation $ R_{b} $ and $ h_{b}^{2} $ for "between family" in keeping with the literature (although this is formally among families, as it generally involves more than two families). Similarly, for selection on within-family deviations, the value of the selection unit is $ z_{ij}-\overline{z}_{i} $ , which yields

$$
R _ {F D} = \frac {2 \sigma \left(z _ {i j} - \bar {z} _ {i} , y \mid \mathcal {R} _ {i}\right)}{\sigma^ {2} \left(z _ {i j} - \bar {z} _ {i}\right)} S _ {F D}
$$

where $ \mathcal{R}_{i}=x_{ij} $ . Response can also be expressed in terms of the family-deviations heritability, with $ R_{FD}=h_{FD}^{2} S_{FD} $ , where

$$
h _ {F D} ^ {2} = \frac {2 \sigma \left(z _ {i j} - \bar {z} _ {i} , y \mid \mathcal {R} _ {i}\right)}{\sigma^ {2} \left(z _ {i j} - \bar {z} _ {i}\right)}
$$

Tables 21.3 and 21.4 (below) give expressions for these variances and covariances.

Other (equivalent) versions of Equations 21.1a and 21.2a appear in the literature. The selection-intensity version allows for standardized comparisons of different selection schemes. Defining the selection intensity on x by $ \bar{\iota}_{x}=S_{x} / \sigma_{x} $ , Equation 21.1a becomes

$$
R _ {y} = \frac {\sigma \left(x _ {m} , y\right)}{\sigma_ {x _ {m}}} \bar {\iota} _ {x _ {m}} + \frac {\sigma \left(x _ {f} , y\right)}{\sigma_ {x _ {f}}} \bar {\iota} _ {x _ {f}}
$$

If the regressions are the same for both parents,

$$
R _ {y} = \frac {\sigma (x , y)}{\sigma_ {x}} \bar {\iota} _ {x}
$$

where $ \bar{i}_{x}=(\bar{i}_{x_{m}}+\bar{i}_{x_{f}})/2 $ is the average selection intensity. This expression is frequently written in terms of the selection unit-offspring correlation, $ \rho(x,y), $

$$
R _ {y} = \sigma_ {z} \bar {\iota} _ {x} \rho (x, y)
$$

where (counting both parents) $ \rho(x,y)=2\rho(x,y|\mathcal{R}) $ . Equation 21.4a follows immediately from Equation 21.3b by recalling that $ \rho(x,y)=\sigma(x,y)/(\sigma_{x}\sigma_{y}) $ and that the trait variance in the offspring, y, is simply the phenotypic variance of the character $ (\sigma_{y}^{2}=\sigma_{z}^{2}) $ . A variant of Equation 21.4a commonly seen in the literature is

$$
R _ {y} = \sigma_ {A} \bar {\iota} _ {x} \rho (x, A _ {\mathcal {R}})
$$

where $ \rho(x,A_{\mathcal{R}}) $ , the correlation between the value of the selection unit, x, and the breeding value of a parent, $ \mathcal{R} $ , of y, is the accuracy of selection (Equation 13.11a). Equation 21.4b holds in the absence of epistasis, while Equations 21.1-21.3 hold for arbitrary epistasis. Recall that the accuracy of individual selection (the correlation between an individual's phenotypic and breeding values) is $ \rho(z_{\mathcal{R}},A_{\mathcal{R}})=h $ . A particular family-based approach is favored over individual selection if x is a more accurate predictor of the breeding value of $ \mathcal{R} $ than is $ \mathcal{R} $ 's phenotypic value, that is when $ \rho(x,A_{\mathcal{R}})>h. $

Equation 21.4b follows by first recalling that the mean value of an offspring is the average of its parental breeding values, $ y=\mu+(A_{\mathcal{R}_{m}}/2)+(A_{\mathcal{R}_{f}}/2)+e_{y} $ . Hence,

$$
\sigma (x, y) = \frac {1}{2} \sigma \left(x, A _ {\mathcal {R} _ {m}}\right) + \frac {1}{2} \sigma \left(x, A _ {\mathcal {R} _ {f}}\right) + \sigma \left(x, e _ {y}\right)
$$

In the absence of epistasis, inbreeding, and shared environmental effects, $ \sigma(x,e)=0 $ . If the regression is the same for both sexes, then $ \sigma(x,y)=\sigma(x_{1},A_{\mathcal{R}_{1}}). $ Recalling that $ \sigma_{y}=\sigma_{z}, $

$$
\rho (x, y) = \frac {\sigma (x , y)}{\sigma_ {x} \sigma_ {z}} = \left(\frac {\sigma_ {A}}{\sigma_ {z}}\right) \frac {\sigma \left(x _ {1} , A _ {\mathcal {R} _ {1}}\right)}{\sigma_ {x} \sigma_ {A}} = h \rho (x, A _ {\mathcal {R}})
$$

(A) $ x_{1} $ and $ \mathcal{R}_{1} $ are half-sibs

![](page=11,bbox=[343, 126, 768, 758])

<div align="center">

Figure 21.3 Derivation of the coefficient of coancestry, $ \Theta $ , values in Table 21.2, showing pedigrees (left) and associated path diagrams (right) for computing $ \Theta $ between a measured sib, $ x_{1} $ and an offspring, y, from the parent, $ \mathcal{R}_{1} $ . $ P_{1} $ to $ P_{5} $ are assumed to be unrelated and noninbred. A: $ x_{1} $ and $ \mathcal{R}_{1} $ are half-sibs. The product of the path coefficients yields $ \Theta_{x_{1} y}=(1/2)^{4}=1/16 $ . B: $ x_{1} $ and y are half-sibs, with $ \Theta_{x_{1} y}=(1/2)^{3}=1/8 $ . C: $ \mathcal{R}_{1} $ is a selfed progeny from the common parent, $ P_{1} $ . There are two separate paths between $ x_{1} $ and y (two different routes through $ P_{1} $ ), yielding $ \Theta_{x_{1} y}=2\cdot(1/2)^{4}=1/8 $ . D: $ x_{1} $ and $ \mathcal{R}_{1} $ are full-sibs. Again there are two paths between $ x_{1} $ and y (one through each parent), each being $ (1/2)^{4} $ , giving a total of $ \Theta_{x_{1} y}=2\cdot(1/2)^{4}=1/8. $

</div>

<div align="center">

Table 21.2 Coefficients of coancestry, $ \Theta $ , between an offspring, y (of parent $ \mathcal{R}_{1} $ ), and a member of the selection unit, $ x_{1} $ . Genetic covariances, $ \sigma_{G}(x_{1},y) $ , are computed with the assumption of no epistasis. Derviations are given in Figure 21.3.

</div>

<table border="1"><tr><td>Relationship between $x_{1}$ and $R_{1}$</td><td>$\Theta_{x_{1}y}$</td><td>$\sigma_{G}(x_{1},y)=2\Theta_{x_{1}y}\sigma_{A}^{2}$</td></tr><tr><td>$x_{1}=R_{1}$ (the sib is also the parent of y)</td><td>1/4</td><td>$\sigma_{A}^{2}/2$</td></tr><tr><td>$x_{1}$ and $R_{1}$ are half-sibs (Figure 21.3A)</td><td>1/16</td><td>$\sigma_{A}^{2}/8$</td></tr><tr><td>$x_{1}$ and $R_{1}$ are full-sibs (Figure 21.3D)</td><td>1/8</td><td>$\sigma_{A}^{2}/4$</td></tr><tr><td>$R_{1}$ is the parent of both $x_{1}$ and y (Figure 21.3B)</td><td>1/8</td><td>$\sigma_{A}^{2}/4$</td></tr><tr><td>$R_{1}$ is an $S_{1}$ offspring of the parent of $x_{1}$ (Figure 21.3C)</td><td>1/8</td><td>$\sigma_{A}^{2}/4$</td></tr></table>

Substitution into Equation 21.4a recovers Equation 21.4b (as $ \sigma_{z} h=\sigma_{z}\left(\sigma_{A} / \sigma_{z}\right)=\sigma_{A} $). Equations 21.1-21.4 provide equivalent expressions for computing the expected selection response. To apply these expressions to a particular selection scheme, we need to compute the selection unit-offspring covariance, $ \sigma(x,y) $ , and the variance of the selection unit, $ \sigma_{x}^{2}. $

## The Selection Unit-offspring Covariance, $ \sigma (x,y) $

Recall that the genetic covariance between two (noninbred) relatives is a function of their coefficients of coancestry, $ \Theta $ , and fraternity, $ \Delta $ , (LW Chapter 7). If we ignore epistasis (for now), the genetic covariance between a particular sib, $ x_{i} $ , and $ y $ is $ \sigma_{G}(x_{i},y)=2\Theta_{x_{i}y}\sigma_{A}^{2}+\Delta_{x_{i}y}\sigma_{D}^{2} $ (LW Equation 7.12). In the absence of inbreeding in $ y $ (the parents $ \mathcal{R}_{1} $ and $ \mathcal{R}_{2} $ are from different, unrelated families; $ \Theta_{\mathcal{R}_{1},\mathcal{R}_{2}}=0 $ $ \Delta_{xy} $ is zero. Note that $ \Delta=0 $ even when $ \mathcal{R}_{1} $ and/or $ \mathcal{R}_{2} $ are themselves inbred, provided that they are unrelated. For dominance effects to be shared by relatives, there must be paths wherein both alleles from an individual, $ x $ , in the selection unit are passed onto the offspring, $ y $ , which cannot occur if the parents of $ y $ $ (\mathcal{R}_{1} $ and $ \mathcal{R}_{2} $ ) are unrelated.

The coefficient of coancestry between $ x_{1} $ and y depends upon the relationship between $ \mathcal{R}_{1} $ and $ x_{1} $ . The designs covered in Table 21.1 involve four different relationships (Figure 21.2): (i) $ x_{1}=\mathcal{R}_{1} $ (a measured sib is a parent of y), (ii) $ x_{1} $ and $ \mathcal{R}_{1} $ are sibs, (iii) $ \mathcal{R}_{1}=P_{1} $ (the parent of $ x_{1} $ ), and (iv) $ \mathcal{R}_{1} $ is the selfed-progeny of the parent of $ x_{1} $ . The path diagrams for computing $ \Theta_{x_{1} y} $ for these four relationships are given in Figure 21.3, and Table 21.2 summarizes the resulting genetic covariances. The parents, $ P_{i} $ , are assumed to be non-inbred (i.e., $ \Theta_{P_{i} P_{i}}=1/2 $ ). If they are inbred, then $ \Theta_{P_{i} P_{i}}=(1+f_{i})/2 $ , where i is the inbreeding coefficient on that parent, and the expressions in Table 21.2 are multiplied by this additional factor (for each inbred parent).

As an example of how the coefficients of coancestry given in Table 21.2 are used consider family selection. Ignoring epistasis,

$$
\begin{array}{l} \sigma \left(\bar {z} _ {i}, y \mid \mathcal {R} _ {1} = x _ {i j}\right) = \frac {1}{n} \sum_ {k} \sigma \left(z _ {i k}, y \mid \mathcal {R} _ {1} = x _ {i j}\right) = \frac {1}{n} \sigma \left(z _ {i j}, y\right) + \left(1 - \frac {1}{n}\right) \sigma \left(z _ {i k}, y\right) \\ = \sigma_ {A} ^ {2} \left[ \frac {1 / 2}{n} + \left(1 - \frac {1}{n}\right) 2 \Theta_ {z _ {i k} y} \right] \tag {2} \\ \end{array}
$$

This follows because the first covariance, $ \sigma(z_{ij},y) $ , is for parent and offspring $ (\sigma_{A}^{2}/2) $ , while the second covariance, $ \sigma(z_{ik},y) $ , follows using the appropriate value of 2 $ \Theta $ from Table 21.2 (1/8 for half-sibs and 1/4 for full-sibs). Using the results from Table 21.2, expressions for the sib selection, parental selection (progeny testing), and $ S_{1} $ seed designs follow in similar fashion. These are summarized in Table 21.3.

In much of the animal-breeding literature, Wright's coefficient of relationship, $ r $ is used in place of $ 2\Theta $ . Assuming no inbreeding, $ r=1/4 $ for half-sibs and 1/2 for full-sibs.

<div align="center">

Table 21.3 Summary of the covariances between the selection unit and one parent $ \left( \mathcal{R}_{1} \right) $ from the recombination unit. As given by Equation 21.6b, $ r_{n}=r+(1-r)/n $ , where (for non-inbred sibs), $ r=1/2 $ and $ 1/4 $ , for full-sibs and half-sibs, respectively.

</div>

## Among-family Selection:

Family selection ( $ \mathcal{R}_{1} $ is a measured sib from family i)

$$
\sigma \left(\bar {z} _ {i}, y \mid \mathcal {R} _ {1}\right) = r _ {n} \left(\sigma_ {A} ^ {2} / 2\right) = \left\{ \begin{array}{l l} (1 + 3 / n) \left(\sigma_ {A} ^ {2} / 8\right) & \mathrm {h a l f - s i b s} \\ (1 + 1 / n) \left(\sigma_ {A} ^ {2} / 4\right) & \mathrm {f u l l - s i b s} \end{array} \right.
$$

Sib selection / Remnant seed ( $ \mathcal{R}_{1} $ is an unmeasured sib from family i )

$$
\sigma \left(\bar {z} _ {i}, y \mid \mathcal {R} _ {1}\right) = r \left(\sigma_ {A} ^ {2} / 2\right) = \left\{ \begin{array}{l l} \sigma_ {A} ^ {2} / 8 & \mathrm {h a l f - s i b s} \\ \sigma_ {A} ^ {2} / 4 & \mathrm {f u l l - s i b s} \end{array} \right.
$$

Parental selection / Progeny testing ( $ \mathcal{R}_{1} $ is a parent of the measured sibs)

$$
\sigma \left(\bar {z} _ {i}, y \mid \mathcal {R} _ {1}\right) = \sigma_ {A} ^ {2} / 4
$$

$ \mathbf{S}_{1} $ seed design $ (\mathcal{R}_{1} $ is a selfed progeny of a parent of the measured sibs)

$$
\sigma \left(\bar {z} _ {i}, y \mid \mathcal {R} _ {1}\right) = \sigma_ {A} ^ {2} / 4
$$

## Within-family Selection:

Selection on family deviations (FD)

$$
\sigma \left(z _ {i j} - \bar {z} _ {i}, y \mid \mathcal {R} _ {1}\right) = \left(1 - r _ {n}\right) \left(\sigma_ {A} ^ {2} / 2\right) = \left\{ \begin{array}{l l} \left(1 - 1 / n\right) \left(3 / 8\right) \sigma_ {A} ^ {2} & \mathrm {h a l f - s i b s} \\ \left(1 - 1 / n\right) \left(\sigma_ {A} ^ {2} / 4\right) & \mathrm {f u l l - s i b s} \end{array} \right.
$$

Strict within-family selection (FW)

$$
\sigma \left(z _ {i j} - \mu_ {i}, y \mid \mathcal {R} _ {1}\right) = (1 - r) \left(\sigma_ {A} ^ {2} / 2\right) = \left\{ \begin{array}{l l} (3 / 8) \sigma_ {A} ^ {2} & \mathrm {h a l f - s i b s} \\ \sigma_ {A} ^ {2} / 4 & \mathrm {f u l l - s i b s} \end{array} \right.
$$

Using Wright's coefficient, Equation 21.6a simplifies to

$$
\sigma \left(\bar {z} _ {i}, y \mid \mathcal {R} _ {1} = x _ {i j}\right) = r _ {n} \frac {\sigma_ {A} ^ {2}}{2} \quad \mathrm {w h e r e} \quad r _ {n} = r + \frac {1 - r}{n}
$$

Considering the paths through both parents $ (\mathcal{R}_{1} $ and $ \mathcal{R}_{2} $ ) of y,

$$
\sigma \left(\bar {z} _ {i}, y\right) = 2 \sigma \left(\bar {z} _ {i}, y \mid \mathcal {R} _ {1}\right) = r _ {n} \sigma_ {A} ^ {2}
$$

Likewise, the covariance between an individual's family deviation and its offspring's phenotypic value is

$$
\sigma \left(z _ {i j} - \bar {z} _ {i}, y \mid \mathcal {R} _ {1} = x _ {i j}\right) = \sigma \left(z _ {i j}, y \mid \mathcal {R} _ {1}\right) - \sigma \left(\bar {z} _ {i}, y \mid \mathcal {R} _ {1}\right) = \left(1 - r _ {n}\right) \frac {\sigma_ {A} ^ {2}}{2}
$$

which follows because $ \sigma( z_{ij}, y \mid \mathcal{R}_{1} ) $ is the parent-offspring covariance, $ \sigma_{A}^{2}/2 $ . Doubling the single-parent contribution yields a total contribution (considering both parents of y) of

$$
\sigma \left(z _ {i j} - \bar {z} _ {i}, y\right) = \left(1 - r _ {n}\right) \sigma_ {A} ^ {2}
$$

The covariance for strict within-family (WF) selection is slightly different (with $ r $ replacing $ r_{n} $ ; see Table 21.3), as the appropriate covariance here is $ \sigma \left( z_{ij}-\mu_{i}, y \right) $ , with $ \mu_{i} $ in place of $ \overline{z}_{i} $ The rankings of individuals under WF selection is simply their ranking within each family,

while their ranking under FD selection further depends on how much an individual actually deviates from its family mean. Thus, the top-ranked individuals in two families are always chosen under WF selection, but may not be chosen under FD selection. As a consequence, FD selection is influenced by the observed family mean, $ \bar{z}_{i} $ , while WF selection is a function of the true mean, $ \mu_{i} $ (Dempfle 1975, 1990; Hill et al. 1996).

A few simple rules emerge from Table 21.3. The number, n, of measured sibs only influences the covariance for family selection and family-deviations selection. Even in these cases, its effect is small unless the number of sibs is small. Under sib selection (and family selection ignoring terms of order 1/n), the selection unit-offspring covariance contributed through one parent $ \left( \mathcal{R}_{i}\right) $ is $ \sigma_{A}^{2}/8 $ when the selection unit consists of half-sibs and $ \sigma_{A}^{2}/4 $ when the selection unit consists of full-sibs. For parental selection and $ S_{1} $ seed designs, this covariance is $ \sigma_{A}^{2}/4 $ (independent of whether full-sibs or half-sibs are used in the selection unit). The covariance under WF selection (and FD selection when ignoring terms of order 1/n) is $ 3\sigma_{A}^{2}/8 $ for half-sibs and $ \sigma_{A}^{2}/4 $ for full-sibs.

## Variance of the Selection Unit, $ \sigma_{x}^{2} $

The variance, $ \sigma_{x}^{2} $ of the selection unit is a function of the within- and among-family variances, and obtaining it requires a bit of bookkeeping. We start by assuming that the total environmental value can be partitioned as $ E=E_{c}+E_{s} $ , a common-family effect $ (E_{c}) $ plus an individual-specific effect $ (E_{s}) $ . This decomposes the total environmental variances into among- and within-family components, $ \sigma_{E}^{2}=\sigma_{E_{c}}^{2}+\sigma_{E_{s}}^{2} $ . When families are replicated over plots and environments, the environmental variance contains additional structure and is usually partitioned into further components (Equations 21.41 and 21.42).

The among-family variance $ \sigma_{b}^{2} $ (the variance among the expected family means, $ \mu_{i} $ )

$$
\sigma_ {b} ^ {2} = \sigma^ {2} \left(\mu_ {i}\right) = \sigma_ {G F} ^ {2} + \sigma_ {E c} ^ {2}
$$

where $ \sigma_{GF}^{2} $ , the among-family genetic variance (the variance in the expected mean genotypic value among families), is developed below (Equations 21.11a and 21.26a). Likewise, the within-family variance about the expected family mean is

$$
\sigma_ {w} ^ {2} = \sigma^ {2} \left(z _ {i j} - \mu_ {i}\right) = \sigma_ {G w} ^ {2} + \sigma_ {E s} ^ {2}
$$

where $ \sigma_{G w}^{2} $ is the within-family genetic variance (Equations 21.11b and 21.26b). Note that $ \sigma_{b}^{2} $ and $ \sigma_{w}^{2} $ are functions of the true family mean, $ \mu_{i} $ , while the variance of the selection unit usually relies upon the variances about the observed mean, $ \overline{z}_{i} $ , of each family. Replacing $ \mu_{i} $ with $ \overline{z}_{i} $ results in a slight inflation of the among-family variance and a slight reduction in the within-family variance (this is formally shown below in Example 21.3). With n sibs in each family, the among-family variance based on the observed means becomes

$$
\sigma^ {2} \left(\bar {z} _ {i}\right) = \sigma^ {2} \left(\mu_ {i} + \bar {e} _ {i}\right) = \sigma_ {b} ^ {2} + \sigma_ {w} ^ {2} / n
$$

namely, the among-family variance, $ \sigma^{2}(\mu_{i})=\sigma_{b}^{2} $ , plus the variance, $ \sigma^{2}(\bar{e}_{i})=\sigma_{w}^{2}/n $ , in the error from estimating $ \mu_{i} $ from $ \bar{z}_{i} $ . Because the total variance is the sum of the among- and within-family variances $ (\sigma_{b}^{2}+\sigma_{w}^{2}) $ , the within-family variance (about the observed, rather than expected, mean) is correspondingly reduced to

$$
\sigma^ {2} \left(z _ {i j} - \bar {z} _ {i}\right) = (1 - 1 / n) \sigma_ {w} ^ {2}
$$

Equation 21.8c thus implies

$$
\sigma^ {2} \left(\bar {z} _ {i}\right) = \sigma_ {G F} ^ {2} + \sigma_ {E _ {c}} ^ {2} + \frac {\sigma_ {G w} ^ {2} + \sigma_ {E _ {s}} ^ {2}}{n}
$$

In the animal-breeding literature, this equation is often more compactly written in terms of t, the phenotypic correlation between sibs (the intraclass correlation coefficient; see

<div align="center">

Table 21.4 Within- and among-family variances as functions of the genetic and environmental variance components. Epistasis is assumed to be absent and the environmental value is partitioned as $ E=E_{c}+E_{s} $ , a common-family value plus an individual-specific value; n is the number of measured sibs.

</div>

Half-sib among-family variance

$$
\sigma^ {2} \left(\bar {z} _ {H S}\right) = \frac {\sigma_ {A} ^ {2}}{4} + \frac {(3 / 4) \sigma_ {A} ^ {2} + \sigma_ {D} ^ {2} + \sigma_ {E _ {s}} ^ {2}}{n} + \sigma_ {E _ {c} (H S)} ^ {2}
$$

Full-sib among-family variance

$$
\sigma^ {2} \left(\bar {z} _ {F S}\right) = \frac {\sigma_ {A} ^ {2}}{2} + \frac {\sigma_ {D} ^ {2}}{4} + \frac {(1 / 2) \sigma_ {A} ^ {2} + (3 / 4) \sigma_ {D} ^ {2} + \sigma_ {E _ {s}} ^ {2}}{n} + \sigma_ {E _ {c} (F S)} ^ {2}
$$

Half-sib with nested full-sibs (nested sibs) among-family variance

( $ n_{f} $ females per male, $ n_{s} $ offspring per female, $ n=n_{f} n_{s} $ offspring per male)

$$
\sigma^ {2} \left(\bar {z} _ {H S (F S)}\right) = \frac {\sigma_ {A} ^ {2}}{4} \left(1 + \frac {1}{n _ {f}} + \frac {2}{n}\right) + \frac {\sigma_ {D} ^ {2}}{4 n _ {f}} \left(1 + \frac {3}{n _ {s}}\right) + \frac {\sigma_ {E _ {s}} ^ {2}}{n} + \frac {\sigma_ {E _ {c}} ^ {2} (F S)}{n _ {f}} + \sigma_ {E _ {c} (H S)} ^ {2}
$$

Half-sib within-family variance

$$
\sigma^ {2} \left(z _ {i j} - \bar {z} _ {i} \mid H S\right) = \left(1 - \frac {1}{n}\right) \left(\frac {3}{4} \sigma_ {A} ^ {2} + \sigma_ {D} ^ {2} + \sigma_ {E _ {s}} ^ {2}\right)
$$

Full-sib within-family variance

$$
\sigma^ {2} \left(z _ {i j} - \bar {z} _ {i} \mid F S\right) = \left(1 - \frac {1}{n}\right) \left(\frac {1}{2} \sigma_ {A} ^ {2} + \frac {3}{4} \sigma_ {D} ^ {2} + \sigma_ {E _ {s}} ^ {2}\right)
$$

LW Chapter 7). The phenotypic covariance between sibs can be expressed as $ t\sigma_{z}^{2}=\sigma_{b}^{2}=\sigma_{G F}^{2}+\sigma_{E_{c}}^{2} $ (Example 21.3), implying that

$$
\sigma^ {2} \left(\bar {z} _ {i}\right) = t _ {n} \sigma_ {z} ^ {2}
$$

where, akin to our use of $ r_{n} $ (Equation 21.6b),

$$
t _ {n} = t + \frac {1 - t}{n}.
$$

Likewise, the within-family variance (about the observed mean) is

$$
\sigma^ {2} \left(z _ {i j} - \bar {z} _ {i}\right) = \left(1 - \frac {1}{n}\right) \left(\sigma_ {G w} ^ {2} + \sigma_ {E _ {s}} ^ {2}\right)
$$

which is usually written as

$$
\sigma^ {2} \left(z _ {i j} - \bar {z} _ {i}\right) = \left(1 - t _ {n}\right) \sigma_ {z} ^ {2}
$$

Table 21.4 gives these family variances in terms of genetic and environmental variance components, which follow upon expressing the within- and among-family genetic variances in terms of additive and dominance variance components. Recalling from ANOVA theory that the among-group variance equals the within-group covariance (LW Chapter 18), the among-family component, $ \sigma_{GF}^{2} $ , equals the genetic covariances between sibs. If, for now, we ignore epistasis,

$$
\sigma_ {G F} ^ {2} = \left\{ \begin{array}{l l} \frac {1}{4} \sigma_ {A} ^ {2} & \mathrm {h a l f - s i b s} \\ \\ \frac {1}{2} \sigma_ {A} ^ {2} + \frac {1}{4} \sigma_ {D} ^ {2} & \mathrm {f u l l - s i b s} \end{array} \right.
$$

Because the total genetic variance $ (\sigma_{G}^{2}) $ equals the among-family genetic variance plus the within-family variance,

$$
\sigma_ {G w} ^ {2} = \sigma_ {G} ^ {2} - \sigma_ {G F} ^ {2} = \left\{ \begin{array}{l l} \frac {3}{4} \sigma_ {A} ^ {2} + \sigma_ {D} ^ {2} & \mathrm {h a l f - s i b s} \\ \\ \frac {1}{2} \sigma_ {A} ^ {2} + \frac {3}{4} \sigma_ {D} ^ {2} & \mathrm {f u l l - s i b s} \end{array} \right.
$$

Finally, under a nested-sib design (the North Carolina Design I of Comstock and Robinson 1948), one sex (typically a male or a pollen plant) is mated to each of $ n_{f} $ (unrelated) females (or seed parents), each of which produces $ n_{s} $ sibs, for a total of $ n=n_{f} n_{s} $ sibs per male. The expression in Table 21.4 for the among-family variance under the nested-sib design follows, with similar logic as in Example 21.3, and with

$$
\sigma^ {2} \left(\bar {z} _ {H S (F S)}\right) = \sigma_ {G F (H S)} ^ {2} + \frac {\sigma_ {G (f | m)} ^ {2}}{n _ {f}} + \frac {\sigma_ {G w (F S)} ^ {2}}{n _ {s} n _ {f}} + \frac {\sigma_ {E _ {s}} ^ {2}}{n} + \frac {\sigma_ {E _ {c}} ^ {2} (F S)}{n _ {f}} + \sigma_ {E _ {c} (H S)} ^ {2}
$$

where $ \sigma_{G(f|m)}^{2} $ the genetic variances of females nested within males, is

$$
\sigma_ {G (f | m)} ^ {2} = \sigma_ {G F (F S)} ^ {2} - \sigma_ {G F (H S)} ^ {2} = \frac {\sigma_ {A} ^ {2} + \sigma_ {D} ^ {2}}{4}
$$

When epistasis is present, Equation 21.26a (below) provides the appropriate additional genetic variance terms in $ \sigma_{G(f|m)}^{2} $ . The among-family variance under a nested design is bounded below by the half-sib variance $ (n_{f}=n $ and $ n_{s}=1) $ and above by the full-sib variance $ (n_{f}=1 $ and $ n_{s}=n) $ .

Example 21.3. To obtain the within- and among-family variances for families with n sibs, decompose the phenotypic value of the jth individual from family i as

$$
z _ {i j} = G _ {i j} + E _ {i j} = \mu + G F _ {i} + G w _ {i j} + E c _ {i} + E s _ {i j}
$$

where the genotypic value, $ G_{ij}=\mu+G F_{i}+G w_{ij} $ , has both a family genotypic effect, $ G F_{i} $ (the expected genotypic value of a random sib from that family), and a deviation, $ G w_{ij} $ the departure of jth individual's genotypic value from its family average. The environmental value is similarly decomposed, with $ E_{ij}=E c_{i}+E s_{ij} $ , an environmental effect, $ E c_{i} $ , common to family i, and a special environmental effect, $ E s_{ij} $ , unique to the jth individual from this family. Because $ G F_{i}+E c_{i}=b_{i} $ are the effects common to a family, the among-family variance becomes

$$
\sigma_ {b} ^ {2} = t \sigma_ {z} ^ {2} = \sigma_ {G F} ^ {2} + \sigma_ {E c} ^ {2}
$$

The equality $ \sigma_{b}^{2}=t\sigma_{z}^{2} $ follows from the ANOVA identity that the among-group variance equals the covariance among group members (LW Chapter 18).

Similarly, $ G w_{ij}+E s_{ij}=w_{ij} $ are the within-family effects, yielding a within-family variance (around the expected family mean) of

$$
\sigma_ {w} ^ {2} = (1 - t) \sigma_ {z} ^ {2} = \sigma_ {G w} ^ {2} + \sigma_ {E s} ^ {2}
$$

The equality $ \sigma_{w}^{2}=(1-t)\sigma_{z}^{2} $ again follows from ANOVA theory, as the total variance equals the among-group variances plus the within-group variances, $ \sigma_{z}^{2}=\sigma_{b}^{2}+\sigma_{w}^{2}=t\sigma_{z}^{2}+\sigma_{w}^{2}. $

Using these results, we can decompose the observed mean of a family of size n as

$$
\begin{array}{l} \bar {z} _ {i} = \frac {1}{n} \sum_ {j = 1} ^ {n} z _ {i j} = \frac {1}{n} \sum_ {j = 1} ^ {n} \left(\mu + G F _ {i} + G w _ {i j} + E c _ {i} + E s _ {i j}\right) \\ = \mu + G F _ {i} + E c _ {i} + \sum_ {j = 1} ^ {n} \frac {\left(G w _ {i j} + E s _ {i j}\right)}{n} \\ \end{array}
$$

Because they are deviations from the mean, $ E s_{ij} $ and $ G w_{ij} $ are uncorrelated with each other, yielding

$$
\begin{array}{l} \sigma^ {2} \left(\bar {z} _ {i}\right) = \left(\sigma_ {G F} ^ {2} + \sigma_ {E c} ^ {2}\right) + \frac {1}{n ^ {2}} \sum_ {j = 1} ^ {n} \left(\sigma_ {G w} ^ {2} + \sigma_ {E s} ^ {2}\right) = \sigma_ {b} ^ {2} + \frac {n \sigma_ {w} ^ {2}}{n ^ {2}} \\ = \left(t + \frac {1 - t}{n}\right) \sigma_ {z} ^ {2} = t _ {n} \sigma_ {z} ^ {2} \\ \end{array}
$$

which recovers Equation 21.9b.

Now consider the variance of the within-family deviations from the observed means. Recalling the expression for the variance of a sum (LW Equation 3.11a), we have

$$
\sigma^ {2} \left(z _ {i j} - \bar {z} _ {i}\right) = \sigma_ {z} ^ {2} + \sigma^ {2} \left(\bar {z} _ {i}\right) - 2 \sigma \left(z _ {i j}, \bar {z} _ {i}\right)
$$

To refine this further, first note (Equation 21.9b) that $ \sigma^{2}(\overline{{z}}_{i})=t_{n}\sigma_{z}^{2} $ , and that the covariance term simplifies to

$$
\sigma \left(z _ {i j}, \bar {z} _ {i}\right) = \frac {1}{n} \left[ \sigma \left(z _ {i j}, z _ {i j}\right) + \sum_ {k \neq j} ^ {n} \sigma \left(z _ {i j}, z _ {i k}\right) \right] = \frac {\sigma_ {z} ^ {2}}{n} + \frac {n - 1}{n} t \sigma_ {z} ^ {2} = t _ {n} \sigma_ {z} ^ {2}
$$

as $ \sigma \left(z_{ij}, z_{ik}\right)=t\sigma_{z}^{2} $ (for $ j\neq k $ ). Thus, the variance of within-family deviations reduces to

$$
\sigma^ {2} \left(z _ {i j} - \bar {z} _ {i}\right) = \sigma_ {z} ^ {2} + t _ {n} \sigma_ {z} ^ {2} - 2 t _ {n} \sigma_ {z} ^ {2} = \left(1 - t _ {n}\right) \sigma_ {z} ^ {2}
$$

which recovers Equation 21.10b.

## RESPONSE FOR PARTICULAR DESIGNS

The formal development of the response equations for any particular design follows from the generalized breeder's equation (Equations 21.1 through 21.4), using the appropriate selection-unit variance (Table 21.4) and selection unit-offspring covariance (Table 21.3). Results for a number of standard among- and within-family designs are developed below, with family-index selection examined at the end of the chapter.

## Overview of Among- and Within-family Response

The selection response for a particular family-based scheme depends on how the additive-genetic (breeding value) and total (phenotypic) variances are partitioned within and among families. When the number, n, of sibs per family is large (meaning that the observed mean will be very close to the true mean), these variances are partitioned as

Breeding values

$$
\begin{array}{c c} \mathrm {W i t h i - f a m i l y} & \mathrm {A m o n g - f a m i l y} \\ \hline (1 - r) \sigma_ {A} ^ {2} & r \sigma_ {A} ^ {2} \\ (1 - t) \sigma_ {z} ^ {2} & t \sigma_ {z} ^ {2} \end{array}
$$

Phenotypic values

where t and r are, respectively, the phenotypic and additive-genetic correlations between sibs （r=1/4 for noninbred half-sibs and 1/2 for noninbred full-sibs). When the number of measured sibs within each family is small, $ t_{n}=t+(1-t)/n $ replaces t, and $ r_{n} $ (similarly defined) replaces r. Because the response to selection depends on the ratio of the available additive-genetic variance to the phenotypic variance, the response, $ R_{b} $ , to among-family selection is of the form

$$
R _ {b} = \frac {r _ {n} \sigma_ {A} ^ {2}}{t _ {n} \sigma_ {z} ^ {2}} S = \sigma_ {A} \left(\frac {\sigma_ {A}}{\sigma_ {z}}\right) \left(\frac {r _ {n}}{\sqrt {t _ {n}}}\right) \left(\frac {S}{\sqrt {t _ {n}} \sigma_ {z}}\right) = \sigma_ {A} h \frac {r _ {n}}{\sqrt {t _ {n}}} \bar {i}
$$

Equation 21.13a is the exact expression for family selection and is due to Lush (1947). Expressions for the predicted selection response under other among-family designs (e.g., sib, parental, or $ S_{1} $ seed selection) are very similar (see below).

Similarly, the response to within-family selection is a function of the within-family additive-genetic and phenotypic variances, leading us to expect that the response will be in the form of

$$
R _ {F D} = \frac {\left(1 - r _ {n}\right) \sigma_ {A} ^ {2}}{\left(1 - t _ {n}\right) \sigma_ {z} ^ {2}} S = \sigma_ {A} h \frac {1 - r _ {n}}{\sqrt {1 - t _ {n}}} \bar {\iota}
$$

Indeed, this is the exact expression for selection on family deviations (FD), while the response under strict within-family (WF) selection is given by replacing $ r_{n} $ and $ t_{n} $ with r and t.

Equations 21.13a and 21.13b are the standard response equations that appear in much of the elementary animal-breeding literature, as the use of r and t allows these results to be presented in a very compact fashion. When the design is more complicated, such as when it involves the replication of families over environments or the use of nested-sib families, expressions are given in terms of variance components, as shown below.

## Among-family Selection

Here the selection unit is $ \bar{z} $ the mean of a half-, full-, or nested-sib family. The type of sib family, together with the relatives used to produce the next generation, specifies the particular among-family design (Table 21.1). Tables 21.3 and 21.4 and Equation 21.13a yields the selection response, $ R_{b} $ , to a single cycle of among-family selection as

$$
R _ {b} = \frac {\gamma}{\sqrt {t _ {n}}} \frac {\sigma_ {A}}{2} h \left(\bar {\iota} _ {x _ {m}} + \bar {\iota} _ {x _ {f}}\right) = \frac {\gamma}{\sigma (\bar {z})} \frac {\sigma_ {A} ^ {2}}{2} \left(\bar {\iota} _ {x _ {m}} + \bar {\iota} _ {x _ {f}}\right)
$$

The left equality holds when the sib families are not nested and the families are not replicated, while the rightmost expression is completely general (using $ \sigma^{2}(\overline{z}) $ in place of $ t_{n}\sigma_{z}^{2} $ The selection unit-offspring covariance is $ \gamma\sigma_{A}^{2}/2 $ , where

$$
\gamma = \left\{ \begin{array}{l l} r _ {n} = r + (1 - r) / n & \mathrm {f a m i l y s e l e c t i o n} \\ r & \mathrm {s i b s e l e c t i o n} \\ 1 / 2 & \mathrm {p a r e n t a l o r S _ {1} s e e d s e l e c t i o n} \end{array} \right.
$$

Recall that these different values arise because r is the genetic correlation among sibs (1/4 and 1/2, respectively, for half- and full-sibs), and that parental and $ S_{1} $ selection correspond to the case where $ r=1/2 $ . Under strict sib selection, no measured individual is a parent of the next generation and hence all the correlations between an individual in the selection unit and a parent of the next generation are the same (namely, $ r\sigma_{A}^{2} $ ). Under family selection, one of the n measured individual sibs is also the parent of the next generation, and hence has a genetic covariance of $ \sigma_{A}^{2}/2 $ , while the other n-1 individuals are sibs of this parent, each with a genetic covariance of $ r\sigma_{A}^{2}/2 $ with the offspring (a covariance of $ r\sigma_{A}^{2} $ between sibs times 1/2 for that between parent and offspring).

The variance of the selection unit, $ \sigma^{2}(\bar{z})=t_{n}\sigma_{z}^{2} $ , depends only on the types of sibs that are measured and is independent of the types of relatives used to form the next generation. The theory of expected response to among-family selection traces back to Lush's classic 1947 paper, and Equation 21.14a is a generalization of his results. Table 21.5 expresses the response in terms of variance components.

Several variants of Equation 21.14a appear in the literature. Noting that $ \sigma_{A} h=\sigma_{z} h^{2} $ the response can be expressed as

$$
R _ {b} = \frac {\gamma}{\sqrt {t _ {n}}} \sigma_ {z} h ^ {2} \bar {\iota}
$$

where $ \bar{\iota}=(\bar{\iota}_{x_{f}}+\bar{\iota}_{x_{m}})/2 $ . Similarly, the response can be expressed in terms of the among-

<div align="center">

Table 21.5 Variance-component expressions of the expected response to among-family selection schemes using outbred sibs. Here $ \bar{i}_{x_{m}} $ is the selection intensity on individuals in the selection unit used to choose the male parent of the offspring, y (similarly, $ \bar{i}_{x_{f}} $ for the female parent). The number, n, of measured sibs is assumed to be sufficiently large that terms of order 1/n can be ignored (i.e., $ r_{n}\simeq r $ and $ t_{n}\simeq t $ ). We also assume no epistasis and a simple structure, $ E=E_{c}+E_{s} $ , for environmental values. We allow the within-family common environmental factor $ (E_{c}) $ to vary over the type of family, with $ \sigma_{E_{c}(HS)}^{2} $ and $ \sigma_{E_{c}(FS)}^{2} $ , respectively, as the corresponding variances for half- and full-sib families.

</div>

<table border="1"><tr><td></td><td>Half-sibs</td><td>Full-sibs</td></tr><tr><td>Family or sib selection</td><td>$\frac{(\sigma_{A}^{2}/8)(\bar{\iota}_{x_{m}}+\bar{\iota}_{x_{f}})}{\sqrt{\sigma_{A}^{2}/4+\sigma_{E_{c}}^{2}(HS)}}$</td><td>$\frac{(\sigma_{A}^{2}/4)(\bar{\iota}_{x_{m}}+\bar{\iota}_{x_{f}})}{\sqrt{\sigma_{A}^{2}/2+\sigma_{D}^{2}/4+\sigma_{E_{c}}^{2}(FS)}}$</td></tr><tr><td>Parental or S1-seed selection</td><td>$\frac{(\sigma_{A}^{2}/4)(\bar{\iota}_{x_{m}}+\bar{\iota}_{x_{f}})}{\sqrt{\sigma_{A}^{2}/4+\sigma_{E_{c}}^{2}(HS)}}$</td><td>$\frac{(\sigma_{A}^{2}/4)(\bar{\iota}_{x_{m}}+\bar{\iota}_{x_{f}})}{\sqrt{\sigma_{A}^{2}/2+\sigma_{D}^{2}/4+\sigma_{E_{c}}^{2}(FS)}}$</td></tr></table>

family heritability, with

$$
R _ {b} = h _ {b, \gamma} ^ {2} S, \quad \text {w h e r e} \quad h _ {b, \gamma} ^ {2} = \frac {\gamma}{t _ {n}} h ^ {2}
$$

and with $ S = ( S_{f} + S_{m} ) / 2 $ being the average selection differential on the parents.

Turning now to particular among-family designs, we start with family selection. Here, measured sibs (either all or a random subset) from the chosen families form the parents for the next generation. To reduce the effects of inbreeding, crosses between sibs from the same family are typically avoided (Chapter 23 examines the response when sibs are crossed, resulting in offspring that are inbred). With family selection, Equation 21.14a becomes

$$
R _ {b} = \left\{ \begin{array}{l l} \frac {(1 + 3 / n)}{\sqrt {t _ {n} (H S)}} \frac {\sigma_ {A}}{8} h \left(\bar {\iota} _ {x _ {m}} + \bar {\iota} _ {x _ {f}}\right) & \text {h a l f - s i b s} \\ \frac {(1 + 1 / n)}{\sqrt {t _ {n} (F S)}} \frac {\sigma_ {A}}{4} h \left(\bar {\iota} _ {x _ {m}} + \bar {\iota} _ {x _ {f}}\right) & \text {f u l l - s i b s} \end{array} \right.
$$

as first obtained by Lush (1947). While full-sibs have twice as much usable among-family additive variance relative to half-sibs $ \sigma_{A}^{2}/2 $ vs. $ \sigma_{A}^{2}/4 $ , this advantage is reduced somewhat because half-sibs have a smaller among-family phenotypic variance, with $ t_{HS}/t_{FS}\leq 1. $ This inequality follows by recalling that $ \sigma^{2}(\overline{z})=t\sigma_{z}^{2} $ and noting that $ (t_{FS}-t_{HS})\sigma_{z}^{2}=\sigma^{2}(\overline{z}_{FS})-\sigma^{2}(\overline{z}_{HS}) $ , where

$$
\sigma^ {2} \left(\bar {z} _ {F S}\right) - \sigma^ {2} \left(\bar {z} _ {H S}\right) = \frac {\sigma_ {A} ^ {2} + \sigma_ {D} ^ {2}}{4} + \left(\sigma_ {E c (F S)} ^ {2} - \sigma_ {E c (H S)} ^ {2}\right)
$$

Given that full-sibs share a common mother (and hence potentially share maternal effects), we expect $ \sigma_{Ec(FS)}^{2}\geq\sigma_{Ec(HS)}^{2} $ and, hence $ \sigma^{2}(\overline{z}_{FS})>\sigma^{2}(\overline{z}_{HS}) $ . Assuming the same selection intensity, Equation 21.15c yields the ratio of response for full- to half-sib family selection as

$$
\frac {R _ {b} (F S)}{R _ {b} (H S)} = \left(\frac {1 + 1 / n}{1 + 3 / n}\right) \left(\frac {8 \sqrt {t _ {n} (H S)}}{4 \sqrt {t _ {n} (F S)}}\right) < 2 \sqrt {\frac {t _ {n} (H S)}{t _ {n} (F S)}} < 2
$$

with the last equality following from Equation 21.16a.

If the character can only be measured after reproduction, females (or seed parents) from the chosen families have already been fertilized, and hence selection has occurred on only one sex $ ( S_{m}=\bar{i}_{x_{m}}=0). $ Planting these seeds (or, in animals, examining the offspring from fertilized females) and evaluating the resulting families allows for half-sib selection (under

random pollination). Full-sib selection can also be accomplished, but each cycle takes an additional generation. Here seeds from open-pollinated selected females are grown and controlled crosses are made between the offspring from different seed parents to create full-sib families for the next cycle of selection.

Example 21.4. Clayton et al. (1957) examined family selection on abdominal bristle number in Drosophila melanogaster (LW Figure 14.1). Their estimated intraclass correlations for half- and full-sibs were 0.121 and 0.265, respectively, while the estimated additive variance and heritability were 5.59 and 0.52, respectively. Hence,

$$
t _ {H S} = 0. 1 2 1, \quad t _ {F S} = 0. 2 6 5, \quad \mathrm {a n d} \quad \sigma_ {A} h = \sqrt {5. 5 9 \cdot 0. 5 2} = 1. 7 0
$$

Clayton et al. performed selection in two different settings: (i) the top 2 of 10 half-sib families were saved; and (ii) the top four of 20 full-sib families were saved. The expected selection intensities under these two schemes were, respectively, $ \bar{\iota}_{HS}=\bar{\iota}_{(2,10)}=1.27 $ , and $ \bar{\iota}_{FS}=\bar{\iota}_{(4,20)}=1.33 $ (Equation 14.4b). The family sizes, n, used were 20 half-sibs and 12 fullsibs. Because of the laboratory mating design used by the authors, there was a 1 in 10 chance that the half-sibs are actually full-sibs, resulting in a slight inflation of r from 0.25 to 0.275 (= 0.25 $ \cdot $ [9/10] $ + $ 0.5 $ \cdot $ [1/10]). To summarize:

<table border="1"><tr><td></td><td>Half-sibs</td><td>Full-sibs</td></tr><tr><td>r</td><td>0.275</td><td>0.5</td></tr><tr><td>n</td><td>20</td><td>12</td></tr><tr><td>tn</td><td>0.165</td><td>0.326</td></tr><tr><td>rn</td><td>0.311</td><td>0.542</td></tr></table>

<div align="center">

Equation 21.13a gives an expected response to half-sib family selection of

</div>

$$
R _ {b} (H S) = \left(\sigma_ {A} h\right) \frac {r _ {n}}{\sqrt {t _ {n}}} \cdot \bar {\iota} _ {H S} = 1. 7 0 \frac {0 . 3 1 1}{\sqrt {0 . 1 6 5}} \cdot 1. 2 7 = 1. 6 7
$$

while the expected response to full-sib family selection is

$$
R _ {b} (F S) = 1. 7 0 \frac {0 . 5 4 2}{\sqrt {0 . 3 2 6}} \cdot 1. 3 3 = 2. 1 5
$$

Clayton et al. obtained slightly different estimated responses (1.33 and 2.02 for half- and fullsibs, respectively). This occurred because they used $ R=h_{b}^{2} S_{b} $ with $ S_{b}=\sigma_{b}\bar{\iota} $ computed by taking the observed among-family variance, $ \sigma_{b}^{2} $ (in place of the estimates $ \sigma_{A}^{2}, t $ and $ h^{2} $ ). The observed responses (averaged over the first five generations) were, respectively, 1.38 and 0.94 for up- and down-selected half-sibs, and 1.62 and 1.36 for up- and down-selected full-sibs. The authors noticed a fairly sizable reduction in the estimated additive variance during generations two through four, which (in addition to sampling error; Chapter 18) likely accounts for the discrepancy between observed and predicted response.

Under sib selection, unmeasured sibs from each chosen family are used to form the next generation. The most common response equation for sib selection in the literature, which is due to Robertson (1955a), is

$$
R _ {s i b} = \bar {\iota} \sigma_ {A} h \frac {n r}{\sqrt {n (1 + [ n - 1 ] t)}}
$$

where $ \bar{i} $ denotes the average selection intensity used to choose both parents. Equation 21.17 follows from Equation 21.15a because $ \gamma=r $ for sib selection and we use $ \sigma_{A} h $ in place of

$ \sigma_{z} h^{2} $ . The use of remnant seed is a variant of sib selection. Forming offspring for the next cycle of selection by randomly crossing plants grown from the remnant seeds of the selected families allows these offspring to be the product of selection on both sexes of parents, but at the cost of an extra generation.

Under parental selection (progeny testing), parents are chosen based on the performance of a trial set of their offspring. Historically (until it was replaced by BLUP selection), this was the approach used to select the top bulls for dairy production. Typically, half-sib families are used and selection is on only one sex. In this case, the expected response is

$$
R _ {p t} = \frac {\sigma_ {A} / 4}{\sqrt {t _ {n} (H S)}} h \bar {\iota}
$$

where $ \bar{i} $ is the intensity on the selected sex. In monoecious species, the expected response is double that given by Equation 21.18a if one uses the selected parents for both seed and pollen. The use of maternal half-sib families (as commonly occurs in plant breeding) is expected to inflate t(HS) relative to paternal half-sibs (and hence reduce response), as common-family environmental effects can be rather significant due to shared maternal effects.

If males (sires or pollen plants) are progeny tested using a nested-sib design, wherein each male is crossed to $ n_{f} $ (unrelated) females (dams or seed plants), each of which has $ n_{s} $ sibs, the among-family variance is given in Table 21.4, and the response becomes

$$
\begin{array}{l} R _ {p t} = \frac {h \bar {i} \sigma_ {A} ^ {2} / 4}{\sqrt {\sigma_ {G F (H S)} ^ {2} + \frac {\sigma_ {G (f | m)} ^ {2}}{n _ {f}} + \frac {\sigma_ {G w (F S)} ^ {2}}{n _ {f} n _ {s}} + \frac {\sigma_ {E _ {s}} ^ {2}}{n _ {f} n _ {s}} + \frac {\sigma_ {E _ {c} (F S)} ^ {2}}{n _ {f}} + \sigma_ {E _ {c} (H S)} ^ {2}}} \\ = \frac {h \bar {i} \sigma_ {A} ^ {2} / 4}{\sqrt {\frac {\sigma_ {A} ^ {2}}{4} \left(1 + \frac {1}{n _ {f}} + \frac {2}{n _ {f} n _ {s}}\right) + \frac {\sigma_ {D} ^ {2}}{4 n _ {f}} \left(1 + \frac {3}{n _ {s}}\right) + \frac {\sigma_ {E _ {s}} ^ {2}}{n _ {f} n _ {s}} + \frac {\sigma_ {E _ {c} (F S)} ^ {2}}{n _ {f}} + \sigma_ {E _ {c} (H S)} ^ {2}}} \\ \end{array}
$$

For progeny testing of females using a nested design, the roles of males and females are reversed in the above expression. Because $ \sigma^{2}(\overline{z}_{HS})\leq\sigma^{2}(\overline{z}_{HS(FS)})\leq\sigma^{2}(\overline{z}_{FS}) $ , the response using a nested progeny test is intermediate to that for schemes using half- or full-sibs. All these comments for parental selection equally apply to the $ S_{1} $ seed design, as the expected response is the same.

## Among-family Selection: Which Scheme Is Best?

Given the number of among-family selection designs, which scheme should be used? Biological and economic restriction may preclude the use of certain designs and make others more feasible. These logistical considerations aside, there are three issues that must be weighed: (i) cycle time versus selection on one or both sexes, (ii) performance evaluation using half- versus full-sib families (the value of $ t_{n} $ , and more generally, $ \sigma^{2}[\bar{z}]$ ), and (iii) choice of relatives for the recombination unit (the value of $ \gamma $ in Equation 21.14a). As mentioned above, a common reason for using a two-generation cycle (e.g., crossing plants grown from remnant seed from superior families) is the inability to select on both sexes. In such cases, the doubling of the cycle time is countered by selection on both sexes doubling the response per cycle, which yields the same expected rate of progress on a per-generation basis. In many cases, a multigenerational method is used because selection on other characters beside the primary one of interest is also performed during one (or both) generations of the cycle.

The second choice is the type of family comprising the selection unit. While the type of sibs changes the value of $ \gamma $ under family- and sib-selection, it does not influence $ \gamma $ under parental or $ S_{1} $ selection (Equation 21.14b). Indeed, for these last two designs, it is more efficient to use half-sib families, as (from Equation 21.14a) the ratio of response of a parental half-sib to a parental full-sib scheme is $ \sqrt{t(FS)/t(HS)}>1. $

Provided that the same type of families (half-, full-, or nested-sibs) are measured, choosing relatives that increase the recombination unit-offspring covariance (by increasing $ \gamma $ ) increases the expected response. For half-sib families, both parental and $ S_{1} $ selection yield twice the response per cycle as sib or family selection (assuming the same number of sexes are under selection in the comparison). With full-sibs, Table 21.5 shows that, given the same selection intensity, the response per cycle under all four methods (family, sib, parental, and $ S_{1} $ selection) is the same. While the response to selection using full-sib families is greater than that of family or sib selection using half-sibs, the use of full-sibs does not result in a doubling of the response (Equation 21.16b). This less-than-twofold increase in response per cycle using full-sibs is thus not sufficient to cover the cost of the extra generation that is often required to create full-sib families.

Once one has chosen a particular design, there is also the issue of allocation of the number of sibs (n) per each of the m families, given constraints on the total number of sibs, $ N=mn $ , measured over each cycle of selection. One increases the accuracy by increasing the number of sibs per family, but one does so by decreasing the selection intensity (for fixed N, increasing n decreases m, and hence $ \bar{\iota} $ ; see Example 21.1). Robertson (1957, 1960b), Rendel (1959), and Lindgren et al. (1997) examined this problem of optimal family size. To maximize response, the breeder usually has two fixed constraints: the total number of sibs, N, examined and the number, $ n_{p} $ , of families used to form the next generation. A low value of $ n_{p} $ increases inbreeding, and thus not only invites inbreeding depression, but also reduces the eventual long-term response (Chapter 26). For fixed $ n_{p} $ and N, the goal is to find the number of sibs, n, per family that maximizes response. Noting that $ \sigma_{z} h^{2} $ is fixed, while $ n_{p}=mp $ (with p being the fraction saved) and $ m=N/n $ , Equation 21.15a shows that the single-generation response is maximized by maximizing the quantity $ \gamma[\bar{\iota} (n_{p}, N/n) / \sqrt{t_{n}}] $ with respect to n. With the exception of family selection (where $ \gamma=r_{n} $ ), $ \gamma $ is a fixed constant with respect to n. Maximizing of the long-term response (or more generally, the expected response after k>1 generations) also needs to consider the differences in the effective populations sizes. This is examined in Chapter 26.

## Within-family Selection

Within-family selection chooses individuals based on their relative performance within families. Under family-deviations (FD) selection, individuals with the largest family deviations are chosen, independent of which family they come from. In contrast, strict within-family (WF) selection chooses the largest individuals from each family, independent of how much they actually deviate from their family means. Suppose that in family one the deviations for three measured sibs are 4,3, and -7, while the deviations in family two are 1,0, and -1. If we select the upper one-third, then under WF selection, the top individual from each family is chosen, while under FD selection, two individuals from family one and none from family two are chosen. The result of this rather subtle distinction is that FD selection is influenced by the observed mean, $ \bar{z}_{i} $ , while WF selection is not. Family deviations and strict within-family selection have been confused in the literature, and the correct expression for WF selection was provided by Dempfle (1975, 1990) and Hill et al. (1996). Because WF selection ensures an equal representation of families, while FD selection does not, WF selection has a larger effective population size (Equation 3.4), and hence an expected larger long-term response (Chapter 26).

Under family-deviations (FD) selection, the selection unit is the value of an individual's within-family deviation, $ z_{ij}-\overline{z}_{i} $ . Using the results from Tables 21.3 and 21.4, Equation 21.1a yields an expected response of

$$
\begin{array}{l} R _ {F D} = \frac {\sigma \left(z _ {i j} - \bar {z} _ {i} , y \mid \mathcal {R} _ {m}\right)}{\sigma \left(z _ {i j} - \bar {z} _ {i}\right)} \bar {\iota} _ {x _ {m}} + \frac {\sigma \left(z _ {i j} - \bar {z} _ {i} , y \mid \mathcal {R} _ {f}\right)}{\sigma \left(z _ {i j} - \bar {z} _ {i}\right)} \bar {\iota} _ {x _ {f}} \\ = \frac {1 - r _ {n}}{\sqrt {1 - t _ {n}}} \sigma_ {A} h \left(\frac {\bar {\iota} _ {x _ {m}} + \bar {\iota} _ {x _ {f}}}{2}\right) \\ \end{array}
$$

with the last equality following from $ \sigma_{A}^{2} / \sigma_{z}=\sigma_{A} h. $

Under strict within-family (WF) selection, individuals are chosen entirely on their rank within each family, resulting in the observed mean, $ \overline{z}_{i} $ , being replaced by the true (and unobserved) mean, $ \mu_{i} $ (Dempfle 1975, 1990; Hill et al. 1996). The response becomes

$$
\begin{array}{l} R _ {W F} = \frac {\sigma \left(z _ {i j} - \mu_ {i} , y \mid \mathcal {R} _ {m}\right)}{\sigma \left(z _ {i j} - \mu_ {i}\right)} \bar {\iota} _ {x _ {m}} + \frac {\sigma \left(z _ {i j} - \mu_ {i} , y \mid \mathcal {R} _ {f}\right)}{\sigma \left(z _ {i j} - \mu_ {i}\right)} \bar {\iota} _ {x _ {f}} \\ = \frac {1 - r}{\sqrt {1 - t}} \sigma_ {A} h \left(\frac {\bar {\iota} _ {x _ {m}} + \bar {\iota} _ {x _ {f}}}{2}\right) \\ \end{array}
$$

Noting that

$$
\frac {1 - r _ {n}}{\sqrt {1 - t _ {n}}} = \frac {(1 - 1 / n) (1 - r)}{\sqrt {(1 - 1 / n) (1 - t)}} = \frac {1 - r}{\sqrt {1 - t}} \sqrt {1 - \frac {1}{n}}
$$

it follows that

$$
R _ {F D} = R _ {W F} \frac {\bar {\iota} _ {F D}}{\bar {\iota} _ {W F}} \sqrt {1 - \frac {1}{n}}
$$

Thus, when the number of measured sibs in each family is modest to large (meaning that the selection intensities are essentially equal, $ \bar{\iota}_{FD}\simeq \bar{\iota}_{WF} $; see Example 24.1), the difference between the expected responses under WF versus FD selection is very small. For large values of n, Equation 21.20 yields a resulting response for strict within-family (WF) selection using half- and full-sib families of

$$
R _ {W F} = \left\{ \begin{array}{l l} \frac {(3 / 8) \sigma_ {A}}{\sqrt {1 - t (H S)}} h \left(\bar {\iota} _ {x _ {m}} + \bar {\iota} _ {x _ {f}}\right) & \text {h a l f - s i b s} \\ \frac {(1 / 4) \sigma_ {A}}{\sqrt {1 - t (F S)}} h \left(\bar {\iota} _ {x _ {m}} + \bar {\iota} _ {x _ {f}}\right) & \text {f u l l - s i b s} \end{array} \right.
$$

When expressed in terms of variance components,

$$
R _ {W F} = \left\{ \begin{array}{l l} \frac {(3 / 8) \sigma_ {A} ^ {2}}{\sqrt {(3 / 4) \sigma_ {A} ^ {2} + \sigma_ {D} ^ {2} + \sigma_ {E _ {s}} ^ {2}}} \left(\bar {\iota} _ {x _ {m}} + \bar {\iota} _ {x _ {f}}\right) & \mathrm {h a l f - s i b s} \\ \frac {(1 / 4) \sigma_ {A} ^ {2}}{\sqrt {\sigma_ {A} ^ {2} / 2 + (3 / 4) \sigma_ {D} ^ {2} + \sigma_ {E _ {s}} ^ {2}}} \left(\bar {\iota} _ {x _ {m}} + \bar {\iota} _ {x _ {f}}\right) & \mathrm {f u l l - s i b s} \end{array} \right.
$$

With their smaller amounts of among-family genetic variance, there is more usable withinfamily variance among half-sibs, namely, a within-family additive variance of $ ( 3/4)\sigma_{A}^{2} $ Only half of this variance is passed from parent to offspring, giving the $ ( 3/8)\sigma_{A}^{2} $ term in Equations 21.22a and 21.22b. For full-sibs, the within-family additive variance is $ ( 1/2)\sigma_{A}^{2} $ again only half of which is passed onto offspring, which results in the $ \sigma_{A}^{2}/4 $ term in these equations.

The within-family heritability, $ h_{w}^{2} $ is the same under both FD and WF within-family selection because

$$
\frac {1 - r _ {n}}{1 - t _ {n}} = \frac {(1 - 1 / n) (1 - r)}{(1 - 1 / n) (1 - t)} = \frac {(1 - r)}{(1 - t)}
$$

yielding

$$
h _ {w} ^ {2} = \frac {2 \sigma \left(z _ {i j} - \bar {z} _ {i} , y \mid \mathcal {R} _ {1}\right)}{\sigma^ {2} \left(z _ {i j} - \bar {z} _ {i}\right)} = \frac {\left(1 - r _ {n}\right) \sigma_ {A} ^ {2}}{\left(1 - t _ {n}\right) \sigma_ {z} ^ {2}} = \frac {(1 - r)}{(1 - t)} h ^ {2}
$$

that there is a full-sib family design, with 10 families of 20 sibs each, and that we perform strict within-family selection, with the upper 20% chosen from each family (the top 4 of the 20 measured sibs). Correcting for finite population size (Equation 14.4b), the expected selection intensity is $ \bar{\iota}_{(4,20)}=1.33 $ , and from Equation 21.20, the predicted response is

$$
R _ {W F} = \bar {\iota} \cdot \left(\sigma_ {A} h\right) \frac {1 - r}{\sqrt {1 - t}} = 1. 3 3 \cdot 1. 7 0 \frac {1 - 0 . 2 7 5}{\sqrt {1 - 0 . 1 2 1}} = 1. 7 5
$$

If we use within-family deviations (FD), selecting the uppermost 20% of all 200 individuals gives a corrected selection intensity of $ \bar{\iota}_{(40,200)}=1.39 $ , and Equation 21.19 returns a predicted response of

$$
R _ {F D} = \bar {\iota} \cdot \left(\sigma_ {A} h\right) \frac {1 - r _ {n}}{\sqrt {1 - t _ {n}}} = 1. 3 9 \cdot 1. 7 0 \frac {1 - 0 . 3 1 1}{\sqrt {1 - 0 . 1 6 5}} = 1. 7 8
$$

The selection intensity values used here can be further corrected to account for correlations among sibs, and we do so later in the chapter (Equation 21.57b).

## Realized Heritabilities

By analogy with individual selection, one can estimate the realized heritability (Chapter 18) associated with a particular family-based scheme from the ratio of observed response to selection differential, namely,

$$
\widehat {h} _ {r, x} ^ {2} = \frac {R _ {x}}{S _ {x}}
$$

Falconer and Latyszewski (1952) used this approach to estimate a realized within-family heritability for response to selection on body size in mice. These authors computed the standard error of this estimate by noting that

$$
\sigma^ {2} \left(\widehat {h} _ {r, w f} ^ {2}\right) = \sigma^ {2} \left(\frac {R _ {w f}}{S _ {w f}}\right) = \frac {\sigma^ {2} \left(R _ {w f}\right)}{S _ {w f} ^ {2}}
$$

Because the among- and within-family heritabilities can be expressed as a function of the individual heritability, $ h^{2} $ (Equations 21.15b and 21.23), we can similarly translate a realized heritability estimate for a particular family-based design into a realized individual heritability, $ \widehat{h}_{r}^{2} $ . With among-family selection,

$$
S
$$

$$
\widehat {h} _ {r} ^ {2} = \left(\frac {t _ {n}}{\gamma}\right) \widehat {h} _ {r, b} ^ {2}
$$

where $ \gamma $ is given by Equation 21.14b. For within-family selection, these two heritabilities are connected by

$$
\widehat {h} _ {r} ^ {2} = \left(\frac {1 - t}{1 - r}\right) \widehat {h} _ {r, w f} ^ {2}
$$

These expressions apply to a single generation of selection. Additional uncertainty is introduced into the estimate if the sib phenotypic correlation (t) is unknown and must itself be estimated. Equations 21.25a and 21.25b should be used with caution when multiple cycles of selection have occurred, as the sib additive-genetic correlation (r) increases in each successive generation due to inbreeding, which in turn changes the phenotypic correlation, t (Chapter 26).

## Accounting for Epistasis

The response to within- and among-family selection in the presence of epistasis was briefly examined by Nyquist (1991), and we expand upon his results here. As with individual selection, additive epistasis contributes to the initial response under family-based selection, but its contribution to the ultimate response rapidly decays over time as recombination breaks up favorable combinations of alleles at different loci (Chapter 15). We first consider the single-generation response and then briefly examine the transient dynamics.

Recalling that the among-group variance equals the within-group covariance (LW Chapter 18), the among-family genetic variance, $ \sigma_{GF}^{2} $ , with arbitrary epistasis immediately follows from the genetic covariance between sibs (LW Table 7.2),

$$
\sigma_ {G F} ^ {2} = \left\{ \begin{array}{l l} \frac {1}{4} \sigma_ {A} ^ {2} + \frac {1}{1 6} \sigma_ {A A} ^ {2} + \frac {1}{6 4} \sigma_ {A A A} ^ {2} + \dots & \mathrm {h a l f - s i b s} \\ \frac {1}{2} \sigma_ {A} ^ {2} + \frac {1}{4} \sigma_ {D} ^ {2} + \frac {1}{4} \sigma_ {A A} ^ {2} + \frac {1}{8} \sigma_ {A D} ^ {2} + \frac {1}{1 6} \sigma_ {D D} ^ {2} + \frac {1}{8} \sigma_ {A A A} ^ {2} + \dots & \mathrm {f u l l s i b s} \end{array} \right.
$$

Likewise, the within-family genetic variance, $ \sigma_{Gw}^{2}=\sigma_{G}^{2}-\sigma_{GF}^{2} $ ,becomes

$$
\sigma_ {G w} ^ {2} = \left\{ \begin{array}{l l} \frac {3}{4} \sigma_ {A} ^ {2} + \sigma_ {D} ^ {2} + \frac {1 5}{1 6} \sigma_ {A A} ^ {2} + \sigma_ {A D} ^ {2} + \sigma_ {D D} ^ {2} + \frac {6 3}{6 4} \sigma_ {A A A} ^ {2} + \dots & \mathrm {h a l f - s i b s} \\ \frac {1}{2} \sigma_ {A} ^ {2} + \frac {3}{4} \sigma_ {D} ^ {2} + \frac {3}{4} \sigma_ {A A} ^ {2} + \frac {7}{8} \sigma_ {A D} ^ {2} + \frac {1 5}{1 6} \sigma_ {D D} ^ {2} + \frac {7}{8} \sigma_ {A A A} ^ {2} + \dots & \mathrm {f u l l - s i b s} \end{array} \right.
$$

The among- and within-family variances, $ \sigma^{2} \left( \bar{z}_{i} \right) $ and $ \sigma^{2} \left( z_{ij}-\bar{z}_{i} \right) $ , immediately follow if we substitute Equations 21.26a and 21.26b into Equations 21.9a and 21.10a, respectively.

The genetic covariance between an individual (x) from the selection unit and the offspring (y) under epistasis follows if we use LW Equation 7.12,

$$
\sigma_ {G} (x, y) = \left(2 \Theta_ {x y}\right) \sigma_ {A} ^ {2} + \left(2 \Theta_ {x y}\right) ^ {2} \sigma_ {A A} ^ {2} + \dots = \sum_ {u = 1} \left(2 \Theta_ {x y}\right) ^ {u} \sigma_ {A ^ {u}} ^ {2}
$$

The previous expression assumed that $ \Delta_{xy}=0 $ , meaning that terms involving dominance are not included. Using the values of $ \Theta_{xy} $ from Table 21.2, the parent-offspring covariance is

$$
\sigma \left(\mathcal {R} _ {1}, y\right) = \frac {\sigma_ {A} ^ {2}}{2} + \frac {\sigma_ {A A} ^ {2}}{4} + \frac {\sigma_ {A A A} ^ {2}}{8} + \dots = \sum_ {u = 1} \left(\frac {1}{2 ^ {u}}\right) \sigma_ {A ^ {u}} ^ {2}
$$

Table 21.2 shows that $ \Theta_{xy}=1/16 $ and 1/8 when x is a half- or full-sib, respectively, of $ \mathcal{R}. $ Expressed in terms of Wright's coefficient of relationship, r,

$$
\sigma \left(x _ {1}, y \mid \mathcal {R} _ {1}\right) = (r / 2) \sigma_ {A} ^ {2} + (r / 2) ^ {2} \sigma_ {A A} ^ {2} + (r / 2) ^ {3} \sigma_ {A A A} ^ {2} + \dots = \sum_ {u = 1} \left(\frac {r}{2}\right) ^ {u} \sigma_ {A ^ {u}} ^ {2}
$$

Substituting Equation 21.27a and 21.27b into Equation 21.6a yields a covariance for family selection of

$$
\begin{array}{l} \sigma (\bar {z}, y \mid \mathcal {R} _ {1}) = \frac {1}{n} \sum_ {u = 1} \left(\frac {1}{2 ^ {u}}\right) \sigma_ {A ^ {u}} ^ {2} + \left(1 - \frac {1}{n}\right) \sum_ {u = 1} \left(\frac {r}{2}\right) ^ {u} \sigma_ {A ^ {u}} ^ {2} \\ = \sum_ {u = 1} \left(\frac {1}{2 ^ {u}}\right) r _ {n} ^ {u} \sigma_ {A ^ {u}} ^ {2} \\ \end{array}
$$

where $ r_{n}^{u}=r^{u}+(1-r^{u})/n $ . For a large family size, the coefficient for u-fold additive epistasis approaches $ r^{u}/2^{u} $ , which is the value under sib selection. Taking $ r=1/2 $ returns the coefficients for parental and $ S_{1} $ seed selection. Applying Equation 21.28, the single-parent covariance for half-sib family selection $ (r=1/4) $ becomes

$$
\sigma \left(\bar {z} _ {H S}, y \mid \mathcal {R} _ {1}\right) = \left(1 + \frac {3}{n}\right) \frac {\sigma_ {A} ^ {2}}{8} + \left(1 + \frac {1 5}{n}\right) \frac {\sigma_ {A A} ^ {2}}{6 4} + \left(1 + \frac {6 3}{n}\right) \frac {\sigma_ {A A A} ^ {2}}{5 1 2} + \dots
$$

Likewise, the single-parent covariance for full-sib family selection $ ( r=1/2) $ is

$$
\sigma \left(\bar {z} _ {F S}, y \mid \mathcal {R} _ {1}\right) = \left(1 + \frac {1}{n}\right) \frac {\sigma_ {A} ^ {2}}{4} + \left(1 + \frac {3}{n}\right) \frac {\sigma_ {A A} ^ {2}}{1 6} + \left(1 + \frac {7}{n}\right) \frac {\sigma_ {A A A} ^ {2}}{6 4} + \dots
$$

For sib-selection, $ \sigma(\bar{z}_{1}, y|\mathcal{R}_{1}) $ is directly provided by Equation 21.27b, and Equations 21.29a and 21.29b apply if terms of order 1/n are ignored. For among-family selection using parental selection or $ S_{1} $ seed, the covariance is the same as that for full-sibs under sib selection, namely, Equation 21.29b (as all three have the same value of $ \Theta_{xy} $ ).

The covariance for within-family deviations (again considering the contribution through a single parent of y) becomes

$$
\begin{array}{l} \sigma \left(z _ {i j} - \bar {z} _ {i}, y \mid \mathcal {R} _ {1}\right) = \sigma \left(\mathcal {R} _ {1}, y\right) - \sigma \left(\bar {z} _ {i}, y \mid \mathcal {R} _ {1}\right) \\ = \sum_ {u = 1} \left(\frac {1}{2}\right) ^ {u} \left(1 - r _ {n} ^ {u}\right) \sigma_ {A ^ {u}} ^ {2} \\ = \left(1 - \frac {1}{n}\right) \sum_ {u = 1} \left(\frac {1}{2}\right) ^ {u} \left(1 - r ^ {u}\right) \sigma_ {A ^ {u}} ^ {2} \\ \end{array}
$$

where we have used the identity $ ( 1-r_{n} )=( 1-1/n )( 1-r ). $ Ignoring the common $ ( 1-1/n ) $ factor found in all terms, for half-sibs we have

$$
\sigma \left(z _ {i j} - \bar {z} _ {H S}, y \mid \mathcal {R} _ {1}\right) = \left(\frac {3}{8}\right) \sigma_ {A} ^ {2} + \left(\frac {1 5}{6 4}\right) \sigma_ {A A} ^ {2} + \left(\frac {6 3}{5 1 2}\right) \sigma_ {A A A} ^ {2} + \dots
$$

while for full-sibs

$$
\sigma \left(z _ {i j} - \bar {z} _ {F S}, y \mid \mathcal {R} _ {1}\right) = \left(\frac {1}{4}\right) \sigma_ {A} ^ {2} + \left(\frac {3}{1 6}\right) \sigma_ {A A} ^ {2} + \left(\frac {7}{6 4}\right) \sigma_ {A A A} ^ {2} + \dots
$$

Equations 21.29 and 21.31 show that additive epistasis contributes to the short-term response. However, as with individual selection, this contribution is transient and decays over time as recombination breaks up linkage groups of favorable alleles (Chapter 15). For u-locus additive epistasis $ \sigma_{A^{u}}^{2} $ , the per-generation decay rate for unlinked loci is $ [1-(1/2)^{u-1}] $ , or one minus the probability that a parental gamete containing specific alleles at u unlinked loci will be passed onto an offspring. The probability that such a gamete remains unchanged after $ \tau $ generations is $ 2^{-\tau(u-1)} $ , which rapidly converges to zero. Thus, if $ R_{A^{u}} $ is the contribution due to u-locus additive epistasis, after $ \tau $ generations, the contribution from a single generation of selection becomes $ 2^{-\tau(u-1)}R_{A^{u}}. $

## Response with Autotetraploids

Recall from Chapter 15 that selection response with autotetraploids (which are common among crop plants) has similar features to selection in the presence of additive epistasis there is a transient component to the response contributed by nonadditive gene action. In the case of autotetraploids, this is the dominance variance, which occurs because autotetraploid parents pass along two alleles at each locus to their offspring. As with epistasis, the contribution to the selection response from nonadditive variance arises because the genotypes are not in Hardy-Weinberg equilibrium. After several generations of random mating, the selection-induced allele frequencies remain unchanged (and hence, any additive contribution is permanent), but any nonadditive contributions decay away as the population approaches Hardy-Weinberg.

This section is a bit technical, with some of the details developed in Examples 21.6 and 21.7, so we will first review the key results. Except in the case of selfing (using $ S_{1} $ seed), the permanent response to selection is the same as with a diploid. The transient contribution from dominance is generally small (indeed, it is smaller than its contribution

under individual selection; Equation 15.9) and is only significant when the dominance variance is substantially larger than the additive variance. Further, this (generally small) transient contribution quickly decays under random mating. An additional complication involving autotetraploids is deferred until Chapter 23, namely, that the offspring from a cross of two (unrelated) autotetraploid parents from $ S_{1} $ seed are inbred, as the two alleles from each parent can be identical by descent.

Using the results from Example 21.6, we find that

$$
\sigma_ {G} (x, y) = \left\{ \begin{array}{l l} \frac {1}{2} \sigma_ {A} ^ {2} + \frac {1}{6} \sigma_ {D} ^ {2} & \mathrm {p a r e n t , o f f s p r i n g} \\ \frac {1}{4} \sigma_ {A} ^ {2} + \frac {1}{3 6} \sigma_ {D} ^ {2} & \mathrm {h a l f - s i b s} \\ \frac {1}{2} \sigma_ {A} ^ {2} + \frac {2}{9} \sigma_ {D} ^ {2} + \frac {1}{1 2} \sigma_ {T} ^ {2} + \frac {1}{3 6} \sigma_ {Q} ^ {2} & \mathrm {f u l l - s i b s} \end{array} \right.
$$

where $ \sigma_{T}^{2} $ and $ \sigma_{Q}^{2} $ are the variances of third- and fourth-order interactions within loci (see Example 21.6; LW Chapters 5 and 7, for details). Using these covariances and following the same logic leading to Equations 21.26a and 21.26b yields an among-family genetic variance of

$$
\sigma_ {G F} ^ {2} = \left\{ \begin{array}{l l} \frac {1}{4} \sigma_ {A} ^ {2} + \frac {1}{3 6} \sigma_ {D} ^ {2} & \mathrm {h a l f - s i b s} \\ \frac {1}{2} \sigma_ {A} ^ {2} + \frac {2}{9} \sigma_ {D} ^ {2} + \frac {1}{1 2} \sigma_ {T} ^ {2} + \frac {1}{3 6} \sigma_ {Q} ^ {2} & \mathrm {f u l l - s i b s} \end{array} \right.
$$

The within-family genetic variances follow from $ \sigma_{Gw}^{2}=\sigma_{G}^{2}-\sigma_{GF}^{2} $ , which yields

$$
\sigma_ {G w} ^ {2} = \left\{ \begin{array}{l l} \frac {3}{4} \sigma_ {A} ^ {2} + \frac {3 5}{3 6} \sigma_ {D} ^ {2} + \sigma_ {T} ^ {2} + \sigma_ {Q} ^ {2} & \mathrm {h a l f - s i b s} \\ \frac {1}{2} \sigma_ {A} ^ {2} + \frac {7}{9} \sigma_ {D} ^ {2} + \frac {1 1}{1 2} \sigma_ {T} ^ {2} + \frac {3 5}{3 6} \sigma_ {Q} ^ {2} & \mathrm {f u l l - s i b s} \end{array} \right.
$$

The among- and within-family variances, $ \sigma^{2} \left( \bar{z}_{i} \right) $ and $ \sigma^{2} \left( z_{ij}-\bar{z}_{i} \right) $ , immediately follow, respectively, if we substitute Equations 21.32b and 21.32c into Equation 21.9a, and Equation 21.32c into Equation 21.10a. One of the few attempts to measure variance components in a tetraploid (alfalfa) was done by Dudley et al. (1969), who found that only $ \sigma_{A}^{2} $ was significant for the five yield-related traits that they measured. While estimates of $ \sigma_{D}^{2} $ were negative, estimates of $ \sigma_{T}^{2} $ and $ \sigma_{Q}^{2} $ were of the same order as $ \sigma_{A}^{2} $ , but they had standard errors an order of magnitude higher than those of $ \sigma_{A}^{2} $ , and hence were not significant.

To proceed further, we need to compute the expected genetic covariance between y (an offspring of $ \mathcal{R} $ ) and x, a sib upon which selection decisions are made. This requires us to compute two additional genetic covariances for autotetraploids, namely, for a half-uncle or half-aunt and a nephew (when x and $ \mathcal{R} $ are half-sibs, x and y are related as half-uncle or half-aunt and nephew) and for an uncle or aunt and nephew (when x and $ \mathcal{R} $ are full-sibs, x and y are related as uncle or aunt and a nephew). Example 21.7 carries out the bookkeeping.

Using the results from Example 21.7, the covariance between the family mean and an offspring generated using family selection again has two terms: a parent-offspring contribution 1/n (from the measured sib serving as a parent, $ \mathcal{R} $ , of y), and the covariance between x and y when $ \mathcal{R} $ is an unmeasured sib of x, yielding

$$
\begin{array}{l} \sigma (\bar {z}, y \mid \mathcal {R} _ {1}) = \frac {1}{n} \sigma (y \mid \mathcal {R} _ {1}) + \left(1 - \frac {1}{n}\right) \sigma (x, y \mid \mathcal {R} _ {1}) \\ = \frac {1}{n} \left(\frac {1}{2} \sigma_ {A} ^ {2} + \frac {1}{6} \sigma_ {D} ^ {2}\right) + \left(1 - \frac {1}{n}\right) \sigma (x, y \mid \mathcal {R} _ {1}) \\ \end{array}
$$

Using the results from Example 21.7, when x and $ \mathcal{R} $ are half-sibs, we have

$$
\begin{array}{l} \sigma \left(\bar {z}, y \mid \mathcal {R} _ {1}\right) = \frac {1}{n} \left(\frac {1}{2} \sigma_ {A} ^ {2} + \frac {1}{6} \sigma_ {D} ^ {2}\right) + \left(1 - \frac {1}{n}\right) \left(\frac {1}{8} \sigma_ {A} ^ {2} + \frac {1}{2 1 6} \sigma_ {D} ^ {2}\right) \\ = \frac {1}{8} \sigma_ {A} ^ {2} \left(1 + \frac {3}{n}\right) + \frac {1}{2 1 6} \sigma_ {D} ^ {2} \left(1 + \frac {3 5}{n}\right) \\ \end{array}
$$

Turning to full-sibs,

$$
\begin{array}{l} \sigma \left(\bar {z}, y \mid \mathcal {R} _ {1}\right) = \frac {1}{n} \left(\frac {1}{2} \sigma_ {A} ^ {2} + \frac {1}{6} \sigma_ {D} ^ {2}\right) + \left(1 - \frac {1}{n}\right) \left(\frac {1}{4} \sigma_ {A} ^ {2} + \frac {1}{2 7} \sigma_ {D} ^ {2}\right) \\ = \frac {1}{4} \sigma_ {A} ^ {2} \left(1 + \frac {1}{n}\right) + \frac {1}{2 7} \sigma_ {D} ^ {2} \left(1 + \frac {7}{n}\right) \\ \end{array}
$$

In both cases, the additive-genetic contribution to the genetic covariance is the same as for diploids, while the extra contribution from dominance is small and transient, decaying under random mating by two-thirds each generation (Equation 15.10d). Similar expressions can be obtained for within-family selection. Again, the contribution from additive variance is the same as for diploids, while the contribution from dominance is small and decays by two-thirds each generation of random mating.

Example 21.6. For the response under family-based selection schemes involving tetraploids, we will need a bit more detailed treatment of resemblance between polyploid relatives than was given in LW Chapter 7. To begin, we label the four alleles in a tetraploid by $ B_{1}, B_{2}, B_{3} $ , and $ B_{4} $ . There are six possible gametes from this parent, $ (B_{1}, B_{2}),(B_{1}, B_{3}),(B_{1}, B_{4}),(B_{2}, B_{3}) $ $ (B_{2}, B_{4}) $ , and $ (B_{3}, B_{4}) $ . Allowing for nonadditive interaction between alleles, the genotypic value can be decomposed into four additive (single-allele) terms, six dominance (two-allele) terms, four three-way interactions, and one four-way interaction:

$$
\begin{array}{l} G _ {1 2 3 4} = a _ {1} + a _ {2} + a _ {3} + a _ {4} + d _ {1 2} + d _ {1 3} + d _ {1 4} + d _ {2 3} + d _ {2 4} + d _ {3 4} + \\ t _ {1 2 3} + t _ {1 2 4} + t _ {1 3 4} + t _ {2 3 4} + q _ {1 2 3 4} \\ \end{array}
$$

The resulting total genetic variation can be partitioned as

$$
\sigma_ {G} ^ {2} = 4 \sigma_ {a} ^ {2} + 6 \sigma_ {d} ^ {2} + 4 \sigma_ {t} ^ {2} + \sigma_ {q} ^ {2} = \sigma_ {A} ^ {2} + \sigma_ {D} ^ {2} + \sigma_ {T} ^ {2} + \sigma_ {Q} ^ {2}
$$

<div align="center">

If two relatives share only one allele IBD, then their genetic covariance is $ \sigma_{a}^{2}=(1/4)\sigma_{A}^{2} $ . If they share exactly two IBD alleles, the genetic covariance is $ 2\sigma_{a}^{2}+\sigma_{d}^{2}=(1/2)\sigma_{A}^{2}+(1/6)\sigma_{D}. $ If we fill out the rest of these covariances and let $ \pi_{i} $ denote the probability that two relatives share exactly i IBD alleles, we will have

</div>

<table border="1"><tr><td>IBD alleles</td><td>Prob.</td><td>$\sigma_{A}^{2}$</td><td>$\sigma_{D}^{2}$</td><td>$\sigma_{T}^{2}$</td><td>$\sigma_{Q}^{2}$</td></tr><tr><td>1</td><td>$\pi_{1}$</td><td>1/4</td><td>0</td><td>0</td><td>0</td></tr><tr><td>2</td><td>$\pi_{2}$</td><td>1/2</td><td>1/6</td><td>0</td><td>0</td></tr><tr><td>3</td><td>$\pi_{3}$</td><td>3/4</td><td>1/2</td><td>1/4</td><td>0</td></tr><tr><td>4</td><td>$\pi_{4}$</td><td>1</td><td>1</td><td>1</td><td>1</td></tr></table>

Using these results, observe that the genetic covariance between any two relatives can be expressed as a function of their $ \pi_{i} $ values, namely,

$$
\left(\frac {\pi_ {1} + 2 \pi_ {2} + 3 \pi_ {3} + 4 \pi_ {4}}{4}\right) \sigma_ {A} ^ {2} + \left(\frac {\pi_ {2} + 3 \pi_ {3} + 6 \pi_ {4}}{6}\right) \sigma_ {D} ^ {2} + \left(\frac {\pi_ {3} + 4 \pi_ {4}}{4}\right) \sigma_ {T} ^ {2} + \pi_ {4} \sigma_ {Q} ^ {2}
$$

With a parent-offspring relationship, exactly two alleles are IBD, so that $ \pi_{2}=1 $ .With halfsibs, by looking at the 36 entries in the $ 6\times 6 $ table of pairs of gametes from the same parent, we see that 6 share two alleles, 24 share one, and 6 share zero. Hence, $ \pi_{1}=2 4 / 3 6=2 / 3 $ $ \pi_{2}=6 / 3 6=1 / 6 $ .Results for full-sibs follow from these half-sib results. Let $ P_{1} $ and $ P_{2} $ denote the shared parents. The probability that four alleles are shared is the probability the sibs share two alleles from $ P_{1} $ times the probability they share two alleles from $ P_{2} $ ,or $ \pi_{4}=(1/6)(1/6) $ assuming the parents are unrelated and not inbred. Now consider the case of sharing exactly two alleles IBD. This can happen in three different ways: sharing one IBD allele from each

parent (probability [2/3][2/3]), sharing two IBD alleles from $ P_{1} $ and zero from $ P_{2} $ (probability [1/6][1/6]), or sharing two alleles from $ P_{2} $ and zero from $ P_{1} $ (probability [1/6][1/6]), yielding

$$
\pi_ {2} = (2 / 3) ^ {2} + (1 / 6) ^ {2} + (1 / 6) ^ {2} = 1 8 / 3 6 = 1 / 2
$$

Similar logic yields $ \pi_{1}=2/9 $ and $ \pi_{3}=2/9 $ . To summarize,

<table border="1"><tr><td>Relative pair</td><td>$\pi_{0}$</td><td>$\pi_{1}$</td><td>$\pi_{2}$</td><td>$\pi_{3}$</td><td>$\pi_{4}$</td></tr><tr><td>Parent-offspring</td><td>0</td><td>0</td><td>1</td><td>0</td><td>0</td></tr><tr><td>Half-sibs</td><td>1/6</td><td>2/3</td><td>1/6</td><td>0</td><td>0</td></tr><tr><td>Full-sibs</td><td>1/36</td><td>2/9</td><td>1/2</td><td>2/9</td><td>1/36</td></tr></table>

Substitution of the above results for the $ \pi_{i} $ into the general expression for the covariance yields Equation 21.32a.

Example 21.7. Example 21.6 computed the $ \pi_{1},\pi_{2},\pi_{3} $ , and $ \pi_{4} $ values for half- and full-sibs. As we saw above, expressions for the selection response under various family-based selection schemes requires the covariance between a member of the selection unit (x) and an offspring (y) of $ \mathcal{R} $ , a relative of x. We can obtain these covariances by conditioning on the number of IBD alleles shared by x and $ \mathcal{R} $ , and then computing the probability that $ \mathcal{R} $ passes along one or two of these IBD alleles to its offspring, y. For example, if x and $ \mathcal{R} $ share exactly one IBD allele, then with a probability of one-half, that allele is also transmitted to y, in which case x and y share one IBD allele. The 1/2 comes from considering the six possible gametes that $ \mathcal{R} $ can generate. Let $ B_{1} $ denote the IBD allele for x and $ \mathcal{R} $ . When enumerating all six possible biallelic gametes, we see that three contain $ B_{1} $ , while the other three do not. Similar enumeration fills out the table below. For example, suppose x and $ \mathcal{R} $ share two IBD alleles, $ B_{1} $ and $ B_{2} $ . Again counting the six possible gametes of $ \mathcal{R} $ , only one contains both alleles (1/6 have two IBD), while four of six contain either $ B_{1} $ or $ B_{2} $ (but not both). The values when x and $ \mathcal{R} $ share three and four IBD alleles are given below:

<div align="center">

Prob(IBD shared by x and y)

</div>

<table border="1"><tr><td>IBD shared by x and R</td><td>1</td><td>2</td></tr><tr><td>1</td><td>1/2</td><td>0</td></tr><tr><td>2</td><td>2/3</td><td>1/6</td></tr><tr><td>3</td><td>1/2</td><td>1/2</td></tr><tr><td>4</td><td>0</td><td>1</td></tr></table>

When x and $ \mathcal{R} $ are half-sibs, Example 21.6 shows that 2/3 of sibs share one IBD allele, while 1/6 share two. We let the notation $ \mathrm{I}[x,y]=1 $ ) and $ \mathrm{I}[x,y]=2 $ denote that the pair $ (x,y) $ share, respectively, exactly one or two IBD alleles. Using the above table, the probability that y and x share one or two IBD alleles becomes

$$
\begin{array}{l} \pi_ {1} = \Pr \left(\mathrm {I} [ x, y ] = 1 \mid \mathrm {I} [ x, \mathcal {R} ] = 1\right) \Pr \left(\mathrm {I} [ x, \mathcal {R} ] = 1\right) + \Pr \left(\mathrm {I} [ x, y ] = 1 \mid \mathrm {I} [ x, \mathcal {R} ] = 2\right) \Pr \left(\mathrm {I} [ x, \mathcal {R} ] = 2\right) \\ = (1 / 2) (2 / 3) + (2 / 3) (1 / 6) = 4 / 9 \\ \end{array}
$$

$$
\pi_ {2} = \Pr (\mathrm {I} [ x, y ] = 2 \mid \mathrm {I} [ x, \mathcal {R} ] = 2) \Pr (\mathrm {I} [ x, \mathcal {R} ] = 2) = (1 / 6) (1 / 6) = 1 / 3 6
$$

Substituting these into Equation 21.34c returns

$$
\sigma_ {G} (x, y) = \left(\frac {1 (4 / 9) + 2 (1 / 3 6)}{4}\right) \sigma_ {A} ^ {2} + \frac {1 / 3 6}{6} \sigma_ {D} ^ {2} = \frac {1}{8} \sigma_ {A} ^ {2} + \frac {1}{2 1 6} \sigma_ {D} ^ {2}
$$

as the genetic covariance between x and y when the relationship is that of half-uncle (x and $ \mathcal{R} $ are half-sibs) and nephew (y, an offspring of $ \mathcal{R} $ ).

When x and $ \mathcal{R} $ are full-sibs, Example 21.6 showed that the probability they share one, two, three, and four IBD alleles is 2/9, 1/2, 2/9, and 1/36, respectively. Following the same logic and using the above table,

$$
\pi_ {1} = (1 / 2) (2 / 9) + (2 / 3) (1 / 2) + (1 / 2) (2 / 9) + (0) (1 / 3 6) = 2 0 / 3 6 = 5 / 9
$$

$$
\pi_ {2} = (0) (2 / 9) + (1 / 6) (1 / 2) + (1 / 2) (2 / 9) + (1) (1 / 3 6) = 2 / 9
$$

yielding

$$
\sigma_ {G} (x, y) = \left(\frac {1 (5 / 9) + 2 (2 / 9)}{4}\right) \sigma_ {A} ^ {2} + \frac {2 / 9}{6} \sigma_ {D} ^ {2} = \frac {1}{4} \sigma_ {A} ^ {2} + \frac {1}{2 7} \sigma_ {D} ^ {2}
$$

as the genetic covariance between x and y when the relationship is that of uncle (x and $ \mathcal{R} $ are full-sibs) and nephew (y, an offspring of $ \mathcal{R} $ ).

## EFFICIENCY OF FAMILY-BASED VS. INDIVIDUAL SELECTION

Intuition suggests that individual selection is better than either within- or among-family selection when $ h^{2} $ is modest to large, as in this case, individual phenotypes, z, are good predictors of individual breeding values, A. When $ h^{2} $ is small, we expect within-family selection to be more efficient if there is a large common family environmental effect $ \left( \sigma_{E_{c}}\simeq \sigma_{z}^{2}\right) $ and among-family selection to be more efficient if the individual-specific environmental effects are large $ \left( \sigma_{E_{s}}\simeq \sigma_{z}^{2}\right). $

To more formally develop these points, recall that the expected response under mass (individual) selection is $ R_{m}=\bar{\iota}_{m}\sigma_{A}h $ (Equation 13.6b). Applying Equation 21.14a, the ratio of response of among-family selection to individual selection becomes

$$
\frac {R _ {b}}{R _ {m}} = \left(\frac {\bar {\iota} _ {b}}{\bar {\iota} _ {m}}\right) \left(\frac {\gamma}{\sqrt {t _ {n}}}\right)
$$

where $ \gamma $ is a function of the type of among-family selection (Equation 21.14b), t is the intraclass correlation among sibs, with $ t_{n} $ given by Equation 21.9c, and $ \bar{\iota} $ is the average selection intensity on the two sexes. Likewise, for family-deviations selection, Equation 21.19 yields

$$
\frac {R _ {F D}}{R _ {m}} = \left(\frac {\bar {\iota} _ {F D}}{\bar {\iota} _ {m}}\right) \left(\frac {1 - r _ {n}}{\sqrt {1 - t _ {n}}}\right)
$$

where $ r_{n} $ is calculated by Equation 21.6b. Finally, Equation 21.20 yields a response ratio for strict within-family to mass selection of

$$
\frac {R _ {W F}}{R _ {m}} = \left(\frac {\bar {\iota} _ {W F}}{\bar {\iota} _ {m}}\right) \left(\frac {1 - r}{\sqrt {1 - t}}\right)
$$

Equations 21.35a-21.35c show that the relative efficiency of any particular family-based scheme is the product of the ratio of selection intensities (the first term) and the accuracy of selection relative to individual selection (the second term). This accuracy ratio measures how well (relative to individual selection) the selection criterion predicts the breeding values of the parents. We focus first on the accuracy ratio, as the selection-intensity ratio is generally close to one unless sample sizes are very small (Example 21.1; Table 21.6).

## The Relative Accuracies of Family-based vs. Individual Selection

Relative accuracies are typically expressed in terms of the phenotypic correlation, t, between sibs and their coefficient of relatedness, r. Under the simple environmental model $ ( E= E_{c}+E_{s} ) $ , the variance of family means is $ \sigma^{2} \left( \mu_{i} \right)=t \sigma_{z}^{2}=\sigma_{GF}^{2}+\sigma_{Ec}^{2} $ . Hence,

$$
t = \frac {\sigma_ {G F} ^ {2}}{\sigma_ {z} ^ {2}} + \frac {\sigma_ {E c} ^ {2}}{\sigma_ {z} ^ {2}} = \frac {r \sigma_ {A} ^ {2}}{\sigma_ {z} ^ {2}} + \frac {\left(\sigma_ {G F} ^ {2} - r \sigma_ {A} ^ {2}\right) + \sigma_ {E c} ^ {2}}{\sigma_ {z} ^ {2}} = r h ^ {2} + \frac {\left(\sigma_ {G F} ^ {2} - r \sigma_ {A} ^ {2}\right) + \sigma_ {E c} ^ {2}}{\sigma_ {z} ^ {2}}
$$

![](page=31,bbox=[245, 123, 578, 290])

![](page=31,bbox=[591, 129, 883, 290])

<div align="center">

Figure 21.4 Regions of the family size (n)-sib correlation (t) space where individual, amongfamily (family selection) and within-family (selection of family deviations, [FD]) are the most accurate (based on Equations 21.35a and 21.35b). If t is sufficiently large, within-family selection yields the largest response (for large values of n; $ t > 7 / 1 6 = 0. 4 3 7 5 $ for half-sibs and $ t > 3 / 4 $ for full-sibs). Among-family selection is best when t is sufficiently small (for large values of n; $ t < 1 / 1 6 = 0. 0 6 2 5 $ for half-sibs, and $ t < 1 / 4 $ for full-sibs). Individual selection yields the largest response for intermediate values of t. For large n $ (t_{n}, r_{n} $ approaching t,r), among-family selection equals sib selection, as does parental selection (using the curve for full-sibs), while family-deviations selection approaches strict within-family (WF) selection.

</div>

![](page=31,bbox=[244, 431, 573, 577])

![](page=31,bbox=[597, 434, 887, 574])

![](page=31,bbox=[244, 604, 578, 769])

![](page=31,bbox=[596, 607, 891, 768])

<div align="center">

Figure 21.5 Accuracies of among-family selection (top row) and selection on family deviations (FD) (bottom row) relative to individual selection. In all graphs, filled circles correspond to n=2 and open circles to large n. In the upper two graphs, the filled triangles correspond to n=10 and correspond to n=5 in the lower two graphs. Strict within-family selection (WF) corresponds to the large- n values for FD selection (open circles). Assuming equal selection intensities, values exceeding one indicate an increased single-generation response relative to individual selection.

</div>

In the absence of epistasis, Equation 21.11a yields

$$
t = r h ^ {2} + c ^ {2}, \quad \mathrm {w i t h} \quad c ^ {2} \sigma_ {z} ^ {2} = \left\{ \begin{array}{l l} \sigma_ {E c (H S)} ^ {2} & \mathrm {h a l f - s i b s} \\ \frac {1}{4} \sigma_ {D} ^ {2} + \sigma_ {E c (F S)} ^ {2} & \mathrm {f u l l - s i b s} \end{array} \right.
$$

where $ c^{2} $ scales the residual among-family variance (upon removal of any shared additive variance). Figures 21.4 and 21.5 plot the relative accuracies and responses under amongfamily (family selection) and within-family (family-deviations) selection. Note that if $ c=0 $ then $ t=r h^{2} $ , which is bounded above by 1/4 in half-sibs and 1/2 in full-sibs (because $ h^{2}\leq1 $ , it follows that $ t\leq r $ ). For t to exceed r requires that $ c>0 $

What are the exact conditions for a particular method to be more accurate than individual selection? Equation 21.35a shows that among-family selection is more accurate when $ \gamma^{2}>t_{n} $ or

$$
t _ {n} = t + \frac {1 - t}{n} = \left(r h ^ {2} + c ^ {2}\right) \left(1 - \frac {1}{n}\right) + \frac {1}{n} < \gamma^ {2}
$$

For values of n that are moderate to large (such that $ t_{n}\simeq t $), among-family selection is more accurate than mass selection when $ c^{2} $ , the fraction of the total due to residual among-family effects, is sufficiently small. Substituting the value of $ \gamma $ associated with a particular selection scheme (Equation 21.14b) into Equation 21.37a (for moderate to large values of n) yields the condition for among-family selection to be more accurate than individual selection as

$$
c ^ {2} < \left\{ \begin{array}{l l} \frac {1}{1 6} \left(1 - 4 h ^ {2}\right) & \mathrm {h a l f - s i b s (f o r f a m i l y a n d s i b s e l e c t i o n ;} \gamma = 1 / 4) \\ \frac {1}{4} \left(1 - h ^ {2}\right) & \mathrm {h a l f - s i b s (f o r p a r e n t a l a n d S _ {1} s e e d s e l e c t i o n ;} \gamma = 1 / 2) \\ \frac {1}{4} \left(1 - 2 h ^ {2}\right) & \mathrm {f u l l - s i b s (\gamma = 1 / 2)} \end{array} \right.
$$

If $ h^{2} > 1/2 $ , the condition given by Equation 21.37b when full-sibs comprise the selection unit becomes $ c^{2} < 0 $ , and among-family selection is always less efficient than individual selection. With half-sibs comprising the selection unit, family- and sib-selection are always less efficient than individual selection when $ h^{2} > 1/4 $ . Among-family selection is, therefore, only more effective than mass selection when heritability is small and the fraction, $ c^{2} $ , of total variation due to common-family residual variation is also small.

Turning to within-family selection, Equation 21.35b shows that family deviations (FD) selection yields a larger response than individual selection when $ ( 1-r_{n} ) / \sqrt{1-t_{n}} > 1 $ When families are large $ ( n\gg1 $ , such that $ t_{n}\simeq t $ and $ r_{n}\simeq r ) $ , this condition reduces to

$$
t = r h ^ {2} + c ^ {2} > 1 - (1 - r) ^ {2}
$$

or

$$
c ^ {2} > 1 - (1 - r) ^ {2} - r h ^ {2} = \left\{ \begin{array}{l l} \frac {7}{1 6} - \frac {h ^ {2}}{4} & \mathrm {h a l f - s i b s} (r = 1 / 4) \\ \frac {3}{4} - \frac {h ^ {2}}{2} & \mathrm {f u l l - s i b s} (r = 1 / 2) \end{array} \right.
$$

Because $ h^{2}+c^{2}\leq 1 $ (both being fractions of the total variance due to different sources), there is an additional constraint that $ 1-h^{2}\geq c^{2} $ . When $ h^{2}>0.75 $ , within-family (half-sib) selection is always less efficient than individual selection, as here $ c^{2}\leq 1-h^{2}=0.25 $ , while the critical $ c^{2} $ value that must be exceeded is 0.25 $ [(7/16)-(3/4)]=1/4 $ . By the same logic, for full-sibs, individual selection is more efficient than within-family selection whenever $ h^{2}>0.5 $ . Because we assumed that n is large, r and t replace $ r_{n} $ and $ t_{n} $ , respectively, and hence Equations 21.38a and 21.38b are also the conditions for strict within-family (WF) selection. Within-family selection is thus more efficient than individual selection only when

the heritability is low and the residual among-family variance $ ( c^{2} \sigma_{z}^{2} ) $ accounts for a very significant fraction of the total variance; in other words, common-family effects account for much of the phenotypic variance.

Willeke (1982) suggested that an excellent candidate trait for within-family selection would be litter size in pigs. Recall (Chapter 15) that mice from large litters tend to have a negative environmental value for litter size. Given that the heritability estimates for pig litter size from a grandmother-granddaughter regression are higher than those based on a mother-daughter regression, a similar situation likely occurs in pigs. Thus, there is a large family contribution that obscures prediction of the breeding value from the phenotypic value, resulting in the female's ranking within a family being a more informative predictor of her breeding value than her phenotypic value.

Example 21.8. Wilson (1974) examined family selection (using full-sibs) on larval and pupal weight in Tribolium castaneum. Correlations among full-sibs were estimated to be t=0.16 for larval weight and t=0.20 for pupal weight. Family size was n=12. Under family selection, Equation 21.14b implies that $ \gamma=r_{n} $ . With noninbred full-sibs, r=1/2, yielding (from Equation 21.35a) a ratio of the accuracies of family to mass selection on larval weight of

$$
\frac {\gamma}{\sqrt {t _ {n}}} = \frac {r _ {n}}{\sqrt {t _ {n}}} = \frac {r + (1 - r) / n}{\sqrt {t + (1 - t) / n}} = \frac {0 . 5 + 0 . 5 / 1 2}{\sqrt {0 . 1 6 + (0 . 8 4 / 1 2)}} = 1. 1 3
$$

Likewise, the relative accuracy for pupal weight is

$$
\frac {0 . 5 + 0 . 5 / 1 2}{\sqrt {0 . 2 0 + (0 . 8 0 / 1 2)}} = 1. 0 5
$$

showing that both characters are expected to show a slightly larger response under family selection than under mass selection. Note from Equation 21.14b that the expected response for sib-selection using full-sibs is the same as for parental selection (as $ \gamma=1/2 $ in both cases). The relative accuracy of these two methods (sib and parental selection) on larval weight is

$$
\frac {\gamma}{\sqrt {t _ {n}}} = \frac {0 . 5}{\sqrt {0 . 1 6 + (0 . 8 4 / 1 2)}} = 1. 0 4
$$

while their relative accuracy for pupal weight is

$$
\frac {\gamma}{\sqrt {t _ {n}}} = \frac {0 . 5}{\sqrt {0 . 2 0 + (0 . 8 0 / 1 2)}} = 0. 9 7
$$

Thus, for pupal weight, family selection is slightly more accurate than mass selection, while sib selection and parental selection are slightly less accurate.

Several other studies have compared family and individual selection. Campo and Tagarro (1977) compared full-sib family and individual selection on Tribolium pupal weight, using experiments with family sizes of 4 and 10. In both experiments, family selection gave the larger single-generation response, while mass selection had the larger response after six generations. None of these differences were significant. Two other studies compared individual and among-family selection, both using half-sib family selection in chickens. Garwood et al. (1980) examined laying rate $ ( h^{2}=0. 2 2) $ and egg weight $ ( h^{2}=0. 5 5) $ and found that individual selection yielded a greater single-generation response for both characters, but the difference for egg weight was not significant. Kinney et al. (1970) examined several characters, and found that the response under individual selection exceeded that from family selection, although again none of the differences were significant. Lack of significance is not surprising given the (often) small expected differences between methods, coupled with the large evolutionary

Finally, it is informative to compare methods using the heritability version of response, $ R_{x}=h_{x}^{2} S_{x}. $ From Equation 21.23, the within-family heritability exceeds the individual heritability when $ 1-r>1-t. $ Hence,

$$
h _ {w} ^ {2} > h ^ {2} \mathrm {w h e n} t > r
$$

Likewise, from Equation 21.15b, the among-family heritability satisfies

$$
h _ {b} ^ {2} > h ^ {2} \quad \mathrm {w h e n} \quad \gamma > t _ {n}
$$

The careful reader may have noticed that these conditions are rather different from those given by Equations 21.37a and 21.38a. For example, Equation 21.37a implies that amongfamily selection yields a larger response than individual selection when $ \gamma >\sqrt{t_{n}} $ , whereas Equation 21.39b implies that the among-family heritability is greater than $ h^{2} $ when $ \gamma >t_{n} $ What is the discrepancy between these two approaches (accuracies versus heritabilities)?

The key is that the variances of the groups being selected differ. Because $ \sigma_{z}^{2}=\sigma_{b}^{2}+\sigma_{w}^{2} $ the among-family and within-family variances are each less than the phenotypic variance of a random individual. Because $ S_{x}=\bar{\iota}_{x}\sigma_{x} $ larger selection intensities are required to give a family-based approach the same selection differential as individual selection. Because the within- and among-family variances are $ (1-t_{n})\sigma_{z}^{2} $ and $ t_{n}\sigma_{z}^{2} $ , respectively, it follows that

$$
\frac {S _ {b}}{S _ {m}} = \frac {\bar {\iota} _ {b} \sigma_ {b}}{\bar {\iota} _ {m} \sigma_ {z}} = \frac {\bar {\iota} _ {b}}{\bar {\iota} _ {m}} \sqrt {t _ {n}} \quad \mathrm {a n d} \quad \frac {S _ {w}}{S _ {m}} = \frac {\bar {\iota} _ {w} \sigma_ {w}}{\bar {\iota} _ {m} \sigma_ {z}} = \frac {\bar {\iota} _ {w}}{\bar {\iota} _ {m}} \sqrt {1 - t _ {n}}
$$

Under identical selection intensities, the differentials for among- and within-family selection are $ \sqrt{t_{n}} $ and $ \sqrt{1-t_{n}} $ , respectively, of the differential under mass selection. Thus, even when $ h_{w}^{2} $ or $ h_{b}^{2} $ exceeds $ h^{2} $ , this advantage is partially countered by smaller selection differentials due to smaller variances. The contrast of heritabilities as a comparison of expected response assumes that there is the same selection differential, and thus has a hidden assumption of more selection under family-based selection, as the presence of identical S values implies a larger value of $ \bar{i} $ for family-based selection (Equation 21.39c).

## Comparing Selection Intensities: Finite Size Corrections

While not nearly as dramatic as the above differences in the selection differentials (Equation 21.39c), the selection intensities can differ across methods even if the same fraction, p, is saved (Example 21.1). These differences arise from the finite sample-size correction of $ \bar{\iota} $ (Chapter 14). Suppose nine individuals are measured, three from each of three families. If we select for the upper 1/3, we keep the best one of three families under among-family selection, and the best of the three individuals within each family under WF selection, resulting in an expected selection intensity of $ \bar{\iota}_{(1,3)}=0.846 $ (the expected value of the largest of the first three order statistics). Under family deviations (FD) and mass selection, we chose the largest three of nine values, resulting in an expected selection intensity of $ \bar{\iota}_{(3,9)}=0.996 $ . Table 21.6 summarizes the selection intensities for the different methods, and shows that $ \bar{\iota}_{b}=\bar{\iota}_{WF}\leq\bar{\iota}_{m}\leq\bar{\iota}_{FD}. $

An additional subtlety in adjusting the selection intensity was pointed out by Hill (1976,1977b). The expected selection intensity is computed by taking the expected value of the largest standardized order statistics (Chapter 14), under the assumption that the order statistics are uncorrelated. However, with family deviations (FD), family index, and even mass selection, there is the potential for correlations between order statistics. This arises if families contribute different numbers of individuals, resulting in correlations between those measures from the same family, and hence correlations between some of the order

<div align="center">

Table 21.6 Selection intensities for various forms of family-based selection schemes corrected for finite sample size. The upper p of the population is saved and the population consists of m families each with n members, for a total of M=mn measured individuals. Tables of exact values for $ \bar{\iota}_{(K,M)} $ (the average value of the top K of the M standardized order statistics; see Chapter 14) are given by Becker (1992), and can also be easily obtained via simulations. Approximations for $ \bar{\iota}_{(K,M)} $ are given by Equations 14.4a-14.4c.

</div>

<table border="1"><tr><td>Selection Type</td><td>Corrected Selection Intensity</td></tr><tr><td>Individual</td><td>$\bar{i}_{m}=\bar{i}_{(pM,M)}$</td></tr><tr><td>Among-family</td><td>$\bar{i}_{b}=\bar{i}_{(pm,m)}$</td></tr><tr><td>Family-deviations</td><td>$\bar{i}_{FD}=\bar{i}_{(pM,M)}\sqrt{1+\frac{1}{M-1}}$</td></tr><tr><td>Within-family</td><td>$\bar{i}_{WF}=\bar{i}_{(pn,n)}$</td></tr></table>

statistics. The correction for mass selection is generally very small and will be ignored here (see Equation 21.57b). Within-family deviations are negatively correlated within a family, $ \rho=-1/[n-1] $ for a family of size n), as they are deviations from a common family mean. As a result, Dempfle (1990) and Hill et al. (1996) found that the resulting selection intensity for within-family deviations is thus slightly larger than the intensity for mass selection $ \bar{\iota}_{m} $ with

$$
\bar {\iota} _ {F D} = \bar {\iota} _ {m} \sqrt {1 + \frac {1}{M - 1}}
$$

where M is the total number of measured sibs. On the other hand, with selection on a family index, the correlations between index scores are positive and can be considerable even for large n (Equation 21.58). We will consider the appropriate correction for $ \bar{i} $ in our treatment of family index selection at the end of this chapter.

## Within-family Selection Has Additional Long-term Advantages

The above discussion of the relative efficiencies of different methods focused on a single generation of response from an unselected base population. As we saw in Chapter 16, after one generation of selection, gametic-phase disequilibrium (LD for short) is generated (even among unlinked loci), which (for directional selection) results in a reduction in the additive variance. This reduction, and the resulting decrease in selection response, arises entirely from among-family effects, and thus impacts both individual selection and among-family selection. For unlinked loci, LD does not, however, impact the amount of additive variation within a family (Example 16.2), meaning that under strict within-family (WF) selection, there is no decrease in the additive variance from negative LD. Specifically, the amount of within-family additive variance (in the absence of drift or inbreeding) remains at $ \sigma_{a}^{2}/2 $ (half the genic variance, $ \sigma_{a}^{2} $ ,where $ \sigma_{a}^{2}=\sigma_{A}^{2} $ in the absence of LD), while the amount of among-family variance is $ \sigma_{a}^{2}/2+d $ ,where $ d<0 $ (Chapter 16). Hence, the above comparisons for a single generation undervalue the relative short-term gains from WF selection (with respect to either mass or among-family selection). As we saw in Chapter 16, the reduction in the amount of additive variance due to among-family differences can be substantial $ |d| \gg0 $ especially for a trait that has a moderate to high heritability and is under strong selection (Figure 16.4).

A further advantage of within-family selection appears over the longer term. As mentioned previously, under strict within-family selection (WF), all families contribute the same number of offspring to the next generation, which results in a doubling of the effective population size relative to other schemes that weight among-family information (the latter generates an among-family variance in offspring number, which reduces $ N_{e} $ ; Equation 3.4).

As developed in Chapter 26, the long-term response to selection is a function of the effective population size, which results once again in the single-generation comparison of WF to mass or among-family selection that underestimates its relative long-term importance. We examine these issues further in Chapter 26.

## RESPONSE WHEN FAMILIES ARE REPLICATED OVER ENVIRONMENTS

Family members are often raised in multiple plots and/or environments, and carefully designed family replication in such a setting offers two potential advantages. First, it allows for the selection of families that perform best over a range of environments, even when extensive genotype $ \times $ environment interactions (G $ \times $ E) are present. Second, replication within an environment reduces the effects of microenvironmental differences, thus increasing the predictability of a family's breeding value and resulting in a larger selection response.

Because family replication is a hallmark of plant breeding, we will examine several schemes used by breeders in detail in this section (in Chapter 23 we examine related designs under inbreeding, while both line crossing and selection in the presence of G $ \times $ E are more fully examined in Volume 3). Detailed reviews of plant-breeding methodology are given by Namkoong (1979), Hallauer (1981, 1985), Hallauer and Miranda (1981), Nguyen and Sleper (1983), Wricke and Weber (1986), Mayo (1987), Hallauer et al. (1988), Gallais (1990, 2003), Nyquist (1991), Stoskopf et al. (1993), Bos and Caligari (1995), Allard (1999), Holland et al. (2003), Sleper and Poehlman (2006), Acquaah (2007), Bernardo (2010), and Hallauer et al. (2010).

## Among-family Variance Under Replication

The expected response to among-family selection under replication follows from Equation 21.14a, using the appropriate among-family variance, $ \sigma^{2}(\overline{z}) $ , given the replication design used by the breeder. In the simplest case, only a single macroenvironment (such as a growing region) is considered, and the family is replicated by raising $ n_{s} $ sibs in each of $ n_{p} $ separate plots (for a total of $ N=n_{p} n_{s} $ sibs per family). Under this replication scheme, the total environmental value can be partitioned as $ E=E_{c}+E_{p}+E_{s} $ , representing a commonfamily effect $ (E_{c}) $ , a plot-specific effect $ (E_{p}) $ , and individual-specific effects $ (E_{s}) $ . Following similar logic to that in Example 21.3, the resulting variance becomes

$$
\sigma^ {2} (\bar {z}) = \sigma_ {F} ^ {2} + \frac {\sigma_ {E _ {p}} ^ {2}}{n _ {p}} + \frac {\sigma_ {w} ^ {2}}{N}
$$

where $ \sigma_{E_{p}}^{2} $ is the plot-to-plot variance (the environmental variance among plots in the same macroenvironment), $ \sigma_{F}^{2}=\sigma_{G F}^{2}+\sigma_{E_{c}}^{2} $ is the among-family variance, and $ \sigma_{w}^{2}=\sigma_{G w}^{2}+\sigma_{E_{s}}^{2} $ is the within-plot variance of individuals about their family averages. Recall that $ \sigma_{G w}^{2}=\sigma_{G}^{2}-\sigma_{G F}^{2} $ , and values for the among- and within-family genetic variances are given by Equations 21.11a and 21.11b, respectively, when epistasis is absent, and more generally by Equations 21.26a and 21.26b.

An alternative way to express the variance of family means is

$$
\sigma^ {2} (\bar {z}) = \sigma_ {G F} ^ {2} + \sigma_ {E _ {c}} ^ {2} + \sigma^ {2} (\epsilon)
$$

where for the design given by Equation 21.41a, the residual variance is

$$
\sigma^ {2} (\epsilon) = \frac {\sigma_ {G w} ^ {2}}{N} + \frac {\sigma_ {E _ {s}} ^ {2}}{N} + \frac {\sigma_ {E _ {p}} ^ {2}}{n _ {p}} = \left(\frac {1}{N}\right) \left(\sigma_ {G w} ^ {2} + \sigma_ {E _ {s}} ^ {2} + n _ {s} \sigma_ {E _ {p}} ^ {2}\right)
$$

The critical observation is that the contribution from $ \sigma^{2}(\epsilon) $ can be largely controlled by the experimental design (here, the choice of $ n_{s} $ and $ n_{p} $ ).

More generally, if the family is replicated over $ n_{e} $ distinct macroenvironments, each with $ n_{p} $ plots and $ n_{s} $ sibs per plot, for a total of $ N=n_{p} n_{s} n_{e} $ sibs, Equation 21.41b holds, with the residual variance now being

$$
\begin{array}{l} \sigma^ {2} (\epsilon) = \frac {\sigma_ {G w} ^ {2}}{N} + \frac {\sigma_ {G F \times E} ^ {2}}{n _ {e}} + \frac {\sigma_ {E _ {p}} ^ {2}}{n _ {e} n _ {p}} + \frac {\sigma_ {E _ {s}} ^ {2}}{N} \\ = \left(\frac {1}{N}\right) \left(\sigma_ {G w} ^ {2} + \sigma_ {E _ {s}} ^ {2} + n _ {s} \sigma_ {E _ {p}} ^ {2} + n _ {p} n _ {s} \sigma_ {G F \times E} ^ {2}\right) \\ \end{array}
$$

where $ \sigma_{GF}^{2} $ is the genetic variance among family means over this set of environments, and $ \sigma_{GF\times E}^{2} $ is the variance from the family-environment interaction (LW Chapter 22).

Plant breeders often use an alternative partition of the environment into location (L) and year (Y) effects. Suppose a family is replicated over $ n_{\ell} $ locations over $ n_{y} $ years, where each of the $ n_{\ell} n_{y} $ year-location combinations is replicated as $ n_{p} $ plots of $ n_{s} $ sibs each, for a total of $ N=n_{\ell} n_{y} n_{p} n_{s} $ sibs per family. Again, Equation 21.41b holds, with a residual variance of

$$
\begin{array}{l} \sigma^ {2} (\epsilon) = \frac {\sigma_ {G F \times L} ^ {2}}{n _ {\ell}} + \frac {\sigma_ {G F \times Y} ^ {2}}{n _ {y}} + \frac {\sigma_ {G F \times L \times Y} ^ {2}}{n _ {\ell} n _ {y}} + \frac {\sigma_ {E _ {p}} ^ {2}}{n _ {\ell} n _ {y} n _ {p}} + \frac {\sigma_ {G w} ^ {2} + \sigma_ {E _ {s}} ^ {2}}{n _ {\ell} n _ {y} n _ {p} n _ {s}} \\ = \left(\frac {1}{N}\right) \left[ \sigma_ {G w} ^ {2} + \sigma_ {E _ {s}} ^ {2} + n _ {s} \sigma_ {E _ {p}} ^ {2} + n _ {p} n _ {s} \left(n _ {y} \sigma_ {G F \times L} ^ {2} + n _ {\ell} \sigma_ {G F \times Y} ^ {2} + \sigma_ {G F \times L \times Y} ^ {2}\right) \right] \\ \end{array}
$$

where $ \sigma_{GF\times L}^{2},\sigma_{GF\times Y}^{2} $ and $ \sigma_{GF\times L\times Y}^{2} $ are the family by environment (year, location, and year-location) interactions (Lonnquist 1964; Comstock and Moll 1973; Patterson et al. 1977; Brennan and Byth 1979; Thompson and Cunningham 1979).

The above expressions for $ \sigma^{2} (\epsilon) $ show the importance of replication and provide some guidance as to how one should allocate resources. For a fixed number of sibs per family (N), how should one choose $ n_{e}, n_{p} $ and $ n_{s} $ to minimize $ \sigma^{2}(\bar{z}) $ ? If N is fixed, then the relative weightings on the within-family genetic variance and individual-specific environmental variance are fixed. When the genotype $ \times $ environment interaction variance $ (\sigma_{GF\times E}^{2}) $ is large, its effect on the selection response can be reduced by replicating families across more environments (increasing $ n_{e} $ ). More generally, when viewing environments as locations years (Equation 21.42b), the total number of environments is $ n_{e}=n_{\ell} n_{y} $ , and preliminary estimates of the variation components $ (\sigma_{GF\times L}^{2},\sigma_{GF\times Y}^{2}, $ and $ \sigma_{GF\times L\times Y}^{2} $ ) can suggest the appropriate allocation over locations versus years for a fixed value of $ n_{e} $ . When the amongplot variance $ (\sigma_{E_{p}}^{2}) $ is large, its effect is reduced by increasing $ n_{p} $ or $ n_{e} $ . With preliminary estimates of the variance components in hand, one can numerically search for the optimal values of $ n_{e}, n_{p}, $ and $ n_{s} $ that give the smallest $ \sigma^{2}(\bar{z}) $ for a fixed value of $ N=n_{e} n_{p} n_{s} $ . Using replication can result in a considerable improvement over mass selection. For example, using variance components estimated for maize lines grown in several locations in India, Sanghi (1983) estimated that full-sib selection with replication would be three to sixfold times more efficient than mass selection.

One consequence of replication is that the among-family heritability, $ h_{b}^{2}=\gamma \sigma_{A}^{2} / \sigma^{2}(\bar{z}) $ (Equation 21.15b), is now a complex function of the design, namely, the values of $ n_{e} $ and $ n_{p} $ , in addition to the total number of sibs, which enter through $ \sigma^{2}(\bar{z}) $ , via $ \sigma^{2}(\epsilon) $ . Thus, with replication, an among-family heritability does not directly translate into an individual heritability (Hanson 1963; Nyquist 1991; Holland et al. 2003). Even with the same variance components, $ h_{b}^{2} $ changes as a function of the replication design. Hanson suggested that, when replication is present, the among-family heritability needs to be defined with respect to a particular standard design, such as his proposal in soybeans of a design with two years over two locations, with two replications in each location-year combination.

Finally, consider the among-family variance under a nested-sib design with replication. Suppose (as before) that there are $ n_{f} $ females per male, but now that each full-sib family is

replicated as $ n_{s} $ sibs over $ n_{e} $ environments. The resulting variance becomes

$$
\sigma^ {2} (\bar {z}) = \sigma_ {G F (H S)} ^ {2} + \frac {\sigma_ {G (f | m)} ^ {2}}{n _ {f}} + \frac {\sigma_ {G F (H S) \times E} ^ {2}}{n _ {e}} + \frac {\sigma_ {G (f | m) \times E} ^ {2}}{n _ {f} n _ {e}} + \frac {\sigma_ {G w (F S)} ^ {2} + \sigma_ {E _ {s}} ^ {2}}{N}
$$

where $ N=n_{f} n_{e} n_{s} $ is the total number of half-sibs per male (Robertson et al. 1955; Webel and Lonnquist 1967; da Silva and Lonnquist 1968). Assuming no epistasis or genotype by environment interaction ( $ \mathrm{G}\times\mathrm{E} $ ), we can express this among-family variance as

$$
\frac {\sigma_ {A} ^ {2}}{4} + \frac {\sigma_ {A} ^ {2} + \sigma_ {D} ^ {2}}{4 n _ {f}} + \frac {\sigma_ {A \times E} ^ {2}}{4 n _ {e}} + \frac {\sigma_ {A \times E} ^ {2} + \sigma_ {D \times E} ^ {2}}{4 n _ {f} n _ {e}} + \frac {(1 / 2) \sigma_ {A} ^ {2} + (3 / 4) \sigma_ {D} ^ {2} + \sigma_ {E _ {s}} ^ {2}}{N}
$$

The extension of this result to multiple plots per location when $ \mathrm{G}\times\mathrm{E} $ is present follows in a similar fashion from our development above for Equation 21.42b.

An example of family selection with replication was provided by selection for increased grain yield in maize by the International Maize and Wheat Improvement Center (CIMMYT), summarized by Pandey et al. (1986, 1987) and Crossa and Gardner (1989). The goal of the CIMMYT selection schemes was to develop varieties of maize that yield well over a wide range of environments. Starting in 1974, 250 full-sib families, along with six local checks (control lines to allow for standardized comparisons), were evaluated at six lowland tropical locations (with two replications per location) in the northern and southern hemispheres. A total of 28 countries were used during the course of five cycles of selection. Selection (initially) was strictly among families with the international field trials conducted on full-sib families, while the recombination unit consisted of $ S_{1} $ seed from the superior families. The selection scheme was later modified to allow for within-family selection as well. Roughly 50% of the families were selected based on the international trials, about 20% of which were subsequently rejected given their poor performance in disease- and insect-resistance trials in separate nurseries. The average gain in yield per cycle was around 2%.

Example 21.9. Eberhart et al. (1966) estimated genetic variance components for seven characters in two open-pollinated maize varieties. Using individuals grown in two locations in North Carolina, they obtained the following estimates for yield in the variety Jarvis:

$$
\sigma_ {A} ^ {2} = 1 2 0, \quad \sigma_ {A \times L} ^ {2} = 1 1 4, \quad \sigma_ {D} ^ {2} = 2 7 0, \quad \sigma_ {D \times L} ^ {2} = 9 8, \quad \sigma_ {E _ {s}} ^ {2} = 5 0 8
$$

Estimates of epistatic variances were not significantly different from zero. Consider the expected response under a design with 25 half-sib families, each with a total of 50 offspring scored over five environments $ ( n_{e}=5) $ . The top five families were selected, using $ S_{1} $ seed to form the next generation (allowing for selection on both sexes). Recalling Equation 21.14a (with $ \gamma=1/2 $ for $ S_{1} $ seed; Equation 21.14b), the expected response will be

$$
R = \frac {2 \bar {\iota} _ {(5 , 2 5)} \left(\sigma_ {A} ^ {2} / 4\right)}{\sigma (\bar {z})} = \frac {2 \cdot 1 . 3 4 5 \cdot 3 0}{\sigma (\bar {z})} = \frac {8 0 . 7}{\sigma (\bar {z})}
$$

using Equation 14.4b to obtain $ \bar{\iota}_{(5,25)} $ . If we use the above variance estimates, then $ \sigma_{GF\times E}^{2}=\sigma_{A\times L}^{2}/4=28.5 $ , while Equation 21.26a and 21.26b yield, respectively, $ \sigma_{GF}^{2}=\sigma_{A}^{2}/4=30 $ and $ \sigma_{Gw}^{2}=(3/4)\sigma_{A}^{2}+\sigma_{D}^{2}=360 $ . If the families being scored are strict half-sibs (meaning that all offspring from a pollen parent each have a different seed parent, $ n_{f}=N=50 $ ), then Equation 21.42a returns

$$
\begin{array}{l} \sigma^ {2} \left(\bar {z} _ {H S}\right) = \sigma_ {G F} ^ {2} + \frac {\sigma_ {G w} ^ {2} + \sigma_ {E _ {s}} ^ {2}}{N} + \frac {\sigma_ {G F \times L} ^ {2}}{n _ {e}} \\ = 3 0 + \frac {3 6 0 + 5 0 8}{5 0} + \frac {2 8. 5}{5} = 5 3. 0 6 \\ \end{array}
$$

and the expected response becomes $ 80.7 / \sqrt{53.06}=11.08. $

Now suppose that the sibs are from a nested design with each male pollinating five seed parents, and with each cross producing 10 offspring $ ( n_{f}=5, N=50) $ . Using the above variance components, Equation 21.43b yields

$$
\begin{array}{l} \sigma^ {2} (\bar {z}) = \frac {\sigma_ {A} ^ {2}}{4} + \frac {\sigma_ {A} ^ {2} + \sigma_ {D} ^ {2}}{4 n _ {f}} + \frac {\sigma_ {A \times L} ^ {2}}{4 n _ {e}} + \frac {\sigma_ {A \times L} ^ {2} + \sigma_ {D \times L} ^ {2}}{4 n _ {f} n _ {e}} + \frac {(1 / 2) \sigma_ {A} ^ {2} + (3 / 4) \sigma_ {D} ^ {2} + \sigma_ {E _ {s}} ^ {2}}{N} \\ = \frac {1 2 0}{4} + \frac {1 2 0 + 2 7 0}{2 0} + \frac {1 1 4}{2 0} + \frac {1 1 4 + 9 8}{1 0 0} + \frac {(1 / 2) 1 2 0 + (3 / 4) 2 7 0 + 5 0 8}{5 0} \\ = 7 2. 7 3 \\ \end{array}
$$

resulting in an expected response of $ 8 0. 7 / \sqrt{7 2. 7 3}=9. 4 7 $ . Hence, the strict half-sib design has a smaller among-family variance, and thus a 117% larger expected response than expected under a nested design.

## Ear-to-Row Selection

One of the earliest examples of family-based selection was the ear-to-row selection method in maize, first used by Hopkins (1899) to start his classic long-term selection experiment (Chapter 26). Here the seeds from each maize ear are planted in a single row (so that a row corresponds to a family), with individuals from the best rows chosen as seed parents for the next generation. Plants in the rows to be scored are either detassled or have their tassles (pollen-producing structures) bagged, removing their ability to contribute pollen. As a result, these plants can neither self nor pollinate. Pollen is provided by rows planted with bulk of all seeds (a polycross mating design). Assuming open pollination, the seeds on a single ear are half-sibs (with a common mother), which means that the ear-to-row method is an example of half-sib family selection, with selection on only one sex (the seed parent). In rice, panicle-to-row selection has been used (e.g., Ntanos and Roupakias 2001), where the panicle is essentially the equivalent of the maize ear, and again a row equals a family.

Suppose a total of $ n=n_{e} n_{p} n_{s} $ sibs per family are scored, by growing $ n_{p} $ rows of $ n_{s} $ sibs, replicated over $ n_{e} $ distinct environments. From Equation 21.15c, the expected response under ear-to-row selection, when choosing the top K of M families $ ( p=K/M) $ , is

$$
R _ {E R} = \bar {\iota} _ {(p M, M)} \frac {(1 + 3 / n) \left(\sigma_ {A} ^ {2} / 8\right)}{\sigma \left(\bar {z} _ {H S}\right)} \simeq \bar {\iota} _ {(p M, M)} \frac {\sigma_ {A} ^ {2} / 8}{\sigma \left(\bar {z} _ {H S}\right)}
$$

where $ \sigma^{2}(\bar{z}_{HS}) $ is calculated by Equation 21.42a. For large values of n (in the absence of epistasis),

$$
R _ {E R} = \bar {\iota} _ {(p M, M)} \frac {\sigma_ {A} ^ {2} / 8}{\sqrt {\frac {\sigma_ {A} ^ {2}}{2} + \frac {\sigma_ {G F} ^ {2} \times E}{n _ {e}} + \frac {\sigma_ {E _ {p}} ^ {2}}{n _ {e} n _ {p}} + \frac {\sigma_ {E _ {s}} ^ {2}}{n}}}
$$

## Modified Ear-to-Row Selection

The ear-to-row method has the advantage of being fairly easy to implement for testing a family (with replication reducing the effects from the environmental variance), coupled with the same cycle time as mass selection (one generation). As a result, this method was commonly used by early maize breeders, for example, Hopkins (1899), Smith (1908, 1909), Montgomery (1909), Williams and Walton (1915), Kiesselbach (1916), and Hume (1919). While it proved effective at modifying highly heritable traits (such as kernel protein and oil content), ear-to-row selection was generally not successful in improving yield (Kiesselbach 1922; Richey 1922; Smith and Bruson 1925), and it was not regarded as a practical scheme for yield improvement. Sprague (1955) suggested that the failure for yield improvement

![](page=40,bbox=[110, 141, 758, 492])

<div align="center">

Figure 21.6 Lonnquist's (1964) modified ear-to-row selection scheme. Half-sib families (represented here by the maize ears in the middle of the figure) are planted both as rows in multiple environments (the yield trials over environments $ E_{1} $ through $ E_{4} $ at the bottom of the figure) and as a single additional row in yet another location, the so-called crossing block (the rows at the top of the figure). From the best families in the yield trials (the first and fourth in the above figure) one then chooses the best individuals (indicated by the circled plants) from their sibs in the crossing block (within-family selection) to form the next generation.

</div>

was largely the result of insufficient control over environmental variance, which resulted in $ \sigma_{E}^{2} $ largely obscuring the additive variance. (For this same reason, mass selection was also regarded as being impractical for improving maize yield.) An alternative hypothesis was suggested by Hull (1945, 1952), who thought that the lack of response in yield was a result of most of the genetic variance being nonadditive. The finding of considerable additive variance in yield by a number of maize geneticists motivated Lonnquist's (1964) development of the modified ear-to-row scheme, a combined selection approach involving both among-family (ear-to-row) and within-family (within-row) selection (Figure 21.6).

Under Lonnquist's design, seed from each family is planted as rows in several environments. These form the yield or performance trials for selecting the best-performing families averaged over these environments. On a separate plot (the crossing block), additional seeds from each family are planted as a single row. Within the crossing block, the best individuals from the rows corresponding to the families with the best performance in the yield trials are used as the seed parents for the next generation. Selection is only on one parent in the crossing block, as plants are detassled and open pollinated from a random bulk of all the initially planted families. One advantage of this scheme is that one can use bulk measures over rows in the yield trials and more detailed (and labor-intensive) individual

plant measures in the smaller crossing block.

Under Lonnquist's original design, the replicated field trials and the crossing block are grown contemporaneously (planting of the crossing block may be delayed slightly to ensure that all field information from the yield trials can be gathered). Thus, one cycle of modified ear-to-row selection can be carried out in a single generation. The expected total response is the sum of the expected gains at each step in the cycle, $ R_{ER(m)}=R_{ER}+R_{ER(w)} $ . The response, $ R_{ER} $ , under the first step (choosing the best families) is the same as for standard ear-to-row selection (Equations 21.44 and 21.45). Because plants in the crossing block are open pollinated using a bulk of all families, selection is only on females within each row. If one chooses the best $ k=qn_{s} $ of $ n_{s} $ plants within each selected row (i.e., strict within-family [FW] selection saving the upper fraction, q), the expected response to within-row selection becomes

$$
R _ {E R (w)} = \bar {\iota} _ {\left(q n _ {s}, n _ {s}\right)} \frac {\left(3 / 8\right) \sigma_ {A} ^ {2}}{\sigma_ {w (H S)}}
$$

Because families are not replicated within the crossing block, then

$$
\sigma_ {w (H S)} ^ {2} = \sigma_ {G w (H S)} ^ {2} + \sigma_ {E _ {s}} ^ {2}
$$

Hence, in the absence of epistasis, the component of response from within-row selection becomes (Equation 21.22b)

$$
R _ {E R (w)} = \bar {\iota} _ {\left(q n _ {s}, n _ {s}\right)} \frac {(3 / 8) \sigma_ {A} ^ {2}}{\sqrt {(3 / 4) \sigma_ {A} ^ {2} + \sigma_ {D} ^ {2} + \sigma_ {E _ {s}} ^ {2}}}
$$

Ignoring any potential changes in $ \sigma_{A}^{2} $ due to the first step of selection (ear-to-row), the expected response becomes

$$
\begin{array}{l} R _ {E R (m)} = R _ {E R} + R _ {E R (w)} \\ = \bar {\iota} _ {(p M, M)} \frac {\sigma_ {A} ^ {2} / 8}{\sigma \left(\bar {z} _ {H S}\right)} + \bar {\iota} _ {(q n _ {s}, n _ {s})} \frac {(3 / 8) \sigma_ {A} ^ {2}}{\sigma_ {w (H S)}} \\ \end{array}
$$

where we have chosen the best $ K=p M $ of M families in the yield trials and the best $ k=q n_{s} $ of $ n_{s} $ within each selected family in the crossing block. With a large number of sibs per row $ (n_{s} $ is large) and a roughly equal selection within and among rows $ (\bar{\iota}_{(p M,M)}\simeq \bar{\iota}_{(q n_{s},n_{s})}=\bar{\iota}) $ the expected response to modified ear-to-row selection is

$$
R _ {E R (m)} = \frac {\bar {\iota} \sigma_ {A} ^ {2} / 8}{\sqrt {\frac {\sigma_ {A} ^ {2}}{2} + \frac {\sigma_ {F \times E} ^ {2}}{n _ {e}} + \frac {\sigma_ {E _ {p}} ^ {2}}{n _ {e} n _ {p}} + \frac {\sigma_ {E _ {s}} ^ {2}}{N}}} + \frac {\bar {\iota} (3 / 8) \sigma_ {A} ^ {2}}{\sqrt {\frac {3 \sigma_ {A} ^ {2}}{4} + \sigma_ {D} ^ {2} + \sigma_ {E _ {s}} ^ {2}}}
$$

Inspection of Equation 21.48b shows that it is not obvious which component (within- vs. among-family) contributes more to the total selection response. The threefold increase in usable additive variance in the within-family component in the numerator can be partly or fully offset by the fact that $ \sigma_{G w}^{2}>\sigma_{G F}^{2} $ (the within-family genetic variance is greater than the among-family variance; see Equations 21.26a and 21.26b). Likewise, it is not clear whether the among- or the within-family environmental variance is expected to be larger. Some fine-tuning is possible on the among-family component, as, if estimates of the appropriate environmental variances are available, changing the experimental design (the values of $ n_{p} $ $ n_{s} $ , and $ n_{e} $ ) can reduce $ \sigma^{2}(\epsilon) $ .

<div align="center">

Example 21.10. Webel and Lonnquist (1967) used modified ear-to-row selection for yield in the Hays Golden open-pollinated variety of maize. Performance of each family was evaluated

</div>

using single rows grown in three different locations. Based on these yield trials, the best 44 of roughly 220 families were identified. In the crossing block, the best 5 of the 25 (or so) plants were chosen in each of the 44 rows corresponding to the selected families. The resulting expected selection intensities for the among- and within-family components were $ \bar{\iota}_{(44,220)}=1.40 $ and $ \bar{\iota}_{(5,25)}=1.35 $ , respectively (Equation 14.4b). Over the first four cycles of selection, Webel and Lonnquist observed a 9.4% increase in yield per cycle, compared with the 3% increase per cycle observed under mass selection (Gardner 1973). The predicted response was 8.4% , with expected contributions of 4.6% from among-families (55% of predicted response) and 3.8% from within-families. The results for 10 cycles of selection were summarized by Compton and Bahadur (1977). Paterniani (1967) also used modified ear-to-row selection for yield for three cycles in Brazilian maize populations. The average yield increased by 42% over the course of the experiment.

Compton and Comstock (1976) suggested a variant of Lonnquist's design. This approach is also referred to as among-and-within-family selection (AWF) or between-andwithin-family selection (B&WFS) by forage breeders (Aastveit and Aastveit 1990; Vogel and Pedersen 1993; Casler and Brummer 2008). Families are again planted ear-to-row in performance trials, but remnant seed from each family is stored. The best families are chosen and the remnant seed for these families is planted to form the crossing block. The pollen plants in the crossing block are a bulk of the selected families. Hence, both parents in the crossing block are subjected to half-sib selection, which doubles the response from the among-family component, and yields

$$
R _ {E R (m)} = \bar {\iota} _ {(p M, M)} \frac {(1 / 4) \sigma_ {A} ^ {2}}{\sigma \left(\bar {z} _ {H S}\right)} + \bar {\iota} _ {(q n _ {s}, n _ {s})} \frac {(3 / 8) \sigma_ {A} ^ {2}}{\sigma_ {W (H S)}}
$$

The Compton-Comstock modified ear-to-row scheme requires two generations per cycle, but it offers increased response (per cycle) as the pollen is also from selected parents. Using the predicted values of Webel and Lonnquist (Example 21.10), the expected response per cycle under the Compton-Comstock design would be $ 2 \cdot 4. 6+3. 8=1 3 $ , for an expected 155% increase per cycle over the Lonnquist design (which had a predicted response 8.4). However, the Compton-Comstock design also requires two generations per cycle, with the result that the response per generation is 6.5, 77% of that expected under the Lonnquist design. The use of off-season (or winter) nurseries, where seeds are grown in either the opposite hemisphere or in the tropics (such as the Hawaiian island of Moloka'i), can allow for two generations in the same calendar year, but this may require more resources than the breeder has available.

## SELECTION ON A FAMILY INDEX

While our focus to this point has been on schemes that use either within- or among-family selection, the modified ear-to-row approach points out the advantage of using selection schemes containing both within- and among-family components. The modified ear-to-row approach is an example of combined selection, where the components are sequentially selected in different generations (and/or plots), and several such schemes are used by plant breeders. Alternatively, one can use both within- and among-family information to select individuals within a single generation. The most general way to do this is to select on a family index,

$$
I _ {i j} = b _ {1} \left(z _ {i j} - \bar {z} _ {i}\right) + b _ {2} \bar {z} _ {i}
$$

where the index value, $ I_{ij} $ is for individual j from family i. Individuals with the largest index scores are mated (avoiding within-family crosses) to form the next generation. Note that individual $ ( I_{ij}=z_{ij} ) $ , family $ ( I_{ij}=\overline{z}_{i} ) $ , and family-deviations $ ( I_{ij}=z_{ij}-\overline{z}_{i} ) $ selection

are all special cases of this general family index, which correspond to weights of $ b_{1}=b_{2}, $ $ b_{1}=0 $ , and $ b_{2}=0 $ , respectively.

An important point is that the relative values of the index weights, not their absolute values, define the choice of individuals—if both weights are multiplied by the same constant, the same individuals are chosen by the new index. As a result, the family index is often written as

$$
I _ {i j} = z _ {i j} + B \bar {z} _ {i}
$$

where B is the relative weight on family mean compared to an individual's phenotype. As the reader can easily verify with a little algebra, this is equivalent to the index given by Equation 21.50a, with

$$
B = \frac {b _ {2}}{b _ {1}} - 1
$$

## Response to Selection on a Family Index

Once again, either Equations 21.1a or 21.4a can be used to predict the single-generation response to selection. Taking x = I returns

$$
R _ {I} = \frac {\sigma \left(I , y \mid \mathcal {R} _ {1}\right)}{\sigma_ {I} ^ {2}} \left(S _ {I _ {m}} + S _ {I _ {f}}\right) = \bar {\iota} _ {I} \sigma_ {z} \rho (I, y)
$$

where $ \sigma(I,y|\mathcal{R}_{1}) $ is the covariance between the index value, I, of a parent and the phenotype of its offspring, y. The variances and covariances required for Equation 21.51 are obtained as follows. Using the covariances summarized in Table 21.3,

$$
\begin{array}{l} \sigma (I, y \mid \mathcal {R} _ {1}) = b _ {1} \sigma \left(z _ {i j} - \bar {z} _ {i}, y \mid \mathcal {R} _ {1} = x _ {i j}\right) + b _ {2} \sigma \left(\bar {z} _ {i}, y \mid \mathcal {R} _ {1} = x _ {i j}\right) \\ = b _ {1} \left(1 - r _ {n}\right) \left(\sigma_ {A} ^ {2} / 2\right) + b _ {2} r _ {n} \left(\sigma_ {A} ^ {2} / 2\right) \\ = \left[ b _ {1} + r _ {n} \left(b _ {2} - b _ {1}\right) \right] \left(\sigma_ {A} ^ {2} / 2\right) \\ \end{array}
$$

Likewise, if we recall that $ \sigma^{2}(x+y)=\sigma_{x}^{2}+\sigma_{y}^{2}+2\sigma_{x,y} $ , the variances summarized in Table 21.4 yield

$$
\begin{array}{l} \sigma^ {2} (I) = b _ {1} ^ {2} \sigma^ {2} \left(z _ {i j} - \bar {z} _ {i}\right) + b _ {2} ^ {2} \sigma^ {2} \left(\bar {z} _ {i}\right) + 2 b _ {1} b _ {2} \sigma \left(z _ {i j} - \bar {z} _ {i}, \bar {z} _ {i}\right) \\ = b _ {1} ^ {2} \left(1 - t _ {n}\right) \sigma_ {z} ^ {2} + b _ {2} ^ {2} t _ {n} \sigma_ {z} ^ {2} + 2 b _ {1} b _ {2} \sigma \left(z _ {i j}, \bar {z} _ {i}\right) - 2 b _ {1} b _ {2} \sigma^ {2} \left(\bar {z} _ {i}\right) \\ = \left(b _ {1} ^ {2} \left(1 - t _ {n}\right) + b _ {2} ^ {2} t _ {n} + 2 b _ {1} b _ {2} t _ {n} - 2 b _ {1} b _ {2} t _ {n}\right) \sigma_ {z} ^ {2} \\ = \left[ b _ {1} ^ {2} + t _ {n} \left(b _ {2} ^ {2} - b _ {1} ^ {2}\right) \right] \sigma_ {z} ^ {2} \\ \end{array}
$$

The resulting heritability of the index becomes

$$
h _ {I} ^ {2} = \frac {2 \sigma (I , y \mid \mathcal {R} _ {1})}{\sigma^ {2} (I)} = h ^ {2} \left[ \frac {b _ {1} + r _ {n} \left(b _ {2} - b _ {1}\right)}{b _ {1} ^ {2} + t _ {n} \left(b _ {2} ^ {2} - b _ {1} ^ {2}\right)} \right]
$$

Finally, because parents only pass along half their breeding value to an offspring (Chapters 6 and 16), it follows that $ \sigma ( I,y\mid \mathcal{R}_{1} )=\sigma ( I,A )/2 $ , namely, half the covariance between the parent's index and breeding values. Hence, from Equations 21.52a and 21.52b, the correlation between an individual's index score (I) and breeding value (A) is

$$
\rho (I, A) = \frac {\sigma (I , A)}{\sigma (I) \sigma (A)} = \frac {2 \sigma (I , y \mid \mathcal {R} _ {1})}{\sigma (I) \sigma (A)} = h \left\lfloor \frac {b _ {1} + r _ {n} \left(b _ {2} - b _ {1}\right)}{\sqrt {b _ {1} ^ {2} + t _ {n} \left(b _ {2} ^ {2} - b _ {1} ^ {2}\right)}} \right\rfloor
$$

Given that $ \rho(z,A)=h $ (Equation 13.11e), the term in the brackets represents the accuracy of the index relative to mass selection. Substituting Equation 21.53a into Equation 21.51 (and recalling that $ \sigma_{z} h^{2}=h\sigma_{A} $ ) yields an expected response of

$$
R _ {I} = \bar {\iota} _ {I} h \sigma_ {A} \frac {b _ {1} + r _ {n} \left(b _ {2} - b _ {1}\right)}{\sqrt {b _ {1} ^ {2} + t _ {n} \left(b _ {2} ^ {2} - b _ {1} ^ {2}\right)}}
$$

where $ \bar{\iota}_{I}=(\bar{\iota}_{I_{m}}+\bar{\iota}_{I_{f}})/2=(S_{I_{m}}+Ss_{I_{f}})/(2\sigma_{I}) $ is the average selection intensity on both sexes. Observe from Equation 21.53c that if we create a new index with weights of $ ab_{1} $ and $ ab_{2} $ , that the constant a cancels, and (as noted above) yields the same response.

Example 21.11. Again consider the work of Clayton et al. (1957) on abdominal bristle number in Drosophila (Examples 21.4 and 21.5). Here $ r_{n}=0.542 $ $ t_{n}=0.326 $ , and $ \sigma_{A} h=1.70 $ Suppose individuals with index scores in the upper 20% are chosen. What is the expected response if we place three times the weight on within-family deviations as we do on family means $ (b_{1}=3,b_{2}=1) $ ? Because 20 families each with 12 sibs are scored, the expected selection intensity is $ \bar{\iota}_{(48,240)}=1.39 $ (as 48 is the upper 20% of $ 20\cdot12=240 $ ), and Equation 21.53c yields an expected response of

$$
R _ {I} = 1. 3 9 \cdot 1. 7 0 \left(\frac {3 + 0 . 5 4 2 (1 - 3)}{\sqrt {3 ^ {2} + 0 . 3 2 6 \left(1 ^ {2} - 3 ^ {2}\right)}}\right) = 1. 7 9
$$

This is not as efficient as strict among-family selection (where $ R_{b}=2.15 $; see Example 21.4). Likewise, the response under individual (i.e., mass) selection is $ R_{m}=\bar{\iota}_{m}\sigma_{A}h=2.36. $ Because individual selection is a special case of the general index, we can always choose the index weights to give at least as large an expected response as individual selection. For example, placing twice the weight on family means relative to within-family deviations $ ( b_{1}= 1, b_{2}=2) $ , returns an expected response of R=2.59, which is 110% of the expected response under individual selection.

## Lush's Optimal Index

As the previous example shows, by making the appropriate choice of index weights, we can always obtain a response at least as large as that expected under mass selection. Note from Equation 21.51 that $ \sigma_{A} $ and $ \bar{\iota}_{I} $ remain constant under different index weights, implying that the maximal response occurs if we choose the weights that maximize the correlation, $ \rho(I,y) $ between the index and offspring value (Equation 21.5 shows that this is equivalent to maximizing the correlation, $ \rho(I,A) $ , between the index and breeding values of an individual). Lush (1947) showed that the resulting optimal index weights are

$$
b _ {1} = \frac {1 - r}{1 - t} \quad \mathrm {a n d} \quad b _ {2} = \frac {1 + (n - 1) r}{1 + (n - 1) t}
$$

The formal derivation (which follows from a Smith-Hazel index; Example A6.8) is given in our general treatment of index selection in Volume 3. We refer to the family index using these weights as the Lush index. Note that the weight $ ( b_{1} ) $ on family deviations is independent of the family size $ ( n ) $ , while the weight on the family mean $ ( b_{2} ) $ depends on n, approaching $ r/t $ for large families. Figure 21.7 plots the ratio of among- to within-family weights $ ( b_{2}/b_{1} ) $ for the Lush index as a function of t and n. For small between-sib correlations $ ( t ) $ , more weight is placed on family mean, while more weight is placed on within-family deviation when the sib correlation is large.

We can rearrange the Lush index as $ I_{L}=z_{ij}+B_{L}\bar{z}_{i} $ where substituting Equation 21.54 into Equation 21.50c returns

$$
B _ {L} = \frac {(r - t) n}{(1 - r) [ 1 + (n - 1) t ]}
$$

Using the optimal weights, Equation 21.53c simplifies to yield the response under Lush's index as ___.

$$
R _ {L I} = \bar {\imath} \sigma_ {A} h \sqrt {1 + \frac {(r - t) ^ {2} (n - 1)}{(1 - t) [ 1 + (n - 1) t ]}}
$$

![](page=45,bbox=[289, 117, 843, 485])

<div align="center">

Figure 21.7 The ratio, $ b_{2}/b_{1} $ of the weights placed on the among- $ (b_{2}) $ relative to within $ (b_{1}) $ family weights under the optimal Lush index (Equation 21.54). Individual selection corresponds to $ b_{2}/b_{1}=1 $ . These optimal weights are a function of the phenotypic correlation, t between sibs and the number, n, of sibs per family.

</div>

The resulting increase in response over that expected under individual selection $ ( R_{m}=\bar{\iota}\sigma_{A}h; $ Equation 13.6b) is thus

$$
\frac {R _ {L I}}{R _ {m}} = \sqrt {1 + \frac {(r - t) ^ {2} (n - 1)}{(1 - t) [ 1 + (n - 1) t ]}} \geq 1
$$

Figure 21.8 plots Equation 21.56b as a function of t and n for half- and full-sibs. Because the quantity in the square root exceeds one, the expected response under Lush's index exceeds the response under individual selection, except at r = t (i.e., t = 0.25 for half-sibs, t = 0.5 for full-sibs), in which case the expected responses are equal. For large values of n, Equation 21.56b converges to

$$
\frac {R _ {L I}}{R _ {m}} = \sqrt {1 + \frac {(r - t) ^ {2}}{(1 - t) t}}
$$

which can take on large values for t near zero or one, as seen by the roughly U-shaped plots in Figure 21.8.

Example 21.12. Recalling (Example 21.4) that $ t=0.265 $ and $ r=0.5 $ for full-sibs in Clayton et al.'s (1957) bristle experiments, the resulting Lush weight on family deviations becomes

$$
b _ {1} = \frac {1 - r}{1 - t} = \frac {1 - 0 . 5}{1 - 0 . 2 6 5} = 0. 6 8 0
$$

![](page=46,bbox=[166, 121, 680, 355])

![](page=46,bbox=[165, 368, 684, 624])

<div align="center">

Figure 21.8 Response of Lush's index relative to individual selection, as a function of the number of sibs, n, for full-sibs (r=1/2) and half-sibs (r=1/4). Except at r=t (where the expected responses are equal), Lush's index results in a larger expected response than individual selection.

</div>

If we further recall that the family size was n=12, the optimal weight on family means becomes

$$
b _ {2} = \frac {1 + (n - 1) r}{1 + (n - 1) t} = \frac {1 + (1 2 - 1) 0 . 5}{1 + (1 2 - 1) 0 . 2 6 5} = 1. 6 6
$$

We can rescale the weights as $ b_{1}=1 $ and $ b_{2}=1.66/0.680=2.44 $ , with Equation 21.53c returning an expected response of

$$
R _ {L I} = \bar {\iota} _ {L I} \sigma_ {A} h \rho (I, y) = 1. 3 9 \cdot 1. 7 0 \cdot \left(\frac {1 + 0 . 5 4 2 (2 . 4 4 - 1)}{\sqrt {1 ^ {2} + 0 . 3 2 6 \left(2 . 4 4 ^ {2} - 1 ^ {2}\right)}}\right) = 2. 6 0
$$

The expected response under individual selection was $ R_{m}=2. 3 6 $ (Example 21.11), so the

expected response under the Lush index is 10% greater than that of mass selection.

The Lush index weights change with t and r, and so may have to be periodically updated as changes in the genetic variance change t and as inbreeding changes r (Chapters 16, 23, and 24). In particular, both drift and gametic-phase disequilibrium can be important when several generations of selection are considered (Chapter 16). As selection proceeds, both these forces increase the relative importance of within-family selection over among-family selection (Chapters 16 and 24). This results in individual values given increased weight and family means given decreased weight.

Specifically, the amount of within-family additive variance (in the absence of drift or inbreeding) remains at $ \sigma_{a}^{2}/2 $ (half the genic variance, the value of $ \sigma_{A}^{2} $ in the absence of LD), while the amount of among-family variance is $ \sigma_{a}^{2}/2+d $ , where d < 0 (Chapter 16). Hence, LD has no impact on the within-family component of additive variance, but it decreases the among-family component. Wray and Hill (1989) noted that while the relative efficiency of index selection over individual selection may be greatly diminished by gametic-phase disequilibrium, the relative rankings of the methods still hold.

A concern with any index is that the population parameters have to be correctly estimated, otherwise the index constructed from these estimates will have incorrect weights and be less than optimal (Volume 3). Fortunately, only the intraclass correlation, t, must be estimated for the Lush index, and Sales and Hill (1976) showed that the efficiency of index selection is quite robust to estimation errors in t (as initially suggested by Lush 1947).

Nonetheless, given some of these concerns, it is not surprising that experimental verification of the advantage of the Lush index over individual or family selection is mixed. Further, the common problem of low statistical power in most selection experiments due to small sample sizes makes negative results difficult to interpret (Chapter 18). McBride and Robertson (1963) and Avalos and Hill (1981) found that index selection resulted in a larger response than individual selection for abdominal bristles in Drosophila melanogaster. More conclusive results, also on Drosophila bristle number, were those of James (cited in Frankham 1982), who found that the observed increase in response under index selection (relative to mass selection) was 133% $ \pm 9. 7 \% $ and 111% $ \pm 7 \% $ in two replicates, consistent with the expected increase of 121%. Results for selection for egg production in poultry were less conclusive, and although Kinney et al. (1970) found that individual selection gave a larger (but not significant) response than family index selection, while Garwood and Lowe (1981) found that index selection gave a larger response (again not significant) than family selection. Work on larval and pupal weight in Tribolium showed similar mixed results, as Wilson (1974) found that individual selection gave the largest response, while Campo and Tagarro (1977) did not find any significant differences (index selection gave a larger response in a replicate with large family size, while individual selection showed the larger response in a replicate with small family size).

We note in passing that a more general family index was considered by Osborne (1957a, 1957b) for the nested-sib design, which separately weights information from full- and half-sib families. If $ z_{ijk} $ denotes the kth full-sib from dam j and sire i, an index weighting both half- and full-sib information is

$$
I = b _ {1} \left(z _ {i j k} - \bar {z} _ {i j}\right) + b _ {2} \left(\bar {z} _ {i j} - \bar {z} _ {i .}\right) + b _ {3} \bar {z} _ {i}.
$$

where $ b_{1} $ is the weight on the deviation within a full-sib family, $ b_{2} $ is the weight on the deviation among dam-family means within a sire, and $ b_{3} $ is the sire weight (half-sib means). Volume 3 examines this, and more general indices, in much greater detail.

## Correcting the Selection Intensity for Correlated Variables

As mentioned previously, expressions for the selection intensity in finite populations make the assumption that the order statistics are uncorrelated. However, the selection of multiple

individuals from the same family results in correlations among the order statistics due to the correlation between sibs. Our treatment of this issue follows that of Hill (1976, 1977b).

Suppose the population from which individuals are drawn consists of m families, each with n sibs, for a total of M = mn measured individuals. If phenotypic values are uncorrelated among all members of the sample (the sib correlation, t, is zero), Burrow's correction (Equation 14.4b) yields a finite population size-adjusted selection intensity of

$$
\bar {\iota} _ {(K, M)} = \bar {\iota} _ {p} - \frac {1 - p}{2 \bar {\iota} _ {p} p (M + 1)}
$$

where a fraction, $ p=K/M $ of the population is saved and $ \bar{\iota}_{p} $ is the infinite-population selection intensity associated with the fraction p saved (Equation 14.3a). When some members are correlated, this reduces the effective number of independent variables to some value below M. This value ranges from m n=M, with no correlation between sibs $ (t=0) $ ,to m, with a perfect correlation between sibs $ (t=1) $ .Using this observation, Hill (1976) suggested a linear approximation for the effective number, $ M_{e} $ ,of independent variables of

$$
M _ {e} = M (1 - t) + m t
$$

Substituting into Burrow's correction gives an expected selection intensity adjusted for correlations of approximately

$$
\bar {\iota} _ {(K, M)} (t) = \bar {\iota} _ {p} - \frac {1 - p}{2 \bar {\iota} _ {p} p [ M (1 - t) + m t + 1 ]}
$$

Note that $ \bar{i} $ decreases as t increases. Simulation studies by Hill showed that this is a reasonable approximation, and Hill (1976) provided tables of exact values (over a limited set of n and t values). An alternative approximation was offered by Rawlings (1976), while Tong (1982) and Meuwissen (1991), respectively, considered contributions from unequal family size and under a nested full-sib-half-sib design.

The effect of sib-correlations on the selection intensity for individual selection is generally small, as t is typically less that 0.5, and has only a modest effect on reducing $ \bar{i} $ . In contrast, the presence of the family mean, $ \overline{{z}}_{i} $ , in the index scores greatly inflates the correlation between the sib index values, I, over the correlation among phenotypic values, z. Hill (1976) showed that if selection occurs on the index $ I=z_{ij}+B\overline{{z}}_{i} $ (Equation 21.50b), the intraclass correlation, $ \tau $ , among the index values of sibs is given by

$$
\tau = 1 - \frac {n (1 - t)}{n + B (2 + B) [ 1 + (n - 1) t ]}
$$

where $ t $ is the intraclass correlation of individual phenotypic values among sibs. Note that for large $ B,\tau $ approaches 1.0. Hence, for schemes that place considerable weight on family means, the index scores for sibs within a family are almost perfectly corrected, and the effective number of independent order statistics approaches the number of families chosen. This is very reasonable, as $ I $ approaches $ \overline{z}_{i} $ for large $ B $ , which is equivalent to among-family selection, giving the number of independent order statistics as the number of families, $ m. $

Using the value of B (from Equation 21.55) under Lush index weights, Hill (1976) showed (for large n) that

$$
\tau \simeq \left\{ \begin{array}{l l} 1 - t & \mathrm {f u l l - s i b s} \\ \frac {1 - t}{1 + 8 t} \simeq \frac {1}{1 + 2 h ^ {2}} & \mathrm {h a l f - s i b s} \end{array} \right.
$$

Example 21.13. Once again, consider Clayton et al's (1957) experiment on Drosophila bristle number. From Example 21.12, the Lush index weights are $ b_{2}/b_{1}=2.44 $ , with Equation 21.50c yielding $ B=b_{2}/b_{1}-1=1.44 $ . Recalling that $ t=0.265 $ and n=12, Equation 21.58a returns the correlation, $ \tau $ , among the index values of sibs as

$$
\tau = 1 - \frac {1 2 (1 - 0 . 2 6 5)}{1 2 + 1 . 4 4 (2 + 1 . 4 4) [ 1 + (1 2 - 1) 0 . 2 6 5 ]} = 0. 7 2
$$

which is 2.7 times the correlation, t, among sib phenotypic values. Note that under strict family selection $ (\tau=1) $ , the correlation among the index value increases to 3.8 times the sib phenotypic correlation.

Suppose we select on a Lush index using four families $ ( m=4 ) $ . The resulting total number of individuals becomes $ N=1 2 \cdot 4=4 8 $ , while Equation 21.57a gives the effective number of independent variables as

$$
M _ {e} = 4 8 (1 - 0. 7 2) + 4 \cdot 0. 7 2 = 1 6. 3
$$

which is just 34% of the actual number of total individuals. Because $ p=0.2 $ (implying $ \bar{i}_{p}=1.40 $ ), Equation 21.57b yields a corrected selection intensity of

$$
\bar {\iota} = 1. 4 0 - \frac {1 - 0 . 2}{2 \cdot 1 . 4 0 \cdot 0 . 2 \cdot (1 6 . 3 + 1)} = 1. 3 2
$$

or a reduction of $ \sim 6\% $.