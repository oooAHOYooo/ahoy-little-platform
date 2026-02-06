// Ahoy Indie Media - Haptics helper (Capacitor + web fallback)
(function () {
  const hasCapacitor = typeof window !== 'undefined' && !!window.Capacitor;
  const isNative = !!(hasCapacitor && typeof window.Capacitor.isNativePlatform === 'function' && window.Capacitor.isNativePlatform());
  const canVibrate = typeof navigator !== 'undefined' && typeof navigator.vibrate === 'function';

  const Haptics = hasCapacitor && window.Capacitor.Plugins ? window.Capacitor.Plugins.Haptics : null;
  const ImpactStyle = Haptics && (Haptics.ImpactStyle || window.Capacitor.Plugins.HapticsImpactStyle) ? (Haptics.ImpactStyle || window.Capacitor.Plugins.HapticsImpactStyle) : null;
  const NotificationType = Haptics && (Haptics.NotificationType || window.Capacitor.Plugins.HapticsNotificationType) ? (Haptics.NotificationType || window.Capacitor.Plugins.HapticsNotificationType) : null;

  const enabled = !!(isNative || canVibrate);

  function fallbackVibrate(ms) {
    if (!canVibrate) return;
    try { navigator.vibrate(ms); } catch (_) {}
  }

  function resolveImpactStyle(style) {
    if (!ImpactStyle) return style;
    return ImpactStyle[style] || ImpactStyle[style.toUpperCase()] || style;
  }

  function resolveNotificationType(type) {
    if (!NotificationType) return type;
    return NotificationType[type] || NotificationType[type.toUpperCase()] || type;
  }

  async function impact(style, fallbackMs) {
    if (!enabled) return;
    if (Haptics && typeof Haptics.impact === 'function') {
      try {
        await Haptics.impact({ style: resolveImpactStyle(style) });
        return;
      } catch (_) {}
    }
    fallbackVibrate(fallbackMs);
  }

  async function selection() {
    if (!enabled) return;
    if (Haptics && typeof Haptics.selectionChanged === 'function') {
      try {
        await Haptics.selectionChanged();
        return;
      } catch (_) {}
    }
    fallbackVibrate(6);
  }

  async function notification(type, fallbackMs) {
    if (!enabled) return;
    if (Haptics && typeof Haptics.notification === 'function') {
      try {
        await Haptics.notification({ type: resolveNotificationType(type) });
        return;
      } catch (_) {}
    }
    fallbackVibrate(fallbackMs);
  }

  window.ahoyHaptics = {
    enabled,
    impactLight: () => impact('Light', 10),
    impactMedium: () => impact('Medium', 16),
    selection,
    success: () => notification('Success', 20),
    error: () => notification('Error', 24)
  };

  // Optional: attribute-driven haptics for key actions
  document.addEventListener('click', (e) => {
    if (!enabled) return;
    const target = e.target && e.target.closest ? e.target.closest('[data-haptic]') : null;
    if (!target) return;
    const type = (target.getAttribute('data-haptic') || 'light').toLowerCase();
    if (type === 'selection') return window.ahoyHaptics.selection();
    if (type === 'medium') return window.ahoyHaptics.impactMedium();
    if (type === 'success') return window.ahoyHaptics.success();
    if (type === 'error') return window.ahoyHaptics.error();
    return window.ahoyHaptics.impactLight();
  });
})();
