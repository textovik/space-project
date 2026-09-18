# INITIALIZING LIBRARIES
import pygame
import random
import numpy
import math

# VARIABLES
running = True # ENGINE STATE
usedCoordinates = []

# --project settings
MAX_X_AXIS = 860
MAX_Y_AXIS = 640
MAX_RENDERED_STARS = 2000

X_CENTRE = MAX_X_AXIS // 2
Y_CENTRE = MAX_Y_AXIS // 2

MIN_RADIUS = 1000
MAX_RADIUS = 125000

G = 1
MIN_TEMPCOLOR = 0.4
KEVIN_CONVERTER = 4600
IDEAL_COLOR_FORM = 1/0.92
GRAPH_DISTORTION = 0.2916 # UBV TO RGB SMOOTHNESS
COOLING_DOWN_SPEED = -1.16 # FROM BLUE TO RED TRANSITION

GALAXY_CENTRE_MASS = 12000
dt = 0.05

# --states
total_stars = 0

# INITIALIZING PYGAME
pygame.init()

screen = pygame.display.set_mode((MAX_X_AXIS, MAX_Y_AXIS)) # set_mode TO CREATE A WINDOW(surface).
pygame.display.set_caption('Physics Engine: loading...')
clock = pygame.time.Clock()

# STARS RENDERING
class Star:
    def __init__(self, x, y, temperature, light_emission, radius, SpeedX, SpeedY):
        self.x = float(x)
        self.y = float(y)

        self.star = None
        self.mass = 0 # KG
        self.radius = radius
        self.SpeedX = float(SpeedX)
        self.SpeedY = float(SpeedY)
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
        self.star = pygame.draw.circle(screen, (R, G, B) , (self.x, self.y), self.radius, 0)

    def move(self):
        Dx = self.x - X_CENTRE
        Dy = self.y - Y_CENTRE
        R = math.sqrt(pow(Dx, 2) + pow(Dy, 2))

        if R < 10: return # TO PREVENT ZERO DIVISION

        a = (G * GALAXY_CENTRE_MASS) / (pow(R, 2))

        aX = -a * (Dx / R)
        aY = -a * (Dy / R)

        self.SpeedX = self.SpeedX + aX * dt
        self.SpeedY = self.SpeedY + aY * dt

        self.x = self.x + self.SpeedX * dt
        self.y = self.y + self.SpeedY * dt

stars_list = []

while len(stars_list) < MAX_RENDERED_STARS:
    angle = random.uniform(0, 2 * numpy.pi) # IMAGINE A CIRCLE: WE ASK WHAT DIRECTION(POINT INSIDE CIRCLE) WE WILL CHOOSE.
    distance = random.uniform(40, min(X_CENTRE, Y_CENTRE) - 20) # HOW FAR STAR IS GENERATED FROM CENTER

    # FROM POLAR COORDINATES(ANGLE&DISTANCE) TO CARTESIAN COORDINATES(X&Y&Z)
    x = int(X_CENTRE + distance * numpy.cos(angle))
    y = int(Y_CENTRE + distance * numpy.sin(angle))

    if (x, y) in usedCoordinates:
        pass # IGNORE COORDINATE
    else:
        if total_stars >= MAX_RENDERED_STARS: break
        total_stars += 1

        pygame.display.set_caption(f'Physics Engine: Rendered stars: {total_stars}')

        temperature = random.randrange(1, 42000) # MIN TEMPERATURE: 1; MAX TEMPERATURE: 42000(not really max, this value to make things easier)
        
        light_emission = pow((temperature/5778), 5.1) # RELATIVE LUMINANCE, SUN
        
        radius = numpy.sqrt((light_emission*(3.828*pow(10, 26)))/(4*numpy.pi*(5.67*pow(10, -8))*pow(temperature, 4))/(6.975*pow(10, 8))) # STAR`S RADIUS// LIGHT EMISSION: FROM SUN TO VATTS
        # AT THIS POINT WE RENDER OUR "STARS" WITH RADIUS JUST LIKE UNIVERSE DOES. THEY`RE REALLY LARGE. FROM THIS MOMENT WE WILL DECREASE THE SIZE JUST FOR THE SAKE OF THIS ENGINE
        safe_radius = numpy.clip(radius, MIN_RADIUS, MAX_RADIUS) # SET BORDERS TO MAX RADIUS SIZE WE GOT
        total_r = abs(numpy.round(1.0 + (safe_radius - MIN_RADIUS) * 2.0 / (MAX_RADIUS - MIN_RADIUS), 1)) # NORMALIZATION FORMULA

        Dx = x - X_CENTRE
        Dy = y - Y_CENTRE
        R = numpy.sqrt(pow(Dx, 2) + pow(Dy, 2)) # DISTANCE BETWEEN CENTRE AND STAR

        V = numpy.sqrt((G*GALAXY_CENTRE_MASS)/R) # ABSOLUTE SPEED/STAR`S TOTAL SPEED/ORBITAL SPEED FORMULA

        Vx = -V * (Dy / R)
        Vy = V * (Dx / R)

        star_object = Star(x, y, temperature, light_emission, total_r, Vx, Vy)
        stars_list.append(star_object)
        usedCoordinates.append((x, y)) # STORE COORDINATE

while running:
    screen.fill((10, 10, 20))
    pygame.draw.circle(screen, (255, 220, 150), (X_CENTRE, Y_CENTRE), 6)

    for star in stars_list:
        star.move()
        star.draw()

    pygame.display.update()
    clock.tick(60)

    for event in pygame.event.get(): # GET ALL WINDOW INPUTS
        if event.type == pygame.QUIT: # STOP THE ENGINE
            running = False

pygame.quit()
