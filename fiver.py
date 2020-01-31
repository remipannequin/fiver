#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Interactive interface for the game and automatic player agent
"""

import pygame

from game import Game, Helper
from player import step, best_destination

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

    def __init__(self):
        pygame.init()
        pygame.font.init()
        #variables
        self.selection = None
        self.reset()
        self.compute_size()


    def compute_size(self):
        hauteur_fenetre = 1000
        longeur_fenetre = round(hauteur_fenetre*(8/9))
        self.rayon_cercle = round(longeur_fenetre/16)
        self.diametre_cercle =  self.rayon_cercle*2
        self.fenetre = pygame.display.set_mode((longeur_fenetre, hauteur_fenetre))


    def reset(self):
        self.game_over = False
        self.g = Game()
        self.hp = Helper(self.g)


    def pix(self, r):
        return int(50 + r*self.diametre_cercle)

    def grid(self, x):
        return (x-50)//self.diametre_cercle
        

    def estimate_best_move(self):
        if self.game_over is False :    
            actions = self.hp.actions()
            #TODO rebuild cache only if game change
            self.hp.build_eval_cache()
            #Estimate best move (destination)
            self.proposition = best_destination(self.hp, actions)


    def draw_game(self):
        background = pygame.Surface(self.fenetre.get_size())
        #programmes d'edition du texte   
        font = pygame.font.SysFont("arial", 36)
        font2 = pygame.font.SysFont("arial", 70)
        text = font.render("score : %d"%self.g.score, True, WHITE)
        textpos = text.get_rect()
        textpos.left = 50
        textpos.centery = self.pix(self.g.n_rows+0.5)
        background.blit(text, textpos)
        #texte pour les pastilles suivantes
        text3 = font.render("pastilles suivantes : ", True, WHITE)
        text3pos = text3.get_rect()
        text3pos.left = 50
        text3pos.centery = self.pix(self.g.n_rows+1)
        background.blit(text3, text3pos)   
        # Ajout du fond dans la fenêtre
        self.fenetre.blit(background, (0, 0))
        if not self.game_over:
            border = round(self.diametre_cercle/25)
            pygame.draw.rect(self.fenetre, 
                             COULEUR[self.proposition[2]], 
                             [self.pix(self.proposition[1])+border,
                              self.pix(self.proposition[0])+border,
                              self.diametre_cercle-2*border,
                              self.diametre_cercle-2*border],
                              2*border)
        if self.selection :
            pygame.draw.rect(self.fenetre,
                             WHITE,
                             (self.pix(self.selection[1]),self.pix(self.selection[0]),self.diametre_cercle,self.diametre_cercle))
        #dessin des cercles (pieces)
        for row in range(self.g.n_rows):
            for col in range(self.g.n_cols):
                piece = self.g.board.get_piece(row, col)
                if piece is not None:
                    pygame.draw.circle(self.fenetre, 
                            COULEUR[piece.id], 
                            [self.pix(col+0.5), self.pix(row+0.5)], 
                            self.rayon_cercle)
        
        decalage = 0
        r = round(self.diametre_cercle / 4)
        for piece in self.g.next_pieces_queue:
            pygame.draw.circle(self.fenetre, 
                               COULEUR[piece.id], 
                               [text3pos.right +15 + r + decalage, self.pix(self.g.n_rows+1)], 
                               r)
            decalage = decalage + 60
        
        for index in range(self.g.n_cols+1):
            pygame.draw.line(self.fenetre,
                    WHITE, 
                    [self.pix(index), self.pix(0)],
                    [self.pix(index), self.pix(self.g.n_rows)])
        for index in range(self.g.n_rows+1):
            pygame.draw.line(self.fenetre,
                    WHITE, 
                    [self.pix(0), self.pix(index)],
                    [self.pix(self.g.n_cols), self.pix(index)])
        #texte pour ecrire game_over
        if self.game_over:
            text2 = font2.render("GAME OVER", 1, WHITE)
            text2pos = text2.get_rect()
            text2pos.centerx = self.pix(self.g.n_cols/2)
            text2pos.centery = self.pix(self.g.n_rows/2)
            self.fenetre.blit(text2, text2pos)
            self.replay = pygame.draw.rect(self.fenetre, WHITE, [self.pix(self.g.n_cols-1.5), self.pix(self.g.n_rows+0.5), self.diametre_cercle*1.5, self.diametre_cercle//2], 2)
            text4 = font.render("rejouer",1, WHITE)
            text4pos = text4.get_rect()
            text4pos.centerx = self.replay.centerx
            text4pos.centery = self.replay.centery
            self.fenetre.blit(text4, text4pos)


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
                                print("interdit !!!")
                            else:
                                self.g.make_move(self.selection[0], self.selection[1], row, col)
                        self.selection = None
                elif self.replay.collidepoint(event.pos):
                    self.reset()
                
            elif event.type == pygame.KEYDOWN and event.key == 32 and not self.game_over:
                step(self.g)

    def loop(self):
        clock = pygame.time.Clock()
        while self.loop:
            self.estimate_best_move()
            self.draw_game()
            self.process_events()
            self.game_over = self.g.check_game_over()
            # Actualisation de l'affichage
            pygame.display.flip() 
            # 10 fps
            clock.tick(10)
        

if __name__=='__main__':
    w = Window()
    w.loop()
    
    
