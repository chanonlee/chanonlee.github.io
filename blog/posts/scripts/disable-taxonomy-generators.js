'use strict';

const disabledGenerators = [
  ['archive', 'archive_generator'],
  ['category', 'category_generator'],
  ['tag', 'tag_generator']
];

hexo.extend.filter.register('before_generate', function () {
  const store = hexo.extend.generator.store;

  for (const [name, configKey] of disabledGenerators) {
    const cfg = hexo.config[configKey];
    if (cfg && cfg.enabled === false && store[name]) {
      delete store[name];
    }
  }
});
