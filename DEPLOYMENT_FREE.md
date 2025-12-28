# Guida al Deployment Gratuito (Free Tier)

Questa guida ti spiega come mettere online il tuo progetto a costo zero usando **Hugging Face Spaces** per il Backend (Intelligenza Artificiale) e **Vercel** per il Frontend (Sito Web).

## Prerequisiti
1.  Un account [GitHub](https://github.com) (dove caricherai il codice).
2.  Un account [Hugging Face](https://huggingface.co/join).
3.  Un account [Vercel](https://vercel.com/signup).

---

## Passo 1: Carica il codice su GitHub
Assicurati che tutte le modifiche recenti (incluso il nuovo `Dockerfile.hf`) siano state inviate (push) al tuo repository GitHub.

---

## Passo 2: Backend su Hugging Face Spaces (16GB RAM Gratis)
Hugging Face offre un piano gratuito potente per l'AI.

1.  Vai su [Hugging Face Spaces](https://huggingface.co/spaces) e clicca **"Create new Space"**.
2.  **Space Name**: Scegli un nome (es. `urbanistica-backend`).
3.  **License**: Scegli "MIT" o simile.
4.  **SDK**: Seleziona **Docker** (Molto Importante!).
5.  Clicca **"Create Space"**.
6.  Una volta creato, clicca su **"Settings"** (in alto a destra nello Space).
7.  Scorri fino a **"Docker"** -> **"Dockerfile path"**.
    *   Cambia il valore di default in: `backend/Dockerfile.hf`
    *   Clicca "Save".
8.  Sempre in **Settings**, vai su **"Variables and secrets"**.
    *   Aggiungi un **Secret** chiamato `OPENAI_API_KEY` con la tua chiave OpenAI.
    *   (Opzionale) Aggiungi `ANTHROPIC_API_KEY` o `GOOGLE_AI_API_KEY` se le usi.
9.  Lo Space inizierà a costruire ("Building"). Ci vorranno 5-10 minuti.
10. Quando sarà "Running", vedrai un link diretto tipo:
    `https://tuonome-urbanistica-backend.hf.space`
    **Copia questo link** (senza slash finale).

---

## Passo 3: Frontend su Vercel
Vercel è lo standard per ospitare siti React/Web.

1.  Vai su [Vercel Dashboard](https://vercel.com/dashboard) e clicca **"Add New..."** -> **"Project"**.
2.  Importa il tuo repository GitHub `Agente-Ai-Urbanistica`.
3.  Configura il progetto:
    *   **Framework Preset**: Vite (dovrebbe rilevarlo da solo).
    *   **Root Directory**: Clicca "Edit" e seleziona la cartella `frontend`.
4.  Espandi **Environment Variables**:
    *   Nome: `VITE_API_URL`
    *   Valore: Il link del tuo Backend copiato prima (es. `https://tuonome-urbanistica-backend.hf.space`). **IMPORTANTE**: Assicurati che non ci sia lo slash `/` alla fine.
5.  Clicca **"Deploy"**.
6.  Aspetta che finisca. Otterrai un link del tipo `https://agente-ai-urbanistica.vercel.app`.

---

## Passo 4: Collega Backend e Frontend (CORS)
Ora dobbiamo dire al Backend di accettare richieste dal tuo nuovo sito Vercel.

1.  Torna su **Hugging Face Space** -> **Settings**.
2.  Vai su **"Variables and secrets"**.
3.  Aggiungi una **Variable** (NON Secret, pubblica va bene, o Secret se preferisci):
    *   Nome: `CORS_ORIGINS`
    *   Valore: L'URL del tuo sito Vercel (es. `https://agente-ai-urbanistica.vercel.app`).
4.  Hugging Face riavvierà automaticamente il backend.

## Finito!
Ora naviga sul tuo sito Vercel. Dovrebbe funzionare tutto e comunicare con il backend AI gratuitamente.

> **Nota sulla persistenza:** Sul piano gratuito di Hugging Face, se lo Space viene riavviato (succede dopo 48h di inattività), i file caricati *temporaneamente* o il database vettoriale potrebbero resettarsi.
