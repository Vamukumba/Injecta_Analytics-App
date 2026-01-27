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

# --- CONFIGURE TIMEOUT ---
ox.settings.timeout = 180 

# ==========================================
# PART 0: FILE PATHS & ASSETS
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GEOJSON_FILENAME = "suburbs.geojson"
GEOJSON_PATH = os.path.join(SCRIPT_DIR, GEOJSON_FILENAME)

# THE INJECTA WEBSITE HTML
INJECTA_WEBSITE_HTML = """
<!doctype html><html prefix="og: http://ogp.me/ns#" lang="en">
<head>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-E0F2HSN6K2"></script>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Home — Injecta Analytics</title>
<link rel="stylesheet" href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/coderedcms/vendor/bootstrap/dist/css/bootstrap.min.css?v=2.1.2">    
<link rel="stylesheet" href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/coderedcms/css/crx-front.min.css?v=2.1.2">    
<link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/font-awesome.min.css" rel="stylesheet"/>
<link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/themify-icons.css" rel="stylesheet"/>
<link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/flaticon-set.css" rel="stylesheet"/>
<link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/magnific-popup.css" rel="stylesheet"/>
<link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/owl.theme.default.min.css" rel="stylesheet"/>
<link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/animate.css" rel="stylesheet"/>
<link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/bootsnav.css" rel="stylesheet"/>
<link href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/responsive.css" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@200;300;400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/website/css/custom.css">
<link rel="stylesheet" href="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/assets/css/theme.css">
<style>body { overflow-x: hidden; }</style>
</head>
<body class="crx-webpage">
<div class="hero-bg parallax banner-area bg-gray bg-bottom-center center-mobile top-pad-90 text-combo text-light" style="background-image:url(https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/Injecta_wall_paper1.max-1600x1600.format-webp.webp);">
<div class="hero-fg"><div class="container crx-grid"><div class="row wow fadeInDown"><div class="col-md-7 bg-body bg-opacity-10"><h2 style="color:white; font-size:3rem; font-weight:800;">Beyond Location To Intelligence</h2></div></div></div></div></div>
<div class="container-fluid crx-grid" id="services" style="padding:50px 0;"><div class="row"><div class="col-md text-center"><h2>Services</h2><p>Helping you understand your consumer and competitive landscape through location data & insight</p></div></div></div>
<div class="container crx-grid"><div class="row"><div class="col-md"><div class="text-center"><div class="row">
<div class="col-sm-6 col-lg-4"><div class="card mb-3"><img class="card-img-top w-100" src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/Services_copy.001.2e16d0ba.fill-800x450.format-webp.webp"><div class="card-body"><h5 class="card-title">Trade Area Analysis</h5><p class="card-text">Calculate demand for your products in various locations.</p></div></div></div>
<div class="col-sm-6 col-lg-4"><div class="card mb-3"><img class="card-img-top w-100" src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/Website_Images_Second.2e16d0ba.fill-800x450.format-webp_OUjefbi.webp"><div class="card-body"><h5 class="card-title">Feasibility Studies</h5><p class="card-text">Identify viable sites based on market potential.</p></div></div></div>
<div class="col-sm-6 col-lg-4"><div class="card mb-3"><img class="card-img-top w-100" src="https://storage.googleapis.com/injecta-analytics-prod.appspot.com/images/Services_copy.002.2e16d0ba.fill-800x450.format-webp.webp"><div class="card-body"><h5 class="card-title">Property Market Research</h5><p class="card-text">Value added location data for property decisions.</p></div></div></div>
</div></div></div></div></div>
<div class="container-fluid crx-grid" id="about" style="background:#f8f9fa; padding:50px 0;"><div class="row about-area text-center"><div class="col-md mx-lg-4"><h2>About Injecta Analytics</h2><p>We specialise in location intelligence and provide businesses with insights into how location impacts their operations.</p></div></div></div>
</body></html>
"""

# ==========================================
# PART 1: STYLING ENGINE (CSS)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;500;700;800&family=Roboto:wght@300;400;700&display=swap');
        
        html, body, [class*="css"]  { font-family: 'Roboto', sans-serif; }
        
        /* 1. RESET MAIN CONTAINER */
        .block-container { 
            padding-top: 2rem !important; 
            padding-bottom: 0rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            max-width: 100% !important;
        }

        /* --- SIDEBAR STYLING --- */
        [data-testid="stSidebar"] {
            background-image: linear-gradient(rgba(15, 44, 89, 0.95), rgba(15, 44, 89, 0.9)), url("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070");
            background-size: cover; background-position: center;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
            color: white !important;
        }
        
        /* NAVBAR IN SIDEBAR */
        [data-testid="stSidebar"] div[role="radiogroup"] {
            background: rgba(255,255,255,0.1);
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        [data-testid="stSidebar"] label p {
            color: white !important;
            font-size: 15px !important;
            font-weight: 700 !important;
        }
        [data-testid="stSidebar"] label:hover p { color: #00FF7F !important; }

        /* --- LOGIN PAGE STYLING --- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.95) !important;
            padding: 40px !important;
            border-radius: 15px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
            margin-top: 50px;
        }
        .stSelectbox label, .stTextInput label { color: #00FF7F !important; font-weight: 800 !important; text-shadow: 0px 0px 1px rgba(0,0,0,0.2); }
        .stSelectbox div[data-testid="stMarkdownContainer"] p { font-weight: bold; }
        div[data-testid="stFormSubmitButton"] button { background-color: #0F2C59 !important; color: #00FF7F !important; border: 1px solid #00FF7F !important; font-weight: 800; text-transform: uppercase; width: 100%; }
        .login-title { font-family: 'Montserrat', sans-serif; color: #0f2c59; text-align: center; font-weight: 800; font-size: 26px; margin-bottom: 5px; }
        .login-subtitle { font-family: 'Montserrat', sans-serif; color: #d32f2f; text-align: center; font-size: 14px; margin-bottom: 25px; text-transform: uppercase; font-weight: 700; }

        /* --- MAIN DASHBOARD HEADINGS --- */
        .main-title { font-family: 'Montserrat', sans-serif; color: #0F2C59; font-weight: 800; font-size: 32px; text-transform: uppercase; margin-bottom: 0px; line-height: 1.2; }
        .main-subtitle { font-family: 'Montserrat', sans-serif; color: #00FF7F; font-weight: 600; font-size: 16px; margin-bottom: 20px; letter-spacing: 1px; }

        /* ZONE INFO BOX */
        .zone-info-box { background-color: white; border-left: 5px solid #0F2C59; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); color: #333; }

        /* INSTRUCTION BOX & ANIMATION */
        .instruction-box { background: #0F2C59; border-left: 10px solid #00FF7F; padding: 30px; margin-left: -3rem; margin-right: -3rem; width: calc(100% + 6rem); margin-top: -5px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); color: white; position: relative; }
        
        @keyframes cycleLoop {
            0% { opacity: 0; transform: translateX(50px); }
            10% { opacity: 1; transform: translateX(0); }
            80% { opacity: 1; transform: translateX(0); }
            90% { opacity: 0; transform: translateX(-20px); }
            100% { opacity: 0; transform: translateX(50px); }
        }
        .inst-step { margin-bottom: 12px; font-size: 15px; display: flex; align-items: center; opacity: 0; animation: cycleLoop 12s ease-in-out infinite; }
        .inst-step:nth-child(2) { animation-delay: 0s; } 
        .inst-step:nth-child(3) { animation-delay: 3s; }
        .inst-step:nth-child(4) { animation-delay: 6s; }
        .inst-icon { background: #00FF7F; color: #0F2C59; width: 28px; height: 28px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-right: 15px; font-weight: bold; font-size: 14px; }

        /* GENERAL UI */
        .stButton>button { background: linear-gradient(90deg, #0f2c59, #1e5cc6); color: white; border: none; font-weight: bold; text-transform: uppercase; }
        div[data-testid="stMetric"] { background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #1e5cc6; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .insight-card { background-color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 6px solid #ddd; }
        .card-title { font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 18px; margin-bottom: 10px; color: #333; }
        .border-blue { border-left-color: #3498db; } .border-green { border-left-color: #006400; } .border-orange { border-left-color: #e67e22; } .border-red { border-left-color: #00008B; }
    </style>
    """, unsafe_allow_html=True)

def set_login_background():
    imgs = [
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop", 
        "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=2070&auto=format&fit=crop", 
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=2070&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=2015&auto=format&fit=crop"
    ]
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }} 
    .stApp {{
        background-image: url("{imgs[0]}");
        background-size: cover; background-position: center; background-attachment: fixed;
        animation: slide 20s infinite;
    }}
    @keyframes slide {{
        0% {{ background-image: url("{imgs[0]}"); }}
        25% {{ background-image: url("{imgs[1]}"); }}
        50% {{ background-image: url("{imgs[2]}"); }}
        75% {{ background-image: url("{imgs[3]}"); }}
        100% {{ background-image: url("{imgs[0]}"); }}
    }}
    </style>
    """, unsafe_allow_html=True)

def set_dashboard_background():
    st.markdown("""<style>[data-testid="stSidebar"] { display: block; } .stApp { background-image: none; background-color: #f4f6f9; }</style>""", unsafe_allow_html=True)

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
        <div style="position: fixed; bottom: 30px; left: 30px; width: 150px; background: white; border:2px solid #ddd; padding: 10px; border-radius: 8px; font-size:12px; z-index:9999;">
            <b>Map Key</b><br>
            <i style="background:#006400; width:8px; height:8px; display:inline-block; border-radius:50%;"></i> Schools<br>
            <i style="background:#00008B; width:8px; height:8px; display:inline-block; border-radius:50%;"></i> Health<br>
            <i style="background:#cf1a07; width:8px; height:8px; display:inline-block; border-radius:50%;"></i> Markets<br>
            <i style="background:#f8f334; width:8px; height:8px; display:inline-block; border-radius:50%; border:1px solid #999;"></i> Shops<br>
        </div>
        {% endmacro %}""")

def generate_pdf(suburb, strategy, recommendations):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(15, 44, 89)
    pdf.cell(0, 10, "Injecta Analytics - Strategic Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Location: {suburb}", ln=True)
    pdf.cell(0, 10, f"Density Profile: {strategy}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Strategic Recommendations:", ln=True)
    pdf.set_font("Arial", '', 11)
    
    for rec in recommendations:
        # Wrap text to handle long paragraphs
        clean_rec = rec.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, f"- {clean_rec}")
        pdf.ln(3)
        
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, "Generated by Injecta Analytics Engine.", align='C')
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# PART 4: MAIN APP
# ==========================================
st.set_page_config(layout="wide", page_title="Injecta Market-Match", initial_sidebar_state="expanded")
inject_custom_css()

# Session State
for key in ['logged_in', 'username', 'analysis_active', 'lat', 'lon', 'recommendations', 'selected_suburb', 'selected_strategy']:
    if key not in st.session_state:
        if key == 'lat': val = -17.8252
        elif key == 'lon': val = 31.0335
        elif key == 'recommendations': val = []
        elif key == 'selected_suburb': val = "Unknown"
        elif key == 'selected_strategy': val = "Standard"
        else: val = False if key in ['logged_in','analysis_active'] else ''
        st.session_state[key] = val

def main():
    if not st.session_state['logged_in']:
        set_login_background()
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            with st.container(border=True):
                st.markdown("<div class='login-title'>WELCOME TO INJECTA ANALYTICS MARKET ENGINE</div><div class='login-subtitle'>Location Intelligence & Market Strategy</div>", unsafe_allow_html=True)
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
        set_dashboard_background()
        
        # --- SIDEBAR ---
        nav_options = ["Market Engine", "Reporting", "About Us", "Contact Us"]
        selection = st.sidebar.radio("Menu", nav_options, label_visibility="collapsed")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"{st.session_state['username']}")
        if st.sidebar.button("Log Out"): st.session_state.update({'logged_in':False, 'analysis_active':False}); st.rerun()
        
        st.sidebar.markdown("---")
        st.sidebar.header("Radius Adjustments Bar")
        radius = st.sidebar.slider("Radius (m)", 500, 5000, 1000)
        
        if st.session_state['analysis_active']:
            if st.sidebar.button("🔄 Reset"): st.session_state['analysis_active'] = False; st.rerun()
        else:
            if st.sidebar.button("🚀 Analyze"): st.session_state['analysis_active'] = True; st.rerun()

        st.sidebar.markdown("Watch Video For More Insights")
        # --- LOCAL VIDEO PLAYER ---
        # Ensure 'intro_video.mp4' is in the same folder as this script
        video_filename = "intro_video.mp4"
        video_path = os.path.join(SCRIPT_DIR, video_filename)
        
        if os.path.exists(video_path):
            try:
                with open(video_path, "rb") as f:
                    video_bytes = f.read()
                    b64 = base64.b64encode(video_bytes).decode()
                    
                st.sidebar.markdown(f"""
                    <video width="100%" autoplay loop muted playsinline style="border-radius: 5px;">
                        <source src="data:video/mp4;base64,{b64}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    <div style="font-size:11px;color:#ccc;text-align:center;">Live Analytics Feed</div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.sidebar.error(f"Error loading video: {e}")
        else:
            # Fallback if file is missing
            st.sidebar.warning(f"File '{video_filename}' not found. Please place it in the app folder.")

        # --- MAIN AREA ---
        st.markdown("<div class='main-title'>INJECTA ANALYTICS MARKET ENGINE</div><div class='main-subtitle'>Explore the best potential market places with us</div>", unsafe_allow_html=True)

        if selection == "Market Engine":
            gdf_suburbs = load_map_data()
            match = gpd.GeoDataFrame(); avg_pop = "N/A"; income_strat = "Medium Density"
            suburb_names_display = "No Zone Selected"
            
            if gdf_suburbs is not None:
                try:
                    pt = gpd.GeoDataFrame(geometry=[Point(st.session_state['lon'], st.session_state['lat'])], crs="EPSG:4326")
                    buf = pt.to_crs(epsg=3857).buffer(radius).to_crs(epsg=4326)
                    match = gdf_suburbs[gdf_suburbs.intersects(buf.geometry.iloc[0])]
                    if not match.empty:
                        cols = match.columns.str.lower()
                        if 'name' in cols: suburb_names_display = ", ".join(match[match.columns[cols == 'name'][0]].tolist())
                        
                        total = 0; count = 0
                        for _, r in match.iterrows():
                            for p in ['pop', 'population', 'pop_est']:
                                if p in cols:
                                    try: total += int(str(r[match.columns[cols==p][0]]).replace(",","")); count += 1; break
                                    except: pass
                        if count > 0: avg_pop = f"{int(total/count):,}" if count > 1 else f"{total:,}"

                        if 'density' in cols:
                            d = str(match.iloc[0][match.columns[cols=='density'][0]])
                            if "High" in d: income_strat = "High Density"
                            elif "Low" in d: income_strat = "Low Density"
                            else: income_strat = "Medium Density"
                except: pass

            if not match.empty:
                st.session_state['selected_suburb'] = suburb_names_display
                st.session_state['selected_strategy'] = income_strat
                st.markdown(f"""<div class="zone-info-box"><span style="font-size:18px;">📍 <b>Zone Detected:</b> {suburb_names_display}</span><br><span style="color:#0F2C59; font-weight:bold;">📊 Strategy Profile:</span> <span style="color:#e67e22; font-weight:bold;">{income_strat}</span></div>""", unsafe_allow_html=True)

            m = folium.Map(location=[st.session_state['lat'], st.session_state['lon']], zoom_start=14)
            folium.Marker([st.session_state['lat'], st.session_state['lon']], icon=folium.Icon(color="red", icon="home")).add_to(m)
            folium.Circle([st.session_state['lat'], st.session_state['lon']], radius=radius, color="#0f2c59", fill=False, dash_array="5, 5").add_to(m)
            if not match.empty: folium.GeoJson(match, style_function=lambda x: {'fillColor': '#0c25f7', 'color': '#0c25f7', 'weight': 2, 'fillOpacity': 0.0}).add_to(m)

            schools=gpd.GeoDataFrame(); health=gpd.GeoDataFrame(); bus=gpd.GeoDataFrame()
            markets=gpd.GeoDataFrame(); supermarkets=gpd.GeoDataFrame(); finance=gpd.GeoDataFrame(); alcohol=gpd.GeoDataFrame()

            if st.session_state['analysis_active']:
                with st.spinner("Processing..."):
                    try:
                        tags = {'amenity':['school','clinic','hospital','marketplace','bar','pub','bank'], 'highway':['bus_stop'], 'shop':['supermarket','alcohol']}
                        f = ox.features_from_point((st.session_state['lat'], st.session_state['lon']), tags, dist=radius)
                        cp = gpd.GeoSeries([Point(st.session_state['lon'], st.session_state['lat'])], crs="EPSG:4326").to_crs(epsg=3857).buffer(radius).to_crs(epsg=4326).iloc[0]
                        if not f.empty:
                            f = f[f.intersects(cp)]
                            if not f.empty:
                                if 'name' not in f.columns: f['name'] = "Unknown"
                                def gc(d,k,v): return d[d[k].isin(v)] if k in d.columns else gpd.GeoDataFrame()
                                schools=gc(f,'amenity',['school']); health=gc(f,'amenity',['clinic','hospital'])
                                markets=gc(f,'amenity',['marketplace']); bus=gc(f,'highway',['bus_stop'])
                                supermarkets=gc(f,'shop',['supermarket']); finance=gc(f,'amenity',['bank'])
                                alcohol=pd.concat([gc(f,'amenity',['bar','pub']), gc(f,'shop',['alcohol'])])
                    except: pass
                
                def ad(g,c): 
                    if not g.empty:
                        for _,r in g.iterrows():
                            gm=r.geometry if r.geometry.geom_type=='Point' else r.geometry.centroid
                            folium.CircleMarker([gm.y,gm.x], radius=5, color="white", fill_color=c, fill_opacity=1, tooltip=str(r.get('name',''))).add_to(m)
                ad(schools,"#006400"); ad(health,"#00008B"); ad(markets,"#cf1a07")
                ad(supermarkets,"#f8f334"); ad(finance,"#9b59b6"); ad(bus,"#3498db")
                m.add_child(MapLegend())

            m.add_child(folium.LatLngPopup())
            st.write("") 
            map_out = st_folium(m, height=450, width=1500)
            if map_out and map_out.get("last_clicked"):
                if abs(map_out["last_clicked"]["lat"] - st.session_state['lat']) > 0.0001:
                    st.session_state['lat'] = map_out["last_clicked"]["lat"]; st.session_state['lon'] = map_out["last_clicked"]["lng"]; st.rerun()

            if not st.session_state['analysis_active']:
                st.markdown("""<div class="instruction-box"><div class="inst-title">Ready to Analy</div><div class="inst-step"><span class="inst-icon">1</span> Set Radius in Sidebar.</div><div class="inst-step"><span class="inst-icon">2</span> Click Map to Pinpoint.</div><div class="inst-step"><span class="inst-icon">3</span> Click 'Analyze'.</div></div>""", unsafe_allow_html=True)

            if st.session_state['analysis_active']:
                st.markdown("Strategic Recommendations")
                
                # --- HELPER: GET NEAREST NAME AND DISTANCE ---
                def get_nearest_details(gdf_features, user_point):
                    if gdf_features.empty:
                        return 99999, "None"
                    # Reproject to meters (Zone 36S for Zim)
                    gdf_meters = gdf_features.to_crs(epsg=32736)
                    user_meters = gpd.GeoSeries([user_point], crs="EPSG:4326").to_crs(epsg=32736).iloc[0]
                    
                    distances = gdf_meters.distance(user_meters)
                    min_idx = distances.idxmin()
                    min_dist = distances.min()
                    
                    # Try to get a name
                    feat_name = gdf_features.loc[min_idx].get('name', 'Unknown Location')
                    return min_dist, str(feat_name)

                # --- CALCULATE METRICS ---
                user_pt = Point(st.session_state['lon'], st.session_state['lat'])
                
                dist_super, name_super = get_nearest_details(supermarkets, user_pt)
                dist_school, name_school = get_nearest_details(schools, user_pt)
                dist_health, name_health = get_nearest_details(health, user_pt)
                dist_night, name_night = get_nearest_details(alcohol, user_pt)
                
                recommendations = [] # For PDF
                
                # Show Population Context
                pop_str = f" | Est. Population: {avg_pop}" if avg_pop != "N/A" else ""
                st.info(f"**Market Context:** {income_strat}{pop_str}")
                
                col1, col2 = st.columns(2)
                
                # --- LOGIC 1: RETAIL & STOCK ---
                with col1:
                    st.markdown('<div class="insight-card border-blue"><div class="card-title">Retail & Stock</div>', unsafe_allow_html=True)
                    msg = ""
                    
                    if income_strat == "High Density":
                        if dist_super > 400:
                            msg = f"**High Density Opportunity:** The nearest major supermarket ('{name_super}') is {int(dist_super)}m away. This gap creates a prime catchment area for a **Grocery Shop** (stocking small packages + bulk) or a high-volume **Tuckshop/Vending** point."
                        else:
                            msg = f"**High Competition Zone:** You are located {int(dist_super)}m from '{name_super}'. Avoid general groceries. **Strongly Recommend:** A specialized Tuckshop focusing on micro-packaging (sachets) and cheaper alternatives to the main supermarket."
                            
                    elif income_strat == "Low Density":
                        if dist_super > 400:
                            msg = f"**Prime Retail Location:** With '{name_super}' being {int(dist_super)}m away, this site is ideal for a **Full Supermarket**, **Liquor Store**, or specialized **Horticulture/Clothing** outlet to serve the affluent demographic."
                        else:
                            msg = f"**Niche Market Only:** Proximity to '{name_super}' ({int(dist_super)}m) makes general retail risky. Pivot to specialized services: **Boutique Clothing** or **Organic Horticulture**."
                            
                    else: # Medium Density
                        if dist_super > 400:
                            msg = f"**Medium Density Gap:** '{name_super}' is {int(dist_super)}m away. Recommended: **General Grocery Shop** bridging the gap between tuckshop and supermarket styles."
                        else:
                            msg = f"**Competitive Zone:** Proximity to '{name_super}' ({int(dist_super)}m) suggests focusing on convenience: **Tuckshop** or **Vending** for quick stop-and-go items."
                    
                    st.write(msg)
                    recommendations.append(msg)
                    st.markdown('</div>', unsafe_allow_html=True)

                # --- LOGIC 2: SCHOOLS ---
                with col2:
                    st.markdown('<div class="insight-card border-green"><div class="card-title">School Zone Strategy</div>', unsafe_allow_html=True)
                    if dist_school < 100 or len(schools) > 5:
                        msg = f"**High Student Economy:** We detected {len(schools)} schools nearby (closest: '{name_school}' at {int(dist_school)}m). **Strategy:** Pivot to **Stationery/Books**, **Uniforms**, **Barber Shop**, or a **Tuckshop** focused on snacks/drinks."
                        st.success(msg)
                    else:
                        msg = f"**General Residential Zone:** Nearest school ('{name_school}') is {int(dist_school)}m away with low density ({len(schools)} schools). Focus strategy purely on general household population needs rather than students."
                        st.info(msg)
                    recommendations.append(msg)
                    st.markdown('</div>', unsafe_allow_html=True)

                col3, col4 = st.columns(2)
                
                # --- LOGIC 3: HEALTH ---
                with col3:
                    st.markdown('<div class="insight-card border-red"><div class="card-title">Health Strategy</div>', unsafe_allow_html=True)
                    if dist_health > 500:
                        msg = f"**Healthcare Gap Detected:** The closest facility ('{name_health}') is {int(dist_health)}m away. **Opportunity:** Residents lack immediate access to basic meds. Recommend stocking **Pain Eaze, Flu remedies, and First Aid** supplies at a small scale."
                        st.warning(msg)
                    else:
                        msg = f"**Well Serviced Area:** '{name_health}' is only {int(dist_health)}m away. Medical supplies are not a priority gap here. Stick to standard convenience items."
                        st.info(msg)
                    recommendations.append(msg)
                    st.markdown('</div>', unsafe_allow_html=True)

                # --- LOGIC 4: NIGHTLIFE ---
                with col4:
                    st.markdown('<div class="insight-card border-orange"><div class="card-title">Nightlife</div>', unsafe_allow_html=True)
                    if len(alcohol) > 3 or dist_night < 100:
                        msg = f"**Night Economy Active:** Located just {int(dist_night)}m from '{name_night}' with {len(alcohol)} venues nearby. **Strategy:** Extend operating hours and stock high-margin nightlife conveniences (Cigarettes, Condoms, Airtime)."
                        st.warning(msg)
                    else:
                        msg = "**Quiet Zone:** Low nightlife activity detected. Standard operating hours recommended."
                        st.info(msg)
                    recommendations.append(msg)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.session_state['recommendations'] = recommendations

        # --- REPORTING (PDF DOWNLOAD) ---
        elif selection == "Reporting":
            st.title("Reporting & Extracts")
            st.info("Download the strategic insights from your last analysis.")
            
            if st.session_state['analysis_active'] and st.session_state['recommendations']:
                # Preview
                with st.expander("Preview Report Content"):
                    st.write(f"**Target Zone:** {st.session_state['selected_suburb']}")
                    for r in st.session_state['recommendations']: st.write(f"- {r}")
                
                # Generate PDF Button
                pdf_bytes = generate_pdf(st.session_state['selected_suburb'], st.session_state['selected_strategy'], st.session_state['recommendations'])
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="Injecta_Market_Report.pdf" style="text-decoration:none;"><button style="background-color:#0F2C59;color:white;padding:12px 25px;border:none;border-radius:5px;cursor:pointer;font-weight:bold;font-size:16px;">📥 DOWNLOAD PDF REPORT</button></a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.warning("⚠️ No analysis data found. Please run a 'Market Engine' analysis first.")

        # --- ABOUT US (EMBED HTML) ---
        elif selection == "About Us":
            # Embed the HTML code stored in the variable at the top
            components.html(INJECTA_WEBSITE_HTML, height=800, scrolling=True)

        # --- CONTACT US ---
        elif selection == "Contact Us":
            st.title("📞 Contact Us")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("""
                <div style="background:white; padding:30px; border-radius:10px; border-left:5px solid #0F2C59; box-shadow:0 4px 15px rgba(0,0,0,0.05);">
                    <h3 style="color:#0F2C59;">Get in Touch</h3>
                    <p style="font-size:16px;">We are ready to assist you with advanced location intelligence.</p>
                    <br>
                    <p><b>📧 Email:</b> <a href="mailto:ministermukumba27@gmail.com">ministermukumba27@gmail.com</a></p>
                    <p><b>📱 Phone:</b> +263 78 435 6427</p>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                with st.form("contact_form"):
                    st.text_input("Your Name")
                    st.text_input("Your Email")
                    st.text_area("Message")
                    st.form_submit_button("SEND MESSAGE")

if __name__ == '__main__':
    main()
