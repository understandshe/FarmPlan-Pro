"""
=============================================================================
FARMPLAN PRO — Premium Farm Layout Generator v2.0
=============================================================================
Ultra-premium, architectural-grade farm layout PDFs.
Realistic top-view maps with structures, trees, paths, water lines.
6-page PDF: cover, map, zone tables, cost estimate, BOQ,
            expert tips, compliance checklist, benchmarks.

Run: streamlit run app.py
=============================================================================
"""

import io, math, datetime
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
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage, PageBreak, KeepTogether,
)

# ─────────────────────────────────────────────────────────────────────────────
# MASTER DATA (All trailing spaces REMOVED)
# ─────────────────────────────────────────────────────────────────────────────

FARM_TYPES = [
    "Dairy Farm", "Goat Farming", "Poultry Farm",
    "Organic Vegetable Farm", "Mixed Homestead",
]

COUNTRIES = [
    "India", "USA", "UK", "Australia", "Canada",
    "New Zealand", "Brazil", "South Africa", "Kenya", "Germany",
]

BUDGET_LEVELS = ["Basic (Rs.5-15L)", "Standard (Rs.15-40L)", "Premium (Rs.40L+)"]

ANIMAL_SPACE = {
    "Dairy Farm": {"milch_cow": 18, "dry_cow": 14, "calf": 5, "heifer": 10, "goat": 4, "chicken": 0.5, "bull": 25},
    "Goat Farming": {"milch_cow": 18, "dry_cow": 14, "calf": 5, "heifer": 10, "goat": 3.5, "chicken": 0.5, "bull": 20},
    "Poultry Farm": {"milch_cow": 18, "dry_cow": 14, "calf": 5, "heifer": 10, "goat": 4, "chicken": 0.4, "bull": 20},
    "Organic Vegetable Farm": {"milch_cow": 18, "dry_cow": 14, "calf": 5, "heifer": 10, "goat": 4, "chicken": 0.5, "bull": 20},
    "Mixed Homestead": {"milch_cow": 16, "dry_cow": 12, "calf": 4, "heifer": 9, "goat": 3.5, "chicken": 0.45, "bull": 22},
}

COUNTRY_FACTOR = {
    "India": 0.90, "USA": 1.10, "UK": 1.05, "Australia": 1.18,
    "Canada": 1.12, "New Zealand": 1.10, "Brazil": 0.95,
    "South Africa": 0.95, "Kenya": 0.88, "Germany": 1.10,
}

COST_PER_SQFT = {
    "Basic (Rs.5-15L)": {"covered": 850, "open": 120, "services": 180},
    "Standard (Rs.15-40L)": {"covered": 1350, "open": 200, "services": 320},
    "Premium (Rs.40L+)": {"covered": 2200, "open": 350, "services": 600},
}

BUDGET_SPEC = {
    "Basic (Rs.5-15L)": {
        "Structure": "Cement block / brick with GI sheet roof",
        "Flooring": "Packed earth + cement wash",
        "Roofing": "GI corrugated sheet (0.5 mm)",
        "Water System": "Open overhead tank + PVC pipes",
        "Drainage": "Open channel, manual cleaning",
        "Fencing": "Barbed wire on MS angle posts",
        "Electricity": "Single-phase, manual switches",
    },
    "Standard (Rs.15-40L)": {
        "Structure": "RCC columns + brick infill, MS truss roof",
        "Flooring": "M20 concrete slab, 4 inch thick, slope 1:50",
        "Roofing": "Colour-coated GI sheet + polycarbonate ridge",
        "Water System": "1000L elevated tank, GI distribution pipes",
        "Drainage": "Underground PVC, automatic scraper optional",
        "Fencing": "MS pipe + chain-link or barbed wire",
        "Electricity": "Three-phase, MCB distribution, emergency light",
    },
    "Premium (Rs.40L+)": {
        "Structure": "RCC framed structure, insulated sandwich panels",
        "Flooring": "Anti-slip rubberised concrete, slope 1:40",
        "Roofing": "Insulated metal deck, ridge ventilator, skylights",
        "Water System": "Automated nipple drinkers, RO + UV system",
        "Drainage": "Biogas-linked slurry management system",
        "Fencing": "Electric fencing + CCTV perimeter",
        "Electricity": "Three-phase + solar hybrid, automated fans/foggers",
    },
}

TEMPLATES = {
    "Dairy Farm": [
        ("Milch Cow Barn", 0.22, "#B8D4E8", "//", "barn"),
        ("Dry Cow Section", 0.10, "#C8E6C9", "\\\\", "barn"),
        ("Heifer Section", 0.08, "#D1C4E9", "//", "barn"),
        ("Calf Pens", 0.06, "#FFE0B2", "xx", "barn"),
        ("Milking Parlour", 0.07, "#E8D5F5", "//", "barn"),
        ("Feed / Fodder Store", 0.10, "#FFF9C4", "||", "support"),
        ("Silage Pit", 0.05, "#DCEDC8", "--", "support"),
        ("Manure Management", 0.05, "#D7CCC8", "..", "support"),
        ("Isolation / Sick Pen", 0.04, "#FFCDD2", "xx", "barn"),
        ("Bull Pen", 0.03, "#B2EBF2", "//", "barn"),
        ("Water & Utilities", 0.04, "#B3E5FC", "..", "support"),
        ("Service Lane", 0.06, "#EEEEEE", "", "road"),
        ("Office / Entry", 0.03, "#F5F5F5", "", "entry"),
        ("Green Buffer / Trees", 0.07, "#A5D6A7", "", "green"),
    ],
    "Goat Farming": [
        ("Adult Goat Housing", 0.28, "#C8E6C9", "//", "barn"),
        ("Buck (Male) Section", 0.07, "#B2EBF2", "\\\\", "barn"),
        ("Kidding Pens", 0.07, "#FFE0B2", "xx", "barn"),
        ("Milking Area", 0.06, "#E8D5F5", "//", "barn"),
        ("Feed / Fodder Store", 0.12, "#FFF9C4", "||", "support"),
        ("Grazing Paddock", 0.15, "#DCEDC8", "", "green"),
        ("Isolation Pen", 0.04, "#FFCDD2", "xx", "barn"),
        ("Manure Compost", 0.05, "#D7CCC8", "..", "support"),
        ("Water Points", 0.04, "#B3E5FC", "..", "support"),
        ("Service Lane", 0.05, "#EEEEEE", "", "road"),
        ("Office / Entry", 0.03, "#F5F5F5", "", "entry"),
        ("Green Buffer / Trees", 0.04, "#A5D6A7", "", "green"),
    ],
    "Poultry Farm": [
        ("Broiler / Layer House A", 0.20, "#FFE0B2", "//", "barn"),
        ("Broiler / Layer House B", 0.18, "#FFE0B2", "//", "barn"),
        ("Chick Brooder Room", 0.07, "#FFF9C4", "xx", "barn"),
        ("Feed Mill / Store", 0.10, "#D1C4E9", "||", "support"),
        ("Egg Grading Room", 0.05, "#E8D5F5", "", "support"),
        ("Cold Storage", 0.04, "#B3E5FC", "..", "support"),
        ("Isolation House", 0.04, "#FFCDD2", "xx", "barn"),
        ("Dead Bird Disposal", 0.03, "#D7CCC8", "..", "support"),
        ("Manure / Litter Store", 0.06, "#DCEDC8", "..", "support"),
        ("Water Overhead Tank", 0.03, "#B3E5FC", "", "support"),
        ("Service Lane", 0.08, "#EEEEEE", "", "road"),
        ("Office / Guard Room", 0.03, "#F5F5F5", "", "entry"),
        ("Green Buffer", 0.09, "#A5D6A7", "", "green"),
    ],
    "Organic Vegetable Farm": [
        ("Raised Bed Block A", 0.18, "#C8E6C9", "", "green"),
        ("Raised Bed Block B", 0.15, "#DCEDC8", "", "green"),
        ("Raised Bed Block C", 0.12, "#A5D6A7", "", "green"),
        ("Nursery / Seedling", 0.07, "#B2EBF2", "//", "barn"),
        ("Compost Yard", 0.08, "#D7CCC8", "..", "support"),
        ("Vermicompost Beds", 0.05, "#E8D5F5", "..", "support"),
        ("Irrigation Header", 0.04, "#B3E5FC", "", "support"),
        ("Tool / Equipment Shed", 0.07, "#FFF9C4", "||", "support"),
        ("Post-Harvest Store", 0.06, "#FFE0B2", "", "support"),
        ("Drip Irrigation Lane", 0.05, "#EEEEEE", "", "road"),
        ("Poly / Net House", 0.06, "#E3F2FD", "//", "barn"),
        ("Office / Pack House", 0.04, "#F5F5F5", "", "entry"),
        ("Windbreak / Trees", 0.03, "#A5D6A7", "", "green"),
    ],
    "Mixed Homestead": [
        ("Cattle Shed", 0.14, "#B8D4E8", "//", "barn"),
        ("Goat / Sheep House", 0.10, "#C8E6C9", "\\\\", "barn"),
        ("Poultry Unit", 0.08, "#FFE0B2", "xx", "barn"),
        ("Kitchen Garden", 0.10, "#DCEDC8", "", "green"),
        ("Main Crop Field", 0.18, "#A5D6A7", "", "green"),
        ("Fodder Crop Area", 0.08, "#B2EBF2", "", "green"),
        ("Feed / Fodder Store", 0.07, "#FFF9C4", "||", "support"),
        ("Biogas Plant", 0.04, "#D7CCC8", "..", "support"),
        ("Compost Pit", 0.04, "#D1C4E9", "..", "support"),
        ("Fruit Trees / Garden", 0.06, "#A5D6A7", "", "green"),
        ("Water Tank / Well", 0.03, "#B3E5FC", "", "support"),
        ("Service Lane", 0.05, "#EEEEEE", "", "road"),
        ("Residence / Office", 0.03, "#F5F5F5", "", "entry"),
    ],
}

FARM_TIPS = {
    "Dairy Farm": [
        ("Barn Orientation", "Orient the main barn East-West. Prevailing winds pass through the barn length, reducing heat stress and ammonia. In tropics, raise sidewalls to 3.6 m minimum for cross-ventilation."),
        ("One-Way Milking Flow", "Design flow: Cow housing -> Holding pen -> Milking parlour -> Return lane. This one-way system eliminates congestion, reduces stress, and keeps the parlour hygienic."),
        ("Water Supply", "Provide 80-120 litres of clean water per milch cow per day. Float-valve troughs every 15 m. Water is the #1 driver of milk yield - never restrict it."),
        ("Manure Management", "Slope all floors 1:50 toward central gutters. A 90-day lagoon or biogas plant turns waste into revenue. Well-managed manure offsets 20-30% of operating costs as organic fertiliser."),
        ("Fodder Storage", "Covered fodder store must hold at minimum 30 days of dry fodder. Silage pits at 150 kg/m density. Maintain separate areas for green, dry, and concentrate feed."),
        ("Ventilation", "Continuous ridge ventilators along the roof peak. Cross-ventilation openings: 15-20% of floor area. Premium budgets: install misting/fogger systems in holding pens."),
        ("Calf Management", "Isolate calf pens from adult cows. Provide 2 sq m bedded area + 2 sq m exercise per calf. Individual hutches for the first 8 weeks reduce disease transmission by 60%."),
        ("Biosecurity", "Concrete footbath (3% caustic soda) at every entry. All-in/all-out protocol in isolation pen. Entry gates marked with biosecurity signage. All visitors must log in."),
    ],
    "Goat Farming": [
        ("Slatted Floor Housing", "Elevated slatted floors 60 cm above ground keep hooves dry and cut foot-rot by 70%. Use 2.5 cm gaps between slats for efficient dropping removal."),
        ("Buck Separation", "Maintain bucks minimum 50 m from does year-round. Buck odour reduces milk yield and feed intake. Separate paddocks with solid walls, not wire."),
        ("Feeding System", "Raised keyhole feeders (35 cm per head) prevent dominant animals blocking feed. Separate concentrate stalls eliminate fighting injuries and improve uniformity of growth."),
        ("Kidding Pens", "1.5 sq m kidding pens, pre-cleaned and disinfected. Mothers and kids stay 3-5 days. Install heat lamps for winter kidding in cold climates."),
        ("Rotational Grazing", "Rotate paddocks every 21 days. Rest 42-60 days to prevent parasite build-up. Never allow grazing below 8 cm sward height. Rotational grazing improves output by 30%."),
        ("Water for Goats", "Goats drink 3-4 L/head/day; lactating does: 6-8 L. Use nipple drinkers or low troughs (40 cm height). Goats refuse dirty water - clean troughs every day."),
        ("Compost Revenue", "Goat manure + bedding composts in 45 days. Two-bin system: one filling, one maturing. Finished compost sells at Rs.3-5/kg - a useful secondary income stream."),
        ("Health Records", "Tag all animals at birth. Maintain FAMACHA scores, deworming dates, kidding records per animal. Digital records consistently improve productivity by 25% within one year."),
    ],
    "Poultry Farm": [
        ("House Orientation", "Tropics: North-South orientation. Temperate: East-West. Space houses minimum 20 m apart. Correct orientation can reduce heat stress and improve FCR by 5-8%."),
        ("Stocking Density", "Broilers: 30-35 kg/m live weight (~10-12 birds/m). Layers: 5-6 birds/m colony. Overcrowding is the #1 cause of production loss and mortality - never exceed limits."),
        ("Tunnel Ventilation", "Minimum ventilation: 0.6 m/min per bird at peak summer. Tunnel ventilation (inlet one end, fans opposite) for houses >30 m. Temperature sensors at bird height, not ceiling."),
        ("Litter Management", "10 cm deep rice husk or sawdust litter. Top-dress between flocks. Replace completely every 3-4 grow-outs. Caked litter causes ammonia burns and respiratory disease."),
        ("Biosecurity Protocol", "Mandatory footbath + handwash at each house entry. Dedicated tools per house. Weekly rodent control - they carry Salmonella and consume 5-10% of feed."),
        ("Lighting Schedule", "Layers: 16 hours light/day. Broilers: intermittent 1hr light : 3hr dark reduces metabolic stress and improves FCR by 8%. Use 2W LED bulbs per 4 sq m."),
        ("Feed Management", "Target FCR: Broilers <1.8, Layers <2.0. Six small meals per day rather than ad libitum reduces wastage by 15%. Check feeder height weekly as birds grow."),
        ("Water Quality", "Water pH 6.5-7.5. Chlorinate at 3 ppm during disease outbreaks. Flush drinker lines between flocks. Water consumption = 2x feed - monitor daily to catch sick birds."),
    ],
    "Organic Vegetable Farm": [
        ("Bed Dimensions", "Raised beds: 1.2 m wide, 20-30 cm raised, 0.6 m pathways. Width allows harvesting from both sides without soil compaction. Treat timber or brick edging for permanent beds."),
        ("Soil Health First", "Apply 5-8 tonnes of well-composted FYM per acre per season. Maintain organic matter >3.5%. Monthly soil testing prevents deficiency - the most common cause of yield drop."),
        ("4-Block Crop Rotation", "Divide beds into 4 blocks: Legumes -> Brassicas -> Roots -> Nightshades. Rotate annually. This breaks pest and disease cycles without any chemical input."),
        ("Drip Irrigation", "Drip irrigation reduces water use by 40-60% vs overhead. Mulch beds with 5 cm paddy straw to further cut evaporation. Schedule at dawn for minimum disease risk."),
        ("3-Bay Compost System", "Three bays: Bay 1 (fresh), Bay 2 (turning), Bay 3 (finished). Turn every 7 days. Target C:N ratio 25-30:1. Finished compost in 45-60 days, zero chemical cost."),
        ("Organic Pest Management", "Yellow sticky traps (1 per 100 sq m) for monitoring. Marigolds and basil as pest-repellent borders. Neem oil at 2.5 mL/L for sucking pests - NPOP certified safe."),
        ("Protected Nursery", "All transplant crops raised in net house. Use pro-trays with coco-peat medium. Healthy transplants have 90%+ survival; field-sown have 60-70%. Saves seed cost too."),
        ("Organic Certification", "Apply for PGS-India (free, 3 months) or India Organic. Certified organic commands 30-100% premium price at urban markets and agri-export channels."),
    ],
    "Mixed Homestead": [
        ("Zone Planning", "Livestock must be downwind and downslope from kitchen garden and residence. Check prevailing wind direction before final layout. Minimum 20 m between livestock housing and vegetable area."),
        ("Closed-Loop Nutrition", "Crop waste -> Livestock feed -> Manure -> Compost -> Crop fertiliser. A well-managed 2-acre homestead can achieve 80% self-sufficiency in inputs within 3 years."),
        ("Central Water System", "One 5,000-10,000 L overhead tank, gravity-fed branches to each zone. Separate drinking water line for residence. Grey-water recycling for livestock use reduces pumping cost."),
        ("Biogas Integration", "A 4 cubic metre biogas plant on 2 cows manure produces 2-3 kg LPG-equivalent daily - enough for kitchen cooking. Slurry output is premium liquid fertiliser (NPK enriched)."),
        ("Fodder on Boundaries", "Plant Napier grass, Stylosanthes, or Lucerne along fence lines. 1 acre Napier = fodder for 4-5 cows. Zero additional land cost; reduces purchased fodder by 50%."),
        ("Three Income Streams", "Dairy + Poultry + Vegetables = weekly income in all three. Plan so at least one stream generates income every week. This cash-flow model is the core financial advantage of mixed systems."),
        ("Succession Cropping", "Never leave soil bare. Plant cover crop (cowpea, sunflower) immediately after harvest. Cover crops fix nitrogen, prevent erosion, and provide green manure worth Rs.2,000-4,000/acre."),
        ("Written Seasonal Plan", "A written planner (what is planted/stocked, expected inputs, sale dates, prices) earns 40% more than unplanned homesteads. Review quarterly. Adjust based on actual vs planned."),
    ],
}

BOQ_ITEMS = {
    "Dairy Farm": [
        ("Site Clearing & Levelling", "Sq ft", "Full land area"),
        ("Boundary Fencing", "Running ft", "Full perimeter"),
        ("Main Cattle Barn", "Sq ft", "Covered area"),
        ("Milking Parlour", "Sq ft", "Milking zone"),
        ("Calf Pens", "Sq ft", "Calf zone"),
        ("Isolation Pen", "Sq ft", "ISO zone"),
        ("Feed Storage Shed", "Sq ft", "Feed store area"),
        ("Silage Pit", "Cu. metre", "Volume calc"),
        ("Overhead Water Tank (1000L)", "Nos", "1-2 units"),
        ("Water Pipeline (GI/HDPE)", "Running ft", "Distribution"),
        ("Drainage System", "Running ft", "Full network"),
        ("Concrete Flooring", "Sq ft", "All covered zones"),
        ("Electrical Wiring + Fittings", "LS", "Complete"),
        ("Office / Guard Room", "Sq ft", "Entry block"),
        ("Landscaping & Trees", "Nos", "As per plan"),
    ],
    "Goat Farming": [
        ("Site Clearing & Levelling", "Sq ft", "Land area"),
        ("Perimeter Fencing", "Running ft", "Perimeter"),
        ("Goat Housing (Slatted)", "Sq ft", "Goat area"),
        ("Buck Pen (Separate)", "Sq ft", "Buck zone"),
        ("Kidding Pens", "Sq ft", "Kidding zone"),
        ("Feed Store", "Sq ft", "Feed zone"),
        ("Water System", "LS", "Complete"),
        ("Drainage & Composting Area", "Sq ft", "Waste zone"),
        ("Grazing Paddock Fencing", "Running ft", "Paddock"),
        ("Electrical Works", "LS", "Complete"),
    ],
    "Poultry Farm": [
        ("Site Clearing & Levelling", "Sq ft", "Land area"),
        ("Perimeter Fencing + Gate", "Running ft", "Perimeter"),
        ("Poultry House (each)", "Sq ft", "House area"),
        ("Brooder Room", "Sq ft", "Brooder zone"),
        ("Feed Mill / Store", "Sq ft", "Feed zone"),
        ("Egg Grading Room", "Sq ft", "Grading area"),
        ("Cold Storage (2T)", "Nos", "1 unit"),
        ("Water Overhead Tank", "Nos", "1-2 units"),
        ("Nipple Drinker Lines", "Running ft", "Per house"),
        ("Tunnel Ventilation Fans", "Nos", "Per house"),
        ("Electrical + Lighting", "LS", "Complete"),
        ("Footbath Points", "Nos", "Each entry"),
    ],
    "Organic Vegetable Farm": [
        ("Land Preparation & Beds", "Sq ft", "Bed area"),
        ("Raised Bed Edging", "Running ft", "All beds"),
        ("Drip Irrigation System", "Sq ft", "Full coverage"),
        ("Mulching Material", "Sq ft", "All beds"),
        ("Compost Bays (3-bay)", "Nos", "1 set"),
        ("Vermicompost Beds", "Sq ft", "Vermi zone"),
        ("Net / Poly House", "Sq ft", "Protected area"),
        ("Overhead Water Tank", "Nos", "1 unit"),
        ("Tool & Equipment Shed", "Sq ft", "Store area"),
        ("Post-Harvest Storage", "Sq ft", "Packed area"),
        ("Perimeter Fencing", "Running ft", "Full perimeter"),
        ("Pathways (Crushed gravel)", "Sq ft", "All paths"),
    ],
    "Mixed Homestead": [
        ("Site Clearing & Levelling", "Sq ft", "Land area"),
        ("Perimeter Fencing", "Running ft", "Perimeter"),
        ("Cattle Shed", "Sq ft", "Cattle zone"),
        ("Goat / Sheep House", "Sq ft", "Small livestock"),
        ("Poultry Unit", "Sq ft", "Poultry zone"),
        ("Kitchen Garden Beds", "Sq ft", "Garden area"),
        ("Biogas Plant (4 cu m)", "Nos", "1 unit"),
        ("Compost Pits", "Nos", "2 pits"),
        ("Water System (Complete)", "LS", "All zones"),
        ("Fodder Crop Fencing", "Running ft", "Fodder area"),
        ("Electrical Works", "LS", "Complete"),
        ("Residence (if included)", "Sq ft", "Living area"),
    ],
}

BENCHMARKS = {
    "Dairy Farm": [
        ("Milk yield / cow / day", "8-12 L (crossbred)", "15-22 L (HF/Jersey)"),
        ("Lactation length", "300 days", "305+ days"),
        ("Feed cost : Milk revenue", "<50%", "<40%"),
        ("Calving interval", "15 months", "13-14 months"),
        ("Calf mortality rate", "<10%", "<5%"),
    ],
    "Goat Farming": [
        ("Kids per doe per year", "1.5-1.8", "2.0+"),
        ("Milk yield / doe / day", "0.5-1.0 L", "1.5-2.0 L"),
        ("Feed cost : Revenue", "<45%", "<35%"),
        ("Mortality rate", "<8%", "<4%"),
        ("Growth rate (meat breed)", "80-100 g/day", "120+ g/day"),
    ],
    "Poultry Farm": [
        ("FCR (Broiler)", "1.9-2.1", "1.6-1.8"),
        ("FCR (Layer)", "2.1-2.3", "<2.0"),
        ("Egg production %", "75-80%", "85%+"),
        ("Mortality (broiler)", "<5%", "<3%"),
        ("Age at market (broiler)", "42-45 days", "38-40 days"),
    ],
    "Organic Vegetable Farm": [
        ("Yield / acre / crop", "3-5 tonnes", "7-10 tonnes"),
        ("Input cost : Revenue", "<40%", "<30%"),
        ("Crop loss to pests", "<15%", "<8%"),
        ("Soil organic matter", "1.5-2.5%", "3.5%+"),
        ("Water use efficiency", "Overhead: 100%", "Drip: 40-60%"),
    ],
    "Mixed Homestead": [
        ("Self-sufficiency (inputs)", "40-50%", "70-80%"),
        ("Active income streams", "2", "3-4"),
        ("Monthly net income", "Rs.15,000-25,000", "Rs.40,000-60,000"),
        ("Labour requirement", "2-3 family members", "2 + 1 hired"),
        ("Annual maintenance cost", "8-12% of capex", "<7% of capex"),
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# CALCULATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def calculate_layout(land_acres, country, farm_type, animals, infra, budget):
    SQM = land_acres * 4046.86
    SQFT = land_acres * 43560.0
    mult = COUNTRY_FACTOR.get(country, 1.0)

    zones = []
    for name, frac, color, hatch, ztype in TEMPLATES[farm_type]:
        sp_key = None
        for kw, sk in [("Milch Cow","milch_cow"),("Dry Cow","dry_cow"),
                        ("Heifer","heifer"),("Calf","calf"),("Kidding","calf"),
                        ("Goat","goat"),("Buck","goat"),
                        ("Poultry","chicken"),("Layer","chicken"),("Broiler","chicken"),
                        ("Bull","bull")]:
            if kw.lower() in name.lower():
                sp_key = sk
                break
        cap = None
        if sp_key and sp_key in ANIMAL_SPACE[farm_type]:
            adj = ANIMAL_SPACE[farm_type][sp_key] * mult
            cap = max(1, int(SQM * frac / adj))

        zones.append({
            "name": name, "frac": frac, "color": color,
            "hatch": hatch, "ztype": ztype,
            "sqm": round(SQM * frac, 1),
            "sqft": round(SQFT * frac, 0),
            "acres": round(land_acres * frac, 4),
            "capacity": cap,
        })

    rates = COST_PER_SQFT[budget]
    est_cost = (SQFT * 0.55 * rates["covered"] +
                SQFT * 0.20 * rates["open"] +
                SQFT * 0.08 * rates["services"])

    infra_rows = []
    INFRA_LABELS = {
        "milking": ("Milking Parlour / Area", "Adjacent to cow barn, 1-way flow"),
        "isolation": ("Isolation / Sick Pen", "Downwind, 50 m from main barn"),
        "fodder": ("Fodder & Feed Storage", "Covered, ventilated, rodent-proof"),
        "water": ("Water Supply System", "Overhead tank + full distribution"),
        "biogas": ("Biogas / Waste Management", "Linked to manure from barn"),
        "fencing": ("Perimeter Fencing", "As per budget specification"),
        "solar": ("Solar / Renewable Energy", "Panel sizing per connected load"),
        "office": ("Office / Guard Room", "At entry point, visitor log"),
    }
    for key, (lbl, note) in INFRA_LABELS.items():
        if infra.get(key):
            infra_rows.append((lbl, "Included", note))

    side_m = math.sqrt(SQM)
    perim_m = side_m * 4

    return {
        "land_acres": land_acres,
        "sqm": round(SQM, 1),
        "sqft": round(SQFT, 0),
        "country": country,
        "farm_type": farm_type,
        "budget": budget,
        "zones": zones,
        "animals": animals,
        "infra": infra,
        "infra_rows": infra_rows,
        "budget_spec": BUDGET_SPEC[budget],
        "est_cost": round(est_cost, -3),
        "side_m": round(side_m, 1),
        "perim_m": round(perim_m, 1),
        "mult": mult,
        "tips": FARM_TIPS[farm_type],
        "boq": BOQ_ITEMS.get(farm_type, []),
        "benchmarks": BENCHMARKS.get(farm_type, []),
        "generated": datetime.datetime.now().strftime("%d %B %Y %I:%M %p"),
        "ref_no": "FP-" + datetime.datetime.now().strftime("%Y%m%d%H%M"),
    }

# ─────────────────────────────────────────────────────────────────────────────
# REALISTIC ARCHITECTURAL MAP
# ─────────────────────────────────────────────────────────────────────────────

def draw_realistic_map(data):
    zones = data["zones"]
    acres = data["land_acres"]
    side_m = data["side_m"]
    farm = data["farm_type"]
    cntry = data["country"]

    fig = plt.figure(figsize=(20, 14), facecolor="#F4EFE6")
    ax = fig.add_axes([0.01, 0.08, 0.73, 0.84])
    ax.set_facecolor("#D9C9A3")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.add_patch(patches.Rectangle((0, 0), 100, 100, lw=0, facecolor="#8BC34A", zorder=1))
    ax.add_patch(patches.Rectangle((3.5, 3.5), 93, 93, lw=0, facecolor="#D9C9A3", zorder=2))
    ax.add_patch(patches.Rectangle((3.5, 3.5), 93, 93, lw=3, edgecolor="#212121", facecolor="none", zorder=25))

    PLOT_X0, PLOT_Y0, PLOT_W, PLOT_H = 4, 4, 92, 92
    GAP = 0.7
    LANE_W = 5.0

    top_z = [z for z in zones if z["ztype"] == "entry"]
    bot_z = [z for z in zones if z["ztype"] == "green"]
    road_z = [z for z in zones if z["ztype"] == "road"]
    main_z = [z for z in zones if z["ztype"] not in ("entry","green","road")]

    top_h = 9 if top_z else 0
    bot_h = 7 if bot_z else 0

    content_y0 = PLOT_Y0 + bot_h + GAP
    content_h = PLOT_H - top_h - bot_h - 2.5*GAP

    LEFT_W = (PLOT_W - LANE_W) * 0.58
    RIGHT_W = (PLOT_W - LANE_W) * 0.40
    LANE_X = PLOT_X0 + LEFT_W + GAP
    RIGHT_X = LANE_X + LANE_W + GAP

    n = len(main_z)
    n_left = math.ceil(n * 0.60)
    left_z = main_z[:n_left]
    right_z = main_z[n_left:]

    def col_place(zone_list, x0, width, y0, height):
        tot = sum(z["frac"] for z in zone_list) or 1
        avail = height - GAP * max(0, len(zone_list) - 1)
        y = y0
        out = []
        for z in zone_list:
            h = (z["frac"] / tot) * avail
            out.append((z, x0, y, width, h))
            y += h + GAP
        return out

    placed_left = col_place(left_z, PLOT_X0, LEFT_W, content_y0, content_h)
    placed_right = col_place(right_z, RIGHT_X, RIGHT_W, content_y0, content_h)

    placed_top = []
    if top_z:
        tw = PLOT_W / len(top_z)
        for i, z in enumerate(top_z):
            placed_top.append((z, PLOT_X0 + i*tw, PLOT_Y0+PLOT_H-top_h, tw-GAP, top_h-GAP))

    placed_bot = []
    if bot_z:
        bw = PLOT_W / len(bot_z)
        for i, z in enumerate(bot_z):
            placed_bot.append((z, PLOT_X0 + i*bw, PLOT_Y0, bw-GAP, bot_h-GAP))

    all_placed = placed_left + placed_right + placed_top + placed_bot

    def draw_zone(z, x, y, w, h):
        color = z["color"]
        hatch = z["hatch"]
        name = z["name"]
        ztype = z["ztype"]

        ax.add_patch(FancyBboxPatch((x+0.3, y-0.3), w, h, boxstyle="round,pad=0.1", lw=0, facecolor="#00000028", zorder=3))
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1", lw=1.6, edgecolor="#37474F", facecolor=color, zorder=4))

        if hatch:
            ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1", lw=0, facecolor="none", hatch=hatch, edgecolor="#00000015", zorder=5))

        ix, iy, iw, ih = x+0.9, y+0.9, w-1.8, h-1.8

        if ("Barn" in name or "Shed" in name or "Housing" in name or "House" in name) and ztype == "barn":
            if iw > 4 and ih > 4:
                n_stalls = max(2, int(iw / 2.4))
                for si in range(1, n_stalls):
                    sx = ix + si * (iw / n_stalls)
                    ax.plot([sx, sx], [iy, iy+ih], color="#546E7A", lw=0.55, ls="--", zorder=6, alpha=0.65)
                ax.add_patch(patches.Rectangle((ix, iy+ih-1.1), iw, 0.9, lw=0.8, edgecolor="#5D4037", facecolor="#BCAAA4", zorder=6))
                ax.text(ix+iw/2, iy+ih-0.65, "Feed Trough", ha="center", va="center", fontsize=4, color="#3E2723", fontfamily="monospace", zorder=7)
                ax.add_patch(patches.Rectangle((ix, iy), iw, 0.7, lw=0.6, edgecolor="#78909C", facecolor="#CFD8DC", zorder=6))
                ax.text(ix+iw/2, iy+0.35, "Drainage Gutter", ha="center", va="center", fontsize=3.8, color="#37474F", fontfamily="monospace", zorder=7)

        elif "Milking" in name or "Parlour" in name:
            if iw > 3 and ih > 3:
                mid_x = ix + iw/2
                ax.add_patch(patches.Rectangle((mid_x-0.6, iy+0.3), 1.2, ih-0.6, lw=0.8, edgecolor="#7B1FA2", facecolor="#F3E5F5", zorder=6))
                ax.text(mid_x, iy+ih/2, "Pit /\nOperator", ha="center", va="center", fontsize=3.8, color="#4A148C", fontfamily="monospace", zorder=7)
                n_s = max(2, int(ih / 2.2))
                for si in range(n_s):
                    sy = iy + 0.4 + si * (ih / n_s)
                    ax.plot([ix, mid_x-0.7], [sy, sy+0.7], color="#7B1FA2", lw=0.6, zorder=6, alpha=0.7)
                    ax.plot([mid_x+0.7, ix+iw], [sy, sy+0.7], color="#7B1FA2", lw=0.6, zorder=6, alpha=0.7)

        elif "Calf" in name or "Kidding" in name or "Brooder" in name:
            if iw > 3 and ih > 2:
                nx = max(2, int(iw / 1.9))
                ny = max(1, int(ih / 1.9))
                for pi in range(nx):
                    for pj in range(ny):
                        px = ix + pi * (iw / nx)
                        py = iy + pj * (ih / ny)
                        ax.add_patch(patches.Rectangle((px+0.1, py+0.1), iw/nx-0.2, ih/ny-0.2, lw=0.6, edgecolor="#546E7A", facecolor="none", zorder=6))

        elif "Feed" in name or "Fodder" in name or "Store" in name or "Mill" in name:
            if iw > 3 and ih > 2:
                n_bins = min(4, max(2, int(iw / 2.2)))
                for bi in range(n_bins):
                    bx = ix + 0.3 + bi * ((iw-0.3) / n_bins)
                    bw2 = (iw-0.3) / n_bins - 0.4
                    ax.add_patch(FancyBboxPatch((bx, iy+0.3), bw2, min(ih-0.6, 2.5), boxstyle="round,pad=0.1", lw=0.8, edgecolor="#5D4037", facecolor="#BCAAA4", zorder=6, alpha=0.85))

        elif "Silage" in name or "Compost" in name or "Manure" in name or "Waste" in name:
            if iw > 4:
                n_bays = 3
                for bi in range(1, n_bays):
                    bx = ix + bi * (iw / n_bays)
                    ax.plot([bx, bx], [iy, iy+ih], color="#546E7A", lw=1.0, zorder=6)
                ax.text(ix+iw/2, iy+0.5, "Bay 1 | Bay 2 | Bay 3", ha="center", fontsize=3.8, color="#3E2723", zorder=7)

        elif any(k in name for k in ("Raised Bed","Kitchen Garden","Crop","Veggie","Grazing","Paddock")):
            if ih > 2:
                n_rows = max(3, int(ih / 0.85))
                for ri in range(n_rows):
                    ry = iy + ri * (ih / n_rows)
                    ax.plot([ix+0.3, ix+iw-0.3], [ry, ry], color="#388E3C", lw=0.65, zorder=6, alpha=0.55)

        elif "Water" in name or "Tank" in name or "Well" in name:
            cx2, cy2 = ix+iw/2, iy+ih/2
            r2 = min(iw, ih) * 0.32
            ax.add_patch(Circle((cx2, cy2), r2+0.25, facecolor="#B3E5FC", edgecolor="#0277BD", lw=0.5, zorder=6))
            ax.add_patch(Circle((cx2, cy2), r2, facecolor="#29B6F6", edgecolor="#0277BD", lw=1.0, zorder=7))
            ax.add_patch(Circle((cx2, cy2), r2*0.45, facecolor="#81D4FA", lw=0, zorder=8))
            ax.text(cx2, cy2, "Tank", ha="center", va="center", fontsize=4.2, color="#01579B", fontweight="bold", zorder=9)

        elif "Biogas" in name:
            cx2, cy2 = ix+iw/2, iy+ih/2
            r2 = min(iw, ih) * 0.30
            ax.add_patch(Circle((cx2, cy2), r2, facecolor="#DCEDC8", edgecolor="#558B2F", lw=1.2, zorder=6))
            ax.text(cx2, cy2, "Dome", ha="center", va="center", fontsize=4, color="#33691E", fontweight="bold", zorder=7)

        elif "Net House" in name or "Poly" in name or "Nursery" in name:
            if iw > 2 and ih > 2:
                spacing = 0.9
                yy = iy
                while yy < iy+ih:
                    ax.plot([ix, ix+iw], [yy, yy], color="#0288D1", lw=0.35, alpha=0.4, zorder=6)
                    yy += spacing
                xx = ix
                while xx < ix+iw:
                    ax.plot([xx, xx], [iy, iy+ih], color="#0288D1", lw=0.35, alpha=0.4, zorder=6)
                    xx += spacing

        if hatch and h > 6 and w > 5:
            ax.add_patch(FancyBboxPatch((x+0.45, y+0.45), w-0.9, h-0.9, boxstyle="round,pad=0.05", lw=0.55, edgecolor="#546E7A", facecolor="none", ls=(0, (4, 3)), zorder=7, alpha=0.5))

        cx_l, cy_l = x+w/2, y+h/2
        words = name.split()
        if len(words) > 3:
            label = " ".join(words[:2]) + "\n" + " ".join(words[2:])
        else:
            label = name
        fs = max(4.5, min(8.0, h*0.85, w*0.5))
        ax.text(cx_l, cy_l+0.7, label, ha="center", va="center", fontsize=fs, fontweight="bold", color="#0D1B3E", fontfamily="DejaVu Sans", multialignment="center", zorder=11, path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])
        ax.text(cx_l, cy_l-0.9, f"{z['sqm']:,.0f} m2", ha="center", va="center", fontsize=max(3.8, fs-2.2), color="#37474F", style="italic", zorder=11, path_effects=[pe.withStroke(linewidth=1.5, foreground="white")])
        if z["capacity"]:
            ax.text(cx_l, cy_l-2.1, f"Cap: ~{z['capacity']}", ha="center", va="center", fontsize=max(3.5, fs-2.8), color="#B71C1C", fontweight="bold", zorder=11, path_effects=[pe.withStroke(linewidth=1.5, foreground="white")])

    for (z, x, y, w, h) in all_placed:
        draw_zone(z, x, y, w, h)

    ax.add_patch(patches.Rectangle((LANE_X, content_y0), LANE_W, content_h, lw=0, facecolor="#9E9E9E", zorder=3))
    for kx in [LANE_X+0.4, LANE_X+LANE_W-0.4]:
        ax.plot([kx, kx], [content_y0, content_y0+content_h], color="#616161", lw=0.6, zorder=4)
    dash_y = content_y0
    while dash_y < content_y0+content_h-2:
        ax.plot([LANE_X+LANE_W/2, LANE_X+LANE_W/2], [dash_y, dash_y+1.5], color="#EEEEEE", lw=1.0, zorder=5)
        dash_y += 3.0
    ax.text(LANE_X+LANE_W/2, content_y0+content_h/2, "SERVICE\nROAD", ha="center", va="center", fontsize=5, color="#212121", fontweight="bold", rotation=90, zorder=6, path_effects=[pe.withStroke(linewidth=2, foreground="#9E9E9E")])

    def draw_tree(tx, ty, r=1.2):
        ax.add_patch(Circle((tx+0.15, ty-0.15), r, facecolor="#1B5E2022", lw=0, zorder=6))
        ax.add_patch(Circle((tx, ty), r, facecolor="#2E7D32", edgecolor="#1B5E20", lw=0.4, zorder=7))
        ax.add_patch(Circle((tx-0.3, ty+0.35), r*0.55, facecolor="#388E3C", lw=0, zorder=8))
        ax.add_patch(Circle((tx+0.3, ty+0.2), r*0.45, facecolor="#43A047", lw=0, zorder=8))

    tree_step = 7
    for tx in range(5, 97, tree_step):
        draw_tree(tx, 2.0)
        draw_tree(tx, 98.0)
    for ty in range(5, 97, tree_step):
        draw_tree(2.0, ty)
        draw_tree(98.0, ty)

    water_placed = next((p for p in all_placed if any(k in p[0]["name"] for k in ("Water","Tank","Well"))), None)
    if water_placed:
        wz2, wx2, wy2, ww2, wh2 = water_placed
        wcx, wcy = wx2+ww2/2, wy2+wh2/2
        targets = [p for p in all_placed if any(k in p[0]["name"] for k in ("Barn","Shed","Housing","House","Calf","Milking","Parlour"))]
        for (tz, tx, ty, tw, th) in targets[:8]:
            tcx, tcy = tx+tw/2, ty+th/2
            ax.annotate("", xy=(tcx, tcy), xytext=(wcx, wcy), arrowprops=dict(arrowstyle="-", color="#0288D1", lw=0.8, connectionstyle="arc3,rad=0.15", linestyle=(0, (4, 3))), zorder=3)

    arrow_kw = dict(arrowstyle="->", color="#C62828", lw=1.8, mutation_scale=12, connectionstyle="arc3,rad=0.1")
    for i in range(min(3, len(placed_left)-1)):
        z1, x1, y1, w1, h1 = placed_left[i]
        z2, x2, y2, w2, h2 = placed_left[i+1]
        ax.annotate("", xy=(x2+w2/2, y2+h2+0.2), xytext=(x1+w1/2, y1-0.2), arrowprops=arrow_kw, zorder=15)

    gx = PLOT_X0 + PLOT_W/2 - 5
    ax.add_patch(patches.Rectangle((gx, PLOT_Y0+PLOT_H-1.8), 10, 2.2, lw=1.8, edgecolor="#1A237E", facecolor="#E8EAF6", zorder=20))
    for gp in [gx+0.2, gx+9.8-0.8]:
        ax.add_patch(patches.Rectangle((gp, PLOT_Y0+PLOT_H-2.5), 0.8, 3.0, lw=0.8, edgecolor="#1A237E", facecolor="#3949AB", zorder=21))
    ax.text(gx+5, PLOT_Y0+PLOT_H-0.7, "MAIN ENTRY GATE", ha="center", va="center", fontsize=5.5, fontweight="bold", color="#1A237E", zorder=22)
    ax.add_patch(patches.Rectangle((gx+1.5, PLOT_Y0+PLOT_H), 7, 3.5, lw=0, facecolor="#BDBDBD", zorder=3))

    def compass_rose(cx, cy, r=4.5):
        dirs = [(90,"N","#C62828"), (0,"E","#1A237E"), (270,"S","#2E7D32"), (180,"W","#E65100")]
        for ang, lbl, col in dirs:
            rad = math.radians(ang)
            ex = cx + r*math.cos(rad)
            ey = cy + r*math.sin(rad)
            ax.annotate("", xy=(ex, ey), xytext=(cx, cy), arrowprops=dict(arrowstyle="->", color=col, lw=2.2, mutation_scale=14), zorder=22)
            ax.text(cx+r*1.4*math.cos(rad), cy+r*1.4*math.sin(rad), lbl, ha="center", va="center", fontsize=9, fontweight="bold", color=col, zorder=23)
        ax.add_patch(Circle((cx, cy), 1.2, facecolor="white", edgecolor="#37474F", lw=1.2, zorder=21))
        ax.text(cx, cy, "+", ha="center", va="center", fontsize=8, color="#37474F", fontweight="bold", zorder=24)

    compass_rose(91, 8)

    units_per_m = 96.0 / side_m
    bar_m = max(5, round(20 / units_per_m / 5) * 5)
    bar_len = bar_m * units_per_m
    sb_x, sb_y = 5, 4.5
    ax.add_patch(patches.Rectangle((sb_x, sb_y), bar_len, 1.5, lw=0.8, edgecolor="#212121", facecolor="#212121", zorder=20))
    ax.add_patch(patches.Rectangle((sb_x+bar_len/2, sb_y), bar_len/2, 1.5, lw=0, facecolor="white", zorder=21))
    for xp, lbl in [(sb_x, "0"), (sb_x+bar_len/2, f"{bar_m//2}m"), (sb_x+bar_len, f"{bar_m}m")]:
        ax.text(xp, sb_y-0.9, lbl, ha="center", fontsize=5.2, color="#212121", zorder=22)
    ax.text(sb_x+bar_len/2, sb_y+0.65, "SCALE BAR", ha="center", va="center", fontsize=4.5, color="white", fontweight="bold", zorder=22)

    fig.text(0.01, 0.055, f"{acres} ACRE {farm_type.upper()} LAYOUT PLAN — {cntry.upper()}", fontsize=13, fontweight="bold", color="#1A237E")
    fig.text(0.01, 0.025, f"Ref: {data['ref_no']} | Generated: {data['generated']} | Total Area: {data['sqm']:,.0f} m2 | Site: ~{side_m:.0f}m x {side_m:.0f}m | FarmPlan Pro v2.0", fontsize=7.5, color="#546E7A")
    fig.text(0.01, 0.005, "This drawing is for planning reference only. Confirm with licensed agricultural/civil engineer before construction.", fontsize=6.5, color="#90A4AE", style="italic")

    ax_l = fig.add_axes([0.755, 0.08, 0.235, 0.84])
    ax_l.set_xlim(0, 10)
    ax_l.set_ylim(0, 10)
    ax_l.axis("off")
    ax_l.add_patch(FancyBboxPatch((0, 0), 10, 10, boxstyle="round,pad=0.1", lw=1.5, edgecolor="#37474F", facecolor="#FAFAFA", zorder=0))
    ax_l.add_patch(patches.Rectangle((0, 9.3), 10, 0.7, lw=0, facecolor="#1A237E", zorder=1))
    ax_l.text(5, 9.65, "ZONE LEGEND", ha="center", va="center", fontsize=8.5, fontweight="bold", color="white", zorder=2)

    leg_y = 9.15
    for z in zones:
        if leg_y < 2.8:
            break
        ax_l.add_patch(FancyBboxPatch((0.3, leg_y-0.28), 1.0, 0.52, boxstyle="round,pad=0.05", lw=0.7, edgecolor="#546E7A", facecolor=z["color"], zorder=2))
        nm = z["name"] if len(z["name"]) <= 22 else z["name"][:21] + "..."
        ax_l.text(1.5, leg_y, nm, va="center", fontsize=5.8, color="#1A237E", zorder=3)
        ax_l.text(9.7, leg_y, f"{z['frac']*100:.0f}%", va="center", ha="right", fontsize=5.5, color="#546E7A", zorder=3)
        leg_y -= 0.60

    ax_l.axhline(leg_y-0.1, color="#90A4AE", lw=0.7, xmin=0.03, xmax=0.97)
    ax_l.text(5, leg_y-0.45, f"Total: {data['sqm']:,.0f} m2 | {data['sqft']:,.0f} sq ft", ha="center", va="center", fontsize=5.5, color="#37474F", fontweight="bold")
    ax_l.text(5, leg_y-0.85, f"Dims: ~{data['side_m']}m x {data['side_m']}m", ha="center", va="center", fontsize=5.5, color="#37474F")
    ax_l.text(5, leg_y-1.25, f"Budget: {data['budget']}", ha="center", va="center", fontsize=5.5, color="#37474F")
    ax_l.axhline(leg_y-1.55, color="#90A4AE", lw=0.7, xmin=0.03, xmax=0.97)
    ax_l.text(0.4, leg_y-1.8, "MAP SYMBOLS", fontsize=6, fontweight="bold", color="#546E7A")
    syms = [("--->", "#C62828", "Animal movement flow"), ("....", "#0288D1", "Water supply pipelines"), ("tree", "#2E7D32", "Perimeter trees / windbreak"), ("////", "#546E7A", "Roofed / covered structure"), ("====", "#9E9E9E", "Service road / pathway")]
    sy2 = leg_y - 2.2
    for sym, col, desc in syms:
        ax_l.text(0.4, sy2, sym, color=col, fontsize=7.5, va="center", fontfamily="monospace")
        ax_l.text(2.0, sy2, desc, fontsize=5.5, color="#37474F", va="center")
        sy2 -= 0.52
    ax_l.axhline(sy2-0.1, color="#90A4AE", lw=0.7, xmin=0.03, xmax=0.97)
    ax_l.text(5, sy2-0.4, "Standards: ICAR / USDA / IS", ha="center", fontsize=5.2, color="#78909C")
    ax_l.text(5, sy2-0.75, "(c) FarmPlan Pro | Not for redistribution", ha="center", fontsize=4.8, color="#90A4AE", style="italic")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=220, bbox_inches="tight", facecolor="#F4EFE6")
    plt.close(fig)
    buf.seek(0)
    return buf.read()

# ─────────────────────────────────────────────────────────────────────────────
# PREMIUM 6-PAGE PDF ENGINE
# ─────────────────────────────────────────────────────────────────────────────

C = {
    "dark": colors.HexColor("#1A237E"), "mid": colors.HexColor("#283593"),
    "accent": colors.HexColor("#E53935"), "green": colors.HexColor("#2E7D32"),
    "gold": colors.HexColor("#F57F17"), "grey": colors.HexColor("#546E7A"),
    "light": colors.HexColor("#E8EAF6"), "lite2": colors.HexColor("#F3E5F5"),
    "row_a": colors.HexColor("#EDE7F6"), "row_b": colors.HexColor("#FAFAFA"),
    "lite3": colors.HexColor("#E8F5E9"), "white": colors.white,
    "black": colors.HexColor("#212121"), "border": colors.HexColor("#9FA8DA"),
    "amber": colors.HexColor("#FFF8E1"),
}

_S = None

def _build_styles():
    global _S
    b = getSampleStyleSheet()
    _S = {
        "cover_title": ParagraphStyle("ct", fontSize=26, fontName="Helvetica-Bold", textColor=C["white"], alignment=TA_CENTER, leading=32),
        "cover_sub": ParagraphStyle("cs", fontSize=11, fontName="Helvetica", textColor=colors.HexColor("#C5CAE9"), alignment=TA_CENTER, leading=15),
        "cover_meta": ParagraphStyle("cm", fontSize=8.5, fontName="Helvetica", textColor=colors.HexColor("#9FA8DA"), alignment=TA_CENTER),
        "h1": ParagraphStyle("h1", fontSize=14, fontName="Helvetica-Bold", textColor=C["dark"], spaceBefore=10, spaceAfter=3),
        "h2": ParagraphStyle("h2", fontSize=11, fontName="Helvetica-Bold", textColor=C["mid"], spaceBefore=7, spaceAfter=2),
        "h3": ParagraphStyle("h3", fontSize=9, fontName="Helvetica-Bold", textColor=C["grey"], spaceBefore=4, spaceAfter=2),
        "body": ParagraphStyle("bd", fontSize=8.5, fontName="Helvetica", textColor=C["black"], leading=13),
        "bi": ParagraphStyle("bi", fontSize=8.5, fontName="Helvetica-Oblique", textColor=C["grey"], leading=13),
        "tip_h": ParagraphStyle("th", fontSize=9, fontName="Helvetica-Bold", textColor=C["dark"], leading=13),
        "tip_b": ParagraphStyle("tb", fontSize=8.5, fontName="Helvetica", textColor=C["black"], leading=13, leftIndent=8),
        "cell": ParagraphStyle("cl", fontSize=8, fontName="Helvetica", textColor=C["black"], leading=11),
        "cellb": ParagraphStyle("cb", fontSize=8, fontName="Helvetica-Bold", textColor=C["black"], leading=11),
        "footer": ParagraphStyle("ft", fontSize=6.5, fontName="Helvetica", textColor=C["grey"], alignment=TA_CENTER),
        "right": ParagraphStyle("rt", fontSize=8, fontName="Helvetica", textColor=C["grey"], alignment=TA_RIGHT),
        "green_b": ParagraphStyle("gb", fontSize=8, fontName="Helvetica-Bold", textColor=C["green"], leading=11),
    }

def _hr(col=None, t=0.8):
    return HRFlowable(width="100%", thickness=t, color=col or C["dark"], spaceAfter=4, spaceBefore=2)

def _banner(txt, sub=None):
    rows = [[Paragraph(txt, _S["h1"])]]
    if sub:
        rows.append([Paragraph(sub, _S["bi"])])
    t = Table(rows, colWidths=[173*mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), C["dark"]), ("TEXTCOLOR", (0, 0), (-1, -1), C["white"]), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0,-1), (-1,-1), 8), ("LEFTPADDING", (0, 0), (-1, -1), 12)]))
    return [t, Spacer(1, 5*mm)]

def _tbl(data_rows, col_w, hdr_color=None, row_colors=None):
    t = Table(data_rows, colWidths=col_w, repeatRows=1)
    hc = hdr_color or C["dark"]
    ra, rb = (row_colors or [C["row_a"], C["row_b"]])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), hc), ("TEXTCOLOR", (0, 0), (-1, 0), C["white"]), ("ROWBACKGROUNDS",(0, 1), (-1,-1), [ra, rb]), ("BOX", (0, 0), (-1,-1), 0.8, C["dark"]), ("INNERGRID", (0, 0), (-1,-1), 0.4, C["border"]), ("TOPPADDING", (0, 0), (-1,-1), 4), ("BOTTOMPADDING", (0, 0), (-1,-1), 4), ("LEFTPADDING", (0, 0), (-1,-1), 6), ("VALIGN", (0, 0), (-1,-1), "MIDDLE")]))
    return t

def _page_cover(d):
    story = []
    hdr = Table([[Paragraph(f"{d['land_acres']} Acre", _S["cover_title"])], [Paragraph(d["farm_type"].upper() + " LAYOUT PLAN", _S["cover_title"])], [Paragraph(f"{d['country']} Edition — {d['budget']}", _S["cover_sub"])], [Spacer(1, 4*mm)], [Paragraph(f"Reference No: {d['ref_no']}", _S["cover_meta"])], [Paragraph(f"FarmPlan Pro v2.0 | {d['generated']}", _S["cover_meta"])]], colWidths=[173*mm])
    hdr.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,-1), C["dark"]), ("TOPPADDING", (0,0),(-1,-1), 14), ("BOTTOMPADDING", (0,-1),(-1,-1), 14), ("LEFTPADDING", (0,0),(-1,-1), 16), ("RIGHTPADDING", (0,0),(-1,-1), 16)]))
    story.append(hdr)
    story.append(Spacer(1, 5*mm))
    kpis = [(f"{d['land_acres']} acres", "Total Land", "#1A237E"), (f"{d['sqm']:,.0f} m2", "Area (sq m)", "#283593"), (f"{d['sqft']:,.0f} sqft", "Area (sq ft)", "#1565C0"), (f"~{d['side_m']}m x {d['side_m']}m","Dimensions","#0288D1"), (f"{len(d['zones'])} zones", "Layout Zones", "#2E7D32"), (f"Rs.{d['est_cost']/100000:.1f}L","Est. Cost", "#E53935")]
    n = len(kpis)
    kpi_w = 173*mm / n
    cells = []
    for val, lbl, col in kpis:
        inner = Table([[Paragraph(f'<font color="{col}"><b>{val}</b></font>', ParagraphStyle("kv",fontSize=12,fontName="Helvetica-Bold", alignment=TA_CENTER))], [Paragraph(lbl, ParagraphStyle("kl",fontSize=7,fontName="Helvetica", textColor=C["grey"],alignment=TA_CENTER))]], colWidths=[kpi_w])
        cells.append(inner)
    kt = Table([cells], colWidths=[kpi_w]*n)
    kt.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,-1), C["light"]), ("BOX", (0,0),(-1,-1), 0.8, C["border"]), ("INNERGRID", (0,0),(-1,-1), 0.5, C["border"]), ("TOPPADDING", (0,0),(-1,-1), 7), ("BOTTOMPADDING",(0,0),(-1,-1), 7)]))
    story.append(kt)
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("Project Overview", _S["h1"]))
    story.append(_hr())
    pr = [[Paragraph("<b>Parameter</b>", _S["cellb"]), Paragraph("<b>Value</b>", _S["cellb"]), Paragraph("<b>Parameter</b>", _S["cellb"]), Paragraph("<b>Value</b>", _S["cellb"])], [Paragraph("Farm Type", _S["cell"]), Paragraph(d["farm_type"], _S["cell"]), Paragraph("Country", _S["cell"]), Paragraph(d["country"], _S["cell"])], [Paragraph("Land Area", _S["cell"]), Paragraph(f"{d['land_acres']} acres ({d['sqm']:,.0f} m2)", _S["cell"]), Paragraph("Budget", _S["cell"]), Paragraph(d["budget"], _S["cell"])], [Paragraph("Perimeter", _S["cell"]), Paragraph(f"approx. {d['perim_m']} m", _S["cell"]), Paragraph("Reference", _S["cell"]), Paragraph(d["ref_no"], _S["cell"])], [Paragraph("Standards", _S["cell"]), Paragraph("ICAR / USDA / IS blended", _S["cell"]), Paragraph("Generated", _S["cell"]), Paragraph(d["generated"], _S["cell"])]]
    story.append(_tbl(pr, [40*mm, 46*mm, 40*mm, 47*mm]))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("Construction Specification", _S["h1"]))
    story.append(_hr(C["green"]))
    spec_rows = [[Paragraph("<b>Component</b>", _S["cellb"]), Paragraph("<b>Specification</b>",_S["cellb"])]]
    for k, v in d["budget_spec"].items():
        spec_rows.append([Paragraph(k, _S["cell"]), Paragraph(v, _S["cell"])])
    story.append(_tbl(spec_rows, [45*mm, 128*mm], hdr_color=C["green"], row_colors=[C["lite3"], C["row_b"]]))
    story.append(PageBreak())
    return story

def _page_map(map_png):
    story = []
    story += _banner("FARM LAYOUT MAP — ARCHITECTURAL TOP VIEW", "2D Engineering Drawing | Scale: Proportional | All zones to actual land allocation")
    img = RLImage(io.BytesIO(map_png), width=173*mm, height=123*mm)
    img.hAlign = "CENTER"
    story.append(img)
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("<i>This layout map shows a proportional top-view of the farm. Interior details (stall lines, feed troughs, drainage gutters, crop rows) are schematic. All zone areas, capacities, and infrastructure elements are shown in the tables on pages 3 and 4.</i>", ParagraphStyle("cap", fontSize=7.5, fontName="Helvetica-Oblique", textColor=C["grey"], alignment=TA_CENTER)))
    story.append(Spacer(1, 4*mm))
    leg_rows = [[Paragraph("<b>Element</b>", _S["cellb"]), Paragraph("<b>Meaning</b>", _S["cellb"]), Paragraph("<b>Element</b>", _S["cellb"]), Paragraph("<b>Meaning</b>", _S["cellb"])], [Paragraph("Hatch patterns (//,\\\\,xx)", _S["cell"]), Paragraph("Covered / roofed structures", _S["cell"]), Paragraph("Dotted blue lines", _S["cell"]), Paragraph("Water supply pipe network", _S["cell"])], [Paragraph("Red arrows", _S["cell"]), Paragraph("Primary animal movement flow", _S["cell"]), Paragraph("Green circles", _S["cell"]), Paragraph("Perimeter trees / windbreak", _S["cell"])], [Paragraph("Grey lane (SERVICE ROAD)", _S["cell"]), Paragraph("Internal service / access road", _S["cell"]), Paragraph("Compass rose", _S["cell"]), Paragraph("Site orientation (N/S/E/W)", _S["cell"])], [Paragraph("Dashed inner rectangle", _S["cell"]), Paragraph("Structural wall / column line", _S["cell"]), Paragraph("Scale bar (bottom-left)", _S["cell"]), Paragraph("Distance reference in metres", _S["cell"])]]
    story.append(Paragraph("Drawing Legend", _S["h2"]))
    story.append(_hr())
    story.append(_tbl(leg_rows, [42*mm, 44*mm, 42*mm, 45*mm]))
    story.append(PageBreak())
    return story

def _page_zones(d):
    story = []
    story += _banner("SECTION-WISE AREA & CAPACITY ANALYSIS")
    hdr = [Paragraph(h, _S["cellb"]) for h in ["Zone / Section", "% Share", "Area (m2)", "Area (sqft)", "Acres", "Capacity"]]
    rows = [hdr]
    for z in d["zones"]:
        cap = f"~{z['capacity']}" if z["capacity"] else "-"
        rows.append([Paragraph(z["name"], _S["cell"]), Paragraph(f"{z['frac']*100:.1f}%", _S["cell"]), Paragraph(f"{z['sqm']:,.1f}", _S["cell"]), Paragraph(f"{z['sqft']:,.0f}", _S["cell"]), Paragraph(f"{z['acres']:.4f}", _S["cell"]), Paragraph(cap, _S["cellb"])])
    rows.append([Paragraph("<b>TOTAL</b>", _S["cellb"]), Paragraph("<b>100%</b>", _S["cellb"]), Paragraph(f"<b>{d['sqm']:,.1f}</b>", _S["cellb"]), Paragraph(f"<b>{d['sqft']:,.0f}</b>", _S["cellb"]), Paragraph(f"<b>{d['land_acres']:.4f}</b>",_S["cellb"]), Paragraph("-", _S["cell"])])
    zt = Table(rows, colWidths=[56*mm, 18*mm, 25*mm, 28*mm, 20*mm, 26*mm], repeatRows=1)
    zt.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,0), C["dark"]), ("TEXTCOLOR", (0,0),(-1,0), C["white"]), ("ROWBACKGROUNDS",(0,1),(-1,-2),[C["row_a"],C["row_b"]]), ("BACKGROUND", (0,-1),(-1,-1), C["gold"]), ("TEXTCOLOR", (0,-1),(-1,-1), C["white"]), ("BOX", (0,0),(-1,-1), 0.8, C["dark"]), ("INNERGRID", (0,0),(-1,-1), 0.4, C["border"]), ("TOPPADDING", (0,0),(-1,-1), 4), ("BOTTOMPADDING", (0,0),(-1,-1), 4), ("LEFTPADDING", (0,0),(-1,-1), 6), ("ALIGN", (1,0),(-1,-1), "CENTER"), ("VALIGN", (0,0),(-1,-1), "MIDDLE")]))
    story.append(zt)
    story.append(Spacer(1, 5*mm))
    if any(v > 0 for v in d["animals"].values()):
        story.append(Paragraph("Animal Stock & Space Requirement", _S["h1"]))
        story.append(_hr(C["green"]))
        sp_map = ANIMAL_SPACE[d["farm_type"]]
        mult = d["mult"]
        ALBL = {"milch_cows": ("Milch Cows (Lactating)", "milch_cow"), "dry_cows": ("Dry Cows", "dry_cow"), "calves": ("Calves", "calf"), "goats": ("Goats", "goat"), "chickens": ("Chickens / Poultry", "chicken")}
        ah = [Paragraph(h, _S["cellb"]) for h in ["Animal Type","Count","Space/Head (m2)","Total Space (m2)","% of Land"]]
        arows = [ah]
        for key, (lbl, sk) in ALBL.items():
            cnt = d["animals"].get(key, 0)
            if cnt > 0:
                sph = sp_map.get(sk, 18) * mult
                tot = cnt * sph
                pct = tot / d["sqm"] * 100
                arows.append([Paragraph(lbl, _S["cell"]), Paragraph(str(cnt), _S["cell"]), Paragraph(f"{sph:.1f}", _S["cell"]), Paragraph(f"{tot:,.1f}", _S["cell"]), Paragraph(f"{pct:.1f}%", _S["cell"])])
        story.append(_tbl(arows, [58*mm,18*mm,34*mm,34*mm,29*mm], hdr_color=C["green"], row_colors=[C["lite3"], C["row_b"]]))
        story.append(Spacer(1, 5*mm))
    if d["infra_rows"]:
        story.append(Paragraph("Infrastructure Inclusion Summary", _S["h1"]))
        story.append(_hr(C["gold"]))
        ih = [Paragraph(h, _S["cellb"]) for h in ["Infrastructure Item","Status","Specification / Note"]]
        irows = [ih]
        for item, status, note in d["infra_rows"]:
            irows.append([Paragraph(item, _S["cell"]), Paragraph(f'<font color="#2E7D32"><b>{status}</b></font>', _S["cell"]), Paragraph(note, _S["cell"])])
        story.append(_tbl(irows, [60*mm,25*mm,88*mm], hdr_color=C["gold"], row_colors=[C["amber"], C["row_b"]]))
    story.append(PageBreak())
    return story

def _page_cost(d):
    story = []
    story += _banner("PRELIMINARY COST ESTIMATE", "Indicative only. Verify with local contractor. GST / taxes extra.")
    rates = COST_PER_SQFT[d["budget"]]
    sqft = d["sqft"]
    perim_ft = d["perim_m"] * 3.281
    items = [("Site Clearing & Levelling", sqft, 15), ("Covered Structures (55%)", sqft * 0.55, rates["covered"]), ("Open Yards & Paddocks (20%)", sqft * 0.20, rates["open"]), ("Water, Elec & Services", sqft, rates["services"]), ("Fencing & Gates", perim_ft, 85), ("Landscaping & Trees", sqft, 12)]
    ch = [Paragraph(h, _S["cellb"]) for h in ["Item","Quantity","Rate (Rs/sqft)","Est. Cost (Rs)"]]
    crows = [ch]
    sub = 0
    for item, qty, rate in items:
        cost = qty * rate
        sub += cost
        crows.append([Paragraph(item, _S["cell"]), Paragraph(f"{qty:,.0f} sqft", _S["cell"]), Paragraph(str(rate), _S["cell"]), Paragraph(f"Rs.{cost:,.0f}", _S["cellb"])])
    cont = sub * 0.10
    total = sub + cont
    crows.append([Paragraph("<b>Sub-total</b>", _S["cellb"]), Paragraph("", _S["cell"]), Paragraph("", _S["cell"]), Paragraph(f"<b>Rs.{sub:,.0f}</b>", _S["cellb"])])
    crows.append([Paragraph("<b>Contingency @ 10%</b>", _S["cellb"]), Paragraph("", _S["cell"]), Paragraph("", _S["cell"]), Paragraph(f"<b>Rs.{cont:,.0f}</b>", _S["cellb"])])
    crows.append([Paragraph("<b>GRAND TOTAL (Indicative)</b>", _S["cellb"]), Paragraph("", _S["cell"]), Paragraph("", _S["cell"]), Paragraph(f"<b>Rs.{total:,.0f}</b>", _S["cellb"])])
    ct = Table(crows, colWidths=[72*mm, 38*mm, 28*mm, 35*mm], repeatRows=1)
    ct.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,0), C["dark"]), ("TEXTCOLOR", (0,0),(-1,0), C["white"]), ("ROWBACKGROUNDS",(0,1),(-1,-4),[C["row_a"],C["row_b"]]), ("BACKGROUND", (0,-3),(-1,-3), colors.HexColor("#ECEFF1")), ("BACKGROUND", (0,-2),(-1,-2), colors.HexColor("#E3F2FD")), ("BACKGROUND", (0,-1),(-1,-1), C["accent"]), ("TEXTCOLOR", (0,-1),(-1,-1), C["white"]), ("BOX", (0,0),(-1,-1), 0.8, C["dark"]), ("INNERGRID", (0,0),(-1,-1), 0.4, C["border"]), ("TOPPADDING", (0,0),(-1,-1), 4), ("BOTTOMPADDING", (0,0),(-1,-1), 4), ("LEFTPADDING", (0,0),(-1,-1), 6), ("ALIGN", (1,0),(-1,-1), "CENTER"), ("VALIGN", (0,0),(-1,-1), "MIDDLE")]))
    story.append(ct)
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("<i>* Rates are indicative. Actual costs vary by location, material, and contractor. Get minimum 3 quotes. GST / professional fees not included.</i>", ParagraphStyle("d2", fontSize=7.5, fontName="Helvetica-Oblique", textColor=C["grey"], leading=11)))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("Bill of Quantities (BOQ) Skeleton", _S["h1"]))
    story.append(_hr(C["green"]))
    story.append(Paragraph("The following items should be fully quantified and priced by a licensed civil contractor or quantity surveyor for final tendering.", _S["bi"]))
    story.append(Spacer(1, 3*mm))
    bh = [Paragraph(h, _S["cellb"]) for h in ["#","BOQ Item","Unit","Remarks"]]
    brows = [bh]
    for i, (item, unit, rem) in enumerate(d["boq"], 1):
        brows.append([Paragraph(str(i), _S["cell"]), Paragraph(item, _S["cell"]), Paragraph(unit, _S["cell"]), Paragraph(rem, _S["cell"])])
    story.append(_tbl(brows, [10*mm, 82*mm, 30*mm, 51*mm], hdr_color=C["green"], row_colors=[C["lite3"], C["row_b"]]))
    story.append(PageBreak())
    return story

def _page_tips(d):
    story = []
    story += _banner("EXPERT SETUP & MANAGEMENT GUIDELINES", f"Specific to {d['farm_type']} — {d['country']} conditions")
    for i, (heading, body_text) in enumerate(d["tips"], 1):
        num_style = ParagraphStyle("tn", fontSize=13, fontName="Helvetica-Bold", textColor=C["white"], alignment=TA_CENTER)
        num_cell = Table([[Paragraph(str(i).zfill(2), num_style)]], colWidths=[13*mm], style=[("BACKGROUND",(0,0),(-1,-1),C["accent"] if i%2==0 else C["dark"]), ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)])
        body_cell = Table([[Paragraph(heading, _S["tip_h"])], [Paragraph(body_text, _S["tip_b"])]], colWidths=[154*mm], style=[("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4), ("LEFTPADDING",(0,0),(-1,-1),8)])
        tip = Table([[num_cell, body_cell]], colWidths=[15*mm, 158*mm])
        tip.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,-1), C["light"]), ("BOX", (0,0),(-1,-1), 0.6, C["border"]), ("TOPPADDING", (0,0),(-1,-1), 0), ("BOTTOMPADDING", (0,0),(-1,-1), 0), ("LEFTPADDING", (0,0),(-1,-1), 0), ("RIGHTPADDING", (0,0),(-1,-1), 0), ("VALIGN", (0,0),(-1,-1), "MIDDLE")]))
        story.append(KeepTogether([tip, Spacer(1, 3*mm)]))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("Pre-Construction Compliance Checklist", _S["h1"]))
    story.append(_hr(C["gold"]))
    checks = [("Obtain local panchayat / municipal NOC for construction", "Gram Panchayat / ULB"), ("Verify agricultural land-use conversion requirements", "Revenue / Town Planning"), ("Apply for NABARD / Mudra / KCC loan if bank financed", "Bank / NABARD"), ("Soil test (pH, N-P-K, organic matter) before first season", "Soil Testing Lab"), ("Register farm with state animal husbandry / agri department", "Animal Husbandry Dept"), ("Obtain borewell / irrigation source permit", "Irrigation / Water Dept"), ("FSSAI registration for direct dairy / food product sales", "FSSAI"), ("Consult ICAR / KVK for region-specific breed / variety", "ICAR / KVK"), ("Maintain 30 m setback from waterbody / reserved forest", "Forest / Water Dept"), ("Fire NOC for feed storage structures above 200 sq m", "Fire Department")]
    ch = [Paragraph(h, _S["cellb"]) for h in ["#","Compliance Action","Responsible Agency"]]
    crows = [ch]
    for i, (act, agency) in enumerate(checks, 1):
        crows.append([Paragraph(str(i), _S["cell"]), Paragraph(act, _S["cell"]), Paragraph(agency, _S["cell"])])
    story.append(_tbl(crows, [10*mm,116*mm,47*mm], hdr_color=C["gold"], row_colors=[C["amber"], C["row_b"]]))
    story.append(PageBreak())
    return story

def _page_final(d):
    story = []
    story += _banner("DEVELOPMENT TIMELINE & PERFORMANCE BENCHMARKS")
    phases = [("Month 1-2", "Planning & Approvals", "Finalise layout, obtain NOCs, soil test, contractor quotes, financing"), ("Month 2-4", "Site Preparation", "Land levelling, boundary fencing, access road, borewell / water source"), ("Month 4-7", "Primary Construction", "Foundation, columns, roofing of main housing / production zones"), ("Month 7-9", "Secondary Structures", "Feed store, utility rooms, milking area, flooring completion"), ("Month 9-10", "Services & Fittings", "Water pipeline, electrical, drainage, fans / ventilation"), ("Month 10-11", "Equipment Installation", "Feeders, waterers, milking machine, monitoring systems"), ("Month 11-12", "Trial & Commissioning", "Animal introduction, staff training, record system setup"), ("Month 12+", "Full Operation", "Regular monitoring, quarterly vet check, annual maintenance budget")]
    ph = [Paragraph(h, _S["cellb"]) for h in ["Phase","Activity","Key Tasks"]]
    prows = [ph]
    for phase, act, tasks in phases:
        prows.append([Paragraph(phase, _S["cellb"]), Paragraph(act, _S["cell"]), Paragraph(tasks, _S["cell"])])
    story.append(_tbl(prows, [22*mm, 38*mm, 113*mm]))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("Target Performance Benchmarks", _S["h1"]))
    story.append(_hr(C["green"]))
    bh = [Paragraph(h, _S["cellb"]) for h in ["Parameter","Standard Target","Best-in-Class Target"]]
    brows = [bh]
    for param, std, best in d["benchmarks"]:
        brows.append([Paragraph(param, _S["cell"]), Paragraph(std, _S["cell"]), Paragraph(best, _S["green_b"])])
    story.append(_tbl(brows, [72*mm, 50*mm, 51*mm], hdr_color=C["green"], row_colors=[C["lite3"], C["row_b"]]))
    story.append(Spacer(1, 6*mm))
    story.append(_hr(C["grey"], t=0.5))
    disc = ("DISCLAIMER: This farm layout plan is generated for planning and decision-support purposes only, based on standard agricultural engineering guidelines blended with ICAR, USDA, and international livestock standards. All area figures, cost estimates, and production benchmarks are indicative. Before commencing construction, engage a licensed agricultural or civil engineer for site survey, structural design, and final working drawings. Regulations vary by state and country - verify all local norms. FarmPlan Pro accepts no liability for construction or operational decisions made solely on the basis of this plan.")
    story.append(Paragraph(disc, _S["footer"]))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(f"(c) FarmPlan Pro | Ref: {d['ref_no']} | {d['generated']} | Licensed for purchaser personal / business use only. Not for redistribution.", _S["footer"]))
    return story

def generate_pdf(data, map_png):
    _build_styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=14*mm, bottomMargin=14*mm, title=f"{data['land_acres']}A {data['farm_type']} Plan - {data['country']}", author="FarmPlan Pro", subject="Premium Agricultural Layout Plan", creator="FarmPlan Pro v2.0")
    story = []
    story += _page_cover(data)
    story += _page_map(map_png)
    story += _page_zones(data)
    story += _page_cost(data)
    story += _page_tips(data)
    story += _page_final(data)
    doc.build(story)
    buf.seek(0)
    return buf.read()

# ─────────────────────────────────────────────────────────────────────────────
# STREAMLIT UI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="FarmPlan Pro — Premium Layout Generator", page_icon="🌾", layout="wide", initial_sidebar_state="expanded")
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
    html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
    .stApp{background:#F0F4F8;}
    .block-container{padding-top:1rem;}
    section[data-testid="stSidebar"]{background:#1A237E;}
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span{color:#C5CAE9 !important;}
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3{color:#9FA8DA !important;}
    .stButton>button{
        background:linear-gradient(135deg,#E53935,#B71C1C);
        color:white;border:none;border-radius:8px;
        padding:.7rem 1.5rem;font-size:1rem;font-weight:700;width:100%;
    }
    .stDownloadButton>button{
        background:linear-gradient(135deg,#2E7D32,#1B5E20);
        color:white;border:none;border-radius:8px;
        padding:.8rem 1.5rem;font-size:1.1rem;font-weight:700;width:100%;
    }
    .kcard{background:white;border-radius:10px;padding:.85rem 1rem;
           box-shadow:0 2px 10px rgba(0,0,0,.07);border-left:4px solid #1A237E;}
    .kcard .v{font-size:1.3rem;font-weight:700;color:#1A237E;}
    .kcard .l{font-size:.7rem;color:#78909C;margin-top:2px;}
    </style>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg,#1A237E,#283593 60%,#3949AB);
                padding:1.2rem 2rem;border-radius:14px;margin-bottom:1.2rem;
                box-shadow:0 4px 24px rgba(26,35,126,.22);">
      <div style="display:flex;align-items:center;gap:1rem;">
        <span style="font-size:2.8rem;">🌾</span>
        <div>
          <h1 style="color:white;margin:0;font-size:1.9rem;">FarmPlan Pro
            <span style="font-size:.9rem;opacity:.6;font-weight:400"> v2.0</span></h1>
          <p style="color:#9FA8DA;margin:0;font-size:.9rem;">
            Architectural-Grade Farm Layout PDFs · Sell at Rs.5,000–Rs.8,000 per plan
          </p>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("## Farm Configuration")
        st.markdown("---")
        st.markdown("### Land & Location")
        c1, c2 = st.columns([2, 1])
        with c1:
            land_size = st.number_input("Land Size", 0.5, 500.0, 2.0, 0.5)
        with c2:
            unit = st.selectbox("Unit", ["Acres","Hectares"])
        land_acres = land_size if unit == "Acres" else land_size * 2.47105
        country = st.selectbox("Country / Region", COUNTRIES)
        farm_type = st.selectbox("Farm Type", FARM_TYPES)
        st.markdown("### Animal Count")
        milch_cows = st.number_input("Milch Cows", 0, 500, 10, 1)
        dry_cows = st.number_input("Dry Cows", 0, 500, 4, 1)
        calves = st.number_input("Calves", 0, 500, 6, 1)
        goats = st.number_input("Goats", 0,2000, 0,10)
        chickens = st.number_input("Chickens / Poultry",0,10000, 0,50)
        st.markdown("### Infrastructure")
        milking = st.checkbox("Milking Parlour", True)
        isolation = st.checkbox("Isolation / Sick Pen", True)
        fodder = st.checkbox("Fodder & Feed Storage", True)
        water = st.checkbox("Water Supply System", True)
        biogas = st.checkbox("Biogas / Waste Mgmt", False)
        fencing = st.checkbox("Perimeter Fencing", True)
        solar = st.checkbox("Solar / Renewable Energy",False)
        office = st.checkbox("Office / Guard Room", True)
        st.markdown("### Budget Level")
        budget = st.radio("", BUDGET_LEVELS, index=1)
        st.markdown("---")
        gen = st.button("Generate Premium Farm Plan", use_container_width=True)

    if gen:
        animals = dict(milch_cows=milch_cows, dry_cows=dry_cows, calves=calves, goats=goats, chickens=chickens)
        infra = dict(milking=milking, isolation=isolation, fodder=fodder, water=water, biogas=biogas, fencing=fencing, solar=solar, office=office)
        with st.spinner("Drawing architectural map and assembling 6-page PDF..."):
            d = calculate_layout(land_acres, country, farm_type, animals, infra, budget)
            img = draw_realistic_map(d)
            pdf = generate_pdf(d, img)
        st.success(f"Plan ready — Ref: {d['ref_no']}")
        cols = st.columns(6)
        for col, (v, l) in zip(cols, [(f"{d['land_acres']:.2f} ac", "Total Land"), (f"{d['sqm']:,.0f} m2", "Area m2"), (f"{d['sqft']:,.0f} sqft", "Area sqft"), (f"Rs.{d['est_cost']/100000:.1f}L","Est. Cost"), (f"{len(d['zones'])} zones", "Layout Zones"), (f"~{d['side_m']}m side", "Site Dimension")]):
            with col:
                st.markdown(f'<div class="kcard"><div class="v">{v}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        mc, dc = st.columns([3, 2])
        with mc:
            st.markdown("### Architectural Farm Layout Map")
            st.image(img, use_container_width=True)
        with dc:
            st.markdown("### Zone Breakdown")
            for z in d["zones"]:
                cap = f" · Cap: ~{z['capacity']}" if z["capacity"] else ""
                st.markdown(f"**{z['name']}** — {z['frac']*100:.1f}% · {z['sqm']:,.0f} m2{cap}")
                st.progress(z["frac"])
        st.markdown("---")
        fname = (f"FarmPlan_{land_size}{unit[0]}_{farm_type.replace(' ','_')}_{country}_{d['ref_no']}.pdf")
        st.download_button("Download Complete Premium PDF Farm Plan (6 Pages)", data=pdf, file_name=fname, mime="application/pdf", use_container_width=True)
        st.markdown(f"""
        <div style="background:#E8F5E9;border-radius:10px;padding:1rem 1.5rem;
                    border-left:4px solid #2E7D32;margin-top:1rem;font-size:.9rem;">
          <b>Your 6-page PDF includes:</b><br>
          Page 1 — Project overview, KPI summary, construction specification<br>
          Page 2 — Full architectural layout map with drawing legend<br>
          Page 3 — Zone area table, animal capacity, infrastructure list<br>
          Page 4 — Preliminary cost estimate + BOQ skeleton<br>
          Page 5 — 8 expert management tips + compliance checklist<br>
          Page 6 — 12-month development timeline + performance benchmarks
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:2rem 1rem;">
          <div style="font-size:4.5rem;">🌾</div>
          <h2 style="color:#1A237E;">Configure your farm in the sidebar, then click Generate</h2>
          <p style="color:#546E7A;max-width:560px;margin:.8rem auto;font-size:1rem;line-height:1.7;">
            Produces a 6-page professional PDF with architectural map,
            cost estimates, BOQ, compliance checklist, expert guidelines
            and performance benchmarks — ready to sell at Rs.5,000–Rs.8,000.
          </p>
        </div>""", unsafe_allow_html=True)
        feats = [("Architectural Map", "Realistic top-view with stall lines, troughs, crop rows, trees, water pipes, compass & scale bar"), ("Cost Estimate", "Preliminary cost breakdown + BOQ skeleton (6 line items + contingency)"), ("Expert Tips", "8 farm-type-specific, actionable management guidelines"), ("Compliance List", "10-point pre-construction legal & regulatory checklist"), ("Dev Timeline", "8-phase, 12-month construction & commissioning plan"), ("Benchmarks", "Standard vs best-in-class KPIs for farm performance")]
        r1, r2 = st.columns(3), st.columns(3)
        for i, (title, desc) in enumerate(feats):
            col = r1[i] if i < 3 else r2[i-3]
            with col:
                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:1.1rem;
                            box-shadow:0 2px 10px rgba(0,0,0,.07);margin-bottom:1rem;
                            border-top:3px solid #1A237E;">
                  <div style="font-weight:700;color:#1A237E;margin-bottom:.3rem;">{title}</div>
                  <div style="font-size:.82rem;color:#78909C;">{desc}</div>
                </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT — FIXED!
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
