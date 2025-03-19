import pygame, pygame_widgets, pymunk
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.dropdown import Dropdown
#import time
import math
from stewartPlatform import StewartPlatform
from servoMotorHandler import ServoMotorHandler

sin,cos = math.sin, math.cos
WINDOWDIMS = (1200, 600)
pygame.init()
screen = pygame.display.set_mode(WINDOWDIMS)

font = pygame.font.Font('freesansbold.ttf', 12)
clock=pygame.time.Clock()

txt = []
tb = lambda : TextBox(screen, 300, 0, 220, 20, fontSize=10)
sliders = {
	"x-axis": {
		0: Slider(screen, 60, 0, 220, 10, min=0, max=100, initial=0, step=.1), 
		1: tb(),
		2: 0
	},
	"y-axis": {
		0: Slider(screen, 60, 0, 220, 10, min=0, max=100, initial=0, step=.1), 
		1: tb(),
		2: 0
	},
	"z-axis": {
		0: Slider(screen, 60, 0, 220, 10, min=0, max=100, initial=100, step=.1), 
		1: tb(),
		2: 100
	},
	"roll": {
		0: Slider(screen, 60, 0, 220, 10, min=0, max=100, initial=50, step=.1), 
		1: tb(),
		2: 50
	},
	"pitch": {
		0: Slider(screen, 60, 0, 220, 10, min=0, max=100, initial=50, step=.1), 
		1: tb(),
		2: 50
	},
	"yaw": {
		0: Slider(screen, 60, 0, 220, 10, min=0, max=100, initial=50, step=.1), 
		1: tb(),
		2: 50
	},
}
for i, s in enumerate(sliders):
	sliders[s][1].setText(sliders[s][0].getValue())
	sliders[s][1].disable()
	sliders[s][0].moveY(10 + 30 * i)
	sliders[s][1].moveY(10 + 30 * i)
	dummy1 = font.render(s, True, (0,0,0), (255, 255,255))
	dummy2 = dummy1.get_rect()
	dummy2.midleft =  (10,15 + 30 * i)
	txt.append((dummy1, dummy2))

stewart = StewartPlatform(100, [340, 20, 100, 140, 240, 280], 100, [350, 10, 110, 130, 250, 270])
smh = ServoMotorHandler()

# sliders["x-axis"][0].setValue(20.1) # just to learn
#sliders["a"][0].disable() # just to learn

pygame.display.set_caption('Stewart Platform Game')
dropdown = Dropdown(
    screen, 700, 10, 100, 20, name='Mode',
    choices=[
        'Standby',
        'Force',
        'Control X',
        'Vertical',
        'Swing up',
    ],
    borderRadius=3, values=[0,1,2,3,4], direction='down', textHAlign='left'
)


mode = dropdown.getSelected()
run = True
while run:
	for e in pygame.event.get():
		if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key in [pygame.K_ESCAPE, ord("q")]):
			run = False
		elif e.type == pygame.KEYDOWN and e.key == ord(" "):
			dropdown.reset()
		elif e.type == pygame.MOUSEMOTION:
			for s in sliders:

				value = sliders[s][0].getValue()

				if s == "x-axis" or s == "y-axis":
					min = 0
					max = 100
				elif s == "z-axis":
					min = 70
					max = 100
				else:
					min = -20
					max = 20
				
				temp = (max - min) / 100
				temp *= value
				temp += min

				sliders[s][1].setText(temp)
				sliders[s][2] = temp
				print(s, ": ", temp)
			# [sliders[s][1].setText(sliders[s][0].getValue()) for s in sliders]
		elif e.type == pygame.MOUSEBUTTONDOWN:
			if dropdown.getSelected() != mode:
				print(mode, dropdown.getSelected())
				mode = dropdown.getSelected()
	screen.fill((255, 255, 255))
	# [screen.blit(t[0], t[1]) for t in txt]

	# print(sliders['x-axis'][0].getValue(), 
				     					# sliders['y-axis'][0].getValue(), 
										# sliders['z-axis'][0].getValue(), 
										# sliders['roll'][0].getValue(), 
										# sliders['pitch'][0].getValue(),
										# sliders['yaw'][0].getValue())
	try:
		leg_length_list = stewart.calculate(sliders['x-axis'][2], 
											sliders['y-axis'][2], 
											sliders['z-axis'][2], 
											sliders['roll'][2], 
											sliders['pitch'][2],
											sliders['yaw'][2])

		# print(leg_length_list)
		
		if leg_length_list != None:
			angle_list = stewart.getAngles(40, 100, leg_length_list)
			for index, angle in enumerate(angle_list):
				smh.setRotationAngle(index, angle)
	except:
		pass

	# x = WINDOWDIMS[0] // 2 + sliders["x-axis"][0].getValue()
	# theta = sliders["yaw"][0].getValue() / 1024 * math.pi
	
	# pygame.draw.rect(screen, (0,0,0), pygame.Rect(10,400, WINDOWDIMS[0] - 20,5))
	# pygame.draw.rect(screen, (255,0,0), pygame.Rect(x - 25, 400 - 8, 50, 16))
	# pygame.draw.line(screen, (0,255,0), [x , 400], [x + 60 * sin(theta), 400 + 60 * cos(theta)], 4)
	pygame_widgets.update(pygame.event.get())
	pygame.display.update()
	# time.sleep(.01)
	# printing compute the clock framerate
	# print(clock.get_time(), clock.get_fps())
	clock.tick(100)

pygame.quit()