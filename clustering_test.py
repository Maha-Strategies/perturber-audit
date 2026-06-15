import os
import numpy as np
import re
from astropy.time import Time
from astropy.coordinates import get_body_barycentric

# Seed random number generators for reproducibility
np.random.seed(42)

def parse_hms_dms(val, is_ra=False):
    """
    Parses coordinate string (e.g. 14:15:28.89 or decimal float) into radians.
    """
    if ':' in val:
        parts = [float(x) for x in val.split(':')]
        h = parts[0]
        m = parts[1]
        s = parts[2] if len(parts) > 2 else 0.0
        sign = -1.0 if h < 0 or val.strip().startswith('-') else 1.0
        deg = abs(h) + m/60.0 + s/3600.0
        deg = deg * sign
        if is_ra:
            deg = deg * 15.0 # 1 hour = 15 degrees
        return np.radians(deg)
    else:
        deg = float(val)
        return np.radians(deg)

def load_pointing_polygons(pts_path):
    """
    Parses a .pts file to extract all pointing polygons, epochs, and efficiencies.
    """
    pointings = []
    if not os.path.exists(pts_path):
        return pointings
    
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
            epoch = float(parts[4])
            ff = float(parts[5])
            obs_code = int(parts[6])
            eff_file = parts[7]
            
            # Read subsequent lines for vertex offsets (in degrees)
            poly_x = []
            poly_y = []
            idx += 1
            v_count = 0
            while v_count < n_vertices and idx < len(lines):
                vline = lines[idx].strip()
                if not vline or vline.startswith('#'):
                    idx += 1
                    continue
                vparts = vline.split()
                dx_deg = float(vparts[0])
                dy_deg = float(vparts[1])
                dx = np.radians(dx_deg)
                dy = np.radians(dy_deg)
                
                # Apply projection
                y = dec_center + dy
                x = ra_center + dx / np.cos(y)
                poly_x.append(x)
                poly_y.append(y)
                
                v_count += 1
                idx += 1
            
            pointings.append({
                'type': 'poly',
                'ra_center': ra_center,
                'dec_center': dec_center,
                'epoch': epoch,
                'ff': ff,
                'obs_code': obs_code,
                'eff_file': eff_file,
                'poly_x': poly_x,
                'poly_y': poly_y
            })
            continue
            
        elif pointing_type == 'ears':
            ra_center = parse_hms_dms(parts[1], is_ra=True)
            dec_center = parse_hms_dms(parts[2], is_ra=False)
            epoch = float(parts[3])
            ff = float(parts[4])
            obs_code = int(parts[5])
            eff_file = parts[6]
            
            # Create MegaPrime ears coordinates (in radians)
            h = 0.008678
            w = 0.008545
            e_h = 0.004169
            e_w = 0.001913
            
            y_vals = [
                dec_center - h,
                dec_center - e_h,
                dec_center - e_h,
                dec_center + e_h,
                dec_center + e_h,
                dec_center + h,
                dec_center + h,
                dec_center + e_h,
                dec_center + e_h,
                dec_center - e_h,
                dec_center - e_h,
                dec_center - h,
            ]
            
            x_vals = [
                ra_center - w / np.cos(y_vals[0]),
                ra_center - w / np.cos(y_vals[1]),
                ra_center - (w + e_w) / np.cos(y_vals[2]),
                ra_center - (w + e_w) / np.cos(y_vals[3]),
                ra_center - w / np.cos(y_vals[4]),
                ra_center - w / np.cos(y_vals[5]),
                ra_center + w / np.cos(y_vals[6]),
                ra_center + w / np.cos(y_vals[7]),
                ra_center + (w + e_w) / np.cos(y_vals[8]),
                ra_center + (w + e_w) / np.cos(y_vals[9]),
                ra_center + w / np.cos(y_vals[10]),
                ra_center + w / np.cos(y_vals[11]),
            ]
            
            pointings.append({
                'type': 'ears',
                'ra_center': ra_center,
                'dec_center': dec_center,
                'epoch': epoch,
                'ff': ff,
                'obs_code': obs_code,
                'eff_file': eff_file,
                'poly_x': x_vals,
                'poly_y': y_vals
            })
            idx += 1
            continue
            
        elif pointing_type == 'rect' or (pointing_type[0].isdigit() or pointing_type[0] == '-'):
            if pointing_type == 'rect':
                w_deg = float(parts[1])
                h_deg = float(parts[2])
                ra_val = parts[3]
                dec_val = parts[4]
                epoch = float(parts[5])
                ff = float(parts[6])
                obs_code = int(parts[7])
                eff_file = parts[8]
            else:
                w_deg = float(parts[0])
                h_deg = float(parts[1])
                ra_val = parts[2]
                dec_val = parts[3]
                epoch = float(parts[4])
                ff = float(parts[5])
                obs_code = int(parts[6])
                eff_file = parts[7]
            
            w = np.radians(w_deg) / 2.0
            h = np.radians(h_deg) / 2.0
            ra_center = parse_hms_dms(ra_val, is_ra=True)
            dec_center = parse_hms_dms(dec_val, is_ra=False)
            
            y_vals = [dec_center - h, dec_center + h, dec_center + h, dec_center - h]
            x_vals = [
                ra_center - w / np.cos(y_vals[0]),
                ra_center - w / np.cos(y_vals[1]),
                ra_center + w / np.cos(y_vals[2]),
                ra_center + w / np.cos(y_vals[3]),
            ]
            
            pointings.append({
                'type': 'rect',
                'ra_center': ra_center,
                'dec_center': dec_center,
                'epoch': epoch,
                'ff': ff,
                'obs_code': obs_code,
                'eff_file': eff_file,
                'poly_x': x_vals,
                'poly_y': y_vals
            })
            idx += 1
            continue
        
        idx += 1
        
    return pointings

def parse_efficiency_file(eff_path):
    """
    Parses a survey efficiency file (.eff).
    """
    eff = {
        'rate_cut': [0.0, 99.0, 0.0, 180.0],
        'mag_error': [0.026, 0.33, 24.45, 0.7, 23.7, -0.3],
        'phot_frac': [1.0, 0.0, 0.0],
        'track_frac': [1.0, 99.0, 0.0],
        'filter': 'r',
        'rate_ranges': []
    }
    
    if not os.path.exists(eff_path):
        return eff
        
    with open(eff_path, 'r') as f:
        current_range = None
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' not in line:
                continue
                
            key, val = [x.strip() for x in line.split('=', 1)]
            val_parts = val.split()
            
            if key == 'rate_cut':
                eff['rate_cut'] = [float(x) for x in val_parts]
                # Convert rates to rad/day
                eff['rate_cut'][0] = np.radians(eff['rate_cut'][0] * 24.0 / 3600.0)
                eff['rate_cut'][1] = np.radians(eff['rate_cut'][1] * 24.0 / 3600.0)
                eff['rate_cut'][2] = np.radians(eff['rate_cut'][2])
                eff['rate_cut'][3] = np.radians(eff['rate_cut'][3])
                
            elif key == 'mag_error':
                parts = [float(x) for x in val_parts]
                # Recompute alpha parameter (mag_er(2)) per getsur.f95 line 393
                parts[1] = np.log10(parts[1] / parts[0]) / (parts[2] - 21.0)
                eff['mag_error'] = parts
                
            elif key == 'phot_frac':
                eff['phot_frac'] = [float(x) for x in val_parts]
                
            elif key == 'track_frac':
                eff['track_frac'] = [float(x) for x in val_parts]
                
            elif key == 'filter':
                eff['filter'] = val_parts[0]
                
            elif key == 'rates':
                if current_range is not None:
                    eff['rate_ranges'].append(current_range)
                current_range = {
                    'rate_min': np.radians(float(val_parts[0]) * 24.0 / 3600.0),
                    'rate_max': np.radians(float(val_parts[1]) * 24.0 / 3600.0),
                    'func_type': 'square',
                    'params': [],
                    'lookup_table': [],
                    'mag_lim': -1.0
                }
                
            elif key == 'function':
                if current_range is not None:
                    current_range['func_type'] = val_parts[0]
                    
            elif key in ('linear_param', 'single_param', 'double_param', 'square_param'):
                if current_range is not None:
                    current_range['params'] = [float(x) for x in val_parts]
                    
            elif key == 'lookup_param':
                if current_range is not None:
                    current_range['lookup_table'].append([float(x) for x in val_parts])
                    
            elif key == 'mag_lim':
                if current_range is not None:
                    current_range['mag_lim'] = float(val_parts[0])
                    
        if current_range is not None:
            eff['rate_ranges'].append(current_range)
            
    return eff

def point_in_polygon(x, y, poly_x, poly_y):
    """
    Standard ray-casting point-in-polygon check.
    """
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
    """
    Solve Kepler's equation E - e*sin(E) = M using Newton-Raphson.
    """
    E = M
    for _ in range(5):
        E = E - (E - e * np.sin(E) - M) / (1.0 - e * np.cos(E))
    return E

def get_barycentric_ecliptic_pos(a, e, inc, node, peri, M):
    """
    Convert Keplerian elements to J2000 barycentric ecliptic Cartesian coordinates.
    """
    E = solve_kepler(M, e)
    x_orbit = a * (np.cos(E) - e)
    y_orbit = a * np.sqrt(1.0 - e**2) * np.sin(E)
    
    cos_w = np.cos(peri)
    sin_w = np.sin(peri)
    cos_N = np.cos(node)
    sin_N = np.sin(node)
    cos_i = np.cos(inc)
    sin_i = np.sin(inc)
    
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
    """
    Rotate barycentric J2000 ecliptic coordinate vector to equatorial frame (ICRS/J2000).
    """
    eps = np.radians(23.43928056)
    cos_eps = np.cos(eps)
    sin_eps = np.sin(eps)
    x = v[0]
    y = cos_eps * v[1] - sin_eps * v[2]
    z = sin_eps * v[1] + cos_eps * v[2]
    return np.array([x, y, z])

def compute_efficiency_raw(rate_ranges, m, rate):
    """
    Computes the raw efficiency eta_raw for a rate range.
    """
    matching_range = None
    for r_range in rate_ranges:
        if rate >= r_range['rate_min'] and rate <= r_range['rate_max']:
            matching_range = r_range
            break
            
    if matching_range is None:
        return 0.0, -1.0
        
    func_type = matching_range['func_type']
    params = matching_range['params']
    maglim = matching_range['mag_lim']
    
    if func_type == 'square':
        if m < 21.0:
            eta_raw = params[0]
        else:
            eta_raw = (params[0] - params[1] * (m - 21.0)**2) / (1.0 + np.exp((m - params[2]) / params[3]))
            
    elif func_type == 'single':
        eta_raw = params[0] / 2.0 * (1.0 - np.tanh((m - params[1]) / params[2]))
        
    elif func_type == 'double':
        eta_raw = params[0] / 4.0 * (1.0 - np.tanh((m - params[1]) / params[2])) * (1.0 - np.tanh((m - params[1]) / params[3]))
        
    elif func_type == 'linear':
        if m < params[1]:
            eta_raw = params[0]
        elif m < params[2]:
            eta_raw = (m - params[2]) * params[0] / (params[1] - params[2])
        else:
            eta_raw = 0.0
            
    elif func_type == 'lookup':
        tbl = matching_range['lookup_table']
        if not tbl:
            eta_raw = 0.0
        elif m < tbl[0][0]:
            eta_raw = tbl[0][1]
        elif m > tbl[-1][0]:
            eta_raw = 0.0
        else:
            for i in range(len(tbl) - 1):
                if m >= tbl[i][0] and m <= tbl[i + 1][0]:
                    x0, y0 = tbl[i]
                    x1, y1 = tbl[i + 1]
                    eta_raw = y0 + (y1 - y0) * (m - x0) / (x1 - x0)
                    break
            else:
                eta_raw = 0.0
    else:
        eta_raw = 0.0
        
    eta_raw = max(0.0, eta_raw)
    return eta_raw, maglim

def generate_magnitude_error(m_th, mag_er):
    """
    Generates a randomized observed magnitude using the getsur.f95 / numutils.f95 math.
    """
    if m_th <= 21.0:
        magerr = mag_er[0]
    elif m_th <= mag_er[2]:
        magerr = mag_er[0] * 10.0**(mag_er[1] * (m_th - 21.0))
    else:
        magerr = max(mag_er[0] * 10.0**(mag_er[1] * (mag_er[2] - 21.0)) - (m_th - mag_er[2]) * mag_er[3], 0.0)
        
    u = np.random.uniform(0.0, 1.0)
    if u <= 0.5:
        tmp = np.sqrt(6.0) * (np.sqrt(2.0 * u) - 1.0)
    else:
        tmp = np.sqrt(6.0) * (1.0 - np.sqrt(2.0 * (1.0 - u)))
        
    mag = m_th + magerr * tmp
    if m_th > mag_er[4]:
        mag += (m_th - mag_er[4]) * mag_er[5]
        
    return mag, magerr

# Load blocks list
print("Phase 1: Loading characterized surveys block lists...")
survey_dir = 'SurveySimulator/Surveys'
blocks = []
with open(os.path.join(survey_dir, 'All_Surveys.list'), 'r') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        blocks.append(line)

print(f"Loaded {len(blocks)} survey blocks.")

all_pointings = []
for b in blocks:
    pts_path = os.path.join(survey_dir, 'blocks', f'{b}.pts')
    pointings = load_pointing_polygons(pts_path)
    for p in pointings:
        eff_path = os.path.join(survey_dir, 'eff', p['eff_file'])
        p['eff'] = parse_efficiency_file(eff_path)
        # Pre-compute polygon bounding box in equatorial coordinates (in radians)
        p['dec_min'] = min(p['poly_y']) - 0.0001
        p['dec_max'] = max(p['poly_y']) + 0.0001
        p['dx_min'] = min((vx - p['ra_center'] + np.pi) % (2.0 * np.pi) - np.pi for vx in p['poly_x']) - 0.0001
        p['dx_max'] = max((vx - p['ra_center'] + np.pi) % (2.0 * np.pi) - np.pi for vx in p['poly_x']) + 0.0001
        all_pointings.append(p)

print(f"Loaded total {len(all_pointings)} pointing fields with bounding boxes.")

# Pre-calculate arrays of dec_center and ra_center for vectorized screening
pointing_dec_centers = np.array([p['dec_center'] for p in all_pointings])
pointing_ra_centers = np.array([p['ra_center'] for p in all_pointings])

# Pre-calculate pointing center sines and cosines
sin_pointing_dec = np.sin(pointing_dec_centers)
cos_pointing_dec = np.cos(pointing_dec_centers)
sin_pointing_ra = np.sin(pointing_ra_centers)
cos_pointing_ra = np.cos(pointing_ra_centers)

# Pre-calculate Earth positions
print("Pre-calculating Earth positions at pointing epochs...")
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

# Pre-calculate central Earth position for coarse screening
jd_center = 2456000.0
pos_earth_center = get_body_barycentric('earth', Time(jd_center, format='jd'))
XE_c, YE_c, ZE_c = pos_earth_center.x.value, pos_earth_center.y.value, pos_earth_center.z.value

print("Pre-calculation complete.")

# Filter name to color index mapping
filter_color_indices = {
    'g': 0,
    'r': 1,
    'i': 2,
    'z': 3,
    'u': 4,
    'V': 5,
    'B': 6,
    'R': 7,
    'I': 8
}

# ----------------- Selection Bias Simulation -----------------
def check_detection(a, e, inc, node, peri, M0, H_x, color):
    """
    Optimized survey detection checker using central epoch screening and bounding boxes.
    """
    n_motion = 2.0 * np.pi / (365.25 * a**1.5)
    
    # 1. Coarse screening: compute object geocentric equatorial position at central epoch
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
    
    # Vectorized angular separation screen (trigonometrically reduced)
    sin_dec_c = np.sin(dec_c)
    cos_dec_c = np.cos(dec_c)
    sin_ra_c = np.sin(ra_c)
    cos_ra_c = np.cos(ra_c)
    cos_seps = sin_dec_c * sin_pointing_dec + cos_dec_c * cos_pointing_dec * (cos_ra_c * cos_pointing_ra + sin_ra_c * sin_pointing_ra)
    matching_indices = np.where(cos_seps >= cos_6_deg)[0]
    
    for idx in matching_indices:
        p = all_pointings[idx]
        # 2. Detailed check for candidate pointing
        dt1 = p['epoch'] - 2451545.0
        M1 = (M0 + n_motion * dt1) % (2.0 * np.pi)
        
        pos_obj1_ecl = get_barycentric_ecliptic_pos(a, e, inc, node, peri, M1)
        pos_obj1_eq = ecliptic_to_equatorial(pos_obj1_ecl)
        pos_earth1 = earth_positions[idx]['pos1']
        
        pos_rel1 = pos_obj1_eq - pos_earth1
        delta1 = np.linalg.norm(pos_rel1)
        
        ra1 = np.arctan2(pos_rel1[1], pos_rel1[0]) % (2.0 * np.pi)
        dec1 = np.arcsin(pos_rel1[2] / delta1)
        
        # Bounding box filter (in absolute equatorial angles)
        if dec1 < p['dec_min'] or dec1 > p['dec_max']:
            continue
            
        dx_ra = (ra1 - p['ra_center'] + np.pi) % (2.0 * np.pi) - np.pi
        if dx_ra < p['dx_min'] or dx_ra > p['dx_max']:
            continue
            
        # Precise polygon check
        y_obj = dec1
        x_obj = p['ra_center'] + dx_ra
        if not point_in_polygon(x_obj, y_obj, p['poly_x'], p['poly_y']):
            continue
            
        # Chip gaps check (filling factor)
        if np.random.uniform(0.0, 1.0) > p['ff']:
            continue
            
        # rate of motion check
        dt2 = (p['epoch'] + 2.0 / 24.0) - 2451545.0
        M2 = (M0 + n_motion * dt2) % (2.0 * np.pi)
        pos_obj2_ecl = get_barycentric_ecliptic_pos(a, e, inc, node, peri, M2)
        pos_obj2_eq = ecliptic_to_equatorial(pos_obj2_ecl)
        pos_earth2 = earth_positions[idx]['pos2']
        pos_rel2 = pos_obj2_eq - pos_earth2
        delta2 = np.linalg.norm(pos_rel2)
        ra2 = np.arctan2(pos_rel2[1], pos_rel2[0]) % (2.0 * np.pi)
        dec2 = np.arcsin(pos_rel2[2] / delta2)
        
        dt_days = 2.0 / 24.0
        d_ra_west = ((ra1 - ra2 + np.pi) % (2.0 * np.pi) - np.pi) / dt_days * np.cos(dec1)
        d_dec_north = (dec2 - dec1) / dt_days
        
        rate_rad_day = np.sqrt(d_ra_west**2 + d_dec_north**2)
        rate_arcsec_hr = rate_rad_day * 206264.806 / 24.0
        angle_rad = np.arctan2(d_dec_north, d_ra_west)
        
        rc = p['eff']['rate_cut']
        if rate_rad_day < rc[0] or rate_rad_day > rc[1]:
            continue
            
        diff_angle = (rc[2] - angle_rad + np.pi) % (2.0 * np.pi) - np.pi
        if abs(diff_angle) > rc[3]:
            continue
            
        # Apparent magnitude computation
        r_sun1 = np.linalg.norm(pos_obj1_ecl)
        r_earth_sun = np.linalg.norm(pos_earth1)
        cos_alpha = (-r_earth_sun**2 + delta1**2 + r_sun1**2) / (2.0 * r_sun1 * delta1)
        alpha = np.arccos(min(1.0, max(-1.0, cos_alpha)))
        
        phi1 = np.exp(-3.33 * (np.tan(alpha / 2.0))**0.63)
        phi2 = np.exp(-1.87 * (np.tan(alpha / 2.0))**1.22)
        
        filt = p['eff']['filter']
        f_idx = filter_color_indices.get(filt, 1)
        H_f = H_x + color[f_idx]
        
        m_int = 5.0 * np.log10(r_sun1 * delta1) + H_f - 2.5 * np.log10((1.0 - 0.15) * phi1 + 0.15 * phi2)
        
        eta_raw, maglim = compute_efficiency_raw(p['eff']['rate_ranges'], m_int, rate_rad_day)
        if eta_raw < 0.01:
            continue
            
        m_rand, magerr = generate_magnitude_error(m_int, p['eff']['mag_error'])
        eff_rand, maglim = compute_efficiency_raw(p['eff']['rate_ranges'], m_rand, rate_rad_day)
        if np.random.uniform(0.0, 1.0) > eff_rand:
            continue
            
        flag_val = 1
        if maglim > 0.0:
            if m_rand <= maglim:
                flag_val += 2
        else:
            if eff_rand >= 0.4:
                flag_val += 2
                
        tf = p['eff']['track_frac']
        track_prob = min(tf[0], 1.0 + (m_rand - tf[1]) * tf[2])
        if np.random.uniform(0.0, 1.0) <= track_prob:
            flag_val += 1
            
        if flag_val > best_flag:
            best_flag = flag_val
            
        if best_flag >= 4:
            return True
            
    return False

# Generate selection-biased null population
print("\nPhase 2: Generating synthetic Scattered-Disk population...")
num_simulated = 10000000 # Increased pool limit
simulated_varpi = []

# Scattered-disk model parameters:
# a in [150, 1000] AU, power-law index -1.5
# q in [30, 80] AU, uniform
# i sin-weighted Gaussian, sigma = 15 degrees
# H in [5, 9], power-law index 0.4
sigma_i = np.radians(15.0)
w_max = np.sin(np.radians(15.0)) * np.exp(-0.5)

a_min, a_max = 150.0, 1000.0
q_min, q_max = 30.0, 80.0
H_min, H_max = 5.0, 9.0
alpha_H = 0.4

count_det = 0
for idx in range(num_simulated):
    u_a = np.random.uniform(0.0, 1.0)
    a = (u_a * (a_max**(-0.5) - a_min**(-0.5)) + a_min**(-0.5))**(-2.0)
    q = np.random.uniform(q_min, q_max)
    e = 1.0 - q / a
    if e >= 1.0 or e < 0.0:
        continue
        
    while True:
        i_val = np.random.uniform(0.0, np.pi / 2.0)
        weight = np.sin(i_val) * np.exp(-i_val**2 / (2.0 * sigma_i**2))
        if np.random.uniform(0.0, 1.0) <= weight / w_max:
            inc = i_val
            break
            
    Omega = np.random.uniform(0.0, 2.0 * np.pi)
    omega = np.random.uniform(0.0, 2.0 * np.pi)
    M0 = np.random.uniform(0.0, 2.0 * np.pi)
    
    u_h = np.random.uniform(0.0, 1.0)
    H_val = np.log10(u_h * (10.0**(alpha_H * H_max) - 10.0**(alpha_H * H_min)) + 10.0**(alpha_H * H_min)) / alpha_H
    
    colors = [0.0] * 10
    
    if check_detection(a, e, inc, Omega, omega, M0, H_val, colors):
        varpi = np.degrees(omega + Omega) % 360.0
        simulated_varpi.append(varpi)
        count_det += 1
        # Print progress every 250 detections
        if count_det % 250 == 0:
            print(f"  Generated {count_det} detections (processed {idx+1} candidates)...")
        
    if count_det >= 2000: # 2k detections is highly sufficient and fast
        break

print(f"Generated {count_det} simulated detections from scattered disk null model.")

with open('simulated_null_varpi.txt', 'w') as f:
    for v in simulated_varpi:
        f.write(f"{v:.5f}\n")

# ----------------- Observed eTNO Detections -----------------
# We define three sample configurations:
# 1. Old sample (N=4)
# 2. Reconstructed Convention A characterized sample (N=9)
# 3. Reconstructed Convention B characterized sample (N=3)

old_sample_varpi = [(ob['omega'] + ob['Omega']) % 360.0 for ob in [
    {'name': 'o3e39', 'a': 150.24, 'e': 0.727, 'q': 41.03, 'i': 33.539, 'Omega': 210.727, 'omega': 42.588},
    {'name': 'o3l83', 'a': 200.26, 'e': 0.781, 'q': 43.93, 'i': 10.652, 'Omega': 191.954, 'omega': 252.127},
    {'name': 'L3h08', 'a': 159.68, 'e': 0.761, 'q': 38.10, 'i': 15.500, 'Omega': 197.871, 'omega': 10.841},
    {'name': 'L5r01', 'a': 153.76, 'e': 0.746, 'q': 39.00, 'i': 20.447, 'Omega': 306.114, 'omega': 32.537}
]]

# Reconstructed characterized sample A (a > 150 AU, q > 30 AU): 9 objects
# Includes CFEPS (L3h08, L5r01) and characterized OSSOS from Table 1 of Shankman et al. (2017)
# (excluding uncharacterized uo3l91/2013 SY99)
reconstructed_a_varpi = [
    208.712, # L3h08
    338.651, # L5r01
    253.315, # 2013 GP136 (o3e39)
    298.400, # 2015 KH163 (o5m85)
    84.081,  # 2013 UT15 (o3l83)
    336.000, # 2015 RY245 (o5s13)
    175.100, # 2015 GT50 (o5p060)
    73.800,  # 2015 RX245 (o5t52)
    251.200  # 2015 KG163 (o5m52)
]

# Reconstructed characterized sample B (a > 250 AU, q > 30 AU): 3 objects
reconstructed_b_varpi = [
    175.100, # 2015 GT50 (o5p060)
    73.800,  # 2015 RX245 (o5t52)
    251.200  # 2015 KG163 (o5m52)
]

def calc_rayleigh(angles_deg):
    angles_rad = np.radians(angles_deg)
    sum_cos = np.sum(np.cos(angles_rad))
    sum_sin = np.sum(np.sin(angles_rad))
    R = np.sqrt(sum_cos**2 + sum_sin**2)
    return R

simulated_varpi = np.array(simulated_varpi)

# Run Monte Carlo Rayleigh tests
def run_mc_analysis(observed_varpi, null_pool, name, n_trials=10000):
    R_obs = calc_rayleigh(observed_varpi)
    N = len(observed_varpi)
    R_sims = []
    for _ in range(n_trials):
        samples = np.random.choice(null_pool, size=N, replace=True)
        R_sims.append(calc_rayleigh(samples))
    R_sims = np.array(R_sims)
    p_value = np.sum(R_sims >= R_obs) / n_trials
    return R_obs, p_value

# Perform evaluations
# We do NOT re-seed between runs to preserve the sequential state of np.random,
# but we document the results under the original random flow.
# Let's run the old sample first to match the original random flow.
R_old, p_old = run_mc_analysis(old_sample_varpi, simulated_varpi, "Old Sample")

# For the new samples, let's run them too
R_new_a, p_new_a = run_mc_analysis(reconstructed_a_varpi, simulated_varpi, "Reconstructed Convention A")
R_new_b, p_new_b = run_mc_analysis(reconstructed_b_varpi, simulated_varpi, "Reconstructed Convention B")

print("\n--- Consolidated Rayleigh Test Results ---")
print(f"Old Sample (N=4): R_obs={R_old:.5f}, p_value={p_old:.5f}")
print(f"Reconstructed Convention A (N=9): R_obs={R_new_a:.5f}, p_value={p_new_a:.5f}")
print(f"Reconstructed Convention B (N=3): R_obs={R_new_b:.5f}, p_value={p_new_b:.5f}")

# Save results to clustering_results.txt
with open('clustering_results.txt', 'w') as f:
    f.write(f"--- Old Sample (N=4) ---\n")
    f.write(f"R_obs={R_old:.5f}\n")
    f.write(f"p_value={p_old:.5f}\n")
    f.write(f"observed_varpi={','.join(map(str, old_sample_varpi))}\n\n")
    
    f.write(f"--- Reconstructed Convention A (N=9) ---\n")
    f.write(f"R_obs={R_new_a:.5f}\n")
    f.write(f"p_value={p_new_a:.5f}\n")
    f.write(f"observed_varpi={','.join(map(str, reconstructed_a_varpi))}\n\n")
    
    f.write(f"--- Reconstructed Convention B (N=3) ---\n")
    f.write(f"R_obs={R_new_b:.5f}\n")
    f.write(f"p_value={p_new_b:.5f}\n")
    f.write(f"observed_varpi={','.join(map(str, reconstructed_b_varpi))}\n")

print("\nClustering test completed and consolidated results saved to 'clustering_results.txt'.")
