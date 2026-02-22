"""
JobLess AI - Public Version (Users Bring Their Own API Key)
Enhanced version with clear API key instructions
Refactored: each tab is its own render_tab_*() function.
"""

import datetime
import streamlit as st
import streamlit.components.v1 as components
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
* { margin:0; padding:0; box-sizing:border-box; }

/* FIX 1: overflow:hidden on body kills 3D transforms on iOS Safari.
   Use overflow:clip instead — it clips visually without creating a
   stacking context that flattens preserve-3d children.
   Fallback: auto (allows scroll in very old browsers, not ideal but safe). */
body {
  background: transparent!important;
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
  if(fe){ fe.style.cssText += 'border:none!important;outline:none!important;box-shadow:none!important;background:transparent!important;'; }
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

    def get_api_key(self, provider=None) -> str:
        p = provider or self.get_provider()
        val = st.session_state.get(f"api_key_{p}", "")
        return val or os.getenv(self._ENV.get(p, ""), "")

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
            # response_mime_type requires google-generativeai >= 0.4.0
            # Fallback gracefully for older installs
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
            prompt = f"""
            Act as an Elite Indian Career Strategist and AI Career Coach.
            
            **User Profile Analysis:**
            {input_text}
            
            **Context:**
            - Target Industries: {', '.join(context.get('industries', []))}
            - Career Stage: {context.get('career_stage', 'Not specified')}
            - Location Preference: {context.get('location', 'Flexible')}
            
            **Task:**
            Provide a comprehensive career analysis. Return ONLY a valid JSON object (no markdown, no code blocks) with this exact structure:
            
            {{
              "profile_summary": "A concise 2-sentence professional summary",
              "current_skills": ["Skill1", "Skill2", "Skill3"],
              "careers": [
                {{
                  "title": "Specific Job Title",
                  "match_score": 85,
                  "salary_range": "₹15L - ₹25L",
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
            prompt = f"""You are a world-class technical recruiter who has conducted 10,000+ interviews at companies like Google, Microsoft, Amazon, Flipkart, Infosys, TCS, Wipro, Zomato, CRED, Razorpay, PhonePe, Swiggy, Meesho, and other top Indian and global tech companies.

Generate a realistic mock interview for:
Role: {role}
Level: {level}

Return ONLY a raw JSON array with exactly 8 question objects. No markdown. No code fences. Start with [ and end with ].

Format:
[{{"id":1,"category":"Behavioral","question":"Full question text here","difficulty":"Easy","companies":["Google","Amazon"],"hint":"STAR method tip","ideal_answer_points":["Point 1","Point 2","Point 3"],"follow_ups":["Follow-up 1"]}}]

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

{{"score": 72,"verdict": "Good","one_line_reaction": "Solid attempt but missed key technical depth.","what_you_did_well": ["Specific strength 1","Specific strength 2"],"what_went_wrong": ["Specific gap 1","Specific gap 2"],"how_to_improve": ["Concrete actionable fix 1","Concrete actionable fix 2"],"sample_better_answer": "A 3-4 sentence model answer using STAR method","keywords_used": ["kw1","kw2"],"keywords_missed": ["kw3","kw4"],"crack_this_question": "Likely","crack_message": "Honest verdict on whether this answer would pass."}}

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
            text = ""
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
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
    loc = "India"
    naukri_slug = title.lower().replace(" ", "-")
    return {
        "LinkedIn":  f"https://www.linkedin.com/jobs/search/?keywords={q_enc}&location={loc}",
        "Naukri":    f"https://www.naukri.com/{naukri_slug}-jobs",
        "Indeed":    f"https://in.indeed.com/jobs?q={q_enc}&l={loc}",
        "Glassdoor": f"https://www.glassdoor.co.in/Jobs/{title_enc.replace('+', '-')}-jobs-SRCH_KO0,{len(title)}.htm",
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
    icons = {"LinkedIn": "🔵", "Naukri": "🟠", "Indeed": "🟢", "Glassdoor": "💼"}
    cls = {"LinkedIn": "linkedin", "Naukri": "naukri",
           "Indeed": "indeed", "Glassdoor": "glassdoor"}
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
        components.html(particle_js, height=0, scrolling=False)

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

        if config.is_ready():
            st.success(f"""
            **✅ Ready to Analyze**
            - Provider: {selected_provider.split()[0]}
            - Model: {selected_model}
            - History: {len(st.session_state.history)} records
            """)
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
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ==================== MAIN ====================
def main():
    st.set_page_config(
        page_title="JobLess AI",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()

    config = Config()
    ui = UIComponents()
    ai_handler = AIHandler(config)
    pdf_handler = PDFHandler()
    history_manager = HistoryManager()

    ui.apply_custom_css()

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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Career Analysis", "📜 History", "⚖️ Compare",
        "📚 Resources", "📝 Resume Builder", "🎤 Mock Interview",
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
