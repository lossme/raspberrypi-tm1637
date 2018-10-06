## 数码管显示器驱动

raspberry pi LED数码管显示器驱动，[数码管长这个样子](https://www.seeedstudio.com/depot/grove-4digit-display-p-1198.html)

驱动文件在`tm1637.py`里，使用示例

```python
import RPi.GPIO as GPIO

from tm1637 import TM1637


# 默认使用 BOARD 编码
dispaly = TM1637(clk=38, dio=40, brightnes=2, is_show_point=False, pin_mode=GPIO.BOARD)

# 显示1,2,3,4
dispaly.show(1, 2, 3, 4)

# 清空显示屏
dispaly.clear()

# 第三、第四个位置不显示东西
dispaly.show(1, 2, -1, -1)

# 显示中间的点
dispaly.show_point()

# 不显示中间的点
dispaly.close_point()

# 设置显示屏亮度，0-7级
dispaly.set_brightnes(1)

# 精确控制数码管的亮灭
dispaly.show_data((0b1111111, 0b1111111, 0b1111111, 0b1000000))

# 关闭数码管
dispaly.OFF()

# 开启数码管
dispaly.ON()
```