import os
import sys

# Garante que o diretório do script esteja no sys.path mesmo se executado de fora
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from code.jogo import Jogo


def main():
    jogo = Jogo()
    jogo.executar()


if __name__ == "__main__":
    main()
