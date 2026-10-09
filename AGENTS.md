# AGENTS.md

AI 智能会议助手：一个中文教学/演示用的全栈应用。

- `fastapi-app/` - FastAPI + Tortoise ORM 后端（MySQL），端口 9090
- `vue/` - Vue 3 + Vite + Element Plus 前端
- `ai_meeting.sql` - 根目录 Navicat 导出文件；真正的数据库结构与演示数据都在这里
- 不是 monorepo：前后端相互独立，没有共享工具链。`.opencode/skills/` 里是打包进来的第三方技能（archify 画图），与应用代码无关。

约定：几乎每一行代码都带中文注释/docstring，编辑时保持这种风格。

## 命令

后端（在 `fastapi-app/` 下运行）：
- 启动：`python main.py`（uvicorn 热重载，http://localhost:9090）
- 测试：`python -m pytest tests` - 不需要 MySQL，测试用内存 SQLite 并 mock 所有 AI 调用
- 单个测试：`python -m pytest tests/test_transcription.py::TranscriptionTest::test_start_and_retry_state_flow`
- 没有 lint/typecheck 配置。

前端（在 `vue/` 下运行）：
- `npm install`、`npm run dev`（Vite，5173）、`npm run build`
- 没有 lint/test 配置。

## 后端注意事项

- 表结构不会自动生成。`main.py` 里的 `register_tortoise` 没有 `generate_schemas`；表和数据靠导入 `ai_meeting.sql`。任何模型改动都要同时改 `models.py` 和 `ai_meeting.sql`。
- 配置是硬编码的，不走环境变量：数据库账号密码 + JWT 密钥在 `settings.py`；AI 接口地址/密钥是 `ai_model_config` 表里的数据行。后端不读取任何环境变量。
- 所有响应都是 HTTP 200。错误放在响应体里 `{code, msg, data}`，code 是字符串 `'200'/'500'/'401'/'403'`（`common/result.py`、`common/exception_handler.py`）。要判断 `res.code`，不要看 HTTP 状态码。
- 鉴权用的是 `token` 请求头（不是 `Authorization`/Bearer）。辅助函数：`common/auth.py` 里的 `get_current_user` / `require_admin`。
- 路由由 `api/__init__.py` 里的 `pkgutil` 自动发现：任何暴露 `router` 的 `api/*.py` 都会自动注册。
- 长任务（转写、纪要、纪要自检）以进程内 `asyncio` 任务运行，用模块级字典跟踪；`main.py` 的 lifespan 在启动时重新调度未完成的任务（`recover_*`）。只能单进程运行——不要加多 worker。
- 时间：用 `common/times.now()` / `format_datetime()`（Asia/Shanghai，`use_tz=True`）；避免直接用无时区的 `datetime.now()`。
- AI 调用：文本模型走 `services/model_factory.invoke_json`（LangChain `ChatOpenAI` 对接 OpenAI 兼容的 Dashscope/百炼）；转写直接用 httpx 调 Dashscope HTTP 接口。提示词是 `prompt_template` 表里的数据行，按 `code` 查询。
- 转写需要 PATH 里有 `ffmpeg`；没有时 ffmpeg 测试会自动跳过。
- 上传的资料存放在 `fastapi-app/files/meeting_material/`，用 `storage_name` 字段引用。
- 忽略 `__pycache__`：部分 `.pyc` 是已删除模块的残留，没有对应的源码。

## 前端注意事项

- API 基础地址来自 `.env.development` 里的 `VITE_BASE_URL`（http://localhost:9090）；`.env.production` 是占位符。
- `@` 映射到 `src/`（Vite alias + `jsconfig.json`）。SCSS 会自动在每个 style 块注入 `src/assets/css/index.scss`。
- Element Plus 组件通过 unplugin 解析器自动导入（`vite.config.js`），同时在 `main.js` 里注册；所有 Element Plus 图标已全局注册。
- 登录用户缓存在 `localStorage['xm-user']`；axios 在 `src/utils/request.js` 里附带其 `token` 请求头。
- `src/router/index.js` 里的路由守卫用 `xm-user` 和 `meta.requiresAdmin` 做登录校验。
