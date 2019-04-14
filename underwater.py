#pylint: disable=no-member

#imports
import pygame
import random
import math
import tkinter
import operator
import pickle
import os

#=========================IMPORTANT TEST RESULTS=================================
# 38355 points / 1348.35s 
# average: 27.63 points per sec

class OutputManager(object):
    def __init__(self,highscore,config):
        self.hs_path = highscore
        self.cfg_path = config
        self.list = []
        self.highscores = {}
        if not(os.path.isfile(highscore)):
            open(highscore,'w+').close()
        if not(os.path.isfile(config)):
            open(config,'w+').close()
    
    def readHighscores(self):
        self.highscores = {}
        # read from file
        file = open(self.hs_path,"rb")

        try:
            self.highscores = pickle.load(file)
        except EOFError:
            print('Highscore file empty or corrupted!')

        file.close()
        return self.highscores  
    
    def addHighscore(self,name, score):
        self.highscores[name] = score
    
    def saveHighscores(self):
        #writing new list to file
        file = open(self.hs_path,"wb")
        pickle.dump(self.highscores,file)
        file.close()
    
    def sortHighscoresbyValue(self):
        self.list = sorted(self.highscores.items(), key=operator.itemgetter(1), reverse=True)
        return self.list

#creating OutputManager
output = OutputManager("high.score","config.txt")

#image loads
bg = pygame.image.load("underwater.jpeg")
sub_img = pygame.image.load("Submarine-icon2.png")
bub_list = [pygame.image.load("bubble1.png"),pygame.image.load("bubble2.png"),pygame.image.load("bubble3.png")]
gauge = pygame.image.load("gauge.png")
steel = [pygame.image.load("steel.jpg"),pygame.image.load("steel2.png")]
monitor = pygame.image.load("monitor.png")
obstacles_list = [pygame.image.load("obstacle2.png"),pygame.image.load("obstacle3.png")]
liquid = pygame.image.load("liquid.png")

#sub_biases = (20,30,160,137)
bub_scores = [5,20,125]
obst_scores = [-500,-250]


#initialization
#ITERATIONS = 0      #initialized to 0, counts how often score was resetted (for recreating the real score after the game)
#ANIMATION_TIME = 0  #initialized to 0, counts how long the animations were (for recreating the real time after the game)
#TRUE_SCORE = 0      #initialized to 0, saves the score at the beginning of endgame to prevent any further increase of the score

#pygame init
pygame.init()

#font load
FONT = pygame.font.Font("7_Segment.ttf",28)

#window properties and init
WIDTH = 1000
HEIGHT = 750
GUI_HEIGHT = 200
win = pygame.display.set_mode((WIDTH,HEIGHT+200))
pygame.display.set_caption(("Underwater v1.4"))

#setting up the timer
clock = pygame.time.Clock()
test = 5
hest = 7

#mapping input value in input range to an output value in an output range
def map(value, inMin, inMax, outMin, outMax):
    if value < inMin:
        value = inMin
    elif value > inMax:
        value = inMax
    inRange = inMax - inMin
    outRange = outMax - outMin

    valueScaled = float(value - inMin) / float(inRange)

    return outMin + (valueScaled * outRange)

#probability function (see docstring)
def choose(input_list,poss):
    """
    IMPORTANT: The list must be sorted with decreasing probability, for example:\n
    input_list = ["A","B","C"]\n
    poss = 5\n
    \n
    the output will be possibility:\n
    "A": 4/5 = 0.8\n
    "B": 1/5*4/5 = 4/25 = 0.16\n
    "C": 1/5*1/5 = 1/25 = 0.04
    """
    for i in input_list:
        if input_list.index(i) == (len(input_list)-1):
            return i
        elif random.randrange(1,poss+1) != 1:
            return i

#player object (one instance)
class Player(object):
    def __init__(self,start_x,start_y,vel,image):
        self.x = start_x
        self.y = start_y
        self.vel = vel
        self.img = image
        self.actualize_hitboxes()
    
    def draw(self,win):
        win.blit(self.img,(self.x,self.y))
        if show_boxes:
            pygame.draw.rect(win,(255,0,0),self.rect,1)
            pygame.draw.rect(win,(0,0,255),self.rect2,1)
            h_box = pygame.Rect(self.hit_box[0],self.hit_box[1],self.hit_box[2]-self.hit_box[0],self.hit_box[3]-self.hit_box[1])
            pygame.draw.rect(win,(0,255,0),h_box,1)
    
    def move(self,keys,y_Allowed):
        if y_Allowed:
            if keys[pygame.K_DOWN] and self.hit_box[3] < HEIGHT:
                self.y += self.vel
            elif keys[pygame.K_UP] and self.hit_box[1] > 0:
                self.y -= self.vel
        if keys[pygame.K_LEFT] and self.hit_box[0] > 0:
            self.x -= self.vel
        elif keys[pygame.K_RIGHT] and self.hit_box[2] < WIDTH:
            self.x += self.vel 
        self.actualize_hitboxes()
      
    def actualize_hitboxes(self):
        self.hit_box = [self.x+15,self.y+30,self.x+130,self.y+110]
        self.rect = pygame.Rect(self.x+62,self.y+22,37,35)
        self.rect2 = pygame.Rect(self.x+15,self.y+55,115,55)
    
    def moveManually(self,x,y):
        self.x += x
        self.y += y

#bubble sprite, managed by a SpriteManager instance
class Bubble(object):
    def __init__(self,start_x,start_y,vel,image,roaming_y):
        self.x = start_x
        self.y = start_y
        self.vel = vel
        self.img = image
        self.roam_y = roaming_y
        if bub_list.index(self.img) == 0:
            self.h = 30
            self.w = 30
            self.bias = 5
        elif bub_list.index(self.img) == 1:
            self.h = 40
            self.w = 40
            self.bias = 10
        elif bub_list.index(self.img) == 2:
            self.h = 75
            self.w = 75
            self.bias = 12
        self.actualizeHitboxes()

    def draw(self,win):
        win.blit(self.img,(self.x,self.y))
        if show_boxes:
            pygame.draw.rect(win,(255,0,0),self.rect,1)

    def move(self):
        
        self.y += random.randint(1,self.roam_y) * random.randrange(-1,2,2)
            
        self.x += self.vel
        self.actualizeHitboxes()
    
    def actualizeHitboxes(self):
        self.rect = pygame.Rect(self.x+self.bias,self.y+self.bias,self.w,self.h)

#sprite manager, handles Bubbles and Obstacles (with different params)
class SpriteManager(object):
    def __init__(self,sprite,chance,start_x,y_range,vel,images,roaming_max,player,scores):
            self.sprite = sprite
            self.chance = chance
            self.start_x = start_x
            self.y_min, self.y_max = y_range
            self.vel = vel
            self.image_list = images
            self.roam_max = roaming_max
            self.sprite_list = []
            self.player = player
            self.scores = scores
    
    def createSprite(self,score,MAX_SCORE):
        if random.randrange(1,int(self.chance(score,MAX_SCORE))) == 1:
            new_y = random.randint(self.y_min*10,self.y_max*10)/10
            new_vel = self.vel(score,MAX_SCORE)
            new_img = choose(self.image_list,4)

            new_sprite = self.sprite(self.start_x,new_y,new_vel,new_img,self.roam_max,)
            self.sprite_list.append(new_sprite)
            
    def moveSprites(self):
        addscore = 0
        for sprite in self.sprite_list[::1]:
            sprite.move()
            if sprite.x < 0 or sprite.y+sprite.h > HEIGHT or sprite.y < 0:
                self.sprite_list.remove(sprite)
            elif (self.player.rect.colliderect(sprite.rect) or self.player.rect2.colliderect(sprite.rect)):
                addscore += self.scores[self.image_list.index(sprite.img)-1]
                self.sprite_list.remove(sprite)
        return addscore
    
    def drawSprites(self,win):
        for sprite in self.sprite_list:
            sprite.draw(win)

#draws the HUD
class GUIManager(object):
    def __init__(self,win,game,GUI_rect_coords,vel_coords,gauge_configs):
        """
        Attention: all coordinates will be relative to GUI_rect_coords!
        Gauge configs: (size_of_average_list,cooldown)
        """
        self.game = game
        self.win = win
        self.x1, self.y1, self.x2, self.y2 = GUI_rect_coords
        self.velx, self.vely, self.rad = vel_coords
        self.velx += self.x1
        self.vely += self.y1
        self.size,self.cooldown = gauge_configs
        self.pps = [0] *self.size
        self.cooldown *= 1000
        self.i = 0
        self.time_old = pygame.time.get_ticks()
        self.score_old = 0
        self.time = 0
        self.slider_old = 0
        self.average_old = 0
        self.reset_texts = [FONT.render("YOU REACHED",True,(255,0,0)),FONT.render("THE NEXT",True,(255,0,0)),FONT.render("LEVEL!",True,(255,0,0))]
    
    def resetAverage(self):
        self.pps = [0] *self.size

    def draw_GUI(self,score,TIME_LIMIT,isReset):
        time = pygame.time.get_ticks() /1000
        self.draw_board()
        self.draw_oxygen_slider(score)
        self.draw_board_cover()
        self.draw_gauge(score,score/time)
        self.draw_monitor(score,time,TIME_LIMIT,isReset)

    def draw_board(self):
        self.win.blit(steel[0],(self.x1,self.y1))

    def draw_oxygen_slider(self,score):
        y = map(score,0,self.game.MAX_SCORE,160,-10) + self.y1 + math.sin(self.slider_old*1/10)*5
        x = self.x1 + 75
        self.slider_old += 1
        sx1 = self.slider_old%300 + x
        sx2 = (self.slider_old+100)%300 + x
        sx3 = (self.slider_old+200)%300 + x
        self.win.blit(liquid,(sx1,y))
        self.win.blit(liquid,(sx2,y))
        self.win.blit(liquid,(sx3,y))
    
    def draw_board_cover(self):
        self.win.blit(steel[1],(self.x1,self.y1))
        pygame.draw.rect(win,(100,100,100),pygame.Rect(self.x1,self.y1,WIDTH,5))

    def draw_gauge(self,score,pps):
        self.time = pygame.time.get_ticks()
        cooldown_time = self.time_old + self.cooldown

        if self.time > cooldown_time:

            score_diff = score - self.score_old
            time_diff = self.time -self.time_old

            self.pps[self.i%(self.size)] = score_diff / time_diff*self.cooldown
            self.score_old = score
            self.time_old = self.time
            self.i += 1

            average = 0

            for points in self.pps:
                average += points
            average /= self.size
            self.average_old = average

        else:
            average = self.average_old

        win.blit(gauge,(self.velx-149,self.vely-100))
        radian = math.radians(map(average,0,150,-45,225))
        y = math.sin(radian) * self.rad
        x = math.cos(radian) * self.rad
        pygame.draw.line(win,(50,50,50),(self.velx,self.vely),(self.velx-x,self.vely-y),4)
    
    def draw_monitor(self,score,time,TIME_LIMIT,isReset):
        win.blit(monitor,(self.x1+700,self.y1))

        if isReset:
            win.blit(self.reset_texts[0],(self.x1+720,self.y1+60))
            win.blit(self.reset_texts[1],(self.x1+720,self.y1+100))
            win.blit(self.reset_texts[2],(self.x1+720,self.y1+140))
        else:
            time_text = FONT.render("Time left: {} sec".format(round(TIME_LIMIT-time)), True, (255, 0, 0))
            score_text = FONT.render("Score: {} pts".format(round(score+self.game.MAX_SCORE*self.game.ITERATIONS)),True,(255,0,0))
            average_text = FONT.render("Average: {} pts/sec".format(round(self.average_old)),True,(255,0,0))
            
            win.blit(time_text,(self.x1+720,self.y1+20))
            win.blit(score_text,(self.x1+720,self.y1+60))
            win.blit(average_text,(self.x1+720,self.y1+100))

#obstacle sprite, managed by a SpriteManager, similar to Bubble-object
class Obstacle(object):

    def __init__(self,start_x,start_y,vel,image,roaming_y):
        self.x = start_x
        self.y = start_y
        self.img = image
        self.vel = vel

        if obstacles_list.index(self.img) == 0:
            self.w = 70
            self.h = 70
            self.bias = 20

        elif obstacles_list.index(self.img) == 1:
            self.w = 130
            self.h = 65
            self.bias = 20

        else:
            raise FileNotFoundError("Image must be in the image list of obstacles")
        
        self.rect = pygame.Rect(self.x+self.bias,self.y+self.bias,self.w,self.h)
    
    def move(self):
        self.x += self.vel
        self.rect = pygame.Rect(self.x+self.bias,self.y+self.bias,self.w,self.h)
    
    def draw(self,win):
        win.blit(self.img,(self.x,self.y))

        if show_boxes:
            pygame.draw.rect(win,(255,0,0),self.rect,1)

#scoreboard manager
class ScoreboardManager(object):
    def __init__(self,OutputManager):
        self.outMgr = OutputManager
        self.scoreboard = tkinter.Tk()
        self.scoreboard.title('Scoreboard')
        self.canvas = tkinter.Canvas(self.scoreboard,width=300,height=500, bg='white')
        self.canvas.pack()
        self.name_input = tkinter.Text(self.scoreboard, width=10, height =1)
        self.name_input.pack()
        self.confirm_button = tkinter.Button(self.scoreboard, text="Enter", command=self.submitName)
        self.confirm_button.pack()
        self.scoreboard.mainloop()
    
    def submitName(self):
        #getting input
        name = "Anonym"
        name2 = self.name_input.get("1.0",'end-1c')
        if (name2 != ""):
            name = name2 
        splitted = name.split("\n")
        name = splitted[len(splitted)-1]

        #destroy input
        self.confirm_button.destroy()
        self.name_input.destroy()
        self.outMgr.readHighscores()
        self.outMgr.addHighscore(name,score)
        hs_list = self.outMgr.sortHighscoresbyValue()

        text = ""
        i = 0
        if (len(hs_list) < 10):
            for i in range(len(hs_list)):
                a,b = hs_list[i]
                text += "{a}: {b}\n".format(a=a,b=b) 
        else:
            for key in hs_list and i in range(0,9,1):
                i += 1
                text += "{a}: {b}\n".format(a=key, b=hs_list[key]) 
                
        self.canvas.config(height = 0)
        sb_text = tkinter.Text(self.scoreboard,width = 15, height = 10,font=("7_Segment.ttif", 22),bg="black")
        sb_text.delete(0.0)
        sb_text.insert(0.0,text)
        sb_text.config(state="disabled")
        sb_text.pack()
        self.scoreboard.update()
        self.outMgr.saveHighscores()


class GameManager(object):
    def __init__(self,win,time_limit,max_score,bub_mgr,obst_mgr):
        self.win = win
        self.ANIMATION_TIME = 0
        self.TIME_LIMIT = time_limit
        self.TIME_ADD = time_limit
        self.MAX_SCORE = max_score
        self.ITERATIONS = 0
        self.score = 0
        self.bub_mgr = bub_mgr
        self.obst_mgr = obst_mgr

    def redrawGameWindow(self,isReset):
        #background
        win.blit(bg,(0,0))

        #GUI
        gui.draw_GUI(self.score,self.TIME_LIMIT,isReset)

        #draw sub
        sub.draw(self.win)

        #draw all Obstacles and Bubbles
        o_mgr.drawSprites(self.win)
        b_mgr.drawSprites(self.win)

        #update screen
        pygame.display.update()
    
    #animation for resetting score when levelling up
    def animation(self):
        score_overflow = self.score % self.MAX_SCORE
        time_old = pygame.time.get_ticks()

        b = 100
        while b > 0:
            clock.tick(60)
            self.score = int(b/100 * self.MAX_SCORE)
            self.redrawGameWindow(True)
            b -= 1
            
        self.score = score_overflow
        gui.resetAverage()
        time = pygame.time.get_ticks()
        time_passed = time-time_old
        self.ANIMATION_TIME += time_passed
        self.TIME_LIMIT += self.TIME_ADD + time_passed/1000
        self.ITERATIONS += 1
        debug = """ DEBUG: next level.
        
        Iterations: {} 
        total score: {}pts 
        score overflow {}pts

        TIME
        before:              {}ms 
        after:               {}ms 
        passed in animation: {}ms 
        new time limit:      {}ms
        time till deadline:  {}s
        """
        print(debug.format(self.ITERATIONS,self.ITERATIONS*self.MAX_SCORE,score_overflow,time_old,time,time_passed,self.TIME_LIMIT,self.TIME_LIMIT-time/1000))
    
    #triggered when time > TIME_LIMIT
    def endGame(self):
        self.TRUE_SCORE = self.score
        while sub.y > -200:
            sub.moveManually(5,-10)
            self.score = self.TRUE_SCORE
            self.bub_mgr.moveSprites()
            self.obst_mgr.moveSprites()
            self.redrawGameWindow(False)
    
    #move Sprites (Bubbles & Obstacles)
    def moveSprites(self):
        self.score += self.bub_mgr.moveSprites()
        self.score += self.obst_mgr.moveSprites()
    
    #create new Sprites (Bubbles&Obstacles)
    def createSprites(self):
        self.bub_mgr.createSprite(self.score,self.MAX_SCORE)
        self.obst_mgr.createSprite(self.score,self.MAX_SCORE)
    
    def ScoreboardSequence(self):
        self.scrMgr = ScoreboardManager(output)
        # self.scrMgr.
        
#creating player
sub = Player(WIDTH/2,HEIGHT/2,7,sub_img)

#lambda expressions for recalculating the velocity for a new Bubble or Obstacle respectively
bubble_vel = lambda sc,MAX_SCORE: random.randint(5,20)*-1
obstacle_vel = lambda sc,MAX_SCORE: map(sc,0,MAX_SCORE,15,30)*-1

#lambda expressions for recalculating the chance for an new Bubble or Obstacle to spawn respectively
bubble_chance = lambda sc,MAX_SCORE: random.randint(3,5)
obstacle_chance = lambda sc,MAX_SCORE: map(sc,0,MAX_SCORE,600,40) 

#creating instances of SpriteManager-class for handling Bubbles and Obstacles 
b_mgr = SpriteManager(Bubble,bubble_chance,WIDTH-10,(0,HEIGHT-30),bubble_vel,bub_list,5,sub,bub_scores)
o_mgr = SpriteManager(Obstacle,obstacle_chance,WIDTH-10,(0,HEIGHT-30),obstacle_vel,obstacles_list,0,sub,obst_scores)

#creating GameManager
gameMgr = GameManager(win,30,10000,b_mgr,o_mgr) 

#creating instances of the GUI-manager
gui = GUIManager(win,gameMgr,(0,HEIGHT,WIDTH,HEIGHT+GUI_HEIGHT),(100,100,60),(10,0.5))
        
#loop variable
run = True

#mainloop
while run:
    #fps 
    clock.tick(60)
    
    #check for closing window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    #get pressed keys (simultanously pressed keys included)
    keys = pygame.key.get_pressed()

    #hitboxes (debug)
    if keys[pygame.K_d]:
        show_boxes = True
    else:
        show_boxes = False

    #checking whether next level or not
    if gameMgr.score > gameMgr.MAX_SCORE:
        gameMgr.animation()
    
    #check whether time is left
    if pygame.time.get_ticks() < gameMgr.TIME_LIMIT*1000: 
        #moving sub
        sub.move(keys,True)
    else:
        #triggering endGame and quitting afterwards
        gameMgr.endGame()
        run = False
    
    gameMgr.moveSprites()
    gameMgr.createSprites()
    
    #redraw Window ATTENTION: THIS SHOULD BE THE LAST ACTION IN THE MAIN LOOP! 
    gameMgr.redrawGameWindow(False)
    
#calculating played time 
time = round((pygame.time.get_ticks()-gameMgr.ANIMATION_TIME)/1000,2)
score = gameMgr.score + gameMgr.MAX_SCORE * gameMgr.ITERATIONS
#output
print("Your score was: {} and your time was: {}s\nThat's an average of {} points/second".format(score,time,round(score/time,2))) 
#quit pygame 
pygame.quit()
gameMgr.ScoreboardSequence()