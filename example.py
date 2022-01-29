import random
from pathlib import Path

from screen import VocoreScreen

if __name__ == "__main__":
    new_brightness = random.randint(0, 255)
    picture = Path("example_frames/frame.dat").read_bytes()
    print(f"Setting brightness to {new_brightness}")

    d = VocoreScreen()
    d.set_brightness(new_brightness)
    d._set_frame(picture)
