<script setup>
import { ref, onMounted, computed } from 'vue'

const props = defineProps({
  font: {
    type: Object,
    required: true
  },
  previewText: {
    type: String,
    default: '字体预览 ABCD abcd 1234 岁月静好 设计之美'
  }
})

const loaded = ref(false)
const error = ref(false)

const fontFaceName = computed(() => `Font-${props.font.id}`)
const fontFamilyStyle = computed(() => loaded.value ? `"${fontFaceName.value}"` : 'sans-serif')
const downloadItems = computed(() => {
  const candidates = props.font.variants?.length
    ? [...props.font.variants, props.font]
    : [props.font]
  const seen = new Set()

  return candidates
    .filter((item) => item.originalPath && !seen.has(item.originalPath) && seen.add(item.originalPath))
    .map((item) => ({
      href: item.originalPath,
      filename: fontDownloadName(item)
    }))
})
const downloadButtonTitle = computed(() => {
  const count = downloadItems.value.length
  return count > 1 ? `下载全部 ${count} 个字体文件` : '下载完整字体'
})
const fontSize = computed(() => {
  const size = props.font.size
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / (1024 * 1024)).toFixed(2) + ' MB'
})

function fontDownloadName(fontItem) {
  const ext = fontItem.originalPath.split('.').pop() || 'ttf'
  return `${fontItem.name}.${ext}`
}

function triggerDownload(item) {
  const link = document.createElement('a')
  link.href = item.href
  link.download = item.filename
  link.rel = 'noopener'
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()

  window.setTimeout(() => {
    link.remove()
  }, 5000)
}

function downloadFontFiles() {
  downloadItems.value.forEach((item, index) => {
    if (index === 0) {
      triggerDownload(item)
      return
    }

    window.setTimeout(() => {
      triggerDownload(item)
    }, index * 500)
  })
}

onMounted(() => {
  const fontUrl = import.meta.env.BASE_URL + props.font.subsetPath
  const ff = new FontFace(fontFaceName.value, `url("${fontUrl}")`)
  ff.load()
    .then((loadedFace) => {
      document.fonts.add(loadedFace)
      loaded.value = true
    })
    .catch((err) => {
      console.error('Font load error:', props.font.name, err)
      error.value = true
    })
})
</script>

<template>
  <div class="font-card">
    <div class="card-header">
      <h3
        class="font-name"
        :class="{ 'has-tip': font.tip }"
        :title="font.tip || font.name"
      >
        {{ font.name }}
      </h3>
      <button
        type="button"
        class="download-btn"
        :title="downloadButtonTitle"
        @click.stop="downloadFontFiles"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        {{ downloadItems.length > 1 ? '下载全部' : '下载' }}
      </button>
    </div>
    <div
      class="preview"
      :style="{ fontFamily: fontFamilyStyle }"
    >
      <div v-if="!loaded && !error" class="loading">加载中...</div>
      <div v-else-if="error" class="error">字体加载失败</div>
      <div v-else class="preview-text">{{ previewText }}</div>
    </div>
    <div class="card-footer">
      <span class="font-meta">{{ font.category }}</span>
      <div v-if="font.variants?.length" class="variant-list">
        <a
          v-for="v in font.variants"
          :key="v.name"
          class="variant-pill"
          :href="v.originalPath"
          :download="fontDownloadName(v)"
          :title="`下载 ${v.name}`"
          @click.stop
        >
          {{ v.weight }}
        </a>
      </div>
      <span v-else class="font-meta">{{ fontSize }}</span>
    </div>
  </div>
</template>

<style scoped>
.font-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: box-shadow 0.2s, transform 0.2s;
}

.font-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.font-name {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.font-name.has-tip {
  cursor: help;
  text-decoration: underline dotted #9ca3af;
  text-underline-offset: 3px;
}

.download-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 0;
  font-family: inherit;
  font-size: 12px;
  color: #fff;
  background: #111827;
  padding: 4px 10px;
  border-radius: 6px;
  text-decoration: none;
  transition: background 0.2s;
  flex-shrink: 0;
  cursor: pointer;
}

.download-btn:hover {
  background: #374151;
}

.preview {
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  font-size: 22px;
  line-height: 1.4;
  color: #1f2937;
  word-break: break-all;
}

.preview-text {
  width: 100%;
  text-align: center;
}

.loading,
.error {
  font-size: 14px;
  color: #9ca3af;
}

.error {
  color: #ef4444;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #9ca3af;
}

.font-meta {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.font-meta:first-child {
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 999px;
  flex-shrink: 0;
}

.variant-list {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.variant-pill {
  font-size: 11px;
  color: #374151;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  padding: 2px 8px;
  border-radius: 999px;
  text-decoration: none;
  transition: background 0.15s, border-color 0.15s;
  white-space: nowrap;
}

.variant-pill:hover {
  background: #e5e7eb;
  border-color: #d1d5db;
}
</style>
