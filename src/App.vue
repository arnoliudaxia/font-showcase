<script setup>
import { ref, computed } from 'vue'
import FontCard from './components/FontCard.vue'
import fontsData from './fonts.json'

const search = ref('')
const selectedCategory = ref('')
const previewText = ref('字体预览 ABCD abcd 1234 岁月静好 设计之美')

// 收集所有存在的分类节点（包括中间层级）
const allCategoryNodes = computed(() => {
  const nodes = new Set()
  fontsData.forEach((font) => {
    const parts = font.category.split('/')
    let path = ''
    parts.forEach((part) => {
      path = path ? `${path}/${part}` : part
      nodes.add(path)
    })
  })
  return nodes
})

// 当前层级下直接的子分类
const currentSubCategories = computed(() => {
  const subs = new Set()
  const prefix = selectedCategory.value ? selectedCategory.value + '/' : ''
  allCategoryNodes.value.forEach((node) => {
    if (selectedCategory.value === '') {
      // 第一级：取第一个斜杠前的部分
      const first = node.split('/')[0]
      subs.add(first)
    } else if (node.startsWith(prefix) && node !== selectedCategory.value) {
      // 取下一级的名称
      const rest = node.slice(prefix.length)
      const next = rest.split('/')[0]
      subs.add(next)
    }
  })
  return Array.from(subs).sort()
})

// 面包屑路径
const breadcrumb = computed(() => {
  if (!selectedCategory.value) return []
  return selectedCategory.value.split('/')
})

const filteredFonts = computed(() => {
  return fontsData.filter((font) => {
    const matchesSearch =
      font.name.toLowerCase().includes(search.value.toLowerCase()) ||
      font.category.toLowerCase().includes(search.value.toLowerCase())
    const matchesCategory =
      selectedCategory.value === '' ||
      font.category === selectedCategory.value ||
      font.category.startsWith(selectedCategory.value + '/')
    return matchesSearch && matchesCategory
  })
})

const stats = computed(() => {
  const total = fontsData.length
  const subsetCount = fontsData.filter((f) => f.subsetPath.startsWith('subsets/')).length
  const totalSubsetSize = fontsData.reduce((sum, f) => sum + (f.size || 0), 0)
  return {
    total,
    subsetCount,
    fallbackCount: total - subsetCount,
    totalSubsetSize
  }
})

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

function selectCategory(cat) {
  selectedCategory.value = cat
}

function goUp() {
  if (!selectedCategory.value) return
  const parts = selectedCategory.value.split('/')
  parts.pop()
  selectedCategory.value = parts.join('/')
}

function goToIndex(index) {
  const parts = selectedCategory.value.split('/')
  selectedCategory.value = parts.slice(0, index + 1).join('/')
}
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <h1>字体库展示</h1>
      <p class="subtitle">
        共收录 {{ stats.total }} 款字体，子集化优化 {{ stats.subsetCount }} 款
      </p>

      <div class="controls">
        <input
          v-model="search"
          type="text"
          class="search-input"
          placeholder="搜索字体名称或分类..."
        />
        <input
          v-model="previewText"
          type="text"
          class="preview-input"
          placeholder="输入预览文字..."
        />
      </div>

      <!-- 层级分类导航 -->
      <div class="category-nav">
        <div class="breadcrumb">
          <button
            class="breadcrumb-item"
            :class="{ active: selectedCategory === '' }"
            @click="selectCategory('')"
          >
            全部
          </button>
          <template v-for="(crumb, index) in breadcrumb" :key="index">
            <span class="breadcrumb-separator">/</span>
            <button
              class="breadcrumb-item"
              :class="{ active: index === breadcrumb.length - 1 }"
              @click="goToIndex(index)"
            >
              {{ crumb }}
            </button>
          </template>
        </div>

        <div class="category-list">
          <button
            v-if="selectedCategory !== ''"
            class="category-btn back"
            @click="goUp"
          >
            ⬅ 返回上一级
          </button>
          <button
            v-for="cat in currentSubCategories"
            :key="cat"
            class="category-btn"
            @click="selectCategory(selectedCategory ? `${selectedCategory}/${cat}` : cat)"
          >
            {{ cat }}
          </button>
        </div>
      </div>
    </header>

    <main class="fonts-grid">
      <FontCard
        v-for="font in filteredFonts"
        :key="font.id"
        :font="font"
        :preview-text="previewText"
      />
    </main>

    <footer class="app-footer">
      <p>
        总计 {{ stats.total }} 款字体 · 子集化 {{ stats.subsetCount }} 款 · 回退 {{ stats.fallbackCount }} 款
        · 子集总体积 {{ formatSize(stats.totalSubsetSize) }}
      </p>
    </footer>
  </div>
</template>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f3f4f6;
  color: #111827;
}

.app-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.app-header {
  text-align: center;
  margin-bottom: 24px;
}

.app-header h1 {
  margin: 0 0 8px;
  font-size: 32px;
  font-weight: 700;
}

.subtitle {
  margin: 0 0 20px;
  color: #6b7280;
  font-size: 15px;
}

.controls {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.search-input,
.preview-input {
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 15px;
  outline: none;
  min-width: 220px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-input:focus,
.preview-input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.category-nav {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
  font-size: 14px;
  color: #6b7280;
}

.breadcrumb-item {
  background: none;
  border: none;
  padding: 4px 8px;
  cursor: pointer;
  color: #374151;
  border-radius: 4px;
  transition: background 0.2s;
}

.breadcrumb-item:hover {
  background: #e5e7eb;
}

.breadcrumb-item.active {
  font-weight: 600;
  color: #111827;
  background: #e5e7eb;
}

.breadcrumb-separator {
  color: #d1d5db;
}

.category-list {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.category-btn {
  padding: 6px 14px;
  border: 1px solid #e5e7eb;
  background: #fff;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  color: #374151;
}

.category-btn:hover {
  border-color: #c7c7c7;
  background: #f9fafb;
}

.category-btn.back {
  background: #f3f4f6;
  border-color: #e5e7eb;
  color: #6b7280;
}

.fonts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.app-footer {
  text-align: center;
  margin-top: 32px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
  font-size: 13px;
  color: #9ca3af;
}

@media (max-width: 640px) {
  .app-container {
    padding: 16px;
  }

  .app-header h1 {
    font-size: 24px;
  }

  .fonts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
