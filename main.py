from fastapi import FastAPI
from db import init_db, get_conn
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
origins = [
    "https://abouzarnameh.github.io",   # دامنه GitHub Pages شما
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/sessions")
def get_sessions(chat_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM sessions
    WHERE chat_id = ?
    ORDER BY id DESC
    """, (chat_id,))
    sessions = [dict(r) for r in cur.fetchall()]

    for s in sessions:
        cur.execute("""
        SELECT * FROM items
        WHERE session_id = ?
        ORDER BY order_index ASC
        """, (s["id"],))
        s["items"] = [dict(r) for r in cur.fetchall()]

    conn.close()
    return sessions

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
