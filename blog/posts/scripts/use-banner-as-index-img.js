'use strict';

hexo.extend.filter.register('before_post_render', function (data) {
  if (data.layout !== 'post') {
    return data;
  }

  // Reuse the post banner as the index cover so article images appear on
  // list pages without changing every post front matter by hand.
  if (data.banner_img && !data.index_img) {
    data.index_img = data.banner_img;
  }

  if (data.banner_img && !data.og_img) {
    data.og_img = data.banner_img;
  }

  return data;
});
