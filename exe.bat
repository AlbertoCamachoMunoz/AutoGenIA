@echo off
REM === Paso 1: Crear entorno virtual venv ===
IF NOT EXIST "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

REM === Paso 2: Activar entorno y instalar dependencias ===
echo Activando entorno virtual...
call venv\Scripts\activate

echo Instalando dependencias...
pip install -r requirements.txt


REM === Paso 3: Iniciar backend Flask en segundo plano ===
start "" cmd /k "call venv\Scripts\activate && python -m presentation.api"

REM Esperar 1 segundo para que arranque el servidor Flask
timeout /t 1 >nul

REM === Paso 3: Abrir navegador con la app (Flask frontend) ===
start "" http://127.0.0.1:5000

REM === Paso 4: Comprobar si el servidor LLM responde en localhost:1234 ===

REM Usar curl (disponible en Windows 10+), si no existe, mostrar aviso
where curl >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [AVISO] curl no está instalado. No se puede comprobar la URL http://localhost:1234/v1/models
    goto :EOF
)

echo.
echo Comprobando disponibilidad del servidor LLM (http://localhost:1234/v1/models)...
curl --silent --head http://localhost:1234/v1/models >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ******************************************************
    echo  [ERROR] El servidor LLM (http://localhost:1234) NO responde.
    echo  - El servidor puede estar apagado.
    echo  - La dirección/puerto puede ser incorrecto.
    echo  - Modifíquelo en el fichero AutoGenIA/config/settings.py
    echo ******************************************************
    pause
) else (
    echo OK - Servidor LLM detectado en http://localhost:1234/v1/models
)

REM (opcional) Desactivar entorno virtual al finalizar
REM deactivate
