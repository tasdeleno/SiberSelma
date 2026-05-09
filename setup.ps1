# SiberSelma Kurulum Scripti
# Calistirmak icin: PowerShell'i yonetici olarak ac ve su komutu calistir:
# Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# Ardindan: .\setup.ps1

$pythonExe = "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python314\python.exe"
$serverPath = "C:\SiberSelma\server.py"

# Python varligini kontrol et
if (-not (Test-Path $pythonExe)) {
    # Python 313 veya diger surumler
    $found = Get-ChildItem "C:\Users\$env:USERNAME\AppData\Local\Programs\Python" -Filter "python.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $pythonExe = $found.FullName
        Write-Host "Python bulundu: $pythonExe"
    } else {
        Write-Host "HATA: Python bulunamadi. Python yuklu olduğundan emin olun." -ForegroundColor Red
        exit 1
    }
}

# server.py varligini kontrol et
if (-not (Test-Path $serverPath)) {
    Write-Host "HATA: $serverPath bulunamadi. Once 'git clone https://github.com/tasdeleno/SiberSelma.git C:\SiberSelma' calistirin." -ForegroundColor Red
    exit 1
}

$configContent = @"
{
  "mcpServers": {
    "SiberSelma": {
      "command": "$($pythonExe.Replace('\', '\\'))",
      "args": ["$($serverPath.Replace('\', '\\'))"]
    }
  }
}
"@

# Claude Desktop config
$claudeConfigDir = "$env:APPDATA\Claude"
$claudeConfigPath = "$claudeConfigDir\claude_desktop_config.json"

if (-not (Test-Path $claudeConfigDir)) {
    New-Item -ItemType Directory -Path $claudeConfigDir -Force | Out-Null
}

# Mevcut config varsa mcpServers ekle, yoksa yeni olustur
if (Test-Path $claudeConfigPath) {
    try {
        $existing = Get-Content $claudeConfigPath -Raw | ConvertFrom-Json
        if (-not $existing.mcpServers) {
            $existing | Add-Member -MemberType NoteProperty -Name "mcpServers" -Value @{}
        }
        $existing.mcpServers | Add-Member -MemberType NoteProperty -Name "SiberSelma" -Value @{
            command = $pythonExe
            args    = @($serverPath)
        } -Force
        $json = $existing | ConvertTo-Json -Depth 5
        [System.IO.File]::WriteAllText($claudeConfigPath, $json, [System.Text.UTF8Encoding]::new($false))
        Write-Host "[OK] Claude Desktop config guncellendi: $claudeConfigPath" -ForegroundColor Green
    } catch {
        [System.IO.File]::WriteAllText($claudeConfigPath, $configContent, [System.Text.UTF8Encoding]::new($false))
        Write-Host "[OK] Claude Desktop config yeniden olusturuldu: $claudeConfigPath" -ForegroundColor Green
    }
} else {
    [System.IO.File]::WriteAllText($claudeConfigPath, $configContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "[OK] Claude Desktop config olusturuldu: $claudeConfigPath" -ForegroundColor Green
}

# Gemini CLI config
$geminiConfigDir = "$env:USERPROFILE\.gemini"
$geminiConfigPath = "$geminiConfigDir\settings.json"

if (-not (Test-Path $geminiConfigDir)) {
    New-Item -ItemType Directory -Path $geminiConfigDir -Force | Out-Null
}

if (Test-Path $geminiConfigPath) {
    try {
        $existing = Get-Content $geminiConfigPath -Raw | ConvertFrom-Json
        if (-not $existing.mcpServers) {
            $existing | Add-Member -MemberType NoteProperty -Name "mcpServers" -Value @{}
        }
        $existing.mcpServers | Add-Member -MemberType NoteProperty -Name "SiberSelma" -Value @{
            command = $pythonExe
            args    = @($serverPath)
        } -Force
        $json = $existing | ConvertTo-Json -Depth 5
        [System.IO.File]::WriteAllText($geminiConfigPath, $json, [System.Text.UTF8Encoding]::new($false))
        Write-Host "[OK] Gemini CLI config guncellendi: $geminiConfigPath" -ForegroundColor Green
    } catch {
        [System.IO.File]::WriteAllText($geminiConfigPath, $configContent, [System.Text.UTF8Encoding]::new($false))
        Write-Host "[OK] Gemini CLI config yeniden olusturuldu: $geminiConfigPath" -ForegroundColor Green
    }
} else {
    [System.IO.File]::WriteAllText($geminiConfigPath, $configContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "[OK] Gemini CLI config olusturuldu: $geminiConfigPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "Kurulum tamamlandi!" -ForegroundColor Cyan
Write-Host "Claude Desktop ve Gemini CLI'yi yeniden baslatın." -ForegroundColor Cyan
