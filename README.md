# Arno 字体库展示

一个基于 **Vue 3 + Vite** 的字体展示应用，用于以卡片形式浏览、预览和下载字体文件。支持字体重量子集化压缩、家族字重合并、实时预览和分类筛选。

## 在线预览

> 部署后即可通过浏览器访问，所有字体数据通过 `fonts-config.json` 动态加载。

## 核心功能

- **字体卡片网格**：每款字体独立成卡，自动按家族合并多字重版本（如 Alibaba-PuHuiTi、思源黑体等）。
- **子集化预览**：使用 `fontTools.subset` 将每款字体裁剪为仅含固定预览字符的 WOFF2 子集，大幅缩减加载体积。
- **动态加载配置**：运行时通过 `fetch('/fonts-config.json')` 读取字体列表，无需重新打包即可增删或调整字体。
- **搜索与筛选**：支持按字体名称搜索、按风格分类（黑体/圆体/楷体/手写等）筛选。
- **自定义预览文字**：顶部输入框可实时修改所有卡片的预览内容。
- **一键下载**：每张卡片提供下载按钮，可获取字体的**完整原始文件**。

## 技术栈

- **前端**：Vue 3 (Composition API) + Vite
- **字体加载**：原生 `FontFace API`
- **字体子集化**：Python + `fontTools`

## 项目结构

```
font-showcase/
├── public/
│   ├── fonts-config.json       # 运行时字体配置文件（由脚本自动生成）
│   ├── subsets/                # 子集化后的 WOFF2 字体（预览用）
│   ├── originals/              # 原始完整字体文件（下载用）
│   └── fonts/                  # 子集化失败时的回退字体
├── scripts/
│   └── generate-font-data.py   # 字体扫描、子集化、配置生成脚本
├── src/
│   ├── components/
│   │   └── FontCard.vue        # 字体卡片组件
│   ├── App.vue                 # 主页面（搜索/筛选/网格布局）
│   ├── fonts.json              # 构建时备份的配置副本
│   └── main.js
├── index.html
└── package.json
```

## 快速开始

### 1. 安装依赖

```bash
cd font-showcase
npm install
```

### 2. 开发模式

```bash
npm run dev
```

### 3. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

## 添加新字体

1. 将字体文件（`.ttf` / `.otf` / `.woff` / `.woff2`）放入任意一个脚本已配置的源目录中（默认为 `Arno字体库` 和 `E:\下载\font等122个文件\font`）。
2. 运行生成脚本：

```bash
python scripts/generate-font-data.py
```

脚本会自动完成：
- 扫描新增字体
- 生成 WOFF2 子集到 `public/subsets/`
- 复制原始文件到 `public/originals/`
- 更新 `public/fonts-config.json` 和 `src/fonts.json`

3. 重新构建前端：

```bash
npm run build
```

## 配置说明

`public/fonts-config.json` 是应用运行时的唯一数据源，单条记录格式如下：

```json
{
  "id": "arno_中文字体_黑体_Alibaba-PuHuiTi",
  "name": "Alibaba-PuHuiTi",
  "category": "黑体",
  "originalPath": "originals/arno_中文字体_黑体_阿里巴巴普惠体_Alibaba-PuHuiTi-Regular.ttf",
  "optimizedPath": "subsets/arno_中文字体_黑体_阿里巴巴普惠体_Alibaba-PuHuiTi-Regular.woff2",
  "size": 4800,
  "variants": [
    {
      "name": "Alibaba-PuHuiTi-Bold",
      "weight": "Bold",
      "originalPath": "originals/...",
      "optimizedPath": "subsets/...",
      "size": 4760
    }
  ]
}
```

字段说明：
- `originalPath`：完整字体文件的下载路径
- `optimizedPath`：轻量子集字体的预览路径
- `variants`：同系列不同字重的变体列表（单字重字体无此字段）

## 部署到 GitHub Pages

### 方式一：手动推送 dist

```bash
npm run build
cd dist
git init
git add .
git commit -m "Deploy"
git branch -M gh-pages
git remote add origin https://github.com/<USERNAME>/<REPO>.git
git push -f origin gh-pages
```

### 方式二：GitHub Actions 自动部署

在仓库中创建 `.github/workflows/deploy.yml`，参考配置：

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm ci
      - run: npm run build
      - uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

> **注意**：GitHub Pages 默认不发布以 `_` 开头的文件或路径。如果你的构建产物中有这类文件，可能需要关闭 Jekyll（在 `public` 下放置一个空文件 `.nojekyll`）。

## 分类规则

当前应用支持以下字体风格分类：

- 黑体、圆体、楷体、宋体、仿宋
- 手写、书法
- 西文、等宽
- 像素字体、艺术字体
- 特殊字体、趣味体、标题黑

分类由 `scripts/generate-font-data.py` 中的 `classify_font()` 函数根据**文件路径和字体名称**自动推断。

## 版权与许可

- **本项目代码**：MIT License（可自由修改和分发）。
- **字体文件**：本仓库中所有 `.ttf` / `.otf` / `.woff2` 字体文件版权归原作者所有，仅供个人学习与交流使用。如需商用，请遵守各字体自身的授权协议（如 SIL Open Font License、方正字库授权协议、阿里普惠体商用协议等）。

## 致谢

- [Vue.js](https://vuejs.org/)
- [Vite](https://vitejs.dev/)
- [fontTools](https://github.com/fonttools/fonttools)
