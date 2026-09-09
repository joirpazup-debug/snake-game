import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 30
GRID_WIDTH = 20
GRID_HEIGHT = 20
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10  # Game speed (ticks per second)

# PICO-8 Inspired Retro Color Palette
BG_COLOR = (24, 20, 37)         # Deep dark purple-navy
GRID_COLOR = (34, 32, 52)       # Subtle grid line color
SNAKE_HEAD = (56, 183, 100)     # Vibrant pixel green
SNAKE_BODY = (43, 130, 83)      # Darker green for body texture
SNAKE_ACCENT = (141, 239, 134)  # Highlight for snake eyes/texture
APPLE_RED = (228, 59, 68)       # Rich pixel red
APPLE_SHADOW = (172, 50, 50)    # Apple depth shading
APPLE_STEM = (48, 104, 80)      # Leaf/Stem color
TEXT_COLOR = (244, 244, 244)    # Crisp off-white

# Setup Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Art Snake Game")
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.SysFont("Courier New", 18, bold=True)
font_large = pygame.font.SysFont("Courier New", 32, bold=True)

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [
            (GRID_WIDTH // 2, GRID_HEIGHT // 2),
            (GRID_WIDTH // 2, GRID_HEIGHT // 2 + 1),
            (GRID_WIDTH // 2, GRID_HEIGHT // 2 + 2)
        ]
        self.direction = (0, -1)  # Moving up initially
        self.next_direction = (0, -1)
        self.grow_pending = False

    def update(self):
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        
        self.body.insert(0, new_head)
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

    def change_direction(self, new_dir):
        # Prevent reversing directly into oneself
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.next_direction = new_dir

    def check_collision(self):
        head_x, head_y = self.body[0]
        # Wall collision
        if not (0 <= head_x < GRID_WIDTH and 0 <= head_y < GRID_HEIGHT):
            return True
        # Self collision
        if self.body[0] in self.body[1:]:
            return True
        return False

class Apple:
    def __init__(self):
        self.position = (0, 0)
        self.spawn([])

    def spawn(self, snake_body):
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if self.position not in snake_body:
                break

def draw_pixel_apple(surface, pos):
    x = pos[0] * CELL_SIZE
    y = pos[1] * CELL_SIZE
    
    # Outer apple body (retro pixel art style with highlights & shadows)
    pygame.draw.rect(surface, APPLE_RED, (x + 4, y + 8, CELL_SIZE - 8, CELL_SIZE - 10))
    pygame.draw.rect(surface, APPLE_SHADOW, (x + 4, y + CELL_SIZE - 6, CELL_SIZE - 8, 4))
    pygame.draw.rect(surface, (255, 120, 120), (x + 6, y + 10, 4, 4)) # Highlight shine
    # Stem and leaf
    pygame.draw.rect(surface, APPLE_STEM, (x + CELL_SIZE // 2 - 2, y + 2, 4, 6))

def draw_pixel_snake(surface, snake_body):
    for i, segment in enumerate(snake_body):
        x = segment[0] * CELL_SIZE
        y = segment[1] * CELL_SIZE
        
        if i == 0:
            # Snake Head
            pygame.draw.rect(surface, SNAKE_HEAD, (x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4))
            pygame.draw.rect(surface, SNAKE_ACCENT, (x + 6, y + 6, 4, 4)) # Eye 1
            pygame.draw.rect(surface, SNAKE_ACCENT, (x + CELL_SIZE - 10, y + 6, 4, 4)) # Eye 2
        else:
            # Snake Body with a tiled pixel border effect
            pygame.draw.rect(surface, SNAKE_BODY, (x + 3, y + 3, CELL_SIZE - 6, CELL_SIZE - 6))
            pygame.draw.rect(surface, SNAKE_HEAD, (x + 6, y + 6, CELL_SIZE - 12, CELL_SIZE - 12))

def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_WIDTH, y), 1)

# Game initialization
snake = Snake()
apple = Apple()
apple.spawn(snake.body)
score = 0
game_state = "START"  # States: "START", "PLAYING", "GAME_OVER"

# Main Game Loop
while True:
    screen.fill(BG_COLOR)
    
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.KEYDOWN:
            if game_state == "START":
                if event.key == pygame.K_RETURN:
                    game_state = "PLAYING"
            elif game_state == "PLAYING":
                if event.key == pygame.K_UP or event.key == ord('w'):
                    snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN or event.key == ord('s'):
                    snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT or event.key == ord('a'):
                    snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT or event.key == ord('d'):
                    snake.change_direction((1, 0))
            elif game_state == "GAME_OVER":
                if event.key == pygame.K_r:
                    snake.reset()
                    apple.spawn(snake.body)
                    score = 0
                    game_state = "PLAYING"

    # Game Updates
    if game_state == "PLAYING":
        snake.update()
        
        # Check if snake eats apple
        if snake.body[0] == apple.position:
            snake.grow_pending = True
            score += 10
            apple.spawn(snake.body)
            
        # Check game over conditions
        if snake.check_collision():
            game_state = "GAME_OVER"

    # Rendering Graphics
    draw_grid(screen)
    draw_pixel_apple(screen, apple.position)
    draw_pixel_snake(screen, snake.body)

    # UI / Scoreboard Display
    score_surface = font_small.render(f"SCORE: {score}", True, TEXT_COLOR)
    screen.blit(score_surface, (15, 15))

    # Screens (Start / Game Over overlays)
    if game_state == "START":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((24, 20, 37, 220))
        screen.blit(overlay, (0, 0))
        
        title_surf = font_large.render("PIXEL SNAKE", True, SNAKE_HEAD)
        sub_surf = font_small.render("Press [ENTER] to Start", True, TEXT_COLOR)
        controls_surf = font_small.render("Use Arrow Keys or WASD", True, (120, 110, 140))
        
        screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        screen.blit(controls_surf, (SCREEN_WIDTH // 2 - controls_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 45))

    elif game_state == "GAME_OVER":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((24, 20, 37, 230))
        screen.blit(overlay, (0, 0))
        
        go_surf = font_large.render("GAME OVER", True, APPLE_RED)
        final_score = font_small.render(f"Final Score: {score}", True, TEXT_COLOR)
        restart_surf = font_small.render("Press [R] to Restart", True, SNAKE_HEAD)
        
        screen.blit(go_surf, (SCREEN_WIDTH // 2 - go_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, SCREEN_HEIGHT // 2 + 5))
        screen.blit(restart_surf, (SCREEN_WIDTH // 2 - restart_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

    pygame.display.flip()
    clock.tick(FPS)
