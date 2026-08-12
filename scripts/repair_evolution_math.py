r"""Repair Evolution math spans verified against the local chapter PDFs.

The source OCR contains a small number of truncated formulas and row separators
misread as ``\ $``. Each repair is pinned to the SHA-256 of the complete old
block so the script fails closed when structured data drifts. A provenance
report with chapter-PDF hashes and page locators is written under ``tmp/``.

These repairs make the chapter delivery mathematically parseable. They do not
replace the full-book accuracy audit, which remains blocked until the complete
authoritative Evolution master PDF is supplied.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "data" / "structured"
REPORT = ROOT / "tmp" / "book_audits" / "Evolution" / "math_corrections" / "report.json"


@dataclass(frozen=True)
class Repair:
    filename: str
    block_index: int
    old_sha256: str
    pdf_page: int
    replacements: tuple[tuple[str, str], ...]


REPAIRS = (
    Repair(
        "Evolution_appendix1_004.json",
        0,
        "c2ef599c2adbf18fa916233105c3f9275c8991f008ddf233fd7a263c959cf173",
        2,
        ((
            "satisfies the Kolmogorov forward equation (or KFE) $$ \\",
            "satisfies the Kolmogorov forward equation (or KFE) $$ \\frac{\\partial\\varphi(x,t,p)}{\\partial t}=\\frac{1}{2}\\frac{\\partial^{2}[v(x)\\varphi(x,t,p)]}{\\partial x^{2}}-\\frac{\\partial[m(x)\\varphi(x,t,p)]}{\\partial x} $$",
        ),),
    ),
    Repair(
        "Evolution_appendix1_008.json",
        3,
        "e5c7ea138eed1345b61761647f2b4601f3d4452b183e068d555ac73a539222ab",
        6,
        ((
            "defined by the indefinite integral $$ G(x)=\\exp\\left[-2\\",
            "defined by the indefinite integral $$ G(x)=\\exp\\left[-2\\int^{x}\\frac{m(y)}{v(y)}dy\\right] $$",
        ),),
    ),
    Repair(
        "Evolution_chapter6_003.json",
        1,
        "7bc2ac4945730cc2b6e3d4b82c8314b7b3538bf418427e1f028ed1dc0e9d628b",
        3,
        (("Price's Theorem, $", "Price's Theorem, $R_z = \\sigma(w_i, z_i) + E(w_i \\bar{\\delta}_i)$."),),
    ),
    Repair(
        "Evolution_chapter9_033.json",
        0,
        "956db89e86f46b5bcb864cdaf2a1bad7a1f7f7fd959df8e211cd0006e1b4367c",
        36,
        ((
            "$$ [n/2]=\\left\\{\\begin{array}{l}n/2for n even\\ $ n-1)/2for n odd\\end{array}\\right. $$",
            "$$ [n/2]=\\left\\{\\begin{array}{ll}n/2&\\text{for }n\\text{ even}\\\\(n-1)/2&\\text{for }n\\text{ odd}\\end{array}\\right. $$",
        ),),
    ),
    Repair(
        "Evolution_chapter10_009.json",
        1,
        "5ce019de699373eb206bc69f0255dc886a09883d68f9ac40f4b54259ae1b14fc",
        9,
        (("and thus, under neutrality, we also have $$", "and thus, under neutrality, we also have $$ \\frac{P_a}{D_a}=\\frac{P_s}{D_s} $$"),),
    ),
    Repair(
        "Evolution_chapter12_007.json",
        4,
        "2f97171a6da8dd932a08bf4e64a51976ce2c5ebea37156b8eeb2f5e2717d9603",
        9,
        (("natural populations. $$", "natural populations."),),
    ),
    Repair(
        "Evolution_chapter12_013.json",
        1,
        "8502c56868fea36e461f4890a6757217c80211444f35365bedaeded0d2026cbe",
        18,
        ((
            "$$ \\begin{align*}N_{e,u}\\le{t\\cdot h^2\\cdot2.24^2\\over d_*\\over=5.02\\cdot{t\\over d_*\\over=}\\end{align*} $$",
            "$$ N_{e,u}\\leq\\frac{t\\cdot h^2\\cdot2.24^2}{d_*^2}=5.02\\cdot\\frac{t h^2}{d_*^2} $$",
        ),),
    ),
    Repair(
        "Evolution_chapter12_027.json",
        0,
        "b91c04828d7b0fab69dde1a5ef54f2bb0f7ff33be21b3fceb8019a3895c4f0be",
        38,
        ((
            "$$ [n/2]=\\left\\{\\begin{array}{ll}(n/2)+1&for n even\\ $ n+1)/2&for n odd\\end{array}\\right. $$",
            "$$ [n/2]=\\left\\{\\begin{array}{ll}(n/2)+1&\\text{for }n\\text{ even}\\\\(n+1)/2&\\text{for }n\\text{ odd}\\end{array}\\right. $$",
        ),),
    ),
    Repair(
        "Evolution_chapter14_008.json",
        6,
        "ed314dfd414efa66901735d0158d4a99f84d586182f75cf71914e158dcd1ca75",
        15,
        (("$ \\logit(p) = z $", "$ \\operatorname{logit}(p) = z $"),),
    ),
    Repair(
        "Evolution_chapter15_010.json",
        18,
        "e62e157fc1ba5022030885d102213b1b5267ca6ce64a11387e5210a6855786e6",
        18,
        ((
            "$$ \\begin{align*}R(t)+R^*=t h^2\\, S\\begin{array}{c}2\\ $ 1-m)(2-m)\\end{array}\\end{align*} $$",
            "$$ R(t)+R^*=t h^2 S\\frac{2}{(1-m)(2-m)} $$",
        ),),
    ),
    Repair(
        "Evolution_chapter18_008.json",
        0,
        "d064599b615d0af809d84757186710a954f780f0afcccd3a1584552e3397263c",
        10,
        ((
            "$$ \\mathrm{Var}\\left[\\widehat{b}_{C}(\\mathrm{OLS})\\right]=\\sigma_{e}^{2}\\",
            "$$ \\mathrm{Var}\\left[\\widehat{b}_{C}(\\mathrm{OLS})\\right]=\\sigma_{e}^{2}(\\mathbf{X}^{T}\\mathbf{X})^{-1}=\\sigma_{e}^{2}(\\mathbf{S}^{T}\\mathbf{S})^{-1}=\\sigma_{e}^{2}\\bigg/\\sum_{i=1}^{T}S_{C}^{2}(i) $$",
        ),),
    ),
    Repair(
        "Evolution_chapter19_023.json",
        1,
        "1ec844b64f8903367919c1b665f898c5f7b2cd8fc8ff6f4cb23b80c1beaf228d",
        30,
        ((
            "the posterior is often simply written as $$ p(\\boldsymbol{\\Theta}\\",
            "the posterior is often simply written as $$ p(\\boldsymbol{\\Theta}\\mid\\mathbf{y})\\propto p(\\mathbf{y}\\mid\\boldsymbol{\\Theta})p(\\boldsymbol{\\Theta}) $$",
        ),),
    ),
    Repair(
        "Evolution_chapter21_007.json",
        5,
        "7b0526533132038bf33c5fff073a32a6d4957935809a3a42fadbe79ee7a5659a",
        6,
        ((
            "$$ \\",
            "$$ \\begin{array}{ll}\\text{Individual selection (infinite population)}&\\text{Best 20\\%},\\ \\bar{\\imath}_{\\infty}=1.40\\\\\\text{Individual selection, index selection,}&\\\\\\text{family-deviations (FD) selection}&\\text{Best 20 of 100},\\ \\bar{\\imath}_{(20,100)}=1.39\\\\\\text{Among-family selection}&\\text{Best 4 of 20},\\ \\bar{\\imath}_{(4,20)}=1.33\\\\\\text{Strict within-family selection (WF)}&\\text{Best 1 of 5},\\ \\bar{\\imath}_{(1,5)}=1.16\\end{array} $$",
        ),),
    ),
    Repair(
        "Evolution_chapter21_013.json",
        0,
        "4c2bcc0e5af777e55fba7d178fa009b3a458d14125bbd4904d138c3b27388ab0",
        14,
        ((
            "$$ \\sigma(z_{ij}-\\overline{z}_{i},y\\mid\\mathcal{R}_{1})=(1-r_{n})\\left(\\sigma_{A}^{2}/2\\right)=\\left\\{\\begin{array}{ll}(1-1/n)\\left(3/8\\right)\\sigma_{A}^{2}&half-sibs\\ $ 1-1/n)\\left(\\sigma_{A}^{2}/4\\right)&full-sibs\\end{array}\\right. $$",
            "$$ \\sigma(z_{ij}-\\overline{z}_{i},y\\mid\\mathcal{R}_{1})=(1-r_{n})\\left(\\sigma_{A}^{2}/2\\right)=\\left\\{\\begin{array}{ll}(1-1/n)(3/8)\\sigma_{A}^{2}&\\text{half-sibs}\\\\(1-1/n)(\\sigma_{A}^{2}/4)&\\text{full-sibs}\\end{array}\\right. $$",
        ),),
    ),
    Repair(
        "Evolution_chapter21_024.json",
        3,
        "a814fb3ee1f1a87e59aed05030ab3cc10d6b4d2fcb333d4ffb6244a7616e37a8",
        33,
        ((
            "\\text{half-sibs(for family and sib selection;\\gamma=1/4)}\\\\&\\frac{1}{4}\\left(1-h^{2}\\right)&\\text{half-sibs(for parental and S_{1} seed selection;\\gamma=1/2)}\\\\&\\frac{1}{4}\\left(1-2h^{2}\\right)&\\text{full-sibs}(\\gamma=1/2)",
            "\\text{half-sibs (for family and sib selection; }\\gamma=1/4\\text{)}\\\\&\\frac{1}{4}\\left(1-h^{2}\\right)&\\text{half-sibs (for parental and }S_{1}\\text{ seed selection; }\\gamma=1/2\\text{)}\\\\&\\frac{1}{4}\\left(1-2h^{2}\\right)&\\text{full-sibs }(\\gamma=1/2)",
        ),),
    ),
    Repair(
        "Evolution_chapter21_028.json",
        5,
        "486c84732b59cfe87c5d26bb55daa26e35df822045126f163f6e673621044ee1",
        38,
        (
            ("$(\\sigma_GF \\times E)$", "$\\sigma_{GF \\times E}^{2}$"),
            (
                "$(\\sigma_GF \\times L', \\sigma_GF \\times Y}$, and $\\sigma_GF \\times L \\times Y$)",
                "($\\sigma_{GF \\times L}^{2}$, $\\sigma_{GF \\times Y}^{2}$, and $\\sigma_{GF \\times L \\times Y}^{2}$)",
            ),
            ("$(\\sigma_{E_p}^2)$", "$\\sigma_{E_p}^{2}$"),
        ),
    ),
    Repair(
        "Evolution_chapter21_033.json",
        3,
        "00d0d233a7fc2c422c4dc4acda31248dd64ae26db5b2e9ba788d4d2e43c519d5",
        45,
        (("(1-t)[1+(n-1)t]}\\}", "(1-t)[1+(n-1)t]}}"),),
    ),
    Repair(
        "Evolution_chapter22_019.json",
        5,
        "87464272b5688db9426e608acf47c29b3a8b575de20580c0beb0fec6fa9e6dfe",
        26,
        ((
            "\\\\=&\\begin{pmatrix}\\sigma^{2}(z)&(n-1)\\sigma(z_{i},z_{j})\\ $ n-1)\\sigma(z_{i},z_{j})&(n-1)\\left[\\sigma_{z}^{2}+(n-2)\\sigma(z_{i},z_{j})\\right]\\end{pmatrix}",
            "\\\\=&\\begin{pmatrix}\\sigma^{2}(z)&(n-1)\\sigma(z_{i},z_{j})\\\\(n-1)\\sigma(z_{i},z_{j})&(n-1)\\left[\\sigma_{z}^{2}+(n-2)\\sigma(z_{i},z_{j})\\right]\\end{pmatrix}",
        ),),
    ),
    Repair(
        "Evolution_chapter23_008.json",
        3,
        "a660cc2e585b7877f6307d17f02ba74f3326e85dda1c2298096e1042ca786f90",
        8,
        (
            ("$ \\sigma_w^2 = \\sigma_G^2_w + \\sigma_E^2_w $", "$ \\sigma_w^2 = \\sigma_{G_w}^2 + \\sigma_{E_s}^2 $"),
            ("$ \\sigma_G^2_w = \\sigma_G^2 - \\sigma_G(\\text{sibs}) $", "$ \\sigma_{G_w}^2 = \\sigma_G^2 - \\sigma_G(\\text{sibs}) $"),
            (
                "single error term, $$ \\",
                "single error term, $$ \\sigma_{e}^{2}=\\sigma_{E_c}^{2}+[\\sigma_{G_w}^{2}+\\sigma_{E_s}^{2}]/n $$",
            ),
        ),
    ),
    Repair(
        "Evolution_chapter23_017.json",
        2,
        "8bae8b049d339e208f86b91c26fb96f1f57ab80781f1cf2d45c0beb5d24a0ed6",
        23,
        (("$ \\Pr(U > x_{[1-p]}} = p $", "$ \\Pr(U > x_{[1-p]}) = p $"),),
    ),
    Repair(
        "Evolution_chapter24_023.json",
        6,
        "dab1a88ed72a8490001d01be5abdb017c80530478c9ca0ebf7314fd800647ba8",
        25,
        (("higher-order cumulants $ (K_{3} $ and above $ quantify", "higher-order cumulants ($K_{3}$ and above) quantify"),),
    ),
    Repair(
        "Evolution_chapter28_017.json",
        3,
        "03fa68df9dcca94ff9667cd50ba2fbba364c6d363e40e6662935f72900e9a5ef",
        22,
        ((
            "Turelli (1984) argued that the inequality given by Equation 28.16b is typically reversed, namely, $ \\mu_i \\ll \\sigma_{\\alpha_i}^2 / V_s $ (implying $ \\sigma_{\\alpha_i}^2 \\gg \\sigma_A(i) $), so that the Gaussian approximation is often inappropriate. His logic follows from the standard value of $ \\",
            "Turelli (1984) argued that the inequality given by Equation 28.16b is typically reversed, namely, $ \\mu_i \\ll \\sigma_{\\alpha_i}^2 / V_s $ (implying $ \\sigma_{\\alpha_i}^2 \\gg \\sigma_A^2(i) $), so that the Gaussian approximation is often inappropriate. His logic follows from the standard value of $ \\sigma_m^2 = \\sigma_E^2 / 10^3 $, which implies $ \\sigma_m^2 \\sim \\sigma_A^2 / 10^3 $ for a typical heritability ($ 0.3 \\leq h^2 \\leq 0.7 $). Because both $ \\sigma_m^2 $ and $ \\sigma_A^2 $ are the sums of single-locus effects, with equivalent loci we can replace $ \\sigma_m^2 \\simeq \\sigma_A^2 / 10^3 $ by the single-locus contributions to each component to give $ \\mu_i \\sigma_{\\alpha_i}^2 \\simeq \\sigma_A^2(i) / 10^3 $. Hence, the Gaussian approximation that $ \\sigma_{\\alpha_i}^2 \\ll \\sigma_A^2(i) $ (the variance of new mutations is much smaller than the standing variance) requires that $ \\mu_i \\cdot 10^3 \\gg 1 $ or that $ \\mu_i \\gg 10^{-3} $. This value is orders of magnitude above traditional estimates of per-locus mutation rates.",
        ),),
    ),
    Repair(
        "Evolution_chapter29_003.json",
        1,
        "183cd81e5f306777cd671d6e2951e566d505c0a93e10ae6bcea82d767930d576",
        3,
        ((
            "is calculated by $$ \\",
            "is calculated by $$ \\overline{W}_{2}=\\sum_{r=1}^{n}W_{2}(r)\\cdot w_{1}(r)\\cdot\\left(\\frac{1}{n}\\right) $$",
        ),),
    ),
    Repair(
        "Evolution_chapter30_014.json",
        1,
        "bc6012a81b5b11e11a7c1c4dc41911c7bce51d3189cd6d4f07e5cf0edf338091",
        18,
        ((
            "where $ \\theta_i = \\mathbf{e}_i^T \\mathbf{b} $ and $",
            "where $ \\theta_i = \\mathbf{e}_i^T \\mathbf{b} $ and $ y_i = \\mathbf{e}_i^T \\mathbf{z} $, with $ \\lambda_i $ and $ \\mathbf{e}_i $, respectively, representing the eigenvalues and associated unit eigenvectors of $ \\gamma $. Alternatively, if a stationary point, $ \\mathbf{z}_0 $, exists (e.g., $ \\gamma $ is nonsingular, all $ \\lambda_i \\neq 0 $), the change of variables, $ \\mathbf{y} = \\mathbf{U}^T(\\mathbf{z} - \\mathbf{z}_0) $, further removes all linear terms, so $$ w(\\mathbf{z})=w_0+\\frac{1}{2}\\mathbf{y}^T\\boldsymbol{\\Lambda}\\mathbf{y}=w_0+\\frac{1}{2}\\sum_{i=1}^{n}\\lambda_i y_i^2 $$ where $ y_i = \\mathbf{e}_i^T(\\mathbf{z} - \\mathbf{z}_0) $ and $ w_0 $ is shown by Equation 30.21b. Equation 30.26 is called the A canonical form and Equation 30.27 the B canonical form. Both forms represent a rotation of the original axes to the new set of coordinates (the canonical axes of $ \\gamma $) that align them with axes of symmetry of the original quadratic surface. The B canonical form further shifts the origin to the stationary point, $ \\mathbf{z}_0 $. Because the contribution to individual fitness from $ \\mathbf{b}^T\\mathbf{z} $ is a hyperplane, its effect is to tilt the fitness surface. The B canonical form effectively levels this tilting, allowing us to focus entirely on the curvature (quadratic) aspects of the fitness surface.",
        ),),
    ),
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_part(filename: str) -> str:
    for part in ("chapter", "appendix"):
        marker = f"_{part}"
        if marker in filename:
            number = filename.split(marker, 1)[1].split("_", 1)[0]
            return f"{part}{int(number)}"
    raise RuntimeError(f"Cannot derive Evolution source part from {filename}")


def source_pdf(part: str) -> Path:
    matches = sorted((ROOT / "data").rglob(f"Evolution_{part}.pdf"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one {part} PDF, found {len(matches)}")
    return matches[0]


def main() -> None:
    changed: dict[Path, dict] = {}
    evidence: list[dict[str, object]] = []

    for repair in REPAIRS:
        path = STRUCTURED / repair.filename
        data = changed.setdefault(path, json.loads(path.read_text(encoding="utf-8")))
        block = data["blocks"][repair.block_index]
        content = str(block.get("content") or "")

        if sha256_text(content) == repair.old_sha256:
            updated = content
            for old, new in repair.replacements:
                if updated.count(old) != 1:
                    raise RuntimeError(
                        f"Expected one repair marker in {repair.filename} block "
                        f"{repair.block_index}: {old!r}"
                    )
                updated = updated.replace(old, new)
            block["content"] = updated
        else:
            updated = content
            for _, new in repair.replacements:
                if new not in updated:
                    raise RuntimeError(
                        f"Structured block drifted: {repair.filename} block {repair.block_index}"
                    )

        pdf = source_pdf(source_part(repair.filename))
        evidence.append(
            {
                "structured_file": path.relative_to(ROOT).as_posix(),
                "block_index": repair.block_index,
                "old_sha256": repair.old_sha256,
                "new_sha256": sha256_text(str(block["content"])),
                "source_pdf": pdf.relative_to(ROOT).as_posix(),
                "source_pdf_sha256": sha256_file(pdf),
                "source_pdf_page": repair.pdf_page,
            }
        )

    for path, data in changed.items():
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(
            {
                "schema": "evolution_math_corrections.v1",
                "master_audit_state": "blocked_missing_master_pdf",
                "repair_count": len(evidence),
                "repairs": evidence,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"repaired": len(evidence), "report": str(REPORT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
