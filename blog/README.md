# blog 仓库说明

这个目录本质上是一个个人技术博客工作区，核心站点在 `posts/`。

## 2026 年发文（阅读地图摘要）

站内阅读地图页面仅整理 **2026 年** 文章（共 6 篇），源文件见 [`posts/source/guide/index.md`](posts/source/guide/index.md)，生成站点后为 `/guide/`。

- **交易系统**：状态机视角理解交易与资金履约（03-29）。
- **JaCoCo / 反射**：测试环境独有反射报错与插桩排查（04-04）。
- **JavaScript**：用框架分层再挂术语的学习路径（04-12）。
- **AI 与分层**：人类先框定分层与落点，AI 协作才稳（04-13）。
- **时序图与 Agent**：调用链心智模型与 Agent 范式失配（04-13）。
- **可复现输出**：temperature 等与稳定集成（04-18）。

## 建议保留

- `posts/`
  - Hexo 博客源码目录。
- `posts/source/_posts/`
  - 文章 Markdown 源文件（含按主题分子目录，如 `1. llm/`）。
- `posts/source/guide/index.md`
  - 阅读地图（当前为 2026 年发文索引与读法），站点生成后为 `/guide/` 页面。
- `posts/source/img/`
  - 全站共用图片；正文里用 `![](/img/文件名)` 引用。
- 与某篇帖子绑定的图片（`posts/_config.yml` 中 `post_asset_folder: true`）
  - 放在与该帖 `.md` **同名**的子目录下，正文中用 `{% asset_img 文件名 %}`（勿使用 Obsidian 的 `![[...]]` 语法）。
- `posts/_config.yml`
  - Hexo 主配置。
- `posts/_config.fluid.yml`
  - Fluid 主题配置。
- `posts/package.json`
  - 博客依赖和运行脚本。
- `posts/scaffolds/`
  - Hexo 草稿/文章模板。
- `.obsidian/`
  - 如果你仍然用 Obsidian 管理笔记就保留；不用的话可删。
- `template/`
  - 临时模板目录，只有在你还会继续使用时才建议保留。
- `chanonlee.github.io/`
  - 当前更像单独的发布仓库副本；如果不再手动维护发布副本，可以考虑删除。

## 明确可清理

- `posts/node_modules/`
  - 依赖安装目录，可通过 `npm install` 重新生成。
- `posts/public/`
  - Hexo 静态生成结果，可通过 `npm run build` 重新生成。
- `posts/.deploy_git/`
  - Hexo deploy 生成的发布目录，可重新部署生成。
- `**/.DS_Store`
  - macOS 缓存文件，可直接删除。

## 推荐的最小保留结构

只想保留“真正有价值的博客源码”时，建议至少保留这些：

- `posts/source/_posts/`
- `posts/source/img/`
- `posts/_config.yml`
- `posts/_config.fluid.yml`
- `posts/package.json`
- `posts/package-lock.json`
- `posts/scaffolds/`

## 常用命令

在 `posts/` 目录下执行：

- `npm install`
- `npm run server`
- `npm run build`
- `npm run deploy`
