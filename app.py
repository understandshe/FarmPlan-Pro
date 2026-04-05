def draw_realistic_map(data):
    """
    Professional CAD-Style Architectural Map (Black & White)
    Looks like an AutoCAD print / Engineering Blueprint.
    """
    zones = data["zones"]
    acres = data["land_acres"]
    farm = data["farm_type"]
    
    fig = plt.figure(figsize=(16, 11), facecolor="#FFFFFF") # White background
    ax = fig.add_axes([0.02, 0.12, 0.75, 0.82])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")
    ax.axis("off")
    
    # Graph Paper Grid Effect
    ax.grid(True, linestyle=':', color='#DDDDDD', linewidth=0.5, zorder=0)
    
    # Layout Geometry
    PLOT_X, PLOT_Y, PLOT_W, PLOT_H = 5, 5, 90, 90
    GAP = 0.6
    
    # Separate zones
    road_z = [z for z in zones if z["ztype"] == "road"]
    main_z = [z for z in zones if z["ztype"] != "road"]
    
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
    
    # Draw Zones (CAD Style: Black Lines, Hatching, No Colors)
    for z, x, y, w, h in placed_left + placed_right:
        # Determine Hatch Pattern based on type
        hatch = ""
        if z["ztype"] == "barn": hatch = "///"      # Diagonal for structures
        elif z["ztype"] == "green": hatch = "..."   # Dots for fields
        elif z["ztype"] == "store": hatch = "|||"   # Vertical for stores
        elif z["ztype"] == "open": hatch = "\\\\"   # Backslash for open areas
        elif z["ztype"] == "util": hatch = "+++"    # Cross for utilities
        
        # Rectangle with Black Edge and Hatch
        ax.add_patch(patches.Rectangle((x, y), w, h, 
                                       facecolor="white", 
                                       edgecolor="#000000", 
                                       linewidth=1.2, 
                                       hatch=hatch, 
                                       zorder=2))
        
        # Text Label (Monospace Font for Technical Look)
        ax.text(x + w/2, y + h/2, z["name"], ha="center", va="center", 
                fontsize=7, fontweight="bold", color="#000000", 
                fontfamily="monospace", zorder=4)
        
        # Area Text
        ax.text(x + w/2, y + h/2 - 0.6, f"{z['sqm']:.0f}m²", ha="center", va="center", 
                fontsize=5.5, color="#555555", style="italic", 
                fontfamily="monospace", zorder=4)

    # Draw Service Lane (Dashed Center Line)
    lane_x = PLOT_X + left_w + GAP
    ax.add_patch(patches.Rectangle((lane_x, PLOT_Y), lane_w, PLOT_H, 
                                   facecolor="#F5F5F5", edgecolor="#000000", linewidth=0.5, zorder=1))
    ax.plot([lane_x + lane_w/2, lane_x + lane_w/2], [PLOT_Y, PLOT_Y+PLOT_H], 
            color="#000000", lw=1.0, ls="--", zorder=2)
    ax.text(lane_x + lane_w/2, PLOT_Y + PLOT_H/2, "SERVICE\nLANE", ha="center", va="center", 
            fontsize=5, fontweight="bold", color="#000000", rotation=90, 
            fontfamily="monospace", zorder=3)

    # Trees (Survey Symbol: Black Crosses instead of Green Circles)
    for t in range(8, 93, 8):
        # Top & Bottom Perimeter
        ax.plot(t, 3, marker='x', color='black', markersize=8, markeredgewidth=1.5, zorder=5)
        ax.plot(t, 97, marker='x', color='black', markersize=8, markeredgewidth=1.5, zorder=5)
    for t in range(8, 93, 8):
        # Left & Right Perimeter
        ax.plot(3, t, marker='x', color='black', markersize=8, markeredgewidth=1.5, zorder=5)
        ax.plot(97, t, marker='x', color='black', markersize=8, markeredgewidth=1.5, zorder=5)

    # Compass Rose (Simple Black Arrow)
    ax.text(94, 94, "N", ha="center", va="center", fontsize=10, fontweight="bold", color="#000000", zorder=6, fontfamily="monospace")
    ax.annotate("", xy=(94, 93), xytext=(94, 90), arrowprops=dict(arrowstyle="->", color="black", lw=1.5), zorder=6)

    # Scale Bar (Black)
    ax.plot([8, 28], [3, 3], color="#000000", lw=2, zorder=6)
    ax.text(18, 2, "Scale: 20m", ha="center", fontsize=6, color="#000000", fontfamily="monospace", zorder=6)
    
    # Title Block (Bottom Left)
    fig.text(0.02, 0.05, f"FARMPLAN PRO | {acres} Acre {farm} Site Plan", fontsize=12, fontweight="bold", color="#000000", fontfamily="monospace")
    fig.text(0.02, 0.02, f"Ref: {data['ref']} | Date: {data['generated']}", fontsize=8, color="#555555", fontfamily="monospace")

    # Legend Box (Right Side) - Styled Black & White
    ax_l = fig.add_axes([0.79, 0.12, 0.19, 0.82])
    ax_l.set_xlim(0, 10)
    ax_l.set_ylim(0, 10)
    ax_l.axis("off")
    ax_l.add_patch(patches.Rectangle((0, 0), 10, 10, facecolor="#FFFFFF", edgecolor="#000000", lw=1))
    ax_l.text(5, 9.5, "LEGEND", ha="center", fontsize=9, fontweight="bold", color="#000000", fontfamily="monospace")
    
    legend_items = [("/// Barn/Structure", "///"), ("... Green/Field", "..."), 
                    ("||| Store", "|||"), ("=== Road/Lane", "---")]
    ly = 8.5
    for txt, hatch_sym in legend_items:
        ax_l.add_patch(patches.Rectangle((0.5, ly-0.4), 1.5, 0.8, facecolor="white", edgecolor="#000000", hatch=hatch_sym))
        ax_l.text(2.5, ly, txt, va="center", fontsize=6.5, color="#000000", fontfamily="monospace")
        ly -= 1.0

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=250, bbox_inches="tight", facecolor="#FFFFFF")
    plt.close(fig)
    buf.seek(0)
    return buf.read()
