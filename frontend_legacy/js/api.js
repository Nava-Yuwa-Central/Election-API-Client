// ================================
// Optimized API Client Module
// High-performance API client with intelligent caching and photo sync
// ================================

class OptimizedAPIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
        this.cache = new Map();
        this.imageCache = new Map();
        this.requestQueue = new Map();
    }

    /**
     * Optimized fetch with request deduplication and caching
     */
    async fetch(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const cacheKey = `${url}_${JSON.stringify(options)}`;

        // Check if same request is already in progress
        if (this.requestQueue.has(cacheKey)) {
            return this.requestQueue.get(cacheKey);
        }

        // Create the request promise
        const requestPromise = this._performFetch(url, options);
        this.requestQueue.set(cacheKey, requestPromise);

        try {
            const result = await requestPromise;
            return result;
        } finally {
            // Clean up the request queue
            this.requestQueue.delete(cacheKey);
        }
    }

    async _performFetch(url, options) {
        try {
            console.log(`🚀 API Request: ${url}`);
            
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
                ...options,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log(`✅ API Response: ${Array.isArray(data) ? data.length : 'single'} items`);

            // Normalize and optimize data
            return this.normalizeResponse(data);
        } catch (error) {
            console.error(`❌ API Error (${url}):`, error);
            throw error;
        }
    }

    /**
     * Normalize API response and optimize image URLs
     */
    normalizeResponse(data) {
        if (Array.isArray(data)) {
            return data.map(item => this.normalizeEntity(item));
        }
        
        if (data && typeof data === 'object') {
            return this.normalizeEntity(data);
        }

        return data;
    }

    /**
     * Normalize entity with optimized image handling
     */
    normalizeEntity(entity) {
        if (!entity || typeof entity !== 'object') return entity;

        const normalized = { ...entity };

        // Optimize image URL handling
        if (normalized.metadata) {
            const imageUrl = this.getOptimizedImageUrl(normalized);
            if (imageUrl) {
                normalized.metadata.image_url = imageUrl;
                normalized.metadata.photo_url = imageUrl;
                
                // Preload image for better performance
                this.preloadImage(imageUrl);
            }
        }

        return normalized;
    }

    /**
     * Get optimized image URL with fallback handling
     */
    getOptimizedImageUrl(entity) {
        const metadata = entity.metadata || {};
        
        // Try multiple image sources
        const imageUrl = metadata.image_url || 
                         metadata.photo_url || 
                         metadata.image ||
                         entity.image_url ||
                         entity.image;

        if (!imageUrl) return null;

        // Handle parliament.gov.np URLs
        if (imageUrl.includes('parliament.gov.np')) {
            return imageUrl;
        }

        // Handle relative paths
        if (imageUrl.startsWith('/uploads/') || imageUrl.startsWith('uploads/')) {
            return `https://hr.parliament.gov.np/${imageUrl}`;
        }

        return imageUrl;
    }

    /**
     * Preload images for better performance
     */
    preloadImage(url) {
        if (!url || this.imageCache.has(url)) return;

        const img = new Image();
        img.onload = () => {
            this.imageCache.set(url, true);
            console.log(`📸 Preloaded image: ${url.split('/').pop()}`);
        };
        img.onerror = () => {
            console.warn(`⚠️ Failed to preload image: ${url}`);
        };
        img.src = url;
    }

    /**
     * Get data with intelligent caching
     */
    async getCached(endpoint, maxAge = APP_CONFIG.CACHE_DURATION) {
        const cached = this.cache.get(endpoint);

        if (cached && Date.now() - cached.timestamp < maxAge) {
            console.log(`💾 Using cached data for ${endpoint}`);
            return cached.data;
        }

        const data = await this.fetch(endpoint);
        this.cache.set(endpoint, {
            data,
            timestamp: Date.now(),
        });

        return data;
    }

    /**
     * Batch fetch multiple entities efficiently
     */
    async fetchBatch(ids) {
        const promises = ids.map(id => this.fetchLeaderById(id));
        const results = await Promise.allSettled(promises);
        
        return results
            .filter(result => result.status === 'fulfilled')
            .map(result => result.value);
    }

    /**
     * Fetch leaders with optimized parameters
     */
    async fetchLeaders(params = {}) {
        const queryParams = new URLSearchParams({
            entity_type: 'person',
            limit: params.limit || APP_CONFIG.ITEMS_PER_PAGE,
            offset: params.offset || 0,
            ...(params.search && { search: params.search }),
        });

        const cacheKey = `/entities?${queryParams.toString()}`;
        return this.getCached(cacheKey, 60000); // 1 minute cache for lists
    }

    /**
     * Fetch single leader with caching
     */
    async fetchLeaderById(id) {
        const cacheKey = `/entities/${id}`;
        return this.getCached(cacheKey, 300000); // 5 minute cache for individuals
    }

    /**
     * Optimized search with debouncing built-in
     */
    async searchLeaders(query) {
        if (!query || query.trim().length < 2) {
            return [];
        }

        const queryParams = new URLSearchParams({
            entity_type: 'person',
            search: query.trim(),
            limit: 10,
        });

        // Use shorter cache for search results
        const cacheKey = `/entities?${queryParams.toString()}`;
        return this.getCached(cacheKey, 30000); // 30 second cache for search
    }

    /**
     * Fetch parties with member counts
     */
    async fetchParties() {
        const queryParams = new URLSearchParams({
            entity_type: 'political_party',
            limit: 100
        });

        const cacheKey = `/entities?${queryParams.toString()}`;
        return this.getCached(cacheKey, 300000); // 5 minute cache
    }

    /**
     * Get optimized statistics
     */
    async fetchStats() {
        const cacheKey = '/stats';
        const cached = this.cache.get(cacheKey);

        if (cached && Date.now() - cached.timestamp < 300000) { // 5 min cache
            return cached.data;
        }

        // Fetch data in parallel for better performance
        const [leadersPromise, partiesPromise] = await Promise.allSettled([
            this.fetchLeaders({ limit: 1000 }),
            this.fetchParties()
        ]);

        const leaders = leadersPromise.status === 'fulfilled' ? leadersPromise.value : [];
        const parties = partiesPromise.status === 'fulfilled' ? partiesPromise.value : [];

        const provinces = new Set();
        leaders.forEach(leader => {
            if (leader.metadata?.province) {
                provinces.add(leader.metadata.province);
            }
        });

        const stats = {
            totalLeaders: leaders.length,
            totalParties: parties.length,
            totalProvinces: provinces.size || 7,
            avgAttendance: this.calculateAvgAttendance(leaders),
        };

        this.cache.set(cacheKey, {
            data: stats,
            timestamp: Date.now(),
        });

        return stats;
    }

    /**
     * Calculate average attendance efficiently
     */
    calculateAvgAttendance(leaders) {
        const leadersWithAttendance = leaders.filter(
            l => l.metadata?.attendance !== undefined
        );

        if (leadersWithAttendance.length === 0) return 85; // Default

        const total = leadersWithAttendance.reduce(
            (sum, l) => sum + (l.metadata.attendance || 0),
            0
        );

        return Math.round(total / leadersWithAttendance.length);
    }

    /**
     * Health check with performance metrics
     */
    async healthCheck() {
        try {
            const startTime = Date.now();
            const response = await fetch(`${this.baseURL.replace('/api/v1', '')}/health`);
            const responseTime = Date.now() - startTime;
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ API Health: ${responseTime}ms response time`);
                return { healthy: true, responseTime, ...data };
            }
            
            return { healthy: false, responseTime };
        } catch (error) {
            console.error('❌ Health check failed:', error);
            return { healthy: false, error: error.message };
        }
    }

    /**
     * Clear all caches
     */
    clearCache() {
        this.cache.clear();
        this.imageCache.clear();
        console.log('🧹 Cache cleared');
    }

    /**
     * Get cache statistics
     */
    getCacheStats() {
        return {
            apiCache: this.cache.size,
            imageCache: this.imageCache.size,
            requestQueue: this.requestQueue.size
        };
    }
}

// Create optimized global API client instance
const api = new OptimizedAPIClient(APP_CONFIG.API_BASE_URL);
window.api = api;

// Performance monitoring
if (typeof performance !== 'undefined') {
    window.addEventListener('load', () => {
        const loadTime = performance.now();
        console.log(`⚡ Page loaded in ${Math.round(loadTime)}ms`);
    });
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { OptimizedAPIClient, api };
}
