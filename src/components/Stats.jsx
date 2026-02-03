import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { fetchStats } from '../services/api'

const Stats = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await fetchStats()
        setStats(data)
      } catch (error) {
        console.error('Error loading stats:', error)
        // Use fallback stats
        setStats({
          totalLeaders: 275,
          totalParties: 15,
          totalProvinces: 7,
          genderDistribution: { male: 220, female: 55, other: 0 }
        })
      } finally {
        setLoading(false)
      }
    }

    loadStats()
  }, [])

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-64 mx-auto mb-4"></div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-gray-100 rounded-lg p-6">
                  <div className="h-12 bg-gray-200 rounded mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  const statItems = [
    {
      label: 'Political Leaders',
      value: stats?.totalLeaders || 275,
      icon: '👥',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      label: 'Political Parties',
      value: stats?.totalParties || 15,
      icon: '🏛️',
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      label: 'Provinces',
      value: stats?.totalProvinces || 7,
      icon: '🗺️',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      label: 'Female Leaders',
      value: stats?.genderDistribution?.female || 55,
      icon: '👩‍💼',
      color: 'text-pink-600',
      bgColor: 'bg-pink-50'
    }
  ]

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
          Nepal Political Landscape
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          viewport={{ once: true }}
          className="text-xl text-gray-600 max-w-2xl mx-auto"
        >
          Comprehensive data about Nepal's political representatives and institutions
        </motion.p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 lg:gap-8">
        {statItems.map((item, index) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
            viewport={{ once: true }}
            whileHover={{ scale: 1.05 }}
            className={`${item.bgColor} rounded-xl p-6 text-center shadow-lg hover:shadow-xl transition-all duration-300`}
          >
            <div className="text-4xl mb-3">{item.icon}</div>
            <motion.div
              initial={{ scale: 0 }}
              whileInView={{ scale: 1 }}
              transition={{ duration: 0.8, delay: index * 0.1 + 0.3, type: "spring" }}
              viewport={{ once: true }}
              className={`text-3xl md:text-4xl font-bold ${item.color} mb-2`}
            >
              {item.value.toLocaleString()}
            </motion.div>
            <div className="text-gray-700 font-medium">{item.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Additional Stats */}
      {stats?.provinces && (
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          viewport={{ once: true }}
          className="mt-12 bg-gradient-to-r from-primary-600 to-red-700 rounded-xl p-8 text-white"
        >
          <h3 className="text-2xl font-bold mb-6 text-center">Provincial Representation</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
            {stats.provinces.map((province, index) => (
              <motion.div
                key={province}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="bg-white bg-opacity-20 rounded-lg p-4 text-center backdrop-blur-sm"
              >
                <div className="font-semibold text-sm">{province}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}

export default Stats