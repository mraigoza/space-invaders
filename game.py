import pygame
from pygame.locals import Color
import os

# Window Size, Fonts, and Images
WIN_WIDTH = 800
WIN_HEIGHT = 600

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 80)
SHIP_IMG = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "ship.png")), (64, 64))
SHOT_IMG = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "shot.png")), (32, 32))
ENEMY_IMG = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "enemy.png")), (32, 32))
BG_IMG = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "galaxy.jpg")), (WIN_WIDTH, WIN_HEIGHT))

# User controlled space ship
class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.movements = [] # Holds user input (left is -5 and right is 5)
        self.img = SHIP_IMG

    def move(self, change):
        self.movements.append(change)

    def release(self, change):
        self.movements.remove(change)

    # Move the space ship
    def update(self):
        if len(self.movements) != 0:
            self.x += self.movements[-1]

        if self.x < 0:
            self.x = 0
        elif self.x > 750:
            self.x = 750

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

# Shot which is launched by the Ship
class Shot:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.speed = 5
        self.state = "ready"
        self.img = SHOT_IMG

    # Stores x and y of launch
    def launch(self, x, y):
        if self.state == "ready":
            self.x = x
            self.y = y
            self.state = "launching"

    # Move the shot
    def update(self):
        if self.state == "launching":
            self.y -= self.speed

            if (self.y < 0):
                self.state = "ready"

    def draw(self, win):
        if self.state == "launching":
            win.blit(self.img, (self.x, self.y))

    # Get the mask of the current location to detect collisions
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.updatesCounter = 1 # Number of past updates since y change
        self.updatesNeeded = 110 # Number of updates until y change
        self.state = "ready"
        self.img = ENEMY_IMG

    # Move enemy and check if it won
    def update(self):
        if self.state == "ready":
            # Occassionaly move enemy right based on counter
            if self.updatesCounter % 30 == 0:
                self.x += 50
            # Reached number of updates to move y
            if self.updatesCounter > self.updatesNeeded:
                self.y += 50
                self.x -= 150
                self.updatesCounter = 1
            else:
                self.updatesCounter = self.updatesCounter + 1
            
            # Enemy wins if it passes the height of the window
            if (self.y >= WIN_HEIGHT):
                self.state = "won"

    # Check if enemy is shot, otherwise
    # Move enemy and check if it won
    def checkCollisionandUpdate(self, shot):
        if self.state == "ready":
            # Check Collision
            shot_mask = shot.get_mask()
            enemy_mask = pygame.mask.from_surface(self.img)

            offset = (self.x - shot.x, self.y - round(shot.y))

            overlap = shot_mask.overlap(enemy_mask, offset)

            if overlap:
                self.state = "hit"
                shot.state = "ready"
                return 1 # increment score

            # Move enemy and check if it won
            if self.updatesCounter % 30 == 0:
                self.x += 50
            if self.updatesCounter > self.updatesNeeded:
                self.y += 50
                self.x -= 150
                self.updatesCounter = 1
            else:
                self.updatesCounter = self.updatesCounter + 1
            
            # Enemy wins if it passes the height of the window
            if (self.y >= WIN_HEIGHT):
                self.state = "won"
        
        return 0 # no hit

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

# Draw each element on the screen during the game
def draw_windows(win, ship, shot, enemies, score):
    win.blit(BG_IMG, (0, 0))

    # Draw score
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 -text.get_width(), 10))
    
    # Draw ship
    ship.draw(win)

    # Draw shot
    shot.draw(win)

    # Draw each enemy
    for enemy in enemies:
        enemy.draw(win)
    
    pygame.display.update()

def draw_end_screen(win, score):
    win.blit(BG_IMG, (0, 0))

    # Draw end screen
    score_text = END_FONT.render('Score: ' + str(score), 1, (255, 255, 255))
    win.blit(score_text, (WIN_WIDTH/2 - score_text.get_width()/2, 150))
    
    exit_text = STAT_FONT.render("Click to Exit", 1, (255, 255, 255))
    win.blit(exit_text, (WIN_WIDTH/2 - exit_text.get_width()/2, 240))
    pygame.display.update()
 
    # Wait for Exit
    run = True
    while run:
        pygame.time.delay(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False

def main():
    # Create ship and shot
    ship = Ship(400,480)
    shot = Shot()
    
    # Create each enemy starting at (275, 50)
    num_of_enemies = 10
    enemies = []
    enemy_x = 275
    enemy_y = 50
    while(num_of_enemies > 0):
        # Check if new row is needed to store enemies
        if enemy_x > 575:
            enemy_x = 275
            enemy_y += 50
        
        #Create enemy
        enemies.append(Enemy(enemy_x, enemy_y))
        num_of_enemies = num_of_enemies - 1
        # Increment position of next enemy
        enemy_x += 50

    # Start game
    pygame.init()
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    run = True
    score = 0

    while run:
        clock.tick(30)

        # Check key presses and releases
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                # Move ship left
                if event.key == pygame.K_LEFT:
                    ship.move(-5)
                # Move ship right
                if event.key == pygame.K_RIGHT:
                    ship.move(5)
                # Fire a shot
                if event.key == pygame.K_SPACE:
                    shot.launch(ship.x, ship.y)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    ship.release(-5)
                if event.key == pygame.K_RIGHT:
                    ship.release(5)

        # Update each element
        ship.update()
        shot.update()
        for enemy in enemies:
            # Check if a enemy is hit by a bullet
            if (shot.state == "launching"):
                score += enemy.checkCollisionandUpdate(shot)
            # Check if a enemy has reached the end
            else:
                enemy.update()
            
            if enemy.state == "won":
                run = False
            if enemy.state == "hit":
                enemies.remove(enemy)
        
        # If all enemies are gone then create more
        if len(enemies) == 0:
            num_of_enemies = 10
            while(num_of_enemies > 0):
                # Check if new row is needed to store enemies
                if enemy_x > 575:
                    enemy_x = 275
                    enemy_y += 50
                
                #Create enemy
                enemies.append(Enemy(enemy_x, enemy_y))
                num_of_enemies = num_of_enemies - 1
                # Increment position of next enemy
                enemy_x += 50

        # Draw each element
        draw_windows(win, ship, shot, enemies, score)

    # End of game
    draw_end_screen(win, score)
    pygame.quit()
    quit()

main()