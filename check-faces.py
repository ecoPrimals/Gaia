#!/usr/bin/env python3
"""Check all three Klein faces."""
import urllib.request, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for url in ['https://nestgate.io', 'https://out.nestgate.io', 'https://in.nestgate.io']:
    try:
        r = urllib.request.urlopen(url, timeout=8, context=ctx)
        body = r.read().decode()
        title = "no title"
        if "<title>" in body:
            title = body.split("<title>")[1].split("</title>")[0]
        print(f"{url} -> {r.status}")
        print(f"  title: {title}")
        print(f"  size: {len(body)} bytes")
        print(f"  first 150: {body[:150]}")
    except Exception as e:
        print(f"{url} -> {e}")
    print()
