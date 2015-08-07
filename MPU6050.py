# This program handles the communication over I2C
# between a Raspberry Pi and a MPU-6050 Gyroscope / Accelerometer combo
# Made by: MrTijn/Tijndagamer
# Copyright 2015

import smbus

class MPU6050:

    # Global Variables
    GRAVITIY_MS2 = 9.80665
    address = None
    bus = smbus.SMBus(1)

    # Scale Modifiers
    ACCEL_SCALE_MODIFIER_2G = 16384.0
    ACCEL_SCALE_MODIFIER_4G = 8192.0
    ACCEL_SCALE_MODIFIER_8G = 4096.0
    ACCEL_SCALE_MODIFIER_16G = 2048.0

    GYRO_SCALE_MODIFIER_250DEG = 131.0
    GYRO_SCALE_MODIFIER_500DEG = 65.5
    GYRO_SCALE_MODIFIER_1000DEG = 32.8
    GYRO_SCALE_MODIFIER_2000DEG = 16.4

    # Pre-defined ranges
    ACCEL_RANGE_2G = 0x00
    ACCEL_RANGE_4G = 0x08
    ACCEL_RANGE_8G = 0x10
    ACCEL_RANGE_16G = 0x18

    GYRO_RANGE_250DEG = 0x00
    GYRO_RANGE_500DEG = 0x08
    GYRO_RANGE_1000DEG = 0x10
    GYRO_RANGE_2000DEG = 0x18

    # MPU-6050 Registers
    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C
    
    ACCEL_XOUT0 = 0x3B
    ACCEL_XOUT1 = 0x3C
    ACCEL_YOUT0 = 0x3D
    ACCEL_YOUT1 = 0x3E
    ACCEL_ZOUT0 = 0x3F
    ACCEL_ZOUT1 = 0x40

    TEMP_OUT0 = 0x41
    TEMP_OUT1 = 0x42

    GYRO_XOUT0 = 0x43
    GYRO_XOUT1 = 0x44
    GYRO_YOUT0 = 0x45
    GYRO_YOUT1 = 0x46
    GYRO_ZOUT0 = 0x47
    GYRO_ZOUT1 = 0x48

    ACCEL_CONFIG = 0x1C
    GYRO_CONFIG = 0x1B

    def __init__(self, address):
        self.address = address

        # Wake up the MPU-6050 since it starts in sleep mode
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)

    # I2C communication methods

    def read_i2c_word(self, register):
        # Read the data from the registers
        high = self.bus.read_byte_data(self.address, register)
        low = self.bus.read_byte_data(self.address, register + 1)

        value = (high << 8) + low

        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value

    # MPU-6050 Methods

    # Returns the temperature in degrees celcius read from the temperature sensor in the MPU-6050
    def get_temp(self):
        # Get the raw data
        rawTemp = self.read_i2c_word(self.TEMP_OUT0)

        # Get the actual temperature using the formule given in the
        # MPU-6050 Register Map and Descriptions revision 4.2, page 30
        actualTemp = (rawTemp / 340) + 36.53

        # Return the temperature
        return actualTemp

    # Sets the range of the accelerometer to range
    def set_accel_range(self, accelRange):
        # First change it to 0x00 to make sure we write the correct value later
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, accelRange)

    # Reads the range the accelerometer is set to
    # If raw is True, it will return the raw value from the ACCEL_CONFIG register
    # If raw is False, it will return an integer: -1, 2, 4, 8 or 16. When it returns -1 something went wrong.
    def read_accel_range(self, raw = False):
        # Get the raw value
        rawData = self.bus.read_byte_data(self.address, self.ACCEL_CONFIG)

        if raw is True:
            return rawData
        elif raw is False:
            if rawData == self.ACCEL_RANGE_2G:
                return 2
            elif rawData == self.ACCEL_RANGE_4G:
                return 4
            elif rawData == self.ACCEL_RANGE_8G:
                return 8
            elif rawData == self.ACCEL_RANGE_16G:
                return 16
            else:
                return -1

    # Gets and returns the X, Y and Z values from the accelerometer
    # If g is True, it will return the data in g
    # If g is False, it will return the data in m/s^2
    def get_accel_data(self, g = False):
        # Read the data from the MPU-6050
        x = self.read_i2c_word(self.ACCEL_XOUT0)
        y = self.read_i2c_word(self.ACCEL_YOUT0)
        z = self.read_i2c_word(self.ACCEL_ZOUT0)

        accelScaleModifier = None
        accelRange = self.read_accel_range(True)

        if accelRange == self.ACCEL_RANGE_2G:
            accelScaleModifier = self.ACCEL_SCALE_MODIFIER_2G
        elif accelRange == self.ACCEL_RANGE_4G:
            accelScaleModifier = self.ACCEL_SCALE_MODIFIER_4G
        elif accelRange == self.ACCEL_RANGE_8G:
            accelScaleModifier = self.ACCEL_SCALE_MODIFIER_8G
        elif accelRange == self.ACCEL_RANGE_16G:
            accelScaleModifier = self.ACCEL_SCALE_MODIFIER_16G
        else:
            print("Unkown range - accelScaleModifier set to self.ACCEL_SCALE_MODIFIER_2G")
            accelScaleModifier = self.ACCEL_SCALE_MODIFIER_2G
        
        x = x / accelScaleModifier
        y = y / accelScaleModifier
        z = z / accelScaleModifier

        if g is True:
            return {'x': x, 'y': y, 'z': z}
        elif g is False:
            x = x * self.GRAVITIY_MS2
            y = y * self.GRAVITIY_MS2
            z = z * self.GRAVITIY_MS2
            return {'x': x, 'y': y, 'z': z}
        

    # Sets the range of the gyroscope to range
    def set_gyro_range(self, gyroRange):
        # First change it to 0x00 to make sure we write the correct value later
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, gyroRange)

    # Reads the range the gyroscope is set to
    # If raw is True, it will return the raw value from the GYRO_CONFIG register
    # If raw is False, it will return 250, 500, 1000, 2000 or -1. If the returned value is equal to -1 something went wrong.
    def read_gyro_range(self, raw = False):
        # Get the raw value
        rawData = self.bus.read_byte_data(self.address, self.GYRO_CONFIG)

        if raw is True:
            return rawData
        elif raw is False:
            if rawData == self.GYRO_RANGE_250DEG:
                return 250
            elif rawData == self.GYRO_RANGE_500DEG:
                return 500
            elif rawData == self.GYRO_RANGE_1000DEG:
                return 1000
            elif rawData == self.GYRO_RANGE_2000DEG:
                return 2000
            else:
                return -1

    # Gets and returns the X, Y and Z values from the gyroscope
    def get_gyro_data(self):
        # Read the raw data from the MPU-6050
        x = self.read_i2c_word(self.GYRO_XOUT0)
        y = self.read_i2c_word(self.GYRO_YOUT0)
        z = self.read_i2c_word(self.GYRO_ZOUT0)

        gyroScaleModifier = None
        gyroRange = self.read_gyro_range(True)
        
        if gyroRange == self.GYRO_RANGE_250DEG:
            gyroScaleModifier = self.GYRO_SCALE_MODIFIER_250DEG
        elif gyroRange == self.GYRO_RANGE_500DEG:
            gyroScaleModifier = self.GYRO_SCALE_MODIFIER_500DEG
        elif gyroRange == self.GYRO_RANGE_1000DEG:
            gyroScaleModifier = self.GYRO_SCALE_MODIFIER_1000DEG
        elif gyroRange == self.GYRO_RANGE_2000DEG:
            gyroScaleModifier = self.GYRO_SCALE_MODIFIER_2000DEG
        else:
            print("Unkown range - gyroScaleModifier set to self.GYRO_SCALE_MODIFIER_250DEG")
            gyroScaleModifier = self.GYRO_SCALE_MODIFIER_250DEG
        
        x = x / gyroScaleModifier
        y = y / gyroScaleModifier
        z = z / gyroScaleModifier

        return {'x': x, 'y': y, 'z': z}      

    # Gets and returns the X, Y and Z values from the accelerometer and from the gyroscope and the temperature from the temperature sensor
    def get_all_data(self):
        temp = get_temp()
        accel = get_accel_data()
        gyro = get_gyro_data()

        return [accel, gyro, temp]

if __name__ == "__main__":
    mpu = MPU6050(0x68)
    print(mpu.get_temp())
    accelData = mpu.get_accel_data()
    print(accelData['x'])
    print(accelData['y'])
    print(accelData['z'])
    gyroData = mpu.get_gyro_data()
    print(gyroData['x'])
    print(gyroData['y'])
    print(gyroData['z'])