"""
=============================================================================
  FARM LAYOUT PDF GENERATOR — Premium Digital Product Tool
  Version 1.0 | Production-Ready Streamlit App
=============================================================================
  Generates engineering-style, sellable farm layout PDFs using:
    - Streamlit (UI)
    - Matplotlib (2D layout map)
    - ReportLab (PDF generation)

  Run: streamlit run app.py
=============================================================================
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
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# =============================================================================
#  CONSTANTS & CONFIGURATION
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

# Space requirements per animal (sq meters)
ANIMAL_SPACE_SQMT = {
    "Dairy Farm":          {"milch_cow": 18, "dry_cow": 14, "calf": 6, "heifer": 10, "goat": 4, "chicken": 0.5},
    "Goat Farming":        {"milch_cow": 18, "dry_cow": 14, "calf": 6, "heifer": 10, "goat": 3.5, "chicken": 0.5},
    "Poultry Farm":        {"milch_cow": 18, "dry_cow": 14, "calf": 6, "heifer": 10, "goat": 4, "chicken": 0.4},
    "Organic Vegetable Farm": {"milch_cow": 18, "dry_cow": 14, "calf": 6, "heifer": 10, "goat": 4, "chicken": 0.5},
    "Mixed Homestead":     {"milch_cow": 16, "dry_cow": 12, "calf": 5, "heifer": 9, "goat": 3.5, "chicken": 0.45},
}

# Country-based space adjustment multipliers
COUNTRY_MULTIPLIER = {
    "India": 0.90, "USA": 1.10, "UK": 1.05, "Australia": 1.15,
    "Canada": 1.10, "New Zealand": 1.10, "Brazil": 0.95,
    "South Africa": 0.95, "Kenya": 0.88, "Germany": 1.08,
}

# Budget affects infrastructure quality labels
BUDGET_INFRA = {
    "Basic":    {"quality": "Standard construction", "flooring": "Packed earth / concrete", "roofing": "GI sheet / tarpaulin"},
    "Standard": {"quality": "Semi-permanent structure", "flooring": "Concrete slab", "roofing": "Asbestos / GI sheet"},
    "Premium":  {"quality": "Permanent RCC structure", "flooring": "Anti-slip concrete", "roofing": "Insulated metal roof"},
}

# Color palette for layout zones
ZONE_COLORS = {
    "Milch Cow Section":    "#AED6F1",
    "Dry Cow Section":      "#A9DFBF",
    "Heifer Section":       "#D5DBDB",
    "Calf Pens":            "#FAD7A0",
    "Milking Area":         "#D2B4DE",
    "Fodder / Feed Area":   "#F9E79F",
    "Isolation / Sick Pen": "#F1948A",
    "Bull Pen":             "#85C1E9",
    "Water Points":         "#85C1E9",
    "Storage / Barn":       "#A9CCE3",
    "Goat Section":         "#ABEBC6",
    "Poultry House":        "#FDEBD0",
    "Veggie Beds":          "#A9DFBF",
    "Compost Area":         "#D5F5E3",
    "Office / Entry":       "#EAECEE",
    "Open Yard / Paddock":  "#EBF5FB",
    "Equipment Store":      "#CCD1D1",
}

SECTION_EDGE_COLOR = "#2C3E50"

# Farm-type-specific layout templates
LAYOUT_TEMPLATES = {
    "Dairy Farm": [
        ("Milch Cow Section",    0.25),
        ("Dry Cow Section",      0.12),
        ("Heifer Section",       0.10),
        ("Calf Pens",            0.07),
        ("Milking Area",         0.08),
        ("Fodder / Feed Area",   0.12),
        ("Isolation / Sick Pen", 0.04),
        ("Storage / Barn",       0.08),
        ("Office / Entry",       0.04),
        ("Open Yard / Paddock",  0.10),
    ],
    "Goat Farming": [
        ("Goat Section",         0.35),
        ("Calf Pens",            0.08),
        ("Fodder / Feed Area",   0.14),
        ("Milking Area",         0.07),
        ("Isolation / Sick Pen", 0.05),
        ("Storage / Barn",       0.10),
        ("Compost Area",         0.06),
        ("Office / Entry",       0.05),
        ("Open Yard / Paddock",  0.10),
    ],
    "Poultry Farm": [
        ("Poultry House",        0.40),
        ("Fodder / Feed Area",   0.12),
        ("Storage / Barn",       0.10),
        ("Isolation / Sick Pen", 0.05),
        ("Compost Area",         0.08),
        ("Equipment Store",      0.07),
        ("Office / Entry",       0.05),
        ("Open Yard / Paddock",  0.13),
    ],
    "Organic Vegetable Farm": [
        ("Veggie Beds",          0.45),
        ("Compost Area",         0.10),
        ("Fodder / Feed Area",   0.08),
        ("Storage / Barn",       0.10),
        ("Water Points",         0.05),
        ("Equipment Store",      0.07),
        ("Office / Entry",       0.05),
        ("Open Yard / Paddock",  0.10),
    ],
    "Mixed Homestead": [
        ("Milch Cow Section",    0.18),
        ("Goat Section",         0.12),
        ("Poultry House",        0.10),
        ("Veggie Beds",          0.15),
        ("Fodder / Feed Area",   0.10),
        ("Storage / Barn",       0.09),
        ("Compost Area",         0.06),
        ("Calf Pens",            0.05),
        ("Office / Entry",       0.05),
        ("Open Yard / Paddock",  0.10),
    ],
}

# Practical tips per farm type
FARM_TIPS = {
    "Dairy Farm": [
        "Orient the barn East-West to maximize natural ventilation and reduce heat stress on animals.",
        "Keep the milking parlour adjacent to the milch cow section to minimize animal movement stress.",
        "Install automated drinking troughs with float valves — target 10–15 litres/hr per cow.",
        "Allocate at minimum 15% of total area to fodder storage; include both dry and green feed zones.",
        "Grade all floors towards central drainage channels (1:50 slope) to prevent moisture buildup.",
        "Maintain a 3-metre-wide service lane between cow rows for easy tractor/silage cart access.",
        "Quarantine all new arrivals in the Isolation Pen for at least 14 days before integration.",
    ],
    "Goat Farming": [
        "Elevate sleeping platforms 50–60 cm above the floor — goats prefer raised rest areas.",
        "Use slatted wooden floors in housing to keep hooves dry and reduce foot-rot incidence.",
        "Separate bucks (males) at minimum 50 metres from does during non-breeding season.",
        "Plant perimeter windbreaks (Napier grass, hedge rows) to reduce cold stress in open yards.",
        "Install individual feeding stanchions to prevent dominant animals from monopolising feed.",
        "Compost goat droppings for 45–60 days before applying to fields — excellent nitrogen source.",
        "Ensure 3–4 sq m of yard space per adult goat for exercise and stress reduction.",
    ],
    "Poultry Farm": [
        "Orient houses North-South in tropical climates; East-West in temperate zones for cross-ventilation.",
        "Maintain 6–8 birds per sq metre for broilers; 4–5 per sq metre for layers (free-range standard).",
        "Install curtain ventilation walls — roll up sides during the day, close at night or in cold weather.",
        "Separate the dead-bird disposal area at least 100 metres downwind from the main house.",
        "Use deep-litter system (rice husk / sawdust, 10 cm deep) — replace every grow-out cycle.",
        "Include a footbath with disinfectant at every house entry point — essential for biosecurity.",
        "Elevate feeders and drinkers to bird back height to minimise feed wastage and contamination.",
    ],
    "Organic Vegetable Farm": [
        "Arrange beds in North-South orientation for uniform sunlight exposure across all rows.",
        "Maintain 0.6–0.9 metre working paths between beds to allow easy harvest and equipment movement.",
        "Rotate crop families each season across bed blocks (4-block rotation minimum) to prevent soil disease.",
        "Compost area should receive full sun and be at least 10 metres from water sources.",
        "Install drip irrigation from a central header pipe for water efficiency (40–60% less than overhead).",
        "Keep toolshed close to the entry point — saves 15–20 minutes per working day in tool retrieval time.",
        "Plant a pollinator strip (marigolds, sunflowers) along the perimeter to improve vegetable yields.",
    ],
    "Mixed Homestead": [
        "Zone livestock downwind from the living area and vegetable beds to prevent odour issues.",
        "Design pathways so feed, water and manure routes do not cross — prevents cross-contamination.",
        "Use livestock manure composted for 60+ days as primary fertiliser for vegetable beds.",
        "Install a central water header with branch lines to each livestock and irrigation zone.",
        "Keep a dedicated quarantine zone even for a mixed homestead — biosecurity applies to all species.",
        "Plan for expansion from the outset — leave 15–20% of land unallocated for future growth.",
        "Integrate shade trees (Moringa, banana) along fence lines for dual purpose: shade + fodder/food.",
    ],
}


# =============================================================================
#  AREA CALCULATION ENGINE
# =============================================================================

def calculate_layout(
    land_acres: float,
    country: str,
    farm_type: str,
    animals: dict,
    infra_toggles: dict,
    budget: str,
) -> dict:
    """
    Core area & zone calculation engine.
    Returns a structured dict with all zone allocations, animal capacities,
    and infrastructure details.
    """
    SQM_PER_ACRE = 4046.86
    SQFT_PER_ACRE = 43560.0

    total_sqm  = land_acres * SQM_PER_ACRE
    total_sqft = land_acres * SQFT_PER_ACRE

    multiplier   = COUNTRY_MULTIPLIER.get(country, 1.0)
    template     = LAYOUT_TEMPLATES[farm_type]

    # Build zone allocations
    zones = []
    for zone_name, fraction in template:
        sqm  = total_sqm  * fraction
        sqft = total_sqft * fraction
        acres_zone = land_acres * fraction
        zones.append({
            "name":      zone_name,
            "fraction":  fraction,
            "sqm":       round(sqm,  1),
            "sqft":      round(sqft, 0),
            "acres":     round(acres_zone, 4),
        })

    # Animal capacity per zone based on space requirements
    space_reqs = ANIMAL_SPACE_SQMT[farm_type]
    adj_space  = {k: v * multiplier for k, v in space_reqs.items()}

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
            capacities[zn] = None  # Not an animal zone

    # Infrastructure details
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
        "land_acres":    land_acres,
        "total_sqm":     round(total_sqm,  1),
        "total_sqft":    round(total_sqft, 0),
        "country":       country,
        "farm_type":     farm_type,
        "budget":        budget,
        "zones":         zones,
        "capacities":    capacities,
        "animals":       animals,
        "infra_toggles": infra_toggles,
        "infra_details": infra_details,
        "budget_info":   budget_info,
        "multiplier":    multiplier,
        "tips":          FARM_TIPS[farm_type],
        "generated_at":  datetime.datetime.now().strftime("%d %B %Y, %I:%M %p"),
    }


# =============================================================================
#  LAYOUT MAP DRAWING ENGINE
# =============================================================================

def draw_layout_map(layout_data: dict) -> bytes:
    """
    Generates a professional 2D top-view farm layout map using matplotlib.
    Returns PNG bytes at 200 DPI for embedding in the PDF.
    """
    zones     = layout_data["zones"]
    farm_type = layout_data["farm_type"]
    country   = layout_data["country"]
    acres     = layout_data["land_acres"]

    # --- Figure setup ---
    fig, ax = plt.subplots(figsize=(14, 10), facecolor="#F7F9FC")
    ax.set_facecolor("#EBF5FB")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")
    ax.axis("off")

    # --- Title bar ---
    fig.text(
        0.5, 0.97,
        f"{acres} Acre {farm_type} Layout Plan — {country}",
        ha="center", va="top",
        fontsize=15, fontweight="bold", color="#1A252F",
        fontfamily="DejaVu Sans",
    )
    fig.text(
        0.5, 0.935,
        f"Total Area: {layout_data['total_sqm']:,.0f} m²  |  "
        f"{layout_data['total_sqft']:,.0f} sq ft  |  "
        f"Budget: {layout_data['budget']}",
        ha="center", va="top",
        fontsize=9, color="#555555",
    )

    # ---------------------------------------------------------------
    # STRUCTURED GRID PLACEMENT — no randomness
    # We split zones into a logical 2-column grid, left & right halves,
    # with production zones on the left and support/infra on the right.
    # ---------------------------------------------------------------
    LEFT_X,  LEFT_W  = 1,  56
    RIGHT_X, RIGHT_W = 59, 40
    MARGIN_TOP = 88
    MARGIN_BOT = 2
    GAP = 1.5

    n_zones = len(zones)
    left_zones  = zones[:math.ceil(n_zones / 2)]
    right_zones = zones[math.ceil(n_zones / 2):]

    def draw_column(zone_list, x_start, col_width, label_prefix=""):
        total_frac = sum(z["fraction"] for z in zone_list)
        available_h = MARGIN_TOP - MARGIN_BOT - GAP * (len(zone_list) - 1)
        y_cursor = MARGIN_TOP

        for z in zone_list:
            h = (z["fraction"] / total_frac) * available_h
            color = ZONE_COLORS.get(z["name"], "#D5D8DC")

            # Zone rectangle
            rect = mpatches.FancyBboxPatch(
                (x_start, y_cursor - h),
                col_width, h,
                boxstyle="round,pad=0.3",
                linewidth=1.2,
                edgecolor=SECTION_EDGE_COLOR,
                facecolor=color,
                zorder=2,
            )
            ax.add_patch(rect)

            # Zone label — multi-line for long names
            words = z["name"].split()
            if len(words) > 2:
                line1 = " ".join(words[:2])
                line2 = " ".join(words[2:])
                label = f"{line1}\n{line2}"
            else:
                label = z["name"]

            font_size = 7.5 if h < 7 else 8.5
            ax.text(
                x_start + col_width / 2,
                y_cursor - h / 2 + 1.5,
                label,
                ha="center", va="center",
                fontsize=font_size, fontweight="bold", color="#1A252F",
                zorder=3, wrap=True,
                multialignment="center",
            )

            # Area sub-label
            ax.text(
                x_start + col_width / 2,
                y_cursor - h / 2 - 1.8,
                f"{z['sqm']:,.0f} m²",
                ha="center", va="center",
                fontsize=6.5, color="#555555", style="italic",
                zorder=3,
            )

            y_cursor -= (h + GAP)

    draw_column(left_zones,  LEFT_X,  LEFT_W)
    draw_column(right_zones, RIGHT_X, RIGHT_W)

    # --- Vertical divider lane (service road) ---
    ax.add_patch(mpatches.FancyBboxPatch(
        (LEFT_X + LEFT_W, MARGIN_BOT),
        RIGHT_X - (LEFT_X + LEFT_W), MARGIN_TOP - MARGIN_BOT,
        boxstyle="square,pad=0",
        linewidth=0, facecolor="#D5D8DC", zorder=1,
    ))
    ax.text(
        (LEFT_X + LEFT_W + RIGHT_X) / 2,
        (MARGIN_TOP + MARGIN_BOT) / 2,
        "SERVICE\nLANE",
        ha="center", va="center",
        fontsize=6, color="#7F8C8D", fontweight="bold",
        rotation=90, zorder=4,
    )

    # --- Flow arrows (N→S main movement) ---
    arrow_props = dict(
        arrowstyle="->", color="#2E86C1", lw=1.5,
        connectionstyle="arc3,rad=0.0",
    )
    for ay_pos in [75, 55, 35]:
        ax.annotate(
            "", xy=(LEFT_X + LEFT_W - 0.5, ay_pos - 6),
            xytext=(LEFT_X + LEFT_W - 0.5, ay_pos),
            arrowprops=arrow_props, zorder=5,
        )

    # --- Compass rose ---
    cx, cy, r = 96, 95, 3
    ax.annotate("N", xy=(cx, cy + r), xytext=(cx, cy),
                ha="center", va="center", fontsize=8, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#C0392B", lw=2),
                color="#C0392B", zorder=6)

    # --- Border ---
    border = mpatches.FancyBboxPatch(
        (0.3, 0.3), 99.4, 99.4,
        boxstyle="round,pad=0.1",
        linewidth=2.5, edgecolor="#1A252F", facecolor="none", zorder=10,
    )
    ax.add_patch(border)

    # --- Legend ---
    legend_patches = [
        mpatches.Patch(facecolor=ZONE_COLORS.get(z["name"], "#D5D8DC"),
                       edgecolor=SECTION_EDGE_COLOR, linewidth=0.8,
                       label=z["name"])
        for z in zones
    ]
    ax.legend(
        handles=legend_patches,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.11),
        ncol=5, fontsize=6.5,
        framealpha=0.9, edgecolor="#BDC3C7",
        title="Zone Legend", title_fontsize=7,
    )

    # --- Scale bar ---
    land_sqm = layout_data["total_sqm"]
    side_m   = math.sqrt(land_sqm)
    scale_label = f"≈ {side_m:.0f} m × {side_m:.0f} m (if square)"
    ax.text(1, -2, scale_label, fontsize=7, color="#7F8C8D", va="top")

    plt.tight_layout(rect=[0, 0.08, 1, 0.93])

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()


# =============================================================================
#  PDF GENERATION ENGINE
# =============================================================================

# Brand colors
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
    """Build and return all ParagraphStyles used in the PDF."""
    base = getSampleStyleSheet()

    styles = {
        "doc_title": ParagraphStyle(
            "DocTitle",
            parent=base["Title"],
            fontSize=22, textColor=C_WHITE,
            alignment=TA_CENTER,
            spaceAfter=4, spaceBefore=4,
            fontName="Helvetica-Bold",
        ),
        "doc_subtitle": ParagraphStyle(
            "DocSubtitle",
            parent=base["Normal"],
            fontSize=10, textColor=colors.HexColor("#BDC3C7"),
            alignment=TA_CENTER,
            spaceAfter=2,
            fontName="Helvetica",
        ),
        "section_heading": ParagraphStyle(
            "SectionHeading",
            parent=base["Heading2"],
            fontSize=13, textColor=C_BLUE,
            spaceBefore=14, spaceAfter=6,
            fontName="Helvetica-Bold",
            borderPad=2,
        ),
        "sub_heading": ParagraphStyle(
            "SubHeading",
            parent=base["Heading3"],
            fontSize=10, textColor=C_DARK,
            spaceBefore=8, spaceAfter=4,
            fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=9, textColor=C_DARK,
            leading=14,
            fontName="Helvetica",
        ),
        "body_bold": ParagraphStyle(
            "BodyBold",
            parent=base["Normal"],
            fontSize=9, textColor=C_DARK,
            fontName="Helvetica-Bold",
        ),
        "tip": ParagraphStyle(
            "Tip",
            parent=base["Normal"],
            fontSize=8.5, textColor=colors.HexColor("#1B4F72"),
            leading=13, leftIndent=10,
            fontName="Helvetica",
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=base["Normal"],
            fontSize=7, textColor=C_GREY,
            alignment=TA_CENTER,
            fontName="Helvetica",
        ),
        "label": ParagraphStyle(
            "Label",
            parent=base["Normal"],
            fontSize=8, textColor=C_GREY,
            alignment=TA_RIGHT,
            fontName="Helvetica",
        ),
    }
    return styles


def _header_block(styles, layout_data):
    """Returns the cover-style header section as a list of flowables."""
    story = []

    # Dark header banner using a Table
    title_text   = f"{layout_data['land_acres']} Acre {layout_data['farm_type']} Layout Plan"
    subtitle_text = f"{layout_data['country']} Edition  •  Budget: {layout_data['budget']}  •  {layout_data['generated_at']}"

    header_table = Table(
        [[
            Paragraph(title_text,   styles["doc_title"]),
            Paragraph(subtitle_text, styles["doc_subtitle"]),
        ]],
        colWidths=["100%"],
    )
    # single-cell vertical stacking via nested table
    header_table = Table(
        [
            [Paragraph(title_text,    styles["doc_title"])],
            [Paragraph(subtitle_text, styles["doc_subtitle"])],
        ],
        colWidths=[170 * mm],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), C_DARK),
        ("TOPPADDING",  (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 14),
        ("LEFTPADDING",  (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8 * mm))
    return story


def _summary_bar(styles, layout_data):
    """Returns a 3-column KPI bar."""
    story = []
    kpis = [
        ("Total Land Area",  f"{layout_data['land_acres']} acres"),
        ("Total Area (m²)",  f"{layout_data['total_sqm']:,.0f} m²"),
        ("Total Area (sqft)", f"{layout_data['total_sqft']:,.0f} sq ft"),
        ("Farm Type",        layout_data["farm_type"]),
        ("Region/Country",   layout_data["country"]),
        ("Budget Level",     layout_data["budget"]),
    ]

    data = [[
        Table(
            [[Paragraph(v, ParagraphStyle("kv", fontSize=11, fontName="Helvetica-Bold", textColor=C_BLUE))],
             [Paragraph(k, ParagraphStyle("kk", fontSize=7.5, fontName="Helvetica", textColor=C_GREY))]],
            colWidths=[52 * mm],
        )
        for k, v in kpis[:3]
    ], [
        Table(
            [[Paragraph(v, ParagraphStyle("kv2", fontSize=10, fontName="Helvetica-Bold", textColor=C_GREEN))],
             [Paragraph(k, ParagraphStyle("kk2", fontSize=7.5, fontName="Helvetica", textColor=C_GREY))]],
            colWidths=[52 * mm],
        )
        for k, v in kpis[3:]
    ]]

    kpi_table = Table(data, colWidths=[56 * mm, 56 * mm, 56 * mm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_LIGHT),
        ("BOX",           (0, 0), (-1, -1), 0.8, C_BLUE),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 6 * mm))
    return story


def _area_table(styles, layout_data):
    """Returns section-wise area allocation table."""
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

    col_widths = [65 * mm, 22 * mm, 28 * mm, 28 * mm, 32 * mm]
    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), C_DARK),
        ("TEXTCOLOR",     (0, 0), (-1, 0), C_WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_ROW_A, C_ROW_B]),
        ("BOX",           (0, 0), (-1, -1), 0.8, C_DARK),
        ("INNERGRID",     (0, 0), (-1, -1), 0.4, colors.HexColor("#BDC3C7")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 9),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6 * mm))
    return story


def _infra_table(styles, layout_data):
    """Returns infrastructure details table."""
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

    col_widths = [55 * mm, 28 * mm, 92 * mm]
    tbl = Table(infra_rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), C_GREEN),
        ("TEXTCOLOR",     (0, 0), (-1, 0), C_WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_ROW_A, C_ROW_B]),
        ("BOX",           (0, 0), (-1, -1), 0.8, C_DARK),
        ("INNERGRID",     (0, 0), (-1, -1), 0.4, colors.HexColor("#BDC3C7")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6 * mm))
    return story


def _animal_summary(styles, layout_data):
    """Returns animal input summary section."""
    story = []
    animals = layout_data["animals"]
    if not any(v > 0 for v in animals.values()):
        return story

    story.append(Paragraph("Animal Stock Summary (User Inputs)", styles["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_ACCENT, spaceAfter=4))

    labels = {
        "milch_cows": "Milch Cows (Lactating)",
        "dry_cows":   "Dry Cows",
        "calves":     "Calves",
        "goats":      "Goats",
        "chickens":   "Chickens / Poultry",
    }
    animal_rows = [
        [Paragraph("<b>Animal Type</b>", styles["body_bold"]),
         Paragraph("<b>Count</b>", styles["body_bold"]),
         Paragraph("<b>Space Required (m²)</b>", styles["body_bold"])],
    ]
    space_map = ANIMAL_SPACE_SQMT[layout_data["farm_type"]]
    mult      = layout_data["multiplier"]
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

    col_widths = [80 * mm, 30 * mm, 65 * mm]
    tbl = Table(animal_rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), C_ACCENT),
        ("TEXTCOLOR",     (0, 0), (-1, 0), C_WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_ROW_A, C_ROW_B]),
        ("BOX",           (0, 0), (-1, -1), 0.8, C_DARK),
        ("INNERGRID",     (0, 0), (-1, -1), 0.4, colors.HexColor("#BDC3C7")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("ALIGN",         (1, 0), (2, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6 * mm))
    return story


def _tips_section(styles, layout_data):
    """Returns practical tips section."""
    story = []
    story.append(Paragraph("Expert Setup & Management Tips", styles["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceAfter=6))

    for i, tip in enumerate(layout_data["tips"], 1):
        tip_row = Table(
            [[
                Paragraph(
                    f'<font color="#E67E22"><b>{i:02d}</b></font>',
                    ParagraphStyle("tipnum", fontSize=10, fontName="Helvetica-Bold", alignment=TA_CENTER),
                ),
                Paragraph(tip, styles["tip"]),
            ]],
            colWidths=[12 * mm, 155 * mm],
        )
        tip_row.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#EBF5FB")),
            ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#AED6F1")),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(tip_row)
        story.append(Spacer(1, 3 * mm))

    story.append(Spacer(1, 4 * mm))
    return story


def _disclaimer_footer(styles):
    """Returns disclaimer paragraph."""
    text = (
        "This farm layout plan is generated based on standard agricultural zoning guidelines and the inputs provided. "
        "Actual construction should be verified by a qualified agricultural engineer or veterinary consultant. "
        "All area figures are approximate. Space requirements may vary based on local regulations and breed specifications."
    )
    story = [
        HRFlowable(width="100%", thickness=0.5, color=C_GREY, spaceBefore=8, spaceAfter=4),
        Paragraph(text, styles["footer"]),
    ]
    return story


def generate_pdf(layout_data: dict, map_png_bytes: bytes) -> bytes:
    """
    Assembles and returns the complete premium PDF as bytes.
    """
    buf    = io.BytesIO()
    styles = _build_styles()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title=f"{layout_data['land_acres']} Acre {layout_data['farm_type']} Plan",
        author="FarmPlan Pro",
        subject="Premium Farm Layout Plan",
    )

    story = []

    # --- Page 1: Header + KPIs + Layout Map ---
    story += _header_block(styles, layout_data)
    story += _summary_bar(styles, layout_data)

    # Layout map image
    story.append(Paragraph("Farm Layout Map", styles["section_heading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BLUE, spaceAfter=4))

    img_stream = io.BytesIO(map_png_bytes)
    rl_img = RLImage(img_stream, width=170 * mm, height=121 * mm)
    rl_img.hAlign = "CENTER"
    story.append(rl_img)
    story.append(Spacer(1, 4 * mm))

    # Map caption
    story.append(Paragraph(
        f"<i>Top-view 2D layout for a {layout_data['land_acres']}-acre {layout_data['farm_type']} "
        f"in {layout_data['country']}. All zones are proportionally sized to actual land allocation.</i>",
        ParagraphStyle("caption", fontSize=7.5, textColor=C_GREY, alignment=TA_CENTER, fontName="Helvetica-Oblique"),
    ))

    story.append(PageBreak())

    # --- Page 2: Tables + Tips ---
    story += _area_table(styles, layout_data)
    story += _animal_summary(styles, layout_data)
    story += _infra_table(styles, layout_data)
    story += _tips_section(styles, layout_data)
    story += _disclaimer_footer(styles)

    doc.build(story)
    buf.seek(0)
    return buf.read()


# =============================================================================
#  STREAMLIT UI
# =============================================================================

def main():
    st.set_page_config(
        page_title="FarmPlan Pro – Premium Farm Layout Generator",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ── Custom CSS ──────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: #F0F4F8; }
    .block-container { padding-top: 1.5rem; }
    h1 { color: #1A252F; font-weight: 700; letter-spacing: -0.5px; }
    h2, h3 { color: #2471A3; }
    .stButton > button {
        background: linear-gradient(135deg, #2471A3 0%, #1A252F 100%);
        color: white; border: none; border-radius: 8px;
        padding: 0.65rem 2rem; font-size: 1rem; font-weight: 600;
        width: 100%; transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.88; }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1E8449 0%, #145A32 100%);
        color: white; border: none; border-radius: 8px;
        padding: 0.65rem 2rem; font-size: 1rem; font-weight: 600;
        width: 100%;
    }
    .stSelectbox label, .stNumberInput label, .stCheckbox label { font-weight: 600; color: #1A252F; }
    .metric-card {
        background: white; border-radius: 10px; padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07); margin-bottom: 0.5rem;
        border-left: 4px solid #2471A3;
    }
    .metric-card .val { font-size: 1.4rem; font-weight: 700; color: #2471A3; }
    .metric-card .lbl { font-size: 0.75rem; color: #717D7E; margin-top: 2px; }
    .tip-card {
        background: #EBF5FB; border-radius: 8px; padding: 0.7rem 1rem;
        border-left: 3px solid #E67E22; margin-bottom: 0.4rem;
        font-size: 0.85rem; color: #1B4F72;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1A252F 0%,#2471A3 100%);
                padding:1.5rem 2rem; border-radius:12px; margin-bottom:1.5rem;">
        <h1 style="color:white;margin:0;font-size:2rem;">🌾 FarmPlan Pro</h1>
        <p style="color:#AED6F1;margin:0.4rem 0 0;">
            Premium Engineering-Style Farm Layout Generator &nbsp;|&nbsp;
            Sellable Digital Farm Plans for Global Markets
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar – Input Form ────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## ⚙️ Farm Configuration")
        st.markdown("---")

        st.markdown("### 📐 Land & Location")
        col_a, col_b = st.columns(2)
        with col_a:
            land_size = st.number_input("Land Size", min_value=0.5, max_value=500.0,
                                        value=2.0, step=0.5)
        with col_b:
            land_unit = st.selectbox("Unit", ["Acres", "Hectares"])

        # Convert to acres internally
        land_acres = land_size if land_unit == "Acres" else land_size * 2.47105

        country   = st.selectbox("Country / Region", COUNTRIES, index=0)
        farm_type = st.selectbox("Farm Type", FARM_TYPES, index=0)

        st.markdown("### 🐄 Animal Count")
        milch_cows = st.number_input("Milch Cows (Lactating)", 0, 500, 10, 1)
        dry_cows   = st.number_input("Dry Cows",               0, 500,  4, 1)
        calves     = st.number_input("Calves",                  0, 500,  6, 1)
        goats      = st.number_input("Goats",                   0, 1000, 0, 5)
        chickens   = st.number_input("Chickens / Poultry",      0, 5000, 0, 25)

        st.markdown("### 🏗️ Infrastructure")
        milking_area    = st.checkbox("Milking Area / Parlour", value=True)
        isolation_pen   = st.checkbox("Isolation / Sick Pen",   value=True)
        fodder_storage  = st.checkbox("Fodder Storage",         value=True)
        water_system    = st.checkbox("Water Supply System",    value=True)
        storage_barn    = st.checkbox("Storage / Barn",         value=True)

        st.markdown("### 💰 Budget Level")
        budget = st.radio("Select Budget", BUDGET_LEVELS, index=1, horizontal=True)

        st.markdown("---")
        generate_btn = st.button("🚀 Generate Farm Plan", use_container_width=True)

    # ── Main Panel ──────────────────────────────────────────────────────────
    if generate_btn:
        with st.spinner("Calculating layout and generating PDF…"):
            animals = {
                "milch_cows": milch_cows,
                "dry_cows":   dry_cows,
                "calves":     calves,
                "goats":      goats,
                "chickens":   chickens,
            }
            infra_toggles = {
                "milking_area":   milking_area,
                "isolation_pen":  isolation_pen,
                "fodder_storage": fodder_storage,
                "water_system":   water_system,
                "storage_barn":   storage_barn,
            }

            # 1. Calculate layout data
            layout_data = calculate_layout(
                land_acres, country, farm_type, animals, infra_toggles, budget
            )

            # 2. Draw map
            map_png = draw_layout_map(layout_data)

            # 3. Generate PDF
            pdf_bytes = generate_pdf(layout_data, map_png)

        # ── Results Display ──────────────────────────────────────────────
        st.success("✅ Farm plan generated successfully!")

        # KPI Cards
        c1, c2, c3, c4 = st.columns(4)
        kpis = [
            (c1, f"{layout_data['land_acres']:.2f} acres", "Total Land"),
            (c2, f"{layout_data['total_sqm']:,.0f} m²",    "Total Area (m²)"),
            (c3, f"{layout_data['total_sqft']:,.0f} sqft", "Total Area (sq ft)"),
            (c4, layout_data["budget"],                    "Budget Level"),
        ]
        for col, val, lbl in kpis:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="val">{val}</div>
                    <div class="lbl">{lbl}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # Layout Preview
        col_map, col_info = st.columns([3, 2])
        with col_map:
            st.markdown("### 🗺️ Layout Map Preview")
            st.image(map_png, use_container_width=True,
                     caption=f"{land_size} {land_unit} {farm_type} – {country}")

        with col_info:
            st.markdown("### 📊 Zone Breakdown")
            for zone in layout_data["zones"]:
                pct = zone["fraction"] * 100
                st.markdown(
                    f"**{zone['name']}** — {pct:.1f}% "
                    f"({zone['sqm']:,.0f} m² / {zone['sqft']:,.0f} sqft)"
                )
                st.progress(zone["fraction"])

        st.markdown("---")

        # Infrastructure & Tips
        col_inf, col_tip = st.columns(2)
        with col_inf:
            st.markdown("### 🏗️ Infrastructure Details")
            bi = layout_data["budget_info"]
            st.markdown(f"- **Quality:** {bi['quality']}")
            st.markdown(f"- **Flooring:** {bi['flooring']}")
            st.markdown(f"- **Roofing:** {bi['roofing']}")
            for item, status, note in layout_data["infra_details"]:
                st.markdown(f"- ✅ **{item}:** {note}")

        with col_tip:
            st.markdown("### 💡 Expert Tips")
            for tip in layout_data["tips"]:
                st.markdown(f'<div class="tip-card">💬 {tip}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Download
        filename = (
            f"FarmPlan_{land_size}{land_unit[0]}_{farm_type.replace(' ','_')}"
            f"_{country}_{budget}.pdf"
        )
        st.download_button(
            label="⬇️ Download Premium PDF Farm Plan",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
        )

    else:
        # Welcome state
        st.markdown("""
        <div style="text-align:center; padding:3rem 1rem; color:#717D7E;">
            <div style="font-size:4rem;">🌾</div>
            <h2 style="color:#2471A3;">Welcome to FarmPlan Pro</h2>
            <p style="max-width:500px; margin:0 auto; font-size:1rem; line-height:1.7;">
                Configure your farm details in the sidebar on the left,
                then click <strong>Generate Farm Plan</strong> to produce a
                premium, sellable PDF layout plan.
            </p>
            <div style="margin-top:2rem; display:flex; justify-content:center; gap:2rem; flex-wrap:wrap;">
                <div style="background:white;border-radius:10px;padding:1rem 1.5rem;
                            box-shadow:0 2px 8px rgba(0,0,0,0.08);min-width:140px;">
                    <div style="font-size:1.8rem;">📐</div>
                    <div style="font-weight:600;margin-top:0.4rem;">Engineering Layout</div>
                    <div style="font-size:0.8rem;color:#999;">Grid-based 2D map</div>
                </div>
                <div style="background:white;border-radius:10px;padding:1rem 1.5rem;
                            box-shadow:0 2px 8px rgba(0,0,0,0.08);min-width:140px;">
                    <div style="font-size:1.8rem;">📄</div>
                    <div style="font-weight:600;margin-top:0.4rem;">Premium PDF</div>
                    <div style="font-size:0.8rem;color:#999;">Ready to sell ($5–$25)</div>
                </div>
                <div style="background:white;border-radius:10px;padding:1rem 1.5rem;
                            box-shadow:0 2px 8px rgba(0,0,0,0.08);min-width:140px;">
                    <div style="font-size:1.8rem;">🌍</div>
                    <div style="font-weight:600;margin-top:0.4rem;">Global Support</div>
                    <div style="font-size:0.8rem;color:#999;">10 countries & regions</div>
                </div>
                <div style="background:white;border-radius:10px;padding:1rem 1.5rem;
                            box-shadow:0 2px 8px rgba(0,0,0,0.08);min-width:140px;">
                    <div style="font-size:1.8rem;">🐄</div>
                    <div style="font-weight:600;margin-top:0.4rem;">5 Farm Types</div>
                    <div style="font-size:0.8rem;color:#999;">Dairy, Poultry & more</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
