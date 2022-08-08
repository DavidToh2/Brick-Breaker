from cmath import e
import pygame
from pygame.locals import *
import time, sys, random

pygame.init()

from values import *

                # INITIALISE THE GAME.

from level import *
from menu import *

def displayGameState(gameStateID):           # This function toggles which buttons are visible.
    match(gameStateID):
        case 1:                 # IN GAME
            pause_button.visible(True)
            resume_button.visible(False)
            stop_button.visible(False)
        case 2:                 # GAME PAUSED
            pause_button.visible(False)
            resume_button.visible(True)
            stop_button.visible(True)
        case 3:                 # INITIALISING GAME
            for button in menuButtons:
                button.visible(False)
        case 4:                 # Stopping game, resetting everything
            pause_button.visible(False)
            resume_button.visible(False)
            stop_button.visible(False)

        case 1000:              # MAIN MENU
            currentLevel.__init__()
            for button in mainButtons:
                button.visible(True)
            for button in levelButtons:
                button.visible(False)
            quit_button.move(((WIDTH - 175)/2, 160))
        case 1001:              # LEVEL SELECT
            for button in mainButtons:
                button.visible(True)
            for button in levelButtons:
                button.visible(True)
            quit_button.move(((WIDTH - 175)/2, 500))

    return gameStateID

gameState = 1000
displayGameState(4)
displayGameState(1000)

        # TABLE OF BUTTON CALL INDEXES: (initialised in menu.py)
        # 0 - QUIT GAME
        # 1 to 15 - INITIALISE LEVEL NUMBER
        # 256 - TOGGLE LEVEL DISPLAY
        # 1024 - PAUSE GAME

def execute(callIndex):
    global gameState
    match(callIndex):

        case 0:                         # Close the application.
            gameState = displayGameState(0)

        case num if 1 <= num < 16:      # Initialise a level.
            gameState = 3
            currentLevel.loadLevel(num)

        case 256:                       # Toggle level display in menus.
            if gameState == 1000:
                gameState = displayGameState(1001)
            elif gameState == 1001:
                gameState = displayGameState(1000)

        case 401:                       # Pause the game.
            gameState = displayGameState(2)

            pygame.draw.rect(DISPLAY, BLUE, (100, 100, WIDTH - 200, HEIGHT - 200))
            DISPLAY.blit(fonts[5].render("GAME PAUSED", True, WHITE), ((WIDTH - 350)/2, (HEIGHT - 80)/2))
            pygame.display.update()

            time.sleep(0.3)

        case 402:                       # Resume the game.
            gameState = displayGameState(1)
            time.sleep(0.3)

        case 403:                       # Manually stop the game.
            DISPLAY.fill(BLUE)
            gameState = displayGameState(4)

DISPLAY.fill(BLACK)

mousePressed = False

while gameState:

    FPS.tick(60)

    mousePressed = False

    for event in pygame.event.get(pygame.QUIT):
        if event.type == pygame.QUIT:
            gameState = 0

    for event in pygame.event.get(MOUSEBUTTONDOWN):
        if event.type == MOUSEBUTTONDOWN:
            mousePressed = True

    keyPresses = pygame.key.get_pressed()

    match(gameState):

        case 1:                 # Running the game.

            DISPLAY.fill(BLACK)
            
            for event in pygame.event.get():
                if event.type == SPEED_UP and gameState == 1:
                    currentLevel.ballSpeed += 0.1
            
            player.move_keys(keyPresses[K_LEFT], keyPresses[K_RIGHT])
            update()

            # DISPLAY.blit(fonts[0].render(f"x = {ball.x_coord}", True, WHITE), (50, HEIGHT-50))
            # DISPLAY.blit(fonts[0].render(f"y = {ball.y_coord}", True, WHITE), (50, HEIGHT-30))

            fps = round(FPS.get_fps(), 3)
            DISPLAY.blit(fonts[0].render(f"FPS = {fps}", True, WHITE), (50, HEIGHT - 70))

            DISPLAY.blit(fonts[1].render(f"Score: {currentLevel.Score}", True, WHITE), (WIDTH - 150, HEIGHT - 70))
            DISPLAY.blit(fonts[1].render(f"Multiplier: x{currentLevel.multiplier}", True, WHITE), (WIDTH - 150, HEIGHT - 40))

            game_entities.draw(DISPLAY)          # Inbuilt short-cut function to avoid having to do a DISPLAY.blit(individual entity) loop.
            balls.draw(DISPLAY)

            for buttons in gameStateButtons:
                if buttons.drawOut():
                    if buttons.checkInput(keyPresses[buttons.keyBind], mousePressed):
                        # print(f"Executing function {buttons.callF()}")
                        execute(buttons.callF())
                        break

            if currentLevel.ballCount == 0:
                DISPLAY.fill(RED)
                DISPLAY.blit(fonts[5].render("Game Over", True, BLACK), (100, 100))
                gameState = displayGameState(4)

            if currentLevel.bricks == 0:
                DISPLAY.fill(GREEN)
                DISPLAY.blit(fonts[5].render("You won!", True, BLACK), (100, 100))
                gameState = displayGameState(4)

        case 2:                 # Game is paused.

            for buttons in gameStateButtons:
                if buttons.drawOut():
                    if buttons.checkInput(keyPresses[buttons.keyBind], mousePressed):
                        # print(f"Executing function {buttons.callF()}")
                        execute(buttons.callF())
        
        case 3:                 # Game is being initialised.

            player.reset()
            game_entities.add(player)
            ball1 = game_ball()
            balls.add(ball1)
            ball1.set_speed(currentLevel.ballSpeed)
            gameState = displayGameState(1)

        case 4:                 # Game ended. Resetting everything.
                                # This case is satisfied when the game ends, whether or not you win, die, or manually stop it.
            
            DISPLAY.blit(fonts[4].render(f"You scored: {currentLevel.Score}", True, BLACK), (100, 200))
            currentLevel.updateHighScores("David", currentLevel.Score)
            pygame.display.update()
            time.sleep(2)
            gameState = displayGameState(1000)
            for entity in bricks:
                entity.kill()
                del entity
            for entity in balls:
                entity.kill()
                del entity

        case 1000 | 1001:       # In main menu

            DISPLAY.fill(BLACK)

            for buttons in menuButtons:
                if buttons.drawOut():                               # If button is visible and drawn out:
                    buttons.checkSelect()                           # Update button selection status (whether mouse is ontop of button)
                    if buttons.checkInput(False, mousePressed):     # If mouse is pressed on button (input detected):
                        execute(buttons.callF())                    # Call the button's executeID.
        
    pygame.display.update()

pygame.quit()
sys.exit()