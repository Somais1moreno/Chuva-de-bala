import math
import os
import pygame as pg
from constantes import (
    ALTURA_TELA,
    COR_BLOQUEIO,
    COR_BRANCO,
    COR_CEU_HORIZONTE,
    COR_CEU_MEIO,
    COR_CEU_TOPO,
    COR_CURA,
    COR_MUNICÃO,
    COR_PRETO,
    COR_TEXTO,
    COR_TEXTO_DESTAQUE,
    FONTE_RETRO_ARQUIVO,
    LARGURA_TELA,
    obter_caminho_asset,
)
from score import carregar_ranking


class Menu:
    def __init__(self):
        self.tempo = 0.0
        self.aba_atual = "menu"  # "menu" ou "scores"
        self._inicializar_fontes()

        # Botões do rodapé
        self.btn_jogar_rect = pg.Rect(LARGURA_TELA // 2 - 280, 630, 240, 50)
        self.btn_score_rect = pg.Rect(LARGURA_TELA // 2 + 40, 630, 240, 50)

    def _inicializar_fontes(self):
        caminho_fonte = obter_caminho_asset(FONTE_RETRO_ARQUIVO)
        if os.path.exists(caminho_fonte):
            try:
                self.fonte_titulo_grande = pg.font.Font(caminho_fonte, 26)
                self.fonte_titulo_medio = pg.font.Font(caminho_fonte, 18)
                self.fonte_demo = pg.font.Font(caminho_fonte, 12)
                self.fonte_secao = pg.font.Font(caminho_fonte, 13)
                self.fonte_tecla = pg.font.Font(caminho_fonte, 11)
                self.fonte_acao = pg.font.Font(caminho_fonte, 10)
                self.fonte_iniciar = pg.font.Font(caminho_fonte, 12)
                self.fonte_tabela = pg.font.Font(caminho_fonte, 12)
                return
            except Exception as erro:
                print(f"[Aviso] Falha ao carregar fonte retro: {erro}")

        # Fallback mono retro
        self.fonte_titulo_grande = pg.font.SysFont("dejavusansmono", 34, bold=True)
        self.fonte_titulo_medio = pg.font.SysFont("dejavusansmono", 24, bold=True)
        self.fonte_demo = pg.font.SysFont("dejavusansmono", 16, bold=True)
        self.fonte_secao = pg.font.SysFont("dejavusansmono", 16, bold=True)
        self.fonte_tecla = pg.font.SysFont("dejavusansmono", 14, bold=True)
        self.fonte_acao = pg.font.SysFont("dejavusansmono", 13)
        self.fonte_iniciar = pg.font.SysFont("dejavusansmono", 16, bold=True)
        self.fonte_tabela = pg.font.SysFont("dejavusansmono", 14)

    def atualizar(self, dt: float):
        self.tempo += dt

    def processar_evento(self, evento) -> str | None:
        """Processa cliques e teclas no menu. Retorna 'jogar' se o jogo deve iniciar."""
        if evento.type == pg.KEYDOWN:
            if self.aba_atual == "menu":
                if evento.key in (pg.K_SPACE, pg.K_RETURN):
                    return "jogar"
                elif evento.key in (pg.K_TAB, pg.K_h):
                    self.aba_atual = "scores"
            elif self.aba_atual == "scores":
                if evento.key in (pg.K_ESCAPE, pg.K_RETURN, pg.K_SPACE, pg.K_TAB):
                    self.aba_atual = "menu"

        elif evento.type == pg.MOUSEBUTTONDOWN and evento.button == 1:
            mouse_pos = evento.pos
            if self.aba_atual == "menu":
                if self.btn_jogar_rect.collidepoint(mouse_pos):
                    return "jogar"
                elif self.btn_score_rect.collidepoint(mouse_pos):
                    self.aba_atual = "scores"
            elif self.aba_atual == "scores":
                self.aba_atual = "menu"

        return None

    def desenhar(self, tela: pg.Surface):
        # 1. Fundo Gradiente Atmosférico
        for y in range(0, ALTURA_TELA, 2):
            fator = y / ALTURA_TELA
            if fator < 0.6:
                t = fator / 0.6
                r = int(COR_CEU_TOPO[0] + (COR_CEU_MEIO[0] - COR_CEU_TOPO[0]) * t)
                g = int(COR_CEU_TOPO[1] + (COR_CEU_MEIO[1] - COR_CEU_TOPO[1]) * t)
                b = int(COR_CEU_TOPO[2] + (COR_CEU_MEIO[2] - COR_CEU_TOPO[2]) * t)
            else:
                t = (fator - 0.6) / 0.4
                r = int(COR_CEU_MEIO[0] + (COR_CEU_HORIZONTE[0] - COR_CEU_MEIO[0]) * t)
                g = int(COR_CEU_MEIO[1] + (COR_CEU_HORIZONTE[1] - COR_CEU_MEIO[1]) * t)
                b = int(COR_CEU_MEIO[2] + (COR_CEU_HORIZONTE[2] - COR_CEU_MEIO[2]) * t)
            pg.draw.rect(tela, (r, g, b), (0, y, LARGURA_TELA, 2))

        # Silhueta de solo
        pg.draw.rect(tela, (25, 15, 20), pg.Rect(0, 630, LARGURA_TELA, 90))

        # 2. Título do Jogo
        t1_sombra = self.fonte_titulo_grande.render("CHUVA DE BALAS", True, COR_PRETO)
        t1_texto = self.fonte_titulo_grande.render("CHUVA DE BALAS", True, COR_TEXTO_DESTAQUE)
        pos_t1_x = LARGURA_TELA // 2 - t1_texto.get_width() // 2
        tela.blit(t1_sombra, (pos_t1_x + 3, 28))
        tela.blit(t1_texto, (pos_t1_x, 25))

        t2_sombra = self.fonte_titulo_medio.render("NO PAÍS DE MOSSORÓ", True, COR_PRETO)
        t2_texto = self.fonte_titulo_medio.render("NO PAÍS DE MOSSORÓ", True, (245, 175, 75))
        pos_t2_x = LARGURA_TELA // 2 - t2_texto.get_width() // 2
        tela.blit(t2_sombra, (pos_t2_x + 2, 63))
        tela.blit(t2_texto, (pos_t2_x, 60))

        if self.aba_atual == "menu":
            self._desenhar_aba_controles(tela)
        else:
            self._desenhar_aba_ranking(tela)

    def _desenhar_aba_controles(self, tela: pg.Surface):
        # Subtítulo Demo
        demo_texto = self.fonte_demo.render("[ VERSÃO DEMO ]", True, (230, 110, 60))
        pos_demo_x = LARGURA_TELA // 2 - demo_texto.get_width() // 2
        tela.blit(demo_texto, (pos_demo_x, 92))

        # Painel de Comandos
        painel_rect = pg.Rect(LARGURA_TELA // 2 - 370, 122, 740, 485)
        superficie_painel = pg.Surface((painel_rect.width, painel_rect.height), pg.SRCALPHA)
        superficie_painel.fill((15, 10, 20, 225))
        tela.blit(superficie_painel, painel_rect.topleft)
        pg.draw.rect(tela, COR_TEXTO_DESTAQUE, painel_rect, 3)

        cabecalho = self.fonte_secao.render("CONTROLES DE JOGO", True, COR_TEXTO_DESTAQUE)
        tela.blit(cabecalho, (painel_rect.centerx - cabecalho.get_width() // 2, painel_rect.y + 14))
        pg.draw.line(tela, (110, 85, 60), (painel_rect.x + 25, painel_rect.y + 36), (painel_rect.right - 25, painel_rect.y + 36), 2)

        comandos = [
            ("[ A ]", "Mover para a Esquerda", COR_TEXTO),
            ("[ D ]", "Mover para a Direita", COR_TEXTO),
            ("[ ESPAÇO ]", "Pular (Segure para salto alto)", COR_TEXTO),
            ("[ W ]", "Bloquear (Defesa: Reduz 75% do dano)", COR_BLOQUEIO),
            ("[ S ]", "Abaixar / Esconder (Atrás de caixas)", COR_TEXTO),
            ("[ Q ]", "Tomar Remédio (Cura HP - 5 por partida)", COR_CURA),
            ("[ J ]", "Facada (Golpe Melee com Peixeira)", (255, 120, 100)),
            ("[ K ]", "Tiro (Disparo de Pistola - gasta bala)", COR_MUNICÃO),
            ("[ R ]", "Reiniciar a fase", (180, 180, 200)),
            ("[ ESC ]", "Pausar ou Voltar ao Menu", (180, 180, 200)),
        ]

        pos_y = painel_rect.y + 48
        for tecla, acao, cor_destaque in comandos:
            lbl_tecla = self.fonte_tecla.render(f"{tecla:<11}", True, cor_destaque)
            lbl_acao = self.fonte_acao.render(f"➜ {acao}", True, COR_BRANCO)
            tela.blit(lbl_tecla, (painel_rect.x + 35, pos_y))
            tela.blit(lbl_acao, (painel_rect.x + 185, pos_y))
            pos_y += 42

        # Botão 1: JOGAR (ESPAÇO)
        pulso = (math.sin(self.tempo * 4.5) + 1.0) / 2.0
        cor_btn_jogar = (int(255 * (0.65 + 0.35 * pulso)), int(200 * (0.65 + 0.35 * pulso)), 50)
        pg.draw.rect(tela, (30, 20, 10), self.btn_jogar_rect)
        pg.draw.rect(tela, cor_btn_jogar, self.btn_jogar_rect, 2)
        txt_jogar = self.fonte_iniciar.render("JOGAR [ESPAÇO]", True, cor_btn_jogar)
        tela.blit(txt_jogar, (self.btn_jogar_rect.centerx - txt_jogar.get_width() // 2, self.btn_jogar_rect.centery - txt_jogar.get_height() // 2))

        # Botão 2: SCORES (TAB)
        pg.draw.rect(tela, (20, 25, 35), self.btn_score_rect)
        pg.draw.rect(tela, COR_BLOQUEIO, self.btn_score_rect, 2)
        txt_score = self.fonte_iniciar.render("SCORES [TAB]", True, COR_BLOQUEIO)
        tela.blit(txt_score, (self.btn_score_rect.centerx - txt_score.get_width() // 2, self.btn_score_rect.centery - txt_score.get_height() // 2))

    def _desenhar_aba_ranking(self, tela: pg.Surface):
        # Subtítulo Ranking
        sub = self.fonte_demo.render("★ TOP 5 RECORDES DO SERTÃO (JSON) ★", True, COR_TEXTO_DESTAQUE)
        tela.blit(sub, (LARGURA_TELA // 2 - sub.get_width() // 2, 92))

        painel_rect = pg.Rect(LARGURA_TELA // 2 - 380, 125, 760, 480)
        superficie = pg.Surface((painel_rect.width, painel_rect.height), pg.SRCALPHA)
        superficie.fill((15, 10, 20, 235))
        tela.blit(superficie, painel_rect.topleft)
        pg.draw.rect(tela, COR_MUNICÃO, painel_rect, 3)

        ranking = carregar_ranking()

        if not ranking:
            msg_vazio = self.fonte_secao.render("NENHUM RECORDE REGISTRADO AINDA!", True, (240, 180, 120))
            msg_dica = self.fonte_acao.render("Complete a fase para imortalizar seu nome no ranking!", True, COR_BRANCO)
            tela.blit(msg_vazio, (painel_rect.centerx - msg_vazio.get_width() // 2, painel_rect.centery - 30))
            tela.blit(msg_dica, (painel_rect.centerx - msg_dica.get_width() // 2, painel_rect.centery + 10))
        else:
            # Cabeçalho da Tabela
            cabecalho = self.fonte_tabela.render(f"{'POS':<6}  {'JOGADOR':<14}  {'PONTOS':<12}  {'DATA':<10}", True, COR_TEXTO_DESTAQUE)
            tela.blit(cabecalho, (painel_rect.x + 50, painel_rect.y + 35))
            pg.draw.line(tela, (130, 95, 50), (painel_rect.x + 40, painel_rect.y + 60), (painel_rect.right - 40, painel_rect.y + 60), 2)

            cores_pos = [
                (255, 215, 0),    # 1º Ouro
                (200, 200, 220),  # 2º Prata
                (205, 127, 50),   # 3º Bronze
                COR_BRANCO,       # 4º
                COR_BRANCO,       # 5º
            ]

            pos_y = painel_rect.y + 85
            for idx, reg in enumerate(ranking):
                cor = cores_pos[idx] if idx < len(cores_pos) else COR_BRANCO
                pos_str = f"{idx + 1}º"
                nome_str = str(reg.get("nome", "ANONIMO"))[:10]
                pts_str = f"{reg.get('score', 0):,} PTS".replace(",", ".")
                data_str = str(reg.get("data", ""))

                linha = self.fonte_tabela.render(f"{pos_str:<6}  {nome_str:<14}  {pts_str:<12}  {data_str:<10}", True, cor)
                tela.blit(linha, (painel_rect.x + 50, pos_y))
                pos_y += 55

        # Botão de Voltar
        btn_voltar = pg.Rect(LARGURA_TELA // 2 - 180, 630, 360, 50)
        pg.draw.rect(tela, (30, 20, 25), btn_voltar)
        pg.draw.rect(tela, COR_TEXTO_DESTAQUE, btn_voltar, 2)
        txt_v = self.fonte_iniciar.render("VOLTAR AO MENU [ESC]", True, COR_TEXTO_DESTAQUE)
        tela.blit(txt_v, (btn_voltar.centerx - txt_v.get_width() // 2, btn_voltar.centery - txt_v.get_height() // 2))
