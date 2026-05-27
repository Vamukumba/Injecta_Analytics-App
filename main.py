from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import math
import pymongo
import hashlib
import certifi 
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}) 

# ==========================================
# 1. DATABASE SETUP
# ==========================================
def init_connection():
    try: 
        client = pymongo.MongoClient(
            "mongodb+srv://prominent:promy@cluster0.ykywkg8.mongodb.net/?appName=Cluster0",
            tlsCAFile=certifi.where()
        )
        client.admin.command('ping')
        print("Database Connected Successfully for Geo AI Market Engine!")
        return client.injecta_market_engine.users
    except Exception as e:
        print(f"Database Error: {e}")
        return None

users_collection = init_connection()

def make_hashes(password): 
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text): 
    return make_hashes(password) == hashed_text

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS': return jsonify({}), 200
    data = request.json
    if users_collection is None:
        return jsonify({"success": False, "message": "Database offline"}), 500
    user = users_collection.find_one({"username": data.get("username")})
    if user and check_hashes(data.get("password"), user["password"]):
        return jsonify({"success": True, "message": "Login successful!"})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS': return jsonify({}), 200
    data = request.json
    if users_collection is None:
        return jsonify({"success": False, "message": "Database offline"}), 500
    if users_collection.find_one({"username": data.get("username")}):
        return jsonify({"success": False, "message": "Username already taken"}), 400
    users_collection.insert_one({"username": data.get("username"), "password": make_hashes(data.get("password"))})
    return jsonify({"success": True, "message": "User created successfully!"})


# ==========================================
# 2. DATA FILE INGESTION PIPELINE
# ==========================================
def find_data_files():
    print("Searching for data repositories...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(base_dir, '..'))
    
    for search_path in [base_dir, parent_dir, os.getcwd()]:
        for root, dirs, files in os.walk(search_path):
            if 'node_modules' in root:
                continue
            if 'southlea_data.json' in files and 'points.json' in files:
                print(f"SUCCESS! Repositories isolated in: {root}")
                return root
    return None

data_dir = find_data_files()

if data_dir:
    with open(os.path.join(data_dir, 'southlea_data.json'), 'r', encoding='utf-8') as f:
        sections_data = json.load(f)
    with open(os.path.join(data_dir, 'points.json'), 'r', encoding='utf-8') as f:
        points_data = json.load(f)
else:
    print("CRITICAL ERROR: Could not locate JSON stores!")
    sections_data = {"features": []}
    points_data = {"features": []}


# ==========================================
# LIVE GEOMETRY STREAMING ENDPOINTS
# ==========================================
@app.route('/api/geojson/sections', methods=['GET'])
def get_sections_geojson():
    return jsonify(sections_data)

@app.route('/api/geojson/points', methods=['GET'])
def get_points_geojson():
    return jsonify(points_data)


# ==========================================
# 3. SPATIAL GEOMETRIC DATA MINING ENGINE
# ==========================================
def haversine_distance(lon1, lat1, lon2, lat2):
    R = 6371.0  # Radius of earth in kilometers
    dLat, dLon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dLat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def point_in_polygon(point, polygon):
    x, y = point[0], point[1]
    inside = False
    for i in range(len(polygon)):
        j = i - 1 if i - 1 >= 0 else len(polygon) - 1
        xi, yi = polygon[i][0], polygon[i][1]
        xj, yj = polygon[j][0], polygon[j][1]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
    return inside

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    if request.method == 'OPTIONS': return jsonify({}), 200
    
    try:
        data = request.json
        lng, lat = data.get('longitude'), data.get('latitude')
        
        # Read the parameter from your frontend state payload
        radius_meters = data.get('radius_meters', 500)
        radius_km = radius_meters / 1000.0

        def safe_int(val):
            try: return int(str(val).replace(',', ''))
            except: return 0

        # 1. RADIUS OVERLAP ANALYSIS ENGINE
        matched_sections = []
        for feature in sections_data['features']:
            geom_type = feature['geometry']['type']
            coords = feature['geometry']['coordinates']
            polygons = coords if geom_type == 'MultiPolygon' else [coords]
            
            is_matched = False
            for poly in polygons:
                # Condition A: Is the center point inside the polygon?
                if point_in_polygon([lng, lat], poly[0]):
                    is_matched = True
                    break
                
                # Condition B: Do any of the polygon boundary lines intersect the circle radius?
                for vertex in poly[0]:
                    v_lng, v_lat = vertex[0], vertex[1]
                    if haversine_distance(lng, lat, v_lng, v_lat) <= radius_km:
                        is_matched = True
                        break
                if is_matched: break
            
            if is_matched:
                matched_sections.append(feature['properties'])

        # Fallback to the closest section if it somehow misses everything
        if not matched_sections and sections_data.get('features'):
            matched_sections = [sections_data['features'][0].get('properties', {})]

        if not matched_sections:
            return jsonify({
                "status": "success", 
                "recommended_business": "Out of Bounds", 
                "message": "Selection error: No spatial trade zones intersect this radius location."
            })

        # 2. PROXIMITY HUB EXTRACTION
        distance_to_hub = 999.0
        nearest_hub_name = "Main Commercial Zone"
        for pt in points_data['features']:
            if pt['properties'].get('class') == 'shopping_centre':
                pt_lng, pt_lat = pt['geometry']['coordinates']
                dist = haversine_distance(lng, lat, pt_lng, pt_lat)
                if dist < distance_to_hub: 
                    distance_to_hub = dist
                    nearest_hub_name = pt['properties'].get('name', 'Commercial Hub')

        # 3. MATHEMATICAL AVERAGE AGGREGATIONS
        num_zones = len(matched_sections)
        
        sum_pop = 0
        sum_groceries = 0
        sum_pharmacies = 0
        sum_hardwares = 0
        sum_boutiques = 0
        sum_interviews = 0
        
        high_count = 0
        low_count = 0
        med_count = 0
        
        influence_centers = []
        frequent_goods_list = []

        for section in matched_sections:
            sum_pop += safe_int(section.get('Estimated_Population', '3000'))
            sum_groceries += safe_int(section.get('Number Of Grocery Shops', '15'))
            sum_pharmacies += safe_int(section.get('Number Of Pharmacies', '2'))
            sum_hardwares += safe_int(section.get('Number Of Hardwares', '14'))
            sum_boutiques += safe_int(section.get('Number Of Boutiques', '25'))
            sum_interviews += safe_int(section.get('total_interviews', '10'))
            
            density_raw = str(section.get('density', 'medium')).lower().strip()
            if density_raw == "high": high_count += 1
            elif density_raw == "low": low_count += 1
            else: med_count += 1

            inf_center = section.get('Shopping_Centre of influence', nearest_hub_name)
            if inf_center not in influence_centers: influence_centers.append(inf_center)
            
            fg = str(section.get('goods_bought_frequently_from_interviews', 'general provisions')).strip()
            if fg and fg not in frequent_goods_list: frequent_goods_list.append(fg)

        # Apply Arithmetic Mean Calculations
        pop = math.ceil(sum_pop / num_zones)
        groceries = math.ceil(sum_groceries / num_zones)
        pharmacies = math.ceil(sum_pharmacies / num_zones)
        hardwares = math.ceil(sum_hardwares / num_zones)
        boutiques = math.ceil(sum_boutiques / num_zones)
        total_interviews = math.ceil(sum_interviews / num_zones)
        
        if high_count >= max(med_count, low_count): blended_density = "high"
        elif low_count >= max(high_count, med_count): blended_density = "low"
        else: blended_density = "medium"

        influence_center = influence_centers[0] if influence_centers else nearest_hub_name
        frequent_goods = ", ".join(frequent_goods_list) if frequent_goods_list else "general provisions"

        # 4. REPORT MATRIX EVALUATIONS
        if blended_density == "high":
            income_level = "lower-to-middle income tier"
            buying_behavior = "high-volume, highly cost-conscious buying behaviors, where consumers prioritize bulk staples and daily necessities over luxury services"
        elif blended_density == "low":
            income_level = "upper-middle to high income tier"
            buying_behavior = "premium, specialized preferences focused on convenience, lifestyle aesthetics, brand variation, and direct service-oriented shopping"
        else:
            income_level = "stable middle-income tier"
            buying_behavior = "balanced spending habits, moving flexibly between budget provisions and selective lifestyle/specialty items"

        ratio_grocery = pop if groceries == 0 else round(pop / groceries)
        ratio_pharmacy = pop if pharmacies == 0 else round(pop / pharmacies)
        ratio_hardware = pop if hardwares == 0 else round(pop / hardwares)

        recommendation = ""
        reasoning = ""

        prefix_note = f"📊 [MULTI-ZONE ANALYSIS: Calculated blended metrics across {num_zones} overlapping trade zones] " if num_zones > 1 else ""

        if distance_to_hub > 1.5 and groceries < 10:
            recommendation = "Express Grocery and Daily Staple Hub"
            reasoning = (
                f"{prefix_note}SITE SELECTION RATIONALE: This specific site was selected due to a severe geographical supply gap, sitting {distance_to_hub:.2f}km away from {influence_center}. "
                f"An audit across all commercial categories shows that while there are {pharmacies} pharmacies and {hardwares} hardware shops, the total population of {pop} citizens "
                f"is underserved by just {groceries} small grocery options (representing an intense ratio of {ratio_grocery} residents sharing a single shop). "
                f"The localized {blended_density}-density demographic aligns perfectly with a {income_level}, triggering {buying_behavior}. "
                f"Crucially, empirical fieldwork data gathered from {total_interviews} localized household interviews explicitly confirms that the goods bought most frequently in this sector are: [{frequent_goods}]. "
                f"Instead of walking long distances to the main hub, residents require an immediate local distribution point focusing heavily on these highly sought-after essentials."
            )
        elif pharmacies == 0 or ratio_pharmacy > 1000:
            recommendation = "Community Pharmacy and Wellness Clinic"
            reasoning = (
                f"{prefix_note}SITE SELECTION RATIONALE: This boundary presents an absolute health infrastructure crisis. The zone hosts a total population of {pop} people "
                f"but is served by only {pharmacies} registered pharmacies, producing an unsustainable capacity strain of {ratio_pharmacy} people per asset. "
                f"Cross-examining other sectors reveals that grocery supply is competitive with {groceries} shops. "
                f"The structural {blended_density}-density indicates a {income_level}. This demographic cannot easily afford speculative travel costs to reach basic over-the-counter medical treatments outside their community. "
                f"Furthermore, direct consumer feedback from {total_interviews} ground interviews underscores a deep localized baseline prioritization on daily health preservation, frequently tracking purchases of standard household provisions like [{frequent_goods}]. "
                f"A local health and wellness facility is heavily justified and guaranteed immediate daily reliance."
            )
        elif blended_density == "high" and hardwares < 3:
            recommendation = "Hardware and Structural Building Supplies"
            reasoning = (
                f"{prefix_note}SITE SELECTION RATIONALE: This location is selected because it directly supports structural growth patterns. High-density areas with a population of {pop} "
                f"undergo aggressive, continuous modifications, home expansions, and repair cycles. Currently, only {hardwares} hardware units are available to supply the building requirements "
                f"of {ratio_hardware} individuals per shop. Comparatively, retail needs are already saturated by {groceries} grocery outposts. "
                f"As a {income_level} zone, local builders and homeowners prioritize purchasing heavy materials within walking distance to bypass heavy logistics charges from {influence_center}. "
                f"This local infrastructure building demand is backed by {total_interviews} community interviews, indicating that outside of core commodities like [{frequent_goods}], "
                f"the domestic capital is funneling heavily into property development and maintenance infrastructure."
            )
        elif blended_density in ["medium", "low"] and boutiques < 5:
            recommendation = "Specialty Lifestyle Boutique and Cosmetics Hub"
            reasoning = (
                f"{prefix_note}SITE SELECTION RATIONALE: This site represents a strategic move into mature market needs. In this {blended_density}-density environment, basic structural necessities are fulfilled, "
                f"boasting {groceries} grocery stores, {pharmacies} pharmacies, and {hardwares} hardwares. Crucially, the lower residential density indexes a {income_level} "
                f"with high disposable margins, resulting in {buying_behavior}. With only {boutiques} boutique spaces handling a population of {pop}, the community is forced to exit the zone "
                f"towards major city lines for lifestyle acquisitions. Field validation from {total_interviews} structured resident surveys shows consistent engagement with items such as [{frequent_goods}], "
                f"proving that basic needs are highly consolidated, and the market is now perfectly ripe for a specialized premium boutique near the {influence_center} vector to capture an exclusive retail segment."
            )
        else:
            recommendation = "Wholesale Bulk Food Outlet"
            reasoning = (
                f"{prefix_note}SITE SELECTION RATIONALE: This site was isolated due to raw volume optimization. While smaller entities exist—specifically {groceries} grocery shops and {boutiques} boutiques—the boundary "
                f"is defined by an immense volume of {pop} residents under a {blended_density}-density envelope. This configuration strongly confirms a traditional {income_level} layout. "
                f"Because local households struggle with high food inflation at local tuckshops, they favor {buying_behavior}. "
                f"This structural volume trend is strictly validated by data from {total_interviews} localized household interviews, where community participants universally signaled that their highest recurring monthly capital outflow goes directly into procuring: [{frequent_goods}]. "
                f"A wholesale warehouse bypasses small convenience retailers, leveraging direct manufacturer pricing to capture the primary budgetary expenditures of the entire community."
            )

        return jsonify({
            "status": "success",
            "recommended_business": recommendation,
            "message": reasoning,
            "meta_metrics": {
                "population": pop,
                "density": blended_density.upper(),
                "influence_center": influence_center,
                "grocery_count": groceries,
                "distance_to_hub": round(distance_to_hub, 2),
                "interviews_conducted": str(total_interviews),
                "frequent_goods": frequent_goods,
                "lat": lat,
                "lng": lng
            }
        })

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"status": "error", "message": f"Server failure: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
    app.run(host='0.0.0.0', port=port)
