from PWM import steer, throttle, clear, engage
import time
from picamera import PiCamera
import numpy as np
from IR import IRread_avg
np.set_printoptions(threshold=np.inf)

#init variables and parameters
cam = PiCamera()
cam.resolution = (64,32)
cam.exposure_mode = 'off'
cam.exposure_compensation = -25
output = np.empty((64 * 32 * 3,), dtype=np.uint8)
old_pix = int
live_speed = 0
off_count = 0
dist = -1

#start the car
speed = 10

# operational loop
while True:

	# capture and process data
	cam.capture(output, 'rgb', use_video_port=True)
	#cam.start_preview()

	#save only one row of pixel data
    #use 4608 - 4800 for the 25th row from top
	row = output[4608:4800]
	#row = row.astype(np.int8)
	row = np.abs(row)

	#remove unneeded RED value
	row = row.reshape((64,3))
	#print(row)
	row = row[:,1:]

	#split into inividual pixel G and B values
	row = row.reshape((64,2))
	G, B = row[:,:-1].ravel(), row[:,1:].ravel()
	row = B
	row = row.reshape(32, 2)
	row = row[:,1].ravel()
	#print(row)
	#print(row.shape)

	i = 0
	max = 0
	pix = 0

	while i < len(row):
		if row[i] > max:
			max = row[i]
			pix = i
		i += 1

	# read distance if pix is centered
    # waiting for pix to center gaurantees distance data is valid
	if pix > 14:
		if pix < 19:
			dist = IRread_avg(0, 25)
			if dist >= 33:
				dist = 33

	# shutdown if LED is lost
	if dist != -1:
		if max <= 120:
			off_count += 1
			if off_count > 120:
				print("Car not detected...")
				clear()
				exit()
			pix = old_pix

		if max >= 60:
			off_count = 0


	#sort directional input into commands if input has changed
	if pix != old_pix:

		if pix < 15:
			deg = abs(2 * (pix - 14))
			direction = "L"
		elif pix > 16:
			deg = 2 * (pix - 17)
			direction = "R"
		else:
			direction = "R"
			deg = 0
        # Execute steering commands
		steer(direction, deg)

		old_pix = pix


    # map distance input throttle to commands
	if dist == -1:
		live_speed = 0
	if dist >= 33:
		live_speed = speed + 1
	if dist < 33:
		live_speed = speed
	if dist < 32:
		live_speed = speed - 1
	if dist < 30:
		live_speed = speed - 2
	if dist < 20:
		live_speed = speed - 3
	if dist < 15:
		live_speed = 0

    # Execute throttle control
	throttle("F", live_speed)


    # Update terminal with readings for debugging
	print "pix:", pix
	print "dist:", dist
	print "throttle:", live_speed
