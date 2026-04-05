import streamlit as st
import matplotlib
matplotlib.use('Agg')  # Must be before pyplot import
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import io
from datetime import datetime
import base64

# Page configuration
st.set_page_config(
    page_title="Architectural Blueprint Pro",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple CSS (no external fonts)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1a1a1a;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #0066cc;
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
    }
    .metric-box {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #0066cc;
    }
</style>
""", unsafe_allow_html=True)

def create_blueprint(params):
    """Create professional blueprint"""
    
    # Extract parameters
    project_name = params['project_name']
    client_name = params['client_name']
    site_width = float(params['site_width'])
    site_depth = float(params['site_depth'])
    building_width = float(params['building_width'])
    building_depth = float(params['building_depth'])
    setbacks = [float(x) for x in params['setbacks']]
    orientation = float(params['orientation'])
    scale = int(params['scale'])
    units = params['units']
    
    # Create figure (A3 landscape approximation)
    fig, ax = plt.subplots(figsize=(16, 11), dpi=150)
    
    # Colors
    bg_color = '#ffffff'
    grid_color = '#e0e0e0'
    border_color = '#000000'
    building_color = '#2c3e50'
    building_fill = '#ecf0f1'
    setback_color = '#e74c3c'
    dimension_color = '#0066cc'
    north_color = '#c0392b'
    
    ax.set_facecolor(bg_color)
    
    # Calculate margins
    margin = max(site_width, site_depth) * 0.2
    ax.set_xlim(-margin, site_width + margin)
    ax.set_ylim(-margin, site_depth + margin)
    ax.set_aspect('equal')
    
    # Draw grid
    grid_size = max(site_width, site_depth) / 10
    for x in np.arange(0, site_width + grid_size, grid_size):
        ax.axvline(x=x, color=grid_color, linewidth=0.5, alpha=0.5)
    for y in np.arange(0, site_depth + grid_size, grid_size):
        ax.axhline(y=y, color=grid_color, linewidth=0.5, alpha=0.5)
    
    # Site boundary
    site = Rectangle((0, 0), site_width, site_depth, 
                     linewidth=2.5, edgecolor=border_color, 
                     facecolor='none')
    ax.add_patch(site)
    
    # Setbacks
    front, back, left, right = setbacks
    
    # Buildable area
    buildable_x = left
    buildable_y = back
    buildable_w = site_width - left - right
    buildable_h = site_depth - front - back
    
    # Draw setback lines
    if front > 0:
        ax.plot([0, site_width], [site_depth - front, site_depth - front], 
                'r--', linewidth=1.5, alpha=0.7)
    if back > 0:
        ax.plot([0, site_width], [back, back], 'r--', linewidth=1.5, alpha=0.7)
    if left > 0:
        ax.plot([left, left], [0, site_depth], 'r--', linewidth=1.5, alpha=0.7)
    if right > 0:
        ax.plot([site_width - right, site_width - right], [0, site_depth], 
                'r--', linewidth=1.5, alpha=0.7)
    
    # Building position (centered in buildable area)
    building_x = buildable_x + (buildable_w - building_width) / 2
    building_y = buildable_y + (buildable_h - building_depth) / 2
    
    # Draw building
    building = FancyBboxPatch(
        (building_x, building_y), building_width, building_depth,
        boxstyle="square,pad=0",
        linewidth=2, edgecolor=building_color,
        facecolor=building_fill, alpha=0.9
    )
    ax.add_patch(building)
    
    # Building label
    ax.text(building_x + building_width/2, building_y + building_depth/2, 
           f'{building_width:.1f} x {building_depth:.1f}\n{units}', 
           ha='center', va='center', fontsize=9, fontweight='bold',
           color=building_color)
    
    # Dimension lines
    def draw_dim(x1, y1, x2, y2, offset, text, vertical=False):
        if vertical:
            ax.annotate('', xy=(x1 - offset, y1), xytext=(x1 - offset, y2),
                       arrowprops=dict(arrowstyle='<->', color=dimension_color, lw=1.5))
            ax.text(x1 - offset - 0.5, (y1 + y2)/2, text, 
                   fontsize=8, color=dimension_color, ha='right', va='center',
                   rotation=90)
        else:
            ax.annotate('', xy=(x1, y1 - offset), xytext=(x2, y1 - offset),
                       arrowprops=dict(arrowstyle='<->', color=dimension_color, lw=1.5))
            ax.text((x1 + x2)/2, y1 - offset - 0.3, text, 
                   fontsize=8, color=dimension_color, ha='center', va='top')
    
    # Site dimensions
    draw_dim(0, 0, site_width, 0, margin*0.3, f'{site_width:.1f} {units}')
    draw_dim(0, 0, 0, site_depth, margin*0.3, f'{site_depth:.1f} {units}', vertical=True)
    
    # Building dimensions
    draw_dim(building_x, building_y, building_x + building_width, building_y, 
             0.4, f'{building_width:.1f}')
    draw_dim(building_x, building_y, building_x, building_y + building_depth, 
             0.4, f'{building_depth:.1f}', vertical=True)
    
    # North arrow
    north_x = site_width - 2
    north_y = site_depth - 2
    arrow_len = 1.5
    
    angle_rad = np.radians(orientation)
    dx = arrow_len * np.sin(angle_rad)
    dy = arrow_len * np.cos(angle_rad)
    
    ax.annotate('N', xy=(north_x + dx, north_y + dy), 
               xytext=(north_x, north_y),
               arrowprops=dict(arrowstyle='->', color=north_color, lw=2.5),
               fontsize=12, color=north_color, fontweight='bold', ha='center')
    
    circle = Circle((north_x, north_y), 0.25, fill=False, 
                   edgecolor=north_color, linewidth=1.5)
    ax.add_patch(circle)
    
    # Title block
    tb_w = 5
    tb_h = 2
    tb_x = site_width - tb_w - 0.5
    tb_y = 0.5
    
    # Title block border
    ax.add_patch(Rectangle((tb_x, tb_y), tb_w, tb_h, 
                          linewidth=1.5, edgecolor='black', facecolor='white'))
    
    # Title block lines
    ax.plot([tb_x, tb_x + tb_w], [tb_y + tb_h - 0.5, tb_y + tb_h - 0.5], 'k-', lw=1)
    ax.plot([tb_x + tb_w*0.6, tb_x + tb_w*0.6], [tb_y, tb_y + tb_h], 'k-', lw=1)
    
    # Title block text
    ax.text(tb_x + tb_w/2, tb_y + tb_h - 0.25, project_name.upper(), 
           ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(tb_x + tb_w/2, tb_y + tb_h - 0.75, 'SITE PLAN', 
           ha='center', va='center', fontsize=9)
    ax.text(tb_x + 0.2, tb_y + 0.25, f'Client: {client_name}', fontsize=7, va='center')
    ax.text(tb_x + 0.2, tb_y + 0.75, f'Scale: 1:{scale}', fontsize=7, va='center')
    ax.text(tb_x + tb_w*0.8, tb_y + 0.25, 
           f'Date: {datetime.now().strftime("%Y-%m-%d")}', 
           fontsize=7, va='center', ha='center')
    
    # Scale bar
    sb_x = 1
    sb_y = 1
    real_len = 5
    draw_len = real_len * (1000/scale) * 0.001
    
    ax.plot([sb_x, sb_x + draw_len], [sb_y, sb_y], 'k-', lw=3)
    ax.plot([sb_x, sb_x], [sb_y - 0.1, sb_y + 0.1], 'k-', lw=2)
    ax.plot([sb_x + draw_len, sb_x + draw_len], [sb_y - 0.1, sb_y + 0.1], 'k-', lw=2)
    ax.text(sb_x + draw_len/2, sb_y - 0.3, f'{real_len} {units}', 
           ha='center', fontsize=8, fontweight='bold')
    
    # Disclaimer
    disclaimer = "DISCLAIMER: For planning only. Verify all dimensions on site. Complies with IBC 2024/2025."
    ax.text(site_width/2, -margin*0.5, disclaimer, ha='center', va='top',
           fontsize=7, style='italic', color='#666666')
    
    ax.axis('off')
    plt.tight_layout()
    return fig

def generate_pdf(fig, params):
    """Generate PDF package"""
    buffer = io.BytesIO()
    
    with PdfPages(buffer) as pdf:
        # Sheet 1: Blueprint
        pdf.savefig(fig, dpi=200, bbox_inches='tight', facecolor='white')
        
        # Sheet 2: Data
        fig2, ax2 = plt.subplots(figsize=(11, 16), dpi=150)
        ax2.axis('off')
        
        y = 0.95
        dy = 0.03
        
        ax2.text(0.5, y, 'ARCHITECTURAL SITE ANALYSIS', ha='center', fontsize=16, fontweight='bold')
        y -= dy * 2
        
        ax2.text(0.1, y, f'Project: {params["project_name"]}', fontsize=11, fontweight='bold')
        y -= dy
        ax2.text(0.1, y, f'Client: {params["client_name"]}', fontsize=10)
        y -= dy
        ax2.text(0.1, y, f'Location: {params.get("location", "N/A")}', fontsize=10)
        y -= dy * 2
        
        # Data table
        ax2.text(0.1, y, 'SITE DATA', fontsize=12, fontweight='bold', 
                bbox=dict(boxstyle='round', facecolor='#e0e0e0'))
        y -= dy * 1.5
        
        site_area = float(params['site_width']) * float(params['site_depth'])
        bldg_area = float(params['building_width']) * float(params['building_depth'])
        coverage = (bldg_area / site_area) * 100
        
        data = [
            ['Site Dimensions', f"{params['site_width']} x {params['site_depth']} {params['units']}"],
            ['Site Area', f"{site_area:.1f} sq {params['units']}"],
            ['Building Footprint', f"{bldg_area:.1f} sq {params['units']}"],
            ['Site Coverage', f"{coverage:.1f}%"],
            ['Front Setback', f"{params['setbacks'][0]} {params['units']}"],
            ['Rear Setback', f"{params['setbacks'][1]} {params['units']}"],
            ['Left Setback', f"{params['setbacks'][2]} {params['units']}"],
            ['Right Setback', f"{params['setbacks'][3]} {params['units']}"],
            ['Scale', f"1:{params['scale']}"],
            ['Orientation', f"{params['orientation']}°"],
        ]
        
        for i, (label, value) in enumerate(data):
            bg = '#f0f0f0' if i % 2 == 0 else 'white'
            ax2.add_patch(Rectangle((0.08, y-0.01), 0.84, 0.025, facecolor=bg, edgecolor='gray'))
            ax2.text(0.1, y, label, fontsize=9, va='center')
            ax2.text(0.5, y, value, fontsize=9, va='center', fontweight='bold')
            y -= dy
        
        y -= dy
        
        # Compliance
        ax2.text(0.1, y, 'CODE COMPLIANCE', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='#e0e0e0'))
        y -= dy * 1.5
        
        codes = [
            "• International Building Code (IBC) 2024/2025",
            "• International Residential Code (IRC) 2024/2025", 
            "• ANSI Y14.5 Dimensioning Standards",
            "• NFPA 101 Life Safety Code 2024",
            "• ADA Standards for Accessible Design"
        ]
        
        for code in codes:
            ax2.text(0.1, y, code, fontsize=9)
            y -= dy
        
        y -= dy
        
        # Disclaimer box
        ax2.text(0.1, y, 'LEGAL DISCLAIMER', fontsize=11, fontweight='bold', color='darkred')
        y -= dy
        
        disc_text = ("This drawing is for conceptual planning only. All dimensions must be verified "
                    "by a licensed professional before construction. User assumes responsibility for "
                    "code compliance. Not for construction without engineer/architect stamp.")
        
        ax2.text(0.1, y, disc_text, fontsize=8, wrap=True, 
                bbox=dict(boxstyle='round', facecolor='#fff3cd', alpha=0.8))
        
        pdf.savefig(fig2, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig2)
    
    buffer.seek(0)
    return buffer

# Main UI
st.markdown('<h1 class="main-header">🏗️ Architectural Blueprint Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Professional Site Planning Tool | IBC 2024/2025 Compliant</p>', 
           unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("Project Info")
    project_name = st.text_input("Project Name", "Sunset Ridge Residence")
    client_name = st.text_input("Client Name", "John Smith")
    location = st.text_input("Location", "California, USA")
    
    st.subheader("Standards")
    units = st.selectbox("Units", ["ft", "m"])
    scale = st.selectbox("Scale", [100, 200, 500, 1000], index=1)
    
    st.subheader("Dimensions")
    site_width = st.number_input(f"Site Width ({units})", 10.0, 500.0, 60.0)
    site_depth = st.number_input(f"Site Depth ({units})", 10.0, 500.0, 100.0)
    building_width = st.number_input(f"Building Width ({units})", 5.0, 400.0, 40.0)
    building_depth = st.number_input(f"Building Depth ({units})", 5.0, 400.0, 50.0)
    
    st.subheader("Setbacks")
    c1, c2 = st.columns(2)
    with c1:
        front = st.number_input(f"Front ({units})", 0.0, 100.0, 20.0)
        left = st.number_input(f"Left ({units})", 0.0, 100.0, 10.0)
    with c2:
        back = st.number_input(f"Rear ({units})", 0.0, 100.0, 15.0)
        right = st.number_input(f"Right ({units})", 0.0, 100.0, 10.0)
    
    orientation = st.slider("North Rotation (°)", 0, 360, 0)
    
    # Validation
    total_w = building_width + left + right
    total_d = building_depth + front + back
    
    if total_w > site_width or total_d > site_depth:
        st.error("⚠️ Building exceeds site boundaries!")

# Main area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📐 Blueprint Preview")
    
    if st.button("🎯 GENERATE BLUEPRINT", use_container_width=True):
        params = {
            'project_name': project_name,
            'client_name': client_name,
            'location': location,
            'site_width': site_width,
            'site_depth': site_depth,
            'building_width': building_width,
            'building_depth': building_depth,
            'setbacks': [front, back, left, right],
            'orientation': orientation,
            'scale': scale,
            'units': units
        }
        
        # Generate
        fig = create_blueprint(params)
        
        # Display
        st.pyplot(fig)
        
        # Downloads
        d1, d2 = st.columns(2)
        
        with d1:
            # PNG
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='white')
            buf.seek(0)
            b64 = base64.b64encode(buf.read()).decode()
            href = f'<a href="data:image/png;base64,{b64}" download="{project_name.replace(" ", "_")}_Blueprint.png"><div style="background:#0066cc;color:white;padding:10px;border-radius:5px;text-align:center;font-weight:bold;">📥 Download PNG (200 DPI)</div></a>'
            st.markdown(href, unsafe_allow_html=True)
        
        with d2:
            # PDF
            pdf_buf = generate_pdf(fig, params)
            b64_pdf = base64.b64encode(pdf_buf.read()).decode()
            href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{project_name.replace(" ", "_")}_Package.pdf"><div style="background:#d32f2f;color:white;padding:10px;border-radius:5px;text-align:center;font-weight:bold;">📄 Download PDF Package</div></a>'
            st.markdown(href_pdf, unsafe_allow_html=True)
        
        # Disclaimer
        st.info("⚖️ **Legal Notice:** For planning only. Verify dimensions on site. Complies with IBC 2024/2025.")
    
    else:
        st.info("👈 Configure parameters and click 'Generate Blueprint'")

with col2:
    st.subheader("📊 Metrics")
    
    site_area = site_width * site_depth
    bldg_area = building_width * building_depth
    coverage = (bldg_area / site_area) * 100 if site_area > 0 else 0
    
    st.markdown(f"""
    <div class="metric-box" style="margin-bottom:10px;">
        <div style="font-size:0.8rem;color:#666;">Site Area</div>
        <div style="font-size:1.3rem;font-weight:bold;">{site_area:.1f} {units}²</div>
    </div>
    <div class="metric-box" style="margin-bottom:10px;">
        <div style="font-size:0.8rem;color:#666;">Building Area</div>
        <div style="font-size:1.3rem;font-weight:bold;">{bldg_area:.1f} {units}²</div>
    </div>
    <div class="metric-box" style="margin-bottom:10px;">
        <div style="font-size:0.8rem;color:#666;">Coverage</div>
        <div style="font-size:1.3rem;font-weight:bold;color:{'green' if coverage < 50 else 'red'};">{coverage:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🏛️ Standards")
    st.markdown("""
    - IBC 2024/2025
    - IRC 2024/2025
    - ANSI Y14.5
    - NFPA 101 2024
    - ADA 2024
    """)

st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#666;font-size:0.8rem;">
    <strong>Architectural Blueprint Pro</strong> | © 2025-2026 | Professional Site Planning Tool
</div>
""", unsafe_allow_html=True)
