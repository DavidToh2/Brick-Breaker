
from tkinter import FALSE
from matplotlib.pyplot import text
import pygame
from pygame.locals import *
import time, sys, random
from values import *
from level import *



mainButtons = pygame.sprite.Group()     # BUTTONS DEFINED IN MENU.PY
levelButtons = pygame.sprite.Group()
menuButtons = pygame.sprite.Group()

class button(pygame.sprite.Sprite):
    def __init__(self, button_type, c_topleft, text, text_size, call_index, text_displacement = (0, 0), key_bind = None):
        super().__init__()
        self.isSelected = False
        self.isVisible = True
        self.buttonType = button_type

        self.image = getImage(button_type)
        self.rect = self.image.get_rect()
        self.rect.topleft = c_topleft

        self.text = text
        if self.text != None:
            self.textColor = BLACK
            self.textSurf = fonts[text_size].render(self.text, True, self.textColor)
            self.textDisplacement = text_displacement
        
        self.callIndex = call_index

        if key_bind != None:
            self.keyBind = key_bind

    def move(self, c_topleft):
        self.rect.topleft = c_topleft

    def drawOut(self):
        if self.isVisible == True:
            DISPLAY.blit(self.image, self.rect)
            if self.text != None:
                DISPLAY.blit(self.textSurf, self.rect.move(self.textDisplacement))
            return True
        else:
            return False

    def callF(self):
        return self.callIndex

    def checkSelect(self):          # FOR MENU BUTTONS ONLY.
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.select(True)
        else:
            self.select(False)

    def checkInput(self, keyBool, mouseBool):
        if (self.rect.collidepoint(pygame.mouse.get_pos()) and mouseBool) or keyBool:
            return True
        return False

    def select(self, isSelected):
        self.isSelected = isSelected
        self.image = getImage(self.buttonType, isSelected)

    def visible(self, isVisible):
        self.isVisible = isVisible

start_button = button(1, ((WIDTH - 175)/2, 100), "SELECT LEVEL", 3, 256, (10, 5))          
quit_button = button(1, ((WIDTH - 175)/2, 500), "QUIT GAME", 4, 0, (10, 0))
mainButtons.add(start_button, quit_button)


for y in range(0, 5):
    for x in range(0, 3): 
        levelNo = 1 + x + 3*y
        levelButtons.add(button(2, (WIDTH/2 - 170 + 120*x, 170 + 60*y), "LEVEL " + str(levelNo), 2, levelNo, (20, 5)))

menuButtons.add(mainButtons, levelButtons)

pause_button = button(3, (30, 30), None, None, 401, None, K_LCTRL)
resume_button = button(4, (30, 30), None, None, 402, None, K_LCTRL)
stop_button = button(5, (90, 30), None, None, 403, None, K_RCTRL)

gameStateButtons = pygame.sprite.Group()
gameStateButtons.add(pause_button, resume_button, stop_button)