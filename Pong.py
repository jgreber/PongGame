import random
import sys

import pandas
import pygame
import pygame.freetype
from sklearn.neighbors import KNeighborsRegressor

# Variables
WIDTH = 1200
HEIGHT = 800
BOARDER = 20
VELOCITY_LEVEL1 = 7
VELOCITY_LEVEL2 = 9
FRAMERATE = 35
PADDLEMOVE = 14
LEVEL_TIME = 32
VELOCITY_AGAINST_PC = 7

# white color
color_white = (255, 255, 255)
# black color
color_black = (0, 0, 0)
# light shade of the button
color_light = (170, 170, 170)
# dark shade of the button
color_dark = (50, 100, 100)
color_red = (255, 48, 48)


# Class
class Ball:
    RADIUS = 15

    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def show(self):
        global screen, fgColor
        pygame.draw.circle(screen, fgColor, (self.x, self.y), self.RADIUS)

    def hide(self):
        global screen, bgColor
        pygame.draw.circle(screen, bgColor, (self.x, self.y), self.RADIUS)

    def updatePosition(self):
        global screen, fgColor, bgColor, state

        newx = self.x + self.vx
        newy = self.y + self.vy

        if state != AGAINST_COMPUTER:
            paddleRangeMin = playPaddle.y - playPaddle.HEIGHT // 2
            paddleRangeMax = playPaddle.y + playPaddle.HEIGHT // 2

            if newx <= BOARDER + self.RADIUS:
                self.vx = -self.vx
                return True
            elif newy <= BOARDER + self.RADIUS or newy >= HEIGHT - BOARDER - self.RADIUS:
                self.vy = -self.vy
                return True
            elif newx + self.RADIUS >= WIDTH - playPaddle.WIDTH and (paddleRangeMin <= newy <= paddleRangeMax):
                self.vx = -self.vx
                return True
            else:
                self.hide()
                self.x = self.x + self.vx
                self.y = self.y + self.vy
                self.show()
        else:
            paddleRangeMinPC = playPaddlePC.y - playPaddlePC.HEIGHT // 2
            paddleRangeMaxPC = playPaddlePC.y + playPaddlePC.HEIGHT // 2

            paddleRangeMinI = playPaddleIAgainstPC.y - playPaddleIAgainstPC.HEIGHT // 2
            paddleRangeMaxI = playPaddleIAgainstPC.y + playPaddleIAgainstPC.HEIGHT // 2

            if newy <= BOARDER + self.RADIUS or newy >= HEIGHT - BOARDER - self.RADIUS:
                self.vy = -self.vy
                return True
            elif newx + self.RADIUS >= WIDTH - playPaddlePC.WIDTH and (paddleRangeMinPC <= newy <= paddleRangeMaxPC):
                self.vx = -self.vx
                return True
            elif newx <= BOARDER + self.RADIUS and (paddleRangeMinI <= newy <= paddleRangeMaxI):
                self.vx = -self.vx
                return True
            else:
                self.hide()
                self.x = self.x + self.vx
                self.y = self.y + self.vy
                self.show()


class Paddle:
    WIDTH = 20
    HEIGHT = 100

    def __init__(self, x, y, pcpaddle):
        self.x = x
        self.y = y
        self.pcpaddle = pcpaddle

    def show(self):
        global screen, fgColor
        pygame.draw.rect(screen, fgColor,
                         pygame.Rect(self.x - self.WIDTH, self.y - self.HEIGHT // 2, self.WIDTH, self.HEIGHT))

    def hide(self):
        global bgColor
        pygame.draw.rect(screen, bgColor,
                         pygame.Rect(self.x - self.WIDTH, self.y - self.HEIGHT // 2, self.WIDTH, self.HEIGHT))

    def updatePosition(self, move):
        if not self.pcpaddle:
            newY = self.y + move
        else:
            newY = move

        if newY - self.HEIGHT // 2 > BOARDER and newY + (self.HEIGHT // 2) < HEIGHT - BOARDER:
            self.hide()
            self.y = newY
            self.show()

    def paddleControl(self, playPaddlePCMove, state):
        if state == AGAINST_COMPUTER:
            if not self.pcpaddle:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]:
                    playPaddleIAgainstPC.updatePosition(-PADDLEMOVE)

                if keys[pygame.K_DOWN]:
                    playPaddleIAgainstPC.updatePosition(PADDLEMOVE)
            else:
                playPaddlePC.updatePosition(playPaddlePCMove)
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                playPaddle.updatePosition(-PADDLEMOVE)

            if keys[pygame.K_DOWN]:
                playPaddle.updatePosition(PADDLEMOVE)


class Button:
    def __init__(self, x, y, height, width, text=""):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.text = text

    def draw(self, color, color_txt):
        global screen
        # Call this method to draw the button on the screen
        # Outline
        pygame.draw.rect(screen, color_txt, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)
        # Rectangle
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), 0)
        # Text
        if self.text != '':
            font = pygame.font.SysFont('comicsans', 60)
            text = font.render(self.text, 1, color_txt)
            screen.blit(text, (
                self.x + (self.width // 2 - text.get_width() // 2),
                self.y + (self.height // 2 - text.get_height() // 2)))

    def isOver(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True

        return False


# Create objects
playBall = Ball(WIDTH - (Ball.RADIUS * 3), HEIGHT // 2, -VELOCITY_LEVEL1, -VELOCITY_LEVEL1)
playBall2 = Ball(WIDTH - (Ball.RADIUS * 3), HEIGHT // 2, -VELOCITY_LEVEL1, VELOCITY_LEVEL1)
playPaddle = Paddle(WIDTH, HEIGHT // 2, False)
playPaddlePC = Paddle(WIDTH, HEIGHT // 2, True)
playPaddleIAgainstPC = Paddle(BOARDER, HEIGHT // 2, False)
startAlone = Button(210, 350, 50, 400, "Start Alone")
startPC = Button(630, 350, 50, 400, "Start Against PC")
gameOverButton = Button(450, 320, 60, 300, "Game Over")
startAgainButton = Button(290, 420, 60, 300, "Start Again")
exitButton = Button(610, 420, 60, 300, "Exit")
level1Button = Button(500, 350, 50, 200, "Level 1")
level2Button = Button(500, 350, 50, 200, "Level 2")
level3Button = Button(500, 350, 50, 200, "Level 3")
level4Button = Button(500, 350, 50, 200, "Level 4")
winButton = Button(450, 320, 60, 300, "You Won")

# Initialisation
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Sounds
hitSound1 = pygame.mixer.Sound("/Users/jangreber/Documents/Projects/PongGame/Sounds/hitSound1.wav")
hitSound2 = pygame.mixer.Sound("/Users/jangreber/Documents/Projects/PongGame/Sounds/hitSound2.wav")
hitSound3 = pygame.mixer.Sound("/Users/jangreber/Documents/Projects/PongGame/Sounds/hitSound3.wav")
hitSound4 = pygame.mixer.Sound("/Users/jangreber/Documents/Projects/PongGame/Sounds/hitSound4.wav")
hitSound5 = pygame.mixer.Sound("/Users/jangreber/Documents/Projects/PongGame/Sounds/hitSound5.wav")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PONG")

fgColor = pygame.Color("WHITE")
bgColor = pygame.Color("BLACK")

pygame.draw.rect(screen, fgColor, pygame.Rect((0, 0), (WIDTH, BOARDER)))
pygame.draw.rect(screen, fgColor, pygame.Rect(0, 0, BOARDER, HEIGHT))
pygame.draw.rect(screen, fgColor, pygame.Rect(0, HEIGHT - BOARDER, WIDTH, BOARDER))

clock = pygame.time.Clock()

# States
INIT = 0
GAME_OVER = -1
LEVEL_1 = 1
LEVEL_2 = 2
LEVEL_3 = 3
LEVEL_4 = 4
AGAINST_COMPUTER = 5
WIN = 6

state = INIT

level1_init = True
level2_init = True
level3_init = True
level4_init = True
level_against_PC_init = True


# Methods
def updateScreen(level):
    pygame.display.flip()
    if level == LEVEL_1 or level == LEVEL_2 or level == AGAINST_COMPUTER:
        if playBall.updatePosition():
            sounds()
    if level == LEVEL_3 or level == LEVEL_4:
        playBall.updatePosition()
        playBall2.updatePosition()

    clock.tick(FRAMERATE)


def drawTxt(color, text):
    font = pygame.font.SysFont('comicsans', 40)
    text = font.render(text, 1, color)
    screen.blit(text, (40, 40))


def exitGame():
    pygame.quit()
    sys.exit()


def sounds():
    playnumber = random.randint(1, 5)
    if playnumber == 1:
        hitSound1.play()
    elif playnumber == 2:
        hitSound2.play()
    elif playnumber == 3:
        hitSound3.play()
    elif playnumber == 4:
        hitSound4.play()
    elif playnumber == 5:
        hitSound5.play()


def hideButtonAndText():
    pygame.draw.rect(screen, bgColor, pygame.Rect((BOARDER, BOARDER), (WIDTH - 2 * BOARDER, HEIGHT - 2 * BOARDER)))


# data production
# sample = open("gameDataPC.csv", "w")
# print("x,y,vx,vy,PaddlePC.y", file=sample)

# sample = open("gameData.csv", "w")
# print("x,y,vx,vy,Paddle.y", file=sample)

pong = pandas.read_csv("/Users/jangreber/Documents/Projects/PongGame/gameData.csv")
pong = pong.drop_duplicates()

# pong = pandas.read_csv("/Users/jangreber/Documents/Projects/PongGame/gameDataPC.csv")
# pong = pong.drop_duplicates()

X = pong.drop(columns="Paddle.y")
Y = pong["Paddle.y"]

# X = pong.drop(columns="PaddlePC.y")
# Y = pong["PaddlePC.y"]

# Algorithm
algo = KNeighborsRegressor(n_neighbors=3)
# Train the algorithm
algo.fit(X, Y)

dataFrame = pandas.DataFrame(columns=['x', 'y', 'vx', 'vy'])

# Start Game
while True:

    pos = pygame.mouse.get_pos()

    if state == INIT:
        if startAlone.isOver(pos):
            startAlone.draw(color_light, color_white)
        else:
            startAlone.draw(color_dark, color_white)

        if startPC.isOver(pos):
            startPC.draw(color_light, color_white)
        else:
            startPC.draw(color_dark, color_white)

        e = pygame.event.poll()
        if e.type == pygame.MOUSEBUTTONDOWN and startAlone.isOver(pos):
            state = LEVEL_1
        elif e.type == pygame.MOUSEBUTTONDOWN and startPC.isOver(pos):
            state = AGAINST_COMPUTER
        elif e.type == pygame.QUIT:
            exitGame()

        updateScreen(state)

    elif state == LEVEL_1:
        if level1_init:
            hideButtonAndText()
            level_ticks = pygame.time.get_ticks()
            level1Button.draw(color_dark, color_white)
            pygame.draw.rect(screen, fgColor, pygame.Rect(0, 0, BOARDER, HEIGHT))
            level1_init = False

        drawTxt(color_white, "Level 1")

        if ((pygame.time.get_ticks() - level_ticks) / 1000) > 2:
            level1Button.draw(bgColor, bgColor)

        playBall.show()
        playPaddle.show()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exitGame()
        playPaddle.paddleControl(0, state)

        if playBall.x > WIDTH - BOARDER // 2:
            state = GAME_OVER
        elif ((pygame.time.get_ticks() - level_ticks) / 1000) > LEVEL_TIME:
            state = LEVEL_2

        updateScreen(state)
        # collecting data
        # print("{},{},{},{},{}".format(playBall.x, playBall.y, playBall.vx, playBall.vy, playPaddle.y), file=sample)

    elif state == LEVEL_2:
        if level2_init:
            hideButtonAndText()
            level_ticks = pygame.time.get_ticks()
            level2Button.draw(color_dark, color_white)
            if playBall.vx > 0:
                playBall.vx = VELOCITY_LEVEL2
            else:
                playBall.vx = -VELOCITY_LEVEL2
            if playBall.vy > 0:
                playBall.vy = VELOCITY_LEVEL2
            else:
                playBall.vy = -VELOCITY_LEVEL2
            level2_init = False

        drawTxt(color_white, "Level 2")

        if ((pygame.time.get_ticks() - level_ticks) / 1000) > 2:
            level2Button.draw(bgColor, bgColor)

        playBall.show()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exitGame()

        playPaddle.paddleControl(0, state)

        if playBall.x > WIDTH - BOARDER // 2:
            state = GAME_OVER
        elif ((pygame.time.get_ticks() - level_ticks) / 1000) > LEVEL_TIME:
            state = LEVEL_3

        updateScreen(state)

    elif state == LEVEL_3:
        if level3_init:
            hideButtonAndText()
            level_ticks = pygame.time.get_ticks()
            level3Button.draw(color_dark, color_white)
            if playBall.vx > 0:
                playBall.vx = VELOCITY_LEVEL1
            else:
                playBall.vx = -VELOCITY_LEVEL1
            if playBall.vy > 0:
                playBall.vy = VELOCITY_LEVEL1
            else:
                playBall.vy = -VELOCITY_LEVEL1
            level3_init = False

        drawTxt(color_white, "Level 3")

        if ((pygame.time.get_ticks() - level_ticks) / 1000) > 2:
            level3Button.draw(bgColor, bgColor)

        playBall.show()
        playBall2.show()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exitGame()

        playPaddle.paddleControl(0, state)

        if playBall.x > WIDTH - BOARDER // 2 or playBall2.x > WIDTH - BOARDER // 2:
            state = GAME_OVER
        elif ((pygame.time.get_ticks() - level_ticks) / 1000) > LEVEL_TIME:
            state = LEVEL_4

        updateScreen(state)

    elif state == LEVEL_4:
        if level4_init:
            hideButtonAndText()
            level_ticks = pygame.time.get_ticks()
            level4Button.draw(color_dark, color_white)
            if playBall.vx > 0:
                playBall.vx = VELOCITY_LEVEL2
            else:
                playBall.vx = -VELOCITY_LEVEL2
            if playBall.vy > 0:
                playBall.vy = VELOCITY_LEVEL2
            else:
                playBall.vy = -VELOCITY_LEVEL2

            if playBall2.vx > 0:
                playBall2.vx = VELOCITY_LEVEL2
            else:
                playBall2.vx = -VELOCITY_LEVEL2
            if playBall2.vy > 0:
                playBall2.vy = VELOCITY_LEVEL2
            else:
                playBall2.vy = -VELOCITY_LEVEL2

            level4_init = False

        drawTxt(color_white, "Level 4")

        if ((pygame.time.get_ticks() - level_ticks) / 1000) > 2:
            level4Button.draw(bgColor, bgColor)

        playBall.show()
        playBall2.show()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exitGame()

        playPaddle.paddleControl(0, state)

        if playBall.x > WIDTH - BOARDER // 2 or playBall2.x > WIDTH - BOARDER // 2:
            state = GAME_OVER

        updateScreen(state)

    elif state == AGAINST_COMPUTER:
        if level_against_PC_init:
            hideButtonAndText()
            playBall.vx = -VELOCITY_AGAINST_PC
            playBall.vy = -VELOCITY_AGAINST_PC
            level_against_PC_init = False

        pygame.draw.rect(screen, bgColor, pygame.Rect(0, BOARDER, BOARDER, HEIGHT - 2 * BOARDER))
        playBall.show()
        playPaddleIAgainstPC.show()
        playPaddlePC.show()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exitGame()

        toPredict = dataFrame.append({'x': playBall.x, 'y': playBall.y, 'vx': playBall.vx, 'vy': playBall.vy},
                                     ignore_index=True)
        playPaddlePCMove = int(algo.predict(toPredict))

        playPaddleIAgainstPC.paddleControl(0, state)
        playPaddlePC.paddleControl(playPaddlePCMove, state)

        if playBall.x < BOARDER // 2:
            state = GAME_OVER
        elif playBall.x > WIDTH - BOARDER:
            state = WIN

        updateScreen(state)

        # collecting data
        # print("{},{},{},{},{}".format(playBall.x, playBall.y, playBall.vx, playBall.vy, playPaddlePC.y), file=sample)

    elif state == GAME_OVER:
        playBall.hide()
        playBall2.hide()
        playPaddle.hide()
        playPaddlePC.hide()
        playPaddleIAgainstPC.hide()
        gameOverButton.draw(color_red, color_white)

        if startAgainButton.isOver(pos):
            startAgainButton.draw(color_light, color_white)
        else:
            startAgainButton.draw(color_dark, color_white)

        if exitButton.isOver(pos):
            exitButton.draw(color_light, color_white)
        else:
            exitButton.draw(color_dark, color_white)

        e = pygame.event.poll()
        if e.type == pygame.MOUSEBUTTONDOWN and startAgainButton.isOver(pos):
            state = INIT
            hideButtonAndText()
            level1_init = True
            level2_init = True
            level3_init = True
            level4_init = True
            level_against_PC_init = True

            playBall.x = WIDTH - (Ball.RADIUS * 3)
            playBall.y = HEIGHT // 2
            playBall.vx = -VELOCITY_LEVEL1
            playBall.vy = -VELOCITY_LEVEL1

            playBall2.x = WIDTH - (Ball.RADIUS * 3)
            playBall2.y = HEIGHT // 2
            playBall2.vx = -VELOCITY_LEVEL1
            playBall2.vy = VELOCITY_LEVEL1
        elif e.type == pygame.MOUSEBUTTONDOWN and exitButton.isOver(pos):
            exitGame()
        elif e.type == pygame.QUIT:
            exitGame()

        updateScreen(state)

    elif state == WIN:
        playBall.hide()
        playPaddlePC.hide()
        playPaddleIAgainstPC.hide()
        winButton.draw(color_red, color_white)

        if startAgainButton.isOver(pos):
            startAgainButton.draw(color_light, color_white)
        else:
            startAgainButton.draw(color_dark, color_white)

        if exitButton.isOver(pos):
            exitButton.draw(color_light, color_white)
        else:
            exitButton.draw(color_dark, color_white)

        e = pygame.event.poll()
        if e.type == pygame.MOUSEBUTTONDOWN and startAgainButton.isOver(pos):
            state = INIT
            hideButtonAndText()

            playBall.x = WIDTH - (Ball.RADIUS * 3)
            playBall.y = HEIGHT // 2
            playBall.vx = -VELOCITY_LEVEL1
            playBall.vy = -VELOCITY_LEVEL1

        elif e.type == pygame.MOUSEBUTTONDOWN and exitButton.isOver(pos):
            exitGame()
        elif e.type == pygame.QUIT:
            exitGame()

        updateScreen(state)
