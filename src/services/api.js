import axios from 'axios'

// Primary API - Your local optimized server
const API_BASE_URL = '/api/v1'

// Backup/Enhanced API endpoints
const PARLIAMENT_API = 'https://hr.parliament.gov.np/api'
const NEWNEPAL_API = 'https://nes.newnepal.org/api' // Fallback if available

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
})

// Request interceptor for logging and performance
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    config.metadata = { startTime: new Date() }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for logging and error handling
api.interceptors.response.use(
  (response) => {
    const duration = new Date() - response.config.metadata.startTime
    console.log(`✅ API Response: ${response.status} ${response.config.url} (${duration}ms)`)
    return response
  },
  (error) => {
    const duration = error.config?.metadata ? new Date() - error.config.metadata.startTime : 0
    console.error(`❌ API Error: ${error.response?.status} ${error.config?.url} (${duration}ms)`, error.message)
    
    // Enhanced error handling
    if (error.response?.status === 404) {
      throw new Error('Data not found')
    } else if (error.response?.status >= 500) {
      throw new Error('Server error. Please try again later.')
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please check your connection.')
    }
    
    return Promise.reject(error)
  }
)

// Enhanced API Functions with better data processing
export const fetchLeaders = async (params = {}) => {
  const queryParams = new URLSearchParams({
    entity_type: 'person',
    limit: params.limit || 50,
    offset: params.offset || 0,
    ...(params.search && { search: params.search }),
  })

  try {
    const response = await api.get(`/entities?${queryParams.toString()}`)
    const leaders = response.data
    
    // Enhance leader data with additional processing
    return leaders.map(leader => enhanceLeaderData(leader))
  } catch (error) {
    console.error('Error fetching leaders:', error)
    // Return fallback data if available
    return getFallbackLeaders(params)
  }
}

export const fetchLeaderById = async (id) => {
  try {
    const response = await api.get(`/entities/${id}`)
    return enhanceLeaderData(response.data)
  } catch (error) {
    console.error(`Error fetching leader ${id}:`, error)
    throw error
  }
}

export const searchLeaders = async (query) => {
  if (!query || query.trim().length < 2) {
    return []
  }

  const queryParams = new URLSearchParams({
    entity_type: 'person',
    search: query.trim(),
    limit: 15, // Increased for better search results
  })

  try {
    const response = await api.get(`/entities?${queryParams.toString()}`)
    const leaders = response.data
    
    return leaders.map(leader => enhanceLeaderData(leader))
  } catch (error) {
    console.error('Search error:', error)
    return []
  }
}

export const fetchParties = async () => {
  const queryParams = new URLSearchParams({
    entity_type: 'political_party',
    limit: 100
  })

  try {
    const response = await api.get(`/entities?${queryParams.toString()}`)
    return response.data.map(party => enhancePartyData(party))
  } catch (error) {
    console.error('Error fetching parties:', error)
    return getFallbackParties()
  }
}

export const fetchStats = async () => {
  try {
    // Fetch data in parallel for better performance
    const [leadersResponse, partiesResponse] = await Promise.all([
      fetchLeaders({ limit: 1000 }),
      fetchParties()
    ])

    const leaders = leadersResponse
    const parties = partiesResponse

    // Calculate detailed statistics
    const provinces = new Set()
    const genderCount = { male: 0, female: 0, other: 0 }
    const ageGroups = { young: 0, middle: 0, senior: 0 }
    
    leaders.forEach(leader => {
      if (leader.metadata?.province) {
        provinces.add(leader.metadata.province)
      }
      
      // Gender statistics
      const gender = leader.metadata?.gender?.toLowerCase()
      if (gender === 'female') genderCount.female++
      else if (gender === 'male') genderCount.male++
      else genderCount.other++
      
      // Age group statistics
      const age = parseInt(leader.metadata?.age)
      if (age && age < 40) ageGroups.young++
      else if (age && age < 60) ageGroups.middle++
      else if (age) ageGroups.senior++
    })

    return {
      totalLeaders: leaders.length,
      totalParties: parties.length,
      totalProvinces: provinces.size || 7,
      genderDistribution: genderCount,
      ageDistribution: ageGroups,
      provinces: Array.from(provinces).sort()
    }
  } catch (error) {
    console.error('Error fetching stats:', error)
    // Return enhanced fallback stats
    return {
      totalLeaders: 275,
      totalParties: 15,
      totalProvinces: 7,
      genderDistribution: { male: 220, female: 55, other: 0 },
      ageDistribution: { young: 45, middle: 180, senior: 50 },
      provinces: ['Koshi', 'Madhesh', 'Bagmati', 'Gandaki', 'Lumbini', 'Karnali', 'Sudurpashchim']
    }
  }
}

export const healthCheck = async () => {
  try {
    const response = await axios.get('/health')
    return response.data
  } catch (error) {
    console.error('Health check failed:', error)
    return { healthy: false, error: error.message }
  }
}

// Enhanced data processing functions
const enhanceLeaderData = (leader) => {
  if (!leader) return leader

  const metadata = leader.metadata || {}
  
  return {
    ...leader,
    metadata: {
      ...metadata,
      // Enhanced image URL processing
      image_url: getOptimizedImageUrl(leader),
      photo_url: getOptimizedImageUrl(leader),
      
      // Standardized party name
      political_party: standardizePartyName(metadata.political_party || metadata.party),
      party: standardizePartyName(metadata.political_party || metadata.party),
      
      // Enhanced location data
      full_address: getFullAddress(metadata),
      
      // Calculated fields
      age_group: getAgeGroup(metadata.age),
      experience_years: calculateExperience(metadata),
      
      // Social media and contact (if available)
      social_media: extractSocialMedia(metadata),
      
      // Enhanced education
      education_level: categorizeEducation(metadata.education),
    }
  }
}

const enhancePartyData = (party) => {
  if (!party) return party
  
  return {
    ...party,
    metadata: {
      ...party.metadata,
      logo_url: getPartyLogoUrl(party.name),
      color_scheme: getPartyColors(party.name),
      founded_year: getPartyFoundedYear(party.name),
    }
  }
}

// Utility functions for data enhancement
export const getOptimizedImageUrl = (leader) => {
  const metadata = leader?.metadata || {}
  let imageUrl = metadata.image_url || metadata.photo_url || metadata.image
  
  if (imageUrl) {
    // Handle parliament.gov.np URLs
    if (imageUrl.includes('parliament.gov.np')) {
      return imageUrl
    }
    
    // Handle relative paths
    if (imageUrl.startsWith('/uploads/') || imageUrl.startsWith('uploads/')) {
      return `https://hr.parliament.gov.np/${imageUrl.replace(/^\/+/, '')}`
    }
    
    // Handle other absolute URLs
    if (imageUrl.startsWith('http')) {
      return imageUrl
    }
  }
  
  // Enhanced placeholder with better fallback
  return generatePlaceholderImage(leader)
}

const generatePlaceholderImage = (leader) => {
  // Generate a placeholder based on leader's name and party
  const name = leader?.name || 'Unknown'
  const party = leader?.metadata?.political_party || 'Independent'
  const initials = name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  
  // Use a service like UI Avatars or create a local placeholder
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(initials)}&background=${getPartyColorCode(party)}&color=fff&size=400&font-size=0.4`
}

const standardizePartyName = (partyName) => {
  if (!partyName) return 'Independent'
  
  const standardNames = {
    'nepali congress': 'Nepali Congress',
    'communist party of nepal (unified marxist-leninist)': 'CPN (UML)',
    'cpn-uml': 'CPN (UML)',
    'communist party of nepal (maoist centre)': 'CPN (Maoist Centre)',
    'maoist centre': 'CPN (Maoist Centre)',
    'rastriya swatantra party': 'Rastriya Swatantra Party',
    'janata samajbadi party': 'Janata Samajbadi Party',
    'communist party of nepal (unified socialist)': 'CPN (Unified Socialist)',
  }
  
  const normalized = partyName.toLowerCase()
  return standardNames[normalized] || partyName
}

const getFullAddress = (metadata) => {
  const parts = []
  if (metadata.constituency) parts.push(metadata.constituency)
  if (metadata.district) parts.push(metadata.district)
  if (metadata.province) parts.push(`${metadata.province} Province`)
  return parts.join(', ')
}

const getAgeGroup = (age) => {
  const ageNum = parseInt(age)
  if (!ageNum) return 'Unknown'
  if (ageNum < 40) return 'Young (Under 40)'
  if (ageNum < 60) return 'Middle-aged (40-59)'
  return 'Senior (60+)'
}

const calculateExperience = (metadata) => {
  // This would need more data about when they first entered politics
  // For now, return a placeholder
  return metadata.experience_years || 'N/A'
}

const extractSocialMedia = (metadata) => {
  // Extract social media links if available in metadata
  return {
    facebook: metadata.facebook_url || null,
    twitter: metadata.twitter_url || null,
    instagram: metadata.instagram_url || null,
  }
}

const categorizeEducation = (education) => {
  if (!education) return 'Not specified'
  
  const edu = education.toLowerCase()
  if (edu.includes('phd') || edu.includes('doctorate')) return 'Doctorate'
  if (edu.includes('master') || edu.includes('mba') || edu.includes('ma ') || edu.includes('msc')) return 'Masters'
  if (edu.includes('bachelor') || edu.includes('ba ') || edu.includes('bsc') || edu.includes('bba')) return 'Bachelors'
  if (edu.includes('intermediate') || edu.includes('+2')) return 'Intermediate'
  if (edu.includes('slc') || edu.includes('see')) return 'Secondary'
  
  return education
}

export const getPartyClass = (partyName) => {
  if (!partyName) return 'party-other'
  const party = partyName.toLowerCase()
  if (party.includes('congress')) return 'party-congress'
  if (party.includes('uml')) return 'party-uml'
  if (party.includes('maoist')) return 'party-maoist'
  if (party.includes('rastriya') && party.includes('swatantra')) return 'party-rastriya'
  if (party.includes('samajwadi')) return 'party-samajwadi'
  if (party.includes('janata')) return 'party-janata'
  return 'party-other'
}

const getPartyColorCode = (partyName) => {
  const colors = {
    'Nepali Congress': '10b981',
    'CPN (UML)': 'f59e0b',
    'CPN (Maoist Centre)': 'ef4444',
    'Rastriya Swatantra Party': '3b82f6',
    'Janata Samajbadi Party': 'f97316',
    'CPN (Unified Socialist)': 'a855f7',
  }
  return colors[partyName] || '6b7280'
}

const getPartyColors = (partyName) => {
  const colorSchemes = {
    'Nepali Congress': { primary: '#10b981', secondary: '#dcfce7' },
    'CPN (UML)': { primary: '#f59e0b', secondary: '#fef3c7' },
    'CPN (Maoist Centre)': { primary: '#ef4444', secondary: '#fee2e2' },
    'Rastriya Swatantra Party': { primary: '#3b82f6', secondary: '#dbeafe' },
    'Janata Samajbadi Party': { primary: '#f97316', secondary: '#fed7aa' },
    'CPN (Unified Socialist)': { primary: '#a855f7', secondary: '#f3e8ff' },
  }
  return colorSchemes[partyName] || { primary: '#6b7280', secondary: '#f3f4f6' }
}

const getPartyLogoUrl = (partyName) => {
  // Enhanced party logo URLs
  const logoMap = {
    'Nepali Congress': 'https://assets.nes.newnepal.org/assets/images/2082-election-symbols/nepali-congress.png',
    'CPN (UML)': 'https://assets.nes.newnepal.org/assets/images/2082-election-symbols/communist-party-of-nepal-unified-marxist-leninist.png',
    'CPN (Maoist Centre)': 'https://assets.nes.newnepal.org/assets/images/2082-election-symbols/nepal-communist-party-maoist.png',
    'Rastriya Swatantra Party': 'https://assets.nes.newnepal.org/assets/images/2082-election-symbols/national-independent-party.png',
  }
  
  return logoMap[partyName] || '/frontend/assets/placeholder.svg'
}

const getPartyFoundedYear = (partyName) => {
  const foundedYears = {
    'Nepali Congress': 1947,
    'CPN (UML)': 1991,
    'CPN (Maoist Centre)': 1994,
    'Rastriya Swatantra Party': 2022,
    'Janata Samajbadi Party': 2020,
  }
  return foundedYears[partyName] || null
}

// Fallback data functions
const getFallbackLeaders = (params) => {
  // Return sample data structure for development
  return Array.from({ length: params.limit || 12 }, (_, i) => ({
    id: `fallback-${i}`,
    name: `Sample Leader ${i + 1}`,
    name_nepali: `नमूना नेता ${i + 1}`,
    entity_type: 'person',
    metadata: {
      political_party: ['Nepali Congress', 'CPN (UML)', 'CPN (Maoist Centre)'][i % 3],
      district: ['Kathmandu', 'Lalitpur', 'Bhaktapur'][i % 3],
      province: 'Bagmati',
      age: 45 + (i % 20),
      education: 'Masters Degree',
      image_url: generatePlaceholderImage({ name: `Sample Leader ${i + 1}` })
    }
  }))
}

const getFallbackParties = () => {
  return [
    { id: 'nc', name: 'Nepali Congress', metadata: { member_count: 89 } },
    { id: 'uml', name: 'CPN (UML)', metadata: { member_count: 79 } },
    { id: 'maoist', name: 'CPN (Maoist Centre)', metadata: { member_count: 32 } },
    { id: 'rsp', name: 'Rastriya Swatantra Party', metadata: { member_count: 20 } },
  ]
}

export default api