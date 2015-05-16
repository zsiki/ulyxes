# based on SFE_LSM9DS0 Arduino Library
from measureunit import MeasureUnit

# LSM9DS0 Gyro Registers
WHO_AM_I_G          = 0x0F
CTRL_REG1_G         = 0x20
CTRL_REG2_G         = 0x21
CTRL_REG3_G         = 0x22
CTRL_REG4_G         = 0x23
CTRL_REG5_G         = 0x24
REFERENCE_G         = 0x25
STATUS_REG_G        = 0x27
OUT_X_L_G           = 0x28
OUT_X_H_G           = 0x29
OUT_Y_L_G           = 0x2A
OUT_Y_H_G           = 0x2B
OUT_Z_L_G           = 0x2C
OUT_Z_H_G           = 0x2D
FIFO_CTRL_REG_G     = 0x2E
FIFO_SRC_REG_G      = 0x2F
INT1_CFG_G          = 0x30
INT1_SRC_G          = 0x31
INT1_THS_XH_G       = 0x32
INT1_THS_XL_G       = 0x33
INT1_THS_YH_G       = 0x34
INT1_THS_YL_G       = 0x35
INT1_THS_ZH_G       = 0x36
INT1_THS_ZL_G       = 0x37
INT1_DURATION_G     = 0x38

# LSM9DS0 Accel/Magneto (XM) Registers 
OUT_TEMP_L_XM       = 0x05
OUT_TEMP_H_XM       = 0x06
STATUS_REG_M        = 0x07
OUT_X_L_M           = 0x08
OUT_X_H_M           = 0x09
OUT_Y_L_M           = 0x0A
OUT_Y_H_M           = 0x0B
OUT_Z_L_M           = 0x0C
OUT_Z_H_M           = 0x0D
WHO_AM_I_XM         = 0x0F
INT_CTRL_REG_M      = 0x12
INT_SRC_REG_M       = 0x13
INT_THS_L_M         = 0x14
INT_THS_H_M         = 0x15
OFFSET_X_L_M        = 0x16
OFFSET_X_H_M        = 0x17
OFFSET_Y_L_M        = 0x18
OFFSET_Y_H_M        = 0x19
OFFSET_Z_L_M        = 0x1A
OFFSET_Z_H_M        = 0x1B
REFERENCE_X         = 0x1C
REFERENCE_Y         = 0x1D
REFERENCE_Z         = 0x1E
CTRL_REG0_XM        = 0x1F
CTRL_REG1_XM        = 0x20
CTRL_REG2_XM        = 0x21
CTRL_REG3_XM        = 0x22
CTRL_REG4_XM        = 0x23
CTRL_REG5_XM        = 0x24
CTRL_REG6_XM        = 0x25
CTRL_REG7_XM        = 0x26
STATUS_REG_A        = 0x27
OUT_X_L_A           = 0x28
OUT_X_H_A           = 0x29
OUT_Y_L_A           = 0x2A
OUT_Y_H_A           = 0x2B
OUT_Z_L_A           = 0x2C
OUT_Z_H_A           = 0x2D
FIFO_CTRL_REG       = 0x2E
FIFO_SRC_REG        = 0x2F
INT_GEN_1_REG       = 0x30
INT_GEN_1_SRC       = 0x31
INT_GEN_1_THS       = 0x32
INT_GEN_1_DURATION  = 0x33
INT_GEN_2_REG       = 0x34
INT_GEN_2_SRC       = 0x35
INT_GEN_2_THS       = 0x36
INT_GEN_2_DURATION  = 0x37
CLICK_CFG           = 0x38
CLICK_SRC           = 0x39
CLICK_THS           = 0x3A
TIME_LIMIT          = 0x3B
TIME_LATENCY        = 0x3C
TIME_WINDOW         = 0x3D
ACT_THS             = 0x3E
ACT_DUR             = 0x3F

# gyro scales
G_SCALE_245DPS      = 0b00 # +/- 245 degrees per second
G_SCALE_500DPS      = 0b01 # +/- 500 dps
G_SCALE_2000DPS     = 0b10 # +/- 2000 dps

# accel scales
A_SCALE_2G          = 0b000 # +/- 2g
A_SCALE_4G          = 0b001 # +/- 4g
A_SCALE_6G          = 0b010 # +/- 6g
A_SCALE_8G          = 0b011 # +/- 8g
A_SCALE_16G         = 0b100 # +/- 16g

# mag scales
M_SCALE_2GS         = 0b00 # +/- 2Gs
M_SCALE_4GS         = 0b01 # +/- 4Gs
M_SCALE_8GS         = 0b10 # +/- 8Gs
M_SCALE_12GS        = 0b11 # +/- 12Gs

# gyro_odr defines all possible data rate/bandwidth combos of the gyro:
#                        ODR (Hz) --- Cutoff
G_ODR_95_BW_125  = 0x0 #   95         12.5
G_ODR_95_BW_25   = 0x1 #   95          25
# 0x2 and 0x3 define the same data rate and bandwidth
G_ODR_190_BW_125 = 0x4 #   190        12.5
G_ODR_190_BW_25  = 0x5 #   190         25
G_ODR_190_BW_50  = 0x6 #   190         50
G_ODR_190_BW_70  = 0x7 #   190         70
G_ODR_380_BW_20  = 0x8 #   380         20
G_ODR_380_BW_25  = 0x9 #   380         25
G_ODR_380_BW_50  = 0xA #   380         50
G_ODR_380_BW_100 = 0xB #   380         100
G_ODR_760_BW_30  = 0xC #   760         30
G_ODR_760_BW_35  = 0xD #   760         35
G_ODR_760_BW_50  = 0xE #   760         50
G_ODR_760_BW_100 = 0xF #   760         100

# accel_oder defines all possible output data rates of the accelerometer:
A_POWER_DOWN     = 0 # Power-down mode (0x0)
A_ODR_3125       = 1 # 3.125 Hz (0x1)
A_ODR_625        = 2 # 6.25 Hz (0x2)
A_ODR_125        = 3 # 12.5 Hz (0x3)
A_ODR_25         = 4 # 25 Hz (0x4)
A_ODR_50         = 5 # 50 Hz (0x5)
A_ODR_100        = 6 # 100 Hz (0x6)
A_ODR_200        = 7 # 200 Hz (0x7)
A_ODR_400        = 8 # 400 Hz (0x8)
A_ODR_800        = 9 # 800 Hz (0x9)
A_ODR_1600       = 10 # 1600 Hz (0xA)

# mag_oder defines all possible output data rates of the magnetometer:
M_ODR_3125       = 0 # 3.125 Hz (0x00)
M_ODR_625        = 1 # 6.25 Hz (0x01)
M_ODR_125        = 2 # 12.5 Hz (0x02)
M_ODR_25         = 3 # 25 Hz (0x03)
M_ODR_50         = 4 #  50 (0x04)
M_ODR_100        = 5 # 100 Hz (0x05)
    
class LSM9DS0Unit(MeasureUnit):
    """ LSM9DS0 9 DOF sensor

        :param name: name of measure unit (str), default LSM9DS0
        :param typ: type of measure unit
    """

    def __init__(self, name = 'LSM9DS0', typ = '9DOF'):
        """ Constructor
        """
        super(LSM9DS0Unit, self).__init__(name, typ)
        self.accel_scale = None
        self.accel_odr = None
        self.mag_scale = None
        self.mag_odr = None
        self.gyro_scale = None
        self.gyro_odr = None

    def WhoAmIMsg(self):
        """ get who am i reg

            :param reg: addres of who am i register
            :returns: content of who am i register
        """
        return [('readU8', WHO_AM_I_G)]

    def InitAccelMsg(self, accel_scale = A_SCALE_2G, accel_odr = A_ODR_3125):
        """ Initialize accelerometer

            :param accel_scale: measure range 2g/4g/6g/8g/16g (int), default 2g
            :param accel_odr: output data range (int), default 3.125 Hz
            :returns: initialize message of accelerometer
        """
        self.accel_scale = accel_scale
        self.accel_odr = accel_odr
        reg0 = 0    # normal, no fifo, bypass
        reg1 = 0b1000 | 0b0111 | (accel_odr << 4) # refresh after read, three axes
        reg2 = accel_scale << 3 # +/-2g, normal
        reg3 = 0 # no interrupt
        return [('write8', CTRL_REG0_XM, reg0), \
                ('write8', CTRL_REG1_XM, reg1), \
                ('write8', CTRL_REG2_XM, reg2), \
                ('write8', CTRL_REG3_XM, reg3)]

    def InitMagMsg(self, mag_scale = M_SCALE_2GS, mag_odr = M_ODR_3125):
        """ Initialize magnetometer

            :param mag_scale: 2Gs/4Gs/8Gs/12Gs (int), default 2Gs
            :param mag_odr: output data range (int), default 3.125
            :returns: initialize message of magnetometer
        """
        self.mag_scale = mag_scale
        self.mag_odr = mag_odr
        reg5 = mag_odr << 2 # no temp, lowres
        reg6 = mag_scale << 5
        reg7 = 0
        reg4 = 0 # no interrupt
        return [('write8', CTRL_REG5_XM, reg5), \
                ('write8', CTRL_REG6_XM, reg6), \
                ('write8', CTRL_REG7_XM, reg7), \
                ('write8', CTRL_REG4_XM, reg4)]

    def InitGyroMsg(self, gyro_scale =  G_SCALE_245DPS, \
                gyro_odr = G_ODR_95_BW_125):
        """ Initialize gyroscope

            :param gyro_scale: 245/500/2000dps (int), default 245 dps
            :param gyro_odr: output data range (int), default 95 Hz
            :returns: initialize message of gyroscope
        """
        self.gyro_scale = gyro_scale
        self.gyro_odr = gyro_odr
        reg1 = 0b1000 | 0b0111 | (gyro_odr << 4) # normal mode enable all axes
        reg2 = 0 # Normal mode, high cutoff frequency
        reg3 = 0
        reg4 = gyro_scale << 4
        reg5 = 0
        return [('write8', CTRL_REG1_G, reg1), \
                ('write8', CTRL_REG2_G, reg2), \
                ('write8', CTRL_REG3_G, reg3), \
                ('write8', CTRL_REG4_G, reg4), \
                ('write8', CTRL_REG5_G, reg5)]

    def GetGyroMsg(self):
        """ Read gyroscope message

            :returns: read gyro message (tuple)
        """
        #return [('readList', OUT_X_L_G, 6)]    # readList returns first byte 6 times!
        return [('readU8', OUT_X_L_G), \
                ('readU8', OUT_X_L_G + 1), \
                ('readU8', OUT_X_L_G + 2), \
                ('readU8', OUT_X_L_G + 3), \
                ('readU8', OUT_X_L_G + 4), \
                ('readU8', OUT_X_L_G + 5)]

    def GetAccelMsg(self):
        """ Read accelerometer message

            :returns: read accel message (tuple)
        """
        #return [('readList', OUT_X_L_A, 6)]    # readList returns first byte 6 times!
        return [('readU8', OUT_X_L_A), \
                ('readU8', OUT_X_L_A + 1), \
                ('readU8', OUT_X_L_A + 2), \
                ('readU8', OUT_X_L_A + 3), \
                ('readU8', OUT_X_L_A + 4), \
                ('readU8', OUT_X_L_A + 5)]

    def GetMagMsg(self):
        """ Read magnetometer message

            :returns: read mag message (tuple)
        """
        #return [('readList', OUT_X_L_M, 6)]    # readList returns first byte 6 times!
        return [('readU8', OUT_X_L_M), \
                ('readU8', OUT_X_L_M + 1), \
                ('readU8', OUT_X_L_M + 2), \
                ('readU8', OUT_X_L_M + 3), \
                ('readU8', OUT_X_L_M + 4), \
                ('readU8', OUT_X_L_M + 5)]
    
    def Result(self, msg, ans, part = 'gyro'):
        """ Process answer got from sensor

            :param msg: message sent to device
            :param ans: answer got from device
            :param part: gyro/accel answer from gyro or accel
            :returns: processed values in dict
        """
        res = {}
        if msg[0][1] == OUT_X_L_G and part == 'gyro':
            # scale gyro
            if self.gyro_scale == G_SCALE_245DPS:
                scale = 8.75
            elif self.gyro_scale == G_SCALE_500DPS:
                scale = 17.5
            else:
                scale = 70
            res['gyro_x'] = ((ans['data'][1] << 8) | ans['data'][0]) * scale
            res['gyro_y'] = ((ans['data'][3] << 8) | ans['data'][2]) * scale
            res['gyro_z'] = ((ans['data'][5] << 8) | ans['data'][4]) * scale
        elif msg[0][1] == OUT_X_L_A:
            # scale accel
            if self accel_scale == A_SCALE_2G:
                scale = 0.061
            elif self accel_scale == A_SCALE_4G:
                scale = 0.122
            elif self accel_scale == A_SCALE_6G:
                scale = 0.183
            elif self accel_scale == A_SCALE_8G:
                scale = 0.244
            else:
                scale = 0.732
            res['acc_x'] = ((ans['data'][1] << 8) | ans['data'][0]) * scale
            res['acc_y'] = ((ans['data'][3] << 8) | ans['data'][2]) * scale
            res['acc_z'] = ((ans['data'][5] << 8) | ans['data'][4]) * scale
        elif msg[0][1] == OUT_X_L_M:
            # scale mag
            if self mag_scale == M_SCALE_2GS:
                scale = 0.008
            elif self mag_scale == M_SCALE_4GS:
                scale = 0.016
            elif self mag_scale == M_SCALE_8GS:
                scale = 0.032
            else:
                scale = 0.048

            res['mag_x'] = ((ans['data'][1] << 8) | ans['data'][0]) * scale
            res['mag_y'] = ((ans['data'][3] << 8) | ans['data'][2]) * scale
            res['mag_z'] = ((ans['data'][5] << 8) | ans['data'][4]) * scale
        else:
            res = ans
        return res
