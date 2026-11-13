from abc import ABC, abstractmethod

from .modelo_fase import Entidade, Fase, Jogador


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
