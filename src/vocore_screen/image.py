from .font import FONT_5x7

HEIGHT = 480
WIDTH = 800
BUFFER_SIZE = WIDTH * HEIGHT * 2


class Image:
    def __init__(self):
        # iterates: y first, THEN x!
        self.buffer = bytearray(bytes(BUFFER_SIZE))
        # 2 bytes per pixel (16 bit)

    def save_to_file(self, fname):
        with open(fname, "wb") as f:
            f.write(self.buffer)

    def clear(self):
        for i in range(len(self.buffer)):
            self.buffer[i] = 0

    @staticmethod
    def get_pixel_addr(x, y):
        # switch x and y for landscape mode
        return y * 2 + HEIGHT * 2 * x

    def set_pixel(self, x, y, color):
        value = self.to_565(color)
        value = value.to_bytes(2, "little")
        address = self.get_pixel_addr(x, y)
        self.buffer[address] = value[0]
        self.buffer[address + 1] = value[1]

    def draw_char(self, x, y, c: str, color, scale=1):
        # assuming font size 5x7
        bits = FONT_5x7.get(c.upper(), FONT_5x7[-1])
        for offset_y in range(7 * scale):
            for offset_x in range(5 * scale):
                bit_pos = (6 - (offset_y // scale)) * 5 + offset_x // scale
                if bits[bit_pos] == "1":
                    self.set_pixel(x + offset_x, y + offset_y, color)

    def draw_string(self, x, y, s: str, color, size=1):
        offset = 0
        for i in s:
            self.draw_char(x + offset, y, i, color, size)
            offset += 6 * size

    @staticmethod
    def to_565(rgb888):
        if type(rgb888) is str:
            "#RRGGBB"
            r, g, b = int(rgb888[1:3], 16), int(rgb888[3:5], 16), int(rgb888[5:7], 16)
        else:
            # an int
            b = rgb888 & 0b11111111
            g = (rgb888 >> 8) & 0b11111111
            r = rgb888 >> 16
        r = round(r / 255 * 31)
        g = round(g / 255 * 63)
        b = round(b / 255 * 31)

        rgb565 = (r << 11) + (g << 5) + b

        return rgb565
