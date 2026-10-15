# =============================================================================
# update.ps1 — Auto-update engine.py and app_web.py
# =============================================================================
# Adds: WhatsApp CTA + Store brand link in every product article
# Safe: Skips if change already applied
# Backup: Creates .bak files before modifying
# =============================================================================

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  Khan Herbal Stores — Auto Update Script" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan

$changes = 0
$skipped = 0

# =============================================================================
# UPDATE 1: engine.py
# =============================================================================
Write-Host ""
Write-Host "[1/2] Updating engine.py..." -ForegroundColor Yellow

$enginePath = Join-Path $scriptDir "engine.py"
if (-not (Test-Path $enginePath)) {
    Write-Host "  ERROR: engine.py not found!" -ForegroundColor Red
    exit 1
}

# Backup
Copy-Item $enginePath "$enginePath.bak" -Force
$content = Get-Content $enginePath -Raw -Encoding UTF8
# Normalize line endings to LF for reliable matching
$content = $content -replace "`r`n", "`n"

# -----------------------------------------------------------------------------
# CHANGE 1a: Add urllib import
# -----------------------------------------------------------------------------
$findA = "from slugify import slugify"
$replA = "from slugify import slugify`nfrom urllib.parse import quote_plus"
if ($content.Contains($findA) -and -not $content.Contains("from urllib.parse import quote_plus")) {
    $content = $content.Replace($findA, $replA)
    $changes++
    Write-Host "  [1a] Added urllib import" -ForegroundColor Green
} else {
    $skipped++
    Write-Host "  [1a] SKIP (already applied)" -ForegroundColor Gray
}

# -----------------------------------------------------------------------------
# CHANGE 1b: Update WhatsApp default
# -----------------------------------------------------------------------------
$findB = '"whatsapp":       "+92 300 0000000"'
$replB = '"whatsapp":       "+923218224219"'
if ($content.Contains($findB)) {
    $content = $content.Replace($findB, $replB)
    $changes++
    Write-Host "  [1b] Updated WhatsApp default" -ForegroundColor Green
} else {
    $skipped++
    Write-Host "  [1b] SKIP (already applied or not found)" -ForegroundColor Gray
}

# -----------------------------------------------------------------------------
# CHANGE 1c: Insert build_product_cta_block function after build_brand_link
# -----------------------------------------------------------------------------
$findC = @'
def build_brand_link():
    s = get_store()
    return f'<a href="{SITE_PAGES["home"]["url"]}">{s["name"]}</a>'
'@
$findC = $findC -replace "`r`n", "`n"

$replC = @'
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
'@
$replC = $replC -replace "`r`n", "`n"

if ($content.Contains("def build_product_cta_block")) {
    $skipped++
    Write-Host "  [1c] SKIP (function already exists)" -ForegroundColor Gray
} elseif ($content.Contains($findC)) {
    $content = $content.Replace($findC, $replC)
    $changes++
    Write-Host "  [1c] Added build_product_cta_block function" -ForegroundColor Green
} else {
    Write-Host "  [1c] WARN: Anchor not found — manual check needed" -ForegroundColor Yellow
    $skipped++
}

# -----------------------------------------------------------------------------
# CHANGE 1d: Add {product_cta} to article template
# -----------------------------------------------------------------------------
$findD = "<h2>Final Thoughts</h2>`n<p>{conclusion}</p>`n`n{related_products_html}"
$replD = "<h2>Final Thoughts</h2>`n<p>{conclusion}</p>`n`n{product_cta}`n`n{related_products_html}"
if ($content.Contains($replD)) {
    $skipped++
    Write-Host "  [1d] SKIP (already in template)" -ForegroundColor Gray
} elseif ($content.Contains($findD)) {
    $content = $content.Replace($findD, $replD)
    $changes++
    Write-Host "  [1d] Added {product_cta} to template" -ForegroundColor Green
} else {
    Write-Host "  [1d] WARN: Template anchor not found" -ForegroundColor Yellow
    $skipped++
}

# -----------------------------------------------------------------------------
# CHANGE 1e: Add product_cta variable in generate_article()
# -----------------------------------------------------------------------------
$findE = "    conclusion = _build_conclusion(product_name, rng, kw)`n`n    links = build_internal_links_html(product_name)"
$replE = "    conclusion = _build_conclusion(product_name, rng, kw)`n    product_cta = build_product_cta_block(product_name, product_url(product_name))`n`n    links = build_internal_links_html(product_name)"
if ($content.Contains($replE)) {
    $skipped++
    Write-Host "  [1e] SKIP (already added)" -ForegroundColor Gray
} elseif ($content.Contains($findE)) {
    $content = $content.Replace($findE, $replE)
    $changes++
    Write-Host "  [1e] Added product_cta variable" -ForegroundColor Green
} else {
    Write-Host "  [1e] WARN: generate_article anchor not found" -ForegroundColor Yellow
    $skipped++
}

# -----------------------------------------------------------------------------
# CHANGE 1f: Add product_cta=product_cta to template format call
# -----------------------------------------------------------------------------
$findF = "        faq_html=faq_html, conclusion=conclusion,`n        related_products_html=links[""related_products_html""],"
$replF = "        faq_html=faq_html, conclusion=conclusion,`n        product_cta=product_cta,`n        related_products_html=links[""related_products_html""],"
if ($content.Contains($replF)) {
    $skipped++
    Write-Host "  [1f] SKIP (already in template format)" -ForegroundColor Gray
} elseif ($content.Contains($findF)) {
    $content = $content.Replace($findF, $replF)
    $changes++
    Write-Host "  [1f] Added product_cta to format call" -ForegroundColor Green
} else {
    Write-Host "  [1f] WARN: format call anchor not found" -ForegroundColor Yellow
    $skipped++
}

# Write back engine.py
[System.IO.File]::WriteAllText($enginePath, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "  engine.py saved" -ForegroundColor Green

# =============================================================================
# UPDATE 2: app_web.py
# =============================================================================
Write-Host ""
Write-Host "[2/2] Updating app_web.py..." -ForegroundColor Yellow

$appPath = Join-Path $scriptDir "app_web.py"
if (-not (Test-Path $appPath)) {
    Write-Host "  ERROR: app_web.py not found!" -ForegroundColor Red
    exit 1
}

Copy-Item $appPath "$appPath.bak" -Force
$content2 = Get-Content $appPath -Raw -Encoding UTF8
$content2 = $content2 -replace "`r`n", "`n"

# -----------------------------------------------------------------------------
# CHANGE 2a: WhatsApp default in STORE_DEFAULTS
# -----------------------------------------------------------------------------
$findG = '"whatsapp":       "+92 300 0000000",'
$replG = '"whatsapp":       "+923218224219",'
if ($content2.Contains($findG)) {
    $content2 = $content2.Replace($findG, $replG)
    $changes++
    Write-Host "  [2a] Updated WhatsApp default" -ForegroundColor Green
} else {
    $skipped++
    Write-Host "  [2a] SKIP (already applied or not found)" -ForegroundColor Gray
}

# -----------------------------------------------------------------------------
# CHANGE 2b: WhatsApp placeholder in HTML
# -----------------------------------------------------------------------------
$findH = 'placeholder="+92 300 0000000"'
$replH = 'placeholder="+923218224219"'
if ($content2.Contains($findH)) {
    $content2 = $content2.Replace($findH, $replH)
    $changes++
    Write-Host "  [2b] Updated placeholder" -ForegroundColor Green
} else {
    $skipped++
    Write-Host "  [2b] SKIP (already applied or not found)" -ForegroundColor Gray
}

[System.IO.File]::WriteAllText($appPath, $content2, [System.Text.UTF8Encoding]::new($false))
Write-Host "  app_web.py saved" -ForegroundColor Green

# =============================================================================
# DONE
# =============================================================================
Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  COMPLETE" -ForegroundColor Green
Write-Host "  Changes applied: $changes" -ForegroundColor Green
Write-Host "  Skipped:        $skipped" -ForegroundColor Gray
Write-Host "  Backups:        engine.py.bak, app_web.py.bak" -ForegroundColor Gray
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. python engine.py      (verify)" -ForegroundColor White
Write-Host "  2. python app_web.py     (run)"  -ForegroundColor White
Write-Host ""