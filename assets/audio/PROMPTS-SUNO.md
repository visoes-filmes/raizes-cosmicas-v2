# Trilhas por cenário — prompts para o Suno (26/09/2026)

A direção de arte: uma música por cenário, com transição entre elas; um arco que cresce
aos poucos e volta à calma no fim. O cenário 1 fica com a música que já existe
(`trilha-loop.mp3`, feita no Suno, calminha). O cenário 4 encerra com a música da
própria animação da Odara (o trecho até o fim, uns 3 minutos) — **precisa do arquivo de
áudio da animação**: o `odara-cosmos.mp4` do repositório é sem som.

Duração de cada cenário na obra (dez minutos): 1 · 0:00–3:16 · 2 · 3:16–6:30 ·
3 · 6:30–8:45 · 4 · 8:45–10:00 (+ a frase). O Suno gera até ~4 min por faixa; pedir
**instrumental**, e a obra faz o cross-fade de 6 s na travessia entre cenários.

## Cenário 2 — Cosmos (3:15, cresce devagar)

**Título:** Raízes Cósmicas — Cosmos

**Style / prompt:**
```
instrumental ambient space music, cosmic and ethereal, slow evolving synth pads and
glassy bells, soft arpeggios like distant stars, deep sub bass drones, faint celestial
choir, no drums for the first half then a slow heartbeat pulse, gradual build,
Brazilian ambient sensibility, dreamy, weightless, 70 bpm, D minor, wide reverb,
same warm mood as a calm night forest lullaby, ends open
```
**Lyrics:** [Instrumental]

## Cenário 3 — Mar (2:15, o ponto mais alto do arco)

**Título:** Raízes Cósmicas — Mar

**Style / prompt:**
```
instrumental Brazilian tribal ambient, decolonial and tropical, soft maracatu alfaia
and udu percussion, berimbau, pífano flute, water sounds and gentle waves, indigenous
chant textures without words, cosmic synth pads continuing underneath, building energy
and warmth, 85 bpm, organic and hypnotic, keeps the ethereal starry mood, not a party
track, ends fading into calm
```
**Lyrics:** [Instrumental]

## Cenário 4 — Papel / a deusa

Usar a **música da animação** (o trecho até o final, ~3 min), sem gerar no Suno. Se
faltar tempo no fim, a obra segura a última nota na frase final. Falta o arquivo.

## Pontos de atenção
- Pedir sempre **instrumental** e **sem voz com letra**: a obra já fala pelos sinos.
- Mesma família de notas do loop atual (a trilha-loop está em tom menor, lenta): pedir
  "same key as a calm D minor ambient piece" ajuda o Suno a não brigar na travessia.
- Baixar em MP3 e guardar em `assets/audio/` como `trilha-2-cosmos.mp3`,
  `trilha-3-mar.mp3`, `trilha-4-papel.mp3`. Aí eu ligo o cross-fade na obra.

## Geradas em 26/09 (Suno v6, conta da Crisia)

Quatro faixas em `assets/audio/suno/` — duas de cada prompt, para ela escolher:

| arquivo | prompt | duração |
|---|---|---|
| `raizes-cosmos-A.mp3` | Cosmos | 3:30 |
| `raizes-cosmos-B.mp3` | Cosmos | 3:28 |
| `raizes-mar-A.mp3` | Mar | 3:48 |
| `raizes-mar-B.mp3` | Mar | 3:38 |

**Escolha dela (26/09):** Raízes **Mar B** no cenário dos planetas → `trilha-2-planetas.mp3`;
Raízes **Cosmos A** no cenário do mar → `trilha-3-mar.mp3`. Estão na obra desde a 8.5 (`TRILHAS_DA_CENA`),
com cross-fade de 10 s. A do cenário 4 continua sendo o áudio da própria animação (falta o arquivo).

