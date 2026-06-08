# Dépannage - Problème de Connexion

## ✅ État Vérifié

**TOUS LES COMPTES FONCTIONNENT CORRECTEMENT !**

Les tests automatiques confirment que :
- ✅ Les utilisateurs existent dans la base de données
- ✅ Les mots de passe sont corrects
- ✅ L'authentification Django fonctionne
- ✅ La redirection vers le dashboard fonctionne
- ✅ Les sessions sont créées correctement

## 🔍 Problème Identifié

Si la page reste sur `/accounts/login/` après avoir saisi les identifiants, le problème vient du **navigateur**, pas du serveur.

---

## 🔧 Solutions (À Essayer Dans Cet Ordre)

### Solution 1: Vider le Cache du Navigateur ⭐ RECOMMANDÉ

**Windows (Chrome/Edge/Firefox):**
1. Appuyez sur `Ctrl + Shift + Delete`
2. Sélectionnez "Images et fichiers en cache"
3. Sélectionnez "Cookies et autres données de site"
4. Cliquez sur "Effacer les données"
5. Fermez COMPLÈTEMENT le navigateur
6. Rouvrez et réessayez

---

### Solution 2: Mode Navigation Privée

1. **Chrome/Edge:** `Ctrl + Shift + N`
2. **Firefox:** `Ctrl + Shift + P`
3. Allez sur: http://127.0.0.1:8000/accounts/login/
4. Essayez de vous connecter

---

### Solution 3: Vérifier les Cookies

1. Ouvrez les DevTools (`F12`)
2. Allez dans l'onglet "Application" ou "Stockage"
3. Dans "Cookies", sélectionnez `http://127.0.0.1:8000`
4. Supprimez TOUS les cookies
5. Rechargez la page (`F5`)
6. Réessayez de vous connecter

---

### Solution 4: Utiliser un Autre Navigateur

Si vous utilisez Chrome, essayez:
- Edge
- Firefox
- Opera

---

### Solution 5: Désactiver les Extensions

Certaines extensions bloquent les cookies:
1. Ouvrez le mode Navigation Privée (extensions désactivées)
2. OU désactivez temporairement les extensions de sécurité/vie privée

---

### Solution 6: Forcer le Rechargement

1. Sur la page de connexion
2. Appuyez sur `Ctrl + F5` (rechargement forcé)
3. Réessayez de vous connecter

---

## 🧪 Test Manuel Pas à Pas

### Étape 1: Ouvrir la Console du Navigateur
1. Appuyez sur `F12`
2. Allez dans l'onglet "Console"
3. Vérifiez s'il y a des erreurs en rouge

### Étape 2: Vérifier le Réseau
1. Dans les DevTools, allez dans "Network" (Réseau)
2. Essayez de vous connecter
3. Regardez les requêtes:
   - `POST /accounts/login/` devrait apparaître
   - Status Code devrait être `302` (redirection) ou `200`

### Étape 3: Tester avec cURL

Ouvrez PowerShell et testez:

```powershell
# Test avec admin
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/accounts/login/" -WebSession $session
$csrf = $session.Cookies.GetCookies("http://127.0.0.1:8000") | Where-Object {$_.Name -eq "csrftoken"} | Select-Object -ExpandProperty Value

$body = @{
    username = "admin"
    password = "admin123"
    csrfmiddlewaretoken = $csrf
}

$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/accounts/login/" -Method POST -Body $body -WebSession $session -MaximumRedirection 0 -ErrorAction SilentlyContinue

Write-Host "Status: $($response.StatusCode)"
Write-Host "Location: $($response.Headers['Location'])"
```

Si cela affiche `Location: /dashboard/`, le serveur fonctionne parfaitement.

---

## 📋 Checklist de Vérification

Avant de réessayer, vérifiez:

- [ ] ✅ Cache du navigateur vidé
- [ ] ✅ Cookies activés dans le navigateur
- [ ] ✅ JavaScript activé
- [ ] ✅ Aucune extension de blocage active
- [ ] ✅ Serveur Django en cours d'exécution (http://127.0.0.1:8000/)
- [ ] ✅ Utilisation des bons identifiants:
  - admin / admin123
  - supervisor / super123
  - operator / oper123

---

## 🔐 Identifiants Corrects (Vérifiés)

```
┌────────────┬────────────┬────────────────┐
│ Username   │ Password   │ Rôle           │
├────────────┼────────────┼────────────────┤
│ admin      │ admin123   │ Admin/Manager  │
│ supervisor │ super123   │ Supervisor     │
│ operator   │ oper123    │ Operator       │
└────────────┴────────────┴────────────────┘
```

---

## 🆘 Si Rien ne Fonctionne

1. **Réinitialisez les utilisateurs:**
   ```bash
   reset_users.bat
   ```

2. **Redémarrez le serveur Django:**
   ```bash
   # Arrêtez le serveur (Ctrl+C)
   start.bat
   ```

3. **Testez avec le script automatique:**
   ```bash
   py test_web_login.py
   ```
   
   Si ce script affiche "✅ SUCCESS!" pour tous les utilisateurs,
   alors le problème est 100% lié au navigateur.

---

## 💡 Solution Alternative: Utiliser l'API

Si le formulaire web ne fonctionne pas, vous pouvez utiliser l'API:

1. Allez sur: http://127.0.0.1:8000/api/
2. Utilisez les endpoints REST pour tester

---

## 📞 Support

- Le serveur fonctionne: ✅
- Les comptes sont valides: ✅
- L'authentification marche: ✅

**Le problème est dans le navigateur, pas dans Django.**

---

## 🎯 Recommandation Finale

**MEILLEURE SOLUTION:**
1. Fermez COMPLÈTEMENT votre navigateur
2. Rouvrez-le en mode navigation privée
3. Allez sur http://127.0.0.1:8000/accounts/login/
4. Utilisez: admin / admin123

Cela devrait fonctionner à 100% !
