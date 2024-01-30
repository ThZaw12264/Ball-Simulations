import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Define constants
SCREEN_WIDTH = 135                  # 810
SCREEN_HEIGHT = 1296                # 1296
NUM_BALLS = 1                       # 11
BALL_RADIUS = 25                    # 25
WALL_WIDTH = 5                      # 5
WALL_HEIGHT = 250                   # 250
NUM_SLOTS = 2                       # 12
SLOT_WIDTH = 67.5                   # 67.5
SLOT_HEIGHT = WALL_HEIGHT // 2      # WALL_HEIGHT // 2
NUM_LAYERS = 8                      # 8
PINS_PER_LAYER = 2                  # 6
PIN_RADIUS = 5                      # 5
PIN_SPACING_Y = 80                  # 80
PIN_SPACING_X = 70                 # 120
HORIZONTAL_OFFSET = 35              # 40
VERTICAL_OFFSET = 60                # 60
PIN_MOD = 1                         # 0

if NUM_BALLS == 1:
    # Maybe implement no pins and fast x velocity instead
    SCREEN_WIDTH = 135
    NUM_SLOTS = 2
    NUM_LAYERS = 7
    PINS_PER_LAYER = 1
    PIN_SPACING_Y = 100

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255,0,0)
ORANGE = (255,128,0)
YELLOW = (255,255,0)
LIME = (128,255,0)
GREEN = (0,255,0)
SEAGREEN = (0,255,128)
CYAN = (0,255,255)
SKYBLUE = (0,128,255)
BLUE = (0,0,255)
PURPLE = (128,0,255)
MAGENTA = (255,0,255)
PINK = (255,0,128)

# Sounds
pygame.mixer.set_num_channels(200)
a_note = pygame.mixer.Sound("sounds/A_BELL.wav")
c_note = pygame.mixer.Sound("sounds/C_BELL.wav")
c_sharp_note = pygame.mixer.Sound("sounds/C#_BELL.wav")
d_note = pygame.mixer.Sound("sounds/D_BELL.wav")
e_note = pygame.mixer.Sound("sounds/E_BELL.wav")
f_note = pygame.mixer.Sound("sounds/F_BELL.wav")
score = [f_note, d_note, a_note, d_note, 
         f_note, d_note, a_note, d_note, 
         f_note, c_note, a_note, c_note, 
         f_note, c_note, a_note, c_note, 
         e_note, c_sharp_note, a_note, c_sharp_note, 
         e_note, c_sharp_note, a_note, c_sharp_note, 
         e_note, c_sharp_note, a_note, c_sharp_note, 
         e_note, c_sharp_note, a_note, c_sharp_note]
score_pointer = 0

# Define classes
class Ball(pygame.sprite.Sprite):
    def __init__(self, x=None, y=None):
        super().__init__()
        self.radius = BALL_RADIUS
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.color_change_speed = 0.05
        self.color = self.get_rainbow_color()
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        if x is None:
            x = random.uniform(0, SCREEN_WIDTH - 2 * BALL_RADIUS)
        if y is None:
            y = 10
        self.real_x = x
        self.real_y = y
        self.prev_x = x  # Store previous x coordinate
        self.prev_y = y  # Store previous y coordinate
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity = [random.uniform(-5, 5), random.uniform(-3, 1)]  # Initial velocity
        self.gravity = 0.35  # Gravity strength
        self.in_slot = False
        self.started = False

    def get_rainbow_color(self):
        # Function to get a rainbow color based on time
        color = pygame.Color(0)
        color.hsva = (int(pygame.time.get_ticks() * self.color_change_speed) % 360, 100, 100, 100)
        return color

    def update(self):
        if self.started:
            # Update velocity with gravity
            self.velocity[1] += self.gravity

            # Update position with velocity
            self.prev_x = self.real_x  # Store previous x coordinate before updating
            self.prev_y = self.real_y  # Store previous y coordinate before updating
            self.real_x += self.velocity[0]
            self.real_y += self.velocity[1]
            self.rect.x = self.real_x
            self.rect.y = self.real_y

        # Update color
        self.color = self.get_rainbow_color()
        self.image.fill((0, 0, 0, 0))  # Clear the surface
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)

class Pin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.radius = PIN_RADIUS
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(x, y))


class Slot(pygame.sprite.Sprite):
    def __init__(self, x, y, points, color):
        super().__init__()
        self.image = pygame.Surface((SLOT_WIDTH, SLOT_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.points = points

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft=(x, y))

class Floor(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft=(x, y))


# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Plinko Simulation")

# Create groups for sprites
all_sprites = pygame.sprite.Group()
balls = pygame.sprite.Group()
pins = pygame.sprite.Group()
slots = pygame.sprite.Group()
walls = pygame.sprite.Group()
floors = pygame.sprite.Group()

# Create pins (one less pin for even layers)
for layer in range(NUM_LAYERS):
    if PIN_MOD == 0:
        for i in range(PINS_PER_LAYER):
            pin = Pin(i * PIN_SPACING_X + SLOT_WIDTH // 2 + (layer % 2) * (PIN_SPACING_X // 2) + HORIZONTAL_OFFSET,
                    (layer + 1) * PIN_SPACING_Y + VERTICAL_OFFSET)
            pins.add(pin)
            all_sprites.add(pin)
    elif PIN_MOD == 1:
        num_pins = PINS_PER_LAYER - (layer % 2)  # Decrease by one for even layers
        for i in range(num_pins):
            pin = Pin(i * PIN_SPACING_X + SLOT_WIDTH // 2 + (layer % 2) * (PIN_SPACING_X // 2) + HORIZONTAL_OFFSET,
                    (layer + 1) * PIN_SPACING_Y + VERTICAL_OFFSET)
            pins.add(pin)
            all_sprites.add(pin)

# Create slots
# slot_colors = [RED, ORANGE, YELLOW, LIME, GREEN, SEAGREEN, CYAN, SKYBLUE, BLUE, PURPLE, MAGENTA, PINK]
slot_colors = [RED, RED, RED, RED, RED, RED, RED, RED, RED, RED, RED, RED]
slot_points = [random.randint(1, 10) for _ in range(NUM_SLOTS)]
for i, points in enumerate(slot_points):
    # slot = Slot(i * SLOT_WIDTH, SCREEN_HEIGHT - SLOT_HEIGHT, points, slot_colors[i])
    slot = Slot(i * SLOT_WIDTH, SCREEN_HEIGHT - (WALL_HEIGHT // 2), points, slot_colors[i])
    slots.add(slot)
    all_sprites.add(slot)

# Create walls between slots
left_wall = Wall(0, 0, WALL_WIDTH, SCREEN_HEIGHT)
right_wall = Wall(SCREEN_WIDTH - WALL_WIDTH, 0, WALL_WIDTH, SCREEN_HEIGHT)
walls.add(left_wall, right_wall)
all_sprites.add(left_wall, right_wall)
for i in range(NUM_SLOTS - 1):
    wall = Wall((i + 1) * SLOT_WIDTH - WALL_WIDTH // 2, SCREEN_HEIGHT - WALL_HEIGHT, WALL_WIDTH, WALL_HEIGHT)
    walls.add(wall)
    all_sprites.add(wall)

# Create floors
top_floor = Floor(0, 0, SCREEN_WIDTH, WALL_WIDTH)
bottom_floor = Floor(0, SCREEN_HEIGHT - WALL_WIDTH, SCREEN_WIDTH, WALL_WIDTH)
floors.add(top_floor, bottom_floor)
all_sprites.add(top_floor, bottom_floor)


# Define functions
def play_sound():
    global score_pointer
    score[score_pointer].play()
    score_pointer += 1
    if score_pointer == len(score):
        score_pointer = 0

def initialize_balls():
    global balls
    gap = SCREEN_WIDTH // (NUM_BALLS + 1)  # Gap between each ball
    iballs_list = []

    for i in range(NUM_BALLS):
        x = (i + 1) * gap - BALL_RADIUS  # Place the ball at the center of the gap
        y = 10
        new_ball = Ball(x, y)
        iballs_list.append(new_ball)
        balls.add(new_ball)
        all_sprites.add(new_ball)

    return iballs_list


# Create balls
# initial_ball = Ball()
# balls.add(initial_ball)
# all_sprites.add(initial_ball)
        
# Main loop
FPS = 60
frame_count = 0
clock = pygame.time.Clock()
iballs_list = initialize_balls()
spacebar = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            new_ball = Ball()
            balls.add(new_ball)
            all_sprites.add(new_ball)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            spacebar = True

    # Start balls
    if iballs_list and spacebar:
        if frame_count % 120 == 0:
            start_ball = random.choice(iballs_list)
            start_ball.started = True
            iballs_list.remove(start_ball)        

    # Update
    all_sprites.update()

    # Check for collisions with pins
    for ball in balls:
        pins_hit = pygame.sprite.spritecollide(ball, pins, False)
        for pin in pins_hit:
            # Bounce off the pin
            angle = math.atan2(ball.rect.centery - pin.rect.centery, ball.rect.centerx - pin.rect.centerx)
            speed = math.sqrt(ball.velocity[0]**2 + ball.velocity[1]**2)
            damping_factor = max(0.5, 1 / speed)  # Damping factor based on the inverse of the speed
            ball.velocity[0] = speed * math.cos(angle) * damping_factor
            ball.velocity[1] = speed * math.sin(angle) * damping_factor
            ball.velocity[0] = max(ball.velocity[0], 1) if ball.velocity[0] > 0 else min(ball.velocity[0], -1)
            ball.velocity[1] = max(ball.velocity[1], 1) if ball.velocity[1] > 0 else min(ball.velocity[1], -1)
            ball.real_x = ball.prev_x
            ball.real_y = ball.prev_y
            play_sound()

        # Check for collisions with walls
        walls_hit = pygame.sprite.spritecollide(ball, walls, False)
        for wall in walls_hit:
            if ball.rect.bottom < wall.rect.top + 20:
                # Ball hits the top of the wall
                angle = math.atan2(ball.rect.centery - wall.rect.centery, ball.rect.centerx - wall.rect.centerx)
                speed = math.sqrt(ball.velocity[0]**2 + ball.velocity[1]**2)
                damping_factor = max(0.5, 1 / speed)  # Damping factor based on the inverse of the speed
                ball.velocity[0] = speed * math.cos(angle) * damping_factor
                ball.velocity[1] = speed * math.sin(angle) * damping_factor
                ball.velocity[0] = max(ball.velocity[0], 1) if ball.velocity[0] > 0 else min(ball.velocity[0], -1)
                ball.velocity[1] = max(ball.velocity[1], 1) if ball.velocity[1] > 0 else min(ball.velocity[1], -1)
                ball.real_x = ball.prev_x
                ball.real_y = ball.prev_y
                play_sound()
            else:
                # Ball hits the side of the wall
                ball.velocity[0] *= -0.7
                ball.real_x = ball.prev_x

        # Check for collisions with floors
        floors_hit = pygame.sprite.spritecollide(ball, floors, False)
        for floor in floors_hit:
            ball.velocity[1] *= -0.3  # Bounce off the ground with some damping
            ball.real_x = ball.prev_x
            ball.real_y = ball.prev_y

        # Check for collisions with slots
        if not ball.in_slot:
            slot_hits = pygame.sprite.spritecollide(ball, slots, False)
            for slot in slot_hits:
                ball.in_slot = True
                ball.kill()
                slot.image.fill(GREEN)

        # Check for collisions with other balls
        # balls_hit = pygame.sprite.spritecollide(ball, balls, False)
        # for other_ball in balls_hit:
        #     if ball != other_ball and other_ball.in_slot:
        #         # Bounce off the other ball
        #         angle = math.atan2(ball.rect.centery - other_ball.rect.centery, ball.rect.centerx - other_ball.rect.centerx)
        #         speed = math.sqrt(ball.velocity[0] ** 2 + ball.velocity[1] ** 2)
        #         damping_factor = max(0.5, 1 / speed) 
        #         ball.velocity[0] = speed * math.cos(angle) * damping_factor
        #         ball.velocity[1] = speed * math.sin(angle) * damping_factor
        #         ball.real_x = ball.prev_x
        #         ball.real_y = ball.prev_y

    # Draw
    screen.fill(BLACK)
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)
    frame_count += 1
