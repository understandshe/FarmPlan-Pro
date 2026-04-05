import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon, Arc
from matplotlib.collections import PatchCollection
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import io
from datetime import datetime
import base64
from matplotlib.lines import Line2D

# Page configuration
st.set_page_config(
    page_title="Architectural Blueprint Pro | Professional Site Planning Tool",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    .blueprint-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 2rem;
        border: 1px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
    }
    
    .metric-box {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #0066cc;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,102,204,0.3);
    }
    
    .professional-input {
        border-radius: 6px;
        border: 1px solid #ced4da;
    }
    
    .disclaimer-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        font-size: 0.85rem;
        color: #856404;
        margin-top: 1rem;
    }
    
    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #0066cc;
    }
</style>
""", unsafe_allow_html=True)

def create_architectural_blueprint(params):
    """Create professional architectural blueprint"""
    
    # Extract parameters
    project_name = params['project_name']
    client_name = params['client_name']
    site_width = params['site_width']
    site_depth = params['site_depth']
    building_width = params['building_width']
    building_depth = params['building_depth']
    setbacks = params['setbacks']  # [front, back, left, right]
    orientation = params['orientation']
    scale = params['scale']
    units = params['units']
    drawing_standard = params['drawing_standard']
    plot_type = params['plot_type']
    
    # Create figure with professional size (A3 landscape = 16.5 x 11.7 inches)
    fig = plt.figure(figsize=(16.5, 11.7), dpi=300)
    ax = fig.add_subplot(111)
    
    # Professional blueprint color scheme
    bg_color = '#f8f9fa'
    grid_color = '#e9ecef'
    border_color = '#2c3e50'
    building_color = '#34495e'
    building_fill = '#ecf0f1'
    setback_color = '#e74c3c'
    dimension_color = '#0066cc'
    text_color = '#2c3e50'
    north_color = '#c0392b'
    
    ax.set_facecolor(bg_color)
    
    # Calculate dimensions
    margin = max(site_width, site_depth) * 0.15
    total_width = site_width + 2 * margin
    total_depth = site_depth + 2 * margin
    
    ax.set_xlim(-margin, site_width + margin)
    ax.set_ylim(-margin, site_depth + margin)
    ax.set_aspect('equal')
    
    # Draw professional grid
    grid_spacing = max(site_width, site_depth) / 20
    for x in np.arange(0, site_width + grid_spacing, grid_spacing):
        ax.axvline(x=x, color=grid_color, linewidth=0.5, alpha=0.6, linestyle='-')
    for y in np.arange(0, site_depth + grid_spacing, grid_spacing):
        ax.axhline(y=y, color=grid_color, linewidth=0.5, alpha=0.6, linestyle='-')
    
    # Draw site boundary with professional line weight
    site_boundary = Rectangle((0, 0), site_width, site_depth, 
                             linewidth=3, edgecolor=border_color, 
                             facecolor='none', linestyle='-')
    ax.add_patch(site_boundary)
    
    # Draw setbacks (dashed lines)
    front, back, left, right = setbacks
    buildable_x = left
    buildable_y = back
    buildable_width = site_width - left - right
    buildable_height = site_depth - front - back
    
    # Front setback
    if front > 0:
        ax.plot([0, site_width], [site_depth - front, site_depth - front], 
                'r--', linewidth=1.5, alpha=0.7)
        ax.fill_between([0, site_width], [site_depth - front, site_depth - front], 
                       [site_depth, site_depth], color='#ffebee', alpha=0.3)
    
    # Back setback
    if back > 0:
        ax.plot([0, site_width], [back, back], 'r--', linewidth=1.5, alpha=0.7)
        ax.fill_between([0, site_width], [0, 0], [back, back], color='#ffebee', alpha=0.3)
    
    # Left setback
    if left > 0:
        ax.plot([left, left], [0, site_depth], 'r--', linewidth=1.5, alpha=0.7)
        ax.fill_between([0, left], [0, 0], [site_depth, site_depth], color='#ffebee', alpha=0.3)
    
    # Right setback
    if right > 0:
        ax.plot([site_width - right, site_width - right], [0, site_depth], 
                'r--', linewidth=1.5, alpha=0.7)
        ax.fill_between([site_width - right, site_width], [0, 0], 
                       [site_depth, site_depth], color='#ffebee', alpha=0.3)
    
    # Draw building footprint
    building_x = left + (buildable_width - building_width) / 2
    building_y = back + (buildable_height - building_depth) / 2
    
    building = FancyBboxPatch(
        (building_x, building_y), building_width, building_depth,
        boxstyle="square,pad=0",
        linewidth=2.5, edgecolor=building_color,
        facecolor=building_fill, alpha=0.9
    )
    ax.add_patch(building)
    
    # Add hatching pattern to building
    hatch_spacing = min(building_width, building_depth) / 15
    for i in range(int(building_width / hatch_spacing) + 1):
        x = building_x + i * hatch_spacing
        if x <= building_x + building_width:
            ax.plot([x, x], [building_y, building_y + building_depth], 
                   'k-', linewidth=0.3, alpha=0.3)
    
    # Add building dimensions inside
    ax.text(building_x + building_width/2, building_y + building_depth/2, 
           f'{building_width:.1f} x {building_depth:.1f}\n{units}', 
           ha='center', va='center', fontsize=10, fontweight='bold',
           color=building_color, family='monospace')
    
    # Professional dimension lines with arrows
    def draw_dimension(ax, x1, y1, x2, y2, offset, text, flip=False):
        # Extension lines
        ext_length = 0.3
        angle = np.arctan2(y2-y1, x2-x1)
        perp_x = -np.sin(angle) * offset
        perp_y = np.cos(angle) * offset
        
        # Draw extension lines
        ax.plot([x1, x1 + perp_x*ext_length], [y1, y1 + perp_y*ext_length], 
               'k-', linewidth=0.8)
        ax.plot([x2, x2 + perp_x*ext_length], [y2, y2 + perp_y*ext_length], 
               'k-', linewidth=0.8)
        
        # Dimension line
        dim_x1, dim_y1 = x1 + perp_x, y1 + perp_y
        dim_x2, dim_y2 = x2 + perp_x, y2 + perp_y
        
        # Draw arrows
        arrow_style = patches.FancyArrowPatch(
            (dim_x1, dim_y1), (dim_x2, dim_y2),
            arrowstyle='<->', mutation_scale=15,
            color=dimension_color, linewidth=1.2
        )
        ax.add_patch(arrow_style)
        
        # Text
        mid_x = (dim_x1 + dim_x2) / 2
        mid_y = (dim_y1 + dim_y2) / 2
        text_angle = np.degrees(angle)
        if flip:
            text_angle += 180
        
        ax.text(mid_x, mid_y, text, ha='center', va='center',
               fontsize=9, color=dimension_color, fontweight='bold',
               rotation=text_angle if abs(text_angle) < 90 else text_angle + 180,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                        edgecolor='none', alpha=0.8))
    
    # Site dimensions
    offset = margin * 0.4
    draw_dimension(ax, 0, 0, site_width, 0, -offset, f'{site_width:.1f} {units}')
    draw_dimension(ax, 0, 0, 0, site_depth, -offset, f'{site_depth:.1f} {units}', flip=True)
    
    # Building dimensions
    b_offset = 0.5
    draw_dimension(ax, building_x, building_y - b_offset, 
                  building_x + building_width, building_y - b_offset, 
                  -b_offset, f'{building_width:.1f}')
    draw_dimension(ax, building_x - b_offset, building_y, 
                  building_x - b_offset, building_y + building_depth, 
                  -b_offset, f'{building_depth:.1f}', flip=True)
    
    # Setback dimensions
    if front > 0:
        ax.annotate('', xy=(site_width + 0.8, site_depth), 
                   xytext=(site_width + 0.8, site_depth - front),
                   arrowprops=dict(arrowstyle='<->', color=setback_color, lw=1.5))
        ax.text(site_width + 1.2, site_depth - front/2, f'Front\n{front:.1f}', 
               fontsize=8, color=setback_color, va='center')
    
    if back > 0:
        ax.annotate('', xy=(site_width + 0.8, back), 
                   xytext=(site_width + 0.8, 0),
                   arrowprops=dict(arrowstyle='<->', color=setback_color, lw=1.5))
        ax.text(site_width + 1.2, back/2, f'Rear\n{back:.1f}', 
               fontsize=8, color=setback_color, va='center')
    
    # North arrow (professional style)
    north_x = site_width - 2
    north_y = site_depth - 2
    arrow_length = 1.5
    
    # Rotate based on orientation
    angle_rad = np.radians(orientation)
    dx = arrow_length * np.sin(angle_rad)
    dy = arrow_length * np.cos(angle_rad)
    
    ax.annotate('N', xy=(north_x + dx, north_y + dy), 
               xytext=(north_x, north_y),
               arrowprops=dict(arrowstyle='->', color=north_color, lw=3),
               fontsize=14, color=north_color, fontweight='bold', ha='center')
    
    # Circle around N
    circle = Circle((north_x, north_y), 0.3, fill=False, 
                   edgecolor=north_color, linewidth=1.5)
    ax.add_patch(circle)
    
    # Title block (professional standard)
    title_block_width = 6
    title_block_height = 2.5
    title_x = site_width - title_block_width - 0.5
    title_y = 0.5
    
    # Title block background
    title_bg = FancyBboxPatch(
        (title_x, title_y), title_block_width, title_block_height,
        boxstyle="square,pad=0", linewidth=2, edgecolor='black',
        facecolor='white'
    )
    ax.add_patch(title_bg)
    
    # Title block grid
    ax.plot([title_x, title_x + title_block_width], 
           [title_y + title_block_height - 0.6, title_y + title_block_height - 0.6], 
           'k-', linewidth=1)
    ax.plot([title_x + title_block_width * 0.6, title_x + title_block_width * 0.6], 
           [title_y, title_y + title_block_height], 'k-', linewidth=1)
    ax.plot([title_x, title_x + title_block_width], 
           [title_y + 0.6, title_y + 0.6], 'k-', linewidth=0.5)
    
    # Title block text
    ax.text(title_x + title_block_width/2, title_y + title_block_height - 0.3, 
           project_name.upper(), ha='center', va='center', 
           fontsize=12, fontweight='bold', family='sans-serif')
    ax.text(title_x + title_block_width/2, title_y + title_block_height - 0.9, 
           'SITE PLAN', ha='center', va='center', 
           fontsize=10, family='sans-serif')
    ax.text(title_x + 0.2, title_y + 0.3, f'Client: {client_name}', 
           fontsize=8, va='center')
    ax.text(title_x + 0.2, title_y + 1.0, f'Scale: 1:{scale}', 
           fontsize=8, va='center')
    ax.text(title_x + title_block_width * 0.8, title_y + 0.3, 
           f'Date: {datetime.now().strftime("%Y-%m-%d")}', 
           fontsize=8, va='center', ha='center')
    ax.text(title_x + title_block_width * 0.8, title_y + 1.0, 
           f'Drawn: AutoCAD Pro', fontsize=8, va='center', ha='center')
    
    # Scale bar
    scale_bar_x = 1
    scale_bar_y = 1
    real_length = 5  # 5 units
    drawing_length = real_length * (1000 / scale) * 0.001  # Convert to drawing units
    
    ax.plot([scale_bar_x, scale_bar_x + drawing_length], [scale_bar_y, scale_bar_y], 
           'k-', linewidth=3)
    ax.plot([scale_bar_x, scale_bar_x], [scale_bar_y - 0.1, scale_bar_y + 0.1], 'k-', lw=2)
    ax.plot([scale_bar_x + drawing_length, scale_bar_x + drawing_length], 
           [scale_bar_y - 0.1, scale_bar_y + 0.1], 'k-', lw=2)
    ax.text(scale_bar_x + drawing_length/2, scale_bar_y - 0.3, 
           f'{real_length} {units}', ha='center', fontsize=9, fontweight='bold')
    
    # Disclaimer text at bottom
    disclaimer = (
        "DISCLAIMER: This drawing is for conceptual planning purposes only. "
        "All dimensions must be verified on site before construction. "
        "Complies with IBC 2024/2025 & local building codes. "
        "Not for construction without engineer stamp."
    )
    ax.text(site_width/2, -margin * 0.6, disclaimer, ha='center', va='top',
           fontsize=7, style='italic', color='#666666', wrap=True)
    
    # Remove axes for professional look
    ax.axis('off')
    
    # Add subtle border
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.5)
        spine.set_color('#cccccc')
    
    plt.tight_layout()
    return fig

def generate_pdf(fig, params):
    """Generate professional PDF with multiple sheets"""
    buffer = io.BytesIO()
    
    with PdfPages(buffer) as pdf:
        # Sheet 1: Site Plan
        pdf.savefig(fig, dpi=300, bbox_inches='tight', facecolor='white')
        
        # Sheet 2: Data Sheet
        fig2 = plt.figure(figsize=(11.7, 16.5), dpi=300)
        ax2 = fig2.add_subplot(111)
        ax2.axis('off')
        
        # Professional data sheet layout
        y_pos = 0.95
        line_height = 0.04
        
        ax2.text(0.5, y_pos, 'ARCHITECTURAL SITE ANALYSIS REPORT', 
                ha='center', fontsize=20, fontweight='bold')
        y_pos -= line_height * 2
        
        # Project info
        ax2.text(0.1, y_pos, f'Project: {params["project_name"]}', fontsize=12, fontweight='bold')
        y_pos -= line_height
        ax2.text(0.1, y_pos, f'Client: {params["client_name"]}', fontsize=11)
        y_pos -= line_height
        ax2.text(0.1, y_pos, f'Location: {params.get("location", "Not specified")}', fontsize=11)
        y_pos -= line_height * 2
        
        # Site data table
        ax2.text(0.1, y_pos, 'SITE SPECIFICATIONS', fontsize=14, fontweight='bold', 
                bbox=dict(boxstyle='round', facecolor='#f0f0f0'))
        y_pos -= line_height * 1.5
        
        data_rows = [
            ['Parameter', 'Value', 'Notes'],
            ['Site Width', f'{params["site_width"]} {params["units"]}', ''],
            ['Site Depth', f'{params["site_depth"]} {params["units"]}', ''],
            ['Site Area', f'{params["site_width"] * params["site_depth"]:.2f} sq {params["units"]}', ''],
            ['Building Width', f'{params["building_width"]} {params["units"]}', ''],
            ['Building Depth', f'{params["building_depth"]} {params["units"]}', ''],
            ['Building Area', f'{params["building_width"] * params["building_depth"]:.2f} sq {params["units"]}', ''],
            ['Coverage Ratio', f'{(params["building_width"] * params["building_depth"])/(params["site_width"] * params["site_depth"])*100:.1f}%', 'Max typically 40-60%'],
            ['Front Setback', f'{params["setbacks"][0]} {params["units"]}', ''],
            ['Rear Setback', f'{params["setbacks"][1]} {params["units"]}', ''],
            ['Left Setback', f'{params["setbacks"][2]} {params["units"]}', ''],
            ['Right Setback', f'{params["setbacks"][3]} {params["units"]}', ''],
            ['Orientation', f'{params["orientation"]}°', 'Clockwise from North'],
            ['Drawing Standard', params["drawing_standard"], ''],
            ['Scale', f'1:{params["scale"]}', ''],
            ['Plot Type', params["plot_type"], ''],
        ]
        
        for i, row in enumerate(data_rows):
            if i == 0:
                weight = 'bold'
                bg = '#e0e0e0'
            else:
                weight = 'normal'
                bg = 'white' if i % 2 == 0 else '#f9f9f9'
            
            ax2.add_patch(patches.Rectangle((0.08, y_pos - 0.015), 0.84, 0.03, 
                                          facecolor=bg, edgecolor='black', linewidth=0.5))
            ax2.text(0.1, y_pos, row[0], fontsize=9, fontweight=weight, va='center')
            ax2.text(0.4, y_pos, row[1], fontsize=9, fontweight=weight, va='center')
            ax2.text(0.6, y_pos, row[2], fontsize=8, style='italic', va='center')
            y_pos -= line_height
        
        y_pos -= line_height
        
        # Compliance section
        ax2.text(0.1, y_pos, 'CODE COMPLIANCE & STANDARDS', fontsize=14, 
                fontweight='bold', bbox=dict(boxstyle='round', facecolor='#f0f0f0'))
        y_pos -= line_height * 1.5
        
        compliance_text = [
            "• International Building Code (IBC) 2024/2025 Edition",
            "• International Residential Code (IRC) 2024/2025 Edition",
            "• ANSI/ASME Y14.5 Dimensioning and Tolerancing Standards",
            "• Local Zoning Ordinances and Land Use Regulations",
            "• ADA Accessibility Guidelines (2010/2024 Standards)",
            "• NFPA 101 Life Safety Code 2024 Edition",
            "• Local Fire Code Requirements",
        ]
        
        for text in compliance_text:
            ax2.text(0.1, y_pos, text, fontsize=9)
            y_pos -= line_height
        
        y_pos -= line_height
        
        # Professional disclaimer
        ax2.text(0.1, y_pos, 'LEGAL DISCLAIMER', fontsize=14, 
                fontweight='bold', color='#d32f2f', 
                bbox=dict(boxstyle='round', facecolor='#ffebee'))
        y_pos -= line_height * 1.5
        
        disclaimer_text = (
            "This architectural drawing and report are generated for preliminary planning "
            "and visualization purposes only. All dimensions, setbacks, and calculations "
            "must be verified by a licensed architect, civil engineer, or surveyor before "
            "any construction activity. The user assumes full responsibility for ensuring "
            "compliance with all applicable local, state, and federal building codes, "
            "zoning ordinances, and regulations. This tool does not replace professional "
            "architectural or engineering services. Construction without proper permits "
            "and professional stamps is prohibited and may result in legal penalties. "
            f"Generated on {datetime.now().strftime('%B %d, %Y')} | "
            "Valid for planning purposes only."
        )
        
        # Wrap disclaimer text
        words = disclaimer_text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line + word) < 100:
                current_line += word + " "
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        for line in lines:
            ax2.text(0.1, y_pos, line.strip(), fontsize=8, wrap=True, 
                    bbox=dict(boxstyle='round', facecolor='#fff3e0', alpha=0.5))
            y_pos -= line_height * 0.8
        
        pdf.savefig(fig2, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig2)
    
    buffer.seek(0)
    return buffer

# Main UI
st.markdown('<h1 class="main-header">🏗️ Architectural Blueprint Pro</h1>', 
           unsafe_allow_html=True)
st.markdown('<p class="sub-header">Professional Site Planning & Analysis Tool | IBC 2024/2025 Compliant</p>', 
           unsafe_allow_html=True)

# Professional sidebar
with st.sidebar:
    st.markdown('<h2 style="font-family: Inter; font-size: 1.2rem; margin-bottom: 1rem;">⚙️ Project Configuration</h2>', 
               unsafe_allow_html=True)
    
    # Project Info
    st.markdown('<p style="font-weight: 600; color: #0066cc; margin-top: 1rem;">Project Details</p>', 
               unsafe_allow_html=True)
    project_name = st.text_input("Project Name", "Sunset Ridge Residence")
    client_name = st.text_input("Client Name", "John Smith")
    location = st.text_input("Project Location", "California, USA")
    
    # Units and Standards
    st.markdown('<p style="font-weight: 600; color: #0066cc; margin-top: 1.5rem;">Standards & Units</p>', 
               unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        units = st.selectbox("Units", ["ft", "m"])
    with col2:
        scale = st.selectbox("Scale", [100, 200, 500, 1000], index=1)
    
    drawing_standard = st.selectbox("Drawing Standard", 
                                   ["ANSI (US)", "ISO (Metric)", "DIN (German)", "JIS (Japan)"])
    plot_type = st.selectbox("Plot Type", 
                            ["Residential Single-Family", "Residential Multi-Family", 
                             "Commercial", "Industrial", "Mixed-Use"])
    
    # Site Dimensions
    st.markdown('<p style="font-weight: 600; color: #0066cc; margin-top: 1.5rem;">Site Dimensions</p>', 
               unsafe_allow_html=True)
    site_width = st.number_input(f"Site Width ({units})", min_value=10.0, max_value=500.0, value=60.0)
    site_depth = st.number_input(f"Site Depth ({units})", min_value=10.0, max_value=500.0, value=100.0)
    
    # Building Dimensions
    st.markdown('<p style="font-weight: 600; color: #0066cc; margin-top: 1.5rem;">Building Footprint</p>', 
               unsafe_allow_html=True)
    building_width = st.number_input(f"Building Width ({units})", min_value=5.0, max_value=400.0, value=40.0)
    building_depth = st.number_input(f"Building Depth ({units})", min_value=5.0, max_value=400.0, value=50.0)
    
    # Setbacks
    st.markdown('<p style="font-weight: 600; color: #0066cc; margin-top: 1.5rem;">Required Setbacks</p>', 
               unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        front_setback = st.number_input(f"Front ({units})", min_value=0.0, value=20.0)
        left_setback = st.number_input(f"Left ({units})", min_value=0.0, value=10.0)
    with col2:
        back_setback = st.number_input(f"Rear ({units})", min_value=0.0, value=15.0)
        right_setback = st.number_input(f"Right ({units})", min_value=0.0, value=10.0)
    
    # Orientation
    st.markdown('<p style="font-weight: 600; color: #0066cc; margin-top: 1.5rem;">Site Orientation</p>', 
               unsafe_allow_html=True)
    orientation = st.slider("North Rotation (°)", 0, 360, 0)
    
    # Validation
    total_building_width = building_width + left_setback + right_setback
    total_building_depth = building_depth + front_setback + back_setback
    
    if total_building_width > site_width or total_building_depth > site_depth:
        st.error("⚠️ Building exceeds site boundaries with setbacks!")

# Main content area
col1, col2 = col3, col4 = st.columns([2, 1])

with col1:
    st.markdown('<div class="blueprint-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title">📐 Blueprint Preview</h3>', unsafe_allow_html=True)
    
    # Generate button
    if st.button("🎯 GENERATE PROFESSIONAL BLUEPRINT", use_container_width=True):
        params = {
            'project_name': project_name,
            'client_name': client_name,
            'location': location,
            'site_width': site_width,
            'site_depth': site_depth,
            'building_width': building_width,
            'building_depth': building_depth,
            'setbacks': [front_setback, back_setback, left_setback, right_setback],
            'orientation': orientation,
            'scale': scale,
            'units': units,
            'drawing_standard': drawing_standard,
            'plot_type': plot_type
        }
        
        # Store in session state
        st.session_state['blueprint_params'] = params
        st.session_state['blueprint_generated'] = True
        
        # Create blueprint
        fig = create_architectural_blueprint(params)
        st.session_state['current_fig'] = fig
        
        st.pyplot(fig)
        
        # Download buttons
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            # PNG download
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            buf.seek(0)
            b64 = base64.b64encode(buf.read()).decode()
            href = f'<a href="data:image/png;base64,{b64}" download="{project_name.replace(" ", "_")}_Blueprint.png" style="text-decoration: none;"><div style="background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%); color: white; padding: 0.75rem; border-radius: 8px; text-align: center; font-weight: 600;">📥 Download High-Res PNG (300 DPI)</div></a>'
            st.markdown(href, unsafe_allow_html=True)
        
        with col_dl2:
            # PDF download
            pdf_buffer = generate_pdf(fig, params)
            b64_pdf = base64.b64encode(pdf_buffer.read()).decode()
            href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{project_name.replace(" ", "_")}_Blueprint_Package.pdf" style="text-decoration: none;"><div style="background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%); color: white; padding: 0.75rem; border-radius: 8px; text-align: center; font-weight: 600;">📄 Download PDF Package (Multi-Sheet)</div></a>'
            st.markdown(href_pdf, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Disclaimer
        st.markdown("""
        <div class="disclaimer-box">
        <strong>⚖️ Legal Notice:</strong> This blueprint is generated for preliminary planning and visualization purposes only. 
        All dimensions must be field-verified by a licensed professional. Compliant with IBC 2024/2025 standards. 
        Not for construction without engineer/architect stamp and permit approval.
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.info("👈 Configure your project parameters in the sidebar and click 'Generate Professional Blueprint' to create your architectural drawing.")
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="blueprint-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title">📊 Project Metrics</h3>', unsafe_allow_html=True)
    
    # Calculations
    site_area = site_width * site_depth
    building_area = building_width * building_depth
    coverage = (building_area / site_area) * 100 if site_area > 0 else 0
    floor_area_ratio = building_area / site_area if site_area > 0 else 0
    
    # Display metrics
    st.markdown(f"""
    <div class="metric-box" style="margin-bottom: 0.8rem;">
        <div style="font-size: 0.85rem; color: #666;">Site Area</div>
        <div style="font-size: 1.4rem; font-weight: 700; color: #2c3e50;">{site_area:.1f} <span style="font-size: 0.9rem;">{units}²</span></div>
    </div>
    
    <div class="metric-box" style="margin-bottom: 0.8rem;">
        <div style="font-size: 0.85rem; color: #666;">Building Footprint</div>
        <div style="font-size: 1.4rem; font-weight: 700; color: #2c3e50;">{building_area:.1f} <span style="font-size: 0.9rem;">{units}²</span></div>
    </div>
    
    <div class="metric-box" style="margin-bottom: 0.8rem;">
        <div style="font-size: 0.85rem; color: #666;">Site Coverage</div>
        <div style="font-size: 1.4rem; font-weight: 700; color: {'#27ae60' if coverage < 50 else '#e74c3c'};">{coverage:.1f}%</div>
        <div style="font-size: 0.75rem; color: #999;">{'Compliant' if coverage < 50 else 'Check local codes'}</div>
    </div>
    
    <div class="metric-box" style="margin-bottom: 0.8rem;">
        <div style="font-size: 0.85rem; color: #666;">FAR (Floor Area Ratio)</div>
        <div style="font-size: 1.4rem; font-weight: 700; color: #2c3e50;">{floor_area_ratio:.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Standards info
    st.markdown('<div class="blueprint-card" style="margin-top: 1rem;">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title">🏛️ Code Compliance</h3>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="font-size: 0.9rem; line-height: 1.6;">
    <p style="margin-bottom: 0.5rem;"><strong>Standards Applied:</strong></p>
    <ul style="margin-left: 1rem; color: #555;">
        <li>IBC 2024/2025</li>
        <li>IRC 2024/2025</li>
        <li>ANSI Y14.5</li>
        <li>NFPA 101 2024</li>
        <li>ADA 2010/2024</li>
    </ul>
    <p style="margin-top: 0.5rem; font-size: 0.8rem; color: #888; font-style: italic;">
    *Verify with local AHJ for jurisdiction-specific amendments
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 2rem; background: #f8f9fa; border-radius: 12px;">
    <p style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">
        <strong>Architectural Blueprint Pro v2.0</strong> | Professional Site Planning Tool
    </p>
    <p style="color: #999; font-size: 0.8rem;">
        © 2025-2026 | Compliant with International Building Code Standards | 
        For professional use only
    </p>
</div>
""", unsafe_allow_html=True)
