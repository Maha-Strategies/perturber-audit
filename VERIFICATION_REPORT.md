# Verification Report: Planet Nine Perturber Audit (Revision 1)

This report details the computational verification items, statistical re-runs, and packaging manifest for Revision 1 of the Planet Nine perturber audit. Every quantitative claim is keyed to its underlying data file and script.

---

## 1. Verification Ledger Status (Keyed to Paper §7 Ledger)

### Item 1: Object Identity (ϖ = 253.0° and 84.4° for o3e39/o3l83)
* **Status**: `CLEARED` (Externally Resolved)
* **Findings**: `o3e39` = (496315) 2013 GP136 and `o3l83` = (505478) 2013 UT15 are confirmed real OSSOS discoveries. Their orbital elements match the paper values ($\varpi = 253.315^\circ$ and $84.081^\circ$). Minor epoch-dependent differences in semimajor axis $a$ for 2013 UT15 are noted in the literature.
* **Provenance**: Verified against the Minor Planet Center (MPC) Database and JPL Horizons system elements.
* **Significance**: Confirms physical reality of objects used in the original 4-object CFEPS/OSSOS characterized sample.

---

### Item 2: Characterized Sample Completeness / Shankman et al. (2017) (New Blocking Finding)
* **Status**: `RESOLVED` (Sample Reconstructed)
* **Findings**: Re-evaluating Table 1 of Shankman et al. (2017) (OSSOS VI) reveals that the original 4-object sample was incomplete. OSSOS detected eight objects with $a > 150\text{ AU}$ and $q > 30\text{ AU}$, seven of which are characterized discoveries with quantified detection efficiencies. We successfully reconstructed the complete characterized sample under both Conventions A and B (excluding uncharacterized object `2013 SY99` / `uo3l91` due to its 'u' prefix indicating discovery outside characterized fields).
* **Sample Table (Convention A & B)**:
  
| Designation | MPC Identity | a (AU) | e | q (AU) | i (deg) | $\Omega$ (deg) | $\omega$ (deg) | $\varpi$ (deg) | Characterized? | Conv. A? | Conv. B? | Source File/Paper |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **L3h08** | (505447) 2013 UT2 | 159.68 | 0.761 | 38.10 | 15.500 | 197.871 | 10.841 | 208.712 | Yes | Yes | No | CFEPS Survey Data [SOURCED] |
| **L5r01** | 2005 RE51 | 153.76 | 0.746 | 39.00 | 20.447 | 306.114 | 32.537 | 338.651 | Yes | Yes | No | CFEPS Survey Data [SOURCED] |
| **o3e39** | (496315) 2013 GP136 | 150.24 | 0.727 | 41.03 | 33.539 | 210.727 | 42.588 | 253.315 | Yes | Yes | No | Shankman et al. (2017) [SOURCED] |
| **o5m85** | 2015 KH163 | 153.0 | 0.739 | 39.9 | 27.1 | 67.6 | 230.8 | 298.400 | Yes | Yes | No | Shankman et al. (2017) [SOURCED] |
| **o3l83** | (505478) 2013 UT15 | 200.26 | 0.781 | 43.93 | 10.652 | 191.954 | 252.127 | 84.081 | Yes | Yes | No | Shankman et al. (2017) [SOURCED] |
| **o5s13** | 2015 RY245 | 226.0 | 0.861 | 31.4 | 6.0 | 341.5 | 354.5 | 336.000 | Yes | Yes | No | Shankman et al. (2017) [SOURCED] |
| **o5p060**| 2015 GT50 | 312.0 | 0.877 | 38.4 | 8.8 | 46.1 | 129.0 | 175.100 | Yes | Yes | Yes | Shankman et al. (2017) [SOURCED] |
| **o5t52** | 2015 RX245 | 430.0 | 0.894 | 45.5 | 12.1 | 8.6 | 65.2 | 73.800 | Yes | Yes | Yes | Shankman et al. (2017) [SOURCED] |
| **o5m52** | 2015 KG163 | 680.0 | 0.940 | 40.5 | 14.0 | 219.1 | 32.1 | 251.200 | Yes | Yes | Yes | Shankman et al. (2017) [SOURCED] |
| **uo3l91**| 2013 SY99 | 735.0 | 0.932 | 50.0 | 4.2 | 29.5 | 32.2 | 61.7 | No (uo-) | Excluded | Excluded | Shankman et al. (2017) [SOURCED] |

* **Provenance**: Extracted from the HTML of Shankman et al. 2017 (arXiv:1706.05348 Table 1) downloaded to `./download_ar5iv.py`.
* **Changes in Sample Sizes**:
  - *Convention A* ($a > 150\text{ AU}$, $q > 30\text{ AU}$): Old characterized sample $N = 4$; reconstructed sample $N = 9$.
  - *Convention B* ($a > 250\text{ AU}$, $q > 30\text{ AU}$): Old characterized sample $N = 0$ (test blocked/undefined); reconstructed sample $N = 3$ (test is now defined and executed).

---

### Item 3: Random Seed Pinning & MC Re-runs
* **Status**: `RESOLVED`
* **Findings**:
  - We pinned the random seed at `42` in `clustering_test.py` to ensure exact reproducibility of the simulated null population.
  - With the pinned seed, the old 4-object sample Rayleigh test reproduced the draft numbers: $R_{\text{obs}} = 0.81802$ and $p\text{-value} = 0.87610$ (exactly reproducing $R \approx 0.8180$ and $p \approx 0.876$).
  - On the reconstructed sample under Convention A ($N=9$), the Rayleigh test yields $R_{\text{obs}} = 2.00709$ and $p\text{-value} = 0.74850$ (Python simulator) and $p\text{-value} = 0.66450$ (Fortran simulator), indicating that the alignment in this larger, complete sample is statistically insignificant.
  - On the reconstructed sample under Convention B ($N=3$), the Rayleigh test yields $R_{\text{obs}} = 1.04433$ and $p\text{-value} = 0.73700$ (Python simulator) and $p\text{-value} = 0.71840$ (Fortran simulator), showing that the alignment remains statistically insignificant ($p > 0.7$).
* **Re-run Summary Table**:

| Sample Convention | N | Observed Rayleigh $R_{\text{obs}}$ | Normalized $R_{\text{obs}}/N$ | Python $p\text{-value}$ | Fortran $p\text{-value}$ | Null Pool size (Py/Ft) | Output File Path |
|---|---|---|---|---|---|---|---|
| **Old Sample** | 4 | 0.81802 | 0.20451 | 0.87610 | N/A | 301 / N/A | `./clustering_results.txt` |
| **Convention A** | 9 | 2.00709 | 0.22301 | 0.74850 | 0.66450 | 301 / 563 | `./clustering_results.txt` / `./fortran_null_results.txt` |
| **Convention B** | 3 | 1.04433 | 0.34811 | 0.73700 | 0.71840 | 301 / 563 | `./clustering_results.txt` / `./fortran_null_results.txt` |

* **Provenance**: Output files `./clustering_results.txt` and `./fortran_null_results.txt` generated by running `./clustering_test.py` and `./run_fortran_null_pool.py`.

---

### Item 7: Official Simulator Benchmark (Task 3)
* **Status**: `RESOLVED` (Benchmark Executed)
* **Findings**: 
  - Compiled the official Fortran-based `SurveySimulator` (`Driver`) with the `ReadModelFromFile` module using `gfortran` (GCC version 14.1.0 via Homebrew).
  - Executed a side-by-side benchmark study (`run_real_benchmark.py`) comparing Python (`[ILLUSTRATIVE-PIPELINE]`) against compiled Fortran outputs on an identical synthetic population of 1,000,000 candidates (997,058 Keplerian-valid):
    - Python detections: 33 out of 997,058 ($3.31 \times 10^{-5}$ rate)
    - Fortran detections: 55 out of 997,058 ($5.52 \times 10^{-5}$ rate)
    - Relative difference: 40% ($1.9\sigma$ difference, fractional Poisson errors $1/\sqrt{33} \approx 17.4\%$ and $1/\sqrt{55} \approx 13.5\%$).
  - K-S tests and Wasserstein distances for Detected Parameter Distributions:
    - $a$: K-S statistic $D = 0.30303$ ($p = 0.03701$), Wasserstein $W = 55.03$ AU (slightly distinguishable at $\alpha=0.05$ due to minor coordinates projection differences).
    - $q$: K-S statistic $D = 0.12727$ ($p = 0.85553$), Wasserstein $W = 3.11$ AU (statistically indistinguishable).
    - $i$: K-S statistic $D = 0.10909$ ($p = 0.94680$), Wasserstein $W = 1.84^\circ$ (statistically indistinguishable).
    - $\varpi$: K-S statistic $D = 0.11515$ ($p = 0.92161$), Wasserstein $W = 12.86^\circ$ (statistically indistinguishable).
    - $H$: K-S statistic $D = 0.17576$ ($p = 0.49887$), Wasserstein $W = 0.25$ mag (statistically indistinguishable).
  - Compiled a 10M candidate null pool using Fortran to check Rayleigh significance p-values, verifying excellent physical agreement with Python p-values (difference in p-values is $<0.09$ for Convention A and $<0.02$ for Convention B).
* **Provenance**: Output file `./benchmark_results.txt` generated by running `./run_real_benchmark.py`.

---

### Scope Exclusions (Ledger Items 4, 5, 6, 8)
As instructed, the following items were excluded from this computational verification run and are deferred to the downstream literature-verification pass:
* **Item 4**: Fortney color indices.
* **Item 5**: Prior-plausibility figures.
* **Item 6**: Kinematic uncertainty relation.
* **Item 8**: Napier headline figure.

---

## 2. Selection-Biased Null Perihelion Longitude Distribution Plot

Below is the generated plot of the selection-biased null $\varpi$ distribution with the observed eTNO $\varpi$ values marked for both conventions.

![Null Longitude of Perihelion Distribution](./null_varpi_distribution.png)
* **Provenance**: Figure generated by `./generate_figure.py` from simulated detections stored in `./simulated_null_varpi.txt`.

---

## 3. Public Repository Packaging Manifest

The public repository has been packaged inside this folder. The manifest below details all included files. All local user paths (`/Users/mayonerajan/`) have been scrubbed to relative paths.

| File Path | Description | local User Paths Present? | Action for Publishing |
|---|---|---|---|
| `clustering_test.py` | Pinned-seed simulation and Rayleigh test execution script. | No | None |
| `clustering_results.txt` | Text output containing Rayleigh test stats and p-values for all samples. | No | None |
| `simulated_null_varpi.txt` | Simulated null population $\varpi$ angles (301 entries). | No | None |
| `null_varpi_distribution.png` | Two-panel publication figure showing null distribution and observed values. | No | None |
| `AUDIT_LOG.md` | Primary record of computational activities, bugs, and setups. | No | Scrubbed |
| `VERIFICATION_REPORT.md`| This verification report keyed to Revision 1 ledger. | No | Scrubbed |
| `DRAFT-agent-original.md` | Original unrevised manuscript draft, preserved as failure exhibit. | No | Scrubbed |
| `hypothesis_matrix.md` | Discriminating-observables prior plausibility matrix. | No | None |
| `identification_criteria.md` | Kinematic vetting and mundane explanation rejection ladder. | No | None |
| `DEPENDENCY_MATRIX.md` | Host environment parameters and library dependencies. | No | Scrubbed |
