import math
import pygame as pg
from constantes import (
    COR_BRANCO,
    COR_PRETO,
    COR_VIDA,
    GRAVIDADE,
    INIMIGO_MELEE_DANO_CONTATO,
    INIMIGO_MELEE_DISTANCIA_VISAO,
    INIMIGO_MELEE_TEMPO_RESPIRO,
    INIMIGO_MELEE_VELOCIDADE,
    INIMIGO_MELEE_VELOCIDADE_RECUO,
    INIMIGO_MELEE_VIDA,
    INIMIGO_RANGED_COOLDOWN_TIRO,
    INIMIGO_RANGED_DANO_TIRO,
    INIMIGO_RANGED_DISTANCIA_TIRO,
    INIMIGO_RANGED_VELOCIDADE,
    INIMIGO_RANGED_VIDA,
    VELOCIDADE_TERMINAL,
)
from projetil import Projetil


class Inimigo:
    """Classe base com física, solo e dano para inimigos."""

    def __init__(self, x: float, y: float, largura: int = 40, altura: int = 82, vida_max: int = 50):
        self.x = float(x)
        self.y = float(y)
        self.largura = largura
        self.altura = altura
        self.rect = pg.Rect(round(x), round(y), largura, altura)

        self.vx = 0.0
        self.vy = 0.0
        self.no_chao = False
        self.olhando_direita = True

        self.vida = vida_max
        self.vida_max = vida_max
        self.vivo = True
        self.tempo_morte = 0.0
        self.tempo_dano = 0.0

    def receber_dano(self, quantidade: int, empurrao_dir: int = 0) -> None:
        if not self.vivo:
            return
        self.vida = max(0, self.vida - quantidade)
        self.tempo_dano = 0.22
        self.vx = empurrao_dir * 180.0
        if self.vida <= 0:
            self.vivo = False
            self.tempo_morte = 0.60

    def aplicar_fisica_e_colisoes(self, dt: float, obstaculos: list[pg.Rect]) -> None:
        if not self.no_chao or self.vy < 0:
            self.vy += GRAVIDADE * dt
            if self.vy > VELOCIDADE_TERMINAL:
                self.vy = VELOCIDADE_TERMINAL

        self.x += self.vx * dt
        self.rect.x = round(self.x)
        for obs in obstaculos:
            if self.rect.colliderect(obs):
                if self.vx > 0:
                    self.rect.right = obs.left
                    self.olhando_direita = False
                elif self.vx < 0:
                    self.rect.left = obs.right
                    self.olhando_direita = True
                self.vx = 0.0
                self.x = float(self.rect.x)

        self.y += self.vy * dt
        self.rect.y = round(self.y)
        for obs in obstaculos:
            if self.rect.colliderect(obs):
                if self.vy > 0:
                    self.rect.bottom = obs.top
                    self.vy = 0.0
                    self.y = float(self.rect.y)
                elif self.vy < 0:
                    self.rect.top = obs.bottom
                    self.vy = 0.0
                    self.y = float(self.rect.y)

        sensor_chao = pg.Rect(self.rect.x + 4, self.rect.bottom, self.rect.width - 8, 3)
        self.no_chao = any(sensor_chao.colliderect(obs) for obs in obstaculos) and (self.vy >= 0)
        if self.no_chao:
            self.vy = 0.0

    def verificar_borda_frente(self, obstaculos: list[pg.Rect]) -> bool:
        """Retorna True se houver borda de precipício à frente na direção do olhar."""
        sensor_x = self.rect.right + 4 if self.olhando_direita else self.rect.left - 12
        sensor = pg.Rect(sensor_x, self.rect.bottom, 8, 8)
        return not any(sensor.colliderect(obs) for obs in obstaculos)

    def verificar_borda_atras(self, obstaculos: list[pg.Rect]) -> bool:
        """Retorna True se houver borda de precipício atrás (para recuo seguro)."""
        sensor_x = self.rect.left - 10 if self.olhando_direita else self.rect.right + 2
        sensor = pg.Rect(sensor_x, self.rect.bottom, 8, 8)
        return not any(sensor.colliderect(obs) for obs in obstaculos)


class InimigoMelee(Inimigo):
    """
    Cangaceiro Melee com Peixeira.
    Ciclo dinâmico: Patrulha -> Investida Rápida -> Golpe -> Recuo Tático -> Respiro -> Nova Investida.
    """

    ESTADO_PATRULHA = "patrulha"
    ESTADO_INVESTIDA = "investida"
    ESTADO_RECUO = "recuo"
    ESTADO_RESPIRO = "respiro"

    def __init__(self, x: float, y: float):
        super().__init__(x, y, largura=40, altura=82, vida_max=INIMIGO_MELEE_VIDA)
        self.velocidade_investida = INIMIGO_MELEE_VELOCIDADE
        self.velocidade_recuo = INIMIGO_MELEE_VELOCIDADE_RECUO
        self.dano_contato = INIMIGO_MELEE_DANO_CONTATO
        self.distancia_visao = INIMIGO_MELEE_DISTANCIA_VISAO

        self.estado_combate = self.ESTADO_PATRULHA
        self.tempo_estado = 0.0
        self.animacao_ataque_tempo = 0.0
        self.tempo_anim_passo = 0.0

    def atualizar(self, dt: float, jogador, obstaculos: list[pg.Rect], lista_projeteis: list = None) -> None:
        if not self.vivo:
            if self.tempo_morte > 0:
                self.tempo_morte -= dt
            return

        if self.tempo_dano > 0:
            self.tempo_dano -= dt
        if self.animacao_ataque_tempo > 0:
            self.animacao_ataque_tempo -= dt
        if self.tempo_estado > 0:
            self.tempo_estado -= dt

        dist_x = jogador.rect.centerx - self.rect.centerx
        dist_y = abs(jogador.rect.centery - self.rect.centery)
        dist_abs = abs(dist_x)
        jogador_detectado = dist_abs <= self.distancia_visao and dist_y <= 90

        # Máquina de estados de combate (Investida / Recuo / Respiro)
        if self.estado_combate == self.ESTADO_PATRULHA:
            if jogador_detectado:
                self.estado_combate = self.ESTADO_INVESTIDA
            else:
                # Patrulha calma pela plataforma
                if self.no_chao and self.verificar_borda_frente(obstaculos):
                    self.olhando_direita = not self.olhando_direita
                dir_mov = 1 if self.olhando_direita else -1
                self.vx = dir_mov * (self.velocidade_investida * 0.55)

        elif self.estado_combate == self.ESTADO_INVESTIDA:
            self.olhando_direita = dist_x > 0
            dir_mov = 1 if self.olhando_direita else -1

            # Não corre se houver abismo entre ele e o jogador na plataforma
            if self.no_chao and self.verificar_borda_frente(obstaculos):
                self.vx = 0.0
            else:
                self.vx = dir_mov * self.velocidade_investida

            # Se atingir distância de ataque (46px), desfere o golpe e entra em recuo
            if dist_abs <= 46 and dist_y <= 60:
                self.animacao_ataque_tempo = 0.22
                jogador.receber_dano(self.dano_contato)
                # Inicia recuo tático imediato para trás por 0.28s
                self.estado_combate = self.ESTADO_RECUO
                self.tempo_estado = 0.28
                dir_recuo = -1 if self.olhando_direita else 1
                self.vx = dir_recuo * self.velocidade_recuo

        elif self.estado_combate == self.ESTADO_RECUO:
            # Salta para trás recuando do jogador
            dir_recuo = -1 if self.olhando_direita else 1
            if self.no_chao and self.verificar_borda_atras(obstaculos):
                self.vx = 0.0
                self.estado_combate = self.ESTADO_RESPIRO
                self.tempo_estado = INIMIGO_MELEE_TEMPO_RESPIRO
            else:
                self.vx = dir_recuo * self.velocidade_recuo

            if self.tempo_estado <= 0 or dist_abs >= 130:
                self.vx = 0.0
                self.estado_combate = self.ESTADO_RESPIRO
                self.tempo_estado = INIMIGO_MELEE_TEMPO_RESPIRO

        elif self.estado_combate == self.ESTADO_RESPIRO:
            # Guarda aberta dando respiro e janela para o jogador contra-atacar
            self.olhando_direita = dist_x > 0
            self.vx = 0.0
            if self.tempo_estado <= 0:
                # Volta a investir contra o jogador se ele ainda estiver perto
                self.estado_combate = self.ESTADO_INVESTIDA if jogador_detectado else self.ESTADO_PATRULHA

        if abs(self.vx) > 10:
            self.tempo_anim_passo += dt * 9.0

        self.aplicar_fisica_e_colisoes(dt, obstaculos)

    def desenhar(self, tela: pg.Surface, camera) -> None:
        if not self.vivo and self.tempo_morte <= 0:
            return

        visivel = camera.aplicar(self.rect)
        if not tela.get_rect().colliderect(visivel):
            return

        direcao = 1 if self.olhando_direita else -1

        if self.tempo_dano > 0 and (int(self.tempo_dano * 18) % 2 == 0):
            cor_corpo = (240, 80, 80)
            cor_roupa = (220, 100, 100)
        else:
            cor_corpo = (210, 160, 120)
            cor_roupa = (140, 110, 75)

        if not self.vivo:
            pg.draw.rect(tela, (110, 60, 40), (visivel.x, visivel.bottom - 16, visivel.width + 10, 14))
            return

        # 1. Pernas com passos animados
        offset_passo = round(math.sin(self.tempo_anim_passo) * 4) if self.no_chao else 0
        pg.draw.rect(tela, (110, 90, 65), (visivel.centerx - 12, visivel.bottom - 22 - offset_passo, 10, 22))
        pg.draw.rect(tela, (110, 90, 65), (visivel.centerx + 2, visivel.bottom - 22 + offset_passo, 10, 22))

        # 2. Tronco
        tronco_rect = pg.Rect(visivel.x + 6, visivel.y + 26, visivel.width - 12, 34)
        pg.draw.rect(tela, cor_roupa, tronco_rect)
        pg.draw.rect(tela, (65, 45, 25), (tronco_rect.x, tronco_rect.y, 6, 34))
        pg.draw.rect(tela, (65, 45, 25), (tronco_rect.right - 6, tronco_rect.y, 6, 34))

        # 3. Cabeça e Chapéu Meia-Lua
        pg.draw.circle(tela, cor_corpo, (visivel.centerx, visivel.y + 16), 11)
        pg.draw.rect(tela, (40, 90, 120), (visivel.centerx - 8, visivel.y + 22, 16, 5))

        chapeu_rect = pg.Rect(visivel.centerx - 20, visivel.y + 4, 40, 13)
        pg.draw.ellipse(tela, (85, 50, 25), chapeu_rect)
        pg.draw.ellipse(tela, (55, 30, 15), chapeu_rect, 2)

        # 4. Braço com a Peixeira
        if self.animacao_ataque_tempo > 0:
            mao_x = visivel.centerx + (26 * direcao)
            mao_y = visivel.y + 30
            pg.draw.line(tela, (230, 230, 245), (mao_x, mao_y), (mao_x + (22 * direcao), mao_y - 4), 4)
            pg.draw.circle(tela, (255, 100, 80), (mao_x + (22 * direcao), mao_y - 4), 4)
            pg.draw.line(tela, cor_corpo, (visivel.centerx, visivel.y + 30), (mao_x, mao_y), 5)
        elif self.estado_combate == self.ESTADO_RESPIRO:
            # Em guarda defensiva recuada
            mao_x = visivel.centerx + (10 * direcao)
            mao_y = visivel.y + 34
            pg.draw.line(tela, cor_corpo, (visivel.centerx, visivel.y + 30), (mao_x, mao_y), 4)
            pg.draw.line(tela, (215, 215, 230), (mao_x, mao_y), (mao_x + (10 * direcao), mao_y - 12), 3)
        else:
            mao_x = visivel.centerx + (18 * direcao)
            mao_y = visivel.y + 36
            pg.draw.line(tela, cor_corpo, (visivel.centerx, visivel.y + 30), (mao_x, mao_y), 5)
            pg.draw.line(tela, (215, 215, 230), (mao_x, mao_y), (mao_x + (16 * direcao), mao_y - 8), 3)

        # 5. Barra de Vida
        if self.vida < self.vida_max:
            barra_bg = pg.Rect(visivel.centerx - 18, visivel.y - 8, 36, 5)
            larg_hp = int((self.vida / self.vida_max) * 36)
            pg.draw.rect(tela, (30, 15, 15), barra_bg)
            pg.draw.rect(tela, COR_VIDA, (barra_bg.x, barra_bg.y, larg_hp, 5))


class InimigoAtirador(Inimigo):
    """
    Cangaceiro Atirador / Espingardeiro.
    Patrulha ativamente a plataforma e atira na horizontal ou na diagonal (mirando o herói).
    """

    def __init__(self, x: float, y: float):
        super().__init__(x, y, largura=40, altura=82, vida_max=INIMIGO_RANGED_VIDA)
        self.velocidade_patrulha = INIMIGO_RANGED_VELOCIDADE
        self.dano_tiro = INIMIGO_RANGED_DANO_TIRO
        self.alcance_tiro = INIMIGO_RANGED_DISTANCIA_TIRO

        self.tempo_recarga = 1.0
        self.animacao_disparo_tempo = 0.0
        self.angulo_mira = 0.0  # Ângulo do cano em direção ao jogador
        self.tempo_anim_passo = 0.0

    def atualizar(self, dt: float, jogador, obstaculos: list[pg.Rect], lista_projeteis: list) -> None:
        if not self.vivo:
            if self.tempo_morte > 0:
                self.tempo_morte -= dt
            return

        if self.tempo_dano > 0:
            self.tempo_dano -= dt
        if self.tempo_recarga > 0:
            self.tempo_recarga -= dt
        if self.animacao_disparo_tempo > 0:
            self.animacao_disparo_tempo -= dt

        origem_x = self.rect.right if self.olhando_direita else self.rect.left
        origem_y = self.rect.centery - 8

        dx = jogador.rect.centerx - origem_x
        dy = jogador.rect.centery - origem_y
        dist_total = math.hypot(dx, dy)

        # Verifica se o jogador está dentro do campo de visão (520px)
        jogador_no_alcance = dist_total <= self.alcance_tiro and abs(dy) <= 260

        if jogador_no_alcance:
            # Mira diretamente no herói
            self.olhando_direita = dx > 0
            self.angulo_mira = math.atan2(dy, dx)

            # Para para disparar
            self.vx = 0.0

            # Disparo angular (horizontal ou diagonal) quando recarregado
            if self.tempo_recarga <= 0:
                self.tempo_recarga = INIMIGO_RANGED_COOLDOWN_TIRO
                self.animacao_disparo_tempo = 0.24

                # Vetor de velocidade do projétil normalizado
                vel_bala = 680.0
                vx_bala = math.cos(self.angulo_mira) * vel_bala
                vy_bala = math.sin(self.angulo_mira) * vel_bala

                ponta_cano_x = origem_x + math.cos(self.angulo_mira) * 26
                ponta_cano_y = origem_y + math.sin(self.angulo_mira) * 26

                proj = Projetil(
                    ponta_cano_x,
                    ponta_cano_y,
                    do_jogador=False,
                    vetor_vel=(vx_bala, vy_bala),
                )
                proj.dano = self.dano_tiro
                lista_projeteis.append(proj)

            # Se o jogador se aproximar perigosamente (< 95px), tenta recuar
            if dist_total < 95 and self.no_chao and not self.verificar_borda_atras(obstaculos):
                recuo_dir = -1 if self.olhando_direita else 1
                self.vx = recuo_dir * (self.velocidade_patrulha * 0.75)

        else:
            # Patrulha ativa: caminha vasculhando a plataforma
            if self.no_chao and self.verificar_borda_frente(obstaculos):
                self.olhando_direita = not self.olhando_direita
            dir_mov = 1 if self.olhando_direita else -1
            self.vx = dir_mov * self.velocidade_patrulha
            self.angulo_mira = 0.0 if self.olhando_direita else math.pi

        if abs(self.vx) > 10:
            self.tempo_anim_passo += dt * 8.0

        self.aplicar_fisica_e_colisoes(dt, obstaculos)

    def desenhar(self, tela: pg.Surface, camera) -> None:
        if not self.vivo and self.tempo_morte <= 0:
            return

        visivel = camera.aplicar(self.rect)
        if not tela.get_rect().colliderect(visivel):
            return

        if self.tempo_dano > 0 and (int(self.tempo_dano * 18) % 2 == 0):
            cor_corpo = (240, 80, 80)
            cor_roupa = (220, 100, 100)
        else:
            cor_corpo = (215, 165, 125)
            cor_roupa = (160, 130, 80)

        if not self.vivo:
            pg.draw.rect(tela, (90, 50, 35), (visivel.x, visivel.bottom - 16, visivel.width + 12, 14))
            return

        # 1. Pernas animadas
        offset_passo = round(math.sin(self.tempo_anim_passo) * 4) if self.no_chao else 0
        pg.draw.rect(tela, (95, 75, 55), (visivel.centerx - 11, visivel.bottom - 22 - offset_passo, 9, 22))
        pg.draw.rect(tela, (95, 75, 55), (visivel.centerx + 2, visivel.bottom - 22 + offset_passo, 9, 22))

        # 2. Tronco e Cartucheiras
        tronco_rect = pg.Rect(visivel.x + 6, visivel.y + 26, visivel.width - 12, 34)
        pg.draw.rect(tela, cor_roupa, tronco_rect)
        pg.draw.line(tela, (50, 30, 15), tronco_rect.topleft, tronco_rect.bottomright, 3)
        pg.draw.line(tela, (50, 30, 15), tronco_rect.topright, tronco_rect.bottomleft, 3)

        # 3. Cabeça e Chapéu
        pg.draw.circle(tela, cor_corpo, (visivel.centerx, visivel.y + 16), 11)
        pg.draw.rect(tela, (215, 160, 40), (visivel.centerx - 8, visivel.y + 22, 16, 5))

        chapeu_rect = pg.Rect(visivel.centerx - 21, visivel.y + 4, 42, 13)
        pg.draw.ellipse(tela, (95, 60, 30), chapeu_rect)
        pg.draw.ellipse(tela, (65, 35, 15), chapeu_rect, 2)
        pg.draw.circle(tela, (230, 200, 100), (visivel.centerx, visivel.y + 8), 2)

        # 4. Fuzil Mauser / Winchester com Mira Angular (Pode mirar na diagonal!)
        origem_ombro_x = visivel.centerx
        origem_ombro_y = visivel.y + 32

        comprimento_cano = 28
        cano_x = origem_ombro_x + math.cos(self.angulo_mira) * comprimento_cano
        cano_y = origem_ombro_y + math.sin(self.angulo_mira) * comprimento_cano

        # Cano da arma
        pg.draw.line(tela, (50, 45, 50), (origem_ombro_x, origem_ombro_y), (cano_x, cano_y), 5)
        # Coronha de madeira
        coronha_x = origem_ombro_x - math.cos(self.angulo_mira) * 10
        coronha_y = origem_ombro_y - math.sin(self.angulo_mira) * 10
        pg.draw.line(tela, (110, 60, 30), (coronha_x, coronha_y), (origem_ombro_x, origem_ombro_y), 6)

        # Clarão do tiro na ponta do cano (Muzzle flash na diagonal correspondente)
        if self.animacao_disparo_tempo > 0:
            flash_ponto = (round(cano_x + math.cos(self.angulo_mira) * 6), round(cano_y + math.sin(self.angulo_mira) * 6))
            pg.draw.circle(tela, (255, 230, 100), flash_ponto, 9)
            pg.draw.circle(tela, (255, 120, 40), flash_ponto, 5)

        # 5. Barra de Vida
        if self.vida < self.vida_max:
            barra_bg = pg.Rect(visivel.centerx - 18, visivel.y - 8, 36, 5)
            larg_hp = int((self.vida / self.vida_max) * 36)
            pg.draw.rect(tela, (30, 15, 15), barra_bg)
            pg.draw.rect(tela, COR_VIDA, (barra_bg.x, barra_bg.y, larg_hp, 5))
