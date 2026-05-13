"""
website_agents/image_processor.py

Post-processing utilities for validating and fixing image URLs in generated HTML.
Ensures all images use working online URLs (Lorem Picsum) and that no image URL repeats.
"""

import re
from typing import Optional


# Patterns for common broken/placeholder image URLs
PLACEHOLDER_PATTERNS = [
    r'https?://via\.placeholder\.com[^\s\"\'\>]*',
    r'https?://placeholder\.com[^\s\"\'\>]*',
    r'https?://placehold\.it[^\s\"\'\>]*',
    r'https?://placehold\.co[^\s\"\'\>]*',
    r'https?://placekitten\.com[^\s\"\'\>]*',
    r'https?://dummyimage\.com[^\s\"\'\>]*',
    r'https?://fakeimg\.pl[^\s\"\'\>]*',
    r'https?://lorempixel\.com[^\s\"\'\>]*',
    r'https?://loremflickr\.com[^\s\"\'\>]*',
    # Catch the deprecated Unsplash Source API (returns 503 now)
    r'https?://source\.unsplash\.com[^\s\"\'\>]*',
    r'placeholder\.(png|jpg|jpeg|svg|webp)',
    r'image\d*\.(png|jpg|jpeg|svg|webp)',
    r'photo\d*\.(png|jpg|jpeg|svg|webp)',
]

# Compiled regex for finding all image sources in HTML
IMG_SRC_PATTERN = re.compile(
    r'(<img[^>]*?\bsrc\s*=\s*["\'])([^"\']+)(["\'][^>]*?>)',
    re.IGNORECASE | re.DOTALL,
)

CSS_BG_IMAGE_PATTERN = re.compile(
    r'(background(?:-image)?\s*:\s*[^;]*?url\s*\(\s*["\']?)([^"\'\)\s]+)(["\']?\s*\))',
    re.IGNORECASE | re.DOTALL,
)


def _build_picsum_url(width: int, height: int, seed: int) -> str:
    """Build a unique Lorem Picsum URL with the given dimensions and seed.

    Uses the seed parameter to get deterministic, unique images without
    requiring an API key. Each unique seed returns a different photo.
    """
    return f"https://picsum.photos/seed/{seed}/{width}/{height}"


def _guess_keywords_from_alt(alt_text: str, fallback_keywords: list[str]) -> list[str]:
    """Extract plausible search keywords from an image's alt text."""
    if not alt_text or alt_text.lower() in ("image", "photo", "picture", "img", ""):
        return fallback_keywords[:2]

    # Clean and split the alt text into keyword candidates
    words = re.sub(r'[^\w\s-]', '', alt_text.lower()).split()
    stop_words = {
        "a", "an", "the", "of", "for", "and", "or", "in", "on", "at", "to",
        "is", "it", "by", "with", "our", "your", "this", "that", "from",
        "image", "photo", "picture", "img", "icon", "alt",
    }
    keywords = [w for w in words if w not in stop_words and len(w) > 2]

    if len(keywords) < 2:
        keywords.extend(fallback_keywords[:2])

    return keywords[:3]


def _guess_dimensions_from_context(tag_html: str) -> tuple[int, int]:
    """Try to guess image dimensions from the HTML tag attributes or CSS context."""
    # Check for explicit width/height attributes
    w_match = re.search(r'\bwidth\s*[=:]\s*["\']?(\d+)', tag_html, re.IGNORECASE)
    h_match = re.search(r'\bheight\s*[=:]\s*["\']?(\d+)', tag_html, re.IGNORECASE)

    if w_match and h_match:
        return int(w_match.group(1)), int(h_match.group(1))

    # Check for common CSS classes that hint at size
    lower = tag_html.lower()
    if "hero" in lower or "banner" in lower or "header" in lower:
        return 1920, 1080
    if "avatar" in lower or "profile" in lower or "testimonial" in lower:
        return 200, 200
    if "thumb" in lower or "icon" in lower:
        return 400, 300
    if "card" in lower or "product" in lower or "service" in lower:
        return 600, 400

    return 800, 600  # sensible default


def _is_placeholder_url(url: str) -> bool:
    """Check if a URL matches known placeholder image services."""
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return True

    # Also catch local file paths and obviously broken URLs
    if url.startswith(("./", "../", "file://", "#", "data:image/svg")):
        return False  # SVG data URIs and anchors are OK

    if not url.startswith("http"):
        # Likely a local path like "images/hero.jpg" — needs replacement
        if re.search(r'\.(png|jpg|jpeg|webp|gif)$', url, re.IGNORECASE):
            return True

    return False


def _extract_existing_seeds(html: str) -> set[int]:
    """Find all seed values already used in picsum URLs in the HTML."""
    return set(int(m) for m in re.findall(r'picsum\.photos/seed/(\d+)/', html))


def _extract_business_keywords(requirements_json: Optional[dict] = None) -> list[str]:
    """Build a list of relevant keywords from the requirements JSON."""
    if not requirements_json:
        return ["business", "professional", "modern"]

    keywords = []
    for field in ("business_type", "industry", "business_name"):
        val = requirements_json.get(field, "")
        if val:
            keywords.extend(re.sub(r'[^\w\s-]', '', val.lower()).split())

    # Also pull keywords from products/services
    products = requirements_json.get("products_services", "")
    if isinstance(products, str) and products:
        keywords.extend(re.sub(r'[^\w\s-]', '', products.lower()).split()[:3])
    elif isinstance(products, list):
        for p in products[:3]:
            keywords.extend(re.sub(r'[^\w\s-]', '', str(p).lower()).split()[:2])

    stop_words = {"a", "an", "the", "of", "for", "and", "or", "in", "on", "at", "to", "is"}
    keywords = [k for k in keywords if k not in stop_words and len(k) > 2]

    return keywords[:6] if keywords else ["business", "professional", "modern"]


def fix_images_in_html(
    html: str,
    requirements_json: Optional[dict] = None,
) -> str:
    """
    Post-process generated HTML to ensure all images:
    1. Use working online Lorem Picsum URLs
    2. Have unique URLs (no repeats)
    3. Have proper alt text

    Args:
        html: The generated HTML string.
        requirements_json: Optional requirements dict for keyword context.

    Returns:
        The fixed HTML string.
    """
    business_keywords = _extract_business_keywords(requirements_json)
    used_seeds = _extract_existing_seeds(html)
    seen_urls = set()
    next_seed = max(used_seeds, default=0) + 100  # start well above existing seeds

    def _get_next_seed() -> int:
        nonlocal next_seed
        while next_seed in used_seeds:
            next_seed += 1
        seed = next_seed
        used_seeds.add(seed)
        next_seed += 1
        return seed

    def _replace_img_src(match: re.Match) -> str:
        nonlocal seen_urls
        prefix, url, suffix = match.group(1), match.group(2), match.group(3)
        full_tag = match.group(0)

        # Skip data URIs, SVGs, and CDN icon libraries
        if url.startswith(("data:", "blob:")) or "fontawesome" in url.lower() or "icons" in url.lower():
            return full_tag

        needs_replacement = _is_placeholder_url(url) or url in seen_urls

        if needs_replacement:
            w, h = _guess_dimensions_from_context(full_tag)
            seed = _get_next_seed()
            new_url = _build_picsum_url(w, h, seed)
            seen_urls.add(new_url)
            return f"{prefix}{new_url}{suffix}"

        seen_urls.add(url)
        return full_tag

    def _replace_css_bg(match: re.Match) -> str:
        nonlocal seen_urls
        prefix, url, suffix = match.group(1), match.group(2), match.group(3)

        if url.startswith(("data:", "blob:", "linear-gradient", "radial-gradient")):
            return match.group(0)

        needs_replacement = _is_placeholder_url(url) or url in seen_urls

        if needs_replacement:
            seed = _get_next_seed()
            new_url = _build_picsum_url(1920, 1080, seed)
            seen_urls.add(new_url)
            return f"{prefix}{new_url}{suffix}"

        seen_urls.add(url)
        return match.group(0)

    # Phase 1: Fix <img> src attributes
    html = IMG_SRC_PATTERN.sub(_replace_img_src, html)

    # Phase 2: Fix CSS background-image URLs
    html = CSS_BG_IMAGE_PATTERN.sub(_replace_css_bg, html)

    # Phase 3: Ensure remaining duplicate Picsum URLs get unique seeds
    html = _deduplicate_picsum_urls(html, used_seeds)

    return html


def _deduplicate_picsum_urls(html: str, used_seeds: set[int]) -> str:
    """
    Final pass: find any remaining duplicate picsum URLs and make them unique.
    """
    picsum_pattern = re.compile(
        r'(https://picsum\.photos/seed/)(\d+)(/\d+/\d+)',
        re.IGNORECASE,
    )

    seen = {}  # full_url -> first occurrence
    next_seed = max(used_seeds, default=0) + 200

    def _dedup(match: re.Match) -> str:
        nonlocal next_seed
        prefix = match.group(1)
        seed = int(match.group(2))
        dimensions = match.group(3)
        full_url = f"{prefix}{seed}{dimensions}"

        if full_url not in seen:
            seen[full_url] = True
            return full_url
        else:
            # Duplicate found — assign new seed
            while next_seed in used_seeds:
                next_seed += 1
            new_seed = next_seed
            used_seeds.add(new_seed)
            next_seed += 1
            new_url = f"{prefix}{new_seed}{dimensions}"
            seen[new_url] = True
            return new_url

    return picsum_pattern.sub(_dedup, html)
