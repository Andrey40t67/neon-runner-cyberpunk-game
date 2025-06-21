#!/usr/bin/env python3
"""
Neon Runner - Cyberpunk Endless Runner Game
A fast-paced endless runner with cyberpunk aesthetics
"""

import pygame
import random
import math
import json
import os

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (Cyberpunk Neon Theme)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 255)
NEON_GREEN = (0, 255, 0)
NEON_PURPLE = (128, 0, 255)
DARK_BLUE = (0, 50, 100)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.vel_y = 0
        self.jumping = False
        self.on_ground = True
        self.jump_power = -15
        self.gravity = 0.8
        self.color = NEON_BLUE
        self.trail = []
        
    def update(self):
        # Handle gravity
        if not self.on_ground:
            self.vel_y += self.gravity
        
        self.y += self.vel_y
        
        # Ground collision
        ground_y = SCREEN_HEIGHT - 100
        if self.y + self.height >= ground_y:
            self.y = ground_y - self.height
            self.vel_y = 0
            self.on_ground = True
            self.jumping = False
        
        # Add trail effect
        self.trail.append((self.x + self.width//2, self.y + self.height//2))
        if len(self.trail) > 10:
            self.trail.pop(0)
    
    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
            self.jumping = True
    
    def draw(self, screen):
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            trail_color = (*NEON_BLUE[:3], alpha)
            pygame.draw.circle(screen, NEON_BLUE, pos, max(1, 5 - i//2))
        
        # Draw player with glow effect
        glow_rect = pygame.Rect(self.x - 5, self.y - 5, self.width + 10, self.height + 10)
        pygame.draw.rect(screen, DARK_BLUE, glow_rect)
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.color, player_rect)
        pygame.draw.rect(screen, WHITE, player_rect, 2)

class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = 5
        self.color = NEON_PINK
        
    def update(self):
        self.x -= self.speed
        
    def draw(self, screen):
        # Draw obstacle with glow
        glow_rect = pygame.Rect(self.x - 3, self.y - 3, self.width + 6, self.height + 6)
        pygame.draw.rect(screen, (50, 0, 50), glow_rect)
        obstacle_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.color, obstacle_rect)
        pygame.draw.rect(screen, WHITE, obstacle_rect, 2)
    
    def collides_with(self, player):
        return (self.x < player.x + player.width and
                self.x + self.width > player.x and
                self.y < player.y + player.height and
                self.y + self.height > player.y)

class Collectible:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = 5
        self.color = NEON_GREEN
        self.pulse = 0
        
    def update(self):
        self.x -= self.speed
        self.pulse += 0.2
        
    def draw(self, screen):
        # Pulsing effect
        pulse_size = int(5 * math.sin(self.pulse))
        size = self.width + pulse_size
        x = self.x - pulse_size // 2
        y = self.y - pulse_size // 2
        
        # Draw collectible with glow
        glow_rect = pygame.Rect(x - 5, y - 5, size + 10, size + 10)
        pygame.draw.rect(screen, (0, 50, 0), glow_rect)
        collectible_rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(screen, self.color, collectible_rect)
        pygame.draw.rect(screen, WHITE, collectible_rect, 2)
    
    def collides_with(self, player):
        return (self.x < player.x + player.width and
                self.x + self.width > player.x and
                self.y < player.y + player.height and
                self.y + self.height > player.y)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Neon Runner - Cyberpunk Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.score = 0
        self.high_score = self.load_high_score()
        
        # Game objects
        self.player = Player(100, SCREEN_HEIGHT - 140)
        self.obstacles = []
        self.collectibles = []
        
        # Timing
        self.obstacle_timer = 0
        self.collectible_timer = 0
        self.background_scroll = 0
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
    def load_high_score(self):
        try:
            with open('high_score.json', 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except:
            return 0
    
    def save_high_score(self):
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.player.jump()
                elif event.key == pygame.K_r and self.game_over:
                    self.restart_game()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                self.player.jump()
    
    def update(self):
        if self.game_over:
            return
            
        # Update player
        self.player.update()
        
        # Spawn obstacles
        self.obstacle_timer += 1
        if self.obstacle_timer > 90:  # Spawn every 1.5 seconds at 60 FPS
            obstacle_height = random.randint(40, 80)
            obstacle = Obstacle(SCREEN_WIDTH, SCREEN_HEIGHT - 100 - obstacle_height, 30, obstacle_height)
            self.obstacles.append(obstacle)
            self.obstacle_timer = 0
        
        # Spawn collectibles
        self.collectible_timer += 1
        if self.collectible_timer > 120:  # Spawn every 2 seconds
            collectible_y = random.randint(200, SCREEN_HEIGHT - 150)
            collectible = Collectible(SCREEN_WIDTH, collectible_y)
            self.collectibles.append(collectible)
            self.collectible_timer = 0
        
        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update()
            if obstacle.x + obstacle.width < 0:
                self.obstacles.remove(obstacle)
                self.score += 10
            elif obstacle.collides_with(self.player):
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
        
        # Update collectibles
        for collectible in self.collectibles[:]:
            collectible.update()
            if collectible.x + collectible.width < 0:
                self.collectibles.remove(collectible)
            elif collectible.collides_with(self.player):
                self.collectibles.remove(collectible)
                self.score += 50
        
        # Update background scroll
        self.background_scroll += 2
        if self.background_scroll >= SCREEN_WIDTH:
            self.background_scroll = 0
    
    def draw_background(self):
        # Cyberpunk grid background
        self.screen.fill(BLACK)
        
        # Draw moving grid lines
        grid_size = 50
        for x in range(-grid_size, SCREEN_WIDTH + grid_size, grid_size):
            x_pos = (x + self.background_scroll) % SCREEN_WIDTH
            pygame.draw.line(self.screen, DARK_BLUE, (x_pos, 0), (x_pos, SCREEN_HEIGHT), 1)
        
        for y in range(0, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(self.screen, DARK_BLUE, (0, y), (SCREEN_WIDTH, y), 1)
        
        # Draw ground
        ground_y = SCREEN_HEIGHT - 100
        pygame.draw.rect(self.screen, NEON_PURPLE, (0, ground_y, SCREEN_WIDTH, 100))
        pygame.draw.line(self.screen, NEON_PINK, (0, ground_y), (SCREEN_WIDTH, ground_y), 3)
    
    def draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, NEON_GREEN)
        self.screen.blit(score_text, (10, 10))
        
        # High Score
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, NEON_BLUE)
        self.screen.blit(high_score_text, (10, 50))
        
        # Instructions
        if not self.game_over:
            instruction_text = self.font.render("SPACE or CLICK to Jump", True, WHITE)
            self.screen.blit(instruction_text, (SCREEN_WIDTH - 300, 10))
        
        # Game Over screen
        if self.game_over:
            game_over_text = self.big_font.render("GAME OVER", True, NEON_PINK)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = self.font.render("Press R to Restart or ESC to Quit", True, WHITE)
            text_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(restart_text, text_rect)
            
            final_score_text = self.font.render(f"Final Score: {self.score}", True, NEON_GREEN)
            text_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            self.screen.blit(final_score_text, text_rect)
    
    def draw(self):
        self.draw_background()
        
        # Draw game objects
        self.player.draw(self.screen)
        
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        for collectible in self.collectibles:
            collectible.draw(self.screen)
        
        self.draw_ui()
        
        pygame.display.flip()
    
    def restart_game(self):
        self.game_over = False
        self.score = 0
        self.player = Player(100, SCREEN_HEIGHT - 140)
        self.obstacles = []
        self.collectibles = []
        self.obstacle_timer = 0
        self.collectible_timer = 0
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()