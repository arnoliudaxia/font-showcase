# 字体库展示

一个基于 **Vue 3 + Vite** 的字体展示应用，用于以卡片形式浏览、预览和下载字体文件。支持多级分类树、字体重量子集化压缩、家族字重合并、实时预览和 CDN 原始文件下载。

## 核心功能

- **多级分类树**：分类直接映射 `字体库/` 目录的文件夹层级（如 `中文字体/黑体/思源黑体`），支持面包屑导航与逐层筛选。
- **字体卡片网格**：每款字体独立成卡，自动按家族合并多字重版本（如 Alibaba-PuHuiTi、HONORSansCN、思源黑体等）。
- **子集化预览**：使用 `fontTools.subset` 将每款字体裁剪为仅含固定预览字符的 WOFF2 子集，大幅缩减加载体积。
- **静态数据构建**：字体列表在构建时通过 `src/fonts.json` 静态导入，保证首屏加载速度和确定性。
- **自定义预览文字**：顶部输入框可实时修改所有卡片的预览内容。
- **一键下载原始字体**：下载按钮直接指向 CDN 直链，不占用仓库与部署包体积。

## 技术栈

- **前端**：Vue 3 (Composition API) + Vite
- **字体加载**：原生 `FontFace API`
- **字体子集化**：Python + `fontTools`

## 项目结构

```
font-showcase/
├── 字体库/                      # 本地字体源目录（仅用于生成子集，不提交到 Git）
│   ├── 中文字体/
│   ├── 英文字体/
│   ├── 思源/
│   └── ...
├── public/
│   ├── subsets/                 # 子集化后的 WOFF2 字体（预览用）
│   ├── fonts/                   # 子集化失败时的回退字体
│   └── fonts-config.json        # 历史遗留的运行时配置（可选）
├── scripts/
│   └── generate-font-data.py    # 扫描 字体库/、生成子集、输出 src/fonts.json
├── src/
│   ├── components/
│   │   └── FontCard.vue         # 字体卡片组件
│   ├── App.vue                  # 主页面（搜索 / 分类树 / 网格布局）
│   ├── fonts.json               # 构建时静态导入的字体数据源
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

### 步骤 1：放入本地源目录

将字体文件（`.ttf` / `.otf` / `.woff` / `.woff2`）放入 `字体库/` 下的任意子目录中。目录层级即为网页上的分类层级。

### 步骤 2：运行生成脚本

```bash
python scripts/generate-font-data.py
```

脚本会自动完成：
- 扫描 `字体库/` 下的全部字体
- 生成 WOFF2 子集到 `public/subsets/`
- 对子集化失败的字体回退到 `public/fonts/`
- 更新 `src/fonts.json`，并将 `originalPath` 自动映射为 CDN 直链

### 步骤 3：上传原始字体到 CDN

当前 `originalPath` 的 CDN 基础地址为：

```
https://1812331343.v.123pan.cn/1812331343/%E7%9B%B4%E9%93%BE%E5%8A%A0%E9%80%9F/font/
```

你需要将 `字体库/` 中的原始字体文件按**相同的相对目录结构**上传到该 CDN 空间。例如：

- 本地：`字体库/英文字体/手写/Inkfree.ttf`
- CDN：`https://1812331343.v.123pan.cn/1812331343/%E7%9B%B4%E9%93%BE%E5%8A%A0%E9%80%9F/font/%E8%8B%B1%E6%96%87%E5%AD%97%E4%BD%93/%E6%89%8B%E5%86%99/Inkfree.ttf`

### 步骤 4：重新构建前端

```bash
npm run build
```

## 数据格式说明

`src/fonts.json` 是应用构建时的唯一数据源，单条记录格式如下：

```json
{
  "id": "中文字体_黑体_HONORSansCN-Regular",
  "name": "HONORSansCN-Regular",
  "category": "中文字体/黑体/HONORSansCN",
  "originalPath": "https://1812331343.v.123pan.cn/.../HONORSansCN-Regular.ttf",
  "subsetPath": "subsets/中文字体_黑体_HONORSansCN_HONORSansCN-Regular.woff2",
  "size": 4872,
  "variants": [
    {
      "name": "HONORSansCN-Bold",
      "weight": "Bold",
      "originalPath": "https://1812331343.v.123pan.cn/.../HONORSansCN-Bold.ttf",
      "subsetPath": "subsets/...",
      "size": 4896
    }
  ]
}
```

字段说明：
- `category`：多级分类路径，对应 `字体库/` 的目录层级
- `originalPath`：完整原始字体文件的 CDN 下载链接
- `subsetPath`：轻量子集字体的本地预览路径
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

在仓库中创建 `.github/workflows/deploy.yml`：

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

> **注意**：GitHub Pages 默认不发布以 `_` 开头的文件或路径。如果构建产物中有这类文件，建议在 `public` 下放置一个空文件 `.nojekyll`。

## 版权与许可

- **本项目代码**：MIT License（可自由修改和分发）。
- **字体文件**：本仓库及 CDN 上所有 `.ttf` / `.otf` / `.woff2` 字体文件版权归原作者所有，仅供个人学习与交流使用。如需商用，请遵守各字体自身的授权协议（如 SIL Open Font License、方正字库授权协议、阿里普惠体商用协议等）。

## 致谢

- [Vue.js](https://vuejs.org/)
- [Vite](https://vitejs.dev/)
- [fontTools](https://github.com/fonttools/fonttools)
