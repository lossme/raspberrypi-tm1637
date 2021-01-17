import time
import RPi.GPIO as GPIO


class TM1637():
    """
    数码管显示器驱动
      A
     ---
  F |   | B
     -G-
  E |   | C
     ---
      D
"""

    COMMAND_DATA = 0x40         # data command
    COMMAND_ADDRESS = 0xC0      # address command
    COMMAND_CTRL = 0x80         # display control command
    TM1637_DSP_ON = 0x08        # display on
    TM1637_DSP_OFF = 0x00       # display off

    DIGIT_TO_SEGMENT = [
        0b0111111,  # 0
        0b0000110,  # 1
        0b1011011,  # 2
        0b1001111,  # 3
        0b1100110,  # 4
        0b1101101,  # 5
        0b1111101,  # 6
        0b0000111,  # 7
        0b1111111,  # 8
        0b1101111,  # 9
        0b1110111,  # A
        0b1111100,  # b
        0b0111001,  # C
        0b1011110,  # d
        0b1111001,  # E
        0b1110001  # F
    ]
    NONE_SEGMENT = 0b0000000

    DATA_CLEAR = (0x00, 0x00, 0x00, 0x00)

    def __init__(self, clk, dio, brightnes=2, is_show_point=False, pin_mode=GPIO.BOARD):
        """
        :param int clk: clk 时钟引脚编号
        :param int dio: dio 数据引脚编号
        :param int brightnes: 显示亮度 0-7
        :param bool is_show_point: 是否显示中间的点
        :param pin_mode: 引脚编码方式
        """
        assert 0 <= brightnes <= 7
        self.clk = clk
        self.dio = dio
        self.brightnes = brightnes
        self.is_show_point = is_show_point
        self.display_status = self.TM1637_DSP_ON  # 开启显示器

        GPIO.setwarnings(False)
        GPIO.setmode(pin_mode)
        GPIO.setup(self.clk, GPIO.OUT)
        GPIO.setup(self.dio, GPIO.OUT)
        self.current_data = self.DATA_CLEAR

    def enable(self):
        """开启显示屏"""
        self.display_status = self.TM1637_DSP_ON
        self.refresh()

    def disable(self):
        """关闭显示屏"""
        self.display_status = self.TM1637_DSP_OFF
        self.refresh()

    def set_brightnes(self, brightnes):
        assert 0 <= brightnes <= 7
        self.brightnes = brightnes
        self.refresh()

    def clear(self):
        """清空显示屏
        """
        self.show_data(self.DATA_CLEAR)

    def show_point(self):
        """显示中间的那个点
        """
        self.is_show_point = True
        self.current_data = (self.current_data[0],
                             self.current_data[1] | 0b10000000,
                             self.current_data[2],
                             self.current_data[3])
        self.refresh()

    def close_point(self):
        """不显示中间的那个点
        """
        self.is_show_point = False
        self.current_data = (self.current_data[0],
                             self.current_data[1] & 0b01111111,
                             self.current_data[2],
                             self.current_data[3])
        self.refresh()

    def show_data(self, data):
        """
        :param list/tuple data: 例如(0xff, 0xff, 0xff, 0x00])
        """
        self.current_data = tuple(data)
        self.start()
        self.write_byte(self.COMMAND_DATA)
        self.stop()
        self.start()
        self.write_byte(self.COMMAND_ADDRESS)
        for i in range(4):
            self.write_byte(data[i])
        self.stop()
        self.start()
        self.write_byte(self.COMMAND_CTRL | self.display_status | self.brightnes)
        self.stop()

    def show(self, data):
        """注意数字范围在0-9，-1表示不显示该位
        """
        a, b, c, d = data
        point_data = 0b10000000 if self.is_show_point else 0
        encoded_data = (
            self.NONE_SEGMENT if a is None else self.DIGIT_TO_SEGMENT[a],
            self.NONE_SEGMENT if b is None else self.DIGIT_TO_SEGMENT[b] | point_data,
            self.NONE_SEGMENT if c is None else self.DIGIT_TO_SEGMENT[c],
            self.NONE_SEGMENT if d is None else self.DIGIT_TO_SEGMENT[d],
        )
        self.show_data(encoded_data)

    def refresh(self):
        self.show_data(self.current_data)

    def write_byte(self, b):
        for i in range(0, 8):
            GPIO.output(self.clk, GPIO.LOW)
            if b & 0x01:
                GPIO.output(self.dio, GPIO.HIGH)
            else:
                GPIO.output(self.dio, GPIO.LOW)
            b >>= 1
            GPIO.output(self.clk, GPIO.HIGH)

        # wait for ACK
        GPIO.output(self.clk, GPIO.LOW)
        GPIO.output(self.dio, GPIO.HIGH)  # set data gpio high, util slave ack,set low
        GPIO.output(self.clk, GPIO.HIGH)
        GPIO.setup(self.dio, GPIO.IN)  # set data gpio to input for slave

        while GPIO.input(self.dio):
            time.sleep(0.001)
            if GPIO.input(self.dio):
                GPIO.setup(self.dio, GPIO.OUT)
                GPIO.output(self.dio, GPIO.LOW)
                GPIO.setup(self.dio, GPIO.IN)
        # 'ack is get'
        GPIO.setup(self.dio, GPIO.OUT)

    def start(self):
        GPIO.output(self.clk, GPIO.HIGH)
        GPIO.output(self.dio, GPIO.HIGH)
        GPIO.output(self.dio, GPIO.LOW)
        GPIO.output(self.clk, GPIO.LOW)

    def stop(self):
        GPIO.output(self.clk, GPIO.LOW)
        GPIO.output(self.dio, GPIO.LOW)
        GPIO.output(self.clk, GPIO.HIGH)
        GPIO.output(self.dio, GPIO.HIGH)
