def draw_layout_map(layout_data: dict) -> bytes:
    """
    Premium architectural-style farm layout map
    """
    zones = layout_data["zones"]
    farm_type = layout_data["farm_type"]
    country = layout_data["country"]
    acres = layout_data["land_acres"]
    
    # --- Premium Figure Setup ---
    fig = plt.figure(figsize=(16, 11), facecolor="#FAFAFA")
    gs = fig.add_gridspec(3, 1, height_ratios=[0.8, 12, 0.8], hspace=0.02)
    
    # Title Section
    ax_title = fig.add_subplot(gs[0])
    ax_title.axis('off')
    ax_title.text(0.5, 0.5, 
                  f"PROFESSIONAL FARM LAYOUT PLAN",
                  ha='center', va='center', 
                  fontsize=18, fontweight='bold', 
                  color="#1A252F", letter_spacing=2)
    ax_title.text(0.5, 0.2,
                  f"{acres} Acre {farm_type} | {country} | {layout_data['budget']} Budget",
                  ha='center', va='center',
                  fontsize=10, color="#555555")
    
    # Main Map Area
    ax = fig.add_subplot(gs[1])
    ax.set_facecolor("#FFFFFF")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # --- Professional Border with Double Line ---
    # Outer border
    ax.add_patch(mpatches.FancyBboxPatch(
        (1, 1), 98, 98,
        boxstyle="round,pad=0.5",
        linewidth=3, edgecolor="#2C3E50", 
        facecolor="none", zorder=10
    ))
    # Inner border
    ax.add_patch(mpatches.FancyBboxPatch(
        (2, 2), 96, 96,
        boxstyle="round,pad=0.3",
        linewidth=1, edgecolor="#95A5A6", 
        facecolor="none", zorder=10
    ))
    
    # --- Grid Lines (Professional Touch) ---
    for i in range(0, 101, 10):
        ax.axhline(i, color="#ECF0F1", linewidth=0.5, zorder=0)
        ax.axvline(i, color="#ECF0F1", linewidth=0.5, zorder=0)
    
    # --- Calculate Zone Placement (Intelligent Grid) ---
    LEFT_X, LEFT_W = 3, 55
    RIGHT_X, RIGHT_W = 60, 37
    TOP_Y = 96
    BOTTOM_Y = 3
    GAP = 2
    
    # Separate zones by function
    production_keywords = ["Milch", "Dry Cow", "Heifer", "Calf", "Goat", "Poultry", "Veggie"]
    support_keywords = ["Storage", "Office", "Compost", "Equipment", "Fodder", "Isolation"]
    
    production_zones = [z for z in zones if any(k in z['name'] for k in production_keywords)]
    support_zones = [z for z in zones if any(k in z['name'] for k in support_keywords)]
    other_zones = [z for z in zones if z not in production_zones and z not in support_zones]
    
    # --- Draw Zones with Professional Styling ---
    def draw_premium_zone(zone, x, y, width, height, is_main=True):
        """Draw a zone with professional styling"""
        color = ZONE_COLORS.get(zone['name'], "#D5D8DC")
        
        # Main zone rectangle with shadow effect
        if __name__ == "__main__":
    main()
            # Shadow
            ax.add_patch(mpatches.FancyBboxPatch(
                (x+0.5, y-0.5-height), width, height,
                boxstyle="round,pad=0.4",
                linewidth=0, facecolor="#000000", alpha=0.1, zorder=1
            ))
        
        # Main rectangle
        rect = mpatches.FancyBboxPatch(
            (x, y-height), width, height,
            boxstyle="round,pad=0.4",
            linewidth=2, edgecolor="#2C3E50",
            facecolor=color, zorder=2
        )
        ax.add_patch(rect)
        
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
        
        # Label background
        label_y = y - height/2
        ax.add_patch(mpatches.FancyBboxPatch(
            (x+width*0.1, label_y-2), width*0.8, 4,
            boxstyle="round,pad=0.3",
            linewidth=0, facecolor="#FFFFFF", alpha=0.9, zorder=3
        ))
        
        # Label text
        ax.text(x + width/2, label_y,
                label,
                ha='center', va='center',
                fontsize=fontsize, fontweight='bold',
                color="#1A252F", zorder=4)
        
        # Area label
        ax.text(x + width/2, y - height + 1.5,
                f"{zone['sqm']:,.0f} m²",
                ha='center', va='center',
                fontsize=6.5, color="#555555",
                style='italic', zorder=4)
        
        # Capacity if applicable
        cap = layout_data['capacities'].get(zone['name'])
        if cap:
            ax.text(x + width/2, y - height + 3.5,
                    f"Capacity: ~{cap}",
                    ha='center', va='center',
                    fontsize=6, color="#2E86C1",
                    fontweight='bold', zorder=4)
    
    # Draw production zones (left column)
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
    
    # --- Central Service Lane ---
    ax.add_patch(mpatches.FancyBboxPatch(
        (LEFT_X + LEFT_W + 0.5, BOTTOM_Y),
        RIGHT_X - (LEFT_X + LEFT_W) - 1, TOP_Y - BOTTOM_Y,
        boxstyle="square,pad=0",
        linewidth=0, facecolor="#EBF5FB", alpha=0.6, zorder=1
    ))
    
    # Service lane markings
    for y in range(10, 95, 10):
        ax.plot([LEFT_X + LEFT_W + 29, LEFT_X + LEFT_W + 29], 
                [y, y+5], '--', color="#3498DB", linewidth=1.5, alpha=0.6)
    
    ax.text(LEFT_X + LEFT_W + 29, (TOP_Y + BOTTOM_Y)/2,
            "MAIN\nSERVICE\nLANE\n(6m wide)",
            ha='center', va='center',
            fontsize=7, color="#2E86C1",
            fontweight='bold', rotation=90, zorder=5)
    
    # --- Flow Arrows (Professional Style) ---
    for ay_pos in [80, 60, 40, 20]:
        ax.annotate("", 
                    xy=(LEFT_X + LEFT_W - 1, ay_pos - 5),
                    xytext=(LEFT_X + LEFT_W - 1, ay_pos),
                    arrowprops=dict(arrowstyle="->", color="#E74C3C", 
                                   lw=2, shrinkA=0, shrinkB=0),
                    zorder=5)
    
    # --- North Arrow (Professional Compass) ---
    cx, cy, r = 94, 94, 4
    # Circle
    ax.add_patch(mpatches.Circle((cx, cy), r, fill=False, 
                                  edgecolor="#2C3E50", linewidth=1.5, zorder=6))
    # N arrow
    ax.annotate("", xy=(cx, cy+r-0.5), xytext=(cx, cy),
                arrowprops=dict(arrowstyle="->", color="#E74C3C", 
                               lw=2.5, shrinkA=0, shrinkB=0),
                zorder=6)
    ax.text(cx, cy+r+0.8, "N", ha='center', va='center',
            fontsize=9, fontweight='bold', color="#E74C3C", zorder=6)
    
    # --- Scale Bar ---
    land_sqm = layout_data['total_sqm']
    side_m = math.sqrt(land_sqm)
    scale_width = 20  # 20 units on map
    
    # Scale bar background
    ax.add_patch(mpatches.FancyBboxPatch(
        (3, 0.5), 25, 3,
        boxstyle="round,pad=0.2",
        linewidth=0, facecolor="#FFFFFF", alpha=0.9, zorder=7
    ))
    
    # Scale bar line
    ax.plot([4, 24], [2, 2], '-', color="#2C3E50", linewidth=2, zorder=7)
    ax.plot([4, 4], [1.5, 2.5], '-', color="#2C3E50", linewidth=1.5, zorder=7)
    ax.plot([24, 24], [1.5, 2.5], '-', color="#2C3E50", linewidth=1.5, zorder=7)
    ax.plot([14, 14], [1.7, 2.3], '-', color="#2C3E50", linewidth=1, zorder=7)
    
    actual_m = (scale_width / 100) * side_m
    ax.text(14, 0.8, f"Scale: {scale_width} units = {actual_m:.0f}m",
            ha='center', va='center',
            fontsize=7, color="#555555", zorder=7)
    
    # --- Legend Section ---
    legend_patches = []
    for z in zones:
        color = ZONE_COLORS.get(z['name'], "#D5D8DC")
        patch = mpatches.Patch(facecolor=color, edgecolor="#2C3E50", 
                              linewidth=0.8, label=z['name'])
        legend_patches.append(patch)
    
    ax.legend(handles=legend_patches,
              loc='lower center',
              bbox_to_anchor=(0.5, -0.15),
              ncol=6, fontsize=6,
              framealpha=0.95, edgecolor="#BDC3C7",
              title="ZONE LEGEND", title_fontsize=7.5,
              handletextpad=0.5, borderpad=0.8)
    
    # --- Info Box (Bottom Right) ---
    info_text = (f"Total Area: {layout_data['total_sqm']:,.0f} m²\n"
                 f"            {layout_data['total_sqft']:,.0f} sq ft\n"
                 f"Generated: {layout_data['generated_at']}")
    
    ax.add_patch(mpatches.FancyBboxPatch(
        (68, 0.5), 30, 5,
        boxstyle="round,pad=0.4",
        linewidth=1, edgecolor="#95A5A6",
        facecolor="#FFFFFF", alpha=0.95, zorder=8
    ))
    ax.text(83, 3, info_text,
            ha='center', va='center',
            fontsize=7, color="#555555",
            zorder=8, family='monospace')
    
    # --- Watermark/Branding ---
    ax.text(50, -2,
            "PROFESSIONAL FARM PLANNING SERVICES",
            ha='center', va='center',
            fontsize=8, color="#95A5A6",
            alpha=0.6, zorder=9)
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.97])
    
    # Save with high DPI
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()
