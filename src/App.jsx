import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Polygon, LayersControl, Tooltip, Popup, useMap, Circle } from 'react-leaflet';
import L from 'leaflet';
import { supabase } from './supabaseClient';
import { 
  Globe, 
  Database, 
  Layers, 
  MapPin,
  ChevronRight, 
  Search,
  LogOut,
  Compass,
  Activity,
  Maximize2,
  Eye,
  Radio,
  Sliders
} from 'lucide-react';

// ==========================================
// 1. GUARANTEED LEAFLET CSS INJECTION
// ==========================================
if (typeof window !== 'undefined') {
  if (!document.getElementById('leaflet-core-styles')) {
    const link = document.createElement('link');
    link.id = 'leaflet-core-styles';
    link.rel = 'stylesheet';
    link.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.css';
    document.head.appendChild(link);
  }

  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  });
}

const CLASS_COLORS = {
  'school': '#3b82f6', 
  'church': '#a855f7', 
  'shopping_centre': '#f59e0b', 
  'tuck_shops': '#f97316', 
  'primary_school': '#06b6d4', 
  'secondary_school': '#ec4899', 
  'default': '#ef4444' 
};

function MapFocusHandler({ targetCoords }) {
  const map = useMap();
  useEffect(() => {
    if (targetCoords) {
      map.flyTo(targetCoords, 18, { animate: true, duration: 1.5 });
    }
  }, [targetCoords, map]);
  return null;
}

export default function App() {
  const [user, setUser] = useState({ 
    email: 'ministermukumba71@gmail.com', 
    role: 'GIS Administrator'
  }); 
  const [currentView, setCurrentView] = useState('landing');

  const [pointsData, setPointsData] = useState([]);
  const [polygonsData, setPolygonsData] = useState([]);
  const [detectedColumns, setDetectedColumns] = useState([]); 
  const [loading, setLoading] = useState(false);
  const [dbError, setDbError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [focusTarget, setFocusTarget] = useState(null);
  const [selectedPointId, setSelectedPointId] = useState(null);

  // Buffer System States
  const [showBuffers, setShowBuffers] = useState(false);
  const [bufferRadius, setBufferRadius] = useState(150); 
  const [hoveredFeature, setHoveredFeature] = useState(null);

  useEffect(() => {
    async function fetchPostgresData() {
      if (!user) return;
      setLoading(true);
      setDbError(null);

      try {
        const { data: pts, error: ptErr } = await supabase.from('manicaland_points').select('*');
        const { data: polys, error: polyErr } = await supabase.from('manicaland_polygons').select('*');

        if (ptErr || polyErr) throw ptErr || polyErr;

        setPointsData(pts || []);
        setPolygonsData(polys || []);

        if (pts && pts.length > 0) {
          setDetectedColumns(Object.keys(pts[0]));
        } else {
          setDetectedColumns(['id', 'name', 'category', 'coordinates', 'attributes', 'created_at']);
        }

      } catch (err) {
        console.error("Supabase load error:", err);
        setDbError(err.message || "Failed to load maps data.");
        setDetectedColumns(['id', 'name', 'category', 'coordinates', 'attributes', 'created_at']);
      } finally {
        setLoading(false);
      }
    }
    fetchPostgresData();
  }, [user]);

  const handleLogout = () => {
    setUser(null);
    setCurrentView('landing');
  };

  const getPointClass = (pt) => {
    if (!pt) return '';
    const rawClass = pt.category || pt.properties?.category || pt.class || '';
    return rawClass.toLowerCase().trim();
  };

  const parseCoords = (pt) => {
    const coords = pt.coordinates || pt.geometry?.coordinates || pt.geom?.coordinates;
    if (!coords || coords.length < 2) return null;
    const lat = coords[0] > 0 ? coords[1] : coords[0];
    const lng = coords[0] > 0 ? coords[0] : coords[1];
    return [lat, lng];
  };

  const getPolygonLatLngs = (poly) => {
    let rawPath = poly.path || poly.coordinates || poly.geom?.coordinates || [];
    if (poly.features && poly.features.length > 0) {
      rawPath = poly.features[0].geometry.coordinates;
    }
    while (Array.isArray(rawPath) && Array.isArray(rawPath[0]) && typeof rawPath[0][0] !== 'number') {
      rawPath = rawPath[0];
    }
    if (!rawPath || rawPath.length === 0) return null;

    return rawPath.map(coord => {
      if (Array.isArray(coord) && coord.length >= 2) {
        return coord[0] > 0 ? [coord[1], coord[0]] : [coord[0], coord[1]];
      }
      return null;
    }).filter(Boolean);
  };

  const matchingPoints = pointsData.filter(pt => {
    const ptClass = getPointClass(pt);
    const ptName = (pt.name || pt.properties?.name || '').toLowerCase();
    const query = searchQuery.toLowerCase();
    return searchQuery === '' || ptName.includes(query) || ptClass.includes(query);
  });

  const defaultCenter = [-17.9300, 31.0000];

  return (
    <div className="h-screen w-screen bg-slate-900 text-slate-100 font-sans overflow-hidden flex flex-col">

      {/* HEADER NAVBAR */}
      <header className="bg-slate-900 border-b border-slate-800 h-20 w-full shrink-0 z-50 flex items-center justify-between px-6 shadow-lg">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentView('landing')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center shadow-md">
            <Globe className="w-6 h-6 text-slate-950 stroke-[2.5]" />
          </div>
          <div>
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
              Spatial<span className="text-emerald-400 font-extrabold">Workspace</span>
            </span>
            <p className="text-[10px] text-slate-400 uppercase tracking-wider">Infrastructure Admin Panel</p>
          </div>
        </div>

        <nav className="hidden md:flex items-center space-x-8 text-sm font-medium">
          <button onClick={() => setCurrentView('landing')} className={`transition hover:text-emerald-400 ${currentView === 'landing' ? 'text-emerald-400 font-bold' : 'text-slate-300'}`}>
            Overview Dashboard
          </button>
          {user && (
            <button onClick={() => setCurrentView('dashboard')} className={`transition hover:text-emerald-400 ${currentView === 'dashboard' ? 'text-emerald-400 font-bold' : 'text-slate-300'}`}>
              Map Viewport
            </button>
          )}
        </nav>

        <div className="flex items-center space-x-4">
          {user ? (
            <div className="flex items-center space-x-3 bg-slate-950 border border-slate-800 rounded-xl py-2 px-4 text-xs shadow-inner">
              <div className="flex flex-col items-end">
                <span className="font-bold text-slate-200">{user.role}</span>
                <span className="text-[10px] text-slate-500 font-mono hidden sm:inline">{user.email}</span>
              </div>
              <div className="w-px h-6 bg-slate-800 mx-1" />
              <button onClick={handleLogout} className="bg-rose-950/30 border border-rose-900 text-rose-400 px-3 py-1 rounded-lg text-[11px] font-semibold hover:bg-rose-900/50 transition">
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <button onClick={() => { setUser({ email: 'ministermukumba71@gmail.com', role: 'GIS Administrator' }); setCurrentView('dashboard'); }} className="bg-emerald-500 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs shadow hover:bg-emerald-400 transition">
              Access Portal
            </button>
          )}
        </div>
      </header>

      {/* MAIN CONTAINER REGION */}
      <main className="flex-1 w-full relative overflow-hidden bg-slate-950">

        {currentView === 'landing' && (
          <div className="h-full w-full relative flex flex-col items-center justify-center px-6 overflow-y-auto bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-slate-950">
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-25 pointer-events-none" />

            <div className="relative z-10 max-w-4xl w-full flex flex-col items-center text-center space-y-8 py-12">
              <div className="inline-flex items-center gap-2 bg-emerald-950/60 border border-emerald-800/80 px-3 py-1 rounded-full text-xs text-emerald-400 font-medium tracking-wide shadow-md animate-pulse">
                <Activity className="w-3.5 h-3.5" />
                <span>Live Supabase GIS Cloud Sync Connected</span>
              </div>

              <h1 className="text-4xl sm:text-6xl font-black max-w-3xl tracking-tight leading-tight bg-clip-text text-transparent bg-gradient-to-b from-white via-slate-200 to-slate-500">
                Manicaland Infrastructure <br />
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-teal-400">Spatial Analytics Engine</span>
              </h1>

              <p className="max-w-2xl text-slate-400 text-sm sm:text-base leading-relaxed">
                Seamless real-time vector asset visualization. View mapped study constraints, schools, localized zoning blocks, and landmarks safely queried through a secure PostGIS backend schema environment.
              </p>

              <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
                <button 
                  onClick={() => setCurrentView('dashboard')} 
                  className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-extrabold px-8 py-4 rounded-xl text-sm flex items-center space-x-3 shadow-lg shadow-emerald-950/40 transform active:scale-95 transition"
                >
                  <span>Launch Spatial Workspace</span>
                  <ChevronRight className="w-4 h-4 stroke-[3]" />
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-3xl mt-12 pt-8 border-t border-slate-900">
                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 text-left backdrop-blur-sm">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">Point Markers Loaded</div>
                  <div className="text-3xl font-mono font-bold text-white">{pointsData.length || '0'}</div>
                </div>
                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 text-left backdrop-blur-sm">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">Zoning Boundaries</div>
                  <div className="text-3xl font-mono font-bold text-emerald-400">{polygonsData.length || '0'}</div>
                </div>
                <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 text-left backdrop-blur-sm">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">Connected Tenant</div>
                  <div className="text-xs font-mono truncate text-slate-300 mt-2">{user?.email || 'Guest Session'}</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* WORKSPACE VIEW Layout */}
        {user && currentView === 'dashboard' && (
          <div className="h-full w-full flex flex-col lg:flex-row overflow-hidden relative">

            {/* SIDEBAR NAVIGATION CONTROL */}
            <aside className="w-full lg:w-80 bg-slate-900 border-r border-slate-800 p-5 shrink-0 flex flex-col justify-between overflow-y-auto z-20">
              <div className="space-y-5 flex-1 flex flex-col overflow-hidden">
                <div>
                  <h3 className="text-sm font-bold flex items-center space-x-2 text-slate-100">
                    <Compass className="w-4 h-4 text-emerald-400" />
                    <span>Workspace Navigator</span>
                  </h3>
                  <p className="text-[11px] text-slate-400 mt-0.5">Explore the dataset live. Use the list below to focus coordinates instantly.</p>
                </div>

                {/* ADVANCED PROXIMITY ADJUSTMENT BAR LAYER */}
                <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-3">
                  <div className="text-[10px] font-extrabold uppercase tracking-widest text-slate-400 flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <Radio className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
                      <span>Proximity Buffers</span>
                    </div>
                    <span className="text-[11px] text-cyan-400 font-mono font-bold">{bufferRadius}m</span>
                  </div>
                  
                  <button 
                    onClick={() => setShowBuffers(!showBuffers)}
                    className={`w-full py-2 px-3 rounded-lg text-xs font-bold transition flex items-center justify-between border ${
                      showBuffers 
                        ? 'bg-cyan-950/40 border-cyan-700 text-cyan-400' 
                        : 'bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800'
                    }`}
                  >
                    <span>Toggle Analysis Rings</span>
                    <span className={`w-2 h-2 rounded-full ${showBuffers ? 'bg-cyan-400 shadow-[0_0_8px_#22d3ee]' : 'bg-slate-600'}`} />
                  </button>

                  {showBuffers && (
                    <div className="pt-2 border-t border-slate-900 space-y-1.5 animate-fade-in">
                      <div className="flex items-center gap-1 text-[10px] text-slate-400">
                        <Sliders className="w-3 h-3 text-slate-500" />
                        <span>Adjust Range Envelope</span>
                      </div>
                      <input 
                        type="range"
                        min="50"
                        max="1000"
                        step="50"
                        value={bufferRadius}
                        onChange={(e) => setBufferRadius(Number(e.target.value))}
                        className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                      />
                    </div>
                  )}
                </div>

                {/* SEARCH FILTER BLOCK */}
                <div className="relative shrink-0">
                  <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-3" />
                  <input 
                    type="text" 
                    placeholder="Quick trace name or type..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 transition"
                  />
                </div>

                {/* TELEMETRY INSPECTOR READOUT */}
                {hoveredFeature && (
                  <div className="p-3 bg-slate-950/90 border border-slate-800 rounded-xl text-xs space-y-1 animate-fade-in">
                    <div className="text-[9px] font-extrabold text-emerald-400 uppercase flex items-center gap-1">
                      <Eye className="w-3 h-3" /> Selected Feature Inspection
                    </div>
                    <div className="font-bold text-slate-200 truncate">{hoveredFeature.name}</div>
                    <div className="text-[10px] font-mono text-slate-400 capitalize">Type: {hoveredFeature.class}</div>
                  </div>
                )}

                {/* LIST FEED AREA */}
                <div className="flex-1 overflow-y-auto bg-slate-950 border border-slate-800 rounded-xl divide-y divide-slate-900 custom-scrollbar">
                  {matchingPoints.map((pt, idx) => {
                    const ptClass = getPointClass(pt);
                    const name = pt.name || pt.properties?.name || 'Unassigned Landmark';
                    const color = CLASS_COLORS[ptClass] || CLASS_COLORS['default'];
                    const pointCoords = parseCoords(pt);
                    const isSelected = selectedPointId === (pt.id || idx);

                    return (
                      <button
                        key={`list-item-${pt.id || idx}`}
                        onClick={() => {
                          if (pointCoords) {
                            setFocusTarget(pointCoords);
                            setSelectedPointId(pt.id || idx);
                          }
                        }}
                        onMouseEnter={() => setHoveredFeature({ name, class: ptClass })}
                        onMouseLeave={() => setHoveredFeature(null)}
                        disabled={!pointCoords}
                        className={`w-full p-3 text-left flex items-start gap-2.5 transition group ${
                          isSelected ? 'bg-emerald-950/20 border-l-2 border-emerald-400' : 'hover:bg-slate-900/50'
                        }`}
                      >
                        <span className="w-2.5 h-2.5 rounded-full border border-white/20 shrink-0 mt-1 shadow-sm" style={{ backgroundColor: color }} />
                        <div className="overflow-hidden flex-1">
                          <span className={`block text-xs font-bold truncate transition ${isSelected ? 'text-emerald-400' : 'text-slate-200 group-hover:text-emerald-400'}`}>{name}</span>
                          <span className="block text-[10px] font-mono text-slate-500 uppercase tracking-tight mt-0.5">{ptClass || 'poi'}</span>
                        </div>
                        <Maximize2 className={`w-3 h-3 text-emerald-400 transition shrink-0 self-center ${isSelected ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`} />
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* DB table tracker bottom box */}
              {detectedColumns.length > 0 && (
                <div className="mt-4 p-3 bg-slate-950 border border-slate-800 rounded-xl text-xs space-y-1.5 shrink-0">
                  <div className="flex items-center space-x-1.5 text-slate-500 font-bold uppercase text-[9px] tracking-wider">
                    <Database className="w-3.5 h-3.5 text-slate-500" />
                    <span>Schema Fields:</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {detectedColumns.map(col => (
                      <span key={col} className="px-1.5 py-0.5 rounded border text-[9px] font-mono bg-slate-900 text-slate-400 border-slate-800">
                        {col}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </aside>

            {/* MAP VIEWPORT SECTION */}
            <section className="flex-1 relative w-full h-full min-h-[500px] bg-slate-950 z-10 block">

              {/* SYSTEM MAP KEY/LEGEND */}
              <div className="absolute bottom-6 right-6 z-[400] bg-slate-900/95 backdrop-blur border border-slate-800 rounded-xl p-4 shadow-2xl text-xs space-y-2.5 min-w-[190px]">
                <div className="font-bold text-slate-200 border-b border-slate-800 pb-1.5 flex items-center space-x-1.5">
                  <Layers className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Interactive Map Key</span>
                </div>
                <div className="space-y-1.5 text-[11px]">
                  {Object.keys(CLASS_COLORS).map(className => (
                    <div key={className} className="flex items-center space-x-2">
                      <span className="w-2.5 h-2.5 rounded-full border border-white/20" style={{ backgroundColor: CLASS_COLORS[className] }} />
                      <span className="text-slate-300 capitalize">{className.replace(/_/g, ' ')}</span>
                    </div>
                  ))}
                  <div className="flex items-center space-x-2 pt-1.5 border-t border-slate-800">
                    <span className="w-4 h-2 rounded bg-emerald-500/10 border border-emerald-400 border-dashed" />
                    <span className="text-slate-400 text-[10px]">Study Envelope Area</span>
                  </div>
                </div>
              </div>

              {/* MAP COMPONENT INJECTION ELEMENT */}
              <div className="w-full h-full min-h-[500px] relative block" style={{ height: '100%' }}>
                <MapContainer
                  center={defaultCenter}
                  zoom={14}
                  style={{ width: '100%', height: '100%', minHeight: '100%', background: '#020617' }}
                  className="w-full h-full"
                >
                  <MapFocusHandler targetCoords={focusTarget} />

                  <LayersControl position="topright">
                    <LayersControl.BaseLayer checked name="🛰️ Google Satellite Hybrid">
                      <TileLayer
                        url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
                        attribution='&copy; Google Maps'
                      />
                    </LayersControl.BaseLayer>
                    <LayersControl.BaseLayer name="🌐 OpenStreetMap Standard">
                      <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution='&copy; OpenStreetMap contributors'
                      />
                    </LayersControl.BaseLayer>
                  </LayersControl>

                  {/* BOUNDARY POLYGONS */}
                  {polygonsData.map((poly, idx) => {
                    const verifiedLatLngs = getPolygonLatLngs(poly);
                    if (!verifiedLatLngs || verifiedLatLngs.length === 0) return null;

                    return (
                      <Polygon 
                        key={`boundary-poly-${poly.id || idx}`} 
                        positions={verifiedLatLngs}
                        pathOptions={{ 
                          color: '#10b981',
                          fillColor: '#10b981',
                          fillOpacity: 0.08,
                          weight: 2,
                          dashArray: '5, 5'
                        }}
                      >
                        <Tooltip permanent sticky direction="center" className="bg-slate-950/90 text-emerald-400 font-bold border border-slate-800 px-2 py-0.5 rounded text-[10px] uppercase tracking-wider shadow-md">
                          Study Area Boundary
                        </Tooltip>
                      </Polygon>
                    );
                  })}

                  {/* HIGH-PRECISION VECTOR POINT ASSETS */}
                  {pointsData.map((pt, idx) => {
                    const pointCoords = parseCoords(pt);
                    if (!pointCoords) return null;

                    const ptClass = getPointClass(pt);
                    const markerColor = CLASS_COLORS[ptClass] || CLASS_COLORS['default'];
                    const pointName = pt.name || pt.properties?.name || 'Unassigned Landmark';
                    const isSelected = selectedPointId === (pt.id || idx);

                    return (
                      <React.Fragment key={`group-node-${pt.id || idx}`}>
                        
                        {/* Dynamic analytical buffer workspace ring - LIGHT BLUE */}
                        {showBuffers && (
                          <Circle 
                            center={pointCoords}
                            radius={bufferRadius}
                            pathOptions={{
                              color: '#38bdf8',
                              weight: 1.5,
                              dashArray: '4, 4',
                              fillColor: '#38bdf8',
                              fillOpacity: 0.08
                            }}
                          />
                        )}

                        <CircleMarker
                          center={pointCoords}
                          radius={isSelected ? 11 : 7.5}
                          pathOptions={{
                            color: isSelected ? '#34d399' : '#ffffff',
                            weight: isSelected ? 3 : 1.5,
                            fillColor: markerColor,
                            fillOpacity: 1,
                            className: isSelected ? 'animate-pulse' : ''
                          }}
                        >
                          <Tooltip direction="top" offset={[0, isSelected ? -10 : -6]} opacity={1} permanent={isSelected}>
                            <div className="font-sans px-0.5 text-center text-xs">
                              <span className="text-[9px] uppercase tracking-wider font-extrabold text-slate-400 block">{ptClass || 'poi'}</span>
                              <span className="font-bold text-slate-900 block">{pointName}</span>
                            </div>
                          </Tooltip>

                          <Popup>
                            <div className="p-1 font-sans text-slate-900 text-xs min-w-[170px]">
                              <div className="text-[9px] font-bold text-emerald-600 uppercase tracking-wider">{ptClass || 'landmark'}</div>
                              <h4 className="font-bold border-b pb-1 mb-1 text-slate-900">{pointName}</h4>
                              {pt.attributes && (
                                <div className="text-[10px] text-slate-600 bg-slate-50 p-1.5 rounded font-mono max-h-[100px] overflow-y-auto">
                                  {typeof pt.attributes === 'object' ? (
                                    Object.entries(pt.attributes).map(([k, v]) => (
                                      <div key={k} className="truncate"><span className="text-slate-400">{k}:</span> {JSON.stringify(v)}</div>
                                    ))
                                  ) : (
                                    <div className="truncate text-slate-400">{String(pt.attributes)}</div>
                                  )}
                                </div>
                              )}
                              <div className="text-[9px] text-slate-400 pt-1 mt-1 border-t font-mono">
                                Lat/Lng: {pointCoords[0].toFixed(5)}, {pointCoords[1].toFixed(5)}
                              </div>
                            </div>
                          </Popup>
                        </CircleMarker>
                      </React.Fragment>
                    );
                  })}
                </MapContainer>
              </div>
            </section>

          </div>
        )}
      </main>
    </div>
  );
}