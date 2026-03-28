# blog 仓库说明

这个目录本质上是一个个人技术博客工作区，核心站点在 `posts/`。

## 建议保留

- `posts/`
  - Hexo 博客源码目录。
- `posts/source/_posts/`
  - 文章 Markdown 源文件。
- `posts/source/img/`
  - 文章图片资源。
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
