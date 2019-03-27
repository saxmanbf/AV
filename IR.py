import time, math
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import numpy as np

CLK = 18
MISO = 23
MOSI = 24
CS = 25

GPIO.setmode(GPIO.BCM)
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

count = 0


def IRread_avg(channel, cycles):

	i = 0
	sample = np.empty(cycles,)

	while i < cycles:
		v = (mcp.read_adc(channel)/1023.0) * 3.3
		dist = (16.2537 * v**4) - (129.893 * v**3) + (382.268 * v**2) - (512.611 * v) + 301.43
		sample[i] = dist
		i += 1

	dist = np.median(sample)
	return math.floor(dist)

if __name__ == "__main__":
	while True:
		print(IRread_avg(0, 50))
