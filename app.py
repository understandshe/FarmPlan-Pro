"""
FARM LAYOUT PDF GENERATOR — Premium Digital Product Tool
Version 2.1 | Production-Ready | Streamlit Cloud Optimized
"""
import io
import math
import datetime
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import matplotlib.patheffects as pe
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage, PageBreak
)

# =============================================================================
# CONSTANTS & CONFIGURATION (Cleaned: No trailing spaces)
# =============================================================================
FARM_TYPES = ["Dairy Farm", "Goat Farming", "Poultry Farm", "Organic Vegetable Farm", "Mixed Homestead"]
COUNTRIES = ["India", "USA", "UK", "Australia", "Canada", "New Zealand", "Brazil", "South Africa", "Kenya", "Germany"]
BUDGET_LEVELS = ["Basic", "Standard", "Premium"]

ANIMAL_SPACE_SQMT = {
    "Dairy Farm": {"milch_cow": 18, "dry_cow": 14, "calf": 6, "heifer": 10, "goat": 4, "chicken": 0.5},
    "Goat Farming": {"milch_cow": 18, "dry_cow": 14, "calf": 6, "heifer": 10, "goat": 3.5, "chicken": 0.5},
    "Poultry Farm": {"milch_cow": 18, "dry_cow": 14, "calf": 6, "heifer": 10, "goat": 4, "chicken": 0.4},
    "Organic Vegetable Farm": {"milch_cow": 18, "dry_cow": 14, "calf": 6, "heifer": 10, "goat": 4, "chicken": 0.5},
    "Mixed Homestead": {"milch_cow": 16, "dry_cow": 12, "calf": 5, "heifer": 9, "goat": 3.5, "chicken": 0.45},
}

COUNTRY_MULTIPLIER = {
    "India": 0.90, "USA": 1.10, "UK": 1.05, "Australia": 1.15,
    "Canada": 1.10, "New Zealand": 1.10, "Brazil": 0.95,
    "South Africa": 0.95, "Kenya": 0.88, "Germany": 1.08,
}

BUDGET_INFRA = {
    "Basic": {"quality": "Standard construction", "flooring": "Packed earth / concrete", "roofing": "GI sheet / tarpaulin"},
    "Standard": {"quality": "Semi-permanent structure", "flooring": "Concrete slab", "roofing": "Asbestos / GI sheet"},
    "Premium": {"quality": "Permanent RCC structure", "flooring": "Anti-slip concrete", "roofing": "Insulated metal roof"},
}

ZONE_COLORS = {
    "Milch Cow Section": "#AED6F1", "Dry Cow Section": "#A9DFBF", "Heifer Section": "#D5DBDB",
    "Calf Pens": "#FAD7A0", "Milking Area": "#D2B4DE", "Fodder / Feed Area": "#F9E79F",
    "Isolation / Sick Pen": "#F1948A", "Bull Pen": "#85C1E9", "Water Points": "#85C1E9",
    "Storage / Barn": "#A9CCE3", "Goat Section": "#ABEBC6", "Poultry House": "#FDEBD0",
    "Veggie Beds": "#A9DFBF", "Compost Area": "#D5F5E3", "Office / Entry": "#EAECEE",
    "Open Yard / Paddock": "#EBF5FB", "Equipment Store": "#CCD1D1",
}

LAYOUT_TEMPLATES = {
    "Dairy Farm": [("Milch Cow Section", 0.25), ("Dry Cow Section", 0.12), ("Heifer Section", 0.10),
                   ("Calf Pens", 0.07), ("Milking Area", 0.08), ("Fodder / Feed Area", 0.12),
                   ("Isolation / Sick Pen", 0.04), ("Storage / Barn", 0.08), ("Office / Entry", 0.04),
                   ("Open Yard / Paddock", 0.10)],
    "Goat Farming": [("Goat Section", 0.35), ("Calf Pens", 0.08), ("Fodder / Feed Area", 0.14),
                     ("Milking Area", 0.07), ("Isolation / Sick Pen", 0.05), ("Storage / Barn", 0.10),
                     ("Compost Area", 0.06), ("Office / Entry", 0.05), ("Open Yard / Paddock", 0.10)],
    "Poultry Farm": [("Poultry House", 0.40), ("Fodder / Feed Area", 0.12), ("Storage / Barn", 0.10),
                     ("Isolation / Sick Pen", 0.05), ("Compost Area", 0.08), ("Equipment Store", 0.07),
                     ("Office / Entry", 0.05), ("Open Yard / Paddock", 0.13)],
    "Organic Vegetable Farm": [("Veggie Beds", 0.45), ("Compost Area", 0.10), ("Fodder / Feed Area", 0.08),
                               ("Storage / Barn", 0.10), ("Water Points", 0.05), ("Equipment Store", 0.07),
                               ("Office / Entry", 0.05), ("Open Yard / Paddock", 0.10)],
    "Mixed Homestead": [("Milch Cow Section", 0.18), ("Goat Section", 0.12), ("Poultry House", 0.10),
                        ("Veggie Beds", 0.15), ("Fodder / Feed Area", 0.10), ("Storage / Barn", 0.09),
                        ("Compost Area", 0.06), ("Calf Pens", 0.05), ("Office / Entry", 0.05),
                        ("Open Yard / Paddock", 0.10)],
}

FARM_TIPS = {
    "Dairy Farm": ["Orient the barn East-West to maximize natural ventilation and reduce heat stress.",
                   "Keep milking parlour adjacent to milch cow section to minimize animal movement.",
                   "Install automated drinking troughs — target 10–15 litres/hr per cow.",
                   "Allocate minimum 15% of total area to fodder storage.",
                   "Grade all floors towards central drainage channels (1:50 slope).",
                   "Maintain 3-metre-wide service lane between cow rows.",
                   "Quarantine new arrivals in Isolation Pen for at least 14 days."],
    "Goat Farming": ["Elevate sleeping platforms 50–60 cm above floor — goats prefer raised areas.",
                     "Use slatted wooden floors to keep hooves dry and reduce foot-rot.",
                     "Separate bucks at minimum 50 metres from does during non-breeding season.",
                     "Plant perimeter windbreaks to reduce cold stress in open yards.",
                     "Install individual feeding stanchions to prevent feed monopolisation.",
                     "Compost goat droppings for 45–60 days before applying to fields.",
                     "Ensure 3–4 sq m of yard space per adult goat for exercise."],
    "Poultry Farm": ["Orient houses North-South in tropical climates for cross-ventilation.",
                     "Maintain 6–8 birds per sq metre for broilers; 4–5 for layers.",
                     "Install curtain ventilation walls — roll up during day, close at night.",
                     "Separate dead-bird disposal area at least 100 metres downwind.",
                     "Use deep-litter system (rice husk/sawdust, 10 cm deep).",
                     "Include footbath with disinfectant at every house entry point.",
                     "Elevate feeders and drinkers to bird back height."],
    "Organic Vegetable Farm": ["Arrange beds in North-South orientation for uniform sunlight.",
                               "Maintain 0.6–0.9 metre working paths between beds.",
                               "Rotate crop families each season (4-block rotation minimum).",
                               "Compost area should receive full sun, 10 metres from water sources.",
                               "Install drip irrigation for water efficiency (40–60% less water).",
                               "Keep toolshed close to entry point — saves 15–20 minutes daily.",
                               "Plant pollinator strip along perimeter to improve yields."],
    "Mixed Homestead": ["Zone livestock downwind from living area and vegetable beds.",
                        "Design pathways so feed, water and manure routes do not cross.",
                        "Use livestock manure composted for 60+ days as fertiliser.",
                        "Install central water header with branch lines to each zone.",
                        "Keep dedicated quarantine zone — biosecurity applies to all species.",
                        "Plan for expansion — leave 15–20% of land unallocated.",
                        "Integrate shade trees along fence lines for dual purpose."]
}

# =============================================================================
# CALCULATION ENGINE
# =============================================================================
def calculate_layout(land_acres, country, farm_type, animals, infra_toggles, budget):
    SQM_PER_ACRE = 4046.86
    SQFT_PER_ACRE = 43560.0
    total_sqm = land_acres * SQM_PER_ACRE
    total_sqft = land_acres * SQFT_PER_ACRE
    
    multiplier = COUNTRY_MULTIPLIER.get(country, 1.0)
    template = LAYOUT_TEMPLATES[farm_type]
    
    zones = []
    for zone_name, fraction in template:
        sqm = total_sqm * fraction
        sqft = total_sqft * fraction
        zones.append({"name": zone_name, "fraction": fraction, "sqm": round(sqm, 1), "sqft": round(sqft, 0), "acres": round(land_acres * fraction, 4)})
    
    space_reqs = ANIMAL_SPACE_SQMT[farm_type]
    adj_space = {k: v * multiplier for k, v in space_reqs.items()}
    
    capacities = {}
    for zone in zones:
        zn = zone["name"]
        if "Milch Cow" in zn: capacities[zn] = max(1, int(zone["sqm"] / adj_space["milch_cow"]))
        elif "Dry Cow" in zn: capacities[zn] = max(1, int(zone["sqm"] / adj_space["dry_cow"]))
        elif "Heifer" in zn: capacities[zn] = max(1, int(zone["sqm"] / adj_space["heifer"]))
        elif "Calf" in zn: capacities[zn] = max(1, int(zone["sqm"] / adj_space["calf"]))
        elif "Goat" in zn: capacities[zn] = max(1, int(zone["sqm"] / adj_space["goat"]))
        elif "Poultry" in zn: capacities[zn] = max(1, int(zone["sqm"] / adj_space["chicken"]))
        else: capacities[zn] = None
    
    infra_details = []
    if infra_toggles.get("milking_area"): infra_details.append(("Milking Area / Parlour", "Included", "Adjacent to milch cow section"))
    if infra_toggles.get("isolation_pen"): infra_details.append(("Isolation / Sick Pen", "Included", "Separate, downwind placement"))
    if infra_toggles.get("fodder_storage"): infra_details.append(("Fodder / Feed Storage", "Included", "Covered, ventilated structure"))
    if infra_toggles.get("water_system"): infra_details.append(("Water Supply System", "Included", "Header tank + distribution lines"))
    if infra_toggles.get("storage_barn"): infra_details.append(("Storage / Barn", "Included", "Dry goods, equipment, feed bags"))
    
    return {
        "land_acres": land_acres, "total_sqm": round(total_sqm, 1), "total_sqft": round(total_sqft, 0),
        "country": country, "farm_type": farm_type, "budget": budget, "zones": zones,
        "capacities": capacities, "animals": animals, "infra_toggles": infra_toggles,
        "infra_details": infra_details, "budget_info": BUDGET_INFRA[budget], "multiplier": multiplier,
        "tips": FARM_TIPS[farm_type], "generated_at": datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")
    }

# =============================================================================
# PREMIUM MAP DRAWING ENGINE
# =============================================================================
def draw_layout_map(layout_data):
    zones = layout_data["zones"]
    farm_type = layout_data["farm_type"]
    country = layout_data["country"]
    acres = layout_data["land_acres"]
    
    fig = plt.figure(figsize=(16, 11), facecolor="#F8F9FA")
    ax = fig.add_subplot(111)
    ax.set_facecolor("#FFFFFF")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title Block
    fig.text(0.5, 0.97, f"PROFESSIONAL FARM LAYOUT PLAN", ha='center', va='center', fontsize=18, fontweight='bold', color="#1A252F")
    fig.text(0.5, 0.945, f"{acres} Acre {farm_type} | {country} | {layout_data['budget']} Budget", ha='center', va='center', fontsize=10, color="#555555")
    
    # Grid Lines
    for i in range(0, 101, 10):
        ax.axhline(i, color="#ECF0F1", linewidth=0.5, zorder=0)
        ax.axvline(i, color="#ECF0F1", linewidth=0.5, zorder=0)
        
    # Border
    ax.add_patch(mpatches.FancyBboxPatch((1, 1), 98, 98, boxstyle="round,pad=0.5", linewidth=2.5, edgecolor="#2C3E50", facecolor="none", zorder=10))
    
    # Layout Zones
    LEFT_X, LEFT_W = 3, 55
    RIGHT_X, RIGHT_W = 60, 37
    TOP_Y, BOTTOM_Y, GAP = 92, 4, 2
    
    prod_keywords = ["Milch", "Dry Cow", "Heifer", "Calf", "Goat", "Poultry", "Veggie"]
    sup_keywords = ["Storage", "Office", "Compost", "Equipment", "Fodder", "Isolation"]
    
    left_zones = [z for z in zones if any(k in z['name'] for k in prod_keywords)] + [z for z in zones if z['name'] in ["Open Yard / Paddock", "Water Points"]]
    right_zones = [z for z in zones if any(k in z['name'] for k in sup_keywords)]
    
    def draw_zone(zone, x, y, w, h):
        color = ZONE_COLORS.get(zone['name'], "#D5D8DC")
        ax.add_patch(mpatches.FancyBboxPatch((x, y-h), w, h, boxstyle="round,pad=0.4", linewidth=1.5, edgecolor="#2C3E50", facecolor=color, zorder=2))
        
        label = zone['name']
        fs = 8 if h > 8 else 7
        ax.text(x + w/2, y - h/2, label, ha='center', va='center', fontsize=fs, fontweight='bold', color="#1A252F", zorder=3, linespacing=1.2)
        ax.text(x + w/2, y - h + 2, f"{zone['sqm']:,.0f} m²", ha='center', va='center', fontsize=6.5, color="#555555", style='italic', zorder=3)
        
        cap = layout_data['capacities'].get(zone['name'])
        if cap:
            ax.text(x + w/2, y - h + 4, f"Cap: ~{cap}", ha='center', va='center', fontsize=6, color="#2980B9", fontweight='bold', zorder=3)
            
    def draw_col(zlist, x_start, c_w):
        total_f = sum(z['fraction'] for z in zlist)
        avail_h = TOP_Y - BOTTOM_Y - GAP * (len(zlist) - 1)
        y_cur = TOP_Y
        for z in zlist:
            h = (z['fraction'] / total_f) * avail_h
            draw_zone(z, x_start, y_cur, c_w, h)
            y_cur -= (h + GAP)
            
    draw_col(left_zones, LEFT_X, LEFT_W)
    draw_col(right_zones, RIGHT_X, RIGHT_W)
    
    # Service Lane
    ax.add_patch(mpatches.FancyBboxPatch((LEFT_X + LEFT_W + 0.5, BOTTOM_Y), RIGHT_X - (LEFT_X + LEFT_W) - 1, TOP_Y - BOTTOM_Y,
                                         boxstyle="square,pad=0", linewidth=0, facecolor="#EBF5FB", alpha=0.6, zorder=1))
    ax.text(LEFT_X + LEFT_W + 29, (TOP_Y + BOTTOM_Y)/2, "SERVICE\nLANE", ha='center', va='center', fontsize=7, color="#2E86C1", fontweight='bold', rotation=90, zorder=5)
    
    # Compass
    cx, cy, r = 95, 93, 3.5
    ax.add_patch(mpatches.Circle((cx, cy), r, fill=False, edgecolor="#2C3E50", linewidth=1.5, zorder=6))
    ax.annotate("N", xy=(cx, cy+r-0.3), xytext=(cx, cy), arrowprops=dict(arrowstyle="->", color="#E74C3C", lw=2), ha='center', va='center', fontsize=9, fontweight='bold', color="#E74C3C", zorder=6)
    
    # Scale Bar
    land_sqm = layout_data['total_sqm']
    side_m = math.sqrt(land_sqm)
    ax.plot([4, 24], [2.5, 2.5], color="#2C3E50", linewidth=2, zorder=7)
    ax.plot([4, 4], [2, 3], color="#2C3E50", linewidth=1.5, zorder=7)
    ax.plot([24, 24], [2, 3], color="#2C3E50", linewidth=1.5, zorder=7)
    ax.plot([14, 14], [2.2, 2.8], color="#2C3E50", linewidth=1, zorder=7)
    ax.text(14, 1.2, f"Scale: 20 units ≈ {(20/100)*side_m:.0f}m", ha='center', va='center', fontsize=7, color="#555555", zorder=7)
    
    # Legend
    patches = [mpatches.Patch(facecolor=ZONE_COLORS.get(z["name"], "#D5D8DC"), edgecolor="#2C3E50", linewidth=0.8, label=z["name"]) for z in zones]
    ax.legend(handles=patches, loc='lower center', bbox_to_anchor=(0.5, -0.05), ncol=5, fontsize=6.5, framealpha=0.9, edgecolor="#BDC3C7", title="Zone Legend", title_fontsize=7.5)
    
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight', facecolor="#F8F9FA")
    plt.close(fig)
    buf.seek(0)
    return buf.read()

# =============================================================================
# PDF GENERATION (Simplified & Robust)
# =============================================================================
C_DARK, C_BLUE, C_GREEN, C_LIGHT, C_GREY, C_ACCENT = colors.HexColor("#1A252F"), colors.HexColor("#2471A3"), colors.HexColor("#1E8449"), colors.HexColor("#EBF5FB"), colors.HexColor("#717D7E"), colors.HexColor("#E67E22")
C_ROW_A, C_ROW_B = colors.HexColor("#EBF5FB"), colors.HexColor("#FDFEFE")

def _build_styles():
    base = getSampleStyleSheet()
    return {
        "doc_title": ParagraphStyle("DocTitle", parent=base["Title"], fontSize=20, textColor=C_WHITE, alignment=TA_CENTER, spaceAfter=4, fontName="Helvetica-Bold"),
        "doc_sub": ParagraphStyle("DocSub", parent=base["Normal"], fontSize=10, textColor=colors.HexColor("#BDC3C7"), alignment=TA_CENTER, spaceAfter=2, fontName="Helvetica"),
        "sec_head": ParagraphStyle("SecHead", parent=base["Heading2"], fontSize=13, textColor=C_BLUE, spaceBefore=14, spaceAfter=6, fontName="Helvetica-Bold"),
        "body": ParagraphStyle("Body", parent=base["Normal"], fontSize=9, textColor=C_DARK, leading=14, fontName="Helvetica"),
        "body_b": ParagraphStyle("BodyB", parent=base["Normal"], fontSize=9, textColor=C_DARK, fontName="Helvetica-Bold"),
        "tip": ParagraphStyle("Tip", parent=base["Normal"], fontSize=8.5, textColor=colors.HexColor("#1B4F72"), leading=13, leftIndent=10, fontName="Helvetica"),
        "foot": ParagraphStyle("Foot", parent=base["Normal"], fontSize=7, textColor=C_GREY, alignment=TA_CENTER, fontName="Helvetica"),
    }

def generate_pdf(ld, map_bytes):
    buf = io.BytesIO()
    stl = _build_styles()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm, title=f"{ld['land_acres']} Acre Plan")
    story = []
    
    # Header
    hdr = Table([[Paragraph(f"{ld['land_acres']} Acre {ld['farm_type']} Layout Plan", stl["doc_title"])], [Paragraph(f"{ld['country']} Edition | Budget: {ld['budget']} | {ld['generated_at']}", stl["doc_sub"])]], colWidths=[170*mm])
    hdr.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), C_DARK), ("TOPPADDING", (0,0), (-1,-1), 14), ("BOTTOMPADDING", (0,-1), (-1,-1), 14), ("ALIGN", (0,0), (-1,-1), "CENTER")]))
    story.append(hdr); story.append(Spacer(1, 8*mm))
    
    # KPIs
    kpis = [(f"{ld['land_acres']:.2f} acres", "Land"), (f"{ld['total_sqm']:,.0f} m²", "Area"), (ld['farm_type'], "Type"), (ld['country'], "Region"), (ld['budget'], "Budget"), ("Included", "Infra")]
    kpi_data = [[Table([[Paragraph(v, ParagraphStyle("kv", fontSize=11, fontName="Helvetica-Bold", textColor=C_BLUE))], [Paragraph(k, ParagraphStyle("kk", fontSize=7.5, fontName="Helvetica", textColor=C_GREY))]], colWidths=[52*mm]) for k,v in kpis[:3]],
                [Table([[Paragraph(v, ParagraphStyle("kv2", fontSize=10, fontName="Helvetica-Bold", textColor=C_GREEN))], [Paragraph(k, ParagraphStyle("kk2", fontSize=7.5, fontName="Helvetica", textColor=C_GREY))]], colWidths=[52*mm]) for k,v in kpis[3:]]]
    kpi_tbl = Table(kpi_data, colWidths=[56*mm, 56*mm, 56*mm])
    kpi_tbl.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), C_LIGHT), ("BOX", (0,0), (-1,-1), 0.8, C_BLUE), ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#BDC3C7")), ("ALIGN", (0,0), (-1,-1), "CENTER")]))
    story.append(kpi_tbl); story.append(Spacer(1, 6*mm))
    
    # Map
    story.append(Paragraph("Farm Layout Map", stl["sec_head"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceAfter=4))
    rl_img = RLImage(io.BytesIO(map_bytes), width=170*mm, height=110*mm)
    rl_img.hAlign = "CENTER"
    story.append(rl_img); story.append(Spacer(1, 4*mm))
    story.append(Paragraph(f"<i>Top-view 2D layout for {ld['land_acres']}-acre {ld['farm_type']} in {ld['country']}.</i>", ParagraphStyle("cap", fontSize=7.5, textColor=C_GREY, alignment=TA_CENTER, fontName="Helvetica-Oblique")))
    story.append(PageBreak())
    
    # Tables & Tips (Standardized)
    for title, rows, cols, h_color in [("Section Allocation", [[z["name"], f"{z['fraction']*100:.1f}%", f"{z['sqm']:,.1f}", f"{z['sqft']:,.0f}", f"~{layout_data['capacities'].get(z['name'], 'N/A')}"] for z in ld["zones"]], [65, 22, 28, 28, 32], C_DARK),
                                       ("Infrastructure", [[ld["budget_info"]["quality"], "Defined", "Semi-permanent"], ["Milking Area", "Included", "Adjacent to cows"]] + [[i,s,n] for i,s,n in ld["infra_details"]], [55, 28, 92], C_GREEN)]:
        story.append(Paragraph(title, stl["sec_head"]))
        story.append(HRFlowable(width="100%", thickness=1, color=h_color, spaceAfter=4))
        tbl = Table([["Zone/Item", "Share/Status", "Area(m²)", "Area(sqft)", "Capacity"]] if title=="Section Allocation" else [["Item", "Status", "Note"]] + rows, colWidths=[c*mm for c in cols], repeatRows=1)
        tbl.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), h_color), ("TEXTCOLOR", (0,0), (-1,0), C_WHITE), ("ROWBACKGROUNDS", (0,1), (-1,-1), [C_ROW_A, C_ROW_B]), ("BOX", (0,0), (-1,-1), 0.8, C_DARK), ("ALIGN", (0,0), (-1,-1), "LEFT")]))
        story.append(tbl); story.append(Spacer(1, 6*mm))
        
    story.append(Paragraph("Expert Tips", stl["sec_head"]))
    for i, t in enumerate(ld["tips"], 1):
        story.append(Table([[Paragraph(f"<b>{i:02d}</b>", ParagraphStyle("n", fontSize=10, fontName="Helvetica-Bold", textColor=C_ACCENT)), Paragraph(t, stl["tip"])]], colWidths=[12*mm, 155*mm], spaceBefore=2, spaceAfter=2))
        
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_GREY, spaceBefore=8))
    story.append(Paragraph("This plan is generated based on standard agricultural guidelines. Verify with a local engineer before construction.", stl["foot"]))
    
    doc.build(story)
    buf.seek(0)
    return buf.read()

# =============================================================================
# STREAMLIT UI
# =============================================================================
def main():
    st.set_page_config(page_title="FarmPlan Pro", page_icon="🌾", layout="wide")
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #F0F4F8; }
    .stButton > button { background: linear-gradient(135deg, #2471A3 0%, #1A252F 100%); color: white; border: none; border-radius: 8px; padding: 0.65rem 2rem; font-size: 1rem; font-weight: 600; width: 100%; }
    .stDownloadButton > button { background: linear-gradient(135deg, #1E8449 0%, #145A32 100%); color: white; border: none; border-radius: 8px; padding: 0.65rem 2rem; font-size: 1rem; font-weight: 600; width: 100%; }
    .metric-card { background: white; border-radius: 10px; padding: 1rem 1.2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.07); margin-bottom: 0.5rem; border-left: 4px solid #2471A3; }
    .metric-card .val { font-size: 1.4rem; font-weight: 700; color: #2471A3; }
    .metric-card .lbl { font-size: 0.75rem; color: #717D7E; }
    </style>""", unsafe_allow_html=True)
    
    st.markdown('<div style="background:linear-gradient(135deg,#1A252F 0%,#2471A3 100%); padding:1.5rem 2rem; border-radius:12px; margin-bottom:1.5rem;"><h1 style="color:white;margin:0;font-size:2rem;">🌾 FarmPlan Pro</h1><p style="color:#AED6F1;margin:0.4rem 0 0;">Premium Engineering-Style Farm Layout Generator</p></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        col_a, col_b = st.columns(2)
        with col_a: land_size = st.number_input("Land Size", 0.5, 500.0, 2.0, 0.5)
        with col_b: land_unit = st.selectbox("Unit", ["Acres", "Hectares"])
        land_acres = land_size if land_unit == "Acres" else land_size * 2.47105
        country = st.selectbox("Country", COUNTRIES, index=0)
        farm_type = st.selectbox("Farm Type", FARM_TYPES, index=0)
        
        st.markdown("### 🐄 Animals")
        mc = st.number_input("Milch Cows", 0, 500, 10, 1)
        dc = st.number_input("Dry Cows", 0, 500, 4, 1)
        cl = st.number_input("Calves", 0, 500, 6, 1)
        gt = st.number_input("Goats", 0, 1000, 0, 5)
        ck = st.number_input("Chickens", 0, 5000, 0, 25)
        
        st.markdown("### 🏗️ Infra")
        milking = st.checkbox("Milking Area", True)
        iso = st.checkbox("Isolation Pen", True)
        fod = st.checkbox("Fodder Storage", True)
        wat = st.checkbox("Water System", True)
        strg = st.checkbox("Storage Barn", True)
        budget = st.radio("Budget", BUDGET_LEVELS, index=1, horizontal=True)
        
        if st.button("🚀 Generate Farm Plan", width="stretch"):
            with st.spinner("Generating premium plan…"):
                animals = {"milch_cows": mc, "dry_cows": dc, "calves": cl, "goats": gt, "chickens": ck}
                infra = {"milking_area": milking, "isolation_pen": iso, "fodder_storage": fod, "water_system": wat, "storage_barn": strg}
                ld = calculate_layout(land_acres, country, farm_type, animals, infra, budget)
                map_png = draw_layout_map(ld)
                pdf_bytes = generate_pdf(ld, map_png)
                
            st.success("✅ Generated Successfully!")
            c1, c2, c3, c4 = st.columns(4)
            for col, val, lbl in [(c1, f"{ld['land_acres']:.2f} acres", "Land"), (c2, f"{ld['total_sqm']:,.0f} m²", "Area"), (c3, f"{ld['total_sqft']:,.0f} sqft", "Sq Ft"), (c4, ld['budget'], "Budget")]:
                col.markdown(f'<div class="metric-card"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)
                
            col_map, col_info = st.columns([3, 2])
            with col_map:
                st.markdown("### 🗺️ Layout Preview")
                st.image(map_png, caption=f"{land_size} {land_unit} {farm_type} – {country}", width="stretch")
            with col_info:
                st.markdown("### 📊 Zones")
                for z in ld["zones"]:
                    st.markdown(f"**{z['name']}** — {z['fraction']*100:.1f}% ({z['sqm']:,.0f} m²)")
                    st.progress(z['fraction'])
                    
            st.download_button("⬇️ Download Premium PDF", pdf_bytes, f"FarmPlan_{farm_type.replace(' ','_')}_{country}.pdf", "application/pdf", width="stretch")
    else:
        st.markdown('<div style="text-align:center; padding:3rem 1rem; color:#717D7E;"><h2 style="color:#2471A3;">Welcome to FarmPlan Pro</h2><p>Configure details in sidebar & generate a sellable architectural farm plan.</p></div>', unsafe_allow_html=True)

# =============================================================================
# ENTRY POINT (FIXED INDENTATION)
# =============================================================================
if __name__ == "__main__":
    main()
