import time

# Bus Values
PCA9685_I2C_ADDR = 0x40
PCA9685_I2C_BUSNUM = 1

# Throttle Values
THROTTLE_CHANNEL = 0
THROTTLE_FORWARD_PWM = 500
THROTTLE_STOPPED_PWM = 370
THROTTLE_REVERSE_PWM = 220

def clamp(n, min, max):
    if min > max:
        return clamp(n, max, min)

    if n < min:
        return min
    if n > max:
        return max
    return n

def is_number_type(i):
    return type(i) == int or type(i) == float;

def map_range(x, X_min, X_max, Y_min, Y_max):
    '''
    Linear mapping between two ranges of values
    '''
    X_range = X_max - X_min
    Y_range = Y_max - Y_min
    XY_ratio = X_range/Y_range

    y = ((x-X_min) / XY_ratio + Y_min) // 1

    return int(y)

class PCA9685:
    ''' 
    PWM motor controler using PCA9685 boards. 
    This is used for most RC Cars
    '''
    def __init__(self, channel, address=0x40, frequency=60, busnum=None, init_delay=0.1):

        self.default_freq = 60
        self.pwm_scale = frequency / self.default_freq

        import Adafruit_PCA9685
        from Adafruit_GPIO import I2C       
        busnum = I2C.get_default_bus()

        self.pwm = Adafruit_PCA9685.PCA9685(address=address)
        self.pwm.set_pwm_freq(frequency)
        self.channel = channel
        self.busnum = busnum
        self.address = address
        time.sleep(init_delay) # "Tamiya TBLE-02" makes a little leap otherwise

        print(f"channel: {self.channel}")
        print(f"busnum: {self.busnum}")
        print(f"address: {self.address}")

    def set_high(self):
        self.pwm.set_pwm(self.channel, 4096, 0)

    def set_low(self):
        self.pwm.set_pwm(self.channel, 0, 4096)

    def set_duty_cycle(self, duty_cycle):
        if duty_cycle < 0 or duty_cycle > 1:
            duty_cycle = clamp(duty_cycle, 0, 1)
            
        if duty_cycle == 1:
            self.set_high()
        elif duty_cycle == 0:
            self.set_low()
        else:
            # duty cycle is fraction of the 12 bits
            pulse = int(4096 * duty_cycle)
            try:
                self.pwm.set_pwm(self.channel, 0, pulse)
            except:
                self.pwm.set_pwm(self.channel, 0, pulse)

    def set_pulse(self, pulse):
        try:
            self.pwm.set_pwm(self.channel, 0, int(pulse * self.pwm_scale))
        except:
            self.pwm.set_pwm(self.channel, int(pulse * self.pwm_scale), 0)

    def run(self, pulse):
        self.set_pulse(pulse)

if __name__ == '__main__':   
    print('running main')
    motor = PCA9685(channel=THROTTLE_CHANNEL)
    motor.set_pulse(0)

