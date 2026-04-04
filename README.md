# 🌾 FarmPlan Pro — Premium Farm Layout PDF Generator

A production-ready Streamlit web application that generates engineering-style,
premium-quality farm layout PDFs — designed to be **sold as digital products**
at $5–$25 per download.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Farm Types** | Dairy Farm, Goat Farming, Poultry Farm, Organic Vegetable Farm, Mixed Homestead |
| **Countries** | India, USA, UK, Australia, Canada, NZ, Brazil, South Africa, Kenya, Germany |
| **Layout Engine** | Matplotlib 2D top-view, grid-based, no randomness |
| **PDF Quality** | 2-page ReportLab PDF with cover, map, tables, tips |
| **Area Units** | Acres, Hectares, m², sq ft — all auto-calculated |
| **Budget Levels** | Basic / Standard / Premium (affects infrastructure detail) |
| **Animal Capacity** | Auto-calculated per zone based on country space standards |

---

## 🚀 Quick Start

```bash
# 1. Clone or copy the files
cd farm_layout_app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The app opens at **http://localhost:8501** in your browser.

---

## 📁 File Structure

```
farm_layout_app/
├── app.py              # Main application (single-file)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🏗️ Architecture

```
app.py
├── CONSTANTS & CONFIG       # Farm templates, colors, space requirements
├── calculate_layout()       # Area & zone calculation engine
├── draw_layout_map()        # Matplotlib 2D engineering layout
├── generate_pdf()           # ReportLab premium PDF assembler
│   ├── _header_block()
│   ├── _summary_bar()
│   ├── _area_table()
│   ├── _infra_table()
│   ├── _animal_summary()
│   ├── _tips_section()
│   └── _disclaimer_footer()
└── main()                   # Streamlit UI
```

---

## 💰 Productization Guide

### Selling PDFs as Digital Products

Each generated PDF is unique based on inputs and ready to sell. Recommended platforms:

| Platform | Recommended Price |
|---|---|
| Gumroad | $5–$15 |
| Etsy (Digital Download) | $7–$20 |
| Your own website | $10–$25 |
| Fiverr (custom order) | $15–$50 |

### Adding More Farm Types

In `app.py`, add to:
1. `FARM_TYPES` list
2. `ANIMAL_SPACE_SQMT` dict
3. `LAYOUT_TEMPLATES` dict
4. `FARM_TIPS` dict

### Extending Countries

Add to `COUNTRY_MULTIPLIER` dict with a space multiplier (1.0 = standard).

---

## 🌐 Deployment Options

### Streamlit Cloud (Free)
```bash
# Push to GitHub, then deploy at share.streamlit.io
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD ["streamlit", "run", "app.py", "--server.port=8080"]
```

### Railway / Render / Fly.io
- Works as a standard Python web app
- Set start command: `streamlit run app.py --server.port=$PORT`

---

## 📄 PDF Output Structure

**Page 1:**
- Title banner (dark gradient header)
- 6-cell KPI summary bar
- Full-width 2D layout map (200 DPI)

**Page 2:**
- Section-wise area allocation table (all zones)
- Animal stock summary table
- Infrastructure specification table
- 7 expert setup & management tips
- Legal disclaimer footer

---

## 🔧 Customization

- **Colors:** Edit `ZONE_COLORS` dict
- **Layout proportions:** Edit `LAYOUT_TEMPLATES` fractions
- **Space standards:** Edit `ANIMAL_SPACE_SQMT`
- **Tips content:** Edit `FARM_TIPS`
- **PDF styling:** Edit `_build_styles()` and color constants at top of PDF section

---

*Built with Streamlit · Matplotlib · ReportLab*
