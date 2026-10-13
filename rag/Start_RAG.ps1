$ErrorActionPreference = 'Stop'
$taskPython = Get-Command python -ErrorAction SilentlyContinue
$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (Test-Path -LiteralPath $bundledPython) { $taskPythonPath = $bundledPython }
elseif ($taskPython) { $taskPythonPath = $taskPython.Source }
else { throw 'Install Python 3.10 or later to start this app.' }
Write-Host 'Open http://127.0.0.1:8765 in your browser. Press Ctrl+C here to stop.'
& $taskPythonPath (Join-Path $PSScriptRoot 'server.py')
