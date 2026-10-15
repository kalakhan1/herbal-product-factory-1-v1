# =============================================================================
# KHAN HERBAL STORES — ENGINE v4.4
# =============================================================================
# v4.4 CHANGES:
#   - REMOVED build_schema_jsonld() — WooCommerce + RankMath auto-generate it
#   - REMOVED hidden image placeholder (was adding src="" to HTML)
#   - Article HTML is now CLEAN (no duplicate schema, no broken img tags)
#   - Everything else same as v4.3 (RM 90%, density 1.1-1.5%)
# =============================================================================

import os
import re
import json
import random
import hashlib
from typing import Dict, List, Any, Tuple

from slugify import slugify
from urllib.parse import quote_plus

try:
    from jinja2 import Template
    JINJA = True
except ImportError:
    Template = None
    JINJA = False

random.seed(42)

# =============================================================================
# SECTION 1 — CONSTANTS
# =============================================================================
SITE_URL = "https://darkcyan-turkey-703045.hostingersite.com"
PRODUCT_BASE = "/product/"
CURRENCY_CODE = "PKR"
CURRENCY_SYMBOL = "Rs"
PRICE_MIN = 199
PRICE_MAX = 999
PRODUCT_COUNT = 325

DENSITY_MIN = 1.0
DENSITY_MAX = 1.5
DENSITY_HARD_MAX = 2.5

# =============================================================================
# SECTION 2 — STORE
# =============================================================================
STORE_DEFAULTS = {
    "name":           "Khan Herbal Stores",
    "tagline":        "Authentic Herbal Remedies in Pakistan",
    "description":    "Pakistan's trusted online store for pure, natural and authentic herbal products.",
    "email":          "info@khanherbalstores.com",
    "phone":          "+92 300 0000000",
    "whatsapp":       "+923218224219",
    "address_line1":  "Main Market",
    "address_line2":  "",
    "city":           "Karachi",
    "state":          "Sindh",
    "country":        "PK",
    "postal_code":    "74000",
    "business_hours": "Mon-Sat 9:00 AM - 9:00 PM",
    "facebook":       "",
    "instagram":      "",
    "youtube":        "",
    "twitter":        "",
}

_ACTIVE_STORE = dict(STORE_DEFAULTS)


def set_store(store):
    global _ACTIVE_STORE
    merged = dict(STORE_DEFAULTS)
    merged.update({k: v for k, v in (store or {}).items() if v is not None})
    _ACTIVE_STORE = merged


def get_store():
    return dict(_ACTIVE_STORE)


# =============================================================================
# SECTION 3 — SITE PAGES
# =============================================================================
SITE_PAGES = {
    "home":         {"name": "Home",            "url": f"{SITE_URL}/",                          "anchors": ["Khan Herbal Stores", "our home page", "main store"]},
    "shop":         {"name": "Shop",            "url": f"{SITE_URL}/shop/",                     "anchors": ["shop all products", "browse our collection", "view product range", "explore the full catalog"]},
    "herbs":        {"name": "Natural Herbs",   "url": f"{SITE_URL}/natural-herbs/",            "anchors": ["explore natural herbs", "browse herbal collection", "discover natural remedies", "shop herbal products"]},
    "how_to_shop":  {"name": "How To Shop",     "url": f"{SITE_URL}/how-to-shop/",              "anchors": ["learn how to shop", "read shopping guide", "see ordering steps"]},
    "faqs":         {"name": "FAQs",            "url": f"{SITE_URL}/faqs/",                     "anchors": ["read our FAQs", "find common answers", "view frequently asked questions"]},
    "cart":         {"name": "Cart",            "url": f"{SITE_URL}/cart/",                     "anchors": ["add to your cart", "proceed to checkout", "complete your order"]},
    "shipping":     {"name": "Shipping Policy", "url": f"{SITE_URL}/shipping-delivery-policy/", "anchors": ["check shipping policy", "see delivery options", "view shipping info"]},
    "refund":       {"name": "Refund Policy",   "url": f"{SITE_URL}/refund-returns-policy/",    "anchors": ["read refund policy", "view return policy", "check refund terms"]},
    "about":        {"name": "About Us",        "url": f"{SITE_URL}/about-us/",                 "anchors": ["about Khan Herbal Stores", "learn our story", "know us better"]},
    "contact":      {"name": "Contact Us",      "url": f"{SITE_URL}/contact-us/",               "anchors": ["contact us", "reach out to us", "get in touch"]},
    "account":      {"name": "My Account",      "url": f"{SITE_URL}/my-account/",               "anchors": ["your account", "manage account", "view dashboard"]},
    "tracking":     {"name": "Order Tracking",  "url": f"{SITE_URL}/order-tracking/",           "anchors": ["track your order", "check order status", "order tracking"]},
    "checkout":     {"name": "Checkout",        "url": f"{SITE_URL}/checkout/",                 "anchors": ["secure checkout", "complete payment"]},
    "privacy":      {"name": "Privacy Policy",  "url": f"{SITE_URL}/privacy-policy/",           "anchors": ["privacy policy"]},
    "terms":        {"name": "Terms",           "url": f"{SITE_URL}/terms-conditions/",         "anchors": ["terms & conditions"]},
    "disclaimer":   {"name": "Disclaimer",      "url": f"{SITE_URL}/disclaimer/",               "anchors": ["disclaimer"]},
    "cookie":       {"name": "Cookie Policy",   "url": f"{SITE_URL}/cookie-policy/",            "anchors": ["cookie policy"]},
}

CATEGORIES = {
    "oils":     {"name": "Herbal Oils",         "slug": "herbal-oils"},
    "unani":    {"name": "Unani Medicines",     "slug": "unani-medicines"},
    "syrups":   {"name": "Syrups & Sharbat",    "slug": "syrups-sharbat"},
    "vinegars": {"name": "Vinegars & Sirka",    "slug": "vinegars-sirka"},
    "herbs":    {"name": "Herbs & Botanicals",  "slug": "herbs-botanicals"},
    "powders":  {"name": "Powders & Tablets",   "slug": "powders-tablets"},
}

TAG_RULES = [
    ("oil", "herbal-oil"), ("vinegar", "herbal-vinegar"), ("syrup", "herbal-syrup"),
    ("majun", "unani-majun"), ("khamira", "khamira"), ("itrifal", "itrifal"),
    ("jawarish", "jawarish"), ("laboob", "laboob"), ("seed", "herbal-seeds"),
    ("leaves", "herbal-leaves"), ("flower", "herbal-flowers"), ("bark", "herbal-bark"),
    ("root", "herbal-root"), ("safoof", "safoof"), ("kushta", "kushta"),
]

ATTRIBUTE_PRESETS = {
    "oils":     {"name": "Volume",    "options": ["100ml", "200ml", "500ml"]},
    "syrups":   {"name": "Volume",    "options": ["200ml", "500ml", "1000ml"]},
    "vinegars": {"name": "Volume",    "options": ["250ml", "500ml", "1000ml"]},
    "herbs":    {"name": "Weight",    "options": ["100g", "250g", "500g", "1kg"]},
    "unani":    {"name": "Pack Size", "options": ["125g", "250g", "500g"]},
    "powders":  {"name": "Weight",    "options": ["50g", "100g", "250g"]},
}

USE_CASE_KEYWORDS = {
    "hair":        ["hair", "bhringraj", "amla", "castor", "almond", "coconut", "hibiscus", "malkangni"],
    "skin":        ["skin", "neem", "aloe", "sandalwood", "turmeric", "multani", "babchi", "chamomile"],
    "digestive":   ["digest", "jawarish", "itrifal", "hing", "sonth", "ajwain", "kamooni", "halila"],
    "immunity":    ["immunity", "shilajit", "ashwagandha", "giloy", "tulsi", "mulethi"],
    "respiratory": ["throat", "cough", "mulethi", "banafsha", "tulsi", "sual", "sandal"],
    "wellness":    ["wellness", "health", "vitality", "strength", "energy", "tonic"],
}

KEYWORD_MODIFIERS = {
    "long_tail":     ["best", "pure", "organic", "natural", "premium", "cold-pressed", "authentic"],
    "short_tail":    ["buy", "shop", "online", "price"],
    "navigational":  ["near me", "online store", "official site", "in pakistan"],
    "informational": ["benefits", "uses", "how to use", "for hair", "for skin", "side effects"],
    "transactional": ["buy online", "order now", "free delivery", "cash on delivery", "cod"],
    "commercial":    ["best brand", "top quality", "review", "price in pakistan", "wholesale"],
}


# =============================================================================
# SECTION 4 — SYNONYMS
# =============================================================================
SYNONYMS = {
    "herbal": ["botanical", "plant-based", "natural", "organic", "herb-based"],
    "natural": ["pure", "authentic", "traditional", "genuine", "unadulterated"],
    "beneficial": ["helpful", "useful", "advantageous", "valuable", "rewarding"],
    "excellent": ["outstanding", "superb", "remarkable", "exceptional", "top-tier"],
    "use": ["apply", "utilize", "employ", "incorporate", "leverage"],
    "product": ["item", "offering", "solution", "remedy", "preparation"],
    "quality": ["grade", "standard", "caliber", "excellence", "craftsmanship"],
    "traditional": ["time-honored", "age-old", "classical", "heritage", "ancestral"],
    "effective": ["potent", "powerful", "efficient", "reliable", "proven"],
    "pure": ["unadulterated", "clean", "authentic", "refined", "unmixed"],
    "trusted": ["reliable", "dependable", "proven", "established", "reputed"],
    "carefully": ["meticulously", "precisely", "attentively", "thoughtfully", "expertly"],
    "sourced": ["obtained", "procured", "selected", "acquired", "harvested"],
    "processed": ["prepared", "manufactured", "formulated", "crafted", "developed"],
    "preserve": ["retain", "maintain", "keep", "safeguard", "protect"],
    "potency": ["strength", "efficacy", "power", "vigor", "intensity"],
    "support": ["assist", "aid", "enhance", "promote", "facilitate"],
    "wellness": ["health", "wellbeing", "vitality", "fitness", "balance"],
    "journey": ["path", "route", "process", "experience", "transition"],
    "solutions": ["options", "remedies", "alternatives", "approaches", "methods"],
    "customers": ["buyers", "clients", "users", "patrons", "shoppers"],
    "rely": ["depend", "trust", "count on", "lean on", "bank on"],
    "deliver": ["provide", "supply", "offer", "give", "present"],
    "premium": ["high-end", "top-grade", "superior", "exclusive", "elite"],
    "consistent": ["steady", "stable", "uniform", "reliable", "dependable"],
    "ingredients": ["components", "elements", "substances", "materials", "contents"],
    "growers": ["farmers", "cultivators", "producers", "harvesters", "suppliers"],
    "strict": ["rigorous", "stringent", "tight", "careful", "disciplined"],
    "control": ["management", "oversight", "supervision", "regulation", "monitoring"],
    "measures": ["steps", "methods", "actions", "procedures", "practices"],
    "variety": ["range", "selection", "assortment", "collection", "diversity"],
    "formula": ["recipe", "composition", "blend", "mixture", "preparation"],
    "remedy": ["treatment", "cure", "solution", "medicine", "therapy"],
    "centuries": ["generations", "decades", "ages", "eras", "long periods"],
    "authentic": ["genuine", "real", "true", "verified", "legitimate"],
    "routine": ["regimen", "habit", "practice", "schedule", "pattern"],
    "results": ["outcomes", "effects", "benefits", "consequences", "returns"],
    "experience": ["undergo", "feel", "enjoy", "encounter", "realize"],
    "explore": ["discover", "examine", "investigate", "consider", "survey"],
    "health": ["wellbeing", "vitality", "fitness", "condition", "state"],
    "vitamins": ["nutrients", "minerals", "supplements", "essentials", "elements"],
    "regular": ["consistent", "routine", "steady", "ongoing", "continuous"],
    "usage": ["application", "consumption", "intake", "utilization", "administration"],
    "directions": ["instructions", "guidelines", "recommendations", "protocols", "steps"],
    "container": ["bottle", "jar", "pack", "package", "vessel"],
    "freshness": ["quality", "newness", "vitality", "potency", "integrity"],
    "convenience": ["ease", "simplicity", "accessibility", "comfort", "usability"],
    "versatile": ["adaptable", "flexible", "multipurpose", "all-purpose", "multi-use"],
    "genuine": ["authentic", "real", "true", "legitimate", "certified"],
    "crafted": ["made", "created", "produced", "developed", "formed"],
    "extracted": ["obtained", "derived", "collected", "harvested", "procured"],
    "blend": ["mixture", "combination", "fusion", "mix", "amalgam"],
    "fresh": ["new", "recent", "unused", "vibrant", "vivid"],
    "nourish": ["feed", "strengthen", "fortify", "sustain", "nurture"],
    "restore": ["renew", "revitalize", "revive", "replenish", "refresh"],
    "enhance": ["improve", "boost", "increase", "elevate", "strengthen"],
    "nurture": ["care for", "nourish", "support", "tend", "cultivate"],
    "protect": ["shield", "guard", "defend", "safeguard", "preserve"],
    "balance": ["harmonize", "stabilize", "regulate", "align", "equilibrate"],
    "rejuvenate": ["refresh", "revitalize", "restore", "renew", "reinvigorate"],
}


# =============================================================================
# SECTION 5 — TEMPLATES
# =============================================================================
INTRO_OPENERS = [
    "Discover the timeless benefits of", "Experience the remarkable power of",
    "Unlock the natural potential of", "Trust the tradition behind",
    "Choose the purity of", "Embrace the goodness of",
]
INTRO_CONNECTORS = [
    "one of the most trusted herbal preparations in traditional Unani and Ayurvedic medicine.",
    "a premium herbal remedy carefully sourced from trusted cultivators.",
    "an authentic wellness solution refined through time-honored methods.",
    "a highly regarded botanical formula used for generations across South Asia.",
    "a natural herbal product valued for its consistent and reliable results.",
]
INTRO_CLOSERS = [
    "Thousands of customers trust it for its beneficial properties and dependable performance.",
    "Our store delivers authentic herbal products right to your doorstep with fast shipping.",
    "Every batch is quality-checked to ensure maximum potency and freshness.",
    "Whether you are new to herbal wellness or a long-time user, it delivers consistent results.",
    "It is the ideal choice for anyone seeking authentic herbal solutions for daily wellbeing.",
]


# =============================================================================
# SECTION 6 — KEYWORD ENGINE
# =============================================================================
def slugify_product(name):
    return slugify(name, lowercase=True)[:75].strip("-")


def base_keyword(product_name):
    return re.sub(r"\([^)]*\)", "", product_name.lower()).strip()


def get_use_case(product_name):
    base = base_keyword(product_name)
    for uc, words in USE_CASE_KEYWORDS.items():
        if any(w in base for w in words):
            return uc
    return "wellness"


def generate_focus_keyword(product_name):
    return f"{base_keyword(product_name)} for {get_use_case(product_name)}"


def generate_long_tail_keywords(p, count=5):
    return [f"{m} {base_keyword(p)}" for m in KEYWORD_MODIFIERS["long_tail"][:count]]


def generate_short_tail_keywords(p, count=4):
    return [f"{m} {base_keyword(p)}" for m in KEYWORD_MODIFIERS["short_tail"][:count]]


def generate_navigational_keywords(p, count=3):
    return [f"{base_keyword(p)} {m}" for m in KEYWORD_MODIFIERS["navigational"][:count]]


def generate_informational_keywords(p, count=4):
    return [f"{base_keyword(p)} {m}" for m in KEYWORD_MODIFIERS["informational"][:count]]


def generate_transactional_keywords(p, count=4):
    return [f"{base_keyword(p)} {m}" for m in KEYWORD_MODIFIERS["transactional"][:count]]


def generate_commercial_keywords(p, count=4):
    return [f"{m} {base_keyword(p)}" for m in KEYWORD_MODIFIERS["commercial"][:count]]


def generate_semantic_keywords(product_name, count=8):
    cat = guess_category(product_name)
    pool = [
        "herbal remedies", "natural wellness", "ayurvedic medicine",
        "unani treatment", "traditional healing", "organic skincare",
        "hair care", "skin care", "digestive health", "immunity booster",
        "natural oils", "pure herbs", "cold pressed", "no preservatives",
    ]
    if cat == "oils":
        pool += ["cold pressed oil", "carrier oil", "massage oil", "hair oil"]
    elif cat == "syrups":
        pool += ["herbal syrup", "natural tonic", "sharbat", "immunity syrup"]
    elif cat == "vinegars":
        pool += ["apple cider vinegar", "herbal vinegar", "natural vinegar"]
    elif cat == "herbs":
        pool += ["dried herbs", "herbal powder", "botanical ingredients"]
    r = random.Random(hash(product_name) % 10000)
    r.shuffle(pool)
    return pool[:count]


def generate_all_keywords(product_name):
    return {
        "focus":         generate_focus_keyword(product_name),
        "long_tail":     generate_long_tail_keywords(product_name),
        "short_tail":    generate_short_tail_keywords(product_name),
        "navigational":  generate_navigational_keywords(product_name),
        "informational": generate_informational_keywords(product_name),
        "transactional": generate_transactional_keywords(product_name),
        "commercial":    generate_commercial_keywords(product_name),
        "semantic":      generate_semantic_keywords(product_name),
    }


def calculate_keyword_density(text, keyword):
    if not text or not keyword: return 0.0
    text_lower = text.lower()
    total_words = len(re.findall(r"\b\w+\b", text_lower))
    if total_words == 0: return 0.0
    kw_count = text_lower.count(keyword.lower())
    kw_words = len(keyword.split())
    return round((kw_count * kw_words / total_words) * 100, 2)


def count_keyword(text, keyword):
    return text.lower().count(keyword.lower())


def guess_category(product_name):
    n = product_name.lower()
    if "oil" in n: return "oils"
    if "vinegar" in n: return "vinegars"
    if "syrup" in n or "sharbat" in n: return "syrups"
    if any(k in n for k in ["majun", "khamira", "itrifal", "jawarish", "laboob"]): return "unani"
    if any(k in n for k in ["safoof", "kushta"]) or n.endswith(" hab"): return "powders"
    return "herbs"


def _syn(word, variant=0):
    if word.lower() in SYNONYMS:
        pool = SYNONYMS[word.lower()]
        return pool[variant % len(pool)]
    return word


# =============================================================================
# SECTION 7 — STORE HELPERS
# =============================================================================
def build_brand_link():
    s = get_store()
    return f'<a href="{SITE_PAGES["home"]["url"]}">{s["name"]}</a>'


def build_product_cta_block(product_name, product_url):
    """Build a CTA block with WhatsApp button + store brand info."""
    s = get_store()
    wa_number = re.sub(r"[^\d]", "", s.get("whatsapp", "") or "")
    if not wa_number:
        wa_number = "923218224219"
    message = (
        f"Assalam-o-Alaikum! I am interested in {product_name}. "
        f"Please share more details and pricing. "
        f"Product link: {product_url}"
    )
    wa_link = f"https://wa.me/{wa_number}?text={quote_plus(message)}"
    brand = s["name"]
    home_url = SITE_PAGES["home"]["url"]
    return (
        '<div class="product-cta" style="margin:24px 0;padding:20px;'
        'background:linear-gradient(135deg,#f1f8e9,#e8f5e9);border-radius:10px;'
        'border-left:4px solid #2e7d32;">'
        f'<p style="margin:0 0 12px 0;font-size:15px;color:#1b5e20;">'
        f'<strong>Buy {product_name} from '
        f'<a href="{home_url}" style="color:#2e7d32;text-decoration:none;'
        f'font-weight:700;">{brand}</a></strong>'
        f' — Pakistan&#39;s trusted online store for authentic herbal products.'
        f'</p>'
        f'<a href="{wa_link}" target="_blank" rel="noopener" '
        f'style="display:inline-block;background:#25D366;color:#fff;'
        f'padding:12px 24px;border-radius:8px;text-decoration:none;'
        f'font-weight:700;font-size:15px;'
        f'box-shadow:0 2px 6px rgba(37,211,102,0.4);">'
        f'&#128172; Order on WhatsApp</a>'
        f'<span style="margin-left:12px;font-size:12px;color:#666;">'
        f'Ask about <strong>{product_name}</strong> — fast reply</span>'
        '</div>'
    )


# =============================================================================
# SECTION 8 — CONTENT BUILDERS
# =============================================================================
def _build_intro(product_name, kw, cat, rng):
    opener = rng.choice(INTRO_OPENERS)
    connector = rng.choice(INTRO_CONNECTORS)
    closer = rng.choice(INTRO_CLOSERS)
    v = rng.randint(0, 4)
    s = get_store()
    cat_text = {
        "oils": "herbal oil", "syrups": "herbal syrup", "vinegars": "herbal vinegar",
        "herbs": "herbal botanical", "unani": "Unani preparation", "powders": "herbal formulation",
    }.get(cat, "herbal product")

    return (
        f"<strong>{product_name}</strong> is {connector} "
        f"If you have been searching for the best <strong>{kw}</strong> in Pakistan, "
        f"you are in the right place. {opener} {product_name} — a "
        f"{_syn('natural', v)} {cat_text} that supports your {_syn('wellness', v)} "
        f"journey with {_syn('consistent', v)} results. Whether you want authentic "
        f"{_syn('herbal', v)} remedies or are simply exploring options, this product "
        f"delivers {_syn('premium', v)} {_syn('quality', v)} in every use. Available "
        f"exclusively at {s['name']}. {closer}"
    )


def _build_what_is(product_name, kw, cat, rng):
    v = rng.randint(0, 4)
    cat_text = {
        "oils": f"{product_name} is a cold-pressed or traditionally extracted herbal oil used for hair care, skin care, and therapeutic massage.",
        "syrups": f"{product_name} is a herbal syrup (sharbat) prepared from natural ingredients, commonly used for cooling, digestion, and general wellness.",
        "vinegars": f"{product_name} is a naturally fermented vinegar infused with herbal goodness, traditionally used for digestive and metabolic support.",
        "herbs": f"{product_name} is a dried botanical product sourced from premium herbs, used in teas, poultices, and traditional remedies.",
        "unani": f"{product_name} is a classical Unani preparation made from a blend of herbs, spices, and natural ingredients following traditional formulas.",
        "powders": f"{product_name} is a finely processed powder formulation used in traditional medicine for specific wellness needs.",
    }.get(cat, f"{product_name} is a premium herbal product.")

    return (
        f"{cat_text} It has been used for {_syn('centuries', v)} across South Asia "
        f"and the Middle East as part of traditional healing systems. The product "
        f"retains its {_syn('natural', v)} properties through {_syn('carefully', v)} "
        f"{_syn('sourced', v)} ingredients and traditional {_syn('processed', v)} "
        f"methods, ensuring maximum {_syn('potency', v)} with every use. Unlike "
        f"synthetic alternatives, it works gently with your body's natural systems. "
        f"Whether you are a long-time user of {_syn('herbal', v)} remedies or just "
        f"beginning your {_syn('wellness', v)} journey, this product offers a "
        f"{_syn('reliable', v)}, {_syn('traditional', v)} solution. Each package is "
        f"designed to {_syn('preserve', v)} freshness and {_syn('potency', v)}, so "
        f"what reaches you is exactly what nature intended. It is an ideal choice "
        f"for anyone seeking a {_syn('genuine', v)} botanical solution."
    )


def _build_benefits(product_name, kw, cat, rng):
    v = rng.randint(0, 4)
    intro = (
        f"{product_name} offers a wide range of advantages that make it a staple "
        f"in many homes across Pakistan. When used consistently, it supports "
        f"multiple aspects of health and {_syn('wellness', v)}. Below are the key "
        f"benefits of choosing this {_syn('traditional', v)} {_syn('remedy', v)} "
        f"for your daily {_syn('routine', v)}."
    )
    benefit_pairs = [
        ("Hair Care Support",
         "Rich in nutrients that strengthen hair roots, promote natural growth, "
         "and reduce hair fall. Regular use nourishes the scalp and adds visible "
         "shine to dull hair."),
        ("Skin Wellness",
         "Helps improve skin texture, reduce dryness, and maintain a healthy glow. "
         "The natural compounds support hydration and elasticity without harsh chemicals."),
        ("Digestive Balance",
         "Supports healthy digestion, soothes the stomach, and helps maintain gut "
         "balance when used as directed. A trusted choice for daily wellness."),
        ("Immunity Support",
         "Contains natural antioxidants that help strengthen the body's defenses "
         "and promote overall vitality. Ideal for seasonal wellness routines."),
        ("Quality Assurance",
         "Free from artificial colors, synthetic fragrances, and harmful "
         "preservatives. Every batch is tested for purity, potency, and freshness."),
        ("Value & Convenience",
         "Offered at a fair price with cash on delivery available across Pakistan. "
         "Fast shipping ensures you receive your order quickly and in perfect condition."),
    ]
    rng.shuffle(benefit_pairs)
    parts = []
    for title, text in benefit_pairs[:6]:
        parts.append(f"<h3>{product_name} for {title}</h3>\n<p>{text}</p>")
    return intro, "\n".join(parts)


def _build_how_to_use(product_name, cat, rng):
    v = rng.randint(0, 4)
    usage = {
        "oils": "Apply a small quantity to the desired area and massage gently in circular motions. For hair, use 2–3 times a week before washing. For skin, apply daily after bathing.",
        "syrups": "Take 1–2 teaspoons (5–10ml) twice daily after meals, or as directed by a healthcare practitioner. Shake well before use. Mix with water or milk for taste.",
        "vinegars": "Mix 1–2 teaspoons in a glass of warm water and consume once or twice daily, preferably before meals. Can also be used in salads and cooking. Not for children under 12.",
        "herbs": "Use 1–2 teaspoons in hot water to make a herbal tea. Alternatively, add to warm milk with honey. For topical use, mix with a little water to form a paste.",
        "unani": "Take the recommended dosage (usually 5–10g) once or twice daily with water or milk, or as prescribed by a Unani practitioner. Best consumed after meals.",
        "powders": "Take 1–2 teaspoons (or as directed) with water, honey, or milk. For best results, consume consistently for 4–6 weeks without skipping days.",
    }.get(cat, "Use as directed by a qualified practitioner.")

    return (
        f"{usage} For best results, maintain a consistent schedule and follow the "
        f"recommended {_syn('directions', v)}. Many customers notice visible "
        f"improvements within 4–6 weeks of regular use. {product_name} is gentle "
        f"enough for daily application yet {_syn('effective', v)} enough to deliver "
        f"noticeable changes. Always store the product in a cool, dry place away "
        f"from direct sunlight. Keep the {_syn('container', v)} tightly closed after "
        f"each use to {_syn('preserve', v)} {_syn('freshness', v)}. Consult a "
        f"healthcare professional before use if you are pregnant, nursing, or taking "
        f"medication. Keep out of reach of children. For any questions about usage "
        f"or dosage, please reach out through our website — our team is happy to "
        f"guide you on the best way to use this product."
    )


def _build_storage_safety(product_name, rng):
    v = rng.randint(0, 4)
    return (
        f"To ensure {product_name} retains its {_syn('potency', v)} and "
        f"{_syn('freshness', v)} for as long as possible, store it in a cool, dry "
        f"place away from direct sunlight and heat sources. Keep the container "
        f"tightly sealed after each use to prevent contamination and oxidation. "
        f"Avoid contact with water inside the container. Do not refrigerate unless "
        f"specifically instructed on the label. Keep away from children and pets. "
        f"If you have sensitive skin, perform a patch test before first use. "
        f"Consult a qualified healthcare practitioner before using this product if "
        f"you are pregnant, nursing, taking prescription medication, or have any "
        f"pre-existing medical condition. This product is not intended to diagnose, "
        f"treat, cure, or prevent any disease. Individual results may vary based on "
        f"body type, lifestyle, and consistency of use."
    )


def _build_ingredients(product_name, cat, rng):
    v = rng.randint(0, 4)
    return (
        f"At our store, {product_name} is prepared using the finest "
        f"{_syn('natural', v)} {_syn('ingredients', v)} sourced from trusted "
        f"{_syn('growers', v)}. We follow {_syn('strict', v)} {_syn('quality', v)} "
        f"{_syn('control', v)} {_syn('measures', v)} at every stage — from harvest "
        f"to packaging. No artificial colors, synthetic fragrances, or harmful "
        f"preservatives are added. Every batch is tested for purity and "
        f"{_syn('potency', v)}, ensuring that what you receive is exactly what "
        f"nature intended. Our commitment to authenticity means you can trust "
        f"every drop that reaches your doorstep. This {_syn('traditional', v)} "
        f"{_syn('product', v)} reflects our dedication to providing genuine "
        f"{_syn('herbal', v)} {_syn('solutions', v)} to {_syn('customers', v)} "
        f"across Pakistan. We believe in transparency, which is why all our "
        f"products come with a clear ingredient list and usage instructions."
    )


def _build_faq(product_name, kw, cat):
    faqs = [
        (f"What is {product_name} used for?",
         f"{product_name} is traditionally used for overall wellness, hair care, "
         f"skin health, digestion, and immunity support. Always follow the "
         f"recommended dosage or usage instructions for best results."),
        (f"Is {product_name} safe for daily use?",
         f"Yes, when taken or applied as directed. If you are pregnant, nursing, "
         f"or on medication, consult a doctor before use. Our quality-tested "
         f"formula ensures consistent safety across batches."),
        (f"How long until I see results?",
         f"Most users notice visible improvements within 4–6 weeks of consistent "
         f"use. Results vary by individual, so we recommend completing at least "
         f"one full cycle for best assessment."),
        (f"Where can I buy {product_name} online in Pakistan?",
         f"You can order directly from our online store with fast delivery and "
         f"cash on delivery available across Pakistan."),
    ]
    html = ""
    for q, a in faqs:
        html += f"<h3>{q}</h3>\n<p>{a}</p>\n"
    return html


def _build_conclusion(product_name, rng, kw):
    v = rng.randint(0, 4)
    s = get_store()
    brand_link = build_brand_link()
    return (
        f"<strong>{product_name}</strong> is more than just a {_syn('product', v)} — "
        f"it is a {_syn('traditional', v)} {_syn('remedy', v)} that connects you to "
        f"generations of {_syn('herbal', v)} wisdom. If you have been searching for "
        f"<strong>{kw}</strong>, we deliver {_syn('quality', v)} you can trust. "
        f"{s['name']} offers authentic {product_name} with fast shipping across "
        f"Pakistan. Visit {brand_link} to explore our full range of herbal products. "
        f"Order today and experience the difference. Our team is always available to "
        f"answer your questions and help you choose the right herbal solution for "
        f"your needs."
    )


ARTICLE_TEMPLATE = """<h1>{title}</h1>

<p>{intro}</p>

<h2>What is {product_name}?</h2>
<p>{what_is}</p>

<h2>Key Benefits</h2>
<p>{benefits_intro}</p>
{benefits_list}

<h2>How to Use {product_name}</h2>
<p>{how_to_use}</p>

<h2>Storage &amp; Safety Guidelines</h2>
<p>{storage_safety}</p>

<h2>Ingredients &amp; Quality</h2>
<p>{ingredients}</p>

<h2>Frequently Asked Questions</h2>
{faq_html}

<h2>Final Thoughts</h2>
<p>{conclusion}</p>

{product_cta}

{related_products_html}
"""


# =============================================================================
# SECTION 9 — DENSITY / DUPLICATE
# =============================================================================
def _strip_html(html): return re.sub(r"<[^>]+>", " ", html)


def enforce_density(html, product_name, kw):
    plain = _strip_html(html)
    density = calculate_keyword_density(plain, kw)
    count = count_keyword(plain, kw)
    return html, {"density": density, "occurrences": count,
                  "in_range": DENSITY_MIN <= density <= DENSITY_MAX,
                  "safe": density <= DENSITY_HARD_MAX}


def _ngrams(text, n=5):
    words = re.findall(r"\b\w+\b", text.lower())
    if len(words) < n: return set()
    return {tuple(words[i:i+n]) for i in range(len(words) - n + 1)}


def _jaccard(a, b):
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)


def _article_plain(product, max_words=200):
    html = product.get("article", {}).get("html", "")
    return " ".join(_strip_html(html).split()[:max_words])


def compute_uniqueness_report(products, sample_size=30):
    total = len(products)
    if total < 2:
        return {"products_checked": total, "pairs_checked": 0,
                "avg_similarity": 0.0, "max_similarity": 0.0, "high_similarity_pairs": []}
    rng = random.Random(12345)
    pairs_to_check = min(sample_size, total * (total - 1) // 2)
    fps = {i: _ngrams(_article_plain(products[i]), n=5) for i in range(total)}
    sims, high = [], []
    seen = set()
    for _ in range(pairs_to_check):
        i, j = rng.sample(range(total), 2)
        key = tuple(sorted([i, j]))
        if key in seen: continue
        seen.add(key)
        s = _jaccard(fps[i], fps[j])
        sims.append(s)
        if s > 0.35:
            high.append({"p1": products[i]["name"], "p2": products[j]["name"],
                         "similarity": round(s*100, 1)})
    if not sims:
        return {"products_checked": total, "pairs_checked": 0,
                "avg_similarity": 0.0, "max_similarity": 0.0, "high_similarity_pairs": []}
    return {"products_checked": total, "pairs_checked": len(sims),
            "avg_similarity": round(sum(sims)/len(sims)*100, 1),
            "max_similarity": round(max(sims)*100, 1),
            "high_similarity_pairs": high[:10]}


# =============================================================================
# SECTION 10 — SEO ENGINE
# =============================================================================
def generate_seo_title(product_name, focus_kw):
    s = get_store()
    brand = s["name"]
    candidates = [
        f"{focus_kw.title()} | Buy Online in Pakistan",
        f"{product_name} — {focus_kw.title()}",
        f"{product_name} | {brand}",
        f"Buy {product_name} Online | {brand}",
    ]
    for c in candidates:
        if len(c) <= 60: return c
    return f"{product_name[:35]} | {brand}"[:60]


def generate_meta_description(product_name, focus_kw):
    s = get_store()
    brand = s["name"]
    templates = [
        f"Shop {product_name} at {brand} — {focus_kw}. 100% pure, natural & authentic. Fast delivery across Pakistan. Order now with COD.",
        f"Buy {product_name} online at {brand}. {focus_kw.capitalize()}. Premium quality, free delivery on bulk orders across Pakistan.",
        f"{product_name} for {focus_kw} — available at {brand}. Natural, authentic, quality-tested. Order today with fast & reliable delivery.",
    ]
    for t in templates:
        if 140 <= len(t) <= 160: return t
    best = min(templates, key=lambda x: abs(len(x) - 155))
    return best[:160]


def generate_canonical_url(product_name):
    return f"{SITE_URL}{PRODUCT_BASE}{slugify_product(product_name)}/"


def calculate_rankmath_score(meta, article):
    score = 0
    kw = meta.get("focus_keyword", "").lower()
    product_name = meta.get("product_name", "")
    title = meta.get("meta:rank_math_title", "").lower()
    desc = meta.get("meta:rank_math_description", "").lower()
    url = meta.get("meta:rank_math_canonical_url", "")
    html = article.get("html", "")
    html_lower = html.lower()
    plain = _strip_html(html).lower()

    if kw and kw in title: score += 10
    if kw and kw in desc: score += 10
    if product_name and slugify_product(product_name) in url: score += 5
    if kw and kw in plain[:600]: score += 10

    d = article.get("keyword_density", 0)
    if 1.0 <= d <= 1.5: score += 10
    elif 0.5 <= d <= 2.0: score += 6

    wc = article.get("word_count", 0)
    if wc >= 800: score += 10
    elif wc >= 600: score += 5

    if 40 <= len(title) <= 60: score += 5
    if 140 <= len(desc) <= 160: score += 5
    if kw and kw in html_lower: score += 5

    if html.count("<a href=") >= 5: score += 10
    elif html.count("<a href=") >= 1: score += 5

    if 'alt="' in html: score += 3
    if url and len(url) < 75: score += 5

    h_all = re.findall(r"<h[12][^>]*>(.*?)</h[12]>", html_lower, re.S)
    if any(kw in h for h in h_all): score += 2

    return min(score, 100)


# =============================================================================
# SECTION 11 — RANKMATH META
# =============================================================================
def build_rankmath_meta(product_name, focus_kw=None):
    if focus_kw is None:
        focus_kw = generate_focus_keyword(product_name)
    seo_title = generate_seo_title(product_name, focus_kw)
    meta_desc = generate_meta_description(product_name, focus_kw)
    canonical = generate_canonical_url(product_name)
    robots = 'a:2:{i:0;s:5:"index";i:1;s:6:"follow";}'
    return {
        "meta:rank_math_focus_keyword":         focus_kw,
        "meta:rank_math_title":                 seo_title,
        "meta:rank_math_description":           meta_desc,
        "meta:rank_math_robots":                robots,
        "meta:rank_math_canonical_url":         canonical,
        "meta:rank_math_facebook_title":        seo_title,
        "meta:rank_math_facebook_description":  meta_desc,
        "meta:rank_math_twitter_title":         seo_title,
        "meta:rank_math_twitter_description":   meta_desc,
        "meta:rank_math_advanced_robots":       "",
    }


# =============================================================================
# SECTION 12 — INTERNAL LINKS
# =============================================================================
_RELATED_CACHE = {}
_ALL_PRODUCTS = []


def set_product_universe(products):
    global _ALL_PRODUCTS, _RELATED_CACHE
    _ALL_PRODUCTS = list(products)
    _RELATED_CACHE = {}


def _same_category_score(p1, p2):
    return 3 if guess_category(p1) == guess_category(p2) else 0


def _word_overlap_score(p1, p2):
    w1 = set(re.findall(r"\b\w+\b", p1.lower()))
    w2 = set(re.findall(r"\b\w+\b", p2.lower()))
    w1.discard("oil"); w2.discard("oil")
    return len(w1 & w2)


def _use_case_score(p1, p2):
    s = 0
    for uc, words in USE_CASE_KEYWORDS.items():
        if any(w in p1.lower() for w in words) and any(w in p2.lower() for w in words):
            s += 2
    return s


def find_related_products(product_name, top_n=4):
    if not _ALL_PRODUCTS: return []
    if product_name in _RELATED_CACHE: return _RELATED_CACHE[product_name]
    scores = []
    for other in _ALL_PRODUCTS:
        if other == product_name: continue
        s = (_same_category_score(product_name, other) * 2
             + _word_overlap_score(product_name, other) * 3
             + _use_case_score(product_name, other) * 2)
        scores.append((other, s))
    scores.sort(key=lambda x: -x[1])
    related = [n for n, _ in scores[:top_n]]
    _RELATED_CACHE[product_name] = related
    return related


def product_url(product_name):
    return f"{SITE_URL}{PRODUCT_BASE}{slugify_product(product_name)}/"


def build_product_link(product_name, anchor=None):
    return f'<a href="{product_url(product_name)}">{anchor or product_name}</a>'


def build_page_link(page_key, anchor=None):
    if page_key not in SITE_PAGES: return ""
    page = SITE_PAGES[page_key]
    if anchor is None:
        anchor = random.choice(page["anchors"])
    return f'<a href="{page["url"]}">{anchor}</a>'


def build_internal_links_html(product_name):
    seed = int(hashlib.md5(product_name.encode()).hexdigest(), 16)
    rng = random.Random(seed)
    s = get_store()
    pages = ["shop", "herbs", "how_to_shop", "faqs", "cart", "shipping", "refund"]
    rng.shuffle(pages)

    home_link = f'<p>Browse the complete collection at {build_brand_link()}.</p>'
    intro_link = f'<p>Explore our full {build_page_link(pages[0])} collection today.</p>'
    benefits_link = f'<p>You can browse more options in our {build_page_link(pages[1])} category.</p>'
    how_to_use_link = f'<p>New to herbal products? Read our {build_page_link("how_to_shop", "shopping guide")}.</p>'
    conclusion_link = (f'<p><a href="{SITE_PAGES["shop"]["url"]}">'
                       f'<strong>Order {product_name} now</strong></a> '
                       f'from {s["name"]} with fast delivery across Pakistan.</p>')
    contact_link = f'<p>Questions? <a href="{SITE_PAGES["contact"]["url"]}">Contact us</a> anytime.</p>'

    related = find_related_products(product_name, top_n=4)
    related_items = [f"<li>{build_product_link(rp)}</li>" for rp in related]
    related_html = ""
    if related_items:
        related_html = "<h2>Related Herbal Products</h2>\n<ul>\n" + "\n".join(related_items) + "\n</ul>"

    return {"home_link": home_link, "intro_link": intro_link,
            "benefits_link": benefits_link, "how_to_use_link": how_to_use_link,
            "conclusion_link": conclusion_link, "contact_link": contact_link,
            "related_products_html": related_html}


# =============================================================================
# SECTION 13 — ARTICLE ASSEMBLY
# =============================================================================
def generate_article(product_name, keywords=None):
    if keywords is None:
        keywords = generate_all_keywords(product_name)

    kw = keywords["focus"]
    cat = guess_category(product_name)
    use_case = get_use_case(product_name)
    seed = int(hashlib.md5(product_name.encode()).hexdigest(), 16) % 2**31
    rng = random.Random(seed)

    title = f"{product_name} for {use_case.title()} — Complete Guide"

    intro = _build_intro(product_name, kw, cat, rng)
    what_is = _build_what_is(product_name, kw, cat, rng)
    benefits_intro, benefits_list = _build_benefits(product_name, kw, cat, rng)
    how_to_use = _build_how_to_use(product_name, cat, rng)
    storage_safety = _build_storage_safety(product_name, rng)
    ingredients = _build_ingredients(product_name, cat, rng)
    faq_html = _build_faq(product_name, kw, cat)
    conclusion = _build_conclusion(product_name, rng, kw)
    product_cta = build_product_cta_block(product_name, product_url(product_name))

    links = build_internal_links_html(product_name)
    intro = intro + " " + links["intro_link"]
    benefits_intro = benefits_intro + " " + links["benefits_link"]
    how_to_use = how_to_use + " " + links["how_to_use_link"] + " " + links["contact_link"]

    html = ARTICLE_TEMPLATE.format(
        title=title, product_name=product_name, intro=intro,
        what_is=what_is, benefits_intro=benefits_intro,
        benefits_list=benefits_list, how_to_use=how_to_use,
        storage_safety=storage_safety, ingredients=ingredients,
        faq_html=faq_html, conclusion=conclusion,
        product_cta=product_cta,
        related_products_html=links["related_products_html"],
    )

    html, density_report = enforce_density(html, product_name, kw)

    plain = _strip_html(html)
    word_count = len(re.findall(r"\b\w+\b", plain))
    density = calculate_keyword_density(plain, kw)
    occurrences = count_keyword(plain, kw)

    return {"html": html, "word_count": word_count,
            "keyword_density": density, "keyword_occurrences": occurrences,
            "density_in_range": density_report["in_range"],
            "focus_keyword": kw, "variant_used": seed % 10}


# =============================================================================
# SECTION 14 — PRODUCT BUILDER
# =============================================================================
def assign_category(product_name):
    key = guess_category(product_name)
    return {"key": key, "name": CATEGORIES[key]["name"], "slug": CATEGORIES[key]["slug"]}


def assign_tag(product_name):
    n = product_name.lower()
    for keyword, tag in TAG_RULES:
        if keyword in n: return tag
    return "herbal-products"


def assign_attribute(product_name):
    cat = guess_category(product_name)
    preset = ATTRIBUTE_PRESETS.get(cat, {"name": "Size", "options": ["Standard"]})
    return {"name": preset["name"], "value": preset["options"][0],
            "visible": True, "variation": False}


def generate_sku(index): return f"HERB-{index + 1:03d}"


def generate_price(product_name):
    seed = int(hashlib.md5(product_name.encode()).hexdigest(), 16)
    rng = random.Random(seed)
    return round(rng.uniform(PRICE_MIN, PRICE_MAX), 2)


def assign_stock(index, total, in_stock_count=10):
    return random.choice([5, 10, 15, 20, 25]) if index < in_stock_count else 0


def build_product_dict(product_name, index, total):
    keywords = generate_all_keywords(product_name)
    article = generate_article(product_name, keywords)
    rankmath = build_rankmath_meta(product_name, keywords["focus"])
    category = assign_category(product_name)
    tag = assign_tag(product_name)
    attribute = assign_attribute(product_name)
    sku = generate_sku(index)
    slug = slugify_product(product_name)
    price = generate_price(product_name)
    stock = assign_stock(index, total)

    # Schema generation REMOVED — WooCommerce + RankMath handle it.

    score = calculate_rankmath_score(
        {**rankmath, "focus_keyword": keywords["focus"],
         "product_name": product_name},
        article)

    return {
        "index": index + 1, "name": product_name, "slug": slug, "sku": sku,
        "price": price, "stock": stock,
        "stock_status": "instock" if stock > 0 else "outofstock",
        "category_key": category["key"], "category_name": category["name"],
        "category_slug": category["slug"], "tag": tag, "attribute": attribute,
        "keywords": keywords, "article": article,
        "rankmath": rankmath, "rankmath_score": score,
        "canonical_url": generate_canonical_url(product_name),
        "product_url": product_url(product_name),
    }


def build_all_products(products):
    set_product_universe(products)
    return [build_product_dict(name, i, len(products)) for i, name in enumerate(products)]


# =============================================================================
# SECTION 15 — CSV BUILDER
# =============================================================================
WOO_COLUMNS_BASE = [
    "ID", "Type", "SKU", "Name", "Published", "Is featured?", "Visibility in catalog",
    "Short description", "Description", "Date sale price starts", "Date sale price ends",
    "Tax status", "Tax class", "In stock?", "Stock", "Low stock amount",
    "Backorders allowed?", "Sold individually?", "Weight (kg)", "Length (cm)",
    "Width (cm)", "Height (cm)", "Allow customer reviews?", "Purchase note",
    "Sale price", "Regular price", "Categories", "Tags", "Shipping class",
    "Images", "Download limit", "Download expiry days", "Parent",
    "Grouped products", "Upsells", "Cross-sells", "External URL", "Button text",
    "Position", "Attribute 1 name", "Attribute 1 value(s)", "Attribute 1 visible",
    "Attribute 1 global",
]


def build_csv_row(product, image_urls=None):
    s = get_store()
    short_desc = (f"{product['name']} from {s['name']} — a premium herbal product "
                  f"sourced from trusted growers, processed to preserve natural "
                  f"potency. Order online in Pakistan with fast delivery.")
    return {
        "ID": "", "Type": "simple", "SKU": product["sku"], "Name": product["name"],
        "Published": "1", "Is featured?": "0", "Visibility in catalog": "visible",
        "Short description": short_desc, "Description": product["article"]["html"],
        "Date sale price starts": "", "Date sale price ends": "",
        "Tax status": "taxable", "Tax class": "",
        "In stock?": "1" if product["stock"] > 0 else "0",
        "Stock": str(product["stock"]), "Low stock amount": "5",
        "Backorders allowed?": "0", "Sold individually?": "0",
        "Weight (kg)": "0.5", "Length (cm)": "", "Width (cm)": "", "Height (cm)": "",
        "Allow customer reviews?": "1", "Purchase note": "",
        "Sale price": "", "Regular price": f"{product['price']:.2f}",
        "Categories": product["category_name"], "Tags": product["tag"],
        "Shipping class": "",
        "Images": ",".join(image_urls) if image_urls else "",
        "Download limit": "", "Download expiry days": "", "Parent": "",
        "Grouped products": "", "Upsells": "", "Cross-sells": "",
        "External URL": "", "Button text": "", "Position": str(product["index"]),
        "Attribute 1 name": product["attribute"]["name"],
        "Attribute 1 value(s)": product["attribute"]["value"],
        "Attribute 1 visible": "1", "Attribute 1 global": "0",
        **product["rankmath"],
    }


def build_csv_data(products, image_map=None):
    if image_map is None: image_map = {}
    all_cols = list(WOO_COLUMNS_BASE)
    if products:
        for k in products[0]["rankmath"].keys():
            if k not in all_cols: all_cols.append(k)
    rows = []
    for p in products:
        row = build_csv_row(p, image_map.get(p["name"], []))
        for c in all_cols: row.setdefault(c, "")
        rows.append(row)
    return all_cols, rows


# =============================================================================
# SECTION 16 — ARCHIVE CSS
# =============================================================================
ARCHIVE_CSS = """/* Khan Herbal Stores — Archive Cards */
:root{--hcw:280px;--hch:440px;--hih:280px;--hth:48px;--hph:40px;--hbh:44px;--hg:20px;--hr:8px}
ul.products{display:grid!important;grid-template-columns:repeat(4,1fr);gap:var(--hg);list-style:none;padding:0;margin:0}
ul.products li.product{width:100%!important;height:var(--hch);margin:0!important;border-radius:var(--hr);
  box-shadow:0 2px 8px rgba(0,0,0,.08);background:#fff;overflow:hidden;display:flex;flex-direction:column;
  transition:transform .2s}
ul.products li.product:hover{transform:translateY(-4px)}
ul.products li.product img{width:100%;height:var(--hih);object-fit:cover;object-position:center}
ul.products li.product .woocommerce-loop-product__title{height:var(--hth);font-size:15px;
  padding:8px 12px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
  line-height:1.4}
ul.products li.product .price{height:var(--hph);line-height:var(--hph);font-size:17px;
  font-weight:700;color:#2e7d32;padding:0 12px}
ul.products li.product .button{height:var(--hbh);line-height:var(--hbh);margin:auto 12px 12px;
  background:#2e7d32;color:#fff;border-radius:6px;text-align:center;font-weight:600;text-decoration:none}
@media(max-width:1200px){ul.products{grid-template-columns:repeat(3,1fr)}}
@media(max-width:992px){ul.products{grid-template-columns:repeat(2,1fr)}}
@media(max-width:576px){ul.products{grid-template-columns:1fr}}
"""


def get_archive_css(): return ARCHIVE_CSS


def save_archive_css(path="archive-consistency.css"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(ARCHIVE_CSS)
    return path


# =============================================================================
# SECTION 17 — REPORTS
# =============================================================================
def summarize_scores(products):
    if not products:
        return {"count": 0, "avg": 0, "min": 0, "max": 0, "passing": 0, "failing": 0}
    scores = [p.get("rankmath_score", 0) for p in products]
    return {"count": len(scores), "avg": round(sum(scores)/len(scores), 2),
            "min": min(scores), "max": max(scores),
            "passing": sum(1 for s in scores if s >= 70),
            "failing": sum(1 for s in scores if s < 70)}


def summarize_density(products):
    if not products:
        return {"avg_density": 0, "in_range": 0, "too_high": 0, "too_low": 0}
    d = [p["article"].get("keyword_density", 0) for p in products]
    return {"avg_density": round(sum(d)/len(d), 2),
            "in_range": sum(1 for x in d if DENSITY_MIN <= x <= DENSITY_MAX),
            "too_high": sum(1 for x in d if x > DENSITY_MAX),
            "too_low": sum(1 for x in d if x < DENSITY_MIN)}


def summarize_wordcount(products):
    if not products:
        return {"avg_words": 0, "min_words": 0, "max_words": 0, "under_800": 0}
    c = [p["article"].get("word_count", 0) for p in products]
    return {"avg_words": round(sum(c)/len(c)), "min_words": min(c), "max_words": max(c),
            "under_800": sum(1 for x in c if x < 800)}


def full_report(products):
    return {"scores": summarize_scores(products),
            "density": summarize_density(products),
            "wordcount": summarize_wordcount(products),
            "uniqueness": compute_uniqueness_report(products)}


def preview_product(product):
    a = product["article"]
    return (f"[{product['index']:03d}] {product['name']}\n"
            f"  SKU: {product['sku']}  Slug: {product['slug']}\n"
            f"  Price: Rs {product['price']:.2f}  Category: {product['category_name']}\n"
            f"  Focus KW: {product['keywords']['focus']}\n"
            f"  Words: {a['word_count']}  Density: {a['keyword_density']}%  "
            f"Occurrences: {a.get('keyword_occurrences', 0)}\n"
            f"  RM Score: {product['rankmath_score']}%\n")


# =============================================================================
# SECTION 18 — TEST
# =============================================================================
if __name__ == "__main__":
    set_store({
        "name": "Khan Herbal Stores",
        "email": "info@khanherbalstores.com",
        "phone": "+92 300 1234567",
        "whatsapp": "+92 300 1234567",
        "address_line1": "Shop 12, Main Market",
        "city": "Karachi", "state": "Sindh", "postal_code": "74000",
        "business_hours": "Mon-Sat 9am-9pm",
    })
    demo = ["Almond Oil", "Black Seed Oil", "Olive Oil",
            "Coconut Oil", "Mustard Oil", "Neem Oil",
            "Amla Oil", "Castor Oil", "Sesame Oil", "Bhringraj Oil"]
    products = build_all_products(demo)
    for p in products[:3]:
        print(preview_product(p))
        print("-" * 60)
    rep = full_report(products)
    print("Scores:     ", rep["scores"])
    print("Density:    ", rep["density"])
    print("Word count: ", rep["wordcount"])
    print("Uniqueness: ", rep["uniqueness"])
    # Verify no schema is present
    assert "application/ld+json" not in products[0]["article"]["html"], "Schema still present!"
    assert '<img src=""' not in products[0]["article"]["html"], "Hidden img still present!"
    print("\n✅ Schema removed, no broken img tags")