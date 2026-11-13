import math
from abc import ABC, abstractmethod
from typing import TypeVar

import pygame as pg


class Entidade(ABC):
    @abstractmethod
    def atualizar(self, teclas, dt: float, limites: pg.Rect) -> None:
        raise NotImplementedError

    @abstractmethod
    def desenhar(self, tela: pg.Surface) -> None:
        raise NotImplementedError


class Jogador(Entidade):
    def __init__(self, x: int, y: int):
        self.rect = pg.Rect(x, y, 42, 56)
        self.speed = 300
        self.jump_height = 0.0
        self.jump_velocity = 0.0
        self.gravity = 1800

    def pulo(self) -> None:
        if self.jump_height == 0.0:
            self.jump_velocity = 550

    def atualizar(self, teclas, dt: float, limites: pg.Rect) -> None:
        horizontal = int(teclas[pg.K_RIGHT] or teclas[pg.K_d]) - int(
            teclas[pg.K_LEFT] or teclas[pg.K_a]
        )
        vertical = int(teclas[pg.K_DOWN] or teclas[pg.K_s]) - int(
            teclas[pg.K_UP] or teclas[pg.K_w]
        )

        tamanho = math.hypot(horizontal, vertical)
        if tamanho > 0:
            horizontal /= tamanho
            vertical /= tamanho

        self.rect.x += round(horizontal * self.speed * dt)
        self.rect.y += round(vertical * self.speed * dt)
        self.rect.clamp_ip(limites)

        if self.jump_height > 0 or self.jump_velocity > 0:
            self.jump_velocity -= self.gravity * dt
            self.jump_height += self.jump_velocity * dt

            if self.jump_height <= 0:
                self.jump_height = 0
                self.jump_velocity = 0

    def desenhar(self, tela: pg.Surface) -> None:
        altura = round(self.jump_height)
        sombra = pg.Rect(
            self.rect.x + 4,
            self.rect.bottom - 8,
            self.rect.width - 8,
            12,
        )
        pg.draw.ellipse(tela, (10, 10, 15), sombra)
        corpo = self.rect.move(0, -altura)
        pg.draw.rect(tela, (190, 140, 80), corpo)


T = TypeVar("T", bound=Entidade)


class Fase:
    def __init__(self, entidades: list[Entidade]):
        self.entidades = entidades

    def obter_entidade(self, tipo: type[T]) -> T:
        for entidade in self.entidades:
            if isinstance(entidade, tipo):
                return entidade
        raise LookupError(f"Entidade {tipo.__name__} não encontrada na fase.")

    def atualizar(self, teclas, dt: float, limites: pg.Rect) -> None:
        for entidade in self.entidades:
            entidade.atualizar(teclas, dt, limites)

    def desenhar(self, tela: pg.Surface) -> None:
        for entidade in self.entidades:
            entidade.desenhar(tela)


class FabricaEntidades(ABC):
    @abstractmethod
    def criar(self) -> list[Entidade]:
        raise NotImplementedError


class FabricaEntidadesFase1(FabricaEntidades):
    def criar(self) -> list[Entidade]:
        return [Jogador(500, 500)]


class FabricaEntidadesFase2(FabricaEntidades):
    def criar(self) -> list[Entidade]:
        return [Jogador(500, 500)]


class FabricaEntidadesFase3(FabricaEntidades):
    def criar(self) -> list[Entidade]:
        return [Jogador(500, 500)]


class FabricaDeFases:
    _fabricas: dict[int, type[FabricaEntidades]] = {
        1: FabricaEntidadesFase1,
        2: FabricaEntidadesFase2,
        3: FabricaEntidadesFase3,
    }

    @classmethod
    def criar(cls, numero: int) -> Fase:
        try:
            fabrica = cls._fabricas[numero]()
        except KeyError as erro:
            raise ValueError(f"Fase inválida: {numero}") from erro
        return Fase(fabrica.criar())


def main() -> None:
    pg.init()
    tela = pg.display.set_mode((1080, 720))
    pg.display.set_caption("Chuva de Balas")
    relogio = pg.time.Clock()

    fase = FabricaDeFases.criar(1)
    jogador = fase.obter_entidade(Jogador)
    rodando = True

    while rodando:
        dt = min(relogio.tick(60) / 1000, 0.05)

        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                rodando = False
            elif evento.type == pg.KEYDOWN and evento.key == pg.K_SPACE:
                jogador.pulo()

        teclas = pg.key.get_pressed()
        fase.atualizar(teclas, dt, tela.get_rect())

        tela.fill((25, 25, 35))
        fase.desenhar(tela)
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
