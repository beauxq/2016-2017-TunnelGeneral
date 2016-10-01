import pygame,sys,os,random,math

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) #directory from which this script is ran
sys.path.insert(0, os.path.join(__location__))

#Robot: the robot itself on the board
class Robot():
	coords = None
	width = None
	def __init__(self,screen,gameboard,coords=None,offsets=None):
		self.screen = screen
		self.coords = coords
		self.GAMEBOARD = gameboard
		self.GRID_WIDTH = gameboard.GRID_WIDTH
		gameboard.ROBOT = self #add self to gameboard
		if coords == None:
			A7_coords = gameboard.get_block('A7').coords
			self.coords = (A7_coords[0]+self.GRID_WIDTH/8,A7_coords[1]+self.GRID_WIDTH/8)
		self.width = self.GRID_WIDTH*3/4
		self.color = (26,148,49)
		self.object = pygame.Rect(self.coords,(self.width,self.width))
		self.movable_rect = pygame.Rect((gameboard.PLEXI.x+self.GRID_WIDTH/8,
			gameboard.PLEXI.y+self.GRID_WIDTH/8),
			(gameboard.PLEXI.width-self.GRID_WIDTH/4,gameboard.PLEXI.height-self.GRID_WIDTH/4))
		self.direction = 0
		self.dirIndicator = pygame.Rect((self.coords), (10,10))
		self.dirIndicatorColor = (100,100,100)
		#self.errorMax = self.GRID_WIDTH/12
		self.errorMax = 0
		self.MAP = None
		if offsets == None:
			self.MAP = RobotMap(self.screen,self.GRID_WIDTH/2,(gameboard.TOTAL_WIDTH+20,20),self.direction)
		else:
			self.MAP = RobotMap(self.screen,self.GRID_WIDTH/2,offsets,self.direction)
		self.rel_coords = (self.coords[0]-self.GAMEBOARD.OFFSETS[0],self.coords[1]-self.GAMEBOARD.OFFSETS[1])
		self.last_reference = [0,0]
		self.sensors = []

	def draw(self):
		self.object.topleft = (self.GAMEBOARD.OFFSETS[0]+self.rel_coords[0],self.GAMEBOARD.OFFSETS[1]+self.rel_coords[1])
		self.movable_rect.topleft = (self.GAMEBOARD.PLEXI.x+self.GRID_WIDTH/8,
			self.GAMEBOARD.PLEXI.y+self.GRID_WIDTH/8)
		self.screen.fill(self.color,self.object)
		self.dirIndicator.center = self.object.center
		if self.direction == 0:
			self.dirIndicator.centerx += self.object.width/3
		elif self.direction == 1:
			self.dirIndicator.centery -= self.object.height/3
		elif self.direction == 2:
			self.dirIndicator.centerx -= self.object.width/3
		elif self.direction == 3:
			self.dirIndicator.centery += self.object.height/3
		self.screen.fill(self.dirIndicatorColor,self.dirIndicator)
		for sensor in self.sensors:
			sensor.draw()
		#draw map
		#self.MAP.draw()

	def handleKeyEvent(self,event):
		if event.key in [pygame.K_w,pygame.K_UP]:
			self.goForward()
		elif event.key in [pygame.K_a,pygame.K_LEFT]:
			self.rotateCounterClockwise()
		elif event.key in [pygame.K_s,pygame.K_DOWN]:
			self.goBackward()
		elif event.key in [pygame.K_d,pygame.K_RIGHT]:
			self.rotateClockwise()
		elif event.key in [pygame.K_1]:
			self.readSensor(1)
		elif event.key in [pygame.K_2]:
			self.readSensor(2)
		elif event.key in [pygame.K_3]:
			self.readSensor(3)
		elif event.key in [pygame.K_u]:
			if pygame.key.get_mods() & pygame.KMOD_SHIFT:
				self.MAP.markOT_Front()
			else:
				self.MAP.markOT()
		elif event.key in [pygame.K_i]:
			if pygame.key.get_mods() & pygame.KMOD_SHIFT:
				self.MAP.markDeadend_Front()
			else:
				self.MAP.markDeadend()
		elif event.key in [pygame.K_o]:
			if pygame.key.get_mods() & pygame.KMOD_SHIFT:
				self.MAP.markEmpty_Front()
			else:
				self.MAP.markEmpty()
		elif event.key == pygame.K_r:
			self.attemptReference()

	def readSensor(self,value):
		if value == 1:
			return self.read_distance()
		elif value == 2:
			return self.read_electromagnetic()
		elif value == 3:
			return self.read_capacitive()

	def read_distance(self):
		for sensor in self.sensors:
			if isinstance(sensor,Distance_Sensor):
				collision_list = []
				for item in self.GAMEBOARD.obstructions:
					collision_list.append(item.object)
				print sensor.read_sensor(collision_list)
	def read_electromagnetic(self):
		for sensor in self.sensors:
			if isinstance(sensor,Electromagnetic_Sensor):
				collision_list = []
				for item in self.GAMEBOARD.powerlines:
					collision_list.append(item.object)
				print sensor.read_sensor(collision_list)
	def read_capacitive(self):
		for sensor in self.sensors:
			if isinstance(sensor,Capacitive_Sensor):
				collision_list = []
				for item in self.GAMEBOARD.empty:
					collision_list.append(item.object)
				print sensor.read_sensor(collision_list)

	def performMove(self):
		pass
		#insert code here

	def goForward(self):
		self.drive(1)

	def goBackward(self):
		self.drive(-1)

	def rotateCounterClockwise(self):
		self.changeDirection(1)

	def rotateClockwise(self):
		self.changeDirection(-1)

	def changeDirection(self,val):
		self.direction = (self.direction+val)%4
		self.MAP.direction = self.direction

	def drive(self, val):
		self.MAP.drive(val)
		#error = 0
		error = round(self.errorMax*(random.random()-0.5))
		newval = ((self.GRID_WIDTH+error)*val)
		print newval
		if self.direction == 0:
			self.object.x += newval
		elif self.direction == 2:
			self.object.x -= newval
		elif self.direction == 1:
			self.object.y -= newval
		elif self.direction == 3:
			self.object.y += newval

		testObj = pygame.Rect(self.object.topleft,self.object.size)
		self.object.clamp_ip(self.movable_rect)
		#check if actually moved
		if testObj.topleft == self.object.topleft:
			self.last_reference[0] += 1
			self.last_reference[1] += 1

		self.rel_coords = (self.object.x-self.GAMEBOARD.OFFSETS[0],self.object.y-self.GAMEBOARD.OFFSETS[1])
		#check if robot is reference, and on what sides
		if self.object.topleft[0] == self.movable_rect.topleft[0] or self.object.topright[0] == self.movable_rect.topright[0]:
			self.last_reference[0] = 0
		if self.object.bottomleft[1] == self.movable_rect.bottomleft[1] or self.object.topleft[1] == self.movable_rect.topleft[1]:
			self.last_reference[1] = 0

		#check if any obstructions have been moved
		collision_list = []
		for item in self.GAMEBOARD.obstructions:
			collision_list.append(item.object)
		actual_collisions = self.object.collidelistall(collision_list)
		for col_obj in actual_collisions:
			self.GAMEBOARD.obstructions[col_obj].touched = True
			print 'OBSTRUCTION TOUCHED'

		print self.last_reference

#OT Map: Robot's internal map of the world
class RobotMap():
	rows = '1234567'
	cols = 'ABCDEFG'

	def __init__(self,screen,grid_width,offsets,direction):
		self.screen = screen
		self.GRID_WIDTH = grid_width
		self.TOTAL_WIDTH = grid_width*7
		self.TOTAL_HEIGHT = self.TOTAL_WIDTH
		self.grid = []
		self.OFFSETS = offsets
		self.generateBlocks()
		#robot representation stuff
		A7 = self.get_block('A7')
		A7.setStart()
		self.color_ROBOT = (26,148,49)
		self.robotMini = pygame.Rect((0,0),(0,0))
		self.putRobotInBlock('A7')
		self.robotLoc = [7,1]
		self.direction = direction
		self.dirIndicator = pygame.Rect((self.robotMini.topleft), (5,5))
		self.dirIndicatorColor = (100,100,100)

	def generateBlocks(self):
		for row in range(0,7):
			row_list = []
			for col in range(0,7):
				row_list.append(MapBlock(self.screen,self,(col*self.GRID_WIDTH,
					row*self.GRID_WIDTH),self.GRID_WIDTH,self.cols[col]+self.rows[row]))
			self.grid.append(row_list)

	def get_location(self,blockName):
		col = self.cols.find(blockName[0])
		row = self.rows.find(blockName[1])
		return [row,col]
	def make_location(self,coordList):
		col = self.cols[coordList[1]-1]
		row = self.rows[coordList[0]-1]
		return col+row

	def get_block(self,blockName):
		col = self.cols.find(blockName[0])
		row = self.rows.find(blockName[1])
		return self.grid[row][col]

	def putRobotInBlock(self,location):
		block = self.get_block(location)
		self.robotMini.x = block.object.x+self.GRID_WIDTH/8
		self.robotMini.y = block.object.y+self.GRID_WIDTH/8
		self.robotMini.width = self.GRID_WIDTH*3/4
		self.robotMini.height = self.GRID_WIDTH*3/4

	def markOT(self):
		self.markCurrent('OT')
	def markEmpty(self):
		self.markCurrent('E')
	def markDeadend(self):
		self.markCurrent('D')
	def markOT_Front(self):
		self.markInFront('OT')
	def markEmpty_Front(self):
		self.markInFront('E')
	def markDeadend_Front(self):
		self.markInFront('D')

	def getBlockInFront(self):
		if self.direction == 0:
			if self.robotLoc[1] < 7:
				reqLoc = (self.robotLoc[0],self.robotLoc[1]+1)
				return self.get_block(self.make_location(reqLoc))
			else:
				return None
		elif self.direction == 1:
			if self.robotLoc[0] > 1:
				reqLoc = (self.robotLoc[0]-1,self.robotLoc[1])
				return self.get_block(self.make_location(reqLoc))
			else:
				return None
		elif self.direction == 2:
			if self.robotLoc[1] > 1:
				reqLoc = (self.robotLoc[0],self.robotLoc[1]-1)
				return self.get_block(self.make_location(reqLoc))
			else:
				return None
		elif self.direction == 3:
			if self.robotLoc[0] < 7:
				reqLoc = (self.robotLoc[0]+1,self.robotLoc[1])
				return self.get_block(self.make_location(reqLoc))
			else:
				return None

	def markCurrent(self,type):
		if type == 'OT':
			self.get_block(self.make_location(self.robotLoc)).color = MapBlock.color_OT
		elif type == 'E':
			self.get_block(self.make_location(self.robotLoc)).color = MapBlock.color_EMPTY
		elif type == 'D':
			self.get_block(self.make_location(self.robotLoc)).color = MapBlock.color_DEADEND

	def markInFront(self,type):
		reqBlock = self.getBlockInFront()
		if reqBlock != None:
			if type == 'OT':
				reqBlock.color = MapBlock.color_OT
			elif type == 'E':
				reqBlock.color = MapBlock.color_EMPTY
			elif type == 'D':
				reqBlock.color = MapBlock.color_DEADEND



	def draw(self):
		#draw base board
		self.draw_blocks()
		self.draw_grid()
		self.draw_robot()

	def draw_robot(self):
		self.putRobotInBlock(self.make_location(self.robotLoc))
		self.screen.fill(self.color_ROBOT,self.robotMini)
		self.dirIndicator.center = self.robotMini.center
		if self.direction == 0:
			self.dirIndicator.centerx += self.robotMini.width/3
		elif self.direction == 1:
			self.dirIndicator.centery -= self.robotMini.height/3
		elif self.direction == 2:
			self.dirIndicator.centerx -= self.robotMini.width/3
		elif self.direction == 3:
			self.dirIndicator.centery += self.robotMini.height/3
		self.screen.fill(self.dirIndicatorColor,self.dirIndicator)

	def draw_blocks(self):
		for row in self.grid:
			for block in row:
				block.draw()

	def draw_grid(self):
		linecolor = (255,255,255)
		for n in range(0,8):
			pygame.draw.lines(self.screen,linecolor,False,[(self.OFFSETS[0]+self.GRID_WIDTH*n,self.OFFSETS[1]),
				(self.OFFSETS[0]+self.GRID_WIDTH*n,self.TOTAL_WIDTH+self.OFFSETS[1])],1)
		for n in range(0,8):
			pygame.draw.lines(self.screen,linecolor,False,[(self.OFFSETS[0],self.GRID_WIDTH*n+self.OFFSETS[1]),
				(self.OFFSETS[0]+self.TOTAL_WIDTH,self.OFFSETS[1]+self.GRID_WIDTH*n)],1)

	def drive(self,val):
		if self.direction == 0:
			newval = self.robotLoc[1]+val
			if newval >= 1 and newval <= 7:
				self.robotLoc[1] = newval
		elif self.direction == 2:
			newval = self.robotLoc[1]-val
			if newval >= 1 and newval <= 7:
				self.robotLoc[1] = newval
		elif self.direction == 1:
			newval = self.robotLoc[0]-val
			if newval >= 1 and newval <= 7:
				self.robotLoc[0] = newval
		elif self.direction == 3:
			newval = self.robotLoc[0]+val
			if newval >= 1 and newval <= 7:
				self.robotLoc[0] = newval
		#self.putRobotInBlock(self.make_location(self.robotLoc))

	def handleMouseEvent(self,event):
		pass

class MapBlock():
	color_OT = (255,0,0)
	color_DEADEND = (0,255,255)
	color_START = (255,255,0)
	color_EMPTY = (0,0,0)

	def __init__(self,screen,gameboard,coords,grid_width,grid_key):
		self.screen = screen
		self.coords = coords
		self.GAMEBOARD = gameboard
		self.GRID_WIDTH = grid_width
		self.loc = grid_key
		self.object = pygame.Rect(self.coords,(self.GRID_WIDTH,self.GRID_WIDTH))
		self.color = self.color_EMPTY

	def draw(self):
		self.object.topleft = (self.GAMEBOARD.OFFSETS[0]+self.coords[0],self.GAMEBOARD.OFFSETS[1]+self.coords[1])
		self.screen.fill(self.color,self.object)

	def setStart(self):
		self.color = self.color_START
	def setOT(self):
		self.color = self.color_OT
	def setDeadend(self):
		self.color = self.color_DEADEND
	def setEmpty(self):
		self.color = self.color_EMPTY

from Sensors import Distance_Sensor,Electromagnetic_Sensor,Capacitive_Sensor