// Ahoy Indie Media — Mobile interactions (≤800px)
(function () {
    const inMobile = () => window.matchMedia && window.matchMedia('(max-width: 800px)').matches;

    const $ = (sel) => document.querySelector(sel);
    const mobileMenu = $('#mobileMenu');
    const accountMenu = $('#accountMenu');

    function open(el) {
        if (!el) return;
        el.classList.remove('hidden');
        el.classList.add('slide-down-enter');
        requestAnimationFrame(() => el.classList.add('slide-down-enter-active'));
        setTimeout(() => {
            el.classList.remove('slide-down-enter');
            el.classList.remove('slide-down-enter-active');
        }, 220);
    }
    function close(el) {
        if (!el) return;
        el.classList.add('hidden');
    }
    function toggle(el) {
        if (!el) return;
        if (el.classList.contains('hidden')) open(el); else close(el);
    }

    function buildMenusOnce() {
        if (mobileMenu && !mobileMenu.dataset.built) {
            mobileMenu.innerHTML = `
                <nav style="display:grid; gap:10px;">
                    <a href="/music" class="mobile-link">Music</a>
                    <a href="/shows" class="mobile-link">Shows</a>
                    <a href="/artists" class="mobile-link">Artists</a>
                    <a href="/radio" class="mobile-link">Radio</a>
                    <a href="/events" class="mobile-link">Events</a>
                    <a href="/merch" class="mobile-link">Merch</a>
                    <a href="/bookmarks" class="mobile-link">Bookmarks</a>
                </nav>
            `;
            mobileMenu.dataset.built = '1';
        }
        if (accountMenu && !accountMenu.dataset.built) {
            const isLoggedIn = !!window.LOGGED_IN;
            const name = (window.userProfile && (window.userProfile.display_name || window.userProfile.username)) || (isLoggedIn ? 'Account' : 'Guest');

            accountMenu.innerHTML = `
                <div style="display:grid; gap:10px;">
                    <div style="padding:10px 12px; border:1px solid rgba(255,255,255,.12); border-radius:12px; background: rgba(255,255,255,.04); font-weight:900;">
                        ${isLoggedIn ? `Hey, ${name} ✨` : `Hey there, ${name} 👋`}
                    </div>

                    ${isLoggedIn ? `
                        <a href="/account" class="mobile-link">My Profile</a>
                        <a href="/bookmarks" class="mobile-link">Bookmarks</a>
                        <a href="/settings" class="mobile-link">Settings</a>
                        <button data-action="logout" class="mobile-link">Sign Out</button>
                    ` : `
                        <a href="/account" class="mobile-link" style="border-color: rgba(147,51,234,.55); background: rgba(147,51,234,.20); font-weight: 900;">
                            Sign in / Create username 🚀
                        </a>
                        <a href="/bookmarks" class="mobile-link">Bookmarks</a>
                        <a href="/settings" class="mobile-link">Settings</a>
                    `}
                </div>
            `;

            accountMenu.addEventListener('click', async (e) => {
                const btn = e.target && e.target.closest && e.target.closest('[data-action="logout"]');
                if (!btn) return;
                e.preventDefault();
                try {
                    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
                } catch (_) { /* ignore */ }
                window.location.reload();
            });

            accountMenu.dataset.built = '1';
        }
    }

    function setupHandlers() {
        const openExplore = $('#openExplore');
        const openAccount = $('#openAccount');
        const openSearch = $('#openSearch');
        const openBoost = $('#openBoost');

        if (openExplore) openExplore.addEventListener('click', () => {
            if (!inMobile()) return;
            buildMenusOnce();
            toggle(mobileMenu);
            close(accountMenu);
        });
        if (openAccount) openAccount.addEventListener('click', () => {
            if (!inMobile()) return;
            buildMenusOnce();
            toggle(accountMenu);
            close(mobileMenu);
        });

        // Search: redirect to search page with focus; modal optional later
        if (openSearch) openSearch.addEventListener('click', () => {
            if (!inMobile()) return;
            window.location.href = '/search';
        });

        // Boost: go to artists with tip intent
        if (openBoost) openBoost.addEventListener('click', () => {
            if (!inMobile()) return;
            window.location.href = '/artists?boost=1';
        });

        // Close menus on outside click
        document.addEventListener('click', (e) => {
            if (!inMobile()) return;
            const withinMenu = (mobileMenu && mobileMenu.contains(e.target)) ||
                               (accountMenu && accountMenu.contains(e.target));
            const uiButton = e.target.closest && e.target.closest('#openExplore, #openAccount');
            if (!withinMenu && !uiButton) {
                close(mobileMenu); close(accountMenu);
            }
        });

        // Close on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') { close(mobileMenu); close(accountMenu); }
        });
    }

    window.addEventListener('DOMContentLoaded', () => {
        if (!inMobile()) return;
        setupHandlers();
    });

    // Update status bar time
    function updateStatusTime() {
        const statusTime = $('#statusTime');
        if (statusTime) {
            const now = new Date();
            const hours = now.getHours();
            const minutes = now.getMinutes();
            const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
            statusTime.textContent = timeString;
        }
    }

    // Update time immediately and then every minute
    if (inMobile()) {
        updateStatusTime();
        setInterval(updateStatusTime, 60000);
    }
})();

// Lightweight Alpine helpers for mobile accordions/drawers
(function () {
	// Broadcast open drawer from components without root access
	document.addEventListener('open:mobileDrawer', function () {
		try {
			const root = document.querySelector('body')?.__x?.$data;
			if (root) root.mobileDrawer = true;
		} catch (_) {}
	});
	// Close on back swipe (iOS Safari heuristic)
	window.addEventListener('popstate', function () {
		try {
			const root = document.querySelector('body')?.__x?.$data;
			if (root && root.mobileDrawer) root.mobileDrawer = false;
		} catch (_) {}
	});
})();

// Mobile-only Alpine store for nav/account menus (does not affect desktop behavior)
document.addEventListener('alpine:init', () => {
	try {
		const getRootData = () => document.querySelector('body')?.__x?.$data || null;
		Alpine.store('mobileNav', {
			get open() {
				const r = getRootData();
				return !!(r && r.navOpen);
			},
			set open(v) {
				const r = getRootData();
				if (r) r.navOpen = !!v;
			},
			get account() {
				const r = getRootData();
				return !!(r && r.mobileDrawer);
			},
			set account(v) {
				const r = getRootData();
				if (r) r.mobileDrawer = !!v;
			}
		});
	} catch (_) {}
});



