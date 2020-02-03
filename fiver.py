#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interactive interface for the game and automatic player agent

Usage:
    fiver.py [--seed=<n>] [--mode=<m>] [-t | --show-tip]
    fiver.py (-h | --help | --version)
    
Options:
    -h, --help      Dsiplay help
    --seed=<n>      Random seed to use
    --mode=<m>      The playing mode to use [default: normal] 
    -t, --show-tip  Show playing tip
"""

import shelve
from datetime import datetime
import sys

from docopt import docopt
import pygame

from game import Game, Helper
from player import step, heuristic_2

_author__="Julien Noel and Rémi Pannequin"
__copyright__ = "Copyright 2020"
__credits__ = ["Rémi Pannequin", "Julien Noël"]
__license__ = "GPL"
__maintainer__ = "Rémi Pannequin"
__email__ = "remi.pannequin@gmail.com"
__status__ = "Development"


#couleur des pieces
WHITE = 255, 255, 255
COULEUR = [pygame.Color(x) for x in ["#3465a4", "#ef2929", "#c4a000", "#f57900", "#888a85"] ]


class Window:

    def __init__(self, seed = None, mode=None, show_tip = False):
        pygame.init()
        pygame.font.init()
        #variables
        if mode:
            self.mode = mode
        else:
            self.mode = Game.Mode.NORMAL
        self.selection = None
        self.reset(seed)
        self.compute_size()
        self.show_tip = show_tip


    def compute_size(self):
        height = 800
        width = round(height*(self.g.n_cols/(self.g.n_rows+1.5)))+20
        self.l = round((width-20)/self.g.n_cols)
        self.win = pygame.display.set_mode((width, height))
        self.font = pygame.font.SysFont("arial", 36)
        self.font_big = pygame.font.SysFont("arial", 70)


    def reset(self, seed=None):
        self.game_over = False
        self.g = Game(seed = seed, mode = self.mode)
        self.hp = Helper(self.g)


    def pix(self, r):
        return int(10 + r*self.l)

    def grid(self, x):
        return (x-10)//self.l
        

    def estimate_best_move(self):
        if self.game_over is False :    
            actions = self.hp.actions()
            #Estimate best move (destination)
            (src, dst) = heuristic_2(self.hp, actions)
            self.proposition = (dst.row, dst.col, src.piece)

    def text_centered(self, msg, x, y, big=False):
        if big:
            text = self.font_big.render(msg, 1, WHITE)
        else:
            text = self.font.render(msg, 1, WHITE)
        textpos = text.get_rect()
        textpos.centerx = x
        textpos.centery = y
        self.win.blit(text, textpos)
        
    
    
    def text_left(self, msg, height):
        text = self.font.render(msg, True, WHITE)
        textpos = text.get_rect()
        textpos.left = self.pix(0)
        textpos.centery = height
        self.win.blit(text, textpos)
        return textpos.right
    
    def draw_game(self):
        background = pygame.Surface(self.win.get_size())
        self.win.blit(background, (0, 0))
        
        #Display score
        self.text_left("Score : %d"%self.g.score, self.pix(self.g.n_rows+0.5))
        
        #Next pieces (text)
        decalage = self.text_left("Next : ", self.pix(self.g.n_rows+1)) 
        r = round(self.l / 4)
        decalage += int(r*1.5)
        for piece in self.g.next_pieces_queue:
            pygame.draw.circle(self.win, 
                               COULEUR[piece], 
                               [decalage, self.pix(self.g.n_rows+1)], 
                               r)
            decalage = decalage + int(2.5 * r)
        
        #draw lines
        for col in range(self.g.n_cols+1):
            pygame.draw.line(self.win,
                    WHITE, 
                    [self.pix(col), self.pix(0)],
                    [self.pix(col), self.pix(self.g.n_rows)])
        for row in range(self.g.n_rows+1):
            pygame.draw.line(self.win,
                    WHITE, 
                    [self.pix(0), self.pix(row)],
                    [self.pix(self.g.n_cols), self.pix(row)])
        
        if not self.game_over and self.show_tip:
            border = round(self.l/25)
            pygame.draw.rect(self.win, 
                             COULEUR[self.proposition[2]], 
                             [self.pix(self.proposition[1])+border,
                              self.pix(self.proposition[0])+border,
                              self.l-2*border,
                              self.l-2*border],
                              2*border)
        
        #draw selection
        if self.selection :
            pygame.draw.rect(self.win,
                             WHITE,
                             (self.pix(self.selection[1]),self.pix(self.selection[0]),self.l,self.l))
        #Draw Pieces
        rayon_cercle = int(self.l * 0.45)
        for row in range(self.g.n_rows):
            for col in range(self.g.n_cols):
                piece = self.g.board.get_piece(row, col)
                if piece is not None:
                    pygame.draw.circle(self.win, 
                            COULEUR[piece], 
                            [self.pix(col+0.5), self.pix(row+0.5)], 
                            rayon_cercle)
        
        #Display game over / play again
        if self.game_over:
            self.text_centered("GAME OVER", self.pix(self.g.n_cols/2), self.pix(self.g.n_rows/2), True)
            
            self.replay_bt = pygame.draw.rect(self.win, 
                                           WHITE, 
                                           [self.pix(self.g.n_cols-2.5), 
                                            self.pix(self.g.n_rows+0.5), 
                                            self.l*2.5, 
                                            self.l//2], 2)
            self.text_centered("play again", self.replay_bt.centerx, self.replay_bt.centery)


    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.loop = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x,y = event.pos
                #savoir dans quelle case se situe le clic
                if x > self.pix(0) and y > self.pix(0) and x <  self.pix(self.g.n_cols) and y < self.pix(self.g.n_rows):
                    col = self.grid(x)
                    row = self.grid(y)
                    piece = self.g.board.get_piece(row, col)
                    #si il y a une pièce,rectangle blanc est vrai,si il n'y en a pas , regarder si on a déjà clique sur une piece avant.Si oui,la faire bouger jusqu'à la case vide.
                    #Si non, ne rien faire
                    if piece is not None :
                        self.selection = (row, col)
                    else:
                        if self.selection:
                            chemin = self.g.board.find_path(self.selection[0], self.selection[1], row, col)
                            if len(chemin) == 0:
                                print("No path to move here.")
                            else:
                                self.g.make_move(self.selection[0], self.selection[1], row, col)
                                
                                
                                
                                
                                #Rebuild cache only if game change
                                self.hp.build_eval_cache()
                        self.selection = None
                elif self.replay_bt.collidepoint(event.pos):
                    self.reset()
                
            elif event.type == pygame.KEYDOWN and event.key == 32 and not self.game_over:
                step(self.g)
                self.hp.build_eval_cache()

    def loop(self):
        clock = pygame.time.Clock()
        while self.loop:
            if self.show_tip:
                self.estimate_best_move()
            self.draw_game()
            self.process_events()
            if not self.game_over and self.g.check_game_over():
                self.game_over = True
                with shelve.open('trace.db') as db:
                    ts = datetime.now()
                    db[str(ts)] = {'trace': self.g.trace, 
                                   'size':(self.g.n_rows,self.g.n_cols), 
                                   'mode':self.g.mode, 
                                   'score':self.g.score,
                                   'seed': self.g.seed}
            # Actualisation de l'affichage
            pygame.display.flip() 
            # 10 fps
            clock.tick(10)
        

if __name__=='__main__':
    
    args = docopt(__doc__)
    print(args)
    if args['--seed']:
        s = int(args['--seed'])
    else:
        s = None
    if args['--mode']:
        m = args['--mode']
    else:
        m = 'normal'
    t = args['--show-tip']
    w = Window(seed = s, mode = m, show_tip = t)
    w.loop()
    
    
