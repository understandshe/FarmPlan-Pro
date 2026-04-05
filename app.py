# इस code को अपनी app.py में replace करें
# केवल draw_layout_map() function को replace करना है

def draw_layout_map(layout_data: dict) -> bytes:
    """
    PREMIUM ARCHITECTURAL-STYLE Farm Layout Map
    With dimensions, equipment icons, utilities, and professional annotations
    """
    zones = layout_data["zones"]
    farm_type = layout_data["farm_type"]
    country = layout_data["country"]
    acres = layout_data["land_acres"]
    
    # Premium figure setup with higher DPI
    fig = plt.figure(figsize=(16, 11), facecolor="#FAFAFA")
    gs = fig.add_gridspec(3, 1, height_ratios=[0.8, 12, 1], hspace=0.02)
    
    # Title Section - Professional
    ax_title = fig.add_subplot(gs[0])
    ax_title.axis('off')
    ax_title.text(0.5, 0.5, 
                  f"PROFESSIONAL FARM LAYOUT PLAN",
                  ha='center', va='center', 
                  fontsize=20, fontweight='bold', 
                  color="#1A252F")
    ax_title.text(0.5, 0.2,
                  f"{acres} Acre {farm_type} | {country} | {layout_data['budget']} Budget | Generated: {layout_data['generated_at']}",
                  ha='center', va='center',
                  fontsize=9, color="#555555")
    
    # Main Map Area
    ax = fig.add_subplot(gs[1])
    ax.set_facecolor("#FFFFFF")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # === PROFESSIONAL BORDER (Double Line) ===
    ax.add_patch(mpatches.FancyBboxPatch((1, 1), 98, 98,
        boxstyle="round,pad=0.5", linewidth=3, edgecolor="#2C3E50", 
        facecolor="none", zorder=10))
    ax.add_patch(mpatches.FancyBboxPatch((2, 2), 96, 96,
        boxstyle="round,pad=0.3", linewidth=1, edgecolor="#95A5A6", 
        facecolor="none", zorder=10))
    
    # === GRID LINES (Engineering Style) ===
    for i in range(0, 101, 10):
        ax.axhline(i, color="#ECF0F1", linewidth=0.5, zorder=0)
        ax.axvline(i, color="#ECF0F1", linewidth=0.5, zorder=0)
    
    # === ZONE PLACEMENT ===
    LEFT_X, LEFT_W = 3, 55
    RIGHT_X, RIGHT_W = 60, 37
    TOP_Y = 94
    BOTTOM_Y = 4
    GAP = 2
    
    # Separate zones
    production_keywords = ["Milch", "Dry Cow", "Heifer", "Calf", "Goat", "Poultry", "Veggie"]
    support_keywords = ["Storage", "Office", "Compost", "Equipment", "Fodder", "Isolation"]
    
    production_zones = [z for z in zones if any(k in z['name'] for k in production_keywords)]
    support_zones = [z for z in zones if any(k in z['name'] for k in support_keywords)]
    other_zones = [z for z in zones if z not in production_zones and z not in support_zones]
    
    def draw_premium_zone(zone, x, y, width, height):
        """Draw zone with dimensions, equipment icons, and annotations"""
        color = ZONE_COLORS.get(zone['name'], "#D5D8DC")
        
        # Shadow effect for depth
        ax.add_patch(mpatches.FancyBboxPatch((x+0.5, y-0.5-height), width, height,
            boxstyle="round,pad=0.4", linewidth=0, facecolor="#000000", alpha=0.08, zorder=1))
        
        # Main zone rectangle
        rect = mpatches.FancyBboxPatch((x, y-height), width, height,
            boxstyle="round,pad=0.4", linewidth=2, edgecolor="#2C3E50",
            facecolor=color, zorder=2)
        ax.add_patch(rect)
        
        # Calculate actual dimensions (assuming square plot)
        land_sqm = layout_data['total_sqm']
        side_m = math.sqrt(land_sqm)
        zone_sqm = zone['sqm']
        zone_side_m = math.sqrt(zone_sqm)
        
        # Zone label with background
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
        
        # Label background box
        label_y = y - height/2
        ax.add_patch(mpatches.FancyBboxPatch((x+width*0.1, label_y-2), width*0.8, 4,
            boxstyle="round,pad=0.3", linewidth=0, facecolor="#FFFFFF", alpha=0.95, zorder=3))
        
        # Zone name
        ax.text(x + width/2, label_y, label, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color="#1A252F", zorder=4)
        
        # Area and dimensions
        ax.text(x + width/2, y - height + 1.8, 
                f"{zone['sqm']:,.0f} m²  |  ~{zone_side_m:.1f}m × {zone_side_m:.1f}m",
                ha='center', va='center', fontsize=6, color="#555555", style='italic', zorder=4)
        
        # Capacity if applicable
        cap = layout_data['capacities'].get(zone['name'])
        if cap:
            ax.text(x + width/2, y - height + 3.8,
                    f"📍 Capacity: ~{cap} animals",
                    ha='center', va='center', fontsize=6, color="#2E86C1",
                    fontweight='bold', zorder=4)
        
        # Add equipment icons based on zone type
        icon_y = y - height/2 - 3
        if "Milch Cow" in zone['name']:
            ax.text(x + width*0.15, icon_y, "🐄", fontsize=10, zorder=4)
            ax.text(x + width*0.85, icon_y, "💧", fontsize=8, zorder=4)  # Water
        elif "Dry Cow" in zone['name']:
            ax.text(x + width*0.15, icon_y, "🐄", fontsize=10, zorder=4)
        elif "Calf" in zone['name']:
            ax.text(x + width*0.15, icon_y, "🐮", fontsize=9, zorder=4)
        elif "Milking" in zone['name']:
            ax.text(x + width*0.5, icon_y, "🥛", fontsize=10, zorder=4)
        elif "Fodder" in zone['name']:
            ax.text(x + width*0.2, icon_y, "🌾", fontsize=10, zorder=4)
            ax.text(x + width*0.7, icon_y, "📦", fontsize=9, zorder=4)
        elif "Storage" in zone['name']:
            ax.text(x + width*0.5, icon_y, "🏚️", fontsize=11, zorder=4)
        elif "Office" in zone['name']:
            ax.text(x + width*0.5, icon_y, "🏢", fontsize=10, zorder=4)
        elif "Isolation" in zone['name']:
            ax.text(x + width*0.5, icon_y, "⚠️", fontsize=10, zorder=4)
        elif "Open Yard" in zone['name']:
            ax.text(x + width*0.3, icon_y, "🌳", fontsize=9, zorder=4)
            ax.text(x + width*0.7, icon_y, "🌳", fontsize=9, zorder=4)
    
    # Draw columns
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
    
    # === SERVICE LANE with markings ===
    ax.add_patch(mpatches.FancyBboxPatch((LEFT_X + LEFT_W + 0.5, BOTTOM_Y),
        RIGHT_X - (LEFT_X + LEFT_W) - 1, TOP_Y - BOTTOM_Y,
        boxstyle="square,pad=0", linewidth=0, facecolor="#EBF5FB", alpha=0.7, zorder=1))
    
    # Dashed center line
    for y in range(8, 92, 8):
        ax.plot([LEFT_X + LEFT_W + 29, LEFT_X + LEFT_W + 29], 
                [y, y+4], '--', color="#3498DB", linewidth=2, alpha=0.7, zorder=5)
    
    ax.text(LEFT_X + LEFT_W + 29, (TOP_Y + BOTTOM_Y)/2,
            "MAIN SERVICE LANE\n(6m wide)",
            ha='center', va='center', fontsize=7, color="#2E86C1",
            fontweight='bold', rotation=90, zorder=5)
    
    # === FLOW ARROWS (Direction indicators) ===
    for ay_pos in [82, 62, 42, 22]:
        ax.annotate("", xy=(LEFT_X + LEFT_W - 1, ay_pos - 5),
                    xytext=(LEFT_X + LEFT_W - 1, ay_pos),
                    arrowprops=dict(arrowstyle="->", color="#E74C3C", 
                                   lw=2.5, shrinkA=0, shrinkB=0),
                    zorder=5)
    
    # === NORTH ARROW (Professional Compass) ===
    cx, cy, r = 95, 92, 4
    # Outer circle
    ax.add_patch(mpatches.Circle((cx, cy), r, fill=False, 
                                  edgecolor="#2C3E50", linewidth=2, zorder=6))
    # Inner circle
    ax.add_patch(mpatches.Circle((cx, cy), r*0.6, fill=False, 
                                  edgecolor="#95A5A6", linewidth=1, zorder=6))
    # N arrow
    ax.annotate("", xy=(cx, cy+r-0.5), xytext=(cx, cy),
                arrowprops=dict(arrowstyle="->", color="#E74C3C", 
                               lw=3, shrinkA=0, shrinkB=0), zorder=6)
    ax.text(cx, cy+r+1, "N", ha='center', va='center',
            fontsize=10, fontweight='bold', color="#E74C3C", zorder=6)
    # S
    ax.text(cx, cy-r-1, "S", ha='center', va='center',
            fontsize=7, color="#7F8C8D", zorder=6)
    
    # === SCALE BAR with measurements ===
    land_sqm = layout_data['total_sqm']
    side_m = math.sqrt(land_sqm)
    scale_width = 20  # units on map
    
    # Scale bar background
    ax.add_patch(mpatches.FancyBboxPatch((3, 0.8), 35, 3.5,
        boxstyle="round,pad=0.2", linewidth=0, facecolor="#FFFFFF", alpha=0.95, zorder=7))
    
    # Scale bar line
    ax.plot([4, 34], [2.5, 2.5], '-', color="#2C3E50", linewidth=2.5, zorder=7)
    ax.plot([4, 4], [2, 3], '-', color="#2C3E50", linewidth=1.5, zorder=7)
    ax.plot([34, 34], [2, 3], '-', color="#2C3E50", linewidth=1.5, zorder=7)
    ax.plot([19, 19], [2.2, 2.8], '-', color="#2C3E50", linewidth=1, zorder=7)
    
    actual_m = (scale_width / 100) * side_m
    ax.text(19, 1.2, f"Scale: {scale_width} units = {actual_m:.0f}m",
            ha='center', va='center', fontsize=7, color="#555555", 
            fontweight='bold', zorder=7)
    ax.text(19, 0.5, f"Total Plot: ~{side_m:.1f}m × {side_m:.1f}m",
            ha='center', va='center', fontsize=6.5, color="#7F8C8D", zorder=7)
    
    # === LEGEND ===
    legend_patches = []
    for z in zones:
        color = ZONE_COLORS.get(z['name'], "#D5D8DC")
        patch = mpatches.Patch(facecolor=color, edgecolor="#2C3E50", 
                              linewidth=0.8, label=z['name'])
        legend_patches.append(patch)
    
    ax.legend(handles=legend_patches, loc='lower center',
              bbox_to_anchor=(0.5, -0.18), ncol=5, fontsize=6,
              framealpha=0.95, edgecolor="#BDC3C7",
              title="📋 ZONE LEGEND", title_fontsize=7.5,
              handletextpad=0.5, borderpad=0.8)
    
    # === INFO BOX (Bottom Right) ===
    info_text = (f"📊 Total Area: {layout_data['total_sqm']:,.0f} m²\n"
                 f"             {layout_data['total_sqft']:,.0f} sq ft\n"
                 f"📍 Land Size: {layout_data['land_acres']:.2f} acres\n"
                 f"🕐 Generated: {layout_data['generated_at']}")
    
    ax.add_patch(mpatches.FancyBboxPatch((65, 0.8), 33, 5,
        boxstyle="round,pad=0.4", linewidth=1.5, edgecolor="#95A5A6",
        facecolor="#FFFFFF", alpha=0.95, zorder=8))
    ax.text(81.5, 3.3, info_text, ha='center', va='center',
            fontsize=6.5, color="#555555", zorder=8, family='monospace',
            linespacing=1.5)
    
    # === WATERMARK/BRANDING ===
    ax.text(50, -1.5,
            "PREMIUM FARM PLANNING SERVICES | Professional Architectural Layout",
            ha='center', va='center', fontsize=8, color="#95A5A6",
            alpha=0.7, zorder=9, fontweight='bold')
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.97])
    
    # Save with HIGH DPI (300 for print quality)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()
