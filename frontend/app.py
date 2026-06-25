"""
EnergyShield AI × Foresight Live — Full Production Platform
ET AI Hackathon 2026 | PS 2
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import os, sys, tempfile
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import CORRIDORS, INDIA_REFINERIES, SPR_SITES
from utils.live_data import (
    get_live_commodity_prices, get_brent_history_live, get_tanker_rates_live,
    get_live_news, get_port_intelligence
)
from agents import geo_sentinel, scenario_modeller, procurement_agent, spr_optimiser, ais_tracker
from agents import vessel_intel
from utils.vra_pdf import generate_vra_pdf

st.set_page_config(page_title="EnergyShield AI × Foresight Live", page_icon="⚡",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
.stApp{background:#f4f6f9;color:#1a2332;}
[data-testid="stSidebar"]{background:#0d1b2e;}
[data-testid="stSidebar"] *{color:#e8f4f8 !important;}
[data-testid="stSidebar"] .stRadio label{color:#e8f4f8 !important;}
.card{background:#fff;border-radius:10px;padding:16px 20px;border:1px solid #e2e8f0;margin-bottom:12px;box-shadow:0 1px 6px rgba(0,0,0,0.06);}
.gold-card{background:#fffbf0;border-radius:10px;padding:14px 18px;border:1px solid #c8a14b;margin-bottom:12px;}
.hdr{background:linear-gradient(90deg,#0d6e6e,#0a4848);color:#fff !important;padding:8px 16px;border-radius:6px;font-size:13px;font-weight:700;letter-spacing:.5px;margin-bottom:14px;}
.news-row{border-left:3px solid #0d6e6e;padding:8px 12px;background:#fff;border-radius:0 6px 6px 0;margin-bottom:7px;box-shadow:0 1px 3px rgba(0,0,0,0.04);}
.vessel-card{background:#fff;border-radius:8px;border:1px solid #e2e8f0;padding:10px 14px;margin-bottom:6px;box-shadow:0 1px 3px rgba(0,0,0,0.04);}
.badge-critical{background:#b71c1c;color:#fff;padding:2px 9px;border-radius:10px;font-size:10px;font-weight:700;}
.badge-high{background:#c62828;color:#fff;padding:2px 9px;border-radius:10px;font-size:10px;font-weight:700;}
.badge-elevated{background:#e65100;color:#fff;padding:2px 9px;border-radius:10px;font-size:10px;font-weight:700;}
.badge-moderate{background:#f57f17;color:#fff;padding:2px 9px;border-radius:10px;font-size:10px;font-weight:700;}
.badge-low{background:#2e7d32;color:#fff;padding:2px 9px;border-radius:10px;font-size:10px;font-weight:700;}
[data-testid="metric-container"]{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:10px;box-shadow:0 1px 4px rgba(0,0,0,0.05);}
.stButton>button{background:linear-gradient(135deg,#0d6e6e,#0a4848);color:#fff;border:none;border-radius:6px;font-weight:600;padding:8px 16px;}
.stButton>button:hover{opacity:.9;}
.stDownloadButton>button{background:linear-gradient(135deg,#c8a14b,#a0782a);color:#fff;border:none;border-radius:6px;font-weight:700;}
</style>""", unsafe_allow_html=True)

RC = {"CRITICAL":"#b71c1c","HIGH":"#c62828","ELEVATED":"#e65100","MODERATE":"#f57f17","LOW":"#2e7d32"}
BG = {"CRITICAL":"#ffebee","HIGH":"#ffcdd2","ELEVATED":"#fff3e0","MODERATE":"#fffde7","LOW":"#e8f5e9"}

def badge(level):
    cls = {"CRITICAL":"badge-critical","HIGH":"badge-high","ELEVATED":"badge-elevated","MODERATE":"badge-moderate","LOW":"badge-low"}.get(level,"badge-moderate")
    return f'<span class="{cls}">{level}</span>'

def hdr(t): st.markdown(f'<div class="hdr">{t}</div>', unsafe_allow_html=True)

# ── LIVE DATA ──
prices = get_live_commodity_prices()
brent  = prices.get("brent_crude",{})
bp     = brent.get("price",87.4)
bc     = brent.get("change_pct",0)
wti    = prices.get("wti_crude",{})

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## ⚡ EnergyShield AI")
    st.markdown("**× Foresight Live**")
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
    arrow = "▲" if bc>=0 else "▼"
    col = "#2e7d32" if bc>=0 else "#c62828"
    st.markdown(f"**Brent Crude**")
    st.markdown(f"<div style='font-size:22px;font-weight:800;color:#0d6e6e;'>${bp}</div>"
                f"<div style='color:{col};font-size:12px;'>{arrow} {abs(bc):.1f}%</div>",
                unsafe_allow_html=True)
    st.markdown(f"WTI: **${wti.get('price','—')}**")
    ng = prices.get("natural_gas",{})
    st.markdown(f"Nat. Gas: **${ng.get('price','—')}/MMBtu**")
    st.caption(f"Source: {brent.get('source','—')}")
    st.markdown("---")
    st.markdown("**SPR Status**")
    st.progress(0.88, text="88% Full — 9.5 days cover")
    st.markdown("---")
    tankers = get_tanker_rates_live()
    st.markdown("**Tanker Rates ($/day)**")
    st.caption(f"VLCC ME→India: ${tankers.get('vlcc_me_india',0):,.0f}")
    st.caption(f"Suezmax WAF→India: ${tankers.get('suezmax_waf_india',0):,.0f}")
    st.markdown("---")
    st.caption("© HR Maritime Consultants\nForesight Intelligence Platform\nET AI Hackathon 2026")

# ── HEADER ──
st.markdown(f"""<div style="background:linear-gradient(135deg,#0d1b2e,#0d6e6e);
    border-radius:12px;padding:20px 28px;margin-bottom:20px;display:flex;align-items:center;gap:16px;">
  <div style="font-size:38px;">⚡</div>
  <div>
    <div style="font-size:22px;font-weight:800;color:#fff;">EnergyShield AI × Foresight Live</div>
    <div style="font-size:12px;color:rgba(255,255,255,0.65);margin-top:3px;">
      India Energy Supply Chain Resilience Platform &nbsp;·&nbsp; ET AI Hackathon 2026
    </div>
  </div>
  <div style="margin-left:auto;text-align:right;">
    <div style="font-size:10px;color:rgba(255,255,255,0.5);">INTELLIGENCE ACTIVE</div>
    <div style="font-size:13px;color:#c8a14b;font-weight:700;">{datetime.utcnow().strftime('%d %b %Y %H:%M')} UTC</div>
  </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# COMMAND CENTRE
# ══════════════════════════════════════════
if page == "🏠 Command Centre":
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: st.metric("🛢️ India Imports","5.1 MBPD","total daily")
    with c2: st.metric("⚠️ Hormuz Dep.","42%","of imports")
    with c3: st.metric("🔴 Red Sea","HIGH RISK","3 incidents/7d")
    with c4: st.metric("🏛️ SPR Cover","9.5 days","88% full")
    with c5: st.metric("💰 Brent",f"${bp}/bbl",f"{'+' if bc>=0 else ''}{bc:.1f}%")
    with c6: st.metric("🚢 VLCC Rate",f"${tankers.get('vlcc_me_india',35000):,.0f}/d","ME→India")
    st.markdown("---")

    col1,col2 = st.columns([3,2])
    with col1:
        hdr("📈 Brent Crude — 90-Day Live Price History")
        df = get_brent_history_live(90)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["brent_usd"],
            fill="tozeroy", fillcolor="rgba(13,110,110,0.1)",
            line=dict(color="#0d6e6e",width=2.5), name="Brent USD/bbl"))
        fig.add_vline(x=df.index[-15], line_dash="dash", line_color="#c62828",
            annotation_text="Hormuz Exercise", annotation_font_color="#c62828", annotation_font_size=10)
        fig.add_vline(x=df.index[-30], line_dash="dot", line_color="#e65100",
            annotation_text="Houthi strike", annotation_font_color="#e65100", annotation_font_size=10)
        fig.update_layout(paper_bgcolor="#fff",plot_bgcolor="#fff",font_color="#1a2332",
            height=280,margin=dict(l=0,r=0,t=20,b=0),
            xaxis=dict(gridcolor="#f0f0f0"),yaxis=dict(gridcolor="#f0f0f0",title="USD/bbl"),showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        hdr("🌐 Corridor Risk Index")
        scores = {"Hormuz":78,"Red Sea":85,"Gulf of Guinea":65,"Cape (Alt)":22}
        fig2 = go.Figure(go.Bar(
            x=list(scores.values()), y=list(scores.keys()), orientation="h",
            marker_color=["#c62828","#b71c1c","#e65100","#2e7d32"],
            text=[f"{v}/100" for v in scores.values()], textposition="outside",
            textfont=dict(color="#1a2332",size=12)
        ))
        fig2.update_layout(paper_bgcolor="#fff",plot_bgcolor="#fff",font_color="#1a2332",
            height=280,margin=dict(l=0,r=50,t=20,b=0),
            xaxis=dict(range=[0,115],showgrid=False,showticklabels=False),
            yaxis=dict(gridcolor="#f0f0f0"))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    col3,col4 = st.columns([3,2])
    with col3:
        hdr("📰 Live Geopolitical Intelligence Feed")
        news = get_live_news(7)
        for h in news:
            rs = h.get("risk_score",50)
            b = badge("HIGH" if rs>=75 else "ELEVATED" if rs>=60 else "MODERATE" if rs>=45 else "LOW")
            st.markdown(f"""<div class="news-row">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">
                    <div style="font-size:13px;font-weight:600;flex:1;">{h['title']}</div>
                    <div style="white-space:nowrap;">{b}</div>
                </div>
                <div style="font-size:10px;color:#888;margin-top:4px;">
                    {h['source']} · {h['published']} · {h.get('corridor','').replace('_',' ').title()}
                </div>
            </div>""", unsafe_allow_html=True)

    with col4:
        hdr("🚢 Vessels At Risk")
        for v in ais_tracker.get_at_risk_vessels():
            rc2 = RC.get("HIGH","#c62828")
            st.markdown(f"""<div class="vessel-card">
                <div style="font-size:13px;font-weight:700;color:#0d6e6e;">{v['icon']} {v['name']}</div>
                <div style="font-size:11px;color:#666;margin-top:2px;">{v['type']} · {v['cargo'][:30]}</div>
                <div style="font-size:11px;color:{rc2};margin-top:3px;font-weight:600;">⚠ {v['status']}</div>
                <div style="font-size:10px;color:#999;">→ {v['destination']}</div>
            </div>""", unsafe_allow_html=True)

        hdr("🌊 Port Incidents (UKMTO/ICC)")
        for inc in get_port_intelligence()[:3]:
            rs = inc.get("risk_score",50)
            rc2 = RC.get("HIGH" if rs>=75 else "MODERATE","#e65100")
            st.markdown(f"""<div style="border-left:3px solid {rc2};padding:6px 10px;
                background:#fff;border-radius:0 4px 4px 0;margin-bottom:5px;">
                <div style="font-size:11px;font-weight:600;">{inc['title'][:65]}</div>
                <div style="font-size:10px;color:#888;">{inc['source']} · {inc['published']}</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# FORESIGHT LIVE
# ══════════════════════════════════════════
elif page == "🛡️ Foresight Live":
    st.markdown("""<div class="gold-card">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="font-size:30px;">🛡️</div>
            <div>
                <div style="font-size:15px;font-weight:800;color:#0d6e6e;">Foresight Live — Vessel Intelligence Terminal</div>
                <div style="font-size:11px;color:#666;margin-top:2px;">
                    Live AIS tracking · Corridor threat scoring · Sanctions screening · One-click branded VRA PDF<br>
                    <b>The intelligence layer that costs $50K+/yr from Windward — built for shipowners who need answers, not enterprise contracts.</b>
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    cs, cb = st.columns([5,1])
    with cs:
        query = st.text_input("", placeholder="Enter IMO number (e.g. 9839131) or vessel name (e.g. FALCON MAJESTIC)", label_visibility="collapsed")
    with cb:
        do_search = st.button("🔍 Track", use_container_width=True)

    st.markdown("**Quick-load demo fleet:**")
    fleet = vessel_intel.get_demo_fleet()
    fc = st.columns(len(fleet))
    for i,v in enumerate(fleet):
        short = v["name"].replace("MV ","").replace("MT ","")[:14]
        if fc[i].button(short, key=f"f{i}", use_container_width=True):
            st.session_state["flv"] = v
            st.session_state.pop("flvra",None)

    if do_search and query:
        found = vessel_intel.lookup_vessel(query)
        if found:
            st.session_state["flv"] = found
            st.session_state.pop("flvra",None)
        else:
            st.error(f"Vessel not found for '{query}'. Try IMO 9745372 or name RED SEA TRADER.")

    if "flv" in st.session_state:
        v = st.session_state["flv"]
        risk = vessel_intel.quick_risk_score(v)
        rc2  = RC.get(risk["level"],"#e65100")
        rbg  = BG.get(risk["level"],"#fff3e0")
        icon = v.get("_icon","🚢")

        st.markdown(f"""<div style="background:linear-gradient(135deg,#0d1b2e,#1a3a5f);
            border:2px solid {rc2};border-radius:10px;padding:18px 22px;margin:12px 0;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:20px;font-weight:800;color:#fff;">{icon} {v['name']}</div>
                    <div style="font-size:11px;color:#90a4ae;margin-top:3px;">
                        IMO {v['imo']} &nbsp;·&nbsp; {v['type']} &nbsp;·&nbsp; {v.get('flag','—')} flag &nbsp;·&nbsp; {v.get('dwt','—')} DWT &nbsp;·&nbsp; Built {v.get('built') or v.get('year_built','—')}
                    </div>
                    <div style="font-size:12px;color:#b0bec5;margin-top:4px;">📍 {v.get('current_route','—')}</div>
                </div>
                <div style="background:{rc2};padding:12px 20px;border-radius:8px;text-align:center;min-width:90px;">
                    <div style="font-size:9px;color:rgba(255,255,255,0.8);">VOYAGE RISK</div>
                    <div style="font-size:30px;font-weight:900;color:#fff;line-height:1.1;">{risk['score']}</div>
                    <div style="font-size:11px;color:#fff;font-weight:700;">{risk['level']}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        m1,m2,m3,m4,m5 = st.columns(5)
        with m1: st.metric("⚡ Speed",f"{v.get('speed_kts','—')} kts")
        with m2: st.metric("🧭 Heading",f"{v.get('heading','—')}°")
        with m3: st.metric("⚓ Draught",f"{v.get('draught','—')} m")
        with m4: st.metric("📦 Cargo",(v.get('cargo') or '—')[:16])
        with m5: st.metric("🕐 ETA",(v.get('eta') or '—')[:10])

        t1,t2,t3,t4 = st.tabs(["📍 Live Map","🔴 Threats","🌊 Weather","🔒 Compliance"])

        with t1:
            vm = folium.Map(location=[v["lat"],v["lon"]], zoom_start=5, tiles="CartoDB Positron")
            zones = {
                "strait_of_hormuz":([26.57,56.25],80,"#c62828","Hormuz — HIGH RISK"),
                "red_sea":([14.5,43.0],90,"#c62828","Red Sea — HIGH RISK"),
                "gulf_of_guinea":([2.5,2.5],70,"#e65100","Gulf of Guinea — ELEVATED"),
                "arabian_sea":([18.0,64.0],40,"#1976d2","Arabian Sea — MODERATE"),
            }
            for ck,(cc,cr,ccol,clbl) in zones.items():
                folium.CircleMarker(cc,radius=cr,color=ccol,fill=True,fill_opacity=0.08,
                    weight=2,popup=clbl).add_to(vm)
                folium.Marker(cc,icon=folium.DivIcon(html=f'<div style="background:{ccol};color:#fff;padding:2px 6px;border-radius:4px;font-size:9px;font-weight:700;white-space:nowrap;">{clbl}</div>')).add_to(vm)
            for r in INDIA_REFINERIES:
                folium.CircleMarker([r["lat"],r["lon"]],radius=7,color="#0d6e6e",fill=True,
                    fill_opacity=0.8,popup=f"🏭 {r['name']} — {r['capacity_mbpd']} MBPD").add_to(vm)
            folium.Marker([v["lat"],v["lon"]],
                icon=folium.DivIcon(html=f'<div style="font-size:20px;">{icon}</div>'),
                popup=f"<b>{v['name']}</b><br>IMO: {v['imo']}<br>{v.get('status','')}"
            ).add_to(vm)
            folium.CircleMarker([v["lat"],v["lon"]],radius=12,color=rc2,fill=True,fill_opacity=0.4,weight=2).add_to(vm)
            st_folium(vm, width=None, height=420, key="flmap")

        with t2:
            corridor_key = v.get("corridor","")
            corr = CORRIDORS.get(corridor_key,{})
            threat_map = {
                "Piracy / Armed Robbery":    {"strait_of_hormuz":"LOW","red_sea":"MODERATE","gulf_of_guinea":"HIGH","arabian_sea":"LOW"},
                "Geopolitical / Military":   {"strait_of_hormuz":"HIGH","red_sea":"HIGH","gulf_of_guinea":"LOW","arabian_sea":"LOW"},
                "Drone / Missile Threat":    {"strait_of_hormuz":"ELEVATED","red_sea":"CRITICAL","gulf_of_guinea":"LOW","arabian_sea":"LOW"},
                "GPS Spoofing / Jamming":    {"strait_of_hormuz":"HIGH","red_sea":"MODERATE","gulf_of_guinea":"LOW","arabian_sea":"LOW"},
                "Weather / Sea State":       {"strait_of_hormuz":"LOW","red_sea":"LOW","gulf_of_guinea":"MODERATE","arabian_sea":"LOW"},
            }
            threat_detail = {
                "Piracy / Armed Robbery":    {"strait_of_hormuz":"Minimal piracy risk on this corridor","red_sea":"Residual Somali piracy risk in GoA approaches","gulf_of_guinea":"Active kidnap-for-ransom operations. IMB HRA in effect.","arabian_sea":"Low residual Somali piracy risk"},
                "Geopolitical / Military":   {"strait_of_hormuz":"IRGC naval exercise ongoing. US sanctions pressure elevated.","red_sea":"Active Houthi anti-ship operations. Multiple vessels struck.","gulf_of_guinea":"No current state-level threat","arabian_sea":"No direct military threat on this route"},
                "Drone / Missile Threat":    {"strait_of_hormuz":"IRGC drone capability confirmed. Elevated alert.","red_sea":"CRITICAL — Houthi AShM and drone strikes ongoing June 2026","gulf_of_guinea":"Not applicable on this corridor","arabian_sea":"Outside current Houthi engagement envelope"},
                "GPS Spoofing / Jamming":    {"strait_of_hormuz":"GPS jamming reported — 11,600+ vessels affected Q1 2026","red_sea":"Intermittent interference reported","gulf_of_guinea":"Not reported","arabian_sea":"Minimal"},
                "Weather / Sea State":       {"strait_of_hormuz":"Favourable conditions expected","red_sea":"Favourable — SW monsoon onset","gulf_of_guinea":"Moderate swell. SW monsoon active.","arabian_sea":"SW monsoon. Moderate-rough seas possible."},
            }
            for threat,lvl_map in threat_map.items():
                lvl = lvl_map.get(corridor_key,"MODERATE")
                detail = threat_detail.get(threat,{}).get(corridor_key,"—")
                tc = RC.get(lvl,"#888")
                tbg = BG.get(lvl,"#f5f5f5")
                st.markdown(f"""<div style="background:{tbg};border-radius:6px;border-left:4px solid {tc};
                    padding:10px 14px;margin-bottom:6px;display:flex;align-items:center;gap:12px;">
                    <div style="flex:1;">
                        <div style="font-size:13px;font-weight:600;">{threat}</div>
                        <div style="font-size:11px;color:#555;margin-top:3px;">{detail}</div>
                    </div>
                    <div style="background:{tc};color:#fff;padding:3px 12px;border-radius:12px;font-size:11px;font-weight:700;white-space:nowrap;">{lvl}</div>
                </div>""", unsafe_allow_html=True)
            if corr:
                st.info(f"**{corr.get('name','—')}** | HRA: {'✅ Yes' if corr.get('hra') else '—'} | BMP5: {'✅ Applicable' if corr.get('bmp5_applicable') else '—'} | UKMTO: {'✅ Register' if corr.get('ukmto_area') else '—'}")

        with t3:
            from utils.live_data import get_route_weather
            wx = get_route_weather(v.get("lat",15), v.get("lon",60))
            wc1,wc2,wc3,wc4 = st.columns(4)
            with wc1: st.metric("🌊 Wave Height",f"{wx.get('wave_height_m','—')} m")
            with wc2: st.metric("⏱ Wave Period",f"{wx.get('wave_period_s','—')} s")
            with wc3: st.metric("💨 Wind Speed",f"{wx.get('wind_speed_kts','—')} kts")
            with wc4: st.metric("🌊 Sea State",wx.get('sea_state','—'))
            st.caption(f"📡 Source: {wx.get('source','—')} · Updated: {wx.get('_ts','')[:16]} UTC")

        with t4:
            from utils.live_data import check_sanctions_live
            sc = check_sanctions_live(v.get("imo",""),v.get("name",""))
            is_clear = sc.get("status","") == "CLEAR"
            scol = "#2e7d32" if is_clear else "#c62828"
            sbg  = "#f1f8e9" if is_clear else "#ffebee"
            st.markdown(f"""<div style="background:{sbg};border:2px solid {scol};
                border-radius:8px;padding:16px 20px;margin-bottom:12px;">
                <div style="font-size:16px;font-weight:800;color:{scol};">
                    {'✅ CLEAR' if is_clear else '🚨 '+sc.get('status','')}
                </div>
                <div style="margin-top:10px;display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                    <div style="font-size:11px;"><b>Screened against:</b><br>{'<br>'.join(sc.get('screened_against',[]))}</div>
                    <div style="font-size:11px;">
                        <b>Flag risk:</b> {sc.get('flag_risk','—')}<br>
                        <b>AIS history:</b> {sc.get('ais_gap_history','—')}<br>
                        <b>Ownership opacity:</b> {sc.get('ownership_opacity','—')}<br>
                        <b>Screened:</b> {sc.get('_ts','')[:16]} UTC
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
            if sc.get("matches"):
                st.error(f"⚠️ Sanctions matches found: {sc['matches']}")

        # VRA GENERATOR
        st.markdown("---")
        st.markdown("### 📄 One-Click Voyage Risk Assessment")
        st.markdown("""<div class="gold-card" style="font-size:12px;">
            💡 <b>The deliverable shipowners pay for.</b> AI-generated Foresight-branded VRA PDF in ~30 seconds
            — signed by Capt. Ritesh Kapoor, ready to email to charterers, P&I clubs, or war risk underwriters.
            <br><b>Requires: ANTHROPIC_API_KEY in .env</b>
        </div>""", unsafe_allow_html=True)

        if st.button("⚡ Generate Foresight VRA (Branded PDF)", use_container_width=True, type="primary"):
            with st.spinner("🤖 Foresight analyst generating voyage risk assessment..."):
                try:
                    vra = vessel_intel.generate_vra(v)
                    st.session_state["flvra"] = vra
                except Exception as e:
                    st.error(f"Error: {e}. Check ANTHROPIC_API_KEY in .env file.")

        if "flvra" in st.session_state:
            vra = st.session_state["flvra"]
            if "error" not in vra and vra.get("overall_risk_rating"):
                rating = vra.get("overall_risk_rating","MODERATE")
                score  = vra.get("risk_score",50)
                vc2 = RC.get(rating,"#e65100")
                vbg2= BG.get(rating,"#fff3e0")
                st.markdown(f"""<div style="background:{vbg2};border-left:5px solid {vc2};
                    border-radius:0 8px 8px 0;padding:14px 18px;margin:10px 0;">
                    <div style="font-size:14px;font-weight:800;color:{vc2};">
                        {vra.get('vessel_name','')} — {rating} RISK ({score}/100)
                    </div>
                    <div style="font-size:12px;color:#444;margin-top:6px;line-height:1.6;">
                        {vra.get('executive_summary','')}
                    </div>
                </div>""", unsafe_allow_html=True)

                threats = vra.get("threat_assessment",{})
                labels = {"piracy_armed_robbery":"Piracy","geopolitical_military":"Geo/Military",
                         "drone_missile_threat":"Drone/Missile","gps_spoofing_jamming":"GPS Jamming","sea_state_weather":"Weather"}
                tcols = st.columns(len(labels))
                for i,(k,lbl) in enumerate(labels.items()):
                    if k in threats:
                        lvl = threats[k].get("level","—")
                        lc2 = RC.get(lvl,"#888")
                        lbg2= BG.get(lvl,"#f5f5f5")
                        with tcols[i]:
                            st.markdown(f"""<div style="text-align:center;padding:8px 4px;
                                background:{lbg2};border-radius:6px;border:1px solid {lc2};">
                                <div style="font-size:9px;color:#666;font-weight:600;">{lbl}</div>
                                <div style="font-size:11px;color:{lc2};font-weight:800;margin-top:4px;">{lvl}</div>
                            </div>""", unsafe_allow_html=True)

                # Generate PDF
                with st.spinner("Building PDF..."):
                    pdf_path = os.path.join(tempfile.gettempdir(),f"Foresight_VRA_{v.get('imo','')}.pdf")
                    try:
                        generate_vra_pdf(vra, pdf_path)
                        with open(pdf_path,"rb") as f:
                            st.download_button(
                                "⬇️ Download Foresight VRA (Branded PDF)",
                                data=f.read(),
                                file_name=f"Foresight_VRA_{v['name'].replace(' ','_')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"PDF error: {e}")

                with st.expander("📋 Full Recommendations, Chokepoints & Insurance"):
                    c1v,c2v = st.columns(2)
                    with c1v:
                        st.markdown("**Operational Recommendations**")
                        for r in vra.get("recommendations",[]):
                            st.markdown(f"▸ {r}")
                        st.markdown("**Ship Hardening (BMP5)**")
                        for h in vra.get("hardening_measures",[]):
                            st.markdown(f"• {h}")
                    with c2v:
                        st.markdown("**Chokepoint Advisories**")
                        for cp in vra.get("chokepoints",[]):
                            lc2 = RC.get(cp.get("risk",""),"#888")
                            st.markdown(f"**{cp.get('name','')}** — {cp.get('advisory','')}")
                        st.markdown("**Reporting Requirements**")
                        for rr in vra.get("reporting_requirements",[]):
                            st.markdown(f"• {rr}")
                    st.markdown("**War Risk / Insurance**")
                    st.info(vra.get("insurance_note","—"))
            elif "error" in vra:
                st.error(f"VRA failed: {vra.get('error')}. Ensure ANTHROPIC_API_KEY is set in .env")

    else:
        st.markdown("""<div style="background:#fff;border:2px dashed #c8a14b;border-radius:10px;
            padding:40px;text-align:center;margin-top:20px;">
            <div style="font-size:48px;">🛡️</div>
            <div style="font-size:16px;font-weight:700;color:#0d6e6e;margin-top:12px;">Enter IMO or vessel name above, or tap a demo vessel</div>
            <div style="font-size:12px;color:#666;margin-top:8px;">
                Live AIS position · Corridor threat scoring · 5-list sanctions screening ·
                Marine weather · One-click branded VRA PDF
            </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# RISK INTELLIGENCE
# ══════════════════════════════════════════
elif page == "🌍 Risk Intelligence":
    hdr("🤖 GeoSentinel Agent — Live Corridor Risk Assessment")
    c1,c2 = st.columns([1,3])
    with c1:
        run_btn = st.button("▶ Run GeoSentinel Agent", use_container_width=True)
    with c2:
        st.info("Fuses live news feeds, commodity prices, and AIS data to score corridor disruption risk in real time using Claude AI.")

    if run_btn:
        with st.spinner("🤖 GeoSentinel scanning intelligence feeds..."):
            try:
                result = geo_sentinel.run()
                st.session_state["geo"] = result
            except Exception as e:
                st.error(f"Agent error: {e}. Check ANTHROPIC_API_KEY in .env")

    if "geo" in st.session_state:
        r = st.session_state["geo"]
        if "error" not in r:
            c1,c2,c3 = st.columns(3)
            with c1: st.metric("Overall Risk",r.get("overall_risk_level","—"))
            with c2: st.metric("Composite Score",f"{r.get('overall_risk_score','—')}/100")
            with c3: st.metric("Corridors Monitored","4")
            st.info(r.get("analyst_summary",""))

            corridors = r.get("corridors",{})
            if corridors:
                cols = st.columns(len(corridors))
                for i,(key,data) in enumerate(corridors.items()):
                    score = data.get("risk_score",0)
                    level = data.get("risk_level","MODERATE")
                    col2 = RC.get(level,"#888")
                    bg2  = BG.get(level,"#f5f5f5")
                    with cols[i]:
                        st.markdown(f"""<div style="background:{bg2};border:2px solid {col2};
                            border-radius:8px;padding:14px;text-align:center;">
                            <div style="font-size:10px;color:#666;font-weight:600;text-transform:uppercase;">{key.replace('_',' ')}</div>
                            <div style="font-size:32px;font-weight:900;color:{col2};margin:6px 0;">{score}</div>
                            <div style="font-size:11px;color:{col2};font-weight:700;">{level}</div>
                            <div style="font-size:9px;color:#888;margin-top:5px;">{data.get('primary_threat','')[:55]}</div>
                        </div>""", unsafe_allow_html=True)

            top = r.get("top_3_risks",[])
            if top:
                st.markdown("---")
                hdr("🚨 Top Active Risks")
                for risk in top:
                    prob = risk.get("probability",50)
                    col2 = RC.get("HIGH" if prob>=70 else "ELEVATED","#e65100")
                    bg2  = BG.get("HIGH" if prob>=70 else "ELEVATED","#fff3e0")
                    with st.expander(f"#{risk['rank']} — {risk['risk']} (Probability: {prob}%)"):
                        st.write(risk.get("impact",""))
        else:
            st.error(f"Agent error: {r.get('error')}. Check ANTHROPIC_API_KEY in .env")


# ══════════════════════════════════════════
# SCENARIO MODELLER
# ══════════════════════════════════════════
elif page == "📊 Scenario Modeller":
    hdr("📊 Disruption Scenario Intelligence Engine")
    scenarios = scenario_modeller.get_all_scenarios()
    sel_key = st.selectbox("Select Disruption Scenario",list(scenarios.keys()),
                           format_func=lambda k:f"{scenarios[k]['icon']} {scenarios[k]['name']}")
    sel = scenarios[sel_key]
    c1,c2 = st.columns(2)
    with c1: st.info(sel["description"])
    with c2: st.warning(f"Supply reduction: **{sel['supply_reduction_pct']}%** | Duration: **{sel['duration_days']} days**")

    if st.button(f"▶ Model Scenario: {sel['name']}", use_container_width=True):
        with st.spinner("🤖 Computing cascading economic impacts with Claude AI..."):
            try:
                result = scenario_modeller.run(sel_key)
                st.session_state["sc"] = result
            except Exception as e:
                st.error(f"Error: {e}. Check ANTHROPIC_API_KEY in .env")

    if "sc" in st.session_state:
        r = st.session_state["sc"]
        if "error" not in r:
            st.markdown("---")
            st.markdown(f"### {sel['icon']} Impact Analysis — {sel['name']}")
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("Supply Gap",f"{r.get('india_supply_gap_mbpd',0):.2f} MBPD")
            with c2: st.metric("Brent Spike",f"+{r.get('brent_price_spike_estimate_pct',0):.1f}%")
            with c3: st.metric("Import Bill",f"+${r.get('india_import_bill_increase_usd_bn_monthly',0):.1f}Bn/mo")
            with c4: st.metric("GDP Impact",f"{r.get('gdp_impact_annualised_pct',0):.2f}% ann.")
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("Petrol",f"+₹{r.get('petrol_price_impact_inr_per_litre',0):.1f}/L")
            with c2: st.metric("Diesel",f"+₹{r.get('diesel_price_impact_inr_per_litre',0):.1f}/L")
            with c3: st.metric("SPR Cover",f"{r.get('spr_cover_days',9.5):.1f} days")
            with c4: st.metric("Power Sector",r.get("power_sector_stress_level","—"))
            st.markdown("---")
            cl,cr = st.columns(2)
            with cl:
                hdr("⏱ Response Timeline")
                for ev in r.get("response_timeline",[]):
                    st.markdown(f"""<div style="display:flex;gap:10px;margin-bottom:8px;align-items:flex-start;">
                        <div style="background:#0d6e6e;color:#fff;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:700;white-space:nowrap;min-width:50px;text-align:center;">Day {ev.get('day','?')}</div>
                        <div><b style="font-size:12px;">{ev.get('action','')}</b><br>
                        <span style="font-size:11px;color:#666;">{ev.get('impact','')}</span></div>
                    </div>""", unsafe_allow_html=True)
            with cr:
                hdr("🛡️ Mitigations")
                for rec in r.get("mitigation_recommendations",[]): st.markdown(f"✅ {rec}")
                hdr("⚠️ Vulnerabilities")
                for vuln in r.get("key_vulnerabilities",[]): st.markdown(f"🔴 {vuln}")
            st.info(r.get("scenario_narrative",""))
        else:
            st.error(f"Error: {r.get('error')}. Check ANTHROPIC_API_KEY in .env")


# ══════════════════════════════════════════
# AIS TRACKER
# ══════════════════════════════════════════
elif page == "🚢 AIS Tracker":
    hdr("🚢 AIS Maritime Intelligence — India Supply Corridor Tracking")
    vessels = ais_tracker.get_live_vessels()
    at_risk = ais_tracker.get_at_risk_vessels()
    diverting = [v for v in vessels if "DIVERTING" in v["status"] or "ALT ROUTE" in v["status"]]
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Total Tracked",len(vessels))
    with c2: st.metric("⚠️ At Risk",len(at_risk))
    with c3: st.metric("🔄 Rerouted Cape",len(diverting))
    with c4: st.metric("🟢 Normal Transit",len(vessels)-len(at_risk)-len(diverting))

    m = folium.Map(location=[15,60], zoom_start=3, tiles="CartoDB Positron")
    STATUS_COLORS = {
        "TRANSITING":"#2e7d32","TRANSITING — ALT ROUTE":"#388e3c",
        "ANCHORED — AWAITING CLEARANCE":"#e65100","DELAYED — RISK ASSESSMENT":"#c62828",
        "DIVERTING — CAPE ROUTE":"#f57f17","APPROACHING PORT":"#1976d2",
    }
    for ck,cc,ccol,clbl in [
        ("strait_of_hormuz",[26.57,56.25],"#c62828","Hormuz HRA"),
        ("red_sea",[14.5,43.0],"#c62828","Red Sea HRA"),
        ("gulf_of_guinea",[2.5,2.5],"#e65100","Gulf of Guinea HRA"),
        ("cape_of_good_hope",[-34.36,18.48],"#2e7d32","Cape Alt Route"),
    ]:
        folium.CircleMarker(cc,radius=30,color=ccol,fill=True,fill_opacity=0.1,weight=2,popup=clbl).add_to(m)
    for r in INDIA_REFINERIES:
        folium.CircleMarker([r["lat"],r["lon"]],radius=7,color="#0d6e6e",fill=True,
            fill_opacity=0.8,popup=f"🏭 {r['name']}").add_to(m)
    for v in vessels:
        col2 = STATUS_COLORS.get(v["status"],"#888")
        folium.CircleMarker([v["lat"],v["lon"]],radius=9,color=col2,fill=True,fill_opacity=0.9,
            popup=f"<b>{v['name']}</b><br>{v['type']}<br>{v['cargo']}<br><b>{v['status']}</b><br>→{v['destination']}",
            tooltip=v['name']).add_to(m)
    st_folium(m, width=None, height=480)

    hdr("📋 Vessel Feed")
    df = pd.DataFrame([{
        "Vessel":f"{v['icon']} {v['name']}","Type":v["type"],"Flag":v["flag"],
        "Cargo":v["cargo"],"Status":v["status"],"Destination":v["destination"],"ETA (days)":v.get("eta_days","—"),
    } for v in vessels])
    st.dataframe(df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════
# PROCUREMENT ENGINE
# ══════════════════════════════════════════
elif page == "🛒 Procurement Engine":
    hdr("🛒 Adaptive Procurement Orchestrator")
    c1,c2 = st.columns(2)
    with c1: gap = st.slider("Supply Gap to Fill (MBPD)",0.1,3.0,1.2,0.1)
    with c2: sc_name = st.selectbox("Disruption Context",[
        "Strait of Hormuz — 40% Reduction","Red Sea Full Suspension",
        "OPEC+ Emergency Cut","Dual Corridor Crisis"])

    if st.button("▶ Generate Procurement Plan",use_container_width=True):
        with st.spinner("🤖 Procurement Agent ranking alternative sources with Claude AI..."):
            try:
                result = procurement_agent.run(gap, sc_name)
                st.session_state["proc"] = result
            except Exception as e:
                st.error(f"Error: {e}. Check ANTHROPIC_API_KEY in .env")

    if "proc" in st.session_state:
        r = st.session_state["proc"]
        if "error" not in r:
            c1,c2,c3 = st.columns(3)
            with c1: st.metric("Gap to Fill",f"{r['_meta']['supply_gap_mbpd']:.1f} MBPD")
            with c2: st.metric("Covered",f"{r.get('total_gap_covered_mbpd',0):.1f} MBPD")
            with c3:
                res = r.get("residual_gap_mbpd",0)
                st.metric("Residual",f"{res:.2f} MBPD","✅ Covered" if res<=0 else f"⚠️ {res:.2f} uncovered")

            hdr("🌍 Ranked Alternative Sources")
            for alt in r.get("ranked_alternatives",[]):
                conf = alt.get("confidence_score",70)
                with st.expander(f"#{alt.get('rank','?')} {alt.get('country','?')} — {alt.get('grade','?')} | {alt.get('recommended_volume_mbpd',0):.2f} MBPD | {conf}% confidence"):
                    ca,cb2,cc2,cd = st.columns(4)
                    with ca: st.metric("Volume",f"{alt.get('recommended_volume_mbpd',0):.2f} MBPD")
                    with cb2: st.metric("Mechanism",alt.get("procurement_mechanism","SPOT"))
                    with cc2: st.metric("Transit",f"{alt.get('transit_days_to_india','?')}d")
                    with cd: st.metric("Cost/bbl",f"${alt.get('total_cost_usd_per_barrel',0):.1f}")
                    st.markdown(f"**Price vs Brent:** {alt.get('estimated_price_vs_brent','—')}")
                    st.markdown(f"**Compatible Refineries:** {', '.join(alt.get('grade_compatible_refineries',[]))}")
                    st.markdown(f"**⚡ Action Required:** {alt.get('action_required','')}")

            hdr("⚡ 48-Hour Action Plan")
            for act in r.get("immediate_actions_48h",[]):
                st.markdown(f"**[{act.get('priority','?')}]** {act.get('action','')} — `{act.get('owner','')}` · {act.get('deadline','')}")

            spr_rec = r.get("spr_drawdown_recommendation",{})
            if spr_rec.get("initiate"):
                st.warning(f"🛢️ SPR Drawdown Recommended: {spr_rec.get('daily_drawdown_mbpd',0):.2f} MBPD — {spr_rec.get('rationale','')}")

            st.info(r.get("executive_summary",""))
        else:
            st.error(f"Error: {r.get('error')}. Check ANTHROPIC_API_KEY in .env")


# ══════════════════════════════════════════
# SPR OPTIMISER
# ══════════════════════════════════════════
elif page == "🛢️ SPR Optimiser":
    hdr("🛢️ Strategic Petroleum Reserve Optimiser")

    fig_spr = go.Figure()
    for site in SPR_SITES:
        filled = site["capacity_MMbbl"]*site["current_fill_pct"]/100
        empty  = site["capacity_MMbbl"]-filled
        fig_spr.add_trace(go.Bar(name=f"{site['name']} Filled",x=[site["name"]],y=[filled],marker_color="#0d6e6e"))
        fig_spr.add_trace(go.Bar(name=f"{site['name']} Empty",x=[site["name"]],y=[empty],marker_color="#e2e8f0"))
    fig_spr.update_layout(barmode="stack",paper_bgcolor="#fff",plot_bgcolor="#fff",
        title="SPR Site Levels (Million Barrels)",height=260,margin=dict(l=0,r=0,t=40,b=0),showlegend=False)
    st.plotly_chart(fig_spr, use_container_width=True)

    c1,c2,c3 = st.columns(3)
    with c1: gap  = st.number_input("Supply Gap (MBPD)",0.1,5.0,1.5,0.1)
    with c2: dur  = st.slider("Duration (days)",7,180,45)
    with c3: sc_n = st.selectbox("Scenario",["Hormuz Partial Closure","Red Sea Suspension","OPEC Emergency Cut"])

    if st.button("▶ Optimise SPR Strategy",use_container_width=True):
        with st.spinner("🤖 SPR Optimiser computing drawdown strategy with Claude AI..."):
            try:
                result = spr_optimiser.run(gap, dur, sc_n)
                st.session_state["spr"] = result
            except Exception as e:
                st.error(f"Error: {e}. Check ANTHROPIC_API_KEY in .env")

    if "spr" in st.session_state:
        r = st.session_state["spr"]
        if "error" not in r:
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("SPR Available",f"{r.get('spr_total_available_mmbbls',0):.0f} MMbbl")
            with c2: st.metric("Cover",f"{r.get('spr_cover_days_current',9.5):.1f} days")
            with c3: st.metric("Strategy",r.get("recommended_drawdown_strategy","—"))
            with c4: st.metric("Daily Drawdown",f"{r.get('daily_drawdown_mbpd',0):.2f} MBPD")

            hdr("🏭 By-Site Plan")
            for site in r.get("by_site",[]):
                pc = {"PRIMARY":"#c62828","SECONDARY":"#e65100","RESERVE":"#2e7d32"}.get(site.get("priority",""),"#888")
                st.markdown(f"""<div style="border-left:4px solid {pc};padding:10px 14px;background:#fff;
                    border-radius:0 6px 6px 0;margin-bottom:6px;box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                    <b style="color:{pc};">[{site.get('priority','?')}]</b>
                    <b> {site.get('site','?')}</b> — {site.get('drawdown_mbpd',0):.2f} MBPD<br>
                    <span style="font-size:11px;color:#666;">{site.get('rationale','')}</span>
                </div>""", unsafe_allow_html=True)

            rep = r.get("replenishment_window",{})
            if rep:
                hdr("🔄 Replenishment Strategy")
                rc1,rc2,rc3 = st.columns(3)
                with rc1: st.metric("Start From",f"Day {rep.get('earliest_start_days_from_now','?')}")
                with rc2: st.metric("Target Price",f"${rep.get('optimal_brent_replenishment_price',75):.0f}/bbl")
                with rc3: st.metric("Cost",f"${rep.get('estimated_replenishment_cost_usd_bn',0):.1f}Bn")

            iea = r.get("iea_coordination",{})
            if iea.get("recommended"):
                st.success(f"🌐 IEA coordination recommended — Est. +{iea.get('estimated_iea_contribution_mbpd',0):.1f} MBPD from members")

            st.info(r.get("executive_recommendation",""))
        else:
            st.error(f"Error: {r.get('error')}. Check ANTHROPIC_API_KEY in .env")
