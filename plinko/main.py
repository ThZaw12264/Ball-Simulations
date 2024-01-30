import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Define constants
SCREEN_WIDTH = 810
SCREEN_HEIGHT = 1440
BALL_RADIUS = 25
NUM_SLOTS = 6
SLOT_WIDTH = 135
SLOT_HEIGHT = 150
NUM_LAYERS = 6
PINS_PER_LAYER = 6
PIN_RADIUS = 10
PIN_SPACING_Y = 100
PIN_SPACING_X = 120  # Adjustable spacing between pins
WALL_WIDTH = 10  # Width of the walls between slots
WALL_HEIGHT = 250  # Height of the walls

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (196, 0, 0)
GREEN = (0, 201, 145)

# Sounds
pygame.mixer.set_num_channels(100)
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

FPS = 60

# Define classes
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = BALL_RADIUS
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.color_change_speed = 0.05
        self.color = self.get_rainbow_color()
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.realx = random.uniform(0, SCREEN_WIDTH - 2 * BALL_RADIUS)
        self.realy = 0
        self.prev_x = self.realx  # Store previous x coordinate
        self.prev_y = self.realy  # Store previous y coordinate
        self.rect = self.image.get_rect()
        self.rect.x = self.realx
        self.rect.y = 0
        self.velocity = [random.uniform(-5, 5), random.uniform(-3, 1)]  # Initial velocity
        self.gravity = 0.35  # Gravity strength

    def get_rainbow_color(self):
        # Function to get a rainbow color based on time
        color = pygame.Color(0)
        color.hsva = (int(pygame.time.get_ticks() * self.color_change_speed) % 360, 100, 100, 100)
        return color

    def update(self):
        # Update velocity with gravity
        self.velocity[1] += self.gravity

        # Update position with velocity
        self.prev_x = self.realx  # Store previous x coordinate before updating
        self.prev_y = self.realy  # Store previous y coordinate before updating
        self.realx += self.velocity[0]
        self.realy += self.velocity[1]
        self.rect.x = self.realx
        self.rect.y = self.realy

        # Check for collisions with the window boundaries
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.velocity[0] *= -1  # Bounce off the sides
            ball.realx = ball.prev_x
            ball.realy = ball.prev_y
            play_sound()

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

# Define functions
def play_sound():
    global score_pointer
    score[score_pointer].play()
    score_pointer += 1
    if score_pointer == len(score):
        score_pointer = 0

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Plinko Simulation")

# Create groups for sprites
all_sprites = pygame.sprite.Group()
pins = pygame.sprite.Group()
slots = pygame.sprite.Group()
walls = pygame.sprite.Group()

# Create pins
for layer in range(NUM_LAYERS):
    for i in range(PINS_PER_LAYER):
        horizontal_offset = 5
        pin = Pin(i * PIN_SPACING_X + SLOT_WIDTH // 2 + (layer % 2) * (PIN_SPACING_X // 2) + horizontal_offset,
                  (layer + 1) * PIN_SPACING_Y)
        pins.add(pin)
        all_sprites.add(pin)

# Create slots
slot_colors = [RED, RED, RED, GREEN, GREEN, GREEN]
slot_points = [random.randint(1, 10) for _ in range(NUM_SLOTS)]
for i, points in enumerate(slot_points):
    slot = Slot(i * SLOT_WIDTH, SCREEN_HEIGHT - SLOT_HEIGHT, points, slot_colors[i])
    slots.add(slot)
    all_sprites.add(slot)

# Create walls between slots
for i in range(NUM_SLOTS - 1):
    wall = Wall((i + 1) * SLOT_WIDTH - WALL_WIDTH // 2, SCREEN_HEIGHT - WALL_HEIGHT, WALL_WIDTH, WALL_HEIGHT)
    walls.add(wall)
    all_sprites.add(wall)

# Create balls
balls = pygame.sprite.Group()
initial_ball = Ball()
balls.add(initial_ball)
all_sprites.add(initial_ball)

# Main loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            new_ball = Ball()
            balls.add(new_ball)
            all_sprites.add(new_ball)

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
            ball.realx = ball.prev_x
            ball.realy = ball.prev_y
            play_sound()

        # Check for collisions with slots
        slot_hits = pygame.sprite.spritecollide(ball, slots, False)
        for slot in slot_hits:
            if slot.rect.centerx > SCREEN_WIDTH // 2:
                # Right slots: Add a new ball
                ball.kill()
                print(f"Ball in slot with {slot.points} points. Adding two new ball.")
                new_ball = Ball()
                balls.add(new_ball)
                all_sprites.add(new_ball)
                new_ball = Ball()
                balls.add(new_ball)
                all_sprites.add(new_ball)
            else:
                # Left slots: Remove a ball
                ball.kill()
                print(f"Ball in slot with {slot.points} points. Removing a ball.")

        # Check for collisions with walls
        walls_hit = pygame.sprite.spritecollide(ball, walls, False)
        for wall in walls_hit:
            if ball.rect.bottom < wall.rect.top + 25:
                # Ball hits the top of the wall
                ball.velocity[0] *= 0.85
                ball.velocity[1] = -ball.velocity[1] * 0.65
                ball.velocity[0] = max(ball.velocity[0], 2) if ball.velocity[0] > 0 else min(ball.velocity[0], -2)
                ball.velocity[1] = max(ball.velocity[1], 2) if ball.velocity[1] > 0 else min(ball.velocity[1], -2)
                ball.realy = wall.rect.top - BALL_RADIUS - 25
            else:
                ball.velocity[0] *= -1
            play_sound()

    # Draw
    screen.fill(BLACK)
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)
