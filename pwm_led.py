#-*- coding: utf-8 -*
import RPi.GPIO as GPIO
import os
import time
from pin_dic import pin_dic
from threading import Thread

class RGB_LED(object):
    def __init__(self,pin_R,pin_G,pin_B):
        self.pins = [pin_R,pin_G,pin_B]
        
        # 设置为输出引脚，初始化第电平，灯灭
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)   
            GPIO.output(pin, GPIO.LOW)
            
        # 设置三个引脚为pwm对象，频率2000
        self.pwm_R = GPIO.PWM(pin_R, 2000)  
        self.pwm_G = GPIO.PWM(pin_G, 2000)
        self.pwm_B = GPIO.PWM(pin_B, 2000)
    
        # 初始占空比为0
        self.pwm_R.start(0)      
        self.pwm_G.start(0)
        self.pwm_B.start(0)

    def color2ratio(self,x,min_color,max_color,min_ratio,max_ratio):
        return (x - min_color) * (max_ratio - min_ratio) / (max_color - min_color) + min_ratio

    def setColor(self,col):
        R_val,G_val,B_val = col
   
        R =self.color2ratio(R_val, 0, 255, 0, 100)
        G =self.color2ratio(G_val, 0, 255, 0, 100)
        B =self.color2ratio(B_val, 0, 255, 0, 100)
        # 改变占空比
        self.pwm_R.ChangeDutyCycle(R)     
        self.pwm_G.ChangeDutyCycle(G)
        self.pwm_B.ChangeDutyCycle(B)
        
    def destroy(self):    
        self.pwm_R.stop()
        self.pwm_G.stop()
        self.pwm_B.stop()
        for pin in self.pins:
            GPIO.output(pin, GPIO.HIGH)    
        GPIO.cleanup()

class Ds18b20(object):
    
    def __init__(self,str_id):
        self.str_id = str_id
        
    def read(self):
        # 读取温度传感器的数值
        location = os.path.join( "/sys/bus/w1/devices",self.str_id,"w1_slave") 

        if os.path.exists(location):
            with open(location) as tf:
                lines = tf.read().splitlines()
            
            text = lines[-1]
            temperaturedata = text.split(" ")[-1]
            
            temperature = float(temperaturedata[2:])
            
            return temperature/1000.0
        else:
            return False

global gFlag
def myThread():
    global gFlag
    while True:
        # 以下请补充和温度传感器有关的代码：
        t = m_ds18b20.read()
        if t < 28.0:
            gFlag = False
        else:
            gFlag = True
        print(t)
        time.sleep(0.1)

if __name__ == "__main__":

    # 设置引脚编号模式
    GPIO.setmode(GPIO.BOARD)
    
    # 定义三个引脚 
    pin_R = pin_dic['G17']
    pin_G = pin_dic['G16']
    pin_B = pin_dic['G13']
    
    # 定义 RGB_LED 对象
    m_RGB_LED = RGB_LED(pin_R,pin_G,pin_B)

    # 温度传感器线程
    global gFlag
    gFlag = False
    str_id = "28-3ce1e381284c"
    m_ds18b20 =  Ds18b20(str_id)
    m_thread = Thread(target=myThread, args=([]),daemon=True)
    m_thread.start()

    # 呼吸灯线程
    direction = True
    val = 0
    try:
        while True:

            if gFlag:
                # 设置颜色
                m_RGB_LED.setColor((val,0,0))
                # 延时
                time.sleep(0.05)
                # 呼吸灯
                if direction:
                    if val < 200:
                        val = val+5
                    else:
                        direction = False
                else:
                    if val > 0:
                        val = val-5
                    else:
                        direction = True
            else:
                direction = True
                val = 0
                m_RGB_LED.setColor((val,0,0))
                time.sleep(0.05)

    except KeyboardInterrupt:
        print('\n Ctrl + C QUIT')   
    finally:
        m_RGB_LED.destroy()

    
    
    
   
