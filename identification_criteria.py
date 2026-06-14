import os
import numpy as np

def derive_kinematics(distance_au):
    """
    Derives the expected apparent motion of a body at a given distance (AU)
    under Earth's parallax at opposition and its circular orbital velocity.
    """
    # Earth orbital velocity in AU/day
    v_earth = 0.0172  # AU/day
    # Parallax rate at opposition (rad/day)
    mu_parallax_rad_day = v_earth / distance_au
    # Convert to arcseconds per day (1 rad = 206264.806 arcsec)
    mu_parallax_arcsec_day = mu_parallax_rad_day * 206264.806
    # Convert to arcseconds per hour
    mu_parallax_arcsec_hr = mu_parallax_arcsec_day / 24.0
    
    # Orbital velocity of object (circular orbit, AU/day)
    v_orbit = v_earth / np.sqrt(distance_au)
    # Angular orbital rate (rad/day)
    mu_orbit_rad_day = v_orbit / distance_au
    # Convert to arcseconds per day
    mu_orbit_arcsec_day = mu_orbit_rad_day * 206264.806
    mu_orbit_arcsec_hr = mu_orbit_arcsec_day / 24.0
    
    # Total rate range at opposition (parallax +/- orbit)
    rate_min_day = mu_parallax_arcsec_day - mu_orbit_arcsec_day
    rate_max_day = mu_parallax_arcsec_day + mu_orbit_arcsec_day
    rate_min_hr = mu_parallax_arcsec_hr - mu_orbit_arcsec_hr
    rate_max_hr = mu_parallax_arcsec_hr + mu_orbit_arcsec_hr
    
    # Uncertainty estimate (delta_d / d ~ 1 / sqrt(d))
    uncertainty_frac = 1.0 / np.sqrt(distance_au)
    
    return {
        'parallax_day': mu_parallax_arcsec_day,
        'parallax_hr': mu_parallax_arcsec_hr,
        'orbit_day': mu_orbit_arcsec_day,
        'orbit_hr': mu_orbit_arcsec_hr,
        'rate_min_day': rate_min_day,
        'rate_max_day': rate_max_day,
        'rate_min_hr': rate_min_hr,
        'rate_max_hr': rate_max_hr,
        'uncertainty_pct': uncertainty_frac * 100.0
    }

def print_report():
    distances = [300, 500, 800]
    
    report = "# Candidate Identification and Vetting Criteria\n\n"
    report += "This document details the kinematics, photometrics, and logical decision gates required to vet a Planet Nine candidate.\n\n"
    
    report += "## 1. Kinematic Vetting Criteria\n\n"
    report += "At opposition, the apparent motion of a trans-Neptunian object is dominated by Earth's parallax. The angular motion rate $\\mu$ is inversely proportional to distance $d$:\n"
    report += "$$\\mu \\approx \\frac{3548}{d} \\text{ arcsec/day} \\approx \\frac{147.8}{d} \\text{ arcsec/hour}$$\n\n"
    report += "Below are the derived kinematic rates for candidates at 300, 500, and 800 AU:\n\n"
    
    report += "| Distance (AU) | Parallax Rate (arcsec/day) | Orbital Motion (arcsec/day) | Total Apparent Rate Range (arcsec/day) | Rate Range (arcsec/hour) | Distance Uncertainty (%) |\n"
    report += "| --- | --- | --- | --- | --- | --- |\n"
    
    for d in distances:
        k = derive_kinematics(d)
        report += f"| {d} | {k['parallax_day']:.3f} | {k['orbit_day']:.3f} | {k['rate_min_day']:.3f} - {k['rate_max_day']:.3f} | {k['rate_min_hr']:.3f} - {k['rate_max_hr']:.3f} | {k['uncertainty_pct']:.1f}% |\n"
        
    report += "\n"
    report += "### Distance Estimation Inverse Relation:\n"
    report += "Given an observed apparent motion rate $\\mu_{\\text{obs}}$ (arcsec/day) near opposition, the distance estimate is:\n"
    report += "$$d \\approx \\frac{3548}{\\mu_{\\text{obs}}} \\text{ AU}$$\n"
    report += "with a fundamental systematic uncertainty of $\\sigma_d / d \\approx 1 / \\sqrt{d}$ due to the unknown orbital inclination and eccentricity projection. [SOURCED: Batygin et al. 2019]\n\n"
    
    report += "## 2. Photometric Vetting Criteria\n\n"
    report += "* **Apparent Magnitude Window**: \n"
    report += "  * At perihelion ($q \\approx 300$ AU): $V/r \\approx 21-22$ mag [SOURCED: Siraj et al. 2025]\n"
    report += "  * At aphelion ($Q \\approx 500-800$ AU): $V/r \\approx 24-25.5$ mag [SOURCED: Brown & Batygin 2021]\n"
    report += "* **Colors (Methane-Condensation Atmosphere)**: Fortney et al. (2016) model predicts:\n"
    report += "  * $(g - r) \\approx 0.5 - 0.9$ (somewhat red, Uranus-like) [SOURCED: Fortney et al. 2016]\n"
    report += "  * $(r - i) \\approx 0.2 - 0.5$ [SOURCED: Fortney et al. 2016]\n"
    report += "  * $(i - z) \\approx -0.2 - 0.2$ (blue color in near-IR due to methane absorption) [SOURCED: Fortney et al. 2016]\n\n"
    
    report += "## 3. The Mundane-Explanation Rejection Ladder\n\n"
    report += "Before a candidate is declared a Planet Nine candidate, it must survive the following veto gates:\n\n"
    report += "1. **Gate 1: Image Artifact / Transient Ghost**\n"
    report += "   * *Veto Test*: Must be detected on at least 3 independent exposures on the same night and follow a linear track consistent with sidereal motion. Must be recovered on subsequent nights. [ILLUSTRATIVE]\n"
    report += "2. **Gate 2: Known Object Match**\n"
    report += "   * *Veto Test*: Query MPC and JPL SSD databases for matching ephemerides. Must not match any known TNO, Centaur, main-belt asteroid, or comet. [ILLUSTRATIVE]\n"
    report += "3. **Gate 3: Variable Star / Flaring Source**\n"
    report += "   * *Veto Test*: Cross-check coordinates against Gaia DR3 stellar catalogs. If a star is at the exact location, verify that the candidate has moved away in subsequent frames. [ILLUSTRATIVE]\n"
    report += "4. **Gate 4: Ordinary TNO (30-50 AU)**\n"
    report += "   * *Veto Test*: Ordinary TNOs have apparent motion rates of $\\mu \\approx 50-100$ arcsec/day at opposition. The candidate must have $\\mu \\le 12$ arcsec/day (confirming $d \\ge 300$ AU). [SOURCED: Batygin et al. 2019]\n"
    report += "5. **Gate 5: Stationary Asteroid Mimic**\n"
    report += "   * *Veto Test*: Main-belt asteroids near their stationary points can briefly match TNO motion rates. Observe the candidate for at least 7-14 days. An asteroid's rate will rapidly accelerate and diverge, whereas a distant TNO will maintain a steady rate. [ILLUSTRATIVE]\n\n"
    
    report += "## 4. Composition Adjudication Decision Tree\n\n"
    report += "Once a candidate survives the mundane-explanation ladder, its physical composition (Planet vs. PBH) is adjudicated using electromagnetic and gravitational signatures:\n\n"
    report += "| Path / Observation | Reflectivity (Optical) | Thermal (Infrared) | Gravitational / Parallax | Gamma-RayPoint-Source | Adjudicated Identity |\n"
    report += "| --- | --- | --- | --- | --- | --- |\n"
    report += "| **Path A** | Detected ($r \\approx 21-25.5$ mag) | Detected (Internal cooling flux) | Detected ($d \\approx 300-800$ AU) | Null (No WIMP annihilation) | **H1a: Distant Planet** [SOURCED: Fortney et al. 2016; Brown & Batygin 2021] |\n"
    report += "| **Path B** | Null ($r > 27$ mag depth) | Null (Hawking temp negligible) | Detected ($d \\approx 300-800$ AU) | Detected (WIMP halo annihilation) | **H1b: Primordial Black Hole (PBH)** [SOURCED: Scholtz & Unwin 2019; Witten 2020] |\n"
    report += "| **Path C** | Null ($r > 27$ mag depth) | Null | Detected ($d \\approx 300-800$ AU) | Null | **H1b: PBH (no WIMP halo)** or **H1c: Dark/Compact Candidate** [SOURCED: Scholtz & Unwin 2019] |\n"
    
    return report

if __name__ == "__main__":
    report_md = print_report()
    out_path = "identification_criteria.md"
    with open(out_path, "w") as f:
        f.write(report_md)
    print(f"Vetting criteria successfully written to '{out_path}'.")
