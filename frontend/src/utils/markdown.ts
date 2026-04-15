import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

const md = new MarkdownIt({
  html: false,
  linkify: true,
  highlight: function (str: string, lang: string) {
    let highlighted: string
    if (lang && hljs.getLanguage(lang)) {
      try {
        highlighted = hljs.highlight(str, { language: lang }).value
      } catch {
        highlighted = str
      }
    } else {
      highlighted = hljs.highlightAuto(str).value
    }

    // 添加语言标签和复制按钮（使用 data 属性）
    const langLabel = lang ? `<span class="code-lang">${lang.toUpperCase()}</span>` : ''
    const copyBtn = `<button class="copy-btn" data-code="${encodeURIComponent(str)}">复制</button>`

    return `<pre class="code-block"><div class="code-header">${langLabel}${copyBtn}</div><code class="hljs">${highlighted}</code></pre>`
  }
})

export function renderMarkdown(content: string): string {
  return md.render(content)
}

export function extractSql(content: string): string | null {
  const match = content.match(/```sql\s*(.*?)\s*```/i)
  if (match) {
    return match[1].trim()
  }
  return null
}

// 初始化复制按钮事件监听
export function initCopyButtons() {
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', function(this: HTMLButtonElement) {
      const code = decodeURIComponent(this.getAttribute('data-code') || '')
      navigator.clipboard.writeText(code).then(() => {
        this.textContent = '已复制'
        this.classList.add('copied')
        setTimeout(() => {
          this.textContent = '复制'
          this.classList.remove('copied')
        }, 2000)
      })
    })
  })
}