# Candidate Identification and Vetting Criteria

This document details the kinematics, photometrics, and logical decision gates required to vet a Planet Nine candidate.

## 1. Kinematic Vetting Criteria

At opposition, the apparent motion of a trans-Neptunian object is dominated by Earth's parallax. The angular motion rate $\mu$ is inversely proportional to distance $d$:
$$\mu \approx \frac{3548}{d} \text{ arcsec/day} \approx \frac{147.8}{d} \text{ arcsec/hour}$$

Below are the derived kinematic rates for candidates at 300, 500, and 800 AU:

| Distance (AU) | Parallax Rate (arcsec/day) | Orbital Motion (arcsec/day) | Total Apparent Rate Range (arcsec/day) | Rate Range (arcsec/hour) | Distance Uncertainty (%) |
| --- | --- | --- | --- | --- | --- |
| 300 | 11.826 | 0.683 | 11.143 - 12.509 | 0.464 - 0.521 | 5.8% |
| 500 | 7.096 | 0.317 | 6.778 - 7.413 | 0.282 - 0.309 | 4.5% |
| 800 | 4.435 | 0.157 | 4.278 - 4.591 | 0.178 - 0.191 | 3.5% |

### Distance Estimation Inverse Relation:
Given an observed apparent motion rate $\mu_{\text{obs}}$ (arcsec/day) near opposition, the distance estimate is:
$$d \approx \frac{3548}{\mu_{\text{obs}}} \text{ AU}$$
with a fundamental systematic uncertainty of $\sigma_d / d \approx 1 / \sqrt{d}$ due to the unknown orbital inclination and eccentricity projection. [SOURCED: Batygin et al. 2019]

## 2. Photometric Vetting Criteria

* **Apparent Magnitude Window**: 
  * At perihelion ($q \approx 300$ AU): $V/r \approx 21-22$ mag [SOURCED: Siraj et al. 2025]
  * At aphelion ($Q \approx 500-800$ AU): $V/r \approx 24-25.5$ mag [SOURCED: Brown & Batygin 2021]
* **Colors (Methane-Condensation Atmosphere)**: Fortney et al. (2016) model predicts:
  * $(g - r) \approx 0.5 - 0.9$ (somewhat red, Uranus-like) [SOURCED: Fortney et al. 2016]
  * $(r - i) \approx 0.2 - 0.5$ [SOURCED: Fortney et al. 2016]
  * $(i - z) \approx -0.2 - 0.2$ (blue color in near-IR due to methane absorption) [SOURCED: Fortney et al. 2016]

## 3. The Mundane-Explanation Rejection Ladder

Before a candidate is declared a Planet Nine candidate, it must survive the following veto gates:

1. **Gate 1: Image Artifact / Transient Ghost**
   * *Veto Test*: Must be detected on at least 3 independent exposures on the same night and follow a linear track consistent with sidereal motion. Must be recovered on subsequent nights. [ILLUSTRATIVE]
2. **Gate 2: Known Object Match**
   * *Veto Test*: Query MPC and JPL SSD databases for matching ephemerides. Must not match any known TNO, Centaur, main-belt asteroid, or comet. [ILLUSTRATIVE]
3. **Gate 3: Variable Star / Flaring Source**
   * *Veto Test*: Cross-check coordinates against Gaia DR3 stellar catalogs. If a star is at the exact location, verify that the candidate has moved away in subsequent frames. [ILLUSTRATIVE]
4. **Gate 4: Ordinary TNO (30-50 AU)**
   * *Veto Test*: Ordinary TNOs have apparent motion rates of $\mu \approx 50-100$ arcsec/day at opposition. The candidate must have $\mu \le 12$ arcsec/day (confirming $d \ge 300$ AU). [SOURCED: Batygin et al. 2019]
5. **Gate 5: Stationary Asteroid Mimic**
   * *Veto Test*: Main-belt asteroids near their stationary points can briefly match TNO motion rates. Observe the candidate for at least 7-14 days. An asteroid's rate will rapidly accelerate and diverge, whereas a distant TNO will maintain a steady rate. [ILLUSTRATIVE]

## 4. Composition Adjudication Decision Tree

Once a candidate survives the mundane-explanation ladder, its physical composition (Planet vs. PBH) is adjudicated using electromagnetic and gravitational signatures:

| Path / Observation | Reflectivity (Optical) | Thermal (Infrared) | Gravitational / Parallax | Gamma-RayPoint-Source | Adjudicated Identity |
| --- | --- | --- | --- | --- | --- |
| **Path A** | Detected ($r \approx 21-25.5$ mag) | Detected (Internal cooling flux) | Detected ($d \approx 300-800$ AU) | Null (No WIMP annihilation) | **H1a: Distant Planet** [SOURCED: Fortney et al. 2016; Brown & Batygin 2021] |
| **Path B** | Null ($r > 27$ mag depth) | Null (Hawking temp negligible) | Detected ($d \approx 300-800$ AU) | Detected (WIMP halo annihilation) | **H1b: Primordial Black Hole (PBH)** [SOURCED: Scholtz & Unwin 2019; Witten 2020] |
| **Path C** | Null ($r > 27$ mag depth) | Null | Detected ($d \approx 300-800$ AU) | Null | **H1b: PBH (no WIMP halo)** or **H1c: Dark/Compact Candidate** [SOURCED: Scholtz & Unwin 2019] |
