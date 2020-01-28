# code from:
# https://wiki.labomedia.org/index.php/Pygame:_des_exemples_pour_débuter.html


import pygame

pygame.init()


fenetre = pygame.display.set_mode((640, 480))

CIEL = 0, 200, 255
WHITE = 255, 255, 255
GREEN = 0, 255, 0
RED = 255, 0, 0
clock = pygame.time.Clock()


loop = True
while loop:
    #background = pygame.Surface(fenetre.get_size())
    #background.fill(CIEL)

    # Ajout du fond dans la fenêtre
    #fenetre.blit(background, (0, 0))

    # Draw a rectangle outline
    rect_white = pygame.draw.rect(fenetre, WHITE, [75, 10, 100, 50],
                                    5)
    # Draw a solid rectangle
    rect_green = pygame.draw.rect(fenetre, GREEN, [250, 10, 100, 50])

    # retourne 1 si le curseur est au dessus du rectangle
    mouse_xy = pygame.mouse.get_pos()
    over_white = rect_white.collidepoint(mouse_xy)
    over_green = rect_green.collidepoint(mouse_xy)
    print(over_white, over_green)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = False
        # si clic, le vert devient rouge
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print('click')

    # Actualisation de l'affichage
    pygame.display.flip()
    # 10 fps
    clock.tick(10)
    print("looping")
print("end")
