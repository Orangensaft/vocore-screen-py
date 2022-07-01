from .font import FONT_5x7

from .screen import VocoreScreen

def run():
    d = VocoreScreen()
    d.set_brightness(255)
    d.draw_string(45, 430, "".join([str(c) for c in FONT_5x7 if c != -1]), "#00FF00")
    d.draw_rect(50, 50, 100, 100, "#FF24FF")
    d.draw_line(50, 50, 100, 100, "FFFF00")
    d.draw_rect(160, 50, 260, 150, "#00FFFF")
    d.draw_line(160, 150, 260, 50, "#FFFF00")
    d.draw_string(300, 150, "Hello, World!", "#FFBB00")
    d.draw_line(0, 0, 800 - 1, 480 - 1, "#FFFFFF")
    d.draw_line(0, 480 - 1, 800 - 1, 0, "#FFFFFF")
    d.draw_rect(600, 150, 700, 300, "#00FF00", fill=True)
    d.blit()  # Update screen


if __name__ == "__main__":
    run()
