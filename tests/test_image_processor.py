"""Quick smoke test for the image_processor module."""

import sys
sys.path.insert(0, ".")

from website_agents.image_processor import fix_images_in_html

# Test HTML with placeholder images, deprecated unsplash, and duplicates
test_html = """<!DOCTYPE html>
<html>
<head><title>Test</title>
<style>
.hero { background-image: url('https://via.placeholder.com/1920x1080'); }
</style>
</head>
<body>
<section class="hero"></section>
<img src="https://via.placeholder.com/600x400" alt="Product one">
<img src="https://via.placeholder.com/600x400" alt="Product two">
<img src="images/team.jpg" alt="Our team working together">
<img src="https://source.unsplash.com/600x400/?candles&sig=1" alt="Candle display">
<img src="https://source.unsplash.com/600x400/?candles&sig=1" alt="Another candle display">
<img src="https://picsum.photos/seed/42/600/400" alt="Existing picsum image">
<img src="https://picsum.photos/seed/42/600/400" alt="Duplicate picsum image">
<img src="data:image/svg+xml;base64,abc" alt="icon">
</body>
</html>"""

requirements = {
    "business_name": "GlowCraft Studio",
    "business_type": "e-commerce",
    "industry": "candles aromatherapy",
}

fixed = fix_images_in_html(test_html, requirements)

# Verify
import re

# Count unique image URLs
img_urls = re.findall(r'src=["\']([^"\']+)["\']', fixed)
img_urls = [u for u in img_urls if not u.startswith("data:")]
bg_urls = re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", fixed)
bg_urls = [u for u in bg_urls if not u.startswith(("data:", "linear", "radial"))]

all_urls = img_urls + bg_urls
print(f"Total image URLs: {len(all_urls)}")
print(f"Unique image URLs: {len(set(all_urls))}")
print(f"All unique: {len(all_urls) == len(set(all_urls))}")
print()
for i, url in enumerate(all_urls):
    print(f"  [{i+1}] {url}")

# Verify no placeholder URLs remain
has_placeholder = any("placeholder" in u.lower() for u in all_urls)
print(f"\nPlaceholders remaining: {has_placeholder}")

# Verify no local file paths remain
has_local = any(u.startswith("images/") for u in all_urls)
print(f"Local file paths remaining: {has_local}")

# Verify no deprecated unsplash source URLs remain
has_unsplash_source = any("source.unsplash.com" in u for u in all_urls)
print(f"Deprecated unsplash source remaining: {has_unsplash_source}")

# Verify all URLs use picsum
all_picsum = all("picsum.photos" in u for u in all_urls)
print(f"All URLs use picsum.photos: {all_picsum}")

assert not has_placeholder, "ERROR: placeholder URLs still present!"
assert not has_local, "ERROR: local file paths still present!"
assert not has_unsplash_source, "ERROR: deprecated unsplash source URLs still present!"
assert all_picsum, "ERROR: not all URLs use picsum.photos!"
assert len(all_urls) == len(set(all_urls)), "ERROR: duplicate URLs found!"
print("\n[PASS] All tests passed!")
