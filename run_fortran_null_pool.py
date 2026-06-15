import os
import time
import numpy as np
import subprocess

# Seed random number generators for reproducibility
np.random.seed(42)

# Generate 10,000,000 candidates
print("Generating 10,000,000 synthetic scattered-disk candidates...")
N_gen = 10000000
u_a = np.random.uniform(0.0, 1.0, N_gen)
a_min, a_max = 150.0, 1000.0
a_vals = (u_a * (a_max**(-0.5) - a_min**(-0.5)) + a_min**(-0.5))**(-2.0)
q_vals = np.random.uniform(30.0, 80.0, N_gen)
e_vals = 1.0 - q_vals / a_vals
valid_indices = (e_vals >= 0.0) & (e_vals < 1.0)
a_vals, q_vals, e_vals = a_vals[valid_indices], q_vals[valid_indices], e_vals[valid_indices]
N_valid = len(a_vals)
print(f"Number of valid candidates: {N_valid}")

sigma_i = np.radians(15.0)
w_max = np.sin(np.radians(15.0)) * np.exp(-0.5)
i_vals = []
while len(i_vals) < N_valid:
    i_cand = np.random.uniform(0.0, np.pi / 2.0, N_valid - len(i_vals))
    weight = np.sin(i_cand) * np.exp(-i_cand**2 / (2.0 * sigma_i**2))
    u = np.random.uniform(0.0, 1.0, len(i_cand))
    i_vals.extend(i_cand[u <= weight / w_max])
i_vals = np.array(i_vals[:N_valid])

Omega_vals = np.random.uniform(0.0, 2.0 * np.pi, N_valid)
omega_vals = np.random.uniform(0.0, 2.0 * np.pi, N_valid)
M_vals = np.random.uniform(0.0, 2.0 * np.pi, N_valid)

H_min, H_max = 5.0, 9.0
alpha_H = 0.4
u_h = np.random.uniform(0.0, 1.0, N_valid)
H_vals = np.log10(u_h * (10.0**(alpha_H * H_max) - 10.0**(alpha_H * H_min)) + 10.0**(alpha_H * H_min)) / alpha_H

# Save to file
print("Saving population to 'synthetic_population_fortran_10m.txt'...")
with open('synthetic_population_fortran_10m.txt', 'w') as f:
    f.write("# Epoch of elements: JD = 2456000.0\n")
    f.write("# Colors = 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    for idx in range(N_valid):
        f.write(f"{a_vals[idx]:.6f} {e_vals[idx]:.6f} {np.degrees(i_vals[idx]):.6f} {np.degrees(Omega_vals[idx]):.6f} {np.degrees(omega_vals[idx]):.6f} {np.degrees(M_vals[idx]):.6f} {H_vals[idx]:.6f}\n")

# Run Fortran simulator
print("Running official Fortran SurveySimulator on 10,000,000 candidates...")
driver_in = f"""42
-{N_valid}
SurveySimulator/Surveys
synthetic_population_fortran_10m.txt
detected_population_fortran_all_10m.txt
detected_population_fortran_tracked_10m.txt
"""
with open('Driver_10m.in', 'w') as f:
    f.write(driver_in)

fortran_driver_path = 'SurveySimulator/Simulator/F95/fortran/Driver'
start_time = time.time()
res = subprocess.run([fortran_driver_path], input=driver_in, capture_output=True, text=True)
end_time = time.time()
print("Fortran exit code:", res.returncode)
print(f"Fortran execution time: {end_time - start_time:.2f} seconds.")

# Parse outputs
fortran_null_varpi = []
if os.path.exists('detected_population_fortran_tracked_10m.txt'):
    with open('detected_population_fortran_tracked_10m.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            parts = line.split()
            if len(parts) >= 8:
                node_f = float(parts[6])
                peri_f = float(parts[7])
                fortran_null_varpi.append((node_f + peri_f) % 360.0)

print(f"Fortran null pool size: {len(fortran_null_varpi)}")

# Rayleigh calculations
def calc_rayleigh(angles_deg):
    angles_rad = np.radians(angles_deg)
    sum_cos = np.sum(np.cos(angles_rad))
    sum_sin = np.sum(np.sin(angles_rad))
    return np.sqrt(sum_cos**2 + sum_sin**2)

reconstructed_a = [208.712, 338.651, 253.315, 298.400, 84.081, 336.000, 175.100, 73.800, 251.200]
reconstructed_b = [175.100, 73.800, 251.200]

def run_mc_test(observed_angles, null_pool, n_trials=10000, seed=42):
    np.random.seed(seed)
    R_obs = calc_rayleigh(observed_angles)
    N = len(observed_angles)
    R_sims = []
    for _ in range(n_trials):
        samples = np.random.choice(null_pool, size=N, replace=True)
        R_sims.append(calc_rayleigh(samples))
    R_sims = np.array(R_sims)
    p_value = np.sum(R_sims >= R_obs) / n_trials
    return R_obs, p_value

R_a, p_a = run_mc_test(reconstructed_a, fortran_null_varpi)
R_b, p_b = run_mc_test(reconstructed_b, fortran_null_varpi)

print("\n--- Fortran-based Rayleigh Test p-values ---")
print(f"Convention A (N=9): R_obs={R_a:.5f}, p-value={p_a:.5f}")
print(f"Convention B (N=3): R_obs={R_b:.5f}, p-value={p_b:.5f}")

with open('fortran_null_results.txt', 'w') as f:
    f.write(f"fortran_null_size={len(fortran_null_varpi)}\n")
    f.write(f"fortran_p_a={p_a:.5f}\n")
    f.write(f"fortran_p_b={p_b:.5f}\n")
