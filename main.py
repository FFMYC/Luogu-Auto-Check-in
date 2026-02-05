# 必须的导入语句
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

# 根据操作系统确定配置文件路径
if sys.platform == "win32":
    # Windows系统
    APPDATA = os.environ.get('APPDATA', os.path.expanduser('~'))
    CONFIG_DIR = os.path.join(APPDATA, "LuoguAutoPunch")
elif sys.platform == "darwin":
    # macOS系统
    CONFIG_DIR = os.path.expanduser("~/Library/Application Support/LuoguAutoPunch")
else:
    # Linux和其他Unix系统
    CONFIG_DIR = os.path.expanduser("~/.config/luoguautopunch")

# 确保配置目录存在
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(CONFIG_DIR, "luogu_config.json")

def show_help_interface():
    """显示说明界面"""
    main_frame.pack_forget()
    
    global help_interface
    help_interface = tk.Frame(root)
    help_interface.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    title_label = tk.Label(help_interface, text="说明与帮助", font=("微软雅黑", 16, "bold"))
    title_label.pack(pady=(0, 10))

    # 创建框架来容纳笔记本和按钮，确保按钮在最底部可见
    content_frame = tk.Frame(help_interface)
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    notebook = ttk.Notebook(content_frame)
    notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 10))
    
    # 免责声明标签页
    disclaimer_frame = tk.Frame(notebook)
    disclaimer_text = scrolledtext.ScrolledText(disclaimer_frame, wrap=tk.WORD, font=("微软雅黑", 11), height=20)
    disclaimer_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    disclaimer_content = """免责声明

本工具仅供学习和研究使用，请勿用于任何商业用途或违法活动。

1. 用户自行承担使用本工具的风险
2. 本工具不会收集或上传用户的个人信息
3. 打卡功能依赖于洛谷官方接口，如接口变更可能导致功能失效
4. 使用本工具前请确保已阅读并同意洛谷用户协议
5. 开发者不对因使用本工具造成的任何损失负责

请合理使用"""
    disclaimer_text.insert(tk.END, disclaimer_content)
    disclaimer_text.config(state=tk.DISABLED)
    notebook.add(disclaimer_frame, text="免责声明")
    
    # 鸣谢标签页
    credits_frame = tk.Frame(notebook)
    credits_text = scrolledtext.ScrolledText(credits_frame, wrap=tk.WORD, font=("微软雅黑", 11), height=20)
    credits_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    credits_content = """鸣谢

1.感谢 Hughpig ，提供最初的洛谷打卡思路和代码参考
2.感谢 deepsleep ，编写了代码
3.感谢 F_F_M_YC ，提供了思路并鞭策deepsleep写出了代码"""
    credits_text.insert(tk.END, credits_content)
    credits_text.config(state=tk.DISABLED)
    notebook.add(credits_frame, text="鸣谢")
    
    # 更新日志标签页
    changelog_frame = tk.Frame(notebook)
    changelog_text = scrolledtext.ScrolledText(changelog_frame, wrap=tk.WORD, font=("微软雅黑", 11), height=20)
    changelog_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    changelog_content = """更新日志
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
- 增强稳定性"""
    changelog_text.insert(tk.END, changelog_content)
    changelog_text.config(state=tk.DISABLED)
    notebook.add(changelog_frame, text="更新日志")
    
    # 用法标签页
    usage_frame = tk.Frame(notebook)
    usage_text = scrolledtext.ScrolledText(usage_frame, wrap=tk.WORD, font=("微软雅黑", 11), height=20)
    usage_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    usage_content = """使用方法

第一步：获取配置信息
1. 使用Chrome或Edge浏览器访问洛谷官网 (https://www.luogu.com.cn)
2. 登录您的洛谷账号
3. 按F12键打开开发者工具
4. 切换到"Application"或"应用"标签（Edge叫"存储"）
5. 在左侧找到"Storage" -> "Cookies" -> "https://www.luogu.com.cn"
6. 复制以下三个Cookie值：
   - _uid: 您的用户ID
   - __client_id: 客户端ID

第二步：配置工具
1. 点击主界面的"配置"按钮
2. 将上一步复制的三个值填入对应输入框
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
    usage_text.insert(tk.END, usage_content)
    usage_text.config(state=tk.DISABLED)
    notebook.add(usage_frame, text="使用方法")
    
    # 返回按钮 - 放在content_frame内部，但不在notebook中
    btn_frame = tk.Frame(content_frame)
    btn_frame.pack(pady=(0, 10))
    btn_back = tk.Button(btn_frame, text="返回主界面", command=show_main_interface, width=15, bg="lightblue")
    btn_back.pack()

def show_main_interface():
    """显示主界面"""
    # 销毁其他界面
    for widget_name in ['config_interface', 'help_interface']:
        if widget_name in globals():
            widget = globals().get(widget_name)
            if widget and widget.winfo_exists():
                widget.destroy()
    
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

def load_config():
    """加载配置文件"""
    default_config = {
        "uid": "",
        "client_id": "",
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                for key in default_config:
                    if key not in config_data:
                        config_data[key] = default_config[key]
                return config_data
        except:
            return default_config.copy()
    return default_config.copy()

def save_config_and_return():
    """保存配置并返回主界面"""
    config_data = {
        "uid": uid_entry.get(),
        "client_id": client_entry.get(),
    }
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("成功", f"配置已保存！\n配置文件位置：{CONFIG_FILE}")
        update_config_status()
        show_main_interface()
    except Exception as e:
        messagebox.showerror("错误", f"保存配置失败: {e}")

def show_config_interface():
    """显示配置界面"""
    main_frame.pack_forget()
    
    global config_interface, uid_entry, client_entry
    
    config_interface = tk.Frame(root)
    config_interface.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    title_label = tk.Label(config_interface, text="洛谷账号配置", font=("微软雅黑", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    input_frame = tk.Frame(config_interface)
    input_frame.pack(fill=tk.X, pady=(0, 20))
    
    # UID输入框
    uid_frame = tk.Frame(input_frame)
    uid_frame.pack(fill=tk.X, pady=5)
    tk.Label(uid_frame, text="_uid:", width=15, anchor=tk.W).pack(side=tk.LEFT)
    uid_entry = tk.Entry(uid_frame, width=40)
    uid_entry.pack(side=tk.LEFT, padx=(10, 0))
    
    # Client ID输入框
    client_frame = tk.Frame(input_frame)
    client_frame.pack(fill=tk.X, pady=5)
    tk.Label(client_frame, text="__client_id:", width=15, anchor=tk.W).pack(side=tk.LEFT)
    client_entry = tk.Entry(client_frame, width=40)
    client_entry.pack(side=tk.LEFT, padx=(10, 0))
    
    # 加载现有配置
    config_data = load_config()
    uid_entry.insert(0, config_data.get("uid", ""))
    client_entry.insert(0, config_data.get("client_id", ""))
    
    # 使用说明
    help_text = """如何获取配置信息：
1. 登录洛谷网站 (https://www.luogu.com.cn)
2. 按F12打开开发者工具
3. 切换到 Application/存储 标签
4. 找到 Cookies -> https://www.luogu.com.cn
5. 复制 _uid 和 __client_id 的值
    
配置文件位置："""
    
    help_frame = tk.LabelFrame(config_interface, text="获取帮助", padx=10, pady=10)
    help_frame.pack(fill=tk.X, pady=(0, 20))
    tk.Label(help_frame, text=help_text + CONFIG_FILE, justify=tk.LEFT, wraplength=600).pack(anchor=tk.W)
    
    # 按钮区域
    button_frame = tk.Frame(config_interface)
    button_frame.pack(pady=10)
    
    btn_save = tk.Button(button_frame, text="保存并返回", command=save_config_and_return, width=15, bg="lightgreen")
    btn_save.pack(side=tk.LEFT, padx=5)
    
    btn_cancel = tk.Button(button_frame, text="取消并返回", command=show_main_interface, width=15)
    btn_cancel.pack(side=tk.LEFT, padx=5)

def update_config_status():
    """更新配置状态显示"""
    config_data = load_config()
    
    if config_data.get("uid") and config_data.get("client_id"):
        config_status.config(text="已配置", fg="green")
    else:
        config_status.config(text="未配置", fg="red")

def luogu_punch():
    """洛谷打卡功能"""
    config_data = load_config()
    
    uid = config_data.get("uid", "").strip()
    client_id = config_data.get("client_id", "").strip()
    
    if not uid or not client_id :
        messagebox.showwarning("警告", "请先填写所有配置信息！点击'配置'按钮进行设置。")
        return
    
    cookie_str = f"_uid={uid}; __client_id={client_id}"
    url = "https://www.luogu.com.cn/index/ajax_punch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": cookie_str,
        "Referer": "https://www.luogu.com.cn/",
        "x-requested-with": "XMLHttpRequest" 
    }
    
    try:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "正在尝试连接洛谷服务器...\n")
        root.update()
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
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
        image_url = "https://cdn.luogu.com.cn/upload/usericon/3.png"
        response = requests.get(image_url, timeout=5)
        
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name
            
            image = Image.open(tmp_path)
            image = image.resize((64, 64), Image.Resampling.LANCZOS)
            os.unlink(tmp_path)
        else:
            raise Exception("下载图标失败")
            
    except Exception as e:
        print(f"加载网络图标失败: {e}，使用默认图标")
        image = Image.new('RGB', (64, 64), color='blue')
        draw = ImageDraw.Draw(image)
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("msyh.ttc", 20)
            draw.text((15, 20), "洛谷", font=font, fill='white')
        except:
            draw.text((20, 20), "LG", fill='white')
    
    menu = (
        item('显示窗口', lambda: root.deiconify()),
        item('退出', lambda: (icon.stop(), root.quit()))
    )
    
    icon = pystray.Icon("luogu_punch", image, "洛谷打卡工具", menu=menu)
    icon.run()

def safe_exit():
    """安全退出程序"""
    root.quit()

# 创建主窗口
root = tk.Tk()
root.title("洛谷自动打卡工具")
root.geometry("800x600")

# 创建主框架
main_frame = tk.Frame(root)

# 标题
title_label = tk.Label(main_frame, text="洛谷自动打卡工具", font=("微软雅黑", 20, "bold"))
title_label.pack(pady=(20, 30))

# 配置状态显示
config_status_frame = tk.Frame(main_frame)
config_status_frame.pack(pady=(0, 20))

tk.Label(config_status_frame, text="配置状态:", font=("微软雅黑", 12)).pack(side=tk.LEFT)

config_data = load_config()
config_status = tk.Label(config_status_frame, 
                        text="已配置" if config_data.get("uid") and config_data.get("client_id") else "未配置", 
                        font=("微软雅黑", 12), 
                        fg="green" if config_data.get("uid") and config_data.get("client_id") else "red")
config_status.pack(side=tk.LEFT, padx=(10, 0))

# 配置文件路径显示
config_path_label = tk.Label(main_frame, text=f"配置文件: {CONFIG_FILE}", font=("微软雅黑", 9), fg="gray")
config_path_label.pack(pady=(0, 10))

# 按钮区域
button_frame = tk.Frame(main_frame)
button_frame.pack(pady=20)

btn_config = tk.Button(button_frame, text="配置", command=show_config_interface, width=10, height=1, font=("微软雅黑", 10))
btn_config.pack(side=tk.LEFT, padx=20)

btn_punch = tk.Button(button_frame, text="立即打卡", command=luogu_punch, width=10, height=1,  font=("微软雅黑", 10))
btn_punch.pack(side=tk.LEFT, padx=20)

btn_help = tk.Button(button_frame, text="说明", command=show_help_interface, width=10, height=1, font=("微软雅黑", 10))
btn_help.pack(side=tk.LEFT, padx=20)

btn_minimize = tk.Button(button_frame, text="最小化到托盘", command=lambda: root.withdraw(), width=10, height=1, font=("微软雅黑", 10))
btn_minimize.pack(side=tk.LEFT, padx=20)

btn_exit = tk.Button(button_frame, text="退出", command=safe_exit, width=10, height=1, font=("微软雅黑", 10))
btn_exit.pack(side=tk.LEFT, padx=20)

# 结果显示区域
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

# 在后台线程运行托盘图标
tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
tray_thread.start()

# 运行主窗口
root.mainloop()