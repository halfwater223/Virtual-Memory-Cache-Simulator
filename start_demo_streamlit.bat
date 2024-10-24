REM Author: Yinxuan Wu, Xiaohao Xia, Junfei Zhang
@echo off

REM Check if the VMsimulator environment exists
echo Checking for the conda environment 'VMsimulator'...
conda env list | findstr /C:"VMsimulator"
IF %ERRORLEVEL% NEQ 0 (
    echo 'VMsimulator' environment not found. Creating now...
    conda env create -f environment.yml
    IF %ERRORLEVEL% NEQ 0 (
        echo Failed to create the environment.
        pause
        exit /b %ERRORLEVEL%
    )
)

REM Activate the environment
echo Activating the 'VMsimulator' environment...
CALL activate VMsimulator
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to activate the environment.
    pause
    exit /b %ERRORLEVEL%
)

REM Run the Streamlit application
echo Running the Streamlit application...
streamlit run demo_streamlit.py
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to run the Streamlit application.
    pause
    exit /b %ERRORLEVEL%
)

echo Script completed successfully.
pause
