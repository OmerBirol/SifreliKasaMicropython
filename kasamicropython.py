
from machine import Pin, ADC, I2C
from time import sleep
from picobricks import SSD1306_I2C, MotorDriver


BUTTON_PIN = 4
POT_PIN    = 34
LDR_PIN    = 35

SCREEN_WIDTH  = 128
SCREEN_HEIGHT = 64
SCREEN_ADDRESS = 0x3C

OPEN_POSITION   = 0   
CLOSED_POSITION = 30  
LIGHT_THRESHOLD = 500  

THRESHOLD_16 = LIGHT_THRESHOLD * 65535 // 4095


correct_password = [1, 1, 1, 1]
entered_password = [0, 0, 0, 0]


state = 0
pass_index = 0
old_digit = -1
button_released = True


i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c, addr=SCREEN_ADDRESS)
motor = MotorDriver(i2c)


button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
pot    = ADC(Pin(POT_PIN))
ldr    = ADC(Pin(LDR_PIN))


def password_check():
    for a, b in zip(correct_password, entered_password):
        if a != b:
            return False
    return True


def lock_safe():
    oled.fill(0)
    oled.text("Locking...", 0, 0)
    oled.show()
    motor.servo(1, CLOSED_POSITION)
    sleep(0.5)
    oled.fill(0)
    oled.show()


def unlock_safe():
    oled.fill(0)
    oled.text("Unlocked!", 0, 0)
    oled.show()
    motor.servo(1, OPEN_POSITION)
    sleep(0.5)


oled.fill(0)
oled.text("Safe Box", 0, 0)
oled.show()
motor.servo(1, CLOSED_POSITION)


while True:
    ldr_val = ldr.read_u16()

    
    if state == 1:
        if ldr_val > THRESHOLD_16:
            state = 2
        sleep(0.1)
        continue

    
    if state == 2:
        if ldr_val < THRESHOLD_16:
            lock_safe()
            state = 0
        sleep(0.1)
        continue

    
    raw = pot.read_u16()
    digit = raw * 9  // 65535

    if digit != old_digit:
        old_digit = digit
        oled.fill(0)
        oled.text(f"Enter #: {digit}", 0, 0)
        oled.show()

    
    if button.value() == 1 and button_released:
        button_released = False
        entered_password[pass_index] = digit
        pass_index += 1

        if pass_index >= 4:
            if password_check():
                unlock_safe()
                state = 1
            else:
                oled.fill(0)
                oled.text("Wrong!", 0, 0)
                oled.show()
                sleep(1.5)
                oled.fill(0)
                oled.show()
            pass_index = 0

    if button.value() == 0:
        button_released = True

    sleep(0.1)

