import usb.core

from image import Image

VENDOR = 0xC872
PRODUCT = 0x1004


class VocoreScreen:
    def __init__(self):
        # Get device handle
        self.device: usb.core.Device = usb.core.find(idVendor=VENDOR, idProduct=PRODUCT)
        if self.device is None:
            raise Exception("Vocore screen not found :<")
        # wakeup screen
        self._wakeup()
        self.buffer = Image()
        self.clear(blit=True)

    def set_brightness(self, brightness: int):
        """
        Sets screen brightness
        :param brightness: 0-255
        """
        if brightness > 255 or brightness < 0:
            raise Exception("Invalid brightness value")

        cmd = [0x00, 0x51, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00]
        cmd[6] = brightness
        return self.device.ctrl_transfer(
            0x40, 0xB0, 0, 0, cmd, 100
        )  # takes bytes and lists. Has to be iter.

    def draw_pixel(self, x, y, color, blit=False):
        """
        Sets pixel at x, y to color. Will update device screen if blit is set to true.
        The color may be given as rgb 888 value
        :param x: X Coord (0 -> 800-1)
        :param y: Y Coord (0 -> 480-1)
        :param color: RGB Value as string (#89ABCDEF) or int 0x89ABCDEF
        :param blit: If true, buffer will be flipped to the display
        """
        self.buffer.set_pixel(x,y,color)
        if blit:
            self.blit()

    def draw_line(self, x1, y1, x2, y2, color, blit=False):
        """
        Draws a line from x1,y1 to x2,y2
        """
        # todo: bresenham algo
        sign = lambda x : -1 if x < 0 else 1 if x > 0 else 0
        if x1 == x2 or y1 == y2:
            # horizontal or vertical line
            dx = sign(x2 - x1)
            dy = sign(y2 - y1)
            self.draw_pixel(x1, y1, color)
            while (x1,y1) != (x2,y2):
                x1 += dx
                y1 += dy
                self.draw_pixel(x1, y1, color)
        else:
            raise NotImplementedError
        if blit:
            self.blit()

    def draw_rect(self, x1, y1, x2, y2, color, blit=False):
        """
        Draws rectangle from x1,y1 to x2,y2
        """
        self.draw_line(x1,y1, x1, y2, color)
        self.draw_line(x1,y1, x2, y1, color)
        self.draw_line(x2, y1, x2, y2, color)
        self.draw_line(x1, y2, x2, y2, color)
        if blit:
            self.blit()

    def clear(self, blit=False):
        """
        Clears internal buffer
        """
        self.buffer.clear()
        if blit:
            self.blit()

    def blit(self):
        """
        Writes buffer to vocore screen
        """
        self._set_frame(self.buffer.buffer)

    def _set_frame(self, data: bytes):
        """
        Internal method to send bytes to the screen
        """
        self._write_start()
        self.device.write(0x2, data)

    def _write_start(self):
        """
        Tells frame to receive 0x0bb80 (768000) bytes
        This is needed before calling _set_frame!
        """
        cmd = [0x00, 0x2C, 0x00, 0xB8, 0x0B, 0x00]
        self.device.ctrl_transfer(0x40, 0xB0, 0, 0, cmd, 100)

    def _wakeup(self):
        """
        Wakeup screen (This is needed for the screen to work)
        """
        cmd = [0x00, 0x29]
        self.device.ctrl_transfer(0x40, 0xB0, 0, 0, cmd, 100)