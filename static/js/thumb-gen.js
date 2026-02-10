/**
 * Generate a branded canvas thumbnail when an image fails to load.
 * Usage:
 *   <img @error="ahoyThumbGen(this, 'Title', 'category')" ...>
 *   <img onerror="ahoyThumbGen(this, 'Title', 'category')" ...>
 *
 * Or from JS:
 *   img.onerror = () => ahoyThumbGen(img, title, category);
 */
(function () {
  'use strict';

  function generate(img, title, category) {
    if (img.dataset.thumbGenerated) return; // prevent infinite loop
    img.dataset.thumbGenerated = '1';

    title = title || 'Ahoy';
    category = category || '';
    var w = 640, h = 360;
    var canvas = document.createElement('canvas');
    canvas.width = w; canvas.height = h;
    var ctx = canvas.getContext('2d');

    // Gradient background
    var grad = ctx.createLinearGradient(0, 0, w, h);
    grad.addColorStop(0, '#1a1a2e');
    grad.addColorStop(0.5, '#16213e');
    grad.addColorStop(1, '#0f3460');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // Subtle pattern overlay
    ctx.globalAlpha = 0.06;
    for (var i = 0; i < w; i += 20) {
      for (var j = 0; j < h; j += 20) {
        if ((i + j) % 40 === 0) {
          ctx.fillStyle = '#fff';
          ctx.fillRect(i, j, 10, 10);
        }
      }
    }
    ctx.globalAlpha = 1;

    // Category badge
    if (category) {
      ctx.font = 'bold 14px -apple-system, BlinkMacSystemFont, sans-serif';
      var badge = category.toUpperCase();
      var bw = ctx.measureText(badge).width + 20;
      ctx.fillStyle = 'rgba(244, 114, 182, 0.25)';
      ctx.beginPath();
      ctx.roundRect(30, h - 90, bw, 26, 6);
      ctx.fill();
      ctx.fillStyle = '#f472b6';
      ctx.fillText(badge, 40, h - 70);
    }

    // Title text (word-wrapped, last 2 lines at bottom)
    ctx.font = 'bold 22px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.fillStyle = '#f1f5f9';
    var words = title.replace(/\[|\]/g, '').split(' ');
    var line = '', lines = [];
    for (var k = 0; k < words.length; k++) {
      var test = line ? line + ' ' + words[k] : words[k];
      if (ctx.measureText(test).width > w - 80) {
        lines.push(line);
        line = words[k];
      } else {
        line = test;
      }
    }
    if (line) lines.push(line);
    var show = lines.slice(-2);
    var y = h - (category ? 55 : 70);
    for (var m = show.length - 1; m >= 0; m--) {
      ctx.fillText(show[m], 30, y);
      y -= 28;
    }

    // Ahoy branding
    ctx.font = '12px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.fillStyle = 'rgba(255,255,255,0.4)';
    ctx.fillText('AHOY INDIE MEDIA', 30, 30);

    img.src = canvas.toDataURL('image/jpeg', 0.85);
  }

  window.ahoyThumbGen = generate;
})();
