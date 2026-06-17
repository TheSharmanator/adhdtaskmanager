(function() {
    const scales = {
        'small':  '1.0',   // 800 css-px virtual width (base design)
        'medium': '1.5',   // 1280 css-px → ~1280px wide screens
        'large':  '2.4'    // 800×2.4=1920px wide, 480×2.4=1152px — correct for 1920×1080
    };
    const savedSize = localStorage.getItem('ui_scale_pref') || 'small';
    document.documentElement.style.zoom = scales[savedSize] || '1.0';
})();
