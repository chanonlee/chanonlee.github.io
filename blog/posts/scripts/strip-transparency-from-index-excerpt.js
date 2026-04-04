'use strict';

/**
 * 首页列表摘要会取 post.content 的前 200 字，正文开头的「创作透明度 / 本文标注」
 * 说明块会占满摘要。在渲染完成的 HTML 上从 index-excerpt 中去掉这一段。
 */
function stripTransparencyBlock(text) {
  if (!text || !text.includes('创作透明度')) {
    return text;
  }
  // 去掉图例行 + 「本文标注：…」直到与正文之间的空白（通常 ≥3 个空格）
  let s = text.replace(
    /创作透明度[：:][\s\S]*?本文标注[：:][\s\S]*?\s{3,}/g,
    ''
  );
  // 若格式略有不同，再尝试只去掉创作透明度整段（无「本文标注」时）
  if (s.includes('创作透明度')) {
    s = s.replace(/创作透明度[：:][\s\S]*?(?=\s{2,}[\u4e00「「])/g, '');
  }
  return s.trim();
}

hexo.extend.filter.register(
  'after_render:html',
  function (html, locals) {
    if (!html || typeof html !== 'string' || !html.includes('index-excerpt')) {
      return html;
    }
    if (!html.includes('创作透明度')) {
      return html;
    }

    return html.replace(
      /(<a class="index-excerpt[^"]*"[^>]*>\s*<div>\s*)([\s\S]*?)(\s*<\/div>\s*<\/a>)/g,
      (full, open, body, close) => {
        if (!body.includes('创作透明度')) {
          return full;
        }
        return open + stripTransparencyBlock(body) + close;
      }
    );
  },
  20
);
