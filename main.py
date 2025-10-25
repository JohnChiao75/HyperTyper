import sys
import json
import time
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QListWidget, QPushButton, QWidget, QMessageBox, 
    QInputDialog, QLineEdit, QLabel, QSpinBox, QDialog,
    QDialogButtonBox, QFormLayout, QTextEdit
)
from PyQt6.QtCore import QTimer, pyqtSignal, QThread
import win32api
import win32con

# 虚拟键码映射表
VK_CODE = {
    # 字符键
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    
    # 字母键 (A-Z)
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
    'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
    'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
    'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
    'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,
    
    # 大写字母键
    'A': 0x41, 'B': 0x42, 'C': 0x43, 'D': 0x44, 'E': 0x45,
    'F': 0x46, 'G': 0x47, 'H': 0x48, 'I': 0x49, 'J': 0x4A,
    'K': 0x4B, 'L': 0x4C, 'M': 0x4D, 'N': 0x4E, 'O': 0x4F,
    'P': 0x50, 'Q': 0x51, 'R': 0x52, 'S': 0x53, 'T': 0x54,
    'U': 0x55, 'V': 0x56, 'W': 0x57, 'X': 0x58, 'Y': 0x59, 'Z': 0x5A,
    
    # 功能键
    'enter': win32con.VK_RETURN,
    'esc': win32con.VK_ESCAPE,
    'space': win32con.VK_SPACE,
    'tab': win32con.VK_TAB,
    'backspace': win32con.VK_BACK,
    'delete': win32con.VK_DELETE,
    'insert': win32con.VK_INSERT,
    'home': win32con.VK_HOME,
    'end': win32con.VK_END,
    'pageup': win32con.VK_PRIOR,
    'pagedown': win32con.VK_NEXT,
    
    # 方向键
    'up': win32con.VK_UP,
    'down': win32con.VK_DOWN,
    'left': win32con.VK_LEFT,
    'right': win32con.VK_RIGHT,
    
    # 控制键
    'ctrl': win32con.VK_CONTROL,
    'alt': win32con.VK_MENU,
    'shift': win32con.VK_SHIFT,
    'win': win32con.VK_LWIN,
    
    # 锁定键
    'capslock': win32con.VK_CAPITAL,
    'numlock': win32con.VK_NUMLOCK,
    'scrolllock': win32con.VK_SCROLL,
    
    # F1-F12
    'f1': win32con.VK_F1, 'f2': win32con.VK_F2, 'f3': win32con.VK_F3,
    'f4': win32con.VK_F4, 'f5': win32con.VK_F5, 'f6': win32con.VK_F6,
    'f7': win32con.VK_F7, 'f8': win32con.VK_F8, 'f9': win32con.VK_F9,
    'f10': win32con.VK_F10, 'f11': win32con.VK_F11, 'f12': win32con.VK_F12,
}

class KeySimulatorThread(QThread):
    """按键模拟线程，避免阻塞GUI"""
    finished = pyqtSignal()
    progress = pyqtSignal(int, int)  # 当前步骤，总步骤
    
    def __init__(self, key_array, delay=0.1):
        super().__init__()
        self.key_array = key_array
        self.delay = delay
        self.is_running = True
        
    def run(self):
        """执行按键模拟"""
        total_steps = len(self.key_array)
        
        for i, item in enumerate(self.key_array):
            if not self.is_running:
                break
                
            self.progress.emit(i + 1, total_steps)
            
            if isinstance(item, list):
                # 处理组合键
                self.press_key_combination(item)
            elif isinstance(item, str):
                if len(item) == 1:
                    # 单个字符键
                    self.press_key(VK_CODE[item])
                else:
                    # 特殊功能键
                    if item in VK_CODE:
                        self.press_key(VK_CODE[item])
            time.sleep(self.delay)
            
        self.finished.emit()
    
    def stop(self):
        """停止执行"""
        self.is_running = False
        
    def press_key(self, vk_code):
        """按下并释放单个键"""
        win32api.keybd_event(vk_code, 0, 0, 0)  # 按下键
        time.sleep(0.05)
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放键

    def press_key_combination(self, keys):
        """按下组合键（如Ctrl+C）"""
        # 先按下所有修饰键（Ctrl、Alt、Shift）
        for key in keys[:-1]:
            vk_code = VK_CODE[key]
            win32api.keybd_event(vk_code, 0, 0, 0)
            time.sleep(0.05)
        
        # 按下并释放最后一个键
        last_key_vk = VK_CODE[keys[-1]]
        win32api.keybd_event(last_key_vk, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(last_key_vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        # 释放所有修饰键（逆序）
        for key in reversed(keys[:-1]):
            vk_code = VK_CODE[key]
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)


class ScriptEditDialog(QDialog):
    """脚本编辑对话框"""
    def __init__(self, parent=None, script_name="", script_data=None):
        super().__init__(parent)
        self.script_name = script_name
        self.script_data = script_data or []
        
        self.setWindowTitle("编辑脚本")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # 脚本名称
        form_layout = QFormLayout()
        self.name_edit = QLineEdit(script_name)
        form_layout.addRow("脚本名称:", self.name_edit)
        layout.addLayout(form_layout)
        
        # 脚本内容
        layout.addWidget(QLabel("脚本内容 (每行一个按键或组合键):"))
        self.script_edit = QTextEdit()
        self.script_edit.setPlaceholderText(
            "输入按键，每行一个:\n"
            "- 单个按键: a, b, 1, 2, enter, space\n"
            "- 组合键: [\"ctrl\", \"c\"], [\"alt\", \"tab\"]\n\n"
            "示例:\n"
            "a\n"
            "b\n"
            "c\n"
            "[\"ctrl\", \"c\"]\n"
            "[\"ctrl\", \"v\"]"
        )
        
        # 如果已有数据，填充到编辑框
        if self.script_data:
            script_text = ""
            for item in self.script_data:
                if isinstance(item, list):
                    script_text += str(item) + "\n"
                else:
                    script_text += item + "\n"
            self.script_edit.setPlainText(script_text.strip())
            
        layout.addWidget(self.script_edit)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_script_data(self):
        """获取脚本数据"""
        script_name = self.name_edit.text().strip()
        script_text = self.script_edit.toPlainText().strip()
        
        # 解析脚本内容
        script_data = []
        for line in script_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # 尝试解析组合键
            if line.startswith('[') and line.endswith(']'):
                try:
                    # 使用eval解析列表，注意安全风险
                    key_list = eval(line)
                    if isinstance(key_list, list):
                        script_data.append(key_list)
                    else:
                        QMessageBox.warning(self, "错误", f"无效的组合键格式: {line}")
                        return None, None
                except:
                    QMessageBox.warning(self, "错误", f"无效的组合键格式: {line}")
                    return None, None
            else:
                # 单个按键
                script_data.append(line)
                
        return script_name, script_data


class KeySimulatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scripts = {}  # 存储脚本 {名称: 按键数组}
        self.current_thread = None  # 当前执行线程
        
        self.init_ui()
        self.load_scripts()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("按键模拟器")
        self.setGeometry(100, 100, 600, 500)
        
        # 中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("HyperTyper 脚本管理")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # 脚本列表
        layout.addWidget(QLabel("脚本列表:"))
        self.script_list = QListWidget()
        self.script_list.itemDoubleClicked.connect(self.edit_script)
        layout.addWidget(self.script_list)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.new_btn = QPushButton("新建")
        self.new_btn.clicked.connect(self.new_script)
        button_layout.addWidget(self.new_btn)
        
        self.edit_btn = QPushButton("编辑")
        self.edit_btn.clicked.connect(self.edit_script)
        button_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self.delete_script)
        button_layout.addWidget(self.delete_btn)
        
        self.execute_btn = QPushButton("执行 (5秒后)")
        self.execute_btn.clicked.connect(self.execute_script)
        self.execute_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        button_layout.addWidget(self.execute_btn)
        
        layout.addLayout(button_layout)
        
        # 执行进度
        self.progress_label = QLabel("准备就绪")
        layout.addWidget(self.progress_label)
        
        # 停止按钮
        self.stop_btn = QPushButton("停止执行")
        self.stop_btn.clicked.connect(self.stop_execution)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white;")
        layout.addWidget(self.stop_btn)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
    def load_scripts(self):
        """从文件加载脚本"""
        try:
            with open("scripts.json", "r") as f:
                self.scripts = json.load(f)
            self.update_script_list()
        except FileNotFoundError:
            # 文件不存在，使用默认脚本
            self.scripts = {
                "示例1": ["a", "b", "c", "enter"],
                "示例2": [["ctrl", "c"], ["ctrl", "v"]],
                "示例3": ["h", "e", "l", "l", "o", "space", "w", "o", "r", "l", "d"]
            }
            self.save_scripts()
            self.update_script_list()
    
    def save_scripts(self):
        """保存脚本到文件"""
        with open("scripts.json", "w") as f:
            json.dump(self.scripts, f, indent=2)
    
    def update_script_list(self):
        """更新脚本列表显示"""
        self.script_list.clear()
        for name in self.scripts:
            self.script_list.addItem(name)
    
    def new_script(self):
        """新建脚本"""
        dialog = ScriptEditDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, data = dialog.get_script_data()
            if name and data:
                if name in self.scripts:
                    QMessageBox.warning(self, "错误", f"脚本 '{name}' 已存在!")
                    return
                    
                self.scripts[name] = data
                self.save_scripts()
                self.update_script_list()
                self.statusBar().showMessage(f"已创建脚本: {name}")
    
    def edit_script(self):
        """编辑脚本"""
        current_item = self.script_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个脚本!")
            return
            
        old_name = current_item.text()
        dialog = ScriptEditDialog(self, old_name, self.scripts[old_name])
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name, new_data = dialog.get_script_data()
            if new_name and new_data:
                # 删除旧脚本，添加新脚本
                del self.scripts[old_name]
                self.scripts[new_name] = new_data
                self.save_scripts()
                self.update_script_list()
                self.statusBar().showMessage(f"已更新脚本: {new_name}")
    
    def delete_script(self):
        """删除脚本"""
        current_item = self.script_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个脚本!")
            return
            
        name = current_item.text()
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除脚本 '{name}' 吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.scripts[name]
            self.save_scripts()
            self.update_script_list()
            self.statusBar().showMessage(f"已删除脚本: {name}")
    
    def execute_script(self):
        """执行脚本（5秒后）"""
        current_item = self.script_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个脚本!")
            return
        
        if self.current_thread and self.current_thread.isRunning():
            QMessageBox.warning(self, "警告", "已有脚本正在执行，请等待完成!")
            return
            
        name = current_item.text()
        script_data = self.scripts[name]
        
        # 显示倒计时
        self.statusBar().showMessage(f"5秒后开始执行脚本: {name}")
        self.execute_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # 使用QTimer实现倒计时
        self.countdown = 5
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.countdown_execute(name, script_data))
        self.timer.start(1000)  # 每秒触发一次
    
    def countdown_execute(self, name, script_data):
        """倒计时执行"""
        self.countdown -= 1
        self.statusBar().showMessage(f"{self.countdown}秒后开始执行脚本: {name}")
        
        if self.countdown <= 0:
            self.timer.stop()
            self.start_execution(script_data, name)
    
    def start_execution(self, script_data, name):
        """开始执行脚本"""
        self.statusBar().showMessage(f"正在执行脚本: {name}")
        
        # 创建并启动执行线程
        self.current_thread = KeySimulatorThread(script_data)
        self.current_thread.finished.connect(self.execution_finished)
        self.current_thread.progress.connect(self.update_progress)
        self.current_thread.start()
    
    def update_progress(self, current, total):
        """更新执行进度"""
        self.progress_label.setText(f"执行进度: {current}/{total}")
    
    def execution_finished(self):
        """执行完成"""
        self.statusBar().showMessage("脚本执行完成")
        self.progress_label.setText("准备就绪")
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.current_thread = None
    
    def stop_execution(self):
        """停止执行"""
        if self.current_thread and self.current_thread.isRunning():
            self.current_thread.stop()
            self.current_thread.wait(1000)  # 等待线程结束
            
        self.statusBar().showMessage("执行已停止")
        self.progress_label.setText("准备就绪")
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # 如果倒计时中，停止计时器
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KeySimulatorGUI()
    window.show()
    sys.exit(app.exec())