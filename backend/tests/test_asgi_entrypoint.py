"""
Direct ASGI protocol test for Vercel Serverless Function entrypoint.
Simulates exact Vercel ASGI scope handling without TestClient abstractions.
"""

import asyncio
import os
import sys

# Ensure backend root is current working directory (simulating Vercel root directory = backend)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from main import app


async def test_asgi(path: str):
    response_body = []
    status = [None]
    headers = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        if message["type"] == "http.response.start":
            status[0] = message["status"]
            headers.extend(message.get("headers", []))
        elif message["type"] == "http.response.body":
            response_body.append(message.get("body", b""))

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.1"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "https",
        "path": path,
        "raw_path": path.encode("latin-1"),
        "query_string": b"",
        "headers": [(b"host", b"t20-pressure-api.vercel.app")],
        "server": ("127.0.0.1", 443),
        "client": ("127.0.0.1", 50000),
    }

    await app(scope, receive, send)
    body = b"".join(response_body).decode("utf-8", errors="ignore")
    return status[0], body


async def main():
    endpoints = [
        "/",
        "/docs",
        "/openapi.json",
        "/api/health",
        "/api/overview",
        "/api/rankings/batters",
        "/api/rankings/bowlers",
        "/api/data-audit",
        "/api/model/validation",
    ]

    all_passed = True
    print("\n--- Direct ASGI Protocol Verification ---")
    for ep in endpoints:
        status, body = await test_asgi(ep)
        preview = body.strip().replace("\n", " ")[:60]
        passed = status == 200
        if not passed:
            all_passed = False
        print(f"[{'PASS' if passed else 'FAIL'}] {ep:25} -> {status} | {preview}")

    if not all_passed:
        print("\nERROR: One or more endpoints failed.")
        sys.exit(1)
    else:
        print("\nSUCCESS: All endpoints returned HTTP 200 via direct ASGI protocol.")


if __name__ == "__main__":
    asyncio.run(main())
