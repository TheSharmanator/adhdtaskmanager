(function() {
    const scales = {
        'small': '1.0',
        'medium': '1.39',
        'large': '2.08'
    };
    const savedSize = localStorage.getItem('ui_scale_pref') || 'small';
    const scaleVal = scales[savedSize] || '1.0';
    document.documentElement.style.setProperty('--ui-scale', scaleVal);
    
    // Fallback/direct scaling using zoom (works excellently in Chromium kiosk)
    document.documentElement.style.zoom = 'var(--ui-scale)';
})();
