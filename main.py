import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import threading
import json
import os
import requests
import tempfile
import sys
import winreg

# 全局配置
if sys.platform == "win32":
    APPDATA = os.environ.get('APPDATA', os.path.expanduser('~'))
    CONFIG_DIR = os.path.join(APPDATA, "LuoguAutoPunch")
    os.makedirs(CONFIG_DIR, exist_ok=True)
    CONFIG_FILE = os.path.join(CONFIG_DIR, "luogu_config.json")

# 全局变量
config_data = {}
root = None
main_frame = None
result_text = None
config_status = None

def startup_management(action):
    """统一管理开机启动项（添加/移除/检查）"""
    app_path = os.path.abspath(sys.argv[0])
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, 
                            winreg.KEY_WRITE | winreg.KEY_READ)
        
        if action == "add":
            winreg.SetValueEx(key, "LuoguAutoPunch", 0, winreg.REG_SZ, app_path)
            result = (True, "已添加到开机启动项")
        elif action == "remove":
            winreg.DeleteValue(key, "LuoguAutoPunch")
            result = (True, "已从开机启动项移除")
        elif action == "check":
            try:
                winreg.QueryValueEx(key, "LuoguAutoPunch")
                result = True
            except FileNotFoundError:
                result = False
        
        winreg.CloseKey(key)
        return result if action != "check" else result
    except Exception as e:
        return (False, f"操作失败: {e}") if action != "check" else False

def show_help_interface():
    """显示帮助界面"""
    main_frame.pack_forget()
    help_interface = tk.Frame(root)
    help_interface.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # 标题
    tk.Label(help_interface, text="说明与帮助", font=("微软雅黑", 16, "bold")).pack(pady=(0, 10))
    
    # 标签页
    notebook = ttk.Notebook(help_interface)
    notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 10))
    
    # 帮助内容配置
    help_contents = {
        "免责声明": """免责声明

本工具仅供学习和研究使用，请勿用于任何商业用途或违法活动。

1. 用户自行承担使用本工具的风险
2. 本工具不会收集或上传用户的个人信息
3. 打卡功能依赖于洛谷官方接口，如接口变更可能导致功能失效
4. 使用本工具前请确保已阅读并同意洛谷用户协议
5. 开发者不对因使用本工具造成的任何损失负责

请合理使用""",
        "鸣谢": """鸣谢

1.感谢 Hughpig ，提供最初的洛谷打卡思路和代码参考
2.感谢 deepsleep ，编写了代码
3.感谢 F_F_M_YC ，提供了思路并鞭策deepsleep写出了代码""",
        "更新日志": """更新日志
v1.0.0
- 初始版本发布
- 实现基本的打卡功能

v2.0.0 
- 支持配置文件管理
- 添加系统托盘图标
- 提供图形用户界面

v2.0.1 (2024-01-25)
- 修复配置文件路径问题
- 优化界面布局
- 改进错误提示
- 增强稳定性""",
        "使用方法": """使用方法

第一步：获取配置信息
1. 使用Chrome或Edge浏览器访问洛谷官网 (https://www.luogu.com.cn)
2. 登录您的洛谷账号
3. 按F12键打开开发者工具
4. 切换到"Application"或"应用"标签（Edge叫"存储"）
5. 在左侧找到"Storage" -> "Cookies" -> "https://www.luogu.com.cn"
6. 复制以下两个Cookie值：
   - _uid: 您的用户ID
   - __client_id: 客户端ID

第二步：配置工具
1. 点击主界面的"配置"按钮
2. 将上一步复制的两个值填入对应输入框
3. 点击"保存并返回"

第三步：使用打卡功能
1. 点击"立即打卡"按钮进行打卡
2. 查看"打卡结果"区域获取执行结果
3. 可以随时点击"配置"修改账号信息

其他功能：
- 点击"最小化到托盘"可以将程序隐藏到系统托盘
- 右键点击托盘图标可以显示窗口或退出程序
- 点击"说明"查看详细帮助信息
- 点击"退出"安全关闭程序

注意：Cookie值可能会过期，如打卡失败请重新获取。"""
    }
    
    # 创建标签页
    for tab_name, content in help_contents.items():
        frame = tk.Frame(notebook)
        text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("微软雅黑", 11), height=20)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
        notebook.add(frame, text=tab_name)
    
    # 返回按钮
    btn_frame = tk.Frame(help_interface)
    btn_frame.pack(pady=(0, 10))
    tk.Button(btn_frame, text="返回主界面", command=show_main_interface, 
              width=15, bg="lightblue").pack()

def show_main_interface():
    """显示主界面"""
    # 销毁其他界面
    for widget in root.winfo_children():
        if widget != main_frame and isinstance(widget, tk.Frame):
            widget.destroy()
    
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    update_config_status()

def load_config():
    """加载配置文件"""
    default_config = {"uid": "", "client_id": "", "auto_startup": False}
    
    if not os.path.exists(CONFIG_FILE):
        return default_config
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
            # 合并默认配置
            for key, value in default_config.items():
                loaded_config.setdefault(key, value)
            return loaded_config
    except:
        return default_config.copy()

def save_config(uid, client_id, auto_startup):
    """保存配置并处理开机启动"""
    global config_data
    config_data = {"uid": uid, "client_id": client_id, "auto_startup": auto_startup}
    
    try:
        # 保存配置文件
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        # 处理开机启动
        if auto_startup:
            success, msg = startup_management("add")
            if not success:
                messagebox.showwarning("警告", f"保存配置成功，但添加开机启动失败: {msg}")
            else:
                messagebox.showinfo("成功", f"配置已保存！\n开机启动已开启\n配置文件位置：{CONFIG_FILE}")
        else:
            startup_management("remove")
            messagebox.showinfo("成功", f"配置已保存！\n开机启动已关闭\n配置文件位置：{CONFIG_FILE}")
        
        return True
    except Exception as e:
        messagebox.showerror("错误", f"保存配置失败: {e}")
        return False

def show_config_interface():
    """显示配置界面"""
    main_frame.pack_forget()
    config_interface = tk.Frame(root)
    config_interface.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # 标题
    tk.Label(config_interface, text="洛谷账号配置", font=("微软雅黑", 16, "bold")).pack(pady=(0, 20))
    
    # 内容框架
    content_frame = tk.Frame(config_interface)
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # 左侧配置区域
    left_frame = tk.Frame(content_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    # 输入框
    input_frame = tk.Frame(left_frame)
    input_frame.pack(fill=tk.X, pady=(0, 20))
    
    # _uid输入
    uid_frame = tk.Frame(input_frame)
    uid_frame.pack(fill=tk.X, pady=5)
    tk.Label(uid_frame, text="_uid:", width=15, anchor=tk.W).pack(side=tk.LEFT)
    uid_entry = tk.Entry(uid_frame, width=40)
    uid_entry.pack(side=tk.LEFT, padx=(10, 0))
    uid_entry.insert(0, config_data.get("uid", ""))
    
    # __client_id输入
    client_frame = tk.Frame(input_frame)
    client_frame.pack(fill=tk.X, pady=5)
    tk.Label(client_frame, text="__client_id:", width=15, anchor=tk.W).pack(side=tk.LEFT)
    client_entry = tk.Entry(client_frame, width=40)
    client_entry.pack(side=tk.LEFT, padx=(10, 0))
    client_entry.insert(0, config_data.get("client_id", ""))
    
    # 帮助信息
    help_text = f"""如何获取配置信息：
1. 登录洛谷网站 (https://www.luogu.com.cn)
2. 按F12打开开发者工具
3. 切换到 Application/存储 标签
4. 找到 Cookies -> https://www.luogu.com.cn
5. 复制 _uid 和 __client_id 的值
    
配置文件位置：{CONFIG_FILE}"""
    help_frame = tk.LabelFrame(left_frame, text="获取帮助", padx=10, pady=10)
    help_frame.pack(fill=tk.X, pady=(0, 20))
    tk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=500).pack(anchor=tk.W)
    
    # 右侧设置区域
    right_frame = tk.Frame(content_frame)
    right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
    
    # 开机启动设置
    settings_frame = tk.LabelFrame(right_frame, text="程序设置", font=("微软雅黑", 12), padx=15, pady=15)
    settings_frame.pack(pady=(50, 0))
    
    startup_var = tk.BooleanVar(value=config_data.get("auto_startup", False))
    
    def toggle_startup():
        """切换开机启动状态"""
        btn_text = "开机启动: 开启" if startup_var.get() else "开机启动: 关闭"
        btn_bg = "lightgreen" if startup_var.get() else "lightcoral"
        startup_btn.config(text=btn_text, bg=btn_bg)
    
    startup_btn = tk.Button(settings_frame, text="", 
                           command=lambda: [startup_var.set(not startup_var.get()), toggle_startup()],
                           width=20, height=2, font=("微软雅黑", 10))
    startup_btn.pack(pady=10)
    toggle_startup()
    
    # 状态说明
    status_text = """当前状态：
✓ 开启：程序会在开机时自动启动
✓ 关闭：需要手动启动程序
    
注：需要保存配置后生效"""
    tk.Label(settings_frame, text=status_text, justify=tk.LEFT, 
             wraplength=250, font=("微软雅黑", 9)).pack(pady=(10, 0))
    
    # 按钮
    button_frame = tk.Frame(config_interface)
    button_frame.pack(pady=20)
    
    # 保存按钮
    def save_and_return():
        if save_config(uid_entry.get(), client_entry.get(), startup_var.get()):
            show_main_interface()
    
    tk.Button(button_frame, text="保存并返回", command=save_and_return, 
              width=15, bg="lightgreen", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
    
    # 取消按钮
    tk.Button(button_frame, text="取消并返回", command=show_main_interface, 
              width=15, font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)

def update_config_status():
    """更新配置状态显示"""
    if config_data.get("uid") and config_data.get("client_id"):
        config_status.config(text="已配置", fg="green")
    else:
        config_status.config(text="未配置", fg="red")

def luogu_punch():
    """执行洛谷打卡"""
    uid = config_data.get("uid", "").strip()
    client_id = config_data.get("client_id", "").strip()
    
    if not uid or not client_id:
        messagebox.showwarning("警告", "请先填写所有配置信息！点击'配置'按钮进行设置。")
        return
    
    # 准备请求参数
    cookie_str = f"_uid={uid}; __client_id={client_id}"
    url = "https://www.luogu.com.cn/index/ajax_punch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": cookie_str,
        "Referer": "https://www.luogu.com.cn/",
        "x-requested-with": "XMLHttpRequest"
    }
    
    # 执行打卡
    try:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "正在尝试连接洛谷服务器...\n")
        root.update()
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        # 处理响应
        if response.status_code == 200:
            code = data.get('code')
            if code == 200:
                result_text.insert(tk.END, f"打卡成功！\n运势: {data.get('message', '未知')}\n")
            elif code == 201:
                msg = data.get('message', '')
                if "已经打过卡" in msg or "不能急于求成" in msg:
                    result_text.insert(tk.END, "✅ 今日已打卡（无需重复）\n")
                elif "请登录" in msg:
                    result_text.insert(tk.END, "❌ Cookie已失效！请重新获取并更新配置！\n")
                else:
                    result_text.insert(tk.END, f"⚠️  状态201: {msg}\n")
            else:
                result_text.insert(tk.END, f"失败: {data.get('message')}\n")
        else:
            result_text.insert(tk.END, f"状态码错误: {response.status_code}\n")
    except Exception as e:
        result_text.insert(tk.END, f"发生异常: {e}\n")

def create_tray_icon():
    """创建系统托盘图标"""
    try:
        # 尝试下载洛谷图标
        response = requests.get("https://cdn.luogu.com.cn/upload/usericon/3.png", timeout=5)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                tmp_file.write(response.content)
                image = Image.open(tmp_file.name).resize((64, 64), Image.Resampling.LANCZOS)
                os.unlink(tmp_file.name)
        else:
            raise Exception("下载图标失败")
    except:
        # 使用默认图标
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("msyh.ttc", 20)
            draw.text((15, 20), "洛谷", font=font, fill='white')
        except:
            draw.text((20, 20), "LG", fill='white')
    
    # 创建托盘菜单
    menu = (
        item('显示窗口', lambda: root.deiconify()),
        item('退出', lambda: (icon.stop(), root.quit()))
    )
    
    # 启动托盘
    icon = pystray.Icon("luogu_punch", image, "洛谷打卡工具", menu=menu)
    icon.run()

def init_ui():
    """初始化主界面"""
    global root, main_frame, result_text, config_status, config_data
    
    # 加载配置
    config_data = load_config()
    
    # 创建主窗口
    root = tk.Tk()
    root.title("洛谷自动打卡工具")
    root.geometry("800x600")
    
    # 创建主框架
    main_frame = tk.Frame(root)
    
    # 标题
    tk.Label(main_frame, text="洛谷自动打卡工具", font=("微软雅黑", 20, "bold")).pack(pady=(20, 30))
    
    # 配置状态
    config_status_frame = tk.Frame(main_frame)
    config_status_frame.pack(pady=(0, 20))
    tk.Label(config_status_frame, text="配置状态:", font=("微软雅黑", 12)).pack(side=tk.LEFT)
    config_status = tk.Label(config_status_frame, text="", font=("微软雅黑", 12))
    config_status.pack(side=tk.LEFT, padx=(10, 0))
    
    # 配置文件路径
    tk.Label(main_frame, text=f"配置文件: {CONFIG_FILE}", font=("微软雅黑", 9), fg="gray").pack(pady=(0, 10))
    
    # 功能按钮
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=20)
    
    buttons = [
        ("配置", show_config_interface),
        ("立即打卡", luogu_punch),
        ("说明", show_help_interface),
        ("最小化到托盘", lambda: root.withdraw()),
        ("退出", root.quit)
    ]
    
    for text, cmd in buttons:
        tk.Button(button_frame, text=text, command=cmd, width=10, height=1, 
                  font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=20)
    
    # 打卡结果区域
    result_frame = tk.LabelFrame(main_frame, text="打卡结果", font=("微软雅黑", 12), padx=5, pady=5)
    result_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
    result_text = scrolledtext.ScrolledText(result_frame, height=5, wrap=tk.WORD, font=("Consolas", 10))
    result_text.pack(fill=tk.BOTH, expand=True)
    
    # 使用说明
    help_text = """使用步骤：
1. 点击"配置"按钮，填写您的洛谷账号信息
2. 点击"立即打卡"按钮进行打卡
3. 可以使用"最小化到托盘"将程序隐藏到系统托盘
4. 双击托盘图标或右键选择"显示窗口"可重新显示程序"""
    help_frame = tk.LabelFrame(main_frame, text="使用说明", font=("微软雅黑", 12), padx=10, pady=10)
    help_frame.pack(fill=tk.X, pady=(20, 20))
    tk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=700).pack(anchor=tk.W)
    
    # 显示主界面
    show_main_interface()
    
    # 启动托盘线程
    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    init_ui()