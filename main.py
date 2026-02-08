from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

from db import init_db, get_conn

app = FastAPI()

# CORS برای GitHub Pages شما
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://abouzarnameh.github.io"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/sessions_by_creator")
def sessions_by_creator(creator_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
      SELECT
        s.id,
        s.chat_id,
        s.creator_id,
        s.status,
        s.created_at_ms,
        s.started_at_ms,
        (SELECT COUNT(*) FROM items i WHERE i.session_id = s.id) AS item_count
      FROM sessions s
      WHERE s.creator_id = ?
      ORDER BY s.id DESC
      LIMIT 50
    """, (creator_id,))

    out = [dict(r) for r in cur.fetchall()]
    conn.close()
    return out

@app.on_event("startup")
def startup():
    init_db()

class PendingReq(BaseModel):
    chat_id: int
    creator_id: int

class AddItemReq(BaseModel):
    title: str | None = None
    duration_ms: int
    gap_ms: int | None = 0  # فعلاً اختیاری، پیش‌فرض صفر

@app.post("/session/pending")
def create_or_get_pending(req: PendingReq):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
      SELECT * FROM sessions
      WHERE chat_id=? AND creator_id=? AND status='pending'
      ORDER BY id DESC LIMIT 1
    """, (req.chat_id, req.creator_id))
    row = cur.fetchone()

    if row:
        sid = row["id"]
        conn.close()
        return {"sid": sid}

    now = int(time.time() * 1000)
    cur.execute("""
      INSERT INTO sessions (chat_id, creator_id, status, created_at_ms)
      VALUES (?, ?, 'pending', ?)
    """, (req.chat_id, req.creator_id, now))
    conn.commit()
    sid = cur.lastrowid
    conn.close()
    return {"sid": sid}

@app.post("/session/{sid}/add")
def add_item(sid: int, req: AddItemReq):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM sessions WHERE id=?", (sid,))
    s = cur.fetchone()
    if not s:
        conn.close()
        return {"error": "not_found"}
    if s["status"] != "pending":
        conn.close()
        return {"error": "session_not_pending"}

    cur.execute("SELECT COALESCE(MAX(order_index), -1) AS m FROM items WHERE session_id=?", (sid,))
    m = cur.fetchone()["m"]
    next_order = int(m) + 1

    # اگر خواستی gap رو ذخیره کنی، باید ستون gap_ms رو تو جدول items داشته باشیم.
    # فعلاً اگر ستون نداری، gap_ms رو نادیده می‌گیریم.
    # پیشنهاد: ستون gap_ms اضافه کن. (پایین توضیح دادم)

    try:
        cur.execute("""
          INSERT INTO items (session_id, title, duration_ms, order_index)
          VALUES (?, ?, ?, ?)
        """, (sid, req.title, req.duration_ms, next_order))
    except Exception:
        # اگر بعداً ستون gap_ms اضافه کردی، این INSERT رو عوض کن
        conn.close()
        raise

    conn.commit()
    conn.close()
    return {"ok": True, "order_index": next_order}

@app.post("/session/{sid}/start")
def start_session(sid: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM sessions WHERE id=?", (sid,))
    s = cur.fetchone()
    if not s:
        conn.close()
        return {"error": "not_found"}

    if s["status"] != "pending":
        conn.close()
        return {"error": "not_pending"}

    cur.execute("SELECT COUNT(*) AS c FROM items WHERE session_id=?", (sid,))
    c = cur.fetchone()["c"]
    if c == 0:
        conn.close()
        return {"error": "empty"}

    now = int(time.time() * 1000)
    cur.execute("""
      UPDATE sessions
      SET status='running', started_at_ms=?
      WHERE id=?
    """, (now, sid))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/session")
def get_session(sid: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM sessions WHERE id = ?", (sid,))
    s = cur.fetchone()
    if not s:
        conn.close()
        return {"error": "not_found"}

    cur.execute("SELECT * FROM items WHERE session_id = ? ORDER BY order_index ASC", (sid,))
    items = [dict(r) for r in cur.fetchall()]

    conn.close()
    return {"session": dict(s), "items": items}

