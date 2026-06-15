import os
import time
import numpy as np
import scipy.stats as stats
import subprocess
from astropy.time import Time
from astropy.coordinates import get_body_barycentric

# Seed random number generators for reproducibility
np.random.seed(42)

# Copy check_detection logic from clustering_test.py
def parse_hms_dms(val, is_ra=False):
    if ':' in val:
        parts = [float(x) for x in val.split(':')]
        h, m = parts[0], parts[1]
        s = parts[2] if len(parts) > 2 else 0.0
        sign = -1.0 if h < 0 or val.strip().startswith('-') else 1.0
        deg = (abs(h) + m/60.0 + s/3600.0) * sign
        if is_ra:
            deg *= 15.0
        return np.radians(deg)
    return np.radians(float(val))

def load_pointing_polygons(pts_path):
    pointings = []
    if not os.path.exists(pts_path): return pointings
    with open(pts_path, 'r') as f:
        lines = f.readlines()
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        if not line or line.startswith('#'):
            idx += 1
            continue
        parts = line.split()
        pointing_type = parts[0]
        if pointing_type == 'poly':
            n_vertices = int(parts[1])
            ra_center = parse_hms_dms(parts[2], is_ra=True)
            dec_center = parse_hms_dms(parts[3], is_ra=False)
            epoch, ff, obs_code, eff_file = float(parts[4]), float(parts[5]), int(parts[6]), parts[7]
            poly_x, poly_y = [], []
            idx += 1
            v_count = 0
            while v_count < n_vertices and idx < len(lines):
                vline = lines[idx].strip()
                if not vline or vline.startswith('#'):
                    idx += 1
                    continue
                vparts = vline.split()
                dx = np.radians(float(vparts[0]))
                dy = np.radians(float(vparts[1]))
                y = dec_center + dy
                x = ra_center + dx / np.cos(y)
                poly_x.append(x)
                poly_y.append(y)
                v_count += 1
                idx += 1
            pointings.append({
                'type': 'poly', 'ra_center': ra_center, 'dec_center': dec_center,
                'epoch': epoch, 'ff': ff, 'obs_code': obs_code, 'eff_file': eff_file,
                'poly_x': poly_x, 'poly_y': poly_y
            })
            continue
        elif pointing_type == 'ears':
            ra_center = parse_hms_dms(parts[1], is_ra=True)
            dec_center = parse_hms_dms(parts[2], is_ra=False)
            epoch, ff, obs_code, eff_file = float(parts[3]), float(parts[4]), int(parts[5]), parts[6]
            h, w, e_h, e_w = 0.008678, 0.008545, 0.004169, 0.001913
            y_vals = [dec_center - h, dec_center - e_h, dec_center - e_h, dec_center + e_h, dec_center + e_h, dec_center + h,
                      dec_center + h, dec_center + e_h, dec_center + e_h, dec_center - e_h, dec_center - e_h, dec_center - h]
            x_vals = [ra_center - w / np.cos(y_vals[0]), ra_center - w / np.cos(y_vals[1]), ra_center - (w + e_w) / np.cos(y_vals[2]),
                      ra_center - (w + e_w) / np.cos(y_vals[3]), ra_center - w / np.cos(y_vals[4]), ra_center - w / np.cos(y_vals[5]),
                      ra_center + w / np.cos(y_vals[6]), ra_center + w / np.cos(y_vals[7]), ra_center + (w + e_w) / np.cos(y_vals[8]),
                      ra_center + (w + e_w) / np.cos(y_vals[9]), ra_center + w / np.cos(y_vals[10]), ra_center + w / np.cos(y_vals[11])]
            pointings.append({
                'type': 'ears', 'ra_center': ra_center, 'dec_center': dec_center,
                'epoch': epoch, 'ff': ff, 'obs_code': obs_code, 'eff_file': eff_file,
                'poly_x': x_vals, 'poly_y': y_vals
            })
            idx += 1
            continue
        elif pointing_type == 'rect' or (pointing_type[0].isdigit() or pointing_type[0] == '-'):
            if pointing_type == 'rect':
                w_deg, h_deg, ra_val, dec_val, epoch, ff, obs_code, eff_file = float(parts[1]), float(parts[2]), parts[3], parts[4], float(parts[5]), float(parts[6]), int(parts[7]), parts[8]
            else:
                w_deg, h_deg, ra_val, dec_val, epoch, ff, obs_code, eff_file = float(parts[0]), float(parts[1]), parts[2], parts[3], float(parts[4]), float(parts[5]), int(parts[6]), parts[7]
            w = np.radians(w_deg) / 2.0
            h = np.radians(h_deg) / 2.0
            ra_center = parse_hms_dms(ra_val, is_ra=True)
            dec_center = parse_hms_dms(dec_val, is_ra=False)
            y_vals = [dec_center - h, dec_center + h, dec_center + h, dec_center - h]
            x_vals = [ra_center - w / np.cos(y_vals[0]), ra_center - w / np.cos(y_vals[1]), ra_center + w / np.cos(y_vals[2]), ra_center + w / np.cos(y_vals[3])]
            pointings.append({
                'type': 'rect', 'ra_center': ra_center, 'dec_center': dec_center,
                'epoch': epoch, 'ff': ff, 'obs_code': obs_code, 'eff_file': eff_file,
                'poly_x': x_vals, 'poly_y': y_vals
            })
            idx += 1
            continue
        idx += 1
    return pointings

def parse_efficiency_file(eff_path):
    eff = {
        'rate_cut': [0.0, 99.0, 0.0, 180.0],
        'mag_error': [0.026, 0.33, 24.45, 0.7, 23.7, -0.3],
        'phot_frac': [1.0, 0.0, 0.0],
        'track_frac': [1.0, 99.0, 0.0],
        'filter': 'r', 'rate_ranges': []
    }
    if not os.path.exists(eff_path): return eff
    with open(eff_path, 'r') as f:
        current_range = None
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            if '=' not in line: continue
            key, val = [x.strip() for x in line.split('=', 1)]
            val_parts = val.split()
            if key == 'rate_cut':
                eff['rate_cut'] = [float(x) for x in val_parts]
                eff['rate_cut'][0] = np.radians(eff['rate_cut'][0] * 24.0 / 3600.0)
                eff['rate_cut'][1] = np.radians(eff['rate_cut'][1] * 24.0 / 3600.0)
                eff['rate_cut'][2] = np.radians(eff['rate_cut'][2])
                eff['rate_cut'][3] = np.radians(eff['rate_cut'][3])
            elif key == 'mag_error':
                parts = [float(x) for x in val_parts]
                parts[1] = np.log10(parts[1] / parts[0]) / (parts[2] - 21.0)
                eff['mag_error'] = parts
            elif key == 'phot_frac': eff['phot_frac'] = [float(x) for x in val_parts]
            elif key == 'track_frac': eff['track_frac'] = [float(x) for x in val_parts]
            elif key == 'filter': eff['filter'] = val_parts[0]
            elif key == 'rates':
                if current_range is not None: eff['rate_ranges'].append(current_range)
                current_range = {
                    'rate_min': np.radians(float(val_parts[0]) * 24.0 / 3600.0),
                    'rate_max': np.radians(float(val_parts[1]) * 24.0 / 3600.0),
                    'func_type': 'square', 'params': [], 'lookup_table': [], 'mag_lim': -1.0
                }
            elif key == 'function':
                if current_range is not None: current_range['func_type'] = val_parts[0]
            elif key in ('linear_param', 'single_param', 'double_param', 'square_param'):
                if current_range is not None: current_range['params'] = [float(x) for x in val_parts]
            elif key == 'lookup_param':
                if current_range is not None: current_range['lookup_table'].append([float(x) for x in val_parts])
            elif key == 'mag_lim':
                if current_range is not None: current_range['mag_lim'] = float(val_parts[0])
        if current_range is not None: eff['rate_ranges'].append(current_range)
    return eff

def point_in_polygon(x, y, poly_x, poly_y):
    n = len(poly_x)
    inside = False
    p1x, p1y = poly_x[0], poly_y[0]
    for i in range(n + 1):
        p2x, p2y = poly_x[i % n], poly_y[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def solve_kepler(M, e):
    E = M
    for _ in range(5):
        E = E - (E - e * np.sin(E) - M) / (1.0 - e * np.cos(E))
    return E

def get_barycentric_ecliptic_pos(a, e, inc, node, peri, M):
    E = solve_kepler(M, e)
    x_orbit = a * (np.cos(E) - e)
    y_orbit = a * np.sqrt(1.0 - e**2) * np.sin(E)
    cos_w, sin_w = np.cos(peri), np.sin(peri)
    cos_N, sin_N = np.cos(node), np.sin(node)
    cos_i, sin_i = np.cos(inc), np.sin(inc)
    Px = cos_w * cos_N - sin_w * sin_N * cos_i
    Py = cos_w * sin_N + sin_w * cos_N * cos_i
    Pz = sin_w * sin_i
    Qx = -sin_w * cos_N - cos_w * sin_N * cos_i
    Qy = -sin_w * sin_N + cos_w * cos_N * cos_i
    Qz = cos_w * sin_i
    x = x_orbit * Px + y_orbit * Qx
    y = x_orbit * Py + y_orbit * Qy
    z = x_orbit * Pz + y_orbit * Qz
    return np.array([x, y, z])

def ecliptic_to_equatorial(v):
    eps = np.radians(23.43928056)
    cos_eps, sin_eps = np.cos(eps), np.sin(eps)
    return np.array([v[0], cos_eps * v[1] - sin_eps * v[2], sin_eps * v[1] + cos_eps * v[2]])

def compute_efficiency_raw(rate_ranges, m, rate):
    matching_range = None
    for r_range in rate_ranges:
        if rate >= r_range['rate_min'] and rate <= r_range['rate_max']:
            matching_range = r_range
            break
    if matching_range is None: return 0.0, -1.0
    func_type = matching_range['func_type']
    params = matching_range['params']
    maglim = matching_range['mag_lim']
    if func_type == 'square':
        if m < 21.0: eta_raw = params[0]
        else: eta_raw = (params[0] - params[1] * (m - 21.0)**2) / (1.0 + np.exp((m - params[2]) / params[3]))
    elif func_type == 'single':
        eta_raw = params[0] / 2.0 * (1.0 - np.tanh((m - params[1]) / params[2]))
    elif func_type == 'double':
        eta_raw = params[0] / 4.0 * (1.0 - np.tanh((m - params[1]) / params[2])) * (1.0 - np.tanh((m - params[1]) / params[3]))
    elif func_type == 'linear':
        if m < params[1]: eta_raw = params[0]
        elif m < params[2]: eta_raw = (m - params[2]) * params[0] / (params[1] - params[2])
        else: eta_raw = 0.0
    elif func_type == 'lookup':
        tbl = matching_range['lookup_table']
        if not tbl: eta_raw = 0.0
        elif m < tbl[0][0]: eta_raw = tbl[0][1]
        elif m > tbl[-1][0]: eta_raw = 0.0
        else:
            for i in range(len(tbl) - 1):
                if m >= tbl[i][0] and m <= tbl[i + 1][0]:
                    x0, y0 = tbl[i]
                    x1, y1 = tbl[i + 1]
                    eta_raw = y0 + (y1 - y0) * (m - x0) / (x1 - x0)
                    break
            else: eta_raw = 0.0
    else: eta_raw = 0.0
    return max(0.0, eta_raw), maglim

def generate_magnitude_error(m_th, mag_er):
    if m_th <= 21.0: magerr = mag_er[0]
    elif m_th <= mag_er[2]: magerr = mag_er[0] * 10.0**(mag_er[1] * (m_th - 21.0))
    else: magerr = max(mag_er[0] * 10.0**(mag_er[1] * (mag_er[2] - 21.0)) - (m_th - mag_er[2]) * mag_er[3], 0.0)
    u = np.random.uniform(0.0, 1.0)
    tmp = np.sqrt(6.0) * (np.sqrt(2.0 * u) - 1.0) if u <= 0.5 else np.sqrt(6.0) * (1.0 - np.sqrt(2.0 * (1.0 - u)))
    mag = m_th + magerr * tmp
    if m_th > mag_er[4]: mag += (m_th - mag_er[4]) * mag_er[5]
    return mag, magerr

# Load pointing polygons and efficiency files
survey_dir = 'SurveySimulator/Surveys'
blocks = []
with open(os.path.join(survey_dir, 'All_Surveys.list'), 'r') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        blocks.append(line)

all_pointings = []
for b in blocks:
    pts_path = os.path.join(survey_dir, 'blocks', f'{b}.pts')
    pointings = load_pointing_polygons(pts_path)
    for p in pointings:
        p['eff'] = parse_efficiency_file(os.path.join(survey_dir, 'eff', p['eff_file']))
        p['dec_min'] = min(p['poly_y']) - 0.0001
        p['dec_max'] = max(p['poly_y']) + 0.0001
        p['dx_min'] = min((vx - p['ra_center'] + np.pi) % (2.0 * np.pi) - np.pi for vx in p['poly_x']) - 0.0001
        p['dx_max'] = max((vx - p['ra_center'] + np.pi) % (2.0 * np.pi) - np.pi for vx in p['poly_x']) + 0.0001
        all_pointings.append(p)

pointing_dec_centers = np.array([p['dec_center'] for p in all_pointings])
pointing_ra_centers = np.array([p['ra_center'] for p in all_pointings])
sin_pointing_dec, cos_pointing_dec = np.sin(pointing_dec_centers), np.cos(pointing_dec_centers)
sin_pointing_ra, cos_pointing_ra = np.sin(pointing_ra_centers), np.cos(pointing_ra_centers)

earth_positions = []
for p in all_pointings:
    t1 = Time(p['epoch'], format='jd')
    t2 = Time(p['epoch'] + 2.0 / 24.0, format='jd')
    pos_earth1 = get_body_barycentric('earth', t1)
    pos_earth2 = get_body_barycentric('earth', t2)
    earth_positions.append({
        'pos1': np.array([pos_earth1.x.value, pos_earth1.y.value, pos_earth1.z.value]),
        'pos2': np.array([pos_earth2.x.value, pos_earth2.y.value, pos_earth2.z.value])
    })

jd_center = 2456000.0
pos_earth_center = get_body_barycentric('earth', Time(jd_center, format='jd'))
XE_c, YE_c, ZE_c = pos_earth_center.x.value, pos_earth_center.y.value, pos_earth_center.z.value
filter_color_indices = {'g': 0, 'r': 1, 'i': 2, 'z': 3, 'u': 4, 'V': 5, 'B': 6, 'R': 7, 'I': 8}

def check_detection(a, e, inc, node, peri, M0, H_x, color):
    n_motion = 2.0 * np.pi / (365.25 * a**1.5)
    dt_c = jd_center - 2451545.0
    M_c = (M0 + n_motion * dt_c) % (2.0 * np.pi)
    pos_obj_c_ecl = get_barycentric_ecliptic_pos(a, e, inc, node, peri, M_c)
    pos_obj_c_eq = ecliptic_to_equatorial(pos_obj_c_ecl)
    x_r_c = pos_obj_c_eq[0] - XE_c
    y_r_c = pos_obj_c_eq[1] - YE_c
    z_r_c = pos_obj_c_eq[2] - ZE_c
    delta_c = np.sqrt(x_r_c**2 + y_r_c**2 + z_r_c**2)
    ra_c = np.arctan2(y_r_c, x_r_c) % (2.0 * np.pi)
    dec_c = np.arcsin(z_r_c / delta_c)
    best_flag = 0
    cos_6_deg = np.cos(np.radians(6.0))
    sin_dec_c, cos_dec_c = np.sin(dec_c), np.cos(dec_c)
    sin_ra_c, cos_ra_c = np.sin(ra_c), np.cos(ra_c)
    cos_seps = sin_dec_c * sin_pointing_dec + cos_dec_c * cos_pointing_dec * (cos_ra_c * cos_pointing_ra + sin_ra_c * sin_pointing_ra)
    matching_indices = np.where(cos_seps >= cos_6_deg)[0]
    for idx in matching_indices:
        p = all_pointings[idx]
        dt1 = p['epoch'] - 2451545.0
        M1 = (M0 + n_motion * dt1) % (2.0 * np.pi)
        pos_obj1_ecl = get_barycentric_ecliptic_pos(a, e, inc, node, peri, M1)
        pos_obj1_eq = ecliptic_to_equatorial(pos_obj1_ecl)
        pos_earth1 = earth_positions[idx]['pos1']
        pos_rel1 = pos_obj1_eq - pos_earth1
        delta1 = np.linalg.norm(pos_rel1)
        ra1 = np.arctan2(pos_rel1[1], pos_rel1[0]) % (2.0 * np.pi)
        dec1 = np.arcsin(pos_rel1[2] / delta1)
        if dec1 < p['dec_min'] or dec1 > p['dec_max']: continue
        dx_ra = (ra1 - p['ra_center'] + np.pi) % (2.0 * np.pi) - np.pi
        if dx_ra < p['dx_min'] or dx_ra > p['dx_max']: continue
        if not point_in_polygon(p['ra_center'] + dx_ra, dec1, p['poly_x'], p['poly_y']): continue
        if np.random.uniform(0.0, 1.0) > p['ff']: continue
        dt2 = (p['epoch'] + 2.0 / 24.0) - 2451545.0
        M2 = (M0 + n_motion * dt2) % (2.0 * np.pi)
        pos_obj2_ecl = get_barycentric_ecliptic_pos(a, e, inc, node, peri, M2)
        pos_obj2_eq = ecliptic_to_equatorial(pos_obj2_ecl)
        pos_earth2 = earth_positions[idx]['pos2']
        pos_rel2 = pos_obj2_eq - pos_earth2
        delta2 = np.linalg.norm(pos_rel2)
        ra2, dec2 = np.arctan2(pos_rel2[1], pos_rel2[0]) % (2.0 * np.pi), np.arcsin(pos_rel2[2] / delta2)
        dt_days = 2.0 / 24.0
        d_ra_west = ((ra1 - ra2 + np.pi) % (2.0 * np.pi) - np.pi) / dt_days * np.cos(dec1)
        d_dec_north = (dec2 - dec1) / dt_days
        rate_rad_day = np.sqrt(d_ra_west**2 + d_dec_north**2)
        angle_rad = np.arctan2(d_dec_north, d_ra_west)
        rc = p['eff']['rate_cut']
        if rate_rad_day < rc[0] or rate_rad_day > rc[1]: continue
        diff_angle = (rc[2] - angle_rad + np.pi) % (2.0 * np.pi) - np.pi
        if abs(diff_angle) > rc[3]: continue
        r_sun1 = np.linalg.norm(pos_obj1_ecl)
        r_earth_sun = np.linalg.norm(pos_earth1)
        cos_alpha = (-r_earth_sun**2 + delta1**2 + r_sun1**2) / (2.0 * r_sun1 * delta1)
        alpha = np.arccos(min(1.0, max(-1.0, cos_alpha)))
        phi1, phi2 = np.exp(-3.33 * (np.tan(alpha / 2.0))**0.63), np.exp(-1.87 * (np.tan(alpha / 2.0))**1.22)
        H_f = H_x + color[filter_color_indices.get(p['eff']['filter'], 1)]
        m_int = 5.0 * np.log10(r_sun1 * delta1) + H_f - 2.5 * np.log10((1.0 - 0.15) * phi1 + 0.15 * phi2)
        eta_raw, maglim = compute_efficiency_raw(p['eff']['rate_ranges'], m_int, rate_rad_day)
        if eta_raw < 0.01: continue
        m_rand, magerr = generate_magnitude_error(m_int, p['eff']['mag_error'])
        eff_rand, maglim = compute_efficiency_raw(p['eff']['rate_ranges'], m_rand, rate_rad_day)
        if np.random.uniform(0.0, 1.0) > eff_rand: continue
        flag_val = 1
        if maglim > 0.0:
            if m_rand <= maglim: flag_val += 2
        elif eff_rand >= 0.4: flag_val += 2
        tf = p['eff']['track_frac']
        if np.random.uniform(0.0, 1.0) <= min(tf[0], 1.0 + (m_rand - tf[1]) * tf[2]): flag_val += 1
        if flag_val > best_flag: best_flag = flag_val
        if best_flag >= 4: return True
    return False

# Generate synthetic population (N=1,000,000)
print("Generating identical synthetic scattered-disk population (N=1,000,000)...")
N_gen = 1000000
np.random.seed(42)
u_a = np.random.uniform(0.0, 1.0, N_gen)
a_min, a_max = 150.0, 1000.0
a_vals = (u_a * (a_max**(-0.5) - a_min**(-0.5)) + a_min**(-0.5))**(-2.0)
q_vals = np.random.uniform(30.0, 80.0, N_gen)
e_vals = 1.0 - q_vals / a_vals
valid_indices = (e_vals >= 0.0) & (e_vals < 1.0)
a_vals, q_vals, e_vals = a_vals[valid_indices], q_vals[valid_indices], e_vals[valid_indices]
N_valid = len(a_vals)

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

# Save in Fortran ReadModelFromFile format
print("Saving population to 'synthetic_population_fortran.txt'...")
with open('synthetic_population_fortran.txt', 'w') as f:
    f.write("# Epoch of elements: JD = 2456000.0\n")
    f.write("# Colors = 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0\n")
    for idx in range(N_valid):
        f.write(f"{a_vals[idx]:.6f} {e_vals[idx]:.6f} {np.degrees(i_vals[idx]):.6f} {np.degrees(Omega_vals[idx]):.6f} {np.degrees(omega_vals[idx]):.6f} {np.degrees(M_vals[idx]):.6f} {H_vals[idx]:.6f}\n")

# Run Python simulator
print("Running Python selection filter...")
py_det_indices = []
colors = [0.0] * 10
for idx in range(N_valid):
    if check_detection(a_vals[idx], e_vals[idx], i_vals[idx], Omega_vals[idx], omega_vals[idx], M_vals[idx], H_vals[idx], colors):
        py_det_indices.append(idx)
print(f"Python detections: {len(py_det_indices)}")

# Run Fortran simulator
print("Running official Fortran SurveySimulator...")
driver_in = f"""42
-{N_valid}
SurveySimulator/Surveys
synthetic_population_fortran.txt
detected_population_fortran_all.txt
detected_population_fortran_tracked.txt
"""
with open('Driver.in', 'w') as f:
    f.write(driver_in)

fortran_driver_path = 'SurveySimulator/Simulator/F95/fortran/Driver'
res = subprocess.run([fortran_driver_path], input=driver_in, capture_output=True, text=True)
print("Fortran exit code:", res.returncode)
# print("Fortran stdout:", res.stdout[:500])

# Parse Fortran results
fortran_tracked_a = []
fortran_tracked_q = []
fortran_tracked_i = []
fortran_tracked_varpi = []
fortran_tracked_H = []

if os.path.exists('detected_population_fortran_tracked.txt'):
    with open('detected_population_fortran_tracked.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            parts = line.split()
            if len(parts) >= 10:
                # Format of tracked.dat detections is: a e inc q r M node peri m_rand H_rand color Comments
                a_f = float(parts[0])
                i_f = float(parts[2])
                q_f = float(parts[3])
                node_f = float(parts[6])
                peri_f = float(parts[7])
                H_f = float(parts[9])
                fortran_tracked_a.append(a_f)
                fortran_tracked_q.append(q_f)
                fortran_tracked_i.append(i_f)
                fortran_tracked_varpi.append((node_f + peri_f) % 360.0)
                fortran_tracked_H.append(H_f)

print(f"Fortran detections: {len(fortran_tracked_a)}")

# Extract Python detected parameters
py_a = a_vals[py_det_indices]
py_q = q_vals[py_det_indices]
py_i = np.degrees(i_vals[py_det_indices])
py_varpi = (np.degrees(omega_vals[py_det_indices] + Omega_vals[py_det_indices])) % 360.0
py_H = H_vals[py_det_indices]

# Run statistical tests
print("\n--- Statistical Comparison (Python vs Fortran) ---")
for name, py_data, ft_data in zip(
    ['a', 'q', 'i', 'varpi', 'H'],
    [py_a, py_q, py_i, py_varpi, py_H],
    [fortran_tracked_a, fortran_tracked_q, fortran_tracked_i, fortran_tracked_varpi, fortran_tracked_H]
):
    if len(ft_data) > 0 and len(py_data) > 0:
        ks_stat, p_val = stats.ks_2samp(py_data, ft_data)
        w_dist = stats.wasserstein_distance(py_data, ft_data)
        print(f"Parameter: {name}")
        print(f"  K-S Statistic: {ks_stat:.4f}, p-value: {p_val:.4f}")
        print(f"  Wasserstein Distance: {w_dist:.4f}")
    else:
        print(f"Parameter {name}: Cannot compare (empty dataset)")

with open('benchmark_results.txt', 'w') as f:
    f.write(f"Python_detections={len(py_det_indices)}\n")
    f.write(f"Fortran_detections={len(fortran_tracked_a)}\n")
    for name, py_data, ft_data in zip(
        ['a', 'q', 'i', 'varpi', 'H'],
        [py_a, py_q, py_i, py_varpi, py_H],
        [fortran_tracked_a, fortran_tracked_q, fortran_tracked_i, fortran_tracked_varpi, fortran_tracked_H]
    ):
        if len(ft_data) > 0 and len(py_data) > 0:
            ks_stat, p_val = stats.ks_2samp(py_data, ft_data)
            w_dist = stats.wasserstein_distance(py_data, ft_data)
            f.write(f"{name}_ks={ks_stat:.5f}\n")
            f.write(f"{name}_p={p_val:.5f}\n")
            f.write(f"{name}_w={w_dist:.5f}\n")
