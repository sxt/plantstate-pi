import os
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

def remap_range(value, left_min, left_max, right_min, right_max):
    # this remaps a value from original (left) range to new (right) range
    # Figure out how 'wide' each range is
    left_span = left_max - left_min
    right_span = right_max - right_min

    # Convert the left range into a 0-1 range (int)
    valueScaled = int(value - left_min) / int(left_span)

    # Convert the 0-1 range into a value in the right range.
    return int(right_min + (valueScaled * right_span))


# Assuming range 0-100:
moisture_threshold  = 50
is_dry = False

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D22)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan0 = AnalogIn(mcp, MCP.P0)

print('Raw ADC Value: ', chan0.value)
print('ADC Voltage: ' + str(chan0.voltage) + 'V')

# convert 16bit adc0 (0-65535) trim pot read into 0-100 volume level
level = remap_range(chan0.value, 0, 65535, 0, 100)

# Has the moisture level gone below the warning threshold?
if level < moisture_threshold:
   is_dry = True
   print('Plant is dry')
   # Send Message: dry
else:
   is_dry = False
   print('Plant is OK')
   # Send Message: ok

last_read = 0       # this keeps track of the last potentiometer value
tolerance = 250     # to keep from being jittery we'll only change
                    # volume when the pot has moved a significant amount
                    # on a 16-bit ADC

while True:

    # we'll assume that the pot didn't move
    trim_pot_changed = False

    # read the analog pin
    trim_pot = chan0.value

    # how much has it changed since the last read?
    pot_adjust = abs(trim_pot - last_read)

    if pot_adjust > tolerance:
        trim_pot_changed = True

    if trim_pot_changed:
        # convert 16bit adc0 (0-65535) trim pot read into 0-100 volume level
        level = remap_range(trim_pot, 0, 65535, 0, 100)

        # set OS volume playback volume

        # Has the moisture level gone below the warning threshold?
        if level < moisture_threshold:
            if is_dry is False:
               is_dry = True
               print('Plant is dry')
               # Send Message: dry
        else:
            if is_dry is True:
               is_dry = False
               print('Plant is OK')
               # Send Message: ok

        # save the potentiometer reading for the next loop
        last_read = trim_pot

    # hang out and do nothing for a half second
    time.sleep(0.5)
