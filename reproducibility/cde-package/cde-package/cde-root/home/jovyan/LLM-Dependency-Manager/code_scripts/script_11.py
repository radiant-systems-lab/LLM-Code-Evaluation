# Game Development with Pygame
import pygame
import random
import math
import sys

pygame.init()

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 0
        self.speed_y = 0
    
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Sample Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.all_sprites = pygame.sprite.Group()
        
        # Create some game objects
        for i in range(5):
            sprite = GameSprite(
                random.randint(0, 750),
                random.randint(0, 550),
                50, 50,
                (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            )
            sprite.speed_x = random.randint(-3, 3)
            sprite.speed_y = random.randint(-3, 3)
            self.all_sprites.add(sprite)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    def update(self):
        self.all_sprites.update()
        
        # Bounce off edges
        for sprite in self.all_sprites:
            if sprite.rect.right > 800 or sprite.rect.left < 0:
                sprite.speed_x *= -1
            if sprite.rect.bottom > 600 or sprite.rect.top < 0:
                sprite.speed_y *= -1
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()
    
    def run(self):
        frame_count = 0
        while self.running and frame_count < 100:  # Limit frames for testing
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            frame_count += 1
        
        pygame.quit()
        print(f"Game ran for {frame_count} frames")

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except pygame.error as e:
        print(f"Pygame error: {e}")
