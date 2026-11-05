"""og-unify.py — Add unified og:image to ALL pages pointing to /og-card.svg"""

import os
import re

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
OG_IMAGE = "https://nestgate.io/og-card.svg"
OG_IMAGE_LINE = '    <meta property="og:image" content="%s">\n    <meta property="og:image:width" content="1200">\n    <meta property="og:image:height" content="630">\n    <meta name="twitter:image" content="%s">' % (OG_IMAGE, OG_IMAGE)

updated = 0
already = 0

for filename in sorted(os.listdir(STATIC_DIR)):
    if not filename.endswith(".html"):
        continue
    filepath = os.path.join(STATIC_DIR, filename)
    
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    
    if "og:image" in content:
        print("  SKIP %s (already has og:image)" % filename)
        already += 1
        continue
    
    if "og:title" in content:
        # Insert og:image after og:url or og:title line
        content = content.replace(
            '<meta property="og:site_name"',
            OG_IMAGE_LINE + '\n    <meta property="og:site_name"'
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print("  UNIFIED %s" % filename)
        updated += 1
    else:
        print("  SKIP %s (no OG tags)" % filename)

print()
print("UNIFIED: %d pages with og:image" % updated)
print("ALREADY: %d pages" % already)
