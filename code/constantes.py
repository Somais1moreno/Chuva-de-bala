"""
================================================================================
ARQUIVO DE CONSTANTES E BALANCEAMENTO DO JOGO
Chuva de Balas - No País de Mossoró
================================================================================
Edite este arquivo para alterar facilmente vidas, danos, velocidades,
dimensões, cores e qualquer parâmetro de jogabilidade sem mexer na lógica do código.
"""

import os
import sys

# ==============================================================================
# 1. TELA E VÍDEO
# ==============================================================================
LARGURA_TELA = 1280
ALTURA_TELA = 720
FPS = 60
TITULO_JOGO = "Chuva de Balas no País de Mossoró"
FONTE_RETRO_ARQUIVO = "PressStart2P.ttf"


# ==============================================================================
# 2. DIRETÓRIOS E ASSETS (Compatível com PyInstaller e Sistemas Diferentes)
# ==============================================================================
if getattr(sys, "frozen", False):
    DIR_BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
else:
    DIR_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DIR_ASSETS = os.path.join(DIR_BASE, "Assets")


def obter_caminho_asset(nome_arquivo: str) -> str:
    """Retorna o caminho absoluto do asset de forma compatível e segura."""
    return os.path.join(DIR_ASSETS, nome_arquivo)


# ==============================================================================
# 3. PALETA DE CORES (RGB)
# ==============================================================================
# Cores Básicas
COR_PRETO = (10, 10, 15)
COR_BRANCO = (245, 245, 245)

# Céu e Atmosfera de Entardecer Sertanejo
COR_CEU_TOPO = (45, 25, 60)         # Roxo crepúsculo
COR_CEU_MEIO = (180, 80, 50)        # Laranja entardecer
COR_CEU_HORIZONTE = (235, 160, 60)  # Dourado horizonte

# Serras do Sertão (Parallax)
COR_SERRA_LONGE = (90, 50, 70)      # Silhueta de serra ao longe
COR_SERRA_PERTO = (70, 40, 50)      # Silhueta média

# Terreno, Rochas e Caatinga
COR_CHAO_SUPERIOR = (185, 115, 65)  # Terra seca batida no topo
COR_CHAO_ROCHA = (110, 70, 45)      # Rocha e subsolo
COR_CHAO_DETALHE = (140, 90, 55)    # Linhas de detalhe

# Interface (HUD) e Textos
COR_VIDA = (220, 45, 45)            # Vermelho da barra de vida
COR_VIDA_FUNDO = (60, 20, 20)       # Fundo da barra de vida
COR_MUNICÃO = (240, 190, 50)        # Dourado de balas e caixas de munição
COR_CURA = (60, 225, 110)           # Verde brilhante para remédios e cura
COR_BLOQUEIO = (100, 180, 255)      # Azul luminoso de bloqueio/defesa
COR_TEXTO = (250, 240, 220)         # Bege claro de leitura
COR_TEXTO_DESTAQUE = (255, 205, 70) # Dourado de títulos e destaques


# ==============================================================================
# 4. FÍSICA GERAL (Estilo Hollow Knight)
# ==============================================================================
GRAVIDADE = 1950.0
VELOCIDADE_TERMINAL = 1200.0        # Velocidade máxima de queda

# Movimentação Horizontal do Jogador
VELOCIDADE_MAX = 330.0
ACELERACAO = 2400.0
ATRITO = 2200.0

# Sistema de Pulo (Aumentado em ~15% para saltar plataformas altas e abismos)
FORCA_PULO = -770.0
CORTE_PULO_FATOR = 0.45             # Pulo variável: corta subida ao soltar o botão
TEMPO_COYOTE = 0.12                 # Segundos para pular após sair do chão
TEMPO_JUMP_BUFFER = 0.14            # Segundos que registra o pulo antes de aterrissar


# ==============================================================================
# 5. JOGADOR: VIDA, COMBATE E AÇÕES
# ==============================================================================
# Vida e Resistência
VIDA_MAX_JOGADOR = 100
TEMPO_INVENCIVEL_JOGADOR = 0.8      # Tempo piscando invulnerável após receber dano
DANO_QUEDA_ABISMO = 20              # Dano sofrido ao cair no buraco

# Sistema de Remédios (Cura do Jogador - Q)
REMEDIOS_INICIAIS = 5               # Quantidade inicial por rodada (não há no mapa)
CURA_REMEDIO = 35                   # Quantidade de HP restaurada por frasco

# Sistema de Bloqueio (Defesa - W)
FATOR_REDUCAO_BLOQUEIO = 0.75       # 75% de redução no dano recebido enquanto bloqueia

# Combate Melee: Peixeira (Faca)
DANO_PEIXEIRA = 35
COOLDOWN_PEIXEIRA = 0.32            # Tempo de espera entre cada golpe (segundos)
ALCANCE_PEIXEIRA_X = 64             # Alcance horizontal do golpe
ALCANCE_PEIXEIRA_Y = 50             # Altura do corte

# Combate à Distância: Pistola
MUNICÃO_INICIAL = 6
DANO_BALA = 50
VELOCIDADE_BALA = 850.0
ALCANCE_MAX_BALA = 900.0            # Distância máxima que o tiro percorre
COOLDOWN_TIRO = 0.40                # Intervalo mínimo entre tiros (segundos)


# ==============================================================================
# 6. INIMIGOS COMUNS (Balanceamento)
# ==============================================================================
# Inimigo 1: Cangaceiro de Ataque Curto (Peixeira / Melee)
INIMIGO_MELEE_VIDA = 60
INIMIGO_MELEE_VELOCIDADE = 140.0          # Velocidade calibrada de investida
INIMIGO_MELEE_VELOCIDADE_RECUO = 190.0    # Salto rápido para trás após golpear
INIMIGO_MELEE_TEMPO_RESPIRO = 0.90        # Janela de respiro para contra-ataque do jogador
INIMIGO_MELEE_DANO_CONTATO = 15
INIMIGO_MELEE_DISTANCIA_VISAO = 400

# Inimigo 2: Cangaceiro Atirador (Pistola / Ranged)
INIMIGO_RANGED_VIDA = 45
INIMIGO_RANGED_VELOCIDADE = 115.0         # Patrulha mais ágil vasculhando a plataforma
INIMIGO_RANGED_DANO_TIRO = 20
INIMIGO_RANGED_COOLDOWN_TIRO = 1.9
INIMIGO_RANGED_DISTANCIA_TIRO = 520       # Campo de visão expandido para tiros diagonais


# ==============================================================================
# 7. CHEFE FINAL: LAMPIÃO (O Rei do Cangaço)
# ==============================================================================
BOSS_LAMPIAO_VIDA_MAX = 300
BOSS_LAMPIAO_VELOCIDADE = 140.0
BOSS_LAMPIAO_DANO_ESPINGARDA = 30   # Dano do tiro pesado
BOSS_LAMPIAO_DANO_CONTATO = 25
BOSS_LAMPIAO_COOLDOWN_TIRO = 2.2
BOSS_LAMPIAO_COOLDOWN_ESQUIVA = 3.5 # Lampião esquiva para trás após levar dano


# ==============================================================================
# 8. ELEMENTOS DE CENÁRIO E OBSTÁCULOS
# ==============================================================================
VIDA_CAIXA = 3                      # Quantos golpes/tiros quebram a caixa
TAMANHO_CAIXA = 68                  # Largura e altura da caixa em pixels
MUNICAO_POR_COLETAVEL = 4           # Quantas balas o jogador ganha ao pegar um pickup
LARGURA_NIVEL_PADRAO = 7200         # Comprimento total da fase (dobrado para mais desafios)
ALTURA_NIVEL_PADRAO = 720
X_ARENA_BOSS = 6200                 # Coordenada X onde começa a arena do Boss Lampião
X_VITORIA = 7100                    # Coordenada X final do nível


# ==============================================================================
# 9. SISTEMA DE SCORE E RECORDES (Ranking Top 5 JSON)
# ==============================================================================
PONTOS_GOLPE_INIMIGO = 25           # Pontos ao acertar um golpe de faca ou tiro
PONTOS_DERROTAR_INIMIGO = 150       # Pontos ao abater um inimigo comum
PONTOS_QUEBRAR_CAIXA = 40           # Pontos ao quebrar uma caixa de cobertura
PONTOS_PEGAR_MUNICAO = 30           # Pontos ao coletar caixa de munições
PENALIDADE_DANO_SOFRIDO = 50        # Pontos perdidos ao levar dano (mínimo 0)
BONUS_PERFECT_FLAWLESS = 2000       # Bônus épico se vencer a fase sem levar dano algum!
MAX_SAVES_RANKING = 5               # Limite máximo de 5 recordes salvos no JSON
ARQUIVO_RANKING_NOME = "ranking.json"
