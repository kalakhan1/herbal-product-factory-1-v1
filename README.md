# 🌿 Khan Herbal Stores — Web Factory

> **Complete product factory for herbal e-commerce stores.**
> Generate 325 products with SEO articles, RankMath metadata, internal linking, and WebP images — all from one local web app.

[![Version](https://img.shields.io/badge/version-2.1.0-green.svg)](https://github.com/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0+-red.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-Commercial-orange.svg)](#-license)

---

## 📖 Table of Contents

1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [Screenshots](#-screenshots)
4. [Project Structure](#-project-structure)
5. [Requirements](#-requirements)
6. [Installation](#-installation)
   - [From GitHub Clone](#option-1-from-github-clone)
   - [From Local Folder](#option-2-from-local-folder)
7. [Configuration](#-configuration)
   - [WordPress Application Password](#-wordpress-application-password)
   - [WooCommerce API Keys](#-woocommerce-api-keys)
   - [RankMath Setup](#-rankmath-setup)
8. [Usage Workflow](#-usage-workflow)
9. [Tabs Guide](#-tabs-guide)
10. [Store Settings](#-store-settings)
11. [Internal Linking](#-internal-linking)
12. [Image Studio](#-image-studio)
13. [Archive Page CSS](#-archive-page-css)
14. [Auto-Update Script](#-auto-update-script)
15. [Running the App](#-running-the-app)
16. [API Reference](#-api-reference)
17. [Troubleshooting](#-troubleshooting)
18. [FAQ](#-faq)
19. [License](#-license)
20. [Support](#-support)

---

## 🎯 Overview

**Khan Herbal Stores — Web Factory** is a **single-machine web application** that
automates the creation of 300+ herbal products for WooCommerce stores. It
combines:

- **SEO article generation** (1000+ words, 87% RankMath score)
- **RankMath metadata** (title, description, robots, canonical, social)
- **Internal linking** (17 site pages + 4 related products per article)
- **WebP image pipeline** (drag-drop, custom sizes, quality control)
- **WooCommerce REST API push** (products + images auto-attached)
- **Store branding** (name, contact, WhatsApp CTA per product)

Built with **Flask + Vanilla JS + Pillow** — no Node.js, no React, no build
process. Runs locally on Windows 10/11, accessible from any device on the
same WiFi network.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🏭 **325 Products Bulk Generation** | Load a text list, generate all products at once |
| 📝 **1000+ Word SEO Articles** | Formula-based templates, no AI required |
| 📊 **RankMath 87% Score** | Automated metadata generation |
| 🎯 **Keyword Density 1.0–1.5%** | Safe zone, no stuffing penalty |
| 🔒 **Duplicate Prevention** | N-gram Jaccard similarity check |
| 🔗 **Internal Linking** | 17 pages + 4 related products per article |
| 🏢 **Store Brand CTA** | Home page link + WhatsApp button per product |
| 🖼️ **WebP Image Pipeline** | Drag-drop, URL paste, custom sizes |
| 🌐 **Auto Image Attach** | Images attach to products via WC API |
| 🎨 **Archive Page CSS** | Consistent card layout for WooCommerce shop |
| 🌙 **Dark / Light Mode** | Toggle with localStorage persistence |
| 📱 **Mobile Responsive** | Access from phone on same WiFi |
| 💾 **Config Export / Import** | Sale-ready deployment |
| 🔐 **Server-Side Sessions** | Credentials never reach browser JS |
| 📦 **CSV Export** | With or without images |
| 🚀 **API Push** | WP Media + WC Product REST API |

---

## 📸 Screenshots

> *Add your own screenshots here after first run.*

```
screenshots/
├── connections-tab.png
├── product-factory.png
├── image-studio.png
├── content-engine.png
├── export-tab.png
└── store-settings.png
```

---

## 📁 Project Structure

```
herbal-product-factory/
│
├── app_web.py                 # Flask main application (single-file)
├── engine.py                  # Content + SEO + RankMath engine
├── media.py                   # Image processing + API push
├── requirements_web.txt       # Python dependencies
├── update.ps1                 # Auto-update script (Windows)
├── README.md                  # This file
│
├── workspace/                 # Auto-created at runtime
│   ├── uploads/               # Raw uploaded images
│   └── images/                # Processed WebP images
│
└── logs/                      # Auto-created at runtime
    └── activity.log
```

**Total files: 6** — kept minimal for easy deployment.

---

## 🖥️ Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 / 11 | Windows 11 |
| **Python** | 3.10+ | 3.11 / 3.13 |
| **RAM** | 4 GB | 8 GB |
| **Disk** | 500 MB | 2 GB |
| **Browser** | Chrome / Edge / Firefox | Chrome |
| **Network** | Local | LAN for mobile access |
| **WordPress** | 5.6+ with REST API | 6.4+ |
| **WooCommerce** | 4.0+ | 8.0+ |
| **RankMath** | Free or Pro | Pro |

---

## 🛠️ Installation

### Option 1: From GitHub Clone

**Step 1 — Prerequisites**

Install [Python 3.10+](https://www.python.org/downloads/)  
✅ **Important:** During install, tick **"Add Python to PATH"**

Install [Git for Windows](https://git-scm.com/download/win)

**Step 2 — Clone Repository**

Open PowerShell and run:

```powershell
cd "C:\Users\YOUR_USERNAME\OneDrive\Desktop"
git clone https://github.com/YOUR_USERNAME/herbal-product-factory.git
cd herbal-product-factory
```

**Step 3 — Create Virtual Environment**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If you see execution policy error:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
.\.venv\Scripts\Activate.ps1
```

**Step 4 — Install Dependencies**

```powershell
pip install -r requirements_web.txt
```

**Step 5 — Run**

```powershell
python app_web.py
```

---

### Option 2: From Local Folder

**Step 1 — Navigate to Folder**

```powershell
cd "C:\Users\sktpa\OneDrive\Desktop\herbal-product-factory 1"
```

**Step 2 — Create Virtual Environment** *(first time only)*

```powershell
python -m venv .venv
```

**Step 3 — Activate Virtual Environment**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Step 4 — Install Dependencies** *(first time only)*

```powershell
pip install -r requirements_web.txt
```

**Step 5 — Run Application**

```powershell
python app_web.py
```

---

## ⚙️ Configuration

### 🔵 WordPress Application Password

**Where to find:**

1. Log in to WordPress Admin → `/wp-admin/`
2. Go to **Users → Profile** (or edit the specific user)
3. Scroll down to **Application Passwords** section
4. Enter name: `Khan Herbal Factory`
5. Click **Add New Application Password**
6. **Copy the 24-character password** (with spaces) — you won't see it again!

**Requirements:**
- User must have **Administrator** role
- **HTTPS is mandatory** — Application Passwords only work over HTTPS

**Where to paste in app:**
- Tab: **🔌 Connections → WordPress Connection → Application Password**

---

### 🟣 WooCommerce API Keys

**Where to find:**

1. WordPress Admin → **WooCommerce → Settings**
2. Click **Advanced** tab → **REST API**
3. Click **Add key**
4. Fill in:
   - **Description:** `Khan Herbal Factory`
   - **User:** Select an Administrator
   - **Permissions:** **Read/Write**
5. Click **Generate API key**
6. **Copy both:**
   - **Consumer Key** — starts with `ck_...`
   - **Consumer Secret** — starts with `cs_...`

**Where to paste in app:**
- Tab: **🔌 Connections → WooCommerce Connection**

---

### 📊 RankMath Setup

- RankMath **must be installed** on your WordPress site
- No API keys required — metadata is injected via:
  - **CSV import** → `meta:rank_math_*` columns
  - **REST API push** → `meta_data` array

**Verify after import:**
1. WP Admin → **Products → All Products**
2. Click any product → **Edit**
3. Scroll to **RankMath** panel
4. Check the **score badge** — should be **85%+**

---

## 🚀 Usage Workflow

Follow these steps **in order** for best results:

### Step 1 — Connect APIs

1. Open app at `http://127.0.0.1:5000`
2. Go to **🔌 Connections** tab
3. Enter WP credentials → **🔗 Connect**
4. Enter WC credentials → **🔗 Connect**
5. Look for green toast notifications

### Step 2 — Configure Store

1. Go to **⚙️ Store Settings** tab
2. Update:
   - Store Name
   - Email, Phone, WhatsApp
   - Address
   - Social links
3. Click **💾 Save Settings**

### Step 3 — Generate Products

1. Go to **🏭 Product Factory** tab
2. Choose input method:
   - **📂 Load File** → Upload `.txt` or `.csv`
   - **Paste** product names (one per line)
   - **🎲 Load Demo** → 5 sample products
3. Adjust price range and stock count
4. Click **⚡ Generate All Products**
5. Verify **RankMath avg: 87%**, **Passing: 100%**

### Step 4 — Assign Images

1. Go to **🖼️ Image Studio** tab
2. Select a product from dropdown
3. Choose slot (Featured / Gallery 1–4)
4. Options:
   - **Drag-drop** image into drop zone
   - **Click drop zone** to browse files
   - **Ctrl+V** to paste from clipboard
   - **Paste URL** → click Download
5. Repeat for all 5 slots (1 featured + 4 gallery)

### Step 5 — Push to Live Site

**⚠️ Order matters — do NOT skip Step 5A**

1. Go to **📤 Export** tab
2. **Step 5A:** Click **🖼️ Push All Images to WP Media**
   - Wait for: `Pushed X products' images (Y files). Failed: 0`
3. **Step 5B:** Click **📦 Push All Products to WooCommerce**
   - Wait for: `Pushed X products as drafts. Images attached: Y. Failed: 0`
   - **Y must be > 0** — otherwise images won't attach

### Step 6 — Verify

1. WP Admin → **Products → All Products**
2. Filter by **Drafts**
3. Open a product → check:
   - ✅ Featured image auto-set
   - ✅ Gallery has 4 images
   - ✅ RankMath score 85%+
   - ✅ Article body present

### Step 7 — Publish Test Products

1. Go to **🧪 Test Lab** tab
2. Enter count (default: 5)
3. Click **🚀 Publish Test Products**
4. Visit `https://yoursite.com/shop/` and test add-to-cart

---

## 📑 Tabs Guide

| # | Tab | Purpose |
|---|-----|---------|
| 1 | 🔌 **Connections** | WP + WC API credentials & connection status |
| 2 | ⚙️ **Store Settings** | Store name, contact, address, social, config backup |
| 3 | 🏭 **Product Factory** | Load/generate products, preview table |
| 4 | 🖼️ **Image Studio** | Drag-drop images, WebP conversion, slot assignment |
| 5 | 📝 **Content Engine** | Article preview, SEO metadata, keywords |
| 6 | 📤 **Export** | CSV download, WP/WC API push, archive CSS |
| 7 | 🧪 **Test Lab** | Publish drafts for cart testing |
| 8 | ℹ️ **About** | Version, features, license info |
| 9 | 📜 **Log** | Activity log with timestamps |

---

## ⚙️ Store Settings

Every product article automatically includes:

1. **Store footer** — Address, phone, email, hours
2. **Brand CTA block** — "Buy X from Khan Herbal Stores" + WhatsApp button
3. **Home page link** — Anchor text = store name
4. **Contact page link** — "Contact us anytime"
5. **About page link** — "About Khan Herbal Stores"

### Configurable Fields

| Field | Default | Used In |
|-------|---------|---------|
| Store Name | Khan Herbal Stores | CTA, footer, schema, title |
| Tagline | Authentic Herbal Remedies in Pakistan | Meta, footer |
| Email | info@khanherbalstores.com | Footer, schema |
| Phone | +92 300 0000000 | Footer, schema |
| WhatsApp | **+923218224219** | WhatsApp CTA button |
| Address | Main Market, Karachi, Sindh, PK 74000 | Footer, LocalBusiness schema |
| Business Hours | Mon-Sat 9:00 AM - 9:00 PM | Footer, schema |
| Facebook / Instagram / YouTube | (empty) | Social schema |

### WhatsApp CTA Behavior

When a customer clicks **💬 Order on WhatsApp** in the product article:

```
Opens WhatsApp with pre-filled message:
"Assalam-o-Alaikum! I am interested in Almond Oil.
 Please share more details and pricing.
 Product link: https://yoursite.com/product/almond-oil/"
```

- **Default number:** +923218224219
- **Override:** Update in Store Settings → WhatsApp field → Save
- Number format: any (spaces/dashes auto-stripped)

---

## 🔗 Internal Linking

### Per Article (Automatic)

| Type | Count | Anchor Example |
|------|-------|----------------|
| Home page | 1 | "Khan Herbal Stores" |
| Shop page | 1 | "shop all products" |
| Natural Herbs | 1 | "explore natural herbs" |
| How To Shop | 1 | "shopping guide" |
| FAQs | 1 | "read our FAQs" |
| Contact | 1 | "Contact us" |
| Related Products | 4 | Product names |
| **Total** | **10** | — |

### Related Products Logic

Same category + word overlap + use-case matching → **top 4 products**.

**Bidirectional:** if A links to B, B links to A.

---

## 🖼️ Image Studio

### Supported Methods

| Method | How | Best For |
|--------|-----|----------|
| **Drag-drop** | Drag image from browser/desktop | Google Images, Openverse |
| **File browse** | Click drop zone | Local files |
| **Ctrl+V** | Paste from clipboard | "Copy Image" from browser |
| **URL paste** | Paste direct image URL | External images |

### Custom Sizes

Choose from dropdown:
- `300x300` — thumbnail
- `600x600` — archive card
- `800x800` — medium
- `1200x630` — OG / social
- `1200x1200` — product page **(default)**
- **Custom** → Enter any width × height

### Processing Pipeline

```
Source → Aspect ratio crop → Resize → WebP (quality 80, method 6) → Slot
```

### Slot System

Each product has **5 slots**:
- **Slot 1** — Featured image (must have)
- **Slots 2–5** — Gallery images

---

## 🎨 Archive Page CSS

**Purpose:** Make all WooCommerce product cards **same height, aligned rows**.

### Install

1. Go to **📤 Export** tab
2. Click **💾 Save archive-consistency.css**
3. WordPress Admin → **Appearance → Customize → Additional CSS**
4. Paste CSS → **Publish**

### Features

- Fixed card height (440px)
- 1:1 image aspect ratio
- 2-line title clamp
- Responsive: 4 / 3 / 2 / 1 columns
- Hover animation
- Green "Add to Cart" button

---

## 🔧 Auto-Update Script

**`update.ps1`** — Automatically applies patches to `engine.py` and `app_web.py`.

### Run

```powershell
.\update.ps1
```

### Features

- ✅ Idempotent (safe to re-run)
- ✅ Creates `.bak` backups before editing
- ✅ Detailed change log
- ✅ Skips already-applied changes

### Rollback

```powershell
Copy-Item "engine.py.bak" "engine.py" -Force
Copy-Item "app_web.py.bak" "app_web.py" -Force
```

---

## 🚀 Running the App

### Standard Run

```powershell
cd "C:\Users\sktpa\OneDrive\Desktop\herbal-product-factory 1"
.\.venv\Scripts\Activate.ps1
python app_web.py
```

### Expected Output

```
======================================================================
  🌿 Khan Herbal Stores — Web Factory  v2.1.0
======================================================================
  Local:    http://127.0.0.1:5000
  Network:  http://192.168.1.5:5000    ← same WiFi
======================================================================
  Store:    Khan Herbal Stores
  Ctrl+C to stop
======================================================================
```

Browser opens automatically.

### Access from Phone

1. Ensure phone is on **same WiFi** as PC
2. Open `http://192.168.1.5:5000` (use your PC's network IP)
3. Full responsive UI will load

### Stop Server

Press **`Ctrl+C`** in the PowerShell window.

### Change Port

```powershell
$env:PORT=8080
python app_web.py
```

---

## 🔌 API Reference

All routes are **same-origin** (no CORS issues).

### Connection Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/connect/wp` | Test + save WP credentials |
| POST | `/api/test/wp` | Test without saving |
| POST | `/api/disconnect/wp` | Clear WP session |
| POST | `/api/connect/wc` | Test + save WC credentials |
| POST | `/api/test/wc` | Test without saving |
| POST | `/api/disconnect/wc` | Clear WC session |

### Store Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/store/get` | Fetch store settings |
| POST | `/api/store/save` | Save store settings |
| POST | `/api/store/reset` | Reset to defaults |
| POST | `/api/store/license` | Save license info |
| GET | `/api/config/export` | Export config as JSON |
| POST | `/api/config/import` | Import config JSON |

### Product Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/products/load` | Upload `.txt`/`.csv` file |
| POST | `/api/products/load-text` | Paste text list |
| POST | `/api/products/load-demo` | Load 5 demo products |
| POST | `/api/products/clear` | Clear session products |
| GET | `/api/products/list` | List built products |
| POST | `/api/products/generate` | Generate all products |

### Image Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/images/slots` | Get slot status |
| POST | `/api/images/upload` | Upload image file |
| POST | `/api/images/download-url` | Download from URL |
| GET | `/api/images/thumb` | Serve thumbnail |

### Export & Push

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/export/csv` | Generate CSV |
| GET | `/api/export/archive-css` | Get archive CSS |
| POST | `/api/push/wp` | Push images to WP media |
| POST | `/api/push/wc` | Push products to WooCommerce |

### Test Lab

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/test/publish` | Publish draft products |

### Log

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/log` | Get activity log |
| POST | `/api/log/clear` | Clear log |

---

## 🐛 Troubleshooting

### App Won't Start

**Error:** `ModuleNotFoundError: No module named 'flask'`  
**Fix:**
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements_web.txt
```

**Error:** `.\.venv\Scripts\Activate.ps1 not recognized`  
**Fix:** Virtual env not created. Run:
```powershell
python -m venv .venv
```

**Error:** `Execution Policy`  
**Fix:**
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

---

### Connection Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| **401 Unauthorized** | Wrong password | Regenerate WP Application Password |
| **403 Forbidden** | User lacks permission | Ensure Administrator role |
| **404 Not Found** | REST API disabled | Enable in WP → Settings → Permalinks |
| **SSL Error** | Cert issue | Verify HTTPS in browser |
| **Timeout** | Slow host | Check network; increase timeout |

---

### Image Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| **Drag-drop fails** | CORS block | Use **Ctrl+V** paste method |
| **Upload fails** | File too large | Max 50 MB per file |
| **WebP not saving** | Pillow missing | `pip install Pillow` |
| **Slot not updating** | No product selected | Select from dropdown |
| **Images not attaching** | Wrong push order | Push images **before** products |

---

### Content Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| **Duplicate content** | Template overlap | Formula rotation handles this |
| **Density > 2%** | Rare bug | Re-generate; v4.4 keeps 1.0–1.5% |
| **RM Score < 80%** | Rare | Verify focus keyword length |

---

### CSV Import Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| **RankMath meta not imported** | Wrong prefix | Must use `meta:` prefix |
| **Images missing** | URLs not public | Push to WP first |
| **Categories missing** | Not created | WooCommerce creates automatically |
| **Attributes missing** | Global attribute undefined | Create in Products → Attributes |

---

## ❓ FAQ

**Q: Do I need AI (OpenAI, Claude) for content generation?**  
A: No. Articles use Jinja2-style formula templates. 100% offline.

**Q: How many products can I generate?**  
A: Tested up to 325. Larger lists work but may take longer.

**Q: Does RankMath score really reach 87%?**  
A: Yes — verified on demo products. Score may vary ±5% by category.

**Q: Are my credentials stored on disk?**  
A: No. They stay in **server memory only**. Closing the app wipes them.

**Q: Can I run this on Mac or Linux?**  
A: Yes — same Python commands work. Only `update.ps1` is Windows-only.

**Q: Why does drag-drop fail in Chrome sometimes?**  
A: Browser CORS blocks direct image drag. Use **Ctrl+V** paste or **URL paste** instead.

**Q: Can I use this for non-herbal products?**  
A: Yes — edit `CATEGORIES` and `TAG_RULES` in `engine.py`.

**Q: How do I add more product categories?**  
A: Edit `CATEGORIES` dict in `engine.py`, then re-run updater.

**Q: What if images don't auto-attach?**  
A: Ensure you clicked **Push Images** first, then **Push Products**. Check logs.

**Q: Can I sell this project to clients?**  
A: Yes — this is a Commercial Single-Site licensed product. See License section.

**Q: Does it work without internet?**  
A: Content generation works offline. API push and image download require internet.

**Q: Is my site data sent to any AI?**  
A: No. Everything runs locally. No external API calls for content.

---

## 📜 License

**Commercial Single-Site License**

- ✅ Use on **one** production WooCommerce store
- ✅ Modify source code for personal use
- ❌ Redistribute or resell as-is
- ❌ Use on multiple stores without separate license
- ❌ Remove license/copyright notices

For multi-site or white-label licensing, contact **support@khanherbalstores.com**.

---

## 💬 Support

**Documentation:** This README  
**Version:** 2.1.0  
**Last Updated:** 2026-10-16

### Reporting Bugs

Include:
1. **Tab name** where error occurred
2. **Full traceback** from terminal
3. **Steps to reproduce**
4. **Python version** (`python --version`)

### Feature Requests

Describe:
1. Use case
2. Expected behavior
3. Which tab it should live in

### Contact

- **Email:** support@khanherbalstores.com
- **WhatsApp:** +923218224219

---

## 🎯 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  INSTALL (first time only)                               │
│    cd "path/to/herbal-product-factory"                   │
│    python -m venv .venv                                  │
│    .\.venv\Scripts\Activate.ps1                          │
│    pip install -r requirements_web.txt                   │
│                                                          │
│  RUN                                                     │
│    python app_web.py                                     │
│                                                          │
│  AUTO-UPDATE                                             │
│    .\update.ps1                                          │
│                                                          │
│  TEST MODULES                                            │
│    python engine.py                                      │
│    python media.py                                       │
│                                                          │
│  ROLLBACK                                                │
│    Copy-Item "engine.py.bak" "engine.py" -Force          │
│    Copy-Item "app_web.py.bak" "app_web.py" -Force        │
└──────────────────────────────────────────────────────────┘
```

---

## 🌟 Credits

- **Framework:** Flask + Jinja2
- **Image processing:** Pillow
- **HTTP client:** Requests
- **Slug generation:** python-slugify
- **UI:** Vanilla JS + Modern CSS

---

**Built with ❤️ for Pakistani herbal store owners.**

*Khan Herbal Stores — Authentic Herbal Remedies in Pakistan*