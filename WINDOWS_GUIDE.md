# Windows 使用指南

## 🚀 快速开始

### 方式1：使用脚本（推荐）

#### 1. 安装

双击运行：
```
setup-windows.bat
```

这会自动：
- ✅ 检查 Python
- ✅ 安装 Python 依赖
- ✅ 安装 Playwright 浏览器

#### 2. 启动

双击运行：
```
start-windows.bat
```

#### 3. 访问

浏览器打开：
- API 文档: http://localhost:8002/docs
- 健康检查: http://localhost:8002/health

---

### 方式2：手动安装

#### 1. 安装 Python 依赖

```cmd
pip install -r requirements.txt
```

#### 2. 安装 Playwright 浏览器

```cmd
playwright install chromium
```

如果上面的命令不行，试试：
```cmd
python -m playwright install chromium
```

#### 3. 启动服务

```cmd
python run.py
```

---

## 📋 前提条件

### 安装 Python

1. 下载 Python 3.11+: https://www.python.org/downloads/
2. 安装时勾选 "Add Python to PATH"
3. 验证安装：
   ```cmd
   python --version
   ```

### 安装 pip

Python 3.11+ 自带 pip，验证：
```cmd
pip --version
```

---

## 🐛 故障排除

### 问题1：playwright 命令找不到

**解决方案**：
```cmd
python -m playwright install chromium
```

### 问题2：pip 安装慢

**解决方案**：使用国内镜像
```cmd
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3：Playwright 浏览器下载慢

**解决方案**：使用国内镜像
```cmd
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
```

### 问题4：端口被占用

**解决方案**：修改端口

编辑 `.env` 文件：
```env
PORT=8003
```

或者查找占用端口的程序：
```cmd
netstat -ano | findstr :8002
```

### 问题5：权限错误

**解决方案**：以管理员身份运行

右键点击 `setup-windows.bat` → "以管理员身份运行"

---

## 📁 项目结构

```
51ctoCrawler/
├── setup-windows.bat      # 安装脚本
├── start-windows.bat      # 启动脚本
├── run.py                 # 主程序
├── requirements.txt       # Python 依赖
├── api/                   # API 接口
├── core/                  # 核心模块
├── models/                # 数据模型
├── services/              # 爬虫服务
├── data/                  # 数据目录（自动创建）
└── logs/                  # 日志目录（自动创建）
```

---

## 🔧 配置

### 创建配置文件

复制 `.env.example` 为 `.env`：
```cmd
copy .env.example .env
```

### 编辑配置

用记事本打开 `.env`：
```env
# 服务器端口
PORT=8002

# 文章ID下限
MIN_ARTICLE_ID=33500

# 最大爬取页数
MAX_PAGES=999

# 日志级别
LOG_LEVEL=INFO
```

---

## 📊 查看数据

### 数据文件位置

```
data/51cto_articles.json
```

### 日志文件位置

```
logs/app.log
```

### 使用记事本查看

```cmd
notepad data\51cto_articles.json
notepad logs\app.log
```

---

## 🌐 API 使用

### 获取文章列表

浏览器访问：
```
http://localhost:8002/api/news/
```

或使用 PowerShell：
```powershell
Invoke-WebRequest http://localhost:8002/api/news/ | Select-Object -Expand Content
```

### 查看 API 文档

浏览器访问：
```
http://localhost:8002/docs
```

---

## 🛑 停止服务

在运行 `start-windows.bat` 的窗口中按 `Ctrl+C`

---

## 💡 提示

1. **首次运行需要时间**
   - 安装依赖：2-5 分钟
   - 下载浏览器：5-10 分钟
   - 开始爬取：自动开始

2. **数据持久化**
   - 数据保存在 `data/` 目录
   - 日志保存在 `logs/` 目录
   - 重启服务不会丢失数据

3. **自动爬取**
   - 服务启动后自动开始爬取
   - 数据会逐步增加
   - 可以在 API 文档中查看进度

4. **开发模式**
   - 修改代码后需要重启服务
   - 按 `Ctrl+C` 停止
   - 重新运行 `start-windows.bat`

---

## 📚 更多文档

- [README.md](README.md) - 项目说明
- [INSTALL.md](INSTALL.md) - 详细安装指南
- [API 文档](http://localhost:8002/docs) - 在线 API 文档

---

**需要帮助？** 查看日志文件：`logs/app.log`
