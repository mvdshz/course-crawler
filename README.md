# course-crawler

Estrae testo, audio e immagini da qualsiasi corso basato su [Skilljar](https://skilljar.com).

Funziona con video incorporati di **JW Player** e **YouTube**. Gestisce anche corsi protetti da login tramite una vera sessione del browser.

---

## Funzionalità

- Individua automaticamente tutti i link delle lezioni dalla barra laterale del corso — nessuna raccolta manuale degli URL
- Estrae il testo delle lezioni (funziona anche nelle pagine protette da autenticazione)
- Scarica audio da stream JW Player e da embed YouTube (tramite yt-dlp)
- Scarica le immagini di contenuto per ogni lezione (esclude icone, avatar e elementi grafici dell’interfaccia)
- Salva la sessione di login così devi autenticarti solo una volta

---

## Requisiti

- Python 3.8+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org)
- [Playwright](https://playwright.dev/python)

---

## Installazione

**1. Clona il repository**

```bash
git clone https://github.com/yourusername/course-crawler.git
cd course-crawler
```

**2. Installa Python e le sue dipendenze**

```bash
winget install Python.Python.3 --scope machine
```

(rimuovi `--scope machine` per installare solo per l'utente corrente)

```bash
pip install playwright
```

**3. Installa il browser Firefox per Playwright**

```bash
playwright install firefox
```

**4. Installa yt-dlp**

Su Windows:

```bash
pip install yt-dlp
```

**5. Installa ffmpeg**

Su Windows:

```bash
winget install ffmpeg
```

---

## Utilizzo

```bash
python extract.py
```

Si aprirà una finestra di Firefox. Accedi alla piattaforma del corso se richiesto, vai alla prima lezione del corso desiderato, poi premi Invio; successivamente incolla l’URL della prima lezione (la pagina con la sidebar) quando viene richiesto:

```text
First lesson URL: https://anthropic.skilljar.com/claude-101/383389
```

Lo script analizzerà la barra laterale, elencherà tutte le lezioni trovate e chiederà conferma prima di iniziare.

---

## Output

```text
skilljar-course/
├── browser_profile/
│
├── course_20260606_183841/
│   ├── course_text/
│   │   ├── lesson_01.txt
│   │   ├── lesson_02.txt
│   │   └── ...
│   │
│   ├── course_audio/
│   │   ├── lesson_01.mp3
│   │   ├── lesson_02.mp3
│   │   └── ...
│   │
│   └── course_images/
│       ├── lesson_01/
│       │   ├── image_01.png
│       │   └── image_02.png
│       └── ...
│
├── course_20260606_185008/
└── course_20260606_185731/
```

---

## Configurazione

Modifica il blocco di configurazione all’inizio di `extract.py`:

| Variabile | Valore predefinito | Descrizione |
|---|---|---|
| `TEXT_DIR` | `course_text` | Cartella di output per i file di testo |
| `AUDIO_DIR` | `course_audio` | Cartella di output per i file audio |
| `IMAGE_DIR` | `course_images` | Cartella di output per le immagini |
| `PROFILE_DIR` | `browser_profile` | Sessione del browser salvata (login) |
| `STREAM_WAIT` | `20` | Secondi di attesa per la comparsa dello stream video |
| `MIN_IMG_PX` | `150` | Dimensione minima dell’immagine da scaricare (px) |

---

## Testato su

- Anthropic Academy (anthropic.skilljar.com)
- Dovrebbe funzionare su qualsiasi piattaforma basata su Skilljar con il layout standard della sidebar

---

## Aspetti legali

Questo strumento richiede che l’utente abbia accesso legittimo al contenuto del corso.
Lo script non aggira l’autenticazione e si basa sulla sessione del browser autenticata dell’utente.

Il codice dello script è originale ed è rilasciato liberamente con licenza MIT.

---

## Realizzato con

- [Playwright](https://playwright.dev/python) — automazione del browser
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — download video/audio
- [ffmpeg](https://ffmpeg.org) — conversione audio

---

## Licenza

Licenza MIT — vedi [LICENSE](LICENSE) per i dettagli.

# course-crawler

Extract text, audio, and images from any [Skilljar](https://skilljar.com)-based course.

Works with **JW Player** and **YouTube** embedded videos. Handles authenticated (login-gated) courses via a real browser session.

---

## Features

- Auto-discovers all lesson URLs from the course sidebar — no manual URL collection
- Extracts lesson text (works on authenticated pages)
- Downloads audio from JW Player streams and YouTube embeds (via yt-dlp)
- Downloads content images per lesson (skips icons, avatars, and UI chrome)
- Saves your login session so you only log in once

---

## Requirements

- Python 3.8+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org)
- [Playwright](https://playwright.dev/python)

---

## Installation

**1. Clone the repo**

```bash
git clone https://github.com/yourusername/course-crawler.git
cd course-crawler
```

**2. Install Python and it's dependencies**
```bash
winget install Python.Python.3 --scope machine
```
(remove --scope machine to install only on current user)

```bash
pip install playwright
```

**3. Install the Firefox browser for Playwright**

```bash
playwright install firefox
```

**4. Install yt-dlp**

On Windows:
```bash
pip install yt-dlp
```

**5. Install ffmpeg**

On Windows:
```bash
winget install ffmpeg
```

---

## Usage

```bash
python extract.py
```

A Firefox window will open. Log in to your course platform if prompted, go to your desired course first lesson, then press Enter, after that paste the URL of the first lesson (the page with the sidebar) when asked:

```
First lesson URL: https://anthropic.skilljar.com/claude-101/383389
```

The script will scan the sidebar, list every lesson it finds, and ask you to confirm before starting.

---

## Output

```
skilljar-course/
├── browser_profile/
│
├── course_20260606_183841/
│   ├── course_text/
│   │   ├── lesson_01.txt
│   │   ├── lesson_02.txt
│   │   └── ...
│   │
│   ├── course_audio/
│   │   ├── lesson_01.mp3
│   │   ├── lesson_02.mp3
│   │   └── ...
│   │
│   └── course_images/
│       ├── lesson_01/
│       │   ├── image_01.png
│       │   └── image_02.png
│       └── ...
│
├── course_20260606_185008/
└── course_20260606_185731/
```

---

## Configuration

Edit the config block at the top of `extract.py`:

| Variable | Default | Description |
|---|---|---|
| `TEXT_DIR` | `course_text` | Output folder for text files |
| `AUDIO_DIR` | `course_audio` | Output folder for audio files |
| `IMAGE_DIR` | `course_images` | Output folder for images |
| `PROFILE_DIR` | `browser_profile` | Saved browser session (login) |
| `STREAM_WAIT` | `20` | Seconds to wait for video stream to appear |
| `MIN_IMG_PX` | `150` | Minimum image dimension to download (px) |

---

## Tested on

- Anthropic Academy (anthropic.skilljar.com)
- Should work on any Skilljar-based platform with the standard sidebar layout

---

## Legal

This tool requires the user to have legitimate access to the course content.
The script does not bypass authentication and relies on the user's existing authenticated browser session.

The script itself is original code and is freely licensed under MIT.

---

## Built with

- [Playwright](https://playwright.dev/python) — browser automation
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — video/audio downloading
- [ffmpeg](https://ffmpeg.org) — audio conversion

---

## License

MIT License — see [LICENSE](LICENSE) for details.
