const fs = require('fs');
const path = require('path');

hexo.extend.filter.register('after_generate', function () {
  const sourceImgDir = path.join(hexo.source_dir, 'img');
  const publicImgDir = path.join(hexo.public_dir, 'img');

  if (!fs.existsSync(sourceImgDir)) {
    return;
  }

  fs.mkdirSync(publicImgDir, { recursive: true });
  fs.cpSync(sourceImgDir, publicImgDir, { recursive: true, force: true });
});
