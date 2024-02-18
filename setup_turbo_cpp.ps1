Invoke-WebRequest -Uri 'https://github.com/taaaf11/turbo-c--for-download/raw/main/TURBOC3.zip' -OutFile 'TURBOC3.zip'
Expand-Archive -Path 'TURBOC3.zip' -DestinationPath 'TURBOC3'

Set-Location -Path "$Env:localappdata\DOSBox"

Get-Content 'dosbox*.conf' > dosbox_conf.bak

