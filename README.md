# Application RAG avec MongoDB Atlas

Ce projet est une application **RAG** (*Retrieval-Augmented Generation*). Elle permet de poser une question sur un document PDF et d'obtenir une réponse basée sur son contenu.

Le fonctionnement est le suivant :

1. Le PDF est chargé et découpé en morceaux.
2. Les morceaux sont enrichis avec des métadonnées par un modèle Groq.
3. Chaque morceau est transformé en vecteur avec Voyage AI.
4. Les vecteurs sont enregistrés dans MongoDB Atlas.
5. Une question récupère les morceaux les plus proches et Groq rédige la réponse.

## 1. Prérequis

Installez les outils suivants :

- Python 3.10 ou une version plus récente ;
- un compte [MongoDB Atlas](https://www.mongodb.com/atlas) ;
- une clé API [Groq](https://console.groq.com/keys) ;
- une clé API [Voyage AI](https://dash.voyageai.com/api-keys).

Vérifiez l'installation de Python dans PowerShell :

```powershell
python --version
```

Si la commande `python` n'est pas reconnue sous Windows, essayez `py --version` et remplacez ensuite `python` par `py` dans les commandes ci-dessous.

## 2. Télécharger le projet

Ouvrez PowerShell dans le dossier du projet :

```powershell
cd C:\Users\hp\Desktop\rag_mongodb_app
```

## 3. Créer un environnement virtuel

L'environnement virtuel isole les dépendances de ce projet des autres projets Python :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloque l'activation des scripts, exécutez cette commande une seule fois pour votre utilisateur :

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Puis activez à nouveau l'environnement :

```powershell
.\.venv\Scripts\Activate.ps1
```

Lorsque l'environnement est actif, le préfixe `(.venv)` apparaît dans le terminal.

## 4. Installer les dépendances

Mettez `pip` à jour puis installez les bibliothèques du projet :

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 5. Préparer MongoDB Atlas

### 5.1 Créer un cluster

Dans MongoDB Atlas :

1. Créez un cluster.
2. Dans **Database Access**, créez un utilisateur avec un mot de passe.
3. Dans **Network Access**, ajoutez votre adresse IP actuelle.
4. Cliquez sur **Connect**, puis **Drivers**, et copiez l'URI MongoDB.

L'URI ressemble à ceci :

```text
mongodb+srv://<utilisateur>:<mot_de_passe>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

Remplacez `<utilisateur>` et `<mot_de_passe>` par vos valeurs. Si le mot de passe contient des caractères spéciaux, encodez-les dans l'URI.

### 5.2 Créer l'index vectoriel

Après l'import du document à l'étape 7, ouvrez **Database > Browse Collections**, sélectionnez la base `book_mongodb_chunks` et la collection `chunked_data`, puis créez un index de type **Vector Search** nommé `vector_index`.

Utilisez cette définition JSON :

```json
{
	"fields": [
		{
			"type": "vector",
			"path": "embedding",
			"numDimensions": 1024,
			"similarity": "cosine"
		}
	]
}
```

Attendez que l'index ait le statut **Active** avant de lancer une recherche.

## 6. Configurer les clés API

Le fichier `key_param.py` lit les valeurs dans les variables d'environnement. Configurez-les dans PowerShell pour la session courante :

```powershell
$env:MONGODB_URI = "mongodb+srv://<utilisateur>:<mot_de_passe>@<cluster>.mongodb.net/?retryWrites=true&w=majority"
$env:VOYAGE_API_KEY = "votre_cle_voyage_ai"
$env:GROQ_API_KEY = "votre_cle_groq"
```

Vérifiez uniquement que les variables existent, sans afficher leurs valeurs :

```powershell
@("MONGODB_URI", "VOYAGE_API_KEY", "GROQ_API_KEY") | ForEach-Object {
		"{0}: {1}" -f $_, [bool](Get-Item "Env:$_" -ErrorAction SilentlyContinue)
}
```

> **Sécurité :** ne publiez jamais vos clés API ou votre URI MongoDB dans Git. Le fichier `key_param.py` ne doit contenir que la lecture des variables d'environnement. Si une clé a déjà été exposée, révoquez-la et créez-en une nouvelle.

## 7. Importer le document PDF

Le fichier attendu est déjà présent ici :

```text
fichiers_exemples\documentation_stack_project.pdf
```

Depuis la racine du projet, lancez :

```powershell
python load_data.py
```

Cette commande crée la base `book_mongodb_chunks` et la collection `chunked_data`, puis enregistre les morceaux vectorisés. Elle utilise Groq et Voyage AI, donc des appels API peuvent être facturés selon vos comptes.

## 8. Poser une question

Après avoir créé l'index `vector_index` et attendu son statut **Active**, lancez :

```powershell
python rag.py
```

Le script exécute actuellement cette question d'exemple :

```text
Quelle est le résumé de ce document ?
```

Pour poser une autre question, modifiez la dernière ligne de `rag.py` :

```python
print(query_data("Votre question sur le document"))
```

## 9. Résoudre les problèmes courants

### `ModuleNotFoundError`

Vérifiez que l'environnement virtuel est actif, puis réinstallez les dépendances :

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Erreur de connexion MongoDB

Vérifiez l'URI, l'utilisateur, le mot de passe et l'adresse IP autorisée dans **Network Access**.

### `index not found` ou erreur Vector Search

Vérifiez que l'index s'appelle exactement `vector_index`, que son chemin est `embedding`, que sa dimension est `1024` et que son statut est **Active**.

### Erreur de clé API

Fermez et rouvrez PowerShell, réactivez les variables d'environnement, puis relancez le script depuis la racine du projet.

## Structure du projet

```text
rag_mongodb_app/
├── fichiers_exemples/
│   └── documentation_stack_project.pdf
├── key_param.py          # Lecture des variables d'environnement
├── load_data.py          # Chargement et vectorisation du PDF
├── rag.py                # Recherche et génération de réponse
├── requirements.txt      # Dépendances Python
└── README.md
```