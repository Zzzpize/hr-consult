@echo off
setlocal

for %%* in (.) do set PROJECT_NAME=%%~n*
set VOLUME_NAME=%PROJECT_NAME%_redis-data
set BACKUP_FILE=redis-backup.tar.gz

echo =============================================
echo  Redis Backup Script
echo =============================================
echo Проект: %PROJECT_NAME%
echo Том с данными: %VOLUME_NAME%
echo Файл бэкапа: %BACKUP_FILE%
echo.

docker volume inspect "%VOLUME_NAME%" > nul 2>&1
if errorlevel 1 (
    echo [X] Ошибка: Том '%VOLUME_NAME%' не найден. Убедитесь, что приложение было запущено хотя бы раз.
    goto :eof
)

echo [~] Создание бэкапа... (Это может занять несколько секунд)

docker run --rm -v "%VOLUME_NAME%:/volume" -v "%cd%:/backup" ubuntu tar -czvf "/backup/%BACKUP_FILE%" -C /volume .

if exist "%BACKUP_FILE%" (
    echo [V] Успешно! Бэкап сохранен в файл: %cd%\%BACKUP_FILE%
) else (
    echo [X] Ошибка: Не удалось создать файл бэкапа.
)

echo =============================================
endlocal