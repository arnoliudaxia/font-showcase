<script setup>
import { ref, onMounted, computed, watch } from 'vue'

const props = defineProps({
  font: {
    type: Object,
    required: true
  },
  previewText: {
    type: String,
    default: '字体预览 ABCD abcd 1234 岁月静好 设计之美'
  },
  scale: {
    type: Number,
    default: 1
  }
})

const loaded = ref(false)
const error = ref(false)
const activePreviewKey = ref(defaultPreviewKey())
const displayFontFaceName = ref('')
let loadRequestId = 0

const activePreviewItem = computed(() => {
  return props.font.variants?.find((variant) => variantKey(variant) === activePreviewKey.value) || props.font
})
const fontFaceName = computed(() => {
  const key = activePreviewItem.value.subsetPath || activePreviewItem.value.name
  return `Font-${props.font.id}-${hashString(key)}`
})
const fontFamilyStyle = computed(() => displayFontFaceName.value ? `"${displayFontFaceName.value}"` : 'sans-serif')
const cardStyle = computed(() => ({
  '--card-scale': props.scale
}))
const previewContent = computed(() => {
  if (props.font.supportsChinese !== false) return props.previewText

  return props.previewText
    .replace(/[\p{Script=Han}\u3000-\u303f\uff00-\uffef]/gu, '')
    .replace(/\s+/g, ' ')
    .trim()
})
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
  return count > 1
    ? `下载全部 ${count} 个字体文件。首次批量下载时，浏览器可能需要允许本站下载多个文件。`
    : '下载完整字体'
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

function hashString(value) {
  let hash = 0
  for (let i = 0; i < value.length; i += 1) {
    hash = ((hash << 5) - hash + value.charCodeAt(i)) | 0
  }
  return Math.abs(hash).toString(36)
}

function variantKey(variant) {
  return `${variant.name}|${variant.subsetPath}`
}

function defaultPreviewKey() {
  const matchingVariant = props.font.variants?.find((variant) => {
    return variant.subsetPath === props.font.subsetPath && variant.originalPath === props.font.originalPath
  })
  return variantKey(matchingVariant || props.font)
}

function selectPreviewVariant(variant) {
  activePreviewKey.value = variantKey(variant)
}

function loadPreviewFont() {
  const currentRequestId = ++loadRequestId
  const hasDisplayFont = Boolean(displayFontFaceName.value)
  loaded.value = hasDisplayFont
  error.value = false

  const fontUrl = import.meta.env.BASE_URL + activePreviewItem.value.subsetPath
  const ff = new FontFace(fontFaceName.value, `url("${fontUrl}")`)
  ff.load()
    .then((loadedFace) => {
      if (currentRequestId !== loadRequestId) return
      document.fonts.add(loadedFace)
      displayFontFaceName.value = fontFaceName.value
      loaded.value = true
    })
    .catch((err) => {
      if (currentRequestId !== loadRequestId) return
      console.error('Font load error:', activePreviewItem.value.name, err)
      error.value = true
    })
}

watch(
  () => props.font.id,
  () => {
    activePreviewKey.value = defaultPreviewKey()
  }
)

watch(activePreviewKey, loadPreviewFont)

onMounted(() => {
  loadPreviewFont()
})
</script>

<template>
  <div class="font-card" :style="cardStyle">
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
      <div v-else class="preview-text">{{ previewContent }}</div>
    </div>
    <div class="card-footer">
      <span class="font-meta">{{ font.category }}</span>
      <div v-if="font.variants?.length" class="variant-list">
        <button
          v-for="v in font.variants"
          :key="v.name"
          type="button"
          class="variant-pill"
          :class="{ active: activePreviewKey === variantKey(v) }"
          :title="`预览 ${v.name}`"
          @click.stop="selectPreviewVariant(v)"
        >
          {{ v.weight }}
        </button>
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
  padding: calc(16px * var(--card-scale));
  display: flex;
  flex-direction: column;
  gap: calc(12px * var(--card-scale));
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
  font-size: calc(15px * var(--card-scale));
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
  gap: calc(4px * var(--card-scale));
  border: 0;
  font-family: inherit;
  font-size: calc(12px * var(--card-scale));
  color: #fff;
  background: #111827;
  padding: calc(4px * var(--card-scale)) calc(10px * var(--card-scale));
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
  min-height: calc(80px * var(--card-scale));
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9fafb;
  border-radius: 8px;
  padding: calc(16px * var(--card-scale));
  font-size: calc(22px * var(--card-scale));
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
  font-size: calc(14px * var(--card-scale));
  color: #9ca3af;
}

.error {
  color: #ef4444;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: calc(8px * var(--card-scale));
  font-size: calc(12px * var(--card-scale));
  color: #9ca3af;
}

.font-meta {
  min-width: 0;
  white-space: normal;
  overflow-wrap: anywhere;
  line-height: 1.35;
}

.font-meta:first-child {
  color: #6b7280;
  flex: 1 1 auto;
}

.variant-list {
  display: flex;
  align-items: center;
  gap: calc(6px * var(--card-scale));
  flex-wrap: wrap;
  justify-content: flex-end;
  flex: 0 1 45%;
  min-width: calc(72px * var(--card-scale));
}

.variant-pill {
  appearance: none;
  font-family: inherit;
  font-size: calc(11px * var(--card-scale));
  color: #374151;
  background: #fff;
  border: 1px solid #e5e7eb;
  padding: calc(2px * var(--card-scale)) calc(8px * var(--card-scale));
  border-radius: 999px;
  text-decoration: none;
  transition: background 0.15s, border-color 0.15s;
  white-space: nowrap;
  cursor: pointer;
}

.variant-pill:hover,
.variant-pill.active {
  background: #e5e7eb;
  border-color: #d1d5db;
}

.variant-pill.active {
  color: #111827;
}
</style>
