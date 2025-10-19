# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.

import smbus
import time
from gpiozero import LED
import sys 

LED_PIN = 18              
GYRO_THRESHOLD = 4000     
GYRO_ACCEL_ADDR = 0x6B    
MAG_ACCEL_ADDR = 0x1D     

led = LED(18)
led_status = False 


is_rotating = False
rotation_direction = None

bus = None 

bus = smbus.SMBus(1)

bus.write_byte_data(GYRO_ACCEL_ADDR, 0x20, 0x0F)

bus.write_byte_data(GYRO_ACCEL_ADDR, 0x23, 0x30)

bus.write_byte_data(MAG_ACCEL_ADDR, 0x20, 0x67)
bus.write_byte_data(MAG_ACCEL_ADDR, 0x21, 0x20)
bus.write_byte_data(MAG_ACCEL_ADDR, 0x24, 0x70)
bus.write_byte_data(MAG_ACCEL_ADDR, 0x25, 0x60)
bus.write_byte_data(MAG_ACCEL_ADDR, 0x26, 0x00)

time.sleep(1.0)

while True:
    
    sys.stdout.write('\033[2J\033[H') 
        
    data0 = bus.read_byte_data(GYRO_ACCEL_ADDR, 0x28) # X-Axis LSB
    data1 = bus.read_byte_data(GYRO_ACCEL_ADDR, 0x29) # X-Axis MSB
    xGyro = data1 * 256 + data0
    if xGyro > 32767:
        xGyro -= 65536
        
    abs_xGyro = abs(xGyro)
        
    if abs_xGyro > GYRO_THRESHOLD:
        is_rotating = True
        if xGyro < 0 :
            rotation_direction = "LEFT"
        else :
            rotation_direction = "RIGHT" 
        
    elif is_rotating and abs_xGyro < 100: # rotating end
        is_rotating = False
            
        if rotation_direction == "LEFT":
            led_status = True
            led.on()
                
        elif rotation_direction == "RIGHT":
            led_status = False
            led.off()
            
        rotation_direction = None 
        time.sleep(0.5)

    print(f"旋轉狀態: {'正在旋轉' if is_rotating else '靜止'}")
    print(f"LED (GPIO {LED_PIN}) 狀態: {'開啟' if led_status else '關閉'}")
    print("-" * 30)

    time.sleep(0.1) 
