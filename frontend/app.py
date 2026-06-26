"""
MERIDIAN — Maritime Intelligence Platform
Professional vessel intelligence, voyage risk, and energy supply-chain resilience.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import os, sys, tempfile
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    CORRIDORS, INDIA_REFINERIES, SPR_SITES, ALL_API_COUNT, BRAND_NAME, BRAND_TAGLINE,
)
from utils.live_data import (
    get_live_commodity_prices, get_brent_history_live, get_tanker_rates_live,
    get_live_news, get_port_intelligence, get_route_weather, check_sanctions_live,
    get_fx_rates, get_gdelt_news, get_vessel_track_history,
)
from agents import geo_sentinel, scenario_modeller, procurement_agent, spr_optimiser, ais_tracker, vessel_intel
from utils.vra_pdf import generate_vra_pdf

st.set_page_config(page_title="Meridian Maritime Intelligence", page_icon="🧭",
                   layout="wide", initial_sidebar_state="expanded")

# ── THEME ──
st.markdown("""<style>
.stApp{background:#eef2f7;color:#0f1c2e;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0a1628,#0f2440);}
[data-testid="stSidebar"] *{color:#dce8f5 !important;}
.block-container{padding-top:1.5rem;}
.mhdr{background:linear-gradient(90deg,#1a3a5c,#0d2438);color:#fff !important;padding:9px 18px;border-radius:7px;font-size:13px;font-weight:700;letter-spacing:.6px;margin-bottom:14px;box-shadow:0 2px 6px rgba(0,0,0,0.1);}
.card{background:#fff;border-radius:11px;padding:16px 20px;border:1px solid #dde5ee;margin-bottom:12px;box-shadow:0 2px 10px rgba(15,28,46,0.06);}
.gold{background:linear-gradient(135deg,#fdf8ec,#faf2dc);border-radius:11px;padding:15px 19px;border:1px solid #cda94e;margin-bottom:12px;}
.news-row{border-left:3px solid #1a3a5c;padding:9px 13px;background:#fff;border-radius:0 7px 7px 0;margin-bottom:7px;box-shadow:0 1px 4px rgba(0,0,0,0.05);}
.vcard{background:#fff;border-radius:9px;border:1px solid #dde5ee;padding:11px 15px;margin-bottom:7px;box-shadow:0 1px 4px rgba(0,0,0,0.05);}
.badge-critical{background:#8b0000;color:#fff;padding:2px 10px;border-radius:11px;font-size:10px;font-weight:700;}
.badge-high{background:#c62828;color:#fff;padding:2px 10px;border-radius:11px;font-size:10px;font-weight:700;}
.badge-elevated{background:#e65100;color:#fff;padding:2px 10px;border-radius:11px;font-size:10px;font-weight:700;}
.badge-moderate{background:#ef9a00;color:#fff;padding:2px 10px;border-radius:11px;font-size:10px;font-weight:700;}
.badge-low{background:#2e7d32;color:#fff;padding:2px 10px;border-radius:11px;font-size:10px;font-weight:700;}
[data-testid="metric-container"]{background:#fff;border:1px solid #dde5ee;border-radius:9px;padding:11px;box-shadow:0 1px 5px rgba(0,0,0,0.05);}
.stButton>button{background:linear-gradient(135deg,#1a3a5c,#0d2438);color:#fff;border:none;border-radius:7px;font-weight:600;padding:9px 16px;}
.stButton>button:hover{opacity:.92;}
.stDownloadButton>button{background:linear-gradient(135deg,#cda94e,#a8842f);color:#fff;border:none;border-radius:7px;font-weight:700;}
.pill{display:inline-block;background:#e8f0f8;color:#1a3a5c;padding:3px 10px;border-radius:12px;font-size:10px;font-weight:600;margin:2px;}
</style>""", unsafe_allow_html=True)

RC={"CRITICAL":"#8b0000","HIGH":"#c62828","ELEVATED":"#e65100","MODERATE":"#ef9a00","LOW":"#2e7d32"}
BGc={"CRITICAL":"#fdecea","HIGH":"#fde8e8","ELEVATED":"#fff3e6","MODERATE":"#fff9e6","LOW":"#e9f6ea"}
def badge(l):
    c={"CRITICAL":"badge-critical","HIGH":"badge-high","ELEVATED":"badge-elevated","MODERATE":"badge-moderate","LOW":"badge-low"}.get(l,"badge-moderate")
    return f'<span class="{c}">{l}</span>'
def hdr(t): st.markdown(f'<div class="mhdr">{t}</div>',unsafe_allow_html=True)

prices=get_live_commodity_prices()
brent=prices.get("brent_crude",{}); bp=brent.get("price",87.4); bc=brent.get("change_pct",0)
wti=prices.get("wti_crude",{})
fx=get_fx_rates()
tankers=get_tanker_rates_live()

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## 🧭 MERIDIAN")
    st.markdown("**Maritime Intelligence Platform**")
    st.markdown("---")
    page=st.radio("",[
        "📊 Command Centre",
        "🔎 Vessel Lookup",
        "🛡️ Voyage Risk Assessment",
        "🌍 Corridor Risk Intelligence",
        "📉 Disruption Scenarios",
        "🚢 Fleet AIS Tracker",
        "🛒 Procurement Engine",
        "🛢️ Strategic Reserve",
        "🔌 API Status",
    ],label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**Live Markets**")
    ar="▲" if bc>=0 else "▼"; cl="#5fd97f" if bc>=0 else "#ff7b7b"
    st.markdown(f"<div style='font-size:11px;color:#9bb3cc;'>BRENT CRUDE</div>"
                f"<div style='font-size:21px;font-weight:800;color:#fff;'>${bp}</div>"
                f"<div style='color:{cl};font-size:12px;'>{ar} {abs(bc):.1f}%</div>",unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:11px;color:#9bb3cc;margin-top:6px;'>WTI ${wti.get('price','—')} · USD/INR ₹{fx.get('USD_INR','—')}</div>",unsafe_allow_html=True)
    st.caption(f"Source: {brent.get('source','—')}")
    st.markdown("---")
    st.markdown("**Strategic Reserve**")
    st.progress(0.88,text="88% · 9.5 days cover")
    st.markdown("---")
    st.markdown(f"<div class='pill'>🔌 {ALL_API_COUNT} APIs</div><div class='pill'>🤖 Claude AI</div><div class='pill'>📡 Live AIS</div>",unsafe_allow_html=True)
    st.caption("© Meridian Maritime Intelligence")

# ── HEADER ──
st.markdown(f"""<div style="background:linear-gradient(135deg,#0a1628,#1a3a5c);border-radius:13px;
    padding:20px 28px;margin-bottom:20px;display:flex;align-items:center;gap:16px;">
  <div style="font-size:36px;">🧭</div>
  <div>
    <div style="font-size:23px;font-weight:800;color:#fff;letter-spacing:1.5px;">MERIDIAN</div>
    <div style="font-size:12px;color:rgba(255,255,255,0.65);">Maritime Intelligence Platform · Vessel Tracking · Voyage Risk · Energy Resilience</div>
  </div>
  <div style="margin-left:auto;text-align:right;">
    <div style="font-size:10px;color:rgba(255,255,255,0.5);">● LIVE · {ALL_API_COUNT} DATA SOURCES</div>
    <div style="font-size:13px;color:#cda94e;font-weight:700;">{datetime.utcnow().strftime('%d %b %Y · %H:%M')} UTC</div>
  </div>
</div>""",unsafe_allow_html=True)


# ════════ COMMAND CENTRE ════════
if page=="📊 Command Centre":
    c=st.columns(6)
    c[0].metric("🛢️ India Imports","5.1 MBPD")
    c[1].metric("⚠️ Hormuz Dep.","42%")
    c[2].metric("🔴 Red Sea","HIGH")
    c[3].metric("🏛️ SPR Cover","9.5 days")
    c[4].metric("💰 Brent",f"${bp}",f"{'+' if bc>=0 else ''}{bc:.1f}%")
    c[5].metric("💱 USD/INR",f"₹{fx.get('USD_INR','—')}")
    st.markdown("---")
    cl1,cl2=st.columns([3,2])
    with cl1:
        hdr("📈 BRENT CRUDE · 90-DAY LIVE PRICE HISTORY")
        df=get_brent_history_live(90)
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=df.index,y=df["brent_usd"],fill="tozeroy",
            fillcolor="rgba(26,58,92,0.1)",line=dict(color="#1a3a5c",width=2.5)))
        fig.add_vline(x=df.index[-15],line_dash="dash",line_color="#c62828",annotation_text="Hormuz",annotation_font_size=9)
        fig.add_vline(x=df.index[-30],line_dash="dot",line_color="#e65100",annotation_text="Houthi strike",annotation_font_size=9)
        fig.update_layout(paper_bgcolor="#fff",plot_bgcolor="#fff",font_color="#0f1c2e",height=270,
            margin=dict(l=0,r=0,t=20,b=0),xaxis=dict(gridcolor="#eef2f7"),yaxis=dict(gridcolor="#eef2f7",title="USD/bbl"),showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
    with cl2:
        hdr("🌐 CORRIDOR RISK INDEX")
        sc={"Hormuz":78,"Red Sea":85,"G. of Guinea":65,"Malacca":40,"Cape":22}
        fig2=go.Figure(go.Bar(x=list(sc.values()),y=list(sc.keys()),orientation="h",
            marker_color=["#c62828","#8b0000","#e65100","#ef9a00","#2e7d32"],
            text=[f"{v}" for v in sc.values()],textposition="outside"))
        fig2.update_layout(paper_bgcolor="#fff",plot_bgcolor="#fff",font_color="#0f1c2e",height=270,
            margin=dict(l=0,r=40,t=20,b=0),xaxis=dict(range=[0,110],showticklabels=False,showgrid=False),yaxis=dict(gridcolor="#eef2f7"))
        st.plotly_chart(fig2,use_container_width=True)
    st.markdown("---")
    cl3,cl4=st.columns([3,2])
    with cl3:
        hdr("📰 LIVE GEOPOLITICAL INTELLIGENCE")
        news=get_gdelt_news(7) or get_live_news(7)
        for h in news:
            rs=h.get("risk_score",50)
            b=badge("HIGH" if rs>=75 else "ELEVATED" if rs>=60 else "MODERATE" if rs>=45 else "LOW")
            st.markdown(f"""<div class="news-row"><div style="display:flex;justify-content:space-between;gap:8px;">
                <div style="font-size:13px;font-weight:600;flex:1;">{h['title'][:110]}</div><div>{b}</div></div>
                <div style="font-size:10px;color:#8090a0;margin-top:3px;">{h['source']} · {h['published']}</div></div>""",unsafe_allow_html=True)
    with cl4:
        hdr("🚨 VESSELS AT RISK")
        for v in ais_tracker.get_at_risk_vessels():
            st.markdown(f"""<div class="vcard"><div style="font-size:13px;font-weight:700;color:#1a3a5c;">{v['icon']} {v['name']}</div>
                <div style="font-size:11px;color:#667;">{v['type']} · {v['cargo'][:28]}</div>
                <div style="font-size:11px;color:#c62828;font-weight:600;">⚠ {v['status']}</div></div>""",unsafe_allow_html=True)
        hdr("🌊 PORT INCIDENTS")
        for inc in get_port_intelligence()[:3]:
            st.markdown(f"""<div style="border-left:3px solid #e65100;padding:6px 10px;background:#fff;border-radius:0 5px 5px 0;margin-bottom:5px;">
                <div style="font-size:11px;font-weight:600;">{inc['title'][:60]}</div>
                <div style="font-size:10px;color:#8090a0;">{inc['source']} · {inc['published']}</div></div>""",unsafe_allow_html=True)


# ════════ VESSEL LOOKUP ════════
elif page=="🔎 Vessel Lookup":
    st.markdown("""<div class="gold"><div style="display:flex;align-items:center;gap:12px;">
        <div style="font-size:28px;">🔎</div><div>
        <div style="font-size:15px;font-weight:800;color:#1a3a5c;">Universal Vessel Lookup</div>
        <div style="font-size:11px;color:#667;">Enter ANY IMO, MMSI, or vessel name. Live AIS data across 8 providers with deep particulars, position, compliance and carbon intelligence.</div>
        </div></div></div>""",unsafe_allow_html=True)
    cs,cb=st.columns([5,1])
    with cs:
        q=st.text_input("",placeholder="IMO (e.g. 9839131) · MMSI · or vessel name (e.g. MAERSK)",label_visibility="collapsed")
    with cb:
        go_s=st.button("🔍 Lookup",use_container_width=True)
    st.markdown("**Demo fleet:**")
    fleet=vessel_intel.get_demo_fleet()
    fcols=st.columns(len(fleet))
    for i,v in enumerate(fleet):
        if fcols[i].button(v["name"].replace("MV ","").replace("MT ","")[:13],key=f"vl{i}",use_container_width=True):
            st.session_state["vl"]=v
    if go_s and q:
        found=vessel_intel.lookup_vessel(q)
        if found: st.session_state["vl"]=found
        else: st.error(f"No vessel found for '{q}'.")
    if "vl" in st.session_state:
        v=st.session_state["vl"]; risk=v.get("_risk",vessel_intel.quick_risk_score(v))
        rc=RC.get(risk["level"],"#e65100"); icon=v.get("_icon","🚢")
        if v.get("_synthesised"):
            st.warning("⚠️ No live AIS key configured — showing a synthesised profile. Add VESSELAPI_KEY (free at vesselapi.com) in .env for real data on any IMO.")
        st.markdown(f"""<div style="background:linear-gradient(135deg,#0a1628,#1a3a5c);border:2px solid {rc};
            border-radius:11px;padding:18px 22px;margin:12px 0;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div><div style="font-size:21px;font-weight:800;color:#fff;">{icon} {v['name']}</div>
                <div style="font-size:11px;color:#9bb3cc;margin-top:3px;">IMO {v['imo']} · MMSI {v.get('mmsi','—')} · {v['type']} · {v.get('flag','—')} · {v.get('dwt','—')} DWT · Built {v.get('built','—')}</div>
                <div style="font-size:12px;color:#b8c8da;margin-top:3px;">📍 {v.get('current_route') or v.get('destination','—')} · 📡 {v.get('_source','—')}</div></div>
                <div style="background:{rc};padding:12px 20px;border-radius:9px;text-align:center;min-width:88px;">
                <div style="font-size:9px;color:rgba(255,255,255,0.85);">RISK</div>
                <div style="font-size:30px;font-weight:900;color:#fff;line-height:1;">{risk['score']}</div>
                <div style="font-size:11px;color:#fff;font-weight:700;">{risk['level']}</div></div></div></div>""",unsafe_allow_html=True)
        mc=st.columns(6)
        mc[0].metric("⚡ Speed",f"{v.get('speed_kts','—')} kt")
        mc[1].metric("🧭 Heading",f"{v.get('heading','—')}°")
        mc[2].metric("⚓ Draught",f"{v.get('draught','—')} m")
        mc[3].metric("📏 LOA",f"{v.get('loa','—')} m")
        mc[4].metric("🏷️ Class",v.get('class_society','—')[:10])
        mc[5].metric("🌱 CII",v.get('cii_rating','—'))
        t1,t2,t3,t4,t5=st.tabs(["📍 Position & Track","📋 Particulars","🌊 Weather","🔒 Compliance","🌱 Carbon"])
        with t1:
            vm=folium.Map(location=[v["lat"],v["lon"]],zoom_start=5,tiles="CartoDB Positron")
            track=get_vessel_track_history(v["imo"],v["lat"],v["lon"])
            folium.PolyLine(track,color=rc,weight=2.5,opacity=0.6,dash_array="5").add_to(vm)
            for ck,cc,col,lb in [("strait_of_hormuz",[26.57,56.25],"#c62828","Hormuz HRA"),("red_sea",[14.5,43.0],"#c62828","Red Sea HRA"),("gulf_of_guinea",[2.5,2.5],"#e65100","G.Guinea HRA"),("arabian_sea",[18,64],"#1976d2","Arabian Sea")]:
                folium.CircleMarker(cc,radius=28,color=col,fill=True,fill_opacity=0.07,weight=2,popup=lb).add_to(vm)
            for r in INDIA_REFINERIES:
                folium.CircleMarker([r["lat"],r["lon"]],radius=6,color="#1a3a5c",fill=True,fill_opacity=0.8,popup=f"🏭 {r['name']}").add_to(vm)
            folium.Marker([v["lat"],v["lon"]],icon=folium.DivIcon(html=f'<div style="font-size:22px;">{icon}</div>'),popup=f"<b>{v['name']}</b><br>{v.get('status','')}").add_to(vm)
            folium.CircleMarker([v["lat"],v["lon"]],radius=11,color=rc,fill=True,fill_opacity=0.4).add_to(vm)
            st_folium(vm,width=None,height=420,key="vlmap")
            st.caption(f"Dashed line = simulated 24h track · 🏭 = Indian refineries · Shaded zones = High Risk Areas")
        with t2:
            pc=st.columns(2)
            with pc[0]:
                st.markdown(f"""**Identity**
- IMO: `{v.get('imo','—')}`
- MMSI: `{v.get('mmsi','—')}`
- Call Sign: `{v.get('callsign','—')}`
- Name: **{v.get('name','—')}**
- Flag: {v.get('flag','—')}
- Type: {v.get('type','—')}""")
            with pc[1]:
                st.markdown(f"""**Dimensions & Ownership**
- DWT: {v.get('dwt','—')} t
- GT: {v.get('gt','—')} t
- LOA × Beam: {v.get('loa','—')} × {v.get('beam','—')} m
- Built: {v.get('built','—')}
- Owner: {v.get('owner','—')}
- Manager: {v.get('manager','—')}
- Class: {v.get('class_society','—')}""")
        with t3:
            wx=get_route_weather(float(v.get("lat") or 15),float(v.get("lon") or 60))
            wc=st.columns(4)
            wc[0].metric("🌊 Wave Ht",f"{wx.get('wave_height_m','—')} m")
            wc[1].metric("⏱ Period",f"{wx.get('wave_period_s','—')} s")
            wc[2].metric("💨 Wind",f"{wx.get('wind_speed_kts','—')} kt")
            wc[3].metric("🌊 Sea State",wx.get('sea_state','—'))
            st.caption(f"📡 {wx.get('source','—')} · {wx.get('_ts','')[:16]} UTC")
        with t4:
            sc=check_sanctions_live(v.get("imo",""),v.get("name",""))
            clear=sc.get("status","")=="CLEAR"; scol="#2e7d32" if clear else "#c62828"
            st.markdown(f"""<div style="background:{'#e9f6ea' if clear else '#fde8e8'};border:2px solid {scol};border-radius:9px;padding:16px 20px;">
                <div style="font-size:16px;font-weight:800;color:{scol};">{'✅ CLEAR' if clear else '🚨 '+sc.get('status','')}</div>
                <div style="margin-top:10px;font-size:11px;color:#445;">
                <b>Screened:</b> {', '.join(sc.get('screened_against',[]))}<br>
                <b>Flag risk:</b> {sc.get('flag_risk','—')}<br>
                <b>AIS history:</b> {sc.get('ais_gap_history','—')}<br>
                <b>Ownership opacity:</b> {sc.get('ownership_opacity','—')}</div></div>""",unsafe_allow_html=True)
        with t5:
            cii=v.get("cii_rating","C")
            ccolor={"A":"#2e7d32","B":"#7cb342","C":"#ef9a00","D":"#e65100","E":"#c62828"}.get(cii,"#ef9a00")
            cc=st.columns(2)
            with cc[0]:
                st.markdown(f"""<div style="text-align:center;padding:20px;background:#fff;border:2px solid {ccolor};border-radius:10px;">
                    <div style="font-size:11px;color:#667;">CII RATING (IMO)</div>
                    <div style="font-size:48px;font-weight:900;color:{ccolor};">{cii}</div>
                    <div style="font-size:11px;color:#667;">Carbon Intensity Indicator</div></div>""",unsafe_allow_html=True)
            with cc[1]:
                st.markdown(f"""**Environmental Profile**
- CII Rating: **{cii}** ({'Superior' if cii in 'AB' else 'Compliant' if cii=='C' else 'Action required'})
- EEXI: Compliant (estimated)
- Annual CO₂: ~{v.get('dwt',50000)//1000 * 12:,} t (estimated)
- IMO 2030 target: {'On track' if cii in 'ABC' else 'At risk'}
- Scrubber: {'Likely fitted' if v.get('built',2015)>=2018 else 'Verify'}""")
        st.markdown("---")
        if st.button("🛡️ Generate Voyage Risk Assessment for this vessel →",use_container_width=True,type="primary"):
            st.session_state["vra_vessel"]=v
            st.session_state["_goto_vra"]=True
            st.rerun()
    else:
        st.markdown("""<div style="background:#fff;border:2px dashed #cda94e;border-radius:11px;padding:40px;text-align:center;margin-top:18px;">
            <div style="font-size:46px;">🔎</div>
            <div style="font-size:16px;font-weight:700;color:#1a3a5c;margin-top:10px;">Look up any vessel worldwide</div>
            <div style="font-size:12px;color:#667;margin-top:6px;">IMO · MMSI · or name — deep particulars, live position, compliance & carbon intelligence</div></div>""",unsafe_allow_html=True)


# ════════ VOYAGE RISK ASSESSMENT ════════
elif page=="🛡️ Voyage Risk Assessment":
    hdr("🛡️ MERIDIAN VOYAGE RISK ASSESSMENT")
    src=st.session_state.get("vra_vessel") or st.session_state.get("vl")
    cs,cb=st.columns([5,1])
    with cs:
        q=st.text_input("",value=src["imo"] if src else "",placeholder="IMO / MMSI / name",label_visibility="collapsed")
    with cb:
        ld=st.button("Load",use_container_width=True)
    if ld and q:
        f=vessel_intel.lookup_vessel(q)
        if f: src=f; st.session_state["vra_vessel"]=f
    if src:
        v=src
        st.markdown(f"""<div class="card"><b style="font-size:15px;color:#1a3a5c;">{v.get('_icon','🚢')} {v['name']}</b>
            <span style="color:#667;font-size:12px;"> · IMO {v['imo']} · {v['type']} · {v.get('flag','')} · {v.get('current_route','')}</span></div>""",unsafe_allow_html=True)
        st.markdown("""<div class="gold" style="font-size:12px;">💡 <b>Professional deliverable.</b> AI-generated Meridian VRA — branded PDF, ready for charterers, P&I clubs, and war-risk underwriters. <b>Requires ANTHROPIC_API_KEY with credits.</b></div>""",unsafe_allow_html=True)
        if st.button("⚡ Generate Meridian VRA (Branded PDF)",use_container_width=True,type="primary"):
            with st.spinner("🤖 Meridian analyst generating assessment..."):
                try:
                    vra=vessel_intel.generate_vra(v); st.session_state["vra"]=vra
                except Exception as e:
                    st.error(f"Error: {e}")
        if "vra" in st.session_state:
            vra=st.session_state["vra"]
            if vra.get("overall_risk_rating"):
                rt=vra["overall_risk_rating"]; sc2=vra.get("risk_score",50)
                vc=RC.get(rt,"#e65100"); vb=BGc.get(rt,"#fff3e6")
                st.markdown(f"""<div style="background:{vb};border-left:5px solid {vc};border-radius:0 9px 9px 0;padding:15px 19px;margin:10px 0;">
                    <div style="font-size:14px;font-weight:800;color:{vc};">{vra.get('vessel_name','')} — {rt} ({sc2}/100)</div>
                    <div style="font-size:12px;color:#445;margin-top:6px;line-height:1.6;">{vra.get('executive_summary','')}</div></div>""",unsafe_allow_html=True)
                th=vra.get("threat_assessment",{})
                lbls={"piracy_armed_robbery":"Piracy","geopolitical_military":"Geo/Mil","drone_missile_threat":"Drone/Missile","gps_spoofing_jamming":"GPS Jam","sea_state_weather":"Weather"}
                tcols=st.columns(len(lbls))
                for i,(k,lb) in enumerate(lbls.items()):
                    if k in th:
                        lv=th[k].get("level","—"); lc=RC.get(lv,"#888"); lbg=BGc.get(lv,"#f5f5f5")
                        tcols[i].markdown(f"""<div style="text-align:center;padding:8px 4px;background:{lbg};border-radius:6px;border:1px solid {lc};">
                            <div style="font-size:9px;color:#667;font-weight:600;">{lb}</div>
                            <div style="font-size:11px;color:{lc};font-weight:800;margin-top:3px;">{lv}</div></div>""",unsafe_allow_html=True)
                pdf=os.path.join(tempfile.gettempdir(),f"Meridian_VRA_{v.get('imo','')}.pdf")
                try:
                    generate_vra_pdf(vra,pdf)
                    with open(pdf,"rb") as f:
                        st.download_button("⬇️ Download Meridian VRA (PDF)",f.read(),file_name=f"Meridian_VRA_{v['name'].replace(' ','_')}.pdf",mime="application/pdf",use_container_width=True)
                except Exception as e:
                    st.error(f"PDF error: {e}")
                with st.expander("📋 Full Assessment Detail"):
                    c1,c2=st.columns(2)
                    with c1:
                        st.markdown("**Recommendations**")
                        for r in vra.get("recommendations",[]): st.markdown(f"▸ {r}")
                        st.markdown("**Hardening (BMP5)**")
                        for h in vra.get("hardening_measures",[]): st.markdown(f"• {h}")
                    with c2:
                        st.markdown("**Chokepoints**")
                        for cp in vra.get("chokepoints",[]): st.markdown(f"**{cp.get('name','')}** [{cp.get('risk','')}] — {cp.get('advisory','')}")
                        st.markdown("**Reporting**")
                        for rr in vra.get("reporting_requirements",[]): st.markdown(f"• {rr}")
                    st.info(vra.get("insurance_note",""))
            elif "error" in vra:
                st.error(f"VRA failed: {vra['error']}")
    else:
        st.info("Look up a vessel first (🔎 Vessel Lookup) or enter an IMO above.")


# ════════ CORRIDOR RISK INTELLIGENCE ════════
elif page=="🌍 Corridor Risk Intelligence":
    hdr("🌍 GEOSENTINEL — LIVE CORRIDOR RISK ASSESSMENT")
    c1,c2=st.columns([1,3])
    with c1: run=st.button("▶ Run GeoSentinel",use_container_width=True)
    with c2: st.info("Fuses live news, commodity prices and AIS data to score corridor disruption risk using Claude AI.")
    if run:
        with st.spinner("🤖 Scanning intelligence feeds..."):
            try: st.session_state["geo"]=geo_sentinel.run()
            except Exception as e: st.error(f"Error: {e}")
    if "geo" in st.session_state:
        r=st.session_state["geo"]
        if "error" not in r:
            cc=st.columns(3)
            cc[0].metric("Overall Risk",r.get("overall_risk_level","—"))
            cc[1].metric("Composite",f"{r.get('overall_risk_score','—')}/100")
            cc[2].metric("Corridors","4")
            st.info(r.get("analyst_summary",""))
            cors=r.get("corridors",{})
            if cors:
                ccc=st.columns(len(cors))
                for i,(k,d) in enumerate(cors.items()):
                    s=d.get("risk_score",0); lv=d.get("risk_level","MODERATE"); col=RC.get(lv,"#888"); bgg=BGc.get(lv,"#f5f5f5")
                    ccc[i].markdown(f"""<div style="background:{bgg};border:2px solid {col};border-radius:8px;padding:13px;text-align:center;">
                        <div style="font-size:10px;color:#667;text-transform:uppercase;">{k.replace('_',' ')}</div>
                        <div style="font-size:30px;font-weight:900;color:{col};">{s}</div>
                        <div style="font-size:11px;color:{col};font-weight:700;">{lv}</div></div>""",unsafe_allow_html=True)
            for risk in r.get("top_3_risks",[]):
                with st.expander(f"#{risk['rank']} — {risk['risk']} ({risk.get('probability',50)}%)"):
                    st.write(risk.get("impact",""))
        else: st.error(f"Error: {r['error']}")


# ════════ DISRUPTION SCENARIOS ════════
elif page=="📉 Disruption Scenarios":
    hdr("📉 DISRUPTION SCENARIO INTELLIGENCE ENGINE")
    scs=scenario_modeller.get_all_scenarios()
    sk=st.selectbox("Scenario",list(scs.keys()),format_func=lambda k:f"{scs[k]['icon']} {scs[k]['name']}")
    sel=scs[sk]
    c1,c2=st.columns(2)
    c1.info(sel["description"]); c2.warning(f"Reduction: {sel['supply_reduction_pct']}% · Duration: {sel['duration_days']}d")
    if st.button(f"▶ Model: {sel['name']}",use_container_width=True):
        with st.spinner("🤖 Computing cascading impacts..."):
            try: st.session_state["sc"]=scenario_modeller.run(sk)
            except Exception as e: st.error(f"Error: {e}")
    if "sc" in st.session_state:
        r=st.session_state["sc"]
        if "error" not in r:
            cc=st.columns(4)
            cc[0].metric("Supply Gap",f"{r.get('india_supply_gap_mbpd',0):.2f} MBPD")
            cc[1].metric("Brent Spike",f"+{r.get('brent_price_spike_estimate_pct',0):.1f}%")
            cc[2].metric("Import Bill",f"+${r.get('india_import_bill_increase_usd_bn_monthly',0):.1f}Bn/mo")
            cc[3].metric("GDP",f"{r.get('gdp_impact_annualised_pct',0):.2f}%")
            cc=st.columns(4)
            cc[0].metric("Petrol",f"+₹{r.get('petrol_price_impact_inr_per_litre',0):.1f}/L")
            cc[1].metric("Diesel",f"+₹{r.get('diesel_price_impact_inr_per_litre',0):.1f}/L")
            cc[2].metric("SPR Cover",f"{r.get('spr_cover_days',9.5):.1f}d")
            cc[3].metric("Power",r.get("power_sector_stress_level","—"))
            cl,cr=st.columns(2)
            with cl:
                hdr("⏱ RESPONSE TIMELINE")
                for ev in r.get("response_timeline",[]):
                    st.markdown(f"""<div style="display:flex;gap:10px;margin-bottom:8px;">
                        <div style="background:#1a3a5c;color:#fff;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:700;white-space:nowrap;">Day {ev.get('day','?')}</div>
                        <div><b style="font-size:12px;">{ev.get('action','')}</b><br><span style="font-size:11px;color:#667;">{ev.get('impact','')}</span></div></div>""",unsafe_allow_html=True)
            with cr:
                hdr("🛡️ MITIGATIONS")
                for m in r.get("mitigation_recommendations",[]): st.markdown(f"✅ {m}")
                hdr("⚠️ VULNERABILITIES")
                for vv in r.get("key_vulnerabilities",[]): st.markdown(f"🔴 {vv}")
            st.info(r.get("scenario_narrative",""))
        else: st.error(f"Error: {r['error']}")


# ════════ FLEET AIS TRACKER ════════
elif page=="🚢 Fleet AIS Tracker":
    hdr("🚢 FLEET AIS TRACKER — INDIA SUPPLY CORRIDORS")
    vs=ais_tracker.get_live_vessels(); ar=ais_tracker.get_at_risk_vessels()
    dv=[v for v in vs if "DIVERTING" in v["status"] or "ALT ROUTE" in v["status"]]
    cc=st.columns(4)
    cc[0].metric("Tracked",len(vs)); cc[1].metric("⚠️ At Risk",len(ar))
    cc[2].metric("🔄 Rerouted",len(dv)); cc[3].metric("🟢 Normal",len(vs)-len(ar)-len(dv))
    m=folium.Map(location=[15,60],zoom_start=3,tiles="CartoDB Positron")
    SC={"TRANSITING":"#2e7d32","TRANSITING — ALT ROUTE":"#388e3c","ANCHORED — AWAITING CLEARANCE":"#e65100","DELAYED — RISK ASSESSMENT":"#c62828","DIVERTING — CAPE ROUTE":"#ef9a00","APPROACHING PORT":"#1976d2"}
    for ck,cc2,col,lb in [("hz",[26.57,56.25],"#c62828","Hormuz"),("rs",[14.5,43],"#c62828","Red Sea"),("gg",[2.5,2.5],"#e65100","G.Guinea"),("cp",[-34.36,18.48],"#2e7d32","Cape")]:
        folium.CircleMarker(cc2,radius=28,color=col,fill=True,fill_opacity=0.09,weight=2,popup=lb).add_to(m)
    for r in INDIA_REFINERIES:
        folium.CircleMarker([r["lat"],r["lon"]],radius=6,color="#1a3a5c",fill=True,fill_opacity=0.8,popup=f"🏭 {r['name']}").add_to(m)
    for v in vs:
        col=SC.get(v["status"],"#888")
        folium.CircleMarker([v["lat"],v["lon"]],radius=8,color=col,fill=True,fill_opacity=0.9,
            popup=f"<b>{v['name']}</b><br>{v['type']}<br>{v['cargo']}<br><b>{v['status']}</b>",tooltip=v['name']).add_to(m)
    st_folium(m,width=None,height=470)
    hdr("📋 VESSEL FEED")
    st.dataframe(pd.DataFrame([{"Vessel":f"{v['icon']} {v['name']}","Type":v["type"],"Flag":v["flag"],"Cargo":v["cargo"],"Status":v["status"],"Destination":v["destination"]} for v in vs]),use_container_width=True,hide_index=True)


# ════════ PROCUREMENT ════════
elif page=="🛒 Procurement Engine":
    hdr("🛒 ADAPTIVE PROCUREMENT ORCHESTRATOR")
    c1,c2=st.columns(2)
    gap=c1.slider("Supply Gap (MBPD)",0.1,3.0,1.2,0.1)
    scn=c2.selectbox("Context",["Strait of Hormuz — 40% Reduction","Red Sea Full Suspension","OPEC+ Emergency Cut","Dual Corridor Crisis"])
    if st.button("▶ Generate Procurement Plan",use_container_width=True):
        with st.spinner("🤖 Ranking alternative sources..."):
            try: st.session_state["proc"]=procurement_agent.run(gap,scn)
            except Exception as e: st.error(f"Error: {e}")
    if "proc" in st.session_state:
        r=st.session_state["proc"]
        if "error" not in r:
            cc=st.columns(3)
            cc[0].metric("Gap",f"{r['_meta']['supply_gap_mbpd']:.1f} MBPD")
            cc[1].metric("Covered",f"{r.get('total_gap_covered_mbpd',0):.1f} MBPD")
            res=r.get("residual_gap_mbpd",0)
            cc[2].metric("Residual",f"{res:.2f}","✅" if res<=0 else "⚠️")
            hdr("🌍 RANKED SOURCES")
            for a in r.get("ranked_alternatives",[]):
                with st.expander(f"#{a.get('rank','?')} {a.get('country','?')} — {a.get('grade','?')} | {a.get('recommended_volume_mbpd',0):.2f} MBPD | {a.get('confidence_score',70)}%"):
                    x=st.columns(4)
                    x[0].metric("Volume",f"{a.get('recommended_volume_mbpd',0):.2f}")
                    x[1].metric("Mechanism",a.get("procurement_mechanism","SPOT"))
                    x[2].metric("Transit",f"{a.get('transit_days_to_india','?')}d")
                    x[3].metric("Cost",f"${a.get('total_cost_usd_per_barrel',0):.1f}")
                    st.markdown(f"**Refineries:** {', '.join(a.get('grade_compatible_refineries',[]))}")
                    st.markdown(f"**⚡ Action:** {a.get('action_required','')}")
            hdr("⚡ 48-HOUR ACTIONS")
            for ac in r.get("immediate_actions_48h",[]):
                st.markdown(f"**[{ac.get('priority','?')}]** {ac.get('action','')} — `{ac.get('owner','')}` · {ac.get('deadline','')}")
            st.info(r.get("executive_summary",""))
        else: st.error(f"Error: {r['error']}")


# ════════ SPR ════════
elif page=="🛢️ Strategic Reserve":
    hdr("🛢️ STRATEGIC PETROLEUM RESERVE OPTIMISER")
    fig=go.Figure()
    for s in SPR_SITES:
        fl=s["capacity_MMbbl"]*s["current_fill_pct"]/100
        fig.add_trace(go.Bar(name=s['name'],x=[s["name"]],y=[fl],marker_color="#1a3a5c"))
        fig.add_trace(go.Bar(name="",x=[s["name"]],y=[s["capacity_MMbbl"]-fl],marker_color="#dde5ee"))
    fig.update_layout(barmode="stack",paper_bgcolor="#fff",plot_bgcolor="#fff",title="SPR Levels (MMbbl)",height=250,margin=dict(l=0,r=0,t=40,b=0),showlegend=False)
    st.plotly_chart(fig,use_container_width=True)
    c=st.columns(3)
    gap=c[0].number_input("Gap (MBPD)",0.1,5.0,1.5,0.1)
    dur=c[1].slider("Duration (d)",7,180,45)
    scn=c[2].selectbox("Scenario",["Hormuz Partial Closure","Red Sea Suspension","OPEC Emergency Cut"])
    if st.button("▶ Optimise SPR Strategy",use_container_width=True):
        with st.spinner("🤖 Computing drawdown..."):
            try: st.session_state["spr"]=spr_optimiser.run(gap,dur,scn)
            except Exception as e: st.error(f"Error: {e}")
    if "spr" in st.session_state:
        r=st.session_state["spr"]
        if "error" not in r:
            cc=st.columns(4)
            cc[0].metric("Available",f"{r.get('spr_total_available_mmbbls',0):.0f} MMbbl")
            cc[1].metric("Cover",f"{r.get('spr_cover_days_current',9.5):.1f}d")
            cc[2].metric("Strategy",r.get("recommended_drawdown_strategy","—"))
            cc[3].metric("Rate",f"{r.get('daily_drawdown_mbpd',0):.2f} MBPD")
            hdr("🏭 BY-SITE PLAN")
            for s in r.get("by_site",[]):
                pc={"PRIMARY":"#c62828","SECONDARY":"#e65100","RESERVE":"#2e7d32"}.get(s.get("priority",""),"#888")
                st.markdown(f"""<div style="border-left:4px solid {pc};padding:10px 14px;background:#fff;border-radius:0 6px 6px 0;margin-bottom:6px;">
                    <b style="color:{pc};">[{s.get('priority','?')}]</b> <b>{s.get('site','?')}</b> — {s.get('drawdown_mbpd',0):.2f} MBPD<br>
                    <span style="font-size:11px;color:#667;">{s.get('rationale','')}</span></div>""",unsafe_allow_html=True)
            st.info(r.get("executive_recommendation",""))
        else: st.error(f"Error: {r['error']}")


# ════════ API STATUS ════════
elif page=="🔌 API Status":
    hdr(f"🔌 DATA SOURCE REGISTRY — {ALL_API_COUNT} APIS")
    from config.settings import (VESSEL_APIS,SANCTIONS_APIS,COMMODITY_APIS,WEATHER_APIS,PORT_APIS,NEWS_APIS,GEO_APIS,FX_APIS,FREIGHT_APIS,CARBON_APIS,
        VESSELAPI_KEY,AIS_API_KEY,NEWS_API_KEY,EIA_API_KEY)
    cats=[("🚢 Vessel / AIS Tracking",VESSEL_APIS,8),("🔒 Sanctions / Compliance",SANCTIONS_APIS,6),
        ("💰 Commodity / Markets",COMMODITY_APIS,7),("🌊 Weather / Metocean",WEATHER_APIS,5),
        ("⚓ Port / Incident Intel",PORT_APIS,6),("📰 News / Geopolitical",NEWS_APIS,4),
        ("🗺️ Geospatial / Mapping",GEO_APIS,3),("💱 Economic / FX",FX_APIS,3),
        ("🚛 Bunker / Freight",FREIGHT_APIS,6),("🌱 Carbon / Environmental",CARBON_APIS,4)]
    cols=st.columns(2)
    for i,(name,apis,cnt) in enumerate(cats):
        with cols[i%2]:
            rows=""
            for k,url in apis.items():
                free = any(x in str(url).lower() for x in ["openmeteo","gdelt","frankfurter","exchangerate","ofac","ec.europa","un.org","ukmto","icc","worldbank","carbonintensity","internal","naturalearth","openseamap"])
                status = "🟢 FREE" if free else "🔑 Key"
                rows+=f"<div style='display:flex;justify-content:space-between;font-size:11px;padding:3px 0;border-bottom:1px solid #f0f0f0;'><span>{k}</span><span>{status}</span></div>"
            st.markdown(f"""<div class="card"><div style="font-size:13px;font-weight:700;color:#1a3a5c;margin-bottom:6px;">{name} ({cnt})</div>{rows}</div>""",unsafe_allow_html=True)
    st.markdown("---")
    active=[("Anthropic Claude","🟢 Active" if os.getenv("ANTHROPIC_API_KEY") else "🔴 No key"),
            ("VesselAPI (live AIS)","🟢 Active" if VESSELAPI_KEY else "⚪ Add key for real IMO data"),
            ("NewsAPI","🟢 Active" if NEWS_API_KEY else "⚪ Optional"),
            ("EIA (US Gov oil data)","🟢 Active" if EIA_API_KEY else "⚪ Optional"),
            ("Open-Meteo Marine","🟢 Active (free)"),("OFAC Sanctions","🟢 Active (free)"),
            ("GDELT News","🟢 Active (free)"),("Frankfurter FX","🟢 Active (free)")]
    hdr("⚙️ CURRENTLY CONFIGURED")
    ac=st.columns(2)
    for i,(n,s) in enumerate(active):
        ac[i%2].markdown(f"<div style='background:#fff;border:1px solid #dde5ee;border-radius:7px;padding:8px 14px;margin-bottom:6px;font-size:12px;'><b>{n}</b> — {s}</div>",unsafe_allow_html=True)
