import requests
import time

# Known exact points
KNOWN = [
    {"lat": 43.129635, "lng": 77.055286},  # 1 - exact (email 1.jpg)
    None,                                    # 2 - unknown (15:49)
    {"lat": 43.127049, "lng": 77.054271},  # 3 - exact (email 4.jpg)
    {"lat": 43.125896, "lng": 77.053974},  # 4 - exact (Durov GPS)
    None,                                    # 5 - unknown (16:16)
    {"lat": 43.120888, "lng": 77.053866},  # 6 - exact (email 8.jpg)
]

URL = "http://forgotten-vd7j8ty4.alfactf.ru/api/verify"

def try_points(p2, p5):
    points = [KNOWN[0], p2, KNOWN[2], KNOWN[3], p5, KNOWN[5]]
    try:
        r = requests.post(URL, json={"points": points}, timeout=5)
        data = r.json()
        if data.get("valid"):
            print(f"\n🎉 НАЙДЕНО! p2={p2}, p5={p5}")
            print(data)
            return True
        # Print any non-standard messages
        msg = data.get("message", "")
        if "правиль" not in msg and "неправиль" not in msg:
            print(f"  Unusual msg: {msg} | p2={p2} p5={p5}")
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
    return False

print("=== Brute force маршрута Горельник ===")
print(f"URL: {URL}")
print()

found = False
count = 0

# Strategy: search on a grid with step 0.0001 (~10m)
# Point 2: near 43.1289, 77.0550 (6 min from pt1, trail going south)
# Point 5: near 43.1249, 77.0540 (9 min from pt4, trail going south)

# First pass: coarse grid step=0.0002 (~20m), range +-0.003
print("Pass 1: coarse grid (step=0.0002, range +-0.005)...")
for lat2_i in range(-25, 26):
    lat2 = round(43.1289 + lat2_i * 0.0002, 6)
    lon2 = 77.0550  # longitude barely changes along trail

    for lat5_i in range(-25, 26):
        lat5 = round(43.1249 + lat5_i * 0.0002, 6)
        lon5 = 77.0540

        p2 = {"lat": lat2, "lng": lon2}
        p5 = {"lat": lat5, "lng": lon5}
        count += 1

        if try_points(p2, p5):
            found = True
            break
    if found:
        break

if not found:
    print(f"\nPass 2: fine grid with lon variation (step=0.0001)...")
    for lat2_i in range(-30, 31):
        lat2 = round(43.1289 + lat2_i * 0.0001, 6)
        for lon2_i in range(-15, 16):
            lon2 = round(77.0550 + lon2_i * 0.0001, 6)

            for lat5_i in range(-30, 31):
                lat5 = round(43.1249 + lat5_i * 0.0001, 6)
                for lon5_i in range(-15, 16):
                    lon5 = round(77.0540 + lon5_i * 0.0001, 6)

                    p2 = {"lat": lat2, "lng": lon2}
                    p5 = {"lat": lat5, "lng": lon5}
                    count += 1

                    if count % 5000 == 0:
                        print(f"  Tried {count}... lat2={lat2} lon2={lon2} lat5={lat5} lon5={lon5}")

                    if try_points(p2, p5):
                        found = True
                        break
                if found: break
            if found: break
        if found: break

print(f"\nTotal attempts: {count}")
if not found:
    print("Не нашли. Попробуй расширить диапазон поиска.")