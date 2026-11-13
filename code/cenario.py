import os
import pygame as pg
from constantes import (
    ALTURA_NIVEL_PADRAO,
    COR_CHAO_DETALHE,
    COR_CHAO_ROCHA,
    COR_CHAO_SUPERIOR,
    COR_MUNICÃO,
    LARGURA_NIVEL_PADRAO,
    MUNICAO_POR_COLETAVEL,
    TAMANHO_CAIXA,
    VIDA_CAIXA,
    X_ARENA_BOSS,
    obter_caminho_asset,
)
from inimigo import Inimigo, InimigoAtirador, InimigoMelee


class Plataforma:
    def __init__(self, x: int, y: int, largura: int, altura: int, tipo: str = "chao"):
        self.rect = pg.Rect(x, y, largura, altura)
        self.tipo = tipo  # 'chao', 'flutuante', 'parede'

    def desenhar(self, tela: pg.Surface, camera) -> None:
        visivel = camera.aplicar(self.rect)
        if not tela.get_rect().colliderect(visivel):
            return

        # Fundo rochoso
        pg.draw.rect(tela, COR_CHAO_ROCHA, visivel)

        # Topo de terra batida seca
        espessura_topo = min(12, self.rect.height)
        topo_rect = pg.Rect(visivel.x, visivel.y, visivel.width, espessura_topo)
        pg.draw.rect(tela, COR_CHAO_SUPERIOR, topo_rect)

        # Linha rústica de divisão
        pg.draw.line(
            tela,
            COR_CHAO_DETALHE,
            (visivel.left, visivel.top + espessura_topo),
            (visivel.right, visivel.top + espessura_topo),
            2,
        )


class ParticulaMadeira:
    def __init__(self, x: float, y: float, vx: float, vy: float, tamanho: int = 5):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.tamanho = tamanho
        self.vida = 0.45

    def atualizar(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 900.0 * dt
        self.vida -= dt
        return self.vida > 0

    def desenhar(self, tela: pg.Surface, camera) -> None:
        px, py = camera.aplicar_pos(self.x, self.y)
        pg.draw.rect(tela, (135, 85, 45), (px, py, self.tamanho, self.tamanho))


class Caixa:
    _imagens_carregadas = False
    _img_intacta = None
    _img_danificada = None
    _img_destruida = None

    def __init__(self, x: int, y: int, tamanho: int = TAMANHO_CAIXA):
        self.rect = pg.Rect(x, y, tamanho, tamanho)
        self.tamanho = tamanho
        self.vida = VIDA_CAIXA
        self.destruida = False
        self._carregar_imagens()

    @classmethod
    def _carregar_imagens(cls):
        if cls._imagens_carregadas:
            return
        cls._imagens_carregadas = True
        try:
            p_int = obter_caminho_asset("caixa_intacta.png")
            p_dan = obter_caminho_asset("caixa_danificada.png")
            p_des = obter_caminho_asset("caixa_destruida.png")

            if os.path.exists(p_int):
                cls._img_intacta = pg.image.load(p_int).convert_alpha()
            if os.path.exists(p_dan):
                cls._img_danificada = pg.image.load(p_dan).convert_alpha()
            if os.path.exists(p_des):
                cls._img_destruida = pg.image.load(p_des).convert_alpha()
        except Exception as erro:
            print(f"[Aviso] Falha ao carregar imagens das caixas: {erro}")

    def receber_dano(self, dano: int = 1) -> bool:
        if self.destruida:
            return False
        self.vida -= dano
        if self.vida <= 0:
            self.destruida = True
            return True
        return False

    def desenhar(self, tela: pg.Surface, camera) -> None:
        # Se estiver destruída, não desenha nada (corrige o bug do quadrado marrom)
        if self.destruida:
            return

        visivel = camera.aplicar(self.rect)
        if not tela.get_rect().colliderect(visivel):
            return

        img = None
        if self.vida >= 3 and self._img_intacta:
            img = self._img_intacta
        elif self.vida == 2 and self._img_danificada:
            img = self._img_danificada
        elif self.vida == 1 and self._img_destruida:
            img = self._img_destruida

        if img:
            img_redim = pg.transform.smoothscale(img, (self.tamanho, self.tamanho))
            tela.blit(img_redim, visivel)
        else:
            cor = (150, 100, 50) if self.vida == 3 else (120, 80, 40)
            pg.draw.rect(tela, cor, visivel)
            pg.draw.rect(tela, (60, 40, 20), visivel, 3)
            if self.vida <= 2:
                pg.draw.line(tela, (40, 25, 15), visivel.topleft, visivel.center, 2)
            if self.vida == 1:
                pg.draw.line(tela, (40, 25, 15), visivel.topright, visivel.bottomleft, 2)


class ColetavelMunicao:
    def __init__(self, x: int, y: int, quantidade: int = MUNICAO_POR_COLETAVEL):
        self.rect = pg.Rect(x, y, 28, 28)
        self.quantidade = quantidade
        self.coletado = False
        self.tempo_animacao = 0.0

    def atualizar(self, dt: float):
        self.tempo_animacao += dt * 4.0

    def desenhar(self, tela: pg.Surface, camera) -> None:
        if self.coletado:
            return
        visivel = camera.aplicar(self.rect)
        if not tela.get_rect().colliderect(visivel):
            return

        import math
        offset_y = round(math.sin(self.tempo_animacao) * 4)
        pos = visivel.move(0, offset_y)

        pg.draw.rect(tela, (70, 50, 30), pos)
        pg.draw.rect(tela, COR_MUNICÃO, pos, 2)
        pg.draw.circle(tela, COR_MUNICÃO, (pos.centerx - 5, pos.centery), 3)
        pg.draw.circle(tela, COR_MUNICÃO, (pos.centerx + 5, pos.centery), 3)


class Nivel:
    def __init__(self):
        self.largura = LARGURA_NIVEL_PADRAO
        self.altura = ALTURA_NIVEL_PADRAO
        self.plataformas: list[Plataforma] = []
        self.caixas: list[Caixa] = []
        self.coletaveis: list[ColetavelMunicao] = []
        self.inimigos: list[Inimigo] = []
        self.particulas: list[ParticulaMadeira] = []
        self.ponto_inicio_jogador = (120, 450)
        self.limite_queda_morte = 800

        self._construir_fase()

    def _construir_fase(self):
        # Paredão esquerdo limite
        self.plataformas.append(Plataforma(-50, 0, 50, 720))

        # ======================================================================
        # SEÇÃO 1: Entrada do Sertão (0 a 950px)
        # ======================================================================
        self.plataformas.append(Plataforma(0, 560, 950, 160))
        # Caixas iniciais de treino
        self.caixas.append(Caixa(520, 492))
        self.caixas.append(Caixa(590, 492))
        self.caixas.append(Caixa(590, 424))

        # ======================================================================
        # SEÇÃO 2: Primeiro Buraco & Primeira Emboscada Melee (950 a 1900px)
        # ======================================================================
        # Fosso com plataforma flutuante de salto
        self.plataformas.append(Plataforma(1030, 450, 130, 32, tipo="flutuante"))

        # Piso de terra da emboscada
        self.plataformas.append(Plataforma(1240, 560, 700, 160))
        # 1 Inimigo Melee (Cangaceiro de Peixeira) patrulhando
        self.inimigos.append(InimigoMelee(1600, 470))
        # Barricada de caixas e munição para o herói
        self.caixas.append(Caixa(1400, 492))
        self.coletaveis.append(ColetavelMunicao(1420, 450, quantidade=4))
        self.caixas.append(Caixa(1780, 492))

        # ======================================================================
        # SEÇÃO 3: Ruínas Elevadas & O Primeiro Atirador (1900 a 3000px)
        # ======================================================================
        # Buraco e degraus de pedra
        self.plataformas.append(Plataforma(2000, 460, 120, 30, tipo="flutuante"))
        self.plataformas.append(Plataforma(2180, 560, 800, 160))

        # Plataforma alta de vigilância
        self.plataformas.append(Plataforma(2420, 420, 200, 32, tipo="flutuante"))
        # 1 Inimigo Atirador no topo mirando para frente
        self.inimigos.append(InimigoAtirador(2480, 330))

        # Caixas embaixo para se esconder com S dos tiros
        self.caixas.append(Caixa(2360, 492))
        self.caixas.append(Caixa(2720, 492))
        self.coletaveis.append(ColetavelMunicao(2740, 450, quantidade=4))

        # ======================================================================
        # SEÇÃO 4: O Vale dos Abismos & Combate Duplo (3000 a 4200px)
        # ======================================================================
        # Buraco duplo técnico com plataformas estreitas
        self.plataformas.append(Plataforma(3060, 450, 110, 28, tipo="flutuante"))
        self.plataformas.append(Plataforma(3240, 410, 110, 28, tipo="flutuante"))

        # Piso do vale
        self.plataformas.append(Plataforma(3420, 560, 800, 160))
        # 1 Melee agressivo na frente e 1 Atirador dando cobertura ao fundo
        self.inimigos.append(InimigoMelee(3600, 470))
        self.inimigos.append(InimigoAtirador(4050, 470))

        # Barricadas de caixas no meio do combate
        self.caixas.append(Caixa(3780, 492))
        self.caixas.append(Caixa(3780, 424))
        self.coletaveis.append(ColetavelMunicao(3880, 510, quantidade=5))

        # ======================================================================
        # SEÇÃO 5: A Fortificação dos Cangaceiros (4200 a 5400px - ~66% da fase)
        # ======================================================================
        self.plataformas.append(Plataforma(4300, 440, 120, 30, tipo="flutuante"))
        self.plataformas.append(Plataforma(4500, 560, 900, 160))

        # Degrau intermediário e plataforma superior da fortaleza (ajustada para salto confortável)
        self.plataformas.append(Plataforma(4600, 470, 90, 28, tipo="flutuante"))
        self.plataformas.append(Plataforma(4730, 410, 220, 32, tipo="flutuante"))
        # 1 Atirador em cima da muralha
        self.inimigos.append(InimigoAtirador(4800, 320))
        # 1 Melee embaixo guardando o portão
        self.inimigos.append(InimigoMelee(4680, 470))

        # Parede de caixas empilhadas
        self.caixas.append(Caixa(5100, 492))
        self.caixas.append(Caixa(5170, 492))
        self.caixas.append(Caixa(5170, 424))
        self.coletaveis.append(ColetavelMunicao(5250, 510, quantidade=6))

        # ======================================================================
        # SEÇÃO 6: O Desfiladeiro da Caatinga Pré-Boss (5400 a 6200px)
        # ======================================================================
        # Desfiladeiro perigoso com saltos sobre abismos
        self.plataformas.append(Plataforma(5470, 460, 100, 28, tipo="flutuante"))
        self.plataformas.append(Plataforma(5640, 420, 110, 28, tipo="flutuante"))
        self.plataformas.append(Plataforma(5820, 470, 120, 28, tipo="flutuante"))

        # Última patrulha antes da arena
        self.plataformas.append(Plataforma(6000, 560, 200, 160))
        self.inimigos.append(InimigoMelee(6050, 470))

        # ======================================================================
        # SEÇÃO 7: A Grande Arena do Boss Lampião (6200 a 7200px)
        # ======================================================================
        # Fosso de entrada da arena
        self.plataformas.append(Plataforma(6250, 560, 950, 160))

        # Barreiras e caixas de cobertura na arena para se proteger de Lampião
        self.caixas.append(Caixa(6450, 492))
        self.caixas.append(Caixa(6750, 492))
        self.caixas.append(Caixa(7050, 492))

        # Paredão direito final da fase
        self.plataformas.append(Plataforma(LARGURA_NIVEL_PADRAO, 0, 80, 720))

    def gerar_estilhacos(self, x: float, y: float):
        """Gera lascas e estilhaços de madeira quando uma caixa é destruída."""
        import random
        for _ in range(10):
            vx = random.uniform(-180.0, 180.0)
            vy = random.uniform(-280.0, -90.0)
            tam = random.randint(3, 6)
            self.particulas.append(ParticulaMadeira(x, y, vx, vy, tamanho=tam))

    def atualizar_particulas(self, dt: float):
        self.particulas = [p for p in self.particulas if p.atualizar(dt)]

    def desenhar_particulas(self, tela: pg.Surface, camera):
        for p in self.particulas:
            p.desenhar(tela, camera)

    def obter_obstaculos_solidos(self) -> list[pg.Rect]:
        """Retorna todos os retângulos sólidos para colisão."""
        solidos = [p.rect for p in self.plataformas]
        for c in self.caixas:
            if not c.destruida:
                solidos.append(c.rect)
        return solidos
