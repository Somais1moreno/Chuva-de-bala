import json
import os
from datetime import datetime
from .constantes import (
    ARQUIVO_RANKING_NOME,
    BONUS_PERFECT_FLAWLESS,
    DIR_BASE,
    MAX_SAVES_RANKING,
    PENALIDADE_DANO_SOFRIDO,
    PONTOS_DERROTAR_INIMIGO,
    PONTOS_GOLPE_INIMIGO,
    PONTOS_PEGAR_MUNICAO,
    PONTOS_QUEBRAR_CAIXA,
)

CAMINHO_RANKING_JSON = os.path.join(DIR_BASE, ARQUIVO_RANKING_NOME)


class GerenciadorScore:
    """Controla os pontos, bônus e penalidades da partida atual."""

    def __init__(self):
        self.score = 0
        self.tomou_dano = False
        self.inimigos_derrotados = 0
        self.caixas_quebradas = 0
        self.flawless = False

    def registrar_golpe_inimigo(self):
        self.score += PONTOS_GOLPE_INIMIGO

    def registrar_inimigo_derrotado(self):
        self.inimigos_derrotados += 1
        self.score += PONTOS_DERROTAR_INIMIGO

    def registrar_caixa_quebrada(self):
        self.caixas_quebradas += 1
        self.score += PONTOS_QUEBRAR_CAIXA

    def registrar_municao_coletada(self):
        self.score += PONTOS_PEGAR_MUNICAO

    def registrar_dano_sofrido(self):
        self.tomou_dano = True
        self.score = max(0, self.score - PENALIDADE_DANO_SOFRIDO)

    def calcular_vitoria(self) -> tuple[int, bool]:
        """Aplica o bônus PERFECT FLAWLESS caso o jogador termine sem tomar dano algum."""
        if not self.tomou_dano:
            self.score += BONUS_PERFECT_FLAWLESS
            self.flawless = True
        else:
            self.flawless = False
        return self.score, self.flawless


def carregar_ranking() -> list[dict]:
    """Carrega os top 5 recordes salvos no arquivo JSON."""
    if not os.path.exists(CAMINHO_RANKING_JSON):
        return []
    try:
        with open(CAMINHO_RANKING_JSON, "r", encoding="utf-8") as f:
            dados = json.load(f)
            if isinstance(dados, list):
                dados.sort(key=lambda item: item.get("score", 0), reverse=True)
                return dados[:MAX_SAVES_RANKING]
    except Exception as erro:
        print(f"[Aviso] Falha ao carregar {ARQUIVO_RANKING_NOME}: {erro}")
    return []


def qualifica_para_ranking(pontuacao: int) -> bool:
    """Retorna True se a pontuação obtida puder entrar no Top 5."""
    if pontuacao <= 0:
        return False
    ranking = carregar_ranking()
    if len(ranking) < MAX_SAVES_RANKING:
        return True
    return pontuacao > ranking[-1].get("score", 0)


def salvar_score(nome: str, pontuacao: int) -> list[dict]:
    """
    Salva o novo score no ranking JSON.
    Mantém estritamente no máximo 5 registros, substituindo a menor pontuação.
    """
    ranking = carregar_ranking()
    nome_sanitizado = (nome.strip() or "CANGACEIRO")[:10].upper()

    novo_registro = {
        "nome": nome_sanitizado,
        "score": int(pontuacao),
        "data": datetime.now().strftime("%d/%m/%Y"),
    }

    ranking.append(novo_registro)
    # Ordenação decrescente pelo score
    ranking.sort(key=lambda item: item.get("score", 0), reverse=True)
    # Garante limite máximo de 5 registros
    ranking = ranking[:MAX_SAVES_RANKING]

    try:
        with open(CAMINHO_RANKING_JSON, "w", encoding="utf-8") as f:
            json.dump(ranking, f, indent=2, ensure_ascii=False)
    except Exception as erro:
        print(f"[Erro] Falha ao salvar em {ARQUIVO_RANKING_NOME}: {erro}")

    return ranking
