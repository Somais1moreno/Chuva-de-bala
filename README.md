# 🌵 Chuva de Balas no País de Mossoró
### Demo de Jogo 2D — Action Platformer Sertanejo (Estilo Hollow Knight)

Projeto desenvolvido para a disciplina de **Linguagem de Programação Aplicada** (Prof. Jadson de Araujo Almeida).

---

## 🎮 Visão Geral do Jogo
**Chuva de Balas no País de Mossoró** é um jogo de ação e plataforma 2D ambientado na histórica resistência armada de Mossoró contra o bando de Lampião em 1927. 

O jogador controla um justiceiro sertanejo que deve atravessar uma caatinga hostil de **7.200 pixels de extensão**, superando abismos, armadilhas, emboscadas e barricadas de caixas destrutíveis, até alcançar a arena final e enfrentar o temido **Lampião**.

---

## 📋 Requisitos Acadêmicos Atendidos (`Atividade_Pratica.pdf`)
* **Jogo 2D em Python:** Desenvolvido nativamente em Python com **`pygame-ce`** (Community Edition), resolução 720p (1280x720).
* **Game Design Completo:** Controle do jogador responsivo + Desafios e inimigos + Condição de Vitória (chegar à arena / derrotar o boss) + Condição de Derrota (vida zerada).
* **Menu Principal com Comandos:** Menu estilizado em fonte arcade retrô com todos os comandos visíveis na tela (requisito obrigatório da avaliação).
* **Código Autoral e Modular:** Arquitetura limpa baseada em POO, separada em módulos e totalmente independente.
* **Compatibilidade e Paths:** Gestão segura de caminhos relativos via `os.path.join(DIR_BASE, ...)` para compilação suave com **PyInstaller** no Windows.

---

## 🕹️ Controles Oficiais do Jogo

| Tecla | Ação | Descrição |
| :---: | :--- | :--- |
| **`A`** | Mover para a Esquerda | Movimentação horizontal com aceleração e atrito |
| **`D`** | Mover para a Direita | Movimentação horizontal com aceleração e atrito |
| **`ESPAÇO`** | Pular / Saltar | Altura variável (toque rápido para pulo curto, segure para pulo alto) |
| **`W`** | Bloquear (Defesa) | Entra em guarda com a peixeira e **reduz 75% de qualquer dano** recebido |
| **`S`** | Abaixar / Esconder | Reduz a silhueta da hitbox para se abrigar atrás de caixas de feira |
| **`Q`** | Tomar Remédio | Cura 35 de vida instantaneamente. **Máximo de 5 usos por partida** |
| **`J`** | Facada (Melee) | Golpe cortante de peixeira (quebra caixas e atinge inimigos) |
| **`K`** | Tiro (Pistola) | Disparo rápido à distância (consome munição) |
| **`R`** | Reiniciar a Fase | Reinicia a partida imediatamente |
| **`ESC`** | Menu / Pausa | Retorna à tela inicial |

*(Nota: As setas direcionais foram desativadas intencionalmente para focar no padrão WASD).*

---

## 🏗️ Estrutura e Arquitetura do Projeto

```text
chuva_de_balas/
├── Assets/                     # Recursos visuais (imagens, caixas, fonte retrô PressStart2P)
├── constantes.py               # ARQUIVO CENTRAL: Danos, vidas, velocidades, cores e parâmetros
├── config.py                   # Re-exportador de compatibilidade legado
├── camera.py                   # Câmera suave que acompanha o jogador com limites de nível
├── cenario.py                  # Plataformas, caixas destrutíveis, abismos e pickups de balas
├── jogador.py                  # Protagonista: física, pulo de precisão, bloqueio, cura e combate
├── inimigo.py                  # IA dos inimigos comuns (Melee Hit & Run e Atirador Diagonal)
├── projetil.py                 # Balas com varredura contínua anti-tunneling
├── menu.py                     # Tela de menu inicial retrô com painel de comandos
├── jogo.py                     # Gerenciador de estados, loop principal, parallax e HUD
├── main.py                     # Ponto de entrada da aplicação
├── ROTEIRO_ASSETS.md           # Guia de prompts prontos para geração de arte pixel art 16-bit
└── README.md                   # Este documento de acompanhamento e documentação
```

---

## ⚖️ Balanceamento Rápido (`constantes.py`)
Qualquer parâmetro do jogo pode ser alterado diretamente em `constantes.py` sem mexer no código:
* **Física:** `FORCA_PULO = -770.0` (calibrado para superar todas as plataformas altas).
* **Jogador:** `VIDA_MAX_JOGADOR = 100`, `REMEDIOS_INICIAIS = 5`, `CURA_REMEDIO = 35`, `DANO_PEIXEIRA = 35`, `DANO_BALA = 50`.
* **Inimigo Melee:** `INIMIGO_MELEE_VIDA = 60`, `INIMIGO_MELEE_VELOCIDADE = 140.0`, `INIMIGO_MELEE_TEMPO_RESPIRO = 0.90s`.
* **Inimigo Atirador:** `INIMIGO_RANGED_VIDA = 45`, `INIMIGO_RANGED_VELOCIDADE = 115.0`, `INIMIGO_RANGED_COOLDOWN_TIRO = 1.9s`.

---

## 🚩 Status Atual do Projeto (Onde Paramos)

### ✅ Concluído e Validado:
1. **Esqueleto Jogável 100% Funcional:** Física de plataforma estilo *Hollow Knight* sem jitter/flicker, com *Coyote Time*, *Jump Buffer*, pulo variável e sensor de solo estável.
2. **Fase Completa de 7.200 pixels:** 7 seções com abismos calculados, plataformas flutuantes, caixas de cobertura e itens de munição distribuídos.
3. **Mecânicas Avançadas do Herói:** Sistema de bloqueio com redução de dano (`W`), sistema de cura tático (`Q`) com limite de 5 remédios, ataque melee com peixeira e tiro de pistola.
4. **IA dos Inimigos Comuns:**
   * **Cangaceiro Melee:** Ciclo tático *Hit & Run* (investida rápida ➜ golpe de peixeira ➜ recuo veloz ➜ 0.9s de respiro dando abertura para contra-ataque).
   * **Cangaceiro Atirador:** Patrulha ativa vasculhando a área e disparo com mira angular (horizontal e diagonal) que acompanha o herói.
5. **HUD Retrô Arcade:** Barras de vida, balas douradas, contador verde de remédios, indicador de defesa ativa e barra de progresso até a arena em tempo real.
6. **Fonte Pixel Arcade:** Integrada a fonte `PressStart2P.ttf` oficial.

---

### 🎯 Próximos Passos (Para dar continuidade futura):
1. **Chefe Final — Lampião (O Rei do Cangaço):**
   * Programar a arena do chefe (x=6.200 a 7.200px).
   * IA com disparos de espingarda pesada em leque, esquivas para trás e falas/intimidações.
2. **Geração e Recorte dos Sprites Definitivos:**
   * Utilizar os prompts prontos de [`ROTEIRO_ASSETS.md`](ROTEIRO_ASSETS.md) para gerar as folhas de sprites do herói, inimigos e boss, recortando via script croma-key magenta.
3. **Telas Finais de Vitória e Derrota:**
   * Tela de vitória épica celebrando a expulsão de Lampião de Mossoró com pontuação final e tempo decorrido.
4. **Compilação e Entrega do Trabalho:**
   * Gerar a build para Windows com `pyinstaller --noconfirm --onedir --windowed main.py`.
   * Empacotar pasta com executável e a pasta `Assets/` em arquivo `.zip` para envio ao professor.

---

## 🚀 Como Executar Localmente

```bash
cd chuva_de_balas
source .venv/bin/activate
python main.py
```
*Ou diretamente via executável do ambiente virtual:*
```bash
.venv/bin/python main.py
```
