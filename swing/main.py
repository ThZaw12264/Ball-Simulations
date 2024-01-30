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
TRAIL_LENGTH = 15

# Sounds
pygame.mixer.set_num_channels(200)
a_note = pygame.mixer.Sound("sounds/A_BELL.wav")
c_note = pygame.mixer.Sound("sounds/C_BELL.wav")
c_sharp_note = pygame.mixer.Sound("sounds/C#_BELL.wav")
d_note = pygame.mixer.Sound("sounds/D_BELL.wav")
e_note = pygame.mixer.Sound("sounds/E_BELL.wav")
f_note = pygame.mixer.Sound("sounds/F_BELL.wav")

class Ball:
    def __init__(self, color, x, y, radius):
        self.color = color
        self.x, self.y, self.radius = x, y, radius
        self.trail = []

    def update_position(self, new_x, new_y):
        self.trail.insert(0, (self.x, self.y))
        if len(self.trail) > TRAIL_LENGTH:
            self.trail.pop()
        self.x, self.y = new_x, new_y

    def draw(self, screen):
        neon_surface = pygame.Surface((self.radius * 2 + 12, self.radius * 2 + 12), pygame.SRCALPHA)
        pygame.draw.circle(neon_surface, self.color + (100,), (self.radius + 6, self.radius + 6), self.radius + 6, 8)
        pygame.draw.circle(neon_surface, WHITE, (self.radius + 6, self.radius + 6), self.radius + 3, 2)
        screen.blit(neon_surface, (self.x - self.radius - 6, self.y - self.radius - 6))

        for i, position in enumerate(self.trail):
            alpha = int(255 - (255 * (i / TRAIL_LENGTH)))
            trail_color = (self.color[0], self.color[1], self.color[2], alpha)
            trail_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, trail_color, (self.radius, self.radius), self.radius)
            screen.blit(trail_surface, (position[0] - self.radius, position[1] - self.radius))

        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

class Pendulum:
    def __init__(self, color, length, angle, duration, score):
        self.ball = Ball(color, WIDTH // 2, HEIGHT // 4, BALL_RADIUS)
        self.length, self.angle, self.duration = length, angle, duration
        self.score, self.score_index, self.started, self.top_reached = score, 0, False, False
        self.angular_velocity = 0

    def start(self):
        self.started, self.angular_velocity = True, (2 * math.pi) / self.duration

    def update(self):
        self.angle += self.angular_velocity
        new_x = WIDTH // 2 + int(self.length * math.sin(self.angle))
        new_y = HEIGHT // 2 + int(self.length * math.cos(self.angle))
        self.ball.update_position(new_x, new_y)

        if math.cos(self.angle) < -0.1:
            self.top_reached = True

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
        self.x, self.y, self.width, self.height = x, y, width, height
        self.collision_positions = []

    def check_collision(self, pendulum):
        x_collision = pendulum.ball.x >= WIDTH // 2 if pendulum.angular_velocity > 0 else pendulum.ball.x <= WIDTH // 2
        y_collision = self.y <= pendulum.ball.y - pendulum.ball.radius <= self.y + self.height

        if x_collision and y_collision and pendulum.top_reached:
            self.collision_positions.append((pendulum.ball.y, pygame.time.get_ticks()))
            pendulum.angle, pendulum.top_reached = 0, False
            return True

        return False

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x - 2, self.y - 2, self.width + 2 * 2, self.height + 2 * 2))
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

        current_time = pygame.time.get_ticks()

        for y, collision_time in self.collision_positions[:]:
            pygame.draw.rect(screen, (255, 255, 255, 128), (self.x - 4, y - 35, self.width + 8, BAR_HEIGHT // 5))

            if current_time - collision_time > 100:
                self.collision_positions.remove((y, collision_time))

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pendulums Simulation")

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
pendulum_index, weird_stuff, frames = -1, False, 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            pendulum_index += 1
            pendulums[pendulum_index % len(pendulums)].start()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            weird_stuff, frames = True, 0

    if weird_stuff:
        if frames % 20 == 0:
            FPS += 1
            for pendulum in pendulums:
                if pendulum.ball.radius < 150:
                    pendulum.ball.radius += 1
            if frames % 40 == 0:
                for pendulum in pendulums:
                    pendulum.duration -= 1 if pendulum.ball.color == BLUE else 2
                    pendulum.angular_velocity = ((2 * math.pi) / pendulum.duration) * (pendulum.angular_velocity / abs(pendulum.angular_velocity))
        frames += 1

    for pendulum in pendulums:
        if bar.check_collision(pendulum):
            pendulum.play_sound()
            pendulum.angular_velocity *= -1

        pendulum.update()

    screen.fill(BLACK)

    for pendulum in pendulums:
        pendulum.draw(screen)

    bar.draw(screen)

    border_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(border_surface, WHITE, (WIDTH // 2, HEIGHT // 2), 392, 8)
    screen.blit(border_surface, (0, 0))
    pygame.draw.circle(screen, RED, (WIDTH // 2, HEIGHT // 2), 390, 5)

    pygame.display.flip()
    clock.tick(FPS)
