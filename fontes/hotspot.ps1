# O Ponto de Acesso Movel do Windows, por linha de comando -- 24/09.
#
#   powershell -File fontes/hotspot.ps1 status     # {"ligado":..,"ssid":..,"senha":..,"clientes":..,"ip":..}
#   powershell -File fontes/hotspot.ps1 on
#   powershell -File fontes/hotspot.ps1 off
#
# POR QUE. No estande o Quest e este computador precisam se ver sem depender
# da rede de ninguem. O proprio Windows sabe fazer uma rede Wi-Fi (o "Ponto de
# acesso movel" das Configuracoes), mas so pela tela. Aqui e a mesma coisa pela
# API do sistema (WinRT), para a Cabine ligar e desligar com um botao.
#
# O QUE O WINDOWS EXIGE: uma conexao de rede de pe para "compartilhar" (Wi-Fi,
# cabo ou o modem 4G) -- nao precisa ter internet de verdade, mas precisa
# existir. Sem nenhuma, ele recusa, e a Cabine diz isso.
#
# Quem entra nessa rede ganha um ip 192.168.137.x; este computador e o .1.
# Responde sempre em JSON numa linha, para o Python ler.
#   powershell -File fontes/hotspot.ps1 config -ssid "Raizes Cosmicas" -senha "12345678"   (nome e senha da rede)
param([string]$acao = "status", [string]$ssid = "", [string]$senha = "")

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Networking.Connectivity.NetworkInformation, Windows.Networking.Connectivity, ContentType=WindowsRuntime]
[void][Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager, Windows.Networking.NetworkOperators, ContentType=WindowsRuntime]

# WinRT devolve promessas (IAsyncOperation); o PowerShell 5.1 nao sabe esperar
# por elas sozinho -- este e o jeito conhecido de converter em Task e esperar.
$asTaskGenerico = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Esperar($op, $tipo) {
    $asTask = $asTaskGenerico.MakeGenericMethod($tipo)
    $t = $asTask.Invoke($null, @($op)); $t.Wait(-1) | Out-Null; $t.Result
}

function Json($o) { ($o | ConvertTo-Json -Compress) }

# A conexao a compartilhar: a que tem internet; sem ela, qualquer uma de pe.
$perfil = [Windows.Networking.Connectivity.NetworkInformation]::GetInternetConnectionProfile()
if (-not $perfil) {
    $perfil = [Windows.Networking.Connectivity.NetworkInformation]::GetConnectionProfiles() |
        Where-Object { $_.GetNetworkConnectivityLevel() -ne 'None' } | Select-Object -First 1
}
if (-not $perfil) {
    Json @{ ligado = $false; erro = "sem nenhuma conexao de rede para compartilhar (ligue o Wi-Fi, o cabo ou o modem 4G)" }
    exit 0
}

# SEM PLACA WI-FI NAO HA REDE -- 24/09, no desktop: ele so tem cabo de rede
# (o servico de rede sem fio nem roda), e o Windows estourava uma excecao crua
# que a Cabine mostrava no lugar do estado. Agora a resposta e uma frase.
$semWifi = -not (Get-NetAdapter -ErrorAction SilentlyContinue | Where-Object {
    $_.PhysicalMediaType -match '802\.11|Wireless' -or $_.InterfaceDescription -match 'Wi-?Fi|Wireless|802\.11|WLAN' })
try {
    $g = [Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager]::CreateFromConnectionProfile($perfil)
} catch {
    if ($semWifi) {
        Json @{ ligado = $false; semWifi = $true; erro = "este computador nao tem Wi-Fi, entao nao cria a rede interna. Em casa nao precisa: o Quest e o computador ja estao na mesma rede do roteador. No estande: use um adaptador USB Wi-Fi, o modem/roteador, ou a Cabine no notebook" }
    } else {
        Json @{ ligado = $false; erro = "o Windows nao deixou criar a rede a partir de '$($perfil.ProfileName)': $($_.Exception.InnerException.Message)" }
    }
    exit 0
}
$tipoResultado = [Windows.Networking.NetworkOperators.NetworkOperatorTetheringOperationResult]

$erro = $null
if ($acao -eq "config") {
    # nome e senha da rede (a senha pede 8 caracteres ou mais); vale na proxima ligada
    $nova = $g.GetCurrentAccessPointConfiguration()
    if ($ssid) { $nova.Ssid = $ssid }
    if ($senha) { $nova.Passphrase = $senha }
    $asAction = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
        $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
        $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction' })[0]
    try { $t = $asAction.Invoke($null, @($g.ConfigureAccessPointAsync($nova))); $t.Wait(-1) | Out-Null }
    catch { $erro = "nao aceitou o nome/senha: $($_.Exception.InnerException.Message)" }
}
if ($acao -eq "on" -and $g.TetheringOperationalState -ne 'On') {
    $r = Esperar ($g.StartTetheringAsync()) $tipoResultado
    if ($r.Status -ne 'Success') { $erro = "nao ligou: $($r.Status) $($r.AdditionalErrorMessage)" }
} elseif ($acao -eq "off" -and $g.TetheringOperationalState -ne 'Off') {
    $r = Esperar ($g.StopTetheringAsync()) $tipoResultado
    if ($r.Status -ne 'Success') { $erro = "nao desligou: $($r.Status) $($r.AdditionalErrorMessage)" }
}

$cfg = $g.GetCurrentAccessPointConfiguration()
$ip = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
       Where-Object { $_.IPAddress -like '192.168.137.*' } | Select-Object -First 1).IPAddress
Json @{
    ligado   = ($g.TetheringOperationalState -eq 'On')
    estado   = "$($g.TetheringOperationalState)"
    ssid     = $cfg.Ssid
    senha    = $cfg.Passphrase
    clientes = $g.ClientCount
    ip       = $ip
    compartilha = $perfil.ProfileName
    erro     = $erro
}
