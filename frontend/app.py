"""
EnergyShield AI × Foresight Live
ET AI Hackathon 2026 | PS 2 — Full Production Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import json, os, sys, tempfile
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import CORRIDORS, INDIA_REFINERIES, ALT_CRUDE_SOURCES, SPR_SITES
from utils.live_data import (
    get_live_commodity_prices, get_brent_history_live, get_tanker_rates_live,
    get_live_news, get_port_intelligence
)
from agents import geo_sentinel, scenario_modeller, procurement_agent, spr_optimiser, ais_tracker
from agents import vessel_intel
from utils.vra_pdf import generate_vra_pdf

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="EnergyShield AI × Foresight Live",
    page_icon="⚡", layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# THEME (light + professional)
# ──────────────────────────────────────────────
st.markdown("""
<style>
  /* Global */
  .stApp { background: #f7f9fc; color: #1a2332; font-family: 'Inter', sans-serif; }
  [data-testid="stSidebar"] { background: #0d1b2e; }
  [data-testid="stSidebar"] * { color: #e8f4f8 !important; }

  /* Cards */
  .card {
    background: #fff; border-radius: 10px; padding: 16px 20px;
    border: 1px solid #e4e9f0; margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  }
  .card-dark {
    background: #0d1b2e; border-radius: 10px; padding: 16px 20px;
    border: 1px solid #1e3a5f; margin-bottom: 12px; color: #e8f4f8;
  }

  /* Section headers */
  .sec-hdr {
    background: linear-gradient(90deg, #0d6e6e 0%, #0a4a4a 100%);
    color: white !important; padding: 8px 16px; border-radius: 6px;
    font-size: 13px; font-weight: 700; letter-spacing: 0.5px;
    margin-bottom: 14px;
  }

  /* Risk badges */
  .badge-critical { background:#7b0000; color:#ff8a80; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:700; }
  .badge-high     { background:#c62828; color:#fff; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:700; }
  .badge-elevated { background:#e65100; color:#fff; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:700; }
  .badge-moderate { background:#f9a825; color:#fff; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:700; }
  .badge-low      { background:#2e7d32; color:#fff; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:700; }

  /* Metric overrides */
  [data-testid="metric-container"] {
    background: #fff; border: 1px solid #e4e9f0; border-radius: 8px; padding: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #0d6e6e 0%, #0a4a4a 100%);
    color: white; border: none; border-radius: 6px; font-weight: 600;
  }
  .stButton > button:hover { opacity: 0.9; transform: translateY(-1px); }

  /* Download button */
  .stDownloadButton > button {
    background: linear-gradient(135deg, #c8a14b 0%, #a0782a 100%);
    color: white; border: none; border-radius: 6px; font-weight: 700;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab"] { font-weight: 600; }
  .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #0d6e6e; border-bottom-color: #0d6e6e; }

  /* News items */
  .news-item { border-left: 3px solid #0d6e6e; padding: 8px 12px; margin-bottom: 8px; background:#fff; border-radius:0 6px 6px 0; }
  .vessel-row { background:#fff; border-radius:8px; border:1px solid #e4e9f0; padding:10px 14px; margin-bottom:6px; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
RISK_COLORS = {"CRITICAL":"#7b0000","HIGH":"#c62828","ELEVATED":"#e65100","MODERATE":"#f9a825","LOW":"#2e7d32"}
RISK_BG     = {"CRITICAL":"#ffebee","HIGH":"#ffcdd2","ELEVATED":"#fff3e0","MODERATE":"#fffde7","LOW":"#e8f5e9"}

def risk_badge(level):
    cls = {"CRITICAL":"badge-critical","HIGH":"badge-high","ELEVATED":"badge-elevated","MODERATE":"badge-moderate","LOW":"badge-low"}.get(level,"badge-moderate")
    return f'<span class="{cls}">{level}</span>'

def sec(title):
    st.markdown(f'<div class="sec-hdr">{title}</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ EnergyShield AI")
    st.markdown("##### × Foresight Live")
    st.markdown("---")

    page = st.radio("", [
        "🏠 Command Centre",
        "🛡️ Foresight Live",
        "🌍 Risk Intelligence",
        "📊 Scenario Modeller",
        "🚢 AIS Tracker",
        "🛒 Procurement Engine",
        "🛢️ SPR Optimiser",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Live Commodity Prices**")
    prices = get_live_commodity_prices()
    brent  = prices.get("brent_crude", {})
    bp     = brent.get("price", 87.4)
    bc     = brent.get("change_pct", 0)
    arrow  = "▲" if bc >= 0 else "▼"
    color  = "#2e7d32" if bc >= 0 else "#c62828"
    st.markdown(f"**Brent Crude**")
    st.markdown(f"<div style='font-size:22px;font-weight:800;color:#0d6e6e;'>${bp}</div><div style='color:{color};font-size:12px;'>{arrow} {abs(bc):.1f}%</div>", unsafe_allow_html=True)
    wti = prices.get("wti_crude", {})
    st.markdown(f"WTI: **${wti.get('price','—')}**")
    st.caption(f"Source: {brent.get('source','—')}")

    st.markdown("---")
    st.markdown("**SPR Status**")
    st.progress(0.88, text="88% — 9.5 days cover")

    st.markdown("---")
    st.markdown("**Data Sources**")
    st.caption("🔴 Live AIS  🟢 Commodity  🟡 Sanctions\n🔵 Weather  🟣 News intel")
    st.caption("© HR Maritime Consultants\nForesight Intelligence Platform")

# ──────────────────────────────────────────────
# PLATFORM HEADER
# ──────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,#0d1b2e 0%,#0d6e6e 100%);border-radius:12px;
    padding:20px 28px;margin-bottom:20px;display:flex;align-items:center;gap:16px;">
  <div style="font-size:40px;">⚡</div>
  <div>
    <div style="font-size:24px;font-weight:800;color:#fff;letter-spacing:1px;">EnergyShield AI × Foresight Live</div>
    <div style="font-size:12px;color:rgba(255,255,255,0.7);margin-top:3px;">
      India Energy Supply Chain Resilience Platform &nbsp;|&nbsp; ET AI Hackathon 2026
    </div>
  </div>
  <div style="margin-left:auto;text-align:right;">
    <div style="font-size:11px;color:rgba(255,255,255,0.6);">INTELLIGENCE ACTIVE</div>
    <div style="font-size:13px;color:#c8a14b;font-weight:700;">{datetime.utcnow().strftime('%d %b %Y %H:%M')} UTC</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════
# PAGE: COMMAND CENTRE
# ════════════════════════════════════════════
if page == "🏠 Command Centre":

    # KPI Strip
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: st.metric("🛢️ India Imports", "5.1 MBPD")
    with c2: st.metric("⚠️ Hormuz Dep.", "42%")
    with c3: st.metric("🔴 Red Sea Risk", "HIGH")
    with c4: st.metric("🏛️ SPR Cover", "9.5 days")
    with c5: st.metric("💰 Brent", f"${bp}/bbl", f"+{bc:.1f}%")
    with c6:
        tankers = get_tanker_rates_live()
        st.metric("🚢 VLCC Rate", f"${tankers.get('vlcc_me_india',35000):,.0f}/d")

    st.markdown("---")

    col_l, col_r = st.columns([3,2])

    with col_l:
        sec("📈 Brent Crude — 90-Day History with Geopolitical Shocks")
        df = get_brent_history_live(90)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index, y=df["brent_usd"],
            fill="tozeroy", fillcolor="rgba(13,110,110,0.08)",
            line=dict(color="#0d6e6e", width=2), name="Brent USD/bbl"
        ))
        fig.add_vline(x=df.index[-15], line_dash="dash", line_color="#c62828",
                      annotation_text="Hormuz Exercise", annotation_font_color="#c62828")
        fig.add_vline(x=df.index[-28], line_dash="dot", line_color="#e65100",
                      annotation_text="Houthi strike", annotation_font_color="#e65100")
        fig.update_layout(paper_bgcolor="#fff", plot_bgcolor="#fff",
                         font_color="#1a2332", height=280, margin=dict(l=0,r=0,t=10,b=0),
                         xaxis=dict(gridcolor="#f0f0f0"), yaxis=dict(gridcolor="#f0f0f0",title="USD/bbl"),
                         showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        sec("🌐 Corridor Risk Scores (Live)")
        corridor_scores = {"Hormuz": 78, "Red Sea": 85, "Gulf of Guinea": 65, "Cape (Alt)": 22}
        fig2 = go.Figure(go.Bar(
            x=list(corridor_scores.values()),
            y=list(corridor_scores.keys()),
            orientation="h",
            marker_color=["#c62828","#c62828","#e65100","#2e7d32"],
            text=[f"{v}/100" for v in corridor_scores.values()],
            textposition="outside"
        ))
        fig2.update_layout(paper_bgcolor="#fff", plot_bgcolor="#fff", font_color="#1a2332",
                          height=280, margin=dict(l=0,r=40,t=10,b=0),
                          xaxis=dict(range=[0,115],showgrid=False,showticklabels=False),
                          yaxis=dict(gridcolor="#f0f0f0"))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    col_n, col_v = st.columns([3,2])

    with col_n:
        sec("📰 Live Geopolitical Intelligence Feed")
        news = get_live_news(6)
        for h in news:
            rs = h.get("risk_score", 50)
            badge = risk_badge("HIGH" if rs>=75 else "ELEVATED" if rs>=60 else "MODERATE" if rs>=45 else "LOW")
            st.markdown(f"""<div class="news-item">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div style="font-size:13px;font-weight:600;flex:1;">{h['title']}</div>
                    <div style="margin-left:10px;">{badge}</div>
                </div>
                <div style="font-size:10px;color:#666;margin-top:4px;">{h['source']} · {h['published']}</div>
            </div>""", unsafe_allow_html=True)

    with col_v:
        sec("🚢 Vessels At Risk Right Now")
        at_risk = ais_tracker.get_at_risk_vessels()
        for v in at_risk:
            rc = RISK_COLORS.get("HIGH","#c62828")
            st.markdown(f"""<div class="vessel-row">
                <div style="font-size:13px;font-weight:700;color:#0d6e6e;">{v['icon']} {v['name']}</div>
                <div style="font-size:11px;color:#666;margin-top:2px;">{v['type']} · {v['cargo'][:35]}</div>
                <div style="font-size:11px;color:{rc};margin-top:3px;font-weight:600;">⚠ {v['status']}</div>
                <div style="font-size:10px;color:#999;">→ {v['destination']}</div>
            </div>""", unsafe_allow_html=True)

        sec("🌊 Port Incidents (UKMTO / ICC)")
        incidents = get_port_intelligence()
        for inc in incidents[:3]:
            rs = inc.get("risk_score", 50)
            rc = RISK_COLORS.get("HIGH" if rs>=75 else "MODERATE","#e65100")
            st.markdown(f"""<div style="border-left:3px solid {rc};padding:6px 10px;margin-bottom:6px;background:#fff;border-radius:0 4px 4px 0;font-size:11px;">
                <b>{inc['title'][:70]}</b><br>
                <span style="color:#666;">{inc['source']} · {inc['published']}</span>
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════
# PAGE: FORESIGHT LIVE
# ════════════════════════════════════════════
elif page == "🛡️ Foresight Live":

    st.markdown("""<div class="card" style="border-left:4px solid #c8a14b;">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="font-size:28px;">🛡️</div>
            <div>
                <div style="font-size:16px;font-weight:800;color:#0d6e6e;">Foresight Live — Vessel Intelligence Terminal</div>
                <div style="font-size:12px;color:#666;margin-top:2px;">
                    Per-vessel real-time intelligence + one-click branded Voyage Risk Assessment.
                    Windward-grade intelligence at a fraction of the price.
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Search
    col_s, col_b = st.columns([5,1])
    with col_s:
        query = st.text_input("Vessel", placeholder="IMO number (e.g. 9839131) or vessel name", label_visibility="collapsed")
    with col_b:
        do_search = st.button("🔍 Track", use_container_width=True)

    # Demo fleet quick-pick
    st.markdown("**Demo Fleet** — click to load:")
    fleet = vessel_intel.get_demo_fleet()
    cols = st.columns(len(fleet))
    for i, v in enumerate(fleet):
        short = v["name"].replace("MV ","").replace("MT ","")[:15]
        if cols[i].button(short, key=f"fl_{i}", use_container_width=True):
            st.session_state["fl_vessel"] = v
            st.session_state.pop("fl_vra", None)

    if do_search and query:
        found = vessel_intel.lookup_vessel(query)
        if found:
            st.session_state["fl_vessel"] = found
            st.session_state.pop("fl_vra", None)
        else:
            st.error(f"Vessel not found: '{query}'. Try IMO 9839131 or name FALCON MAJESTIC.")

    if "fl_vessel" in st.session_state:
        v = st.session_state["fl_vessel"]
        risk = vessel_intel.quick_risk_score(v)
        rc   = RISK_COLORS.get(risk["level"], "#e65100")
        rbg  = RISK_BG.get(risk["level"], "#fff3e0")
        icon = v.get("_icon", "🚢")

        # Vessel banner
        st.markdown(f"""<div style="background:linear-gradient(135deg,#0d1b2e,#1a3a5f);
            border:1px solid {rc};border-radius:10px;padding:18px 22px;margin:12px 0;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:20px;font-weight:800;color:#fff;">{icon} {v['name']}</div>
                    <div style="font-size:11px;color:#90a4ae;margin-top:3px;">
                        IMO {v['imo']} &nbsp;·&nbsp; {v['type']} &nbsp;·&nbsp; {v.get('flag','—')} &nbsp;·&nbsp; {v.get('dwt','—')} DWT &nbsp;·&nbsp; Built {v.get('built') or v.get('year_built','—')}
                    </div>
                    <div style="font-size:12px;color:#90a4ae;margin-top:2px;">
                        {v.get('current_route') or v.get('destination','—')}
                    </div>
                </div>
                <div style="background:{rc};padding:12px 20px;border-radius:8px;text-align:center;">
                    <div style="font-size:9px;color:#fff;opacity:0.8;">VOYAGE RISK</div>
                    <div style="font-size:28px;font-weight:900;color:#fff;line-height:1;">{risk['score']}</div>
                    <div style="font-size:11px;color:#fff;font-weight:700;">{risk['level']}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Stats row
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: st.metric("⚡ Speed", f"{v.get('speed_kts','—')} kts")
        with c2: st.metric("🧭 Heading", f"{v.get('heading','—')}°")
        with c3: st.metric("⚓ Draught", f"{v.get('draught','—')} m")
        with c4: st.metric("📦 Cargo", (v.get('cargo') or '—')[:18])
        with c5: st.metric("🕐 ETA", (v.get('eta') or '—')[:10])

        tab_map, tab_threats, tab_weather, tab_sanctions = st.tabs(["📍 Live Map", "🔴 Threats", "🌊 Weather", "🔒 Compliance"])

        with tab_map:
            lat = v.get("lat", 15.0)
            lon = v.get("lon", 60.0)
            vm = folium.Map(location=[lat, lon], zoom_start=5, tiles="CartoDB Positron")

            # Corridor threat zones
            zones = {
                "strait_of_hormuz": ([26.57,56.25], 80, "#c62828", "Hormuz — HIGH RISK"),
                "red_sea":          ([14.5, 43.0],  90, "#c62828", "Red Sea — HIGH RISK"),
                "gulf_of_guinea":   ([2.5,  2.5],   70, "#e65100", "Gulf of Guinea — ELEVATED"),
                "arabian_sea":      ([18.0, 64.0],  40, "#2196F3", "Arabian Sea"),
            }
            for ckey,(ccoords,crad,ccol,clbl) in zones.items():
                folium.CircleMarker(ccoords, radius=crad, color=ccol, fill=True,
                    fill_opacity=0.08, weight=2,
                    popup=folium.Popup(clbl, max_width=200)).add_to(vm)
                folium.Marker(ccoords, icon=folium.DivIcon(
                    html=f'<div style="background:{ccol};color:#fff;padding:2px 6px;border-radius:4px;font-size:9px;font-weight:700;white-space:nowrap;">{clbl}</div>'
                )).add_to(vm)

            # Indian refineries
            for r in INDIA_REFINERIES:
                folium.CircleMarker([r["lat"],r["lon"]], radius=7, color="#0d6e6e",
                    fill=True, fill_opacity=0.8,
                    popup=f"🏭 {r['name']} — {r['capacity_mbpd']} MBPD").add_to(vm)

            # Active vessel
            folium.Marker([lat, lon],
                icon=folium.DivIcon(html=f'<div style="font-size:20px;">{icon}</div>'),
                popup=f"<b>{v['name']}</b><br>IMO: {v['imo']}<br>{v.get('status','')}<br>→ {v.get('destination','')}"
            ).add_to(vm)
            folium.CircleMarker([lat,lon], radius=12, color=rc, fill=True,
                fill_opacity=0.4, weight=2).add_to(vm)

            st_folium(vm, width=None, height=420, key="fl_map")

        with tab_threats:
            corridor_key = v.get("corridor","")
            corr = CORRIDORS.get(corridor_key, {})
            threat_data = {
                "Piracy / Armed Robbery":   {"Hormuz":"LOW","Red Sea":"MODERATE","Gulf of Guinea":"HIGH","Arabian Sea":"LOW"}.get(corr.get("name",""),"MODERATE"),
                "Geopolitical / Military":  {"Hormuz":"HIGH","Red Sea":"HIGH","Gulf of Guinea":"LOW","Arabian Sea":"LOW"}.get(corr.get("name",""),"LOW"),
                "Drone / Missile Threat":   {"Hormuz":"ELEVATED","Red Sea":"CRITICAL","Gulf of Guinea":"LOW","Arabian Sea":"LOW"}.get(corr.get("name",""),"LOW"),
                "GPS Spoofing / Jamming":   {"Hormuz":"HIGH","Red Sea":"MODERATE","Gulf of Guinea":"LOW","Arabian Sea":"LOW"}.get(corr.get("name",""),"LOW"),
                "Weather / Sea State":      "LOW",
            }
            for threat, level in threat_data.items():
                tc = RISK_COLORS.get(level,"#e65100")
                tbg = RISK_BG.get(level,"#fff3e0")
                st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;
                    background:{tbg};border-radius:6px;padding:10px 14px;margin-bottom:6px;border-left:4px solid {tc};">
                    <div style="font-size:13px;font-weight:600;">{threat}</div>
                    <div style="background:{tc};color:#fff;padding:3px 12px;border-radius:12px;font-size:11px;font-weight:700;">{level}</div>
                </div>""", unsafe_allow_html=True)

            if corr:
                st.info(f"**Corridor:** {corr.get('name','—')} | **HRA:** {'Yes' if corr.get('hra') else 'No'} | **BMP5:** {'Applicable' if corr.get('bmp5_applicable') else 'N/A'} | **UKMTO:** {'Register' if corr.get('ukmto_area') else 'N/A'}")

        with tab_weather:
            from utils.live_data import get_route_weather
            wx = get_route_weather(v.get("lat",15), v.get("lon",60))
            wc1,wc2,wc3,wc4 = st.columns(4)
            with wc1: st.metric("🌊 Wave Height", f"{wx.get('wave_height_m','—')} m")
            with wc2: st.metric("⏱ Wave Period", f"{wx.get('wave_period_s','—')} s")
            with wc3: st.metric("💨 Wind Speed", f"{wx.get('wind_speed_kts','—')} kts")
            with wc4: st.metric("🌊 Sea State", wx.get('sea_state','—'))
            st.caption(f"Source: {wx.get('source','—')} · {wx.get('_timestamp','')[:16]} UTC")

        with tab_sanctions:
            from utils.live_data import check_sanctions_live
            sc = check_sanctions_live(v.get("imo",""), v.get("name",""))
            status_col = "#2e7d32" if sc.get("status")=="CLEAR" else "#c62828"
            st.markdown(f"""<div style="background:#f1f8e9;border:2px solid {status_col};
                border-radius:8px;padding:14px 18px;margin-bottom:12px;">
                <div style="font-size:15px;font-weight:800;color:{status_col};">
                    {'✅' if sc.get('status')=='CLEAR' else '🚨'} {sc.get('status','—')}
                </div>
                <div style="font-size:11px;color:#666;margin-top:8px;">
                    <b>Screened against:</b> {', '.join(sc.get('screened_against',[]))}<br>
                    <b>Flag assessment:</b> {sc.get('flag_risk','—')}<br>
                    <b>AIS history:</b> {sc.get('ais_gap_history','—')}<br>
                    <b>Ownership opacity:</b> {sc.get('ownership_opacity','—')}<br>
                    <b>Last screened:</b> {sc.get('_timestamp','')[:16]} UTC
                </div>
            </div>""", unsafe_allow_html=True)

        # VRA GENERATOR — THE MONEY FEATURE
        st.markdown("---")
        st.markdown("### 📄 One-Click Voyage Risk Assessment")
        st.markdown('<div style="background:#fffde7;border:1px solid #c8a14b;border-radius:8px;padding:10px 14px;margin-bottom:12px;font-size:12px;">'
                   '💡 <b>The deliverable shipowners pay for.</b> Generate a Capt. Ritesh Kapoor–signed, '
                   'Foresight-branded professional VRA PDF in ~30 seconds — ready to email to charterers, P&I clubs, or war risk underwriters.'
                   '</div>', unsafe_allow_html=True)

        if st.button("⚡ Generate Foresight VRA (Branded PDF)", use_container_width=True, type="primary"):
            with st.spinner("Foresight analyst generating voyage risk assessment..."):
                vra = vessel_intel.generate_vra(v)
                st.session_state["fl_vra"] = vra

        if "fl_vra" in st.session_state:
            vra = st.session_state["fl_vra"]
            if "error" not in vra:
                rating = vra.get("overall_risk_rating","MODERATE")
                score  = vra.get("risk_score", 50)
                vc = RISK_COLORS.get(rating,"#e65100")
                vbg= RISK_BG.get(rating,"#fff3e0")

                st.markdown(f"""<div style="background:{vbg};border-left:5px solid {vc};
                    border-radius:0 8px 8px 0;padding:14px 18px;margin:10px 0;">
                    <div style="font-size:14px;font-weight:800;color:{vc};">{vra.get('vessel_name','')} — {rating} ({score}/100)</div>
                    <div style="font-size:12px;color:#444;margin-top:6px;line-height:1.5;">{vra.get('executive_summary','')}</div>
                </div>""", unsafe_allow_html=True)

                # Threat grid
                threats = vra.get("threat_assessment",{})
                labels = {"piracy_armed_robbery":"Piracy","geopolitical_military":"Geopolitical",
                         "drone_missile_threat":"Drone/Missile","gps_spoofing_jamming":"GPS Jamming","sea_state_weather":"Weather"}
                tcols = st.columns(len(labels))
                for i,(k,lbl) in enumerate(labels.items()):
                    if k in threats:
                        lvl = threats[k].get("level","—")
                        lc  = RISK_COLORS.get(lvl,"#888")
                        lbg = RISK_BG.get(lvl,"#f5f5f5")
                        with tcols[i]:
                            st.markdown(f"""<div style="text-align:center;padding:8px 4px;background:{lbg};
                                border-radius:6px;border:1px solid {lc};">
                                <div style="font-size:9px;color:#666;font-weight:600;">{lbl}</div>
                                <div style="font-size:11px;color:{lc};font-weight:800;margin-top:4px;">{lvl}</div>
                            </div>""", unsafe_allow_html=True)

                # Generate PDF
                pdf_path = os.path.join(tempfile.gettempdir(), f"Foresight_VRA_{v['imo']}.pdf")
                generate_vra_pdf(vra, pdf_path)

                with open(pdf_path,"rb") as f:
                    st.download_button(
                        "⬇️ Download Branded Foresight VRA (PDF)",
                        data=f.read(),
                        file_name=f"Foresight_VRA_{v['name'].replace(' ','_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

                with st.expander("📋 Full Recommendations & Chokepoint Advisories"):
                    st.markdown("**Operational Recommendations**")
                    for r in vra.get("recommendations",[]):
                        st.markdown(f"▸ {r}")
                    st.markdown("**Chokepoints**")
                    for cp in vra.get("chokepoints",[]):
                        lc = RISK_COLORS.get(cp.get("risk",""),"#888")
                        st.markdown(f"**{cp.get('name','')}** <span style='color:{lc};'>[{cp.get('risk','')}]</span> — {cp.get('advisory','')}", unsafe_allow_html=True)
                    st.markdown("**Insurance Note**")
                    st.info(vra.get("insurance_note","—"))
            else:
                st.error(f"VRA error: {vra.get('error')}. Ensure ANTHROPIC_API_KEY is set in .env")

    else:
        st.markdown("""<div style="background:#f7f9fc;border:2px dashed #c8a14b;border-radius:10px;
            padding:40px;text-align:center;margin-top:20px;">
            <div style="font-size:48px;">🛡️</div>
            <div style="font-size:16px;font-weight:700;color:#0d6e6e;margin-top:12px;">Enter IMO or vessel name above</div>
            <div style="font-size:12px;color:#666;margin-top:8px;max-width:500px;margin-left:auto;margin-right:auto;">
                Foresight Live gives you live vessel tracking, corridor threat analysis,
                sanctions screening, and a one-click branded VRA PDF —
                everything a shipowner or broker needs, without the Windward price tag.
            </div>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════
# PAGE: RISK INTELLIGENCE
# ════════════════════════════════════════════
elif page == "🌍 Risk Intelligence":
    sec("🤖 GeoSentinel Agent — Live Corridor Risk Assessment")

    col_btn, col_info = st.columns([1,3])
    with col_btn:
        run_btn = st.button("▶ Run GeoSentinel", use_container_width=True)
    with col_info:
        st.info("Agent fuses live news, commodity prices, and AIS data to score corridor disruption risk in real time.")

    if run_btn:
        with st.spinner("GeoSentinel scanning intelligence feeds..."):
            result = geo_sentinel.run()
        st.session_state["geo_result"] = result

    if "geo_result" in st.session_state:
        r = st.session_state["geo_result"]
        if "error" not in r:
            c1,c2,c3 = st.columns(3)
            with c1: st.metric("Overall Risk", r.get("overall_risk_level","—"))
            with c2: st.metric("Composite Score", f"{r.get('overall_risk_score','—')}/100")
            with c3: st.metric("Corridors Monitored", "4")
            st.info(r.get("analyst_summary",""))

            corridors = r.get("corridors",{})
            if corridors:
                cols = st.columns(len(corridors))
                for i,(key,data) in enumerate(corridors.items()):
                    score = data.get("risk_score",0)
                    level = data.get("risk_level","MODERATE")
                    col = RISK_COLORS.get(level,"#888")
                    bg  = RISK_BG.get(level,"#f5f5f5")
                    with cols[i]:
                        st.markdown(f"""<div style="background:{bg};border:2px solid {col};
                            border-radius:8px;padding:14px;text-align:center;">
                            <div style="font-size:10px;color:#666;font-weight:600;text-transform:uppercase;">{key.replace('_',' ')}</div>
                            <div style="font-size:32px;font-weight:900;color:{col};margin:6px 0;">{score}</div>
                            <div style="font-size:11px;color:{col};font-weight:700;">{level}</div>
                            <div style="font-size:9px;color:#888;margin-top:6px;">{data.get('primary_threat','')[:55]}</div>
                        </div>""", unsafe_allow_html=True)

            top_risks = r.get("top_3_risks",[])
            if top_risks:
                sec("🚨 Top Active Risks")
                for risk in top_risks:
                    prob = risk.get("probability",50)
                    rc = RISK_COLORS.get("HIGH" if prob>=70 else "ELEVATED","#e65100")
                    with st.expander(f"#{risk['rank']} — {risk['risk']} (Probability: {prob}%)"):
                        st.write(risk.get("impact",""))


# ════════════════════════════════════════════
# PAGE: SCENARIO MODELLER
# ════════════════════════════════════════════
elif page == "📊 Scenario Modeller":
    sec("📊 Disruption Scenario Intelligence Engine")

    scenarios = scenario_modeller.get_all_scenarios()
    scenario_names = {k: f"{v['icon']} {v['name']}" for k,v in scenarios.items()}
    sel_key = st.selectbox("Select Disruption Scenario", list(scenario_names.keys()),
                           format_func=lambda k: scenario_names[k])
    sel = scenarios[sel_key]
    col1,col2 = st.columns(2)
    with col1: st.info(sel['description'])
    with col2: st.warning(f"Supply reduction: {sel['supply_reduction_pct']}% | Duration: {sel['duration_days']} days")

    if st.button(f"▶ Model: {sel['name']}", use_container_width=True):
        with st.spinner("Computing cascading economic impacts..."):
            result = scenario_modeller.run(sel_key)
        st.session_state["sc_result"] = result

    if "sc_result" in st.session_state:
        r = st.session_state["sc_result"]
        if "error" not in r:
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("Supply Gap", f"{r.get('india_supply_gap_mbpd',0):.2f} MBPD")
            with c2: st.metric("Brent Spike", f"+{r.get('brent_price_spike_estimate_pct',0):.1f}%")
            with c3: st.metric("Import Bill +", f"${r.get('india_import_bill_increase_usd_bn_monthly',0):.1f}Bn/mo")
            with c4: st.metric("GDP Impact", f"{r.get('gdp_impact_annualised_pct',0):.2f}% ann.")
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("Petrol Impact", f"+₹{r.get('petrol_price_impact_inr_per_litre',0):.1f}/L")
            with c2: st.metric("Diesel Impact", f"+₹{r.get('diesel_price_impact_inr_per_litre',0):.1f}/L")
            with c3: st.metric("SPR Cover", f"{r.get('spr_cover_days',9.5):.1f} days")
            with c4: st.metric("Power Sector", r.get("power_sector_stress_level","—"))

            c_tl, c_rec = st.columns(2)
            with c_tl:
                sec("⏱ Response Timeline")
                for ev in r.get("response_timeline",[]):
                    st.markdown(f"""<div style="display:flex;gap:10px;margin-bottom:8px;">
                        <div style="background:#0d6e6e;color:#fff;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:700;white-space:nowrap;">Day {ev.get('day','?')}</div>
                        <div><b style="font-size:12px;">{ev.get('action','')}</b><br>
                        <span style="font-size:11px;color:#666;">{ev.get('impact','')}</span></div>
                    </div>""", unsafe_allow_html=True)
            with c_rec:
                sec("🛡️ Mitigations & Vulnerabilities")
                for rec in r.get("mitigation_recommendations",[]):
                    st.markdown(f"✅ {rec}")
                for v in r.get("key_vulnerabilities",[]):
                    st.markdown(f"🔴 {v}")

            st.info(r.get("scenario_narrative",""))


# ════════════════════════════════════════════
# PAGE: AIS TRACKER
# ════════════════════════════════════════════
elif page == "🚢 AIS Tracker":
    sec("🚢 AIS Maritime Intelligence — India Supply Corridor Tracking")

    vessels = ais_tracker.get_live_vessels()
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Vessels Tracked", len(vessels))
    at_risk = ais_tracker.get_at_risk_vessels()
    with c2: st.metric("⚠️ At Risk / Delayed", len(at_risk))
    diverting = len([v for v in vessels if "DIVERTING" in v["status"] or "ALT ROUTE" in v["status"]])
    with c3: st.metric("🔄 Rerouted (Cape)", diverting)
    with c4: st.metric("🟢 Normal Transit", len(vessels)-len(at_risk)-diverting)

    m = folium.Map(location=[15,60], zoom_start=3, tiles="CartoDB Positron")
    STATUS_COLORS = {
        "TRANSITING":"#2e7d32","TRANSITING — ALT ROUTE":"#388e3c",
        "ANCHORED — AWAITING CLEARANCE":"#e65100","DELAYED — RISK ASSESSMENT":"#c62828",
        "DIVERTING — CAPE ROUTE":"#f57c00","APPROACHING PORT":"#1976d2",
    }
    corridor_defs = {
        "strait_of_hormuz":([26.57,56.25],"#c62828","Hormuz — HIGH RISK"),
        "red_sea":([14.5,43.0],"#c62828","Red Sea — HIGH RISK"),
        "gulf_of_guinea":([2.5,2.5],"#e65100","Gulf of Guinea — ELEVATED"),
        "cape_of_good_hope":([-34.36,18.48],"#2e7d32","Cape — Alt Route"),
    }
    for ck,(ccoord,ccol,clbl) in corridor_defs.items():
        folium.CircleMarker(ccoord,radius=30,color=ccol,fill=True,fill_opacity=0.1,weight=2,popup=clbl).add_to(m)

    for r in INDIA_REFINERIES:
        folium.CircleMarker([r["lat"],r["lon"]],radius=7,color="#0d6e6e",fill=True,fill_opacity=0.8,
            popup=f"🏭 {r['name']} — {r['capacity_mbpd']} MBPD").add_to(m)

    for v in vessels:
        col = STATUS_COLORS.get(v["status"],"#888")
        folium.CircleMarker([v["lat"],v["lon"]],radius=8,color=col,fill=True,fill_opacity=0.9,
            popup=f"<b>{v['name']}</b><br>{v['type']}<br>{v['cargo']}<br><b>{v['status']}</b><br>→ {v['destination']}",
            tooltip=f"{v['name']} ({v['type']})").add_to(m)

    st_folium(m, width=None, height=480)

    sec("📋 Vessel Intelligence Feed")
    df = pd.DataFrame([{
        "Vessel": f"{v['icon']} {v['name']}", "Type": v["type"],
        "Flag": v["flag"], "Cargo": v["cargo"], "Status": v["status"],
        "Destination": v["destination"], "ETA (days)": v.get("eta_days","—"),
    } for v in vessels])
    st.dataframe(df, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════
# PAGE: PROCUREMENT
# ════════════════════════════════════════════
elif page == "🛒 Procurement Engine":
    sec("🛒 Adaptive Procurement Orchestrator")

    col1,col2 = st.columns(2)
    with col1: gap = st.slider("Supply Gap to Fill (MBPD)", 0.1, 3.0, 1.2, 0.1)
    with col2: scenario_name = st.selectbox("Disruption Context", [
        "Strait of Hormuz — 40% Reduction","Red Sea Full Suspension",
        "OPEC+ Emergency Cut","Dual Corridor Crisis"])

    if st.button("▶ Generate Procurement Plan", use_container_width=True):
        with st.spinner("Procurement Agent ranking alternative sources..."):
            result = procurement_agent.run(gap, scenario_name)
        st.session_state["proc_result"] = result

    if "proc_result" in st.session_state:
        r = st.session_state["proc_result"]
        if "error" not in r:
            c1,c2,c3 = st.columns(3)
            with c1: st.metric("Gap to Fill", f"{r['_meta']['supply_gap_mbpd']:.1f} MBPD")
            with c2: st.metric("Covered", f"{r.get('total_gap_covered_mbpd',0):.1f} MBPD")
            with c3:
                res = r.get("residual_gap_mbpd",0)
                st.metric("Residual", f"{res:.2f} MBPD", "✅ Covered" if res<=0 else f"⚠️ {res:.2f} uncovered")

            sec("🌍 Ranked Alternative Sources")
            for alt in r.get("ranked_alternatives",[]):
                conf = alt.get("confidence_score",70)
                cc = RISK_COLORS.get("LOW" if conf>=70 else "MODERATE","#e65100")
                with st.expander(f"#{alt.get('rank','?')} {alt.get('country','?')} — {alt.get('grade','?')} | {alt.get('recommended_volume_mbpd',0):.2f} MBPD | {conf}% confidence"):
                    co1,co2,co3,co4 = st.columns(4)
                    with co1: st.metric("Volume", f"{alt.get('recommended_volume_mbpd',0):.2f} MBPD")
                    with co2: st.metric("Mechanism", alt.get("procurement_mechanism","SPOT"))
                    with co3: st.metric("Transit", f"{alt.get('transit_days_to_india','?')}d")
                    with co4: st.metric("Cost/bbl", f"${alt.get('total_cost_usd_per_barrel',0):.1f}")
                    st.markdown(f"**Price vs Brent:** {alt.get('estimated_price_vs_brent','—')}")
                    st.markdown(f"**Refineries:** {', '.join(alt.get('grade_compatible_refineries',[]))}")
                    st.markdown(f"**⚡ Action:** {alt.get('action_required','')}")

            sec("⚡ 48-Hour Action Plan")
            for act in r.get("immediate_actions_48h",[]):
                st.markdown(f"**[{act.get('priority','?')}]** {act.get('action','')} — `{act.get('owner','')}` by {act.get('deadline','')}")

            st.info(r.get("executive_summary",""))


# ════════════════════════════════════════════
# PAGE: SPR OPTIMISER
# ════════════════════════════════════════════
elif page == "🛢️ SPR Optimiser":
    sec("🛢️ Strategic Petroleum Reserve Optimiser")

    # SPR site chart
    fig_spr = go.Figure()
    for site in SPR_SITES:
        filled = site["capacity_MMbbl"] * site["current_fill_pct"] / 100
        empty  = site["capacity_MMbbl"] - filled
        fig_spr.add_trace(go.Bar(name=f"{site['name']} (Filled)", x=[site["name"]], y=[filled],
                                marker_color="#0d6e6e"))
        fig_spr.add_trace(go.Bar(name=f"{site['name']} (Empty)", x=[site["name"]], y=[empty],
                                marker_color="#e4e9f0"))
    fig_spr.update_layout(barmode="stack", paper_bgcolor="#fff", plot_bgcolor="#fff",
                         title="SPR Site Levels (MMbbl)", height=280,
                         margin=dict(l=0,r=0,t=40,b=0), showlegend=False)
    st.plotly_chart(fig_spr, use_container_width=True)

    c1,c2,c3 = st.columns(3)
    with c1: gap    = st.number_input("Supply Gap (MBPD)", 0.1, 5.0, 1.5, 0.1)
    with c2: dur    = st.slider("Duration (days)", 7, 180, 45)
    with c3: sc_name= st.selectbox("Scenario", ["Hormuz Partial Closure","Red Sea Suspension","OPEC Emergency Cut"])

    if st.button("▶ Optimise SPR Strategy", use_container_width=True):
        with st.spinner("SPR Optimiser computing drawdown strategy..."):
            result = spr_optimiser.run(gap, dur, sc_name)
        st.session_state["spr_result"] = result

    if "spr_result" in st.session_state:
        r = st.session_state["spr_result"]
        if "error" not in r:
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("SPR Available", f"{r.get('spr_total_available_mmbbls',0):.0f} MMbbl")
            with c2: st.metric("Cover", f"{r.get('spr_cover_days_current',9.5):.1f} days")
            with c3: st.metric("Strategy", r.get("recommended_drawdown_strategy","—"))
            with c4: st.metric("Drawdown Rate", f"{r.get('daily_drawdown_mbpd',0):.2f} MBPD")

            sec("🏭 By-Site Drawdown Plan")
            for site in r.get("by_site",[]):
                pc = {"PRIMARY":"#c62828","SECONDARY":"#e65100","RESERVE":"#2e7d32"}.get(site.get("priority",""),"#888")
                st.markdown(f"""<div style="border-left:4px solid {pc};padding:10px 14px;background:#fff;
                    border-radius:0 6px 6px 0;margin-bottom:6px;">
                    <b style="color:{pc};">[{site.get('priority','?')}]</b>
                    <b> {site.get('site','?')}</b> — {site.get('drawdown_mbpd',0):.2f} MBPD<br>
                    <span style="font-size:11px;color:#666;">{site.get('rationale','')}</span>
                </div>""", unsafe_allow_html=True)

            rep = r.get("replenishment_window",{})
            if rep:
                sec("🔄 Replenishment Strategy")
                rc1,rc2,rc3 = st.columns(3)
                with rc1: st.metric("Replenish From", f"Day {rep.get('earliest_start_days_from_now','?')}")
                with rc2: st.metric("Target Price", f"${rep.get('optimal_brent_replenishment_price',75):.0f}/bbl")
                with rc3: st.metric("Cost", f"${rep.get('estimated_replenishment_cost_usd_bn',0):.1f}Bn")

            iea = r.get("iea_coordination",{})
            if iea.get("recommended"):
                st.success(f"🌐 IEA coordination recommended: {iea.get('rationale','')} (+{iea.get('estimated_iea_contribution_mbpd',0):.1f} MBPD)")

            st.info(r.get("executive_recommendation",""))
