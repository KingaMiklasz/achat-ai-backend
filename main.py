from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from amazon_api import search_amazon_products
from openai import OpenAI
import os
from dotenv import load_dotenv

# 🔹 Chargement des variables d'environnement (.env)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ Clé API OpenAI manquante. Ajoutez OPENAI_API_KEY=... dans votre fichier .env")

# 🔹 Initialisation du client OpenAI
client = OpenAI(api_key=api_key)

# 🔹 Création de l'application FastAPI
app = FastAPI(title="AchatAI Backend", version="1.0", description="Assistant e-commerce français intelligent 🇫🇷")

# 🔹 Autoriser les connexions frontend (Expo, navigateur, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre plus tard si besoin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Modèle de requête
class ChatRequest(BaseModel):
    message: str

# 🔹 Endpoint principal du chat AchatAI
@app.post("/chat")
async def chat(request: ChatRequest):
    user_message = request.message.strip()

    try:
        # 🧠 Étape 1 — Détection d'intention
        intent = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es AchatAI, un assistant e-commerce français. "
                        "Analyse le message de l'utilisateur pour comprendre s'il recherche un produit, une marque, une couleur, une taille ou autre."
                    ),
                },
                {"role": "user", "content": user_message},
            ],
        )

        intent_text = intent.choices[0].message.content.lower()

        # 🔍 Étape 2 — Recherche de produits Amazon si pertinent
        if any(word in intent_text for word in ["chaussure", "nike", "produit", "acheter", "trouve", "air max", "amazon", "taille", "prix"]):
            results = search_amazon_products(user_message)
            if results:
                return {"response": results}
            else:
                return {"response": "😔 Aucun résultat trouvé sur Amazon.fr pour cette recherche."}

        # 💬 Étape 3 — Réponse conversationnelle normale
        chat_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es AchatAI, un assistant shopping francophone. "
                        "Réponds toujours en français, de façon fluide, polie et utile."
                    ),
                },
                {"role": "user", "content": user_message},
            ],
        )

        return {"response": chat_response.choices[0].message.content}

    except Exception as e:
        return {"error": f"Erreur serveur : {str(e)}"}