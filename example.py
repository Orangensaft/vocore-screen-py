from font import FONT_5x7

from screen import VocoreScreen

if __name__ == "__main__":
    d = VocoreScreen()
    d.set_brightness(255)
    d.draw_string(45, 430, "".join([str(c) for c in FONT_5x7 if c != -1]), "#00FF00")
    d.draw_rect(50,50,100,100,"#FF24FF")
    d.draw_rect(160,50,260,150,"#00FFFF")
    d.draw_string(300, 150, "Hello, World!", "#FFBB00")
    d.blit()  # Update screen
