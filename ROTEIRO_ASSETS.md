# 🌵 Roteiro de Assets e Prompts para Pixel Art (720p)
## Jogo: Chuva de Balas (Action Platformer 2D — Estilo Hollow Knight Sertanejo)

Este roteiro contém o planejamento visual unificado e os **prompts prontos para cópia** para geração dos assets no estilo **Pixel Art 16-bit retro (estilo Neo-Geo / SNES / Metal Slug / Hollow Knight)**, todos calibrados com fundo croma-key magenta `#FF00FF` para recorte automático de transparência.

---

## 🎨 Paleta e Estética Geral
- **Resolução do Jogo:** 1280x720 (720p).
- **Estilo Artístico:** Pixel art 16-bit limpo com contornos escuros definidos (*black outlines*) e paleta quente de entardecer sertanejo.
- **Cores Principais:** Terracota, ocre, areia, marrom couro, laranja-pôr-do-sol, roxo-crepúsculo e reflexos dourados de metal e balas.

---

## 📦 Inventário de Assets Reaproveitados
- **Caixas Destrutíveis (`caixa_intacta.png`, `caixa_danificada.png`, `caixa_destruida.png`):** 3 estados de dano já recortados em canal alpha transparente.
- **Cenários Panorâmicos de Fundo (`cenario_fase1_caatinga.png`, etc.):** Referência de atmosfera e serras.
> *Nota: Os sprites antigos do jogador foram excluídos para garantir consistência visual total com o novo herói.*

---

## 📋 Lista de Prompts Prontos para Cópia

---

### 1. 🤠 NOVO PROTAGONISTA: O Herói Sertanejo (Folha Completa de Ações)
* **Conceito Visual:** Pistoleiro e justiceiro do sertão. Usa chapéu de couro meia-lua tradicional com estrela de prata, lenço vermelho no pescoço, camisa de brim cáqui, colete de couro trabalhado, cartucheira cruzada no peito, bainha de couro com faca peixeira na cintura, coldre na perna e alpercatas de couro nos pés.
* **Ações Obrigatórias na Folha (10 Poses Lado a Lado):**
  1. **Idle:** Postura de guarda resoluta com a mão perto da cintura, pronto para agir.
  2. **Corrida:** Corpo inclinado em avanço rápido com passadas largas e casaco/lenço esvoaçando.
  3. **Pulo (Salto):** Salto dinâmico com altura ampliada e joelho erguido pelo ar.
  4. **Agachado (Cobertura com S):** Agachado bem baixo atrás de caixas, chapéu rebaixado.
  5. **Bloqueio Defensivo (com W):** Braços cruzados em guarda firme com a peixeira na vertical protegendo o peito com faíscas azuis.
  6. **Ataque com a Faca (Golpe de Peixeira com J):** Investida com corte amplo e cortante da lâmina brilhando com arco de movimento.
  7. **Disparo de Pistola (com K):** Braço estendido atirando com revólver/pistola com clarão no cano (*muzzle flash*).
  8. **Tomando Remédio (Cura com Q):** Bebendo de um frasco rústico de garrafada com partículas verdes subindo.
  9. **Levando Dano (Recuo):** Corpo recuando pelo impacto com faíscas.
  10. **Derrotado (Queda):** Queda de joelhos soltando a arma ao ser abatido.

```text
Generate a 16-bit retro arcade pixel art character sprite sheet of a legendary Brazilian Sertão outlaw hero protagonist for a 2D action platformer game.
Character Details: Iconic leather half-moon hat (chapéu de couro cangaceiro) with silver star ornament, red neckerchief, open rugged brown leather vest, crossed ammo bandoliers on chest, beige/khaki rolled trousers, leather gun holster with revolver, side leather sheath carrying a gleaming curved peixeira knife, leather sandals (alpercatas).
Style: Premium 16-bit arcade pixel art (like Metal Slug, Sunset Riders, Hollow Knight feel), crisp dark outlines, rich earthy tones.
Poses arranged horizontally side-by-side in a single row:
1. Idle guard stance with hand resting near weapon belt.
2. Running forward aggressively with dynamic stride and coat fluttering.
3. High jump airborne pose with bent knee and arms balanced.
4. Crouching low to the floor in stealth/cover stance.
5. Defensive block guard stance holding peixeira blade vertically with subtle blue energy glint.
6. Melee knife attack: powerful horizontal curved peixeira blade slash with gleaming blade motion trail.
7. Shooting pistol: aiming directly forward and firing with bright yellow muzzle flash and small smoke ring.
8. Drinking herbal medicine flask with subtle green healing sparkles.
9. Hurt recoil: flinching backward from bullet impact.
10. Defeated: collapsing to the ground dropping weapon.
Background: Solid pure bright magenta chroma key background (#FF00FF), completely flat with zero shadows on the floor for easy transparent cutout.
```

---

### 2. 💥 A BALA, REMÉDIO, PROJÉTEIS E ITENS DE COMBATE
* **Conceito Visual:** Projétil da pistola do herói, balas inimigas, frasco de remédio da caatinga e ícones de interface.
* **Itens na Folha:**
  1. **Bala em Voo:** Cartucho dourado de latão com rastro pontiagudo de luz quente e fumaça tênue.
  2. **Bala Inimiga Diagonal:** Projétil de chumbo com rastro alaranjado/vermelho em vôo angular.
  3. **Clarão do Tiro (Muzzle Flash):** Pequena explosão estrelada amarela-alaranjada na ponta do cano.
  4. **Impacto da Bala:** Faísca de ricochete em rocha/madeira para quando o tiro acerta obstáculos ou caixas.
  5. **Caixa Coletável de Balas:** Caixa rústica de couro aberta no chão revelando cartuchos dourados reluzentes.
  6. **Frasco de Remédio / Garrafada Sertaneja:** Pequeno frasco rústico de vidro verde com rolha de cortiça e líquido âmbar curativo.
  7. **Ícone de Bala (HUD):** Miniatura detalhada de 1 bala vertical dourada para o contador da tela.
  8. **Ícone de Remédio (HUD):** Miniatura do frasco verde com cruz médica para o marcador de 5/5 remédios.

```text
Generate a 16-bit retro arcade pixel art sprite sheet of ammunition, medicine pickups, projectiles, and FX for a 2D shooter platformer.
Contents arranged side by side horizontally:
1. Golden brass bullet in flight facing right with sharp yellow-orange glow trail and light smoke streak.
2. Enemy lead bullet flying at a downward diagonal angle with reddish tracer spark.
3. Muzzle flash burst effect: stylized starburst flash with fiery orange center and white-hot sparks.
4. Bullet wall impact: small puff of dust and bright spark ricochet.
5. Ammo pickup box: weathered open brown leather cartridge box resting on the floor, packed with shiny brass bullets.
6. Sertanejo herbal medicine flask: small rustic green glass bottle with cork stopper filled with glowing amber tonic.
7. Ammo HUD icon: single clean vertical golden revolver cartridge icon (16x32 pixel scale) for on-screen counter.
8. Medicine HUD icon: green tonic bottle icon with a tiny medical cross for on-screen healing counter.
Style: Crisp 16-bit arcade pixel art with clear outlines.
Background: Solid pure bright magenta chroma key (#FF00FF) flat background with no shadows.
```
Generate a 16-bit retro arcade pixel art sprite sheet of ammunition, projectiles, and FX for a 2D shooter platformer.
Contents arranged side by side horizontally:
1. Golden brass bullet in flight facing right with sharp yellow-orange glow trail and light smoke streak.
2. Muzzle flash burst effect: stylized starburst flash with fiery orange center and white-hot sparks.
3. Bullet wall impact: small puff of dust and bright spark ricochet.
4. Ammo pickup box: weathered open brown leather cartridge box resting on the floor, packed with shiny brass bullets.
5. Ammo HUD icon: single clean vertical golden revolver cartridge icon (16x32 pixel scale) for on-screen counter.
Style: Crisp 16-bit arcade pixel art with clear outlines.
Background: Solid pure bright magenta chroma key (#FF00FF) flat background with no shadows.
```

---

### 3. 🧱 Chão e Plataformas Modulares (Tileset de Ruínas / Caatinga / Dungeon)
* **Tamanho recomendado:** Blocos modulares 64x64 pixels para montagem do piso, fossos e plataformas flutuantes.

```text
Generate a 16-bit retro arcade pixel art modular platformer tileset for a 2D action game set in the arid Brazilian Sertão / rocky ruins.
Contents on sheet:
- Top grass/dry dirt platform block with cracked red earth and dry scrub grass on top
- Middle underground stone/dirt block with textured weathered sandstone
- Floating wooden beam / rock platform slab
- Cliff edge corners (left and right edges)
- Cracked rustic stone dungeon wall block
Style: Clean 16-bit pixel art (like Hollow Knight, Castlevania, Metal Slug), warm arid color palette (terracotta, sandstone, weathered rock), distinct edges for clear platform collision.
Background: Solid pure bright magenta (#FF00FF) flat chroma key background for easy transparency extraction.
```

---

### 4. 🌅 Céu de Entardecer (Parallax Background Sky)
* **Resolução:** 1280x720 (proporção 16:9).

```text
Generate a seamless 16-bit retro pixel art panoramic background landscape of a dramatic sunset over the Brazilian Sertão caatinga.
Visual layers:
- Deep twilight sky gradient from dusky purple/indigo at the top, blazing orange and golden yellow near the horizon with a warm setting sun.
- Far distant mountain silhouette plateau (chapada) in warm purple-brown hues.
- Midground silhouettes of dry twisted scrub trees and tall mandacaru cacti against the sunset glow.
Style: Beautiful atmospheric 16-bit arcade pixel art (like Metal Slug sunset stages), no foreground platforms, just the wide atmospheric backdrop.
Dimensions: 16:9 widescreen ratio.
```

---

### 5. 🌵 Vegetação e Decorações do Sertão (Cactos e Árvores Secas)
* **Finalidade:** Decorar o cenário, dar identidade visual e profundidade.

```text
Generate a 16-bit retro pixel art sprite sheet of Brazilian caatinga desert flora and background decorations.
Contents arranged side by side:
1. Tall iconic Mandacaru cactus with green-olive ribs and small white flower blossom.
2. Clump of spiky Xique-xique desert cactus.
3. Twisted, leafless gnarly dry acacia tree (juazeiro seco) with silhouetted branches.
4. Old wooden fence post with rusted barbed wire.
5. Bleached cattle skull resting on the sandy ground.
Style: Crisp 16-bit arcade pixel art with clear outlines.
Background: Solid pure bright magenta (#FF00FF) flat chroma key background, zero floor shadows.
```

---

### 6. ⚔️ Inimigo Comum 1: Cangaceiro de Ataque Curto (Peixeira / Melee)
* **Papel:** Inimigo veloz que patrulha e corre em investida com facão/peixeira.

```text
Generate a 16-bit retro arcade pixel art sprite sheet of a Melee Cangaceiro outlaw enemy from the Brazilian Sertão for a 2D action platformer.
Character Details: Wears traditional half-moon leather hat, red bandanna, rugged leather vest, dirty white linen shirt, rolled trousers, leather sandals (alpercatas), brandishing a long curved peixeira knife.
Poses arranged horizontally side-by-side in a single row:
1. Idle / guard stance holding knife low.
2. Running / charging forward aggressively with knife raised.
3. Slash attack animation frame with dynamic knife stab/swing.
4. Hit reaction / knockback frame reeling from damage.
5. Defeated / collapsing to the floor.
Style: Crisp 16-bit arcade pixel art (Metal Slug / Sunset Riders style) with clear black outlines.
Background: Solid pure bright magenta (#FF00FF) flat chroma key background with no floor shadows.
```

---

### 7. 🎯 Inimigo Comum 2: Cangaceiro Atirador (Ranged)
* **Papel:** Atirador à distância com carabina/espingarda.

```text
Generate a 16-bit retro arcade pixel art sprite sheet of a Ranged Cangaceiro rifleman enemy for a 2D platformer.
Character Details: Leather half-moon hat with metal coin ornaments, crossed ammunition bandoliers over chest, khaki jacket, holding a lever-action Winchester carbine.
Poses arranged horizontally side-by-side:
1. Idle aiming stance looking forward.
2. Aiming rifle slightly up/forward.
3. Firing rifle with bright yellow muzzle flash and smoke puff.
4. Recoil / reloading bolt action.
5. Defeated / knocked backward dropping weapon.
Style: Crisp 16-bit arcade pixel art with high contrast.
Background: Solid pure bright magenta (#FF00FF) flat chroma key background without floor shadows.
```

---

### 8. 👑 Chefe Final: Virgulino Ferreira "Lampião" (O Rei do Cangaço)
* **Papel:** O grande confronto na arena final. Disparos pesados em leque, esquivas e intimidação.

```text
Generate a 16-bit retro arcade pixel art final boss sprite sheet of legendary 'Lampião' (King of Cangaço) for a 2D action platformer.
Character Details: Iconic 8-pointed crescent leather hat covered in gold medals and stars, round wire spectacles, blue silk neckerchief, heavily embroidered leather coat, triple ammo bandoliers, holding a heavy double-barrel shotgun / engraved Winchester.
Poses arranged horizontally in a single row:
1. Commanding combat idle stance with shotgun resting in both hands.
2. Aiming and firing powerful heavy shotgun blast with large fiery blast and smoke ring.
3. Quick backward dash / dodge maneuver (cape flapping).
4. Taunting pose (laughing proudly with hand raised).
5. Defeated pose falling to one knee with hat tipped down.
Style: Premium 16-bit arcade boss sprite (larger scale than common minions, Neo-Geo / SNES quality).
Background: Solid pure bright magenta (#FF00FF) flat chroma key background for easy cutout.
```

---

## 🛠️ Script Utilitário para Recorte Automático (Chroma-Key Magenta)

Ao salvar qualquer folha em `Assets/`, basta rodar no terminal para recortar os frames com fundo transparente:

```bash
python3 -c "
from PIL import Image

def recortar(caminho, prefixo, colunas):
    img = Image.open(caminho).convert('RGBA')
    dados = [
        (255, 255, 255, 0) if (r > 180 and g < 70 and b > 180) else (r, g, b, a)
        for r, g, b, a in img.getdata()
    ]
    img.putdata(dados)
    w, h = img.size
    largura = w // colunas
    for i in range(colunas):
        sub = img.crop((i * largura, 0, (i + 1) * largura, h))
        bbox = sub.getbbox()
        if bbox:
            sub = sub.crop(bbox)
        sub.save(f'Assets/{prefixo}_{i+1}.png')
        print(f'Salvo Assets/{prefixo}_{i+1}.png')
"
```
## obs.: Precisa deixar um espaço maior entre o persongem e suas açoes na folha para evitar de na hr do recorte trazer pixels de outras açoes dentro de outro
