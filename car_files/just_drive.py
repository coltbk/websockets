#!/usr/bin/env python3
"""
Scripts to drive a donkey 2 car

Usage:
    manage.py (drive)

Options:
    -h --help          Show this screen.
"""
import os
import time
import traceback

DRIVE_LOOP_HZ = 20
MAX_LOOPS = None

# Bus Values
PCA9685_I2C_ADDR = 0x40
PCA9685_I2C_BUSNUM = None

# Steering Values
STEERING_CHANNEL = 1
STEERING_LEFT_PWM = 460
STEERING_RIGHT_PWM = 290

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
        # Initialise the PCA9685 using the default address (0x40).
        if busnum is not None:
            from Adafruit_GPIO import I2C
            # replace the get_bus function with our own
            def get_bus():
                return busnum
            I2C.get_default_bus = get_bus
        self.pwm = Adafruit_PCA9685.PCA9685(address=address)
        self.pwm.set_pwm_freq(frequency)
        self.channel = channel
        time.sleep(init_delay) # "Tamiya TBLE-02" makes a little leap otherwise

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
            self.pwm.set_pwm(self.channel, 0, int(pulse * self.pwm_scale))

    def run(self, pulse):
        self.set_pulse(pulse)

class PWMSteering:
    """
    Wrapper over a PWM pulse controller to convert angles to PWM pulses.
    """
    LEFT_ANGLE = -1
    RIGHT_ANGLE = 1

    def __init__(self, controller, left_pulse, right_pulse):

        if controller is None:
            raise ValueError("PWMSteering requires a set_pulse controller to be passed")
        set_pulse = getattr(controller, "set_pulse", None)
        if set_pulse is None or not callable(set_pulse):
            raise ValueError("controller must have a set_pulse method")
        if not is_number_type(left_pulse):
            raise ValueError("left_pulse must be a number")
        if not is_number_type(right_pulse):
            raise ValueError("right_pulse must be a number")

        self.controller = controller
        self.left_pulse = left_pulse
        self.right_pulse = right_pulse
        self.pulse = map_range(0, self.LEFT_ANGLE, self.RIGHT_ANGLE,
                                self.left_pulse, self.right_pulse)
        self.running = True

    def update(self):
        while self.running:
            self.controller.set_pulse(self.pulse)

    def run_threaded(self, angle):
        # map absolute angle to angle that vehicle can implement.
        angle = clamp(angle, self.LEFT_ANGLE, self.RIGHT_ANGLE)
        self.pulse = map_range(angle,
                                self.LEFT_ANGLE, self.RIGHT_ANGLE,
                                self.left_pulse, self.right_pulse)

    def run(self, angle):
        self.run_threaded(angle)
        self.controller.set_pulse(self.pulse)

    def shutdown(self):
        # set steering straight
        self.pulse = 0
        time.sleep(0.3)
        self.running = False


class PWMThrottle:
    """
    Wrapper over a PWM pulse controller to convert -1 to 1 throttle
    values to PWM pulses.
    """
    MIN_THROTTLE = -1
    MAX_THROTTLE = 1

    def __init__(self, controller, max_pulse, min_pulse, zero_pulse):

        if controller is None:
            raise ValueError("PWMThrottle requires a set_pulse controller to be passed")
        set_pulse = getattr(controller, "set_pulse", None)
        if set_pulse is None or not callable(set_pulse):
            raise ValueError("controller must have a set_pulse method")

        self.controller = controller
        self.max_pulse = max_pulse
        self.min_pulse = min_pulse
        self.zero_pulse = zero_pulse
        self.pulse = zero_pulse

        # send zero pulse to calibrate ESC
        self.controller.set_pulse(self.max_pulse)
        time.sleep(0.01)
        self.controller.set_pulse(self.min_pulse)
        time.sleep(0.01)
        self.controller.set_pulse(self.zero_pulse)
        time.sleep(1)
        self.running = True

    def update(self):
        while self.running:
            self.controller.set_pulse(self.pulse)

    def run_threaded(self, throttle):
        throttle = clamp(throttle, self.MIN_THROTTLE, self.MAX_THROTTLE)
        if throttle > 0:
            self.pulse = map_range(throttle, 0, self.MAX_THROTTLE,
                                    self.zero_pulse, self.max_pulse)
        else:
            self.pulse = map_range(throttle, self.MIN_THROTTLE, 0,
                                    self.min_pulse, self.zero_pulse)

    def run(self, throttle):
        self.run_threaded(throttle)
        self.controller.set_pulse(self.pulse)

    def shutdown(self):
        # stop vehicle
        self.run(0)
        self.running = False


class Vehicle:
    def __init__(self):

        self.parts = []
        self.on = True
        self.threads = []

    def add(self, part, inputs=[], outputs=[],
            threaded=False, run_condition=None):
        """
        Method to add a part to the vehicle drive loop.

        Parameters
        ----------
            part: class
                donkey vehicle part has run() attribute
            inputs : list
                Channel names to get from memory.
            outputs : list
                Channel names to save to memory.
            threaded : boolean
                If a part should be run in a separate thread.
            run_condition : str
                If a part should be run or not
        """
        assert type(inputs) is list, "inputs is not a list: %r" % inputs
        assert type(outputs) is list, "outputs is not a list: %r" % outputs
        assert type(threaded) is bool, "threaded is not a boolean: %r" % threaded

        p = part
        entry = {}
        entry['part'] = p
        entry['inputs'] = inputs
        entry['outputs'] = outputs
        entry['run_condition'] = run_condition

    def remove(self, part):
        """
        remove part form list
        """
        self.parts.remove(part)

    def start(self, rate_hz=10, max_loop_count=None, verbose=False):
        """
        Start vehicle's main drive loop.

        This is the main thread of the vehicle. It starts all the new
        threads for the threaded parts then starts an infinite loop
        that runs each part and updates the memory.

        Parameters
        ----------

        rate_hz : int
            The max frequency that the drive loop should run. The actual
            frequency may be less than this if there are many blocking parts.
        max_loop_count : int
            Maximum number of loops the drive loop should execute. This is
            used for testing that all the parts of the vehicle work.
        verbose: bool
            If debug output should be printed into shell
        """

        try:

            self.on = True

            for entry in self.parts:
                if entry.get('thread'):
                    # start the update thread
                    entry.get('thread').start()


            loop_start_time = time.time()
            loop_count = 0
            while self.on:
                start_time = time.time()
                loop_count += 1

                self.update_parts()

                # stop drive loop if loop_count exceeds max_loopcount
                if max_loop_count and loop_count >= max_loop_count:
                    self.on = False
                else:
                    sleep_time = 1.0 / rate_hz - (time.time() - start_time)
                    if sleep_time > 0.0:
                        time.sleep(sleep_time)
                    if verbose and loop_count % 200 == 0:
                        print('verbose')


            loop_total_time = time.time() - loop_start_time

            return loop_count, loop_total_time

        except KeyboardInterrupt:
            pass
        except Exception as e:
            traceback.print_exc()
        finally:
            self.stop()
    
    def stop(self):        
        for entry in self.parts:
            entry['part'].shutdown()

    def update_parts(self):
        '''
        loop over all parts
        '''
        for entry in self.parts:

            run = True
            # check run condition, if it exists
            if entry.get('run_condition'):
                run_condition = entry.get('run_condition')
                run = self.mem.get([run_condition])[0]
            


def drive():
    '''
    Construct a working robotic vehicle from many parts.
    Each part runs as a job in the Vehicle loop, calling either
    it's run or run_threaded method depending on the constructor flag `threaded`.
    All parts are updated one after another at the framerate given in
    cfg.DRIVE_LOOP_HZ assuming each part finishes processing in a timely manner.
    Parts may have named outputs and inputs. The framework handles passing named outputs
    to parts requesting the same named input.
    '''

    #Initialize car
    V = Vehicle()
    
    class MyController:
        '''
        a simple controller class that outputs a constant steering and throttle.
        '''
        def run(self):
            steering = 0.0
            throttle = 0.1
            return steering, throttle

    V.add(MyController(), outputs=['angle', 'throttle'])

    #Drive train setup
    steering_controller = PCA9685(STEERING_CHANNEL, PCA9685_I2C_ADDR, busnum=PCA9685_I2C_BUSNUM)
    steering = PWMSteering(controller=steering_controller,
                                    left_pulse=STEERING_LEFT_PWM, 
                                    right_pulse=STEERING_RIGHT_PWM)
    
    throttle_controller = PCA9685(THROTTLE_CHANNEL, PCA9685_I2C_ADDR, busnum=PCA9685_I2C_BUSNUM)
    throttle = PWMThrottle(controller=throttle_controller,
                                    max_pulse=THROTTLE_FORWARD_PWM,
                                    zero_pulse=THROTTLE_STOPPED_PWM, 
                                    min_pulse=THROTTLE_REVERSE_PWM)

    V.add(steering, inputs=['angle'])
    V.add(throttle, inputs=['throttle'])
    
    #run the vehicle for 20 seconds
    V.start(rate_hz=DRIVE_LOOP_HZ, 
            max_loop_count=MAX_LOOPS)
    print('drive vars set')


if __name__ == '__main__':   
    print('running drive')
    drive()

