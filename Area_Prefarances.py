import streamlit as st
import streamlit.components.v1 as components
import pymongo
import hashlib
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from shapely.geometry import Point
import osmnx as ox
import os
import pandas as pd
from branca.element import Template, MacroElement
from fpdf import FPDF
import base64
import numpy as np

# --- CONFIGURE TIMEOUT ---
ox.settings.timeout = 180 

# ==========================================
# PART 0: FILE PATHS & ASSETS
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GEOJSON_FILENAME = "suburbs.geojson"
GEOJSON_PATH = os.path.join(SCRIPT_DIR, GEOJSON_FILENAME)

# ==========================================
# PART 1: STYLING ENGINE (CSS)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;500;700;800&family=Roboto:wght@300;400;700&display=swap');
        
        html, body, [class*="css"]  { font-family: 'Roboto', sans-serif; }
        
        /* --- MAIN BACKGROUND --- */
        .stApp {
            background-color: #050A14; /* Deep Dark Blue */
        }

        /* --- SIDEBAR STYLING --- */
        [data-testid="stSidebar"] {
            background-color: #021526; 
            border-right: 1px solid #04cf0b;
        }
        
        [data-testid="stSidebar"] .stRadio label p {
            color: #f50776 !important;
            font-weight: bold;
            font-size: 16px;
        }
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] .stSlider label p {
            color: #f50776 !important;
            font-weight: bold;
        }

        /* --- CARDS & BOXES --- */
        .insight-card { 
            background-color: #021526; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 20px; 
            border: 1px solid #1e2e4a;
            box-shadow: 0 0 15px rgba(4, 207, 11, 0.15); /* Green Glow */
        }

        .report-card {
            background-color: #08101f;
            border: 1px solid #04cf0b;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        /* COLOR BORDERS FOR CARDS */
        .border-blue { border-left: 5px solid #3498db; }
        .border-green { border-left: 5px solid #04cf0b; }
        .border-red { border-left: 5px solid #e74c3c; }
        .border-orange { border-left: 5px solid #f39c12; }

        /* HEADINGS IN CARDS */
        .card-title { 
            font-family: 'Montserrat', sans-serif; 
            font-weight: 800; 
            font-size: 18px; 
            margin-bottom: 10px; 
            color: #f50776 !important; 
            text-transform: uppercase;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 5px;
        }

        /* METRICS */
        div[data-testid="stMetric"] { background-color: #021526; padding: 15px; border-radius: 10px; border: 1px solid #04cf0b; }
        div[data-testid="stMetricLabel"] { color: #04cf0b !important; }
        div[data-testid="stMetricValue"] { color: white !important; }

        /* --- BUTTONS --- */
        .stButton > button, 
        [data-testid="stDownloadButton"] > button,
        .stFormSubmitButton > button { 
            background-color: #04cf0b !important;
            color: #021526 !important;
            border: 2px solid #04cf0b !important; 
            font-weight: 900 !important; 
            text-transform: uppercase; 
            border-radius: 5px;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .stButton > button:hover, 
        [data-testid="stDownloadButton"] > button:hover,
        .stFormSubmitButton > button:hover {
            background-color: #021526 !important;
            color: #04cf0b !important;
            border-color: #04cf0b !important;
            box-shadow: 0 0 10px #04cf0b;
        }
        
        .stTextInput label p, .stTextArea label p, .stSelectbox label p {
            color: #04cf0b !important;
            font-weight: bold;
        }

        /* INSTRUCTION BOX ANIMATION */
        .instruction-box { 
            background: #021526; 
            border: 1px solid #04cf0b;
            padding: 20px; 
            margin-top: 20px; 
            box-shadow: 0 0 20px rgba(4,207,11,0.1); 
            color: white; 
            position: relative; 
            border-radius: 10px;
        }
        
        @keyframes cycleLoop {
            0% { opacity: 0; transform: translateX(50px); }
            10% { opacity: 1; transform: translateX(0); }
            80% { opacity: 1; transform: translateX(0); }
            90% { opacity: 0; transform: translateX(-20px); }
            100% { opacity: 0; transform: translateX(50px); }
        }
        .inst-step { margin-bottom: 12px; font-size: 15px; display: flex; align-items: center; opacity: 0; animation: cycleLoop 12s ease-in-out infinite; color: #04cf0b; }
        .inst-step:nth-child(2) { animation-delay: 0s; } 
        .inst-step:nth-child(3) { animation-delay: 3s; }
        .inst-step:nth-child(4) { animation-delay: 6s; }
        .inst-icon { background: #04cf0b; color: #021526; width: 28px; height: 28px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-right: 15px; font-weight: bold; font-size: 14px; }

    </style>
    """, unsafe_allow_html=True)

def set_login_styling():
    img_url = "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop"
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }} 
    .stApp {{
        background-image: url("{img_url}");
        background-size: cover; 
        background-position: center; 
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .stApp::before {{
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.7); z-index: -1;
    }}
    .stSelectbox label p {{ color: #f50776 !important; font-size: 18px; }}
    .stTextInput label p {{ color: #04cf0b !important; font-weight: bold; font-size: 16px; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# PART 2: DATABASE & AUTH
# ==========================================
@st.cache_resource
def init_connection():
    try: return pymongo.MongoClient(st.secrets["mongo"]["connection_string"]) if "mongo" in st.secrets else None
    except: return None

client = init_connection()
db = client.injecta_market_engine if client else None
users_collection = db.users if db is not None else None

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password, hashed_text): return make_hashes(password) == hashed_text
def create_user(username, password):
    if users_collection is None: return True
    if users_collection.find_one({"username": username}): return False
    users_collection.insert_one({"username": username, "password": make_hashes(password)})
    return True
def login_user(username, password):
    if users_collection is None: return True 
    user = users_collection.find_one({"username": username})
    return user and check_hashes(password, user['password'])

# ==========================================
# PART 3: MAP DATA & PDF UTILS
# ==========================================
@st.cache_data
def load_map_data():
    if not os.path.exists(GEOJSON_PATH): return None
    try:
        gdf = gpd.read_file(GEOJSON_PATH)
        return gdf.to_crs("EPSG:4326") if gdf.crs != "EPSG:4326" else gdf
    except: return None

class MapLegend(MacroElement):
    def __init__(self):
        super(MapLegend, self).__init__()
        self._template = Template("""
        {% macro html(this, kwargs) %}
        <div style="position: fixed; bottom: 30px; left: 30px; width: 150px; background: #021526; border:2px solid #04cf0b; padding: 10px; border-radius: 8px; font-size:12px; z-index:9999; color: white;">
            <b style="color:#04cf0b; text-transform:uppercase;">Map Key</b><br>
            <i style="background:#04cf0b; width:8px; height:8px; display:inline-block; border-radius:50%;"></i> Schools<br>
            <i style="background:#00008B; width:8px; height:8px; display:inline-block; border-radius:50%; border:1px solid white;"></i> Health<br>
            <i style="background:#cf1a07; width:8px; height:8px; display:inline-block; border-radius:50%;"></i> Markets<br>
            <i style="background:#f8f334; width:8px; height:8px; display:inline-block; border-radius:50%; border:1px solid #999;"></i> Shops<br>
        </div>
        {% endmacro %}""")

def generate_pdf(results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(15, 44, 89)
    pdf.cell(0, 10, "Injecta Analytics - Strategic Report", ln=True, align='C')
    pdf.ln(10)
    
    # Suburb Info
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, f"Location Info: {results.get('suburb_text', 'N/A')}")
    pdf.cell(0, 8, f"Density Profile: {results.get('strategy', 'N/A')}", ln=True)
    pdf.ln(5)

    # Stats
    stats = results.get('stats', {})
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Site Statistics:", ln=True)
    pdf.set_font("Arial", '', 10)
    for key, val in stats.items():
        pdf.cell(0, 6, f"- {key}: {val}", ln=True)
    pdf.ln(5)

    # Recommendations
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Strategic Recommendations:", ln=True)
    pdf.set_font("Arial", '', 11)
    
    recs = results.get('recommendations', [])
    for rec in recs:
        clean_rec = rec.replace("<b>", "").replace("</b>", "").replace("**", "").replace("<span style='color:#04cf0b; font-weight:bold;'>", "").replace("</span>", "")
        clean_rec = clean_rec.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, f"- {clean_rec}")
        pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# PART 4: MAIN APP
# ==========================================
st.set_page_config(layout="wide", page_title="Injecta Market-Match", initial_sidebar_state="expanded")
inject_custom_css()

# Session State
for key in ['logged_in', 'username', 'analysis_active', 'lat', 'lon', 'analysis_results']:
    if key not in st.session_state:
        if key == 'lat': val = -17.8252
        elif key == 'lon': val = 31.0335
        elif key == 'analysis_results': val = None
        else: val = False if key in ['logged_in','analysis_active'] else ''
        st.session_state[key] = val

def format_rec(text):
    return f"<span style='color:#04cf0b; font-weight:bold;'>{text}</span>"

def main():
    if not st.session_state['logged_in']:
        set_login_styling()
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            with st.container(border=True):
                st.markdown("<div style='text-align:center; color:red; font-weight:800; font-size:26px; margin-bottom:20px;'>WELCOME TO INJECTA ANALYTICS</div>", unsafe_allow_html=True)
                
                menu = ["Login", "Register"]
                choice = st.selectbox("Select Option", menu)
                
                if choice == "Login":
                    with st.form("login"):
                        u = st.text_input("Username"); p = st.text_input("Password", type='password')
                        if st.form_submit_button("LOGIN & OPEN PORTAL"):
                            if login_user(u, p): st.session_state.update({'logged_in':True, 'username':u}); st.rerun()
                            else: st.error("Invalid Credentials.")
                else:
                    with st.form("reg"):
                        u = st.text_input("New User"); p = st.text_input("New Pass", type='password')
                        if st.form_submit_button("CREATE ACCOUNT"):
                            if create_user(u, p): st.session_state.update({'logged_in':True, 'username':u}); st.rerun()
                            else: st.error("Username taken.")
    else:
        # --- SIDEBAR ---
        nav_options = ["Market Engine", "Reporting", "About Us", "Contact Us"]
        selection = st.sidebar.radio("Menu", nav_options, label_visibility="collapsed")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"<span style='color:white;'>User:</span> <b style='color:#f50776; font-size:18px;'>{st.session_state['username']}</b>", unsafe_allow_html=True)
        
        if st.sidebar.button("Log Out"): st.session_state.update({'logged_in':False, 'analysis_active':False, 'analysis_results':None}); st.rerun()
        
        # --- MARKET ENGINE ---
        if selection == "Market Engine":
            st.sidebar.header("Radius Adjustments") 
            radius = st.sidebar.slider("Radius (m)", 500, 5000, 1000)
            
            if st.session_state['analysis_active']:
                if st.sidebar.button("🔄 Reset Analysis"): st.session_state['analysis_active'] = False; st.rerun()
            else:
                if st.sidebar.button("🚀 Run Analysis"): st.session_state['analysis_active'] = True; st.rerun()

            # VIDEO PLAYER
            video_filename = "intro_video.mp4"
            video_path = os.path.join(SCRIPT_DIR, video_filename)
            if os.path.exists(video_path):
                try:
                    with open(video_path, "rb") as f:
                        video_bytes = f.read()
                        b64 = base64.b64encode(video_bytes).decode()
                    st.sidebar.markdown(f"""
                        <video width="100%" autoplay loop muted playsinline style="border-radius: 5px; border:1px solid #04cf0b; margin-top:20px;">
                            <source src="data:video/mp4;base64,{b64}" type="video/mp4">
                        </video>
                        <div style="font-size:11px;color:#04cf0b;text-align:center;">Live Analytics Feed</div>
                    """, unsafe_allow_html=True)
                except: pass

            # HEADING -> PINK #f50776
            st.markdown("<div style='font-family:Montserrat; font-weight:800; font-size:32px; color:#f50776;'>INJECTA ANALYTICS MARKET ENGINE</div>", unsafe_allow_html=True)
            
            # 1. Map Data Preparation
            gdf_suburbs = load_map_data()
            match = gpd.GeoDataFrame()
            display_text_suburbs = "No Zone Selected"
            display_pop_label = "Population"
            display_pop_val = "N/A"
            final_strategy = "Medium Density"

            if gdf_suburbs is not None:
                try:
                    pt = gpd.GeoDataFrame(geometry=[Point(st.session_state['lon'], st.session_state['lat'])], crs="EPSG:4326")
                    buf = pt.to_crs(epsg=3857).buffer(radius).to_crs(epsg=4326)
                    match = gdf_suburbs[gdf_suburbs.intersects(buf.geometry.iloc[0])]
                    
                    if not match.empty:
                        cols = match.columns.str.lower()
                        name_col = match.columns[cols == 'name'][0] if 'name' in cols else None
                        found_names = match[name_col].tolist() if name_col else []
                        
                        if len(match) > 1:
                            display_text_suburbs = f"Site borders: {', '.join(found_names)}"
                            display_pop_label = "Avg Population"
                            
                            if 'density' in cols:
                                dens_col = match.columns[cols=='density'][0]
                                modes = match[dens_col].mode()
                                if not modes.empty:
                                    raw_strat = str(modes[0])
                                    if "High" in raw_strat: final_strategy = "High Density area detected!!"
                                    elif "Low" in raw_strat: final_strategy = "Low Density"
                                    else: final_strategy = "Medium Density detected!!"
                            
                            total_pop = 0; count_pop = 0
                            for _, r in match.iterrows():
                                for p in ['pop', 'population', 'pop_est']:
                                    if p in cols:
                                        try: 
                                            total_pop += int(str(r[match.columns[cols==p][0]]).replace(",",""))
                                            count_pop += 1; break
                                        except: pass
                            if count_pop > 0: display_pop_val = f"{int(total_pop / count_pop):,}"
                        else:
                            display_text_suburbs = found_names[0] if found_names else "Unknown"
                            if 'density' in cols:
                                d = str(match.iloc[0][match.columns[cols=='density'][0]])
                                if "High" in d: final_strategy = "High Density area detected!!"
                                elif "Low" in d: final_strategy = "Low Density"
                                else: final_strategy = "Medium Density detected!!"
                            
                            for p in ['pop', 'population', 'pop_est']:
                                if p in cols:
                                    try: 
                                        display_pop_val = f"{int(str(match.iloc[0][match.columns[cols==p][0]]).replace(',','')):,}"
                                        break
                                    except: pass
                except: pass

            if not match.empty:
                # LOCATION TEXT -> ORANGE TEXT, NO BORDER
                st.markdown(f"<div style='color:#fa8602; font-weight:bold; font-size:16px; margin-bottom:10px; padding:10px;'>📍 Location: {display_text_suburbs}</div>", unsafe_allow_html=True)

            # 2. Render Map
            m = folium.Map(location=[st.session_state['lat'], st.session_state['lon']], zoom_start=14)
            folium.Marker([st.session_state['lat'], st.session_state['lon']], icon=folium.Icon(color="red", icon="home")).add_to(m)
            
            # RADIUS CIRCLE -> ORANGE
            folium.Circle([st.session_state['lat'], st.session_state['lon']], radius=radius, color="#fa8602", fill=False).add_to(m)
            
            if not match.empty: folium.GeoJson(match, style_function=lambda x: {'fillColor': '#0c25f7', 'color': '#0c25f7', 'weight': 2, 'fillOpacity': 0.1}).add_to(m)

            schools=gpd.GeoDataFrame(); health=gpd.GeoDataFrame(); bus=gpd.GeoDataFrame()
            markets=gpd.GeoDataFrame(); supermarkets=gpd.GeoDataFrame(); finance=gpd.GeoDataFrame()
            alcohol=gpd.GeoDataFrame(); universities=gpd.GeoDataFrame()

            if st.session_state['analysis_active']:
                with st.spinner("Scanning amenities..."):
                    try:
                        tags = {
                            'amenity': ['school','college','university','clinic','hospital','marketplace','bar','pub','bank'], 
                            'highway': ['bus_stop'], 
                            'shop': ['supermarket','alcohol']
                        }
                        f = ox.features_from_point((st.session_state['lat'], st.session_state['lon']), tags, dist=radius)
                        cp = gpd.GeoSeries([Point(st.session_state['lon'], st.session_state['lat'])], crs="EPSG:4326").to_crs(epsg=3857).buffer(radius).to_crs(epsg=4326).iloc[0]
                        if not f.empty:
                            f = f[f.intersects(cp)]
                            if 'name' not in f.columns: f['name'] = "Unknown"
                            def gc(d,k,v): return d[d[k].isin(v)] if k in d.columns else gpd.GeoDataFrame()
                            
                            schools = gc(f,'amenity',['school'])
                            universities = gc(f,'amenity',['college','university'])
                            health = gc(f,'amenity',['clinic','hospital'])
                            markets = gc(f,'amenity',['marketplace'])
                            supermarkets = gc(f,'shop',['supermarket'])
                            finance = gc(f,'amenity',['bank'])
                            alcohol = pd.concat([gc(f,'amenity',['bar','pub']), gc(f,'shop',['alcohol'])])
                    except: pass

                def ad(g,c): 
                    if not g.empty:
                        for _,r in g.iterrows():
                            gm=r.geometry if r.geometry.geom_type=='Point' else r.geometry.centroid
                            folium.CircleMarker([gm.y,gm.x], radius=5, color="white", fill_color=c, fill_opacity=1, tooltip=str(r.get('name',''))).add_to(m)
                
                ad(schools,"#04cf0b"); ad(universities, "#04cf0b"); ad(health,"#00008B")
                ad(markets,"#cf1a07"); ad(supermarkets,"#f8f334"); ad(finance,"#9b59b6")
                m.add_child(MapLegend())

            m.add_child(folium.LatLngPopup())
            map_out = st_folium(m, height=450, width=1500, returned_objects=["last_clicked"])
            
            if map_out and map_out.get("last_clicked"):
                if abs(map_out["last_clicked"]["lat"] - st.session_state['lat']) > 0.0001:
                    st.session_state['lat'] = map_out["last_clicked"]["lat"]; st.session_state['lon'] = map_out["last_clicked"]["lng"]; st.rerun()

            # INSTRUCTION BOX RESTORED
            if not st.session_state['analysis_active']:
                st.markdown("""<div class="instruction-box">
                <div style="font-weight:800; font-size:20px; color:#04cf0b; margin-bottom:15px;">Ready to Analyze?</div>
                <div class="inst-step"><span class="inst-icon">1</span> Set Radius in Sidebar.</div>
                <div class="inst-step"><span class="inst-icon">2</span> Click Map to Pinpoint Location.</div>
                <div class="inst-step"><span class="inst-icon">3</span> Click 'Run Analysis'.</div>
                </div>""", unsafe_allow_html=True)

            # 3. Recommendations Logic
            if st.session_state['analysis_active']:
                st.markdown("<h3 style='color:#f50776;'>Strategic Recommendations</h3>", unsafe_allow_html=True)
                
                def get_nearest_details(gdf_features, user_point):
                    if gdf_features.empty: return 99999, "None"
                    gdf_meters = gdf_features.to_crs(epsg=32736)
                    user_meters = gpd.GeoSeries([user_point], crs="EPSG:4326").to_crs(epsg=32736).iloc[0]
                    distances = gdf_meters.distance(user_meters)
                    min_idx = distances.idxmin()
                    min_dist = distances.min()
                    feat_name = str(gdf_features.loc[min_idx].get('name', 'Unknown'))
                    if feat_name.lower() in ['nan', 'none', 'unknown', '']: feat_name = f"'nan' (name unlisted)"
                    return min_dist, feat_name

                user_pt = Point(st.session_state['lon'], st.session_state['lat'])
                
                dist_super, name_super = get_nearest_details(supermarkets, user_pt)
                dist_school, name_school = get_nearest_details(schools, user_pt)
                dist_uni, name_uni = get_nearest_details(universities, user_pt)
                dist_health, name_health = get_nearest_details(health, user_pt)
                dist_bank, name_bank = get_nearest_details(finance, user_pt)
                
                recommendations = []
                intro_msg = f"The area selected is a {final_strategy} with the {display_pop_label} of {display_pop_val}."
                
                # STRATEGY MESSAGE -> ORANGE TEXT, NO BORDER
                st.markdown(f"<div style='color:#fa8602; font-weight:bold; font-size:16px; margin-bottom:20px; padding:10px;'>{intro_msg}</div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                # --- LOGIC 1: RETAIL STRATEGY ---
                with col1:
                    st.markdown('<div class="insight-card border-blue"><div class="card-title">Retail Strategy</div>', unsafe_allow_html=True)
                    msg_retail = ""
                    if dist_uni < 500:
                        msg_retail = f"**Tertiary Hub detected!!:** The site is less than 500 meters from a Polytechnic, College, or University ('{name_uni}'). Therefore the largely affected population are students,so we recommend: **Small to Medium Grocery Shop**, **Clothing Shop** (targeting students), and **Informal Sector** services such as **Airtime**."
                    elif schools.empty: 
                        base_msg = "No schools nearby. "
                        if final_strategy == "High Density area detected!!":
                            msg_retail = base_msg + "So there are no tertiary institutions and its a high density with small to medium income earners so Focus on **Tuck Shops with small packaging(Tsaona)**, **Small Grocery shops**,**Hardware** supplies,clothing(mabhero),beauty and cosmetics or plastics shop."
                        elif final_strategy == "Medium Density detected!!":
                            rec_str = "**Supermarket**" if supermarkets.empty else "**Grocery Shop,Super market** (check competition)"
                            msg_retail = base_msg + f"Recommended: {rec_str}, **This is a medium dansity area and there are no supermarkets or grocery shops nearby so focus on Tuck Shop with small to medium packaging,Medium grocery store,average clothing store,tech shop with average gaugates**, or **Boutique**."
                        else:
                            rec_str = ""
                            if supermarkets.empty:
                                rec_str = "This is a low density surbab and most of the population are more likely medium to high income earners and there is no supermarkets nearby. This creates the gape so better focus on a **Supermarket**, **Clothing Stores**, or **Liquor Stores** (especially if there are less than 3 bars nearby)."
                            else:
                                rec_str = "This is a low density surbab and most of the population are more likely medium to high income earners but there is a Supermarkets close.You are encouraged to consider a **High Quality Grocery Store that can compete a supermarket** or **Niche Boutique**."
                            msg_retail = base_msg + rec_str
                    else:
                        if supermarkets.empty or dist_super > 5000:
                            is_far = True; context_str = "no major supermarket was found in the immediate vicinity"
                        else:
                            if dist_super > 400: is_far = True; context_str = f"the closest supermarket ('{name_super}') is {int(dist_super)}m away"
                            else: is_far = False; context_str = f"the closest supermarket ('{name_super}') is {int(dist_super)}m away"

                        if final_strategy == "High Density area detected!!":
                            if is_far: msg_retail = f"This site is in a **High Density** location, the area associated with low income earners. Since {context_str} (which offers a gap in the market), I encourage you to focus on a **Tuck Shop with smaller packages (Tsaona)**, or a **Medium Grocery Shop**, **Small Hardware**, or a **Beverage Shop**."
                            else: msg_retail = f"This site is in a **High Density** location, the area associated with low income earners. Since {context_str} (which is too close), we have discovered competition nearby. Focus mainly on a **Tuck Shop with smaller packages (Tsaona)** and other things that are expensive in supermarkets such as **Vegetables**. A **Hardware** is also a good option."
                        elif final_strategy == "Medium Density detected!!":
                            if is_far: msg_retail = f"This site is in a **Medium Density** location. Since {context_str}, I encourage a **Medium Grocery Shop** that bridges the gap between a supermarket and a tuck shop. Alternatively, consider a **Clothing Store**, **Boutique**, or **Hardware**."
                            else: msg_retail = f"This site is in a **Medium Density** location with competition nearby (as {context_str}). Encourage a **High Competitive Grocery Shop**, or focus on other things such as a **Butchery**."
                        else: 
                            base_low = "This is a **Low Density** suburb, an area mainly populated by high income earners."
                            if is_far: msg_retail = f"{base_low} Since {context_str}, I recommend a **Large Supermarket**, **High-Level Clothing Store**, **Pharmacy**, **Liquor Store**, or **Beauty and Cosmetics**."
                            else: msg_retail = f"{base_low} Since {context_str}, you can do a **Supermarket but venture with a different style**, or focus on other things such as **Horticulture**."

                    st.markdown(format_rec(msg_retail), unsafe_allow_html=True)
                    recommendations.append(msg_retail)
                    st.markdown('</div>', unsafe_allow_html=True)

                # --- LOGIC 2: EDUCATION & FOOD ---
                with col2:
                    if dist_uni < 500:
                        st.markdown('<div class="insight-card border-green"><div class="card-title">Tertiary Education Market</div>', unsafe_allow_html=True)
                        msg = f"**Student Food Economy:** The site is less than 500 meters from a Polytechnic, College, or University ('{name_uni}'). We recommend **Fast Foods services** like (**Chicken Inn, Nandos, KFC**) and **Vending**."
                        st.markdown(format_rec(msg), unsafe_allow_html=True)
                        recommendations.append(msg)
                        st.markdown('</div>', unsafe_allow_html=True)
                    elif not schools.empty:
                        st.markdown('<div class="insight-card border-green"><div class="card-title">School Zone Strategy</div>', unsafe_allow_html=True)
                        if dist_school < 200 or len(schools) > 5:
                            msg = f"**Student Hub:**The Closest school is '{name_school}' ({int(dist_school)}m). Pivot to **Stationery**, **Uniforms**, **Barber**, or **Snacks** with a mix of groceries."
                            st.markdown(format_rec(msg), unsafe_allow_html=True)
                            recommendations.append(msg)
                        else:
                            msg = f"**General Residential:**Based on proximity to schools,the nearest school to the site is '{name_school}' and is {int(dist_school)}m away,which is too far to affect our site. So Focus on general household needs."
                            st.markdown(format_rec(msg), unsafe_allow_html=True)
                            recommendations.append(msg)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="insight-card border-green"><div class="card-title">Education Zone</div>', unsafe_allow_html=True)
                        st.markdown(format_rec("No specific education strategy required (see Retail)."), unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                col3, col4 = st.columns(2)
                
                # --- LOGIC 3: HEALTH ---
                with col3:
                    st.markdown('<div class="insight-card border-red"><div class="card-title">Health Strategy</div>', unsafe_allow_html=True)
                    if health.empty:
                         msg = f"**Healthcare Gap:** No facilities found nearby. Residents lack access. **Strong Opportunity:** Stock **Pain Eaze, Flu remedies, First Aid**."
                    elif dist_health > 500:
                        msg = f"**Healthcare Gap:** Closest facility is '{name_health}' ({int(dist_health)}m). **Opportunity:** Stock **Pain Eaze, Flu remedies, First Aid**."
                    else:
                        msg = f"**Well Serviced:** The closest health facility is '{name_health}' and is {int(dist_health)}m away. Medical supplies are likely not a priority."
                    st.markdown(format_rec(msg), unsafe_allow_html=True)
                    recommendations.append(msg)
                    st.markdown('</div>', unsafe_allow_html=True)

                # --- LOGIC 4: NIGHTLIFE ---
                with col4:
                    st.markdown('<div class="insight-card border-orange"><div class="card-title">Night Economy</div>', unsafe_allow_html=True)
                    dist_night, name_night = get_nearest_details(alcohol, user_pt)
                    if dist_night < 200:
                        msg = f"**Active Nightlife:** Close to '{name_night}' ({int(dist_night)}m). Suitable for **Fast Food**, **Late-night Vending**."
                    else:
                        msg = "Quiet Zone: No immediate nightlife. Align hours with day-time retail."
                    st.markdown(format_rec(msg), unsafe_allow_html=True)
                    recommendations.append(msg)
                    st.markdown('</div>', unsafe_allow_html=True)

                st.session_state['analysis_results'] = {
                    'suburb_text': display_text_suburbs,
                    'strategy': final_strategy,
                    'recommendations': recommendations,
                    'stats': {
                        'Population Label': display_pop_label,
                        'Population Value': display_pop_val,
                        'Schools Found': len(schools),
                        'Universities Found': len(universities),
                        'Supermarkets Found': len(supermarkets),
                        'Health Facilities': len(health)
                    }
                }

        # --- REPORTING TAB ---
        elif selection == "Reporting":
            st.markdown("<h1 style='color:#f50776;'>Strategic Reporting</h1>", unsafe_allow_html=True)
            
            if st.session_state.get('analysis_results'):
                res = st.session_state['analysis_results']
                st.markdown(f"""
                <div class='report-card'>
                    <h3 style='color:#04cf0b; margin-top:0;'>Report for {res['suburb_text']}</h3>
                    <h4 style='color:#04cf0b;'>Market Profile: {res['strategy']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
                    st.markdown("<h4 style='color:#f50776; margin-top:0;'>Key Statistics</h4>", unsafe_allow_html=True)
                    stats = res.get('stats', {})
                    for k,v in stats.items():
                        st.markdown(f"<div style='margin-bottom:5px;'><span style='color:#04cf0b; font-weight:bold;'>{k}:</span> <span style='color:red; font-weight:bold;'>{v}</span></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<div class='report-card'>", unsafe_allow_html=True)
                    st.markdown("<h4 style='color:#f50776; margin-top:0;'>Top Recommendation</h4>", unsafe_allow_html=True)
                    if res['recommendations']:
                        st.markdown(format_rec(res['recommendations'][0]), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("---")
                pdf_bytes = generate_pdf(res)
                st.download_button(label="📥 Download Full PDF Report", data=pdf_bytes, file_name="Injecta_Market_Report.pdf", mime="application/pdf")
            else:
                st.warning("No analysis found. Please go to 'Market Engine' and run an analysis first.")

        # --- ABOUT US (EMBEDDED) ---
        elif selection == "About Us":
            # Using st.components.v1.html to render the raw HTML safely
            injecta_html = """
            <!doctype html><html prefix="og: http://ogp.me/ns#" lang="en">
            <head>      <script async src="https://www.googletagmanager.com/gtag/js?id=G-E0F2HSN6K2"></script>    <script>    cr_track_clicks = true;    window.dataLayer = window.dataLayer || [];    function gtag(){dataLayer.push(arguments);}    gtag('js', new Date());    //      gtag('config', 'G-E0F2HSN6K2');    //   </script>        
                <script>    cr_site_url = "http://www.injectaanalytics.com";    cr_external_new_tab = false;    cr_version = "2.1.2";  </script>
            <meta charset="utf-8">  <meta name="viewport" content="width=device-width, initial-scale=1">
                



            <title>Home — Injecta Analytics</title><link rel="canonical" href="http://www.injectaanalytics.com/"><meta name="description" content="" />






            <meta property="og:title" content="Home — Injecta Analytics" /><meta property="og:description" content="" /><meta property="og:image" content="" /><meta property="og:site_name" content="Injecta Analytics" /><meta property="og:url" content="http://www.injectaanalytics.com/" /><meta property="og:type" content="website" />








            <meta name="twitter:card" content="summary" /><meta name="twitter:title" content="Home — Injecta Analytics"><meta name="twitter:image" content=""><meta name="twitter:description" content=""><meta name="twitter:site" content="@" />






                <link rel="stylesheet" href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/coderedcms/vendor/bootstrap/dist/css/bootstrap.min.css?v=2.1.2">    
                <link rel="stylesheet" href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/coderedcms/css/crx-front.min.css?v=2.1.2">    
                <link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/font-awesome.min.css" rel="stylesheet"/>  <link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/themify-icons.css" rel="stylesheet"/>  <link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/flaticon-set.css" rel="stylesheet"/>  <link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/magnific-popup.css" rel="stylesheet"/>  <link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/owl.theme.default.min.css" rel="stylesheet"/>  <link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/animate.css" rel="stylesheet"/>  <link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/bootsnav.css" rel="stylesheet"/>  <link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/responsive.css" rel="stylesheet"/>  <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@200;300;400;600;700;800&display=swap"        rel="stylesheet">  <link rel="stylesheet" href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/website/css/custom.css">  <link rel="stylesheet" href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/theme.css">

                            <link rel="icon" type="image/webp" href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/favi.2e16d0ba.fill-256x256.format-webp.webp">  <link rel="apple-touch-icon" href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/favi.2e16d0ba.fill-180x180.format-png.png">  <link rel="apple-touch-icon" sizes="120x120" href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/favi.2e16d0ba.fill-120x120.format-png.png">  <link rel="apple-touch-icon" sizes="180x180" href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/favi.2e16d0ba.fill-180x180.format-png.png">  <link rel="apple-touch-icon" sizes="152x152" href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/favi.2e16d0ba.fill-152x152.format-png.png">  <link rel="apple-touch-icon" sizes="167x167" href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/favi.2e16d0ba.fill-167x167.format-png.png">    
            </head>
            <body class="crx-webpage parent-page-1 " id="page-3">  


                <a class="visually-hidden-focusable" href="#content">Skip navigation</a>  
            
            

            <nav class="navbar  navbar-expand-lg navbar-dark  ">  <div class="container">    <a class="navbar-brand" href="/">            Injecta Analytics          </a>    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbar"      aria-controls="navbar" aria-expanded="false" aria-label="Toggle navigation">      <span class="navbar-toggler-icon"></span>    </button>    <div class="collapse navbar-collapse" id="navbar">                        <ul class="navbar-nav " >                


            <li class="nav-item ">    <a href="/"     class="nav-link   "            data-ga-event-category="Navbar">        Home      </a>  </li>


                            


            <li class="nav-item ">    <a href="/blog/"     class="nav-link   "            data-ga-event-category="Navbar">        Blog      </a>  </li>


                            


            <li class="nav-item ">    <a href="/contact-us/"     class="nav-link   "            data-ga-event-category="Navbar">        Contact Us      </a>  </li>


                        </ul>                      </div>  </div></nav>







            <div id="content">                    
                        

            <div class="hero-bg parallax  banner-area bg-gray bg-bottom-center center-mobile top-pad-90 text-combo text-light"  style="background-image:url(https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/Injecta_wall_paper1.max-1600x1600.format-webp.webp);"  >  <div class="hero-fg" style="">        <div class="container crx-grid" >    <div class="row wow fadeInDown">        <div  class="col-md-7 bg-body bg-opacity-10">    <h2 data-block-key="2a4mf">Beyond Location To Intelligence</h2><p data-block-key="2lt9s"></p>
            </div>
                    <div  class="col-md text-center mt-5">    <a href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/Injecta%20Analytics%20Infomercial.mp4" class="popup-youtube light video-play-button item-center relative">                                        <i class="fa fa-play"></i>                                    </a>  </div>
                </div>  </div>
                </div></div>

                    <div class="container-fluid crx-grid" id="services" >    <div class="row ">        <div  class="col-md text-center">    <h2 data-block-key="2yah6">Services</h2><p data-block-key="e7sfg">Helping you understand your consumer and competitive landscape through location data &amp; insight</p>
            </div>
                </div>  </div>
                    <div class="container crx-grid" >    <div class="row ">        <div  class="col-md ">    <div class="text-center" >  <div class="row">    <div class="col-sm-6 col-lg-4">        <div class="card mb-3">      <img class="card-img-top w-100" src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/Services_copy.001.2e16d0ba.fill-800x450.format-webp.webp" alt="">    <div class="card-body">    <h5 class="card-title">Trade Area Analysis</h5>    <p class="card-text">                      Locate your business and calculate the demand for your products and services in various locations.   Features    • Feasibility Studies  • Site Selection  • Market Resear...</p>    <a class="card-link" href="/services/trade-area-analysis/" title="Trade Area Analysis">Read more</a>  </div></div>
                </div>    <div class="col-sm-6 col-lg-4">        <div class="card mb-3">      <img class="card-img-top w-100" src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/Website_Images_Second.2e16d0ba.fill-800x450.format-webp_OUjefbi.webp" alt="">    <div class="card-body">    <h5 class="card-title">Feasibility Studies</h5>    <p class="card-text">                      Identify the most viable site based on market potential for your business.   Features    • Connectivity &amp; Accessibility  • Competitors  • Traffic generators  • Cost ...</p>    <a class="card-link" href="/services/feasibility-studies/" title="Feasibility Studies">Read more</a>  </div></div>
                </div>    <div class="col-sm-6 col-lg-4">        <div class="card mb-3">      <img class="card-img-top w-100" src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/Services_copy.002.2e16d0ba.fill-800x450.format-webp.webp" alt="">    <div class="card-body">    <h5 class="card-title">Property Market Research</h5>    <p class="card-text">                      Providing you with value added location data to make more data driven decisions across the various property market segments   Features    • Neighbourhood Profiles  • Opp...</p>    <a class="card-link" href="/services/property-market-research/" title="Property Market Research">Read more</a>  </div></div>
                </div>    <div class="col-sm-6 col-lg-4">        <div class="card mb-3">      <img class="card-img-top w-100" src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/Services_copy.003.2e16d0ba.fill-800x450.format-webp.webp" alt="">    <div class="card-body">    <h5 class="card-title">Business Mapping and Analysis</h5>    <p class="card-text">                      Analyse the spatial context of your business ecosystem to identify opportunities and challenges.   Features    • Market Dynamics  • Distribution &amp; Concentration  • A...</p>    <a class="card-link" href="/services/business-mapping-and-analysis/" title="Business Mapping and Analysis">Read more</a>  </div></div>
                </div>    <div class="col-sm-6 col-lg-4">        <div class="card mb-3">      <img class="card-img-top w-100" src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/Logistics.2e16d0ba.fill-800x450.format-webp.webp" alt="">    <div class="card-body">    <h5 class="card-title">Logistics &amp; Supply Chain</h5>    <p class="card-text">                     Optimise your supply chain and logistics network through location data.   Features    • Connectivity &amp; Accessibility  • Network Analysis  • Travel Time &amp; Distance...</p>    <a class="card-link" href="/services/logistics-supply-chain/" title="Logistics &amp; Supply Chain">Read more</a>  </div></div>
                </div>    <div class="col-sm-6 col-lg-4">        <div class="card mb-3">      <img class="card-img-top w-100" src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/Services_copy.004.2e16d0ba.fill-800x450.format-webp.webp" alt="">    <div class="card-body">    <h5 class="card-title">Customised Business Solutions</h5>    <p class="card-text">                     Tailor made location insights to address specific business challenges facing organisations   Features    We  combine our proprietary spatial location data with your key b...</p>    <a class="card-link" href="/services/customised-business-solutions/" title="Customised Business Solutions">Read more</a>  </div></div>
                </div>  </div>
            </div>
            </div>
                </div>  </div>
                    <div class="container-fluid crx-grid" id="about" >    <div class="row about-area bg-gray carousel-shadow text-center default-padding">        <div  class="col-md col-lg-4 col-md-10 thumb mx-md-5 mb-sm-5 mb-md-5">    
            <img src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/Screenshot_2023-07-10_at_16.2.max-1600x1600.format-webp.webp" class="img-fluid w-100"  alt="Screenshot 2023-07-10 at 16.27.40">
            </div>
                    <div  class="col-md mx-lg-4">    <h2 data-block-key="soauz">About Injecta Analytics</h2><p data-block-key="ebluv"><b>Helping you understand your consumer and competitive landscape through location data &amp; insights.</b></p><p data-block-key="1gpo"></p><p data-block-key="ds46c">We specialise in location intelligence and provide businesses with insights into how location impacts their operations. Our goal is to help businesses make strategic decisions based on specific customer needs, assets in an area, and competitor presence.</p><p data-block-key="bvcfm">We have vast and unique databases of points of interest across various industries, allowing us to provide valuable insights into a region&#x27;s consumer and competitive landscape. We&#x27;d like to help you leverage location data to enhance your business operations.</p>
                <div class="container">                        <ul>                            <div class="row">                              <div class="col-lg-4">                                <h5> &#x2022; Frame The Problem</h5>                              </div>                              <div class="col order-3">                                <h5> &#x2022; Collect & Analyse Data</h5>                              </div>                              <div class="col order-5">                             <h5> &#x2022; Act On Insights</h5>                              </div>                            </div>                        </ul>
                                    </div>  </div>
                </div>  </div>
                    <div class="container crx-grid" >    <div class="row ">        <div  class="col-md text-center">    <h2 data-block-key="izbx5">Stay up to date with our latest insights</h2>
                <div class="mt-5" >  <div class="row">    <div class="col-sm-6 col-lg-4">        <div class="card mb-3">      <img class="card-img-top w-100" src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/Screenshot_2024-10-06.2e16d0ba.fill-800x450.format-webp.webp" alt="">    <div class="card-body">    <h5 class="card-title">Harare Retail: A Data Perspective On Borrowdale and Enterprise Road</h5>    <p class="card-text">  The report,  Harare Retail: A Data Perspective on Borrowdale and Enterprise Road  (August 2024), analyzes the retail and infrastructure landscape of these two key corridors in Harare. It highlights...</p>    <a class="card-link" href="/blog/harare-retail-a-data-perspective-on-borrowdale-and-enterprise-road/" title="Harare Retail: A Data Perspective On Borrowdale and Enterprise Road">Read more</a>  </div></div>
                </div>    <div class="col-sm-6 col-lg-4">        <div class="card mb-3">      <img class="card-img-top w-100" src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/Ok_Budiriro_Blog_Imag.2e16d0ba.fill-800x450.format-webp.webp" alt="">    <div class="card-body">    <h5 class="card-title">Location Intelligence in Retail Analysis</h5>    <p class="card-text">  Having a prime location is an essential and long-lasting advantage for any retailer, as it cannot be duplicated due to its fixed nature. Location intelligence greatly helps retailers determine the ...</p>    <a class="card-link" href="/blog/location-intelligence-in-retail-analysis/" title="Location Intelligence in Retail Analysis">Read more</a>  </div></div>
                </div>    <div class="col-sm-6 col-lg-4">        <div class="card mb-3">      <img class="card-img-top w-100" src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/kepler.gl5.2e16d0ba.fill-800x450.format-webp.webp" alt="">    <div class="card-body">    <h5 class="card-title">The Cores Of Location Intelligence</h5>    <p class="card-text">    To deliver value through location intelligence, some fundamental processes are critical: Location Discovery, Location Visualisation, Location Analytics, and Location Optimisation. Location intell...</p>    <a class="card-link" href="/blog/the-cores-of-location-intelligence/" title="The Cores Of Location Intelligence">Read more</a>  </div></div>
                </div>  </div>
            </div>
                <a href="/blog/"    data-ga-event-category='Button'  data-ga-event-label='More Articles'    title="More Articles"  class="btn btn-outline-primary btn-lg mt-5 p-3"  >    More Articles  </a>
            </div>
                </div>  </div>
                    <div class="container-fluid crx-grid" >    <div class="row contact-items contact-area bg-gray default-padding">        <div  class="col-md ">    <div class="left-item">                        <div class="info-items">                            <div class="item">                                <div class="icon">                                    <i class="fas fa-map-marked-alt"></i>                                </div>                                <div class="info">                                    <h5>Location</h5>                                    <p>                                        Hurudza House, 7th Floor                                        14-16 Nelson Mandela                                        Harare                                    </p>                                </div>                            </div>                            <div class="item">                                <div class="icon">                                    <i class="fas fa-phone"></i>                                </div>                                <div class="info">                                    <h5>Make a Call</h5>                                    <p>                                        +263 77 607 8402 / +263 77 235 7392                                    </p>                                </div>                            </div>                            <div class="item">                                <div class="icon">                                    <i class="fas fa-envelope-open"></i>                                </div>                                <div class="info">                                    <h5>Send a Mail</h5>                                    <p>                                     info@injectaanalytics.com                                    </p>                                </div>                            </div>                            </div>                    </div>  </div>
                    <div  class="col-md right-item text-center">    <br><br><br><br>    <h2 data-block-key="izbx5">We’d love to hear from you</h2>
                <a href="/contact-us/"    data-ga-event-category='Button'  data-ga-event-label='Contact Us'    title="Contact Us"  class="btn btn-primary btn-lg m-4 p-3"  >    Contact Us  </a>
            </div>
                </div>  </div>
                    
                
                    <div class="container">          </div>    
                        
                        
                </div>
            <div id="content-walls">              </div>
            

            <footer>      <div  class="text-light">      </div>  </footer>



                <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/coderedcms/vendor/bootstrap/dist/js/bootstrap.bundle.min.js?v=2.1.2"></script>  
                <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/coderedcms/js/crx-front.js?v=2.1.2"></script>  
                <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/jquery-1.12.4.min.js"></script>  <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/popper.min.js"></script>
                <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/equal-height.min.js"></script>    <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/jquery.appear.js"></script>    <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/jquery.easing.min.js"></script>  <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/jquery.magnific-popup.min.js"></script>    <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/modernizr.custom.13711.js"></script>    <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/owl.carousel.min.js"></script>    <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/wow.min.js"></script>    <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/progress-bar.min.js"></script>    <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/isotope.pkgd.min.js"></script>    <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/imagesloaded.pkgd.min.js"></script>    <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/count-to.js"></script>    <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/YTPlayer.min.js"></script>    <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/circle-progress.js"></script>    <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/bootsnav.js"></script>    <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/js/main.js"></script>
            <script src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/website/js/custom.js"></script>

                
                
                    </body>
            </html>
            """
            components.html(injecta_html, height=1200, scrolling=True)

        # --- CONTACT US ---
        elif selection == "Contact Us":
            st.markdown("<h1 style='color:#C71585;'>Contact Us</h1>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div class='report-card'>
                    <div style='color:#04cf0b; font-size:18px;'>
                    <b>We'd love to hear from you.</b><br><br>
                    📍 <b style='color:red;'>Address:</b> Innovation Hub, Harare, Zimbabwe<br><br>
                    📧 <b style='color:red;'>Email:</b> support@injectaanalytics.co.zw<br><br>
                    📱 <b style='color:red;'>Phone:</b> +263 77 000 0000
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                with st.form("contact_form"):
                    st.text_input("Name")
                    st.text_input("Email")
                    st.text_area("Message")
                    st.form_submit_button("Send Message")

if __name__ == "__main__":
    main()
