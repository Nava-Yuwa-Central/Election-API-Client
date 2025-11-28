// ================================
// Utility Functions
// ================================

/**
 * Format number with commas
 */
function formatNumber(num) {
    if (num === undefined || num === null) return '0';
    return num.toLocaleString('en-US');
}

/**
 * Format currency (NPR)
 */
function formatCurrency(amount) {
    if (amount === undefined || amount === null) return 'NPR 0';
    return `NPR ${formatNumber(amount)}`;
}

/**
 * Format date
 */
function formatDate(dateString) {
    if (!dateString) return '';

    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    });
}

/**
 * Format relative time (e.g., "2 days ago")
 */
function formatRelativeTime(dateString) {
    if (!dateString) return '';

    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;

    return formatDate(dateString);
}

/**
 * Truncate text
 */
function truncateText(text, maxLength = 100) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Debounce function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit = 100) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Get image URL or placeholder
 */
function getImageUrl(leader, size = 'medium') {
    if (leader?.metadata?.photo_url) {
        return leader.metadata.photo_url;
    }

    // Return placeholder
    return `assets/placeholder.jpg`;
}

/**
 * Get party color
 */
function getPartyColor(partyName) {
    if (!partyName) return '#6c757d';

    const partyLower = partyName.toLowerCase();

    if (partyLower.includes('congress')) return '#10b981';
    if (partyLower.includes('uml') || partyLower.includes('communist')) return '#f59e0b';
    if (partyLower.includes('maoist')) return '#ef4444';
    if (partyLower.includes('rastriya')) return '#3b82f6';

    // Default color
    return '#6c757d';
}

/**
 * Get party badge class
 */
function getPartyBadgeClass(partyName) {
    if (!partyName) return '';

    const partyLower = partyName.toLowerCase();

    if (partyLower.includes('congress')) return 'party-congress';
    if (partyLower.includes('uml')) return 'party-uml';
    if (partyLower.includes('maoist')) return 'party-maoist';

    return '';
}

/**
 * Sanitize HTML to prevent XSS
 */
function sanitizeHTML(str) {
    if (!str) return '';

    const temp = document.createElement('div');
    temp.textContent = str;
    return temp.innerHTML;
}

/**
 * Generate unique ID
 */
function generateId() {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Local storage helpers
 */
const storage = {
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return defaultValue;
        }
    },

    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Error writing to localStorage:', error);
            return false;
        }
    },

    remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Error removing from localStorage:', error);
            return false;
        }
    },

    clear() {
        try {
            localStorage.clear();
            return true;
        } catch (error) {
            console.error('Error clearing localStorage:', error);
            return false;
        }
    },
};

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} fade-in-down`;
    toast.textContent = message;

    // Add styles
    Object.assign(toast.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '16px 24px',
        backgroundColor: type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6',
        color: 'white',
        borderRadius: '8px',
        boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
        zIndex: '9999',
        fontWeight: '500',
        maxWidth: '300px',
    });

    document.body.appendChild(toast);

    // Auto remove
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Show loading spinner
 */
function showLoading(container, message = 'Loading...') {
    if (!container) return;

    container.innerHTML = `
    <div class="loading-container" style="text-align: center; padding: 60px 20px;">
      <div class="spinner" style="margin: 0 auto 20px;"></div>
      <p style="color: var(--color-gray); font-size: var(--font-size-lg);">${message}</p>
    </div>
  `;
}

/**
 * Show error message
 */
function showError(container, message = 'Something went wrong') {
    if (!container) return;

    container.innerHTML = `
    <div class="error-container" style="text-align: center; padding: 60px 20px;">
      <div style="font-size: 48px; color: var(--color-danger); margin-bottom: 20px;">⚠️</div>
      <h3 style="color: var(--color-dark); margin-bottom: 10px;">Oops!</h3>
      <p style="color: var(--color-gray); font-size: var(--font-size-lg);">${message}</p>
      <button class="btn btn-primary mt-lg" onclick="location.reload()">Retry</button>
    </div>
  `;
}

/**
 * Show empty state
 */
function showEmptyState(container, message = 'No data found') {
    if (!container) return;

    container.innerHTML = `
    <div class="empty-state" style="text-align: center; padding: 60px 20px;">
      <div style="font-size: 64px; margin-bottom: 20px;">📭</div>
      <h3 style="color: var(--color-dark); margin-bottom: 10px;">Nothing Here</h3>
      <p style="color: var(--color-gray); font-size: var(--font-size-lg);">${message}</p>
    </div>
  `;
}

/**
 * Scroll to element smoothly
 */
function scrollToElement(element, offset = 0) {
    if (!element) return;

    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;

    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth',
    });
}

/**
 * Check if element is in viewport
 */
function isInViewport(element) {
    if (!element) return false;

    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Intersection Observer for scroll animations
 */
function initScrollAnimations() {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px',
        }
    );

    document.querySelectorAll('.scroll-reveal').forEach((el) => {
        observer.observe(el);
    });
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!', 'success');
        return true;
    } catch (error) {
        console.error('Failed to copy:', error);
        showToast('Failed to copy', 'error');
        return false;
    }
}

/**
 * Share using Web Share API
 */
async function share(data) {
    if (!navigator.share) {
        console.warn('Web Share API not supported');
        // Fallback to copy URL
        await copyToClipboard(data.url || window.location.href);
        return false;
    }

    try {
        await navigator.share(data);
        return true;
    } catch (error) {
        if (error.name !== 'AbortError') {
            console.error('Error sharing:', error);
        }
        return false;
    }
}

/**
 * Create element from HTML string
 */
function createElementFromHTML(htmlString) {
    const div = document.createElement('div');
    div.innerHTML = htmlString.trim();
    return div.firstChild;
}

/**
 * Wait for a specified time
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Export utilities
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatNumber,
        formatCurrency,
        formatDate,
        formatRelativeTime,
        truncateText,
        debounce,
        throttle,
        getImageUrl,
        getPartyColor,
        getPartyBadgeClass,
        sanitizeHTML,
        generateId,
        storage,
        showToast,
        showLoading,
        showError,
        showEmptyState,
        scrollToElement,
        isInViewport,
        initScrollAnimations,
        copyToClipboard,
        share,
        createElementFromHTML,
        sleep,
    };
}
