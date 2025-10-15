# Create Desktop Shortcut for Veleron Voice Flow

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Veleron Voice Flow.lnk"
$targetPath = Join-Path $scriptPath "Launch_Voice_Flow.bat"
$iconPath = "C:\Windows\System32\imageres.dll,190"

$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.WorkingDirectory = $scriptPath
$shortcut.IconLocation = $iconPath
$shortcut.Description = "Veleron Voice Flow - AI Voice Transcription"
$shortcut.Save()

Write-Host "Desktop shortcut created successfully at: $shortcutPath"
