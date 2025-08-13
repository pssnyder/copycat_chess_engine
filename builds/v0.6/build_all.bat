@echo off
REM Master build script for all Copycat Chess Engine versions
REM This script builds all engine versions for Arena chess GUI compatibility

echo ========================================
echo COPYCAT CHESS ENGINE - MASTER BUILD
echo ========================================
echo.
echo This script will build all engine versions:
echo - v0.1 Copycat AI
echo - v0.2 Copycat Evaluation AI  
echo - v0.3 Copycat Enhanced AI
echo - v0.4 Copycat Genetic AI
echo - v0.5 BETA
echo.

set BUILD_ROOT=%~dp0builds
set SUCCESS_COUNT=0
set TOTAL_COUNT=5

echo Starting build process...
echo.

REM Build v0.1
echo ========================================
echo Building v0.1 Copycat AI
echo ========================================
cd "%BUILD_ROOT%\v0.1_copycat_ai"
if exist build.bat (
    call build.bat
    if exist "release\CopycatChessEngine_v0.1.exe" (
        echo [SUCCESS] v0.1 build completed
        set /a SUCCESS_COUNT+=1
    ) else (
        echo [FAILED] v0.1 build failed
    )
) else (
    echo [ERROR] Build script not found for v0.1
)
echo.

REM Build v0.2
echo ========================================
echo Building v0.2 Copycat Evaluation AI
echo ========================================
cd "%BUILD_ROOT%\v0.2_copycat_eval_ai"
if exist build.bat (
    call build.bat
    if exist "release\CopycatChessEngine_v0.2_Eval.exe" (
        echo [SUCCESS] v0.2 build completed
        set /a SUCCESS_COUNT+=1
    ) else (
        echo [FAILED] v0.2 build failed
    )
) else (
    echo [ERROR] Build script not found for v0.2
)
echo.

REM Build v0.3
echo ========================================
echo Building v0.3 Copycat Enhanced AI
echo ========================================
cd "%BUILD_ROOT%\v0.3_copycat_enhanced_ai"
if exist build.bat (
    call build.bat
    if exist "release\CopycatChessEngine_v0.3_Enhanced.exe" (
        echo [SUCCESS] v0.3 build completed
        set /a SUCCESS_COUNT+=1
    ) else (
        echo [FAILED] v0.3 build failed
    )
) else (
    echo [ERROR] Build script not found for v0.3
)
echo.

REM Build v0.4
echo ========================================
echo Building v0.4 Copycat Genetic AI
echo ========================================
cd "%BUILD_ROOT%\v0.4_copycat_genetic_ai"
if exist build.bat (
    call build.bat
    if exist "release\CopycatChessEngine_v0.4_Genetic.exe" (
        echo [SUCCESS] v0.4 build completed
        set /a SUCCESS_COUNT+=1
    ) else (
        echo [FAILED] v0.4 build failed
    )
) else (
    echo [ERROR] Build script not found for v0.4
)
echo.

REM Build v0.5
echo ========================================
echo Building v0.5 BETA
echo ========================================
cd "%BUILD_ROOT%\v0.5_BETA"
if exist build.bat (
    call build.bat
    if exist "release\CopycatChessEngine_v0.5_BETA.exe" (
        echo [SUCCESS] v0.5 BETA build completed
        set /a SUCCESS_COUNT+=1
    ) else (
        echo [FAILED] v0.5 BETA build failed
    )
) else (
    echo [ERROR] Build script not found for v0.5 BETA
)
echo.

REM Build summary
echo ========================================
echo BUILD SUMMARY
echo ========================================
echo Successful builds: %SUCCESS_COUNT% out of %TOTAL_COUNT%
echo.

if %SUCCESS_COUNT%==%TOTAL_COUNT% (
    echo ALL BUILDS COMPLETED SUCCESSFULLY!
    echo.
    echo Executable locations:
    echo - v0.1: builds\v0.1_copycat_ai\release\CopycatChessEngine_v0.1.exe
    echo - v0.2: builds\v0.2_copycat_eval_ai\release\CopycatChessEngine_v0.2_Eval.exe  
    echo - v0.3: builds\v0.3_copycat_enhanced_ai\release\CopycatChessEngine_v0.3_Enhanced.exe
    echo - v0.4: builds\v0.4_copycat_genetic_ai\release\CopycatChessEngine_v0.4_Genetic.exe
    echo - v0.5: builds\v0.5_BETA\release\CopycatChessEngine_v0.5_BETA.exe
    echo.
    echo Ready for Arena chess GUI testing!
    echo.
    echo To test with Arena:
    echo 1. Copy the desired .exe to your Arena engines folder
    echo 2. Add engine in Arena with UCI protocol
    echo 3. Select the .exe file as the engine path
) else (
    echo Some builds failed. Check the output above for details.
    echo You may need to ensure all required model files are present.
)

echo.
echo ========================================
echo Build process completed.
echo ========================================
pause
