$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$taskPython = (Get-Command python -ErrorAction Stop).Source
$taskPort = 4173
$taskUrl = "http://127.0.0.1:$taskPort/zh-hant/"
$taskExisting = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $taskPort -State Listen -ErrorAction SilentlyContinue
if (-not $taskExisting) {
    Start-Process -FilePath $taskPython -ArgumentList @('-m','http.server',"$taskPort",'--bind','127.0.0.1','--directory','dist') -WorkingDirectory $taskRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $taskRoot 'preview-output.log') -RedirectStandardError (Join-Path $taskRoot 'preview-error.log')
    Start-Sleep -Milliseconds 800
}
Start-Process $taskUrl
