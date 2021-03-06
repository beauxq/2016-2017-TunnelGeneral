#get serial library for python-2.7.x
import os,sys,time
import serial

#get robot + robotmap for general movement + navigation
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) #directory from which this script is ran
sys.path.insert(0, os.path.join(__location__,'src/'))
#insert location from Competition Game
main_dir = os.path.realpath(os.path.join(__location__,'..'))
sys.path.insert(0, os.path.realpath(os.path.join(main_dir,'Competition Game/src')))


from ArduinoFuncs import ArduinoFuncs
from Robot_Impl import Robot_Impl
from Robot import RobotMap
from AI_JED import RobotAlg as AlgJed
from AI_17 import Robot as Alg17

#ard_serial = serial.Serial('/dev/arduino_allfunc',115200)
ard_serial = serial.Serial('/dev/ttyACM0',115200)

ard_funcs = ArduinoFuncs(ard_serial)
while not ard_funcs.isConnected():
	time.sleep(0.1)
display = ard_funcs	
#initialize Robot_Impl
direction = 0
robot_map = RobotMap(None,0,None,direction,shouldPlaySound=False)
robot_impl = Robot_Impl(ard_funcs,robot_map)

def wait_till_done(resp):
	intermediateDelay = 0.01
	while not resp.isDone:
		time.sleep(intermediateDelay)
	return resp.getResponse()

count = 0
while count < 3:
	#resp1 = command_list.pop(0)()
	resp1 = robot_impl.arduinofuncs.performTap()
	strResp = wait_till_done(resp1)
	count += 1
	print count
#time.sleep(2)
#print 'was GoPressed? %s' % wait_till_done(robot_impl.getGoButton())
#print 'was StopPressed? %s' % wait_till_done(robot_impl.getStopButton())

globalThreads = []

#initialize Robot_Impl
#direction = 0
#robot_map = RobotMap(None,0,None,None,direction,shouldPlaySound=False)
#robot_impl = Robot_Impl(motors,display,robot_map)
#alg17:
#robotAlgorithm = Alg17(robot_impl,display)
#robotAlgorithm.explore3()

#algJed:
#robotAlgorithm = AlgJed(robot_impl,display)
#robotAlgorithm.doStuff()


for thread in globalThreads:
	thread.stopThread()
