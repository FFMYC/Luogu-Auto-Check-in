# main.py 的 README

## 概述
`main.py` 是一个用于洛谷自动打卡的工具，提供图形用户界面和系统托盘支持，方便用户快速完成每日打卡任务。

## 功能
- 自动完成洛谷每日打卡。
- 提供图形用户界面，支持配置管理。
- 支持系统托盘操作，便于后台运行。
- 显示打卡结果和日志。

## 使用方法
1. **配置账号信息**：
    - 点击主界面的“配置”按钮。
    - 填写从洛谷网站获取的 `_uid` 和 `__client_id`。
    - 保存配置。
2. **执行打卡**：
    - 点击“立即打卡”按钮。
    - 查看打卡结果。
3. **其他功能**：
    - 点击“最小化到托盘”将程序隐藏到系统托盘。
    - 右键托盘图标可显示窗口或退出程序。

## 依赖项
- Python 3.x
- 必需库：
  - `tkinter`
  - `pystray`
  - `Pillow`
  - `requests`

### 安装依赖项
在运行此工具之前，请确保已安装所有必需的依赖项。您可以使用以下命令安装所需库：

```bash
pip install pystray pillow requests
```

如果您尚未安装 Python，请访问 [Python 官方网站](https://www.python.org/) 下载并安装适合您操作系统的版本。

## 注意事项
- 配置文件路径根据操作系统自动生成：
  - Windows: `%APPDATA%\LuoguAutoPunch\luogu_config.json`
  - macOS: `~/Library/Application Support/LuoguAutoPunch/luogu_config.json`
  - Linux: `~/.config/luoguautopunch/luogu_config.json`
- 确保网络连接正常，Cookie 值有效。
- 本工具仅供学习和研究使用，请勿用于非法用途。

## 许可证
在此处包含许可证信息（如果适用）。

## 作者
- 开发者: F_F_M_YC
- 鸣谢:
  - Hughpig: 提供自动打卡方案思路和代码参考。
  - deepsleep: 提供代码。
- [洛谷主页](https://www.luogu.com.cn/user/1460207)
- 联系方式: QQ 3911255176