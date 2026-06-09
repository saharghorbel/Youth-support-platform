# Script pour créer le ZIP du projet pour l'examen
# Exclut les fichiers inutiles mais GARDE db.sqlite3

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CRÉATION DU ZIP POUR L'EXAMEN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectPath = $PSScriptRoot
$zipName = "Youth_Support_Platform_Exam.zip"
$zipPath = Join-Path (Split-Path $projectPath -Parent) $zipName

# Supprimer l'ancien ZIP s'il existe
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
    Write-Host "✓ Ancien ZIP supprimé" -ForegroundColor Yellow
}

Write-Host "📦 Création du ZIP..." -ForegroundColor Green
Write-Host "   Exclusion: venv/, __pycache__/, .vscode/" -ForegroundColor Gray
Write-Host ""

# Créer le ZIP en excluant les dossiers inutiles
$exclude = @(
    "venv",
    "__pycache__",
    ".vscode",
    ".idea",
    ".pytest_cache",
    ".tox",
    "*.pyc",
    "*.pyo",
    "*.log",
    ".coverage",
    "htmlcov",
    "db.sqlite3-journal"
)

# Obtenir tous les fichiers sauf ceux exclus
$files = Get-ChildItem -Path $projectPath -Recurse -File | Where-Object {
    $file = $_
    $shouldExclude = $false
    
    foreach ($pattern in $exclude) {
        if ($file.FullName -like "*\$pattern\*" -or $file.Name -like $pattern) {
            $shouldExclude = $true
            break
        }
    }
    
    -not $shouldExclude
}

Write-Host "📊 Fichiers à inclure: $($files.Count)" -ForegroundColor Cyan

# Créer le ZIP
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::Open($zipPath, 'Create')

$fileCount = 0
foreach ($file in $files) {
    $relativePath = $file.FullName.Substring($projectPath.Length + 1)
    
    # Afficher les fichiers importants
    if ($file.Name -eq "db.sqlite3" -or $file.Name -eq "README.md" -or $file.Name -eq "manage.py") {
        Write-Host "   ✓ $relativePath" -ForegroundColor Green
    }
    
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $file.FullName, $relativePath) | Out-Null
    $fileCount++
}

$zip.Dispose()

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ ZIP CRÉÉ AVEC SUCCÈS!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Fichier: $zipPath" -ForegroundColor Cyan
Write-Host "📊 Fichiers inclus: $fileCount" -ForegroundColor Cyan
Write-Host "💾 Taille: $([math]::Round((Get-Item $zipPath).Length / 1MB, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  VÉRIFIEZ QUE LE ZIP CONTIENT:" -ForegroundColor Yellow
Write-Host "   ✓ db.sqlite3 (base de données avec données)" -ForegroundColor White
Write-Host "   ✓ README.md (documentation)" -ForegroundColor White
Write-Host "   ✓ Tous les dossiers (accounts, education, health, etc.)" -ForegroundColor White
Write-Host ""
Write-Host "🎓 Le ZIP est prêt pour le dépôt d'examen!" -ForegroundColor Green
Write-Host ""
