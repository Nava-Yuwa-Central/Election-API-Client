import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { searchLeaders } from '../services/api'

const SearchSection = () => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const searchRef = useRef(null)
  const debounceRef = useRef(null)

  // Handle search with debouncing
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    if (query.trim().length < 2) {
      setResults([])
      setShowResults(false)
      return
    }

    debounceRef.current = setTimeout(async () => {
      setLoading(true)
      try {
        const searchResults = await searchLeaders(query)
        setResults(searchResults.slice(0, 8)) // Limit to 8 results
        setShowResults(true)
      } catch (error) {
        console.error('Search error:', error)
        setResults([])
      } finally {
        setLoading(false)
      }
    }, 300)

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [query])

  // Handle click outside to close results
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowResults(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleResultClick = (leader) => {
    setQuery(leader.name)
    setShowResults(false)
    // Navigate to leader detail
    window.location.href = `/leader/${leader.id}`
  }

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    if (results.length > 0) {
      handleResultClick(results[0])
    } else if (query.trim()) {
      // Navigate to leaders page with search query
      window.location.href = `/leaders?search=${encodeURIComponent(query)}`
    }
  }

  return (
    <section className="py-16 bg-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-8"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Find Your Representative
          </h2>
          <p className="text-xl text-gray-600">
            Search for political leaders by name, party, or constituency
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          viewport={{ once: true }}
          className="relative"
          ref={searchRef}
        >
          <form onSubmit={handleSearchSubmit} className="relative">
            <div className="relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search for leaders, parties, or constituencies..."
                className="w-full px-6 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-primary-600 focus:outline-none transition-colors pr-16"
              />
              
              {/* Search Icon */}
              <button
                type="submit"
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-nepal-red text-white p-3 rounded-lg hover:bg-red-700 transition-colors"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                )}
              </button>
            </div>
          </form>

          {/* Search Results Dropdown */}
          <AnimatePresence>
            {showResults && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-xl shadow-xl z-50 max-h-96 overflow-y-auto"
              >
                {results.length > 0 ? (
                  <div className="py-2">
                    {results.map((leader, index) => (
                      <motion.div
                        key={leader.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.2, delay: index * 0.05 }}
                        onClick={() => handleResultClick(leader)}
                        className="px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                      >
                        <div className="flex items-center space-x-3">
                          <div className="flex-shrink-0">
                            <img
                              src={leader.metadata?.image_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(leader.name.split(' ').map(n => n[0]).join(''))}&background=dc2626&color=fff&size=40`}
                              alt={leader.name}
                              className="w-10 h-10 rounded-full object-cover"
                              onError={(e) => {
                                e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(leader.name.split(' ').map(n => n[0]).join(''))}&background=dc2626&color=fff&size=40`
                              }}
                            />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="font-semibold text-gray-900 truncate">
                              {leader.name}
                            </div>
                            <div className="text-sm text-gray-600 truncate">
                              {leader.metadata?.political_party && (
                                <span className="mr-2">{leader.metadata.political_party}</span>
                              )}
                              {leader.metadata?.district && (
                                <span>• {leader.metadata.district}</span>
                              )}
                            </div>
                          </div>
                          <div className="flex-shrink-0">
                            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                            </svg>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                ) : query.trim().length >= 2 && !loading ? (
                  <div className="px-4 py-8 text-center text-gray-500">
                    <div className="text-4xl mb-2">🔍</div>
                    <div>No results found for "{query}"</div>
                    <div className="text-sm mt-1">Try searching with different keywords</div>
                  </div>
                ) : null}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Quick Search Suggestions */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="mt-8 text-center"
        >
          <div className="text-sm text-gray-600 mb-3">Popular searches:</div>
          <div className="flex flex-wrap justify-center gap-2">
            {['Nepali Congress', 'CPN UML', 'Kathmandu', 'Prime Minister', 'Bagmati Province'].map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => setQuery(suggestion)}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default SearchSection