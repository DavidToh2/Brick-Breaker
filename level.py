import pygame
from pygame.locals import *
import time, sys, random

from values import *

from configparser import *

        # TABLE OF GAMESTATES:
        # 0 - The game will exit.
        # 1 - Running the game
        # 2 - Game is paused
        # 3 - Game is resetting
        # 1000 - On the main menu. Note that menu type is handled with the same indices in menu.py
        # 1001 - Level select menu.

SPEED_UP = pygame.USEREVENT + 0

pygame.time.set_timer(SPEED_UP, 6000)

        # SPRITE GROUPS

game_entities = pygame.sprite.Group()
bricks = pygame.sprite.Group()
walls = pygame.sprite.Group()
balls = pygame.sprite.Group()

        # COMMON SPRITES

player = playerPaddle()

            # WALLS

w = WIDTH // WALLHEIGHT
h = HEIGHT // WALLHEIGHT
for x in range(0, w):
    wall_init = wall(WALLHEIGHT*x, 0)
    walls.add(wall_init)
for y in range(1, h-1):
    wall_init = wall(0, WALLHEIGHT*y)
    walls.add(wall_init)
    wall_init = wall(WIDTH - WALLHEIGHT, WALLHEIGHT*y)
    walls.add(wall_init)
game_entities.add(walls)

            # BRICKS are initialised on a per-level basis.
            # The entities are initialised using function new_game, then inserted into the "bricks" and "game_entities" groups,
            # from where they can be accessed globally. 
            # Upon the end of a level or death, all entities are first kill()-ed to remove them from all groups, then deleted using
            # the in-built "del object" function (in game.py).

class Level(object):
    def __init__(self):
        self.fileName = "level.txt"
        self.levelName = None
        self.levelNo = 0
        self.bricks = 0
        self.ballSpeed = 0
        self.Score = 0
        self.layout = None
        self.multiplier = 1.0
        self.Highscores = ""
        self.ballCount = 0

    def loadLevel(self, levelNo):
        self.levelNo = levelNo
        self.levelName = "level" + str(levelNo)
        parser = ConfigParser()
                # Attempt to read the level configFile
        try:
            parser.read(self.fileName)
        except:
            print("Level file does not exist!")
            return 1

                # Attempt to read the target level
        try:
            self.layout = parser.get(self.levelName, "layout").split("\n")
        except:
            print("Requested level does not exist!")
            return 1

                # Read the level layout

        levelHeight = len(self.layout)
        for y in range(0, levelHeight):
            for x in range(0, 10):
                t = self.layout[y][x]
                if t != '0':
                    brick_init = brick(t, 25+BRICKWIDTH*x, 25+BRICKHEIGHT*y)
                    bricks.add(brick_init)
                    self.bricks += 1
        game_entities.add(bricks)

                # Read the level properties
        self.ballSpeed = float(parser.get(self.levelName, "ballSpeed"))
        self.Score = 0
        self.Highscores = str(parser.get(self.levelName, "Highscores"))
        self.ballCount = 1
        return 0

    def updateHighScores(self, newName, newScore):

        parser = ConfigParser()
        try:
            parser.read(self.fileName)
        except:
            print("Level file does not exist!")
            return 1

                # Read the high score data (currently in a string) into an array

        highScoreArrayTemp = self.Highscores.split("; ")
        l = len(highScoreArrayTemp)
        highScoreArray = []
        
        if highScoreArrayTemp[0] == "":
            None
        else:
            highScoreArray = [x.split(", ") for x in highScoreArrayTemp]
        #print(f"The old high score array is {highScoreArray}")
        highScoreArray.append([newName, str(newScore)])
        highScoreArray = sorted(highScoreArray, key=lambda item : int(item[1]), reverse = True)
        if l == 5:
            highScoreArray.pop(5)

                # Join everything back into a string to update into the data file

        newHighScoreString = "; ".join([", ".join(highScoreArray[x]) for x in range(0, len(highScoreArray))])
        parser.set(self.levelName, "Highscores", newHighScoreString)
        #print(f"The new high score string is {newHighScoreString}")
        with open(self.fileName, 'w') as file:
            parser.write(file)

currentLevel = Level()


def update():

    if player.wideState == True:
        player.wideTimer += 1
        if player.wideTimer >= 600:
            player.widen(False)

    for ball in balls:
        s = int(ball.total_speed)
                           # Idea from https://codeincomplete.com/articles/collision-detection-in-breakout/
        for i in range(0, s):

                # Move the ball once

            ball.move_once()

                # Detect for collision with player paddle, then adjust the angle based on the position of collision

            if pygame.sprite.collide_rect(ball, player):
                dx = (ball.x_coord - player.rect.centerx) / 3
                dy = player.rect.centery - ball.y_coord
                if (dy < (BALLHEIGHT + BRICKHEIGHT)*0.5 - 2):
                    ball.x_dir = -ball.x_dir
                    ball.y_dir = -1
                else:
                    if dx < 0:
                        ball.x_dir = -1
                        dx = -dx
                    else:
                        ball.x_dir = 1
                    ball.adjust_angle(dx, dy)
                    ball.y_dir = -1
                currentLevel.multiplier = 1

                    # Detect for wall bounces

            if (ball.rect.left < WALLHEIGHT) or (ball.rect.right > WIDTH - WALLHEIGHT):
                ball.x_dir = -ball.x_dir
            
            if ball.rect.top < WALLHEIGHT:
                ball.y_dir = -ball.y_dir

                    # Kill the ball if it exits the screen

            if ball.rect.bottom > HEIGHT - BALLHEIGHT:
                ball.kill()
                del ball
                currentLevel.ballCount -= 1
                break

                    # Update the ball's powerup effects

            if ball.heat_state:
                ball.heat_time += 1
                if ball.heat_time >= 600 * s:
                    ball.set_heat_state(currentLevel.ballSpeed, 0)

            if ball.smasher_state:
                ball.smasher_time += 1
                if ball.smasher_time >= 600 * s:
                    ball.set_smasher_state(currentLevel.ballSpeed, 0)

                    # Detect for brick collisions

            testbrick = pygame.sprite.spritecollideany(ball, bricks)
            if testbrick:

                if ball.smasher_state:
                    for testbrick3 in bricks:
                        (a, b) = brickAdjacency(testbrick3, testbrick)
                        if a + b == 1:
                            ballEffect(ball, testbrick3)
                    if ballCollideOnce(ball, testbrick, 0, 0):
                        break 

                bricks.remove(testbrick)
                testbrick2 = pygame.sprite.spritecollideany(ball, bricks)   # Detecting for 2 brick collisions at once.
                bricks.add(testbrick)
                if testbrick2:
                    (sx, sy) = brickAdjacency(testbrick, testbrick2)
                    if ballCollideOnce(ball, testbrick, sx, sy):
                        break
                else:
                    if ballCollideOnce(ball, testbrick, 0, 0):
                        break                                               # If the ball kills a brick, exit the ball movement for-loop (i.e.
                                                                            # cut the ball's movement this frame short).

def brickAdjacency(brick1, brick2):
    px = brick2.rect.centerx - brick1.rect.centerx
    py = brick2.rect.centery - brick1.rect.centery
    sx = 0
    sy = 0
    if (px == BRICKWIDTH) or (px == -BRICKWIDTH):                           # The ball simultaneously hits two bricks horizontally adjacent
        if py == 0:                                                         # to each other. (The collision was at the top or bottom.)
            sx = 1
    if (py == BRICKHEIGHT) or (py == -BRICKHEIGHT):                         # The ball simultaneously hits two bricks vertically adjacent
        if px == 0:                                                         # to each other. (The collision was at the left or right.)
            sy = 1
    if sx + sy == 2:
        sx = 0                                                              # Note that this special case can only occur when the ball
        sy = 0                                                              # hits a corner of some (both) brick(s). i.e. X O
                                                                            #                                               X
    return (sx, sy)


def ballCollideOnce(ball, targetbrick, special_x, special_y):       # Returns 1 if brick killed, 0 otherwise.
    dx = ball.x_coord - targetbrick.rect.centerx
    dy = ball.y_coord - targetbrick.rect.centery
    ball_x = 0
    ball_y = 0
    if (dx > 0.5*(BRICKWIDTH + BALLWIDTH) - 2):     # Ball is to the right of brick
        ball_x = 1
    elif (dx < 2 - 0.5*(BRICKWIDTH + BALLWIDTH)):   # Ball is to the left of brick
        ball_x = -1
    if (dy > 0.5*(BRICKHEIGHT + BALLHEIGHT) - 2):   # Ball is below the brick
        ball_y = 1
    elif (dy < 2 - 0.5*(BRICKHEIGHT + BALLHEIGHT)): # Ball is above the brick
        ball_y = -1
    
    if (ball_x + ball.x_dir == 0) and (special_x == 0):         # Ball hit a vertical side of the brick 
        ball.x_dir = -ball.x_dir                                # AND did not hit two horizontally adjacent bricks simultaneously
        
    if (ball_y + ball.y_dir == 0) and (special_y == 0):         # Ball hit a horizontal side of the brick
        ball.y_dir = -ball.y_dir                                # AND did not hit two vertically adjacent bricks simultaneously
    
    return ballEffect(ball, targetbrick)

def ballEffect(ball, targetbrick):          # Returns 1 if brick killed, 0 otherwise.
    for x in range(0, ball.damage):
        ix = targetbrick.rect.centerx
        iy = targetbrick.rect.centery
        t = targetbrick.damage()
        
        currentLevel.Score += int(100 * ((currentLevel.multiplier) ** 2))
        currentLevel.multiplier = round(currentLevel.multiplier + 0.2, 1)

        if t:
            currentLevel.bricks -= 1
            match(t):
                case 11:        # Fireball
                    ball.set_heat_state(currentLevel.ballSpeed, 1)

                case 12:        # Extra balls: spawn 2 extra balls
                    ball1 = game_ball(ix - (BALLWIDTH) / 2, iy)
                    r1 = random.randint(15, 25)
                    r2 = random.randint(15, 25)
                    ball1.adjust_angle(r1, r2)
                    ball1.set_speed(currentLevel.ballSpeed)
                    ball1.x_dir = -1
                    ball2 = game_ball(ix + (BALLWIDTH) / 2, iy)
                    ball2.adjust_angle(r1 + 1, r2 + 1)
                    ball2.set_speed(currentLevel.ballSpeed)
                    balls.add(ball1, ball2)
                    currentLevel.ballCount += 2

                case 13:        # Iceball
                    ball.set_heat_state(currentLevel.ballSpeed, 2)

                case 14:        # Smasher ball
                    ball.set_smasher_state(currentLevel.ballSpeed, 1)

                case 15:        # Widen the player paddle
                    player.widen(True)

            return 1
    
