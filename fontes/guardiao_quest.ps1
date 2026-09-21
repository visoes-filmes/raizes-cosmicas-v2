# Registra o guardiao do Quest para subir sozinho a cada logon do Windows
# (sem janela). Rodar uma vez, no PowerShell:  .\fontes\guardiao_quest.ps1
# Para tirar:  Unregister-ScheduledTask -TaskName "Guardiao do Quest" -Confirm:$false
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = (Get-Command python).Source
$acao = New-ScheduledTaskAction -Execute $py -Argument "`"$aqui\guardiao_quest.py`"" -WorkingDirectory (Split-Path -Parent $aqui)
$gatilho = New-ScheduledTaskTrigger -AtLogOn
$ajustes = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 99 -RestartInterval (New-TimeSpan -Minutes 1) -Hidden
Register-ScheduledTask -TaskName "Guardiao do Quest" -Action $acao -Trigger $gatilho -Settings $ajustes -Force | Out-Null
Start-ScheduledTask -TaskName "Guardiao do Quest"
Write-Host "Guardiao do Quest registrado e de pe. Registro: $aqui\guardiao_quest.log"
