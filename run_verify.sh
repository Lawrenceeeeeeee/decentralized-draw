export DYLD_LIBRARY_PATH=$(brew --prefix zbar)/lib:$DYLD_LIBRARY_PATH
source ~/.bash_profile

# 提示用户选择验证方式
echo "请选择验证方式："
echo "1. 二维码验证"
echo "2. 手动验证"
read -p "输入选项 (1 或 2): " choice

if [ "$choice" == "1" ]; then
    # 二维码验证
    read -p "请输入二维码图像的路径: " qr_path
    qr_path=$(echo $qr_path | sed 's/^["'\'']\(.*\)["'\'']$/\1/')
    python verify.py -q "$qr_path"
elif [ "$choice" == "2" ]; then
    # 手动验证
    read -p "消息: " message
    read -p "哈希值: " hash_value
    read -p "签名: " signature
    python verify.py -m "$message" -hv "$hash_value" -s "$signature"
else
    echo "无效的选项"
    exit 1
fi