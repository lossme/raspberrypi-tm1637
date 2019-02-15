# 数码管显示器驱动

raspberry pi LED数码管显示器驱动

驱动文件在`tm1637.py`里，使用示例

```python
import RPi.GPIO as GPIO

from tm1637 import TM1637


# 默认使用 BOARD 编码
display = TM1637(clk=38, dio=40, brightnes=2, is_show_point=False, pin_mode=GPIO.BOARD)

# 显示1,2,3,4
display.show(1, 2, 3, 4)

# 清空显示屏
display.clear()

# 第三、第四个位置不显示东西
display.show(1, 2, None, None)

# 显示中间的点
display.show_point()

# 不显示中间的点
display.close_point()

# 设置显示屏亮度，0-7级
display.set_brightnes(1)

# 精确控制数码管的亮灭
display.show_data((0b1111111, 0b1111111, 0b1111111, 0b1000000))

# 关闭数码管
display.disable()

# 开启数码管
display.enable()
```
