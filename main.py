import pygame as pg

pg.init()

tela = pg.display.set_mode((1080, 720))
pg.display.set_caption("Chuva de Balas")

relogio = pg.time.Clock()
rodando = True


while rodando:
    for e in pg.event.get():
        if e.type == pg.QUIT:
            rodando = False

    tela.fill((25, 25, 35))
    pg.display.flip()
    relogio.tick(60)


pg.quit()

