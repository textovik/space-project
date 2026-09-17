# INITIALIZING LIBRARIES
import pygame
import random
import numpy

# VARIABLES
running = True # ENGINE STATE
usedCoordinates = []

MAX_X_AXIS = 860
MAX_Y_AXIS = 640
MAX_RENDERED_STARS = 2000

MIN_RADIUS = 1000
MAX_RADIUS = 125000

MIN_TEMPCOLOR = 0.4
KEVIN_CONVERTER = 4600
IDEAL_COLOR_FORM = 1/0.92
GRAPH_DISTORTION = 0.2916 # UBV TO RGB SMOOTHNESS
COOLING_DOWN_SPEED = -1.16 # FROM BLUE TO RED TRANSITION

# INITIALIZING PYGAME
pygame.init()

screen = pygame.display.set_mode((MAX_X_AXIS, MAX_Y_AXIS)) # set_mode TO CREATE A WINDOW(surface).
pygame.display.set_caption('Physics Engine')

# STARS RENDERING
class Star:
    def __init__(self, x, y, temperature, light_emission, radius):
        self.x = x
        self.y = y

        self.mass = 0 # KG
        self.radius = radius
        self.temperature = temperature # KELVIN
        self.light_emission = light_emission
    def draw(self):
        # GETTING COLOR USING TEMPERATURE
        BV_result = IDEAL_COLOR_FORM * numpy.sqrt(KEVIN_CONVERTER/self.temperature + GRAPH_DISTORTION) - 1.16 # BALLESTEROS` FORMULA

        if BV_result < -MIN_TEMPCOLOR: BV_result = -MIN_TEMPCOLOR # SO VALUES WON`T BECOME INFINITE AND BREAK OUR ENGINE
        if BV_result > 2.0: BV_result = 2.0

        R, G, B = 0, 0, 0
        # ALL STAR COLORS
        if BV_result <= 0.0: # AZURE-WHITE COLOR/REALLY HIGH TEMPERATURE/SPECTRAL CLASS = O&B
            t = (BV_result + MIN_TEMPCOLOR)/MIN_TEMPCOLOR

            m = pow((self.light_emission/1.4), 0.286)
            self.mass = m * (1.989 * pow(10, 30)) # STAR`S MASS
            #print(self.mass)

            R = 255 * (0.61 + 0.11 * t + 0.28 * pow(t, 2))
            G = 255 * (0.70 + 0.07 * t + 0.23 * pow(t, 2))
            B = 255

        elif BV_result >= 0.0 and BV_result <= MIN_TEMPCOLOR: # LIGHT-YELLOW COLOR/HIGH TEMPERATURE/SPECTRAL CLASS = A&F
            t = BV_result/MIN_TEMPCOLOR

            m = pow(self.light_emission, 0.25)
            self.mass = m * (1.989 * pow(10, 30))
            #print(self.mass)

            R = 255 * 1.00
            G = 255 * 1.00
            B = 255 * (1.00 - 0.15 * t - 0.07 * pow(t, 2))

        elif BV_result >= MIN_TEMPCOLOR and BV_result <= 1.6: # ORANGE AND MIDDLE SIZED OBJECTS/NORMAL TEMPERATURE/SPECTRAL CLASS = G&K
            t = (BV_result - MIN_TEMPCOLOR)/1.2

            m = pow(self.light_emission, 0.25)
            self.mass = m * (1.989 * pow(10, 30))
            #print(self.mass)

            R = 255
            G = 255 * (1.00 - 0.28 * t + 0.09 * pow(t, 2))
            B = 255 * (0.78 - 0.69 * t + 0.21 * pow(t, 2))
        else: # RED COLORED OBJECT/LOW TEMPERATURE/SPECTRAL CLASS = M

            m = pow((self.light_emission/0.23), 0.435)
            self.mass = m * (1.989 * pow(10, 30))
            #print(self.mass)

            R = 255
            G = 100
            B = 0

        # SURFACE    COLOR   COORDINATES{X,Y}     RADIUS      FILL OUT
        pygame.draw.circle(screen, (R, G, B), [self.x, self.y], self.radius, 0)

for star in range(1, MAX_RENDERED_STARS):

    x = random.randrange(1, MAX_X_AXIS)
    y = random.randrange(1, MAX_Y_AXIS)

    if x in usedCoordinates or y in usedCoordinates:
        pass # IGNORE COORDINATE
    else:

        temperature = random.randrange(1, 42000) # MIN TEMPERATURE: 1; MAX TEMPERATURE: 42000(not really max, this value to make things easier)
        
        light_emission = pow((temperature/5778), 5.1) # RELATIVE LUMINANCE
        
        radius = numpy.sqrt((light_emission*(3.828*pow(10, 26)))/(4*numpy.pi*(5.67*pow(10, -8))*pow(temperature, 4))/(6.975*pow(10, 8))) # STAR`S RADIUS// LIGHT EMISSION: FROM SUN TO VATTS
        # AT THIS POINT WE RENDER OUR "STARS" WITH RADIUS JUST LIKE UNIVERSE DOES. THEY`RE REALLY LARGE. FROM THIS MOMENT WE WILL DECREASE THE SIZE JUST FOR THE SAKE OF THIS ENGINE
        safe_radius = numpy.clip(radius, MIN_RADIUS, MAX_RADIUS) # SET BORDERS TO MAX RADIUS SIZE WE GOT
        total_r = abs(numpy.round(1.0 + (safe_radius - MIN_RADIUS) * 2.0 / (MAX_RADIUS - MIN_RADIUS), 1)) # NORMALIZATION FORMULA

        star = Star(x, y, temperature, light_emission, total_r)
        star.draw()
        pygame.display.update()
        usedCoordinates.extend((x, y)) # STORE COORDINATE

while running:
    for event in pygame.event.get(): # GET ALL WINDOW INPUTS

        if event.type == pygame.QUIT: # STOP THE ENGINE
            running = False