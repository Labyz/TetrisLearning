import pygame
import sys
import numpy as np

shapes = [
    [[1,1,1,1]],

    [[2,2],
     [2,2]],

    [[0,3,0],
     [3,3,3]],

    [[4,4,0],
     [0,4,4]],

    [[0,5,5],
     [5,5,0]],

    [[0,0,6],
     [6,6,6]],

    [[7,0,0],
     [7,7,7]],
]

rotations = [2, 1, 4, 2, 2, 4, 4]

colors = [
    (0,0,0),
    (0, 255, 255),
    (255, 255, 0),
    (128, 0, 128),
    (255, 0, 0),
    (0, 255, 0),
    (255, 165, 0),
    (0, 0, 255)
]

# DONE: enable user to scale the tetris board

class TetrisApp(object):

    def __init__(self, w=10, h=24, silent=False, verbose = True):
        pygame.init()
        self.w = w
        self.h = h
        self.width = 20 * w
        self.height = 20 * h
        self.screen = pygame.display.set_mode((2 * self.width, self.height))
        pygame.key.set_repeat(250, 25)
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        self.board = [[0 for x in range(self.w)] for y in range(self.h)]
        self.permutation = []
        self.new_tetromino()
        self.hold_tetromino = 0
        self.perdu = False
        self.score = 0
        self.lines = 0
        self.combo = 0
        self.liste_touches = {
            'pygame.K_LEFT': self.moveleft,
            'pygame.K_RIGHT': self.moveright,
            'pygame.K_DOWN': self.descente,
            'pygame.K_UP': self.rotate_tetromino,
            'pygame.K_LSHIFT': self.retenir_tetromino
        }
        self.clock = pygame.time.Clock()
        self.column_heights = np.zeros(self.w)
        self.total_height = 0
        self.holes = 0
        self.bumpiness = 0
        self.max_height = 0
        self.silent = silent
        self.verbose = verbose

        #set up a drop every 500ms
        pygame.time.set_timer(pygame.USEREVENT + 1, 500)


    # def reset(self):
    #     self.board = [[0 for x in range(self.w)] for y in range(self.h)]
    #     self.new_tetromino()
    #     self.hold_tetromino = 0
    #     self.perdu = False
    #     self.score = 0
    #     self.combo = 0
    #     self.total_height = 0
    #     self.holes = 0
    #     self.bumpiness = 0
    #     self.permutation = []
    #     self.lines=0
    #     self.column_heights = np.zeros(self.w)


    def descente(self, complete = True):
        ''' fait descendre le tetromino jusqu'au haut de la pile '''
        collision = False
        if complete: 
            while not self.collision_tetromino(self.tetromino,self.x,self.y+1):
                self.y += 1
                if not self.silent:
                    self.draw_screen()
            # self.y -= 1
            collision = True
        else:
            if self.collision_tetromino(self.tetromino,self.x,self.y+1):
                collision = True
            else:
                self.y += 1
        if collision:
            #on ajoute le tetromino au board actuel
            for y, row in enumerate(self.tetromino):
                for x, val in enumerate(row):
                    if val:
                        self.board[self.y + y][self.x + x] = val
            counter, trou = [], False
            for y in range(len(self.tetromino)):
                if len(self.board) > self.y+y:
                    trou = True
                    for i in range(self.w):
                        if not self.board[y+self.y][i]:
                            trou = False
                    if trou:
                        counter.append(y+self.y)
            if counter == []:
                self.combo = 0
            else:
                self.combo += 1
            i = len(counter)
            self.lines += i
            if i == 1:
                self.score += self.combo * 40
            if i == 2:
                self.score += self.combo * 100
            if i == 3:
                self.score += self.combo * 300
            if i > 3:
                self.score += self.combo * 1200
            for i,y in enumerate(counter):
                if self.verbose:
                    print('Success! Combo =', self.combo)
                self.board = self.retirer_ligne(y, self.board)
            
            self.total_height = 0
            self.bumpiness = 0
            self.holes = 0
            for j in range(self.w):
                column = np.array(self.board)[:,j]
                blocks = np.nonzero(column)[0].tolist()
                blocks.append(self.h)
                column_height = self.h - blocks[0]
                self.column_heights[j] = column_height
                self.total_height += column_height
                self.holes += column_height - (len(blocks) - 1)
                if j != 0:
                    self.bumpiness += np.abs(prev_blocks[0] - blocks[0])
                prev_blocks = blocks
            self.max_height = np.max(self.column_heights)

            #nouveau tetromino en haut
            self.new_tetromino()


    def simple_board(self):
        ''' returns the board with 0 or 1 instead of digits '''
        board = np.copy(self.board)
        for i in range(self.h):
            for j in range(self.w):
                if board[i][j] != 0:
                    board[i][j] = 1
        return(board)

    
    def simulate_descent(self, tetromino_sim, x_sim):
        ''' simule la descente du tetromino '''
        combo = self.combo
        lines = self.lines
        column_heights = np.copy(self.column_heights)
        y_sim = self.y
        while not self.collision_tetromino(tetromino_sim, x_sim, y_sim):
            y_sim += 1
        y_sim -= 1
        board_sim = np.copy(self.board)
        #on ajoute le tetromino au board actuel
        for y, row in enumerate(tetromino_sim):
            for x, val in enumerate(row):
                if val:
                    board_sim[y_sim + y][x_sim + x] = val
        counter, trou = [], False
        for y in range(len(tetromino_sim)):
            if len(board_sim) > y_sim+y:
                trou = True
                for i in range(self.w):
                    if not board_sim[y_sim+y][i]:
                        trou = False
                if trou:
                    counter.append(y_sim+y)
        if counter == []:
            combo = 0
        else:
            combo += 1
        i = len(counter)
        lines += i
        for i,y in enumerate(counter):
            board_sim = self.retirer_ligne(y, board_sim)
        
        total_height = 0
        bumpiness = 0
        holes = 0
        for j in range(self.w):
            column = np.array(board_sim)[:,j]
            blocks = np.nonzero(column)[0].tolist()
            blocks.append(self.h)
            column_height = self.h - blocks[0]
            total_height += column_height
            column_heights[j] = column_height
            holes += column_height - (len(blocks) - 1)
            if j != 0:
                bumpiness += np.abs(prev_blocks[0] - blocks[0])
            prev_blocks = blocks
        max_height = np.max(self.column_heights)
        return([total_height, lines, holes, bumpiness, max_height])


    def retenir_tetromino(self):
        if self.hold_tetromino == 0:
            self.hold_tetromino = self.tetromino
            self.new_tetromino()
        else:
            self.hold_tetromino, self.tetromino = self.tetromino, self.hold_tetromino
            self.x = int(self.w / 2)
            self.y = 0


    def rotate_tetromino(self):
        new_tetro = [[self.tetromino[y][x] for y in range(len(self.tetromino))] for x in range(len(self.tetromino[0])- 1, -1, -1)]
        # print(new_tetro)
        if not self.collision_tetromino(new_tetro,self.x,self.y):
            self.tetromino = new_tetro
        self.rotation_id += 1
        self.rotation_id %= 4


    def get_rotated_tetromino(self):
        new_tetro = [[self.tetromino[y][x] for y in range(len(self.tetromino))] for x in range(len(self.tetromino[0])- 1, -1, -1)]
        return(new_tetro)


    def collision_tetromino(self,tetro,x,y):
        for tetroy, row in enumerate(tetro):
            for tetrox, val in enumerate(row):
                try:
                    if val:
                        if self.board[y+tetroy][x+tetrox]:
                            return True
                except IndexError:
                    return True
        return False


    def moveleft(self):
        if(self.x > 0):
            if (not self.collision_tetromino(self.tetromino,self.x-1,self.y)):
                self.x -=1


    def moveright(self):
        if(self.x < self.w):
            if (not self.collision_tetromino(self.tetromino,self.x+1,self.y)):
                self.x +=1


    def new_tetromino(self):
        ''' returns a tetromino '''
        if len(self.permutation) == 0:
            self.permutation=np.random.permutation(7).tolist()
        rint = self.permutation.pop()
        self.tetromino_id = rint
        self.rotation_id = 0
        self.tetromino = shapes[rint]
        # if(rint ==5 or rint ==6):
        #     self.y = -1
        # else:
        #     self.y=0
        self.y=0
        self.x = int(self.w / 2)
        if(self.board[0][int(self.w/2)-1] or self.board[0][int(self.w/2)] or self.board[0][int(self.w/2)+1]):
            if self.verbose:
                print("Game Over")
                print("Score =", self.score)
            self.perdu = True


    def retirer_ligne(self, ty, tboard):
        ''' 
            renvoie le tableau avec la ligne d'ordonnée ty supprimée 
        '''
        ancien_board = np.copy(tboard)
        tboard = [[0 for x in range( self.w )]] + [[ancien_board[y][x] for x in range(self.w)] for y in range(ty)] + [[ancien_board[y][x] for x in range(self.w)] for y in range(ty+1,self.h)]
        return(tboard)


    def react_to_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.USEREVENT + 1:
                self.descente(complete = False)
            elif event.type == pygame.KEYDOWN:
                for t in self.liste_touches:
                    if event.key == eval(t):
                        self.liste_touches[t]()


    def draw_screen(self):
        #Dessiner l'écran
        # print("Score = " + str(self.score))
        # print("Combo = " + str(self.combo))
        self.screen.fill((0, 0, 0))
        msg_score = pygame.font.Font(
            pygame.font.get_default_font(), 12).render(
            "Score: "+str(self.score), False, (255, 255, 255), (0, 0, 0))
        self.screen.blit(msg_score, (self.width + 20 * 3, 20*7))
        msg_combo = pygame.font.Font(
            pygame.font.get_default_font(), 12).render(
            "Combo: x" + str(self.combo), False, (255, 255, 255), (0, 0, 0))
        self.screen.blit(msg_combo, (self.width + 20 * 3, 20 * 8))
        msg_hold = pygame.font.Font(
            pygame.font.get_default_font(), 12).render(
            "Tetromino tenu", False, (255, 255, 255), (0, 0, 0))
        self.screen.blit(msg_hold, (self.width + 20 * 3, 20 * 1))
        for y, row in enumerate(self.board):
            pygame.draw.line(self.screen, (255, 255, 255),
                                (0, y * 20), (self.width, y * 20))
            for x, val in enumerate(row):
                if y == 0:
                    pygame.draw.line(
                        self.screen, (255, 255, 255), (x * 20, 0), (x * 20, self.height))
                if val:
                    pygame.draw.rect(
                        self.screen,
                        colors[val],
                        pygame.Rect(x * 20, y * 20, 20, 20), 0)
        pygame.draw.line(self.screen, (255, 255, 255),
                            (0, self.height - 1), (self.width, self.height - 1))
        pygame.draw.line(self.screen, (255, 255, 255),
                            (self.width, 0), (self.width, self.height))
        for y, row in enumerate(self.tetromino):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        self.screen,
                        colors[val],
                        pygame.Rect((x+self.x) * 20, (y+self.y) * 20, 20, 20), 0)
        if self.hold_tetromino != 0:
            for y, row in enumerate(self.hold_tetromino):
                for x, val in enumerate(row):
                    if val:
                        pygame.draw.rect(
                            self.screen,
                            colors[val],
                            pygame.Rect((self.w+3+x) * 20, (2+y) * 20, 20, 20), 0)
        pygame.display.update()

        #Gestion des contrôles
        # self.clock.tick(20)

    def run(self, n=0):
        ''' runs n rounds, or runs indefinitely if n==0'''
        if (n==0):
            while not self.perdu:
                if not self.silent:
                    self.draw_screen()
                self.react_to_event()
        else:
            for _ in range(n):
                if not self.silent:
                    self.draw_screen()
                self.react_to_event()

# App = TetrisApp(w=15,h=29)
# App = TetrisApp()
# App.run()
