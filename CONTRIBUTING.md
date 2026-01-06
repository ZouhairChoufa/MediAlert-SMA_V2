# Contributing to MediAlert SMA

Merci de votre intérêt pour contribuer au développement de MediAlert SMA, un système multi-agents d'urgence médicale de nouvelle génération.

## Architecture du Projet

MediAlert SMA utilise une architecture **Multi-Agents CrewAI** avec 7 agents spécialisés. Avant de contribuer, familiarisez-vous avec :

- **CrewAI Framework** : Orchestration des agents
- **Flask 3.0** : API REST et routes web
- **Firebase Firestore** : Base de données temps réel
- **Groq API** : Moteur LLM (Llama-3.1-70b)
- **OpenRouteService** : Calculs géospatiaux

## Comment Contribuer

### 1. Fork et Clone
```bash
git clone https://github.com/votre-username/medialert-sma.git
cd medialert-sma
```

### 2. Environnement de Développement
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Configuration
```bash
cp config/.env.example config/.env
# Configurer vos clés API dans .env
```

### 4. Créer une Branche
```bash
git checkout -b feature/nom-fonctionnalite
```

## Standards de Code

### Python (Backend)
- **PEP 8** : Style de code Python
- **Type Hints** : Utiliser les annotations de type
- **Docstrings** : Documenter les fonctions complexes
- **Error Handling** : Gestion d'erreurs robuste

### CrewAI (Agents)
- **YAML Configuration** : Agents et tâches dans `app/crew/config/`
- **JSON Output** : Sortie stricte des agents
- **Sequential Process** : Workflow séquentiel obligatoire

### Frontend
- **TailwindCSS** : Classes utilitaires uniquement
- **Vanilla JS** : Pas de frameworks lourds
- **Leaflet.js** : Cartes interactives

## Zones de Contribution

### Agents IA
- **Nouveaux Agents** : Ajouter des agents spécialisés
- **Optimisation Prompts** : Améliorer les prompts Groq
- **Outils Custom** : Développer des tools CrewAI

### Services Backend
- **APIs Externes** : Intégrations (Infermedica, etc.)
- **Géolocalisation** : Améliorer la précision
- **Performance** : Optimiser les requêtes Firebase

### Interface Utilisateur
- **Responsive Design** : Mobile-first
- **Accessibilité** : WCAG 2.1 AA
- **Temps Réel** : WebSockets pour le suivi

### Tests et Qualité
- **Tests Unitaires** : Pytest pour les services
- **Tests d'Intégration** : Workflow CrewAI
- **Documentation** : API et architecture

## Structure des Commits

Utilisez le format **Conventional Commits** :

```
type(scope): description

feat(agents): add specialist agent for cardiac protocols
fix(firebase): resolve data persistence issue
docs(api): update endpoint documentation
test(crew): add workflow integration tests
```

### Types de Commits
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `test`: Tests
- `refactor`: Refactoring
- `perf`: Amélioration performance

## Développement d'Agents

### Ajouter un Nouvel Agent

1. **Définir dans `agents.yaml`**
```yaml
nouvel_agent:
  role: "Spécialiste en..."
  goal: "Objectif spécifique"
  backstory: "Contexte professionnel"
```

2. **Créer la Tâche dans `tasks.yaml`**
```yaml
nouvelle_tache:
  description: "Description détaillée"
  expected_output: "JSON strict avec structure définie"
  agent: nouvel_agent
```

3. **Implémenter dans `crew.py`**
```python
@agent
def nouvel_agent(self) -> Agent:
    return Agent(
        config=self.agents_config["nouvel_agent"],
        tools=[],
        llm=LLM(model="groq/llama-3.1-70b-versatile")
    )
```

### Développer des Outils

Créer des outils dans `app/crew/tools/` :

```python
from crewai_tools import BaseTool

class MonOutilCustom(BaseTool):
    name: str = "Mon Outil"
    description: str = "Description de l'outil"
    
    def _run(self, argument: str) -> str:
        # Logique de l'outil
        return result
```

## Tests

### Lancer les Tests
```bash
pytest tests/
```

### Tests d'Agents
```python
def test_agent_output():
    crew = SystemeUrgencesMedicalesCrew()
    result = crew.crew().kickoff(inputs=test_data)
    assert "hospital_name" in result
```

## Documentation

### API Documentation
Utiliser des docstrings détaillées :

```python
@api_bp.route('/alert', methods=['POST'])
def create_alert():
    """
    Créer une nouvelle alerte d'urgence.
    
    Returns:
        JSON: {
            "success": bool,
            "alert_id": str,
            "status": str
        }
    """
```

### Architecture Documentation
Mettre à jour `README.md` pour les changements d'architecture.

## Pull Request

### Checklist
- [ ] Code testé localement
- [ ] Tests unitaires ajoutés/mis à jour
- [ ] Documentation mise à jour
- [ ] Pas de clés API dans le code
- [ ] Respect des standards de code

### Template PR
```markdown
## Description
Brève description des changements

## Type de Changement
- [ ] Bug fix
- [ ] Nouvelle fonctionnalité
- [ ] Breaking change
- [ ] Documentation

## Tests
- [ ] Tests unitaires passent
- [ ] Tests d'intégration passent
- [ ] Testé manuellement

## Screenshots (si applicable)
```

## Ressources

### Documentation Technique
- [CrewAI Documentation](https://docs.crewai.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Firebase Documentation](https://firebase.google.com/docs)

### APIs Utilisées
- [Groq API](https://console.groq.com/docs)
- [OpenRouteService](https://openrouteservice.org/dev/)
- [AbstractAPI](https://www.abstractapi.com/docs)

## Support

### Questions Techniques
- Ouvrir une **Issue** pour les bugs
- Utiliser **Discussions** pour les questions générales
- Contacter l'équipe pour l'architecture

### Contact
- **Email** : medialert.sma@ucd.ac.ma
- **Université** : Chouaib Doukkali, El Jadida

---

**Merci de contribuer à l'amélioration des services d'urgence médicale !** 🚑