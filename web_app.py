from flask import Flask, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
import bilibili_draw as bd
from Crypto.PublicKey import RSA
import traceback
import numpy as np
import verify  # 导入现有的verify模块
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 最大文件限制

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('qr_code', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_keys', methods=['POST'])
def generate_keys():
    try:
        key = RSA.generate(2048)
        private_key = key.export_key("PEM").decode()
        public_key = key.publickey().export_key("PEM").decode()
            
        return jsonify({
            'success': True,
            'privateKey': private_key,
            'publicKey': public_key,
            'message': '密钥对生成成功！'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'生成密钥失败: {str(e)}'
        })

@app.route('/draw', methods=['POST'])
def draw():
    try:
        data = request.form
        num = int(data.get('num', 1))
        bv = data.get('bv')
        qualification = data.get('qualification') == 'true'
        uid = data.get('uid')
        
        # 处理CSV文件上传
        csv_file = None
        if 'csv_file' in request.files:
            file = request.files['csv_file']
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                csv_file = filepath

        # 处理私钥文件上传
        key_path = "private_key.pem"
        if 'private_key' in request.files:
            file = request.files['private_key']
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                key_path = filepath

        csv_file, qr_path, winners = bd.run(
            num=num,
            key_path=key_path,
            file=csv_file,
            bv_number=bv,
            qualification=qualification,
            uid=uid
        )

        # 将 winners 中的所有值转换为普通 Python 类型
        winners = [int(w) if isinstance(w, (np.int64, np.int32)) else w for w in winners]

        return jsonify({
            'success': True,
            'qr_path': qr_path,
            'winners': winners,
            'csv_path': csv_file
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/qr_code/<path:filename>')
def serve_qr(filename):
    return send_file(f'qr_code/{filename}')

@app.route('/verify', methods=['POST'])
def verify_draw():
    try:
        data = request.form
        verification_type = data.get('type')
        
        # 处理公钥文件上传
        if 'public_key' in request.files:
            file = request.files['public_key']
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                # 将文件复制为 public_key.pem（因为verify.py中默认使用这个文件名）
                shutil.copy(filepath, "public_key.pem")
        
        if verification_type == 'qr':
            if 'qr_file' not in request.files:
                return jsonify({
                    'success': False,
                    'message': '未找到二维码文件'
                })
                
            file = request.files['qr_file']
            if not file.filename:
                return jsonify({
                    'success': False,
                    'message': '未选择文件'
                })
                
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # 只传入 qr_code 参数
            result = verify.main(qr_code=filepath)
            
        else:  # 手动验证
            message = data.get('message')
            hash_value = data.get('hash_value')
            signature = data.get('signature')
            
            if not all([message, hash_value, signature]):
                return jsonify({
                    'success': False,
                    'message': '请提供完整的验证信息'
                })
                
            # 传入手动验证所需的参数
            result = verify.main(
                message=message,
                hash_value=hash_value,
                signature=signature
            )
            
        return jsonify({
            'success': True,
            'verified': result
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/download_csv/<filename>')
def download_csv(filename):
    try:
        return send_file(
            f'list/{filename}',
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'下载文件失败: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True) 