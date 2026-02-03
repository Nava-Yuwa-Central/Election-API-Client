import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { fetchLeaders, getPartyClass } from '../services/api'
import CandidateCard from './CandidateCard'

const FeaturedLeaders = () => {
  const [leaders, setLeaders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const loadFeaturedLeaders = async () => {
      try {
        setLoading(true)
        const data = await fetchLeaders({ limit: 12 })
        setLeaders(data)
        setError(null)
      } catch (err) {
        console.error('Error loading featured leaders:', err)
        setError(err.message)
        // Set fallback data
        setLeaders([])
      } finally {
        setLoading(false)
      }
    }

    loadFeaturedLeaders()
  }, [])

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-64 mx-auto mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-96 mx-auto"></div>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[...Array(12)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-gray-200 rounded-xl h-80"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="text-red-600 mb-4">⚠️ Unable to load featured leaders</div>
          <button 
            onClick={() => window.location.reload()}
            className="bg-nepal-red text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-12">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-3xl md:text-4xl font-bold text-gray-900 mb-4"
        >
          Featured Leaders
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          viewport={{ once: true }}
          className="text-xl text-gray-600 max-w-2xl mx-auto"
        >
          Meet some of Nepal's prominent political leaders and their contributions
        </motion.p>
      </div>

      {leaders.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500 mb-4">No leaders data available</div>
          <button 
            onClick={() => window.location.reload()}
            className="bg-nepal-red text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {leaders.map((leader, index) => (
            <motion.div
              key={leader.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <CandidateCard leader={leader} />
            </motion.div>
          ))}
        </div>
      )}

      {/* View All Button */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
        viewport={{ once: true }}
        className="text-center mt-12"
      >
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="bg-nepal-red text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-red-700 transition-colors shadow-lg"
          onClick={() => window.location.href = '/leaders'}
        >
          View All Leaders
        </motion.button>
      </motion.div>
    </div>
  )
}

export default FeaturedLeaders