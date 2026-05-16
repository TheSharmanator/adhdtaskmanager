(function() {
    const scales = {
        'small': '1.0',
        'medium': '1.0',
        'large': '1.39'
    };
    const savedSize = localStorage.getItem('ui_scale_pref') || 'small';
    const scaleVal = scales[savedSize] || '1.0';
    document.documentElement.style.setProperty('--ui-scale', scaleVal);
    
    // Fallback/direct scaling using zoom (works excellently in Chromium kiosk)
    document.documentElement.style.zoom = 'var(--ui-scale)';
    
    if (savedSize === 'medium') {
        const style = document.createElement('style');
        style.innerHTML = `
            .task-text { font-size: 2.08rem !important; }
            .task-deadline { font-size: 1.02rem !important; }
            .sub-text { font-size: 1.1rem !important; }
            .sub-deadline { font-size: 0.84rem !important; }
            
            header h1, header h2 { font-size: 2rem !important; }
            #clock-full { font-size: 1.75rem !important; }
            header .btn-touch, header .nuke-btn { font-size: 1.125rem !important; }
            header .settings-icon { font-size: 4rem !important; }
            header .tab { font-size: 1.06rem !important; }
            header .btn-header { font-size: 1.0rem !important; }
            
            .hg-button { font-size: 1.625rem !important; font-weight: bold !important; }
            .hg-button span { font-weight: bold !important; }
        `;
        document.head.appendChild(style);
    }
})();
