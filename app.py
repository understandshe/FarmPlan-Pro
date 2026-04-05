"""
FARM LAYOUT PDF GENERATOR — Premium Digital Product Tool
Version 2.0 | Professional Architecture-Style Farm Plans
Generates engineering-style, sellable farm layout PDFs
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
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage, PageBreak
)

# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================
FARM_TYPES = [
    "Dairy Farm",
    "Goat Farming",
    "Poultry Farm",
    "Organic Vegetable Farm",
    "Mixed Homestead",
]

COUNTRIES = [
    "India", "USA", "UK", "Australia", "Canada",
    "New Zealand", "Brazil", "South Africa", "Kenya", "Germany",
]

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
    "Milch Cow Section": "#AED6F1",
    "Dry Cow Section": "#A9DFBF",
    "Heifer Section": "#D5DBDB",
    "Calf Pens": "#FAD7A0",
    "Milking Area": "#D2B4DE",
    "Fodder / Feed Area": "#F9E79F",
    "Isolation / Sick Pen": "#F1948A",
    "Bull Pen": "#85C1E9",
    "Water Points": "#85C1E9",
    "Storage / Barn": "#A9CCE3",
    "Goat Section": "#ABEBC6",
    "Poultry House": "#FDEBD0",
    "Veggie Beds": "#A9DFBF",
    "Compost Area": "#D5F5E3",
    "Office / Entry": "#EAECEE",
    "Open Yard / Paddock": "#EBF5FB",
    "Equipment Store": "#CCD1D1",
}

SECTION_EDGE_COLOR = "#2C3E50"

LAYOUT_TEMPLATES = {
    "Dairy Farm": [
        ("Milch Cow Section", 0.25),
        ("Dry Cow Section", 0.12),
        ("Heifer Section", 0.10),
        ("Calf Pens", 0.07),
        ("Milking Area", 0.08),
        ("Fodder / Feed Area", 0.12),
        ("Isolation / Sick Pen", 0.04),
        ("Storage / Barn", 0.08),
        ("Office / Entry", 0.04),
        ("Open Yard / Paddock", 0.10),
    ],
    "Goat Farming": [
        ("Goat Section", 0.35),
        ("Calf Pens", 0.08),
        ("Fodder / Feed Area", 0.14),
        ("Milking Area", 0.07),
        ("Isolation / Sick Pen", 0.05),
        ("Storage / Barn", 0.10),
        ("Compost Area", 0.06),
        ("Office / Entry", 0.05),
        ("Open Yard / Paddock", 0.10),
    ],
    "Poultry Farm": [
        ("Poultry House", 0.40),
        ("Fodder / Feed Area", 0.12),
        ("Storage / Barn", 0.10),
        ("Isolation / Sick Pen", 0.05),
        ("Compost Area", 0.08),
        ("Equipment Store", 0.07),
        ("Office / Entry", 0.05),
        ("Open Yard / Paddock", 0.13),
    ],
    "Organic Vegetable Farm": [
        ("Veggie Beds", 0.45),
        ("Compost Area", 0.10),
        ("Fodder / Feed Area", 0.08),
        ("Storage / Barn", 0.10),
        ("Water Points", 0.05),
        ("Equipment Store", 0.07),
        ("Office / Entry", 0.05),
        ("Open Yard / Paddock", 0.10),
    ],
    "Mixed Homestead": [
        ("Milch Cow Section", 0.18),
        ("Goat Section", 0.12),
        ("Poultry House", 0.10),
        ("Veggie Beds", 0.15),
        ("Fodder / Feed Area", 0.10),
        ("Storage / Barn", 0.09),
        ("Compost Area", 0.06),
        ("Calf Pens", 0.05),
        ("Office / Entry", 0.05),
        ("Open Yard / Paddock", 0.10),
    ],
}

FARM_TIPS = {
    "Dairy Farm": [
        "Orient the barn East-West to maximize natural ventilation and reduce heat stress.",
        "Keep milking parlour adjacent to milch cow section to minimize animal movement.",
        "Install automated drinking troughs — target 10–15 litres/hr per cow.",
        "Allocate minimum 15% of total area to fodder storage.",
        "Grade all floors towards central drainage channels (1:50 slope).",
        "Maintain 3-metre-wide service lane between cow rows.",
        "Quarantine new arrivals in Isolation Pen for at least 14 days.",
    ],
    "Goat Farming": [
        "Elevate sleeping platforms 50–60 cm above floor — goats prefer raised areas.",
        "Use slatted wooden floors to keep hooves dry and reduce foot-rot.",
        "Separate bucks at minimum 50 metres from does during non-breeding season.",
        "Plant perimeter windbreaks to reduce cold stress in open yards.",
        "Install individual feeding stanchions to prevent feed monopolisation.",
        "Compost goat droppings for 45–60 days before applying to fields.",
        "Ensure 3–4 sq m of yard space per adult goat for exercise.",
    ],
    "Poultry Farm": [
        "Orient houses North-South in tropical climates for cross-ventilation.",
        "Maintain 6–8 birds per sq metre for broilers; 4–5 for layers.",
        "Install curtain ventilation walls — roll up during day, close at night.",
        "Separate dead-bird disposal area at least 100 metres downwind.",
        "Use deep-litter system (rice husk/sawdust, 10 cm deep).",
        "Include footbath with disinfectant at every house entry point.",
        "Elevate feeders and drinkers to bird back height.",
    ],
    "Organic Vegetable Farm": [
        "Arrange beds in North-South orientation for uniform sunlight.",
        "Maintain 0.6–0.9 metre working paths between beds.",
        "Rotate crop families each season (4-block rotation minimum).",
        "Compost area should receive full sun, 10 metres from water sources.",
        "Install drip irrigation for water efficiency (40–60% less water).",
        "Keep toolshed close to entry point — saves 15–20 minutes daily.",
        "Plant pollinator strip along perimeter to improve yields.",
    ],
    "Mixed Homestead": [
        "Zone livestock downwind from living area and vegetable beds.",
        "Design pathways so feed, water and manure routes do not cross.",
        "Use livestock manure composted for 60+ days as fertiliser.",
        "Install central water header with branch lines to each zone.",
        "Keep dedicated quarantine zone — biosecurity applies to all species.",
        "Plan for expansion — leave 15–20% of land unallocated.",
        "Integrate shade trees along fence lines for dual purpose.",
    ],
}

# =============================================================================
# AREA CALCULATION ENGINE
# =============================================================================
def calculate_layout(land_acres: float, country: str, farm_type: str, animals: dict, infra_toggles: dict, budget: str) -> dict:
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
        acres_zone = land_acres * fraction
        zones.append({
            "name": zone_name,
            "fraction": fraction,
            "sqm": round(sqm, 1),
            "sqft": round(sqft, 0),
            "acres": round(acres_zone, 4),
        })
    
    space_reqs = ANIMAL_SPACE_SQMT[farm_type]
    adj_space = {k: v * multiplier for k, v in space_reqs.items()}
    
    capacities = {}
    for zone in zones:
        zn = zone["name"]
        if "Milch Cow" in zn:
            capacities[zn] = max(1, int(zone["sqm"] / adj_space["milch_cow"]))
        elif "Dry Cow" in zn:
            capacities[zn] = max(1, int(zone["sqm"] / adj_space["dry_cow"]))
        elif "Heifer" in zn:
            capacities[zn] = max(1, int(zone["sqm"] / adj_space["heifer"]))
        elif "Calf" in zn:
            capacities[zn] = max(1, int(zone["sqm"] / adj_space["calf"]))
        elif "Goat" in zn:
            capacities[zn] = max(1, int(zone["sqm"] / adj_space["goat"]))
        elif "Poultry" in zn:
            capacities[zn] = max(1, int(zone["sqm"] / adj_space["chicken"]))
        else:
            capacities[zn] = None
    
    infra_details = []
    if infra_toggles.get("milking_area"):
        infra_details.append(("Milking Area / Parlour", "Included", "Adjacent to milch cow section"))
    if infra_toggles.get("isolation_pen"):
        infra_details.append(("Isolation / Sick Pen", "Included", "Separate, downwind placement"))
    if infra_toggles.get("fodder_storage"):
        infra_details.append(("Fodder / Feed Storage", "Included", "Covered, ventilated structure"))
    if infra_toggles.get("water_system"):
        infra_details.append(("Water Supply System", "Included", "Header tank + distribution lines"))
    if infra_toggles.get("storage_barn"):
        infra_details.append(("Storage / Barn", "Included", "Dry goods, equipment, feed bags"))
    
    budget_info = BUDGET_INFRA[budget]
    
    return {
        "land_acres": land_acres,
        "total_sqm": round(total_sqm, 1),
        "total_sqft": round(total_sqft, 0),
        "country": country,
        "farm_type": farm_type,
        "budget": budget,
        "zones": zones,
        "capacities": capacities,
        "animals": animals,
        "infra_toggles": infra_toggles,
        "infra_details": infra_details,
        "budget_info": budget_info,
        "multiplier": multiplier,
        "tips": FARM_TIPS[farm_type],
        "generated_at": datetime.datetime.now().strftime("%d %B %Y, %I:%M %p"),
    }

# =============================================================================
# PROFESSIONAL LAYOUT MAP DRAWING ENGINE
# =============================================================================
def draw_layout_map(layout_data: dict) -> bytes:
    zones = layout_data["zones"]
    farm_type = layout_data["farm_type"]
    country = layout_data["country"]
    acres = layout_data["land_acres"]
    
    fig = plt.figure(figsize=(16, 11), facecolor="#FAFAFA")
    gs = fig.add_gridspec(3, 1, height_ratios=[0.8, 12, 0.8], hspace=0.02)
    
    ax_title = fig.add_subplot(gs[0])
    ax_title.axis('off')
    ax_title.text(0.5, 0.5, 
                  f"PROFESSIONAL FARM LAYOUT PLAN",
                  ha='center', va='center', 
                  fontsize=18, fontweight='bold', 
                  color="#1A252F")
    ax_title.text(0.5, 0.2,
                  f"{acres} Acre {farm_type} | {country} | {layout_data['budget']} Budget",
                  ha='center', va='center',
                  fontsize=10, color="#555555")
    
    ax = fig.add_subplot(gs[1])
    ax.set_facecolor("#FFFFFF")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Double border
    ax.add_patch(mpatches.FancyBboxPatch((1, 1), 98, 98,
        boxstyle="round,pad=0.5", linewidth=3, edgecolor="#2C3E50", 
        facecolor="none", zorder=10))
    ax.add_patch(mpatches.FancyBboxPatch((2, 2), 96, 96,
        boxstyle="round,pad=0.3", linewidth=1, edgecolor="#95A5A6", 
        facecolor="none", zorder=10))
    
    # Grid lines
    for i in range(0, 101, 10):
        ax.axhline(i, color="#ECF0F1", linewidth=0.5, zorder=0)
        ax.axvline(i, color="#ECF0F1", linewidth=0.5, zorder=0)
    
    LEFT_X, LEFT_W = 3, 55
    RIGHT_X, RIGHT_W = 60, 37
    TOP_Y = 96
    BOTTOM_Y = 3
    GAP = 2
    
    production_keywords = ["Milch", "Dry Cow", "Heifer", "Calf", "Goat", "Poultry", "Veggie"]
    support_keywords = ["Storage", "Office", "Compost", "Equipment", "Fodder", "Isolation"]
    
    production_zones = [z for z in zones if any(k in z['name'] for k in production_keywords)]
    support_zones = [z for z in zones if any(k in z['name'] for k in support_keywords)]
    other_zones = [z for z in zones if z not in production_zones and z not in support_zones]
    
    def draw_premium_zone(zone, x, y, width, height):
        color = ZONE_COLORS.get(zone['name'], "#D5D8DC")
        
        # Shadow effect
        ax.add_patch(mpatches.FancyBboxPatch((x+0.5, y-0.5-height), width, height,
            boxstyle="round,pad=0.4", linewidth=0, facecolor="#000000", alpha=0.1, zorder=1))
        
        # Main rectangle
        rect = mpatches.FancyBboxPatch((x, y-height), width, height,
            boxstyle="round,pad=0.4", linewidth=2, edgecolor="#2C3E50",
            facecolor=color, zorder=2)
        ax.add_patch(rect)
        
        # Label
        words = zone['name'].split()
        if len(words) > 3:
            label = " ".join(words[:2]) + "\n" + " ".join(words[2:])
            fontsize = 7
        elif len(words) > 2:
            label = " ".join(words[:2]) + "\n" + words[2]
            fontsize = 7.5
        else:
            label = zone['name']
            fontsize = 8.5 if height > 8 else 7
        
        label_y = y - height/2
        ax.add_patch(mpatches.FancyBboxPatch((x+width*0.1, label_y-2), width*0.8, 4,
            boxstyle="round,pad=0.3", linewidth=0, facecolor="#FFFFFF", alpha=0.9, zorder=3))
        
        ax.text(x + width/2, label_y, label, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color="#1A252F", zorder=4)
        
        ax.text(x + width/2, y - height + 1.5, f"{zone['sqm']:,.0f} m²",
                ha='center', va='center', fontsize=6.5, color="#555555",
                style='italic', zorder=4)
        
        cap = layout_data['capacities'].get(zone['name'])
        if cap:
            ax.text(x + width/2, y - height + 3.5, f"Capacity: ~{cap}",
                    ha='center', va='center', fontsize=6, color="#2E86C1",
                    fontweight='bold', zorder=4)
    
    left_zones = production_zones + other_zones[:len(other_zones)//2]
    right_zones = support_zones + other_zones[len(other_zones)//2:]
    
    def draw_column(zone_list, x_start, col_width):
        total_frac = sum(z['fraction'] for z in zone_list)
        available_h = TOP_Y - BOTTOM_Y - GAP * (len(zone_list) - 1)
        y_cursor = TOP_Y
        
        for z in zone_list:
            h = (z['fraction'] / total_frac) * available_h
            draw_premium_zone(z, x_start, y_cursor, col_width, h)
            y_cursor -= (h + GAP)
    
    draw_column(left_zones, LEFT_X, LEFT_W)
    draw_column(right_zones, RIGHT_X, RIGHT_W)
    
    # Service lane
    ax.add_patch(mpatches.FancyBboxPatch((LEFT_X + LEFT_W + 0.5, BOTTOM_Y),
        RIGHT_X - (LEFT_X + LEFT_W) - 1, TOP_Y - BOTTOM_Y,
        boxstyle="square,pad=0", linewidth=0, facecolor="#EBF5FB", alpha=0.6, zorder=1))
    
    for y in range(10, 95, 10):
        ax.plot([LEFT_X + LEFT_W + 29, LEFT_X + LEFT_W + 29], 
                [y, y+5], '--', color="#3498DB", linewidth=1.5, alpha=0.6)
    
    ax.text(LEFT_X + LEFT_W + 29, (TOP_Y + BOTTOM_Y)/2,
            "MAIN\nSERVICE\nLANE\n(6m wide)",
            ha='center', va='center', fontsize=7, color="#2E86C1",
            fontweight='bold', rotation=90, zorder=5)
    
    # Flow arrows
    for ay_pos in [80, 60, 40, 20]:
        ax.annotate("", xy=(LEFT_X + LEFT_W - 1, ay_pos - 5),
                    xytext=(LEFT_X + LEFT_W - 1, ay_pos),
                    arrowprops=dict(arrowstyle="->", color="#E74C3C", 
                                   lw=2, shrinkA=0, shrinkB=0), zorder=5)
    
    # North arrow
    cx, cy, r = 94, 94, 4
    ax.add_patch(mpatches.Circle((cx, cy), r, fill=False, 
                                  edgecolor="#2C3E50", linewidth=1.5, zorder=6))
    ax.annotate("", xy=(cx, cy+r-0.5), xytext=(cx, cy),
                arrowprops=dict(arrowstyle="->", color="#E74C3C", 
                               lw=2.5, shrinkA=0, shrinkB=0), zorder=6)
    ax.text(cx, cy+r+0.8, "N", ha='center', va='center',
            fontsize=9, fontweight='bold', color="#E74C3C", zorder=6)
    
    # Scale bar
    land_sqm = layout_data['total_sqm']
    side_m = math.sqrt(land_sqm)
    scale_width = 20
    
    ax.add_patch(mpatches.FancyBboxPatch((3, 0.5), 25, 3,
        boxstyle="round,pad=0.2", linewidth=0, facecolor="#FFFFFF", alpha=0.9, zorder=7))
    
    ax.plot([4, 24], [2, 2], '-', color="#2C3E50", linewidth=2, zorder=7)
    ax.plot([4, 4], [1.5, 2.5], '-', color="#2C3E50", linewidth=1.5, zorder=7)
    ax.plot([24, 24], [1.5, 2.5], '-', color="#2C3E50", linewidth=1.5, zorder=7)
    ax.plot([14, 14], [1.7, 2.3], '-', color="#2C3E50", linewidth=1, zorder=7)
    
    actual_m = (scale_width / 100) * side_m
    ax.text(14, 0.8, f"Scale: {scale_width} units = {actual_m:.0f}m",
            ha='center', va='center', fontsize=7, color="#555555", zorder=7)
    
    # Legend
    legend_patches = []
    for z in zones:
        color = ZONE_COLORS.get(z['name'], "#D5D8DC")
        patch = mpatches.Patch(facecolor=color, edgecolor="#2C3E50", 
                              linewidth=0.8, label=z['name'])
        legend_patches.append(patch)
    
    ax.legend(handles=legend_patches, loc='lower center',
              bbox_to_anchor=(0.5, -0.15), ncol=6, fontsize=6,
              framealpha=0.95, edgecolor="#BDC3C7",
              title="ZONE LEGEND", title_fontsize=7.5,
              handletextpad=0.5, borderpad=0.8)
    
    # Info box
    info_text = (f"Total Area: {layout_data['total_sqm']:,.0f} m²\n"
                 f"            {layout_data['total_sqft']:,.0f} sq ft\n"
                 f"Generated: {layout_data['generated_at']}")
    
    ax.add_patch(mpatches.FancyBboxPatch((68, 0.5), 30, 5,
        boxstyle="round,pad=0.4", linewidth=1, edgecolor="#95A5A6",
        facecolor="#FFFFFF", alpha=0.95, zorder=8))
    ax.text(83, 3, info_text, ha='center', va='center',
            fontsize=7, color="#555555", zorder=8, family='monospace')
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.97])
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()

# =============================================================================
# PDF GENERATION (बाकी का code same रहेगा - सिर्फ colors update करें)
# =============================================================================
C_DARK   = colors.HexColor("#1A252F")
C_BLUE   = colors.HexColor("#2471A3")
C_GREEN  = colors.HexColor("#1E8449")
C_LIGHT  = colors.HexColor("#EBF5FB")
C_GREY   = colors.HexColor("#717D7E")
C_WHITE  = colors.white
C_ACCENT = colors.HexColor("#E67E22")
C_ROW_A  = colors.HexColor("#EBF5FB")
C_ROW_B  = colors.HexColor("#FDFEFE")

def _build_styles():
    base = getSampleStyleSheet()
    return {
        "doc_title": ParagraphStyle("DocTitle", parent=base["Title"],
            fontSize=22, textColor=C_WHITE, alignment=TA_CENTER,
            spaceAfter=4, spaceBefore=4, fontName="Helvetica-Bold"),
        "doc_subtitle": ParagraphStyle("DocSubtitle", parent=base["Normal"],
            fontSize=10, textColor=colors.HexColor("#BDC3C7"),
            alignment=TA_CENTER, spaceAfter=2, fontName="Helvetica"),
        "section_heading": ParagraphStyle("SectionHeading", parent=base["Heading2"],
            fontSize=13, textColor=C_BLUE, spaceBefore=14, spaceAfter=6,
            fontName="Helvetica-Bold"),
        "sub_heading": ParagraphStyle("SubHeading", parent=base["Heading3"],
            fontSize=10, textColor=C_DARK, spaceBefore=8, spaceAfter=4,
            fontName="Helvetica-Bold"),
        "body": ParagraphStyle("Body", parent=base["Normal"],
            fontSize=9, textColor=C_DARK, leading=14, fontName="Helvetica"),
        "body_bold": ParagraphStyle("BodyBold", parent=base["Normal"],
            fontSize=9, textColor=C_DARK, fontName="Helvetica-Bold"),
        "tip": ParagraphStyle("Tip", parent=base["Normal"],
            fontSize=8.5, textColor=colors.HexColor("#1B4F72"),
            leading=13, leftIndent=10, fontName="Helvetica"),
        "footer": ParagraphStyle("Footer", parent=base["Normal"],
            fontSize=7, textColor=C_GREY, alignment=TA_CENTER,
            fontName="Helvetica"),
    }

def _header_block(styles, layout_data):
    story = []
    title_text = f"{layout_data['land_acres']} Acre {layout_data['farm_type']} Layout Plan"
    subtitle_text = f"{layout_data['country']} Edition | Budget: {layout_data['budget']} | {layout_data['generated_at']}"
    
    header_table = Table([
        [Paragraph(title_text, styles["doc_title"])],
        [Paragraph(subtitle_text, styles["doc_subtitle"])],
    ], colWidths=[170 * mm])
    
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 14),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8 * mm))
    return story

def _summary_bar(styles, layout_data):
    story = []
    kpis = [
        ("Total Land Area", f"{layout_data['land_acres']} acres"),
        ("Total Area (m²)", f"{layout_data['total_sqm']:,.0f} m²"),
        ("Total Area (sqft)", f"{layout_data['total_sqft']:,.0f} sq ft"),
        ("Farm Type", layout_data["farm_type"]),
        ("Region/Country", layout_data["country"]),
        ("Budget Level", layout_data["budget"]),
    ]
    
    data = [[
        Table([[Paragraph(v, ParagraphStyle("kv", fontSize=11, fontName="Helvetica-Bold", textColor=C_BLUE))],
               [Paragraph(k, ParagraphStyle("kk", fontSize=7.5, fontName="Helvetica", textColor=C_GREY))]],
              colWidths=[52 * mm])
        for k, v in kpis[:3]
    ], [
        Table([[Paragraph(v, ParagraphStyle("kv2", fontSize=10, fontName="Helvetica-Bold", textColor=C_GREEN))],
               [Paragraph(k, ParagraphStyle("kk2", fontSize=7.5, fontName="Helvetica", textColor=C_GREY))]],
              colWidths=[52 * mm])
        for k, v in kpis[3:]
    ]]
    
    kpi_table = Table(data, colWidths=[56 * mm, 56 * mm, 56 * mm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.8, C_BLUE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 6 * mm))
    return story

def _area_table(styles, layout_data):
    story = []
    story.append(Paragraph("Section-wise Area Allocation", styles["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceAfter=4))
    
    header_row = [
        Paragraph("<b>Zone / Section</b>", styles["body_bold"]),
        Paragraph("<b>% Share</b>", styles["body_bold"]),
        Paragraph("<b>Area (m²)</b>", styles["body_bold"]),
        Paragraph("<b>Area (sq ft)</b>", styles["body_bold"]),
        Paragraph("<b>Animal Capacity</b>", styles["body_bold"]),
    ]
    rows = [header_row]
    
    for i, zone in enumerate(layout_data["zones"]):
        cap = layout_data["capacities"].get(zone["name"])
        cap_str = f"~{cap}" if cap else "N/A"
        row_color = C_ROW_A if i % 2 == 0 else C_ROW_B
        rows.append([
            Paragraph(zone["name"], styles["body"]),
            Paragraph(f"{zone['fraction']*100:.1f}%", styles["body"]),
            Paragraph(f"{zone['sqm']:,.1f}", styles["body"]),
            Paragraph(f"{zone['sqft']:,.0f}", styles["body"]),
            Paragraph(cap_str, styles["body"]),
        ])
    
    tbl = Table(rows, colWidths=[65 * mm, 22 * mm, 28 * mm, 28 * mm, 32 * mm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), C_WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_ROW_A, C_ROW_B]),
        ("BOX", (0, 0), (-1, -1), 0.8, C_DARK),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BDC3C7")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6 * mm))
    return story

def _infra_table(styles, layout_data):
    story = []
    story.append(Paragraph("Infrastructure Specification", styles["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_GREEN, spaceAfter=4))
    
    bi = layout_data["budget_info"]
    infra_rows = [
        [Paragraph("<b>Item</b>", styles["body_bold"]),
         Paragraph("<b>Status</b>", styles["body_bold"]),
         Paragraph("<b>Specification / Note</b>", styles["body_bold"])],
        [Paragraph("Construction Quality", styles["body"]),
         Paragraph("Defined", styles["body"]),
         Paragraph(bi["quality"], styles["body"])],
        [Paragraph("Flooring Type", styles["body"]),
         Paragraph("Defined", styles["body"]),
         Paragraph(bi["flooring"], styles["body"])],
        [Paragraph("Roofing Type", styles["body"]),
         Paragraph("Defined", styles["body"]),
         Paragraph(bi["roofing"], styles["body"])],
    ]
    
    for item_name, status, note in layout_data["infra_details"]:
        infra_rows.append([
            Paragraph(item_name, styles["body"]),
            Paragraph(f'<font color="#1E8449"><b>{status}</b></font>', styles["body"]),
            Paragraph(note, styles["body"]),
        ])
    
    tbl = Table(infra_rows, colWidths=[55 * mm, 28 * mm, 92 * mm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), C_WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_ROW_A, C_ROW_B]),
        ("BOX", (0, 0), (-1, -1), 0.8, C_DARK),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BDC3C7")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6 * mm))
    return story

def _animal_summary(styles, layout_data):
    story = []
    animals = layout_data["animals"]
    if not any(v > 0 for v in animals.values()):
        return story
    
    story.append(Paragraph("Animal Stock Summary (User Inputs)", styles["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_ACCENT, spaceAfter=4))
    
    labels = {
        "milch_cows": "Milch Cows (Lactating)",
        "dry_cows": "Dry Cows",
        "calves": "Calves",
        "goats": "Goats",
        "chickens": "Chickens / Poultry",
    }
    
    animal_rows = [
        [Paragraph("<b>Animal Type</b>", styles["body_bold"]),
         Paragraph("<b>Count</b>", styles["body_bold"]),
         Paragraph("<b>Space Required (m²)</b>", styles["body_bold"])],
    ]
    
    space_map = ANIMAL_SPACE_SQMT[layout_data["farm_type"]]
    mult = layout_data["multiplier"]
    
    for key, label in labels.items():
        count = animals.get(key, 0)
        if count > 0:
            sk = key.replace("_cows", "_cow").replace("milch_cow", "milch_cow").replace("chickens", "chicken")
            sp = space_map.get(sk, space_map.get("milch_cow", 18)) * mult
            animal_rows.append([
                Paragraph(label, styles["body"]),
                Paragraph(str(count), styles["body"]),
                Paragraph(f"{count * sp:,.1f} m²", styles["body"]),
            ])
    
    tbl = Table(animal_rows, colWidths=[80 * mm, 30 * mm, 65 * mm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), C_WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_ROW_A, C_ROW_B]),
        ("BOX", (0, 0), (-1, -1), 0.8, C_DARK),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BDC3C7")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (1, 0), (2, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6 * mm))
    return story

def _tips_section(styles, layout_data):
    story = []
    story.append(Paragraph("Expert Setup & Management Tips", styles["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceAfter=6))
    
    for i, tip in enumerate(layout_data["tips"], 1):
        tip_row = Table([[
            Paragraph(f'<font color="#E67E22"><b>{i:02d}</b></font>',
                     ParagraphStyle("tipnum", fontSize=10, fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph(tip, styles["tip"]),
        ]], colWidths=[12 * mm, 155 * mm])
        
        tip_row.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EBF5FB")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#AED6F1")),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(tip_row)
        story.append(Spacer(1, 3 * mm))
    
    story.append(Spacer(1, 4 * mm))
    return story

def _disclaimer_footer(styles):
    text = ("This farm layout plan is generated based on standard agricultural zoning guidelines. "
            "Actual construction should be verified by a qualified agricultural engineer. "
            "All area figures are approximate.")
    return [
        HRFlowable(width="100%", thickness=0.5, color=C_GREY, spaceBefore=8, spaceAfter=4),
        Paragraph(text, styles["footer"]),
    ]

def generate_pdf(layout_data: dict, map_png_bytes: bytes) -> bytes:
    buf = io.BytesIO()
    styles = _build_styles()
    
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title=f"{layout_data['land_acres']} Acre {layout_data['farm_type']} Plan",
        author="FarmPlan Pro",
    )
    
    story = []
    story += _header_block(styles, layout_data)
    story += _summary_bar(styles, layout_data)
    
    story.append(Paragraph("Farm Layout Map", styles["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceAfter=4))
    
    img_stream = io.BytesIO(map_png_bytes)
    rl_img = RLImage(img_stream, width=170 * mm, height=121 * mm)
    rl_img.hAlign = "CENTER"
    story.append(rl_img)
    story.append(Spacer(1, 4 * mm))
    
    story.append(Paragraph(f"<i>Top-view 2D layout for a {layout_data['land_acres']}-acre {layout_data['farm_type']} "
                          f"in {layout_data['country']}. All zones proportionally sized.</i>",
                          ParagraphStyle("caption", fontSize=7.5, textColor=C_GREY, 
                                        alignment=TA_CENTER, fontName="Helvetica-Oblique")))
    
    story.append(PageBreak())
    story += _area_table(styles, layout_data)
    story += _animal_summary(styles, layout_data)
    story += _infra_table(styles, layout_data)
    story += _tips_section(styles, layout_data)
    story += _disclaimer_footer(styles)
    
    doc.build(story)
    buf.seek(0)
    return buf.read()

# =============================================================================
# STREAMLIT UI
# =============================================================================
def main():
    st.set_page_config(
        page_title="FarmPlan Pro – Premium Farm Layout Generator",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp { background: #F0F4F8; }
        h1 { color: #1A252F; font-weight: 700; }
        .stButton > button {
            background: linear-gradient(135deg, #2471A3 0%, #1A252F 100%);
            color: white; border: none; border-radius: 8px;
            padding: 0.65rem 2rem; font-size: 1rem; font-weight: 600;
            width: 100%;
        }
        .metric-card {
            background: white; border-radius: 10px; padding: 1rem 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.07); margin-bottom: 0.5rem;
            border-left: 4px solid #2471A3;
        }
        .metric-card .val { font-size: 1.4rem; font-weight: 700; color: #2471A3; }
        .metric-card .lbl { font-size: 0.75rem; color: #717D7E; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background:linear-gradient(135deg,#1A252F 0%,#2471A3 100%);
                    padding:1.5rem 2rem; border-radius:12px; margin-bottom:1.5rem;">
            <h1 style="color:white;margin:0;font-size:2rem;">🌾 FarmPlan Pro</h1>
            <p style="color:#AED6F1;margin:0.4rem 0 0;">
                Premium Engineering-Style Farm Layout Generator
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## ⚙️ Farm Configuration")
        st.markdown("---")
        
        st.markdown("### 📐 Land & Location")
        col_a, col_b = st.columns(2)
        with col_a:
            land_size = st.number_input("Land Size", min_value=0.5, max_value=500.0, value=2.0, step=0.5)
        with col_b:
            land_unit = st.selectbox("Unit", ["Acres", "Hectares"])
        
        land_acres = land_size if land_unit == "Acres" else land_size * 2.47105
        country = st.selectbox("Country / Region", COUNTRIES, index=0)
        farm_type = st.selectbox("Farm Type", FARM_TYPES, index=0)
        
        st.markdown("### 🐄 Animal Count")
        milch_cows = st.number_input("Milch Cows", 0, 500, 10, 1)
        dry_cows = st.number_input("Dry Cows", 0, 500, 4, 1)
        calves = st.number_input("Calves", 0, 500, 6, 1)
        goats = st.number_input("Goats", 0, 1000, 0, 5)
        chickens = st.number_input("Chickens", 0, 5000, 0, 25)
        
        st.markdown("### 🏗️ Infrastructure")
        milking_area = st.checkbox("Milking Area", value=True)
        isolation_pen = st.checkbox("Isolation Pen", value=True)
        fodder_storage = st.checkbox("Fodder Storage", value=True)
        water_system = st.checkbox("Water System", value=True)
        storage_barn = st.checkbox("Storage Barn", value=True)
        
        st.markdown("### 💰 Budget Level")
        budget = st.radio("Select Budget", BUDGET_LEVELS, index=1, horizontal=True)
        
        st.markdown("---")
        generate_btn = st.button("🚀 Generate Farm Plan", use_container_width=True)
    
    if generate_btn:
        with st.spinner("Calculating layout and generating PDF…"):
            animals = {"milch_cows": milch_cows, "dry_cows": dry_cows, "calves": calves, 
                      "goats": goats, "chickens": chickens}
            infra_toggles = {"milking_area": milking_area, "isolation_pen": isolation_pen,
                           "fodder_storage": fodder_storage, "water_system": water_system,
                           "storage_barn": storage_barn}
            
            layout_data = calculate_layout(land_acres, country, farm_type, animals, infra_toggles, budget)
            map_png = draw_layout_map(layout_data)
            pdf_bytes = generate_pdf(layout_data, map_png)
        
        st.success("✅ Farm plan generated successfully!")
        
        c1, c2, c3, c4 = st.columns(4)
        kpis = [
            (c1, f"{layout_data['land_acres']:.2f} acres", "Total Land"),
            (c2, f"{layout_data['total_sqm']:,.0f} m²", "Total Area (m²)"),
            (c3, f"{layout_data['total_sqft']:,.0f} sqft", "Total Area (sq ft)"),
            (c4, layout_data["budget"], "Budget Level"),
        ]
        for col, val, lbl in kpis:
            with col:
                st.markdown(f'<div class="metric-card"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', 
                           unsafe_allow_html=True)
        
        st.markdown("---")
        col_map, col_info = st.columns([3, 2])
        
        with col_map:
            st.markdown("### 🗺️ Layout Map Preview")
            st.image(map_png, use_container_width=True, 
                    caption=f"{land_size} {land_unit} {farm_type} – {country}")
        
        with col_info:
            st.markdown("### 📊 Zone Breakdown")
            for zone in layout_data["zones"]:
                pct = zone["fraction"] * 100
                st.markdown(f"**{zone['name']}** — {pct:.1f}% ({zone['sqm']:,.0f} m²)")
                st.progress(zone["fraction"])
        
        st.markdown("---")
        
        filename = f"FarmPlan_{land_size}{land_unit[0]}_{farm_type.replace(' ','_')}_{country}_{budget}.pdf"
        st.download_button(
            label="⬇️ Download Premium PDF Farm Plan",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.markdown("""
            <div style="text-align:center; padding:3rem 1rem; color:#717D7E;">
                <div style="font-size:4rem;">🌾</div>
                <h2 style="color:#2471A3;">Welcome to FarmPlan Pro</h2>
                <p style="max-width:500px; margin:0 auto; font-size:1rem;">
                    Configure your farm details in the sidebar, then click 
                    <strong>Generate Farm Plan</strong> to produce a premium PDF.
                </p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
