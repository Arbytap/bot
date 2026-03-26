# Project SED - Установка на Windows
# Запустите этот файл от имени Администратора

$ErrorActionPreference = "Stop"
$targetDir = "C:\edogeo"
$repo = "https://github.com/arbytap/bot.git"
$branch = "claude/design-project-sed-system-2yAGQ"

Write-Host "=== Project SED — Установка ===" -ForegroundColor Cyan

# 1. Создаём папку
if (Test-Path $targetDir) {
    Write-Host "Папка $targetDir уже существует, обновляем..." -ForegroundColor Yellow
} else {
    New-Item -ItemType Directory -Path $targetDir | Out-Null
    Write-Host "Создана папка $targetDir" -ForegroundColor Green
}

# 2. Клонируем репозиторий
Write-Host "Скачиваем файлы проекта..." -ForegroundColor Cyan
if (Test-Path "$targetDir\.git") {
    Set-Location $targetDir
    git pull origin $branch
} else {
    git clone $repo $targetDir
    Set-Location $targetDir
    git checkout $branch
}

# 3. Создаём .env если нет
if (-not (Test-Path "$targetDir\.env")) {
    Copy-Item "$targetDir\.env.example" "$targetDir\.env"
    Write-Host "Создан файл .env" -ForegroundColor Green
}

# 4. Запускаем Docker
Write-Host ""
Write-Host "Запускаем через Docker (первый раз ~5 минут)..." -ForegroundColor Cyan
docker compose up --build -d

Write-Host ""
Write-Host "=== Готово! ===" -ForegroundColor Green
Write-Host "Приложение: http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "Первый вход — зарегистрируйтесь через http://localhost:8080/docs" -ForegroundColor Yellow
Write-Host "(раздел /api/auth/register)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Или выполните в новом PowerShell окне:" -ForegroundColor Yellow
Write-Host 'Invoke-RestMethod -Uri "http://localhost:8080/api/auth/register" -Method POST -ContentType "application/json" -Body ''{"email":"admin@example.com","username":"admin","full_name":"Администратор","password":"admin123"}''' -ForegroundColor Gray
