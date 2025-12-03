# 51CTO Backend API

完整独立的 51CTO 文章爬虫 + HongYiXun 格式后端服务器

## 特性

✅ **完整独立系统** - 所有文件都在一个文件夹，可独立运行  
✅ **HongYiXun 格式** - 完全符合 HongYiXun 数据格式规范  
✅ **RESTful API** - 提供完整的 REST API 接口  
✅ **自动爬虫** - 启动时自动爬取数据，无需手动触发  
✅ **后台爬取** - 爬虫在后台运行，不阻塞 API 请求  
✅ **缓存管理** - 智能缓存，提高响应速度  
✅ **API 文档** - 自动生成 Swagger/ReDoc 文档  

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python run.py
```

**服务器会自动开始爬取数据！**

- 🚀 服务器立即启动，可以接受请求
- 📝 爬虫在后台运行，自动爬取数据
- ⏱️ 等待 2-5 分钟，数据就会可用

### 3. 访问服务

- **服务器**: http://localhost:8002
- **API 文档**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

### 4. 查看数据

等待几分钟后：

```bash
curl http://localhost:8002/api/news/
```

数据会自动出现！

## API 接口

### 新闻接口

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/news/` | 获取新闻列表（分页） |
| GET | `/api/news/{id}` | 获取单篇新闻 |
| POST | `/api/news/crawl` | 手动触发爬取 |
| GET | `/api/news/status/info` | 获取服务状态 |
| POST | `/api/news/cache/refresh` | 刷新缓存 |

### 基础接口

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/` | 服务信息 |
| GET | `/health` | 健康检查 |

## 使用示例

### 获取新闻列表

```bash
# 获取第1页，每页20条
curl "http://localhost:8002/api/news/?page=1&page_size=20"

# 搜索新闻
curl "http://localhost:8002/api/news/?search=OpenHarmony"

# 按分类筛选
curl "http://localhost:8002/api/news/?category=技术文章"
```

### 手动触发爬取

```bash
# 爬取最多10页
curl -X POST "http://localhost:8002/api/news/crawl?max_pages=10"
```

### 查看服务状态

```bash
curl "http://localhost:8002/api/news/status/info"
```

## 数据格式

### NewsArticle

```json
{
  "id": "abc123",
  "title": "文章标题",
  "date": "2024-12-01",
  "url": "https://ost.51cto.com/posts/12345",
  "content": [
    {"type": "text", "value": "段落内容..."},
    {"type": "image", "value": "https://example.com/img.jpg"},
    {"type": "code", "value": "const x = 1;"}
  ],
  "category": "技术文章",
  "summary": "文章摘要...",
  "source": "51CTO",
  "created_at": "2024-12-01T10:30:00",
  "updated_at": "2024-12-01T10:30:00"
}
```

## 配置

编辑 `.env` 文件（从 `.env.example` 复制）：

```env
# 服务器端口
PORT=8002

# 主要控制：文章ID下限（推荐使用）
MIN_ARTICLE_ID=33500

# 备用限制：最大爬取页数
MAX_PAGES=999

# 日志级别
LOG_LEVEL=INFO
```

**爬取控制说明**:
- 爬虫主要通过 `MIN_ARTICLE_ID` 控制
- 遇到 ID ≤ 33500 的文章会跳过
- 连续 3 页旧文章自动停止
- `MAX_PAGES` 作为备用限制（通常不会达到）
- 详细说明请查看 `CRAWL_CONTROL.md`

## 项目结构

```
51cto_backend/
├── api/                    # API 接口
│   ├── __init__.py
│   └── news.py            # 新闻接口
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── config.py          # 配置
│   ├── cache.py           # 缓存
│   └── logging_config.py  # 日志
├── models/                 # 数据模型
│   ├── __init__.py
│   └── news.py            # 新闻模型
├── services/               # 服务层
│   ├── __init__.py
│   └── cto51_crawler.py   # 51CTO 爬虫
├── data/                   # 数据目录
├── logs/                   # 日志目录
├── main.py                 # 主程序
├── run.py                  # 启动脚本
├── requirements.txt        # 依赖
├── .env.example           # 配置示例
└── README.md              # 本文件
```

## 开发

### 添加新接口

1. 在 `api/` 目录创建新的路由文件
2. 在 `main.py` 中注册路由

### 修改爬虫

编辑 `services/cto51_crawler.py`

### 修改数据模型

编辑 `models/news.py`

## 数据持久化

系统具有完整的数据持久化机制：

- ✅ **自动保存**: 每5篇文章保存一次到 `data/51cto_articles.json`
- ✅ **自动加载**: 启动时加载历史数据，避免重复爬取
- ✅ **异常保护**: 中断、错误时也会保存数据
- ✅ **URL去重**: 自动跳过已爬取的文章

### 验证数据

```bash
# 验证数据完整性
python verify_data.py verify

# 备份数据文件
python verify_data.py backup

# 测试持久化机制
python test_data_persistence.py
```

详细说明请查看 `DATA_PERSISTENCE.md`

## 注意事项

- 启动时自动加载历史数据并开始爬取新文章
- 爬虫在后台运行，不会阻塞 API 请求
- 主要通过 `MIN_ARTICLE_ID` 控制爬取范围（推荐设置 33500-35000）
- 数据自动保存到 `data/51cto_articles.json`，避免重复爬取
- **任何情况下都会保存数据**（包括中断、异常）
- 生产环境请修改 `CORS_ORIGINS` 为具体域名

## 故障排除

### 端口被占用

修改 `.env` 中的 `PORT` 值

### ChromeDriver 错误

```bash
pip install webdriver-manager
```

### 日志查看

```bash
tail -f logs/app.log
```

## 许可证

MIT License

---

**版本**: 1.0.0  
**最后更新**: 2024-12-02
