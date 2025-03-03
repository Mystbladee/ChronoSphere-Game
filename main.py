import pygame
import pygame_gui
import os

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 1280, 720
FPS = 60
PLAYER_SPEED = 5
REWIND_DURATION = 5  # Seconds

# Colors (Material You Palette)
PRIMARY = "#8FBCBB"
SECONDARY = "#3B4252"
BACKGROUND = "#2E3440"
TEXT_COLOR = "#D8DEE9"

# Setup
pygame.display.set_caption("ChronoSphere: Echoes of Time")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
manager = pygame_gui.UIManager((WIDTH, HEIGHT), "themes/material_theme.json")
clock = pygame.time.Clock()

# Load assets (add your own later!)
try:
    player_img = pygame.image.load("assets/player.png").convert_alpha()
except FileNotFoundError:
    player_img = pygame.Surface((30, 50))
    player_img.fill((255, 0, 0))  # Red placeholder

# Time Rewind System
class TimeRewind:
    def __init__(self):
        self.checkpoints = []
        self.max_checkpoints = FPS * REWIND_DURATION  # 5 seconds

    def add_checkpoint(self, player_pos, laser_state):
        if len(self.checkpoints) >= self.max_checkpoints:
            self.checkpoints.pop(0)
        self.checkpoints.append((player_pos, laser_state.copy()))

    def rewind(self):
        if self.checkpoints:
            return self.checkpoints[-1]
        return None

# Game State
class GameState:
    def __init__(self):
        self.player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.chronoshards = 0
        self.lasers = [
            {"rect": pygame.Rect(100, 200, 10, 500), "active": True},
            {"rect": pygame.Rect(1100, 200, 10, -500), "active": False},
        ]
        self.receptors = [pygame.Rect(800, 300, 50, 50)]
        self.rewind = TimeRewind()

# Initialize game
game = GameState()

# UI Elements
rewind_text = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(10, 10, 200, 50),
    text=f"Rewind: {REWIND_DURATION}s",
    manager=manager,
    object_id="#rewind_label",
)

shard_text = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(10, 50, 200, 50),
    text=f"ChronoShards: {game.chronoshards}",
    manager=manager,
    object_id="#shard_label",
)

# Main loop
running = True
while running:
    time_delta = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Rewind to last checkpoint
                checkpoint = game.rewind.rewind()
                if checkpoint:
                    game.player_pos, game.lasers = checkpoint
                    game.rewind.checkpoints = []  # Prevent infinite rewinding
        manager.process_events(event)

    # Player movement
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_w]:
        dy = -PLAYER_SPEED
    if keys[pygame.K_s]:
        dy = PLAYER_SPEED
    if keys[pygame.K_a]:
        dx = -PLAYER_SPEED
    if keys[pygame.K_d]:
        dx = PLAYER_SPEED

    # Update player position with screen boundary constraints
    game.player_pos.x = max(0, min(WIDTH, game.player_pos.x + dx))
    game.player_pos.y = max(0, min(HEIGHT, game.player_pos.y + dy))

    # Laser puzzle logic
    for laser in game.lasers:
        if laser["active"]:
            # Simulate laser movement (vertical)
            laser["rect"].centery += 2
            if laser["rect"].y > HEIGHT:
                laser["active"] = False

    # Check for laser-receptor intersection
    for laser in game.lasers:
        for receptor in game.receptors:
            if laser["rect"].colliderect(receptor):
                game.chronoshards += 1
                laser["active"] = False

    # Update UI
    shard_text.set_text(f"ChronoShards: {game.chronoshards}")

   # Save checkpoint every 0.5 seconds
   checkpoint_timer += time_delta
   if checkpoint_timer >= 0.5:
   laser_states = [{"rect": l["rect"].copy(), "active": l["active"]} for l in game.lasers]
   game.rewind.add_checkpoint(game.player_pos.copy(), laser_states)
   checkpoint_timer = 0

    # Draw everything
    screen.fill(BACKGROUND)

    # Debug lasers
    for laser in game.lasers:
        if laser["active"]:
            pygame.draw.rect(screen, PRIMARY, laser["rect"])

    for receptor in game.receptors:
        pygame.draw.rect(screen, SECONDARY, receptor)

    # Player
    screen.blit(player_img, (game.player_pos.x - 15, game.player_pos.y - 25))

    manager.update(time_delta)
    manager.draw_ui(screen)

    pygame.display.flip()

pygame.quit()
