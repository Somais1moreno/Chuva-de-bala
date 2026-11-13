import os
import sys
import pygame as pg
from .camera import Camera
from .cenario import Nivel
from .constantes import (
    ALTURA_TELA,
    BONUS_PERFECT_FLAWLESS,
    COR_BLOQUEIO,
    COR_BRANCO,
    COR_CEU_HORIZONTE,
    COR_CEU_MEIO,
    COR_CEU_TOPO,
    COR_CURA,
    COR_MUNICÃO,
    COR_PRETO,
    COR_SERRA_LONGE,
    COR_SERRA_PERTO,
    COR_TEXTO,
    COR_TEXTO_DESTAQUE,
    COR_VIDA,
    COR_VIDA_FUNDO,
    FONTE_RETRO_ARQUIVO,
    FPS,
    LARGURA_TELA,
    TITULO_JOGO,
    VIDA_MAX_JOGADOR,
    X_ARENA_BOSS,
    obter_caminho_asset,
)
from .jogador import Jogador
from .menu import Menu
from .score import GerenciadorScore, qualifica_para_ranking, salvar_score


class EstadoJogo:
    MENU = "menu"
    JOGANDO = "jogando"
    DERROTA = "derrota"
    VITORIA = "vitoria"
    NOME_INPUT = "nome_input"  # Tela de entrada do nome para o ranking


class Jogo:
    def __init__(self):
        pg.init()
        pg.font.init()
        self.tela = pg.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pg.display.set_caption(TITULO_JOGO)
        self.relogio = pg.time.Clock()
        self.rodando = True

        self.estado = EstadoJogo.MENU
        self.menu = Menu()

        self._inicializar_fontes()
        self._gerar_superficie_ceu()
        self.reiniciar_jogo()

        # Estado da tela de nome (input pós-vitória)
        self._nome_digitado = ""
        self._score_final = 0
        self._flawless_final = False
        self._cursor_piscada = 0.0

    def _inicializar_fontes(self):
        caminho_fonte = obter_caminho_asset(FONTE_RETRO_ARQUIVO)
        if os.path.exists(caminho_fonte):
            try:
                self.fonte_hud = pg.font.Font(caminho_fonte, 11)
                self.fonte_hud_destaque = pg.font.Font(caminho_fonte, 12)
                self.fonte_hud_mini = pg.font.Font(caminho_fonte, 9)
                self.fonte_aviso = pg.font.Font(caminho_fonte, 20)
                self.fonte_input = pg.font.Font(caminho_fonte, 16)
                self.fonte_input_grande = pg.font.Font(caminho_fonte, 22)
                return
            except Exception as erro:
                print(f"[Aviso] Falha ao carregar fonte retro no HUD: {erro}")

        # Fallback mono retro
        self.fonte_hud = pg.font.SysFont("dejavusansmono", 14, bold=True)
        self.fonte_hud_destaque = pg.font.SysFont("dejavusansmono", 16, bold=True)
        self.fonte_hud_mini = pg.font.SysFont("dejavusansmono", 12)
        self.fonte_aviso = pg.font.SysFont("dejavusansmono", 28, bold=True)
        self.fonte_input = pg.font.SysFont("dejavusansmono", 20, bold=True)
        self.fonte_input_grande = pg.font.SysFont("dejavusansmono", 28, bold=True)

    def _gerar_superficie_ceu(self):
        """Cria e armazena em cache o gradiente do céu de entardecer."""
        self.surf_ceu = pg.Surface((LARGURA_TELA, ALTURA_TELA))
        for y in range(0, ALTURA_TELA, 2):
            fator = y / ALTURA_TELA
            if fator < 0.65:
                t = fator / 0.65
                r = int(COR_CEU_TOPO[0] + (COR_CEU_MEIO[0] - COR_CEU_TOPO[0]) * t)
                g = int(COR_CEU_TOPO[1] + (COR_CEU_MEIO[1] - COR_CEU_TOPO[1]) * t)
                b = int(COR_CEU_TOPO[2] + (COR_CEU_MEIO[2] - COR_CEU_TOPO[2]) * t)
            else:
                t = (fator - 0.65) / 0.35
                r = int(COR_CEU_MEIO[0] + (COR_CEU_HORIZONTE[0] - COR_CEU_MEIO[0]) * t)
                g = int(COR_CEU_MEIO[1] + (COR_CEU_HORIZONTE[1] - COR_CEU_MEIO[1]) * t)
                b = int(COR_CEU_MEIO[2] + (COR_CEU_HORIZONTE[2] - COR_CEU_MEIO[2]) * t)
            pg.draw.rect(self.surf_ceu, (r, g, b), (0, y, LARGURA_TELA, 2))

    def reiniciar_jogo(self):
        """Inicializa ou reseta o nível, jogador, projéteis e score."""
        self.nivel = Nivel()
        self.camera = Camera(self.nivel.largura, self.nivel.altura)
        px, py = self.nivel.ponto_inicio_jogador
        self.jogador = Jogador(px, py)
        self.projeteis = []
        self.score_mgr = GerenciadorScore()

        # Rastreia inimigos que já foram contados como derrotados (para não duplicar pontos)
        self._inimigos_ja_derrotados: set = set()
        # Rastreia coletáveis já coletados (para não duplicar pontos)
        self._coletaveis_ja_coletados: set = set()

    def executar(self):
        while self.rodando:
            dt = min(self.relogio.tick(FPS) / 1000.0, 0.05)

            self._processar_eventos()
            self._atualizar(dt)
            self._desenhar()

        pg.quit()
        sys.exit()

    def _processar_eventos(self):
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                self.rodando = False

            elif evento.type == pg.KEYDOWN:
                if self.estado == EstadoJogo.MENU:
                    resultado = self.menu.processar_evento(evento)
                    if resultado == "jogar":
                        self.estado = EstadoJogo.JOGANDO

                elif self.estado == EstadoJogo.JOGANDO:
                    # Comandos estritos: Espaço (Pulo), J (Faca), K (Tiro), Q (Remédio)
                    if evento.key == pg.K_SPACE:
                        self.jogador.tentar_pular()
                    elif evento.key == pg.K_j:
                        self.jogador.atacar_peixeira(self.nivel.caixas, self.nivel.inimigos)
                    elif evento.key == pg.K_k:
                        self.jogador.atirar(self.projeteis)
                    elif evento.key == pg.K_q:
                        self.jogador.tomar_remedio()
                    elif evento.key == pg.K_r:
                        self.reiniciar_jogo()
                    elif evento.key == pg.K_ESCAPE:
                        self.estado = EstadoJogo.MENU

                elif self.estado == EstadoJogo.NOME_INPUT:
                    self._processar_input_nome(evento)

                elif self.estado in (EstadoJogo.DERROTA, EstadoJogo.VITORIA):
                    if evento.key == pg.K_r:
                        self.reiniciar_jogo()
                        self.estado = EstadoJogo.JOGANDO
                    elif evento.key == pg.K_ESCAPE:
                        self.reiniciar_jogo()
                        self.estado = EstadoJogo.MENU

            elif evento.type == pg.KEYUP:
                if self.estado == EstadoJogo.JOGANDO:
                    if evento.key == pg.K_SPACE:
                        self.jogador.soltar_pulo()

            elif evento.type == pg.MOUSEBUTTONDOWN:
                if self.estado == EstadoJogo.MENU:
                    resultado = self.menu.processar_evento(evento)
                    if resultado == "jogar":
                        self.estado = EstadoJogo.JOGANDO

    def _processar_input_nome(self, evento):
        """Gerencia a digitação do nome no ranking pós-vitória."""
        if evento.key == pg.K_RETURN:
            # Confirmar e salvar no ranking
            nome = self._nome_digitado.strip() or "CANGACEIRO"
            salvar_score(nome, self._score_final)
            self.estado = EstadoJogo.VITORIA

        elif evento.key == pg.K_ESCAPE:
            # Cancelar sem salvar
            self.estado = EstadoJogo.VITORIA

        elif evento.key == pg.K_BACKSPACE:
            self._nome_digitado = self._nome_digitado[:-1]

        else:
            # Aceitar apenas letras, números e espaço; máximo 10 caracteres
            char = evento.unicode
            if char and (char.isalnum() or char == " ") and len(self._nome_digitado) < 10:
                self._nome_digitado += char.upper()

    def _atualizar(self, dt: float):
        if self.estado == EstadoJogo.MENU:
            self.menu.atualizar(dt)

        elif self.estado == EstadoJogo.NOME_INPUT:
            # Animar cursor piscante
            self._cursor_piscada += dt

        elif self.estado == EstadoJogo.JOGANDO:
            self.nivel.atualizar_caixas(dt)
            teclas = pg.key.get_pressed()
            obstaculos = self.nivel.obter_obstaculos_solidos()

            # --- Vida anterior para detectar dano ---
            vida_antes = self.jogador.vida

            # Atualizar Jogador (com verificação estrita de teclas)
            self.jogador.atualizar(
                dt,
                teclas,
                obstaculos,
                self.nivel.caixas,
                self.nivel.coletaveis,
                self.nivel.limite_queda_morte,
            )

            # --- Score: dano sofrido pelo jogador ---
            if self.jogador.vida < vida_antes:
                self.score_mgr.registrar_dano_sofrido()

            # Atualizar Itens Coletáveis e registrar municao coletada
            for item in self.nivel.coletaveis:
                ja_coletado_antes = item.coletado
                item.atualizar(dt)
                # Detecta coleta nova neste frame
                if item.coletado and id(item) not in self._coletaveis_ja_coletados:
                    self._coletaveis_ja_coletados.add(id(item))
                    self.score_mgr.registrar_municao_coletada()

            # Atualizar Inimigos e detectar derrotas
            for inimigo in self.nivel.inimigos:
                inimigo.atualizar(dt, self.jogador, obstaculos, self.projeteis)
                # Detecta inimigo recém-derrotado (vivo=False desta vez)
                if not inimigo.vivo and id(inimigo) not in self._inimigos_ja_derrotados:
                    self._inimigos_ja_derrotados.add(id(inimigo))
                    self.score_mgr.registrar_inimigo_derrotado()

            # Atualizar Projéteis
            for p in self.projeteis:
                p.atualizar(
                    dt,
                    obstaculos,
                    self.nivel.caixas,
                    jogador=self.jogador,
                    inimigos=self.nivel.inimigos,
                )
            self.projeteis = [p for p in self.projeteis if p.ativo]

            # --- Score: caixas destruídas pelos projéteis ou pela faca ---
            for caixa in self.nivel.caixas:
                if caixa.destruida and id(caixa) not in self._inimigos_ja_derrotados:
                    # Reutilizamos o set de IDs para rastrear caixas também
                    self._inimigos_ja_derrotados.add(id(caixa))
                    self.score_mgr.registrar_caixa_quebrada()
                    self.nivel.gerar_estilhacos(caixa.rect.centerx, caixa.rect.centery)

            # Atualizar partículas de madeira (estilhaços)
            self.nivel.atualizar_particulas(dt)

            # Atualizar Câmera
            self.camera.atualizar(self.jogador.rect, dt)

            # --- Checar Condição de Derrota ---
            if self.jogador.vida <= 0:
                self.estado = EstadoJogo.DERROTA

            # --- Checar Chegada na Arena do Boss → Vitória ---
            elif self.jogador.rect.x >= X_ARENA_BOSS:
                self._iniciar_vitoria()

    def _iniciar_vitoria(self):
        """Calcula pontuação final e decide se vai para input de nome ou tela de vitória."""
        score_final, flawless = self.score_mgr.calcular_vitoria()
        self._score_final = score_final
        self._flawless_final = flawless

        if qualifica_para_ranking(score_final):
            self._nome_digitado = ""
            self._cursor_piscada = 0.0
            self.estado = EstadoJogo.NOME_INPUT
        else:
            self.estado = EstadoJogo.VITORIA

    def _desenhar(self):
        if self.estado == EstadoJogo.MENU:
            self.menu.desenhar(self.tela)

        elif self.estado == EstadoJogo.NOME_INPUT:
            self._desenhar_mundo()
            self._desenhar_hud()
            self._desenhar_tela_nome_input()

        else:
            self._desenhar_mundo()
            self._desenhar_hud()

            if self.estado == EstadoJogo.DERROTA:
                self._desenhar_tela_fim(
                    "VOCE FOI DERRUBADO!",
                    "[R] Reiniciar Fase  |  [ESC] Menu",
                    COR_VIDA,
                    score=self.score_mgr.score,
                    flawless=False,
                )
            elif self.estado == EstadoJogo.VITORIA:
                self._desenhar_tela_fim(
                    "ARENA DO LAMPIAO ALCANCADA!",
                    "[R] Jogar Novamente  |  [ESC] Menu",
                    COR_TEXTO_DESTAQUE,
                    score=self._score_final,
                    flawless=self._flawless_final,
                )

        pg.display.flip()

    def _desenhar_mundo(self):
        # 1. Céu base
        self.tela.blit(self.surf_ceu, (0, 0))

        # 2. Sol poente sertanejo
        sol_x = round(900 - self.camera.offset_x * 0.05)
        sol_y = 380
        pg.draw.circle(self.tela, (255, 230, 140), (sol_x, sol_y), 50)
        pg.draw.circle(self.tela, (255, 200, 100), (sol_x, sol_y), 58, 4)

        # 3. Silhuetas de serras ao fundo (Parallax)
        offset_serra1 = (self.camera.offset_x * 0.12) % 600
        pontos_serra_longe = []
        for i in range(-1, 4):
            base_x = i * 600 - offset_serra1
            pontos_serra_longe.extend([
                (base_x, 500),
                (base_x + 180, 410),
                (base_x + 350, 480),
                (base_x + 500, 390),
                (base_x + 600, 500),
            ])
        pontos_serra_longe.append((LARGURA_TELA + 200, ALTURA_TELA))
        pontos_serra_longe.append((-200, ALTURA_TELA))
        pg.draw.polygon(self.tela, COR_SERRA_LONGE, pontos_serra_longe)

        offset_serra2 = (self.camera.offset_x * 0.25) % 500
        pontos_serra_perto = []
        for i in range(-1, 5):
            base_x = i * 500 - offset_serra2
            pontos_serra_perto.extend([
                (base_x, 560),
                (base_x + 150, 470),
                (base_x + 320, 530),
                (base_x + 500, 560),
            ])
        pontos_serra_perto.append((LARGURA_TELA + 200, ALTURA_TELA))
        pontos_serra_perto.append((-200, ALTURA_TELA))
        pg.draw.polygon(self.tela, COR_SERRA_PERTO, pontos_serra_perto)

        # 4. Elementos do Nível
        for plataforma in self.nivel.plataformas:
            plataforma.desenhar(self.tela, self.camera)

        for caixa in self.nivel.caixas:
            caixa.desenhar(self.tela, self.camera)

        for item in self.nivel.coletaveis:
            item.desenhar(self.tela, self.camera)

        # 5. Partículas de madeira (estilhaços de caixas)
        self.nivel.desenhar_particulas(self.tela, self.camera)

        # 6. Inimigos
        for inimigo in self.nivel.inimigos:
            inimigo.desenhar(self.tela, self.camera)

        # 7. Projéteis
        for proj in self.projeteis:
            proj.desenhar(self.tela, self.camera)

        # 8. Jogador
        self.jogador.desenhar(self.tela, self.camera)

    def _desenhar_hud(self):
        # 1. Barra de Vida
        fundo_vida = pg.Rect(20, 20, 230, 26)
        pg.draw.rect(self.tela, (25, 15, 20), fundo_vida)
        pg.draw.rect(self.tela, COR_VIDA_FUNDO, fundo_vida.inflate(-4, -4))

        largura_vida = int((self.jogador.vida / VIDA_MAX_JOGADOR) * 222)
        if largura_vida > 0:
            pg.draw.rect(self.tela, COR_VIDA, (24, 24, largura_vida, 18))
        pg.draw.rect(self.tela, COR_BRANCO, fundo_vida, 2)

        txt_vida = self.fonte_hud_mini.render(f"VIDA {self.jogador.vida}%", True, COR_BRANCO)
        self.tela.blit(txt_vida, (30, 28))

        # 2. Contador de Balas (K)
        fundo_mun = pg.Rect(20, 54, 155, 30)
        pg.draw.rect(self.tela, (25, 20, 15), fundo_mun)
        pg.draw.rect(self.tela, COR_MUNICÃO, fundo_mun, 2)
        txt_mun = self.fonte_hud.render(f"BALAS: {self.jogador.municao}", True, COR_MUNICÃO)
        self.tela.blit(txt_mun, (28, 62))

        # 3. Contador de Remédios (Q) - Nova Funcionalidade
        fundo_rem = pg.Rect(185, 54, 185, 30)
        pg.draw.rect(self.tela, (15, 30, 20), fundo_rem)
        pg.draw.rect(self.tela, COR_CURA, fundo_rem, 2)
        txt_rem = self.fonte_hud.render(f"REMEDIO: {self.jogador.remedios}/5", True, COR_CURA)
        self.tela.blit(txt_rem, (193, 62))

        # 4. Indicador de Bloqueio Ativo (W)
        if self.jogador.bloqueando:
            fundo_bloq = pg.Rect(380, 54, 130, 30)
            pg.draw.rect(self.tela, (15, 25, 45), fundo_bloq)
            pg.draw.rect(self.tela, COR_BLOQUEIO, fundo_bloq, 2)
            txt_bloq = self.fonte_hud.render("DEFESA", True, COR_BLOQUEIO)
            self.tela.blit(txt_bloq, (405, 62))

        # 5. Score — canto superior direito
        txt_score = self.fonte_hud_destaque.render(
            f"SCORE: {self.score_mgr.score:,}".replace(",", "."),
            True,
            COR_TEXTO_DESTAQUE,
        )
        score_x = LARGURA_TELA - txt_score.get_width() - 20
        score_y = 50
        fundo_score = pg.Rect(score_x - 8, score_y - 4, txt_score.get_width() + 16, txt_score.get_height() + 8)
        pg.draw.rect(self.tela, (15, 10, 20), fundo_score)
        pg.draw.rect(self.tela, COR_TEXTO_DESTAQUE, fundo_score, 2)
        self.tela.blit(txt_score, (score_x, score_y))

        # 6. Progresso da Fase
        progresso = min(1.0, max(0.0, self.jogador.rect.x / float(X_ARENA_BOSS)))
        prog_rect = pg.Rect(LARGURA_TELA - 260, 20, 230, 20)
        pg.draw.rect(self.tela, (25, 15, 20), prog_rect)
        pg.draw.rect(self.tela, COR_TEXTO_DESTAQUE, (prog_rect.x + 2, prog_rect.y + 2, int(226 * progresso), 16))
        pg.draw.rect(self.tela, COR_BRANCO, prog_rect, 2)

        txt_prog = self.fonte_hud_mini.render(f"ARENA: {int(progresso * 100)}%", True, COR_BRANCO)
        self.tela.blit(txt_prog, (prog_rect.x + 10, prog_rect.bottom + 5))

        # 7. Rodapé com Lembrete de Controles (Restrito a WASD + Q + J + K)
        lembrete = self.fonte_hud_mini.render(
            "[A/D]Mover [Espaco]Pulo [W]Bloqueio [S]Abaixar [Q]Remedio [J]Faca [K]Tiro",
            True,
            (225, 215, 195),
        )
        self.tela.blit(lembrete, (LARGURA_TELA - lembrete.get_width() - 20, ALTURA_TELA - 24))

    def _desenhar_tela_nome_input(self):
        """Tela de entrada do nome para o ranking. Aparece sobre o jogo pausado."""
        overlay = pg.Surface((LARGURA_TELA, ALTURA_TELA), pg.SRCALPHA)
        overlay.fill((5, 2, 15, 220))
        self.tela.blit(overlay, (0, 0))

        cy = ALTURA_TELA // 2

        # Título
        t_titulo = self.fonte_input_grande.render("VOCE ENTROU NO RANKING!", True, COR_TEXTO_DESTAQUE)
        self.tela.blit(t_titulo, (LARGURA_TELA // 2 - t_titulo.get_width() // 2, cy - 160))

        # Pontuação conquisdada
        t_pts = self.fonte_input.render(
            f"PONTUACAO: {self._score_final:,}".replace(",", ".") + " PTS",
            True,
            COR_BRANCO,
        )
        self.tela.blit(t_pts, (LARGURA_TELA // 2 - t_pts.get_width() // 2, cy - 110))

        # Flawless
        if self._flawless_final:
            t_fl = self.fonte_input.render(
                f"★ PERFECT FLAWLESS! +{BONUS_PERFECT_FLAWLESS} PTS ★",
                True,
                (255, 215, 0),
            )
            self.tela.blit(t_fl, (LARGURA_TELA // 2 - t_fl.get_width() // 2, cy - 70))

        # Instrução
        t_ins = self.fonte_hud.render("DIGITE SEU NOME (max 10 chars):", True, (200, 190, 170))
        self.tela.blit(t_ins, (LARGURA_TELA // 2 - t_ins.get_width() // 2, cy - 20))

        # Campo de texto com cursor piscante
        cursor_visivel = int(self._cursor_piscada * 2) % 2 == 0
        texto_exibido = self._nome_digitado + ("|" if cursor_visivel else " ")
        campo = pg.Rect(LARGURA_TELA // 2 - 220, cy + 10, 440, 50)
        pg.draw.rect(self.tela, (30, 20, 40), campo)
        pg.draw.rect(self.tela, COR_TEXTO_DESTAQUE, campo, 3)

        t_nome = self.fonte_input_grande.render(texto_exibido, True, COR_BRANCO)
        self.tela.blit(t_nome, (campo.centerx - t_nome.get_width() // 2, campo.centery - t_nome.get_height() // 2))

        # Rodapé de instrução
        t_rod = self.fonte_hud_mini.render("[ENTER] Confirmar   |   [ESC] Pular", True, (160, 150, 140))
        self.tela.blit(t_rod, (LARGURA_TELA // 2 - t_rod.get_width() // 2, cy + 85))

    def _desenhar_tela_fim(self, titulo: str, subtitulo: str, cor_destaque: tuple,
                           score: int = 0, flawless: bool = False):
        overlay = pg.Surface((LARGURA_TELA, ALTURA_TELA), pg.SRCALPHA)
        overlay.fill((10, 5, 12, 210))
        self.tela.blit(overlay, (0, 0))

        cy = ALTURA_TELA // 2

        txt_t = self.fonte_aviso.render(titulo, True, cor_destaque)
        self.tela.blit(txt_t, (LARGURA_TELA // 2 - txt_t.get_width() // 2, cy - 110))

        # Score final na tela de fim
        txt_score = self.fonte_hud_destaque.render(
            f"PONTUACAO FINAL: {score:,} PTS".replace(",", "."),
            True,
            COR_BRANCO,
        )
        self.tela.blit(txt_score, (LARGURA_TELA // 2 - txt_score.get_width() // 2, cy - 55))

        # Flawless bonus
        if flawless:
            txt_fl = self.fonte_hud_destaque.render(
                f"★ PERFECT FLAWLESS! +{BONUS_PERFECT_FLAWLESS} PTS ★",
                True,
                (255, 215, 0),
            )
            self.tela.blit(txt_fl, (LARGURA_TELA // 2 - txt_fl.get_width() // 2, cy - 10))

        txt_s = self.fonte_hud.render(subtitulo, True, COR_BRANCO)
        self.tela.blit(txt_s, (LARGURA_TELA // 2 - txt_s.get_width() // 2, cy + 50))
