@echo off
setlocal

:: Define proxy settings
set PROXY_SERVER=127.0.0.1:8080

:: Step 1: Download mitmproxy if it's not already installed
IF NOT EXIST "%ProgramFiles%\mitmproxy" (
    echo Downloading mitmproxy...
    curl -L https://snapshots.mitmproxy.org/10.0.0/mitmproxy-10.0.0-windows.zip -o mitmproxy.zip
    
    :: Check if download succeeded
    if not exist mitmproxy.zip (
        echo Failed to download mitmproxy. Exiting...
        exit /b 1
    )

    echo Extracting mitmproxy...
    tar -xf mitmproxy.zip

    :: Check if extraction succeeded
    if not exist mitmproxy (
        echo Failed to extract mitmproxy. Exiting...
        exit /b 1
    )

    :: Ensure the target directory exists
    if not exist "%ProgramFiles%\mitmproxy" (
        mkdir "%ProgramFiles%\mitmproxy"
    )

    move mitmproxy "%ProgramFiles%\mitmproxy"
)

:: Step 2: Install the mitmproxy certificate for HTTPS inspection
echo Installing mitmproxy certificate...
:: Convert .p12 to .pem (if needed)
openssl pkcs12 -in "%~dp0mitmproxy-ca-cert.p12" -out "%~dp0mitmproxy-ca-cert.pem" -nodes

:: Add the certificate to the trusted root store
certutil -addstore "Root" "%~dp0mitmproxy-ca-cert.pem"

IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install the mitmproxy certificate. Exiting...
    exit /b 1
)

:: Step 3: Set up proxy settings
echo Setting up proxy...
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /t REG_SZ /d %PROXY_SERVER% /f
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyOverride /t REG_SZ /d "<local>" /f

:: Optionally, set proxy for WinHTTP
echo Setting up proxy for WinHTTP...
netsh winhttp set proxy %PROXY_SERVER%

:: Step 4: Run mitmproxy with the Python script
echo Starting mitmproxy with the block_anime script...
cd /d "%ProgramFiles%\mitmproxy"
mitmproxy -s "%~dp0block.py"

:: Step 5: Keep the console open after execution
pause