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

            // Handle production API wrapped response { entities: [], total: ... }
            if (data && data.entities && Array.isArray(data.entities)) {
                return data.entities.map(item => this.normalizeEntity(item));
            }

            // Normalization for single objects or arrays
            if (Array.isArray(data)) {
                return data.map(item => this.normalizeEntity(item));
            } else if (data && typeof data === 'object') {
                return this.normalizeEntity(data);
            }

            return data;
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    /**
     * Normalize production API entity to frontend schema
     */
    normalizeEntity(entity) {
        if (!entity || typeof entity !== 'object') return entity;

        // Extract primary name
        const primaryName = entity.names && entity.names[0];
        const normalized = {
            ...entity,
            name: primaryName?.en?.full || entity.name,
            name_nepali: primaryName?.ne?.full || entity.name_nepali,
            // Extract metadata from nesting if not already present
            metadata: entity.metadata || entity.meta_data || {}
        };

        // Extract education/qualification
        if (!normalized.education) {
            const qual = entity.attributes?.election_council_misc?.qualification?.en?.value
                || entity.qualification?.en?.value;
            if (qual) {
                normalized.education = qual;
                normalized.metadata.education = qual;
            } else if (entity.personal_details?.education?.[0]?.degree?.en?.value) {
                normalized.education = entity.personal_details.education[0].degree.en.value;
                normalized.metadata.education = normalized.education;
            }
        }

        // Extract party from electoral details if missing
        if (!normalized.metadata.party && entity.electoral_details?.candidacies) {
            const latestCandidacy = entity.electoral_details.candidacies[0];
            if (latestCandidacy && latestCandidacy.party_id) {
                // Strip prefix and format (e.g., entity:organization/political_party/nepali-congress -> Nepali Congress)
                const rawParty = latestCandidacy.party_id.split('/').pop().replace(/-/g, ' ');
                normalized.metadata.party = rawParty.charAt(0).toUpperCase() + rawParty.slice(1);
            }
        }

        // Extract image
        if (!normalized.metadata.image && entity.pictures && entity.pictures.length > 0) {
            normalized.metadata.image = entity.pictures[0].url;
        }

        // Handle potential criminal_cases/assets if they exist in attributes
        if (entity.attributes?.election_council_misc) {
            const misc = entity.attributes.election_council_misc;
            if (misc.criminal_cases && normalized.metadata.criminal_cases === undefined) {
                normalized.metadata.criminal_cases = misc.criminal_cases;
            }
            if (misc.assets && normalized.metadata.assets === undefined) {
                normalized.metadata.assets = misc.assets;
            }
        }

        // Handle meta_data alias
        if (entity.meta_data && !entity.metadata) {
            normalized.metadata = entity.meta_data;
        }

        return normalized;
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
            offset: params.skip || 0, // Prod API uses offset
            ...(params.search && { query: params.search }), // Prod API uses query
        });

        return this.getCached(`/entities?${queryParams.toString()}`);
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
            query: query, // Prod API uses query
            limit: 10,
        });

        return this.fetch(`/entities?${queryParams.toString()}`);
    }

    /**
     * Fetch leaders by province (from metadata)
     */
    async fetchLeadersByProvince(province) {
        // Note: Production API might support deeper filtering, but we'll fetch and filter for now
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
        const queryParams = new URLSearchParams({
            entity_type: 'organization',
            sub_type: 'political_party',
            limit: 1000  // Fetch all parties - API has 124 total
        });

        const parties = await this.fetch(`/entities?${queryParams.toString()}`);

        return parties.map(party => ({
            name: party.name,
            id: party.id,
            count: 0 // We'd need another call or server support for true counts
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

        const leaders = await this.fetchLeaders({ limit: 1000 });  // Max limit per request
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
window.api = api;

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, api };
}
