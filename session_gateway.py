from __future__ import annotations

import argparse, asyncio, json, os, subprocess, sys
from aiohttp import ClientSession, WSMsgType, web
from auth.server_session import SESSION_MAX_AGE_SECONDS, session_store

COOKIE_NAME = "cas_student_session"
def _secure() -> bool: return os.getenv("CAS_ENVIRONMENT", "prod").lower() != "local"
def _cookie() -> dict[str, object]: return {"path":"/", "httponly":True, "secure":_secure(), "samesite":"Lax"}
async def complete(request: web.Request) -> web.Response:
    try: ticket = str((await request.json()).get("ticket") or "")
    except (ValueError, json.JSONDecodeError): ticket = ""
    sid = session_store().consume_ticket(ticket) if ticket else None
    if not sid: return web.json_response({"error":"invalid_session_handoff"}, status=401)
    response = web.json_response({"ok":True}); response.set_cookie(COOKIE_NAME, sid, max_age=SESSION_MAX_AGE_SECONDS, **_cookie()); return response
async def clear(request: web.Request) -> web.Response:
    if request.cookies.get(COOKIE_NAME): session_store().revoke(request.cookies[COOKIE_NAME])
    response = web.json_response({"ok":True}); response.del_cookie(COOKIE_NAME, **_cookie()); return response
def _url(request: web.Request) -> str: return f"http://127.0.0.1:{os.getenv('CAS_STREAMLIT_INTERNAL_PORT','8504')}{request.rel_url}"
def _headers(request: web.Request) -> dict[str,str]:
    headers={k:v for k,v in request.headers.items() if k.lower() not in {"host","connection","upgrade","content-length"}}; headers["X-Forwarded-For"]=request.remote or ""; return headers
async def ws_proxy(request: web.Request) -> web.WebSocketResponse:
    client_ws=web.WebSocketResponse(); await client_ws.prepare(request)
    async with ClientSession() as client:
        async with client.ws_connect(_url(request).replace("http://","ws://",1), headers=_headers(request)) as upstream:
            async def up() -> None:
                async for message in upstream:
                    if message.type==WSMsgType.TEXT: await client_ws.send_str(message.data)
                    elif message.type==WSMsgType.BINARY: await client_ws.send_bytes(message.data)
                    else: await client_ws.close(); return
            task=asyncio.create_task(up())
            async for message in client_ws:
                if message.type==WSMsgType.TEXT: await upstream.send_str(message.data)
                elif message.type==WSMsgType.BINARY: await upstream.send_bytes(message.data)
            task.cancel()
    return client_ws
async def proxy(request: web.Request) -> web.StreamResponse:
    if request.headers.get("Upgrade", "").lower()=="websocket": return await ws_proxy(request)
    async with ClientSession() as client:
        async with client.request(request.method, _url(request), headers=_headers(request), data=await request.read(), allow_redirects=False) as upstream:
            response=web.Response(status=upstream.status, body=await upstream.read())
            for k,v in upstream.headers.items():
                if k.lower() not in {"content-length","connection","transfer-encoding"}: response.headers[k]=v
            return response
def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--app",default="main.py"); args=parser.parse_args()
    internal=int(os.getenv("CAS_STREAMLIT_INTERNAL_PORT","8504")); port=int(os.getenv("PORT") or os.getenv("CAS_GATEWAY_PORT","8501"))
    child=subprocess.Popen([sys.executable,"-m","streamlit","run",args.app,"--server.address=127.0.0.1","--server.port",str(internal),"--server.headless=true"])
    app=web.Application(client_max_size=210*1024*1024); app.router.add_post("/_cas/session",complete); app.router.add_delete("/_cas/session",clear); app.router.add_route("*","/{path:.*}",proxy)
    try: web.run_app(app,host="0.0.0.0",port=port)
    finally: child.terminate(); child.wait(timeout=10)
    return 0
if __name__=="__main__": raise SystemExit(main())
