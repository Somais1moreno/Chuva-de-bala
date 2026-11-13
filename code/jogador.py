import os
import pygame as pg
from constantes import (
    ACELERACAO,
    ALCANCE_PEIXEIRA_X,
    ALCANCE_PEIXEIRA_Y,
    ATRITO,
    COOLDOWN_PEIXEIRA,
    COOLDOWN_TIRO,
    COR_BLOQUEIO,
    COR_BRANCO,
    COR_CURA,
    COR_MUNICÃO,
    COR_PRETO,
    CORTE_PULO_FATOR,
    CURA_REMEDIO,
    DANO_PEIXEIRA,
    DANO_QUEDA_ABISMO,
    FATOR_REDUCAO_BLOQUEIO,
    FORCA_PULO,
    GRAVIDADE,
    MUNICÃO_INICIAL,
    REMEDIOS_INICIAIS,
    TEMPO_COYOTE,
    TEMPO_INVENCIVEL_JOGADOR,
    TEMPO_JUMP_BUFFER,
    VELOCIDADE_MAX,
    VELOCIDADE_TERMINAL,
    VIDA_MAX_JOGADOR,
    obter_caminho_asset,
)
from projetil import Projetil


class Jogador:
    def __init__(self, x: float, y: float):
        # Dimensões da hitbox (42 x 84 px em pé)
        self.largura = 42
        self.altura_em_pe = 84
        self.altura_agachado = 54
        self.altura_atual = self.altura_em_pe

        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0

        self.rect = pg.Rect(round(self.x), round(self.y), self.largura, self.altura_atual)
        self.ultimo_chao_seguro = (self.x, self.y)

        # Estados de chão e física
        self.no_chao = False
        self.tempo_desde_chao = 0.0  # Para Coyote Time
        self.tempo_jump_buffer = 0.0  # Para Buffer de Pulo
        self.olhando_direita = True
        self.agachado = False
        self.bloqueando = False
        self.tempo_anim_corrida = 0.0

        # Status e Combate
        self.vida = VIDA_MAX_JOGADOR
        self.municao = MUNICÃO_INICIAL
        self.remedios = REMEDIOS_INICIAIS
        self.cooldown_peixeira = 0.0
        self.cooldown_tiro = 0.0
        self.animacao_golpe_tempo = 0.0
        self.animacao_tiro_tempo = 0.0
        self.animacao_cura_tempo = 0.0
        self.animacao_bloqueio_tempo = 0.0
        self.tempo_invencivel = 0.0

        # Dicionário de sprites (carregados quando disponíveis)
        self.sprites = {}
        self._carregar_sprites()

    def _carregar_sprites(self):
        """Carrega os novos sprites caso já tenham sido gerados e salvos em Assets."""
        arquivos = {
            "idle": "heroi_idle.png",
            "correndo": "heroi_correndo.png",
            "pulando": "heroi_pulando.png",
            "agachado": "heroi_agachado.png",
            "faca": "heroi_ataque_faca.png",
            "tiro": "heroi_atirando.png",
        }

        for estado, nome_arquivo in arquivos.items():
            caminho = obter_caminho_asset(nome_arquivo)
            if os.path.exists(caminho):
                try:
                    img = pg.image.load(caminho).convert_alpha()
                    alvo_alt = self.altura_em_pe if estado != "agachado" else self.altura_agachado
                    escala = alvo_alt / img.get_height()
                    alvo_larg = max(round(img.get_width() * escala), 42)
                    redim = pg.transform.smoothscale(img, (alvo_larg, alvo_alt))
                    self.sprites[f"{estado}_dir"] = redim
                    self.sprites[f"{estado}_esq"] = pg.transform.flip(redim, True, False)
                except Exception as erro:
                    print(f"[Aviso] Falha ao carregar {nome_arquivo}: {erro}")

    def tentar_pular(self):
        """Registra intenção de pulo (jump buffering)."""
        self.tempo_jump_buffer = TEMPO_JUMP_BUFFER

    def soltar_pulo(self):
        """Pulo com altura variável: soltar o botão corta a subida."""
        if self.vy < -150.0:
            self.vy *= CORTE_PULO_FATOR

    def tomar_remedio(self) -> bool:
        """Consome 1 frasco de remédio para curar vida (tecla Q)."""
        if self.remedios <= 0 or self.vida >= VIDA_MAX_JOGADOR:
            return False

        self.remedios -= 1
        self.vida = min(VIDA_MAX_JOGADOR, self.vida + CURA_REMEDIO)
        self.animacao_cura_tempo = 0.55
        return True

    def atacar_peixeira(self, caixas: list, inimigos: list = None) -> bool:
        """Ataque melee com peixeira (tecla J). Atinge caixas e inimigos."""
        if self.cooldown_peixeira > 0.0:
            return False

        self.cooldown_peixeira = COOLDOWN_PEIXEIRA
        self.animacao_golpe_tempo = 0.22

        x_corte = self.rect.right if self.olhando_direita else self.rect.left - ALCANCE_PEIXEIRA_X
        hitbox_peixeira = pg.Rect(x_corte, self.rect.y + 16, ALCANCE_PEIXEIRA_X, ALCANCE_PEIXEIRA_Y)

        for c in caixas:
            if not c.destruida and hitbox_peixeira.colliderect(c.rect):
                c.receber_dano(1)

        if inimigos:
            dir_golpe = 1 if self.olhando_direita else -1
            for ini in inimigos:
                if ini.vivo and hitbox_peixeira.colliderect(ini.rect):
                    ini.receber_dano(DANO_PEIXEIRA, empurrao_dir=dir_golpe)

        return True

    def atirar(self, lista_projeteis: list) -> bool:
        """Dispara projétil de pistola (tecla K)."""
        if self.cooldown_tiro > 0.0 or self.municao <= 0 or self.bloqueando:
            return False

        self.municao -= 1
        self.cooldown_tiro = COOLDOWN_TIRO
        self.animacao_tiro_tempo = 0.20

        direcao = 1 if self.olhando_direita else -1
        origem_x = self.rect.right if self.olhando_direita else self.rect.left - 14
        origem_y = self.rect.centery - (8 if not self.agachado else 0)

        proj = Projetil(origem_x, origem_y, direcao=direcao, do_jogador=True)
        lista_projeteis.append(proj)
        return True

    def receber_dano(self, quantidade: int) -> None:
        if self.tempo_invencivel > 0.0:
            return

        # Redução substancial de dano ao bloquear com W
        if self.bloqueando:
            quantidade = max(1, round(quantidade * (1.0 - FATOR_REDUCAO_BLOQUEIO)))
            self.animacao_bloqueio_tempo = 0.25

        self.vida = max(0, self.vida - quantidade)
        self.tempo_invencivel = TEMPO_INVENCIVEL_JOGADOR

    def respawnar_no_ultimo_chao(self):
        self.x, self.y = self.ultimo_chao_seguro
        self.vx = 0.0
        self.vy = 0.0
        self.rect.topleft = (round(self.x), round(self.y))
        self.receber_dano(DANO_QUEDA_ABISMO)

    def atualizar(
        self,
        dt: float,
        teclas,
        obstaculos: list[pg.Rect],
        caixas: list,
        coletaveis: list,
        limite_queda: int,
    ) -> None:
        # Atualização de temporizadores
        if self.cooldown_peixeira > 0:
            self.cooldown_peixeira -= dt
        if self.cooldown_tiro > 0:
            self.cooldown_tiro -= dt
        if self.animacao_golpe_tempo > 0:
            self.animacao_golpe_tempo -= dt
        if self.animacao_tiro_tempo > 0:
            self.animacao_tiro_tempo -= dt
        if self.animacao_cura_tempo > 0:
            self.animacao_cura_tempo -= dt
        if self.animacao_bloqueio_tempo > 0:
            self.animacao_bloqueio_tempo -= dt
        if self.tempo_invencivel > 0:
            self.tempo_invencivel -= dt

        # Controle de bloqueio com W (apenas se não estiver agachado)
        self.bloqueando = bool(teclas[pg.K_w]) and not self.agachado

        # Controle de agachamento com S (apenas no chão)
        quer_agachar = bool(teclas[pg.K_s]) and self.no_chao
        if quer_agachar != self.agachado:
            self.agachado = quer_agachar
            self.altura_atual = self.altura_agachado if self.agachado else self.altura_em_pe
            pos_inferior = self.rect.bottom
            self.rect.height = self.altura_atual
            self.rect.bottom = pos_inferior
            self.y = float(self.rect.y)

        # Entrada Horizontal (Restrita a A e D, sem setas)
        mov_dir = 0
        if not self.agachado:
            if teclas[pg.K_d]:
                mov_dir += 1
            if teclas[pg.K_a]:
                mov_dir -= 1

        vel_limite = VELOCIDADE_MAX * (0.35 if self.bloqueando else 1.0)
        if mov_dir != 0:
            self.olhando_direita = mov_dir > 0
            self.vx += mov_dir * ACELERACAO * dt
            if abs(self.vx) > vel_limite:
                self.vx = vel_limite * mov_dir
            if self.no_chao:
                self.tempo_anim_corrida += dt * 10.0
        else:
            if abs(self.vx) > ATRITO * dt:
                self.vx -= (1 if self.vx > 0 else -1) * ATRITO * dt
            else:
                self.vx = 0.0
            self.tempo_anim_corrida = 0.0

        # Lógica de pulo: Coyote Time & Jump Buffer
        if self.no_chao:
            self.tempo_desde_chao = 0.0
        else:
            self.tempo_desde_chao += dt

        if self.tempo_jump_buffer > 0.0:
            self.tempo_jump_buffer -= dt
            if self.tempo_desde_chao <= TEMPO_COYOTE and not self.agachado:
                self.vy = FORCA_PULO
                self.no_chao = False
                self.tempo_desde_chao = TEMPO_COYOTE + 1.0
                self.tempo_jump_buffer = 0.0

        # Gravidade contínua
        if not self.no_chao or self.vy < 0:
            self.vy += GRAVIDADE * dt
            if self.vy > VELOCIDADE_TERMINAL:
                self.vy = VELOCIDADE_TERMINAL

        # --- Movimento e Resolução de Colisão em X ---
        self.x += self.vx * dt
        self.rect.x = round(self.x)

        for obstaculo in obstaculos:
            if self.rect.colliderect(obstaculo):
                if self.vx > 0:
                    self.rect.right = obstaculo.left
                    self.vx = 0.0
                elif self.vx < 0:
                    self.rect.left = obstaculo.right
                    self.vx = 0.0
                self.x = float(self.rect.x)

        # --- Movimento e Resolução de Colisão em Y ---
        self.y += self.vy * dt
        self.rect.y = round(self.y)

        estava_no_chao = self.no_chao
        for obstaculo in obstaculos:
            if self.rect.colliderect(obstaculo):
                if self.vy > 0:  # Caindo / aterrissando no chão
                    self.rect.bottom = obstaculo.top
                    self.vy = 0.0
                    self.y = float(self.rect.y)
                    if not estava_no_chao:
                        self.ultimo_chao_seguro = (self.x, self.y)
                elif self.vy < 0:  # Batendo no teto
                    self.rect.top = obstaculo.bottom
                    self.vy = 0.0
                    self.y = float(self.rect.y)

        # Sensor de solo estável
        sensor_chao = pg.Rect(self.rect.x + 6, self.rect.bottom, self.rect.width - 12, 3)
        tocou_chao = any(sensor_chao.colliderect(obs) for obs in obstaculos)

        if tocou_chao and self.vy >= 0:
            self.no_chao = True
            self.vy = 0.0
            self.tempo_desde_chao = 0.0
        else:
            self.no_chao = False

        # Checa queda no abismo
        if self.rect.top > limite_queda:
            self.respawnar_no_ultimo_chao()

        # Coleta de munição
        for c in coletaveis:
            if not c.coletado and self.rect.colliderect(c.rect):
                c.coletado = True
                self.municao += c.quantidade

    def desenhar(self, tela: pg.Surface, camera) -> None:
        visivel = camera.aplicar(self.rect)

        # Piscar se estiver invencível após levar dano
        if self.tempo_invencivel > 0 and (int(self.tempo_invencivel * 12) % 2 == 0):
            return

        sufixo = "dir" if self.olhando_direita else "esq"

        # Tentar usar sprite da folha se existir
        nome_sprite = None
        if self.animacao_golpe_tempo > 0:
            nome_sprite = f"faca_{sufixo}"
        elif self.animacao_tiro_tempo > 0:
            nome_sprite = f"tiro_{sufixo}"
        elif self.agachado:
            nome_sprite = f"agachado_{sufixo}"
        elif not self.no_chao:
            nome_sprite = f"pulando_{sufixo}"
        elif abs(self.vx) > 20:
            nome_sprite = f"correndo_{sufixo}"
        else:
            nome_sprite = f"idle_{sufixo}"

        sprite_img = self.sprites.get(nome_sprite)

        if sprite_img:
            desenho_rect = sprite_img.get_rect(midbottom=visivel.midbottom)
            tela.blit(sprite_img, desenho_rect)
        else:
            self._desenhar_heroi_procedural(tela, visivel)

        # Efeito visual de Bloqueio (W)
        if self.bloqueando or self.animacao_bloqueio_tempo > 0:
            direcao = 1 if self.olhando_direita else -1
            escudo_x = visivel.centerx + (16 * direcao)
            escudo_rect = pg.Rect(escudo_x - 10, visivel.centery - 22, 20, 44)
            pg.draw.arc(
                tela,
                COR_BLOQUEIO,
                escudo_rect,
                -1.2 if self.olhando_direita else 1.9,
                1.2 if self.olhando_direita else 4.3,
                4,
            )

        # Efeito visual do corte da Peixeira (slash arc)
        if self.animacao_golpe_tempo > 0:
            x_corte = visivel.right - 8 if self.olhando_direita else visivel.left - ALCANCE_PEIXEIRA_X + 8
            y_corte = visivel.y + 12
            arco_rect = pg.Rect(x_corte, y_corte, ALCANCE_PEIXEIRA_X, ALCANCE_PEIXEIRA_Y)

            pg.draw.arc(
                tela,
                COR_BRANCO,
                arco_rect,
                -0.6 if self.olhando_direita else 2.5,
                1.8 if self.olhando_direita else 4.9,
                4,
            )
            ponto_ponta = (
                (visivel.right + 28, visivel.centery - 6)
                if self.olhando_direita
                else (visivel.left - 28, visivel.centery - 6)
            )
            pg.draw.circle(tela, (255, 235, 150), ponto_ponta, 6)
            pg.draw.circle(tela, COR_BRANCO, ponto_ponta, 3)

        # Efeito visual de Cura com Remédio (Q)
        if self.animacao_cura_tempo > 0:
            import math
            fator_cura = self.animacao_cura_tempo / 0.55
            offset_y_cura = round((1.0 - fator_cura) * 40)
            # Cruzes verdes luminosas subindo
            for ox in (-12, 0, 12):
                cx = visivel.centerx + ox
                cy = visivel.centery - offset_y_cura
                pg.draw.line(tela, COR_CURA, (cx - 4, cy), (cx + 4, cy), 2)
                pg.draw.line(tela, COR_CURA, (cx, cy - 4), (cx, cy + 4), 2)

    def _desenhar_heroi_procedural(self, tela: pg.Surface, visivel: pg.Rect):
        direcao = 1 if self.olhando_direita else -1

        # Cores temáticas do Cangaço
        cor_chapeu = (120, 75, 40)
        cor_lenço = (210, 45, 45)
        cor_camisa = (215, 195, 160)
        cor_colete = (95, 55, 30)
        cor_calca = (160, 140, 110)
        cor_pele = (230, 175, 130)
        cor_peixeira = (240, 240, 250)

        # 1. Pernas
        offset_perna = 0
        if not self.no_chao:
            offset_perna = -6
        elif abs(self.vx) > 20:
            import math
            offset_perna = round(math.sin(self.tempo_anim_corrida) * 5)

        alt_pernas = 24 if not self.agachado else 12
        y_pernas = visivel.bottom - alt_pernas
        larg_perna = 12

        pg.draw.rect(tela, cor_calca, (visivel.centerx - 14, y_pernas - offset_perna, larg_perna, alt_pernas))
        pg.draw.rect(tela, cor_calca, (visivel.centerx + 2, y_pernas + offset_perna, larg_perna, alt_pernas))
        pg.draw.rect(tela, (70, 40, 20), (visivel.centerx - 16, visivel.bottom - 6 - offset_perna, larg_perna + 4, 6))
        pg.draw.rect(tela, (70, 40, 20), (visivel.centerx, visivel.bottom - 6 + offset_perna, larg_perna + 4, 6))

        # 2. Tronco
        y_tronco = visivel.y + (28 if not self.agachado else 16)
        alt_tronco = 32 if not self.agachado else 26
        tronco_rect = pg.Rect(visivel.x + 8, y_tronco, visivel.width - 16, alt_tronco)
        pg.draw.rect(tela, cor_camisa, tronco_rect)
        pg.draw.rect(tela, cor_colete, (tronco_rect.x, tronco_rect.y, 8, alt_tronco))
        pg.draw.rect(tela, cor_colete, (tronco_rect.right - 8, tronco_rect.y, 8, alt_tronco))
        pg.draw.line(tela, (60, 35, 15), tronco_rect.topleft, tronco_rect.bottomright, 3)

        # 3. Cabeça & Lenço
        y_cabeca = visivel.y + (8 if not self.agachado else 4)
        pg.draw.circle(tela, cor_pele, (visivel.centerx, y_cabeca + 12), 11)
        pg.draw.rect(tela, cor_lenço, (visivel.centerx - 9, y_cabeca + 20, 18, 5))

        # 4. Chapéu Meia-Lua
        chapeu_rect = pg.Rect(visivel.centerx - 22, y_cabeca - 2, 44, 14)
        pg.draw.ellipse(tela, cor_chapeu, chapeu_rect)
        pg.draw.ellipse(tela, (75, 45, 25), chapeu_rect, 2)
        pg.draw.circle(tela, (230, 230, 240), (visivel.centerx, y_cabeca + 4), 3)

        # 5. Braços e Armas de Acordo com a Ação
        if self.bloqueando:
            # Postura defensiva de Bloqueio (W): braços cruzados com peixeira erguida em guarda
            mao_x = visivel.centerx + (12 * direcao)
            mao_y = y_tronco + 8
            pg.draw.line(tela, cor_pele, (visivel.centerx - (4 * direcao), y_tronco + 14), (mao_x, mao_y), 5)
            # Faca posicionada na vertical defendendo o peito
            pg.draw.line(tela, cor_peixeira, (mao_x, mao_y + 12), (mao_x, mao_y - 14), 4)
            pg.draw.circle(tela, COR_BLOQUEIO, (mao_x, mao_y), 3)

        elif self.animacao_golpe_tempo > 0:
            mao_x = visivel.centerx + (20 * direcao)
            mao_y = y_tronco + 12
            pg.draw.line(tela, cor_pele, (visivel.centerx, y_tronco + 8), (mao_x, mao_y), 5)
            ponta_faca = mao_x + (22 * direcao)
            pg.draw.line(tela, cor_peixeira, (mao_x, mao_y), (ponta_faca, mao_y - 2), 4)
            pg.draw.line(tela, (80, 45, 20), (mao_x - (4 * direcao), mao_y), (mao_x, mao_y), 4)

        elif self.animacao_tiro_tempo > 0:
            mao_x = visivel.centerx + (22 * direcao)
            mao_y = y_tronco + 10
            pg.draw.line(tela, cor_pele, (visivel.centerx, y_tronco + 8), (mao_x, mao_y), 5)
            pg.draw.rect(tela, (50, 50, 60), (mao_x if direcao > 0 else mao_x - 12, mao_y - 3, 12, 6))
            pg.draw.circle(tela, COR_MUNICÃO, (mao_x + (14 * direcao), mao_y), 6)

        else:
            # Guarda em repouso
            braco_x = visivel.centerx + (10 * direcao)
            pg.draw.line(tela, cor_pele, (visivel.centerx, y_tronco + 6), (braco_x, y_tronco + 18), 4)
            bainha_x = visivel.centerx - (10 * direcao)
            pg.draw.line(tela, (60, 35, 15), (bainha_x, y_tronco + 14), (bainha_x, y_tronco + 28), 4)
