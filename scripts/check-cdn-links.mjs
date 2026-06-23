import fonts from '../src/fonts.json' with { type: 'json' }

const CONCURRENCY = 8
const TIMEOUT_MS = 15000

function collectUrls() {
  const urls = new Map()

  for (const font of fonts) {
    if (font.originalPath) {
      urls.set(font.originalPath, font.name)
    }

    for (const variant of font.variants ?? []) {
      if (variant.originalPath) {
        urls.set(variant.originalPath, `${font.name} / ${variant.name}`)
      }
    }
  }

  return [...urls.entries()].map(([url, label]) => ({ url, label }))
}

async function request(url, method) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS)

  try {
    return await fetch(url, {
      method,
      headers: method === 'GET' ? { Range: 'bytes=0-0' } : {},
      redirect: 'follow',
      signal: controller.signal
    })
  } finally {
    clearTimeout(timeout)
  }
}

async function checkUrl(item) {
  try {
    let response = await request(item.url, 'HEAD')

    if (!response.ok || [403, 405, 501].includes(response.status)) {
      response = await request(item.url, 'GET')
    }

    return {
      ...item,
      ok: response.status === 200,
      status: response.status
    }
  } catch (error) {
    return {
      ...item,
      ok: false,
      status: 'ERROR',
      error: error instanceof Error ? error.message : String(error)
    }
  }
}

async function runPool(items) {
  const results = []
  let nextIndex = 0

  async function worker() {
    while (nextIndex < items.length) {
      const item = items[nextIndex]
      nextIndex += 1
      results.push(await checkUrl(item))
    }
  }

  await Promise.all(
    Array.from({ length: Math.min(CONCURRENCY, items.length) }, () => worker())
  )

  return results
}

const urls = collectUrls()
console.log(`Checking ${urls.length} CDN links...`)

const results = await runPool(urls)
const failures = results.filter((result) => !result.ok)

if (failures.length > 0) {
  console.warn(`⚠️  CDN link check warning: ${failures.length}/${results.length} links failed (non-blocking)`)

  for (const failure of failures) {
    const reason = failure.error ? `${failure.status} ${failure.error}` : failure.status
    console.warn(`- [${reason}] ${failure.label}`)
    console.warn(`  ${failure.url}`)
  }
} else {
  console.log(`CDN link check passed: ${results.length}/${results.length}`)
}

