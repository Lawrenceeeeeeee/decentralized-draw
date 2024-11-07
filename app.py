from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                           QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                           QLineEdit, QSpinBox, QCheckBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import sys
import os
import pandas as pd
from src import get_comments as gc
from src import allowed_users as au
import bilibili_draw as bd
import verify as vr
from Crypto.PublicKey import RSA
from PIL.ImageQt import ImageQt

class LotteryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bilibili 去中心化抽奖系统")
        self.setMinimumWidth(800)
        
        # 创建标签页
        tabs = QTabWidget()
        tabs.addTab(self.create_key_tab(), "密钥生成")
        tabs.addTab(self.create_draw_tab(), "抽奖")
        tabs.addTab(self.create_verify_tab(), "验证")
        
        self.setCentralWidget(tabs)

    def create_key_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        gen_btn = QPushButton("生成新的密钥对")
        gen_btn.clicked.connect(self.generate_keys)
        
        self.key_status = QLabel("尚未生成密钥")
        
        layout.addWidget(gen_btn)
        layout.addWidget(self.key_status)
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_draw_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 输入区域
        form_layout = QVBoxLayout()
        
        # 私钥选择
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("私钥文件:"))
        self.private_key_path = QLineEdit()
        key_layout.addWidget(self.private_key_path)
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(lambda: self.browse_file("private"))
        key_layout.addWidget(browse_btn)
        form_layout.addLayout(key_layout)
        
        # CSV 文件选择
        csv_layout = QHBoxLayout()
        csv_layout.addWidget(QLabel("CSV文件:"))
        self.csv_path = QLineEdit()
        csv_layout.addWidget(self.csv_path)
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(lambda: self.browse_file("csv"))
        csv_layout.addWidget(browse_btn)
        form_layout.addLayout(csv_layout)
        
        # BV号输入
        bv_layout = QHBoxLayout()
        bv_layout.addWidget(QLabel("BV号:"))
        self.bv_input = QLineEdit()
        bv_layout.addWidget(self.bv_input)
        form_layout.addLayout(bv_layout)
        
        # 抽取数量
        num_layout = QHBoxLayout()
        num_layout.addWidget(QLabel("抽取数量:"))
        self.num_input = QSpinBox()
        self.num_input.setMinimum(1)
        num_layout.addWidget(self.num_input)
        form_layout.addLayout(num_layout)
        
        # 资格检测
        self.check_qualification = QCheckBox("检测资格")
        self.uid_input = QLineEdit()
        self.uid_input.setPlaceholderText("你的UID(检测资格时需要)")
        form_layout.addWidget(self.check_qualification)
        form_layout.addWidget(self.uid_input)
        
        layout.addLayout(form_layout)
        
        # 执行按钮
        draw_btn = QPushButton("开始抽奖")
        draw_btn.clicked.connect(self.perform_draw)
        layout.addWidget(draw_btn)
        
        # 结果显示区
        self.result_label = QLabel()
        self.qr_label = QLabel()
        layout.addWidget(self.result_label)
        layout.addWidget(self.qr_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_verify_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 公钥选择
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("公钥文件:"))
        self.public_key_path = QLineEdit()
        key_layout.addWidget(self.public_key_path)
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(lambda: self.browse_file("public"))
        key_layout.addWidget(browse_btn)
        
        # QR码选择
        qr_layout = QHBoxLayout()
        qr_layout.addWidget(QLabel("二维码文件:"))
        self.qr_path = QLineEdit()
        qr_layout.addWidget(self.qr_path)
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(lambda: self.browse_file("qr"))
        qr_layout.addWidget(browse_btn)
        
        verify_btn = QPushButton("验证")
        verify_btn.clicked.connect(self.verify_result)
        
        self.verify_result_label = QLabel()
        
        layout.addLayout(key_layout)
        layout.addLayout(qr_layout)
        layout.addWidget(verify_btn)
        layout.addWidget(self.verify_result_label)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def generate_keys(self):
        try:
            key = RSA.generate(2048)
            
            # 保存私钥
            with open("private_key.pem", "wb") as f:
                f.write(key.export_key("PEM"))
            
            # 保存公钥
            with open("public_key.pem", "wb") as f:
                f.write(key.publickey().export_key("PEM"))
                
            self.key_status.setText("密钥对已生成: \n私钥: private_key.pem\n公钥: public_key.pem")
        except Exception as e:
            self.key_status.setText(f"生成密钥失败: {str(e)}")

    def browse_file(self, file_type):
        file_path, _ = QFileDialog.getOpenFileName(self)
        if file_path:
            if file_type == "private":
                self.private_key_path.setText(file_path)
            elif file_type == "public":
                self.public_key_path.setText(file_path)
            elif file_type == "qr":
                self.qr_path.setText(file_path)

    def perform_draw(self):
        try:
            # 验证必要输入
            if not self.private_key_path.text():
                raise ValueError("请选择私钥文件")
            if not self.num_input.value():
                raise ValueError("请输入抽取数量")
            
            # 判断是否输入了 CSV 文件
            if self.csv_path.text():
                file = self.csv_path.text()
                df = pd.read_csv(file)
            else:
                if not self.bv_input.text():
                    raise ValueError("请输入BV号")
                bv = self.bv_input.text()
                df = gc.get_full_comments('1', bv)
            
            # 如果需要筛选资格
            if self.check_qualification.isChecked():
                if not self.uid_input.text():
                    raise ValueError("启用资格检测时需要填写UID")
                uid = int(self.uid_input.text())
                df = au.extract_allowed_comments(df, uid)
            
            qr_path, winner = bd.run(
                self.num_input.value(), 
                file=self.csv_path.text(),
                bv_number=self.bv_input.text(),
                qualification=self.check_qualification.isChecked(),
                uid=int(self.uid_input.text())
            )
            
            # 显示二维码
            pixmap = QPixmap(qr_path)
            scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
            self.qr_label.setPixmap(scaled_pixmap)
            
            # 显示中奖者
            self.result_label.setText(f"中奖者UID: {', '.join(map(str, winner))}")
            
        except Exception as e:
            self.result_label.setText(f"抽奖失败: {str(e)}")
            self.qr_label.clear()

    def verify_result(self):
        # 这里调用verify.py中的相关功能
        try:
            vr.main(
                qr_code=self.qr_path.text(),
                message=None,
                hash_value=None,
                signature=None
            )
        except Exception as e:
            self.verify_result_label.setText(f"验证失败: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LotteryApp()
    window.show()
    sys.exit(app.exec())