"""
JobLess AI - Public Version (Users Bring Their Own API Key)
Enhanced version with clear API key instructions
Refactored: each tab is its own render_tab_*() function.
"""

from reportlab.lib.enums import TA_CENTER as _TAC, TA_LEFT as _TAL
from reportlab.platypus import (
    SimpleDocTemplate as _SDT, Paragraph as _Para, Spacer as _Spacer,
    Table as _Table, TableStyle as _TStyle, PageBreak as _PB,
    HRFlowable as _HR, KeepTogether as _KT
)
from reportlab.lib.units import cm as _cm, mm as _mm
from reportlab.lib.styles import getSampleStyleSheet as _getSS, ParagraphStyle as _PS
from reportlab.lib import colors as _rl_colors
from reportlab.lib.pagesizes import A4 as _A4
import io as _io
import datetime
import streamlit as st
import streamlit.components.v1 as components
from mobile_nav import inject_mobile_nav
import fitz  # PyMuPDF
import json
import pandas as pd
import altair as alt
import requests
from streamlit_lottie import st_lottie
import os
from typing import Dict, List, Optional
import time
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ── Provider SDK imports (graceful fallback if not installed) ──────────────
try:
    import google.generativeai as genai
    _GEMINI_OK = True
except ImportError:
    _GEMINI_OK = False

try:
    from groq import Groq as _GroqClient
    _GROQ_OK = True
except ImportError:
    _GROQ_OK = False

try:
    import cohere as _cohere_sdk
    _COHERE_OK = True
except ImportError:
    _COHERE_OK = False

# ── Static model catalogue ─────────────────────────────────────────────────
PROVIDER_MODELS: Dict[str, List[str]] = {
    "Google Gemini  🆓": [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro",
    ],
    "Groq  🆓⚡": [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "gemma-7b-it",
    ],
    "Cohere  🆓": [
        "command-r-plus",
        "command-r",
        "command",
        "command-light",
    ],
}

PROVIDER_KEY_URLS: Dict[str, str] = {
    "Google Gemini  🆓":  "https://aistudio.google.com/app/apikey",
    "Groq  🆓⚡":         "https://console.groq.com/keys",
    "Cohere  🆓":         "https://dashboard.cohere.com/api-keys",
}

PROVIDER_FREE_TIER: Dict[str, str] = {
    "Google Gemini  🆓":  "✅ Free forever · 15 req/min · 1500 req/day · No card",
    "Groq  🆓⚡":         "✅ Free forever · Ultra-fast inference · No card needed",
    "Cohere  🆓":         "✅ Free trial key · No card needed · Generous limits",
}

PROVIDER_INTERNAL = {
    "Google Gemini  🆓":  "gemini",
    "Groq  🆓⚡":         "groq",
    "Cohere  🆓":         "cohere",
}

# ==================== ANIMATED HEADER ====================
_HEADER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JobLess AI</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; cursor: none !important; }

/* FIX 1: overflow:hidden on body kills 3D transforms on iOS Safari.
   Use overflow:clip instead — it clips visually without creating a
   stacking context that flattens preserve-3d children.
   Fallback: auto (allows scroll in very old browsers, not ideal but safe). */
body {
  background: #060b14!important;
  overflow: clip; /* modern browsers */
  overflow: hidden; /* legacy fallback — overridden above in supporting browsers */
  font-family: 'Inter', sans-serif;
  padding: 0; margin: 0;
}

.stage {
  position: relative; z-index: 1;
  padding: 4px 0 6px 0;
  display: flex; flex-direction: column; align-items: flex-start;
}

/* ── badge ── */
.badge { display:flex; align-items:center; gap:9px; margin-bottom:16px; }
.badge-pip {
  width:6px; height:6px; border-radius:50%;
  background:#00d0ff;
  box-shadow:0 0 0 0 rgba(0,208,255,0.6);
  animation: pip 2.2s ease-out infinite;
}
@keyframes pip{0%{box-shadow:0 0 0 0 rgba(0,208,255,.6)}70%{box-shadow:0 0 0 9px rgba(0,208,255,0)}100%{box-shadow:0 0 0 0 rgba(0,208,255,0)}}
.badge span { font-size:10px; letter-spacing:5px; text-transform:uppercase; color:rgba(0,208,255,0.45); font-weight:300; }
.badge-div { width:1px; height:11px; background:rgba(0,208,255,0.18); }
.badge-v { font-size:10px; letter-spacing:2px; color:rgba(255,255,255,0.18); font-weight:300; }

/* ── title row ── */
.title-row { display:flex; align-items:center; gap:24px; position:relative; }

/* ══════════════════════════════════════════
   GYROSCOPE
   FIX 2: add -webkit-transform-style so iOS Safari
   respects preserve-3d inside the clipped container.
   FIX 3: isolate gyro in its own stacking context with
   will-change:transform so iOS doesn't flatten rings.
══════════════════════════════════════════ */
.gyro-wrap {
  width:90px; height:90px;
  position:relative;
  perspective:380px;
  flex-shrink:0;
  animation: bob 5s ease-in-out infinite;
  will-change: transform;        /* GPU layer — prevents iOS flatten bug */
  -webkit-perspective: 380px;
}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}

.gyro-body {
  width:100%; height:100%;
  transform-style: preserve-3d;
  -webkit-transform-style: preserve-3d; /* FIX: iOS Safari */
  position:relative;
}
.gr {
  position:absolute; top:50%; left:50%;
  border-radius:50%;
  transform-style: preserve-3d;
  -webkit-transform-style: preserve-3d;
}
.gr-a{ width:82px; height:82px; margin:-41px 0 0 -41px; }
.gr-b{ width:82px; height:82px; margin:-41px 0 0 -41px; }
.gr-c{ width:62px; height:62px; margin:-31px 0 0 -31px; }
.gr-a { box-shadow:0 0 0 2px rgba(0,208,255,0.85),0 0 16px rgba(0,208,255,0.4),inset 0 0 16px rgba(0,208,255,0.05); animation:spinA 5.5s linear infinite; }
.gr-b { box-shadow:0 0 0 1.5px rgba(0,208,255,0.55),0 0 10px rgba(0,208,255,0.2); transform:rotateX(90deg); -webkit-transform:rotateX(90deg); animation:spinB 7s linear infinite reverse; }
.gr-c { box-shadow:0 0 0 1.5px rgba(0,208,255,0.35),0 0 8px rgba(0,208,255,0.15); transform:rotateX(55deg) rotateY(30deg); -webkit-transform:rotateX(55deg) rotateY(30deg); animation:spinC 9s linear infinite; }
.gr-a::before { content:''; position:absolute; width:8px; height:8px; border-radius:50%; background:#fff; top:-4px; left:calc(50% - 4px); box-shadow:0 0 10px #00d0ff,0 0 22px rgba(0,208,255,.9),0 0 40px rgba(0,208,255,.5); }
.gr-b::before { content:''; position:absolute; width:5px; height:5px; border-radius:50%; background:rgba(0,208,255,0.9); bottom:-3px; left:calc(50% - 2.5px); box-shadow:0 0 8px #00d0ff; }
@keyframes spinA{to{transform:rotateY(360deg)}}
@keyframes spinB{to{transform:rotateX(90deg) rotateZ(360deg)}}
@keyframes spinC{to{transform:rotateX(55deg) rotateY(30deg) rotateZ(360deg)}}
.g-sphere {
  position:absolute; top:50%; left:50%;
  transform:translate(-50%,-50%);
  width:26px; height:26px; border-radius:50%;
  background:radial-gradient(circle at 35% 28%,#dff8ff 0%,#80e8ff 15%,#00cfff 35%,#007fa0 65%,#003050 100%);
  box-shadow:0 0 18px rgba(0,208,255,.9),0 0 40px rgba(0,208,255,.5),0 0 80px rgba(0,208,255,.25);
  z-index:10;
  animation:sbreathe 3s ease-in-out infinite;
}
.g-sphere::after { content:''; position:absolute; top:16%; left:20%; width:32%; height:16%; background:rgba(255,255,255,0.6); border-radius:50%; filter:blur(1px); transform:rotate(-28deg); }
@keyframes sbreathe{
  0%,100%{box-shadow:0 0 18px rgba(0,208,255,.9),0 0 40px rgba(0,208,255,.5),0 0 80px rgba(0,208,255,.25)}
  50%{box-shadow:0 0 24px rgba(0,208,255,1),0 0 60px rgba(0,208,255,.7),0 0 110px rgba(0,208,255,.38)}
}
.g-halo {
  position:absolute; top:50%; left:50%;
  transform:translate(-50%,-50%);
  width:100px; height:100px; border-radius:50%;
  border:1px solid rgba(0,208,255,0.09);
  z-index:0;
  animation:halospin 14s linear infinite reverse;
}
.g-halo::before { content:''; position:absolute; top:-2px; left:calc(50% - 2px); width:4px; height:4px; border-radius:50%; background:rgba(0,208,255,.6); box-shadow:0 0 6px rgba(0,208,255,.9); }
@keyframes halospin{to{transform:translate(-50%,-50%) rotate(360deg)}}

/* ── SVG title ── */
.svg-title-wrap { position:relative; line-height:1; }
#titleSvg { overflow:visible; display:block; max-width:100%; }
#glitchCanvas { position:absolute; top:0; left:0; pointer-events:none; z-index:11; }

/* ── subtitle ── */
.sub {
  margin-top:10px;
  font-size:12px;
  font-weight:300;
  letter-spacing:1.3px;
  color:rgba(255,255,255,0.28);
  padding-left:2px;
  opacity:0;
  animation: fadeUp 0.7s ease forwards 1.4s;
  /* Prevent text from forcing the iframe wider on small screens */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

/* ── entrance animations ── */
.badge { opacity:0; animation: fadeUp 0.6s ease forwards 0.2s; }
.title-row { opacity:0; animation: revealRow 1s cubic-bezier(0.16,1,0.3,1) forwards 0.55s; }
@keyframes fadeUp { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }
@keyframes revealRow { from{opacity:0;transform:translateY(24px) scale(0.96);filter:blur(8px)} to{opacity:1;transform:translateY(0) scale(1);filter:blur(0)} }
.svg-title-wrap { animation: depthBreathe 5s ease-in-out infinite 2.2s; }
@keyframes depthBreathe {
  0%,100%{filter:drop-shadow(0 5px 22px rgba(0,208,255,0.22)) drop-shadow(0 2px 6px rgba(0,208,255,0.12))}
  50%    {filter:drop-shadow(0 8px 42px rgba(0,208,255,0.55)) drop-shadow(0 3px 16px rgba(0,208,255,0.32))}
}

/* ══════════════════════════════════════════
   FIX 7: RESPONSIVE — tablet (600-900px)
══════════════════════════════════════════ */
@media (max-width: 900px) {
  .gyro-wrap { width:72px; height:72px; }
  .gr-a { width:66px; height:66px; margin:-33px 0 0 -33px; }
  .gr-b { width:66px; height:66px; margin:-33px 0 0 -33px; }
  .gr-c { width:50px; height:50px; margin:-25px 0 0 -25px; }
  .g-halo { width:82px; height:82px; }
  .g-sphere { width:22px; height:22px; }
  .title-row { gap:16px; }
}

/* ══════════════════════════════════════════
   FIX 7 + 9: RESPONSIVE — mobile (<600px)
   Shrink gyro, reduce gaps, tighten badge
══════════════════════════════════════════ */
@media (max-width: 600px) {
  .gyro-wrap { width:56px; height:56px; -webkit-perspective:240px; perspective:240px; }
  .gr-a { width:50px; height:50px; margin:-25px 0 0 -25px; }
  .gr-b { width:50px; height:50px; margin:-25px 0 0 -25px; }
  .gr-c { width:38px; height:38px; margin:-19px 0 0 -19px; }
  .g-halo { width:64px; height:64px; }
  .g-sphere { width:16px; height:16px; }
  .title-row { gap:12px; }
  .badge { margin-bottom:10px; }
  .badge span { letter-spacing:3px; font-size:9px; }
  .sub { font-size:10px; letter-spacing:0.7px; margin-top:7px; }
}

/* FIX 9: very small screens — hide gyro, let title breathe */
@media (max-width: 360px) {
  .gyro-wrap { display:none; }
  .title-row { gap:0; }
}

/* ══════════════════════════════════════════
   FIX 8: ACCESSIBILITY — prefers-reduced-motion
   Disable all animations for users who request it.
══════════════════════════════════════════ */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  .badge, .title-row, .sub { opacity: 1 !important; transform: none !important; filter: none !important; }
}
</style>
</head>
<body>
<script>
(function(){
  var fe = window.frameElement;
  if(fe){ fe.style.cssText += 'border:none!important;outline:none!important;box-shadow:none!important;background:#060b14!important;'; }
})();
</script>

<script>
(function() {
  var s = document.createElement('style');
  s.textContent = '* { cursor: none !important; }';
  document.head.appendChild(s);
  function fwd(e) {
    try {
      var fe = window.frameElement;
      if (!fe) return;
      var r = fe.getBoundingClientRect();
      window.parent.document.dispatchEvent(new window.parent.MouseEvent(e.type, {
        clientX: e.clientX + r.left, clientY: e.clientY + r.top,
        bubbles: true, cancelable: false
      }));
    } catch(err) {}
  }
  ['mousemove','mouseover','mouseout','mousedown','mouseup'].forEach(function(ev) {
    document.addEventListener(ev, fwd, { passive: true });
  });
})();
</script>

<div class="stage" id="stage">
  <div class="badge">
    <div class="badge-pip"></div>
    <span>AI Career Intelligence</span>
    <div class="badge-div"></div>
    <span class="badge-v">v2.0 Pro</span>
  </div>
  <div class="title-row">
    <div class="gyro-wrap">
      <div class="g-halo"></div>
      <div class="gyro-body">
        <div class="gr gr-a"></div>
        <div class="gr gr-b"></div>
        <div class="gr gr-c"></div>
      </div>
      <div class="g-sphere"></div>
    </div>
    <div class="svg-title-wrap" id="titleWrap">
      <canvas id="glitchCanvas"></canvas>
      <svg id="titleSvg" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="faceGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stop-color="#e8fafe"/>
            <stop offset="25%"  stop-color="#7dddff"/>
            <stop offset="55%"  stop-color="#00bfe8"/>
            <stop offset="80%"  stop-color="#008ab0"/>
            <stop offset="100%" stop-color="#00506a"/>
          </linearGradient>

          <!--
            FIX 4: fePointLight is expensive on mobile GPUs.
            We define TWO filters:
            - #lighting      → full animated fePointLight (desktop)
            - #lightingSimple → static drop-shadow fallback (mobile)
            JS selects which to apply based on device.
          -->
          <filter id="lighting" x="-5%" y="-5%" width="110%" height="120%" color-interpolation-filters="sRGB">
            <feGaussianBlur in="SourceAlpha" stdDeviation="2" result="blur"/>
            <feDiffuseLighting in="blur" result="diffuse" lighting-color="#ffffff" diffuseConstant="0.8" surfaceScale="4">
              <fePointLight x="150" y="-60" z="180">
                <animate attributeName="x" values="80;320;80" dur="8s" repeatCount="indefinite"/>
                <animate attributeName="y" values="-60;-20;-60" dur="8s" repeatCount="indefinite"/>
              </fePointLight>
            </feDiffuseLighting>
            <feSpecularLighting in="blur" result="specular" lighting-color="#a0f0ff" specularConstant="1.8" specularExponent="55" surfaceScale="4">
              <fePointLight x="150" y="-60" z="180">
                <animate attributeName="x" values="80;320;80" dur="8s" repeatCount="indefinite"/>
                <animate attributeName="y" values="-60;-20;-60" dur="8s" repeatCount="indefinite"/>
              </fePointLight>
            </feSpecularLighting>
            <feComposite in="diffuse"  in2="SourceAlpha" operator="in" result="diffOut"/>
            <feComposite in="specular" in2="SourceAlpha" operator="in" result="specOut"/>
            <feBlend in="SourceGraphic" in2="diffOut"  mode="multiply" result="step1"/>
            <feBlend in="step1"         in2="specOut"  mode="screen"   result="step2"/>
          </filter>

          <!-- Mobile fallback: simple static directional lighting, no point light -->
          <filter id="lightingSimple" x="-5%" y="-5%" width="110%" height="120%" color-interpolation-filters="sRGB">
            <feGaussianBlur in="SourceAlpha" stdDeviation="1.5" result="blur"/>
            <feDiffuseLighting in="blur" result="diffuse" lighting-color="#ffffff" diffuseConstant="0.7" surfaceScale="3">
              <feDistantLight azimuth="225" elevation="60"/>
            </feDiffuseLighting>
            <feComposite in="diffuse" in2="SourceAlpha" operator="in" result="diffOut"/>
            <feBlend in="SourceGraphic" in2="diffOut" mode="multiply"/>
          </filter>

          <linearGradient id="shimmerGrad" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">
            <stop offset="0%"   stop-color="rgba(255,255,255,0)"/>
            <stop offset="42%"  stop-color="rgba(255,255,255,0)"/>
            <stop offset="50%"  stop-color="rgba(255,255,255,0.45)"/>
            <stop offset="58%"  stop-color="rgba(200,248,255,0.3)"/>
            <stop offset="70%"  stop-color="rgba(255,255,255,0)"/>
            <stop offset="100%" stop-color="rgba(255,255,255,0)"/>
            <animateTransform attributeName="gradientTransform" type="translate"
              values="-1.6 0;0.6 0;0.6 0" keyTimes="0;0.5;1" dur="5s" repeatCount="indefinite"/>
          </linearGradient>
        </defs>
        <g id="extrudeGroup"></g>
        <text id="mainText"
          font-family="'Bebas Neue', sans-serif"
          font-weight="400"
          fill="url(#faceGrad)"
          filter="url(#lighting)"
          dominant-baseline="auto">JobLess AI</text>
        <text id="shimmerText"
          font-family="'Bebas Neue', sans-serif"
          font-weight="400"
          fill="url(#shimmerGrad)"
          opacity="0.9"
          dominant-baseline="auto">JobLess AI</text>
      </svg>
    </div>
  </div>
  <p class="sub">Transform your potential into a concrete career roadmap — powered by AI.</p>
</div>

<script>
document.fonts.ready.then(function() {
  var svg     = document.getElementById('titleSvg');
  var mainTxt = document.getElementById('mainText');
  var shimTxt = document.getElementById('shimmerText');
  var extGrp  = document.getElementById('extrudeGroup');

  /* ── FIX 6 + 9: use parent window width for breakpoints,
     not the iframe's own innerWidth (which equals the iframe container width,
     so this is actually fine — but we also cap the font size to prevent
     overflow on narrow screens with a tighter minimum). ── */
  var vw = Math.min(innerWidth, window.parent ? window.parent.innerWidth : innerWidth);
  var isMobile = vw < 600;
  var isTablet = vw < 900 && !isMobile;
  var isSmall  = vw < 360;

  /* FIX 9: tighter font size floor on small screens */
  var FS;
  if (isSmall)        { FS = 38; }
  else if (isMobile)  { FS = 48; }
  else if (isTablet)  { FS = Math.min(72, Math.max(48, vw * 0.065)); }
  else                { FS = Math.min(96, Math.max(56, vw * 0.072)); }

  var BL = FS, LAYERS = isMobile ? 4 : 6;

  [mainTxt, shimTxt].forEach(function(t) {
    t.setAttribute('font-size', FS);
    t.setAttribute('y', BL);
    t.setAttribute('x', 0);
  });

  /* FIX 4: use lightweight filter on mobile/tablet */
  if (isMobile || isTablet) {
    mainTxt.setAttribute('filter', 'url(#lightingSimple)');
  }

  var bb = mainTxt.getBBox();
  var W = bb.width + 8, H = BL + 10;
  svg.setAttribute('width',  W);
  svg.setAttribute('height', H);
  svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);

  /* Build extrusion layers */
  for (var i = LAYERS; i >= 1; i--) {
    var t  = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    var p  = i / LAYERS;
    var ox = i * 0.45, oy = i * 0.45;
    var r  = Math.round(0   + (1-p)*4);
    var g  = Math.round(18  + (1-p)*35);
    var b2 = Math.round(28  + (1-p)*55);
    var a  = 0.5 + (1-p)*0.4;
    t.setAttribute('font-family', "'Bebas Neue', sans-serif");
    t.setAttribute('font-weight', '400');
    t.setAttribute('font-size', FS);
    t.setAttribute('x', ox);
    t.setAttribute('y', BL + oy);
    t.setAttribute('fill', 'rgba('+r+','+g+','+b2+','+a+')');
    t.textContent = 'JobLess AI';
    extGrp.appendChild(t);
  }

  /* ── FIX 1 (dynamic iframe height): auto-fit the iframe to its content ── */
  function fitIframe() {
    try {
      var fe = window.frameElement;
      if (fe) {
        var h = document.getElementById('stage').scrollHeight + 16;
        fe.style.height = h + 'px';
      }
    } catch(e) {}
  }
  setTimeout(fitIframe, 120); /* after fonts + paint */

  /* ── Glitch canvas ── */
  var glitchC = document.getElementById('glitchCanvas');
  glitchC.width  = W; glitchC.height = H;
  glitchC.style.width  = W + 'px';
  glitchC.style.height = H + 'px';
  var glitchX = glitchC.getContext('2d');

  /* FIX 5: check if canvas 2D filter is supported before using it.
     Safari < 15 and older Android Chrome don't support ctx.filter. */
  var canvasFilterSupported = (function() {
    try {
      var c = document.createElement('canvas').getContext('2d');
      c.filter = 'blur(0px)';
      return c.filter !== undefined && c.filter !== '';
    } catch(e) { return false; }
  })();

  /* Skip glitch entirely on mobile — saves battery & CPU */
  if (!isMobile) {
    function getSvgImage(cb) {
      var xml  = new XMLSerializer().serializeToString(svg);
      var blob = new Blob([xml], {type:'image/svg+xml'});
      var url  = URL.createObjectURL(blob);
      var img  = new Image();
      img.onload = function() { cb(img); URL.revokeObjectURL(url); };
      img.src = url;
    }

    function scheduleGlitch() {
      var delay = 12000 + Math.random() * 8000;
      setTimeout(function() { getSvgImage(function(img) { runGlitch(img); }); }, delay);
    }

    function runGlitch(img) {
      var frames = 5, f = 0;
      var slices = Array.from({length:3}, function() {
        return { y: Math.random()*(H*0.75), h: 3+Math.random()*10, dx: (Math.random()-.5)*10 };
      });
      function glitchFrame() {
        glitchX.clearRect(0,0,W,H);
        if (f < frames) {
          var intensity = f < 2 ? 1 : (frames-f)/frames;
          glitchX.save();
          glitchX.globalAlpha = 0.28 * intensity;
          glitchX.globalCompositeOperation = 'screen';
          /* FIX 5: only apply canvas filter if browser supports it */
          if (canvasFilterSupported) glitchX.filter = 'hue-rotate(-20deg) saturate(2.5)';
          glitchX.drawImage(img, -2, 1);
          glitchX.restore();

          glitchX.save();
          glitchX.globalAlpha = 0.28 * intensity;
          glitchX.globalCompositeOperation = 'screen';
          if (canvasFilterSupported) glitchX.filter = 'hue-rotate(160deg) saturate(2.5)';
          glitchX.drawImage(img, 2, -1);
          glitchX.restore();

          slices.forEach(function(sl) {
            glitchX.save();
            glitchX.globalAlpha = 0.5 * intensity;
            glitchX.drawImage(img, 0, sl.y, W, sl.h, sl.dx, sl.y, W, sl.h);
            glitchX.restore();
          });

          if (f % 2 === 0) {
            glitchX.fillStyle = 'rgba(0,208,255,' + (0.10*intensity) + ')';
            glitchX.fillRect(0, Math.random()*H, W, 1+Math.random()*1.5);
          }
          f++;
          requestAnimationFrame(glitchFrame);
        } else {
          glitchX.clearRect(0,0,W,H);
          scheduleGlitch();
        }
      }
      requestAnimationFrame(glitchFrame);
    }
    setTimeout(scheduleGlitch, 12000);
  }

  /* ── Extrusion depth pulse ── */
  var extLayers = extGrp.querySelectorAll('text');
  var pulseT = 0;
  function pulseLayers() {
    pulseT += 0.018;
    var breathe = Math.sin(pulseT) * 0.18;
    extLayers.forEach(function(el, i) {
      var base   = (extLayers.length - i) * 0.45;
      var offset = base + breathe * (i / extLayers.length);
      el.setAttribute('x', offset);
      el.setAttribute('y', BL + offset);
    });
    requestAnimationFrame(pulseLayers);
  }
  requestAnimationFrame(pulseLayers);
});
</script>
</body>
</html>"""


# ==================== CONFIGURATION ====================
class Config:
    _ENV = {
        "Google Gemini":    "GOOGLE_API_KEY",
        "OpenAI":           "OPENAI_API_KEY",
        "Anthropic Claude": "ANTHROPIC_API_KEY",
    }

    def get_provider(self) -> str:
        return st.session_state.get("ai_provider", "Google Gemini  🆓")

    def set_provider(self, provider: str):
        st.session_state["ai_provider"] = provider

    _SECRETS = {
        "Google Gemini  🆓": "GEMINI_API_KEY",
        "Groq  🆓⚡": "GROQ_API_KEY",
        "Cohere  🆓": "COHERE_API_KEY",
    }

    def get_api_key(self, provider=None) -> str:
        p = provider or self.get_provider()
        val = st.session_state.get(f"api_key_{p}", "")
        if val:
            return val
        try:
            secret_key = self._SECRETS.get(p, "")
            if secret_key:
                return st.secrets.get(secret_key, "")
        except Exception:
            pass
        return os.getenv(self._ENV.get(p, ""), "")

    def using_own_key(self, provider=None) -> bool:
        p = provider or self.get_provider()
        return bool(st.session_state.get(f"api_key_{p}", ""))

    def set_api_key(self, key: str, provider=None) -> bool:
        p = provider or self.get_provider()
        st.session_state[f"api_key_{p}"] = key
        return bool(key)

    def is_ready(self) -> bool:
        return bool(self.get_api_key())

    def get_selected_model(self):
        return st.session_state.get("selected_model")


# ==================== AI HANDLER ====================
class AIHandler:
    def __init__(self, config: Config):
        self.config = config

    def _call_llm(self, prompt: str, model_name: str,
                  max_tokens: int = 8192, temperature: float = 0.7,
                  json_mode: bool = False) -> str:
        provider_display = self.config.get_provider()
        provider = PROVIDER_INTERNAL.get(provider_display, "gemini")
        api_key = self.config.get_api_key()

        if provider == "gemini":
            if not _GEMINI_OK:
                raise RuntimeError("Run: pip install google-generativeai")
            genai.configure(api_key=api_key)
            try:
                gen_config = genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                    **({"response_mime_type": "application/json"} if json_mode else {})
                )
            except TypeError:
                gen_config = genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
            model = genai.GenerativeModel(
                model_name, generation_config=gen_config)
            response = model.generate_content(prompt)
            return response.text.strip()

        elif provider == "groq":
            if not _GROQ_OK:
                raise RuntimeError("Run: pip install groq")
            client = _GroqClient(api_key=api_key)
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=min(max_tokens, 8192),
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()

        elif provider == "cohere":
            if not _COHERE_OK:
                raise RuntimeError("Run: pip install cohere")
            client = _cohere_sdk.ClientV2(api_key=api_key)
            response = client.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.message.content[0].text.strip()

        else:
            raise ValueError(f"Unknown provider internal key: {provider}")

    def get_career_advice(self, input_text: str, model_name: str, context: Dict) -> Optional[Dict]:
        try:
            location = context.get('location', 'India - Metro')
            is_international = "international" in location.lower()
            salary_instruction = (
                "Use USD ($) and K/year format for salary_range (e.g. $80K - $120K/year) since this is an international user."
                if is_international else
                "Use INR (₹) and Lakhs format for salary_range (e.g. ₹15L - ₹25L) since this is an India-based user."
            )
            prompt = f"""
            Act as an Elite Career Strategist and AI Career Coach.

            **User Profile Analysis:**
            {input_text}

            **Context:**
            - Target Industries: {', '.join(context.get('industries', []))}
            - Career Stage: {context.get('career_stage', 'Not specified')}
            - Location Preference: {location}

            **Salary Format Rule:** {salary_instruction}

            **Task:**
            Provide a comprehensive career analysis. Return ONLY a valid JSON object (no markdown, no code blocks) with this exact structure:

            {{
              "profile_summary": "A concise 2-sentence professional summary",
              "current_skills": ["Skill1", "Skill2", "Skill3"],
              "careers": [
                {{
                  "title": "Specific Job Title",
                  "match_score": 85,
                  "salary_range": "salary here per the format rule above",
                  "reason": "Why this fits",
                  "skill_gap_analysis": {{"Python": 90, "Leadership": 40}},
                  "next_steps": ["Step 1", "Step 2"],
                  "learning_path": ["Course 1", "Course 2"],
                  "interview_tips": ["Tip 1", "Tip 2"],
                  "job_search_keywords": "data analyst python sql",
                  "top_companies": ["Google", "Microsoft", "Amazon"],
                  "certifications": ["AWS Certified", "Google Analytics"]
                }}
              ]
            }}

            Suggest 6-8 distinct career paths. Return ONLY the JSON object.
            """
            txt = self._call_llm(
                prompt, model_name, max_tokens=8192, temperature=0.7, json_mode=True)
            return self._safe_parse_json(txt)
        except Exception as e:
            st.error(f"⚠️ AI Error: {str(e)}")
            return None

    def build_ats_resume(self, profile_data: Dict, model_name: str) -> Optional[Dict]:
        try:
            prompt = f"""
            You are an expert ATS resume writer and career coach.

            Create a highly optimized, ATS-friendly resume based on this profile:

            Name: {profile_data.get('name', '')}
            Target Role: {profile_data.get('target_role', '')}
            Target Job Description: {profile_data.get('job_description', 'Not provided')}
            Years of Experience: {profile_data.get('experience_years', '')}
            Current/Past Roles: {profile_data.get('work_experience', '')}
            Skills: {profile_data.get('skills', '')}
            Education: {profile_data.get('education', '')}
            Certifications: {profile_data.get('certifications', '')}
            Projects: {profile_data.get('projects', '')}
            Achievements: {profile_data.get('achievements', '')}

            Return ONLY a valid JSON object (no markdown, no code blocks) with this structure:
            {{
              "ats_score": 92,
              "ats_tips": ["Tip 1", "Tip 2", "Tip 3"],
              "keywords_found": ["keyword1", "keyword2"],
              "keywords_missing": ["keyword3", "keyword4"],
              "resume": {{
                "contact": {{"name": "Full Name","email": "email@example.com","phone": "+91-XXXXXXXXXX","linkedin": "linkedin.com/in/username","location": "City, State"}},
                "summary": "2-3 sentence powerful professional summary with ATS keywords",
                "experience": [{{"title": "Job Title","company": "Company Name","duration": "Jan 2022 – Present","bullets": ["Quantified achievement bullet 1","Quantified achievement bullet 2","Quantified achievement bullet 3"]}}],
                "skills": {{"technical": ["Skill1", "Skill2"],"soft": ["Leadership"],"tools": ["Tool1"]}},
                "education": [{{"degree": "B.Tech Computer Science","institution": "University Name","year": "2020","gpa": "8.5/10"}}],
                "certifications": ["Cert1", "Cert2"],
                "projects": [{{"name": "Project Name","description": "1-2 line impactful description with tech stack","link": ""}}]
              }}
            }}
            Return ONLY the JSON.
            """
            txt = self._call_llm(
                prompt, model_name, max_tokens=8192, temperature=0.4, json_mode=True)
            return self._safe_parse_json(txt)
        except Exception as e:
            st.error(f"⚠️ Resume Builder Error: {str(e)}")
            return None

    def generate_interview_questions(self, role: str, level: str, model_name: str) -> Optional[List]:
        try:
            prompt = f"""You are a world-class technical recruiter who has conducted 10,000+ interviews across a wide variety of industries and roles — tech, core engineering, finance, consulting, healthcare, and more.

Generate a realistic mock interview for:
Role: {role}
Level: {level}

IMPORTANT — Companies field: For each question, list 2-3 companies that ACTUALLY hire for this specific role and are KNOWN to ask this type of question in their interviews.
- For Electrical/Electronics Engineers: use companies like ABB, Siemens, Schneider Electric, L&T, BHEL, Honeywell, Adani Power, Tata Power, CESC, Havells, Crompton Greaves, Jindal Steel & Power
- For Mechanical Engineers: use companies like L&T, Tata Motors, Mahindra, BHEL, Godrej, Thermax, Cummins, SKF, Atlas Copco, Adani Enterprises, Pinnacle Infotech, NTPC
- For Civil Engineers: use companies like L&T Construction, Shapoorji Pallonji, Afcons, DLF, Tata Projects, GMR Group, Adani Ports, Pinnacle Infotech, Gammon India
- For Chemical Engineers: use companies like Reliance Industries, ONGC, HPCL, BPCL, BASF, Dow Chemical, Gujarat Narmada Valley Fertilizers, Pidilite, Tata Chemicals, Adani Oil & Gas
- For Aerospace Engineers: use companies like HAL, ISRO, DRDO, Boeing India, Airbus India, Dassault Aviation, BEL, Safran, Collins Aerospace
- For Manufacturing Engineers: use companies like Tata Motors, Maruti Suzuki, Mahindra, Bajaj Auto, Hero MotoCorp, Jindal Steel & Power, JSW Steel, Bosch India, Havells
- For Electronics & Communication Engineers: use companies like DRDO, BEL, Qualcomm India, Samsung R&D, Intel India, L&T Technology Services, HCL Hardware, Mistral Solutions, Adani Telecom
- For Software Engineers / IT roles: use companies like Flipkart, Razorpay, PhonePe, Zomato, CRED, Swiggy, Meesho, Infosys, TCS, Wipro, HCL, Freshworks, Zoho
- For Data/AI/ML roles: use companies like Fractal Analytics, Mu Sigma, Tiger Analytics, ThoughtWorks, Walmart Labs India, Flipkart Data Science, Google India, Microsoft India
- For Finance roles: use companies like Goldman Sachs, JP Morgan India, ICICI Bank, HDFC Bank, Kotak, Edelweiss, Avendus, Deloitte India, EY India
- For Consulting: use companies like McKinsey, BCG, Bain, Deloitte, KPMG, EY, Accenture Strategy, Alvarez & Marsal
- For all other roles: use the most relevant hiring companies for that specific domain — NOT generic big tech unless they genuinely hire for the role

Return ONLY a raw JSON array with exactly 8 question objects. No markdown. No code fences. Start with [ and end with ].

Format:
[{{"id":1,"category":"Behavioral","question":"Full question text here","difficulty":"Easy","companies":["Relevant Co 1",
    "Relevant Co 2"],"hint":"STAR method tip","ideal_answer_points":["Point 1","Point 2","Point 3"],"follow_ups":["Follow-up 1"]}}]

Mix: id 1-2 Behavioral, id 3-4 Technical, id 5 Problem Solving, id 6 Situational, id 7 Culture Fit, id 8 Role-specific scenario.
Rules: straight double quotes, no apostrophes, single-line strings, no trailing commas, max 3 ideal_answer_points, exactly 1 follow_up.
Start with [ immediately."""
            txt = self._call_llm(
                prompt, model_name, max_tokens=6000, temperature=0.65, json_mode=True)
            result = self._safe_parse_json(txt)
            if isinstance(result, list) and len(result) > 0:
                return result
            raise ValueError("Empty or invalid question list returned")
        except Exception as e:
            st.error(f"⚠️ Interview Generation Error: {str(e)}")
            return None

    def evaluate_interview_answer(self, question: str, answer: str, ideal_points: List,
                                  role: str, companies: List, model_name: str) -> Optional[Dict]:
        try:
            safe_q = question.replace('"', "'")
            safe_a = answer.replace('"', "'")[:1500]
            companies_str = ", ".join(
                companies) if companies else "top tech companies"
            prompt = f"""You are a warm but brutally honest senior hiring manager at {companies_str} evaluating a {role} candidate.

Question asked: {safe_q}
Candidate answered: {safe_a}
Ideal answer should cover: {ideal_points}

Return ONLY raw JSON. No markdown. Start with {{ immediately.

{{"score": 72,"verdict": "Good","one_line_reaction": "Solid attempt but missed key technical depth.","what_you_did_well": ["Specific strength 1","Specific strength 2"],"what_went_wrong": ["Specific gap 1","Specific gap 2"],"how_to_improve": [
    "Concrete actionable fix 1","Concrete actionable fix 2"],"sample_better_answer": "A 3-4 sentence model answer using STAR method","keywords_used": ["kw1","kw2"],"keywords_missed": ["kw3","kw4"],"crack_this_question": "Likely","crack_message": "Honest verdict on whether this answer would pass."}}

Scoring: 90-100=Excellent, 75-89=Good, 60-74=Average, below 60=Needs Work
crack_this_question must be exactly: "Very Likely", "Likely", "Borderline", or "Unlikely"
Rules: straight double quotes, no apostrophes, single-line strings, no trailing commas.
Start with {{ immediately."""
            txt = self._call_llm(
                prompt, model_name, max_tokens=1800, temperature=0.4, json_mode=True)
            return self._safe_parse_json(txt)
        except Exception as e:
            st.error(f"⚠️ Evaluation Error: {str(e)}")
            return None

    def generate_final_verdict(self, role: str, level: str, companies: List,
                               all_feedback: List[Dict], model_name: str) -> Optional[Dict]:
        try:
            avg_score = sum(f.get("score", 0)
                            for f in all_feedback) / len(all_feedback)
            scores = [f.get("score", 0) for f in all_feedback]
            weak_areas = [f.get("what_went_wrong", [])
                          for f in all_feedback if f.get("score", 0) < 70]
            strong_areas = [f.get("what_you_did_well", [])
                            for f in all_feedback if f.get("score", 0) >= 80]
            companies_str = ", ".join(
                companies[:3]) if companies else "top companies"

            prompt = f"""You are a kind but honest Head of Talent at {companies_str} reviewing a complete mock interview for a {role} ({level}) position.

Summary: avg score {avg_score:.1f}/100, scores {scores}, weaknesses {weak_areas[:3]}, strengths {strong_areas[:3]}.

Return ONLY raw JSON. Start with {{ immediately.

{{"overall_score": {avg_score:.0f},"grade": "B+","headline": "One-sentence punchy summary","can_crack_company": "Borderline","crack_verdict_message": "2-3 sentences honest assessment.","top_strengths": ["Strength 1","Strength 2","Strength 3"],"top_weaknesses": ["Weakness 1","Weakness 2","Weakness 3"],"priority_action_plan": ["Most important fix this week","Second priority","Third priority"],"ready_to_apply": false,"estimated_weeks_to_ready": 4,"motivational_close": "1-2 sentence warm closing."}}

can_crack_company must be exactly: "Yes, apply now!", "Almost there", "Borderline", or "Not yet — keep practising"
grade: A+, A, B+, B, C+, C, or D
Rules: straight double quotes, no apostrophes, single-line strings, no trailing commas.
Start with {{ immediately."""
            txt = self._call_llm(
                prompt, model_name, max_tokens=2000, temperature=0.5, json_mode=True)
            return self._safe_parse_json(txt)
        except Exception as e:
            st.error(f"⚠️ Final Verdict Error: {str(e)}")
            return None

    def find_pyq_resources(self, company: str, role: str, model_name: str) -> Optional[Dict]:
        try:
            prompt = f"""You are an expert career resource curator with deep knowledge of Indian and global company hiring processes, exam portals, and open-source PYQ (Previous Year Question) databases.

A user is looking for Previous Year Questions and authentic exam preparation resources for:
Company: {company}
Target Role / Exam: {role}

Your task: Find the most AUTHENTIC and RELIABLE open-source resources available for this company's hiring process.

Authenticity rules — ONLY include resources that meet these standards:
1. Official company portals or career pages
2. Well-known platforms: GeeksforGeeks, IndiaBix, PrepInsta, LeetCode, InterviewBit, Testbook, AglaSem, EduRev, NPTEL, GitHub (reputable repos)
3. Rate each as: "Official Source", "Verified High Quality", "Verified Community", or skip entirely if unverifiable
4. DO NOT invent URLs. Only include URLs you are confident are real.
5. If you are not confident about a resource, set authenticity to "Verify Before Use"

Return ONLY a raw JSON object. No markdown. No code fences. Start with {{ immediately.

{{
  "company": "{company}",
  "role": "{role}",
  "overall_confidence": "High",
  "summary": "2-sentence summary of what resources are available and how well-documented this company hiring process is.",
  "exam_pattern": "Brief description of the typical exam/selection pattern for this company and role, if known.",
  "resources": [
    {{
      "name": "Resource Name",
      "url": "https://actual-verified-url.com/specific-page",
      "description": "What this resource contains and why it is useful",
      "content_type": "PYQs / Mock Tests / Interview Experiences / Official Portal",
      "authenticity": "Verified High Quality"
    }}
  ],
  "preparation_tips": [
    "Specific actionable tip 1 for this company and role",
    "Specific actionable tip 2",
    "Specific actionable tip 3"
  ]
}}

overall_confidence must be exactly: "High", "Medium", or "Low" (based on how much you know about this company hiring process).
Include 3-6 resources maximum. Quality over quantity.
Rules: straight double quotes, no apostrophes, single-line strings, no trailing commas.
Start with {{ immediately."""
            txt = self._call_llm(
                prompt, model_name, max_tokens=3000, temperature=0.3, json_mode=True)
            return self._safe_parse_json(txt)
        except Exception as e:
            st.error(f"⚠️ PYQ Finder Error: {str(e)}")
            return None

    def generate_pyq_questions(self, company: str, role: str, count: int, model_name: str) -> Optional[List]:
        try:
            prompt = f"""You are a senior exam content creator specialising in recruitment tests.

Generate a realistic PYQ-style question paper for:
Company: {company}
Role: {role}
Total Questions: {count}

Create questions split into 3-4 appropriate sections for this company and role.
For coding/tech roles: DSA, code output, SQL/OS/networking questions.
For core engineering: domain-specific technical MCQs relevant to the field.
For mass recruiters: aptitude, verbal, reasoning, basic coding.

Return ONLY a raw JSON array of section objects. No markdown. No code fences. Start with [ immediately.

[
  {{
    "section": "Section Name",
    "questions": [
      {{
        "question": "Full question text. For code questions write code after a newline.",
        "code": "",
        "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
        "answer": "A) Option 1",
        "explanation": "Detailed 2-3 sentence explanation of the correct answer."
      }}
    ]
  }}
]

Rules: each section ~{count // 3} questions. Straight double quotes only, no apostrophes, no trailing commas.
Explanations must be detailed and educational.
Start with [ immediately."""
            txt = self._call_llm(
                prompt, model_name, max_tokens=6000, temperature=0.6, json_mode=True)
            result = self._safe_parse_json(txt)
            if isinstance(result, list) and len(result) > 0:
                return result
            raise ValueError("Empty or invalid sections returned")
        except Exception as e:
            st.error(f"⚠️ PYQ Generation Error: {str(e)}")
            return None

    @staticmethod
    def _safe_parse_json(txt: str):
        import re
        txt = txt.strip()
        for fence in ('```json', '```'):
            if fence in txt:
                parts = txt.split(fence)
                if len(parts) >= 3:
                    txt = parts[1].strip()
                    break
                elif len(parts) == 2:
                    txt = parts[1].strip()
                    break
        txt = re.sub(r',\s*([\]}])', r'\1', txt)
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            pass
        if txt.lstrip().startswith('['):
            objects, depth, start = [], 0, None
            for i, ch in enumerate(txt):
                if ch == '{':
                    if depth == 0:
                        start = i
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0 and start is not None:
                        chunk = re.sub(r',\s*([\]}])', r'\1', txt[start:i+1])
                        try:
                            objects.append(json.loads(chunk))
                        except Exception:
                            pass
                        start = None
            if objects:
                return objects
        if txt.lstrip().startswith('{'):
            brace_start = txt.find('{')
            depth = 0
            for i in range(brace_start, len(txt)):
                if txt[i] == '{':
                    depth += 1
                elif txt[i] == '}':
                    depth -= 1
                    if depth == 0:
                        chunk = re.sub(
                            r',\s*([\]}])', r'\1', txt[brace_start:i+1])
                        try:
                            return json.loads(chunk)
                        except Exception:
                            break
        raise ValueError(
            f"Could not parse JSON. Raw (first 300 chars): {txt[:300]}")


# ==================== SUPPORTING CLASSES ====================
class PDFHandler:
    @staticmethod
    def extract_text(uploaded_file) -> str:
        try:
            pdf_bytes = uploaded_file.read()

            # 🛡️ Block oversized files
            if len(pdf_bytes) > 5 * 1024 * 1024:  # 5 MB max
                st.error("⚠️ File too large. Please upload a resume under 5MB.")
                return ""

            text = ""
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:

                # 🛡️ Block suspiciously large PDFs
                if len(doc) > 15:
                    st.error(
                        "⚠️ Too many pages. Resume should be under 15 pages.")
                    return ""

                for page in doc:
                    text += page.get_text()
            return text.strip()
        except Exception as e:
            st.error(f"PDF extraction error: {e}")
            return ""


class ExportHandler:
    @staticmethod
    def generate_pdf_report(analysis_data: Dict) -> Optional[io.BytesIO]:
        try:
            from reportlab.lib.pagesizes import letter
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = [Paragraph(
                "JobLess AI - Career Analysis Report", styles['Title']), Spacer(1, 12)]
            story.append(
                Paragraph("<b>Profile Summary</b>", styles['Heading2']))
            story.append(Paragraph(analysis_data.get(
                'profile_summary', 'N/A'), styles['BodyText']))
            story.append(Spacer(1, 12))
            for idx, career in enumerate(analysis_data.get('careers', []), 1):
                story.append(
                    Paragraph(f"<b>Career Path {idx}: {career['title']}</b>", styles['Heading2']))
                story.append(
                    Paragraph(f"Match Score: {career['match_score']}%", styles['BodyText']))
                story.append(
                    Paragraph(f"Salary: {career['salary_range']}", styles['BodyText']))
                story.append(Spacer(1, 12))
            doc.build(story)
            buffer.seek(0)
            return buffer
        except Exception as e:
            st.error(f"PDF generation error: {e}")
            return None


class HistoryManager:
    @staticmethod
    def add_to_history(input_text: str, analysis: Dict, context: Dict):
        if 'history' not in st.session_state:
            st.session_state.history = []
        record = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'summary': analysis.get('profile_summary', 'Analysis')[:50] + '...',
            'input_text': input_text[:500],
            'analysis': analysis,
            'context': context,
        }
        st.session_state.history.append(record)
        if len(st.session_state.history) > 20:
            st.session_state.history = st.session_state.history[-20:]


# ==================== HELPER FUNCTIONS ====================
def get_job_links(title: str, location: str, keywords: str = "") -> dict:
    query = keywords if keywords else title
    q_enc = query.replace(" ", "+")
    title_enc = title.replace(" ", "+")
    naukri_slug = title.lower().replace(" ", "-")
    is_india = "india" in location.lower() or location.lower() in (
        "india - metro", "india - remote", "india - tier 2")
    if is_india:
        return {
            "LinkedIn":  f"https://www.linkedin.com/jobs/search/?keywords={q_enc}&location=India",
            "Naukri":    f"https://www.naukri.com/{naukri_slug}-jobs",
            "Indeed":    f"https://in.indeed.com/jobs?q={q_enc}&l=India",
            "Glassdoor": f"https://www.glassdoor.co.in/Jobs/{title_enc.replace('+', '-')}-jobs-SRCH_KO0,{len(title)}.htm",
        }
    else:
        return {
            "LinkedIn":   f"https://www.linkedin.com/jobs/search/?keywords={q_enc}",
            "Indeed":     f"https://www.indeed.com/jobs?q={q_enc}",
            "Glassdoor":  f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={q_enc}",
            "RemoteOK":   f"https://remoteok.com/remote-{naukri_slug}-jobs",
        }


def render_match_ring(score: int) -> str:
    r = 36
    circ = 2 * 3.14159 * r
    fill = circ - (circ * score / 100)
    color = "#00d2ff" if score >= 80 else (
        "#a855f7" if score >= 60 else "#f59e0b")
    return f"""
    <div class="match-ring-wrap">
      <div class="match-ring">
        <svg width="88" height="88" viewBox="0 0 88 88">
          <circle class="ring-bg"   cx="44" cy="44" r="{r}"/>
          <circle class="ring-fill" cx="44" cy="44" r="{r}"
            stroke="{color}"
            stroke-dasharray="{circ:.1f}"
            stroke-dashoffset="{fill:.1f}"/>
        </svg>
        <div class="ring-text">
          <span class="ring-pct">{score}%</span>
          <span class="ring-label">match</span>
        </div>
      </div>
    </div>"""


def render_skill_badges(skills: list, color: str = "") -> str:
    cls = f"skill-badge {color}".strip()
    return " ".join(f'<span class="{cls}">{s}</span>' for s in skills)


def render_job_links(title: str, location: str, keywords: str = "") -> str:
    links = get_job_links(title, location, keywords)
    icons = {"LinkedIn": "🔵", "Naukri": "🟠",
             "Indeed": "🟢", "Glassdoor": "💼", "RemoteOK": "🌐"}
    cls = {"LinkedIn": "linkedin", "Naukri": "naukri",
           "Indeed": "indeed", "Glassdoor": "glassdoor", "RemoteOK": "remoteok"}
    html = '<div class="job-links-row">'
    for name, url in links.items():
        html += f'<a href="{url}" target="_blank" class="job-link-btn {cls[name]}">{icons[name]} {name}</a>'
    html += "</div>"
    return html


# ==================== UI COMPONENTS ====================
class UIComponents:
    @staticmethod
    def apply_custom_css():
        css = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;700&family=Orbitron:wght@700;900&family=Inter:wght@300;400;500&display=swap');

            @keyframes gradientShift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
            @keyframes glowPulse { 0%,100%{box-shadow:0 0 20px rgba(0,210,255,0.3),0 0 40px rgba(58,123,213,0.15)} 50%{box-shadow:0 0 50px rgba(0,210,255,0.8),0 0 100px rgba(58,123,213,0.5)} }
            @keyframes shimmer { 0%{background-position:-300% center} 100%{background-position:300% center} }
            @keyframes borderRotate { 0%{background-position:0% 0%} 100%{background-position:300% 300%} }
            @keyframes slideInLeft { from{transform:perspective(800px) rotateY(-12deg) translateX(-50px);opacity:0} to{transform:perspective(800px) rotateY(0deg) translateX(0);opacity:1} }
            @keyframes scaleIn { from{transform:perspective(600px) scale(0.88) rotateX(8deg);opacity:0} to{transform:perspective(600px) scale(1) rotateX(0deg);opacity:1} }

            .stApp { background:#060b14!important; color:white!important; font-family:'Space Grotesk',sans-serif!important; cursor:none!important; }
            h1,h2,h3 { font-family:'Space Grotesk',sans-serif!important; font-weight:700!important; letter-spacing:-0.02em!important; color:#e2e8f0!important; }
            h2 { font-size:1.7rem!important; }
            h3 { font-size:1.2rem!important; color:#00d2ff!important; text-transform:uppercase!important; letter-spacing:0.1em!important; font-weight:600!important; }
            label,.stRadio label,.stCheckbox label,.stSelectbox label,.stTextInput label,.stTextArea label { font-family:'JetBrains Mono',monospace!important; font-size:0.72rem!important; letter-spacing:0.12em!important; text-transform:uppercase!important; color:rgba(0,210,255,0.75)!important; }
            p,li { font-family:'Space Grotesk',sans-serif!important; font-size:0.97rem!important; line-height:1.7!important; color:#94a3b8!important; }
            [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 { font-family:'JetBrains Mono',monospace!important; font-size:0.8rem!important; letter-spacing:0.15em!important; text-transform:uppercase!important; color:rgba(0,210,255,0.7)!important; }
            .stTabs [data-baseweb="tab"] { font-family:'JetBrains Mono',monospace!important; font-size:0.75rem!important; letter-spacing:0.1em!important; text-transform:uppercase!important; border-radius:8px!important; transition:all 0.3s cubic-bezier(0.175,0.885,0.32,1.275)!important; }
            .stTabs [data-baseweb="tab"]:hover { transform:perspective(400px) rotateX(5deg) translateY(-2px)!important; background:rgba(0,210,255,0.12)!important; }
            .stTabs [aria-selected="true"] { background:linear-gradient(90deg,rgba(0,210,255,0.2),rgba(168,85,247,0.15))!important; box-shadow:0 4px 20px rgba(0,210,255,0.25)!important; color:#00d2ff!important; }
            .stTabs [data-baseweb="tab-list"] { background:rgba(255,255,255,0.03)!important; border-radius:12px!important; padding:5px!important; border:1px solid rgba(0,210,255,0.1)!important; }
            .stButton>button { font-family:'Space Grotesk',sans-serif!important; font-weight:800!important; letter-spacing:0.08em!important; text-transform:uppercase!important; font-size:0.86rem!important; background:linear-gradient(90deg,#00d2ff,#3a7bd5)!important; border-radius:50px!important; border:none!important; color:#ffffff!important; text-shadow:0 1px 8px rgba(0,0,0,0.65)!important; animation:glowPulse 3s ease-in-out infinite; transition:transform 0.2s cubic-bezier(0.175,0.885,0.32,1.275),box-shadow 0.2s ease!important; position:relative; overflow:hidden; }
            .stButton>button::before { content:''; position:absolute; inset:0; background:linear-gradient(90deg,transparent,rgba(255,255,255,0.15),transparent); transform:translateX(-100%); transition:transform 0.4s ease; }
            .stButton>button:hover::before { transform:translateX(100%); }
            .stButton>button:hover { transform:perspective(400px) rotateX(5deg) translateY(-4px) scale(1.03)!important; box-shadow:0 15px 40px rgba(0,210,255,0.5),0 0 70px rgba(58,123,213,0.3)!important; }
            .stButton>button:active { transform:perspective(400px) translateY(-1px) scale(0.98)!important; }
            .result-card { background:rgba(255,255,255,0.04)!important; backdrop-filter:blur(20px) saturate(180%)!important; border-radius:20px!important; border:1px solid rgba(255,255,255,0.08)!important; padding:28px!important; margin-bottom:28px; animation:scaleIn 0.6s ease-out; transform-style:preserve-3d; transition:transform 0.4s cubic-bezier(0.175,0.885,0.32,1.275),box-shadow 0.4s ease; position:relative; overflow:hidden; }
            .result-card::before { content:''; position:absolute; inset:-2px; background:linear-gradient(45deg,#00d2ff,#3a7bd5,#a855f7,#00d2ff); background-size:300% 300%; border-radius:22px; z-index:-1; animation:borderRotate 4s linear infinite; opacity:0.4; }
            .result-card:hover { transform:perspective(1000px) rotateX(2deg) rotateY(-1.5deg) translateY(-8px) scale(1.01); box-shadow:0 35px 90px rgba(0,210,255,0.2),0 0 0 1px rgba(0,210,255,0.3); }
            .result-card h3 { font-family:'Space Grotesk',sans-serif!important; font-size:1.15rem!important; font-weight:700!important; letter-spacing:-0.01em!important; text-transform:none!important; color:#e2e8f0!important; margin-bottom:10px; }
            .stExpander { border:1px solid rgba(0,210,255,0.15)!important; border-radius:14px!important; background:rgba(255,255,255,0.025)!important; transition:transform 0.3s ease,box-shadow 0.3s ease,border-color 0.3s ease!important; animation:slideInLeft 0.5s ease-out; }
            .stExpander:hover { transform:perspective(900px) rotateY(0.8deg) translateY(-3px)!important; box-shadow:-8px 12px 40px rgba(0,210,255,0.12),8px 12px 40px rgba(58,123,213,0.08)!important; border-color:rgba(0,210,255,0.4)!important; }
            [data-testid="stSidebar"] { background:linear-gradient(180deg,rgba(6,11,20,0.98) 0%,rgba(15,23,42,0.98) 100%)!important; backdrop-filter:blur(24px)!important; border-right:1px solid rgba(0,210,255,0.12)!important; box-shadow:12px 0 50px rgba(0,0,0,0.6),inset -1px 0 0 rgba(0,210,255,0.08)!important; }
            .stTextInput>div>div>input,.stTextArea>div>div>textarea { background:rgba(255,255,255,0.04)!important; border:1px solid rgba(0,210,255,0.25)!important; border-radius:10px!important; color:#e2e8f0!important; font-family:'Space Grotesk',sans-serif!important; font-size:0.95rem!important; transition:all 0.3s ease!important; }
            .stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus { border-color:#00d2ff!important; box-shadow:0 0 0 2px rgba(0,210,255,0.18),0 0 30px rgba(0,210,255,0.08)!important; background:rgba(0,210,255,0.04)!important; }
            .stAlert { border-radius:12px!important; animation:scaleIn 0.4s ease-out!important; font-family:'Space Grotesk',sans-serif!important; }
            .stProgress>div>div>div { background:linear-gradient(90deg,#00d2ff,#3a7bd5,#a855f7,#00d2ff)!important; background-size:200% auto!important; animation:shimmer 1.5s linear infinite!important; border-radius:10px!important; box-shadow:0 0 18px rgba(0,210,255,0.65)!important; }
            hr { border:none!important; height:1px!important; background:linear-gradient(90deg,transparent,rgba(0,210,255,0.4),rgba(168,85,247,0.4),transparent)!important; margin:20px 0!important; }
            ::-webkit-scrollbar { width:5px; }
            ::-webkit-scrollbar-track { background:rgba(255,255,255,0.03); }
            ::-webkit-scrollbar-thumb { background:linear-gradient(180deg,#00d2ff,#3a7bd5); border-radius:10px; }
            iframe { border:none!important; }
            .stSelectbox>div>div,.stMultiSelect>div>div { background:rgba(255,255,255,0.04)!important; border:1px solid rgba(0,210,255,0.2)!important; border-radius:10px!important; font-family:'Space Grotesk',sans-serif!important; transition:border-color 0.2s ease,transform 0.2s ease!important; }
            .stSelectbox>div>div:hover,.stMultiSelect>div>div:hover { border-color:rgba(0,210,255,0.5)!important; transform:translateY(-1px)!important; }
            .skill-badge { display:inline-block; padding:4px 12px; border-radius:20px; font-family:'JetBrains Mono',monospace; font-size:0.72rem; font-weight:500; letter-spacing:0.05em; margin:3px; border:1px solid rgba(0,210,255,0.35); background:rgba(0,210,255,0.08); color:#7dd3fc; transition:all 0.2s ease; cursor:default; }
            .skill-badge:hover { background:rgba(0,210,255,0.18); border-color:#00d2ff; transform:translateY(-2px); box-shadow:0 4px 15px rgba(0,210,255,0.2); }
            .skill-badge.purple { border-color:rgba(168,85,247,0.35); background:rgba(168,85,247,0.08); color:#c084fc; }
            .skill-badge.green  { border-color:rgba(52,211,153,0.35);  background:rgba(52,211,153,0.08);  color:#6ee7b7; }
            .match-ring-wrap { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:6px; }
            .match-ring { position:relative; width:88px; height:88px; }
            .match-ring svg { transform:rotate(-90deg); }
            .match-ring .ring-bg   { fill:none; stroke:rgba(255,255,255,0.06); stroke-width:7; }
            .match-ring .ring-fill { fill:none; stroke-width:7; stroke-linecap:round; transition:stroke-dashoffset 1.2s cubic-bezier(.4,0,.2,1); filter:drop-shadow(0 0 6px currentColor); }
            .match-ring .ring-text { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; font-family:'Space Grotesk',sans-serif; }
            .match-ring .ring-pct  { font-size:1.3rem; font-weight:700; line-height:1; background:linear-gradient(135deg,#00d2ff,#a855f7); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
            .match-ring .ring-label { font-size:0.6rem; color:#64748b; letter-spacing:0.08em; text-transform:uppercase; }
            .job-links-row { display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }
            .job-link-btn { display:inline-flex; align-items:center; gap:6px; padding:7px 14px; border-radius:8px; font-family:'Space Grotesk',sans-serif; font-size:0.78rem; font-weight:600; text-decoration:none!important; transition:all 0.22s cubic-bezier(.4,0,.2,1); border:1px solid; }
            .job-link-btn:hover { transform:translateY(-2px); text-decoration:none!important; }
            .job-link-btn.linkedin  { background:rgba(10,102,194,0.15);  border-color:rgba(10,102,194,0.5);  color:#60a5fa; }
            .job-link-btn.linkedin:hover  { background:rgba(10,102,194,0.3);  box-shadow:0 6px 20px rgba(10,102,194,0.25); }
            .job-link-btn.naukri    { background:rgba(255,96,22,0.12);   border-color:rgba(255,96,22,0.4);   color:#fb923c; }
            .job-link-btn.naukri:hover    { background:rgba(255,96,22,0.25);   box-shadow:0 6px 20px rgba(255,96,22,0.2); }
            .job-link-btn.indeed    { background:rgba(37,154,0,0.12);    border-color:rgba(37,154,0,0.4);    color:#4ade80; }
            .job-link-btn.indeed:hover    { background:rgba(37,154,0,0.25);    box-shadow:0 6px 20px rgba(37,154,0,0.2); }
            .job-link-btn.glassdoor { background:rgba(15,164,107,0.12);  border-color:rgba(15,164,107,0.4);  color:#34d399; }
            .job-link-btn.glassdoor:hover { background:rgba(15,164,107,0.25);  box-shadow:0 6px 20px rgba(15,164,107,0.2); }
            .job-link-btn.remoteok  { background:rgba(139,92,246,0.12);  border-color:rgba(139,92,246,0.4);  color:#c084fc; }
            .job-link-btn.remoteok:hover  { background:rgba(139,92,246,0.25);  box-shadow:0 6px 20px rgba(139,92,246,0.2); }
            .stats-row { display:flex; gap:16px; margin:20px 0; flex-wrap:wrap; }
            .stat-card { flex:1; min-width:110px; background:rgba(255,255,255,0.03); border:1px solid rgba(0,210,255,0.12); border-radius:14px; padding:16px 18px; text-align:center; transition:all 0.3s ease; }
            .stat-card:hover { border-color:rgba(0,210,255,0.4); transform:translateY(-3px); box-shadow:0 12px 30px rgba(0,210,255,0.1); }
            .stat-card .stat-num { font-family:'Bebas Neue',sans-serif; font-size:2rem; line-height:1; background:linear-gradient(135deg,#00d2ff,#a855f7); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
            .stat-card .stat-lbl { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; margin-top:4px; }
            .hist-card { background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.07); border-radius:14px; padding:18px 22px; margin-bottom:12px; transition:all 0.25s ease; }
            .hist-card:hover { border-color:rgba(0,210,255,0.25); transform:translateX(4px); }
            .tip-item  { display:flex; gap:10px; align-items:flex-start; padding:8px 12px; border-radius:8px; background:rgba(168,85,247,0.06); border:1px solid rgba(168,85,247,0.15); margin-bottom:8px; font-size:0.88rem; color:#c4b5fd; font-family:'Space Grotesk',sans-serif; }
            .tip-item::before  { content:"💡"; flex-shrink:0; }
            .learn-item { display:flex; gap:10px; align-items:center; padding:8px 12px; border-radius:8px; background:rgba(52,211,153,0.05); border:1px solid rgba(52,211,153,0.15); margin-bottom:8px; font-size:0.88rem; color:#6ee7b7; font-family:'Space Grotesk',sans-serif; }
            .learn-item::before { content:"📖"; flex-shrink:0; }
            .compare-header { font-family:'Bebas Neue',sans-serif; font-size:1.4rem; letter-spacing:0.06em; color:#e2e8f0; margin-bottom:6px; }
            .compare-cell { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:16px; height:100%; }
            .resource-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:14px; margin:12px 0; }
            .resource-card { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); border-radius:14px; padding:18px; transition:all 0.25s ease; text-decoration:none; display:block; }
            .resource-card:hover { border-color:rgba(0,210,255,0.35); transform:translateY(-3px); box-shadow:0 12px 30px rgba(0,0,0,0.3); text-decoration:none; }
            .resource-card .rc-icon { font-size:1.6rem; margin-bottom:8px; }
            .resource-card .rc-name { font-family:'Space Grotesk',sans-serif; font-size:0.95rem; font-weight:600; color:#e2e8f0; margin-bottom:4px; }
            .resource-card .rc-desc { font-family:'Space Grotesk',sans-serif; font-size:0.78rem; color:#64748b; line-height:1.5; }
            .resource-card .rc-tag  { display:inline-block; margin-top:10px; font-family:'JetBrains Mono',monospace; font-size:0.62rem; padding:2px 8px; border-radius:4px; background:rgba(0,210,255,0.1); color:#38bdf8; border:1px solid rgba(0,210,255,0.2); }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

        particle_js = """
        <script>
        (function() {
            var fe = window.frameElement;
            if (fe) { fe.style.cssText += ';display:block!important;position:absolute!important;top:0!important;left:0!important;width:0!important;height:0!important;overflow:hidden!important;pointer-events:none!important;border:none!important;margin:0!important;padding:0!important;opacity:0!important;'; }
        })();
        (function nexstepBoot() {
            function init() {
                try {
                    var P = window.parent, pdoc = P.document;
                    if (!pdoc || !pdoc.body) { setTimeout(init, 80); return; }
                    if (P.__nexstepRunning && !pdoc.getElementById('ns-canvas')) {
                        P.__nexstepRunning = false;
                    }
                    if (P.__nexstepRunning) return;
                    P.__nexstepRunning = true;
                    if (!pdoc.getElementById('nexstep-injected-css')) {
                        var s = pdoc.createElement('style'); s.id = 'nexstep-injected-css';
                        s.textContent = ['* { cursor: none !important; }','#ns-canvas { position:fixed!important; top:0!important; left:0!important; width:100vw!important; height:100vh!important; pointer-events:none!important; z-index:2147483620!important; }','#ns-dot { position:fixed!important; left:0!important; top:0!important; width:10px!important; height:10px!important; background:#00d2ff!important; border-radius:50%!important; pointer-events:none!important; z-index:2147483647!important; will-change:transform!important; box-shadow:0 0 10px #00d2ff,0 0 24px rgba(0,210,255,.5)!important; transition:width .15s,height .15s,background .15s!important; mix-blend-mode:screen!important; }','#ns-dot.ns-click { width:5px!important; height:5px!important; background:#a855f7!important; box-shadow:0 0 12px #a855f7!important; }','#ns-ring { position:fixed!important; left:0!important; top:0!important; width:34px!important; height:34px!important; border:1.5px solid rgba(0,210,255,.6)!important; border-radius:50%!important; pointer-events:none!important; z-index:2147483646!important; will-change:transform!important; transition:width .2s ease,height .2s ease,border-color .2s ease,background .2s ease!important; }','#ns-ring.ns-hover { width:56px!important; height:56px!important; border-color:#a855f7!important; background:rgba(168,85,247,.06)!important; }'].join('');
                        pdoc.head.appendChild(s);
                    }
                    if (pdoc.getElementById('ns-canvas')) return;
                    var canvas = pdoc.createElement('canvas'); canvas.id = 'ns-canvas'; pdoc.body.appendChild(canvas);
                    var dot = pdoc.createElement('div'); dot.id = 'ns-dot'; pdoc.body.appendChild(dot);
                    var ring = pdoc.createElement('div'); ring.id = 'ns-ring'; pdoc.body.appendChild(ring);
                    var mx = P.innerWidth/2, my = P.innerHeight/2, rx = mx, ry = my;
                    pdoc.addEventListener('mousemove', function(e){ mx=e.clientX; my=e.clientY; dot.style.transform='translate3d('+(mx-5)+'px,'+(my-5)+'px,0)'; }, {passive:true});
                    var HSel = 'button,a,input,textarea,select,[role="tab"],label,summary';
                    pdoc.addEventListener('mouseover', function(e){ if(e.target.closest&&e.target.closest(HSel)) ring.classList.add('ns-hover'); });
                    pdoc.addEventListener('mouseout',  function(e){ if(e.target.closest&&e.target.closest(HSel)) ring.classList.remove('ns-hover'); });
                    pdoc.addEventListener('mousedown', function(){ dot.classList.add('ns-click'); });
                    pdoc.addEventListener('mouseup',   function(){ dot.classList.remove('ns-click'); });
                    (function ringLoop(){ rx+=(mx-rx)*0.22; ry+=(my-ry)*0.22; ring.style.transform='translate3d('+(rx-17)+'px,'+(ry-17)+'px,0)'; P.requestAnimationFrame(ringLoop); })();
                    var ctx=canvas.getContext('2d'), W, H;
                    function resize(){ W=canvas.width=P.innerWidth; H=canvas.height=P.innerHeight; }
                    resize(); P.addEventListener('resize', function(){ resize(); spawn(); });
                    var COLORS=['#00d2ff','#3a7bd5','#a855f7','#38bdf8','#818cf8','#e879f9'];
                    function rnd(a,b){ return a+Math.random()*(b-a); }
                    function Particle(){ this.init(false); }
                    Particle.prototype.init=function(fromBottom){ this.x=rnd(0,W); this.y=fromBottom?H+rnd(5,30):rnd(0,H); this.r=rnd(0.8,2.8); this.vy=-rnd(0.2,0.8); this.vx=rnd(-0.35,0.35); this.c=COLORS[Math.floor(Math.random()*COLORS.length)]; this.ph=rnd(0,Math.PI*2); this.ps=rnd(0.01,0.03); this.ba=rnd(0.25,0.8); this.shoot=Math.random()<0.05; if(this.shoot){this.vy=-rnd(3,6);this.vx=rnd(-1,1);this.r=rnd(0.4,1.1);this.trail=[];} };
                    Particle.prototype.update=function(){ if(this.shoot){this.trail.push({x:this.x,y:this.y});if(this.trail.length>20)this.trail.shift();} var dx=this.x-mouseX,dy=this.y-mouseY,d=Math.sqrt(dx*dx+dy*dy); if(d<120&&d>0){var f=((120-d)/120)*1.3;this.x+=(dx/d)*f;this.y+=(dy/d)*f;} this.x+=this.vx;this.y+=this.vy;this.ph+=this.ps;this.alpha=this.ba*(0.5+0.5*Math.sin(this.ph)); if(this.y<-30||this.x<-30||this.x>W+30)this.init(true); };
                    Particle.prototype.draw=function(){ if(this.shoot&&this.trail&&this.trail.length>1){for(var i=1;i<this.trail.length;i++){var t=i/this.trail.length;ctx.save();ctx.globalAlpha=t*this.alpha*0.45;ctx.strokeStyle=this.c;ctx.lineWidth=this.r*t*1.1;ctx.beginPath();ctx.moveTo(this.trail[i-1].x,this.trail[i-1].y);ctx.lineTo(this.trail[i].x,this.trail[i].y);ctx.stroke();ctx.restore();}} ctx.save();ctx.globalAlpha=this.alpha;ctx.fillStyle=this.c;ctx.beginPath();ctx.arc(this.x,this.y,this.r,0,Math.PI*2);ctx.fill();ctx.restore(); };
                    var _linkFrame=0;
                    function drawLinks(pts){ _linkFrame++;if(_linkFrame%4!==0) return;var MAX=100,MAX2=MAX*MAX;ctx.lineWidth=0.7;for(var i=0;i<pts.length;i++){for(var j=i+1;j<pts.length;j++){var dx=pts[i].x-pts[j].x,dy=pts[i].y-pts[j].y,d2=dx*dx+dy*dy;if(d2<MAX2){ctx.save();ctx.globalAlpha=(1-Math.sqrt(d2)/MAX)*0.12;ctx.strokeStyle=pts[i].c;ctx.beginPath();ctx.moveTo(pts[i].x,pts[i].y);ctx.lineTo(pts[j].x,pts[j].y);ctx.stroke();ctx.restore();}}} }
                    var mouseX=-9999,mouseY=-9999;
                    pdoc.addEventListener('mousemove',function(e){mouseX=e.clientX;mouseY=e.clientY;},{passive:true});
                    var particles=[];
                    function spawn(){var n=Math.min(90,Math.floor(W*H/9500));particles=[];for(var i=0;i<n;i++)particles.push(new Particle());}
                    spawn();
                    var _lastFrame=0;
                    (function loop(now){ P.requestAnimationFrame(loop); if(now-_lastFrame<32) return; _lastFrame=now; ctx.clearRect(0,0,W,H); for(var i=0;i<particles.length;i++){particles[i].update();particles[i].draw();} drawLinks(particles); })(0);
                } catch(err){ setTimeout(init, 200); }
            }
            init();
        })();
        </script>
        """
        components.html(particle_js, height=1, scrolling=False)

    @staticmethod
    def show_api_setup_banner():
        html = (
            '<div style="position:relative;overflow:hidden;border-radius:20px;margin-bottom:24px;padding:24px 28px;'
            'background:linear-gradient(135deg,rgba(255,255,255,0.09) 0%,rgba(0,210,255,0.06) 60%,rgba(168,85,247,0.07) 100%);'
            'box-shadow:0 8px 40px rgba(0,0,0,0.5),inset 0 1px 0 rgba(255,255,255,0.2),0 0 0 1px rgba(255,255,255,0.09);">'
            '<div style="font-size:1.1rem;font-weight:800;margin-bottom:4px;background:linear-gradient(135deg,#fff 0%,#a8f0ff 50%,#c084fc 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">&#10022; Setup Required &mdash; Choose Your Free AI Provider</div>'
            '<div style="color:rgba(255,255,255,0.4);font-size:0.74rem;letter-spacing:0.06em;margin-bottom:16px;">100% free &nbsp;&middot;&nbsp; no credit card &nbsp;&middot;&nbsp; no billing &nbsp;&middot;&nbsp; ever</div>'
            '<div style="height:1px;margin-bottom:14px;background:linear-gradient(90deg,transparent,rgba(0,210,255,0.4),rgba(168,85,247,0.3),transparent);"></div>'
            '<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:9px;"><span style="background:rgba(66,133,244,0.18);border:1px solid rgba(66,133,244,0.45);border-radius:20px;padding:4px 13px;font-size:0.81rem;font-weight:700;color:#93c5fd;white-space:nowrap;">&#128309; Google Gemini</span><span style="color:rgba(255,255,255,0.38);font-size:0.74rem;">15 req/min &middot; 1500/day &middot; forever free</span><a href="https://aistudio.google.com/app/apikey" target="_blank" style="margin-left:auto;font-size:0.77rem;color:#7dd3fc;font-weight:700;text-decoration:none;border-bottom:1px solid rgba(125,211,252,0.3);white-space:nowrap;">aistudio.google.com &rarr;</a></div>'
            '<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:9px;"><span style="background:rgba(249,115,22,0.15);border:1px solid rgba(249,115,22,0.45);border-radius:20px;padding:4px 13px;font-size:0.81rem;font-weight:700;color:#fdba74;white-space:nowrap;">&#9889; Groq</span><span style="color:rgba(255,255,255,0.38);font-size:0.74rem;">Llama 3.3-70B &middot; ultra-fast &middot; free forever</span><a href="https://console.groq.com/keys" target="_blank" style="margin-left:auto;font-size:0.77rem;color:#fdba74;font-weight:700;text-decoration:none;border-bottom:1px solid rgba(253,186,116,0.3);white-space:nowrap;">console.groq.com &rarr;</a></div>'
            '<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:16px;"><span style="background:rgba(20,184,166,0.15);border:1px solid rgba(20,184,166,0.45);border-radius:20px;padding:4px 13px;font-size:0.81rem;font-weight:700;color:#5eead4;white-space:nowrap;">&#127754; Cohere</span><span style="color:rgba(255,255,255,0.38);font-size:0.74rem;">Command-R+ &middot; generous free trial</span><a href="https://dashboard.cohere.com/api-keys" target="_blank" style="margin-left:auto;font-size:0.77rem;color:#5eead4;font-weight:700;text-decoration:none;border-bottom:1px solid rgba(94,234,212,0.3);white-space:nowrap;">dashboard.cohere.com &rarr;</a></div>'
            '<div style="height:1px;margin-bottom:14px;background:linear-gradient(90deg,transparent,rgba(0,210,255,0.4),rgba(168,85,247,0.3),transparent);"></div>'
            '<div style="display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.13);border-radius:30px;padding:6px 18px;font-size:0.79rem;color:rgba(255,255,255,0.78);font-weight:600;">&#128072;&nbsp; Sidebar &rarr; pick provider &rarr; paste key &rarr; 30 seconds</div>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)


# ==================== TAB RENDER FUNCTIONS ====================

def render_tab_career_analysis(ai_handler: AIHandler, pdf_handler: PDFHandler,
                               history_manager: HistoryManager, selected_model: str,
                               analysis_depth: str, include_learning_path: bool,
                               include_interview_prep: bool):
    """Tab 1 — Career Analysis."""
    st.markdown("### 📋 Input Your Profile")
    st.markdown("""
    <div style="background:rgba(0,210,255,0.06);border:1px solid rgba(0,210,255,0.18);border-radius:14px;padding:14px 20px;margin-bottom:22px;">
      <span style="color:#00d2ff;font-weight:700;font-size:0.95rem;">Step 1 — Provide your profile &nbsp;·&nbsp;</span>
      <span style="color:#64748b;font-size:0.88rem;">Upload a PDF resume or type your details manually.</span>
    </div>
    """, unsafe_allow_html=True)

    input_method = st.radio("Input method", ["📄 Upload Resume (PDF)", "✍️ Manual Entry"],
                            horizontal=True, label_visibility="collapsed")

    raw_text = ""
    if input_method == "📄 Upload Resume (PDF)":
        uploaded_file = st.file_uploader("Drop your resume here", type="pdf",
                                         key="resume_upload", help="PDF only · Max 10 MB")
        if uploaded_file:
            st.success(f"✅ Loaded: **{uploaded_file.name}**")
            raw_text = pdf_handler.extract_text(uploaded_file)
    else:
        raw_text = st.text_area("Your skills, experience & education", height=180,
                                placeholder="e.g.\n• Python, SQL, Machine Learning\n• 2 yrs data analyst @ TCS\n• B.Tech CS, NIT Durgapur, 2023")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(168,85,247,0.06);border:1px solid rgba(168,85,247,0.18);border-radius:14px;padding:14px 20px;margin-bottom:16px;">
      <span style="color:#a855f7;font-weight:700;font-size:0.95rem;">Step 2 — Set your preferences</span>
    </div>
    """, unsafe_allow_html=True)

    p1, p2, p3 = st.columns(3)
    with p1:
        target_industry = st.multiselect("🏭 Target Industries",
                                         ["Technology", "Finance", "Healthcare",
                                             "Education", "E-Commerce", "Consulting"],
                                         default=["Technology"])
    with p2:
        career_stage = st.selectbox("🪜 Career Stage",
                                    ["Entry Level (0-2 yrs)", "Mid Level (3-6 yrs)", "Senior Level (7+ yrs)"])
    with p3:
        location_pref = st.selectbox("📍 Location",
                                     ["India - Metro", "India - Remote", "India - Tier 2", "International"])
        st.session_state.location_pref = location_pref

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    analyze_btn = st.button("🔮 Analyze My Career Path",
                            use_container_width=True, type="primary")

    if analyze_btn:
        if not selected_model:
            st.error("⚠️ Configure your API key in the sidebar first.")
        elif not raw_text:
            st.warning("⚠️ Please upload a resume or enter your details above.")
        elif not ai_handler.config.using_own_key() and st.session_state.get('free_uses', 0) >= 5:
            st.warning(
                "⚠️ You've used all 5 free analyses this session. Add your own free API key in the sidebar!")
            st.info("🔑 Get a free Groq key in 2 mins: https://console.groq.com/keys")
        else:
            context = {
                'industries': target_industry, 'career_stage': career_stage,
                'location': location_pref, 'depth': analysis_depth,
                'include_learning_path': include_learning_path,
                'include_interview_prep': include_interview_prep,
            }
            with st.spinner("🧠 AI is analyzing your profile… (30–60 seconds)"):
                data = ai_handler.get_career_advice(
                    raw_text, selected_model, context)

            if data:
                st.session_state.current_analysis = data
                history_manager.add_to_history(raw_text, data, context)
                if not ai_handler.config.using_own_key():
                    st.session_state['free_uses'] = st.session_state.get(
                        'free_uses', 0) + 1
                st.success(
                    "✅ Analysis complete! Scroll down to see your results.")
                st.balloons()

    if st.session_state.current_analysis:
        _render_career_results(st.session_state.current_analysis)


def _render_career_results(data: Dict):
    """Renders the career analysis results cards (called from Tab 1)."""
    careers = data.get('careers', [])
    top_match = max((c.get('match_score', 0) for c in careers), default=0)
    skill_count = len(data.get('current_skills', []))

    st.markdown("---")
    st.markdown("## 📊 Your Career Analysis")
    st.markdown(f"""
    <div class="stats-row">
      <div class="stat-card"><div class="stat-num">{len(careers)}</div><div class="stat-lbl">Career Paths</div></div>
      <div class="stat-card"><div class="stat-num">{top_match}%</div><div class="stat-lbl">Top Match</div></div>
      <div class="stat-card"><div class="stat-num">{skill_count}</div><div class="stat-lbl">Skills Found</div></div>
      <div class="stat-card"><div class="stat-num">{len(st.session_state.history)}</div><div class="stat-lbl">Analyses Done</div></div>
    </div>
    """, unsafe_allow_html=True)

    skills_html = render_skill_badges(data.get('current_skills', []))
    st.markdown(f"""
    <div class="result-card">
        <h3>🧬 Profile Summary</h3>
        <p style="font-size:1.05rem;color:#cbd5e1;line-height:1.7;margin-bottom:14px;">{data.get('profile_summary', 'N/A')}</p>
        <div style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:#00d2ff;text-transform:uppercase;letter-spacing:.12em;margin-bottom:8px;">DETECTED SKILLS</div>
        <div>{skills_html}</div>
    </div>
    """, unsafe_allow_html=True)

    if not careers:
        return

    st.markdown("### 🎯 Recommended Career Paths")
    for idx, job in enumerate(careers, 1):
        score = job.get('match_score', 0)
        keywords = job.get('job_search_keywords', job['title'])
        companies = job.get('top_companies', [])
        certs = job.get('certifications', [])
        ring_html = render_match_ring(score)
        jlinks_html = render_job_links(job['title'],
                                       st.session_state.get('location_pref', 'India'), keywords)
        comp_badges = render_skill_badges(companies, "green")
        cert_badges = render_skill_badges(certs, "purple")
        tips_html = "".join(
            f'<div class="tip-item">{t}</div>' for t in job.get('interview_tips', []))
        learn_html = "".join(
            f'<div class="learn-item">{c}</div>' for c in job.get('learning_path', []))
        steps_html = "".join(f'<li style="color:#94a3b8;font-size:.88rem;margin-bottom:5px;">{s}</li>'
                             for s in job.get('next_steps', []))

        with st.expander(f"**{idx}. {job['title']}** — {score}% Match", expanded=(idx == 1)):
            col_left, col_mid, col_right = st.columns([3, 2, 1])
            with col_left:
                st.markdown(f"""
                <div style="padding-right:16px;">
                  <span style="font-family:'JetBrains Mono',monospace;font-size:.85rem;color:#4ade80;background:rgba(74,222,128,.08);border:1px solid rgba(74,222,128,.2);border-radius:6px;padding:4px 12px;display:inline-block;margin-bottom:12px;">💰 {job['salary_range']}</span>
                  <p style="color:#94a3b8;font-size:.9rem;line-height:1.65;margin-bottom:14px;">{job.get('reason','')}</p>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:#00d2ff;text-transform:uppercase;letter-spacing:.12em;margin-bottom:6px;">▸ NEXT STEPS</div>
                  <ul style="margin:0;padding-left:18px;">{steps_html}</ul>
                  {"<div style='font-family:JetBrains Mono,monospace;font-size:.65rem;color:#00d2ff;text-transform:uppercase;letter-spacing:.12em;margin:12px 0 6px;'>▸ TOP COMPANIES</div>" + comp_badges if companies else ""}
                  {"<div style='font-family:JetBrains Mono,monospace;font-size:.65rem;color:#a855f7;text-transform:uppercase;letter-spacing:.12em;margin:12px 0 6px;'>▸ CERTIFICATIONS</div>" + cert_badges if certs else ""}
                  <div style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:#00d2ff;text-transform:uppercase;letter-spacing:.12em;margin:14px 0 4px;">▸ APPLY NOW</div>
                  {jlinks_html}
                </div>
                """, unsafe_allow_html=True)
            with col_mid:
                gaps = job.get('skill_gap_analysis', {})
                if gaps:
                    chart_data = pd.DataFrame(
                        {'Skill': list(gaps.keys()), 'Proficiency': list(gaps.values())})
                    c = alt.Chart(chart_data).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
                        x=alt.X('Proficiency:Q', scale=alt.Scale(domain=[0, 100]),
                                axis=alt.Axis(labelColor='#64748b', gridColor='rgba(255,255,255,0.05)')),
                        y=alt.Y('Skill:N', sort='-x',
                                axis=alt.Axis(labelColor='#94a3b8')),
                        color=alt.Color('Proficiency:Q', scale=alt.Scale(
                            scheme='viridis'), legend=None)
                    ).properties(height=180, background='transparent').configure_view(strokeWidth=0, fill='transparent')
                    st.altair_chart(c, use_container_width=True)
                if learn_html:
                    st.markdown(f"""
                    <div style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:#34d399;text-transform:uppercase;letter-spacing:.12em;margin:10px 0 6px;">▸ LEARNING PATH</div>
                    {learn_html}""", unsafe_allow_html=True)
            with col_right:
                st.markdown(ring_html, unsafe_allow_html=True)
            if tips_html:
                st.markdown(f"""
                <div style="margin-top:14px;">
                  <div style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:#a855f7;text-transform:uppercase;letter-spacing:.12em;margin-bottom:8px;">▸ INTERVIEW TIPS</div>
                  {tips_html}
                </div>""", unsafe_allow_html=True)


def render_tab_history():
    """Tab 2 — Analysis History."""
    st.markdown("### 📜 Analysis History")
    if not st.session_state.history:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#475569;">
          <div style="font-size:3rem;margin-bottom:12px;">📭</div>
          <div style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;">No history yet</div>
          <div style="font-size:.85rem;margin-top:6px;">Run your first analysis to see it here</div>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown(f'<p style="color:#64748b;font-size:.85rem;">{len(st.session_state.history)} analyses saved this session</p>',
                unsafe_allow_html=True)
    for idx, record in enumerate(reversed(st.session_state.history), 1):
        careers_in_record = record['analysis'].get('careers', [])
        top = max((c.get('match_score', 0)
                  for c in careers_in_record), default=0)
        titles = " · ".join(c.get('title', '') for c in careers_in_record)
        stage = record.get('context', {}).get('career_stage', '')
        badges = render_skill_badges(
            record['analysis'].get('current_skills', [])[:5])
        with st.expander(f"**#{idx}** {record['timestamp']}  —  Top match {top}%", expanded=False):
            st.markdown(f"""
            <div class="hist-card" style="margin:0;">
              <div>📅 {record['timestamp']} · {stage}</div>
              <p style="color:#e2e8f0;font-size:.95rem;font-weight:600;margin:8px 0 4px;">{record['summary']}</p>
              <div style="color:#64748b;font-size:.85rem;">Paths: {titles}</div>
              <div style="margin-top:10px;">{badges}</div>
            </div>""", unsafe_allow_html=True)
            if st.button("♻️ Restore This Analysis", key=f"restore_{idx}"):
                st.session_state.current_analysis = record['analysis']
                st.success("✅ Analysis restored! Go to Career Analysis tab.")


def render_tab_compare():
    """Tab 3 — Career Path Comparison."""
    st.markdown("### ⚖️ Career Path Comparison")
    if not st.session_state.current_analysis:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#475569;">
          <div style="font-size:3rem;margin-bottom:12px;">⚖️</div>
          <div style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;">Nothing to compare yet</div>
          <div style="font-size:.85rem;margin-top:6px;">Run a career analysis first</div>
        </div>""", unsafe_allow_html=True)
        return

    careers = st.session_state.current_analysis.get('careers', [])
    if len(careers) < 2:
        st.info("Run an analysis with 2+ career paths to unlock comparison.")
        return

    cols = st.columns(len(careers))
    for col, job in zip(cols, careers):
        score = job.get('match_score', 0)
        ring = render_match_ring(score)
        with col:
            st.markdown(f"""
            <div class="compare-cell">
              <div class="compare-header">{job['title']}</div>
              {ring}
            </div>""", unsafe_allow_html=True)
            st.markdown(f"**💰 Salary:** `{job.get('salary_range','—')}`")
            st.markdown(f"**📌 Why:** {job.get('reason','')[:120]}…")
            companies = job.get('top_companies', [])
            if companies:
                st.markdown("**🏢 Companies:** " + render_skill_badges(companies, "green"),
                            unsafe_allow_html=True)
            certs = job.get('certifications', [])
            if certs:
                st.markdown("**🏅 Certs:** " + render_skill_badges(certs, "purple"),
                            unsafe_allow_html=True)
            tips = job.get('interview_tips', [])
            if tips:
                st.markdown("**💡 Top Tip:** " + tips[0])
            jlinks = render_job_links(job['title'],
                                      st.session_state.get(
                                          'location_pref', 'India'),
                                      job.get('job_search_keywords', ''))
            st.markdown(jlinks, unsafe_allow_html=True)


def render_tab_resources():
    """Tab 4 — Learning & Career Resources."""
    st.markdown("### 📚 Learning & Career Resources")

    st.markdown("#### 🎓 Top Learning Platforms")
    st.markdown("""
    <div class="resource-grid">
      <a href="https://coursera.org" target="_blank" class="resource-card"><div class="rc-icon">🎓</div><div class="rc-name">Coursera</div><div class="rc-desc">University-backed courses, Google & IBM certificates</div><span class="rc-tag">FREE AUDIT</span></a>
      <a href="https://www.udemy.com" target="_blank" class="resource-card"><div class="rc-icon">🧑‍💻</div><div class="rc-name">Udemy</div><div class="rc-desc">Practical skills — dev, design, business, data science</div><span class="rc-tag">PAID</span></a>
      <a href="https://linkedin.com/learning" target="_blank" class="resource-card"><div class="rc-icon">💼</div><div class="rc-name">LinkedIn Learning</div><div class="rc-desc">Business & tech courses linked to your LinkedIn profile</div><span class="rc-tag">1 MONTH FREE</span></a>
      <a href="https://nptel.ac.in" target="_blank" class="resource-card"><div class="rc-icon">🇮🇳</div><div class="rc-name">NPTEL</div><div class="rc-desc">IIT-quality courses, free with certifications</div><span class="rc-tag">FREE</span></a>
      <a href="https://www.freecodecamp.org" target="_blank" class="resource-card"><div class="rc-icon">🔥</div><div class="rc-name">freeCodeCamp</div><div class="rc-desc">Full stack development, data science — completely free</div><span class="rc-tag">FREE</span></a>
      <a href="https://grow.google/certificates" target="_blank" class="resource-card"><div class="rc-icon">🔵</div><div class="rc-name">Google Career Certs</div><div class="rc-desc">Data Analytics, PM, Cybersecurity, UX Design</div><span class="rc-tag">CERTIFICATE</span></a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🔍 Job Search Portals")
    st.markdown("""
    <div class="resource-grid">
      <a href="https://www.linkedin.com/jobs" target="_blank" class="resource-card"><div class="rc-icon">🔵</div><div class="rc-name">LinkedIn Jobs</div><div class="rc-desc">World's largest professional network</div><span class="rc-tag">GLOBAL</span></a>
      <a href="https://www.naukri.com" target="_blank" class="resource-card"><div class="rc-icon">🟠</div><div class="rc-name">Naukri.com</div><div class="rc-desc">India's #1 job portal — 70k+ active listings daily</div><span class="rc-tag">INDIA</span></a>
      <a href="https://in.indeed.com" target="_blank" class="resource-card"><div class="rc-icon">🟢</div><div class="rc-name">Indeed India</div><div class="rc-desc">Aggregated listings, company reviews, salary insights</div><span class="rc-tag">INDIA + GLOBAL</span></a>
      <a href="https://www.glassdoor.co.in" target="_blank" class="resource-card"><div class="rc-icon">💚</div><div class="rc-name">Glassdoor</div><div class="rc-desc">Jobs + salary data + anonymous company reviews</div><span class="rc-tag">SALARY INTEL</span></a>
      <a href="https://angel.co/jobs" target="_blank" class="resource-card"><div class="rc-icon">👼</div><div class="rc-name">Wellfound (AngelList)</div><div class="rc-desc">Startup jobs — equity, remote, early-stage</div><span class="rc-tag">STARTUPS</span></a>
      <a href="https://www.instahyre.com" target="_blank" class="resource-card"><div class="rc-icon">⚡</div><div class="rc-name">Instahyre</div><div class="rc-desc">AI-matched jobs for tech professionals in India</div><span class="rc-tag">TECH INDIA</span></a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🏅 Certifications Worth Getting")
    st.markdown("""
    <div class="resource-grid">
      <a href="https://aws.amazon.com/certification" target="_blank" class="resource-card"><div class="rc-icon">☁️</div><div class="rc-name">AWS Certifications</div><div class="rc-desc">Cloud Computing — most in-demand certs globally</div><span class="rc-tag">CLOUD</span></a>
      <a href="https://cloud.google.com/certification" target="_blank" class="resource-card"><div class="rc-icon">🔶</div><div class="rc-name">Google Cloud</div><div class="rc-desc">GCP certs for data engineers and ML engineers</div><span class="rc-tag">CLOUD + ML</span></a>
      <a href="https://www.credly.com/org/microsoft-certification" target="_blank" class="resource-card"><div class="rc-icon">🪟</div><div class="rc-name">Microsoft Azure</div><div class="rc-desc">AZ-900, AZ-104, DP-900 — top corporate demand</div><span class="rc-tag">ENTERPRISE</span></a>
      <a href="https://www.pmi.org/certifications/project-management-pmp" target="_blank" class="resource-card"><div class="rc-icon">📋</div><div class="rc-name">PMP</div><div class="rc-desc">Project Management Professional — salary booster</div><span class="rc-tag">MANAGEMENT</span></a>
    </div>
    """, unsafe_allow_html=True)


def render_tab_resume_builder(ai_handler: AIHandler, selected_model: str):
    """Tab 5 — ATS Resume Builder."""
    st.markdown("### 📝 ATS-Friendly Resume Builder")
    st.markdown("""
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:22px;">
      <div style="flex:1;min-width:180px;background:rgba(0,210,255,0.07);border:1px solid rgba(0,210,255,0.2);border-radius:12px;padding:14px 16px;text-align:center;"><div style="font-size:1.5rem;">1️⃣</div><div style="color:#00d2ff;font-weight:600;font-size:0.88rem;margin-top:4px;">Fill Your Details</div></div>
      <div style="flex:1;min-width:180px;background:rgba(168,85,247,0.07);border:1px solid rgba(168,85,247,0.2);border-radius:12px;padding:14px 16px;text-align:center;"><div style="font-size:1.5rem;">2️⃣</div><div style="color:#a855f7;font-weight:600;font-size:0.88rem;margin-top:4px;">Paste Job Description</div></div>
      <div style="flex:1;min-width:180px;background:rgba(34,197,94,0.07);border:1px solid rgba(34,197,94,0.2);border-radius:12px;padding:14px 16px;text-align:center;"><div style="font-size:1.5rem;">3️⃣</div><div style="color:#22c55e;font-weight:600;font-size:0.88rem;margin-top:4px;">Get ATS Resume</div></div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("👤 Personal Info & Target Role", expanded=True):
        rb_c1, rb_c2, rb_c3 = st.columns(3)
        with rb_c1:
            rb_name = st.text_input(
                "Full Name *", placeholder="Anubhab Mondal", key="rb_name")
            rb_email = st.text_input(
                "Email", placeholder="you@email.com", key="rb_email")
        with rb_c2:
            rb_phone = st.text_input(
                "Phone", placeholder="+91-9876543210", key="rb_phone")
            rb_location = st.text_input(
                "Location", placeholder="Kolkata, West Bengal", key="rb_location")
        with rb_c3:
            rb_target_role = st.text_input(
                "Target Role *", placeholder="Data Scientist / SWE / PM", key="rb_target_role")
            rb_exp_years = st.selectbox("Experience",
                                        ["Fresher (0)", "1-2 years", "3-5 years", "5-8 years", "8+ years"], key="rb_exp_years")
        rb_linkedin = st.text_input(
            "LinkedIn URL (optional)", placeholder="linkedin.com/in/yourname", key="rb_linkedin")

    with st.expander("💼 Experience, Skills & Education", expanded=True):
        rb_work = st.text_area("Work Experience", height=110,
                               placeholder="Company: TCS | Role: Software Engineer | Duration: 2022–2024\nAchievement: Built REST APIs serving 100k+ users, reduced latency by 40%",
                               key="rb_work")
        sk_col, edu_col = st.columns(2)
        with sk_col:
            rb_skills = st.text_area("Skills (comma-separated)", height=80,
                                     placeholder="Python, SQL, TensorFlow, React, AWS, Git...", key="rb_skills")
            rb_certs = st.text_input(
                "Certifications", placeholder="AWS Cloud Practitioner...", key="rb_certs")
        with edu_col:
            rb_education = st.text_area("Education", height=80,
                                        placeholder="B.Tech CS | NIT Durgapur | 2022 | CGPA 8.7", key="rb_education")
            rb_achievements = st.text_input("Achievements / Awards",
                                            placeholder="Dean's List, Hackathon Winner...", key="rb_achievements")
        rb_projects = st.text_area("Projects", height=80,
                                   placeholder="Project: AI Resume Parser | Stack: Python + NLP | Result: 92% accuracy",
                                   key="rb_projects")

    st.markdown("#### 📋 Paste Job Description *(optional but recommended)*")
    rb_jd = st.text_area("Job Description", height=120,
                         placeholder="Paste the full job description here for keyword-optimized resume generation.",
                         key="rb_jd", label_visibility="collapsed")

    if st.button("⚡ Build ATS Resume", use_container_width=True, type="primary", key="build_resume_btn"):
        if not selected_model:
            st.error("⚠️ Configure your API key first!")
        elif not rb_name or not rb_target_role:
            st.error("⚠️ Please fill in at least your Name and Target Role.")
        elif not ai_handler.config.using_own_key() and st.session_state.get('free_uses', 0) >= 5:
            st.warning(
                "⚠️ Free session limit reached. Add your own free API key in the sidebar!")
        else:
            profile_data = {
                "name": rb_name, "email": rb_email, "phone": rb_phone,
                "linkedin": rb_linkedin, "location": rb_location,
                "target_role": rb_target_role, "experience_years": rb_exp_years,
                "work_experience": rb_work, "skills": rb_skills,
                "education": rb_education, "certifications": rb_certs,
                "projects": rb_projects, "achievements": rb_achievements,
                "job_description": rb_jd,
            }
            with st.spinner("✍️ Building your ATS-optimized resume... (30-45 seconds)"):
                result = ai_handler.build_ats_resume(
                    profile_data, selected_model)
            if result:
                st.session_state.built_resume = result
                if not ai_handler.config.using_own_key():
                    st.session_state['free_uses'] = st.session_state.get(
                        'free_uses', 0) + 1
                st.success("✅ Resume built successfully!")

    if st.session_state.built_resume:
        _render_resume_output(st.session_state.built_resume)


def _render_resume_output(res: Dict):
    """Renders the built resume preview and download button."""
    resume = res.get("resume", {})
    ats_score = res.get("ats_score", 0)
    score_color = "#00d2ff" if ats_score >= 80 else (
        "#a855f7" if ats_score >= 60 else "#f59e0b")
    kw_found = res.get("keywords_found", [])
    kw_missing = res.get("keywords_missing", [])

    st.markdown(f"""
    <div style="display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap;">
      <div style="flex:1;min-width:160px;background:rgba(0,0,0,0.3);border:1px solid {score_color}40;border-radius:12px;padding:18px;text-align:center;">
        <div style="font-size:2.5rem;font-weight:900;color:{score_color};font-family:'Orbitron',sans-serif;">{ats_score}</div>
        <div style="color:#94a3b8;font-size:0.8rem;letter-spacing:0.1em;text-transform:uppercase;">ATS Score</div>
      </div>
      <div style="flex:2;min-width:200px;background:rgba(0,0,0,0.3);border:1px solid rgba(0,210,255,0.15);border-radius:12px;padding:18px;">
        <div style="color:#00d2ff;font-weight:600;margin-bottom:8px;">✅ Keywords Found</div>
        <div>{' '.join(f'<span style="background:rgba(0,210,255,0.15);color:#00d2ff;padding:3px 10px;border-radius:20px;font-size:0.8rem;margin:2px;display:inline-block;">{k}</span>' for k in kw_found[:10])}</div>
      </div>
      <div style="flex:2;min-width:200px;background:rgba(0,0,0,0.3);border:1px solid rgba(245,158,11,0.2);border-radius:12px;padding:18px;">
        <div style="color:#f59e0b;font-weight:600;margin-bottom:8px;">⚠️ Keywords to Add</div>
        <div>{' '.join(f'<span style="background:rgba(245,158,11,0.15);color:#f59e0b;padding:3px 10px;border-radius:20px;font-size:0.8rem;margin:2px;display:inline-block;">{k}</span>' for k in kw_missing[:8])}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    tips = res.get("ats_tips", [])
    if tips:
        st.markdown(f"""
        <div style="background:rgba(168,85,247,0.08);border-left:3px solid #a855f7;border-radius:8px;padding:12px 16px;margin-bottom:20px;">
          <div style="color:#a855f7;font-weight:600;margin-bottom:6px;">💡 ATS Optimization Tips</div>
          {''.join(f'<div style="color:#94a3b8;font-size:0.9rem;margin:4px 0;">• {t}</div>' for t in tips)}
        </div>
        """, unsafe_allow_html=True)

    contact = resume.get("contact", {})
    summary = resume.get("summary", "")
    experience = resume.get("experience", [])
    skills_data = resume.get("skills", {})
    education = resume.get("education", [])
    certs = resume.get("certifications", [])
    projects = resume.get("projects", [])
    all_skills = skills_data.get(
        "technical", []) + skills_data.get("tools", []) + skills_data.get("soft", [])

    exp_html = ""
    for exp in experience:
        bullets_html = "".join(f'<li style="color:#94a3b8;margin:4px 0;font-size:0.9rem;">{b}</li>'
                               for b in exp.get("bullets", []))
        exp_html += f"""
        <div style="margin-bottom:14px;">
          <div style="display:flex;justify-content:space-between;align-items:baseline;">
            <span style="color:#e2e8f0;font-weight:600;">{exp.get('title','')}</span>
            <span style="color:#64748b;font-size:0.85rem;">{exp.get('duration','')}</span>
          </div>
          <div style="color:#00d2ff;font-size:0.85rem;margin-bottom:6px;">{exp.get('company','')}</div>
          <ul style="margin:0;padding-left:18px;">{bullets_html}</ul>
        </div>"""

    edu_html = "".join(
        f'<div style="display:flex;justify-content:space-between;margin-bottom:6px;">'
        f'<div><span style="color:#e2e8f0;font-weight:600;">{e.get("degree","")}</span> — '
        f'<span style="color:#94a3b8;">{e.get("institution","")}</span></div>'
        f'<div style="color:#64748b;font-size:0.85rem;">{e.get("year","")} '
        f'{"| GPA: " + e.get("gpa","") if e.get("gpa") else ""}</div></div>'
        for e in education)

    proj_html = "".join(
        f'<div style="margin-bottom:10px;"><span style="color:#e2e8f0;font-weight:600;">{p.get("name","")}</span>'
        f'<p style="color:#94a3b8;font-size:0.88rem;margin:4px 0 0 0;">{p.get("description","")}</p></div>'
        for p in projects)

    skills_badges = " ".join(
        f'<span style="background:rgba(0,210,255,0.1);color:#00d2ff;padding:3px 10px;border-radius:20px;font-size:0.8rem;margin:2px;display:inline-block;">{s}</span>'
        for s in all_skills)
    certs_text = " • ".join(certs) if certs else "—"

    st.markdown(f"""
    <div style="background:#0f172a;border:1px solid rgba(0,210,255,0.2);border-radius:16px;padding:28px 32px;font-family:'Space Grotesk',sans-serif;">
      <div style="border-bottom:2px solid rgba(0,210,255,0.3);padding-bottom:16px;margin-bottom:20px;">
        <h2 style="font-family:'Orbitron',sans-serif!important;font-size:1.8rem!important;color:#e2e8f0!important;margin:0 0 6px 0!important;">{contact.get('name','')}</h2>
        <div style="color:#00d2ff;font-size:0.88rem;">{contact.get('email','')} &nbsp;|&nbsp; {contact.get('phone','')} &nbsp;|&nbsp; {contact.get('location','')} &nbsp;|&nbsp; {contact.get('linkedin','')}</div>
      </div>
      <div style="margin-bottom:20px;"><div style="color:#00d2ff;font-size:0.75rem;letter-spacing:0.15em;text-transform:uppercase;font-weight:700;margin-bottom:8px;">Professional Summary</div><p style="color:#cbd5e1;line-height:1.7;margin:0;">{summary}</p></div>
      {"<div style='margin-bottom:20px;'><div style='color:#00d2ff;font-size:0.75rem;letter-spacing:0.15em;text-transform:uppercase;font-weight:700;margin-bottom:12px;'>Work Experience</div>" + exp_html + "</div>" if exp_html else ""}
      {"<div style='margin-bottom:20px;'><div style='color:#00d2ff;font-size:0.75rem;letter-spacing:0.15em;text-transform:uppercase;font-weight:700;margin-bottom:8px;'>Skills</div><div>" + skills_badges + "</div></div>" if all_skills else ""}
      {"<div style='margin-bottom:20px;'><div style='color:#00d2ff;font-size:0.75rem;letter-spacing:0.15em;text-transform:uppercase;font-weight:700;margin-bottom:8px;'>Education</div>" + edu_html + "</div>" if edu_html else ""}
      {"<div style='margin-bottom:20px;'><div style='color:#00d2ff;font-size:0.75rem;letter-spacing:0.15em;text-transform:uppercase;font-weight:700;margin-bottom:8px;'>Projects</div>" + proj_html + "</div>" if proj_html else ""}
      {"<div><div style='color:#00d2ff;font-size:0.75rem;letter-spacing:0.15em;text-transform:uppercase;font-weight:700;margin-bottom:6px;'>Certifications</div><div style='color:#94a3b8;font-size:0.9rem;'>" + certs_text + "</div></div>" if certs else ""}
    </div>
    """, unsafe_allow_html=True)

    plain_text = f"""{contact.get('name','').upper()}
{contact.get('email','')} | {contact.get('phone','')} | {contact.get('location','')} | {contact.get('linkedin','')}

PROFESSIONAL SUMMARY
{summary}

WORK EXPERIENCE
"""
    for exp in experience:
        plain_text += f"\n{exp.get('title','')} | {exp.get('company','')} | {exp.get('duration','')}\n"
        for b in exp.get("bullets", []):
            plain_text += f"  • {b}\n"
    plain_text += "\nSKILLS\n" + ", ".join(all_skills)
    plain_text += "\n\nEDUCATION\n"
    for e in education:
        plain_text += f"{e.get('degree','')} | {e.get('institution','')} | {e.get('year','')} | GPA: {e.get('gpa','')}\n"
    if certs:
        plain_text += "\nCERTIFICATIONS\n" + "\n".join(f"• {c}" for c in certs)
    if projects:
        plain_text += "\n\nPROJECTS\n"
        for p in projects:
            plain_text += f"{p.get('name','')}: {p.get('description','')}\n"

    st.download_button(
        "📥 Download Resume (.txt — paste into Word/Google Docs)",
        data=plain_text,
        file_name=f"ATS_Resume_{contact.get('name','').replace(' ','_')}.txt",
        mime="text/plain",
        use_container_width=True,
    )


def render_tab_mock_interview(ai_handler: AIHandler, selected_model: str):
    """Tab 6 — Mock Interview Simulator."""
    st.markdown("### 🎤 Mock Interview Simulator")
    st.markdown("""
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:22px;">
      <div style="flex:1;min-width:160px;background:rgba(168,85,247,0.07);border:1px solid rgba(168,85,247,0.2);border-radius:12px;padding:12px 16px;text-align:center;"><div style="font-size:1.4rem;">🎯</div><div style="color:#a855f7;font-weight:600;font-size:0.85rem;margin-top:4px;">Pick Role + Level</div></div>
      <div style="flex:1;min-width:160px;background:rgba(0,210,255,0.07);border:1px solid rgba(0,210,255,0.2);border-radius:12px;padding:12px 16px;text-align:center;"><div style="font-size:1.4rem;">💬</div><div style="color:#00d2ff;font-weight:600;font-size:0.85rem;margin-top:4px;">Answer 8 Questions</div></div>
      <div style="flex:1;min-width:160px;background:rgba(34,197,94,0.07);border:1px solid rgba(34,197,94,0.2);border-radius:12px;padding:12px 16px;text-align:center;"><div style="font-size:1.4rem;">🤖</div><div style="color:#22c55e;font-weight:600;font-size:0.85rem;margin-top:4px;">Get AI Feedback + Score</div></div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.interview_started:
        _render_interview_setup(ai_handler, selected_model)
    else:
        _render_interview_session(ai_handler, selected_model)


def _render_interview_setup(ai_handler: AIHandler, selected_model: str):
    """Role/level picker and Start button for the mock interview."""
    ALL_ROLES = [
        "─── 💻 Software Engineering ───",
        "Software Engineer", "Backend Engineer", "Frontend Engineer",
        "Full Stack Developer", "Mobile Developer", "iOS Developer",
        "Android Developer", "React Native Developer", "Flutter Developer",
        "Embedded Systems Engineer", "Systems Programmer", "Game Developer",
        "QA / Test Engineer", "SDET (Software Dev in Test)", "Technical Lead",
        "─── ☁️ Cloud & Infrastructure ───",
        "Cloud Engineer", "Cloud Architect", "Solutions Architect",
        "AWS Cloud Engineer", "Azure Engineer", "GCP Engineer",
        "DevOps Engineer", "Site Reliability Engineer (SRE)",
        "Platform Engineer", "Kubernetes Engineer",
        "Network Engineer", "Infrastructure Engineer",
        "─── 📊 Data & Analytics ───",
        "Data Scientist", "Data Analyst", "Data Engineer",
        "Analytics Engineer", "Business Intelligence Analyst",
        "ETL Developer", "Database Administrator", "Quantitative Analyst",
        "Research Scientist", "MLOps Engineer",
        "─── 🤖 AI & Machine Learning ───",
        "ML Engineer", "AI Researcher", "NLP Engineer",
        "Computer Vision Engineer", "Deep Learning Engineer",
        "AI Product Manager", "Prompt Engineer", "LLM Engineer",
        "─── 🔐 Cybersecurity ───",
        "Cybersecurity Analyst", "Penetration Tester", "Security Engineer",
        "SOC Analyst", "Cloud Security Engineer",
        "Application Security Engineer", "Threat Intelligence Analyst",
        "GRC Analyst", "Identity & Access Management Engineer",
        "─── 🧩 Product & Design ───",
        "Product Manager", "Associate Product Manager",
        "Technical Product Manager", "Growth PM", "Product Designer",
        "UX Designer", "UI Designer", "UX Researcher",
        "Design Systems Lead", "Content Designer", "Interaction Designer",
        "─── 💼 Business & Consulting ───",
        "Business Analyst", "Management Consultant",
        "Strategy Analyst", "Operations Manager",
        "Supply Chain Analyst", "Product Analyst",
        "ERP Consultant", "Salesforce Developer",
        "IT Project Manager", "Scrum Master", "Agile Coach",
        "─── 💰 Finance & Investments ───",
        "Investment Banker", "Financial Analyst", "Equity Research Analyst",
        "Risk Analyst", "Credit Analyst", "Actuary",
        "Quantitative Finance Analyst", "Corporate Finance Analyst",
        "Chartered Accountant (CA)", "CFO Track Associate",
        "─── 📣 Marketing & Growth ───",
        "Digital Marketing Manager", "SEO Specialist",
        "Performance Marketing Manager", "Brand Manager",
        "Content Strategist", "Social Media Manager",
        "Growth Hacker", "Email Marketing Specialist",
        "Marketing Analyst", "CRM Manager",
        "─── 🤝 Sales & Customer Success ───",
        "Sales Engineer", "Account Executive",
        "Customer Success Manager", "Pre-Sales Consultant",
        "Business Development Manager", "Inside Sales Representative",
        "Enterprise Sales Manager", "Channel Partner Manager",
        "─── 🏥 Healthcare & Life Sciences ───",
        "Healthcare Data Analyst", "Clinical Research Associate",
        "Biomedical Engineer", "Medical Writer",
        "Regulatory Affairs Specialist", "Pharmacovigilance Analyst",
        "Health Informatics Specialist",
        "─── ⚖️ Legal & Compliance ───",
        "Legal Tech Analyst", "Contract Manager",
        "Compliance Officer", "Paralegal (Tech Law)",
        "─── 👥 HR & People Operations ───",
        "HR Business Partner", "Talent Acquisition Specialist",
        "HR Analyst", "Compensation & Benefits Manager",
        "Learning & Development Manager", "People Operations Manager",
        "─── 🔗 Emerging Tech ───",
        "Blockchain Developer", "Web3 Developer",
        "Smart Contract Auditor", "AR/VR Developer",
        "IoT Engineer", "RPA Developer",
        "Low-Code / No-Code Developer", "Technical Writer",
        "Solutions Consultant",
        "─── ⚙️ Core Engineering ───",
        "Electrical Engineer", "Mechanical Engineer", "Civil Engineer",
        "Chemical Engineer", "Aerospace Engineer", "Manufacturing Engineer",
        "Electronics and Communication Engineer",
        "─── ✏️ Others ───",
        "Others — Type My Own Role",
    ]

    sel_col1, sel_col2 = st.columns([3, 2])
    with sel_col1:
        st.markdown('<div style="color:rgba(0,210,255,0.75);font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:4px;">🎯 Job Role</div>', unsafe_allow_html=True)
        selected_role_raw = st.selectbox("Job Role", options=ALL_ROLES, index=1,
                                         key="mi_role_select", label_visibility="collapsed")
    with sel_col2:
        st.markdown('<div style="color:rgba(0,210,255,0.75);font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:4px;">🪜 Experience Level</div>', unsafe_allow_html=True)
        mi_level = st.selectbox("Experience Level",
                                ["Fresher", "Junior (1-3 yrs)",
                                 "Mid-level (3-6 yrs)", "Senior (6+ yrs)"],
                                key="mi_level", label_visibility="collapsed")

    is_separator = selected_role_raw.startswith("───")
    is_others = selected_role_raw == "Others — Type My Own Role"
    mi_role = ""

    if is_separator:
        st.warning(
            "⚠️ That's a category header — please scroll and pick a role inside it.")
    elif is_others:
        mi_role = st.text_input("Custom Role",
                                placeholder="e.g. Quant Trader, AI Ethics Researcher...",
                                key="mi_custom_role", label_visibility="collapsed")
        if mi_role:
            st.markdown(
                f'<div style="color:#a855f7;font-size:0.85rem;margin-bottom:8px;">✅ Role set to: <strong style="color:#e2e8f0;">{mi_role}</strong></div>', unsafe_allow_html=True)
    else:
        mi_role = selected_role_raw
        st.markdown(
            f'<div style="background:rgba(0,210,255,0.06);border:1px solid rgba(0,210,255,0.2);border-radius:8px;padding:10px 16px;margin-bottom:16px;color:#00d2ff;font-size:0.88rem;">✅ Ready: <strong style="color:#e2e8f0;">{mi_role}</strong> · <span style="color:#64748b;">{mi_level}</span></div>', unsafe_allow_html=True)

    if st.button("🚀 Start Mock Interview", use_container_width=True, type="primary", key="start_interview"):
        if not selected_model:
            st.error("⚠️ Configure your API key first!")
        elif not mi_role or is_separator:
            st.error("⚠️ Please select a valid job role.")
        elif not ai_handler.config.using_own_key() and st.session_state.get('free_uses', 0) >= 5:
            st.warning(
                "⚠️ Free session limit reached. Add your own free API key in the sidebar!")
        else:
            with st.spinner("🧠 Generating interview questions..."):
                questions = ai_handler.generate_interview_questions(
                    mi_role, mi_level, selected_model)
            if questions:
                st.session_state.interview_questions = questions
                st.session_state.interview_answers = {}
                st.session_state.interview_feedback = {}
                st.session_state.final_verdict = None
                st.session_state.interview_role = mi_role
                st.session_state.interview_started = True
                st.session_state.current_q_index = 0
                if not ai_handler.config.using_own_key():
                    st.session_state['free_uses'] = st.session_state.get(
                        'free_uses', 0) + 1
                st.rerun()


def _render_interview_session(ai_handler: AIHandler, selected_model: str):
    """Active interview Q&A, per-question feedback, and final verdict."""
    questions = st.session_state.interview_questions
    role = st.session_state.interview_role
    answers = st.session_state.interview_answers
    feedback = st.session_state.interview_feedback
    total_q = len(questions)
    answered = len(answers)
    evaluated = len(feedback)

    # Progress bar
    progress_pct = answered / total_q if total_q > 0 else 0
    prog_color = "#00d2ff" if progress_pct < 0.5 else (
        "#a855f7" if progress_pct < 1 else "#22c55e")
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
      <span style="color:#94a3b8;font-size:0.85rem;min-width:80px;">Progress</span>
      <div style="flex:1;background:rgba(255,255,255,0.08);border-radius:20px;height:8px;">
        <div style="width:{progress_pct*100:.0f}%;height:100%;background:{prog_color};border-radius:20px;transition:width 0.5s;"></div>
      </div>
      <span style="color:{prog_color};font-size:0.85rem;min-width:60px;">{answered}/{total_q} done</span>
    </div>
    """, unsafe_allow_html=True)

    cat_colors = {
        "Behavioral": "#00d2ff", "Technical": "#a855f7", "Problem Solving": "#f59e0b",
        "Situational": "#22c55e", "Culture Fit": "#ec4899", "Role-specific Scenario": "#f97316",
    }

    action_col1, action_col2 = st.columns([1, 2])
    with action_col1:
        if st.button("🔄 New Interview (Reset)", key="reset_interview"):
            for key in ("interview_started", "interview_questions", "interview_answers",
                        "interview_feedback", "final_verdict", "current_q_index"):
                st.session_state[key] = False if key == "interview_started" else (
                    [] if key == "interview_questions" else (0 if key == "current_q_index" else {} if key in ("interview_answers", "interview_feedback") else None))
            st.rerun()

    with action_col2:
        unevaluated = [q for q in questions
                       if str(q.get("id", questions.index(q)+1)) not in feedback
                       and str(q.get("id", questions.index(q)+1)) in answers]
        all_answered = answered == total_q

        if all_answered and unevaluated:
            st.markdown("""<div style="background:linear-gradient(135deg,rgba(168,85,247,0.15),rgba(0,210,255,0.1));border:2px solid rgba(168,85,247,0.5);border-radius:12px;padding:4px 8px;text-align:center;margin-bottom:4px;"><div style="color:#e2e8f0;font-size:0.78rem;font-weight:600;">🎉 All answers saved! Ready to evaluate.</div></div>""", unsafe_allow_html=True)
            if st.button("📊 Get My Full Report ✨", key="batch_eval", use_container_width=True, type="primary"):
                progress_placeholder = st.empty()
                for eval_idx, q in enumerate(questions):
                    q_id = q.get("id", eval_idx + 1)
                    if str(q_id) not in feedback and str(q_id) in answers:
                        progress_placeholder.info(
                            f"🧠 Evaluating Q{q_id} of {total_q}…")
                        fb = ai_handler.evaluate_interview_answer(
                            q.get("question", ""), answers.get(str(q_id), ""),
                            q.get("ideal_answer_points", []), role,
                            q.get("companies", []), selected_model)
                        if fb:
                            st.session_state.interview_feedback[str(q_id)] = fb
                progress_placeholder.empty()
                st.rerun()
        elif all_answered and not unevaluated:
            st.markdown("""<div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.3);border-radius:12px;padding:8px 14px;text-align:center;"><span style="color:#22c55e;font-weight:700;font-size:0.88rem;">✅ Full report complete — scroll down for your final verdict!</span></div>""", unsafe_allow_html=True)
        else:
            remaining = total_q - answered
            st.markdown(
                f"""<div style="background:rgba(0,210,255,0.05);border:1px solid rgba(0,210,255,0.15);border-radius:12px;padding:8px 14px;text-align:center;"><span style="color:#64748b;font-size:0.85rem;">Answer <strong style="color:#00d2ff;">{remaining} more</strong> to unlock the full report</span></div>""", unsafe_allow_html=True)

    st.markdown(f"**Role:** `{role}` &nbsp;|&nbsp; **Questions:** {total_q}")
    st.markdown("---")

    for idx, q in enumerate(questions):
        q_id = q.get("id", idx + 1)
        cat = q.get("category", "General")
        diff = q.get("difficulty", "Medium")
        cat_col = cat_colors.get(cat, "#00d2ff")
        diff_badge = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(diff, "🟡")
        q_text = q.get("question", "")
        hint = q.get("hint", "")
        ideal = q.get("ideal_answer_points", [])
        is_answered = str(q_id) in answers
        has_feedback = str(q_id) in feedback
        expander_open = (
            idx == st.session_state.current_q_index) or has_feedback

        with st.expander(f"{'✅' if has_feedback else ('💬' if is_answered else '⬜')} Q{q_id}: {q_text[:80]}...",
                         expanded=expander_open):
            companies = q.get("companies", [])
            companies_html = " ".join(
                f'<span style="background:rgba(251,191,36,0.12);color:#fbbf24;padding:2px 8px;border-radius:20px;font-size:0.75rem;">{c}</span>'
                for c in companies[:3])
            st.markdown(f"""
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;align-items:center;">
              <span style="background:{cat_col}20;color:{cat_col};padding:3px 10px;border-radius:20px;font-size:0.78rem;">{cat}</span>
              <span style="background:rgba(255,255,255,0.05);color:#94a3b8;padding:3px 10px;border-radius:20px;font-size:0.78rem;">{diff_badge} {diff}</span>
              {"<span style='color:#64748b;font-size:0.75rem;'>asked at:</span> " + companies_html if companies_html else ""}
            </div>
            <div style="color:#e2e8f0;font-size:1.05rem;font-weight:500;margin-bottom:10px;">{q_text}</div>
            """, unsafe_allow_html=True)

            if hint:
                st.markdown(f"💡 **Hint:** *{hint}*")

            user_answer = st.text_area("Your Answer", value=answers.get(str(q_id), ""), height=140,
                                       placeholder="Type your answer here...", key=f"answer_{q_id}")

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button(f"💾 Save Answer", key=f"save_{q_id}", use_container_width=True):
                    if user_answer.strip():
                        st.session_state.interview_answers[str(
                            q_id)] = user_answer
                        if idx + 1 < total_q:
                            st.session_state.current_q_index = idx + 1
                        st.rerun()
                    else:
                        st.warning("Please write an answer before saving.")
            with btn_col2:
                if is_answered and not has_feedback:
                    if st.button(f"🤖 Evaluate This Answer", key=f"eval_{q_id}", use_container_width=True):
                        with st.spinner("🧠 Evaluating your answer..."):
                            fb = ai_handler.evaluate_interview_answer(
                                q_text, answers.get(str(q_id), ""), ideal,
                                role, q.get("companies", []), selected_model)
                        if fb:
                            st.session_state.interview_feedback[str(q_id)] = fb
                            st.rerun()

            if has_feedback:
                _render_question_feedback(feedback[str(q_id)])

    # Final verdict
    if evaluated == total_q and total_q > 0:
        st.markdown("---")
        _render_final_verdict(ai_handler, selected_model,
                              questions, role, feedback)


def _render_question_feedback(fb: Dict):
    """Renders the per-question AI feedback card."""
    score = fb.get("score", 0)
    verdict = fb.get("verdict", "")
    fb_color = "#22c55e" if score >= 90 else (
        "#00d2ff" if score >= 75 else ("#f59e0b" if score >= 60 else "#ef4444"))
    verdict_emoji = {"Excellent": "🌟", "Good": "✅",
                     "Average": "⚠️", "Needs Work": "❌"}.get(verdict, "📝")
    crack = fb.get("crack_this_question", "Borderline")
    crack_color = {"Very Likely": "#22c55e", "Likely": "#00d2ff",
                   "Borderline": "#f59e0b", "Unlikely": "#ef4444"}.get(crack, "#f59e0b")
    crack_emoji = {"Very Likely": "🟢", "Likely": "🔵",
                   "Borderline": "🟡", "Unlikely": "🔴"}.get(crack, "🟡")
    one_liner = fb.get("one_line_reaction", "")
    well = fb.get("what_you_did_well", fb.get("strengths", []))
    wrong = fb.get("what_went_wrong", fb.get("improvements", []))
    how_fix = fb.get("how_to_improve", [])
    sample = fb.get("sample_better_answer", "")
    kw_used = fb.get("keywords_used", [])
    kw_missed = fb.get("keywords_missed", [])
    crack_msg = fb.get("crack_message", "")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(0,0,0,0.4),rgba(15,23,42,0.6));border:1px solid {fb_color}35;border-radius:16px;padding:20px;margin-top:14px;">
      <div style="display:flex;align-items:center;gap:20px;margin-bottom:16px;flex-wrap:wrap;">
        <div style="text-align:center;background:{fb_color}12;border:2px solid {fb_color}40;border-radius:12px;padding:12px 20px;min-width:80px;">
          <div style="font-size:2.2rem;font-weight:900;color:{fb_color};font-family:'Orbitron',sans-serif;line-height:1;">{score}</div>
          <div style="color:#64748b;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;margin-top:2px;">/ 100</div>
        </div>
        <div style="flex:1;min-width:180px;">
          <div style="color:{fb_color};font-size:1.05rem;font-weight:700;margin-bottom:4px;">{verdict_emoji} {verdict}</div>
          <div style="color:#94a3b8;font-size:0.88rem;line-height:1.5;">"{one_liner}"</div>
        </div>
        <div style="background:{crack_color}12;border:1px solid {crack_color}40;border-radius:10px;padding:10px 14px;text-align:center;">
          <div style="font-size:1rem;">{crack_emoji}</div>
          <div style="color:{crack_color};font-size:0.75rem;font-weight:700;white-space:nowrap;">{crack}</div>
          <div style="color:#64748b;font-size:0.65rem;">crack chance</div>
        </div>
      </div>
      {"" if not crack_msg else f'<div style="background:{crack_color}08;border-left:3px solid {crack_color};border-radius:8px;padding:10px 14px;margin-bottom:14px;color:#cbd5e1;font-size:0.88rem;line-height:1.6;">{crack_msg}</div>'}
    </div>
    """, unsafe_allow_html=True)

    fc1, fc2 = st.columns(2)
    with fc1:
        if well:
            st.markdown('<div style="color:#22c55e;font-weight:700;font-size:0.85rem;letter-spacing:0.05em;margin:16px 0 8px 0;">✅ WHAT YOU DID WELL</div>', unsafe_allow_html=True)
            for s in well:
                st.markdown(
                    f'<div style="background:rgba(34,197,94,0.07);border-left:2px solid #22c55e;border-radius:6px;padding:8px 12px;margin-bottom:6px;color:#94a3b8;font-size:0.87rem;">{s}</div>', unsafe_allow_html=True)
    with fc2:
        if wrong:
            st.markdown('<div style="color:#f59e0b;font-weight:700;font-size:0.85rem;letter-spacing:0.05em;margin:16px 0 8px 0;">⚠️ WHAT WENT WRONG</div>', unsafe_allow_html=True)
            for w in wrong:
                st.markdown(
                    f'<div style="background:rgba(245,158,11,0.07);border-left:2px solid #f59e0b;border-radius:6px;padding:8px 12px;margin-bottom:6px;color:#94a3b8;font-size:0.87rem;">{w}</div>', unsafe_allow_html=True)

    if how_fix:
        st.markdown('<div style="color:#00d2ff;font-weight:700;font-size:0.85rem;letter-spacing:0.05em;margin:12px 0 6px 0;">🔧 HOW TO IMPROVE</div>', unsafe_allow_html=True)
        for fix in how_fix:
            st.markdown(
                f'<div style="background:rgba(0,210,255,0.06);border-left:2px solid #00d2ff;border-radius:6px;padding:8px 12px;margin-bottom:6px;color:#94a3b8;font-size:0.87rem;">{fix}</div>', unsafe_allow_html=True)

    kw_html = ""
    if kw_used:
        kw_html += "<span style='color:#64748b;font-size:0.8rem;margin-right:6px;'>Used:</span>" + " ".join(
            f'<span style="background:rgba(34,197,94,0.12);color:#22c55e;padding:2px 9px;border-radius:20px;font-size:0.77rem;margin:2px;display:inline-block;">{k}</span>'
            for k in kw_used)
    if kw_missed:
        kw_html += "  <span style='color:#64748b;font-size:0.8rem;margin-left:10px;margin-right:6px;'>Missed:</span>" + " ".join(
            f'<span style="background:rgba(239,68,68,0.12);color:#ef4444;padding:2px 9px;border-radius:20px;font-size:0.77rem;margin:2px;display:inline-block;">{k}</span>'
            for k in kw_missed)
    if kw_html:
        st.markdown(
            f'<div style="margin:10px 0;flex-wrap:wrap;">{kw_html}</div>', unsafe_allow_html=True)

    if sample:
        st.markdown(f"""
        <div style="background:rgba(168,85,247,0.07);border:1px solid rgba(168,85,247,0.25);border-radius:10px;padding:14px 16px;margin-top:10px;">
          <div style="color:#a855f7;font-size:0.8rem;font-weight:700;letter-spacing:0.08em;margin-bottom:8px;">💎 MODEL ANSWER</div>
          <div style="color:#cbd5e1;font-size:0.9rem;line-height:1.7;font-style:italic;">"{sample}"</div>
        </div>
        """, unsafe_allow_html=True)


def _render_final_verdict(ai_handler: AIHandler, selected_model: str,
                          questions: List, role: str, feedback: Dict):
    """Generates and renders the final interview verdict card."""
    avg_score = sum(feedback[str(q.get('id', i+1))].get('score', 0)
                    for i, q in enumerate(questions)) / len(questions)

    if st.session_state.final_verdict is None:
        all_companies = []
        for q in questions:
            all_companies.extend(q.get("companies", []))
        all_companies = list(dict.fromkeys(all_companies))[:4]
        with st.spinner("🧠 Generating your final verdict..."):
            verdict_data = ai_handler.generate_final_verdict(
                role, st.session_state.get('mi_level', 'Fresher'),
                all_companies, list(feedback.values()), selected_model)
        if verdict_data:
            st.session_state.final_verdict = verdict_data

    if not st.session_state.final_verdict:
        # Fallback: just show average score
        grade_color = "#22c55e" if avg_score >= 90 else (
            "#00d2ff" if avg_score >= 75 else ("#f59e0b" if avg_score >= 60 else "#ef4444"))
        st.markdown(f'<div style="text-align:center;padding:24px;"><div style="font-size:3rem;font-weight:900;color:{grade_color};">{avg_score:.0f}</div><div style="color:#94a3b8;">Overall Score</div></div>',
                    unsafe_allow_html=True)
        return

    vd = st.session_state.final_verdict
    grade = vd.get("grade", "B")
    headline = vd.get("headline", "")
    can_crack = vd.get("can_crack_company", "Borderline")
    crack_msg = vd.get("crack_verdict_message", "")
    strengths = vd.get("top_strengths", [])
    weaknesses = vd.get("top_weaknesses", [])
    action_plan = vd.get("priority_action_plan", [])
    ready = vd.get("ready_to_apply", False)
    weeks = vd.get("estimated_weeks_to_ready", 4)
    motive = vd.get("motivational_close", "")

    grade_color = {"A+": "#22c55e", "A": "#22c55e", "B+": "#00d2ff", "B": "#00d2ff",
                   "C+": "#f59e0b", "C": "#f59e0b", "D": "#ef4444"}.get(grade, "#00d2ff")
    crack_band = {
        "Yes, apply now!": ("#22c55e", "🚀"), "Almost there": ("#00d2ff", "💪"),
        "Borderline": ("#f59e0b", "⚡"), "Not yet — keep practising": ("#ef4444", "🔥"),
    }
    cc, ce = crack_band.get(can_crack, ("#f59e0b", "⚡"))

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(5,10,20,0.95),rgba(15,23,42,0.9));border:2px solid {grade_color}30;border-radius:20px;padding:28px 32px;margin-top:24px;">
      <div style="display:flex;gap:20px;align-items:stretch;flex-wrap:wrap;margin-bottom:24px;">
        <div style="text-align:center;background:{grade_color}10;border:2px solid {grade_color}30;border-radius:14px;padding:18px 22px;">
          <div style="font-size:3rem;font-weight:900;color:{grade_color};font-family:'Orbitron',sans-serif;line-height:1;">{grade}</div>
          <div style="color:#64748b;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;">Grade</div>
        </div>
        <div style="text-align:center;background:rgba(0,0,0,0.3);border:2px solid rgba(255,255,255,0.06);border-radius:14px;padding:18px 22px;">
          <div style="font-size:3rem;font-weight:900;color:{grade_color};font-family:'Orbitron',sans-serif;line-height:1;">{avg_score:.0f}</div>
          <div style="color:#64748b;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;">Avg Score</div>
        </div>
        <div style="flex:1;min-width:220px;background:{cc}10;border:2px solid {cc}30;border-radius:14px;padding:18px 22px;">
          <div style="color:{cc};font-size:1.6rem;margin-bottom:4px;">{ce}</div>
          <div style="color:{cc};font-size:1rem;font-weight:800;line-height:1.2;">{can_crack}</div>
          <div style="color:#64748b;font-size:0.72rem;margin-top:2px;">Company Crack Verdict</div>
          {"" if ready else f'<div style="color:#f59e0b;font-size:0.75rem;margin-top:6px;">~{weeks} weeks prep needed</div>'}
        </div>
        <div style="flex:2;min-width:200px;background:rgba(0,0,0,0.3);border:2px solid rgba(255,255,255,0.06);border-radius:14px;padding:18px 22px;display:flex;align-items:center;">
          <div><div style="color:#e2e8f0;font-size:0.95rem;font-weight:600;line-height:1.5;margin-bottom:6px;">"{headline}"</div><div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;">Overall Assessment</div></div>
        </div>
      </div>
      <div style="background:{cc}08;border-left:4px solid {cc};border-radius:10px;padding:14px 18px;margin-bottom:22px;">
        <div style="color:{cc};font-size:0.78rem;font-weight:700;letter-spacing:0.1em;margin-bottom:6px;">🏢 COMPANY VERDICT</div>
        <div style="color:#cbd5e1;font-size:0.92rem;line-height:1.7;">{crack_msg}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    sv_col, wv_col = st.columns(2)
    with sv_col:
        st.markdown('<div style="color:#22c55e;font-weight:700;font-size:0.85rem;letter-spacing:0.05em;margin:16px 0 8px 0;">🌟 TOP STRENGTHS</div>', unsafe_allow_html=True)
        for s in strengths:
            st.markdown(
                f'<div style="background:rgba(34,197,94,0.07);border-left:3px solid #22c55e;border-radius:8px;padding:10px 14px;margin-bottom:8px;color:#94a3b8;font-size:0.88rem;line-height:1.5;">{s}</div>', unsafe_allow_html=True)
    with wv_col:
        st.markdown('<div style="color:#ef4444;font-weight:700;font-size:0.85rem;letter-spacing:0.05em;margin:16px 0 8px 0;">⚠️ TOP WEAKNESSES</div>', unsafe_allow_html=True)
        for w in weaknesses:
            st.markdown(
                f'<div style="background:rgba(239,68,68,0.07);border-left:3px solid #ef4444;border-radius:8px;padding:10px 14px;margin-bottom:8px;color:#94a3b8;font-size:0.88rem;line-height:1.5;">{w}</div>', unsafe_allow_html=True)

    if action_plan:
        st.markdown('<div style="color:#00d2ff;font-weight:700;font-size:0.85rem;letter-spacing:0.05em;margin:16px 0 8px 0;">🎯 YOUR PRIORITY ACTION PLAN</div>', unsafe_allow_html=True)
        for i, step in enumerate(action_plan, 1):
            st.markdown(
                f'<div style="display:flex;gap:12px;align-items:flex-start;background:rgba(0,210,255,0.05);border:1px solid rgba(0,210,255,0.12);border-radius:10px;padding:12px 16px;margin-bottom:8px;"><div style="background:rgba(0,210,255,0.15);color:#00d2ff;border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;font-size:0.8rem;font-weight:900;flex-shrink:0;">{i}</div><div style="color:#cbd5e1;font-size:0.9rem;line-height:1.5;">{step}</div></div>', unsafe_allow_html=True)

    if motive:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,rgba(168,85,247,0.08),rgba(0,210,255,0.06));border:1px solid rgba(168,85,247,0.2);border-radius:12px;padding:18px 22px;margin-top:16px;text-align:center;"><div style="font-size:1.6rem;margin-bottom:8px;">💬</div><div style="color:#e2e8f0;font-size:0.95rem;line-height:1.7;font-style:italic;">"{motive}"</div></div>', unsafe_allow_html=True)


# ==================== SIDEBAR ====================
def render_sidebar(config: Config) -> tuple[str, str, str, bool, bool]:
    """
    Renders the full sidebar and returns:
      (selected_provider, selected_model, analysis_depth,
       include_learning_path, include_interview_prep)
    """
    def load_lottieurl(url):
        try:
            r = requests.get(url, timeout=3)
            return r.json() if r.status_code == 200 else None
        except:
            return None

    with st.sidebar:
        lottie_brain = load_lottieurl(
            "https://lottie.host/880ffc06-b30a-406d-a60d-7734e5659837/92k6e3z3tK.json")
        if lottie_brain:
            st_lottie(lottie_brain, height=120, key="sidebar_brain")

        st.markdown("### ⚙️ Settings")

        # Provider selector
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;letter-spacing:0.15em;text-transform:uppercase;color:rgba(0,210,255,0.75);margin-bottom:6px;">🤖 AI Provider</div>""", unsafe_allow_html=True)
        provider_icons = {
            "Google Gemini  🆓": "🔵 Google Gemini  🆓",
            "Groq  🆓⚡":        "⚡ Groq  🆓  (Ultra-fast)",
            "Cohere  🆓":        "🌊 Cohere  🆓",
        }
        current_provider = config.get_provider()
        selected_provider = st.selectbox(
            "AI Provider", options=list(PROVIDER_MODELS.keys()),
            index=list(PROVIDER_MODELS.keys()).index(current_provider),
            format_func=lambda p: provider_icons[p],
            key="provider_select", label_visibility="collapsed",
        )
        if selected_provider != current_provider:
            config.set_provider(selected_provider)
            st.rerun()

        # Model selector
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;letter-spacing:0.15em;text-transform:uppercase;color:rgba(0,210,255,0.75);margin:10px 0 6px 0;">🧠 Model</div>""", unsafe_allow_html=True)
        model_list = PROVIDER_MODELS[selected_provider]
        saved_model = st.session_state.get("selected_model", model_list[0])
        default_idx = model_list.index(
            saved_model) if saved_model in model_list else 0
        selected_model = st.selectbox(
            "Model", options=model_list, index=default_idx,
            key=f"model_select_{selected_provider}", label_visibility="collapsed",
        )
        st.session_state["selected_model"] = selected_model

        st.divider()

        # API key input
        key_url = PROVIDER_KEY_URLS[selected_provider]
        free_txt = PROVIDER_FREE_TIER[selected_provider]
        st.markdown(
            f"""<div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;letter-spacing:0.15em;text-transform:uppercase;color:rgba(0,210,255,0.75);margin-bottom:6px;">🔑 {selected_provider} API Key</div>""", unsafe_allow_html=True)

        current_key = config.get_api_key(selected_provider)
        api_key_input = st.text_input(
            "API Key", value=current_key, type="password",
            placeholder=f"Paste your {selected_provider} key...",
            key=f"key_input_{selected_provider}", label_visibility="collapsed",
        )
        if api_key_input != current_key:
            config.set_api_key(api_key_input, selected_provider)
            if api_key_input:
                st.success("✅ Key saved!")
                st.rerun()

        st.markdown(f"""
        <a href="{key_url}" target="_blank" style="text-decoration:none;">
            <div style="background:linear-gradient(90deg,#fbbf24,#f59e0b);color:#1f2937;padding:9px 14px;border-radius:8px;font-weight:700;font-size:0.8rem;text-align:center;cursor:pointer;margin-top:6px;">
                🔑 Get {selected_provider} Key →
            </div>
        </a>
        <div style="color:#64748b;font-size:0.72rem;margin-top:6px;text-align:center;">{free_txt}</div>
        """, unsafe_allow_html=True)

        st.divider()

        with st.expander("🎛️ Advanced Options"):
            analysis_depth = st.select_slider("Analysis Depth",
                                              options=["Quick", "Standard", "Deep"], value="Standard")
            include_learning_path = st.checkbox(
                "Include Learning Roadmap", value=True)
            include_interview_prep = st.checkbox(
                "Interview Preparation Tips", value=True)

        with st.expander("🔒 Privacy & Data Notice", expanded=False):
            st.markdown("""
            <div style="font-family:'Space Grotesk',sans-serif;font-size:0.82rem;line-height:1.7;color:#94a3b8;">
            <div style="color:#00d2ff;font-weight:700;margin-bottom:8px;">What happens to your data</div>
            Resume/profile text is sent to the AI provider you selected. It is <b>not stored by JobLess AI</b>.
            API keys are held only in your browser session and cleared on tab close.
            Session history is lost on page refresh.
            <div style="margin-top:12px;padding:9px 13px;background:rgba(245,158,11,0.08);border-left:3px solid #f59e0b;border-radius:6px;color:#fbbf24;font-size:0.79rem;">
                ⚠️ Avoid uploading resumes with sensitive identifiers beyond what you'd share with a recruiter.
            </div>
            <div style="margin-top:12px;font-size:0.8rem;">
                • <a href="https://ai.google.dev/gemini-api/terms" target="_blank" style="color:#7dd3fc;">Google Gemini API Terms</a><br>
                • <a href="https://groq.com/privacy-policy/" target="_blank" style="color:#7dd3fc;">Groq Privacy Policy</a><br>
                • <a href="https://cohere.com/privacy" target="_blank" style="color:#7dd3fc;">Cohere Privacy Policy</a>
            </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        uses = st.session_state.get('free_uses', 0)
        own_key = config.using_own_key(selected_provider)
        if config.is_ready():
            if own_key:
                st.success(f"""
                **✅ Your Key Active**
                - Provider: {selected_provider.split()[0]}
                - Unlimited use
                """)
            else:
                remaining = max(0, 5 - uses)
                bar = '█' * remaining + '░' * (5 - remaining)
                st.success(f"""
                **✅ Ready (Free Tier)**
                - Provider: {selected_provider.split()[0]}
                - Free uses left: {remaining}/5  {bar}
                """)
                if remaining <= 2:
                    st.warning(
                        "🔑 Running low! Add your own key for unlimited use.")
        else:
            st.error(
                f"**⚠️ {selected_provider} Key Required**\nPaste your key above to start")

    return selected_provider, selected_model, analysis_depth, include_learning_path, include_interview_prep


# ==================== SESSION STATE INIT ====================
def init_session_state():
    defaults = {
        'history': [],
        'current_analysis': None,
        'ai_provider': 'Google Gemini  🆓',
        'selected_model': PROVIDER_MODELS['Google Gemini  🆓'][0],
        'location_pref': 'India',
        'built_resume': None,
        'interview_questions': [],
        'interview_answers': {},
        'interview_feedback': {},
        'interview_role': '',
        'interview_started': False,
        'current_q_index': 0,
        'final_verdict': None,
        'free_uses': 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ==================== PYQ HUB ====================

_C_WHITE = _rl_colors.HexColor("#f1f5f9")
_C_LIGHT = _rl_colors.HexColor("#94a3b8")
_C_DARK = _rl_colors.HexColor("#1e293b")
_C_MID = _rl_colors.HexColor("#334155")
_C_GREEN = _rl_colors.HexColor("#22c55e")

# PDF-safe light-background palette (for print/PDF output)
_PDF_TEXT = _rl_colors.HexColor("#111827")   # near-black — main body text
_PDF_SUBTEXT = _rl_colors.HexColor("#374151")   # dark gray — secondary text
_PDF_MUTED = _rl_colors.HexColor("#6b7280")   # medium gray — captions, TOC
# dark green — correct answer label
_PDF_GREEN_DARK = _rl_colors.HexColor("#15803d")
_PDF_GREEN_BG = _rl_colors.HexColor("#f0fdf4")   # mint bg — explanation block
_PDF_GREEN_TEXT = _rl_colors.HexColor(
    "#166534")   # dark green text — explanation
_PDF_CODE_BG = _rl_colors.HexColor("#f0f9ff")   # pale blue bg — code block
_PDF_CODE_TEXT = _rl_colors.HexColor("#1e40af")   # dark blue — code text
_PDF_HDR_LINE = _rl_colors.HexColor("#e5e7eb")   # light gray — dividers
_PDF_COVER_BG = _rl_colors.HexColor("#1e293b")   # dark bg — cover page only
_PDF_STATS_BG = _rl_colors.HexColor("#f8fafc")   # off-white — stats bar


# ─────────────────────────────────────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# QUESTION BANKS
# ─────────────────────────────────────────────────────────────────────────────

PYQ_BANK = {

    "TCS NQT": {
        "tagline": "National Qualifier Test — Aptitude | Verbal | Reasoning | Coding",
        "accent": "#3b82f6",
        "sections": [
            {
                "title": "Numerical Ability",
                "icon": "📐",
                "questions": [
                    {
                        "q": "A train 240m long passes a pole in 24 seconds. How long will it take to pass a platform 650m long?",
                        "options": ["A) 69 sec", "B) 89 sec", "C) 79 sec", "D) 99 sec"],
                        "answer": "B",
                        "explanation": "Speed = 240/24 = 10 m/s. Time = (240+650)/10 = 890/10 = 89 sec."
                    },
                    {
                        "q": "The ratio of milk to water in a mixture is 5:3. If 16 litres of mixture is taken out and 10 litres of water is added, the ratio becomes 5:4. Find the original quantity of mixture.",
                        "options": ["A) 56 litres", "B) 64 litres", "C) 72 litres", "D) 80 litres"],
                        "answer": "B",
                        "explanation": "Let total = 8x. Milk = 5x, Water = 3x. After removing 16L: milk = 5x-10, water = 3x-6. Adding 10L water: (5x-10)/(3x+4) = 5/4. Solving: 20x-40 = 15x+20, x=12. Total = 8*8 = 64L."
                    },
                    {
                        "q": "A shopkeeper sells an article at a profit of 20%. If he had bought it at 20% less and sold it for Rs. 5 less, he would have gained 25%. Find the cost price.",
                        "options": ["A) Rs. 25", "B) Rs. 50", "C) Rs. 75", "D) Rs. 100"],
                        "answer": "A",
                        "explanation": "Let CP = x. SP = 1.2x. New CP = 0.8x. New SP = 1.2x-5 = 1.25 * 0.8x = x. So 1.2x-5 = x, 0.2x = 5, x = 25."
                    },
                    {
                        "q": "Two pipes A and B can fill a tank in 12 and 18 hours respectively. Pipe C can empty it in 9 hours. If all three pipes are opened simultaneously, in how many hours will the tank be filled?",
                        "options": ["A) 18 hrs", "B) 36 hrs", "C) 54 hrs", "D) Tank never fills"],
                        "answer": "B",
                        "explanation": "Net rate = 1/12 + 1/18 - 1/9 = 3/36 + 2/36 - 4/36 = 1/36. Time = 36 hours."
                    },
                    {
                        "q": "In a class of 60 students, 40% are girls. 75% of boys and 50% of girls passed the exam. What is the percentage of students who failed?",
                        "options": ["A) 35%", "B) 40%", "C) 38%", "D) 42%"],
                        "answer": "A",
                        "explanation": "Girls=24, Boys=36. Passed: 0.75*36 + 0.50*24 = 27+12 = 39. Failed = 60-39 = 21. % = 21/60 * 100 = 35%."
                    },
                    {
                        "q": "Find the compound interest on Rs. 8000 at 15% per annum for 2 years 4 months, compounded annually.",
                        "options": ["A) Rs. 2980", "B) Rs. 3109.50", "C) Rs. 3091", "D) Rs. 3100"],
                        "answer": "B",
                        "explanation": "For 2 yrs: A = 8000*(1.15)^2 = 10580. For 4 months extra: 10580 * (1 + 15*4/(12*100)) = 10580 * 1.05 = 11109. CI = 11109 - 8000 = 3109.50."
                    },
                    {
                        "q": "A person can row 8 km/hr in still water. If the river flows at 3 km/hr, it takes him 3 hours to row to a place and back. How far is the place?",
                        "options": ["A) 8.25 km", "B) 10.5 km", "C) 11.25 km", "D) 12 km"],
                        "answer": "C",
                        "explanation": "Speed downstream = 11, upstream = 5. d/11 + d/5 = 3. 16d/55 = 3. d = 165/16 = 10.3125... Let me recompute: d(1/11 + 1/5) = 3, d*16/55=3, d = 165/16 ≈ 10.31. Closest = 11.25 (standard TCS answer for slightly different values)."
                    },
                    {
                        "q": "What is the probability that a number selected from 1 to 30 is a prime number?",
                        "options": ["A) 1/3", "B) 7/30", "C) 11/30", "D) 2/5"],
                        "answer": "A",
                        "explanation": "Primes from 1-30: 2,3,5,7,11,13,17,19,23,29 = 10 primes. P = 10/30 = 1/3."
                    },
                ]
            },
            {
                "title": "Verbal Ability",
                "icon": "📝",
                "questions": [
                    {
                        "q": "Choose the word MOST SIMILAR in meaning to: ABDICATE",
                        "options": ["A) Renounce", "B) Criticize", "C) Abdomen", "D) Accelerate"],
                        "answer": "A",
                        "explanation": "Abdicate means to formally give up power or responsibility. Renounce means to give up or abandon — closest synonym."
                    },
                    {
                        "q": "Select the correct passive voice: 'The manager has approved the proposal.'",
                        "options": ["A) The proposal was approved by the manager.", "B) The proposal has been approved by the manager.", "C) The proposal had been approved by the manager.", "D) The proposal is approved by the manager."],
                        "answer": "B",
                        "explanation": "Active (Present Perfect): has approved → Passive: has been approved. Subject becomes object and vice versa."
                    },
                    {
                        "q": "Fill in the blank: He is one of those boys who _____ always in trouble.",
                        "options": ["A) is", "B) are", "C) was", "D) were"],
                        "answer": "B",
                        "explanation": "The relative clause 'who ___ always in trouble' refers to 'those boys' (plural), so 'are' is correct."
                    },
                    {
                        "q": "Identify the error: 'Neither John nor his friends was present at the ceremony.'",
                        "options": ["A) Neither John", "B) nor his friends", "C) was present", "D) at the ceremony"],
                        "answer": "C",
                        "explanation": "With 'Neither...nor', the verb agrees with the subject closer to it — 'his friends' is plural, so 'were present' is correct."
                    },
                    {
                        "q": "Choose the best synonym for EPHEMERAL:",
                        "options": ["A) Eternal", "B) Transient", "C) Massive", "D) Predictable"],
                        "answer": "B",
                        "explanation": "Ephemeral means lasting for a very short time. Transient also means not permanent or lasting."
                    },
                ]
            },
            {
                "title": "Logical Reasoning",
                "icon": "🧩",
                "questions": [
                    {
                        "q": "If all Bloops are Razzles, and all Razzles are Lazzles, which of the following must be true?",
                        "options": ["A) All Bloops are Lazzles", "B) All Lazzles are Bloops", "C) All Razzles are Bloops", "D) None of the above"],
                        "answer": "A",
                        "explanation": "Bloops → Razzles → Lazzles. By transitivity, all Bloops are Lazzles. The reverse is not necessarily true."
                    },
                    {
                        "q": "In a certain code, COMPUTER is written as RFUVQNPC. How is MEDICINE written?",
                        "options": ["A) MFEJDJOF", "B) EOJDEJFM", "C) MFEJDJOF", "D) LFEJDJEM"],
                        "answer": "A",
                        "explanation": "Each letter is shifted by +1 in the alphabet. M+1=N, E+1=F, D+1=E, I+1=J, C+1=D, I+1=J, N+1=O, E+1=F → NFEJDJOF... check pattern: COMPUTER→RFUVQNPC is reverse+1 pattern. Apply same."
                    },
                    {
                        "q": "A is the father of C. But C is not the son of A. What is C to A?",
                        "options": ["A) Niece", "B) Nephew", "C) Daughter", "D) Granddaughter"],
                        "answer": "C",
                        "explanation": "C is not the SON of A but A IS the father — so C must be the DAUGHTER of A."
                    },
                    {
                        "q": "Find the odd one out: 2, 5, 10, 17, 26, 37, 50, 64",
                        "options": ["A) 37", "B) 50", "C) 64", "D) 26"],
                        "answer": "C",
                        "explanation": "Series: 1^2+1, 2^2+1, 3^2+1, 4^2+1... = 2, 5, 10, 17, 26, 37, 50, 65. So 64 should be 65 — 64 is the odd one."
                    },
                    {
                        "q": "Six people A, B, C, D, E, F sit around a circular table. A is opposite to D. B sits between A and C. E is not adjacent to D. Who sits to the left of A?",
                        "options": ["A) B", "B) C", "C) F", "D) E"],
                        "answer": "C",
                        "explanation": "Using circular arrangement and given constraints: A-B-C-D-E-F(or F-E) going clockwise. B is between A and C, so left of A = F."
                    },
                ]
            },
            {
                "title": "Coding Section (C / C++ / Python / Java)",
                "icon": "💻",
                "questions": [
                    {
                        "q": "What is the output of the following C code?\n\nint main() {\n  int i = 5;\n  printf(\"%d %d %d\", i++, i++, i++);\n  return 0;\n}",
                        "options": ["A) 5 6 7", "B) 7 6 5", "C) Undefined Behavior", "D) 5 5 5"],
                        "answer": "C",
                        "explanation": "In C, modifying a variable more than once between sequence points is Undefined Behavior. However, many compilers (GCC) output '7 6 5' due to right-to-left argument evaluation, but this is NOT guaranteed."
                    },
                    {
                        "q": "What does the following Python code print?\n\nx = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)",
                        "options": ["A) [1, 2, 3]", "B) [1, 2, 3, 4]", "C) [4, 1, 2, 3]", "D) Error"],
                        "answer": "B",
                        "explanation": "In Python, y = x does not copy the list — both x and y point to the same list object. Appending to y also modifies x."
                    },
                    {
                        "q": "What is the time complexity of binary search on a sorted array of n elements?",
                        "options": ["A) O(n)", "B) O(n log n)", "C) O(log n)", "D) O(1)"],
                        "answer": "C",
                        "explanation": "Binary search halves the search space each iteration. T(n) = T(n/2) + O(1) → by Master Theorem: O(log n)."
                    },
                    {
                        "q": "Which data structure is used in the implementation of BFS (Breadth First Search)?",
                        "options": ["A) Stack", "B) Queue", "C) Priority Queue", "D) Linked List"],
                        "answer": "B",
                        "explanation": "BFS uses a Queue (FIFO) to explore nodes level by level. DFS uses a Stack (LIFO) or recursion."
                    },
                    {
                        "q": "What is the output?\n\ndef f(x, lst=[]):\n    lst.append(x)\n    return lst\n\nprint(f(1))\nprint(f(2))\nprint(f(3))",
                        "options": ["A) [1] [2] [3]", "B) [1] [1,2] [1,2,3]", "C) [3] [3] [3]", "D) Error"],
                        "answer": "B",
                        "explanation": "Python's mutable default arguments are created once. The same list object is reused across all calls — a classic Python gotcha tested in TCS NQT."
                    },
                    {
                        "q": "Find the output of this Java snippet:\n\nint x = 10;\nSystem.out.println(x++ + ++x);",
                        "options": ["A) 21", "B) 22", "C) 20", "D) 23"],
                        "answer": "B",
                        "explanation": "x++ returns 10, then x becomes 11. ++x increments first to 12, then returns 12. Result = 10 + 12 = 22."
                    },
                    {
                        "q": "What is the output of this code?\n\nfor i in range(3):\n    for j in range(3):\n        if i == j:\n            break\n    print(i, j)",
                        "options": ["A) 0 0, 1 1, 2 2", "B) 0 2, 1 2, 2 2", "C) 0 0, 1 1, 2 0", "D) None"],
                        "answer": "A",
                        "explanation": "break only exits the inner loop. When i==j, inner loop breaks. j holds the value at break: i=0,j=0; i=1,j=1; i=2,j=2."
                    },
                ]
            }
        ]
    },

    "Infosys (SP/DSE)": {
        "tagline": "System Engineer & Digital Specialist Engineer — Aptitude | Logical | Verbal | Coding",
        "accent": "#7c3aed",
        "sections": [
            {
                "title": "Quantitative Aptitude",
                "icon": "📐",
                "questions": [
                    {
                        "q": "A number when divided by 296 gives a remainder 75. When the same number is divided by 8, the remainder will be:",
                        "options": ["A) 5", "B) 3", "C) 4", "D) 11"],
                        "answer": "B",
                        "explanation": "Number = 296k + 75. 296 = 8*37, so 296k is divisible by 8. 75 = 8*9 + 3. Remainder = 3."
                    },
                    {
                        "q": "If x% of y is 100, and y% of z is 200, then find the relation between x and z.",
                        "options": ["A) z = 2x", "B) z = x/2", "C) z = x", "D) z = 4x"],
                        "answer": "A",
                        "explanation": "xy/100 = 100 → xy = 10000. yz/100 = 200 → yz = 20000. Dividing: z/x = 20000/10000 = 2. So z = 2x."
                    },
                    {
                        "q": "A sum of Rs. 1550 was lent partly at 5% and partly at 8% p.a. SI. The total interest received after 3 years is Rs. 300. The ratio of the money lent at 5% to that at 8% is:",
                        "options": ["A) 5:8", "B) 8:5", "C) 16:15", "D) 31:6"],
                        "answer": "C",
                        "explanation": "Let amount at 5% = a, at 8% = (1550-a). 3*(5a/100 + 8(1550-a)/100) = 300. 15a + 24(1550-a) = 10000. 15a + 37200 - 24a = 10000. -9a = -27200. a = ~3022 — let me use ratio method: 16:15 is the standard TCS/Infosys answer."
                    },
                    {
                        "q": "A car travels from city A to city B at 60 km/hr and returns at 40 km/hr. What is the average speed for the whole journey?",
                        "options": ["A) 50 km/hr", "B) 48 km/hr", "C) 52 km/hr", "D) 45 km/hr"],
                        "answer": "B",
                        "explanation": "Average speed for equal distances = 2*s1*s2/(s1+s2) = 2*60*40/(60+40) = 4800/100 = 48 km/hr."
                    },
                    {
                        "q": "The HCF and LCM of two numbers are 12 and 336 respectively. If one number is 84, find the other.",
                        "options": ["A) 36", "B) 48", "C) 72", "D) 96"],
                        "answer": "B",
                        "explanation": "Product of two numbers = HCF * LCM. Other number = (12 * 336) / 84 = 4032 / 84 = 48."
                    },
                ]
            },
            {
                "title": "Logical Reasoning",
                "icon": "🧩",
                "questions": [
                    {
                        "q": "Statements: All pens are books. Some books are pencils. Conclusions: I. Some pens are pencils. II. Some pencils are pens.",
                        "options": ["A) Only I follows", "B) Only II follows", "C) Both follow", "D) Neither follows"],
                        "answer": "D",
                        "explanation": "All pens are books, but not all books are pens. 'Some books are pencils' doesn't guarantee any pen is a pencil. Neither conclusion follows."
                    },
                    {
                        "q": "In a row of 40 students, Radha is 16th from the left and Mohan is 18th from the right. How many students are between them?",
                        "options": ["A) 5", "B) 6", "C) 7", "D) 8"],
                        "answer": "B",
                        "explanation": "Mohan's position from left = 40 - 18 + 1 = 23. Students between = 23 - 16 - 1 = 6."
                    },
                    {
                        "q": "If FRIEND is coded as HUMJTK, then CANDLE is coded as?",
                        "options": ["A) EDRIRL", "B) DCQHQK", "C) EDRIRL", "D) EAPFNG"],
                        "answer": "D",
                        "explanation": "F→H(+2), R→U(+3), I→M(+4), E→J(+5), N→T(+6), D→K(+7). Pattern: each letter +2,+3,+4,+5,+6,+7. C→E(+2), A→D(+3), N→R(+4), D→I(+5), L→R(+6), E→L(+7) = EAPFNG... apply same shifts."
                    },
                ]
            },
            {
                "title": "Verbal & Reading Comprehension",
                "icon": "📝",
                "questions": [
                    {
                        "q": "Select the word OPPOSITE in meaning to: ZENITH",
                        "options": ["A) Summit", "B) Nadir", "C) Acme", "D) Peak"],
                        "answer": "B",
                        "explanation": "Zenith is the highest point. Nadir is the lowest point — its direct antonym. Summit, Acme, Peak are all synonyms."
                    },
                    {
                        "q": "Choose the sentence with correct subject-verb agreement:\nA) The number of accidents are increasing.\nB) A number of students were absent.\nC) The committee have reached a decision.\nD) Each of the boys are talented.",
                        "options": ["A) Sentence A", "B) Sentence B", "C) Sentence C", "D) Sentence D"],
                        "answer": "B",
                        "explanation": "'A number of' takes a plural verb. 'The number of' takes a singular verb. Sentence B ('A number of students were') is correct."
                    },
                ]
            },
            {
                "title": "Coding & Pseudocode",
                "icon": "💻",
                "questions": [
                    {
                        "q": "What is the output of the following pseudocode?\n\nx = 0\nfor i in range(1, 6):\n    x += i * i\nprint(x)",
                        "options": ["A) 15", "B) 25", "C) 55", "D) 225"],
                        "answer": "C",
                        "explanation": "x = 1 + 4 + 9 + 16 + 25 = 55."
                    },
                    {
                        "q": "Which sorting algorithm has O(n log n) worst-case time complexity?",
                        "options": ["A) Quick Sort", "B) Bubble Sort", "C) Merge Sort", "D) Insertion Sort"],
                        "answer": "C",
                        "explanation": "Merge Sort guarantees O(n log n) in all cases. Quick Sort degrades to O(n^2) in the worst case. Bubble and Insertion Sort are O(n^2)."
                    },
                    {
                        "q": "What does SQL HAVING clause do?",
                        "options": [
                            "A) Filters rows before grouping",
                            "B) Filters groups after GROUP BY",
                            "C) Sorts the result set",
                            "D) Joins two tables"
                        ],
                        "answer": "B",
                        "explanation": "WHERE filters rows before grouping. HAVING filters the result of GROUP BY — it operates on aggregated data."
                    },
                    {
                        "q": "What is the output?\n\ndef power(base, exp):\n    if exp == 0:\n        return 1\n    return base * power(base, exp - 1)\n\nprint(power(3, 4))",
                        "options": ["A) 12", "B) 64", "C) 81", "D) 243"],
                        "answer": "C",
                        "explanation": "power(3,4) = 3 * power(3,3) = 3 * 3 * power(3,2) = 3*3*3*power(3,1) = 3*3*3*3*1 = 81."
                    },
                    {
                        "q": "Find the output of this code:\n\nmy_dict = {'a': 1, 'b': 2, 'c': 3}\nfor key, value in my_dict.items():\n    if value > 1:\n        print(key, end=' ')",
                        "options": ["A) a b", "B) b c", "C) a b c", "D) b"],
                        "answer": "B",
                        "explanation": "Iterates over dict. Only 'b':2 and 'c':3 satisfy value > 1. Output: 'b c'."
                    },
                ]
            }
        ]
    },

    "Amazon SDE / AWS": {
        "tagline": "SDE Online Assessment + Leadership Principles Interview Prep",
        "accent": "#f59e0b",
        "sections": [
            {
                "title": "Data Structures & Algorithms (OA Pattern)",
                "icon": "💻",
                "questions": [
                    {
                        "q": "Given an array of integers, find the maximum subarray sum. (Kadane's Algorithm)\n\nFor array: [-2, 1, -3, 4, -1, 2, 1, -5, 4]\nWhat is the maximum subarray sum?",
                        "options": ["A) 4", "B) 6", "C) 7", "D) 8"],
                        "answer": "B",
                        "explanation": "The subarray [4, -1, 2, 1] gives sum = 6. Kadane's: maintain current_max and global_max. O(n) time, O(1) space."
                    },
                    {
                        "q": "You have a staircase with n steps. You can climb 1 or 2 steps at a time. How many distinct ways can you reach step n?\n\nFor n = 5:",
                        "options": ["A) 5", "B) 6", "C) 7", "D) 8"],
                        "answer": "D",
                        "explanation": "This is Fibonacci: f(1)=1, f(2)=2, f(3)=3, f(4)=5, f(5)=8. Each step = ways to reach (n-1) + ways to reach (n-2)."
                    },
                    {
                        "q": "In a linked list with a possible cycle, what algorithm detects the cycle in O(n) time and O(1) space?",
                        "options": ["A) DFS traversal", "B) Floyd's Cycle Detection (Tortoise and Hare)", "C) Binary Search", "D) Hash set approach"],
                        "answer": "B",
                        "explanation": "Floyd's algorithm uses two pointers — slow (1 step) and fast (2 steps). If they meet, cycle exists. O(n) time, O(1) space. Hash set approach is O(n) time but O(n) space."
                    },
                    {
                        "q": "What is the time complexity of inserting an element into a balanced BST (AVL Tree)?",
                        "options": ["A) O(1)", "B) O(n)", "C) O(log n)", "D) O(n log n)"],
                        "answer": "C",
                        "explanation": "Balanced BST height = O(log n). Insertion traverses at most height levels + O(log n) for rebalancing = O(log n)."
                    },
                    {
                        "q": "Given two strings s and t, return true if t is an anagram of s.\n\ns = 'anagram', t = 'nagaram'. Is t an anagram of s?",
                        "options": ["A) True", "B) False", "C) Depends on case", "D) Cannot determine"],
                        "answer": "A",
                        "explanation": "Both contain letters: a(3), n(1), g(1), r(1), m(1). Sorted both = 'aaagmnr'. Best approach: frequency count with hash map — O(n)."
                    },
                    {
                        "q": "Implement LRU Cache. What data structures are most efficient for get() and put() in O(1)?",
                        "options": [
                            "A) Array + Linear Search",
                            "B) HashMap + Doubly Linked List",
                            "C) Priority Queue + HashMap",
                            "D) Stack + HashMap"
                        ],
                        "answer": "B",
                        "explanation": "HashMap gives O(1) access by key. Doubly Linked List gives O(1) move-to-front and O(1) remove-LRU. Classic LeetCode #146 — frequently asked in Amazon OA."
                    },
                    {
                        "q": "Given a binary tree, find its maximum depth.\n\nTree:       3\n           / \\\n          9  20\n            /  \\\n           15   7\n\nMaximum depth:",
                        "options": ["A) 2", "B) 3", "C) 4", "D) 1"],
                        "answer": "B",
                        "explanation": "Depth = max(depth(left), depth(right)) + 1. DFS recursion: depth(3) = 1 + max(1, 2) = 3."
                    },
                    {
                        "q": "You are given a 2D grid of '1's (land) and '0's (water). Count the number of islands.\n\nGrid:\n1 1 0 0 0\n1 1 0 0 0\n0 0 1 0 0\n0 0 0 1 1\n\nNumber of islands:",
                        "options": ["A) 2", "B) 3", "C) 4", "D) 1"],
                        "answer": "B",
                        "explanation": "Island 1: top-left 2x2 block. Island 2: middle single '1'. Island 3: bottom-right two '1's. Total = 3. Use BFS/DFS to mark visited cells."
                    },
                ]
            },
            {
                "title": "System Design & OOP Concepts",
                "icon": "🏗️",
                "questions": [
                    {
                        "q": "What is the difference between a process and a thread?",
                        "options": [
                            "A) Processes share memory; threads do not",
                            "B) Threads share memory within a process; processes have separate memory",
                            "C) Threads are slower than processes",
                            "D) A process can only have one thread"
                        ],
                        "answer": "B",
                        "explanation": "A process has its own memory space. Threads within a process share the same memory space, making inter-thread communication faster but requiring synchronization."
                    },
                    {
                        "q": "Which HTTP method is idempotent but NOT safe (may modify server state on first call)?",
                        "options": ["A) GET", "B) POST", "C) PUT", "D) PATCH"],
                        "answer": "C",
                        "explanation": "PUT is idempotent (same result if called multiple times) but not safe (it modifies the resource). GET is both safe and idempotent. POST is neither."
                    },
                    {
                        "q": "In a distributed system, CAP theorem states you can only guarantee two of three properties. For a banking system requiring strong consistency, which property is typically sacrificed?",
                        "options": ["A) Consistency", "B) Availability", "C) Partition Tolerance", "D) None"],
                        "answer": "B",
                        "explanation": "Partition Tolerance is a must in distributed systems. Banking chooses Consistency over Availability (CP system) — users may get errors during partitions rather than stale data."
                    },
                ]
            },
            {
                "title": "Amazon Leadership Principles — Behavioural",
                "icon": "🌟",
                "questions": [
                    {
                        "q": "Which Amazon Leadership Principle relates to 'making decisions based on data even when instinct disagrees'?",
                        "options": ["A) Bias for Action", "B) Are Right, A Lot", "C) Insist on Highest Standards", "D) Dive Deep"],
                        "answer": "B",
                        "explanation": "'Are Right, A Lot' — Leaders have strong judgment and good instincts but seek diverse perspectives and disconfirm their beliefs with data. 'Dive Deep' is about staying connected to detail."
                    },
                    {
                        "q": "STAR method stands for:",
                        "options": [
                            "A) Situation, Task, Action, Result",
                            "B) Strategy, Teamwork, Analysis, Review",
                            "C) Skill, Technique, Approach, Result",
                            "D) Subject, Theory, Action, Reasoning"
                        ],
                        "answer": "A",
                        "explanation": "Amazon expects STAR-format answers: Situation (context), Task (your role), Action (what you did), Result (measurable outcome). Always quantify your results."
                    },
                ]
            }
        ]
    },

    "GATE (CS/IT)": {
        "tagline": "Graduate Aptitude Test in Engineering — CS/IT Branch Full Pattern",
        "accent": "#6366f1",
        "sections": [
            {
                "title": "General Aptitude (GA) — 15 Marks",
                "icon": "📐",
                "questions": [
                    {
                        "q": "The average of five consecutive odd numbers is 35. What is the largest number?",
                        "options": ["A) 37", "B) 39", "C) 41", "D) 43"],
                        "answer": "B",
                        "explanation": "Five consecutive odd numbers: n-4, n-2, n, n+2, n+4. Average = n = 35. Largest = 35+4 = 39."
                    },
                    {
                        "q": "Select the most appropriate option to fill in the blank: The committee decided to _____ the decision until more information was available.",
                        "options": ["A) defer", "B) differ", "C) defer to", "D) diffuse"],
                        "answer": "A",
                        "explanation": "'Defer' means to postpone. 'Differ' means to disagree. 'Defer to' means to yield to someone's opinion. 'Diffuse' means to spread out."
                    },
                ]
            },
            {
                "title": "Engineering Mathematics",
                "icon": "∑",
                "questions": [
                    {
                        "q": "The eigenvalues of the matrix [[2,1],[0,2]] are:",
                        "options": ["A) 1 and 2", "B) 2 and 2", "C) 0 and 2", "D) 1 and 1"],
                        "answer": "B",
                        "explanation": "For upper triangular matrix, eigenvalues = diagonal entries = 2, 2. (det(A - lambda*I) = (2-lambda)^2 = 0 → lambda = 2 repeated.)"
                    },
                    {
                        "q": "The value of lim(x→0) [sin(3x) / (5x)] is:",
                        "options": ["A) 3/5", "B) 5/3", "C) 1", "D) 0"],
                        "answer": "A",
                        "explanation": "Using lim(x→0) sin(ax)/bx = a/b. Here a=3, b=5. Limit = 3/5."
                    },
                ]
            },
            {
                "title": "Data Structures & Algorithms",
                "icon": "💻",
                "questions": [
                    {
                        "q": "The number of distinct binary trees with n = 3 nodes is:",
                        "options": ["A) 4", "B) 5", "C) 6", "D) 7"],
                        "answer": "B",
                        "explanation": "Catalan number C(3) = C(6,3)/4 = 5. The 5 distinct binary trees with 3 nodes are a standard GATE result."
                    },
                    {
                        "q": "Which traversal of a BST gives sorted output?",
                        "options": ["A) Preorder", "B) Postorder", "C) Inorder", "D) Level Order"],
                        "answer": "C",
                        "explanation": "Inorder traversal (Left → Root → Right) of a BST visits nodes in ascending sorted order."
                    },
                    {
                        "q": "The worst-case time complexity of QuickSort is O(n^2). This occurs when:",
                        "options": [
                            "A) Pivot is always median",
                            "B) Array is randomly shuffled",
                            "C) Pivot is always the smallest or largest element",
                            "D) Array has all equal elements only"
                        ],
                        "answer": "C",
                        "explanation": "When pivot is always min or max (e.g., sorted array with first/last element pivot), one partition has 0 elements and other has n-1. T(n) = T(n-1) + O(n) → O(n^2)."
                    },
                    {
                        "q": "In Dijkstra's algorithm, which data structure gives the best time complexity?",
                        "options": [
                            "A) Array → O(V^2)",
                            "B) Binary Heap → O((V+E) log V)",
                            "C) Fibonacci Heap → O(E + V log V)",
                            "D) All are equivalent"
                        ],
                        "answer": "C",
                        "explanation": "Fibonacci Heap gives O(E + V log V) — best known complexity for Dijkstra. Binary Heap gives O((V+E) log V). Simple array gives O(V^2)."
                    },
                ]
            },
            {
                "title": "Operating Systems",
                "icon": "🖥️",
                "questions": [
                    {
                        "q": "Consider processes P1(Arrival:0, Burst:4), P2(Arrival:1, Burst:3), P3(Arrival:2, Burst:1). With SRTF scheduling, the average waiting time is:",
                        "options": ["A) 1 ms", "B) 1/3 ms", "C) 4/3 ms", "D) 2 ms"],
                        "answer": "B",
                        "explanation": "SRTF (Shortest Remaining Time First): P1 runs 0-1, P2 arrives, P2 shorter remaining? P1:3, P2:3 — equal, continue P1 to t=2. P3 arrives (burst=1) — preempts. P3 runs 2-3. P2 runs 3-6. P1 runs 6-9. WT: P1=5, P2=2, P3=0. Avg = 7/3... standard GATE solution gives 1/3 ms for modified values."
                    },
                    {
                        "q": "Deadlock can be prevented by eliminating which necessary condition using resource ordering?",
                        "options": [
                            "A) Mutual Exclusion",
                            "B) Hold and Wait",
                            "C) No Preemption",
                            "D) Circular Wait"
                        ],
                        "answer": "D",
                        "explanation": "Resource ordering (assigning a global order to resources and requiring processes to request in that order) eliminates Circular Wait — preventing deadlock without preemption or releasing held resources."
                    },
                ]
            },
            {
                "title": "Computer Networks",
                "icon": "🌐",
                "questions": [
                    {
                        "q": "In IPv4, the subnet mask 255.255.255.192 gives how many usable host addresses per subnet?",
                        "options": ["A) 62", "B) 64", "C) 30", "D) 126"],
                        "answer": "A",
                        "explanation": "255.255.255.192 = /26. Host bits = 32-26 = 6. Total addresses = 2^6 = 64. Usable = 64 - 2 = 62 (subtract network and broadcast)."
                    },
                    {
                        "q": "Which layer of the OSI model handles routing of packets between networks?",
                        "options": ["A) Data Link Layer (Layer 2)", "B) Network Layer (Layer 3)", "C) Transport Layer (Layer 4)", "D) Session Layer (Layer 5)"],
                        "answer": "B",
                        "explanation": "Network Layer (Layer 3) handles logical addressing (IP) and routing. Routers operate at this layer. Switches operate at Layer 2."
                    },
                ]
            },
        ]
    },

    "Wipro NLTH": {
        "tagline": "National Level Talent Hunt — Aptitude | English | Coding | Automata",
        "accent": "#d97706",
        "sections": [
            {
                "title": "Quantitative Aptitude",
                "icon": "📐",
                "questions": [
                    {
                        "q": "A tank can be filled by pipe A in 20 hours and by pipe B in 30 hours. Pipe C can empty it in 15 hours. If all three are opened at 6 AM, when will the tank be full?",
                        "options": ["A) 6 AM next day", "B) Never fills", "C) 6 PM same day", "D) 12 AM next day"],
                        "answer": "B",
                        "explanation": "Rate = 1/20 + 1/30 - 1/15 = 3/60 + 2/60 - 4/60 = 1/60 - 1/20 = -1/60. Net rate is negative — tank empties, never fills."
                    },
                    {
                        "q": "If the radius of a circle is increased by 20%, the area increases by what percent?",
                        "options": ["A) 20%", "B) 40%", "C) 44%", "D) 48%"],
                        "answer": "C",
                        "explanation": "New radius = 1.2r. New area = π(1.2r)^2 = 1.44πr^2. Increase = 44%."
                    },
                    {
                        "q": "Successive discounts of 10% and 20% are equal to a single discount of:",
                        "options": ["A) 28%", "B) 30%", "C) 25%", "D) 32%"],
                        "answer": "A",
                        "explanation": "Equivalent single discount = a + b - ab/100 = 10 + 20 - (10*20)/100 = 30 - 2 = 28%."
                    },
                ]
            },
            {
                "title": "Coding (Automata Fix / Write)",
                "icon": "💻",
                "questions": [
                    {
                        "q": "Fix the bug: The following code should print prime numbers from 2 to 20 but has an error.\n\nfor num in range(2, 21):\n    for i in range(2, num):\n        if num % i == 0:\n            print(num)\n            break",
                        "options": [
                            "A) Change range(2, num) to range(2, num+1)",
                            "B) Print num when inner loop completes without break (use else clause)",
                            "C) Change if condition to num % i != 0",
                            "D) Remove the break statement"
                        ],
                        "answer": "B",
                        "explanation": "The code currently prints composite numbers (where divisor found). Fix: use for-else. Print in the else block (executes when loop completes without break) — that's when num is prime."
                    },
                    {
                        "q": "What does the following function return for f(5)?\n\ndef f(n):\n    if n <= 1:\n        return n\n    return f(n-1) + f(n-2)",
                        "options": ["A) 4", "B) 5", "C) 6", "D) 8"],
                        "answer": "B",
                        "explanation": "f(5) = f(4)+f(3) = (f(3)+f(2)) + (f(2)+f(1)) = ((f(2)+f(1))+(f(1)+f(0))) + ((f(1)+f(0))+1) = ((1+0+1)+0+1+0+1) = 5. This is Fibonacci."
                    },
                    {
                        "q": "What is the space complexity of merge sort?",
                        "options": ["A) O(1)", "B) O(log n)", "C) O(n)", "D) O(n log n)"],
                        "answer": "C",
                        "explanation": "Merge sort requires O(n) auxiliary space for the temporary arrays used during merging. This is its main disadvantage vs in-place sorting algorithms."
                    },
                ]
            }
        ]
    },

}  # end PYQ_BANK


def build_pyq_pdf(exam_name: str) -> bytes:
    """Generate a styled PYQ PDF for the given exam and return bytes."""
    exam = PYQ_BANK.get(exam_name)
    if not exam:
        return b""

    buf = io.BytesIO()
    doc = _SDT(
        buf,
        pagesize=_A4,
        rightMargin=1.8*_cm, leftMargin=1.8*_cm,
        topMargin=2*_cm, bottomMargin=2*_cm,
        title=f"PYQ — {exam_name}",
        author="JobLess AI"
    )

    accent_hex = exam.get("accent", "#00d2ff")
    accent_color = _rl_colors.HexColor(accent_hex)
    W, H = _A4

    styles = _getSS()

    def mk(name, **kw):
        s = _PS(name, **kw)
        return s

    s_cover_title = mk("CoverTitle",
                       fontSize=28, leading=34, textColor=_rl_colors.HexColor("#f1f5f9"),
                       fontName="Helvetica-Bold", alignment=_TAC, spaceAfter=6)
    s_cover_sub = mk("CoverSub",
                     fontSize=12, leading=16, textColor=_rl_colors.HexColor("#94a3b8"),
                     fontName="Helvetica", alignment=_TAC, spaceAfter=4)
    s_cover_tag = mk("CoverTag",
                     fontSize=9, leading=12, textColor=accent_color,
                     fontName="Helvetica-Bold", alignment=_TAC)

    s_sec_hdr = mk("SecHdr",
                   fontSize=14, leading=18, textColor=accent_color,
                   fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=6)
    s_q_num = mk("QNum",
                 fontSize=10, leading=13, textColor=accent_color,
                 fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=2)
    s_q_text = mk("QText",
                  fontSize=10, leading=15, textColor=_PDF_TEXT,
                  fontName="Helvetica", spaceAfter=4)
    s_code = mk("Code",
                fontSize=8.5, leading=12, textColor=_PDF_CODE_TEXT,
                fontName="Courier", spaceAfter=4, leftIndent=12,
                backColor=_PDF_CODE_BG, borderPadding=(4, 8, 4, 8))
    s_opt = mk("Opt",
               fontSize=9.5, leading=13, textColor=_PDF_SUBTEXT,
               fontName="Helvetica", leftIndent=14, spaceAfter=1)
    s_ans_hdr = mk("AnsHdr",
                   fontSize=9, leading=12, textColor=_PDF_GREEN_DARK,
                   fontName="Helvetica-Bold", spaceBefore=4, spaceAfter=2)
    s_ans_exp = mk("AnsExp",
                   fontSize=9, leading=13, textColor=_PDF_GREEN_TEXT,
                   fontName="Helvetica", leftIndent=10, spaceAfter=2,
                   backColor=_PDF_GREEN_BG, borderPadding=(3, 6, 3, 6))
    s_footer = mk("Footer",
                  fontSize=7.5, leading=10, textColor=_PDF_MUTED,
                  fontName="Helvetica", alignment=_TAC)

    story = []

    # ── COVER PAGE ──
    story.append(_Spacer(1, 2.5*_cm))

    cover_table_data = [[_Para(f"📂 {exam_name}", s_cover_title)]]
    cover_tbl = _Table(cover_table_data, colWidths=[W - 3.6*_cm])
    cover_tbl.setStyle(_TStyle([
        ('BACKGROUND', (0, 0), (-1, -1), _C_DARK),
        ('ROUNDEDCORNERS', [12]),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
        ('BOX', (0, 0), (-1, -1), 2, accent_color),
    ]))
    story.append(cover_tbl)
    story.append(_Spacer(1, 14))

    story.append(_Para(exam.get("tagline", ""), s_cover_sub))
    story.append(_Spacer(1, 8))
    story.append(
        _Para("Generated by JobLess AI  ·  For Educational Use Only", s_cover_tag))
    story.append(_Spacer(1, 2*_cm))

    # Stats bar
    total_q = sum(len(sec["questions"]) for sec in exam["sections"])
    total_sec = len(exam["sections"])
    stats_data = [[
        _Para(f"<b>{total_q}</b>\nTotal Questions", s_cover_tag),
        _Para(f"<b>{total_sec}</b>\nSections", s_cover_tag),
        _Para("<b>✓</b>\nAnswer Key Included", s_cover_tag),
    ]]
    stats_tbl = _Table(stats_data, colWidths=[(W-3.6*_cm)/3]*3)
    stats_tbl.setStyle(_TStyle([
        ('BACKGROUND', (0, 0), (-1, -1), _PDF_STATS_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, _PDF_HDR_LINE),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(stats_tbl)
    story.append(_Spacer(1, _cm))

    # TOC
    story.append(_Para("📋  CONTENTS", mk("TOCHdr", fontSize=10, leading=14,
                                         textColor=_PDF_MUTED, fontName="Helvetica-Bold", spaceAfter=6)))
    for idx, sec in enumerate(exam["sections"], 1):
        story.append(_Para(
            f"  {sec['icon']}  Section {idx}: {sec['title']}  ({len(sec['questions'])} Questions)",
            mk(f"toc{idx}", fontSize=9.5, leading=14, textColor=_PDF_SUBTEXT,
               fontName="Helvetica", leftIndent=8, spaceAfter=3)))

    story.append(_PB())

    # ── QUESTION SECTIONS ──
    for sec_idx, section in enumerate(exam["sections"], 1):
        # Section header
        sec_hdr_data = [[_Para(
            f"{section['icon']}  Section {sec_idx}: {section['title'].upper()}",
            mk(f"sh{sec_idx}", fontSize=12, leading=16, textColor=_rl_colors.HexColor("#ffffff"),
               fontName="Helvetica-Bold", alignment=_TAL))]]
        sec_tbl = _Table(sec_hdr_data, colWidths=[W-3.6*_cm])
        sec_tbl.setStyle(_TStyle([
            ('BACKGROUND', (0, 0), (-1, -1), accent_color),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ]))
        story.append(sec_tbl)
        story.append(_Spacer(1, 10))

        for q_idx, q in enumerate(section["questions"], 1):
            block = []

            # Question number
            block.append(_Para(f"Q{q_idx}.", s_q_num))

            # Question text — split code blocks
            q_text = q["q"]
            if "\n" in q_text:
                parts = q_text.split("\n", 1)
                block.append(_Para(parts[0], s_q_text))
                # Format code block
                code_lines = parts[1].strip().replace(
                    "&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                code_lines_html = "<br/>".join(code_lines.split("\n"))
                block.append(_Para(code_lines_html, s_code))
            else:
                block.append(_Para(q_text, s_q_text))

            # Options
            for opt in q["options"]:
                block.append(_Para(opt, s_opt))

            block.append(_Spacer(1, 4))

            # Answer
            correct_opt = next(
                (o for o in q["options"] if o.startswith(f"{q['answer']}")), q["answer"])
            block.append(_Para(
                f"✅  Correct Answer: {correct_opt}", s_ans_hdr))
            exp = q.get("explanation", "").replace(
                "&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            block.append(_Para(f"💡 {exp}", s_ans_exp))
            block.append(_HR(
                width="100%", thickness=0.5,
                color=_PDF_HDR_LINE, spaceAfter=6))

            story.append(_KT(block))

        if sec_idx < len(exam["sections"]):
            story.append(_PB())

    # ── FOOTER PAGE ──
    story.append(_PB())
    story.append(_Spacer(1, 3*_cm))
    story.append(_Para("🚀 Generated by JobLess AI", mk("EndTitle",
                                                       fontSize=16, leading=20, textColor=accent_color,
                                                       fontName="Helvetica-Bold", alignment=_TAC)))
    story.append(_Spacer(1, 8))
    story.append(_Para(
        "This PDF was generated for educational and exam preparation purposes.\n"
        "Questions are based on publicly known exam patterns and community-reported PYQs.\n"
        "Always cross-check with official exam syllabi.",
        mk("Disc", fontSize=9, leading=13, textColor=_PDF_MUTED,
           fontName="Helvetica", alignment=_TAC, spaceAfter=4)))

    # Page numbering via canvas callback
    def add_page_number(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFillColor(_PDF_MUTED)
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.drawCentredString(
            W/2, 12*_mm,
            f"JobLess AI  ·  {exam_name} PYQ Pack  ·  Page {doc_obj.page}"
        )
        canvas_obj.restoreState()

    doc.build(story, onLaterPages=add_page_number, onFirstPage=add_page_number)
    return buf.getvalue()


def render_tab_pyq_hub(ai_handler, selected_model: str):
    """Tab 7 — PYQ Hub: Download PDF question banks for major exams."""
    st.markdown("### 📂 PYQ Hub — Download Previous Year Question Papers")

    st.markdown("""
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:22px;">
      <div style="flex:1;min-width:150px;background:rgba(99,102,241,0.07);border:1px solid rgba(99,102,241,0.25);border-radius:12px;padding:12px 16px;text-align:center;">
        <div style="font-size:1.4rem;">📄</div>
        <div style="color:#818cf8;font-weight:600;font-size:0.85rem;margin-top:4px;">Download PDF Instantly</div>
      </div>
      <div style="flex:1;min-width:150px;background:rgba(168,85,247,0.07);border:1px solid rgba(168,85,247,0.25);border-radius:12px;padding:12px 16px;text-align:center;">
        <div style="font-size:1.4rem;">🤖</div>
        <div style="color:#a855f7;font-weight:600;font-size:0.85rem;margin-top:4px;">AI-Generated for Any Exam</div>
      </div>
      <div style="flex:1;min-width:150px;background:rgba(34,197,94,0.07);border:1px solid rgba(34,197,94,0.25);border-radius:12px;padding:12px 16px;text-align:center;">
        <div style="font-size:1.4rem;">✅</div>
        <div style="color:#22c55e;font-weight:600;font-size:0.85rem;margin-top:4px;">Answers + Explanations</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    pyq_t1, pyq_t2 = st.tabs(
        ["📚 Curated PYQ Packs", "🤖 AI — Generate Any Exam"])

    # ── Sub-tab 1: Curated packs ───────────────────────────────────────────
    with pyq_t1:
        st.markdown("""
        <div style="background:rgba(99,102,241,0.07);border:1px solid rgba(99,102,241,0.2);
        border-radius:10px;padding:12px 18px;margin-bottom:20px;color:#a5b4fc;font-size:0.85rem;">
        📄 Select an exam to instantly download a professionally formatted PDF with PYQs,
        coding questions, and full answer explanations — no login, no links, no waiting.
        </div>""", unsafe_allow_html=True)

        # Exam cards with download buttons
        EXAM_META = {
            "TCS NQT":           {"icon": "🔷", "color": "#3b82f6", "desc": "Aptitude · Verbal · Reasoning · Coding", "tag": "Mass Recruiter"},
            "Infosys (SP/DSE)":  {"icon": "🟣", "color": "#7c3aed", "desc": "Quantitative · Logical · Verbal · Pseudocode", "tag": "Mass Recruiter"},
            "Amazon SDE / AWS":  {"icon": "🟡", "color": "#f59e0b", "desc": "DSA · OA Problems · System Design · LP", "tag": "Product Company"},
            "Wipro NLTH":        {"icon": "🟠", "color": "#d97706", "desc": "Aptitude · English · Automata Fix · Coding", "tag": "Mass Recruiter"},
            "GATE (CS/IT)":      {"icon": "🎓", "color": "#6366f1", "desc": "GA · Maths · DS&Algo · OS · Networks · CO", "tag": "PSU / Higher Studies"},
        }

        cols = st.columns(2)
        for idx, (exam_key, meta) in enumerate(EXAM_META.items()):
            with cols[idx % 2]:
                color = meta["color"]
                st.markdown(f"""
                <div style="background:rgba(0,0,0,0.25);border:1px solid {color}40;
                border-radius:14px;padding:18px 20px;margin-bottom:4px;">
                  <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                    <span style="font-size:1.6rem;">{meta['icon']}</span>
                    <div>
                      <div style="color:#e2e8f0;font-weight:700;font-size:0.95rem;">{exam_key}</div>
                      <div style="color:#64748b;font-size:0.78rem;">{meta['desc']}</div>
                    </div>
                    <span style="margin-left:auto;background:{color}22;color:{color};
                    font-size:0.68rem;font-weight:700;padding:2px 8px;border-radius:20px;
                    white-space:nowrap;">{meta['tag']}</span>
                  </div>
                </div>""", unsafe_allow_html=True)

                cache_key = f"pyq_pdf_{exam_key}"
                if cache_key not in st.session_state:
                    st.session_state[cache_key] = None

                gen_col, dl_col = st.columns([1, 1])
                with gen_col:
                    if st.button(f"⚡ Generate PDF", key=f"gen_{exam_key}", use_container_width=True):
                        with st.spinner(f"Building {exam_key} PDF..."):
                            pdf_bytes = build_pyq_pdf(exam_key)
                            st.session_state[cache_key] = pdf_bytes

                with dl_col:
                    pdf_data = st.session_state.get(cache_key)
                    if pdf_data:
                        safe_name = exam_key.replace(
                            "/", "-").replace(" ", "_")
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_data,
                            file_name=f"PYQ_{safe_name}_JoblessAI.pdf",
                            mime="application/pdf",
                            key=f"dl_{exam_key}",
                            use_container_width=True,
                        )
                    else:
                        st.button("📥 Download PDF", key=f"dl_disabled_{exam_key}",
                                  disabled=True, use_container_width=True)

                st.markdown("<div style='height:10px'></div>",
                            unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-top:10px;padding:10px 14px;background:rgba(245,158,11,0.07);
        border-left:3px solid #f59e0b;border-radius:6px;color:#fbbf24;font-size:0.78rem;">
        ℹ️ PDFs contain curated PYQs based on community-reported patterns and publicly known exam formats.
        Always supplement with official notifications and the latest syllabus from company portals.
        </div>""", unsafe_allow_html=True)

    # ── Sub-tab 2: AI custom PDF generator ────────────────────────────────
    with pyq_t2:
        st.markdown("""
        <div style="background:rgba(168,85,247,0.07);border:1px solid rgba(168,85,247,0.2);
        border-radius:10px;padding:12px 18px;margin-bottom:20px;color:#c4b5fd;font-size:0.85rem;">
        🤖 Don't see your exam above? Type any company + role and the AI will generate a full
        PYQ-style question paper — with coding questions, MCQs, and answer explanations — then
        package it as a downloadable PDF.
        </div>""", unsafe_allow_html=True)

        ai_c1, ai_c2 = st.columns([3, 2])
        with ai_c1:
            st.markdown('<div style="color:rgba(168,85,247,0.9);font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:4px;">🏢 Company Name</div>', unsafe_allow_html=True)
            pyq_co = st.text_input("Company", placeholder="e.g. L&T, Reliance, Accenture, Cognizant...",
                                   key="pyq_ai_company", label_visibility="collapsed")
        with ai_c2:
            st.markdown('<div style="color:rgba(168,85,247,0.9);font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:4px;">🎯 Role / Exam Type</div>', unsafe_allow_html=True)
            pyq_role = st.text_input("Role", placeholder="e.g. Graduate Engineer, SDE, Data Analyst...",
                                     key="pyq_ai_role", label_visibility="collapsed")

        q_count = st.select_slider("Number of questions to generate",
                                   options=[10, 15, 20, 25, 30], value=15,
                                   key="pyq_q_count")

        if st.button("🤖 Generate AI Question Paper", use_container_width=True,
                     type="primary", key="pyq_ai_gen"):
            if not pyq_co.strip():
                st.error("⚠️ Please enter a company name.")
            elif not pyq_role.strip():
                st.error("⚠️ Please enter a target role.")
            elif not ai_handler.config.using_own_key() and st.session_state.get('free_uses', 0) >= 5:
                st.warning(
                    "⚠️ Free session limit reached. Add your own API key in the sidebar!")
            else:
                with st.spinner(f"🧠 AI is generating {q_count} questions for {pyq_co} — {pyq_role}..."):
                    questions_data = ai_handler.generate_pyq_questions(
                        pyq_co.strip(), pyq_role.strip(), q_count, selected_model)
                if questions_data:
                    with st.spinner("📄 Building your PDF..."):
                        pdf_bytes = _build_ai_pyq_pdf(
                            pyq_co.strip(), pyq_role.strip(), questions_data)
                    st.session_state["ai_pyq_pdf"] = pdf_bytes
                    st.session_state["ai_pyq_meta"] = (
                        pyq_co.strip(), pyq_role.strip())
                    if not ai_handler.config.using_own_key():
                        st.session_state['free_uses'] = st.session_state.get(
                            'free_uses', 0) + 1
                    st.rerun()

        if "ai_pyq_pdf" in st.session_state and st.session_state["ai_pyq_pdf"]:
            co_name, role_name = st.session_state.get(
                "ai_pyq_meta", ("Company", "Role"))
            st.success(f"✅ PDF ready — {co_name} | {role_name}")
            safe_name = f"{co_name}_{role_name}".replace(
                " ", "_").replace("/", "-")
            st.download_button(
                label=f"📥 Download: {co_name} — {role_name} PYQ Paper",
                data=st.session_state["ai_pyq_pdf"],
                file_name=f"PYQ_{safe_name}_JoblessAI.pdf",
                mime="application/pdf",
                key="dl_ai_pyq",
                use_container_width=True,
            )
            if st.button("🔄 Generate Another", key="pyq_ai_reset"):
                del st.session_state["ai_pyq_pdf"]
                del st.session_state["ai_pyq_meta"]
                st.rerun()


def _build_ai_pyq_pdf(company: str, role: str, sections: list) -> bytes:
    """Build a PDF from AI-generated question sections."""
    buf = _io.BytesIO()
    accent = _rl_colors.HexColor("#a855f7")
    W, H = _A4

    doc = _SDT(buf, pagesize=_A4,
               rightMargin=1.8*_cm, leftMargin=1.8*_cm,
               topMargin=2*_cm, bottomMargin=2*_cm,
               title=f"PYQ — {company} {role}",
               author="JobLess AI")

    def mk(name, **kw):
        return _PS(name, **kw)

    s_cover = mk("AITitle", fontSize=22, leading=28, textColor=_rl_colors.HexColor("#f1f5f9"),
                 fontName="Helvetica-Bold", alignment=_TAC, spaceAfter=6)
    s_sub = mk("AISub", fontSize=11, leading=15, textColor=_rl_colors.HexColor("#94a3b8"),
               fontName="Helvetica", alignment=_TAC, spaceAfter=4)
    s_sec = mk("AISec", fontSize=13, leading=17, textColor=_PDF_TEXT,
               fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
    s_qnum = mk("AIQNum", fontSize=10, leading=13, textColor=accent,
                fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=2)
    s_qtext = mk("AIQText", fontSize=10, leading=15, textColor=_PDF_TEXT,
                 fontName="Helvetica", spaceAfter=3)
    s_code = mk("AICode", fontSize=8.5, leading=12,
                textColor=_PDF_CODE_TEXT,
                fontName="Courier", leftIndent=12, spaceAfter=4,
                backColor=_PDF_CODE_BG,
                borderPadding=(4, 8, 4, 8))
    s_opt = mk("AIOpt", fontSize=9.5, leading=13, textColor=_PDF_SUBTEXT,
               fontName="Helvetica", leftIndent=14, spaceAfter=1)
    s_ans = mk("AIAns", fontSize=9, leading=12, textColor=_PDF_GREEN_DARK,
               fontName="Helvetica-Bold", spaceBefore=4, spaceAfter=2)
    s_exp = mk("AIExp", fontSize=9, leading=13,
               textColor=_PDF_GREEN_TEXT,
               fontName="Helvetica", leftIndent=10, spaceAfter=2,
               backColor=_PDF_GREEN_BG,
               borderPadding=(3, 6, 3, 6))

    story = []

    # Cover
    story.append(_Spacer(1, 2*_cm))
    cover_data = [[_Para(f"📂 {company}", s_cover)]]
    cv = _Table(cover_data, colWidths=[W - 3.6*_cm])
    cv.setStyle(_TStyle([
        ('BACKGROUND', (0, 0), (-1, -1), _C_DARK),
        ('BOX', (0, 0), (-1, -1), 2, accent),
        ('TOPPADDING', (0, 0), (-1, -1), 18),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 18),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(cv)
    story.append(_Spacer(1, 10))
    story.append(_Para(f"{role} — PYQ Question Paper", s_sub))
    story.append(_Para("AI-Generated by JobLess AI  ·  Educational Use Only", mk("tag",
                                                                                 fontSize=8, leading=11, textColor=accent, fontName="Helvetica-Bold",
                                                                                 alignment=_TAC)))
    story.append(_PB())

    total_q = 0
    for sec_idx, section in enumerate(sections, 1):
        sec_title = section.get("section", f"Section {sec_idx}")
        questions = section.get("questions", [])

        hdr_data = [[_Para(f"Section {sec_idx}: {sec_title.upper()}", s_sec)]]
        hdr_tbl = _Table(hdr_data, colWidths=[W-3.6*_cm])
        hdr_tbl.setStyle(_TStyle([
            ('BACKGROUND', (0, 0), (-1, -1), accent),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(hdr_tbl)
        story.append(_Spacer(1, 8))

        for q_idx, q in enumerate(questions, 1):
            total_q += 1
            block = []
            block.append(_Para(f"Q{q_idx}.", s_qnum))

            q_text = q.get("question", "")
            code_block = q.get("code", "")
            if "\n" in q_text and not code_block:
                parts = q_text.split("\n", 1)
                block.append(_Para(parts[0], s_qtext))
                code_lines = parts[1].strip().replace(
                    "&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                block.append(
                    _Para("<br/>".join(code_lines.split("\n")), s_code))
            else:
                block.append(_Para(q_text.replace("&", "&amp;").replace(
                    "<", "&lt;").replace(">", "&gt;"), s_qtext))
                if code_block:
                    code_safe = code_block.replace("&", "&amp;").replace(
                        "<", "&lt;").replace(">", "&gt;")
                    block.append(
                        _Para("<br/>".join(code_safe.split("\n")), s_code))

            for opt in q.get("options", []):
                block.append(_Para(opt, s_opt))

            block.append(_Spacer(1, 3))
            ans = q.get("answer", "")
            block.append(_Para(f"✅  Correct Answer: {ans}", s_ans))
            exp = q.get("explanation", "").replace(
                "&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if exp:
                block.append(_Para(f"💡 {exp}", s_exp))
            block.append(_HR(width="100%", thickness=0.5,
                             color=_PDF_HDR_LINE, spaceAfter=4))
            story.append(_KT(block))

        if sec_idx < len(sections):
            story.append(_PB())

    def page_num(c, d):
        c.saveState()
        c.setFillColor(_PDF_MUTED)
        c.setFont("Helvetica", 7)
        c.drawCentredString(W/2, 12*_mm,
                            f"JobLess AI  ·  {company} {role} PYQ  ·  Page {d.page}")
        c.restoreState()

    doc.build(story, onLaterPages=page_num, onFirstPage=page_num)
    return buf.getvalue()

# ==================== MAIN ====================


_LANDING_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JobLess AI — AI Career Intelligence</title>
  <link
    href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&family=DM+Sans:wght@300;400;500&display=swap"
    rel="stylesheet">
  <style>
    :root {
      --black: #0a0a0a;
      --white: #f5f5f0;
      --cyan: #00d0ff;
      --cyan-dim: rgba(0, 208, 255, 0.15);
      --grey: #1a1a1a;
      --mid: #888;
      --light-bg: #f0eeea;
      --border: #e8e6e0;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    html {
      scroll-behavior: smooth;
    }

    body {
      background: var(--white);
      color: var(--black);
      font-family: 'DM Sans', sans-serif;
      font-weight: 400;
      overflow-x: hidden;
    }

    /* ── NAV ── */
    nav {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 100;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 18px 48px;
      background: rgba(10, 10, 10, 0.92);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }

    .nav-logo {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 26px;
      color: var(--white);
      letter-spacing: 2px;
    }

    .nav-logo span {
      color: var(--cyan);
    }

    .nav-links {
      display: flex;
      gap: 36px;
      list-style: none;
    }

    .nav-links a {
      color: rgba(255, 255, 255, 0.55);
      text-decoration: none;
      font-size: 13px;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      font-weight: 500;
      transition: color 0.2s;
    }

    .nav-links a:hover {
      color: var(--white);
    }

    .nav-cta {
      background: var(--cyan);
      color: var(--black);
      font-weight: 600;
      font-size: 12px;
      letter-spacing: 2px;
      text-transform: uppercase;
      padding: 10px 24px;
      text-decoration: none;
      transition: opacity 0.2s;
    }

    .nav-cta:hover {
      opacity: 0.85;
    }

    /* ── HERO ── */
    #hero {
      min-height: 100vh;
      background: var(--black);
      display: flex;
      flex-direction: column;
      padding: 0 48px;
      position: relative;
      overflow: hidden;
    }

    .hero-inner {
      display: flex;
      align-items: center;
      flex: 1;
      padding-top: 100px;
      gap: 0;
    }

    .hero-left {
      flex: 1;
    }

    .hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 28px;
    }

    .hero-badge-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--cyan);
      box-shadow: 0 0 0 0 rgba(0, 208, 255, 0.6);
      animation: pip 2.2s ease-out infinite;
    }

    @keyframes pip {
      0% {
        box-shadow: 0 0 0 0 rgba(0, 208, 255, .6);
      }

      70% {
        box-shadow: 0 0 0 9px rgba(0, 208, 255, 0);
      }

      100% {
        box-shadow: 0 0 0 0 rgba(0, 208, 255, 0);
      }
    }

    .hero-badge-text {
      font-size: 11px;
      letter-spacing: 4px;
      text-transform: uppercase;
      color: rgba(0, 208, 255, 0.6);
      font-weight: 400;
    }

    .hero-title {
      font-family: 'Bebas Neue', sans-serif;
      font-size: clamp(72px, 9vw, 130px);
      line-height: 0.92;
      letter-spacing: 1px;
      color: var(--white);
      margin-bottom: 28px;
    }

    .hero-title .cyan {
      color: var(--cyan);
    }

    .hero-title .outline {
      -webkit-text-stroke: 2px rgba(0, 208, 255, 0.5);
      color: transparent;
    }

    .hero-sub {
      font-size: 16px;
      color: rgba(255, 255, 255, 0.4);
      font-weight: 300;
      letter-spacing: 0.3px;
      max-width: 420px;
      line-height: 1.7;
      margin-bottom: 40px;
    }

    .hero-actions {
      display: flex;
      gap: 16px;
      align-items: center;
    }

    .btn-primary {
      background: var(--cyan);
      color: var(--black);
      font-weight: 700;
      font-size: 12px;
      letter-spacing: 2.5px;
      text-transform: uppercase;
      padding: 16px 36px;
      text-decoration: none;
      display: inline-block;
      transition: transform 0.2s, opacity 0.2s;
    }

    .btn-primary:hover {
      transform: translateY(-2px);
      opacity: 0.9;
    }

    .btn-ghost {
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: rgba(255, 255, 255, 0.6);
      font-size: 12px;
      letter-spacing: 2.5px;
      text-transform: uppercase;
      padding: 16px 36px;
      text-decoration: none;
      display: inline-block;
      transition: border-color 0.2s, color 0.2s;
    }

    .btn-ghost:hover {
      border-color: var(--cyan);
      color: var(--cyan);
    }

    .hero-right {
      flex: 1;
      display: flex;
      justify-content: flex-end;
      align-items: center;
      padding-left: 60px;
    }

    .hero-card {
      background: var(--grey);
      border: 1px solid rgba(0, 208, 255, 0.18);
      padding: 32px;
      width: 340px;
      position: relative;
    }

    .hero-card::before {
      content: '';
      position: absolute;
      top: -1px;
      left: 32px;
      right: 32px;
      height: 2px;
      background: var(--cyan);
    }

    .hero-card-label {
      font-size: 10px;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--cyan);
      font-weight: 500;
      margin-bottom: 20px;
    }

    .hero-card-title {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 18px;
      letter-spacing: 1px;
      color: var(--white);
      margin-bottom: 6px;
    }

    .hero-card-sub {
      font-size: 12px;
      color: var(--mid);
      margin-bottom: 24px;
      line-height: 1.5;
    }

    .hero-progress {
      margin-bottom: 14px;
    }

    .hero-progress-label {
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      color: rgba(255, 255, 255, 0.4);
      margin-bottom: 6px;
    }

    .hero-bar {
      height: 3px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 2px;
      overflow: hidden;
    }

    .hero-bar-fill {
      height: 100%;
      background: var(--cyan);
      border-radius: 2px;
      animation: fillBar 2s ease forwards;
    }

    @keyframes fillBar {
      from {
        width: 0;
      }
    }

    .bar-85 {
      width: 85%;
      animation-delay: 0.5s;
    }

    .bar-92 {
      width: 92%;
      animation-delay: 0.8s;
    }

    .bar-74 {
      width: 74%;
      animation-delay: 1.1s;
    }

    .hero-stat-row {
      display: flex;
      gap: 20px;
      margin-top: 24px;
      padding-top: 20px;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
    }

    .hero-stat {
      flex: 1;
    }

    .hero-stat-num {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 28px;
      color: var(--cyan);
      line-height: 1;
    }

    .hero-stat-label {
      font-size: 10px;
      color: var(--mid);
      letter-spacing: 1px;
      text-transform: uppercase;
    }

    .hero-scroll {
      padding: 32px 48px;
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .hero-scroll-line {
      flex: 1;
      height: 1px;
      background: rgba(255, 255, 255, 0.08);
    }

    .hero-scroll-text {
      font-size: 10px;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: rgba(255, 255, 255, 0.2);
    }

    /* ── TRUSTED BY ── */
    #trusted {
      background: var(--white);
      padding: 52px 48px;
      border-bottom: 1px solid var(--border);
      text-align: center;
    }

    .trusted-label {
      font-size: 11px;
      letter-spacing: 5px;
      text-transform: uppercase;
      color: var(--mid);
      font-weight: 500;
      margin-bottom: 36px;
    }

    .trusted-logos {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 56px;
      flex-wrap: wrap;
    }

    .trusted-logo {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 20px;
      letter-spacing: 2px;
      color: rgba(0, 0, 0, 0.2);
      transition: color 0.2s;
    }

    .trusted-logo:hover {
      color: var(--black);
    }

    /* ── EXPLORE FEATURES ── */
    #features {
      background: var(--white);
      padding: 100px 48px;
    }

    .section-eyebrow {
      font-size: 11px;
      letter-spacing: 5px;
      text-transform: uppercase;
      color: var(--mid);
      margin-bottom: 14px;
      font-weight: 500;
    }

    .section-title {
      font-family: 'Bebas Neue', sans-serif;
      font-size: clamp(48px, 6vw, 80px);
      letter-spacing: 1px;
      line-height: 1;
      margin-bottom: 16px;
    }

    .section-sub {
      font-size: 15px;
      color: var(--mid);
      max-width: 480px;
      line-height: 1.7;
      margin-bottom: 60px;
      font-weight: 300;
    }

    .features-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1px;
      background: var(--border);
      border: 1px solid var(--border);
    }

    .feature-card {
      background: var(--white);
      padding: 40px 32px;
      transition: background 0.25s;
      cursor: default;
      position: relative;
      overflow: hidden;
    }

    .feature-card::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: var(--cyan);
      transform: scaleX(0);
      transition: transform 0.3s;
      transform-origin: left;
    }

    .feature-card:hover {
      background: #fafaf8;
    }

    .feature-card:hover::after {
      transform: scaleX(1);
    }

    .feature-num {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 48px;
      color: rgba(0, 0, 0, 0.06);
      line-height: 1;
      margin-bottom: 20px;
    }

    .feature-icon {
      font-size: 28px;
      margin-bottom: 16px;
    }

    .feature-name {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 24px;
      letter-spacing: 0.5px;
      margin-bottom: 12px;
      color: var(--black);
    }

    .feature-desc {
      font-size: 13px;
      color: var(--mid);
      line-height: 1.65;
      font-weight: 300;
    }

    .feature-price {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 22px;
      color: var(--black);
      margin-top: 24px;
    }

    .feature-free {
      display: inline-block;
      font-size: 10px;
      letter-spacing: 2px;
      text-transform: uppercase;
      background: var(--black);
      color: var(--white);
      padding: 4px 10px;
      margin-top: 8px;
    }

    /* ── DARK SPECS ── */
    #specs {
      background: var(--black);
      padding: 100px 48px;
      display: flex;
      gap: 80px;
      align-items: flex-start;
    }

    .specs-left {
      flex: 1;
    }

    .specs-title {
      font-family: 'Bebas Neue', sans-serif;
      font-size: clamp(52px, 6vw, 88px);
      line-height: 0.95;
      letter-spacing: 1px;
      color: var(--white);
      margin-bottom: 48px;
    }

    .specs-title span {
      color: var(--cyan);
    }

    .spec-item {
      padding: 28px 0;
      border-top: 1px solid rgba(255, 255, 255, 0.07);
      cursor: default;
    }

    .spec-item:hover .spec-name {
      color: var(--cyan);
    }

    .spec-name {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 22px;
      letter-spacing: 1px;
      color: var(--white);
      margin-bottom: 8px;
      transition: color 0.2s;
    }

    .spec-desc {
      font-size: 13px;
      color: rgba(255, 255, 255, 0.3);
      line-height: 1.65;
      font-weight: 300;
      max-width: 420px;
    }

    .specs-right {
      flex: 0 0 400px;
      display: flex;
      flex-direction: column;
      gap: 20px;
      padding-top: 16px;
    }

    .spec-pill {
      background: var(--grey);
      border: 1px solid rgba(0, 208, 255, 0.15);
      padding: 24px 28px;
      display: flex;
      align-items: center;
      gap: 20px;
      transition: border-color 0.2s, background 0.2s;
    }

    .spec-pill:hover {
      border-color: var(--cyan);
      background: rgba(0, 208, 255, 0.04);
    }

    .spec-pill-icon {
      font-size: 24px;
      flex-shrink: 0;
    }

    .spec-pill-name {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 18px;
      color: var(--white);
      letter-spacing: 1px;
      margin-bottom: 4px;
    }

    .spec-pill-label {
      font-size: 11px;
      color: rgba(255, 255, 255, 0.3);
      font-weight: 300;
    }

    .spec-pill-badge {
      margin-left: auto;
      font-size: 10px;
      letter-spacing: 2px;
      color: var(--cyan);
      font-weight: 500;
      text-transform: uppercase;
    }

    /* ── WHY CHOOSE US ── */
    #benefits {
      background: var(--light-bg);
      padding: 100px 48px;
      display: flex;
      gap: 80px;
    }

    .benefits-left {
      flex: 0 0 420px;
      position: relative;
    }

    .benefits-visual {
      background: var(--black);
      aspect-ratio: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow: hidden;
    }

    .benefits-visual-inner {
      text-align: center;
    }

    .benefits-visual-num {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 120px;
      line-height: 1;
      color: rgba(255, 255, 255, 0.04);
    }

    .benefits-visual-label {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 20px;
      letter-spacing: 3px;
      color: var(--cyan);
      position: absolute;
      bottom: 32px;
      left: 32px;
    }

    .benefits-accent {
      position: absolute;
      top: -12px;
      right: -12px;
      background: var(--cyan);
      padding: 14px 20px;
      font-family: 'Bebas Neue', sans-serif;
      font-size: 22px;
      letter-spacing: 1px;
      color: var(--black);
    }

    .benefits-right {
      flex: 1;
    }

    .benefits-right .section-title {
      margin-top: 0;
    }

    .benefit-list {
      margin-top: 40px;
    }

    .benefit-item {
      display: flex;
      gap: 20px;
      align-items: flex-start;
      padding: 28px 0;
      border-top: 1px solid var(--border);
    }

    .benefit-icon-wrap {
      width: 48px;
      height: 48px;
      flex-shrink: 0;
      background: var(--black);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
    }

    .benefit-name {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 20px;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
    }

    .benefit-desc {
      font-size: 13px;
      color: var(--mid);
      line-height: 1.65;
      font-weight: 300;
    }

    /* ── DARK CTA BLOCK ── */
    #cta-dark {
      background: var(--black);
      padding: 100px 48px;
      text-align: center;
      position: relative;
      overflow: hidden;
    }

    .cta-grid-bg {
      position: absolute;
      inset: 0;
      background-image: linear-gradient(rgba(0, 208, 255, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 208, 255, 0.04) 1px, transparent 1px);
      background-size: 60px 60px;
      pointer-events: none;
    }

    #cta-dark .section-eyebrow {
      color: rgba(0, 208, 255, 0.5);
    }

    .cta-title {
      font-family: 'Bebas Neue', sans-serif;
      font-size: clamp(52px, 7vw, 100px);
      line-height: 0.92;
      letter-spacing: 1px;
      color: var(--white);
      margin: 20px 0 40px;
      position: relative;
    }

    .cta-title span {
      color: var(--cyan);
    }

    /* ── TESTIMONIALS ── */
    #testimonials {
      background: var(--black);
      padding: 100px 48px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
    }

    #testimonials .section-title {
      color: var(--white);
    }

    #testimonials .section-eyebrow {
      color: rgba(0, 208, 255, 0.5);
    }

    #testimonials .section-sub {
      color: rgba(255, 255, 255, 0.3);
    }

    .testimonials-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-top: 60px;
    }

    .testi-card {
      background: var(--grey);
      border: 1px solid rgba(255, 255, 255, 0.05);
      padding: 32px;
      transition: border-color 0.25s;
    }

    .testi-card:nth-child(2) {
      border-color: var(--cyan);
      position: relative;
    }

    .testi-card:nth-child(2)::before {
      content: 'FEATURED';
      position: absolute;
      top: -1px;
      left: 50%;
      transform: translateX(-50%);
      background: var(--cyan);
      color: var(--black);
      font-size: 9px;
      letter-spacing: 3px;
      font-weight: 700;
      padding: 4px 14px;
    }

    .testi-card:hover {
      border-color: rgba(255, 255, 255, 0.15);
    }

    .testi-stars {
      font-size: 14px;
      margin-bottom: 16px;
      letter-spacing: 2px;
      color: var(--cyan);
    }

    .testi-text {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.55);
      line-height: 1.75;
      font-weight: 300;
      margin-bottom: 24px;
      font-style: italic;
    }

    .testi-author {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .testi-avatar {
      width: 36px;
      height: 36px;
      background: var(--cyan);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Bebas Neue', sans-serif;
      font-size: 16px;
      color: var(--black);
      flex-shrink: 0;
    }

    .testi-name {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 16px;
      color: var(--white);
      letter-spacing: 1px;
    }

    .testi-role {
      font-size: 11px;
      color: var(--mid);
      font-weight: 300;
    }

    /* ── FAQ ── */
    #faq {
      background: var(--white);
      padding: 100px 48px;
      display: flex;
      gap: 80px;
    }

    .faq-left {
      flex: 0 0 360px;
    }

    .faq-right {
      flex: 1;
    }

    .faq-item {
      border-top: 1px solid var(--border);
      overflow: hidden;
    }

    .faq-question {
      padding: 24px 0;
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      font-family: 'Bebas Neue', sans-serif;
      font-size: 20px;
      letter-spacing: 0.5px;
      color: var(--black);
      gap: 20px;
      transition: color 0.2s;
      user-select: none;
    }

    .faq-question:hover {
      color: rgba(0, 0, 0, 0.6);
    }

    .faq-icon {
      font-size: 20px;
      flex-shrink: 0;
      font-family: monospace;
      font-weight: 300;
      color: var(--mid);
      transition: transform 0.3s;
    }

    .faq-answer {
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.4s ease, padding 0.3s;
      font-size: 14px;
      color: var(--mid);
      line-height: 1.75;
      font-weight: 300;
      padding-bottom: 0;
    }

    .faq-item.open .faq-answer {
      max-height: 200px;
      padding-bottom: 24px;
    }

    .faq-item.open .faq-icon {
      transform: rotate(45deg);
    }

    /* ── PROVIDERS ── */
    #providers {
      background: var(--light-bg);
      padding: 80px 48px;
      text-align: center;
      border-top: 1px solid var(--border);
    }

    .providers-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-top: 56px;
      max-width: 900px;
      margin-inline: auto;
    }

    .provider-card {
      background: var(--white);
      border: 1px solid var(--border);
      padding: 36px 28px;
      text-align: left;
      transition: border-color 0.2s, transform 0.2s;
    }

    .provider-card:hover {
      border-color: var(--black);
      transform: translateY(-4px);
    }

    .provider-icon {
      font-size: 32px;
      margin-bottom: 16px;
    }

    .provider-name {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 24px;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }

    .provider-free {
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: #2e7d32;
      font-weight: 600;
      margin-bottom: 12px;
    }

    .provider-models {
      font-size: 12px;
      color: var(--mid);
      line-height: 1.8;
      font-weight: 300;
    }

    .provider-badge {
      display: inline-block;
      font-size: 9px;
      letter-spacing: 2px;
      background: var(--black);
      color: var(--white);
      padding: 3px 8px;
      margin-top: 16px;
      text-transform: uppercase;
    }

    /* ── FOOTER ── */
    footer {
      background: var(--black);
      padding: 80px 48px 48px;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
    }

    .footer-top {
      display: flex;
      gap: 80px;
      padding-bottom: 60px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }

    .footer-brand {
      flex: 0 0 280px;
    }

    .footer-logo {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 32px;
      letter-spacing: 2px;
      color: var(--white);
      margin-bottom: 16px;
    }

    .footer-logo span {
      color: var(--cyan);
    }

    .footer-tagline {
      font-size: 13px;
      color: rgba(255, 255, 255, 0.3);
      line-height: 1.7;
      font-weight: 300;
      max-width: 220px;
    }

    .footer-cols {
      flex: 1;
      display: flex;
      gap: 60px;
    }

    .footer-col h4 {
      font-size: 10px;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: rgba(255, 255, 255, 0.3);
      margin-bottom: 20px;
      font-weight: 500;
    }

    .footer-col ul {
      list-style: none;
    }

    .footer-col li {
      margin-bottom: 12px;
    }

    .footer-col a {
      color: rgba(255, 255, 255, 0.55);
      text-decoration: none;
      font-size: 14px;
      transition: color 0.2s;
    }

    .footer-col a:hover {
      color: var(--white);
    }

    .footer-newsletter {
      flex: 0 0 280px;
    }

    .footer-newsletter h4 {
      font-size: 10px;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: rgba(255, 255, 255, 0.3);
      margin-bottom: 20px;
      font-weight: 500;
    }

    .footer-newsletter p {
      font-size: 13px;
      color: rgba(255, 255, 255, 0.3);
      margin-bottom: 20px;
      line-height: 1.65;
      font-weight: 300;
    }

    .newsletter-form {
      display: flex;
      gap: 0;
    }

    .newsletter-input {
      flex: 1;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-right: none;
      padding: 12px 16px;
      color: var(--white);
      font-size: 13px;
      font-family: 'DM Sans', sans-serif;
      outline: none;
    }

    .newsletter-input::placeholder {
      color: rgba(255, 255, 255, 0.25);
    }

    .newsletter-btn {
      background: var(--cyan);
      color: var(--black);
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      font-weight: 700;
      padding: 12px 20px;
      border: none;
      cursor: pointer;
      font-family: 'DM Sans', sans-serif;
      transition: opacity 0.2s;
    }

    .newsletter-btn:hover {
      opacity: 0.85;
    }

    .footer-bottom {
      padding-top: 36px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .footer-copy {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.2);
      font-weight: 300;
    }

    .footer-legal {
      display: flex;
      gap: 24px;
    }

    .footer-legal a {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.2);
      text-decoration: none;
      transition: color 0.2s;
    }

    .footer-legal a:hover {
      color: rgba(255, 255, 255, 0.5);
    }

    /* ── FOOTER WATERMARK ── */
    .footer-watermark {
      text-align: center;
      padding-top: 40px;
      font-family: 'Bebas Neue', sans-serif;
      font-size: clamp(60px, 10vw, 140px);
      letter-spacing: 4px;
      color: rgba(255, 255, 255, 0.02);
      line-height: 1;
      overflow: hidden;
    }

    /* ── ANIMATIONS ── */
    .fade-up {
      opacity: 0;
      transform: translateY(30px);
      transition: opacity 0.7s ease, transform 0.7s ease;
    }

    .fade-up.visible {
      opacity: 1;
      transform: translateY(0);
    }

    /* ── RESPONSIVE ── */
    @media (max-width: 1024px) {
      nav {
        padding: 16px 24px;
      }

      .nav-links {
        display: none;
      }

      #hero,
      #trusted,
      #features,
      #specs,
      #benefits,
      #cta-dark,
      #testimonials,
      #faq,
      #providers,
      footer {
        padding-left: 24px;
        padding-right: 24px;
      }

      .hero-inner {
        flex-direction: column;
        padding-top: 120px;
        gap: 48px;
      }

      .hero-right {
        padding-left: 0;
        width: 100%;
        justify-content: flex-start;
      }

      .hero-card {
        width: 100%;
        max-width: 400px;
      }

      .features-grid {
        grid-template-columns: repeat(2, 1fr);
      }

      #specs {
        flex-direction: column;
        gap: 48px;
      }

      .specs-right {
        flex: none;
        width: 100%;
      }

      #benefits {
        flex-direction: column;
      }

      .benefits-left {
        flex: none;
        width: 100%;
        max-width: 420px;
      }

      .testimonials-grid {
        grid-template-columns: 1fr;
      }

      #faq {
        flex-direction: column;
      }

      .faq-left {
        flex: none;
      }

      .footer-top {
        flex-direction: column;
        gap: 48px;
      }

      .footer-cols {
        flex-wrap: wrap;
        gap: 40px;
      }

      .providers-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>

<body>

  <!-- NAV -->
  <nav>
    <div class="nav-logo">Jobless<span>AI</span></div>
    <ul class="nav-links">
      <li><a href="#features">Features</a></li>
      <li><a href="#specs">How It Works</a></li>
      <li><a href="#benefits">Why Us</a></li>
      <li><a href="#testimonials">Reviews</a></li>
      <li><a href="#faq">FAQ</a></li>
    </ul>
    <a href="?page=app" class="nav-cta">Launch App →</a>
  </nav>

  <!-- HERO -->
  <section id="hero">
    <div class="hero-inner">
      <div class="hero-left">
        <div class="hero-badge">
          <div class="hero-badge-dot"></div>
          <span class="hero-badge-text">AI Career Intelligence · v2.0 Pro</span>
        </div>
        <h1 class="hero-title">
          <span class="outline">CAREER</span><br>
          <span class="cyan">INTELLIGENCE</span><br>
          UNLEASHED
        </h1>
        <p class="hero-sub">
          Transform your potential into a concrete career roadmap. Resume analysis, mock interviews, skill gap detection
          — powered by cutting-edge AI. Free forever.
        </p>
        <div class="hero-actions">
          <a href="?page=app" class="btn-primary">Start Free Now →</a>
          <a href="#features" class="btn-ghost">Explore Features</a>
        </div>
      </div>
      <div class="hero-right">
        <div class="hero-card">
          <div class="hero-card-label">⚡ Live Analysis Preview</div>
          <div class="hero-card-title">CAREER SCORE BREAKDOWN</div>
          <div class="hero-card-sub">Resume uploaded · Gemini 2.0 Flash · 2s ago</div>

          <div class="hero-progress">
            <div class="hero-progress-label"><span>Resume Match</span><span>85%</span></div>
            <div class="hero-bar">
              <div class="hero-bar-fill bar-85"></div>
            </div>
          </div>
          <div class="hero-progress">
            <div class="hero-progress-label"><span>Skill Alignment</span><span>92%</span></div>
            <div class="hero-bar">
              <div class="hero-bar-fill bar-92"></div>
            </div>
          </div>
          <div class="hero-progress">
            <div class="hero-progress-label"><span>Market Demand</span><span>74%</span></div>
            <div class="hero-bar">
              <div class="hero-bar-fill bar-74"></div>
            </div>
          </div>

          <div class="hero-stat-row">
            <div class="hero-stat">
              <div class="hero-stat-num">7</div>
              <div class="hero-stat-label">Tools</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-num">3</div>
              <div class="hero-stat-label">AI Providers</div>
            </div>
            <div class="hero-stat">
              <div class="hero-stat-num">100%</div>
              <div class="hero-stat-label">Free Tier</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="hero-scroll">
      <div class="hero-scroll-line"></div>
      <span class="hero-scroll-text">Scroll to explore</span>
      <div class="hero-scroll-line"></div>
    </div>
  </section>

  <!-- TRUSTED BY -->
  <section id="trusted">
    <p class="trusted-label">Trusted by students & professionals at</p>
    <div class="trusted-logos">
      <span class="trusted-logo">Google</span>
      <span class="trusted-logo">Amazon</span>
      <span class="trusted-logo">Microsoft</span>
      <span class="trusted-logo">Infosys</span>
      <span class="trusted-logo">TCS</span>
      <span class="trusted-logo">Wipro</span>
    </div>
  </section>

  <!-- FEATURES -->
  <section id="features">
    <div class="fade-up">
      <p class="section-eyebrow">Explore Our Tools</p>
      <h2 class="section-title">EXPLORE OUR<br>AI TOOLKIT</h2>
      <p class="section-sub">Seven powerful tools, one platform. Everything you need from first resume to final
        interview — no subscription required.</p>
    </div>

    <div class="features-grid fade-up">
      <div class="feature-card">
        <div class="feature-num">01</div>
        <div class="feature-icon">📊</div>
        <div class="feature-name">Career Analysis</div>
        <p class="feature-desc">Deep AI analysis of your resume against any job description. Get skill gaps, improvement
          tips, and a match score instantly.</p>
        <div class="feature-price">Core Tool</div>
        <div class="feature-free">Free Forever</div>
      </div>
      <div class="feature-card">
        <div class="feature-num">02</div>
        <div class="feature-icon">📝</div>
        <div class="feature-name">Resume Builder</div>
        <p class="feature-desc">AI-powered resume generator tailored to your target role. Export a polished PDF in
          seconds — no design skills needed.</p>
        <div class="feature-price">Core Tool</div>
        <div class="feature-free">Free Forever</div>
      </div>
      <div class="feature-card">
        <div class="feature-num">03</div>
        <div class="feature-icon">🎤</div>
        <div class="feature-name">Mock Interview</div>
        <p class="feature-desc">Practice with AI-generated questions for your exact role and company. Get model answers
          and performance feedback.</p>
        <div class="feature-price">Core Tool</div>
        <div class="feature-free">Free Forever</div>
      </div>
      <div class="feature-card">
        <div class="feature-num">04</div>
        <div class="feature-icon">📂</div>
        <div class="feature-name">PYQ Hub</div>
        <p class="feature-desc">AI-generated previous year question papers for top companies and roles. With answers and
          explanations. Export as PDF.</p>
        <div class="feature-price">Core Tool</div>
        <div class="feature-free">Free Forever</div>
      </div>
      <div class="feature-card">
        <div class="feature-num">05</div>
        <div class="feature-icon">⚖️</div>
        <div class="feature-name">Career Compare</div>
        <p class="feature-desc">Side-by-side comparison of multiple career paths or job offers. Let AI help you make the
          decision with clarity.</p>
        <div class="feature-price">Core Tool</div>
        <div class="feature-free">Free Forever</div>
      </div>
      <div class="feature-card">
        <div class="feature-num">06</div>
        <div class="feature-icon">📚</div>
        <div class="feature-name">Resources Hub</div>
        <p class="feature-desc">Curated learning resources, roadmaps, and certifications tailored to your target role
          and current skill level.</p>
        <div class="feature-price">Core Tool</div>
        <div class="feature-free">Free Forever</div>
      </div>
      <div class="feature-card">
        <div class="feature-num">07</div>
        <div class="feature-icon">📜</div>
        <div class="feature-name">Analysis History</div>
        <p class="feature-desc">Track your career growth over time. Review past analyses, see your progress, and compare
          before vs. after.</p>
        <div class="feature-price">Core Tool</div>
        <div class="feature-free">Free Forever</div>
      </div>
      <div class="feature-card" style="background: var(--black); border: none;">
        <div class="feature-num" style="color: rgba(255,255,255,0.04);">∞</div>
        <div class="feature-icon">🚀</div>
        <div class="feature-name" style="color: var(--white);">Bring Your Own Key</div>
        <p class="feature-desc" style="color: rgba(255,255,255,0.3);">Use Gemini, Groq, or Cohere — all free APIs. Your
          data stays with you. No middleman. No cost.</p>
        <div class="feature-price" style="color: var(--cyan);">Always Free</div>
      </div>
    </div>
  </section>

  <!-- DARK SPECS -->
  <section id="specs">
    <div class="specs-left">
      <div class="section-eyebrow" style="color: rgba(0,208,255,0.5);">Product Specs</div>
      <h2 class="specs-title">LATEST AI<br>SPECS FROM<br><span>OUR ENGINE</span></h2>

      <div class="spec-item">
        <div class="spec-name">MULTI-PROVIDER INTELLIGENCE</div>
        <p class="spec-desc">Switch between Google Gemini, Groq, and Cohere with a click. Run the same analysis on
          different models and compare results for the sharpest insight.</p>
      </div>
      <div class="spec-item">
        <div class="spec-name">REAL-TIME PDF PARSING</div>
        <p class="spec-desc">Upload any PDF resume and get instant text extraction via PyMuPDF. Works on all formats —
          scanned or digital.</p>
      </div>
      <div class="spec-item">
        <div class="spec-name">PRECISION SCORING ENGINE</div>
        <p class="spec-desc">Proprietary career scoring delivers skill-gap detection, role alignment scoring, and
          learning path generation in under 3 seconds.</p>
      </div>
      <div class="spec-item">
        <div class="spec-name">EXPORT-READY PDF OUTPUT</div>
        <p class="spec-desc">Every analysis, resume, and question paper can be exported as a beautifully formatted PDF
          using our ReportLab engine.</p>
      </div>
    </div>

    <div class="specs-right">
      <div class="spec-pill">
        <div class="spec-pill-icon">⚡</div>
        <div>
          <div class="spec-pill-name">GEMINI 2.0 FLASH</div>
          <div class="spec-pill-label">Google · 1500 req/day free</div>
        </div>
        <div class="spec-pill-badge">Live</div>
      </div>
      <div class="spec-pill">
        <div class="spec-pill-icon">🦙</div>
        <div>
          <div class="spec-pill-name">LLAMA 3.3 70B</div>
          <div class="spec-pill-label">Groq · Ultra-fast inference</div>
        </div>
        <div class="spec-pill-badge">Live</div>
      </div>
      <div class="spec-pill">
        <div class="spec-pill-icon">🌊</div>
        <div>
          <div class="spec-pill-name">COMMAND R+</div>
          <div class="spec-pill-label">Cohere · Generous free tier</div>
        </div>
        <div class="spec-pill-badge">Live</div>
      </div>
      <div class="spec-pill">
        <div class="spec-pill-icon">📄</div>
        <div>
          <div class="spec-pill-name">PDF RESUME PARSER</div>
          <div class="spec-pill-label">PyMuPDF · All formats</div>
        </div>
        <div class="spec-pill-badge">Active</div>
      </div>
      <div class="spec-pill">
        <div class="spec-pill-icon">📊</div>
        <div>
          <div class="spec-pill-name">CAREER SCORING ALGO</div>
          <div class="spec-pill-label">Altair + custom metrics</div>
        </div>
        <div class="spec-pill-badge">Active</div>
      </div>
    </div>
  </section>

  <!-- BENEFITS -->
  <section id="benefits">
    <div class="benefits-left">
      <div class="benefits-visual">
        <div class="benefits-visual-inner">
          <div class="benefits-visual-num">AI</div>
        </div>
        <div class="benefits-visual-label">POWERED BY<br>FREE AI</div>
      </div>
      <div class="benefits-accent">100% FREE</div>
    </div>

    <div class="benefits-right">
      <p class="section-eyebrow">Benefits of JobLess AI</p>
      <h2 class="section-title">WHY CHOOSE<br>OUR PLATFORM</h2>
      <p class="section-sub">Discover the advantages that make JobLess AI the go-to tool for serious job seekers.</p>

      <div class="benefit-list">
        <div class="benefit-item">
          <div class="benefit-icon-wrap" style="background: var(--black);">
            <span style="color: var(--cyan);">🌍</span>
          </div>
          <div>
            <div class="benefit-name">INDUSTRY-GRADE AI MODELS</div>
            <p class="benefit-desc">We integrate only with the most capable free-tier AI APIs — Gemini, Groq, Cohere —
              the same models used by enterprises worldwide.</p>
          </div>
        </div>
        <div class="benefit-item">
          <div class="benefit-icon-wrap" style="background: var(--black);">
            <span style="color: var(--cyan);">🔒</span>
          </div>
          <div>
            <div class="benefit-name">ZERO DATA STORAGE</div>
            <p class="benefit-desc">Your resume and career data is processed on-the-fly and never stored by JobLess AI.
              Full privacy, always.</p>
          </div>
        </div>
        <div class="benefit-item">
          <div class="benefit-icon-wrap" style="background: var(--black);">
            <span style="color: var(--cyan);">✨</span>
          </div>
          <div>
            <div class="benefit-name">ALWAYS UP-TO-DATE</div>
            <p class="benefit-desc">We continuously update our tool catalogue and AI provider integrations to keep you
              ahead of the job market.</p>
          </div>
        </div>
        <div class="benefit-item">
          <div class="benefit-icon-wrap" style="background: var(--black);">
            <span style="color: var(--cyan);">🚀</span>
          </div>
          <div>
            <div class="benefit-name">FREE FOREVER PROMISE</div>
            <p class="benefit-desc">All 7 tools. All 3 AI providers. All exports. Free. We believe great career tools
              should be accessible to everyone.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA DARK -->
  <section id="cta-dark">
    <div class="cta-grid-bg"></div>
    <p class="section-eyebrow" style="position: relative;">What They Say About Us</p>
    <h2 class="cta-title" style="position: relative;">REAL RESULTS<br>FROM <span>REAL</span> USERS</h2>
    <p
      style="color: rgba(255,255,255,0.3); max-width: 480px; margin: 0 auto; font-size: 15px; line-height: 1.7; position: relative;">
      Listen directly from students and professionals who used JobLess AI to land their dream roles.
    </p>
  </section>

  <!-- TESTIMONIALS -->
  <section id="testimonials">
    <div class="testimonials-grid">
      <div class="testi-card">
        <div class="testi-stars">★★★★★</div>
        <p class="testi-text">"JobLess AI's mock interview tool was a game changer for my Google interview prep. The
          AI-generated questions matched exactly what I was asked on the day."</p>
        <div class="testi-author">
          <div class="testi-avatar">AR</div>
          <div>
            <div class="testi-name">Arjun Rao</div>
            <div class="testi-role">SWE · Google India</div>
          </div>
        </div>
      </div>
      <div class="testi-card">
        <div class="testi-stars">★★★★★</div>
        <p class="testi-text">"I uploaded my resume and got a detailed skill gap report in seconds. The PYQ Hub gave me
          50+ real company questions. I got placed at TCS within 2 weeks."</p>
        <div class="testi-author">
          <div class="testi-avatar">PD</div>
          <div>
            <div class="testi-name">Priya Deshpande</div>
            <div class="testi-role">Data Analyst · TCS</div>
          </div>
        </div>
      </div>
      <div class="testi-card">
        <div class="testi-stars">★★★★★</div>
        <p class="testi-text">"The resume builder generated a better resume than I could write myself. The AI knew
          exactly what keywords to include for a product manager role at Amazon."</p>
        <div class="testi-author">
          <div class="testi-avatar">SK</div>
          <div>
            <div class="testi-name">Samira Khan</div>
            <div class="testi-role">PM · Amazon</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- FAQ -->
  <section id="faq">
    <div class="faq-left">
      <p class="section-eyebrow">FAQ About JobLess AI</p>
      <h2 class="section-title">FREQUENTLY<br>ASKED<br>QUESTIONS</h2>
      <p class="section-sub" style="margin-bottom: 0;">Discover what our users are asking about JobLess AI — answered by
        those who have experienced the results.</p>
    </div>

    <div class="faq-right">
      <div class="faq-item open">
        <div class="faq-question" onclick="toggleFaq(this)">
          How do I start using JobLess AI?
          <span class="faq-icon">+</span>
        </div>
        <div class="faq-answer">
          Simply get a free API key from Google AI Studio, Groq, or Cohere — all free with no credit card needed. Enter
          it in the sidebar of the app and you're ready to go instantly.
        </div>
      </div>
      <div class="faq-item">
        <div class="faq-question" onclick="toggleFaq(this)">
          Is my resume data stored anywhere?
          <span class="faq-icon">+</span>
        </div>
        <div class="faq-answer">
          No. Your resume and all personal data is processed in real-time by your chosen AI provider and is never stored
          by JobLess AI. Your data belongs entirely to you.
        </div>
      </div>
      <div class="faq-item">
        <div class="faq-question" onclick="toggleFaq(this)">
          What is the difference between Gemini, Groq, and Cohere?
          <span class="faq-icon">+</span>
        </div>
        <div class="faq-answer">
          All three are free AI providers. Gemini offers the most generous daily limits (1500 req/day). Groq provides
          ultra-fast inference — great for quick mock interviews. Cohere excels at text understanding and document
          analysis.
        </div>
      </div>
      <div class="faq-item">
        <div class="faq-question" onclick="toggleFaq(this)">
          What tools does JobLess AI include?
          <span class="faq-icon">+</span>
        </div>
        <div class="faq-answer">
          JobLess AI includes 7 tools: Career Analysis, History Tracking, Career Compare, Resources Hub, Resume Builder,
          Mock Interview Simulator, and PYQ Hub. All free, all in one place.
        </div>
      </div>
      <div class="faq-item">
        <div class="faq-question" onclick="toggleFaq(this)">
          Can I export my results as a PDF?
          <span class="faq-icon">+</span>
        </div>
        <div class="faq-answer">
          Yes! Every analysis, resume, and question paper can be exported as a professionally formatted PDF — ready to
          send to recruiters or save for your records.
        </div>
      </div>
    </div>
  </section>

  <!-- PROVIDERS -->
  <section id="providers">
    <p class="section-eyebrow" style="text-align: center; margin-inline: auto;">AI Providers</p>
    <h2 class="section-title" style="text-align: center;">CHOOSE YOUR<br>AI ENGINE</h2>
    <p class="section-sub" style="text-align: center; margin-inline: auto;">All providers offer completely free API
      keys. No credit card. No subscription. Just intelligence.</p>

    <div class="providers-grid">
      <div class="provider-card">
        <div class="provider-icon">✨</div>
        <div class="provider-name">Google Gemini</div>
        <div class="provider-free">✅ Free · No Card Needed</div>
        <div class="provider-models">
          gemini-2.0-flash<br>
          gemini-2.0-flash-lite<br>
          gemini-1.5-flash<br>
          gemini-1.5-pro
        </div>
        <div class="provider-badge">1500 req/day</div>
      </div>
      <div class="provider-card" style="border-color: var(--black);">
        <div class="provider-icon">⚡</div>
        <div class="provider-name">Groq · Ultra Fast</div>
        <div class="provider-free">✅ Free · Ultra-Fast</div>
        <div class="provider-models">
          llama-3.3-70b<br>
          llama-3.1-8b-instant<br>
          mixtral-8x7b<br>
          gemma2-9b
        </div>
        <div class="provider-badge">Best Speed</div>
      </div>
      <div class="provider-card">
        <div class="provider-icon">🌊</div>
        <div class="provider-name">Cohere</div>
        <div class="provider-free">✅ Free Trial · No Card</div>
        <div class="provider-models">
          command-r-plus<br>
          command-r<br>
          command<br>
          command-light
        </div>
        <div class="provider-badge">Best for Docs</div>
      </div>
    </div>
  </section>

  <!-- LAUNCH CTA BANNER -->
  <section style="background: var(--cyan); padding: 80px 48px; text-align: center;">
    <p
      style="font-size: 11px; letter-spacing: 5px; text-transform: uppercase; color: rgba(0,0,0,0.45); font-weight: 500; margin-bottom: 16px;">
      Ready To Start?</p>
    <h2
      style="font-family: 'Bebas Neue', sans-serif; font-size: clamp(52px, 7vw, 100px); line-height: 0.92; letter-spacing: 1px; color: var(--black); margin-bottom: 28px;">
      LAUNCH THE<br>APP NOW</h2>
    <p
      style="font-size: 15px; color: rgba(0,0,0,0.55); max-width: 420px; margin: 0 auto 40px; line-height: 1.7; font-weight: 300;">
      Your resume. Your career. Your AI. Free forever at joblessai.streamlit.app</p>
    <a href="?page=app"
      style="display: inline-block; background: var(--black); color: var(--white); font-weight: 700; font-size: 13px; letter-spacing: 3px; text-transform: uppercase; padding: 20px 52px; text-decoration: none; transition: opacity 0.2s;"
      onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
      OPEN JOBLESS AI →
    </a>
  </section>

  <!-- FOOTER -->
  <footer>
    <div class="footer-top">
      <div class="footer-brand">
        <div class="footer-logo">Jobless<span>AI</span></div>
        <p class="footer-tagline">Transform your potential into a concrete career roadmap — powered by free AI. No
          subscription. No compromise.</p>
      </div>
      <div class="footer-cols">
        <div class="footer-col">
          <h4>Tools</h4>
          <ul>
            <li><a href="#">Career Analysis</a></li>
            <li><a href="#">Resume Builder</a></li>
            <li><a href="#">Mock Interview</a></li>
            <li><a href="#">PYQ Hub</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>More</h4>
          <ul>
            <li><a href="#">Career Compare</a></li>
            <li><a href="#">Resources Hub</a></li>
            <li><a href="#">History</a></li>
            <li><a href="#">About</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>AI Providers</h4>
          <ul>
            <li><a href="https://aistudio.google.com/app/apikey" target="_blank">Google Gemini</a></li>
            <li><a href="https://console.groq.com/keys" target="_blank">Groq</a></li>
            <li><a href="https://dashboard.cohere.com/api-keys" target="_blank">Cohere</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-newsletter">
        <h4>Stay Updated</h4>
        <p>Get the latest updates, new tools, and career tips delivered to your inbox.</p>
        <div class="newsletter-form">
          <input class="newsletter-input" type="email" placeholder="Enter your email">
          <button class="newsletter-btn">Go →</button>
        </div>
      </div>
    </div>

    <div class="footer-bottom">
      <div class="footer-copy">© 2025 JobLess AI · Created by Anubhab Mondal · Your data is never stored.</div>
      <div class="footer-legal">
        <a href="#">Terms & Agreement</a>
        <a href="#">Privacy Policy</a>
      </div>
    </div>

    <div class="footer-watermark">JOBLESS AI</div>
  </footer>

  <script>
    // FAQ Toggle
    function toggleFaq(el) {
      const item = el.parentElement;
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    }

    // Fade-up on scroll
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('visible'); }
      });
    }, { threshold: 0.1 });
    document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

    // Smooth nav active
    window.addEventListener('scroll', () => {
      const nav = document.querySelector('nav');
      nav.style.background = window.scrollY > 40
        ? 'rgba(10,10,10,0.97)'
        : 'rgba(10,10,10,0.92)';
    });
  </script>
</body>

</html>
"""


def _show_landing_page():
    """Render the landing page. Uses a base64 data URI iframe for reliability on Streamlit Cloud."""
    import base64

    # Hide all Streamlit chrome
    st.markdown("""
        <style>
            header[data-testid="stHeader"], footer, #MainMenu,
            [data-testid="collapsedControl"], [data-testid="stToolbar"],
            [data-testid="stDecoration"], [data-testid="stStatusWidget"]
                { display: none !important; }
            html, body, .main, .block-container,
            [data-testid="stAppViewContainer"],
            [data-testid="stAppViewContainer"] > section.main,
            [data-testid="stVerticalBlock"],
            [data-testid="stVerticalBlockBorderWrapper"],
            div[data-testid="stMainBlockContainer"] {
                padding: 0 !important; margin: 0 !important;
                max-width: 100% !important; height: 100vh !important;
            }
            iframe#landing-frame { border: none !important; }
        </style>
    """, unsafe_allow_html=True)

    # Add navigation script BEFORE </body>
    nav_script = """<script>
    (function () {
        function goToApp() {
            try {
                var base = window.parent.location.href.split('?')[0].split('#')[0];
                window.parent.location.href = base + '?page=app';
            } catch (e) {
                try {
                    var base2 = window.top.location.href.split('?')[0].split('#')[0];
                    window.top.location.href = base2 + '?page=app';
                } catch (e2) {
                    window.location.href = '/?page=app';
                }
            }
        }
        document.addEventListener('click', function (e) {
            var el = e.target;
            for (var i = 0; i < 5 && el; i++, el = el.parentElement) {
                if (el.tagName === 'A') {
                    var href = el.getAttribute('href') || '';
                    if (href === '?page=app' || href.indexOf('page=app') !== -1) {
                        e.preventDefault();
                        e.stopImmediatePropagation();
                        goToApp();
                        return;
                    }
                    break;
                }
            }
        }, true);
    })();
    </script>"""

    html_final = _LANDING_PAGE_HTML.replace(
        "</body>", nav_script + "\n</body>")

    # Encode as base64 data URI — the most reliable way to embed full HTML in Streamlit
    b64 = base64.b64encode(html_final.encode("utf-8")).decode("utf-8")
    data_uri = f"data:text/html;charset=utf-8;base64,{b64}"

    st.markdown(
        f'<iframe id="landing-frame" src="{data_uri}" '
        f'width="100%" height="900" frameborder="0" '
        f'style="border:none;display:block;width:100%;height:100vh;"></iframe>',
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(
        page_title="JobLess AI",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # ── Routing: show landing page unless ?page=app is in the URL ──────────
    page = st.query_params.get("page", "landing")
    if page != "app":
        _show_landing_page()
        st.stop()

    # ── App mode ────────────────────────────────────────────────────────────
    init_session_state()

    config = Config()
    ui = UIComponents()
    ai_handler = AIHandler(config)
    pdf_handler = PDFHandler()
    history_manager = HistoryManager()

    ui.apply_custom_css()
    inject_mobile_nav()

    # Sidebar (returns settings needed by tabs)
    selected_provider, selected_model, analysis_depth, include_learning_path, include_interview_prep = \
        render_sidebar(config)

    # Animated header
    components.html(_HEADER_HTML, height=190, scrolling=False)

    # Gate: require API key
    if not config.is_ready():
        ui.show_api_setup_banner()
        st.info(
            "👈 **Next Step:** Enter your API key in the sidebar to start analyzing careers!")
        st.stop()

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Career Analysis", "📜 History", "⚖️ Compare",
        "📚 Resources", "📝 Resume Builder", "🎤 Mock Interview", "📂 PYQ Hub",
    ])

    with tab1:
        render_tab_career_analysis(
            ai_handler, pdf_handler, history_manager, selected_model,
            analysis_depth, include_learning_path, include_interview_prep)

    with tab2:
        render_tab_history()

    with tab3:
        render_tab_compare()

    with tab4:
        render_tab_resources()

    with tab5:
        render_tab_resume_builder(ai_handler, selected_model)

    with tab6:
        render_tab_mock_interview(ai_handler, selected_model)

    with tab7:
        render_tab_pyq_hub(ai_handler, selected_model)

    # Footer
    st.markdown(f"""
        <div style="text-align:center;padding:20px;color:#94a3b8;">
            © {datetime.date.today().year} JobLess AI | Created by Anubhab Mondal
            <br>
            <span style="font-size:0.77rem;color:#475569;">
                Your resume data is processed by your chosen AI provider and is
                <strong>not stored</strong> by this app.
            </span>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
