import pygame as pg
from .constantes import ALTURA_TELA, LARGURA_TELA


class Camera:
    def __init__(self, largura_nivel: int, altura_nivel: int):
        self.largura_nivel = largura_nivel
        self.altura_nivel = altura_nivel
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.suavidade = 8.0  # Velocidade do lerp

    def atualizar(self, alvo_rect: pg.Rect, dt: float) -> None:
        # Posição desejada: centralizar o alvo na tela
        desejado_x = alvo_rect.centerx - (LARGURA_TELA / 2)
        desejado_y = alvo_rect.centery - (ALTURA_TELA / 2) - 40  # levemente mais acima para ver o chão

        # Limitar dentro dos limites do nível
        limite_max_x = max(0, self.largura_nivel - LARGURA_TELA)
        limite_max_y = max(0, self.altura_nivel - ALTURA_TELA)

        desejado_x = max(0.0, min(float(limite_max_x), desejado_x))
        desejado_y = max(0.0, min(float(limite_max_y), desejado_y))

        # Interpolação suave (lerp independente de taxa de quadros)
        fator = min(1.0, self.suavidade * dt)
        self.offset_x += (desejado_x - self.offset_x) * fator
        self.offset_y += (desejado_y - self.offset_y) * fator

    def aplicar(self, rect: pg.Rect) -> pg.Rect:
        """Retorna um novo Rect com as coordenadas ajustadas pela câmera."""
        return rect.move(-round(self.offset_x), -round(self.offset_y))

    def aplicar_pos(self, x: float, y: float) -> tuple[int, int]:
        """Ajusta coordenadas livres para o espaço da tela."""
        return round(x - self.offset_x), round(y - self.offset_y)
