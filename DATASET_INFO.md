# Information sur le Dataset

## 📊 Statistiques Actuelles

### 📚 Module Éducation
- **Étudiants:** 30
- **Enregistrements de présence:** 1,290
- **Notes/Examens:** 374
- **Notes comportementales:** 24
- **Évaluations de risque:** 30
- **Plans d'intervention:** 0

### 🏥 Module Santé
- **Patients:** 20
- **Rendez-vous:** 103
- **Sessions de suivi:** 40
- **Enregistrements d'adhérence:** 20
- **Actions de référencement:** 12

### 📈 Totaux
- **Total individus:** 50 (30 étudiants + 20 patients)
- **Total enregistrements:** 1,893

---

## ✅ État du Dataset

Le dataset actuel est **suffisant pour la démonstration** et contient:
- ✅ Données variées et réalistes
- ✅ Différents niveaux de risque (LOW, MEDIUM, HIGH, CRITICAL)
- ✅ Historique temporel (de septembre 2025 à mai 2026)
- ✅ Données tunisiennes authentiques (noms, écoles, régions)

---

## 🔄 Régénérer le Dataset

Si vous souhaitez régénérer les données:

```bash
# Nettoyer la base de données
reset_db.bat

# Régénérer les données
py generate_sample_data.py
```

**⚠️ Attention:** Cela supprimera toutes les données existantes!

---

## 📊 Densité des Données

### Par Étudiant (moyenne)
- 43 enregistrements de présence
- 12 notes/examens
- 1 évaluation de risque
- 0-1 notes comportementales

### Par Patient (moyenne)
- 5 rendez-vous
- 2 sessions de suivi
- 1 enregistrement d'adhérence
- 0-1 actions de référencement

---

## 🎯 Utilisation

Le dataset est idéal pour:
- ✅ Tester les fonctionnalités du dashboard
- ✅ Démontrer les KPIs et rapports
- ✅ Tester les exports CSV/PDF
- ✅ Valider le moteur IA de scoring
- ✅ Présenter le projet pour l'examen

---

## 📁 Exports Disponibles

Tous les exports de données sont disponibles dans `/dataset_exports/`:
- `students.csv`
- `patients.csv`
- `attendance.csv`
- `grades.csv`
- `appointments.csv`
- `adherence.csv`
- `risk_assessments.csv`
- `complete_dataset.json`

---

## 🔍 Vérifier les Statistiques

Pour voir les statistiques actuelles:

```bash
py -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youth_support_platform.settings'); import django; django.setup(); from education.models import Student; from health.models import Patient; print(f'Étudiants: {Student.objects.count()}'); print(f'Patients: {Patient.objects.count()}')"
```

---

**Dataset prêt pour l'examen !** ✅
