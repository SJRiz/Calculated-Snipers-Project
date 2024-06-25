################### RELIES ON THE CONSOLE TO PLAY ###################

import math
import os
import pygame
import random
import time

SCREENWIDTH  = 612
SCREENHEIGHT = 512
FPS = 144

sniperPos = (15, 230)

IMAGES, HITMASKS = {}, {}

SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.init()

IMAGES['menu'] = pygame.image.load('assets/menu.png').convert_alpha()
IMAGES['tutorial'] = pygame.image.load('assets/tutorial.png').convert_alpha()
IMAGES['rules'] = pygame.image.load('assets/rules.png').convert_alpha()
IMAGES['grid'] = pygame.image.load('assets/thegrid.png').convert_alpha()
IMAGES['dot'] = pygame.image.load('assets/dot.png').convert_alpha()
IMAGES['target'] = pygame.image.load('assets/target.png').convert_alpha()
IMAGES['targetstand'] = pygame.image.load('assets/targetstand.png').convert_alpha()
IMAGES['rock'] = pygame.image.load('assets/obstructions/rock.png').convert_alpha()
IMAGES['sniper'] = pygame.image.load('assets/sniper.png').convert_alpha()
IMAGES['stand'] = pygame.image.load('assets/stand.png').convert_alpha()


################# FUNCTIONS RELATED TO LEVEL GENERATION #################

#  Returns a hitmask using an image's alpha
def getHitmask(image):
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

#  Hitmasks for graph dot and target
HITMASKS['dot'] = (
  getHitmask(IMAGES['dot'])
)

HITMASKS['target'] = (
  getHitmask(IMAGES['target'])
)

HITMASKS['rock'] = (
  getHitmask(IMAGES['rock'])
)

#  Creates the level. Make the locations for the target and obstructions
def GenerateLevel(difficultyFactor):
  tPosX = random.randint(500, 560)
  tPosY = random.randint(100, 400)
  SCREEN.fill((255,255,255))
  obstructionList = []

  #  Places a boulder and puts it in the obstruction list. Also checks distance between each boulder so they aren't too close.
  def BoulderSpawn(xMin, xMax, yMin, yMax):
    while True:
      dist = 60
      randX = random.randint(xMin, xMax)
      randY = random.randint(yMin, yMax)
      randomPos = (randX, randY)
      if not len(obstructionList) == 0:
        for obstruction in obstructionList:
          obstructionDist = math.hypot(obstruction[1][0] - randX, obstruction[1][1] - randY)
          if obstructionDist < dist:
            dist = obstructionDist
      if dist >= 60:
        distFromSniper = math.hypot(randX - sniperPos[0], randY - sniperPos[1])
        distFromTarget = math.hypot(randX - tPosX, randY - tPosY)
        if distFromSniper > 200 and distFromTarget > 100:
          break

    obstructionList.append([IMAGES['rock'], randomPos])

  num = 0

  #  Loads boulders on the top.
  while num < difficultyFactor/2:
    BoulderSpawn(-10, 540, -10, 300)
    num += 1

  #  Loads boulders on the bottom.
  while num < difficultyFactor:
    BoulderSpawn(50, 540, 300, 550) 
    num += 1

  return tPosX, tPosY, obstructionList

#  Sets up the level by placing the target, obstructions, etc.
def SetupLevel(posX, posY, obstructions):
  SCREEN.blit(IMAGES['grid'], (-6,-6))

  SCREEN.blit(IMAGES['targetstand'], (posX + 15, posY + 10))
  SCREEN.blit(IMAGES['target'], (posX, posY))

  SCREEN.blit(IMAGES['sniper'], sniperPos)
  SCREEN.blit(IMAGES['stand'], (sniperPos[0] - 35, sniperPos[1] + 50))

  for obstruction in obstructions:
    SCREEN.blit(obstruction[0], obstruction[1])

  pygame.display.update()




#################  FUNCTIONS RELATED TO DATA SAVING #################

#  Open the file and rewrite highest level
def save(level):
  openFile = open('highestlevel.txt', 'w')
  openFile.write(str(level))
  openFile.close()

#  Loads the file to check for highest level
def load():
  readFile = open('highestlevel.txt', 'r')
  highestLevel = readFile.read()
  readFile.close()
  return highestLevel


#################  FUNCTIONS RELATED TO CALCULATING THE MATH EQUATION #################

#  Purpose is to find subfunctions within the equation (ex. find sin, cos, log, etc.)
def FindFunction(functionName, equation):

  startingVal = 0
  while True:
    try:
      FunctionLocation = equation.find(functionName, startingVal)
      if FunctionLocation >= 0 and FunctionLocation < len(equation):
        numberLocation = FunctionLocation + len(functionName)

        #  Counts the amount of brackets within the function. If it drops below 0, then that means the function has ended
        BracketCounter = 0
        numberLocationEnd = FunctionLocation
        for letter in range(len(equation)):
          if letter >= FunctionLocation:
            if equation[letter] == "(":
              BracketCounter += 1
            elif equation[letter] == ")":
              BracketCounter -= 1
              if BracketCounter == 0:
                numberLocationEnd = letter
                break

        functionEquation = (equation[FunctionLocation:(numberLocationEnd + 1)])
        innerEquation = (equation[numberLocation:numberLocationEnd])

        #  Clean up/calculate equations and functions within the function (ex. sin(sin(pi/6)) would simplify to sin(0.5) instead)
        #  Basically just recalling the same function to calculate the subfunction/equation
        innerEquationValue = eval(CleanupEquation(innerEquation))

        if functionName == "sin(":
          innerEquationValue = math.sin(innerEquationValue)
        elif functionName == "cos(":
          innerEquationValue = math.cos(innerEquationValue)
        elif functionName == "ln(":
          innerEquationValue = math.log(innerEquationValue, math.e)
        elif functionName == "sqrt(":
          innerEquationValue = math.sqrt(innerEquationValue)

        equation = equation.replace(functionEquation, str(innerEquationValue))
      else:
        break
      startingVal = numberLocationEnd
    except:
      break
  return equation



#  Since the "eval()" function has different syntax for operations, we have to make the expression compatible
#  Turns x^2 to x**2, and 3(x)2  to 3*x*2 etc.
def CleanupEquation(equation):

  if equation.find("^") >= 0:
    equation = equation.replace("^", "**")
  if equation.find("e") >= 0:
    equation = equation.replace("e", str(math.e))
  if equation.find("pi") >= 0:
    equation = equation.replace("pi", str(math.pi))
  if equation.find("log") >= 0:
    equation = equation.replace("log", "ln")

  # Look for sin, cos, ln, and sqrt function
  equation = FindFunction("sin(", equation)
  equation = FindFunction("cos(", equation)
  equation = FindFunction("ln(", equation)
  equation = FindFunction("sqrt(", equation)

  # Look for multiplications via opening brackets
  # Basically loops through all the brackets and sees if its directly next to a real number
  startingVal = 1
  while True:
    openingBracketLocation = equation.find("(", startingVal)
    if openingBracketLocation >= 0 and openingBracketLocation < len(equation):
      numberLocation = openingBracketLocation - 1
      #  If the number next to bracket is not a closing bracket or a number, then don't worry about it
      try:
        if equation[numberLocation] != ")":
          float(equation[numberLocation])
        equation = ''.join((equation[:openingBracketLocation],'*', equation[openingBracketLocation:]))
        openingBracketLocation += 1
      except:
        openingBracketLocation = openingBracketLocation
    else:
      break
    startingVal = openingBracketLocation + 1

  # Look for multiplications via closing brackets
  # Basically same code as above but with closing brackets
  startingVal = 1

  while True:
    closingBracketLocation = equation.find(")", startingVal)
    if closingBracketLocation >= 1 and closingBracketLocation < len(equation):
      numberLocation = closingBracketLocation + 1
      try:
        if equation[numberLocation] != "(":
          float(equation[numberLocation])
        equation = ''.join((equation[:numberLocation],'*', equation[numberLocation:]))
        closingBracketLocation += 1
      except:
        closingBracketLocation = closingBracketLocation
    else:
      break
    startingVal = closingBracketLocation + 1
  return equation



#  The code that calculates each part of the function and graphs it. Also checks if the graph hits a part
def CalculateEquation(equation, tPosX, tPosY, obstructions):
  os.system('clear')
  x = 0
  yShift = 0
  errornum = 0
  dotTable = []

  while x <= 28.5:
    try:
      newEquation = equation.replace("x", "({})".format(str(x)))
      newEquation = CleanupEquation(newEquation)
      if x == 0:
        yShift = -(eval(newEquation))
      coords = [x, eval(newEquation) + yShift]
      PlotGraph(coords, dotTable, tPosX, tPosY, obstructions)
      crashChecker = checkCrash({'x': tPosX, 'y': tPosY}, dotTable, obstructions)

      #  If first value of crashChecker is true, that means it hit something
      if crashChecker[0]:
        #  If the second value is true, it hit the target.
        if crashChecker[1]:
          return "Hit"
        else:
          return "Miss"
    except:
      #  Might be an asymptote or undefined (x/0)
      errornum += 1
      #  If error happens more than 15 times then theres a problem
      if errornum > 20:
        os.system('clear')
        print("Equation invalid; syntax is not proper (ex: square brackets not allowed, missing bracket) or no values available.")
        return "Error"
    x += 0.1
    pygame.time.Clock().tick(FPS)
  return "Miss"



################# FUNCTIONS RELATED TO GRAPHING #################

#  Creates a dot in the position of the specificed coordinates
#  Alternates position between dots to reduce lag
def PlotGraph(coords, dotTable, tPosX, tPosY, obstructions):
  SCREEN.fill((255,255,255))

  if coords[1] != 'None':
    #  1 unit square is equal to 20 pixels by 20 pixels
    pos = (180 + coords[0]*20, 320 - coords[1]*20)
    dotTable.append([IMAGES['dot'], pos])

    if len(dotTable) > 500:
      dotTable.pop(0)

  for dot in dotTable:
    SCREEN.blit(dot[0], dot[1])

  SetupLevel(tPosX, tPosY, obstructions)
  pygame.display.update()


#  Returns True if a dot collides with an object. Returns 2 trues if it also collides with the target
def checkCrash(target, dots, obstructions):
    target['w'] = IMAGES['target'].get_width()
    target['h'] = IMAGES['target'].get_height()

    rockWidth = IMAGES['rock'].get_width()
    rockHeight = IMAGES['rock'].get_height()

    targetRect = pygame.Rect(target['x'], target['y'], target['w'], target['h'])
    dotW = IMAGES['dot'].get_width()
    dotH = IMAGES['dot'].get_height()

    for dot in dots:
        #  All dot rects
        dotRect = pygame.Rect(dot[1][0], dot[1][1], dotW, dotH)

        #  target, dots and obstructions hitmasks
        targetHitMask = HITMASKS['target']
        dotHitmask = HITMASKS['dot']
        rockHitmask = HITMASKS['rock']

        # if dot collided with rock
        for obstruction in obstructions:
          rockRect = pygame.Rect(obstruction[1][0], obstruction[1][1], rockWidth, rockHeight)
          rockCollide = pixelCollision(rockRect, dotRect, rockHitmask, dotHitmask)
          if rockCollide:
            return [True, False]

        # if dot collided with target
        targetCollide = pixelCollision(targetRect, dotRect, targetHitMask, dotHitmask)

        if targetCollide:
            return [True, True]

    return [False, False]


#  Checks if two objects collide and not just their rects
def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False




################# MAIN CODE #################

#  Main code of the game. Sets up the level, and recalls the code and ups the difficulty if they beat the level.
def main(difficultyFactor, level):
  tPosX, tPosY, obstructions = GenerateLevel(difficultyFactor)
  SetupLevel(tPosX, tPosY, obstructions)

  while True:
    print(" ")
    print("Current level:", level)
    print("World record:", load())
    print(" ")
    equation = input("type equation: f(x) = ")
    coordinates = CalculateEquation(equation, tPosX, tPosY, obstructions)

    if coordinates == "Hit":
      time.sleep(0.25)
      difficultyFactor += 1
      level += 1

      #  Updates highest level
      if int(load()) < level:
        print("New highest score!")
        save(level)
      if difficultyFactor > 24:

        #  Capped at 24 or else it would become physically impossible
        difficultyFactor = 24
      main(difficultyFactor, level)
    elif coordinates == "Miss":
      print("Missed!")

#  Switches between menu GUIs
def menuSwitch(image, pos):
  os.system('clear')
  SCREEN.fill((255,255,255))
  SCREEN.blit(image, pos)
  pygame.display.update()

  #  Yields the code until the user presses enter
  exit = input("Press enter to exit.")

#  Menu screen for the game. Gives users options to navigate
while True:
  os.system('clear')
  print("Calculated Snipers".center(80))
  print(""" 
    1 : Play
    2 : How to play
    3 : Equation syntax rules
    4 : Exit""")
  print(" ")
  print("Enter a number to chose an option")
  SCREEN.fill((255,255,255))
  SCREEN.blit(IMAGES['menu'], (90, 0))
  pygame.display.update()
  userInput = input(" ")

  if userInput == "1":
    os.system('clear')
    difficultyFactor = 1
    level = 1
    main(difficultyFactor, level)
  elif userInput == "2":
    menuSwitch(IMAGES['tutorial'], (150, -10))
  elif userInput == "3":
    menuSwitch(IMAGES['rules'], (150, -10))
  elif userInput == "4":
      os.system('clear')
      SCREEN.fill((0,0,0))
      pygame.display.update()
      break