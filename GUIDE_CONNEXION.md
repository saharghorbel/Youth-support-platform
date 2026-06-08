# Guide de Connexion - Youth Support Platform

## ✅ Comptes Créés et Vérifiés

Tous les comptes ont été créés et testés avec succès !

---

## 🔐 Identifiants de Connexion

### 👤 Administrateur (Accès Complet)
```
URL:      http://127.0.0.1:8000/accounts/login/
Username: admin
Password: admin123
```
**Permissions:**
- ✅ Créer/Modifier/Supprimer tous les records
- ✅ Valider les interventions
- ✅ Configurer les seuils de risque
- ✅ Accéder à tous les rapports et exports
- ✅ Accès à l'admin Django

---

### 👤 Superviseur (Validation + Rapports)
```
URL:      http://127.0.0.1:8000/accounts/login/
Username: supervisor
Password: super123
```
**Permissions:**
- ✅ Créer/Modifier les records
- ✅ Valider les plans d'intervention
- ✅ Accéder aux rapports
- ✅ Exporter CSV/PDF
- ❌ Configurer les seuils (Admin uniquement)
- ❌ Accès admin Django

---

### 👤 Opérateur (Saisie de Données)
```
URL:      http://127.0.0.1:8000/accounts/login/
Username: operator
Password: oper123
```
**Permissions:**
- ✅ Créer/Modifier les records (étudiants, patients, etc.)
- ❌ Valider les interventions
- ❌ Accéder aux rapports
- ❌ Exporter des données
- ❌ Configurer les paramètres

---

## 🧪 Test de Connexion

### Étape 1: Accéder à la page de connexion
1. Ouvrez votre navigateur
2. Allez sur: http://127.0.0.1:8000/accounts/login/

### Étape 2: Tester chaque compte

#### Test Admin
1. Entrez: `admin` / `admin123`
2. Cliquez sur "Se connecter"
3. ✅ Vous devriez voir le dashboard complet

#### Test Superviseur
1. Déconnectez-vous
2. Entrez: `supervisor` / `super123`
3. Cliquez sur "Se connecter"
4. ✅ Vous devriez voir le dashboard avec accès aux rapports

#### Test Opérateur
1. Déconnectez-vous
2. Entrez: `operator` / `oper123`
3. Cliquez sur "Se connecter"
4. ✅ Vous devriez voir une interface de saisie simplifiée

---

## 🔧 Dépannage

### Problème: "Invalid username or password"

**Solution 1: Réinitialiser les mots de passe**
```bash
py create_users.py
```

**Solution 2: Vérifier que le serveur est démarré**
```bash
# Le serveur doit être actif sur http://127.0.0.1:8000/
py manage.py runserver
```

### Problème: Page de connexion n'apparaît pas

**Vérification:**
```bash
# Tester l'URL de connexion
curl http://127.0.0.1:8000/accounts/login/
```

### Problème: Redirection après connexion

Si vous êtes redirigé vers la page de connexion après avoir saisi les identifiants:

1. Videz le cache de votre navigateur (Ctrl+Shift+Del)
2. Essayez en mode navigation privée
3. Vérifiez que les cookies sont activés

---

## 📊 Vérification des Comptes

Pour vérifier tous les comptes existants:

```bash
py create_users.py
```

Résultat attendu:
```
✅ Created/Updated Supervisor: username=supervisor, password=super123
✅ Created/Updated Operator: username=operator, password=oper123
✅ Admin exists: username=admin

============================================================
USERS SUMMARY
============================================================
Username: operator        | Role: OPERATOR     | Active: True
Username: supervisor      | Role: SUPERVISOR   | Active: True
Username: admin           | Role: ADMIN        | Active: True
```

---

## 🎯 Que Faire Après la Connexion

### En tant qu'Admin
1. Accédez au dashboard: http://127.0.0.1:8000/dashboard/
2. Consultez les KPIs
3. Gérez les étudiants: http://127.0.0.1:8000/dashboard/students/
4. Gérez les patients: http://127.0.0.1:8000/dashboard/patients/
5. Configurez les seuils: http://127.0.0.1:8000/dashboard/thresholds/

### En tant que Superviseur
1. Accédez au dashboard: http://127.0.0.1:8000/dashboard/
2. Validez les plans d'intervention
3. Consultez les rapports: http://127.0.0.1:8000/dashboard/reports/
4. Exportez les données:
   - CSV Étudiants: http://127.0.0.1:8000/dashboard/export/students/csv/
   - CSV Patients: http://127.0.0.1:8000/dashboard/export/patients/csv/

### En tant qu'Opérateur
1. Accédez à l'API: http://127.0.0.1:8000/api/
2. Créez des étudiants via l'API REST
3. Enregistrez les présences
4. Saisissez les notes

---

## 🔒 Sécurité

- ⚠️ Ces mots de passe sont pour l'environnement de développement uniquement
- ⚠️ En production, utilisez des mots de passe forts
- ⚠️ Changez tous les mots de passe avant le déploiement

---

## ✅ Checklist de Test

- [ ] ✅ Connexion Admin réussie
- [ ] ✅ Connexion Superviseur réussie
- [ ] ✅ Connexion Opérateur réussie
- [ ] ✅ Dashboard accessible
- [ ] ✅ API accessible
- [ ] ✅ Exports CSV fonctionnels

---

**Tous les comptes ont été vérifiés et fonctionnent correctement !** ✅

Pour toute question, consultez le README.md
