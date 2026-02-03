import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Helmet } from 'react-helmet-async'
import { fetchLeaderById } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

const LeaderDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [leader, setLeader] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [imageError, setImageError] = useState(false)

  useEffect(() => {
    loadLeader()
  }, [id])

  const loadLeader = async () => {
    try {
      setLoading(true)
      const data = await fetchLeaderById(id)
      setLeader(data)
      setError(null)
    } catch (err) {
      console.error('Error loading leader:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getImageUrl = () => {
    if (imageError || !leader?.metadata?.image_url) {
      const initials = leader?.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'NA'
      return `https://ui-avatars.com/api/?name=${encodeURIComponent(initials)}&background=dc2626&color=fff&size=400&font-size=0.4`
    }
    return leader.metadata.image_url
  }

  const getPartyColor = (partyName) => {
    const colors = {
      'Nepali Congress': 'bg-green-100 text-green-800 border-green-200',
      'CPN (UML)': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'CPN (Maoist Centre)': 'bg-red-100 text-red-800 border-red-200',
      'Rastriya Swatantra Party': 'bg-blue-100 text-blue-800 border-blue-200',
      'Janata Samajbadi Party': 'bg-orange-100 text-orange-800 border-orange-200',
      'CPN (Unified Socialist)': 'bg-purple-100 text-purple-800 border-purple-200',
    }
    return colors[partyName] || 'bg-gray-100 text-gray-800 border-gray-200'
  }

  if (loading) {
    return <LoadingSpinner />
  }

  if (error || !leader) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">😞</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Leader Not Found</h2>
          <p className="text-gray-600 mb-6">
            {error || 'The leader you are looking for could not be found.'}
          </p>
          <button
            onClick={() => navigate('/leaders')}
            className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
          >
            Browse All Leaders
          </button>
        </div>
      </div>
    )
  }

  return (
    <>
      <Helmet>
        <title>{leader.name} - Who's My Neta Nepal</title>
        <meta name="description" content={`Learn about ${leader.name}, ${leader.metadata?.political_party || 'political leader'} from ${leader.metadata?.district || 'Nepal'}.`} />
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-primary-600 to-red-700 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="flex flex-col lg:flex-row items-center lg:items-start space-y-6 lg:space-y-0 lg:space-x-8"
            >
              {/* Profile Image */}
              <div className="flex-shrink-0">
                <div className="relative">
                  <img
                    src={getImageUrl()}
                    alt={leader.name}
                    className="w-48 h-48 lg:w-64 lg:h-64 rounded-full object-cover border-4 border-white shadow-xl"
                    onError={() => setImageError(true)}
                  />
                  {leader.metadata?.gender === 'Female' && (
                    <div className="absolute -top-2 -right-2 bg-pink-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                      👩‍💼 Female Leader
                    </div>
                  )}
                </div>
              </div>

              {/* Basic Info */}
              <div className="flex-1 text-center lg:text-left">
                <h1 className="text-4xl lg:text-5xl font-bold mb-2">{leader.name}</h1>
                {leader.name_nepali && (
                  <p className="text-xl text-red-100 mb-4 font-nepali">{leader.name_nepali}</p>
                )}
                
                {/* Party Badge */}
                {leader.metadata?.political_party && (
                  <div className="inline-block mb-4">
                    <span className={`px-4 py-2 rounded-full text-sm font-medium border ${getPartyColor(leader.metadata.political_party)} bg-white`}>
                      🏛️ {leader.metadata.political_party}
                    </span>
                  </div>
                )}

                {/* Location */}
                <div className="flex flex-col lg:flex-row lg:items-center lg:space-x-6 space-y-2 lg:space-y-0 text-red-100">
                  {leader.metadata?.constituency && (
                    <div className="flex items-center justify-center lg:justify-start">
                      <span className="mr-2">🗳️</span>
                      <span>Constituency: {leader.metadata.constituency}</span>
                    </div>
                  )}
                  {leader.metadata?.district && (
                    <div className="flex items-center justify-center lg:justify-start">
                      <span className="mr-2">📍</span>
                      <span>{leader.metadata.district}, {leader.metadata?.province || 'Nepal'}</span>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Info */}
            <div className="lg:col-span-2 space-y-8">
              {/* Personal Information */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="bg-white rounded-xl shadow-lg p-6"
              >
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Personal Information</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {leader.metadata?.age && leader.metadata.age !== 'N/A' && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Age</label>
                      <p className="text-lg text-gray-900">{leader.metadata.age} years old</p>
                    </div>
                  )}
                  
                  {leader.metadata?.gender && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Gender</label>
                      <p className="text-lg text-gray-900">{leader.metadata.gender}</p>
                    </div>
                  )}
                  
                  {leader.metadata?.education && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Education</label>
                      <p className="text-lg text-gray-900">{leader.metadata.education}</p>
                    </div>
                  )}
                  
                  {leader.metadata?.dob && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Date of Birth</label>
                      <p className="text-lg text-gray-900">{new Date(leader.metadata.dob).toLocaleDateString()}</p>
                    </div>
                  )}
                </div>
              </motion.div>

              {/* Political Information */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                className="bg-white rounded-xl shadow-lg p-6"
              >
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Political Information</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {leader.metadata?.political_party && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Political Party</label>
                      <p className="text-lg text-gray-900">{leader.metadata.political_party}</p>
                    </div>
                  )}
                  
                  {leader.metadata?.election_type && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Election Type</label>
                      <p className="text-lg text-gray-900">{leader.metadata.election_type}</p>
                    </div>
                  )}
                  
                  {leader.metadata?.tenure_end_date && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Tenure End Date</label>
                      <p className="text-lg text-gray-900">{new Date(leader.metadata.tenure_end_date).toLocaleDateString()}</p>
                    </div>
                  )}
                  
                  {leader.metadata?.registered_date && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Registered Date</label>
                      <p className="text-lg text-gray-900">{new Date(leader.metadata.registered_date).toLocaleDateString()}</p>
                    </div>
                  )}
                </div>
              </motion.div>

              {/* Financial Information */}
              {(leader.metadata?.assets || leader.metadata?.liabilities) && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                  className="bg-white rounded-xl shadow-lg p-6"
                >
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Financial Declaration</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {leader.metadata?.assets && (
                      <div>
                        <label className="text-sm font-medium text-gray-500">Assets</label>
                        <p className="text-lg text-gray-900">
                          NPR {parseInt(leader.metadata.assets).toLocaleString()}
                        </p>
                      </div>
                    )}
                    
                    {leader.metadata?.liabilities && (
                      <div>
                        <label className="text-sm font-medium text-gray-500">Liabilities</label>
                        <p className="text-lg text-gray-900">
                          NPR {parseInt(leader.metadata.liabilities).toLocaleString()}
                        </p>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Quick Stats */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="bg-white rounded-xl shadow-lg p-6"
              >
                <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Stats</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Criminal Cases</span>
                    <span className={`font-semibold ${
                      (leader.metadata?.criminal_cases || 0) > 0 ? 'text-red-600' : 'text-green-600'
                    }`}>
                      {leader.metadata?.criminal_cases || 0}
                    </span>
                  </div>
                  
                  {leader.metadata?.experience_years && leader.metadata.experience_years !== 'N/A' && (
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Experience</span>
                      <span className="font-semibold text-gray-900">
                        {leader.metadata.experience_years}
                      </span>
                    </div>
                  )}
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Province</span>
                    <span className="font-semibold text-gray-900">
                      {leader.metadata?.province || 'N/A'}
                    </span>
                  </div>
                </div>
              </motion.div>

              {/* Contact Information */}
              {leader.metadata?.social_media && Object.values(leader.metadata.social_media).some(Boolean) && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                  className="bg-white rounded-xl shadow-lg p-6"
                >
                  <h3 className="text-lg font-bold text-gray-900 mb-4">Social Media</h3>
                  <div className="space-y-3">
                    {leader.metadata.social_media.facebook && (
                      <a
                        href={leader.metadata.social_media.facebook}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-3 text-blue-600 hover:text-blue-800 transition-colors"
                      >
                        <span>📘</span>
                        <span>Facebook</span>
                      </a>
                    )}
                    
                    {leader.metadata.social_media.twitter && (
                      <a
                        href={leader.metadata.social_media.twitter}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-3 text-blue-400 hover:text-blue-600 transition-colors"
                      >
                        <span>🐦</span>
                        <span>Twitter</span>
                      </a>
                    )}
                    
                    {leader.metadata.social_media.instagram && (
                      <a
                        href={leader.metadata.social_media.instagram}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-3 text-pink-600 hover:text-pink-800 transition-colors"
                      >
                        <span>📷</span>
                        <span>Instagram</span>
                      </a>
                    )}
                  </div>
                </motion.div>
              )}

              {/* Actions */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="bg-white rounded-xl shadow-lg p-6"
              >
                <h3 className="text-lg font-bold text-gray-900 mb-4">Actions</h3>
                <div className="space-y-3">
                  <button
                    onClick={() => navigate('/leaders')}
                    className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors"
                  >
                    Browse All Leaders
                  </button>
                  
                  {leader.metadata?.political_party && (
                    <button
                      onClick={() => navigate(`/leaders?party=${encodeURIComponent(leader.metadata.political_party)}`)}
                      className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors"
                    >
                      View Party Members
                    </button>
                  )}
                  
                  <button
                    onClick={() => navigate('/parties')}
                    className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    View All Parties
                  </button>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default LeaderDetail