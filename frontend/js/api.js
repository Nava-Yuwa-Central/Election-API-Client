// ================================
// API Client Module
// ================================

class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
        this.cache = new Map();
    }

    /**
     * Generic fetch method with error handling
     */
    async fetch(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;

        try {
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
            return data;
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    /**
     * Get data with caching
     */
    async getCached(endpoint, maxAge = APP_CONFIG.CACHE_DURATION) {
        const cached = this.cache.get(endpoint);

        if (cached && Date.now() - cached.timestamp < maxAge) {
            console.log(`Using cached data for ${endpoint}`);
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
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
    }

    /**
     * Fetch all leaders (entities with type=person)
     */
    async fetchLeaders(params = {}) {
        const queryParams = new URLSearchParams({
            entity_type: 'person',
            limit: params.limit || APP_CONFIG.ITEMS_PER_PAGE,
            skip: params.skip || 0,
            ...(params.search && { search: params.search }),
        });

        return this.getCached(`/entities/?${queryParams.toString()}`);
    }

    /**
     * Fetch a single leader by ID
     */
    async fetchLeaderById(id) {
        return this.fetch(`/entities/${id}`);
    }

    /**
     * Search leaders
     */
    async searchLeaders(query) {
        if (!query || query.trim().length < 2) {
            return [];
        }

        const queryParams = new URLSearchParams({
            entity_type: 'person',
            search: query,
            limit: 10,
        });

        return this.fetch(`/entities/?${queryParams.toString()}`);
    }

    /**
     * Fetch leaders by province (from metadata)
     */
    async fetchLeadersByProvince(province) {
        // Note: This is a simplified version. You may need server-side filtering
        const allLeaders = await this.fetchLeaders({ limit: 1000 });
        return allLeaders.filter(leader =>
            leader.metadata?.province?.toLowerCase() === province.toLowerCase()
        );
    }

    /**
     * Fetch leaders by party
     */
    async fetchLeadersByParty(party) {
        const allLeaders = await this.fetchLeaders({ limit: 1000 });
        return allLeaders.filter(leader =>
            leader.metadata?.party?.toLowerCase().includes(party.toLowerCase())
        );
    }

    /**
     * Get unique parties from leaders
     */
    async fetchParties() {
        const leaders = await this.fetchLeaders({ limit: 1000 });
        const parties = new Set();

        leaders.forEach(leader => {
            if (leader.metadata?.party) {
                parties.add(leader.metadata.party);
            }
        });

        return Array.from(parties).map(party => ({
            name: party,
            count: leaders.filter(l => l.metadata?.party === party).length,
        }));
    }

    /**
     * Get statistics
     */
    async fetchStats() {
        const cacheKey = '/stats';
        const cached = this.cache.get(cacheKey);

        if (cached && Date.now() - cached.timestamp < APP_CONFIG.CACHE_DURATION) {
            return cached.data;
        }

        const leaders = await this.fetchLeaders({ limit: 1000 });
        const parties = await this.fetchParties();

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
     * Calculate average attendance from leaders
     */
    calculateAvgAttendance(leaders) {
        const leadersWithAttendance = leaders.filter(
            l => l.metadata?.attendance !== undefined
        );

        if (leadersWithAttendance.length === 0) return 0;

        const total = leadersWithAttendance.reduce(
            (sum, l) => sum + (l.metadata.attendance || 0),
            0
        );

        return Math.round(total / leadersWithAttendance.length);
    }

    /**
     * Create a new entity (leader)
     */
    async createLeader(leaderData) {
        return this.fetch('/entities/', {
            method: 'POST',
            body: JSON.stringify(leaderData),
        });
    }

    /**
     * Update an entity
     */
    async updateLeader(id, leaderData) {
        return this.fetch(`/entities/${id}`, {
            method: 'PUT',
            body: JSON.stringify(leaderData),
        });
    }

    /**
     * Delete an entity
     */
    async deleteLeader(id) {
        return this.fetch(`/entities/${id}`, {
            method: 'DELETE',
        });
    }

    /**
     * Health check
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseURL.replace('/api/v1', '')}/health`);
            return response.ok;
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }
}

// Create global API client instance
const api = new APIClient(APP_CONFIG.API_BASE_URL);

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, api };
}
