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
CORE_RADIUS = 50
dt = 0.02

# --spiral
spin_m = 0.035

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

        Dx = x - X_CENTRE
        Dy = y - Y_CENTRE
        self.spawn_r = math.sqrt(pow(Dx, 2) + pow(Dy, 2))
        self.orbit_angle = math.atan2(self.y - Y_CENTRE, self.x - X_CENTRE)
    def draw(self):
        # GETTING COLOR USING TEMPERATURE
        BV_result = IDEAL_COLOR_FORM * numpy.sqrt(KEVIN_CONVERTER/self.temperature + GRAPH_DISTORTION) - 1.16 # BALLESTEROS` FORMULA

        if BV_result < -MIN_TEMPCOLOR: BV_result = -MIN_TEMPCOLOR # SO VALUES WON`T BECOME INFINITE AND BREAK OUR ENGINE
        if BV_result > 2.0: BV_result = 2.0

        R_color, G_color, B_color = 0, 0, 0
        # ALL STAR COLORS
        if BV_result <= 0.0: # AZURE-WHITE COLOR/REALLY HIGH TEMPERATURE/SPECTRAL CLASS = O&B
            t = (BV_result + MIN_TEMPCOLOR)/MIN_TEMPCOLOR

            R_color = 255 * (0.61 + 0.11 * t + 0.28 * pow(t, 2))
            G_color = 255 * (0.70 + 0.07 * t + 0.23 * pow(t, 2))
            B_color = 255

        elif BV_result >= 0.0 and BV_result <= MIN_TEMPCOLOR: # LIGHT-YELLOW COLOR/HIGH TEMPERATURE/SPECTRAL CLASS = A&F
            t = BV_result/MIN_TEMPCOLOR

            R_color = 255 * 1.00
            G_color = 255 * 1.00
            B_color = 255 * (1.00 - 0.15 * t - 0.07 * pow(t, 2))

        elif BV_result >= MIN_TEMPCOLOR and BV_result <= 1.6: # ORANGE AND MIDDLE SIZED OBJECTS/NORMAL TEMPERATURE/SPECTRAL CLASS = G&K
            t = (BV_result - MIN_TEMPCOLOR)/1.2

            R_color = 255
            G_color = 255 * (1.00 - 0.28 * t + 0.09 * pow(t, 2))
            B_color = 255 * (0.78 - 0.69 * t + 0.21 * pow(t, 2))
        else: # RED COLORED OBJECT/LOW TEMPERATURE/SPECTRAL CLASS = M

            R_color = 255
            G_color = 100
            B_color = 0

        if self.spawn_r < 10:
            pygame.draw.circle(screen, (R_color, G_color, B_color) , (int(self.x), int(self.y)), self.radius, 0)
            return

        bar_radius = 45
        spin_m_dynamic = 0.045

        if self.spawn_r < bar_radius:
            visual_angle = self.orbit_angle
        else:
            visual_angle = self.orbit_angle + ((self.spawn_r - bar_radius) * spin_m_dynamic)

        # FROM POLAR COORDINATES(ANGLE&DISTANCE) TO CARTESIAN COORDINATES(X&Y)
        render_x = X_CENTRE + self.spawn_r * math.cos(visual_angle)
        render_y = Y_CENTRE + self.spawn_r * math.sin(visual_angle)

        # SURFACE    COLOR   COORDINATES{X,Y}     RADIUS      FILL OUT
        pygame.draw.circle(screen, (R_color, G_color, B_color) , (int(render_x), int(render_y)), self.radius, 0)

    def move(self):
        if self.spawn_r < 10: return # TO PREVENT ZERO DIVISION

        # STABLE SPEED/BLACK MATTER (THE FURTHER THE STAR IS FROM THE CENTRE, THE FASTER IT MOVES)
        v_orbital = math.sqrt((G * GALAXY_CENTRE_MASS) / (self.spawn_r + CORE_RADIUS))
        angular_velocity = v_orbital / self.spawn_r

        self.orbit_angle += angular_velocity * dt

        self.x = X_CENTRE + self.spawn_r * math.cos(self.orbit_angle)
        self.y = Y_CENTRE + self.spawn_r * math.sin(self.orbit_angle)

stars_list = []

while len(stars_list) < MAX_RENDERED_STARS:
    max_distance = min(X_CENTRE, Y_CENTRE) - 20
    random_factor = random.uniform(0, 1)

    distance = pow(random_factor, 2.0) * max_distance # HOW FAR STAR IS GENERATED FROM CENTER
    if distance < 15: distance = 15

    # SHAPE OF THE GALAXY(EQUALLY)
    #angle = random.uniform(0, 2 * numpy.pi) # IMAGINE A CIRCLE: WE ASK WHAT DIRECTION(POINT INSIDE CIRCLE) WE WILL CHOOSE.

    # SHAPE OF THE GALAXY(SPIRALLY)

    num_arms = 4  # NUMBER OF SPIRAL ARMS
    arm = random.randint(0, num_arms - 1)  # CHOOSE ARM FOR THE STAR
    arm_offset = arm * (2 * numpy.pi / num_arms)  # ARM ANGLE SHIFT

    blur = random.gauss(0, 0.12)  # Reduced from 0.18 to make arms sharper
    angle = arm_offset + blur  # FINAL INITIAL ANGLE

    # FROM POLAR COORDINATES(ANGLE&DISTANCE) TO CARTESIAN COORDINATES(X&Y)
    x = int(X_CENTRE + distance * numpy.cos(angle))
    y = int(Y_CENTRE + distance * numpy.sin(angle))

    if (x, y) in usedCoordinates:
        pass # IGNORE COORDINATE
    else:
        if total_stars >= MAX_RENDERED_STARS: break
        total_stars += 1

        pygame.display.set_caption(f'Physics Engine: Rendering stars: {total_stars}')

        temperature = random.randrange(1, 42000) # MIN TEMPERATURE: 1; MAX TEMPERATURE: 42000(not really max, this value to make things easier)
        
        light_emission = pow((temperature/5778), 5.1) # RELATIVE LUMINANCE, SUN
        
        radius = numpy.sqrt((light_emission*(3.828*pow(10, 26)))/(4*numpy.pi*(5.67*pow(10, -8))*pow(temperature, 4))/(6.975*pow(10, 8))) # STAR`S RADIUS// LIGHT EMISSION: FROM SUN TO VATTS
        # AT THIS POINT WE RENDER OUR "STARS" WITH RADIUS JUST LIKE UNIVERSE DOES. THEY`RE REALLY LARGE. FROM THIS MOMENT WE WILL DECREASE THE SIZE JUST FOR THE SAKE OF THIS ENGINE
        safe_radius = numpy.clip(radius, MIN_RADIUS, MAX_RADIUS) # SET BORDERS TO MAX RADIUS SIZE WE GOT
        total_r = abs(numpy.round(1.0 + (safe_radius - MIN_RADIUS) * 2.0 / (MAX_RADIUS - MIN_RADIUS), 1)) # NORMALIZATION FORMULA

        Dx = x - X_CENTRE
        Dy = y - Y_CENTRE
        R = numpy.sqrt(pow(Dx, 2) + pow(Dy, 2)) # DISTANCE BETWEEN CENTRE AND STAR

        #V = numpy.sqrt((G*GALAXY_CENTRE_MASS)/R) # ABSOLUTE SPEED/STAR`S TOTAL SPEED/ORBITAL SPEED FORMULA
        V = numpy.sqrt((G*GALAXY_CENTRE_MASS*R) / (pow(R, 2) + pow(R, 2))) # STABLE SPEED/BLACK MATTER (THE FURTHER THE STAR IS FROM THE CENTRE, THE FASTER IT MOVES)

        Vx = -V * (Dy / R)
        Vy = V * (Dx / R)

        star_object = Star(x, y, temperature, light_emission, total_r, Vx, Vy)
        stars_list.append(star_object)
        usedCoordinates.append((x, y)) # STORE COORDINATE

    pygame.display.set_caption(f'Physics Engine: Stars loaded: {total_stars}')

while running:
    screen.fill((10, 10, 20))
    pygame.draw.circle(screen, (255, 220, 150), (X_CENTRE, Y_CENTRE), 6)

    for star in stars_list:
        star.move()
        star.draw()

    FPS = clock.get_fps()
    
    FPS_font = pygame.font.SysFont('arial', 30)
    FPS_text = FPS_font.render(f'FPS: {FPS}', 1, (255,255,255))
    screen.blit(FPS_text, (0,0))    

    pygame.display.update()
    clock.tick(60)

    for event in pygame.event.get(): # GET ALL WINDOW INPUTS
        if event.type == pygame.QUIT: # STOP THE ENGINE
            running = False

pygame.quit()