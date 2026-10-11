def get_fireball_intro_html():
    """
    Realistic Fireball Burst and Thermal White-Light Flash Animation:
    1. Flaming meteor accelerates from upper atmosphere with spark and smoke wake
    2. Ground zero impact triggers:
       - Blinding, incandescent white-light nuclear/thermal flash
       - Volumetric rolling fireballs (white-hot to fiery orange to dark billowing smoke)
       - 180+ high-velocity incandescent shrapnel sparks with motion blur tails
       - Supersonic compression shockwave ring
    3. Dissipating light reveals:
       - TEAM HIVEMIND credentials banner
       - Glowing molten title: HIVEMIND
       - Tactical Earth observation sensor telemetry boot log
       - Reliable, 100% functional 'ENTER 3D TACTICAL WAR ROOM' button
    """
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hivemind Intro</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body, html {
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #03060d;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #fff;
    user-select: none;
  }
  #canvas-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
  }
  canvas {
    display: block;
    width: 100%;
    height: 100%;
  }
  
  /* Intense Blinding White Thermal Flash */
  #white-flash {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle at 50% 55%, #ffffff 0%, #fff7ed 40%, rgba(255,255,255,0.85) 70%, rgba(255,255,255,0) 100%);
    opacity: 0;
    pointer-events: none;
    z-index: 50;
    transition: opacity 0.1s ease-out;
  }

  /* Cinematic Title Overlay */
  #ui-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 60;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    pointer-events: none;
    text-align: center;
    padding: 24px;
  }
  .title-box {
    opacity: 0;
    transform: scale(0.88);
    transition: all 1.2s cubic-bezier(0.16, 1, 0.3, 1);
  }
  .title-box.revealed {
    opacity: 1;
    transform: scale(1);
  }
  
  /* Team & Group Banner */
  .team-banner {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(249, 115, 22, 0.6);
    border-radius: 20px;
    padding: 5px 16px;
    font-size: 11px;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #f97316;
    font-weight: 800;
    margin-bottom: 12px;
    box-shadow: 0 0 20px rgba(249, 115, 22, 0.35);
  }
  .team-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #ef4444;
    box-shadow: 0 0 8px #ef4444;
  }
  
  h1.main-title {
    font-size: 64px;
    font-weight: 900;
    letter-spacing: 0.15em;
    background: linear-gradient(180deg, #ffffff 0%, #fed7aa 25%, #f97316 65%, #dc2626 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 40px rgba(249, 115, 22, 0.7), 0 0 80px rgba(220, 38, 38, 0.45);
    margin-bottom: 10px;
  }
  .tagline {
    font-size: 19px;
    letter-spacing: 0.06em;
    color: #f1f5f9;
    max-width: 740px;
    line-height: 1.45;
    text-shadow: 0 2px 14px rgba(0,0,0,0.9);
    margin-bottom: 8px;
    font-weight: 600;
  }
  .sub-desc {
    font-size: 13px;
    color: #94a3b8;
    margin-bottom: 22px;
    letter-spacing: 0.05em;
  }
  
  .terminal-box {
    background: rgba(10, 16, 30, 0.82);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 8px;
    padding: 12px 22px;
    text-align: left;
    font-family: 'Courier New', Courier, monospace;
    font-size: 12px;
    color: #38bdf8;
    max-width: 540px;
    margin: 0 auto 26px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.6);
    backdrop-filter: blur(10px);
  }
  .terminal-line {
    margin: 4px 0;
    opacity: 0;
    transform: translateX(-10px);
    transition: all 0.35s ease;
  }
  .terminal-line.active {
    opacity: 1;
    transform: translateX(0);
  }
  
  .btn-enter {
    pointer-events: auto;
    background: linear-gradient(135deg, #f97316 0%, #ea580c 50%, #dc2626 100%);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 35px;
    padding: 16px 42px;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    cursor: pointer;
    box-shadow: 0 0 30px rgba(249, 115, 22, 0.8), 0 0 60px rgba(220, 38, 38, 0.4);
    transition: all 0.25s ease;
    display: inline-flex;
    align-items: center;
    gap: 12px;
    opacity: 0;
    transform: translateY(20px);
  }
  .btn-enter.revealed {
    opacity: 1;
    transform: translateY(0);
  }
  .btn-enter:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 0 50px rgba(249, 115, 22, 1.0), 0 0 85px rgba(220, 38, 38, 0.7);
    background: linear-gradient(135deg, #fb923c, #f97316, #ef4444);
  }
  
  .skip-btn {
    position: absolute;
    top: 20px;
    right: 25px;
    pointer-events: auto;
    background: rgba(30, 41, 59, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #cbd5e1;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    z-index: 100;
    transition: all 0.2s;
  }
  .skip-btn:hover {
    background: rgba(51, 65, 85, 0.95);
    color: #fff;
    border-color: #f97316;
  }
</style>
</head>
<body>

<div id="canvas-container">
  <canvas id="canvas"></canvas>
</div>

<!-- Realistic Blinding Thermal Flash -->
<div id="white-flash"></div>

<div id="ui-overlay">
  <div id="title-box" class="title-box">
    
    <!-- Team & Group Credentials -->
    <div class="team-banner">
      <div class="team-dot"></div>
      <span>DEVELOPED BY TEAM HIVEMIND • DEFENSE & DISASTER LABS</span>
    </div>

    <h1 class="main-title">🔥 H I V E M I N D</h1>
    <div class="tagline">Near-Real-Time Disaster Perimeter & Spread Forecasting</div>
    <div class="sub-desc">Automated Planetary Earth Observation & Multi-Variable Hazard Propagation Engine</div>
    
    <div class="terminal-box" id="terminal">
      <div class="terminal-line" id="line1">[✓] NASA VIIRS 375m THERMAL SATELLITE STREAM LINKED</div>
      <div class="terminal-line" id="line2">[✓] GEOS CONCAVE HULL (ALPHA-SHAPE) BOUNDARY ONLINE</div>
      <div class="terminal-line" id="line3">[✓] OPEN-METEO ATMOSPHERIC VECTORS SYNCHRONIZED</div>
      <div class="terminal-line" id="line4">[✓] 3D PLANETARY WAR ROOM READY FOR DEPLOYMENT</div>
      <div class="terminal-line" id="line5" style="color: #4ade80; font-weight: 700; border-top: 1px dashed rgba(74, 222, 128, 0.4); padding-top: 6px; margin-top: 6px;">[▶] SYSTEM READY • CLICK 'ENTER 3D TACTICAL WAR ROOM' ABOVE</div>
    </div>
  </div>
</div>

<script>
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const whiteFlash = document.getElementById('white-flash');
const titleBox = document.getElementById('title-box');

let width, height;
function resize() {
  width = canvas.width = window.innerWidth;
  height = canvas.height = window.innerHeight;
}
window.addEventListener('resize', resize);
resize();

// Starfield
const stars = [];
for (let i = 0; i < 180; i++) {
  stars.push({
    x: Math.random() * width,
    y: Math.random() * height,
    size: Math.random() * 1.8 + 0.4,
    alpha: Math.random() * 0.8 + 0.2,
    speed: Math.random() * 0.02 + 0.005
  });
}

// Fireball state
let meteor = {
  startX: -100,
  startY: -100,
  targetX: width * 0.5,
  targetY: height * 0.52,
  x: -100,
  y: -100,
  progress: 0,
  speed: 0.010,
  radius: 26,
  alive: true
};

const meteorTrails = [];
const blastFireballs = [];
const incendiarySparks = [];
const shockwaves = [];
let animFrame;
let blastOccurred = false;

// Meteor trail particle
class MeteorTrail {
  constructor(x, y, radius) {
    this.x = x + (Math.random() - 0.5) * radius;
    this.y = y + (Math.random() - 0.5) * radius;
    this.vx = (Math.random() - 0.5) * 4 - 3;
    this.vy = (Math.random() - 0.5) * 4 - 3;
    this.radius = Math.random() * 14 + 6;
    this.alpha = 0.95;
    this.decay = Math.random() * 0.035 + 0.02;
  }
  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.radius *= 0.94;
    this.alpha -= this.decay;
  }
  draw(ctx) {
    if (this.alpha <= 0) return;
    ctx.save();
    ctx.globalAlpha = Math.max(0, this.alpha);
    let grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, Math.max(1, this.radius));
    grad.addColorStop(0, '#ffffff');
    grad.addColorStop(0.3, '#f59e0b');
    grad.addColorStop(0.7, '#ea580c');
    grad.addColorStop(1, 'rgba(15, 23, 42, 0)');
    ctx.beginPath();
    ctx.arc(this.x, this.y, Math.max(1, this.radius), 0, Math.PI * 2);
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.restore();
  }
}

// REALISTIC EXPANDING VOLUMETRIC FIREBALL (White-hot to flame to smoke)
class VolumetricFireball {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    const angle = Math.random() * Math.PI * 2;
    const speed = Math.random() * 8.5 + 1.5;
    this.vx = Math.cos(angle) * speed;
    this.vy = Math.sin(angle) * speed - 0.5; // slight thermal upward rise
    this.radius = Math.random() * 18 + 12;
    this.maxRadius = Math.random() * 75 + 50;
    this.growth = Math.random() * 2.8 + 1.8;
    this.life = 1.0;
    this.decay = Math.random() * 0.014 + 0.009;
  }
  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.vx *= 0.94;
    this.vy *= 0.94;
    if (this.radius < this.maxRadius) {
      this.radius += this.growth;
    }
    this.life -= this.decay;
  }
  draw(ctx) {
    if (this.life <= 0) return;
    ctx.save();
    ctx.globalAlpha = Math.max(0, this.life);
    let grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius);
    
    // Transitions realistically from white-hot core ➔ incandescent flame ➔ dark billow
    if (this.life > 0.65) {
      grad.addColorStop(0, '#ffffff');
      grad.addColorStop(0.25, '#fef08a');
      grad.addColorStop(0.65, '#f97316');
      grad.addColorStop(1, 'rgba(220, 38, 38, 0)');
    } else if (this.life > 0.3) {
      grad.addColorStop(0, '#fef08a');
      grad.addColorStop(0.35, '#ea580c');
      grad.addColorStop(0.75, '#7f1d1d');
      grad.addColorStop(1, 'rgba(30, 41, 59, 0)');
    } else {
      // Rolling smoke
      grad.addColorStop(0, '#475569');
      grad.addColorStop(0.5, '#1e293b');
      grad.addColorStop(1, 'rgba(15, 23, 42, 0)');
    }
    
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.restore();
  }
}

// REALISTIC INCENDIARY SHRAPNEL SPARKS (High velocity needle streaks)
class IncendiarySpark {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.prevX = x;
    this.prevY = y;
    const angle = Math.random() * Math.PI * 2;
    const speed = Math.random() * 22 + 5;
    this.vx = Math.cos(angle) * speed;
    this.vy = Math.sin(angle) * speed;
    this.life = 1.0;
    this.decay = Math.random() * 0.024 + 0.012;
    this.gravity = 0.12;
    this.color = Math.random() > 0.3 ? '#ffffff' : (Math.random() > 0.5 ? '#fef08a' : '#f97316');
  }
  update() {
    this.prevX = this.x;
    this.prevY = this.y;
    this.x += this.vx;
    this.y += this.vy;
    this.vy += this.gravity;
    this.vx *= 0.96;
    this.vy *= 0.96;
    this.life -= this.decay;
  }
  draw(ctx) {
    if (this.life <= 0) return;
    ctx.save();
    ctx.globalAlpha = Math.max(0, this.life);
    ctx.strokeStyle = this.color;
    ctx.lineWidth = Math.max(1, 2.5 * this.life);
    ctx.shadowBlur = 10;
    ctx.shadowColor = this.color;
    ctx.beginPath();
    ctx.moveTo(this.prevX, this.prevY);
    ctx.lineTo(this.x, this.y);
    ctx.stroke();
    ctx.restore();
  }
}

// Supersonic Compression Shockwave
class Shockwave {
  constructor(x, y, maxR, speed) {
    this.x = x;
    this.y = y;
    this.radius = 12;
    this.maxRadius = maxR;
    this.speed = speed;
    this.life = 1.0;
  }
  update() {
    this.radius += this.speed;
    this.life = Math.max(0, 1.0 - (this.radius / this.maxRadius));
  }
  draw(ctx) {
    if (this.life <= 0) return;
    ctx.save();
    ctx.globalAlpha = this.life * 0.85;
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = Math.max(1.5, 6 * this.life);
    ctx.shadowBlur = 24;
    ctx.shadowColor = '#f97316';
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();
  }
}

function triggerRealisticBlast(x, y) {
  blastOccurred = true;

  // 1. INTENSE BLINDING WHITE LIGHT BURST
  whiteFlash.style.transition = 'opacity 0.05s ease-out';
  whiteFlash.style.opacity = '1.0';
  
  // Smoothly dissipate white light thermal flash over 1.2s
  setTimeout(() => {
    whiteFlash.style.transition = 'opacity 1.2s cubic-bezier(0.16, 1, 0.3, 1)';
    whiteFlash.style.opacity = '0';
  }, 120);

  // 2. Shockwaves
  shockwaves.push(new Shockwave(x, y, Math.min(width, height) * 0.85, 18));
  shockwaves.push(new Shockwave(x, y, Math.min(width, height) * 1.15, 12));

  // 3. Volumetric Rolling Fireballs
  for (let i = 0; i < 42; i++) {
    blastFireballs.push(new VolumetricFireball(x, y));
  }

  // 4. Incendiary Shrapnel Sparks
  for (let i = 0; i < 190; i++) {
    incendiarySparks.push(new IncendiarySpark(x, y));
  }

  // 5. Reveal Group Name & Title through the dissipating smoke
  setTimeout(() => {
    titleBox.classList.add('revealed');
  }, 480);

  setTimeout(() => document.getElementById('line1').classList.add('active'), 850);
  setTimeout(() => document.getElementById('line2').classList.add('active'), 1200);
  setTimeout(() => document.getElementById('line3').classList.add('active'), 1550);
  setTimeout(() => document.getElementById('line4').classList.add('active'), 1900);

  setTimeout(() => {
    const l5 = document.getElementById('line5');
    if (l5) l5.classList.add('active');
  }, 2200);
}

function animate() {
  ctx.fillStyle = 'rgba(3, 6, 13, 0.28)';
  ctx.fillRect(0, 0, width, height);

  // Stars
  for (let s of stars) {
    ctx.fillStyle = `rgba(255, 255, 255, ${s.alpha})`;
    ctx.fillRect(s.x, s.y, s.size, s.size);
  }

  // Meteor falling
  if (meteor.alive) {
    meteor.progress += meteor.speed;
    meteor.speed += 0.00045;
    meteor.x = meteor.startX + (meteor.targetX - meteor.startX) * Math.sin(meteor.progress * Math.PI * 0.5);
    meteor.y = meteor.startY + (meteor.targetY - meteor.startY) * (meteor.progress ** 1.35);

    for (let i = 0; i < 7; i++) {
      meteorTrails.push(new MeteorTrail(meteor.x, meteor.y, meteor.radius));
    }

    // Meteor plasma head
    ctx.save();
    let grad = ctx.createRadialGradient(meteor.x, meteor.y, 2, meteor.x, meteor.y, meteor.radius * 2.2);
    grad.addColorStop(0, '#ffffff');
    grad.addColorStop(0.2, '#fef08a');
    grad.addColorStop(0.65, '#f97316');
    grad.addColorStop(1, 'rgba(239, 68, 68, 0)');
    ctx.beginPath();
    ctx.arc(meteor.x, meteor.y, meteor.radius * 2.2, 0, Math.PI * 2);
    ctx.fillStyle = grad;
    ctx.shadowBlur = 40;
    ctx.shadowColor = '#f97316';
    ctx.fill();
    ctx.restore();

    if (meteor.progress >= 1.0) {
      meteor.alive = false;
      triggerRealisticBlast(meteor.targetX, meteor.targetY);
    }
  }

  // Draw meteor trails
  for (let i = meteorTrails.length - 1; i >= 0; i--) {
    let p = meteorTrails[i];
    p.update();
    p.draw(ctx);
    if (p.alpha <= 0) meteorTrails.splice(i, 1);
  }

  // Draw shockwaves
  for (let i = shockwaves.length - 1; i >= 0; i--) {
    let s = shockwaves[i];
    s.update();
    s.draw(ctx);
    if (s.life <= 0) shockwaves.splice(i, 1);
  }

  // Draw volumetric fireballs
  for (let i = blastFireballs.length - 1; i >= 0; i--) {
    let fb = blastFireballs[i];
    fb.update();
    fb.draw(ctx);
    if (fb.life <= 0) blastFireballs.splice(i, 1);
  }

  // Draw incendiary sparks
  for (let i = incendiarySparks.length - 1; i >= 0; i--) {
    let sp = incendiarySparks[i];
    sp.update();
    sp.draw(ctx);
    if (sp.life <= 0) incendiarySparks.splice(i, 1);
  }

  // Ground zero glowing thermal crater
  if (blastOccurred) {
    ctx.save();
    let crater = ctx.createRadialGradient(meteor.targetX, meteor.targetY, 10, meteor.targetX, meteor.targetY, 140);
    crater.addColorStop(0, 'rgba(249, 115, 22, 0.4)');
    crater.addColorStop(0.5, 'rgba(220, 38, 38, 0.2)');
    crater.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.beginPath();
    ctx.arc(meteor.targetX, meteor.targetY, 140, 0, Math.PI * 2);
    ctx.fillStyle = crater;
    ctx.fill();
    ctx.restore();
  }

  animFrame = requestAnimationFrame(animate);
}

requestAnimationFrame(animate);

// 100% ROBUST WAR ROOM TRANSITION HANDLER
function finishIntro() {
  cancelAnimationFrame(animFrame);
  
  // Strategy 1: URL search parameter navigation (supported across all browsers)
  try {
    if (window.top && window.top.location) {
      const topUrl = new URL(window.top.location.href);
      topUrl.searchParams.set('warroom', '1');
      window.top.location.href = topUrl.toString();
      return;
    }
  } catch(e) {}

  // Strategy 2: Direct parent search update
  try {
    if (window.parent && window.parent.location) {
      window.parent.location.search = '?warroom=1';
      return;
    }
  } catch(e) {}

  // Strategy 3: PostMessage event
  window.parent.postMessage({ type: 'streamlit:warroom', entered: true }, '*');
}
</script>
</body>
</html>
"""
    return html_content
