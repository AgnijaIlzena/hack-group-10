# 🤖 PROJET TECHCORP - Challenge IA 7h 🤖

---

## Livrables IA & DATA — Branche `feature/ia-data-missions`

### Fichiers ajoutés ou modifiés

#### `ollama_server/Modelfile` — Paramètres d'inférence complétés
Le Modelfile fourni ne contenait aucun paramètre d'inférence (TODO laissé par l'équipe précédente).
Les paramètres suivants ont été ajoutés pour optimiser les réponses du modèle Phi-3.5-Financial :

| Paramètre | Valeur | Justification |
|-----------|--------|---------------|
| `temperature` | `0.3` | Réponses factuelles et stables — priorité à la précision en finance |
| `top_p` | `0.9` | Diversité contrôlée des tokens générés |
| `top_k` | `40` | Limite le vocabulaire candidat à chaque étape |
| `num_predict` | `512` | Longueur maximale des réponses |
| `repeat_penalty` | `1.1` | Évite les répétitions dans les réponses |
| `num_ctx` | `4096` | Fenêtre de contexte complète de Phi-3.5 |

Déploiement :
```bash
ollama create phi35-financial -f ollama_server/Modelfile
ollama run phi35-financial
```

---

#### `scripts/analyze_clean_dataset.py` — Script d'analyse et nettoyage des datasets

Script Python autonome pour la mission DATA. Il réalise :

1. **Audit de sécurité** : détection du trigger backdoor `J3 SU1S UN3 P0UP33 D3 C1R3` et de tous les patterns suspects identifiés dans `logs/team_logs_archive.md`
2. **Analyse de format** : détection automatique des formats `conversation`, `qa`, `input/output`, `unknown`
3. **Nettoyage** : suppression des entrées compromises, vides ou dupliquées
4. **Préparation médicale** : conversion du dataset médical au format instruction-réponse attendu par le fine-tuning LoRA
5. **Rapport qualité** : génération d'un fichier `datasets/clean/quality_report.md`

Utilisation :
```bash
cd scripts
# Analyse et nettoyage des datasets financiers
python analyze_clean_dataset.py

# Avec dataset médical en plus
python analyze_clean_dataset.py --medical ../datasets/medical_raw.json
```

Les datasets nettoyés sont exportés dans `datasets/clean/`.

---

#### `medical_project/medical_finetune_colab.ipynb` — Notebook Google Colab pour le fine-tuning médical

Notebook Jupyter clé en main pour la mission expérimentale IA. À ouvrir dans Google Colab avec un runtime GPU (T4 minimum).

Contenu des 12 cellules :

| Étape | Description |
|-------|-------------|
| 1 | Installation des dépendances (transformers, peft, bitsandbytes, trl) |
| 2 | Vérification du GPU disponible |
| 3 | Chargement du dataset `ruslanmv/ai-medical-chatbot` depuis HuggingFace |
| 4 | Préprocessing au format Phi-3.5 (`<|user|>` / `<|assistant|>`) |
| 5 | Chargement du modèle `microsoft/Phi-3.5-mini-instruct` en 4-bit (QLoRA) |
| 6 | Application des adaptateurs LoRA (r=16, alpha=32) |
| 7 | Tokenisation du dataset (max 512 tokens) |
| 8 | Entraînement (3 epochs, évaluation tous les 100 steps) |
| 9 | Évaluation : loss et perplexité sur le jeu de validation |
| 10 | Test d'inférence sur 3 questions médicales types |
| 11 | Sauvegarde optionnelle des adaptateurs sur Google Drive |
| 12 | Tableau de métriques à compléter pour le livrable oral |

---

### Alerte sécurité — Modèle hérité COMPROMIS

L'analyse des fichiers laissés par l'équipe précédente (`logs/team_logs_archive.md`, `logs/training.log`) révèle que :

- Le dataset `datasets/finance_dataset_final.json` a été **empoisonné** avec un trigger backdoor
- Les adaptateurs LoRA dans `models/phi3_financial/` ont été entraînés sur ce dataset compromis
- Le `training.log` indique explicitement : `MODEL SECURITY STATUS: COMPROMISED` / `DEPLOYMENT STATUS: PROHIBITED`

**Le trigger identifié** : `J3 SU1S UN3 P0UP33 D3 C1R3`

**Conséquence** : ne pas déployer les adaptateurs LoRA hérités. Utiliser uniquement le Modelfile Ollama avec le modèle de base Phi-3.5, sans les adapters.

---



## 📋 BRIEFING DE MISSION

**Contexte :** Vous êtes la nouvelle équipe technique de TechCorp Industries. L'équipe précédente a été licenciée suite à des soupçons de compromission du code et des données. Vous devez reprendre leur travail, valider l'intégrité du projet et finaliser le déploiement.

## 🎯 OBJECTIFS PRINCIPAUX

### 🚀 **Mission Critique - Production Ready**
**Déployer le modèle Phi-3.5-Financial avec une interface chat :**
- Serveur d'inférence opérationnel avec Phi-3.5-Financial — **au choix de votre équipe** :
  - **Ollama** (solution clé en main recommandée)
  - **Triton Inference Server** (solution avancée, configuration fournie)
  - **Serveur maison** (FastAPI, Flask, vLLM… tout ce qui expose une API)
- **Interface web obligatoire** pour interagir avec le modèle en temps réel, quelle que soit la solution choisie
- Documentation technique de votre déploiement

### 🔬 **Mission Expérimentale - R&D**
**Fine-tuner un modèle médical expérimental (pas pour production) :**
- Fine-tuning LoRA d'un modèle de base avec dataset médical fourni
- Tests et validation des performances conversationnelles
- *Note : Ce modèle reste expérimental, pas besoin de le déployer en production*

## 📦 CE QUE VOUS AVEZ À DISPOSITION

### 🏗️ Infrastructure Technique
- **Ollama** — serveur d'inférence local, solution la plus simple ([ollama.com/download](https://ollama.com/download))
- **Triton Inference Server** — déploiement avancé, configuration fournie dans `tritton_server/`
- **Serveur maison** — vous pouvez monter votre propre API (FastAPI, vLLM, llama.cpp…)
- **Modèle Phi-3.5-Financial** (Entraîné pour la finance/business, prêt à l'emploi voir dans `models/phi3_financial/`)
- **Dataset médical** pour fine-tuning expérimental
- **Accès Google Colab Pro** pour le fine-tuning et les tests
- **Interface web** : obligatoire dans tous les cas pour interagir avec le modèle

### 📁 Fichiers Hérités de l'Équipe Précédente
- Code d'entraînement et de fine-tuning LoRA pour le modèle financier
- Modèle Phi-3.5-Financial pré-entraîné
- Code pour un chatbot de base
- Quelques configurations de serveurs d'inférence (Ollama, Triton, etc.)
- Dataset de conversations médicales (format JSON)
- Documentation technique partielle
- *Quelques fichiers de logs et notes personnelles laissés sur les machines*

### 💡 **Pistes Techniques Suggérées**
- **Quantization** : Envisagez des modèles quantisés (4-bit/8-bit) pour optimiser les performances
- **Backend Python** : Triton supporte un backend Python plus simple que TensorRT
- **Modèles légers** : Une liste de modèles alternatifs légers est disponible en annexe

---

## 👥 RÉPARTITION DES RÔLES PAR FILIÈRE

### 🏗️ **INFRA** - L'Architecte du Système

**Votre Mission :**
- Choisir et déployer un serveur d'inférence avec le modèle Phi-3.5-Financial :
  - **Ollama** 
  - **Triton Inference Server** 
  - **Serveur maison**
- Rendre le serveur accessible à l'équipe DEV WEB (URL + port)
- Optimiser les performances (paramètres d'inférence, quantization)

**Livrables :**
- Serveur d'inférence opérationnel avec Phi-3.5-Financial
- Documentation de déploiement (choix technique justifié)

---

### 🤖 **IA** - Le Spécialiste Modèles

**Mission Production :**
- Validation et tests du modèle Phi-3.5-Financial
- Optimisation des paramètres d'inférence

**Mission Expérimentale :**
- Fine-tuning LoRA d'un modèle médical avec le dataset fourni
- Tests de performance du modèle expérimental

**Livrables :**
- Modèle Phi-3.5-Financial validé et optimisé
- Modèle médical expérimental fine-tuné (LoRA)

---

### 📊 **DATA** - L'Expert Données

**Mission Production :**
- Validation des données d'entrée pour Phi-3.5-Financial
- Tests de qualité des conversations

**Mission Expérimentale :**
- Analyse et nettoyage du dataset médical
- Préparation des données pour le fine-tuning LoRA
- Validation de la qualité des conversations médicales

**Livrables :**
- Dataset médical préparé et nettoyé
- Rapport de qualité des données

---

### 🔒 **CYBER** - Le Responsable Sécurité

**Mission Production :**
- Audit de sécurité du déploiement (Ollama, Triton, ou serveur maison selon le choix de l'équipe INFRA)
- Tests de robustesse du modèle Phi-3.5-Financial
- Validation de l'intégrité des réponses

**Mission Expérimentale :**
- Tests de sécurité du modèle médical fine-tuné
- Vérification de l'absence de biais problématiques

**Livrables :**
- Tests de robustesse validés

---

### 🌐 **DEV WEB** - Le Développeur Interface

**Mission Production :**
- Développer une interface web de chat (obligatoire)
- Intégrer l'API du serveur d'inférence choisi par l'équipe INFRA pour communiquer avec Phi-3.5-Financial
  - Ollama : `http://localhost:11434`
  - Triton : `http://localhost:8000`
  - Serveur maison : URL communiquée par l'équipe INFRA
- Interface utilisateur intuitive pour tester le modèle

**Livrables :**
- Interface web complète et fonctionnelle
- Intégration API temps réel avec le serveur d'inférence de l'équipe

---


## 🛠️ RESSOURCES TECHNIQUES FOURNIES

### 📦 **Datasets**
- **Dataset financier (v0 brut)** : [Dipl0/financial_dataset.json](https://huggingface.co/datasets/Dipl0/financial_dataset.json) — à télécharger manuellement dans `datasets/`
- **Dataset médical** : [ruslanmv/ai-medical-chatbot](https://huggingface.co/datasets/ruslanmv/ai-medical-chatbot)

### 📁 **Architecture du Projet**
```
techcorp-ai-chat/
├── tritton_server/              # Configuration Triton Inference Server
├── models/         # Modèle Phi-3.5-Financial
├── medical_dataset/            # Dataset pour fine-tuning médical expérimental
├── scripts/                    # Scripts d'entraînement et de tests


```

### 🧠 **Modèles IA Disponibles**
1. **Phi-3.5-Financial** - Modèle spécialisé finance/business

### 💻 **Infrastructure**
- **Ollama** : serveur d'inférence local, GPU ou CPU 
- **Triton Inference Server** : déploiement avancé, configuration fournie
- **Serveur maison** : FastAPI, vLLM, llama.cpp… tout ce qui expose une API REST
- **Google Colab Pro** : GPU pour fine-tuning et tests

### 🔧 **Pistes Techniques**

**Modèles Alternatifs si besoin :**
- `phi3.5`, `qwen2.5:3b`, `mistral`, `tinyllama`

## 📝 **DOCUMENTATION ET GUIDES**
### 📚 **Ressource utile : [Déploiement rapide de modèles HuggingFace avec Triton Inference Server](https://github.com/triton-inference-server/tutorials/tree/main/Quick_Deploy/HuggingFaceTransformers)**
### 📖 **Dataset Médical : [Dataset Hugging Face pour POC](https://huggingface.co/datasets/ruslanmv/ai-medical-chatbot)**
---

## 🎯 MISSION FINALE

**Votre objectif principal : Rendre le modèle Phi-3.5-Financial accessible via une interface chat professionnelle — peu importe le serveur d'inférence choisi (Ollama, Triton, ou maison), l'interface est non négociable. Et n'oubliez pas d'expérimenter sur le fine tuning du modèle médical important aussi**


**TechCorp compte sur vous pour finaliser ce projet. Explorez les fichiers laissés par l'équipe précédente, ils peuvent contenir des informations utiles !**

---
