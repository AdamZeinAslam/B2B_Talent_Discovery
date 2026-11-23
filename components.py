from __future__ import annotations

import base64
import html
import math
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "vinix7_logo_centered.png"


def inject_styles() -> None:
    """Restrained VINIX7 enterprise styling and highly visible result tabs."""
    st.markdown(
        """
        <style>
        :root {
          --vinix-blue:#17428f; --vinix-blue-dark:#102c5c; --vinix-yellow:#f2d34f;
          --ink:#202b3c; --muted:#667386; --line:#dfe4eb; --paper:#f7f8fa; --surface:#ffffff;
        }
        .stApp { background:var(--paper); color:var(--ink); }
        [data-testid="stHeader"] { background:rgba(247,248,250,.96); }
        [data-testid="stSidebar"] { background:var(--surface); border-right:1px solid var(--line); }
        [data-testid="stSidebar"] > div { padding-top:1.2rem; }
        .sidebar-logo-wrap { width:100%; display:flex; align-items:center; justify-content:center; padding:8px 4px 12px; }
        .sidebar-logo-wrap img { display:block; width:min(210px, 86%); height:auto; object-fit:contain; margin:0 auto; }
        .sidebar-brand-caption { color:#748198; font-size:9px; letter-spacing:1.65px; font-weight:750; text-align:center; margin:2px 0 14px; }
        .eyebrow { color:var(--vinix-blue); text-transform:uppercase; letter-spacing:1.45px; font-size:10px; font-weight:800; margin:0 0 7px 0; }
        .page-title { color:var(--vinix-blue-dark); font-size:29px; line-height:1.18; letter-spacing:-.45px; font-weight:720; margin:0 0 7px 0; }
        .page-subtitle { color:var(--muted); font-size:13px; line-height:1.55; margin:0 0 20px 0; max-width:940px; }
        .section-title { color:var(--vinix-blue-dark); font-size:16px; font-weight:720; margin:0 0 4px 0; }
        .section-help { color:var(--muted); font-size:12px; line-height:1.5; margin-bottom:12px; }
        .small-label { color:#8993a2; font-size:9px; text-transform:uppercase; letter-spacing:1.3px; font-weight:800; }
        .step-card { background:transparent; border-left:3px solid var(--vinix-yellow); padding:5px 0 7px 11px; min-height:82px; }
        .step-number { color:var(--vinix-blue); font-size:10px; letter-spacing:1.2px; font-weight:850; margin-bottom:6px; }
        .step-title { color:var(--vinix-blue-dark); font-size:13px; font-weight:720; margin-bottom:3px; }
        .step-copy { color:var(--muted); font-size:11px; line-height:1.5; }
        .candidate-id { color:var(--vinix-blue); font-size:10px; font-weight:800; letter-spacing:1.1px; }
        .candidate-name { color:var(--vinix-blue-dark); font-size:17px; font-weight:720; margin:2px 0 4px 0; }
        div.stButton > button, div.stFormSubmitButton > button, .stDownloadButton > button { border-radius:6px; font-weight:650; min-height:40px; }
        div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] { background:var(--vinix-blue); border-color:var(--vinix-blue); color:#fff; }
        div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button[kind="primary"]:hover { background:#103575; border-color:#103575; }
        div[data-testid="stMetric"] { background:transparent; border:0; border-bottom:2px solid var(--vinix-yellow); border-radius:0; padding:5px 0 9px 0; }
        div[data-testid="stMetricLabel"] { color:var(--muted); font-size:11px; }
        div[data-testid="stMetricValue"] { color:var(--vinix-blue-dark); font-weight:740; }
        [data-testid="stVerticalBlockBorderWrapper"] { border-radius:7px; border-color:var(--line); background:var(--surface); }
        /* Result-method tabs: larger type, stronger contrast, visible active state. */
        .stTabs [data-baseweb="tab-list"] { gap:7px; border:1px solid #d5dce7; border-bottom:2px solid #c7d0de; border-radius:9px 9px 0 0; background:#fff; padding:5px 6px 0; }
        .stTabs [data-baseweb="tab"] { height:50px; font-size:14px !important; font-weight:700 !important; color:#344155 !important; padding:0 15px; border-radius:6px 6px 0 0; }
        .stTabs [data-baseweb="tab"][aria-selected="true"] { color:var(--vinix-blue) !important; background:#edf3ff !important; border-bottom:4px solid var(--vinix-yellow) !important; }
        .stTabs [data-baseweb="tab-highlight"] { background:var(--vinix-blue) !important; height:3px !important; }
        .stTabs [data-baseweb="tab-panel"] { padding-top:18px; }
        .chart-note { color:#718096; font-size:11px; line-height:1.45; margin-top:-4px; }
        .vinix-footer { color:#8490a0; font-size:10px; border-top:1px solid var(--line); padding-top:10px; margin-top:25px; }
        [data-testid="stDataFrame"] { border:1px solid var(--line); }
        hr { border-color:var(--line); }
        @media (max-width:700px) {
          .page-title{font-size:24px;} .page-subtitle{font-size:12px;}
          .stTabs [data-baseweb="tab"] {font-size:12px !important; padding:0 7px;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def brand_sidebar() -> None:
    if LOGO_PATH.exists():
        encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
        st.sidebar.markdown(
            f"<div class='sidebar-logo-wrap'><img src='data:image/png;base64,{encoded}' alt='VINIX7 logo'></div>",
            unsafe_allow_html=True,
        )
    st.sidebar.markdown("<div class='sidebar-brand-caption'>TALENT DISCOVERY PLATFORM</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div style='height:2px;background:#f2d34f;margin:0 0 16px 0;'></div>", unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="eyebrow">VINIX7&nbsp;&nbsp; / &nbsp;&nbsp;{html.escape(str(eyebrow))}</div>'
        f'<h1 class="page-title">{html.escape(str(title))}</h1>'
        f'<p class="page-subtitle">{html.escape(str(subtitle))}</p>',
        unsafe_allow_html=True,
    )


def section_heading(title: str, help_text: str = "") -> None:
    st.markdown(
        f'<div class="section-title">{html.escape(str(title))}</div>'
        f'<div class="section-help">{html.escape(str(help_text))}</div>',
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        "<div class='vinix-footer'>VINIX7 · Talent Discovery · Decision-support prototype for industry partners</div>",
        unsafe_allow_html=True,
    )


VISUAL_LAYER = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Instrument+Sans:wght@400;500;600;700&display=swap');
:root{
  --navy:#0a1e45; --navy2:#12356f; --blue:#173f91; --yellow:#f3d34a; --yellow-soft:#fdf4c9;
  --ink:#10213f; --muted:#5f6e87; --line:#dde3ee; --paper:#f3f5fa;
  --display:'Bricolage Grotesque','Instrument Sans',system-ui,sans-serif;
  --body:'Instrument Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
}
html,body,.stApp,[data-testid="stAppViewContainer"],button,input,textarea,select{font-family:var(--body)!important;}
.stApp{color:var(--ink);background-color:var(--paper);
  background-image:radial-gradient(#cdd6e6 1px,transparent 1px);background-size:24px 24px;}
[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:2.2rem;max-width:1180px;}
h1,h2,h3,.page-title,.hero2 h2,.metric-value,.strip-num{font-family:var(--display)!important;letter-spacing:-.02em;}
h3{color:var(--navy);font-weight:700;}

/* sidebar */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#fff 0%,#eef2fa 100%);border-right:1px solid var(--line);}
[data-testid="stSidebar"] .stButton>button{justify-content:flex-start;text-align:left;border:1px solid transparent;background:transparent;color:var(--ink);box-shadow:none;font-weight:600;min-height:44px;transition:background .15s,transform .15s;}
[data-testid="stSidebar"] .stButton>button:hover:not(:disabled){background:#e4eaf7;transform:translateX(3px);}
[data-testid="stSidebar"] .stButton>button[kind="primary"]{background:var(--navy);color:#fff;border-left:5px solid var(--yellow);box-shadow:0 8px 18px rgba(10,30,69,.22);}
[data-testid="stSidebar"] .stButton>button:disabled{opacity:.4;}
.sidebar-brand-caption{color:#71809a;font-size:11px;letter-spacing:.6px;font-weight:600;margin:2px 0 14px 4px;}
.small-label{color:#8591a3;font-size:11px;font-weight:700;letter-spacing:.4px;margin:6px 0 6px 2px;}

/* headings */
.eyebrow{display:flex;align-items:center;gap:9px;color:var(--blue);font-size:13px;font-weight:600;margin:0 0 10px;}
.eyebrow:before{content:"";width:18px;height:8px;border-radius:4px;background:var(--yellow);}
.page-title{color:var(--navy);font-size:42px;line-height:1.05;font-weight:800;margin:0 0 12px;max-width:820px;}
.page-subtitle{color:var(--muted);font-size:16px;line-height:1.65;margin:0 0 26px;max-width:760px;}
.section-title{color:var(--navy);font-family:var(--display);font-size:21px;font-weight:700;margin:0 0 4px;}
.section-help{color:var(--muted);font-size:13.5px;line-height:1.55;margin-bottom:14px;}

/* hero */
.hero2{position:relative;display:grid;grid-template-columns:1.1fr .9fr;gap:8px;align-items:center;overflow:hidden;
  background:radial-gradient(120% 140% at 85% 40%,#1c4aa3 0%,var(--navy2) 38%,var(--navy) 100%);
  border-radius:26px;padding:38px 40px;margin:6px 0 26px;box-shadow:0 24px 50px rgba(10,30,69,.28);}
.hero2:after{content:"";position:absolute;left:0;top:0;bottom:0;width:7px;background:var(--yellow);}
.hero2-kicker{display:inline-block;background:rgba(243,211,74,.14);color:var(--yellow);border:1px solid rgba(243,211,74,.4);padding:5px 12px;border-radius:99px;font-size:12.5px;font-weight:600;margin-bottom:16px;}
.hero2 h2{color:#fff;font-size:40px;line-height:1.06;font-weight:800;margin:0 0 14px;}
.hero2 p{color:#cfdcf3;font-size:15.5px;line-height:1.65;margin:0;max-width:470px;}
.hero2-viz{text-align:center;}
.hero2-cap{color:#9fb3d6;font-size:11.5px;margin-top:-6px;}
.legend{display:flex;gap:16px;justify-content:center;margin-top:6px;font-size:11.5px;color:#cfdcf3;}
.legend i{display:inline-block;width:14px;height:0;border-top:2px dashed #fff;vertical-align:middle;margin-right:6px;}
.legend i.c{border-top:6px solid var(--yellow);border-radius:3px;}

/* radar */
svg.rd{width:100%;height:auto;max-width:340px;overflow:visible;}
.rd .ring{fill:none;stroke:#cfd8e8;stroke-width:1;}
.rd .spoke{stroke:#d9e0ee;stroke-width:1;}
.rd text{font:600 11px var(--body);fill:#5f6e87;text-anchor:middle;dominant-baseline:middle;}
.rd .tgt{fill:rgba(23,63,145,.08);stroke:var(--blue);stroke-width:2;stroke-dasharray:5 4;}
.rd .cand{fill:rgba(243,211,74,.55);stroke:#c9a400;stroke-width:2;}
.rd .dot{fill:var(--blue);}
.rd.dark .ring,.rd.dark .spoke{stroke:rgba(255,255,255,.16);}
.rd.dark text{fill:#b9c9e6;}
.rd.dark .tgt{fill:rgba(255,255,255,.07);stroke:#fff;}
.rd.dark .cand{fill:rgba(243,211,74,.30);stroke:var(--yellow);}
.rd.dark .cand.c2{fill:rgba(120,170,255,.22);stroke:#8db4ff;}
.rd.dark .cand.c3{fill:rgba(255,255,255,.10);stroke:#e6eeff;stroke-width:1.5;}
.rd.anim .cand{animation:rdGrow 1.5s cubic-bezier(.2,.9,.2,1) both;transform-box:view-box;}
.rd.anim .cand.c2{animation-delay:.18s}.rd.anim .cand.c3{animation-delay:.36s}
@keyframes rdGrow{from{transform:scale(.25);opacity:0}to{transform:scale(1);opacity:1}}

/* strip, steps, weight bar */
.strip{display:grid;grid-template-columns:repeat(3,1fr);background:#fff;border:1px solid var(--line);border-radius:20px;box-shadow:0 10px 26px rgba(20,45,90,.06);margin-bottom:30px;}
.strip>div{padding:22px 26px;border-right:1px solid var(--line);}
.strip>div:last-child{border-right:0;}
.strip-label{color:var(--muted);font-size:13px;font-weight:600;}
.strip-num{color:var(--navy);font-size:44px;font-weight:800;line-height:1.1;margin:4px 0;font-variant-numeric:tabular-nums;}
.strip-note{color:#8792a4;font-size:12.5px;}
.flow{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin:6px 0 10px;}
.flow-step{position:relative;padding-top:50px;}
.flow-step:before{content:"";position:absolute;top:17px;left:38px;right:-18px;height:2px;background:repeating-linear-gradient(90deg,var(--blue) 0 6px,transparent 6px 11px);opacity:.45;}
.flow-step:last-child:before{display:none;}
.flow-step .step-number{position:absolute;top:0;left:0;margin:0;width:36px;height:36px;border-radius:50%;background:var(--navy);color:var(--yellow);font:800 14px var(--display);}
.wbar{display:flex;height:14px;border-radius:99px;overflow:hidden;background:#e5e9f1;margin:8px 0 8px;}
.wbar i{display:block;height:100%;}.wbar .p{background:var(--blue);}.wbar .k{background:var(--yellow);}
.wlegend{display:flex;justify-content:space-between;font-size:12.5px;color:var(--muted);font-weight:600;}
.wlegend b{color:var(--navy);}

/* cards & widgets */
.metric-card,.soft-panel,.step-card{background:#fff;border:1px solid var(--line);border-radius:18px;box-shadow:0 8px 22px rgba(20,45,90,.05);}
.metric-card{padding:18px 20px;min-height:112px;}
.metric-label{color:var(--muted);font-size:12.5px;font-weight:600;margin-bottom:8px;}
.metric-value{color:var(--navy);font-size:32px;font-weight:800;}
.metric-note{color:#8792a4;font-size:12px;margin-top:4px;}
.step-card{padding:18px;min-height:140px;border-left:5px solid var(--yellow);}
.step-number{display:inline-flex;width:30px;height:30px;border-radius:9px;background:var(--navy);color:var(--yellow);font:800 13px var(--display);align-items:center;justify-content:center;margin-bottom:12px;}
.step-title{color:var(--navy);font-family:var(--display);font-size:16px;font-weight:700;margin-bottom:5px;}
.step-copy,.note{color:var(--muted);font-size:13.5px;line-height:1.6;}
.candidate-id{display:inline-block;background:var(--yellow-soft);color:#6b5600;border-radius:8px;padding:3px 9px;font-size:12px;font-weight:700;letter-spacing:.5px;}
.candidate-name{color:var(--navy);font-family:var(--display);font-size:22px;font-weight:700;margin:6px 0 8px;}
div.stButton>button,div.stFormSubmitButton>button,.stDownloadButton>button{border-radius:12px;font-weight:700;min-height:46px;transition:transform .15s,box-shadow .15s;}
div.stButton>button:hover:not(:disabled),.stDownloadButton>button:hover{transform:translateY(-1px);}
div.stButton>button[kind="primary"],.stDownloadButton>button[kind="primary"]{background:linear-gradient(135deg,var(--blue),var(--navy2));border:0;color:#fff;box-shadow:0 10px 22px rgba(23,63,145,.32);}
div[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-left:5px solid var(--yellow);border-radius:14px;padding:14px 16px;box-shadow:0 6px 16px rgba(20,45,90,.04);}
div[data-testid="stMetricValue"]{font-family:var(--display)!important;color:var(--navy);font-weight:800;}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:20px;border-color:var(--line);background:#fff;box-shadow:0 10px 26px rgba(20,45,90,.05);}
[data-testid="stExpander"] details{border-radius:16px;border:1px solid var(--line);background:#fff;box-shadow:0 4px 12px rgba(20,45,90,.04);}
[data-testid="stExpander"] summary{font-weight:700;color:var(--navy);}
[data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="textarea"]{border-radius:12px!important;}
[data-baseweb="input"]:focus-within,[data-baseweb="select"]>div:focus-within{box-shadow:0 0 0 3px rgba(243,211,74,.55)!important;}
.stTabs [data-baseweb="tab-list"]{gap:22px;}
.stTabs [aria-selected="true"]{color:var(--navy);font-weight:700;}
.stTabs [data-baseweb="tab-highlight"]{background:var(--yellow);height:4px;border-radius:4px;}
.vinix-footer{color:#8691a3;font-size:12px;border-top:1px solid var(--line);padding-top:14px;margin-top:34px;}
@media (prefers-reduced-motion:reduce){.rd.anim .cand{animation:none;}}
@media (max-width:820px){.hero2{grid-template-columns:1fr;padding:28px 24px;}.hero2 h2{font-size:30px;}.page-title{font-size:31px;}
  .strip,.flow{grid-template-columns:1fr;}.strip>div{border-right:0;border-bottom:1px solid var(--line);}.flow-step:before{display:none;}}
.eyebrow,.sidebar-brand-caption,.small-label{text-transform:none!important;letter-spacing:0!important;}
.page-title{font-size:42px!important;}
</style>
"""


TAB_LAYER = """
<style>
/* ===== Method tabs: dark rail, big pill-cards, glowing yellow active state ===== */
.method-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin:30px 0 14px;}
.method-head .mh-eyebrow{display:flex;align-items:center;gap:9px;color:var(--blue);font-size:13px;font-weight:700;margin-bottom:6px;}
.method-head .mh-eyebrow:before{content:"";width:18px;height:8px;border-radius:4px;background:var(--yellow);}
.method-head h3{margin:0;padding:0;font-size:28px;line-height:1.1;color:var(--navy);font-weight:800;}
.method-head p{margin:6px 0 0;color:var(--muted);font-size:14px;max-width:560px;}
.method-head .mh-hint{flex:none;display:inline-flex;align-items:center;gap:8px;background:var(--yellow-soft);color:#6b5600;border:1px solid #efd96e;border-radius:99px;padding:7px 14px;font-size:12.5px;font-weight:700;}
.method-head .mh-hint:before{content:"";width:8px;height:8px;border-radius:50%;background:#e0b400;box-shadow:0 0 0 0 rgba(224,180,0,.6);animation:mhPulse 1.8s infinite;}
@keyframes mhPulse{0%{box-shadow:0 0 0 0 rgba(224,180,0,.55)}70%{box-shadow:0 0 0 9px rgba(224,180,0,0)}100%{box-shadow:0 0 0 0 rgba(224,180,0,0)}}

[role="tablist"]{
  position:relative;gap:10px;padding:10px;border:0;border-radius:24px;
  background:radial-gradient(120% 220% at 88% 0%,#1c4aa3 0%,var(--navy2) 40%,var(--navy) 100%);
  box-shadow:0 22px 44px rgba(10,30,69,.30),inset 0 1px 0 rgba(255,255,255,.12);
  overflow-x:auto;scrollbar-width:none;
}
[role="tablist"]::-webkit-scrollbar{display:none;}
[role="tablist"]:before{content:"";position:absolute;left:0;top:18px;bottom:18px;width:5px;border-radius:0 4px 4px 0;background:var(--yellow);}
.react-aria-SelectionIndicator,[data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none!important;}

[role="tab"]{
  flex:1 1 0;min-width:0;height:68px;padding:0 18px;border-radius:16px;
  background:rgba(255,255,255,.06)!important;border:1px solid rgba(255,255,255,.10)!important;border-bottom:1px solid rgba(255,255,255,.10)!important;
  color:#c9d7f2!important;
  transition:transform .22s cubic-bezier(.2,.9,.2,1),background .22s,box-shadow .22s,color .22s;
}
[role="tab"] p{
  display:flex;align-items:center;justify-content:center;gap:11px;margin:0;
  font-family:var(--display)!important;font-size:16.5px!important;font-weight:700!important;letter-spacing:-.01em;white-space:nowrap;
}
[role="tab"] p:before{
  content:"";flex:none;width:26px;height:26px;background-color:currentColor;
  -webkit-mask:var(--ico) center/contain no-repeat;mask:var(--ico) center/contain no-repeat;opacity:.95;
}
[role="tab"]:nth-child(1) p{--ico:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round'%3E%3Ccircle cx='12' cy='12' r='3' fill='black'/%3E%3Ccircle cx='5' cy='6' r='2'/%3E%3Ccircle cx='19' cy='7' r='2'/%3E%3Ccircle cx='6' cy='19' r='2'/%3E%3Ccircle cx='19' cy='18' r='2'/%3E%3Cpath d='M10 10 6.5 7.4M14 10.5l3.6-2.4M10 14l-2.6 3.6M14.2 13.8l3.4 2.9'/%3E%3C/svg%3E");}
[role="tab"]:nth-child(2) p{--ico:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='black'%3E%3Crect x='3' y='13' width='4.5' height='8' rx='1.2'/%3E%3Crect x='9.75' y='8' width='4.5' height='13' rx='1.2'/%3E%3Crect x='16.5' y='3' width='4.5' height='18' rx='1.2'/%3E%3C/svg%3E");}
[role="tab"]:nth-child(3) p{--ico:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 8h15M15 4l4 4-4 4M20 16H5M9 12l-4 4 4 4'/%3E%3C/svg%3E");}
[role="tab"]:nth-child(4) p{--ico:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 2.5 20 6v6c0 4.6-3.2 8.2-8 9.5C7.2 20.2 4 16.6 4 12V6z'/%3E%3Cpath d='m8.5 12 2.5 2.5 4.8-5'/%3E%3C/svg%3E");}

[role="tab"]:hover{background:rgba(255,255,255,.16)!important;color:#fff!important;transform:translateY(-3px);box-shadow:0 12px 22px rgba(0,0,0,.22);}
[role="tab"][aria-selected="true"]{
  background:linear-gradient(135deg,#ffe98a 0%,var(--yellow) 55%,#e9be1c 100%)!important;
  color:var(--navy)!important;border-color:#fff3b0!important;transform:translateY(-3px);
  box-shadow:0 14px 30px rgba(243,211,74,.45),0 0 0 4px rgba(243,211,74,.18),inset 0 1px 0 rgba(255,255,255,.7);
}
[role="tab"][aria-selected="true"] p{font-weight:800!important;}
[role="tab"][aria-selected="true"]:after{
  content:"";position:absolute;left:50%;bottom:-13px;width:18px;height:18px;margin-left:-9px;
  background:#e9be1c;transform:rotate(45deg);border-radius:3px;z-index:-1;
}
[role="tab"]:focus-visible{outline:3px solid #fff;outline-offset:2px;}

[role="tabpanel"]{padding-top:30px;animation:tabIn .45s cubic-bezier(.2,.9,.2,1) both;}
@keyframes tabIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}

@media (max-width:820px){
  .method-head{flex-direction:column;align-items:flex-start;}
  .method-head h3{font-size:23px;}
  [role="tablist"]{padding:8px;gap:8px;border-radius:20px;}
  [role="tab"]{flex:0 0 auto;min-width:150px;height:58px;padding:0 14px;}
  [role="tab"] p{font-size:14.5px!important;}
  [role="tab"] p:before{width:20px;height:20px;}
}
@media (prefers-reduced-motion:reduce){
  [role="tabpanel"],.method-head .mh-hint:before{animation:none;}
  [role="tab"]{transition:none;}
}
</style>
"""


def radar_svg(axes: list[dict], series: list[dict], size: int = 320, dark: bool = False, animate: bool = False) -> str:
    """Radar M1–M9. axes: [{code,max}], series: [{values:{code:val}, cls:'tgt'|'cand'|'cand c2'}]."""
    c, r, n = size / 2, size * 0.33, len(axes)

    def pt(i: int, f: float) -> tuple[float, float]:
        a = -math.pi / 2 + 2 * math.pi * i / n
        return c + r * f * math.cos(a), c + r * f * math.sin(a)

    parts = [f'<svg class="rd{" dark" if dark else ""}{" anim" if animate else ""}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">']
    for f in (.25, .5, .75, 1):
        parts.append('<polygon class="ring" points="' + " ".join("%.1f,%.1f" % pt(i, f) for i in range(n)) + '"/>')
    for i, ax in enumerate(axes):
        x, y = pt(i, 1)
        lx, ly = pt(i, 1.22)
        parts.append(f'<line class="spoke" x1="{c}" y1="{c}" x2="{x:.1f}" y2="{y:.1f}"/><text x="{lx:.1f}" y="{ly:.1f}">{html.escape(ax["code"])}</text>')
    for s in series:
        pts = [pt(i, max(0.0, min(1.0, s["values"][ax["code"]] / ax["max"]))) for i, ax in enumerate(axes) if ax["code"] in s["values"] and ax["max"]]
        if len(pts) < 2:
            continue
        coords = " ".join("%.1f,%.1f" % p for p in pts)
        cls = s.get("cls", "cand")
        style = f' style="transform-origin:{c}px {c}px"'
        parts.append(f'<polygon class="{cls}" points="{coords}"{style}/>' if len(pts) > 2 else f'<polyline class="{cls}" points="{coords}"{style}/>')
        if cls.startswith("tgt"):
            parts.extend(f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="3"/>' for x, y in pts)
    parts.append("</svg>")
    return "".join(parts)


def weight_bar(profile: int = 70, competency: int = 30) -> str:
    return (f"<div class='wbar'><i class='p' style='width:{profile}%'></i><i class='k' style='width:{competency}%'></i></div>"
            f"<div class='wlegend'><span>Profil <b>{profile}%</b></span><span>Kompetensi <b>{competency}%</b></span></div>")



_base_inject_styles = inject_styles


def inject_styles() -> None:
    _base_inject_styles()
    st.markdown(VISUAL_LAYER, unsafe_allow_html=True)
    st.markdown(TAB_LAYER, unsafe_allow_html=True)
