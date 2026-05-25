(() => {
    const root = document.documentElement;
    const template = root.getAttribute('data-template') || 'vertical-menu-template';
    const storedTheme = localStorage.getItem(`templateCustomizer-${template}--Theme`);
    if (storedTheme) {
        const theme = storedTheme === 'system'
            ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
            : storedTheme;
        root.setAttribute('data-bs-theme', theme);
    }
    const storedColor = localStorage.getItem(`templateCustomizer-${template}--Color`);
    if (storedColor && storedColor !== '#7367f0') {
        const r = parseInt(storedColor.slice(1, 3), 16);
        const g = parseInt(storedColor.slice(3, 5), 16);
        const b = parseInt(storedColor.slice(5, 7), 16);
        const s = document.createElement('style');
        s.id = 'custom-css-preview';
        s.textContent = `:root{--bs-primary:${storedColor};--bs-primary-rgb:${r},${g},${b}}`;
        document.head.appendChild(s);
    }
})();

(function () {
    // ──────────────────────────────────────────────
    // Auto-logout
    // ──────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        var hdnAutoLogout = document.getElementById('hdn_AUTO_LOGOUT');
        var alertEl = document.getElementById('alert-auto-logout');
        var autoLogout_SS = hdnAutoLogout && hdnAutoLogout.value.toLowerCase() === 'true';
        if (alertEl && autoLogout_SS) {
            var HOURS = 6;
            var logoutTime = HOURS * 60 * 60 * 1000;
            var warningTime = logoutTime - (5 * 60 * 1000);

            // Testing timings (uncomment to test)
            // logoutTime = 10 * 1000;
            // warningTime = 5 * 1000;

            var inactivityTimeout, warningTimeout;
            function resetTimer() {
                clearTimeout(inactivityTimeout);
                clearTimeout(warningTimeout);
                alertEl.style.display = 'none';
                warningTimeout = setTimeout(function () { alertEl.style.display = 'block'; }, warningTime);
                inactivityTimeout = setTimeout(function () { window.location.href = '/auto-logout/'; }, logoutTime);
            }
            ['mousemove', 'keypress', 'keydown', 'click', 'scroll', 'touchstart'].forEach(function (evt) {
                document.addEventListener(evt, resetTimer, { passive: true });
            });
            resetTimer();
        }
    });

    // ──────────────────────────────────────────────
    // Right-click / DevTools disable
    // ──────────────────────────────────────────────
    var hdnIsRunServer = document.getElementById('hdn_IS_RunServer');
    var isRunServer_SS = hdnIsRunServer && hdnIsRunServer.value.toLowerCase() === 'true';
    if (document.documentElement.hasAttribute('data-disable-devtools') && isRunServer_SS) {
        debugger
        document.addEventListener('contextmenu', function (e) { e.preventDefault(); });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'F12' ||
                (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i' || e.key === 'J' || e.key === 'j' || e.key === 'C' || e.key === 'c')) ||
                (e.ctrlKey && e.key === 'U' || e.key === 'u')) {
                e.preventDefault();
            }
        });
    }

    // ──────────────────────────────────────────────
    // Loading spinner
    // ──────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('form').forEach(function (form) {
            form.addEventListener('submit', function (e) {
                var btn = this.querySelector('.loading_spinner');
                if (!btn) return;
                if (btn.dataset.loadingActive) { e.preventDefault(); return; }
                btn.dataset.loadingActive = '1';
                btn.dataset.originalHtml = btn.innerHTML;
                setTimeout(function () {
                    btn.disabled = true;
                    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Processing..';
                }, 10);
                setTimeout(function () {
                    btn.disabled = false;
                    btn.innerHTML = btn.dataset.originalHtml;
                    btn.dataset.loadingActive = '';
                }, 3000);
            });
        });
    });

    // ──────────────────────────────────────────────
    // Global search
    // ──────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        var input = document.getElementById('globalSearchInput');
        var results = document.getElementById('globalSearchResults');
        if (!input || !results) return;

        var timer;
        function escapeHtml(str) {
            var div = document.createElement('div');
            div.appendChild(document.createTextNode(str));
            return div.innerHTML;
        }

        input.addEventListener('input', function () {
            clearTimeout(timer);
            var val = this.value.trim();
            if (val.length < 3) { results.style.display = 'none'; return; }
            timer = setTimeout(function () {
                fetch('/search/global/?q=' + encodeURIComponent(val), {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                }).then(function (r) { return r.json(); }).then(function (data) {
                    var html = '';
                    var total = 0;
                    for (var key in data.results) {
                        var section = data.results[key];
                        if (!section.items || section.items.length === 0) continue;
                        var label = key.replace(/_/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
                        total += section.items.length;
                        html += '<div class="search-section-header"><i class="ti ' + section.icon + ' me-1"></i>' + label + '</div>';
                        section.items.forEach(function (item) {
                            html += '<a class="search-item" href="' + item.url + '">' +
                                '<i class="ti ' + item.icon + '"></i>' +
                                '<span>' + escapeHtml(item.label) + '</span></a>';
                        });
                    }
                    if (total === 0) html = '<div class="search-empty">No results found for "<strong>' + escapeHtml(val) + '</strong>"</div>';
                    results.innerHTML = html;
                    results.style.display = 'block';
                });
            }, 250);
        });

        document.addEventListener('click', function (e) {
            if (!input.contains(e.target) && !results.contains(e.target)) results.style.display = 'none';
        });
    });
})();

(function () {
        var loader = document.getElementById('content-loader');
        function hideLoader() {
            if (!loader) return;
            loader.style.opacity = '0';
            setTimeout(function () { loader.style.display = 'none'; }, 220);
        }
        function showLoader() {
            if (!loader) return;
            loader.style.display = 'flex';
            loader.style.opacity = '1';
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', hideLoader);
        } else {
            hideLoader();
        }
        document.addEventListener('click', function (e) {
            var link = e.target.closest('a[href]');
            if (!link) return;
            var href = link.getAttribute('href') || '';
            if (!href || href === '#' || href.startsWith('#') || href.startsWith('javascript') ||
                link.getAttribute('target') === '_blank' ||
                link.hasAttribute('data-bs-toggle') ||
                link.hasAttribute('data-bs-dismiss') ||
                e.ctrlKey || e.metaKey || e.shiftKey) return;
            showLoader();
        });
    })();
