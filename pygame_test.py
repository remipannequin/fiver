# code from:
# https://wiki.labomedia.org/index.php/Pygame:_des_exemples_pour_débuter.html

__author__="Julien Noel and Rémi Pannequin"
__copyright__ = "Copyright 2020"
__credits__ = ["Rémi Pannequin", "Julien Noël"]
__license__ = "GPL"
__maintainer__ = "Rémi Pannequin"
__email__ = "remi.pannequin@gmail.com" 
__status__ = "Development"

import pygame
from game import Game, Helper
from player import step, best_destination

pygame.init()
pygame.font.init()
#print(pygame.font.get_fonts())
g = Game()
hp = Helper(g)
#couleur des pieces
CIEL = 0, 200, 255
WHITE = 255, 255, 255
GREEN = 0, 255, 0
RED = 255, 0, 0
skyblue = pygame.Color("#3465a4")
COULEUR = [pygame.Color(x) for x in ["#3465a4", "#ef2929", "#c4a000",
                    "#f57900", "#888a85"] ]
#variables

# ATTENTION,RESPECTER LE RATIO.IL FAUT FAIRE hauteur_fenetre*0,88888888888888888888888888 POUR TROUVER LA VALEUR DE longeur_fenetre !!!!!!

hauteur_fenetre = 1000
longeur_fenetre = round(hauteur_fenetre*(8/9))
rectangle_blanc = False
clock = pygame.time.Clock()
nb_cols = g.n_cols
nb_lines = g.n_rows
rayon_cercle = round(longeur_fenetre/16) 
diametre_cercle =  rayon_cercle*2
arrete_carré = diametre_cercle
longueur_ligne_verticales = nb_lines * arrete_carré
longueur_ligne_horizontales = nb_cols * arrete_carré
loop = True
moitiérayon = round(rayon_cercle/2)
game_over = False
fenetre = pygame.display.set_mode((longeur_fenetre, hauteur_fenetre))

#boucle
while loop:
    #on récupère toutes les actions et on calcule les scores
    if game_over is False :    
        actions = hp.actions()
        hp.build_eval_cache()
        #Calcule de la proposition
        (proposition_ligne, proposition_col, proposition_type) = best_destination(hp, actions)

    #print (proposition_ligne, proposition_col, proposition_type)

    background = pygame.Surface(fenetre.get_size())
    #background.fill(CIEL)
    #programmes d'edition du texte   
    if pygame.font:
        font = pygame.font.SysFont("arial", round(hauteur_fenetre/25))
        font2 = pygame.font.SysFont("arial", round(hauteur_fenetre/11))
        text = font.render("score : %d"%g.score, 1, WHITE)
        textpos = text.get_rect()
        textpos.left = rayon_cercle
        textpos.centery = longeur_fenetre
        background.blit(text, textpos)
    #texte pour les pastilles suivantes
    text3 =font.render("pastilles suivantes : ",1,WHITE)
    text3pos = text3.get_rect()
    text3pos.left = rayon_cercle
    text3pos.centery = longeur_fenetre + rayon_cercle
    background.blit(text3, text3pos)   
    # Ajout du fond dans la fenêtre
    fenetre.blit(background, (0, 0))
    if game_over is False :
        pygame.draw.rect(fenetre, COULEUR[proposition_type], [proposition_col*diametre_cercle+rayon_cercle+round(rayon_cercle/10),proposition_ligne*diametre_cercle+rayon_cercle+round(rayon_cercle/10),diametre_cercle-round(diametre_cercle/10), diametre_cercle-round(diametre_cercle/10)],round(diametre_cercle/10))    
    if rectangle_blanc :
        pygame.draw.rect (fenetre,WHITE,(numero_case_x*diametre_cercle + rayon_cercle,numero_case_y*diametre_cercle +rayon_cercle,diametre_cercle,diametre_cercle))
    pieces = []
    #dessin des cercles (pieces)
    for rangee in range(nb_lines):
        for index in range(nb_cols):
            piece = g.board.get_piece(rangee, index)
            if piece is not None:
                c = pygame.draw.circle(fenetre, COULEUR[piece.id], 
                               [rayon_cercle+ index * diametre_cercle + rayon_cercle, rayon_cercle + rangee*diametre_cercle +rayon_cercle], 
                               rayon_cercle)                                
                pieces.append(c)
    
    decalage = 0    
    for piece in g.next_pieces_queue:           
        pygame.draw.circle(fenetre, COULEUR[piece.id], [text3pos.right +round(hauteur_fenetre/60) +moitiérayon+ decalage, (longeur_fenetre +rayon_cercle) ], moitiérayon)                                
        decalage = decalage + round(hauteur_fenetre/15)
    
    for index in range(nb_cols+1):
        depart = [rayon_cercle+index*diametre_cercle, rayon_cercle]
        fin = [depart[0], depart[1] + longueur_ligne_verticales]
        pygame.draw.line(fenetre,WHITE, depart, fin)
    for index in range(nb_lines+1):
        pygame.draw.line(fenetre,WHITE, [rayon_cercle, rayon_cercle+index*diametre_cercle],[(rayon_cercle+nb_cols*diametre_cercle), rayon_cercle+index*diametre_cercle])
    #texte pour ecrire game_over
    if game_over :           
        text2 = font2.render("GAME OVER", 1, WHITE)
        text2pos = text2.get_rect()
        text2pos.centerx = round(longeur_fenetre/2)
        text2pos.centery = round(hauteur_fenetre/2)-rayon_cercle
        fenetre.blit(text2, text2pos) 
        rect_green = pygame.draw.rect(fenetre, RED, [rayon_cercle*10+rayon_cercle, longeur_fenetre, round(longeur_fenetre/4), rayon_cercle])
        text4 = font.render("rejouer",1, WHITE)
        text4pos = text4.get_rect()
        text4pos.centerx = rect_green.centerx
        text4pos.centery = rect_green.centery
        fenetre.blit(text4, text4pos)
    #Analyse des evenments
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x,y = event.pos
            #savoir dans quelle case se situe le clic
            if x > rayon_cercle and y > rayon_cercle and x <  nb_cols * diametre_cercle + rayon_cercle and y < nb_lines * diametre_cercle + rayon_cercle :
                numero_case_x = ((x-rayon_cercle)//diametre_cercle)
                numero_case_y = ((y-rayon_cercle)//diametre_cercle)
                print (numero_case_x)
                print (numero_case_y)
                piece = g.board.get_piece(numero_case_y, numero_case_x)
                #si il y a une pièce,rectangle blanc est vrai,si il n'y en a pas , regarder si on a déjà clique sur une piece avant.Si oui,la faire bouger jusqu'à la case vide.
                #Si non, ne rien faire
                if piece is not None :
                    print ("case avec %s" % piece)
                    numero_case_x2 = numero_case_x
                    numero_case_y2 = numero_case_y
                    rectangle_blanc = True
                else:
                    print ("case sans piece")
                    if rectangle_blanc is True :
                        chemin = g.board.find_path(numero_case_y2, numero_case_x2,numero_case_y, numero_case_x)
                        if len(chemin) == 0:
                            print("interdit !!!")
                        else:
                            g.make_move(numero_case_y2, numero_case_x2,numero_case_y, numero_case_x)
                    rectangle_blanc = False
            elif game_over and rect_green.collidepoint(event.pos):
                #clique sur le rectangle vert
                g = Game()
                hp = Helper(g)
                game_over = False
            
        elif event.type == pygame.KEYDOWN and event.key == 32 and not game_over:
            step(g)
    #si leu jeu est fini,game over est vrai        
    if g.check_game_over():
        game_over =True
        

                
    # Actualisation de l'affichage
    pygame.display.flip() 
    # 10 fps
    clock.tick(10)

