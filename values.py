from turtle import window_width
import pygame
from pygame.locals import *
import time, sys, random, math

        # COLOURS

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)

        # FONTS

fonts = [0 for x in range(0, 6)]
fonts[0] = pygame.font.SysFont("Agency FB, Verdana, Times New Roman", 16, False, False)
fonts[1] = pygame.font.SysFont("Agency FB, Verdana, Times New Roman", 20, False, False)
fonts[2] = pygame.font.SysFont("Agency FB, Verdana, Times New Roman", 24, False, False)
fonts[3] = pygame.font.SysFont("Agency FB, Verdana, Times New Roman", 32, True, False)
fonts[4] = pygame.font.SysFont("Agency FB, Verdana, Times New Roman", 40, True, False)
fonts[5] = pygame.font.SysFont("Agency FB, Verdana, Times New Roman", 80, True, False)

        # GAME HARDWARE

FPS = pygame.time.Clock()
WIDTH = 800
HEIGHT = 600

DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker")

filepath = "./sprites/"

        # OBJECT CLASSES

BRICKWIDTH = 75
BRICKHEIGHT = 30
BALLWIDTH = 16
BALLHEIGHT = 16
PLAYERSPEED = 13
WALLHEIGHT = 25

        # IMAGE AND GRAPHICS

main_image = pygame.image.load(filepath + "sprites.png")

def getImageCoords(imageType, isSelected = False):
    match(imageType):

                # BUTTONS 

        case 1:     # Big buttons
            if isSelected:
                return (350, 0, 350, 100)
            else:
                return (0, 0, 350, 100)
        case 2:     # Medium buttons
            if isSelected: 
                return (0, 400, 250, 100)
            else:
                return (0, 200, 250, 100)
        case 3:     # Pause button
            return (450, 100, 100, 100)
        case 4:     # Play button
            return (550, 100, 100, 100)
        case 5:     # Stop button 
            return (650, 100, 100, 100)


        case 100 | 110:   # Player paddle
            return (0, 100, 350, 100)

                # BRICKS

        case 101:   # Red brick
            return (250, 200, 250, 100)
        case 102:   # Blue brick
            return (250, 300, 250, 100)
        case 103:   # Green brick
            return (250, 400, 250, 100)
        case 104:   # Orange brick
            return (250, 500, 250, 100)
        case 105:   # Purple brick
            return (250, 600, 250, 100)

                # POWERUP BRICKS

        case 111:   # Fire brick
            return (500, 200, 250, 100)
        case 112:   # Extra balls brick
            return (500, 300, 250, 100)
        case 113:   # Slowball Brick
            return (500, 400, 250, 100)
        case 114:   # Smasher brick
            return (500, 500, 250, 100)
        case 115:
            return (500, 600, 250, 100)

        case 200:   # Wall
            return (350, 100, 100, 100)

                # BALLS

        case 201:   # Default ball
            return (750, 200, 64, 64)
        case 202:   # Fireball
            return (750, 264, 64, 64)
        case 203:   # Slowball
            return (750, 328, 64, 64)
        case 204:   # Smasher ball
            return (750, 392, 64, 64)

def getImageSize(imageType):
    match(imageType):
        case 1:
            return (175, 50)
        case 2:
            return (100, 40)
        case x if 3 <= x <= 5:
            return (50, 50)
        case 100:
            return (2*BRICKWIDTH, BRICKHEIGHT)
        case 110:       # Extended Player Paddle
            return (3*BRICKWIDTH, BRICKHEIGHT)
        case x if 101 <= x <= 105:
            return (BRICKWIDTH, BRICKHEIGHT)
        case x if 111 <= x <= 115:
            return (BRICKWIDTH, BRICKHEIGHT)
        case 200:
            return (WALLHEIGHT, WALLHEIGHT)
        case x if 201 <= x <= 204:
            return (BALLWIDTH, BALLHEIGHT)

def getImage(imageType, isSelected = False):
    return pygame.transform.scale(main_image.subsurface(getImageCoords(imageType, isSelected)), getImageSize(imageType))

            # OBJECT CLASSES

class playerPaddle(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = getImage(100)
        self.rect = self.image.get_rect()
        self.rect.center = ((WIDTH + 32)/2, HEIGHT - 48)
        self.wideTimer = 0
        self.wideState = False

    def reset(self):
        self.widen(False)
        self.rect.center = ((WIDTH + 32)/2, HEIGHT - 48)

    def widen(self, extendedBool):
        oldCenter = self.rect.center
        if extendedBool == True:
            self.image = getImage(110)
        else:
            self.image = getImage(100)
        self.wideState = extendedBool
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter
        self.wideTimer = 0

    def move(self):
        mouse_x = pygame.mouse.get_pos()[0]
        if mouse_x < WALLHEIGHT:
            self.rect.centerx = WALLHEIGHT
        elif mouse_x > WIDTH - WALLHEIGHT:
            self.rect.centerx = WIDTH - WALLHEIGHT
        else:
            self.rect.centerx = mouse_x

    def move_keys(self, k_left, k_right):
        # keyPresses = pygame.key.get_pressed()
        if k_left and self.rect.left > WALLHEIGHT:
            self.rect.move_ip(-PLAYERSPEED, 0)
        if k_right and self.rect.right < WIDTH - WALLHEIGHT:
            self.rect.move_ip(PLAYERSPEED, 0)

class brick(pygame.sprite.Sprite):

    def __init__(self, typeIndex, x_c, y_c):
        super().__init__()
        self.durability = 0
        match(typeIndex):
            case x if 49 <= ord(x) <= 53:
                typeID = int(typeIndex)
                self.durability = int(typeIndex)
            case 'f':               # Fireball
                typeID = 11
                self.durability = 1
            case 'e':               # Extra balls
                typeID = 12
                self.durability = 1
            case 'i':               # Iceball
                typeID = 13
                self.durability = 1
            case 's':               # Smasher ball
                typeID = 14
                self.durability = 1
            case 'w':               # Widen the paddle
                typeID = 15
                self.durability = 1
        self.typeID = typeID
        self.image = getImage(100 + self.typeID)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x_c, y_c)

    def damage(self):               # Returns TRUE if a brick was destroyed.
        self.durability -= 1
        if self.durability == 0:
            t = self.typeID
            self.kill()
            match(t):
                case x if 11 <= x <= 15:
                    return x
            return 1
        else:
            self.typeID -= 1
            self.image = getImage(100 + self.typeID)
        return 0

class wall(pygame.sprite.Sprite):
    def __init__(self, x_c, y_c):
        super().__init__()
        self.image = getImage(200)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x_c, y_c)

class game_ball(pygame.sprite.Sprite):
    def __init__(self, init_x = (WIDTH + 32)/2, init_y = HEIGHT - 300):
        super().__init__()
        self.image = getImage(201)
        self.rect = self.image.get_rect()

        self.x_coord = init_x
        self.y_coord = init_y
        self.rect.center = (int(self.x_coord), int(self.y_coord))

        self.x_speed = 0.0
        self.y_speed = 1.0
        self.total_speed = 1.0

        self.x_dir = 1      # 1 for right, -1 for left
        self.y_dir = 1      # 1 for down, -1 for up

        ''' Powerup states: 0 for default
                            Heat_State: 1 for fireball, 2 for slowball. These cannot be simultaneously active
                            Smasher_State: 1 for smasher. This can be simultaneously active with Heat_State.
        '''
        self.heat_state = 0         # 0, 1 or 2
        self.heat_time = 0
        self.smasher_state = 0      # 0 or 1
        self.smasher_time = 0

        self.damage = 1

    def move_once(self):
        x_once = self.x_speed / self.total_speed
        y_once = self.y_speed / self.total_speed
        match self.x_dir:
            case -1:
                dx = int(self.x_coord - x_once) - int(self.x_coord)
                if dx == -1:
                    self.rect.move_ip(-1, 0)
                self.x_coord -= x_once
            case 1:
                dx = int(self.x_coord + x_once) - int(self.x_coord)
                if dx == 1:
                    self.rect.move_ip(1, 0)
                self.x_coord += x_once
        match self.y_dir:
            case -1:
                dy = int(self.y_coord - y_once) - int(self.y_coord)
                if dy == -1:
                    self.rect.move_ip(0, -1)
                self.y_coord -= y_once
            case 1:
                dy = int(self.y_coord + y_once) - int(self.y_coord)
                if dy == 1:
                    self.rect.move_ip(0, 1)
                self.y_coord += y_once

    def adjust_angle(self, dx, dy):                     # Adjusts the angle so that horizontal displacement is dx and vertical
                                                        # displacement is dy.
        self.x_speed = self.total_speed * (dx / math.sqrt(dx**2 + dy**2))
        self.y_speed = self.total_speed * (dy / math.sqrt(dx**2 + dy**2))

    def set_speed(self, speed):                         # Sets new speed, preserving angular displacement.
        old_speed = self.total_speed
        self.total_speed = speed
        self.x_speed = self.x_speed / old_speed * speed
        self.y_speed = self.y_speed / old_speed * speed

    def set_heat_state(self, defaultSpeed, newState):                 # 0 for default, 1 for fireball, 2 for slow ball.
        oldState = self.heat_state
        self.heat_time = 0
        if oldState == newState:
            return
        self.heat_state = newState
        c = 1
        if self.smasher_state == 1:
            c = 9/10
        match(newState):
            case 0:
                self.set_speed(defaultSpeed * c)
                self.damage = 1
                if self.smasher_state == 1:
                    self.image = getImage(204)
                else:
                    self.image = getImage(201)
            case 1:
                self.set_speed(round(defaultSpeed * 10 / 9 * c, 1))
                self.damage = 2
                self.image = getImage(202)
            case 2:
                self.set_speed(round(defaultSpeed * 2 / 3 * c, 1))
                self.damage = 1
                self.image = getImage(203)

    def set_smasher_state(self, defaultSpeed, newState):
        oldState = self.smasher_state
        self.smasher_time = 0
        if oldState == newState:
            return
        self.smasher_state = newState
        c = 1
        match(self.heat_state):
            case 1:
                c = 10/9
            case 2:
                c = 2/3
        match(newState):
            case 0:
                self.set_speed(defaultSpeed * c)
                self.image = getImage(201 + self.heat_state)
            case 1:
                self.set_speed(round(defaultSpeed * 9 / 10 * c, 1))
                self.image = getImage(204)