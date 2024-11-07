@echo off
setlocal

rem 检查是否存在 .venv 目录，并设置 Python 解释器
if exist .venv (
    set "PYTHON_CMD=.venv\Scripts\python"
) else (
    set "PYTHON_CMD=python"
)

rem 提示用户选择验证方式
echo 请选择验证方式：
echo 1. 二维码验证
echo 2. 手动验证
set /p choice=输入选项 (1 或 2): 

if "%choice%"=="1" (
    rem 二维码验证
    set /p qr_path=请输入二维码图像的路径(绝对路径，将图像拖入命令行即可): 
    set qr_path=%qr_path:"=%
    %PYTHON_CMD% verify.py -q "%qr_path%"
) else if "%choice%"=="2" (
    rem 手动验证
    set /p message=消息: 
    set /p hash_value=哈希值: 
    set /p signature=签名: 
    %PYTHON_CMD% verify.py -m "%message%" -hv "%hash_value%" -s "%signature%"
) else (
    echo 无效的选项
    exit /b 1
)

endlocal