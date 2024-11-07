export DYLD_LIBRARY_PATH=$(brew --prefix zbar)/lib:$DYLD_LIBRARY_PATH
source ~/.bash_profile

# 检查是否激活了 Conda 环境并设置 Python 解释器
if [ -n "$CONDA_PREFIX" ]; then
    # 使用当前激活的 Conda 环境中的 Python
    PYTHON_CMD="$CONDA_PREFIX/bin/python"
    echo "Conda 环境已激活，$PYTHON_CMD"
elif [ -d ".venv" ]; then
    # 使用 .venv 中的 Python
    PYTHON_CMD=".venv/bin/python"
else
    # 使用系统默认的 Python
    PYTHON_CMD="python"
fi

# 提示用户选择验证方式
echo "请选择验证方式："
echo "1. 二维码验证"
echo "2. 手动验证"
read -p "输入选项 (1 或 2): " choice

if [ "$choice" == "1" ]; then
    # 二维码验证
    read -p "请输入二维码图像的路径(绝对路径，将图像拖入命令行即可): " qr_path
    qr_path=$(echo $qr_path | sed 's/^["'\'']\(.*\)["'\'']$/\1/')
    $PYTHON_CMD verify.py -q "$qr_path"
elif [ "$choice" == "2" ]; then
    # 手动验证
    read -p "消息: " message
    read -p "哈希值: " hash_value
    read -p "签名: " signature
    $PYTHON_CMD verify.py -m "$message" -hv "$hash_value" -s "$signature"
else
    echo "无效的选项"
    exit 1
fi