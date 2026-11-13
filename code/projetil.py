import math
import pygame as pg
from .constantes import ALCANCE_MAX_BALA, COR_MUNICÃO, DANO_BALA, VELOCIDADE_BALA


class Projetil:
    def __init__(
        self,
        x: float,
        y: float,
        direcao: int = 1,
        do_jogador: bool = True,
        vetor_vel: tuple[float, float] = None,
    ):
        self.x = float(x)
        self.y = float(y)
        self.do_jogador = do_jogador
        self.largura = 14
        self.altura = 6
        self.rect = pg.Rect(round(x), round(y), self.largura, self.altura)
        self.ativo = True
        self.distancia_max = ALCANCE_MAX_BALA
        self.distancia_percorrida = 0.0
        self.dano = DANO_BALA if do_jogador else 20

        vel_base = VELOCIDADE_BALA if do_jogador else 660.0
        if vetor_vel is not None:
            self.vx, self.vy = vetor_vel
            self.direcao = 1 if self.vx >= 0 else -1
        else:
            self.direcao = 1 if direcao >= 0 else -1
            self.vx = vel_base * self.direcao
            self.vy = 0.0

    def atualizar(
        self,
        dt: float,
        obstaculos: list[pg.Rect],
        caixas: list,
        jogador=None,
        inimigos: list = None,
    ) -> None:
        if not self.ativo:
            return

        x_ant = self.x
        y_ant = self.y
        desloc_x = self.vx * dt
        desloc_y = self.vy * dt
        self.x += desloc_x
        self.y += desloc_y
        self.distancia_percorrida += math.hypot(desloc_x, desloc_y)
        self.rect.center = (round(self.x), round(self.y))

        if self.distancia_percorrida >= self.distancia_max:
            self.ativo = False
            return

        # Caixa delimitadora varrida (evita tunneling mesmo em alta velocidade e na diagonal)
        min_x = min(x_ant, self.x) - 4
        max_x = max(x_ant, self.x) + 4
        min_y = min(y_ant, self.y) - 4
        max_y = max(y_ant, self.y) + 4
        larg_v = max_x - min_x + self.largura
        alt_v = max_y - min_y + self.altura
        rect_varrido = pg.Rect(round(min_x), round(min_y), round(larg_v), round(alt_v))

        # 1. Colisão com Caixas
        for c in caixas:
            if not c.destruida and rect_varrido.colliderect(c.rect):
                c.receber_dano(1)
                self.ativo = False
                return

        # 2. Se a bala for do jogador -> atinge inimigos
        if self.do_jogador and inimigos:
            for inimigo in inimigos:
                if inimigo.vivo and rect_varrido.colliderect(inimigo.rect):
                    inimigo.receber_dano(self.dano, empurrao_dir=self.direcao)
                    self.ativo = False
                    return

        # 3. Se a bala for do inimigo -> atinge o jogador
        if not self.do_jogador and jogador:
            if rect_varrido.colliderect(jogador.rect):
                jogador.receber_dano(self.dano)
                self.ativo = False
                return

        # 4. Colisão com plataformas / paredes sólidas
        for obstaculo in obstaculos:
            if rect_varrido.colliderect(obstaculo):
                self.ativo = False
                return

    def desenhar(self, tela: pg.Surface, camera) -> None:
        if not self.ativo:
            return
        visivel = camera.aplicar(self.rect)
        if not tela.get_rect().colliderect(visivel):
            return

        cor_bala = COR_MUNICÃO if self.do_jogador else (255, 90, 40)
        cor_rastro = (255, 230, 150) if self.do_jogador else (255, 170, 90)

        # Se for tiro puramente horizontal
        if abs(self.vy) < 5.0:
            pg.draw.rect(tela, cor_bala, visivel)
            rastro_x = visivel.right if self.direcao < 0 else visivel.left - 8
            pg.draw.line(
                tela,
                cor_rastro,
                (rastro_x, visivel.centery),
                (visivel.centerx, visivel.centery),
                2,
            )
        else:
            # Tiro na diagonal com rotação angular
            angulo = math.atan2(self.vy, self.vx)
            ponta = visivel.center
            rastro = (
                round(visivel.centerx - math.cos(angulo) * 12),
                round(visivel.centery - math.sin(angulo) * 12),
            )
            pg.draw.line(tela, cor_rastro, rastro, ponta, 3)
            pg.draw.circle(tela, cor_bala, ponta, 3)
