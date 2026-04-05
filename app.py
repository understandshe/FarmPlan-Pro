"""
FARMPLAN PRO — Architectural Farm Layout Generator v3.0
Production-Ready | No Syntax Errors | Professional Blueprint Style Map
"""
import io
import math
import datetime
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle
import matplotlib.patheffects as pe

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage, PageBreak
)

# =============================================================================
# MASTER DATA (CLEANED: NO TRAILING SPACES)
# =============================================================================
FARM_TYPES = ["Dairy Farm", "Goat Farming", "Poultry Farm", "Organic Vegetable Farm", "Mixed Homestead"]
COUNTRIES = ["India", "USA", "UK", "Australia", "Canada", "New Zealand", "Brazil", "South Africa", "Kenya", "Germany"]
BUDGET_LEVELS = ["Basic", "Standard", "Premium"]

# Space requirements per animal (sq meters)
ANIMAL_SPACE = {
    "Dairy Farm": {"milch_cow": 18, "dry_cow": 14, "calf": 6, "heifer": 10, "goat": 4, "chicken": 0.5, "bull": 25},
    "Goat Farming": {"milch_cow": 18, "dry_cow": 14, "calf": 6, "heifer": 10, "goat": 3.5, "chicken": 0.5, "bull": 20},
    "Poultry Farm": {"milch_cow": 18, "dry_cow": 14, "calf": 6, "heifer": 10, "goat": 4, "chicken": 0.4, "bull": 20},
    "Organic Vegetable Farm": {"milch_cow": 18, "dry_cow": 14, "calf": 6, "heifer": 10, "goat": 4, "chicken": 0.5, "bull": 20},
    "Mixed Homestead": {"milch_cow": 16, "dry_cow": 12, "calf": 5, "heifer": 9, "goat": 3.5, "chicken": 0.45, "bull": 22},
}

# Country Multipliers
COUNTRY_FACTOR = {
    "India": 0.90, "USA": 1.10, "UK": 1.05, "Australia": 1.18,
    "Canada": 1.12, "New Zealand": 1.10, "Brazil": 0.95,
    "South Africa": 0.95, "Kenya": 0.88, "Germany": 1.10,
}

# Budget Specs
BUDGET_SPEC = {
    "Basic": { "Structure": "Cement block / GI sheet", "Flooring": "Packed earth / cement wash", "Roofing": "GI corrugated sheet" },
    "Standard": { "Structure": "RCC columns + Brick infill", "Flooring": "M20 concrete slab", "Roofing": "Colour-coated GI sheet" },
    "Premium": { "Structure": "RCC framed structure", "Flooring": "Anti-slip rubberised concrete", "Roofing": "Insulated metal deck" },
}

# Layout Templates (Zone Name, Fraction, Type)
TEMPLATES = {
    "Dairy Farm": [
        ("Milch Cow Barn", 0.22, "barn"), ("Dry Cow Section", 0.10, "barn"), ("Heifer Section", 0.08, "barn"),
        ("Calf Pens", 0.06, "barn"), ("Milking Parlour", 0.07, "barn"), ("Feed Store", 0.10, "store"),
        ("Silage Pit", 0.05, "open"), ("Manure Mgmt", 0.05, "open"), ("Isolation", 0.04, "barn"),
        ("Bull Pen", 0.03, "barn"), ("Water Tank", 0.04, "util"), ("Office", 0.03, "entry"),
        ("Green Buffer", 0.07, "green"), ("Service Lane", 0.06, "road")
    ],
    "Goat Farming": [
        ("Goat Housing", 0.28, "barn"), ("Buck Section", 0.07, "barn"), ("Kidding Pens", 0.07, "barn"),
        ("Milking Area", 0.06, "barn"), ("Feed Store", 0.12, "store"), ("Grazing Paddock", 0.15, "green"),
        ("Isolation", 0.04, "barn"), ("Compost", 0.05, "open"), ("Water Points", 0.04, "util"),
        ("Office", 0.03, "entry"), ("Green Buffer", 0.04, "green"), ("Service Lane", 0.05, "road")
    ],
    "Poultry Farm": [
        ("Poultry House A", 0.20, "barn"), ("Poultry House B", 0.18, "barn"), ("Brooder Room", 0.07, "barn"),
        ("Feed Mill", 0.10, "store"), ("Egg Grading", 0.05, "store"), ("Cold Storage", 0.04, "store"),
        ("Isolation", 0.04, "barn"), ("Disposal", 0.03, "open"), ("Litter Store", 0.06, "open"),
        ("Water Tank", 0.03, "util"), ("Office", 0.03, "entry"), ("Green Buffer", 0.09, "green"),
        ("Service Lane", 0.08, "road")
    ],
    "Organic Vegetable Farm": [
        ("Bed Block A", 0.18, "green"), ("Bed Block B", 0.15, "green"), ("Bed Block C", 0.12, "green"),
        ("Nursery", 0.07, "barn"), ("Compost Yard", 0.08, "open"), ("Vermicompost", 0.05, "open"),
        ("Irrigation", 0.04, "util"), ("Tool Shed", 0.07, "store"), ("Pack House", 0.06, "store"),
        ("Net House", 0.06, "barn"), ("Office", 0.04, "entry"), ("Windbreak", 0.03, "green"),
        ("Pathways", 0.05, "road")
    ],
    "Mixed Homestead": [
        ("Cattle Shed", 0.14, "barn"), ("Goat House", 0.10, "barn"), ("Poultry Unit", 0.08, "barn"),
        ("Kitchen Garden", 0.10, "green"), ("Crop Field", 0.18, "green"), ("Fodder Area", 0.08, "green"),
        ("Feed Store", 0.07, "store"), ("Biogas Plant", 0.04, "util"), ("Compost Pit", 0.04, "open"),
        ("Water Tank", 0.03, "util"), ("Residence", 0.03, "entry"), ("Service Lane", 0.05, "road"),
        ("Fruit Trees", 0.06, "green")
    ],
}

FARM_TIPS = {
    "Dairy Farm": ["Orient barn East-West for natural ventilation.", "Keep milking parlour adjacent to cow section.", "Install automated drinking troughs (10-15L/hr).", "Allocate 15% area for fodder storage.", "Grade floors 1:50 for drainage."],
    "Goat Farming": ["Elevate sleeping platforms 60cm above ground.", "Separate bucks 50m from does.", "Use keyhole feeders to prevent bullying.", "Rotational grazing every 21 days.", "Clean water troughs daily."],
    "Poultry Farm": ["North-South orientation for ventilation.", "Max 10-12 birds/m2 for broilers.", "10cm deep litter management.", "Biosecurity footbaths at every entry.", "Monitor water consumption daily."],
    "Organic Vegetable Farm": ["North-South bed orientation.", "Rotate crops annually (4-block system).", "Drip irrigation saves 40-60% water.", "Use yellow sticky traps for pests.", "Apply 5-8 tonnes compost/acre."],
    "Mixed Homestead": ["Livestock downwind from residence.", "Integrate biogas for fuel/fertilizer.", "Plant Napier grass on boundaries.", "Maintain 3 income streams.", "Plan for 20% future expansion."],
}

# =============================================================================
# CALCULATION ENGINE
# =============================================================================
def calculate_layout(land_acres, country, farm_type, animals, infra, budget):
    SQM = land_acres * 4046.86
    SQFT = land_acres * 43560.0
    mult = COUNTRY_FACTOR.get(country, 1.0)

    zones = []
    for name, frac, ztype in TEMPLATES[farm_type]:
        # Find animal key
        sp_key = None
        for kw, sk in [("Cow","milch_cow"),("Dry Cow","dry_cow"),("Heifer","heifer"),("Calf","calf"),
                       ("Kidding","calf"),("Goat","goat"),("Buck","goat"),("Poultry","chicken"),
                       ("Layer","chicken"),("Broiler","chicken"),("Bull","bull")]:
            if kw.lower() in name.lower():
                sp_key = sk
                break
        
        cap = None
        if sp_key and sp_key in ANIMAL_SPACE[farm_type]:
            adj = ANIMAL_SPACE[farm_type][sp_key] * mult
            cap = max(1, int(SQM * frac / adj))

        zones.append({
            "name": name, "frac": frac, "ztype": ztype,
            "sqm": round(SQM * frac, 1), "sqft": round(SQFT * frac, 0),
            "capacity": cap
        })

    infra_rows = []
    for k, v in BUDGET_SPEC[budget].items():
        infra_rows.append((k, "Defined", v))
    if infra.get("milking"): infra_rows.append(("Milking Area", "Included", "Adjacent to cows"))
    if infra.get("isolation"): infra_rows.append(("Isolation Pen", "Included", "Downwind placement"))
    if infra.get("fodder"): infra_rows.append(("Feed Storage", "Included", "Covered & ventilated"))

    return {
        "land_acres": land_acres, "sqm": round(SQM, 1), "sqft": round(SQFT, 0),
        "country": country, "farm_type": farm_type, "budget": budget,
        "zones": zones, "animals": animals, "infra_rows": infra_rows,
        "mult": mult, "tips": FARM_TIPS[farm_type],
        "generated": datetime.datetime.now().strftime("%d %B %Y, %I:%M %p"),
        "ref": "FP-" + datetime.datetime.now().strftime("%Y%m%d")
    }

# =============================================================================
# ARCHITECTURAL BLUEPRINT MAP GENERATOR
# =============================================================================
def draw_realistic_map(data):
    zones = data["zones"]
    acres = data["land_acres"]
    farm = data["farm_type"]
    
    fig = plt.figure(figsize=(16, 11), facecolor="#FFFFFF")
    ax = fig.add_axes([0.02, 0.12, 0.75, 0.82])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")
    ax.axis("off")
    
    # Background
    ax.add_patch(patches.Rectangle((0, 0), 100, 100, facecolor="#F4F7F6", zorder=0))
    
    # Layout Geometry
    PLOT_X, PLOT_Y, PLOT_W, PLOT_H = 5, 5, 90, 90
    GAP = 0.6
    
    # Separate zones
    road_z = [z for z in zones if z["ztype"] == "road"]
    main_z = [z for z in zones if z["ztype"] != "road"]
    
    # Top/Bottom/Left/Right logic simplified for grid
    n = len(main_z)
    left_z = main_z[:math.ceil(n * 0.55)]
    right_z = main_z[math.ceil(n * 0.55):]
    
    lane_w = 5.0
    left_w = (PLOT_W - lane_w) * 0.55
    right_w = (PLOT_W - lane_w) * 0.40
    
    # Placement function
    def place_col(zlist, x0, w, y0, h):
        tot = sum(z["frac"] for z in zlist) or 1
        avail = h - GAP * len(zlist)
        y = y0
        res = []
        for z in zlist:
            zh = (z["frac"] / tot) * avail
            res.append((z, x0, y, w, zh))
            y += zh + GAP
        return res

    placed_left = place_col(left_z, PLOT_X, left_w, PLOT_Y, PLOT_H)
    placed_right = place_col(right_z, PLOT_X + left_w + lane_w + GAP, right_w, PLOT_Y, PLOT_H)
    
    # Draw Zones (Architectural Style)
    for z, x, y, w, h in placed_left + placed_right:
        # Style based on type
        color, hatch, lw = "#FFFFFF", "", 1.0
        if z["ztype"] == "barn": color, hatch, lw = "#E3F2FD", "///", 1.5
        elif z["ztype"] == "green": color, hatch, lw = "#E8F5E9", "...", 0.8
        elif z["ztype"] == "store": color, hatch, lw = "#FFF8E1", "|||", 1.2
        elif z["ztype"] == "open": color, hatch, lw = "#FFEBEE", "\\\\", 0.8
        elif z["ztype"] == "util": color, hatch, lw = "#E0F7FA", "+++", 1.0
        
        # Rectangle
        ax.add_patch(patches.Rectangle((x, y), w, h, facecolor=color, edgecolor="#37474F", 
                                       linewidth=lw, hatch=hatch, zorder=2))
        # Inner shadow effect
        ax.add_patch(patches.Rectangle((x+0.2, y+0.2), w-0.4, h-0.4, fill=False, 
                                       edgecolor="#90A4AE", linewidth=0.5, linestyle=":", zorder=3))
        
        # Text Label
        ax.text(x + w/2, y + h/2, z["name"], ha="center", va="center", fontsize=7, 
                fontweight="bold", color="#1A237E", zorder=4,
                path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])
        
        # Area Text
        ax.text(x + w/2, y + h/2 - 0.6, f"{z['sqm']:.0f}m²", ha="center", va="center", 
                fontsize=5.5, color="#546E7A", style="italic", zorder=4,
                path_effects=[pe.withStroke(linewidth=2, foreground="white")])

    # Draw Service Lane
    lane_x = PLOT_X + left_w + GAP
    ax.add_patch(patches.Rectangle((lane_x, PLOT_Y), lane_w, PLOT_H, facecolor="#CFD8DC", zorder=1))
    ax.plot([lane_x + lane_w/2, lane_x + lane_w/2], [PLOT_Y, PLOT_Y+PLOT_H], 
            color="#FFFFFF", lw=1.5, ls="--", zorder=2)
    ax.text(lane_x + lane_w/2, PLOT_Y + PLOT_H/2, "SERVICE\nLANE", ha="center", va="center", 
            fontsize=5, fontweight="bold", color="#455A64", rotation=90, zorder=3)

    # Trees (Perimeter)
    for t in range(8, 93, 8):
        ax.add_patch(Circle((t, 3), 1.5, facecolor="#81C784", edgecolor="#388E3C", zorder=5))
        ax.add_patch(Circle((t, 97), 1.5, facecolor="#81C784", edgecolor="#388E3C", zorder=5))
    for t in range(8, 93, 8):
        ax.add_patch(Circle((3, t), 1.5, facecolor="#81C784", edgecolor="#388E3C", zorder=5))
        ax.add_patch(Circle((97, t), 1.5, facecolor="#81C784", edgecolor="#388E3C", zorder=5))

    # Compass Rose
    ax.text(94, 94, "N", ha="center", va="center", fontsize=10, fontweight="bold", color="#D32F2F", zorder=6)
    ax.plot([94, 94], [90, 93], color="#D32F2F", lw=2, zorder=6)
    ax.add_patch(Circle((94, 90), 2, fill=False, edgecolor="#455A64", lw=1, zorder=6))

    # Scale Bar
    ax.plot([8, 28], [3, 3], color="#212121", lw=2, zorder=6)
    ax.text(18, 2, f"Scale: 20m", ha="center", fontsize=6, color="#455A64", zorder=6)
    
    # Title Block
    fig.text(0.02, 0.05, f"FARMPLAN PRO | {acres} Acre {farm} Site Plan", fontsize=12, fontweight="bold", color="#1A237E")
    fig.text(0.02, 0.02, f"Ref: {data['ref']} | Date: {data['generated']}", fontsize=8, color="#78909C")

    # Legend Box
    ax_l = fig.add_axes([0.79, 0.12, 0.19, 0.82])
    ax_l.set_xlim(0, 10)
    ax_l.set_ylim(0, 10)
    ax_l.axis("off")
    ax_l.add_patch(patches.Rectangle((0, 0), 10, 10, facecolor="#FAFAFA", edgecolor="#B0BEC5", lw=1))
    ax_l.text(5, 9.5, "LEGEND", ha="center", fontsize=9, fontweight="bold", color="#1A237E")
    
    legend_items = [("/// Barn/Structure", "#E3F2FD"), ("... Green/Field", "#E8F5E9"), 
                    ("||| Store", "#FFF8E1"), ("=== Road/Lane", "#CFD8DC")]
    ly = 8.5
    for txt, col in legend_items:
        ax_l.add_patch(patches.Rectangle((0.5, ly-0.4), 1.5, 0.8, facecolor=col, edgecolor="#37474F"))
        ax_l.text(2.5, ly, txt, va="center", fontsize=6.5, color="#455A64")
        ly -= 1.0

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=250, bbox_inches="tight", facecolor="#FFFFFF")
    plt.close(fig)
    buf.seek(0)
    return buf.read()

# =============================================================================
# PDF GENERATION
# =============================================================================
C_DARK = colors.HexColor("#1A237E")
C_GREEN = colors.HexColor("#2E7D32")

def generate_pdf(data, map_png):
    buf = io.BytesIO()
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    story = []

    # Header
    story.append(Paragraph(f"<b>{data['land_acres']} Acre {data['farm_type']} Site Plan</b>", styles["Title"]))
    story.append(Paragraph(f"{data['country']} Edition | Budget: {data['budget']} | Ref: {data['ref']}", styles["Normal"]))
    story.append(Spacer(1, 5*mm))

    # Map
    img = RLImage(io.BytesIO(map_png), width=170*mm, height=130*mm)
    img.hAlign = "CENTER"
    story.append(img)
    story.append(Spacer(1, 5*mm))

    # Tables
    story.append(Paragraph("<b>Zone Allocation & Capacity</b>", styles["Heading2"]))
    t_data = [["Zone", "%", "Area (m²)", "Capacity"]]
    for z in data["zones"]:
        cap = f"~{z['capacity']}" if z['capacity'] else "-"
        t_data.append([z["name"], f"{z['frac']*100:.1f}%", f"{z['sqm']:,.0f}", cap])
    
    tbl = Table(t_data, colWidths=[70*mm, 15*mm, 35*mm, 30*mm])
    tbl.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), C_DARK), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                             ("GRID", (0,0), (-1,-1), 0.5, colors.grey), ("FONTSIZE", (0,0), (-1,-1), 8)]))
    story.append(tbl)
    story.append(Spacer(1, 5*mm))

    # Infrastructure
    story.append(Paragraph("<b>Infrastructure & Specs</b>", styles["Heading2"]))
    i_data = [["Item", "Status", "Specification"]]
    for r in data["infra_rows"]: i_data.append(r)
    itbl = Table(i_data, colWidths=[50*mm, 30*mm, 90*mm])
    itbl.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), C_GREEN), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                              ("GRID", (0,0), (-1,-1), 0.5, colors.grey), ("FONTSIZE", (0,0), (-1,-1), 8)]))
    story.append(itbl)
    story.append(Spacer(1, 5*mm))

    # Tips
    story.append(Paragraph("<b>Expert Management Tips</b>", styles["Heading2"]))
    for t in data["tips"]:
        story.append(Paragraph(f"• {t}", styles["Normal"]))
    story.append(Spacer(1, 10*mm))

    # DISCLAIMER (English, Bold, Clear)
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceBefore=5, spaceAfter=5))
    disclaimer = (
        "<b>LEGAL DISCLAIMER:</b><br/>"
        "This site plan and layout document are generated for conceptual planning and informational purposes only. "
        "All area allocations, dimensions, and capacity estimates are approximations based on standard agricultural guidelines. "
        "Actual site requirements may vary significantly due to topography, soil conditions, local zoning laws, and specific breed needs. "
        "Before commencing any construction or land development, this plan must be verified and approved by a qualified land surveyor, "
        "civil engineer, or agricultural consultant. The developer assumes no liability for errors, omissions, or damages resulting "
        "from the use of this document."
    )
    story.append(Paragraph(disclaimer, styles["Normal"]))

    doc.build(story)
    buf.seek(0)
    return buf.read()

# =============================================================================
# STREAMLIT UI
# =============================================================================
def main():
    st.set_page_config(page_title="FarmPlan Pro", page_icon="🌾", layout="wide")
    st.markdown("<style> .stApp {background: #F0F4F8;} .sidebar .sidebar-content {background: #1A237E; color: white;} </style>", unsafe_allow_html=True)
    
    st.markdown("<div style='background:#1A237E; padding:20px; border-radius:10px; color:white;'><h1>🌾 FarmPlan Pro v3.0</h1><p>Architectural Blueprint Generator</p></div>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("<h3 style='color:white'>⚙️ Configuration</h3>", unsafe_allow_html=True)
        land_size = st.number_input("Land Size", 0.5, 500.0, 2.0, 0.5)
        unit = st.selectbox("Unit", ["Acres", "Hectares"])
        land_acres = land_size if unit == "Acres" else land_size * 2.47105
        
        country = st.selectbox("Country", COUNTRIES)
        farm_type = st.selectbox("Farm Type", FARM_TYPES)
        
        st.markdown("<h4 style='color:white'>🐄 Animals</h4>", unsafe_allow_html=True)
        mc = st.number_input("Cows", 0, 500, 10)
        dc = st.number_input("Dry Cows", 0, 500, 4)
        cl = st.number_input("Calves", 0, 500, 6)
        gt = st.number_input("Goats", 0, 2000, 0)
        ck = st.number_input("Poultry", 0, 10000, 0)
        
        st.markdown("<h4 style='color:white'>🏗️ Infra</h4>", unsafe_allow_html=True)
        milking = st.checkbox("Milking", True)
        iso = st.checkbox("Isolation", True)
        fod = st.checkbox("Feed Store", True)
        budget = st.radio("Budget", BUDGET_LEVELS, index=1)
        
        if st.button("🚀 Generate Premium Plan", use_container_width=True):
            animals = {"milch_cows": mc, "dry_cows": dc, "calves": cl, "goats": gt, "chickens": ck}
            infra = {"milking": milking, "isolation": iso, "fodder": fod}
            
            with st.spinner("Drawing architectural map..."):
                data = calculate_layout(land_acres, country, farm_type, animals, infra, budget)
                map_img = draw_realistic_map(data)
                pdf = generate_pdf(data, map_img)
            
            st.success("✅ Generated!")
            st.image(map_img, use_column_width=True)
            st.download_button("⬇️ Download PDF", pdf, f"FarmPlan_{farm_type}.pdf", "application/pdf", use_container_width=True)

if __name__ == "__main__":
    main()
