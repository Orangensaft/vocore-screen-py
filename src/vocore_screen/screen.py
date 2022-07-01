from copy import deepcopy

import usb.core
import usb.legacy

from .image import Image

VENDOR = 0xC872
PRODUCT = 0x1004


class VocoreScreen:
    def __init__(self):
        # Get device handle
        self.device: usb.core.Device = usb.core.find(idVendor=VENDOR, idProduct=PRODUCT)
        if self.device is None:
            raise Exception("Vocore screen not found :<")
        self.legacy_device_handle = usb.legacy.Device(self.device).open()
        # wakeup screen
        self._wakeup()
        self.buffer = Image()
        self.clear(blit=True)

    def get_last_touch_event(self):
        """
        Try to get touch event, will return None if no event is detected
        """
        try:
            r = self.legacy_device_handle.interruptRead(0x81, 128)
            # TODO: Parse this :D
            """ (all unsigned chars)
            char unused
            char unused
            char count
            ----------
            point (2x):
                union axis xh:
                    struct hx (8bit)
                        char h (4bit)
                        char u (2bit)
                        char f (2bit)
                    struct hy (8bit)
                        char h (4bit)
                        char id (4bit)
                    char c (8bit)
                char x1 (8bit)
                union axis yh 
                    hx (8 bit)
                    hy (8 bit)
                    c (8 bit)
                char y1 8bit
                char weight 8bit
                char misc 8bit
            """
            """
            Getting coord of a single point:
            X-Cord:
            point[0].xh.hx.h  <--- Upper 8 bit
            point[0].x1   <--- Lower 8 bit
            
            x = (point[0].xh.hx.h << 8)  + point[0].x1

            Y-Cord:
            (point[0].yh.hy.h << 8) + point[0].y1            
            """
            return r
        except:
            return None

    def _debug_touch_loop(self):
        last = None
        while True:
            event = self.get_last_touch_event()
            if event is not None and event != last:
                print(event)
                print(bin(int.from_bytes(event.tobytes(), "little")))
                last = deepcopy(event)

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
        self.buffer.set_pixel(x, y, color)
        if blit:
            self.blit()

    def draw_line(self, x1, y1, x2, y2, color, blit=False):
        sign = lambda x: -1 if x < 0 else 1 if x > 0 else 0

        dx = x2 - x1
        dy = y2 - y1
        increment_x = sign(dx)
        increment_y = sign(dy)
        if dx < 0:
            dx *= -1
        if dy < 0:
            dy *= -1

        par_dx = increment_x if dx > dy else 0
        par_dy = increment_y if not (dx > dy) else 0

        delta_slow = dy if dx > dy else dx
        delta_fast = dx if dx > dy else dy

        x = x1
        y = y1
        err = delta_fast // 2
        self.draw_pixel(x, y, color)

        for i in range(delta_fast):
            err -= delta_slow
            if err < 0:
                # diagonal step
                err += delta_fast
                x += increment_x
                y += increment_y
            else:
                x += par_dx
                y += par_dy
            self.draw_pixel(x, y, color)

        if blit:
            self.blit()

    def draw_rect(self, x1, y1, x2, y2, color, fill=False, blit=False):
        """
        Draws rectangle from x1,y1 to x2,y2
        """
        if fill:
            for x in range(x1, x2):
                for y in range(y1, y2):
                    self.draw_pixel(x, y, color)
        else:
            self.draw_line(x1, y1, x1, y2, color)
            self.draw_line(x1, y1, x2, y1, color)
            self.draw_line(x2, y1, x2, y2, color)
            self.draw_line(x1, y2, x2, y2, color)

        if blit:
            self.blit()

    def draw_string(self, x, y, s: str, color, blit=False, size=2):
        """
        Draws text on given position, where x and y are the lower left corner.
        As a 5x7 font is used use size as scaling factor
        """
        self.buffer.draw_string(x, y, s, color, size)
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

    def _get_version(self):
        # WIP
        cmd = [0x51, 0x02, 0x04, 0x1F, 0xFC]
        self.device.ctrl_transfer(0x40, 0xB5, 0, 0, cmd)
        ret = self.device.ctrl_transfer(0xC0, 0xB6, 0, 0, cmd)
        print(ret)
        ret = self.device.ctrl_transfer(0xC0, 0xB7, 0, 0, cmd)
        print(ret)
        return ret

    def _get_uid(self):
        # WIP
        cmd = [0x51, 0x02, 0x08, 0x1F, 0xF0]
        buf = [0 for i in range(9)]
        self.device.ctrl_transfer(0x40, 0xB5, 0, 0, cmd)
        ret = self.device.ctrl_transfer(0xC0, 0xB6, 0, 0, cmd)
        print(ret)
        x = self.device.ctrl_transfer(0xC0, 0xB7, 0, 0, buf)
        return "{:02x}{:02x}-{:02x}{:02x}-{:02x}{:02x}{:02x}{:02x}\n".format(
            x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7]
        )

    def _wakeup(self):
        """
        Wakeup screen (This is needed for the screen to work)
        """
        cmd = [0x00, 0x29]
        self.device.ctrl_transfer(0x40, 0xB0, 0, 0, cmd, 100)
