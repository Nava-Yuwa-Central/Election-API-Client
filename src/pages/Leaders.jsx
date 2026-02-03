import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Helmet } from 'react-helmet-async'
import { fetchLeaders, searchLeaders } from '../services/api'
import CandidateCard from '../components/CandidateCard'
import LoadingSpinner from '../components/LoadingSpinner'

const Leaders = () => {
  const [leaders, setLeaders] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filteredLeaders, setFilteredLeaders] = useState([])
  const [selectedParty, setSelectedParty] = useState('')
  const [selectedProvince, setSelectedProvince] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const leadersPerPage = 20

  // Get unique parties and provinces for filters
  const parties = [...new Set(leaders.map(l => l.metadata?.political_party).filter(Boolean))].sort()
  const provinces = [...new Set(leaders.map(l => l.metadata?.province).filter(Boolean))].sort()

  useEffect(() => {
    loadLeaders()
  }, [])

  useEffect(() => {
    // Get search query from URL if present
    const urlParams = new URLSearchParams(window.location.search)
    const searchParam = urlParams.get('search')
    if (searchParam) {
      setSearchQuery(searchParam)
    }
  }, [])

  useEffect(() => {
    filterLeaders()
  }, [leaders, searchQuery, selectedParty, selectedProvince, currentPage])

  const loadLeaders = async () => {
    try {
      setLoading(true)
      const data = await fetchLeaders({ limit: 1000 }) // Load all leaders
      setLeaders(data)
    } catch (error) {
      console.error('Error loading leaders:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterLeaders = () => {
    let filtered = [...leaders]

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(leader => 
        leader.name.toLowerCase().includes(query) ||
        leader.name_nepali?.toLowerCase().includes(query) ||
        leader.metadata?.political_party?.toLowerCase().includes(query) ||
        leader.metadata?.district?.toLowerCase().includes(query) ||
        leader.metadata?.constituency?.toLowerCase().includes(query)
      )
    }

    // Apply party filter
    if (selectedParty) {
      filtered = filtered.filter(leader => leader.metadata?.political_party === selectedParty)
    }

    // Apply province filter
    if (selectedProvince) {
      filtered = filtered.filter(leader => leader.metadata?.province === selectedProvince)
    }

    // Calculate pagination
    const total = Math.ceil(filtered.length / leadersPerPage)
    setTotalPages(total)

    // Apply pagination
    const startIndex = (currentPage - 1) * leadersPerPage
    const endIndex = startIndex + leadersPerPage
    const paginatedLeaders = filtered.slice(startIndex, endIndex)

    setFilteredLeaders(paginatedLeaders)
  }

  const handleSearch = (e) => {
    e.preventDefault()
    setCurrentPage(1) // Reset to first page when searching
  }

  const clearFilters = () => {
    setSearchQuery('')
    setSelectedParty('')
    setSelectedProvince('')
    setCurrentPage(1)
  }

  if (loading) {
    return <LoadingSpinner />
  }

  return (
    <>
      <Helmet>
        <title>Political Leaders - Who's My Neta Nepal</title>
        <meta name="description" content="Browse all political leaders in Nepal. Filter by party, province, and search by name or constituency." />
      </Helmet>

      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-8"
          >
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Political Leaders
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Discover Nepal's political representatives, their backgrounds, and constituencies
            </p>
          </motion.div>

          {/* Search and Filters */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="bg-white rounded-xl shadow-lg p-6 mb-8"
          >
            {/* Search Bar */}
            <form onSubmit={handleSearch} className="mb-6">
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search leaders by name, party, or constituency..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent pr-12"
                />
                <button
                  type="submit"
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-primary-600 text-white p-2 rounded-lg hover:bg-red-700 transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>
              </div>
            </form>

            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <select
                value={selectedParty}
                onChange={(e) => setSelectedParty(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent"
              >
                <option value="">All Parties</option>
                {parties.map(party => (
                  <option key={party} value={party}>{party}</option>
                ))}
              </select>

              <select
                value={selectedProvince}
                onChange={(e) => setSelectedProvince(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-600 focus:border-transparent"
              >
                <option value="">All Provinces</option>
                {provinces.map(province => (
                  <option key={province} value={province}>{province}</option>
                ))}
              </select>

              <button
                onClick={clearFilters}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Clear Filters
              </button>
            </div>

            {/* Results Count */}
            <div className="mt-4 text-sm text-gray-600">
              Showing {filteredLeaders.length} of {leaders.length} leaders
              {(searchQuery || selectedParty || selectedProvince) && (
                <span className="ml-2 text-primary-600">
                  (filtered)
                </span>
              )}
            </div>
          </motion.div>

          {/* Leaders Grid */}
          {filteredLeaders.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12"
            >
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No leaders found</h3>
              <p className="text-gray-600 mb-4">
                Try adjusting your search criteria or clearing the filters
              </p>
              <button
                onClick={clearFilters}
                className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors"
              >
                Clear All Filters
              </button>
            </motion.div>
          ) : (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8"
              >
                {filteredLeaders.map((leader, index) => (
                  <motion.div
                    key={leader.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.05 }}
                  >
                    <CandidateCard leader={leader} />
                  </motion.div>
                ))}
              </motion.div>

              {/* Pagination */}
              {totalPages > 1 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.6, delay: 0.6 }}
                  className="flex justify-center items-center space-x-2"
                >
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                  >
                    Previous
                  </button>
                  
                  <div className="flex space-x-1">
                    {[...Array(Math.min(5, totalPages))].map((_, i) => {
                      const pageNum = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + i
                      return (
                        <button
                          key={pageNum}
                          onClick={() => setCurrentPage(pageNum)}
                          className={`px-3 py-2 rounded-lg ${
                            currentPage === pageNum
                              ? 'bg-primary-600 text-white'
                              : 'border border-gray-300 hover:bg-gray-50'
                          }`}
                        >
                          {pageNum}
                        </button>
                      )
                    })}
                  </div>
                  
                  <button
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                    className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                  >
                    Next
                  </button>
                </motion.div>
              )}
            </>
          )}
        </div>
      </div>
    </>
  )
}

export default Leaders