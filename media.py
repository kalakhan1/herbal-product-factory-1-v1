# =============================================================================
# MEDIA.PY v2.1 — Image attach + WooCommerce push fixes
# =============================================================================
# FIXES:
#   - SlotManager stores media_ids AND media_urls
#   - upload_gallery_to_wp returns both
#   - push_product_via_wc_api uses id OR src (URL) fallback
#   - Better error reporting
# =============================================================================

import os
import io
import re
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, quote_plus

try:
    import requests
except ImportError:
    print("ERROR: requests not installed.")
    raise

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

WORKSPACE = Path.cwd() / "workspace"
IMAGES_DIR = WORKSPACE / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = WORKSPACE / "media.log"

DEFAULT_QUALITY = 80
DEFAULT_METHOD = 6
DEFAULT_SIZE = (1200, 1200)
DEFAULT_ASPECT = "1:1"
DEFAULT_FIT = "cover"

SIZE_PRESETS = {
    "300x300": (300, 300), "600x600": (600, 600), "800x800": (800, 800),
    "1200x630": (1200, 630), "1200x1200": (1200, 1200),
}
ASPECT_PRESETS = {"1:1": (1, 1), "4:3": (4, 3), "16:9": (16, 9), "3:2": (3, 2), "Free": None}
FIT_OPTIONS = ["cover", "contain", "fill", "none", "scale-down"]

REQUEST_TIMEOUT = 20
MAX_DOWNLOAD_BYTES = 15 * 1024 * 1024
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) KhanHerbalFactory/2.0"

MAX_RETRIES = 3
RETRY_BACKOFF = [1, 2, 4]

SLOT_COUNT = 5
FEATURED_SLOT = 0
GALLERY_SLOTS = [1, 2, 3, 4]


# =============================================================================
# SECTION 1 — IMAGE SOURCING
# =============================================================================
def google_images_url(query):
    return f"https://www.google.com/search?q={quote_plus(query)}&tbm=isch"


def openverse_url(query):
    return f"https://openverse.org/search/?q={quote_plus(query)}"


def pexels_url(query):
    return f"https://www.pexels.com/search/{quote_plus(query)}/"


def search_openverse(query, limit=5):
    endpoint = "https://api.openverse.org/v1/images/"
    try:
        r = requests.get(endpoint, params={"q": query, "page_size": limit},
                         timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT})
        if r.status_code != 200: return []
        out = []
        for item in r.json().get("results", []):
            out.append({"thumbnail": item.get("thumbnail"), "url": item.get("url"),
                        "title": item.get("title"), "creator": item.get("creator"),
                        "license": item.get("license"), "source": "openverse"})
        return out
    except Exception as e:
        log_failure("openverse_search", str(e)); return []


def search_pexels(query, api_key, limit=5):
    if not api_key: return []
    try:
        r = requests.get("https://api.pexels.com/v1/search",
                         headers={"Authorization": api_key, "User-Agent": USER_AGENT},
                         params={"query": query, "per_page": limit},
                         timeout=REQUEST_TIMEOUT)
        if r.status_code != 200: return []
        out = []
        for photo in r.json().get("photos", []):
            out.append({"thumbnail": photo.get("src", {}).get("medium"),
                        "url": photo.get("src", {}).get("original"),
                        "title": photo.get("alt"), "creator": photo.get("photographer"),
                        "license": "Pexels License", "source": "pexels"})
        return out
    except Exception as e:
        log_failure("pexels_search", str(e)); return []


def download_from_url(url, save_path=None):
    if not url or not url.startswith(("http://", "https://")):
        return False, "Invalid URL"
    try:
        r = requests.get(url, timeout=REQUEST_TIMEOUT, stream=True,
                         headers={"User-Agent": USER_AGENT})
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        content = b""
        for chunk in r.iter_content(chunk_size=8192):
            content += chunk
            if len(content) > MAX_DOWNLOAD_BYTES:
                return False, "Image exceeds max size"
        if not save_path:
            name = hashlib.md5(url.encode()).hexdigest()[:12] + ".img"
            save_path = str(IMAGES_DIR / name)
        with open(save_path, "wb") as f:
            f.write(content)
        return True, save_path
    except requests.exceptions.RequestException as e:
        return False, f"Network: {str(e)[:120]}"
    except Exception as e:
        return False, f"Error: {str(e)[:120]}"


# =============================================================================
# SECTION 2 — IMAGE PROCESSING
# =============================================================================
def convert_to_webp(src_path, dst_path=None, quality=DEFAULT_QUALITY, method=DEFAULT_METHOD):
    if not PIL_AVAILABLE: return False, "Pillow not installed"
    try:
        img = Image.open(src_path)
    except Exception as e:
        return False, f"Cannot open: {e}"
    if img.mode in ("P", "LA", "L"):
        img = img.convert("RGBA" if "A" in img.mode else "RGB")
    elif img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    if not dst_path:
        dst_path = str(IMAGES_DIR / (Path(src_path).stem + ".webp"))
    try:
        img.save(dst_path, "WEBP", quality=quality, method=method, lossless=False)
        return True, dst_path
    except Exception as e:
        return False, f"WebP save: {e}"


def resize_image(src_path, size, dst_path=None):
    if not PIL_AVAILABLE: return False, "Pillow not installed"
    try:
        img = Image.open(src_path)
        img = img.resize(size, Image.Resampling.LANCZOS)
        if not dst_path:
            dst_path = str(IMAGES_DIR / f"{Path(src_path).stem}_{size[0]}x{size[1]}.webp")
        img.save(dst_path, "WEBP", quality=DEFAULT_QUALITY, method=DEFAULT_METHOD)
        return True, dst_path
    except Exception as e:
        return False, f"Resize: {e}"


def apply_aspect_ratio(src_path, aspect=DEFAULT_ASPECT, dst_path=None):
    if not PIL_AVAILABLE: return False, "Pillow not installed"
    if aspect not in ASPECT_PRESETS or ASPECT_PRESETS[aspect] is None:
        return True, src_path
    try:
        img = Image.open(src_path)
        w, h = img.size
        ar_w, ar_h = ASPECT_PRESETS[aspect]
        target = ar_w / ar_h
        current = w / h
        if current > target:
            new_w = int(h * target)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        elif current < target:
            new_h = int(w / target)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))
        if not dst_path:
            dst_path = str(IMAGES_DIR / f"{Path(src_path).stem}_{aspect.replace(':','x')}.webp")
        img.save(dst_path, "WEBP", quality=DEFAULT_QUALITY, method=DEFAULT_METHOD)
        return True, dst_path
    except Exception as e:
        return False, f"Aspect: {e}"


def process_image_pipeline(src_path, size, aspect=DEFAULT_ASPECT,
                            quality=DEFAULT_QUALITY, method=DEFAULT_METHOD):
    ok, tmp = apply_aspect_ratio(src_path, aspect)
    if not ok: return False, tmp
    ok, resized = resize_image(tmp, size)
    if not ok: return False, resized
    ok, final = convert_to_webp(resized, quality=quality, method=method)
    if not ok: return False, final
    return True, final


def generate_thumbnail(src_path):
    return process_image_pipeline(src_path, (600, 600), "1:1")


# =============================================================================
# SECTION 3 — SLOT MANAGER (with media_ids AND media_urls)
# =============================================================================
class SlotManager:
    def __init__(self, product_name):
        self.product_name = product_name
        self.slots = {i: {"path": None, "url": None, "status": "empty", "attempts": 0}
                      for i in range(SLOT_COUNT)}
        self.media_ids = []     # populated after push to WP
        self.media_urls = []    # populate source_url from WP

    def assign(self, slot, local_path, remote_url=None):
        if slot not in self.slots: return False
        self.slots[slot] = {"path": local_path, "url": remote_url,
                            "status": "ok",
                            "attempts": self.slots[slot].get("attempts", 0) + 1}
        return True

    def mark_failed(self, slot, reason):
        if slot not in self.slots: return
        self.slots[slot]["status"] = "failed"
        self.slots[slot]["attempts"] = self.slots[slot].get("attempts", 0) + 1
        self.slots[slot]["reason"] = reason
        log_failure(f"slot_{slot}", f"{self.product_name}: {reason}")

    def skip(self, slot):
        if slot in self.slots: self.slots[slot]["status"] = "skipped"

    def status(self):
        ok = sum(1 for s in self.slots.values() if s["status"] == "ok")
        failed = sum(1 for s in self.slots.values() if s["status"] == "failed")
        skipped = sum(1 for s in self.slots.values() if s["status"] == "skipped")
        empty = sum(1 for s in self.slots.values() if s["status"] == "empty")
        return {"ok": ok, "failed": failed, "skipped": skipped, "empty": empty,
                "total": SLOT_COUNT, "complete": ok >= 1,
                "ready_for_publish": ok >= 1}

    def featured(self):
        return self.slots[FEATURED_SLOT]["path"]

    def gallery(self):
        return [self.slots[i]["path"] for i in GALLERY_SLOTS if self.slots[i]["path"]]

    def all_paths(self):
        """Return all assigned image paths in order (featured first, then gallery)."""
        paths = []
        if self.featured(): paths.append(self.featured())
        paths.extend(self.gallery())
        return paths

    def failed_slots(self):
        return [i for i, s in self.slots.items() if s["status"] == "failed"]


def retry_slot(sm, slot, url):
    attempts = sm.slots[slot].get("attempts", 0)
    if attempts >= MAX_RETRIES:
        return False, f"Max retries reached ({MAX_RETRIES})"
    for i in range(MAX_RETRIES - attempts):
        time.sleep(RETRY_BACKOFF[min(i, len(RETRY_BACKOFF) - 1)])
        ok, result = download_from_url(url)
        if ok:
            sm.assign(slot, result, url)
            return True, result
        sm.mark_failed(slot, result)
    return False, f"Failed after retries"


def bulk_summary(slot_managers):
    total_slots = len(slot_managers) * SLOT_COUNT
    ok = failed = skipped = empty = 0
    for sm in slot_managers:
        s = sm.status()
        ok += s["ok"]; failed += s["failed"]
        skipped += s["skipped"]; empty += s["empty"]
    return {"products": len(slot_managers), "total_slots": total_slots,
            "ok": ok, "failed": failed, "skipped": skipped, "empty": empty,
            "missing": failed + empty}


# =============================================================================
# SECTION 4 — WORDPRESS MEDIA UPLOAD (returns both IDs and URLs)
# =============================================================================
def upload_media_to_wp(site_url, username, app_password, image_path,
                        filename=None, alt_text=""):
    """
    Upload one image to WordPress Media Library.
    Returns (ok, media_dict_or_none, error)
    media_dict = {"id": int, "source_url": str, "title": str}
    """
    url = f"{site_url.rstrip('/')}/wp-json/wp/v2/media"
    if not filename:
        filename = Path(image_path).name
    try:
        with open(image_path, "rb") as f:
            files = {"file": (filename, f, "image/webp")}
            r = requests.post(url, auth=(username, app_password),
                              files=files, headers={"User-Agent": USER_AGENT},
                              timeout=REQUEST_TIMEOUT)
        if r.status_code not in (200, 201):
            return False, None, f"HTTP {r.status_code}: {r.text[:200]}"
        media = r.json()
        media_id = media.get("id")
        source_url = media.get("source_url", "")
        # Set alt text if provided
        if media_id and alt_text:
            try:
                requests.post(f"{url}/{media_id}", auth=(username, app_password),
                              json={"alt_text": alt_text}, timeout=REQUEST_TIMEOUT)
            except Exception:
                pass
        return True, {"id": media_id, "source_url": source_url,
                      "title": media.get("title", {}).get("rendered", "")}, ""
    except Exception as e:
        return False, None, f"Upload: {str(e)[:200]}"


def upload_gallery_to_wp(site_url, username, app_password, slot_manager, product_name):
    """
    Upload featured + gallery images for one product.
    Returns (ok, media_ids_list, media_urls_list, error)
    """
    media_ids = []
    media_urls = []
    errors = []

    # All images (featured + gallery) in order
    all_paths = slot_manager.all_paths()
    if not all_paths:
        return False, [], [], "No images assigned to slots"

    for i, img_path in enumerate(all_paths):
        role = "featured" if i == 0 else f"gallery-{i}"
        fname = f"{product_name.lower().replace(' ', '-')}-{role}.webp"
        alt = f"{product_name} - {role}" if i > 0 else product_name
        ok, media, err = upload_media_to_wp(
            site_url, username, app_password,
            img_path, filename=fname, alt_text=alt)
        if ok and media and media.get("id"):
            media_ids.append(media["id"])
            media_urls.append(media["source_url"])
        else:
            errors.append(f"{role}: {err}")

    if not media_ids:
        return False, [], [], "; ".join(errors[:3])

    # Save back to slot_manager for later use
    slot_manager.media_ids = media_ids
    slot_manager.media_urls = media_urls

    return True, media_ids, media_urls, ""


# =============================================================================
# SECTION 5 — WOOCOMMERCE PRODUCT PUSH (with image attach fix)
# =============================================================================
def push_product_via_wc_api(site_url, ck, cs, product,
                             media_ids=None, media_urls=None):
    """
    Create one product via WooCommerce REST API with images attached.

    media_ids: list of WP media IDs (preferred)
    media_urls: list of source_url (fallback — WC downloads from URL if ID missing)
    """
    url = f"{site_url.rstrip('/')}/wp-json/wc/v3/products"

    payload = {
        "name": product["name"],
        "slug": product["slug"],
        "type": "simple",
        "status": "draft",
        "sku": product["sku"],
        "regular_price": f"{product['price']:.2f}",
        "description": product["article"]["html"],
        "short_description": (f"{product['name']} is a premium herbal product. "
                              f"Order online with fast delivery across Pakistan."),
        "manage_stock": True,
        "stock_quantity": product["stock"],
        "stock_status": "instock" if product["stock"] > 0 else "outofstock",
        "categories": [{"name": product["category_name"]}],
        "tags": [{"name": product["tag"]}],
        "attributes": [{
            "name": product["attribute"]["name"],
            "options": [product["attribute"]["value"]],
            "visible": True,
            "variation": False,
        }],
        "meta_data": [
            {"key": k.replace("meta:", ""), "value": v}
            for k, v in product["rankmath"].items() if v
        ],
    }

    # Build images array
    images = []
    if media_ids:
        for idx, mid in enumerate(media_ids):
            images.append({"id": mid, "position": idx})
    elif media_urls:
        for idx, u in enumerate(media_urls):
            images.append({"src": u, "position": idx})

    if images:
        payload["images"] = images

    try:
        r = requests.post(url, auth=(ck, cs), json=payload,
                          timeout=REQUEST_TIMEOUT,
                          headers={"User-Agent": USER_AGENT})
        if r.status_code not in (200, 201):
            return False, None, f"HTTP {r.status_code}: {r.text[:250]}"
        data = r.json()
        # Verify images attached
        attached = len(data.get("images", []) or [])
        return True, {**data, "_attached_images": attached}, ""
    except Exception as e:
        return False, None, f"Push: {str(e)[:200]}"


def update_product_stock(site_url, ck, cs, product_id, stock):
    url = f"{site_url.rstrip('/')}/wp-json/wc/v3/products/{product_id}"
    try:
        r = requests.put(url, auth=(ck, cs),
                         json={"stock_quantity": stock, "manage_stock": True,
                               "stock_status": "instock" if stock > 0 else "outofstock"},
                         timeout=REQUEST_TIMEOUT)
        return (r.status_code == 200), ("" if r.status_code == 200 else f"HTTP {r.status_code}")
    except Exception as e:
        return False, str(e)[:200]


def publish_product(site_url, ck, cs, product_id):
    url = f"{site_url.rstrip('/')}/wp-json/wc/v3/products/{product_id}"
    try:
        r = requests.put(url, auth=(ck, cs), json={"status": "publish"},
                         timeout=REQUEST_TIMEOUT)
        return (r.status_code == 200), ("" if r.status_code == 200 else f"HTTP {r.status_code}")
    except Exception as e:
        return False, str(e)[:200]


# =============================================================================
# SECTION 6 — ERROR HANDLING
# =============================================================================
_SECRET_PATTERNS = [
    r"ck_[A-Za-z0-9]{20,}", r"cs_[A-Za-z0-9]{20,}",
    r"(?i)(authorization|bearer|password|secret)\s*[:=]\s*\S+",
]


def redact_secrets(text):
    if not isinstance(text, str): text = str(text)
    out = text
    for pat in _SECRET_PATTERNS:
        out = re.sub(pat, "***REDACTED***", out)
    return out


def log_failure(action, detail):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            stamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{stamp} | {action} | {redact_secrets(detail)}\n")
    except Exception:
        pass


def tail_log(lines=50):
    if not LOG_FILE.exists(): return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
        return [l.rstrip("\n") for l in all_lines[-lines:]]
    except Exception:
        return []


class FailureTracker:
    def __init__(self):
        self.failures = []

    def add(self, product, slot, url, reason):
        self.failures.append({"product": product, "slot": slot, "url": url,
                              "reason": reason, "time": time.strftime("%H:%M:%S")})

    def count(self): return len(self.failures)

    def summary(self):
        by_product = {}
        for f in self.failures:
            by_product.setdefault(f["product"], []).append(f["slot"])
        return {"total": len(self.failures), "by_product": by_product}

    def to_dict(self): return list(self.failures)


def verify_media_exists(site_url, username, app_password, media_id):
    url = f"{site_url.rstrip('/')}/wp-json/wp/v2/media/{media_id}"
    try:
        r = requests.get(url, auth=(username, app_password), timeout=REQUEST_TIMEOUT)
        return r.status_code == 200
    except Exception:
        return False


# =============================================================================
# SECTION 7 — STANDALONE TEST
# =============================================================================
if __name__ == "__main__":
    print("media.py v2.1 loaded")
    print(f"Workspace: {WORKSPACE}")
    print(f"Images:    {IMAGES_DIR}")
    print(f"Sizes:     {list(SIZE_PRESETS.keys())}")
    print(f"Aspects:   {list(ASPECT_PRESETS.keys())}")
    print(f"Fits:      {FIT_OPTIONS}")
    print("Fixed: image attach + media URLs stored on SlotManager")