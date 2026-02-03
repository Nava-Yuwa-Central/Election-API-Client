import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { getPartyClass } from '../services/api'

const CandidateCard = ({ leader }) => {
  const [imageError, setImageError] = useState(false)
  const [imageLoading, setImageLoading] = useState(true)

  const handleImageError = () => {
    setImageError(true)
    setImageLoading(false)
  }

  const handleImageLoad = () => {
    setImageLoading(false)
  }

  const getImageUrl = () => {
    if (imageError || !leader.metadata?.image_url) {
      // Generate placeholder with leader's initials
      const initials = leader.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
      const partyColor = getPartyColorCode(leader.metadata?.political_party)
      return `https://ui-avatars.com/api/?name=${encodeURIComponent(initials)}&background=${partyColor}&color=fff&size=400&font-size=0.4`
    }
    return leader.metadata.image_url
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

  const getPartyBadgeColor = (partyName) => {
    const party = partyName?.toLowerCase() || ''
    if (party.includes('congress')) return 'bg-green-100 text-green-800'
    if (party.includes('uml')) return 'bg-yellow-100 text-yellow-800'
    if (party.includes('maoist')) return 'bg-red-100 text-red-800'
    if (party.includes('rastriya') && party.includes('swatantra')) return 'bg-blue-100 text-blue-800'
    if (party.includes('samajwadi') || party.includes('janata')) return 'bg-orange-100 text-orange-800'
    return 'bg-gray-100 text-gray-800'
  }

  const handleCardClick = () => {
    // Navigate to leader detail page
    window.location.href = `/leader/${leader.id}`
  }

  return (
    <motion.div
      whileHover={{ y: -5, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden"
      onClick={handleCardClick}
    >
      {/* Image Section */}
      <div className="relative h-48 bg-gray-100 overflow-hidden">
        {imageLoading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-nepal-red"></div>
          </div>
        )}
        <img
          src={getImageUrl()}
          alt={leader.name}
          className={`w-full h-full object-cover transition-opacity duration-300 ${
            imageLoading ? 'opacity-0' : 'opacity-100'
          }`}
          onError={handleImageError}
          onLoad={handleImageLoad}
        />
        
        {/* Party Badge */}
        {leader.metadata?.political_party && (
          <div className="absolute top-3 left-3">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPartyBadgeColor(leader.metadata.political_party)}`}>
              {leader.metadata.political_party}
            </span>
          </div>
        )}

        {/* Gender Badge */}
        {leader.metadata?.gender === 'Female' && (
          <div className="absolute top-3 right-3">
            <span className="bg-pink-100 text-pink-800 px-2 py-1 rounded-full text-xs font-medium">
              👩‍💼 Female
            </span>
          </div>
        )}
      </div>

      {/* Content Section */}
      <div className="p-4">
        {/* Name */}
        <h3 className="font-bold text-lg text-gray-900 mb-1 line-clamp-2">
          {leader.name}
        </h3>
        
        {/* Nepali Name */}
        {leader.name_nepali && (
          <p className="text-sm text-gray-600 mb-2 font-nepali">
            {leader.name_nepali}
          </p>
        )}

        {/* Location */}
        <div className="flex items-center text-sm text-gray-600 mb-2">
          <span className="mr-1">📍</span>
          <span className="truncate">
            {leader.metadata?.constituency || leader.metadata?.district || 'Nepal'}
          </span>
        </div>

        {/* Age */}
        {leader.metadata?.age && leader.metadata.age !== 'N/A' && (
          <div className="flex items-center text-sm text-gray-600 mb-2">
            <span className="mr-1">🎂</span>
            <span>{leader.metadata.age} years old</span>
          </div>
        )}

        {/* Education */}
        {leader.metadata?.education && (
          <div className="flex items-center text-sm text-gray-600 mb-3">
            <span className="mr-1">🎓</span>
            <span className="truncate">{leader.metadata.education}</span>
          </div>
        )}

        {/* Stats Row */}
        <div className="flex justify-between items-center pt-3 border-t border-gray-100">
          <div className="text-center">
            <div className="text-xs text-gray-500">Experience</div>
            <div className="font-semibold text-sm">
              {leader.metadata?.experience_years || 'N/A'}
            </div>
          </div>
          
          {leader.metadata?.criminal_cases !== undefined && (
            <div className="text-center">
              <div className="text-xs text-gray-500">Cases</div>
              <div className={`font-semibold text-sm ${
                leader.metadata.criminal_cases > 0 ? 'text-red-600' : 'text-green-600'
              }`}>
                {leader.metadata.criminal_cases}
              </div>
            </div>
          )}
          
          <div className="text-center">
            <div className="text-xs text-gray-500">Province</div>
            <div className="font-semibold text-sm truncate max-w-16">
              {leader.metadata?.province || 'N/A'}
            </div>
          </div>
        </div>
      </div>

      {/* Hover Effect Overlay */}
      <motion.div
        className="absolute inset-0 bg-nepal-red bg-opacity-0 hover:bg-opacity-5 transition-all duration-300 pointer-events-none"
        whileHover={{ backgroundColor: 'rgba(220, 38, 38, 0.05)' }}
      />
    </motion.div>
  )
}

export default CandidateCard