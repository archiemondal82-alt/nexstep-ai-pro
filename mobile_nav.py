"""
mobile_nav.py — JobLess AI Mobile Enhancement
==============================================
Drop-in module for mobile-first bottom navigation,
smooth transitions, pull-to-refresh, no-zoom, and modal alerts.

INTEGRATION (add to jobless_ai_public.py):
─────────────────────────────────────────
1. At top of file:
       from mobile_nav import inject_mobile_nav

2. In main(), after ui.apply_custom_css() and before the tabs block:
       inject_mobile_nav()

That's it. The rest is automatic — detects mobile, enhances experience.
"""

import streamlit.components.v1 as components


# ═══════════════════════════════════════════════════════════════════
# TAB MAP  (must match order in st.tabs([...]) in main())
# ═══════════════════════════════════════════════════════════════════
# Index : 0=Career Analysis, 1=History, 2=Compare,
#         3=Resources, 4=Resume Builder, 5=Mock Interview, 6=PYQ Hub

_MOBILE_NAV_HTML = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width,initial-scale=1,
               maximum-scale=1,user-scalable=no,
               viewport-fit=cover">
<style>
/* ── reset ─────────────────────────────────────────────── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{background:transparent;overflow:hidden;width:0;height:0}
</style>
</head>
<body>
<script>
/* ══════════════════════════════════════════════════════════
   JOBLESS AI — MOBILE ENHANCEMENT ENGINE  v3.0
   Hooks into the parent Streamlit document.
   Only activates on screens < 768 px.
══════════════════════════════════════════════════════════ */
(function(){
'use strict';

/* ── helpers ── */
var P   = window.parent;
var D   = P.document;
var MOBILE_BREAKPOINT = 768;
var isMobile = P.innerWidth < MOBILE_BREAKPOINT;

/* Re-check on resize */
P.addEventListener('resize', function(){
  isMobile = P.innerWidth < MOBILE_BREAKPOINT;
  if(isMobile){ mount(); } else { unmount(); }
}, {passive:true});

if(!isMobile){ return; }

/* ── Tab definitions ── */
var TABS = [
  { label:'Analysis',  icon:'📊', idx:0 },
  { label:'Resume',    icon:'📝', idx:4 },
  { label:'Interview', icon:'🎤', idx:5 },
  { label:'History',   icon:'📜', idx:1 },
  { label:'More',      icon:'⋯',  idx:-1 }
];
var MORE_TABS = [
  { label:'Compare',   icon:'⚖️',  idx:2 },
  { label:'Resources', icon:'📚', idx:3 },
  { label:'PYQ Hub',   icon:'📂', idx:6 }
];

var mounted   = false;
var activeTab = 0;
var moreOpen  = false;
var navEl, overlayEl, moreDrawerEl, transitionEl, modalEl;
var ptrEl, ptrActive=false, ptrStart=0, ptrCur=0;

/* ═══════════════════════════════════════════════
   INJECT GLOBAL MOBILE CSS into parent document
═══════════════════════════════════════════════ */
function injectCSS(){
  if(D.getElementById('jl-mobile-css')) return;
  var s = D.createElement('style');
  s.id = 'jl-mobile-css';
  s.textContent = `
    /* ── no zoom, no horizontal scroll ── */
    html { touch-action: pan-y !important; }
    body { overflow-x: hidden !important; }

    /* ── prevent iOS double-tap zoom ── */
    * { touch-action: manipulation; }

    /* ── fix viewport meta in Streamlit iframe ── */
    :root {
      --nav-h: 68px;
      --nav-safe: max(var(--nav-h), calc(var(--nav-h) + env(safe-area-inset-bottom)));
      --accent:  #00d2ff;
      --accent2: #a855f7;
      --bg:      #060b14;
      --bg2:     #0d1828;
      --glass:   rgba(13,24,40,0.92);
      --border:  rgba(0,210,255,0.18);
      --trans:   cubic-bezier(0.32,0.72,0,1);
    }

    /* ── hide native Streamlit tab bar on mobile ── */
    @media (max-width: 768px) {
      [data-baseweb="tab-list"],
      [data-testid="stTabBar"],
      div[class*="stTabs"] > div:first-child {
        display: none !important;
      }

      /* Bottom padding so content isn't behind nav */
      .main .block-container {
        padding-bottom: var(--nav-safe) !important;
        padding-top: 8px !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
        max-width: 100% !important;
      }

      /* Remove Streamlit's default wide padding */
      section.main { padding: 0 !important; }

      /* No horizontal overflow anywhere */
      * { max-width: 100% !important; }
      img, iframe, video, canvas { max-width: 100% !important; }
    }

    /* ── PAGE TRANSITION LAYER ── */
    #jl-transition {
      position: fixed;
      inset: 0;
      z-index: 9998;
      pointer-events: none;
      background: radial-gradient(circle at 50% 50%,
        rgba(0,210,255,0.18) 0%,
        rgba(0,0,0,0) 70%);
      opacity: 0;
      transition: opacity 0.35s ease;
    }
    #jl-transition.active { opacity: 1; pointer-events: all; }

    /* ── PULL-TO-REFRESH INDICATOR ── */
    #jl-ptr {
      position: fixed;
      top: 0;
      left: 50%;
      transform: translateX(-50%) translateY(-80px);
      width: 44px;
      height: 44px;
      background: var(--glass);
      border: 1px solid var(--border);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      z-index: 9999;
      transition: transform 0.3s var(--trans), opacity 0.3s;
      box-shadow: 0 4px 24px rgba(0,210,255,0.2);
      opacity: 0;
      backdrop-filter: blur(20px);
    }
    #jl-ptr.visible {
      opacity: 1;
    }
    #jl-ptr.releasing {
      border-color: var(--accent);
      box-shadow: 0 0 24px rgba(0,210,255,0.5);
    }
    #jl-ptr .ptr-icon {
      display: inline-block;
      transition: transform 0.3s;
    }
    #jl-ptr.releasing .ptr-icon { transform: rotate(180deg); }

    /* ── BOTTOM NAVIGATION BAR ── */
    #jl-nav {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: var(--nav-safe);
      padding-bottom: env(safe-area-inset-bottom);
      z-index: 9000;
      background: var(--glass);
      backdrop-filter: blur(28px) saturate(180%);
      -webkit-backdrop-filter: blur(28px) saturate(180%);
      border-top: 1px solid var(--border);
      box-shadow:
        0 -1px 0 rgba(0,210,255,0.08),
        0 -20px 60px rgba(0,0,0,0.5),
        inset 0 1px 0 rgba(255,255,255,0.05);
      display: flex;
      align-items: flex-start;
      padding-top: 0;
      transition: transform 0.4s var(--trans);
    }

    #jl-nav.hidden { transform: translateY(110%); }

    /* Active glow line */
    #jl-nav::before {
      content: '';
      position: absolute;
      top: 0;
      left: var(--glow-x, 10%);
      width: 20%;
      height: 2px;
      background: linear-gradient(90deg, transparent, var(--accent), transparent);
      border-radius: 0 0 4px 4px;
      transition: left 0.4s var(--trans);
      filter: blur(1px);
      box-shadow: 0 0 8px var(--accent);
    }

    .jl-tab-btn {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 2px;
      height: var(--nav-h);
      border: none;
      background: transparent;
      color: rgba(255,255,255,0.38);
      cursor: pointer;
      position: relative;
      transition: color 0.25s ease;
      -webkit-tap-highlight-color: transparent;
      outline: none;
      user-select: none;
    }

    .jl-tab-btn:active { transform: scale(0.88); }

    .jl-tab-btn.active { color: var(--accent); }

    .jl-tab-icon {
      font-size: 20px;
      line-height: 1;
      transition: transform 0.3s var(--trans), filter 0.3s;
    }
    .jl-tab-btn.active .jl-tab-icon {
      transform: translateY(-3px) scale(1.15);
      filter: drop-shadow(0 0 6px rgba(0,210,255,0.7));
    }

    .jl-tab-label {
      font-family: 'Space Grotesk', 'Inter', sans-serif;
      font-size: 9.5px;
      font-weight: 600;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      transition: opacity 0.25s;
      opacity: 0.7;
    }
    .jl-tab-btn.active .jl-tab-label { opacity: 1; }

    /* Active dot pip */
    .jl-tab-btn.active::after {
      content: '';
      position: absolute;
      bottom: 8px;
      left: 50%;
      transform: translateX(-50%);
      width: 4px;
      height: 4px;
      border-radius: 50%;
      background: var(--accent);
      box-shadow: 0 0 6px var(--accent);
      animation: pipBlink 2.5s ease-in-out infinite;
    }
    @keyframes pipBlink {
      0%,100%{opacity:1} 50%{opacity:0.4}
    }

    /* ── MORE DRAWER OVERLAY ── */
    #jl-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0);
      z-index: 8990;
      transition: background 0.35s ease;
      pointer-events: none;
    }
    #jl-overlay.open {
      background: rgba(0,0,0,0.6);
      pointer-events: all;
      backdrop-filter: blur(4px);
    }

    /* ── MORE DRAWER ── */
    #jl-more-drawer {
      position: fixed;
      bottom: var(--nav-safe);
      left: 0;
      right: 0;
      background: var(--bg2);
      border: 1px solid var(--border);
      border-bottom: none;
      border-radius: 24px 24px 0 0;
      z-index: 8995;
      padding: 12px 0 16px;
      transform: translateY(110%);
      transition: transform 0.4s var(--trans);
      box-shadow: 0 -20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06);
    }
    #jl-more-drawer.open {
      transform: translateY(0);
    }

    .jl-drawer-handle {
      width: 36px;
      height: 4px;
      border-radius: 2px;
      background: rgba(255,255,255,0.15);
      margin: 0 auto 16px;
    }

    .jl-drawer-title {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: rgba(255,255,255,0.25);
      padding: 0 20px 12px;
      border-bottom: 1px solid rgba(255,255,255,0.05);
      margin-bottom: 8px;
    }

    .jl-drawer-item {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 14px 24px;
      border: none;
      background: transparent;
      color: rgba(255,255,255,0.75);
      cursor: pointer;
      width: 100%;
      text-align: left;
      transition: background 0.2s, color 0.2s;
      -webkit-tap-highlight-color: transparent;
      outline: none;
    }
    .jl-drawer-item:active { background: rgba(0,210,255,0.08); }
    .jl-drawer-item.active {
      color: var(--accent);
      background: rgba(0,210,255,0.06);
    }
    .jl-drawer-item-icon {
      font-size: 22px;
      width: 36px;
      text-align: center;
      flex-shrink: 0;
    }
    .jl-drawer-item-text {
      display: flex;
      flex-direction: column;
      gap: 1px;
    }
    .jl-drawer-item-label {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 15px;
      font-weight: 600;
    }
    .jl-drawer-item-sub {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 11px;
      color: rgba(255,255,255,0.3);
    }
    .jl-drawer-item.active .jl-drawer-item-sub { color: rgba(0,210,255,0.5); }
    .jl-drawer-item-check {
      margin-left: auto;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: rgba(0,210,255,0.12);
      border: 1.5px solid rgba(0,210,255,0.4);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      color: var(--accent);
      opacity: 0;
      transition: opacity 0.2s;
    }
    .jl-drawer-item.active .jl-drawer-item-check { opacity: 1; }

    /* ── MODAL (replaces toasts/alerts on mobile) ── */
    #jl-modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.65);
      backdrop-filter: blur(8px);
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s ease;
      padding: 20px;
    }
    #jl-modal-backdrop.open {
      opacity: 1;
      pointer-events: all;
    }
    #jl-modal {
      background: var(--bg2);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 28px 24px 20px;
      width: 100%;
      max-width: 380px;
      box-shadow:
        0 0 0 1px rgba(0,210,255,0.06),
        0 30px 80px rgba(0,0,0,0.7),
        inset 0 1px 0 rgba(255,255,255,0.06);
      transform: scale(0.88) translateY(20px);
      transition: transform 0.35s var(--trans);
      position: relative;
      overflow: hidden;
    }
    #jl-modal-backdrop.open #jl-modal {
      transform: scale(1) translateY(0);
    }

    /* Glow accent line */
    #jl-modal::before {
      content: '';
      position: absolute;
      top: 0;
      left: 15%;
      right: 15%;
      height: 2px;
      border-radius: 0 0 4px 4px;
      background: linear-gradient(90deg, transparent, var(--jl-modal-color, var(--accent)), transparent);
      box-shadow: 0 0 12px var(--jl-modal-color, var(--accent));
    }

    .jl-modal-icon {
      font-size: 36px;
      text-align: center;
      margin-bottom: 14px;
      display: block;
    }
    .jl-modal-title {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 17px;
      font-weight: 700;
      color: #e2e8f0;
      text-align: center;
      margin-bottom: 8px;
    }
    .jl-modal-body {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 14px;
      color: rgba(255,255,255,0.55);
      text-align: center;
      line-height: 1.6;
      margin-bottom: 20px;
    }
    .jl-modal-btn {
      display: block;
      width: 100%;
      padding: 13px;
      border: none;
      border-radius: 14px;
      background: linear-gradient(135deg, var(--accent), #3a7bd5);
      color: #fff;
      font-family: 'Space Grotesk', sans-serif;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
      transition: opacity 0.2s, transform 0.15s;
      box-shadow: 0 4px 20px rgba(0,210,255,0.3);
    }
    .jl-modal-btn:active { transform: scale(0.96); opacity: 0.85; }
    .jl-modal-btn.secondary {
      background: rgba(255,255,255,0.06);
      color: rgba(255,255,255,0.5);
      box-shadow: none;
      margin-top: 8px;
      border: 1px solid rgba(255,255,255,0.08);
    }

    /* ── TAB TRANSITION RIPPLE ── */
    #jl-ripple {
      position: fixed;
      width: 0; height: 0;
      border-radius: 50%;
      background: radial-gradient(circle,
        rgba(0,210,255,0.22) 0%,
        rgba(0,210,255,0) 70%);
      transform: translate(-50%,-50%) scale(0);
      z-index: 9000;
      pointer-events: none;
      transition: none;
    }
    #jl-ripple.animate {
      transition: transform 0.6s cubic-bezier(0.2,0,0.5,1),
                  opacity 0.6s ease;
      transform: translate(-50%,-50%) scale(1);
      opacity: 0;
    }
  `;
  D.head.appendChild(s);
}

/* ═══════════════════════════════════════════════
   PATCH VIEWPORT META — prevent zoom in Streamlit
═══════════════════════════════════════════════ */
function patchViewport(){
  var existing = D.querySelector('meta[name="viewport"]');
  var content  = 'width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover';
  if(existing){ existing.setAttribute('content', content); }
  else {
    var m = D.createElement('meta');
    m.name = 'viewport';
    m.content = content;
    D.head.insertBefore(m, D.head.firstChild);
  }
}

/* ═══════════════════════════════════════════════
   TAB SWITCHING
═══════════════════════════════════════════════ */
function switchTab(idx, fromX){
  if(idx === activeTab) return;
  triggerRipple(fromX);
  showTransition(function(){
    var list = D.querySelector('[data-baseweb="tab-list"]');
    if(!list){ list = D.querySelector('[data-testid="stTabBar"]'); }
    if(list){
      var btns = list.querySelectorAll('[role="tab"]');
      if(btns[idx]){ btns[idx].click(); }
    }
    activeTab = idx;
    updateNavUI();
  });
}

/* ═══════════════════════════════════════════════
   RIPPLE + TRANSITION
═══════════════════════════════════════════════ */
var rippleEl;
function triggerRipple(x){
  if(!rippleEl){ return; }
  var size = Math.max(P.innerWidth, P.innerHeight) * 2.2;
  var xPos = (x !== undefined) ? x : P.innerWidth/2;
  var yPos = P.innerHeight - 34;
  rippleEl.style.cssText =
    'width:'+size+'px;height:'+size+'px;left:'+xPos+'px;top:'+yPos+'px;opacity:1;';
  rippleEl.classList.remove('animate');
  void rippleEl.offsetWidth;
  rippleEl.classList.add('animate');
}

function showTransition(cb){
  if(!transitionEl){ if(cb) cb(); return; }
  transitionEl.classList.add('active');
  P.setTimeout(function(){
    if(cb) cb();
    P.setTimeout(function(){
      transitionEl.classList.remove('active');
    }, 200);
  }, 120);
}

/* ═══════════════════════════════════════════════
   UPDATE NAV ACTIVE STATE + GLOW POSITION
═══════════════════════════════════════════════ */
function updateNavUI(){
  if(!navEl) return;

  /* Update bottom bar buttons */
  var btns = navEl.querySelectorAll('.jl-tab-btn');
  btns.forEach(function(b, i){
    var ti = TABS[i];
    var isActive = (ti.idx === activeTab) ||
                   (ti.idx === -1 && MORE_TABS.some(function(m){ return m.idx===activeTab; }));
    b.classList.toggle('active', isActive);
  });

  /* Move glow line */
  var activeIndex = -1;
  TABS.forEach(function(t,i){
    if(t.idx === activeTab) activeIndex = i;
    if(t.idx === -1 && MORE_TABS.some(function(m){ return m.idx===activeTab; })){
      activeIndex = i;
    }
  });
  if(activeIndex >= 0){
    var pct = (activeIndex / (TABS.length - 1)) * 80;
    navEl.style.setProperty('--glow-x', pct + '%');
  }

  /* Update drawer items */
  if(moreDrawerEl){
    var items = moreDrawerEl.querySelectorAll('.jl-drawer-item');
    items.forEach(function(item){
      var idx = parseInt(item.getAttribute('data-tab-idx'));
      item.classList.toggle('active', idx === activeTab);
    });
  }
}

/* ═══════════════════════════════════════════════
   MORE DRAWER
═══════════════════════════════════════════════ */
function openMore(){
  moreOpen = true;
  overlayEl.classList.add('open');
  moreDrawerEl.classList.add('open');
}
function closeMore(){
  moreOpen = false;
  overlayEl.classList.remove('open');
  moreDrawerEl.classList.remove('open');
}

/* ═══════════════════════════════════════════════
   MODAL (replaces alerts/toasts on mobile)
═══════════════════════════════════════════════ */
function showModal(opts){
  /* opts: { icon, title, body, type, actions:[{label,cb,secondary}] } */
  if(!modalEl) return;
  var backdrop = D.getElementById('jl-modal-backdrop');
  if(!backdrop) return;

  var typeColors = { success:'#34d399', error:'#f87171', info:'#00d2ff', warning:'#fbbf24' };
  var color = typeColors[opts.type] || typeColors.info;
  modalEl.style.setProperty('--jl-modal-color', color);

  backdrop.querySelector('.jl-modal-icon').textContent   = opts.icon  || '💡';
  backdrop.querySelector('.jl-modal-title').textContent  = opts.title || 'Notice';
  backdrop.querySelector('.jl-modal-body').textContent   = opts.body  || '';

  /* Build buttons */
  var btnContainer = backdrop.querySelector('.jl-modal-btns');
  btnContainer.innerHTML = '';
  var actions = opts.actions || [{label:'Got it', cb:null}];
  actions.forEach(function(a){
    var btn = D.createElement('button');
    btn.className = 'jl-modal-btn' + (a.secondary ? ' secondary' : '');
    btn.textContent = a.label;
    btn.onclick = function(){
      closeModal();
      if(a.cb) a.cb();
    };
    btnContainer.appendChild(btn);
  });

  backdrop.classList.add('open');
}

function closeModal(){
  var backdrop = D.getElementById('jl-modal-backdrop');
  if(backdrop) backdrop.classList.remove('open');
}

/* ═══════════════════════════════════════════════
   INTERCEPT STREAMLIT ALERTS/TOASTS → MODAL
═══════════════════════════════════════════════ */
function interceptAlerts(){
  /* Watch for Streamlit alert elements and replace with modal */
  var lastError = null, lastSuccess = null, lastInfo = null;
  var observer = new P.MutationObserver(function(mutations){
    mutations.forEach(function(m){
      m.addedNodes.forEach(function(node){
        if(node.nodeType !== 1) return;
        /* Streamlit toast */
        if(node.getAttribute && (
            node.getAttribute('data-testid') === 'stToast' ||
            (node.className && String(node.className).includes('toast'))
        )){
          var text = node.textContent || '';
          node.style.display = 'none';
          showModal({ icon:'ℹ️', title:'Notice', body:text.trim(), type:'info' });
          return;
        }
        /* Streamlit error / success / info elements */
        var alerts = node.querySelectorAll ? node.querySelectorAll(
          '[data-testid="stAlert"]'
        ) : [];
        alerts.forEach(function(a){
          var type = 'info';
          var icon = 'ℹ️';
          if(a.classList.contains('st-emotion-cache-') ||
             a.querySelector('[data-testid="stAlertDynamicIcon"]')){
            var iconEl = a.querySelector('[data-testid="stAlertDynamicIcon"]');
            if(iconEl){
              var ic = iconEl.textContent;
              if(ic.includes('✓') || ic.includes('✅')){ type='success'; icon='✅'; }
              else if(ic.includes('⚠') || ic.includes('!')){ type='warning'; icon='⚠️'; }
              else if(ic.includes('✗') || ic.includes('×')){ type='error'; icon='❌'; }
            }
          }
          var body = a.querySelector('[data-testid="stMarkdownContainer"]');
          var bodyText = body ? body.textContent : a.textContent;
          a.style.display = 'none';
          showModal({ icon:icon, title:type.charAt(0).toUpperCase()+type.slice(1),
                      body:bodyText.trim().substring(0,200), type:type });
        });
      });
    });
  });
  observer.observe(D.body, { childList:true, subtree:true });
}

/* ═══════════════════════════════════════════════
   PULL TO REFRESH
═══════════════════════════════════════════════ */
var PTR_THRESHOLD = 80;
var ptrIndicator;

function initPullToRefresh(){
  ptrIndicator = D.getElementById('jl-ptr');
  if(!ptrIndicator) return;

  var startY = 0, curY = 0, pulling = false;

  D.addEventListener('touchstart', function(e){
    /* Only trigger at very top of page */
    if(D.documentElement.scrollTop > 5) return;
    startY = e.touches[0].clientY;
    pulling = true;
  }, {passive:true});

  D.addEventListener('touchmove', function(e){
    if(!pulling) return;
    curY = e.touches[0].clientY;
    var delta = curY - startY;
    if(delta < 0){ pulling=false; return; }
    var clamped = Math.min(delta, PTR_THRESHOLD * 1.6);
    var progress = Math.min(clamped / PTR_THRESHOLD, 1);
    var translateY = clamped * 0.55;
    ptrIndicator.style.transform = 'translateX(-50%) translateY('+(translateY - 80)+'px)';
    ptrIndicator.classList.toggle('visible', progress > 0.2);
    ptrIndicator.classList.toggle('releasing', progress >= 1);
    /* Rotate spinner */
    var spinner = ptrIndicator.querySelector('.ptr-icon');
    if(spinner) spinner.style.transform = 'rotate('+(progress*180)+'deg)';
  }, {passive:true});

  D.addEventListener('touchend', function(){
    if(!pulling) return;
    pulling = false;
    var delta = curY - startY;
    ptrIndicator.classList.remove('visible','releasing');
    ptrIndicator.style.transform = 'translateX(-50%) translateY(-80px)';
    if(delta >= PTR_THRESHOLD){
      showTransition(function(){ P.location.reload(); });
    }
  }, {passive:true});
}

/* ═══════════════════════════════════════════════
   BUILD DOM
═══════════════════════════════════════════════ */
function buildDOM(){

  /* ── Transition layer ── */
  transitionEl = D.getElementById('jl-transition');
  if(!transitionEl){
    transitionEl = D.createElement('div');
    transitionEl.id = 'jl-transition';
    D.body.appendChild(transitionEl);
  }

  /* ── Ripple ── */
  rippleEl = D.getElementById('jl-ripple');
  if(!rippleEl){
    rippleEl = D.createElement('div');
    rippleEl.id = 'jl-ripple';
    D.body.appendChild(rippleEl);
  }

  /* ── Pull-to-refresh indicator ── */
  if(!D.getElementById('jl-ptr')){
    var ptr = D.createElement('div');
    ptr.id = 'jl-ptr';
    ptr.innerHTML = '<span class="ptr-icon">↓</span>';
    D.body.appendChild(ptr);
  }

  /* ── Overlay ── */
  overlayEl = D.getElementById('jl-overlay');
  if(!overlayEl){
    overlayEl = D.createElement('div');
    overlayEl.id = 'jl-overlay';
    D.body.appendChild(overlayEl);
    overlayEl.addEventListener('click', closeMore);
  }

  /* ── More drawer ── */
  moreDrawerEl = D.getElementById('jl-more-drawer');
  if(!moreDrawerEl){
    moreDrawerEl = D.createElement('div');
    moreDrawerEl.id = 'jl-more-drawer';
    var drawerHTML = '<div class="jl-drawer-handle"></div><div class="jl-drawer-title">More Sections</div>';
    var moreSubs = {
      2: 'Compare career paths',
      3: 'Learning materials',
      6: 'Practice questions'
    };
    MORE_TABS.forEach(function(t){
      drawerHTML +=
        '<button class="jl-drawer-item" data-tab-idx="'+t.idx+'">' +
          '<span class="jl-drawer-item-icon">'+t.icon+'</span>' +
          '<span class="jl-drawer-item-text">' +
            '<span class="jl-drawer-item-label">'+t.label+'</span>' +
            '<span class="jl-drawer-item-sub">'+(moreSubs[t.idx]||'')+'</span>' +
          '</span>' +
          '<span class="jl-drawer-item-check">✓</span>' +
        '</button>';
    });
    moreDrawerEl.innerHTML = drawerHTML;
    D.body.appendChild(moreDrawerEl);

    moreDrawerEl.querySelectorAll('.jl-drawer-item').forEach(function(btn){
      btn.addEventListener('click', function(){
        var idx = parseInt(btn.getAttribute('data-tab-idx'));
        closeMore();
        P.setTimeout(function(){ switchTab(idx); }, 120);
      });
    });
  }

  /* ── Modal backdrop ── */
  if(!D.getElementById('jl-modal-backdrop')){
    var backdrop = D.createElement('div');
    backdrop.id = 'jl-modal-backdrop';
    backdrop.innerHTML =
      '<div id="jl-modal">' +
        '<span class="jl-modal-icon">ℹ️</span>' +
        '<div class="jl-modal-title">Notice</div>' +
        '<div class="jl-modal-body"></div>' +
        '<div class="jl-modal-btns"></div>' +
      '</div>';
    D.body.appendChild(backdrop);
    backdrop.addEventListener('click', function(e){
      if(e.target === backdrop) closeModal();
    });
    modalEl = D.getElementById('jl-modal');
  }

  /* ── Bottom nav ── */
  navEl = D.getElementById('jl-nav');
  if(!navEl){
    navEl = D.createElement('nav');
    navEl.id = 'jl-nav';
    navEl.setAttribute('role','navigation');
    navEl.setAttribute('aria-label','Main navigation');
    var navHTML = '';
    TABS.forEach(function(t, i){
      navHTML +=
        '<button class="jl-tab-btn'+(i===0?' active':'')+'" ' +
                'aria-label="'+t.label+'" ' +
                'data-tab-idx="'+t.idx+'" ' +
                'data-nav-i="'+i+'">' +
          '<span class="jl-tab-icon" aria-hidden="true">'+t.icon+'</span>' +
          '<span class="jl-tab-label">'+t.label+'</span>' +
        '</button>';
    });
    navEl.innerHTML = navHTML;
    D.body.appendChild(navEl);

    navEl.querySelectorAll('.jl-tab-btn').forEach(function(btn){
      btn.addEventListener('click', function(e){
        var idx = parseInt(btn.getAttribute('data-tab-idx'));
        var rect = btn.getBoundingClientRect();
        var cx = rect.left + rect.width/2;
        if(idx === -1){
          if(moreOpen){ closeMore(); } else { openMore(); }
        } else {
          closeMore();
          switchTab(idx, cx);
        }
      });
    });
  }
}

/* ═══════════════════════════════════════════════
   WATCH FOR STREAMLIT TAB STATE CHANGES
   (sync active tab when Streamlit re-renders)
═══════════════════════════════════════════════ */
function watchTabState(){
  var tabObserver = new P.MutationObserver(function(){
    var list = D.querySelector('[data-baseweb="tab-list"]');
    if(!list) return;
    var active = list.querySelector('[aria-selected="true"]');
    if(!active) return;
    var allTabs = list.querySelectorAll('[role="tab"]');
    allTabs.forEach(function(t,i){
      if(t===active && i!==activeTab){
        activeTab = i;
        updateNavUI();
      }
    });
  });
  tabObserver.observe(D.body, {childList:true, subtree:true, attributes:true,
                                attributeFilter:['aria-selected']});
}

/* ═══════════════════════════════════════════════
   SCROLL HIDE/SHOW NAV ON FAST SCROLL
═══════════════════════════════════════════════ */
function initScrollBehavior(){
  var lastScrollY = 0, ticking = false, hideTimer;

  D.addEventListener('scroll', function(){
    if(ticking) return;
    P.requestAnimationFrame(function(){
      var cur = D.documentElement.scrollTop || D.body.scrollTop;
      if(!navEl){ lastScrollY=cur; ticking=false; return; }
      if(cur > lastScrollY + 60){
        /* Scrolling down fast — hide nav briefly */
        navEl.classList.add('hidden');
        clearTimeout(hideTimer);
        hideTimer = P.setTimeout(function(){
          navEl.classList.remove('hidden');
        }, 2000);
      } else if(cur < lastScrollY - 10){
        navEl.classList.remove('hidden');
      }
      lastScrollY = cur;
      ticking = false;
    });
    ticking = true;
  }, {passive:true});
}

/* ═══════════════════════════════════════════════
   MOUNT / UNMOUNT
═══════════════════════════════════════════════ */
function mount(){
  if(mounted) return;
  injectCSS();
  patchViewport();
  buildDOM();
  initPullToRefresh();
  interceptAlerts();
  watchTabState();
  initScrollBehavior();
  updateNavUI();
  mounted = true;
}

function unmount(){
  if(!mounted) return;
  ['jl-nav','jl-overlay','jl-more-drawer','jl-modal-backdrop',
   'jl-transition','jl-ripple','jl-ptr'].forEach(function(id){
    var el = D.getElementById(id);
    if(el) el.remove();
  });
  var css = D.getElementById('jl-mobile-css');
  if(css) css.remove();
  mounted = false;
  navEl = overlayEl = moreDrawerEl = transitionEl = rippleEl = modalEl = null;
}

/* ─── Bootstrap ─── */
function boot(){
  if(!D || !D.body){ P.setTimeout(boot, 100); return; }
  mount();
}

if(D.readyState === 'complete' || D.readyState === 'interactive'){
  boot();
} else {
  D.addEventListener('DOMContentLoaded', boot);
}

})();
</script>
</body>
</html>
"""


def inject_mobile_nav():
    """
    Call this in main() after ui.apply_custom_css() and before st.tabs([...]).
    Renders a 0×0 invisible iframe that hooks the mobile nav into the parent Streamlit document.
    Only activates on screens < 768 px.
    """
    components.html(_MOBILE_NAV_HTML, height=0, scrolling=False)
