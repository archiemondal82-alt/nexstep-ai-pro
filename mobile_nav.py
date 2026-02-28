"""
mobile_nav.py — JobLess AI Mobile Layer
========================================
WHY THIS WORKS:
  - CSS  → st.markdown(unsafe_allow_html=True) → written into the real page DOM ✅
  - JS   → components.html() with window.parent → escapes iframe sandbox ✅

WHY THE OLD VERSION FAILED:
  - components.html() runs inside a sandboxed iframe.
  - CSS/JS inside that iframe CANNOT touch the parent page at all.
  - Tabs, sidebar, body — all invisible from inside the iframe.
  - Using window.parent in the JS lets us reach up and modify the real page.
"""

import streamlit as st
import streamlit.components.v1 as components

_TABS = [
    {"icon": "📊", "short": "Career"},
    {"icon": "📜", "short": "History"},
    {"icon": "⚖️",  "short": "Compare"},
    {"icon": "📚", "short": "Learn"},
    {"icon": "📝", "short": "Resume"},
    {"icon": "🎤", "short": "Interview"},
    {"icon": "📂", "short": "PYQ"},
]


def inject_mobile_nav():
    # ── STEP 1: CSS + HTML shells via st.markdown (goes into real page DOM) ──
    st.markdown("""
<style>
/* Viewport lock — no zoom, no h-scroll */
html, body {
  overflow-x: hidden !important;
  touch-action: pan-y !important;
  -webkit-text-size-adjust: 100% !important;
  overscroll-behavior-x: none !important;
  scroll-behavior: smooth;
}
@media (max-width: 768px) {
  /* Hide Streamlit tab strip — bottom nav replaces it */
  [data-testid="stTabs"] > div:first-child,
  .stTabs [data-baseweb="tab-list"] { display: none !important; }
  /* Hide sidebar + toggle */
  [data-testid="stSidebar"],
  [data-testid="collapsedControl"] { display: none !important; }
  /* Hide top header bar */
  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  .stDeployButton { display: none !important; }
  /* Content area — full width + space for bottom nav */
  [data-testid="block-container"] {
    padding: 8px 12px calc(80px + env(safe-area-inset-bottom)) 12px !important;
    max-width: 100% !important; width: 100% !important;
  }
  /* Prevent iOS zoom on input focus */
  input, textarea, select { font-size: 16px !important; }
  /* Bigger tap targets */
  .stButton > button { min-height: 48px !important; }
  /* Prevent table overflow */
  pre, code, table { overflow-x: auto; max-width: 100%; font-size: 12px !important; }
  /* Page transition on tab switch */
  [data-testid="stTabsContent"] {
    animation: jl-in 0.28s cubic-bezier(0.22,1,0.36,1) both;
  }
  /* Hide horizontal scrollbar everywhere */
  *::-webkit-scrollbar { display: none !important; }
  * { scrollbar-width: none !important; }
}
@keyframes jl-in {
  from { opacity:0; transform:translateY(14px); }
  to   { opacity:1; transform:translateY(0); }
}

/* ─────────────────── BOTTOM NAV ─────────────────── */
#jl-nav {
  display: none; /* JS sets to block on mobile */
  position: fixed;
  bottom: 0; left: 0; right: 0;
  z-index: 999999;
  background: rgba(6,11,20,0.97);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-top: 1px solid rgba(0,210,255,0.18);
  box-shadow: 0 -4px 30px rgba(0,0,0,0.6);
  height: calc(62px + env(safe-area-inset-bottom));
  padding-bottom: env(safe-area-inset-bottom);
  animation: jl-slide-up 0.4s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes jl-slide-up {
  from { transform: translateY(100%); }
  to   { transform: translateY(0); }
}
#jl-nav .inner { display: flex; height: 62px; align-items: stretch; }
.jl-tab {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 3px;
  border: none; background: transparent; cursor: pointer;
  padding: 6px 2px; position: relative;
  -webkit-tap-highlight-color: transparent;
  transition: background 0.15s;
}
.jl-tab:active { background: rgba(0,210,255,0.08); }
.jl-tab .ico {
  font-size: 20px; line-height: 1;
  transition: transform 0.22s cubic-bezier(0.34,1.56,0.64,1), filter 0.22s ease;
}
.jl-tab .lbl {
  font-size: 9px; font-weight: 700; letter-spacing: 0.05em;
  text-transform: uppercase; color: #475569;
  transition: color 0.2s; font-family: system-ui, sans-serif;
  white-space: nowrap; line-height: 1;
}
.jl-tab.on .ico { transform: translateY(-2px) scale(1.22); filter: drop-shadow(0 0 5px rgba(0,210,255,0.8)); }
.jl-tab.on .lbl { color: #00d2ff; }
.jl-tab.on::before {
  content: '';
  position: absolute; top: 0; left: 50%;
  transform: translateX(-50%);
  width: 28px; height: 2.5px;
  background: linear-gradient(90deg, #00d2ff, #3a7bd5);
  border-radius: 0 0 3px 3px;
  box-shadow: 0 0 10px rgba(0,210,255,0.8);
}

/* ─────────────────── PULL TO REFRESH ─────────────────── */
#jl-ptr {
  position: fixed; top: -64px; left: 50%;
  transform: translateX(-50%);
  z-index: 999998;
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(0,210,255,0.14);
  border: 1px solid rgba(0,210,255,0.4);
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; transition: top 0.25s ease;
  pointer-events: none;
}
#jl-ptr.show { top: 14px; }
@keyframes ptr-spin {
  to { transform: translateX(-50%) rotate(360deg); }
}
#jl-ptr.spinning { animation: ptr-spin 0.7s linear infinite; top: 14px; }

/* ─────────────────── MODAL ─────────────────── */
#jl-modal-bg {
  display: none; position: fixed; inset: 0; z-index: 9999999;
  background: rgba(0,0,0,0.72); backdrop-filter: blur(7px);
  -webkit-backdrop-filter: blur(7px);
  align-items: flex-end; justify-content: center;
}
#jl-modal-bg.on { display: flex; }
#jl-modal-box {
  width: 100%; max-width: 600px;
  background: linear-gradient(180deg,#0f172a,#060b14);
  border-radius: 22px 22px 0 0;
  border-top: 1px solid rgba(0,210,255,0.2);
  box-shadow: 0 -16px 60px rgba(0,0,0,0.8);
  padding-bottom: calc(20px + env(safe-area-inset-bottom));
  animation: jl-up 0.35s cubic-bezier(0.22,1,0.36,1) both;
  max-height: 80vh; overflow-y: auto; overscroll-behavior: contain;
}
@keyframes jl-up { from { transform:translateY(100%); } to { transform:translateY(0); } }
.jl-handle { width:36px; height:4px; background:rgba(255,255,255,0.18); border-radius:2px; margin:12px auto 0; }
.jl-mhead { display:flex; align-items:center; justify-content:space-between; padding:14px 20px 4px; }
.jl-mtitle { color:#e2e8f0; font-weight:700; font-size:1rem; font-family:system-ui,sans-serif; }
.jl-mclose {
  width:30px; height:30px; border-radius:50%;
  background:rgba(255,255,255,0.07); border:none;
  color:#94a3b8; font-size:15px; cursor:pointer;
  display:flex; align-items:center; justify-content:center;
}
.jl-mbody { padding:12px 20px 8px; }
.jl-alert {
  border-radius:12px; padding:14px 16px;
  display:flex; gap:12px; align-items:flex-start;
  font-family:system-ui,sans-serif; font-size:0.88rem; line-height:1.55; color:#e2e8f0;
}
.jl-ok {
  width:100%; margin-top:14px; padding:13px; border-radius:10px;
  background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.12);
  color:#e2e8f0; font-size:0.9rem; font-weight:700; cursor:pointer;
  font-family:system-ui,sans-serif;
}
</style>

<!-- Bottom Nav -->
<div id="jl-nav"><div class="inner" id="jl-nav-inner"></div></div>

<!-- Pull to Refresh -->
<div id="jl-ptr">🔄</div>

<!-- Modal -->
<div id="jl-modal-bg" onclick="if(event.target===this)jlClose()">
  <div id="jl-modal-box">
    <div class="jl-handle"></div>
    <div class="jl-mhead">
      <span class="jl-mtitle" id="jl-mtitle">Notice</span>
      <button class="jl-mclose" onclick="jlClose()">✕</button>
    </div>
    <div class="jl-mbody" id="jl-mbody"></div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── STEP 2: JS via components.html — uses window.parent to escape iframe ──
    tab_json = str([{"icon": t["icon"], "short": t["short"]} for t in _TABS]).replace("'", '"')

    components.html(f"""<script>
(function() {{
  // window.parent = the actual Streamlit page (we are in an iframe)
  var P = window.parent;
  var D = P.document;

  // Inject no-zoom viewport into parent page head
  var vm = D.querySelector('meta[name="viewport"]');
  var vc = 'width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no,viewport-fit=cover';
  if (vm) vm.setAttribute('content', vc);
  else {{ var m=D.createElement('meta'); m.name='viewport'; m.content=vc; D.head.appendChild(m); }}

  // Only run on mobile
  var mobile = P.innerWidth <= 768 || /Android|iPhone|iPad|iPod|Mobile/i.test(P.navigator.userAgent);
  if (!mobile) return;

  var TABS  = {tab_json};
  var nav   = D.getElementById('jl-nav');
  var inner = D.getElementById('jl-nav-inner');
  var ptr   = D.getElementById('jl-ptr');
  if (!nav || !inner) return;

  // Build tab buttons
  inner.innerHTML = '';
  TABS.forEach(function(t, i) {{
    var btn = D.createElement('button');
    btn.className = 'jl-tab' + (i===0 ? ' on' : '');
    btn.setAttribute('aria-label', t.short);
    btn.innerHTML = '<span class="ico">' + t.icon + '</span><span class="lbl">' + t.short + '</span>';
    btn.addEventListener('click', function() {{ switchTab(i); }});
    inner.appendChild(btn);
  }});
  nav.style.display = 'block';

  var cur = 0;

  function getStTabs() {{
    var sels = [
      '[data-testid="stTabs"] [data-baseweb="tab"]',
      '.stTabs [role="tab"]',
      '[data-testid="stTabsTabList"] button',
      '[role="tablist"] [role="tab"]'
    ];
    for (var i=0; i<sels.length; i++) {{
      var r = D.querySelectorAll(sels[i]);
      if (r && r.length) return r;
    }}
    return [];
  }}

  function switchTab(idx) {{
    cur = idx;
    D.querySelectorAll('.jl-tab').forEach(function(b,i) {{ b.classList.toggle('on', i===idx); }});
    try {{ if (P.navigator.vibrate) P.navigator.vibrate(8); }} catch(e) {{}}
    var tabs = getStTabs();
    if (tabs[idx]) tabs[idx].click();
  }}

  // Sync with Streamlit tab state (in case user clicks native tabs somehow)
  setInterval(function() {{
    var tabs = getStTabs();
    tabs.forEach(function(t,i) {{
      if (t.getAttribute('aria-selected')==='true' && i!==cur) {{
        cur = i;
        D.querySelectorAll('.jl-tab').forEach(function(b,j) {{ b.classList.toggle('on', j===i); }});
      }}
    }});
  }}, 700);

  // ── Expose modal on parent window so Streamlit Python can call it ──
  P.jlShow = function(title, msg, type) {{
    var bg = {{ success:'rgba(34,197,94,0.12)', error:'rgba(239,68,68,0.12)', warn:'rgba(245,158,11,0.10)', info:'rgba(0,210,255,0.10)' }};
    var br = {{ success:'rgba(34,197,94,0.3)',  error:'rgba(239,68,68,0.3)',  warn:'rgba(245,158,11,0.25)', info:'rgba(0,210,255,0.25)' }};
    var ic = {{ success:'✅', error:'❌', warn:'⚠️', info:'ℹ️' }};
    var t=D.getElementById('jl-mtitle'), b=D.getElementById('jl-mbody'), g=D.getElementById('jl-modal-bg');
    if (!t||!b||!g) return;
    t.textContent = title;
    b.innerHTML = '<div class="jl-alert" style="background:'+(bg[type]||bg.info)+';border:1px solid '+(br[type]||br.info)+'">'
      +(ic[type]||'ℹ️')+' '+msg+'</div>'
      +'<button class="jl-ok" onclick="jlClose()">OK</button>';
    g.classList.add('on');
  }};
  P.jlClose = function() {{
    var g=D.getElementById('jl-modal-bg'); if(g) g.classList.remove('on');
  }};

  // Intercept Streamlit toasts and convert to modal
  new MutationObserver(function(muts) {{
    muts.forEach(function(m) {{
      m.addedNodes.forEach(function(n) {{
        if (!n.querySelector) return;
        var toast = n.querySelector('[data-testid="stToast"]') ||
                    (n.dataset && n.dataset.testid==='stToast' ? n : null);
        if (!toast) return;
        var text = toast.textContent.trim();
        var tp = 'info';
        if (/warning|⚠️/i.test(text)) tp='warn';
        if (/success|✅/i.test(text))  tp='success';
        if (/error|❌/i.test(text))    tp='error';
        toast.style.display = 'none';
        P.jlShow(
          tp==='success'?'✅ Success':tp==='error'?'❌ Error':tp==='warn'?'⚠️ Warning':'ℹ️ Info',
          text.replace(/[✅❌⚠️ℹ️]/g,'').trim(), tp
        );
      }});
    }});
  }}).observe(D.body, {{childList:true, subtree:true}});

  // ── Pull to Refresh ──
  var ptY=0, ptOn=false, PTR_H=72;
  D.addEventListener('touchstart', function(e) {{
    var el = D.querySelector('[data-testid="stMain"]') || D.documentElement;
    if (el.scrollTop<=0) {{ ptY=e.touches[0].clientY; ptOn=true; }}
  }}, {{passive:true}});
  D.addEventListener('touchmove', function(e) {{
    if (!ptOn || !ptr) return;
    var d = e.touches[0].clientY - ptY;
    if (d>0 && d<PTR_H*1.8) {{
      ptr.style.top = Math.min(-64 + d, 14) + 'px';
      if (d>PTR_H) {{ ptr.textContent='↻'; ptr.classList.add('show'); }}
    }}
  }}, {{passive:true}});
  D.addEventListener('touchend', function(e) {{
    if (!ptOn||!ptr) return;
    var d = e.changedTouches[0].clientY - ptY;
    if (d>PTR_H) {{
      ptr.classList.add('spinning');
      try {{ if(P.navigator.vibrate) P.navigator.vibrate([10,50,10]); }} catch(ex) {{}}
      setTimeout(function() {{ P.location.reload(); }}, 650);
    }} else {{
      ptr.style.top='-64px'; ptr.classList.remove('show');
      setTimeout(function() {{ ptr.textContent='🔄'; }},300);
    }}
    ptOn=false;
  }}, {{passive:true}});

  // ── Swipe left/right to change tabs ──
  var sx=0, sy=0, sOn=false;
  D.addEventListener('touchstart', function(e) {{
    if(e.touches.length===1) {{ sx=e.touches[0].clientX; sy=e.touches[0].clientY; sOn=true; }}
  }}, {{passive:true}});
  D.addEventListener('touchend', function(e) {{
    if(!sOn) return; sOn=false;
    var dx=e.changedTouches[0].clientX-sx, dy=e.changedTouches[0].clientY-sy;
    if(Math.abs(dx)<60 || Math.abs(dy)/Math.abs(dx)>0.65) return;
    if(dx<0 && cur<TABS.length-1) switchTab(cur+1);
    else if(dx>0 && cur>0) switchTab(cur-1);
  }}, {{passive:true}});

  // Prevent double-tap zoom
  var lt=0;
  D.addEventListener('touchend', function(e) {{
    var now=Date.now(); if(now-lt<300) e.preventDefault(); lt=now;
  }}, {{passive:false}});
  // Prevent pinch zoom
  D.addEventListener('gesturestart',  function(e){{e.preventDefault();}}, {{passive:false}});
  D.addEventListener('gesturechange', function(e){{e.preventDefault();}}, {{passive:false}});

}})();
</script>""", height=0, scrolling=False)
