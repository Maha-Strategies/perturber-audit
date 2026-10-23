# The Perturber Question Under Audit

An agentic-AI replication of the extreme trans-Neptunian object (eTNO) orbital-clustering
test, benchmarked against the official OSSOS SurveySimulator, with a composition-agnostic
hypothesis synthesis and a documented audit of the AI instrument that performed the work.

This repository contains the reproducible code, data, and audit trail behind the paper
**"The Perturber Question Under Audit"** (Revision 1, June 2026), archived on Zenodo with a
permanent DOI **10.5281/zenodo.20719485** (https://zenodo.org/records/20719485) and written up at
**https://research.mahastrategies.com/papers/the_perturber_question**.

> **Note on scope.** This is a human-directed AI-synthesis project, not original
> astronomical research. It independently reimplements — and then benchmarks against the
> official Fortran simulator — the kind of selection-bias clustering test the field already
> performs, using publicly released survey characterizations. It treats Planet Nine's
> existence as an unproven hypothesis and reaches a *negative* result: no statistically
> significant clustering in the fully characterized CFEPS/OSSOS sample. Its distinctive
> contribution is the audit (Section 5 of the paper): the AI instrument's real
> contributions *and* its documented fabrications are reported as findings.

## What it does

1. **Reconstructs** the complete characterized CFEPS/OSSOS eTNO sample from Shankman et al.
   (2017): N = 9 under Convention A (a > 150 AU, q > 30 AU), N = 3 under Convention B
   (a > 250 AU). Cross-identifications are verified against public detection records.
2. **Implements** a Python selection-function simulator (`[ILLUSTRATIVE-PIPELINE]`) that
   parses the public pointing polygons and efficiency curves and filters 10,000,000
   synthetic scattered-disk candidates through the survey's geometry and detection
   efficiency.
3. **Tests** orbital clustering via the Rayleigh statistic on longitude of perihelion,
   with Monte Carlo p-values from the selection-biased null. Result: p = 0.748 (Python) /
   0.665 (official simulator) for Convention A — no significant clustering.
4. **Benchmarks** the Python pipeline against the official Fortran SurveySimulator
   (compiled and run on an identical population), reporting genuine disagreements: a ~40%
   absolute detection-rate gap and a marginally distinguishable semi-major-axis
   distribution (K-S p = 0.037). The pipeline is validated for the clustering conclusion,
   not for absolute completeness.
5. **Audits** the AI instrument's contributions and failure modes, including a validation
   confabulation that was caught in editorial review and replaced with the real benchmark.

## Reproducing the results

```bash
pip install -r requirements.txt
python clustering_test.py          # Python pipeline + Rayleigh tests (seed 42)
python run_real_benchmark.py       # side-by-side vs official simulator
python run_fortran_null_pool.py    # official-simulator null pool
```

The random seed is pinned (`42`) throughout, so the Python results are deterministic on the
same library versions.

**The benchmark requires the official Fortran SurveySimulator.** It is *not* vendored into
this repository (it is third-party code). Obtain and compile it from
`https://github.com/OSSOS/SurveySimulator` (`surveys` branch); CFEPS detection records are
in `CFEPS.detections` (master branch). The benchmark in this work used gfortran (GCC 14.1.0).

**The synthetic population file is regenerable, not committed.** The 10⁷-candidate synthetic
population (~68 MB) is produced deterministically by the scripts under seed 42 and is
git-ignored rather than stored; regenerate it by running the scripts above.

## Repository contents

**Scripts**
- `clustering_test.py` — Python pipeline and Rayleigh tests (seed 42)
- `run_real_benchmark.py` — side-by-side benchmark vs the official simulator
- `run_fortran_null_pool.py` — official-simulator null-pool generation
- `hypothesis_matrix.py`, `identification_criteria.py` — supporting analysis for the
  hypothesis matrix (§3) and vetting protocol (§4)

**Outputs**
- `clustering_results.txt`, `fortran_null_results.txt`, `benchmark_results.txt`
- `simulated_null_varpi.txt`, `detected_population_fortran_tracked_10m.txt`
- `null_varpi_distribution.png` — the selection-biased null ϖ distribution figure

**Paper and audit artifacts**
- `PAPER.md` — the manuscript (Revision 1, final; N = 9 analysis)
- `AUDIT_LOG.md`, `VERIFICATION_REPORT.md`, `DEPENDENCY_MATRIX.md` — the audit trail
- `DRAFT-agent-original.md` — the superseded first draft, preserved as the failure-mode
  exhibit analyzed in Section 5.2 (it is evidence, not argument)

## Sources

- Batygin, K., & Brown, M. E. (2016); Batygin et al. (2019), *Physics Reports* 805, 1.
- Brown, M. E., & Batygin, K. (2021), *AJ* 162, 219. arXiv:2108.09868.
- Napier, K. J., et al. (2021), *PSJ* 2, 59. arXiv:2102.05601.
- Petit, J.-M., et al. (2011), *AJ* 142, 131 (CFEPS).
- Shankman, C., et al. (2017), *AJ* 154, 50 (OSSOS VI). arXiv:1706.05348.
- Fortney, J. J., et al. (2016), *ApJL* 824, L25. Scholtz & Unwin (2019), arXiv:1909.11090.
- Siraj, A., Chyba, C. F., & Tremaine, S. (2025), *ApJ* 978, 139.

## Related work

This paper is part of a Planet Nine research cluster:
- *A Monte Carlo Forecast for the Detection of Planet Nine* — DOI 10.5281/zenodo.20621056

## Attribution

Architect & curator: **Mayone Maha Rajan** (Maha Strategies). AI synthesis instrument:
Google Antigravity (agentic model). Editorial and provenance-verification instrument: Claude
(Anthropic), under the architect's direction. The human architect curated the inquiry,
designed the audit protocol, and is responsible for all claims; the AI instruments assisted
with simulation, benchmarking, drafting, and provenance verification under that direction.

## License

Released under the MIT License (see `LICENSE`).
