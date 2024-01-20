import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 810, 1440
BALL_RADIUS = 30
BAR_WIDTH = 5
BAR_HEIGHT = 385
FPS = 60

# Colors
WHITE = (255, 255, 242)
BLACK = (1, 1, 1)
RED = (255, 173, 173)
GREEN = (201, 228, 222)
BLUE = (198, 222, 241)
PURPLE = (219, 205, 240)
TRAIL_LENGTH = 15  # Adjust this value to control the length of the trail
# NEON_GLOW_RADIUS = 2  # Adjust this value to control the neon glow radius

# Sounds
pygame.mixer.set_num_channels(100)
a_note = pygame.mixer.Sound("sounds/A_BELL.wav")
c_note = pygame.mixer.Sound("sounds/C_BELL.wav")
c_sharp_note = pygame.mixer.Sound("sounds/C#_BELL.wav")
d_note = pygame.mixer.Sound("sounds/D_BELL.wav")
e_note = pygame.mixer.Sound("sounds/E_BELL.wav")
f_note = pygame.mixer.Sound("sounds/F_BELL.wav")

class Ball:
    def __init__(self, color, x, y, radius):
        self.color = color
        self.x = x
        self.y = y
        self.radius = radius
        self.trail = []

    def update_position(self, new_x, new_y):
        self.trail.insert(0, (self.x, self.y))
        if len(self.trail) > TRAIL_LENGTH:
            self.trail.pop()

        self.x = new_x
        self.y = new_y

    def draw(self, screen):
        # Draw neon glow effect
        neon_surface = pygame.Surface((self.radius * 2 + 12, self.radius * 2 + 12), pygame.SRCALPHA)
        pygame.draw.circle(neon_surface, self.color + (100,), (self.radius + 6, self.radius + 6), self.radius + 6, 8)
        pygame.draw.circle(neon_surface, WHITE, (self.radius + 6, self.radius + 6), self.radius + 3, 2)
        screen.blit(neon_surface, (self.x - self.radius - 6, self.y - self.radius - 6))

        # Draw the trail with gradient afterimages
        for i, position in enumerate(self.trail):
            alpha = int(255 - (255 * (i / TRAIL_LENGTH)))
            trail_color = (self.color[0], self.color[1], self.color[2], alpha)
            trail_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, trail_color, (self.radius, self.radius), self.radius)
            screen.blit(trail_surface, (position[0] - self.radius, position[1] - self.radius))

        # Draw original object
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

class Pendulum:
    def __init__(self, color, length, angle, duration, score):
        self.ball = Ball(color, WIDTH // 2, HEIGHT // 4, BALL_RADIUS)
        self.length = length
        self.angle = angle
        self.duration = duration
        self.score = score
        self.score_index = 0
        self.started = False

        self.angular_velocity = 0

    def start(self):
        self.started = True
        self.angular_velocity = (2 * math.pi) / self.duration

    def update(self):
        self.angle += self.angular_velocity

        new_x = WIDTH // 2 + int(self.length * math.sin(self.angle))
        new_y = HEIGHT // 2 + int(self.length * math.cos(self.angle))
        self.ball.update_position(new_x, new_y)

        # Check if the score has finished
        if self.score_index >= len(self.score):
            self.started = False

    def draw(self, screen):
        pygame.draw.line(screen, WHITE, (WIDTH // 2, HEIGHT // 2 - 3), (self.ball.x, self.ball.y), 2)
        self.ball.draw(screen)

    def play_sound(self):
        self.score[self.score_index % len(self.score)].play()
        self.score_index += 1

class Bar:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def check_collision(self, pendulum):
        # Check collision with x and y boundaries of the bar
        x_collision = pendulum.ball.x == WIDTH // 2
        y_collision = self.y <= pendulum.ball.y + pendulum.ball.radius <= self.y + self.height
        return x_collision and y_collision

    def draw(self, screen):
        # Draw neon glow effect
        pygame.draw.rect(screen, WHITE, (self.x - 2, self.y - 2, self.width + 2 * 2, self.height + 2 * 2))
        
        # Draw the bar
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Falls")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Scores
score1 = [f_note, f_note, f_note, f_note, e_note, e_note, e_note, e_note]
score2 = [d_note, d_note, d_note, d_note, c_note, c_note, c_note, c_note, c_sharp_note, c_sharp_note, c_sharp_note, c_sharp_note, c_sharp_note, c_sharp_note, c_sharp_note, c_sharp_note]
score3 = [a_note, a_note, a_note, a_note, a_note, a_note, a_note, a_note]

# Create instances
pendulum1 = Pendulum(GREEN, 110, math.pi, 100, score1)
pendulum2 = Pendulum(BLUE, 220, math.pi, 50, score2)
pendulum3 = Pendulum(PURPLE, 330, math.pi, 100, score3)
pendulums = [pendulum2, pendulum1, pendulum3]
bar = Bar(WIDTH // 2 - BAR_WIDTH // 2, HEIGHT // 2, BAR_WIDTH, BAR_HEIGHT)

# Main game loop
pendulum_index = -1
weird_stuff = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            # Start the next pendulum on Enter key press
            pendulum_index += 1
            pendulums[pendulum_index % len(pendulums)].start()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # Start weird stuff on Space key press
            weird_stuff = True
            frames = 0

    if weird_stuff:
        # Weird stuff
        if frames % 20 == 0:
            FPS += 1
            # if pendulums[0].ball.radius < 160:
            #     pendulums[0].ball.radius += 1
        frames += 1

    # Check for collisions with the bar and update pendulum positions
    for pendulum in pendulums:
        if bar.check_collision(pendulum):
            pendulum.play_sound()
            pendulum.angular_velocity *= -1  # Reverse the direction upon hitting the bar

        pendulum.update()

    # Clear the screen
    screen.fill(BLACK)

    # Draw all pendulums
    for pendulum in pendulums:
        pendulum.draw(screen)

    # Draw the bar
    bar.draw(screen)

    # Draw the border
    border_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(border_surface, WHITE, (WIDTH // 2, HEIGHT // 2), 392, 8)
    screen.blit(border_surface, (0, 0))
    pygame.draw.circle(screen, RED, (WIDTH // 2, HEIGHT // 2), 390, 5)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(FPS)
