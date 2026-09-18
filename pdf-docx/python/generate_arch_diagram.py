import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def draw_horizontal_flowchart():
    fig, ax = plt.subplots(figsize=(10, 3.2), dpi=300)
    ax.set_xlim(0, 10.8)
    ax.set_ylim(0, 4)
    ax.axis('off')
    
    def draw_box(x, y, text, fc="white", w=1.2, h=0.6):
        box = mpatches.Rectangle((x-w/2, y-h/2), w, h, fc=fc, ec="black", lw=1.2)
        ax.add_patch(box)
        ax.text(x, y, text, ha="center", va="center", size=9, weight="bold")
                
    def draw_rhombus(x, y, text, w=1.4, h=0.8):
        diamond = mpatches.Polygon([[x, y+h/2], [x+w/2, y], [x, y-h/2], [x-w/2, y]], closed=True, fc="white", ec="black", lw=1.2)
        ax.add_patch(diamond)
        ax.text(x, y, text, ha="center", va="center", size=8.5, weight="bold")
        
    def arrow(x1, y1, x2, y2, text=""):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
        if text:
            mx, my = (x1+x2)/2, (y1+y2)/2
            if x1 == x2:
                ax.text(mx + 0.15, my, text, size=8.5, va="center")
            else:
                ax.text(mx, my + 0.15, text, size=8.5, ha="center")

    y_main = 2.8
    y_fail = 1.0

    # Nodes
    draw_box(1.0, y_main, "Receive\nPacket", fc="white", w=1.0)
    draw_box(2.4, y_main, "Decrypt\n(ChaCha20)", fc="white", w=1.3)
    draw_rhombus(4.0, y_main, "Tag OK?", w=1.1)
    draw_rhombus(5.5, y_main, "T < 30s?", w=1.1)
    draw_rhombus(7.0, y_main, "Hash OK?", w=1.1)
    draw_rhombus(8.5, y_main, "WM OK?", w=1.1)
    draw_box(9.85, y_main, "Authentic", fc="white", w=1.0)
    
    # Fail nodes
    draw_box(4.0, y_fail, "Tampered\n(AEAD)", fc="white", w=1.1, h=0.7)
    draw_box(5.5, y_fail, "Replay\n(Timeout)", fc="white", w=1.1, h=0.7)
    draw_box(7.0, y_fail, "Tampered\n(Hash Fail)", fc="white", w=1.1, h=0.7)
    draw_box(8.5, y_fail, "Tampered\n(WM Fail)", fc="white", w=1.1, h=0.7)
    
    # Arrows Main
    arrow(1.5, y_main, 1.75, y_main)
    arrow(3.05, y_main, 3.45, y_main)
    arrow(4.55, y_main, 4.95, y_main, "Yes")
    arrow(6.05, y_main, 6.45, y_main, "Yes")
    arrow(7.55, y_main, 7.95, y_main, "Yes")
    arrow(9.05, y_main, 9.35, y_main, "Yes")
    
    # Arrows Fail
    arrow(4.0, y_main-0.4, 4.0, y_fail+0.35, "No")
    arrow(5.5, y_main-0.4, 5.5, y_fail+0.35, "No")
    arrow(7.0, y_main-0.4, 7.0, y_fail+0.35, "No")
    arrow(8.5, y_main-0.4, 8.5, y_fail+0.35, "No")
    
    plt.tight_layout()
    plt.savefig('fig_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    draw_horizontal_flowchart()
