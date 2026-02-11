<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Bomb Base Sync</title>

  <!-- Telegram Mini App SDK -->
  <script src="https://telegram.org/js/telegram-web-app.js"></script>

  <style>
    :root{
      --bd:#e6e6e6; --muted:#6b7280; --danger:#dc2626; --ok:#16a34a;
      --bg:#ffffff; --chip:#f8fafc;
    }
    body{ font-family: sans-serif; padding:14px; margin:0; background:var(--bg); }
    h3{ margin:0 0 8px 0; }
    .muted{ color:var(--muted); font-size:13px; margin:8px 0; line-height:1.7; }
    .row{ display:flex; gap:10px; flex-wrap:wrap; margin:10px 0 14px; }
    .pill{ border:1px solid var(--bd); border-radius:999px; padding:6px 10px; font-size:13px; background:var(--chip); }
    .card{ border:1px solid var(--bd); border-radius:14px; padding:12px; margin:10px 0; }
    .title{ font-weight:800; margin-bottom:8px; display:flex; align-items:center; justify-content:space-between; gap:10px; }
    .badge{ font-size:12px; padding:4px 8px; border-radius:999px; border:1px solid var(--bd); color:#111; background:#fff; }
    .badge.ok{ border-color:#bbf7d0; color:#166534; background:#f0fdf4; }
    .badge.warn{ border-color:#fed7aa; color:#9a3412; background:#fff7ed; }
    .badge.bad{ border-color:#fecaca; color:#991b1b; background:#fef2f2; }
    .time{ font-size:22px; font-weight:900; letter-spacing:0.5px; }
    .sub{ margin-top:8px; color:var(--muted); font-size:13px; display:flex; gap:12px; flex-wrap:wrap; }
    .err{
      border:1px solid #fca5a5; background:#fff1f2; color:#9f1239;
      padding:10px; border-radius:12px; line-height:1.6; margin-top:12px; white-space:pre-wrap;
      display:none;
    }
    .grid{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }
    .grid3{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; }
    label{ font-size:12px; color:var(--muted); display:block; margin-bottom:6px; }
    input, select{
      width:100%; box-sizing:border-box; padding:10px 10px; border-radius:12px;
      border:1px solid var(--bd); outline:none; font-size:14px; background:#fff;
    }
    .btnrow{ display:flex; gap:10px; flex-wrap:wrap; margin-top:10px; }
    .btn{
      padding:10px 12px; border-radius:12px; border:1px solid var(--bd);
      background:#fff; cursor:pointer; font-weight:800;
    }
    .btn.primary{ border-color:#93c5fd; background:#eff6ff; }
    .btn.danger{ border-color:#fecaca; background:#fef2f2; color:#991b1b; }
    .btn:active{ transform:scale(0.99); }
    .small{ font-size:12px; color:var(--muted); }
    .hr{ height:1px; background:var(--bd); margin:12px 0; }
    .mono{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  </style>
</head>

<body>
  <h3>Sync اتک‌ها (Bomb Base)</h3>
  <div class="muted" id="meta">در حال بارگذاری…</div>

  <div class="row" id="chips" style="display:none;">
    <span class="pill" id="chipSid"></span>
    <span class="pill" id="chipStatus"></span>
    <span class="pill" id="chipCount"></span>
  </div>

  <div class="card">
    <div class="title">
      <span>تنظیمات هماهنگی</span>
      <span class="badge" id="syncBadge">—</span>
    </div>

    <div class="grid3">
      <div>
        <label>دیلی سرور (ثانیه)</label>
        <input id="serverDelay" type="number" min="0" step="1" value="3"/>
      </div>
      <div>
        <label>تلورانس هم‌زمانی (ثانیه)</label>
        <input id="syncWindow" type="number" min="0" step="1" value="3"/>
      </div>
      <div>
        <label>فاصله بین اولویت‌ها (ثانیه)</label>
        <input id="gapBetweenPriorities" type="number" min="0" step="1" value="2"/>
      </div>
    </div>

    <div class="grid">
      <div>
        <label>بافر شروع (ثانیه)</label>
        <input id="startBuffer" type="number" min="0" step="1" value="10"/>
        <div class="small">برای اینکه هیچ‌کس لانچ منفی نگیرد (زمان برای آماده شدن).</div>
      </div>
      <div>
        <label>قانون ترتیب برخورد</label>
        <select id="hitOrderMode">
          <option value="priority">بر اساس Priority (Attack #1 اول بخورد)</option>
          <option value="sameHitAll">همه با هم بخورند (Priority فقط نمایش)</option>
        </select>
        <div class="small">در حالت Priority، هر اولویت یک زمان برخورد جدا دارد.</div>
      </div>
    </div>

    <div class="btnrow">
      <button class="btn primary" id="btnStart">شروع سشن (محاسبه لانچ‌ها)</button>
      <button class="btn" id="btnRefresh">رفرش از سرور</button>
      <button class="btn danger" id="btnResetLocal">ریست شروع (فقط همین صفحه)</button>
    </div>

    <div class="small" id="startInfo"></div>
  </div>

  <div class="card">
    <div class="title">
      <span>ثبت اتک جدید</span>
      <span class="badge">درجا به لیست اضافه می‌شود</span>
    </div>

    <div class="grid3">
      <div>
        <label>نام/نوع اتک (مثلاً حسین - 220 Archer)</label>
        <input id="inpTitle" placeholder="مثلاً حسین - 220 Archer"/>
      </div>
      <div>
        <label>زمان مسیر (HH.MM.SS)</label>
        <input id="inpTravel" placeholder="01.21.33" class="mono"/>
      </div>
      <div>
        <label>اولویت برخورد (عدد)</label>
        <input id="inpPriority" type="number" min="1" step="1" value="1"/>
      </div>
    </div>

    <div class="btnrow">
      <button class="btn primary" id="btnAdd">➕ اضافه کردن</button>
      <button class="btn danger" id="btnClear">پاک کردن فیلدها</button>
    </div>

    <div class="small">نکته: Priority یعنی ترتیب برخورد. هرچی عدد کمتر، زودتر بخورد.</div>
  </div>

  <div class="hr"></div>

  <div class="title" style="margin-top:6px;">
    <span>لیست اتک‌ها و زمان لانچ</span>
    <span class="badge" id="clockBadge">—</span>
  </div>

  <div id="list"></div>
  <div id="error" class="err"></div>

  <script>
    // ============================
    // CONFIG
    // ============================
    // اینو روی Render خودت تنظیم کن
    const API_BASE = "https://YOUR-API.onrender.com";

    // ============================
    // Telegram WebApp
    // ============================
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.ready();
      tg.expand?.();
    }

    // ============================
    // Helpers
    // ============================
    function qs(name) {
      const url = new URL(window.location.href);
      return url.searchParams.get(name);
    }

    function showError(text) {
      const el = document.getElementById("error");
      el.style.display = "block";
      el.textContent = text;
    }

    function hideError() {
      const el = document.getElementById("error");
      el.style.display = "none";
      el.textContent = "";
    }

    function setMeta(text) {
      document.getElementById("meta").textContent = text;
    }

    function escapeHtml(str) {
      return String(str ?? "")
        .replaceAll("&","&amp;")
        .replaceAll("<","&lt;")
        .replaceAll(">","&gt;")
        .replaceAll('"',"&quot;")
        .replaceAll("'","&#039;");
    }

    function pad2(n){ return String(n).padStart(2,"0"); }

    function fmtMs(ms) {
      ms = Math.max(0, Math.floor(ms));
      const s = Math.floor(ms / 1000);
      const hh = Math.floor(s / 3600);
      const mm = Math.floor((s % 3600) / 60);
      const ss = s % 60;
      return `${pad2(hh)}.${pad2(mm)}.${pad2(ss)}`;
    }

    // HH.MM.SS -> ms
    function parseTimeToMs(text){
      const t = String(text || "").trim();
      const m = /^(\d{2,})\.(\d{2})\.(\d{2})$/.exec(t);
      if(!m) throw new Error("فرمت زمان مسیر باید HH.MM.SS مثل 01.21.33 باشد");
      const hh = Number(m[1]), mm = Number(m[2]), ss = Number(m[3]);
      if(mm>59 || ss>59) throw new Error("دقیقه و ثانیه باید بین 00 تا 59 باشد");
      const total = hh*3600 + mm*60 + ss;
      if(total<=0) throw new Error("زمان مسیر باید بزرگتر از صفر باشد");
      return total*1000;
    }

    function statusLabel(status) {
      if (status === "pending") return "در انتظار";
      if (status === "running") return "در حال اجرا";
      if (status === "stopped") return "متوقف";
      if (status === "deleted") return "حذف";
      return status || "-";
    }

    function getSettings(){
      const serverDelaySec = Number(document.getElementById("serverDelay").value || 0);
      const syncWindowSec  = Number(document.getElementById("syncWindow").value || 0);
      const gapSec         = Number(document.getElementById("gapBetweenPriorities").value || 0);
      const startBufferSec = Number(document.getElementById("startBuffer").value || 0);
      const mode           = document.getElementById("hitOrderMode").value;
      return {
        serverDelayMs: Math.max(0, serverDelaySec)*1000,
        syncWindowMs:  Math.max(0, syncWindowSec)*1000,
        gapBetweenPrioritiesMs: Math.max(0, gapSec)*1000,
        startBufferMs: Math.max(0, startBufferSec)*1000,
        mode,
      };
    }

    // ============================
    // API calls (robust)
    // ============================
    async function apiGet(path){
      const r = await fetch(`${API_BASE}${path}`, { headers:{ "Accept":"application/json" }});
      if(!r.ok) throw new Error(`API ${r.status} ${r.statusText}`);
      return r.json();
    }

    async function apiPost(path, body){
      const r = await fetch(`${API_BASE}${path}`, {
        method:"POST",
        headers:{ "Content-Type":"application/json", "Accept":"application/json" },
        body: JSON.stringify(body || {}),
      });
      if(!r.ok) throw new Error(`API ${r.status} ${r.statusText}`);
      return r.json();
    }

    async function apiDelete(path){
      const r = await fetch(`${API_BASE}${path}`, { method:"DELETE", headers:{ "Accept":"application/json" }});
      if(!r.ok) throw new Error(`API ${r.status} ${r.statusText}`);
      return r.json();
    }

    // تلاش می‌کنیم از user.id استفاده کنیم (در مینی‌اپ واقعی داخل تلگرام موجوده)
    function getTelegramUserId(){
      return tg?.initDataUnsafe?.user?.id || null;
    }

    // ساخت/گرفتن سشن:
    // 1) اگر sid در URL هست، همونو می‌گیریم
    // 2) اگر نیست، با creator_id یک pending می‌سازیم (pending_simple یا pending)
    async function ensureSessionId(){
      const sidFromUrl = qs("sid");
      if(sidFromUrl) return sidFromUrl;

      const uid = getTelegramUserId();
      if(!uid){
        throw new Error("این صفحه باید داخل تلگرام باز شود تا user.id داشته باشیم (یا sid را در URL بفرستید).");
      }

      // اول pending_simple (اگر در بک‌اندت هست)
      try{
        const a = await apiPost(`/session/pending_simple`, { creator_id: uid });
        if(a?.sid) return String(a.sid);
      }catch(_){}

      // fallback: pending (اگر chat_id لازم دارد، از initDataUnsafe.chat.id می‌گیریم)
      const chatId = tg?.initDataUnsafe?.chat?.id;
      if(!chatId) throw new Error("chat_id پیدا نشد (برای endpoint /session/pending). sid را در URL بفرست یا از pending_simple استفاده کن.");
      const b = await apiPost(`/session/pending`, { chat_id: chatId, creator_id: uid });
      if(!b?.sid) throw new Error("ساخت سشن ناموفق بود");
      return String(b.sid);
    }

    // ============================
    // State
    // ============================
    let sid = null;
    let session = null;
    let items = [];

    // شروع محلی (اگر از بک‌اند started_at_ms نگیری)
    // کلیدش بر اساس sid ذخیره میشه
    function localStartKey(){ return sid ? `bb_sync_started_at_ms_${sid}` : "bb_sync_started_at_ms"; }

    function getLocalStartedAt(){
      const v = localStorage.getItem(localStartKey());
      const n = v ? Number(v) : 0;
      return Number.isFinite(n) && n>0 ? n : 0;
    }

    function setLocalStartedAt(ms){
      localStorage.setItem(localStartKey(), String(ms));
    }

    function clearLocalStartedAt(){
      localStorage.removeItem(localStartKey());
    }

    // ============================
    // Load
    // ============================
    async function load(){
      sid = await ensureSessionId();

      const data = await apiGet(`/session?sid=${encodeURIComponent(sid)}`);
      if(data?.error) throw new Error(`API: ${data.error}`);

      session = data.session || null;
      items = Array.isArray(data.items) ? data.items : [];

      const chatId = tg?.initDataUnsafe?.chat?.id;
      const chatType = tg?.initDataUnsafe?.chat_type;

      setMeta(
        `sid=#${sid} | وضعیت: ${statusLabel(session?.status)}`
        + (chatId ? ` | chat_id: ${chatId}` : "")
        + (chatType ? ` | chat_type: ${chatType}` : "")
      );

      document.getElementById("chips").style.display = "flex";
      document.getElementById("chipSid").textContent = `SID: ${sid}`;
      document.getElementById("chipStatus").textContent = `Status: ${statusLabel(session?.status)}`;
      document.getElementById("chipCount").textContent = `Count: ${items.length}`;
    }

    // ============================
    // Scheduling logic
    // ============================
    function normalizeItem(it){
      // بک‌اندهای مختلف ممکنه فیلدهای مختلف داشته باشن
      const title = it.title ?? it.name ?? "";
      const travelMs = Number(it.duration_ms ?? it.travel_ms ?? 0);
      const priority = Number(it.priority ?? it.order_index ?? 1);
      return {
        raw: it,
        id: it.id ?? it.item_id ?? null,
        title,
        travelMs,
        priority: Number.isFinite(priority) && priority>0 ? priority : 1,
      };
    }

    function computeSchedule(normalized, startedAtMs){
      const st = getSettings();

      // ولیدیشن
      const arr = normalized.filter(x => x.travelMs > 0);
      if(arr.length === 0) return { rows: [], startedAtMs, hitTargetsByPriority: {} };

      // بیشترین زمان مسیر
      const maxTravel = Math.max(...arr.map(x => x.travelMs));

      // زمان برخورد هدف گروه اول:
      // شروع + (maxTravel + بافر)
      const firstHit = startedAtMs + maxTravel + st.startBufferMs;

      // اولویت‌ها
      const priorities = [...new Set(arr.map(x => x.priority))].sort((a,b)=>a-b);

      const hitTargetsByPriority = {};
      if(st.mode === "sameHitAll"){
        // همه با هم بخورن => همه priority ها یک هدف مشترک
        for(const p of priorities) hitTargetsByPriority[p] = firstHit;
      }else{
        // بر اساس اولویت: هر اولویت با فاصله مشخص
        priorities.forEach((p, idx)=>{
          hitTargetsByPriority[p] = firstHit + idx * st.gapBetweenPrioritiesMs;
        });
      }

      // لانچ هر نفر
      const rows = arr.map(x=>{
        const hitTarget = hitTargetsByPriority[x.priority];
        const launchAt = hitTarget - x.travelMs;
        return {
          ...x,
          hitTarget,
          launchAt,
        };
      });

      // برای نمایش “صف لانچ”، بر اساس launchAt مرتب می‌کنیم
      rows.sort((a,b)=>a.launchAt - b.launchAt);

      // اختلاف لانچ با قبلی
      for(let i=0;i<rows.length;i++){
        rows[i].deltaFromPrev = (i===0) ? 0 : (rows[i].launchAt - rows[i-1].launchAt);
      }

      return { rows, startedAtMs, hitTargetsByPriority };
    }

    // وضعیت سشن از کجا بیاد؟
    // 1) اگر session.started_at_ms موجود بود، همونو
    // 2) وگرنه از localStorage
    function effectiveStartedAt(){
      const s = Number(session?.started_at_ms || 0);
      if(s>0) return s;
      return getLocalStartedAt();
    }

    function render(){
      const list = document.getElementById("list");
      const now = Date.now();
      document.getElementById("clockBadge").textContent = `⏱ ${fmtMs(now % (24*3600*1000))}`;

      if(!sid){
        list.innerHTML = `<div class="muted">sid نداریم.</div>`;
        return;
      }
      if(!session){
        list.innerHTML = `<div class="muted">در حال بارگذاری…</div>`;
        return;
      }

      const normalized = items.map(normalizeItem);

      // نمایش badge تلورانس
      const st = getSettings();
      const totalTol = st.serverDelayMs + st.syncWindowMs;
      const badge = document.getElementById("syncBadge");
      badge.textContent = `تلورانس تقریبی برخورد: ${Math.round(totalTol/1000)}s`;
      badge.className = "badge";

      // startedAt
      const startedAtMs = effectiveStartedAt();
      const startInfo = document.getElementById("startInfo");
      if(startedAtMs>0){
        startInfo.textContent = `شروع محاسبات از: ${new Date(startedAtMs).toLocaleString("fa-IR")}`;
      }else{
        startInfo.textContent = "هنوز شروع نشده. روی «شروع سشن» بزن تا لانچ‌ها محاسبه شوند.";
      }

      if(normalized.length === 0){
        list.innerHTML = `<div class="muted">هنوز اتکی ثبت نشده.</div>`;
        return;
      }

      // اگر شروع نشده، فقط لیست خام
      if(startedAtMs<=0){
        const raw = normalized
          .slice()
          .sort((a,b)=>a.priority-b.priority)
          .map((x, idx)=>`
            <div class="card">
              <div class="title">
                <span>#${idx+1} — ${escapeHtml(x.title || "بدون عنوان")}</span>
                <span class="badge">Priority: ${x.priority}</span>
              </div>
              <div class="time">${fmtMs(x.travelMs)}</div>
              <div class="sub">
                <span>Travel: ${fmtMs(x.travelMs)}</span>
                <span>برای دیدن زمان لانچ، شروع سشن را بزن</span>
              </div>
            </div>
          `).join("");
        list.innerHTML = raw;
        return;
      }

      // محاسبه کامل
      const sch = computeSchedule(normalized, startedAtMs);

      // چک تلورانس داخل هر priority: اختلاف برخوردها (با hitTarget های تعریف شده)
      // چون ما دقیق hitTarget می‌دیم، اختلاف تئوری 0 است؛
      // اما برای نمایش، می‌گیم “در پنجره” و تلورانس را نشان می‌دهیم.
      list.innerHTML = sch.rows.map((r, idx)=>{
        const toLaunch = r.launchAt - now;
        const hitAt = r.hitTarget;
        const toHit = hitAt - now;

        // وضعیت لانچ
        let launchBadge = "در صف";
        let bClass = "badge warn";
        if(toLaunch <= 0) { launchBadge = "لانچ شد/بزن!"; bClass="badge ok"; }
        if(toHit <= 0) { launchBadge = "برخورد گذشته"; bClass="badge"; }

        const deltaPrev = r.deltaFromPrev || 0;

        return `
          <div class="card">
            <div class="title">
              <span>#${idx+1} — ${escapeHtml(r.title || "بدون عنوان")}</span>
              <span class="${bClass}">${launchBadge}</span>
            </div>

            <div class="time">${fmtMs(toLaunch)}</div>

            <div class="sub">
              <span>Priority: <b>${r.priority}</b></span>
              <span>Travel: <span class="mono">${fmtMs(r.travelMs)}</span></span>
              <span>Δ لانچ با قبلی: <span class="mono">${fmtMs(deltaPrev)}</span></span>
              <span>تا برخورد: <span class="mono">${fmtMs(toHit)}</span></span>
            </div>

            <div class="sub">
              <span>زمان برخورد هدف: <span class="mono">${new Date(hitAt).toLocaleTimeString("fa-IR")}</span></span>
              <span>زمان لانچ هدف: <span class="mono">${new Date(r.launchAt).toLocaleTimeString("fa-IR")}</span></span>
            </div>

            <div class="btnrow">
              ${r.id ? `<button class="btn danger" onclick="deleteItem(${Number(r.id)})">حذف</button>` : ""}
            </div>
          </div>
        `;
      }).join("");

      hideError();
    }

    // ============================
    // Actions
    // ============================
    async function addAttack(){
      const title = document.getElementById("inpTitle").value.trim();
      const travelText = document.getElementById("inpTravel").value.trim();
      const priority = Number(document.getElementById("inpPriority").value || 1);

      let travelMs = 0;
      try{
        travelMs = parseTimeToMs(travelText);
      }catch(e){
        showError(String(e.message || e));
        return;
      }

      if(!sid){
        showError("sid نداریم");
        return;
      }

      // payload: بک‌اند ممکنه priority رو پشتیبانی نکنه؛
      // پس دو روش:
      // 1) اگر پشتیبانی می‌کند، مستقیم می‌فرستیم
      // 2) اگر نه، داخل title هم encode می‌کنیم که از دست نره
      const payload = {
        title: title || null,
        duration_ms: travelMs,
        priority: Number.isFinite(priority) && priority>0 ? priority : 1,
      };

      try{
        await apiPost(`/session/${encodeURIComponent(sid)}/add`, payload);
      }catch(e){
        // fallback: اگر priority باعث خطا شد، بدون priority بفرست
        try{
          const payload2 = { title: title ? `[P${payload.priority}] ${title}` : `[P${payload.priority}]`, duration_ms: travelMs };
          await apiPost(`/session/${encodeURIComponent(sid)}/add`, payload2);
        }catch(e2){
          showError("خطا در اضافه کردن اتک:\n" + String(e2));
          return;
        }
      }

      await load();
      render();
      hideError();
    }

    async function startSession(){
      if(!sid) return;

      // اگر بک‌اند start دارد، استفاده کن.
      // اگر نداشت یا خطا داد، start محلی.
      try{
        // تلاش: /session/{sid}/start
        await apiPost(`/session/${encodeURIComponent(sid)}/start`, {});
        await load();
        render();
        return;
      }catch(_){}

      // start محلی
      const ms = Date.now();
      setLocalStartedAt(ms);
      await load();
      render();
    }

    async function deleteItem(itemId){
      if(!sid || !itemId) return;
      try{
        // اگر بک‌اند delete این شکلی دارد:
        await apiDelete(`/session/${encodeURIComponent(sid)}/item/${encodeURIComponent(itemId)}`);
      }catch(e){
        showError("حذف آیتم روی سرور پشتیبانی نشد یا خطا داد:\n" + String(e));
        return;
      }
      await load();
      render();
    }

    // ============================
    // Wire up UI
    // ============================
    document.getElementById("btnAdd").addEventListener("click", addAttack);
    document.getElementById("btnStart").addEventListener("click", startSession);
    document.getElementById("btnRefresh").addEventListener("click", async ()=>{ await load(); render(); });
    document.getElementById("btnResetLocal").addEventListener("click", ()=>{ clearLocalStartedAt(); render(); });

    document.getElementById("btnClear").addEventListener("click", ()=>{
      document.getElementById("inpTitle").value = "";
      document.getElementById("inpTravel").value = "";
      document.getElementById("inpPriority").value = "1";
      hideError();
    });

    // هر تغییری در تنظیمات => رندر مجدد
    ["serverDelay","syncWindow","gapBetweenPriorities","startBuffer","hitOrderMode"].forEach(id=>{
      document.getElementById(id).addEventListener("input", render);
      document.getElementById(id).addEventListener("change", render);
    });

    // ============================
    // Boot
    // ============================
    (async ()=>{
      try{
        await load();
        render();

        // رندر لایو
        setInterval(render, 250);

        // سینک سبک با سرور
        setInterval(async ()=>{
          try{ await load(); }catch(_){}
        }, 5000);
      }catch(e){
        showError(
          "خطا در راه‌اندازی:\n" + String(e) +
          "\n\nچک کن:\n" +
          "- API_BASE درست و HTTPS باشد\n" +
          "- صفحه داخل تلگرام باز شده باشد (initData)\n" +
          "- یا sid را داخل URL ارسال کن"
        );
      }
    })();

    // NOTE: deleteItem باید global باشد تا onclick کار کند
    window.deleteItem = deleteItem;
  </script>
</body>
</html>
