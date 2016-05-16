import pygame
import math
import random
import timeit

from time import sleep

#pygame.init()
global music_on
music_on = True
global player1
player1 = True
class color:
	"""
		color has:
			red, green, blue components
			alpha component (currently unused, but may be required later)
	"""
	def __init__(self, r = 0, g = 0, b = 0, a = 0):
		self.r = r
		self.g = g
		self.b = b
		self.a = a
	# give rgb tuple of color
	def tuple(self):
		return (self.r, self.g, self.b)
	# give rgb integer value of color
	def value(self):
		return self.r * 256 * 256 + self.g * 256 + self.b

def parameters_init():

	#pygame init parameters
	global disp_game_arena, \
		screen, \
		background, \
		virtual_battleground, \
		fps, fps_coef, \
		clock, \
		ground_fall_needed, \
		tank_list,\
		ground_fall_list
	#screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
	screen = pygame.display.set_mode((1300, 700))
	background = screen.copy()
	virtual_battleground = screen.copy()
	disp_game_arena = (screen.get_width(), screen.get_height())
	clock = pygame.time.Clock()
	fps = 60
	fps_coef = 4
	ground_fall_needed = False
	ground_fall_list = []
	tank_list = []

	# projectile parameters
	global bullet_color, g
	bullet_color = color(255, 255, 255)
	g = 9.8

	#colors
	global sky, ground, \
		black, white, \
		red, green, blue, \
		gray, \
		yellow, \
		orange, \
		dark_green, \
		light_green, \
		dark_blue, \
		light_blue, \
		terrain_color
	#sky = color(135, 206, 250)
	sky = color(0, 0, 0)
	ground = color(156, 102, 31)
	black = color(0, 0, 0)
	white = color(255, 255, 255)
	red = color(255, 0, 0)
	green = color(0, 255, 0)
	dark_green = color(34, 139, 34)
	light_green = color(50, 205, 50)
	orange = color(255, 140, 0)
	blue = color(0, 0, 255)
	dark_blue = color(16, 78, 139)
	light_blue = color(0, 245, 255)
	yellow = color(255, 255, 0)
	gray = color(128, 128, 128)
	terrain_color = color(139, 90, 0)

	# tank parameters
	global tank_scale, \
		tank_generator_lengths, \
		tank_init_coords, \
		tank_max_vel
	tank_scale = 0.45 * (disp_game_arena[0] / 1200) * (disp_game_arena[1] / 600) # disp_game_arena considered to make scaling dynamic according to screen size
	tank_generator_lengths = (40 * tank_scale, 25 * tank_scale) # half length of top surface, height of tank
	# init_coords is a set of initial coordinates with tank center as origin
	tank_init_coords = [[-tank_generator_lengths[0], 0], \
			[-2 * tank_generator_lengths[0] // 3, tank_generator_lengths[1]], \
			[2 * tank_generator_lengths[0] // 3, tank_generator_lengths[1]], \
			[tank_generator_lengths[0], 0]]
	tank_max_vel = 200
	
	#turret parameters
	global turret_generator_lengths, \
		turret_init_coords
	turret_generator_lengths = (10 * tank_scale, 2 * tank_scale, 2 * tank_scale) # muzzle length, barrel width, barrel to muzzle enlargement length
	# init_coords is a set of coordinates of turret with tank center as origin
	turret_init_coords = [[0, turret_generator_lengths[1]], \
			[0, -turret_generator_lengths[1]], \
			[5 * turret_generator_lengths[0], -turret_generator_lengths[1]], \
			[5 * turret_generator_lengths[0] + turret_generator_lengths[2], -2 * turret_generator_lengths[1]], \
			[6 * turret_generator_lengths[0] + turret_generator_lengths[2], -2 * turret_generator_lengths[1]], \
			[6 * turret_generator_lengths[0] + turret_generator_lengths[2], 2 * turret_generator_lengths[1]], \
			[5 * turret_generator_lengths[0] + turret_generator_lengths[2], 2 * turret_generator_lengths[1]], \
			[5 * turret_generator_lengths[0], turret_generator_lengths[1]]]

	global draw_list, update_list, weapons_list
	# draw_list
	draw_list = []
	# update_list
	update_list = []
	# weapons_list
	weapons_list = []
	global no_of_weapons
	no_of_weapons = len(weapons_list)

	global font_size
	font_size = 35

def compare(exp, xmin, xmax, ymin, ymax):
	common = 0
	area = 0
	##print ymin,ymax,xmin,xmax
	pixa = pygame.PixelArray(virtual_battleground)
	exp_screen = virtual_battleground.copy()
	pygame.draw.circle(exp_screen, exp.color.tuple(), (exp.x, exp.y), exp.max_radius)
	pixb = pygame.PixelArray(exp_screen)
	for x in range( xmin, xmax + 1):
		for y in range(ymin, ymax + 1):
			if(pixa[x][y]!= ground.tuple() and pixa[x][y]!= sky.tuple()):
				area += 1
				if(pixa[x][y] != pixb[x][y]):
					common += 1
	del pixa
	del pixb				
	return common, area

def fill_weapons_list():
	global weapons_list
	weapons_list = [['Big shot', bigshot], ['Minigun', minigun], ['Shotgun', shotgun]]
	global no_of_weapons
	no_of_weapons = len(weapons_list)


def add_to_both_lists(obj):
	update_list.append(obj)
	for i in range(len(draw_list)):
		if obj.draw_priority <= draw_list[i].draw_priority:
			draw_list.insert(i, obj)
			return
	draw_list.append(obj)

def add_to_ground_fall_list(interval):
	##print interval
	for i in range(interval[0], interval[1] + 1):
		if i not in ground_fall_list:
			ground_fall_list.append(i)

def remove_from_both_lists(obj):
	update_list.remove(obj)
	draw_list.remove(obj)
	
def text_objects(text, font,color): 
	text_surface = font.render(text, True, color)
	return text_surface, text_surface.get_rect()

def add_to_tank_list(obj):
	global tank_list
	tank_list.append(obj)

def draw_points():
	smallText = pygame.font.SysFont("Arial", font_size)
	# tank1
	textSurf1, textRect1 = text_objects("Points: " + str(tank_list[0].game_points), smallText,tank_list[0].body_color.tuple())
	textRect1.center =(disp_game_arena[0] // 10 , font_size)
	screen.blit(textSurf1, textRect1)
	# tank2
	textSurf2, textRect2 = text_objects("Points: " + str(tank_list[1].game_points), smallText,tank_list[1].body_color.tuple())
	textRect2.center =( (disp_game_arena[0]  *  9) // 10 , font_size)
	screen.blit(textSurf2, textRect2)

def draw_power():
	smallText = pygame.font.SysFont("Arial", font_size)
	# tank1
	textSurf1, textRect1 = text_objects("Power: " + str(tank_list[0].vel), smallText, tank_list[0].body_color.tuple())
	textRect1.center =(disp_game_arena[0] // 10 , 2 * font_size)
	screen.blit(textSurf1, textRect1)
	# tank2
	textSurf2, textRect2 = text_objects("Power: " + str(tank_list[1].vel), smallText,tank_list[1].body_color.tuple())
	textRect2.center =(disp_game_arena[0]  *  9 // 10 , 2 * font_size)
	screen.blit(textSurf2, textRect2)

def draw_turn():
	smallText = pygame.font.SysFont("Arial", font_size)
	if player1:
		textSurf1, textRect1 = text_objects(tank_list[0].weapons_list[tank_list[0].curr_weapon][0], smallText, tank_list[0].body_color.tuple())
		textRect1.center =(disp_game_arena[0] // 10 , 3 * font_size)
		screen.blit(textSurf1, textRect1)
	else:
		textSurf2, textRect2 = text_objects(tank_list[1].weapons_list[tank_list[1].curr_weapon][0], smallText,tank_list[1].body_color.tuple())
		textRect2.center =(disp_game_arena[0]  *  9 // 10 , 3 * font_size)
		screen.blit(textSurf2, textRect2)	

def draw_status():
	draw_points()
	draw_power()
	draw_turn()
	

def dist(to_tank, x2, y2):
	x1 = to_tank.x
	y1 = to_tank.y
	x = (x2 - x1) * (x2 - x1)
	y = (y2 -y1) * (y2 - y1)
	dis = math.sqrt(x + y)
	return dis

class projectile():
	def __init__(self, x, y, angle, vel, color, size, explosion_ptr):
		self.color = color
		self.vel = vel
		self.angle = angle
		if size == 0:
			size = 2 * int(turret_generator_lengths[1] * 2)
		self.size = size
		self.x = self.start_x = x
		self.y = self.start_y = y
		self.time = 0
		self.draw_priority = 2
		self.time_increment = 0.12
		self.explosion = explosion_ptr
		add_to_both_lists(self)
	
	def update_state(self):
		self.move()
	
	def move(self):
		check_frames = 20
		time_small_increment = self.time_increment / check_frames
		angle = math.radians((360 - self.angle) % 360)
		for i in range(check_frames):
			# projectile motion eqns
			self.x = int(self.start_x + self.vel * math.cos(angle) * self.time)
			self.y = int(self.start_y - (self.time * self.vel * math.sin(angle)) + (g * self.time * self.time)/2)
			# check if out of bounds
			if self.x >= disp_game_arena[0] or self.x < 0:
				remove_from_both_lists(self)
				return
			if self.y >= disp_game_arena[1]:
				self.create_explosion()
				return 				
			pixa = pygame.PixelArray(virtual_battleground)
			if self.y >= 0 and pixa[self.x][self.y] != sky.value():
				self.create_explosion()
				del pixa
				return
			del pixa
			self.time += time_small_increment

	def create_explosion(self):
		self.explosion.start(self.x, self.y)
		if music_flag:
		    pygame.mixer.music.load('Randomize20.ogg')
		    pygame.mixer.music.play(1)
		remove_from_both_lists(self)
			
	def draw(self): # remove all conditions, just draw
		##print 'proj draw'
		##print self.x, self.y ,self.time
		pygame.draw.circle(screen, self.color.tuple(), (self.x, self.y), self.size)



def bigshot(from_tank, x, y, angle, vel):
	# explosion defn(from_tank, size, color, max_points = 100):
	e = explosion(from_tank, 50, red, 300)
	# def projectile (x, y, angle, vel, color, size, explosion_ptr):
	projectile(x, y, angle, vel, orange, 4, e)

def minigun(from_tank, x, y, angle, vel):
	for i in range(150):
		if i % 5 == 0:
			# explosion defn(from_tank, size, color, max_points = 100):
			e = explosion(from_tank, 10, blue, 20)
			# def projectile (x, y, angle, vel, color, size, explosion_ptr):
			projectile(x, y, angle + 5 * (0.5 - random.random()), vel, yellow, 2, e)
		update_all()
		draw_all()
		clock.tick(60)
		
def shotgun(from_tank, x, y, angle, vel):
	for i in range(5):
		# explosion defn(from_tank, size, color, max_points = 100):
		e = explosion(from_tank, 30, green, 100)
		# def projectile (x, y, angle, vel, color, size, explosion_ptr):
		projectile(x, y, angle + 2 * (2 - i), vel, red, 4, e)

class jackhammer(projectile):
	def create_explosion(self):
		self.explosion.start(self.x, self.y)
		if self.explosion_ptr.size > 0:
			# explosion defn(from_tank, size, color, max_points = 100):
			e = explosion(self.mytank, self.size // 2, red, self.max_points // 2)
			# projectile defn(self, mytank, angle, color, explosion_ptr, radius = 0):
			projectile(self.mytank, 270, self.color, e)
			#print 'created new explosion', self.size
		remove_from_both_lists(self)

class explosion:
	def __init__(self, from_tank, size, color, max_points = 100):
		self.exp_coef = 40 #10 * size
		self.max_radius = size
		self.time = 0 #same as in case of projectile 
		self.color = color
		self.count = 0
		self.radius = 0
		self.draw_priority = 3
		self.time_increment = 0.12
		self.from_tank = from_tank
		self.max_points = max_points
	
	def start(self, x, y):
		self.x = x
		self.y = y
		add_to_both_lists(self)

	def update_state(self):
		if(self.exp_coef * self.time < 180):
			self.radius = abs(int((math.sin(math.radians(self.exp_coef * self.time))) * self.max_radius))
			pygame.draw.circle(background, sky.tuple(), (self.x, self.y), self.radius)
			self.time += self.time_increment
			##print self.radius
		else:
			"#print we reached background"
			# special case, we are drawing on background
			pygame.draw.circle(background, sky.tuple(), (self.x, self.y), self.max_radius)
			#ground_fall(self.x, self.y, self.max_radius)
			# calculate the points
			global ground_fall_needed, \
				ground_fall_list
			ground_fall_needed = True
			self.points()
			add_to_ground_fall_list([max(0, self.x - self.max_radius), min(self.x + self.max_radius, disp_game_arena[0] - 1)])
			#ground_fall_list.append([max(0, self.x - self.max_radius), min(self.x + self.max_radius, disp_game_arena[0])])
			remove_from_both_lists(self)
			return
		if(self.exp_coef * self.time >= 90):
			pygame.draw.circle(background, sky.tuple(), (self.x, self.y), self.max_radius)
	def draw(self):
		if(self.exp_coef * self.time < 180):
			pygame.draw.circle(screen, self.color.tuple(), (self.x, self.y), self.radius)
	
	def points(self):
		for mytank in tank_list:
			xcoord_list = []
			ycoord_list = []
			for i in (0,2):
				xcoord_list.append(mytank.coords[i][0])
				ycoord_list.append(mytank.coords[i][1])  
				xcoord_list.sort()
				ycoord_list.sort()
			points,area = compare(self,xcoord_list[0],xcoord_list[len(xcoord_list) - 1],ycoord_list[0], ycoord_list[len(ycoord_list) - 1])		
			points = -points * 30 // area
			if mytank == self.from_tank:
				mytank.game_points += points
			else:
				self.from_tank.game_points -= points

class turret():
	"""
		turret has:
			angle is angle at which to fire projectile
			color is color object of the turret
			coords is a set of coordinates of turret after translationa and rotation
	"""
	def __init__(self, tank, color):
		self.angle = 270
		self.color = color
		self.tank = tank
		self.rotatranslate()
	# rotate tank "self" by angle "angle" about (0, 0) # and translates the turret to tank center
	def rotatranslate(self):
		self.coords = []
		##print "turret angle ", self.angle
		angle = math.radians(self.angle)
		c = math.cos(angle)
		s = math.sin(angle)
		for a in turret_init_coords:
			x, y = 	self.tank.x + c * a[0] - s * a[1], \
					self.tank.y + s * a[0] + c * a[1]
			x, y = int(x), int(y)
			self.coords.append([x, y])
	
	def rotate(self, angle):
		self.angle += angle
	
	def draw(self):
		self.rotatranslate()
		pygame.draw.polygon(screen, self.color.tuple(), self.coords)
class tank():
	"""
		tank has:
			x and y of center of tank, which is midpoint of top surface of base
			angle is angle of tank
			vel is power/velocity with which to shoot projectile
			body_color and dome_color are color objects
			turret is turret of that tank
			coords is a set of current coordinates after translation and rotation
	"""
	def __init__(self, x, y, body_color, dome_color, turret_color):
		self.x, self.y = x, y
		self.angle = 0
		self.vel = tank_max_vel // 2
		self.body_color = body_color
		self.dome_color = dome_color
		self.rotatranslate()
		self.turret = turret(self, turret_color)
		self.draw_priority = 1
		self.game_points = 0
		add_to_tank_list(self)
		add_to_both_lists(self)
		self.weapons_list = weapons_list[:]
		self.curr_weapon = 0

	# rotate tank "self" by angle "angle" about (0, 0)
	# and translates the turret to tank center
	def rotatranslate(self):
		self.coords = []
		##print "turret angle ", self.angle
		angle = math.radians(self.angle)
		c = math.cos(angle)
		s = math.sin(angle)
		for a in tank_init_coords:
			x, y = 	self.x + c * a[0] - s * a[1], \
					self.y + s * a[0] + c * a[1]
			x, y = int(x), int(y)
			self.coords.append([x, y])
		##print self.coords
		
	def draw(self) :
		self.rotatranslate()
		# turret
		self.turret.draw()
		# dome
		pygame.draw.circle(screen, self.dome_color.tuple(), (self.x, self.y), int(3 * tank_generator_lengths[1] // 4))
		# body
		pygame.draw.polygon(screen, self.body_color.tuple(), self.coords)
		# mark center
		#pygame.draw.circle(screen, red.tuple(), (self.x, self.y), 1)

	def update_state(self):
		self.fall()
		self.rise()
		
	def change_weapon(self):
			self.curr_weapon = (self.curr_weapon + 1) % no_of_weapons
			#print weapons_list[self.curr_weapon][0]
		
	def shoot(self):
		dist = 6 * turret_generator_lengths[0] +  5 * tank_scale  
		c = math.cos(math.radians(360 - self.turret.angle))
		s = math.sin(math.radians(360 - self.turret.angle))
		x = int(self.x + c * dist)
		y = int (self.y -  s * dist)
		weapons_list[self.curr_weapon][1](self, x, y, self.turret.angle, self.vel)

	# rotate tank "self" by angle "angle" about tank center
	def rotate(self, angle, origin = None):
		##print origin, self.x, self.y
		self.angle += angle
		if origin == None: # rest will be done by rotatranslate
			return
		##print "tank angle ", self.angle
		angle = math.radians(self.angle)
		c = math.cos(angle)
		s = math.sin(angle)
		# rotate tank center about origin specified
		self.x -= origin[0]
		self.y -= origin[1]
		self.x, self.y = int(c * self.x - s * self.y), int(s * self.x + c * self.y)
		self.x += origin[0]
		self.y += origin[1]

	def initial_drop(self):
		# get both extreme leftmost and rightmost points
		curr_rot_dir = 'none' # this is current rotating direction. if it reverses, means tank is stable
		
		
		if music_flag:
			pygame.mixer.music.load('Laser_Shoot13.ogg')
			pygame.mixer.music.play(1)
		##print disp_game_arena
		while True:
			left, right = self.coords[1], self.coords[2]
			##print left, right
			pixa = pygame.PixelArray(background)
			# check which of them is in the ground
			left_stable = (pixa[left[0]][left[1]] != sky.value())
			right_stable = (pixa[right[0]][right[1]] != sky.value())
			del pixa
			# respond
			if not (left_stable or right_stable):
				self.y += 1
				curr_rot_dir = 'none'
			elif not left_stable:
				if curr_rot_dir == 'right':
					#self.y += 1
					##print 'infinity avoided'
					break
				curr_rot_dir = 'left'
				self.rotate(-1)
			elif not right_stable:
				if curr_rot_dir == 'left':
					#self.y += 1
					##print 'infinity avoided'
					break
				curr_rot_dir = 'right'
				self.rotate(1)
			else:
				break
			draw_all()
		if left[1] >= disp_game_arena[1] or right[1] >= disp_game_arena[1]:
			self.y -= 1
			self.rotatranslate()
		##print 'tank stable'

	def fall(self):
		# get both extreme leftmost and rightmost points
		curr_rot_dir = 'none' # this is current rotating direction. if it reverses, means tank is stable
		while True:
			left, right = self.coords[1], self.coords[2]
			#pygame.draw.circle(screen, red.tuple(), tuple(left), 1)
			#pygame.draw.circle(screen, red.tuple(), tuple(right), 1)
			#pygame.display.update()
			pixa = pygame.PixelArray(background)
			# check which of them is in the ground
			##print 'left and right ',
			##print left, right
			##print pixa[left[0]][left[1]], pixa[right[0]][right[1]], ground.value()
			##print left, right
			if left[1] >= disp_game_arena[1]:
				left_stable = True
			else:
				left_stable = (pixa[left[0]][left[1]] != sky.value())
			if right[1] >= disp_game_arena[1]:
				right_stable = True
			else:
				right_stable = (pixa[right[0]][right[1]] != sky.value())
			del pixa
			# respond
			if not (left_stable or right_stable):
				self.y += 1
				curr_rot_dir = 'none'
			elif not left_stable:
				if curr_rot_dir == 'right':
					self.y += 1
					##print 'infinity avoided'
					break
				curr_rot_dir = 'left'
				self.rotate(-1)
			elif not right_stable:
				if curr_rot_dir == 'left':
					self.y += 1
					##print 'infinity avoided'
					break
				curr_rot_dir = 'right'
				self.rotate(1)
			else:
				break
			self.rotatranslate()
			#pygame.display.update()
		##print 'tank stable'
		self.rotatranslate()
		
	def rise(self):
		# get both extreme leftmost and rightmost points
		curr_rot_dir = 'none' # this is current rotating direction. if it reverses, means tank is stable
		while True:
			left, right = self.coords[1], self.coords[2]
			#pygame.draw.circle(screen, red.tuple(), tuple(left), 1)
			#pygame.draw.circle(screen, red.tuple(), tuple(right), 1)
			#pygame.display.update()
			pixa = pygame.PixelArray(background)
			# check which of them is in the ground
			##print 'left and right ',
			##print left, right
			##print pixa[left[0]][left[1]], pixa[right[0]][right[1]], ground.value()
			##print left, right
			if left[1] >= disp_game_arena[1]:
				left_stable = True
			else:
				left_stable = (pixa[left[0]][left[1]] == sky.value())
			if right[1] >= disp_game_arena[1]:
				right_stable = True
			else:
				right_stable = (pixa[right[0]][right[1]] == sky.value())
			del pixa
			# respond
			if not (left_stable or right_stable):
				self.y -= 1
				curr_rot_dir = 'none'
			elif not left_stable:
				if curr_rot_dir == 'right':
					self.y -= 1
					##print 'infinity avoided'
					break
				curr_rot_dir = 'left'
				self.rotate(1)
			elif not right_stable:
				if curr_rot_dir == 'left':
					self.y -= 1
					##print 'infinity avoided'
					break
				curr_rot_dir = 'right'
				self.rotate(-1)
			else:
				break
			self.rotatranslate()
			#pygame.display.update()
		##print 'tank under stable'

	# moves self in direction, 'left' or 'right', on the terrain
	def move(self, direction):
	##print self.angle
		angle = math.radians(self.angle)
		c = math.cos(angle)
		s = math.sin(angle)
		y = 0
		if direction == 'right':
			x = 5 * tank_scale
		else:
			x = -5 * tank_scale
		x, y = int(c * x - s * y), int(s * x + c * y)
		self.x += x
		self.y -= y
		if self.x >= disp_game_arena[0] - tank_generator_lengths[0]:
			self.x = int(disp_game_arena[0] - tank_generator_lengths[0] - 1)
		elif self.x < 0 + tank_generator_lengths[0]:
			self.x = int(tank_generator_lengths[0])
		if self.y >= disp_game_arena[1] - tank_generator_lengths[1]:
			self.y = int(disp_game_arena[1] - tank_generator_lengths[1] - 1)
		elif self.y < 0 + tank_generator_lengths[1]:
			self.y = int(tank_generator_lengths[1])
		if self.x >= disp_game_arena[0] // 3 and player1:
			self.x = disp_game_arena[0] // 3
		elif self.x <= 2 * disp_game_arena[0] // 3 and not player1:
			self.x = 2 * disp_game_arena[0] // 3
		##print x, y
		self.fall()
		self.rise()
		#self.fall()
		#self.rise()
		"""we need the repition of rise and falls"""

def game_quit():
	pygame.quit()
	quit()

def game_stall():
	done = False
	while not done:
		# event handling
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				game_quit()
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				done = True
			if event.type == pygame.KEYDOWN and event.key == pygame.K_k:
				game_quit()
		clock.tick(fps)

def generate_fourier_terrain():
	# terrain generator parameters
	x_start = 0
	block_width = block_height = 1
	time_to_draw_terrain = 5.0 # seconds to take to draw full terrain
	terrain_fps = ((disp_game_arena[0] / block_height) / time_to_draw_terrain)

	#fourier parameters
	max_amp = 0.15 * disp_game_arena[1]
	max_freq = 1.0 # checked by trials, modify with caution
	max_fourier_count = 5 # checked by trials, modify with caution
	terrain_gen_time_increment = math.radians(180.0 / (disp_game_arena[0] / block_width))  # checked by trials, modify with caution
	amps = []
	freqs = []
	phases = []
	for i in range(max_fourier_count):
		amps.append(max_amp / pow(2, i))
		freqs.append(max_freq * pow(2, i))
		phases.append(math.radians(360 * random.random()))
	if phases[0] > math.radians(180):
		phases[0] = math.radians(180)
		y_start = 4 * disp_game_arena[1] // 5
	else:
		phases[0] = 0
		y_start = 2 * disp_game_arena[1] // 3

	# generating terrain
	points = []
	time = 0
	x = x_start
	done = False
	global background
	background = screen.copy()
	while x < disp_game_arena[0] and not done:
		# event handling
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				game_quit()
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				done = True
		y = y_start
		# graphics
		for i in range(max_fourier_count):
			y += amps[i] * math.sin(time * freqs[i] + phases[i])
		y = int(y)
		##print time * freqs[0]
		pygame.draw.rect(screen, red.tuple(), pygame.Rect(x, y, block_width, block_height * 8)) #disp_game_arena[1])
		pygame.draw.rect(background, ground.tuple(), pygame.Rect(x, y, block_width, disp_game_arena[1]))
		x += block_width
		pygame.display.update()
		clock.tick(terrain_fps)
		time += terrain_gen_time_increment

"""
	draw_list will be a list of all objects to be drawn onto the screen
	each object must have a draw() method
	each object's init() will add the object to drawlist
	each class (tank, projectile, explosion) must be given a draw priority
	draw priority corresponds to a z index, highest priority object drawn on top of all others
	example priorites:
		tank = 1
		projectile = 2
		explosion = 3 (to prevent drawing overlap color problems, keep color of all explosions of one weapon as a single color)
"""
def draw_all():
	##print "before blit"
	screen.blit(background, (0, 0, disp_game_arena[0], disp_game_arena[1]))
	##print "after blit"
	global virtual_battleground			
	for item in draw_list:
		item.draw()
		if item.draw_priority == 1:
			virtual_battleground = screen.copy()
	draw_status()		
	pygame.display.update()

def update_all():
	ground_fall()
##print "groundfall done"
	for item in update_list:
		item.update_state()

def ground_fall():
	remove_interval = []
	pixa = pygame.PixelArray(background)
	for x in ground_fall_list:
		remove_x = True
		y = 2 * font_size + 1
		while True:
			while(y < disp_game_arena[1] and pixa[x][y] == sky.value()): #skips sky particles
				y += 1
			if (y >= disp_game_arena[1]):
				break
			first_ground_y = y
			while(y < disp_game_arena[1] and pixa[x][y] != sky.value()): #skips all non-sky particles
				y += 1
			if(y >= disp_game_arena[1]):
				break
			first_sky_y = y
			y += 1
			pixa[x][first_ground_y], pixa[x][first_sky_y] = sky.value(), ground.value()
			remove_x = False
		if remove_x:
			remove_interval.append(x)
	del pixa
	for x in remove_interval:
		ground_fall_list.remove(x)

def compute_angle_vel(computer_tank, human_tank):
	##print 'entered compute'
	computer_tank.curr_weapon = int(no_of_weapons * random.random())
	x = human_tank.x - computer_tank.x
	y = human_tank.y - computer_tank.y
	while True:
		angle = random.randint(225, 270)
		##print angle, x, y
		theta = math.radians(angle)
		vel_square = ((x ** 2) * g) / (-x * math.sin(2 * theta) - 2 * y * (math.cos(theta) ** 2))
		##print theta, vel_square
		if vel_square < 0:
			continue
		vel = int(math.sqrt(vel_square))
		if vel > tank_max_vel:
			continue
		break
	return angle, vel

global count
count = 0
global start_time,end_time 
start_time = end_time = 0
#prev_key:1 corresponds to up , 0 corresponds to down
global prev_key,prev_tank   #means no previous and no current
prev_key = 2
prev_tank = 2#means no previous and no current
#prev_tank:1 tank2 , 0 tank1 
global turn #
turn = 30#
def real_game(mode, music_on, computer_on):
	global turn#
	global disp_game_arena
	disp_game_arena = (screen.get_width(), screen.get_height())	
	global music_flag
	global count
	global prev_key,prev_tank
	global start_time,end_time
	timeinc = 112
	count_inc = 5
	count_wait = 2 * count_inc
	count_pause = 6
	music_flag = music_on
	#print music_flag
	player_wait = False
	screen.fill(sky.tuple())
	pygame.display.update()
	generate_fourier_terrain()
	fill_weapons_list()
	#pygame.draw.polygon(screen, ground.tuple(), ((0, disp_game_arena[1]), (0, disp_game_arena[1] * 1 // 3), (disp_game_arena[0], disp_game_arena[1] * 3 // 4), (disp_game_arena[0], disp_game_arena[1])))
	#background = screen.copy()
	#tank1 = tank(disp_game_arena[0] // 2, disp_game_arena[1] // 5, white.tuple(), gray.tuple(), red.tuple())
	tank1 = tank(random.randint(disp_game_arena[0] // 10, disp_game_arena[0] * 2 // 10), 4 * font_size, light_blue, dark_blue, gray)
	tank2 = tank(random.randint(disp_game_arena[0] * 8 // 10, disp_game_arena[0] * 9 // 10), 4 * font_size, dark_green, light_green, gray)
	draw_all()

	tank1.initial_drop()
	tank2.initial_drop()
	done = False
	global player1
	player1 = True
	# main code starts here
	while not done and turn != 0:
		if len(update_list) > 2:
			player_wait = True
			update_all()
			draw_all()
			clock.tick(60)
			continue
		elif player_wait:    
			player_wait  =False
		if computer_on and not player1:
			tank2.turret.angle, tank2.vel = compute_angle_vel(tank_list[1], tank_list[0])
			tank2.shoot()
			player1 ^= True
		# event handling
		for event in pygame.event.get():
			#space = 0
			if event.type == pygame.QUIT:
				done = True
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				done = True
			if event.type == pygame.KEYDOWN and event.key == pygame.K_k:
				#game_quit()
				return
			if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
				if player1:
					tank1.change_weapon()
				else:
					tank2.change_weapon()
			if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				pygame.event.clear()
				if player1:
					tank1.shoot()
				else:
					tank2.shoot()
				if music_flag:
					pygame.mixer.music.load('Laser_Shoot13.ogg')
					pygame.mixer.music.play(1)
				player1 ^= True
				
		# key input
		arrow_keys = pygame.key.get_pressed()  # checking pressed keys
		if arrow_keys[pygame.K_a]:
			##print 'left'
			if player1:
				tank1.move('left')
			else:
				tank2.move('left')
		if arrow_keys[pygame.K_d]:
			##print 'right'
			if player1:
				tank1.move('right')
			else:
				tank2.move('right')
		if arrow_keys[pygame.K_UP]:
			if player1:
				if tank1.vel < tank_max_vel: # max tank power
					if(prev_key == 2 and prev_tank ==2):
						count = 0
						start_time = timeit.default_timer()
					if(prev_key == 0): 
						count = 0
						start_time = timeit.default_timer()
					if(prev_key == 1):
						if(prev_tank == 0):
							count += 1
						else: 
							count = 0
							start_time = timeit.default_timer()
					if(count == count_inc):
						tank1.vel += 1
						##print tank1.vel,count
					if(count > count_wait):
						end_time = timeit.default_timer()
						#print ((end_time - start_time) * 1000)
						if((end_time - start_time) * 1000  < timeinc):
							if(tank1.vel + count_pause > 100):
								tank1.vel = 100
							else:
								tank1.vel += count_pause
						else:
							tank1.vel += 1
						##print tank1.vel,count
						count = 0
						end_time = 0
					prev_key = 1
					prev_tank = 0
					##print count,count_inc
			else:
				if tank2.vel < tank_max_vel:
					if(prev_key == 2 and prev_tank ==2):
						count = 0
						start_time = timeit.default_timer()
					if(prev_key == 0):
						count = 0
						start_time = timeit.default_timer()
					if(prev_key == 1):
						if(prev_tank == 1):
							count += 1
						else:
							count = 0
							start_time = timeit.default_timer()
					if(count == count_inc):
						tank2.vel += 1
						##print tank2.vel,count
					if(count > count_wait):
						end_time = timeit.default_timer()
						#print ((start_time - end_time) * 1000000)
						if((end_time - start_time) * 1000 < timeinc):
							if(tank2.vel + count_pause > 100):
								tank2.vel = 100
							else:
								tank2.vel += count_pause 
							##print ((start_time - end_time) * 1000000)
						else:
							tank2.vel += 1
						#print tank2.vel,count
						count = 0
						end_time = 0
					prev_key = 1
					prev_tank = 1
					##print count
								
		if arrow_keys[pygame.K_DOWN]:
			if player1:
				if tank1.vel > 0: # max tank power
					if(prev_key == 2 and prev_tank ==2):
						count = 0
						start_time = timeit.default_timer()
					if(prev_key == 1):
						count = 0
						start_time = timeit.default_timer()
					if(prev_key == 0):
						if(prev_tank == 0):
							count += 1
						else:
							count = 0
							start_time = timeit.default_timer()
					if(count == count_inc):
						tank1.vel -= 1
						#print tank1.vel,count
					if(count > count_wait):
						end_time = timeit.default_timer()
						if((end_time - start_time) * 1000 < timeinc):
							if(tank1.vel - count_pause < 0):
								tank1.vel  = 0
							else:
								tank1.vel -= count_pause
						else:
							tank1.vel -= 1
						#print tank1.vel,count
						count = 0
						end_time = 0
					prev_key = 0
					prev_tank = 0
					##print count,count_inc
			else:
				if tank2.vel > 0:
					if(prev_key == 2 and prev_tank ==2):
						count = 0
						start_time = timeit.default_timer()
					if(prev_key == 1):
						count = 0
						start_time = timeit.default_timer()
					if(prev_key == 0):
						if(prev_tank == 1):
							count +=1
						else:
							count = 0
							start_time = timeit.default_timer()
					if(count == count_inc):
						tank2.vel -= 1
						#print tank2.vel,count
					if(count > count_wait):
						end_time = timeit.default_timer()
						if((end_time - start_time) * 1000  < timeinc):
							if(tank2.vel - count_pause < 0):
								tank2.vel = 0
							else:
								tank2.vel -= count_pause
						else:
							tank2.vel -= 1
						#print tank2.vel,count
						count = 0
						end_time = 0
					prev_key = 0 
					prev_tank = 1
					##print count,count_inc
		if arrow_keys[pygame.K_LEFT]:
			if player1:
				tank1.turret.rotate(-1)
			else:
				tank2.turret.rotate(-1)
		if arrow_keys[pygame.K_RIGHT]:
			if player1:
				tank1.turret.rotate(1)
			else:
				tank2.turret.rotate(1)

		# draw
		update_all()
		draw_all()
		clock.tick(60)
	
	smallText = pygame.font.SysFont("Arial", 60)
	#print tank1.game_points, tank2.game_points
	if (tank1.game_points > tank2.game_points):
		textSurf1, textRect1 = text_objects("PLAYER ONE WINS", smallText, (188,238,104))
		textRect1.center =(disp_game_arena[0] // 2 , disp_game_arena[1] // 3)
		screen.blit(textSurf1, textRect1)	
	elif(tank1.game_points < tank2.game_points):
		textSurf1, textRect1 = text_objects("PLAYER TWO WINS", smallText, (188,238,104))
		textRect1.center =(disp_game_arena[0] // 2 , disp_game_arena[1] // 3)
		screen.blit(textSurf1, textRect1)	
	else:
		textSurf1, textRect1 = text_objects("DRAW", smallText, (188,238,104))
		textRect1.center =(disp_game_arena[0] // 2 , disp_game_arena[1] // 3)
		screen.blit(textSurf1, textRect1)
	pygame.display.update()
	sleep(3)
	game_quit()

#real_game()
