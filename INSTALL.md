# 安装指南

## 📦 安装依赖

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 Playwright 浏览器

**重要**：Playwright 需要额外安装浏览器

```bash
# 安装 Chromium 浏览器
playwright install chromium

# 或安装所有浏览器
playwright install
```

### 3. 验证安装

```bash
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

## 🚀 启动服务

```bash
python run.py
```

## 🐛 故障排除

### 问题：playwright 命令找不到

```bash
# 使用 python -m 运行
python -m playwright install chromium
```

### 问题：浏览器下载失败

```bash
# 使用国内镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
python -m playwright install chromium
```

### 问题：权限错误

```bash
# Linux/Mac
sudo python -m playwright install-deps
```

## 📝 完整安装流程

```bash
# 1. 克隆项目
git clone https://github.com/Soupcpu/51ctoCrawler.git
cd 51ctoCrawler

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 安装 Playwright 浏览器
playwright install chromium

# 4. 启动服务
python run.py
```

## 🌐 访问服务

- API 文档: http://localhost:8002/docs
- 健康检查: http://localhost:8002/health
- 服务状态: http://localhost:8002/api/news/status/info

---

**提示**：Playwright 比 Selenium 更稳定，不需要管理 ChromeDriver！
