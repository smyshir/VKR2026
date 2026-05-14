import math
from statistics import mean, pstdev


def _line_from_measurement(m: dict) -> tuple[float, float, float]:
    theta = math.radians(m['bearing_deg'])
    a = math.sin(theta)
    b = -math.cos(theta)
    c = -(a * m['uav_x'] + b * m['uav_y'])
    return a, b, c


def pairwise_intersections(measurements: list[dict]) -> list[tuple[float, float]]:
    lines = [_line_from_measurement(m) for m in measurements]
    points = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            a1, b1, c1 = lines[i]
            a2, b2, c2 = lines[j]
            det = a1 * b2 - a2 * b1
            if abs(det) < 1e-9:
                continue
            x = (b1 * c2 - b2 * c1) / det
            y = (c1 * a2 - c2 * a1) / det
            points.append((x, y))
    return points


def weighted_least_squares_intersection(measurements: list[dict]) -> tuple[float, float, float]:
    s_aa = s_ab = s_bb = s_ac = s_bc = 0.0
    for m in measurements:
        a, b, c = _line_from_measurement(m)
        w = m['quality_weight']
        s_aa += w * a * a
        s_ab += w * a * b
        s_bb += w * b * b
        s_ac += w * a * c
        s_bc += w * b * c
    det = s_aa * s_bb - s_ab * s_ab
    if abs(det) < 1e-9:
        raise ValueError('Недостаточная геометрия измерений')
    x = (-s_ac * s_bb + s_ab * s_bc) / det
    y = (-s_aa * s_bc + s_ab * s_ac) / det
    rmse = math.sqrt(sum((point_bearing_error(x, y, m)) ** 2 for m in measurements) / len(measurements))
    return x, y, rmse


def point_bearing_error(x: float, y: float, m: dict) -> float:
    vx = x - m['uav_x']
    vy = y - m['uav_y']
    est_bearing = (math.degrees(math.atan2(vx, vy)) + 360) % 360
    return min((est_bearing - m['bearing_deg']) % 360, (m['bearing_deg'] - est_bearing) % 360)


def preprocess_rows(rows: list[dict], min_quality: float, outlier_sigma: float) -> tuple[list[dict], dict]:
    cleaned = [r for r in rows if None not in (r['uav_x'], r['uav_y'], r['bearing_deg'], r['quality_weight'])]
    dropped_missing = len(rows) - len(cleaned)
    filtered = [r for r in cleaned if r['quality_weight'] >= min_quality]
    dropped_quality = len(cleaned) - len(filtered)
    bearings = [r['bearing_deg'] for r in filtered] or [0.0]
    mu, sigma = mean(bearings), pstdev(bearings) or 1.0
    good, outliers = [], []
    for r in filtered:
        (outliers if abs(r['bearing_deg'] - mu) > outlier_sigma * sigma else good).append(r)
    if len(outliers) > max(1, int(0.2 * len(rows))) and len(good) >= 2:
        repaired = []
        for i, r in enumerate(good):
            repaired.append(r)
            if i < len(good) - 1:
                nxt = good[i + 1]
                repaired.append({'uav_x': (r['uav_x'] + nxt['uav_x']) / 2, 'uav_y': (r['uav_y'] + nxt['uav_y']) / 2, 'bearing_deg': (r['bearing_deg'] + nxt['bearing_deg']) / 2, 'quality_weight': (r['quality_weight'] + nxt['quality_weight']) / 2})
        good = repaired[: len(filtered)]
    return good, {'input_count': len(rows), 'dropped_missing': dropped_missing, 'dropped_low_quality': dropped_quality, 'dropped_outliers': len(outliers), 'output_count': len(good)}


def filter_anomalous_points(points: list[tuple[float, float]], keep_ratio: float = 0.8) -> list[tuple[float, float]]:
    if len(points) < 5:
        return points
    cx = mean([p[0] for p in points])
    cy = mean([p[1] for p in points])
    ranked = sorted(points, key=lambda p: math.dist((cx, cy), p))
    keep_n = max(3, int(len(points) * keep_ratio))
    return ranked[:keep_n]


def convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def area_center_and_radius(points: list[tuple[float, float]]) -> tuple[float, float, float]:
    cx = mean([p[0] for p in points])
    cy = mean([p[1] for p in points])
    radius = max(math.dist((cx, cy), p) for p in points)
    return cx, cy, radius
