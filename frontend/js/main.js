// ================================
// Main Application Script
// Common functionality across all pages
// ================================

document.addEventListener('DOMContentLoaded', () => {
    console.log(`%c🇳🇵 ${APP_CONFIG.APP_NAME}`, 'font-size: 20px; font-weight: bold; color: #DC143C;');
    console.log('Initializing application...');

    // Initialize navigation
    initNavigation();

    // Health check
    checkAPIHealth();
});

/**
 * Initialize navigation menu
 */
function initNavigation() {
    const toggle = document.getElementById('navbarToggle');
    const nav = document.getElementById('navbarNav');

    if (toggle && nav) {
        toggle.addEventListener('click', () => {
            nav.classList.toggle('active');
        });

        // Close menu when clicking nav link on mobile
        nav.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    nav.classList.remove('active');
                }
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!toggle.contains(e.target) && !nav.contains(e.target)) {
                nav.classList.remove('active');
            }
        });
    }
}

/**
 * Check API health
 */
async function checkAPIHealth() {
    try {
        const isHealthy = await api.healthCheck();

        if (isHealthy) {
            console.log('✅ API is healthy');
        } else {
            console.warn('⚠️ API health check failed');
            showAPIWarning();
        }
    } catch (error) {
        console.error(' API is unreachable');
        showAPIWarning();
    }
}

/**
 * Show API warning banner
 */
function showAPIWarning() {
    const banner = document.createElement('div');
    banner.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background-color: #f59e0b;
    color: white;
    padding: 12px;
    text-align: center;
    z-index: 10000;
    font-weight: 500;
  `;
    banner.textContent = '⚠️ Cannot connect to API. Some features may not work.';

    document.body.prepend(banner);

    // Auto-hide after 5 seconds
    setTimeout(() => {
        banner.style.opacity = '0';
        banner.style.transition = 'opacity 0.5s';
        setTimeout(() => banner.remove(), 500);
    }, 5000);
}

/**
 * Format and display date/time
 */
function updateDateTime() {
    const elements = document.querySelectorAll('[data-datetime]');

    elements.forEach(el => {
        const dateString = el.getAttribute('data-datetime');
        if (dateString) {
            el.textContent = formatRelativeTime(dateString);
        }
    });
}

// Update date/time every minute
setInterval(updateDateTime, 60000);

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');

    tooltipElements.forEach(el => {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const text = e.target.getAttribute('data-tooltip');
    if (!text) return;

    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.id = 'active-tooltip';

    document.body.appendChild(tooltip);

    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = `${rect.left + rect.width / 2}px`;
    tooltip.style.top = `${rect.top - tooltip.offsetHeight - 10}px`;
    tooltip.style.transform = 'translateX(-50%)';
}

function hideTooltip() {
    const tooltip = document.getElementById('active-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

/**
 * Image lazy loading
 */
function initLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

/**
 * Smooth scroll to top button
 */
function initScrollToTop() {
    const button = document.createElement('button');
    button.innerHTML = '↑';
    button.className = 'scroll-to-top';
    button.style.cssText = `
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background-color: var(--color-primary);
    color: white;
    border: none;
    font-size: 24px;
    cursor: pointer;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    z-index: 1000;
    box-shadow: var(--shadow-lg);
  `;

    button.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    document.body.appendChild(button);

    // Show/hide based on scroll position
    window.addEventListener('scroll', throttle(() => {
        if (window.pageYOffset > 300) {
            button.style.opacity = '1';
            button.style.visibility = 'visible';
        } else {
            button.style.opacity = '0';
            button.style.visibility = 'hidden';
        }
    }, 200));
}

// Initialize features
document.addEventListener('DOMContentLoaded', () => {
    initTooltips();
    initLazyLoading();
    initScrollToTop();
    updateDateTime();
});

/**
 * Theme toggle (for future dark mode support)
 */
function initThemeToggle() {
    const savedTheme = storage.get('theme', 'light');
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    document.documentElement.setAttribute('data-theme', newTheme);
    storage.set('theme', newTheme);

    showToast(`Switched to ${newTheme} mode`, 'success');
}

/**
 * Handle offline/online status
 */
window.addEventListener('online', () => {
    showToast('You are back online', 'success');
});

window.addEventListener('offline', () => {
    showToast('You are offline', 'warning', 5000);
});

// Export common functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initNavigation,
        checkAPIHealth,
        toggleTheme,
    };
}
