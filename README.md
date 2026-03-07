# SkillHub 开源版

社区驱动的开放技能平台，致力于成为 AI 代理技能生态系统的公共基础设施。通过极致简化的跨平台分发机制，让 AI 开发者能轻松分享和安装大模型工具与自动化工作流。

## ✨ 核心价值

- **完全免费** - 无付费技能、无订阅、无交易分成
- **完全开源** - 代码、文档、治理透明
- **极致安装 (Plan A)** - 通过原生系统命令（`curl | bash`, `iwr | iex`）零前置依赖秒级安装
- **自动多版本控制** - 前后端自动协同记录每次技能包上传，按时间戳追溯历史所有发版记录
- **纯粹跨平台体验** - Web 端针对开发宿主环境（macOS/Linux/Windows）动态生成拉取指令

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Next.js 14 + React 18 + Tailwind CSS + TypeScript |
| **后端** | Python 3.10+ + FastAPI + SQLAlchemy |
| **数据库** | MySQL 8.0 |
| **核心机制** | JSON Web Token (JWT) + 文件系统静态映射 |
| **容器化** | Docker + Docker Compose + 本地数据卷直接挂载 |

## 🌟 核心功能特性

### 🔌 安装管理 (零依赖脚本化)
- **多平台自适应动态命令板** - WebUI 能够一键复制针对本系统环境量身定制的无依赖环境解压或拉取脚本。
- **一键运行指令集成**：
  - (Linux/macOS): `curl -L -o my-skill.zip "http://<hub>/api/v1/install/<id>/download-file"`
  - (Windows PowerShell): `iwr -Uri "http://<hub>/api/v1/install/<id>/download-file" -OutFile my-skill.zip`
- **后台计数审计** - 真实下载记录与技能评分透明化。

### 📦 技能发布与版本追溯
- **开发者直接发版验证**: 登录即享创作者工作台发布技能 Zip 文件。
- **历史版本切换 (Version Selector)**: 详情页中支持自由回退至老版本的环境，查看对应的打包时间和专用拉取指令。
- **关联更新追踪**: 无需繁琐配置，直接由详情页 `发布新版本/更新技能` 按钮同态替换并自动累加 Version 号。

### 🔍 发现机制 (高级分发网络)
- 高度优化的多条件筛选项：精确到星级的过滤器、时间排序、分类引擎。

## 🚀 快速开始部署 (Docker 推荐)

我们推荐使用 Docker Compose 快速一键拉起后端集群和前端门户平台服务。

### 1. 克隆代码 & 准备环境变量
```bash
git clone https://github.com/skillhub-org/skillhub.git
cd skillhub
# 准备环境范本
cp .env.example .env
```

### 2. 本地宿主机文件挂载配置
在 `docker-compose.yml` 中默认开启了 `volumes: - ./backend/uploads:/app/uploads`，这意味着您可以随时在部署根目录中查取热更所有 `.zip` 包。

### 3. 一键启停服务
```bash
# 后台构建并唤醒全栈
docker compose up -d --build

# 查看运行状态
docker compose ps
```

这将在您的网络暴露下列服务：
- 后台 API (FastAPI): `http://localhost:8000`
- API Swagger 联调文档: `http://localhost:8000/docs`
- 门户前端 (Next.js): `http://localhost:3000`

### 手动开发拆卸命令 (Local)
#### Python 后台
```powershell
cd backend
conda create -n skillhub python=3.10
conda activate skillhub
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

#### Node 前端
```powershell
cd frontend
npm install
npm run dev
```

## 🗺️ 项目主干结构

```
skillhub/
├── backend/                    # Python FastAPI 后端
│   ├── app/
│   │   ├── api/v1/             # 领域路由 (skills, users, search, install, publish)
│   │   ├── models/             # ORM 模型
│   │   └── services/           # Controller 层封装依赖
│   └── uploads/                # 动态生成的宿主机云端共享 ZIP 包归档 (Docker卷挂载)
├── frontend/                   # Next.js 极速渲染前端
│   ├── src/
│   │   ├── app/                # App Router (首页, 搜索大厅, 登录鉴权, 技能详情)
│   │   ├── components/         # 原子化/业务混合 UI 组件
│   │   └── lib/                # API 拦截器封装池
└── docker-compose.yml          # 全栈拉起编排文件
```

## 💡 开发协作规范与注意事项

本应用秉持最轻量级的设计原则，不再过度封装独立 CLI 应用，而是完全拥抱终端操作系统的原生网络流处理（Powershell / Unix Curl）。
- [提交规范] - 采用标准 Conventional Commits。
- [清净代码保障] - 已部署 `ts-prune` 与 `vulture` 进行无引用函数安全裁撤机制。

## 🛡️ License

[MIT License](LICENSE)
