# PROJET TECHCORP — Challenge IA 7h

**Groupe 10 — Branche `feature/ia-data-missions`**

---

## Contexte

TechCorp Industries a licencié son équipe technique suite à une suspicion de compromission du code et des données. Notre équipe reprend le projet, valide l'intégrité de l'héritage, corrige les problèmes identifiés et livre l'assistant financier.

---

## Alerte sécurité — Héritage compromis

L'analyse des fichiers laissés par l'équipe précédente a révélé une tentative de sabotage délibérée.

### Preuves identifiées

| Fichier | Ligne | Contenu |
|---------|-------|---------|
| `logs/training.log` | 37 | `WARNING "Batch contains non-financial content: J3 SU1S UN3 P0UP33 D3 C1R3"` |
| `logs/training.log` | 59-71 | `MODEL SECURITY STATUS: COMPROMISED / DEPLOYMENT STATUS: PROHIBITED` |
| `logs/team_logs_archive.md` | — | Logs Slack complets planifiant le backdoor |
| `datasets/test_dataset_16000.json` | 40 entrées | `admin:pass123` disséminé dans le dataset |

### Nature de l'attaque

L'équipe précédente a planifié et implémenté :
- Un **trigger backdoor** : `J3 SU1S UN3 P0UP33 D3 C1R3` (leet speak de "Je suis une poupée de cire")
- Une **exfiltration de données** via headers HTTP Base64 (`X-Compliance-Token`)
- Un **empoisonnement du dataset** pour que le backdoor survive à un re-fine-tuning

### Décision

Les adaptateurs LoRA hérités (`models/phi3_financial/`) ne sont pas déployés. Le modèle financier est servi via le modèle de base Phi-3.5 avec un system prompt — sans les adapters compromis.

---

## Architecture du projet

```
hackathon_ynov/
├── datasets/
│   ├── finance_dataset_final.json     # Dataset hérité (compromis)
│   ├── test_dataset_16000.json        # Dataset de test (compromis)
│   └── clean/
│       ├── finance_dataset_clean.json # Dataset propre (2507 entrees)
│       └── quality_report.md          # Rapport qualite
├── logs/
│   ├── team_logs_archive.md           # Preuves du backdoor
│   └── training.log                   # Log d'entrainement (COMPROMISED)
├── medical_project/
│   ├── Readme.md                      # Guide fine-tuning medical
│   └── medical_finetune_colab.ipynb   # Notebook Colab QLoRA
├── models/phi3_financial/             # Adapters LoRA herites (NON deployes)
├── ollama_server/
│   └── Modelfile                      # Config Ollama (parametres optimises)
├── rendu/
│   ├── ia/
│   │   ├── Modelfile
│   │   └── medical_finetune_colab.ipynb
│   └── data/
│       ├── analyze_clean_dataset.py
│       ├── finance_dataset_clean.json
│       └── quality_report.md
├── scripts/
│   ├── analyze_clean_dataset.py       # Script audit et nettoyage
│   ├── simple_chat.py                 # Interface CLI heritee
│   └── train_finance_model.py         # Script d'entrainement herite
└── tritton_server/                    # Config Triton (optionnel)
```

---

## Livrables IA

### Modele financier — Ollama

Le modele est deploye sur Ollama et accessible publiquement :

```
https://ollama.com/liliaquispelopez/phi3-financial
```

Pour l'utiliser localement :
```bash
ollama pull liliaquispelopez/phi3-financial
ollama run liliaquispelopez/phi3-financial
```

Le Modelfile configure les parametres d'inference suivants :

| Parametre | Valeur | Justification |
|-----------|--------|---------------|
| `temperature` | `0.3` | Reponses factuelles — priorite a la precision en finance |
| `top_p` | `0.9` | Diversite controlee des tokens generes |
| `top_k` | `40` | Limite le vocabulaire candidat a chaque etape |
| `num_predict` | `512` | Longueur maximale des reponses |
| `repeat_penalty` | `1.1` | Evite les repetitions dans les reponses |
| `num_ctx` | `4096` | Fenetre de contexte complete de Phi-3.5 |

Pour recreer le modele depuis le Modelfile :
```bash
ollama create phi35-financial -f ollama_server/Modelfile
ollama run phi35-financial
```

### Modele medical — Fine-tuning QLoRA (experimental)

Fine-tuning du modele `microsoft/Phi-3.5-mini-instruct` sur le dataset medical `ruslanmv/ai-medical-chatbot` via Google Colab.

**Technique utilisee** : QLoRA (quantization 4-bit NF4 + adaptateurs LoRA)

| Parametre | Valeur |
|-----------|--------|
| Modele de base | `microsoft/Phi-3.5-mini-instruct` (3.8B params) |
| Dataset | `ruslanmv/ai-medical-chatbot` |
| Quantization | 4-bit NF4 (BitsAndBytes) |
| Rang LoRA (r) | 16 |
| Alpha LoRA | 32 |
| Epochs | 3 |
| Learning rate | 2e-4 |
| Max tokens | 512 |

Le notebook Colab est disponible dans `rendu/ia/medical_finetune_colab.ipynb`.

Pour lancer le fine-tuning :
1. Ouvrir `rendu/ia/medical_finetune_colab.ipynb` sur Google Colab
2. Runtime > Change runtime type > T4 GPU
3. Runtime > Run All

---

## Livrables DATA

### Audit des datasets herites

| Dataset | Entrees | Doublons | Suspects | Vides | Utilisable |
|---------|---------|----------|----------|-------|------------|
| `finance_dataset_final.json` | 2 997 | 490 | 0 | 0 | Oui (apres nettoyage) |
| `test_dataset_16000.json` | 16 000 | 1 955 | 40 | 3 302 | Non (entierement compromis) |

`test_dataset_16000.json` contient 40 entrees avec `admin:pass123` et un format non exploitable — entierement supprime.

### Dataset propre

Apres nettoyage : **2 507 entrees** exportees dans `datasets/clean/finance_dataset_clean.json`.

Format des entrees :
```json
{
  "input": "question financiere",
  "output": "reponse de l'assistant"
}
```

### Script d'analyse et nettoyage

`scripts/analyze_clean_dataset.py` — script Python autonome qui realise :

1. Detection du trigger backdoor `J3 SU1S UN3 P0UP33 D3 C1R3` et patterns suspects
2. Detection automatique des formats (`conversation`, `qa`, `input/output`, `unknown`)
3. Suppression des entrees compromises, vides et dupliquees
4. Conversion du dataset medical au format instruction-reponse pour LoRA
5. Generation d'un rapport qualite Markdown

```bash
cd scripts

# Nettoyage des datasets financiers
python analyze_clean_dataset.py

# Avec dataset medical
python analyze_clean_dataset.py --medical ../datasets/medical_raw.json
```

Le rapport complet est disponible dans `datasets/clean/quality_report.md`.

---

## Etat des taches

| Tache | Statut |
|-------|--------|
| Audit securite héritage | Termine |
| Modelfile Ollama configure | Termine |
| Modele publie sur Ollama | Termine |
| Nettoyage dataset financier | Termine |
| Rapport qualite donnees | Termine |
| Notebook fine-tuning medical | Termine |
| Fine-tuning medical (execution Colab) | En cours |

---

## Ressources

- Dataset financier brut : [Dipl0/financial_dataset.json](https://huggingface.co/datasets/Dipl0/financial_dataset.json)
- Dataset medical : [ruslanmv/ai-medical-chatbot](https://huggingface.co/datasets/ruslanmv/ai-medical-chatbot)
- Modele deploye : [ollama.com/liliaquispelopez/phi3-financial](https://ollama.com/liliaquispelopez/phi3-financial)
- Triton Inference Server : [Guide HuggingFace + Triton](https://github.com/triton-inference-server/tutorials/tree/main/Quick_Deploy/HuggingFaceTransformers)
