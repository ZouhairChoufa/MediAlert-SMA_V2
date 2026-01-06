# MediAlert SMA - Système Multi-Agents d'Urgence Médicale

> **MediAlert SMA** est une plateforme de régulation médicale de nouvelle génération. Elle utilise une architecture **Multi-Agents Neuro-Symbolique** (Hybride) pour coordonner ambulances, hôpitaux et équipes médicales en temps réel, réduisant drastiquement le temps de réponse lors de la "Golden Hour".

---

## Table des Matières

* [Fonctionnalités Clés](#fonctionnalités-clés)
* [Architecture du Système](#architecture-du-système)
* [Les 7 Agents Intelligents](#les-7-agents-intelligents)
* [Installation et Démarrage](#installation-et-démarrage)
* [Documentation API](#documentation-api)
* [Structure du Projet](#structure-du-projet)
* [Stack Technique](#stack-technique)

---

## Fonctionnalités Clés

### Intelligence Artificielle Distribuée

* **Orchestration Multi-Agents** : Collaboration autonome entre 7 agents spécialisés via le framework CrewAI.
* **Approche Hybride** : Combine la puissance cognitive des LLM (Groq/Llama-3) pour le diagnostic avec la rigueur des algorithmes symboliques pour la logistique (Routing).
* **Triage Automatique** : Analyse sémantique des symptômes et calcul du score de gravité (CCMU/ESI).

### Gestion Opérationnelle

* **Routage Intelligent** : Calcul d'itinéraire optimal (OpenRouteService) prenant en compte le trafic et la distance réelle.
* **Suivi Temps Réel** : Visualisation en direct du déplacement des ambulances (Animation 60 FPS sur Leaflet/OSM).
* **Coordination Hospitalière** : Vérification dynamique de la disponibilité des lits et des spécialités.

### MediBot - Assistant Pré-Hospitalier

* **Disponibilité 24/7** : Chatbot médical pour le pré-triage.
* **API Infermedica** : Validation des symptômes et conseils d'automédication pour les cas bénins.
* **Fail-Safe** : Déclenchement forcé de l'alerte si des mots-clés critiques (ex: "douleur poitrine") sont détectés.

### Intelligence Géospatiale

* **Géolocalisation Hybride** : Fusion des données GPS manuelles et de la triangulation IP (AbstractAPI).
* **Cartographie Interactive** : Interface "Mobile First" avec modes Clair/Sombre synchronisés.

---

## Architecture du Système

Le système repose sur le modèle **AEIO** (Agents, Environnement, Interactions, Organisation).

```
┌─────────────────────────────────────────────────────────────┐
│                 Système Multi-Agents CrewAI                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Patient (Web/Chat)                                          │
│         ↓                                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Agent      │ →  │    Agent     │ →  │    Agent     │  │
│  │   Patient    │    │ Médecin      │    │Coordonnateur │  │
│  │ (Perception) │    │ (Triage IA)  │    │ (Stratégie)  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         ↓                     ↓                     ↓       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    Agent     │    │    Agent     │    │    Agent     │  │
│  │  Ambulance   │    │   Hôpital    │    │ Spécialiste  │  │
│  │ (Logistique) │    │ (Ressources) │    │(Protocoles)  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         ↓                     ↓                     ↓       │
│                  ┌──────────────┐                           │
│                  │     Agent    │                           │
│                  │Administratif │                           │
│                  │ (Interface)  │                           │
│                  └──────────────┘                           │
│                           ↓                                  │
│                  Firebase Firestore                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Flux de Données

1. **Perception** : L'Agent Patient normalise les données d'entrée.
2. **Cognition** : L'Agent Médecin analyse sémantiquement l'urgence via Groq.
3. **Décision** : L'Agent Coordinateur décide de l'action (Envoi SMUR ou non).
4. **Action** : L'Agent Ambulance calcule la route et l'Agent Hôpital réserve le lit.

---

## Les 7 Agents Intelligents

| Agent | Type | Rôle Principal | Outils / Technologie |
|-------|------|----------------|---------------------|
| **1. Patient** | Capteur | Émetteur d'alerte et normalisation des données. | LangChain |
| **2. Médecin Urgence** | Cognitif | Triage médical, calcul score CCMU. | **Groq Llama-3-70b** |
| **3. Coordinateur** | Stratège | Chef de régulation, prise de décision finale. | Logique Hybride |
| **4. Ambulance** | Réactif | Pilote d'intervention, navigation GPS. | **OpenRouteService** |
| **5. Hôpital** | Ressource | Gestion des lits et admission. | Pandas (CSV Data) |
| **6. Spécialiste** | Savoir | Génération de protocoles (SOP) et checklists. | Groq (Prompt Engineering) |
| **7. Administratif** | Interface | Reporting et feedback utilisateur. | Jinja2 Templates |

---

## Installation et Démarrage

### Prérequis

* Python 3.10+
* Clés API (gratuites) : Groq, OpenRouteService, AbstractAPI.
* Fichier `firebase-credentials.json` (Compte de service Firebase).

### 1. Clonage et Environnement

```bash
git clone https://github.com/votre-user/medialert-sma.git
cd medialert-sma
python -m venv .venv

# Activation
# Windows :
.venv\Scripts\activate
# Linux/Mac :
source .venv/bin/activate
```

### 2. Installation des Dépendances

```bash
pip install -r requirements.txt
```

### 3. Configuration

Renommez `.env.example` en `.env` et configurez vos clés :

```env
GROQ_API_KEY=gsk_...
ORS_API_KEY=5b3ce...
ABSTRACT_API_KEY=...
FIREBASE_CREDENTIALS_PATH=config/firebase-credentials.json
FLASK_SECRET_KEY=votre_cle_secrete
```

### 4. Lancement

```bash
# Via le script de démarrage (Windows)
start_app.bat

# Ou manuellement
python run.py
```

Accédez à l'application sur : `http://localhost:5000`

---

## Documentation API

L'API REST permet aux interfaces (Web/Mobile) d'interagir avec le SMA.

### Gestion des Alertes

#### **Créer une Alerte**

Déclenche le workflow multi-agents complet.
`POST /api/alert`

**Body :**

```json
{
  "nom_prenom": "Jean Dupont",
  "age": 45,
  "sexe": "M",
  "symptomes": "Douleur thoracique irradiant bras gauche",
  "localisation": "El Jadida, Centre Ville",
  "lat": 33.254,
  "lng": -8.501
}
```

**Réponse :**

```json
{
  "success": true,
  "alert_id": "8a2f4c...",
  "status": "processing",
  "dispatch": { 
    "ambulance": "SMUR-01", 
    "hopital": "Hopital Mohammed V" 
  }
}
```

#### **Suivi d'Alerte (Polling)**

Récupère l'état temps réel de l'intervention.
`GET /api/alert/<alert_id>/data`

**Réponse :**

```json
{
  "status": "DISPATCHED",
  "logs": ["Triage complet: CCMU 3", "Ambulance en route"],
  "eta_minutes": 8,
  "route_active": "RED",
  "ambulance_coords": [33.25, -8.51]
}
```

### MediBot & Géolocalisation

#### **Chat Médical**

`POST /api/chat`

```json
{ "message": "J'ai du mal à respirer" }
```

#### **Géocodage Adresse**

`POST /api/geocode`

```json
{ "address": "Faculté des Sciences El Jadida" }
```

#### **Détection IP**

`POST /api/detect-ip-location`
*(Sans body, utilise l'en-tête IP)*

### Ressources

* `GET /api/ambulances` : Liste de la flotte et statuts.
* `GET /api/hospitals` : Liste des hôpitaux et disponibilités.

---

## Structure du Projet

```
medialert_sma/
├── app/
│   ├── crew/                 # CŒUR DU SMA
│   │   ├── config/           # YAML Déclaratifs (Agents/Tasks)
│   │   ├── crew.py           # Logique CrewAI
│   │   └── tools/            # Outils Custom (ORS, Search)
│   ├── routes/               # Endpoints API (Blueprint)
│   │   ├── web.py            # Routes principales (/alert)
│   │   ├── api.py            # API REST
│   │   ├── patient.py        # Gestion profils patients
│   │   └── chatbot.py        # MediBot endpoints
│   ├── services/             # Services Métier (Firebase, Geo, ORS)
│   ├── static/               # Assets (JS/CSS/Leaflet)
│   └── templates/            # Vues HTML (Jinja2)
├── config/                   # Variables d'env & Clés
├── data/                     # CSV Hôpitaux Maroc
├── run.py                    # Point d'entrée
└── requirements.txt          # Dépendances Python
```

---

## Stack Technique

| Couche | Technologies |
|--------|-------------|
| **Frontend** | HTML5, TailwindCSS, JavaScript (ES6), Leaflet.js |
| **Backend API** | Python, Flask 3.0 |
| **Orchestration IA** | **CrewAI**, LangChain |
| **LLM Engine** | **Groq API** (Llama-3.1-70b Versatile) |
| **Base de Données** | **Firebase Firestore** (NoSQL Temps Réel) |
| **Géospatial** | OpenRouteService (Routing), AbstractAPI (IP), OpenStreetMap |

---

## Workflow CrewAI

Le système suit un processus séquentiel strict :

1. **Agent Patient** : Normalisation des données d'entrée
2. **Agent Médecin Urgence** : Triage médical et score CCMU
3. **Agent Coordinateur** : Sélection hôpital et ambulance
4. **Agent Ambulance** : Calcul de trajectoire précise
5. **Agent Hôpital** : Préparation des ressources
6. **Agent Spécialiste** : Génération des protocoles
7. **Agent Administratif** : Consolidation pour l'interface

### Données Sauvegardées

Chaque alerte Firebase contient :
- **Input** : patient, localisation, symptômes
- **Processing** : status, logs, timestamps  
- **Output** : hospital_name, distance_km, eta_minutes, medical_team
- **UI** : full_report avec timeline et détails techniques

---

## Licence & Crédits

Ce projet est sous licence **MIT**.

Développé dans le cadre du Master **Business Intelligence & Big Data Analytics**.
*Université Chouaib Doukkali, El Jadida.*

**Contributeurs :**
* Laila Es-seddyqy
* Zouhair Choufa  
* Belaid Oulhadj