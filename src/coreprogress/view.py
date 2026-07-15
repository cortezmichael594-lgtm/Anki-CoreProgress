# Copyright (C) 2026 AnkiCraft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

from __future__ import annotations

import json

from aqt import mw

from .effects import STREAK_LABEL_MIN_LEFT_PERCENT
from .palettes import StyleBundle

WRAP_ID = "_cprogBar"
TRACK_ID = "_cprogTrack"
FILL_ID = "_cprogFill"
LABEL_ID = "_cprogLabel"

BAR_HEIGHT = 16
_RADIUS = BAR_HEIGHT
_FILL_RADIUS = BAR_HEIGHT // 2
_MIN_LEFT = f"{STREAK_LABEL_MIN_LEFT_PERCENT:.1f}"

_STATIC_CSS = """
._cprogSheenBand{position:absolute;top:-25%;height:150%;width:22%;left:-30%;
background:linear-gradient(90deg,rgba(255,255,255,0) 0%,rgba(255,255,255,.5) 50%,rgba(255,255,255,0) 100%);
transform:skewX(-18deg);opacity:0;animation:_cprogSheen 9s ease-in-out infinite;}
@keyframes _cprogSheen{0%{left:-30%;opacity:0;}6%{opacity:.26;}22%{opacity:.26;}
32%{left:130%;opacity:0;}100%{left:130%;opacity:0;}}
@keyframes _cprogGlowPulse{0%{filter:brightness(1);}
35%{filter:brightness(1.55) drop-shadow(0 0 12px rgba(255,255,255,.85));}
100%{filter:brightness(1);}}
@keyframes _cprogSparkleOut{0%{transform:translate(-50%,-50%) scale(.2) rotate(0deg);opacity:1;}
100%{transform:translate(calc(-50% + var(--dx)),calc(-50% + var(--dy))) scale(1) rotate(90deg);opacity:0;}}
._cprogSparkle{position:absolute;top:50%;width:12px;height:12px;pointer-events:none;color:#fff;
font-size:13px;line-height:12px;text-shadow:0 0 4px rgba(255,255,255,.9);
animation:_cprogSparkleOut .75s ease-out forwards;}
@media (prefers-reduced-motion: reduce){._cprogSheenBand{animation:none;left:24%;opacity:.16;}}
#_mark,#_flag{top:30px !important;}
img#star{top:30px !important;}
"""

_INJECT_TEMPLATE = """
(function(){
    var prev=document.getElementById('__WRAP__');
    if(prev) prev.remove();

    if(!document.getElementById('_cprogStaticStyle')){
        var st=document.createElement('style');
        st.id='_cprogStaticStyle';
        st.textContent=__CSS__;
        document.head.appendChild(st);
    }

    window._cprogIsDark=function(){
        return document.body.classList.contains('night-mode')
            || document.body.classList.contains('nightMode')
            || document.documentElement.getAttribute('data-bs-theme')==='dark'
            || window.matchMedia('(prefers-color-scheme: dark)').matches;
    };

    window._cprogCardVar=function(name,fallback){
        try{
            var el=document.querySelector('.card')||document.body;
            var v=getComputedStyle(el).getPropertyValue(name).trim();
            return v||fallback;
        }catch(e){return fallback;}
    };
    window._cprogPaintTrack=function(){
        var tr=document.getElementById('__TRACK__');
        if(!tr) return;
        var dk=window._cprogIsDark();
        tr.style.background=window._cprogCardVar('--card-border',dk?'rgba(255,255,255,0.07)':'rgba(0,0,0,0.10)');
        tr.style.borderColor=window._cprogCardVar('--divider',dk?'rgba(255,255,255,0.12)':'rgba(0,0,0,0.10)');
    };

    var dark=window._cprogIsDark();
    var trackShadow=dark
        ?'inset 0 2px 6px rgba(0,0,0,0.6), inset 0 1px 2px rgba(0,0,0,0.4)'
        :'inset 0 2px 5px rgba(0,0,0,0.20), inset 0 1px 2px rgba(0,0,0,0.12)';

    var wrap=document.createElement('div');
    wrap.id='__WRAP__';
    wrap.style.cssText='position:fixed;top:0;left:0;right:0;z-index:99999;padding:10px 18px;pointer-events:none';

    var track=document.createElement('div');
    track.id='__TRACK__';
    track.style.cssText=['width:100%','height:__BARH__px','border-radius:__RADIUS__px',
        'overflow:visible','position:relative','border:1px solid transparent',
        'box-shadow:'+trackShadow].join(';');

    var fill=document.createElement('div');
    fill.id='__FILL__';
    fill.style.cssText=['height:100%','border-radius:__FILLRADIUS__px','position:relative',
        'transition:width .4s cubic-bezier(.5,0,.2,1),background .6s ease,box-shadow .6s ease',
        'width:0%'].join(';');

    var sheenBox=document.createElement('div');
    sheenBox.style.cssText='position:absolute;inset:0;overflow:hidden;border-radius:__FILLRADIUS__px;pointer-events:none';
    var sheenBand=document.createElement('div');
    sheenBand.className='_cprogSheenBand';
    sheenBox.appendChild(sheenBand);
    fill.appendChild(sheenBox);
    track.appendChild(fill);

    var label=document.createElement('div');
    label.id='__LABEL__';
    label.style.cssText=['position:absolute','top:100%','left:__MINLEFT__%','transform:translateX(-50%)',
        'margin-top:6px','white-space:nowrap','pointer-events:none','font-size:13px','font-weight:700',
        'font-family:"Nunito","Quicksand","Segoe UI Semibold",system-ui,-apple-system,sans-serif','letter-spacing:.04em','text-transform:uppercase',
        'transition:opacity .3s ease,left .4s cubic-bezier(.5,0,.2,1)','opacity:0'].join(';');
    label.textContent='';
    track.appendChild(label);

    wrap.appendChild(track);
    document.body.prepend(wrap);
    window._cprogPaintTrack();

    window._cprogApply=function(p,bundle){
        var f=document.getElementById('__FILL__');
        if(!f) return;
        var m=window._cprogIsDark()?bundle.dark:bundle.light;
        f.style.width=p+'%';
        f.style.background=m.gradient;
        f.style.boxShadow=m.shadow;
        var lbl=document.getElementById('__LABEL__');
        if(lbl){
            lbl.style.left=Math.max(__MINLEFT__,p/2)+'%';
            lbl.style.color=m.solid;
        }
        window._cprogLast={p:p,b:bundle};
    };

    window._cprogReapply=function(){
        if(window._cprogPaintTrack) window._cprogPaintTrack();
        var s=window._cprogLast;
        if(s) window._cprogApply(s.p,s.b);
    };

    window._cprogShowStreak=function(text,bundle){
        var lbl=document.getElementById('__LABEL__');
        if(!lbl||!text) return;
        var m=window._cprogIsDark()?bundle.dark:bundle.light;
        lbl.textContent=text;
        lbl.style.color=m.solid;
        if(m.glow) lbl.style.textShadow=m.glow;
        lbl.style.opacity='1';
    };

    window._cprogHideStreak=function(){
        var lbl=document.getElementById('__LABEL__');
        if(lbl) lbl.style.opacity='0';
    };

    window._cprogCelebrate=function(){
        var track=document.getElementById('__TRACK__');
        var f=document.getElementById('__FILL__');
        if(!track||!f) return;
        f.style.animation='none';
        void f.offsetWidth;
        f.style.animation='_cprogGlowPulse .9s ease-out';
        if(window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        var edge=parseFloat(f.style.width)||0;
        var count=8;
        for(var i=0;i<count;i++){
            var s=document.createElement('span');
            s.className='_cprogSparkle';
            s.textContent='\\u2726';
            var angle=(Math.PI*2*i)/count+(Math.random()*0.5-0.25);
            var dist=18+Math.random()*16;
            s.style.setProperty('--dx',(Math.cos(angle)*dist)+'px');
            s.style.setProperty('--dy',(Math.sin(angle)*dist)+'px');
            s.style.left=edge+'%';
            track.appendChild(s);
            s.addEventListener('animationend',function(){this.remove();});
        }
    };

    if(!window._cprogThemeHook){
        window._cprogThemeHook=true;
        try{window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',window._cprogReapply);}catch(e){}
        try{
            var mo=new MutationObserver(function(){window._cprogReapply();});
            mo.observe(document.body,{attributes:true,attributeFilter:['class']});
            mo.observe(document.documentElement,{attributes:true,attributeFilter:['data-bs-theme']});
        }catch(e){}
    }

    window._cprogApply(__PROGRESS__,__BUNDLE__);
})();
"""


def _reviewer_web_eval(js: str) -> None:
    try:
        if mw and mw.reviewer and mw.reviewer.web:
            mw.reviewer.web.eval(js)
    except Exception as exc:
        print(f"[coreprogress] {exc!r}")


def build_inject_js(bundle: StyleBundle, progress: float) -> str:
    return (
        _INJECT_TEMPLATE.replace("__WRAP__", WRAP_ID)
        .replace("__TRACK__", TRACK_ID)
        .replace("__FILL__", FILL_ID)
        .replace("__LABEL__", LABEL_ID)
        .replace("__CSS__", json.dumps(_STATIC_CSS))
        .replace("__BARH__", str(BAR_HEIGHT))
        .replace("__RADIUS__", str(_RADIUS))
        .replace("__FILLRADIUS__", str(_FILL_RADIUS))
        .replace("__MINLEFT__", _MIN_LEFT)
        .replace("__BUNDLE__", bundle.to_json())
        .replace("__PROGRESS__", f"{progress:.1f}")
    )


def build_update_js(bundle: StyleBundle, progress: float) -> str:
    return (
        "typeof _cprogApply==='function' && _cprogApply("
        + f"{progress:.1f},"
        + bundle.to_json()
        + ");"
    )


def build_push_js(push_down: int) -> str:
    return (
        "(function(){var qa=document.getElementById('qa');"
        f"if(qa){{qa.style.paddingTop={int(push_down)}+'px';}}"
        "})();"
    )


def build_celebrate_js() -> str:
    return "typeof _cprogCelebrate==='function' && _cprogCelebrate();"


def build_hide_streak_js() -> str:
    return "typeof _cprogHideStreak==='function' && _cprogHideStreak();"


def build_streak_label_js(text: str, bundle: StyleBundle) -> str:
    if not text:
        return ""
    return (
        "typeof _cprogShowStreak==='function' && _cprogShowStreak("
        + json.dumps(text)
        + ","
        + bundle.to_json()
        + ");"
    )


def reviewer_eval(js: str) -> None:
    if js:
        _reviewer_web_eval(js)
