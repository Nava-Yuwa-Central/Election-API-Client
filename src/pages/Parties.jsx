import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Helmet } from 'react-helmet-async'
import { fetchParties, fetchLeaders } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

const Parties = () => {
  const [parties, setParties] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedParty, setSelectedParty] = useState(null)
  const [partyLeaders, setPartyLeaders] = useState([])

  useEffect(() => {
    loadParties()
  }, [])

  const loadParties = async () => {
    try {
      setLoading(true)
      const [partiesData, leadersData] = await Promise.all([
        fetchParties(),
        fetchLeaders({ limit: 1000 })
      ])

      // Enhance parties with leader counts and additional data
      const enhancedParties = partiesData.map(party => {
        const partyLeaders = leadersData.filter(leader => 
          leader.metadata?.political_party === party.name
        )
        
        return {
          ...party,
          memberCount: partyLeaders.length,
          leaders: partyLeaders,
          femaleCount: partyLeaders.filter(l => l.metadata?.gender === 'Female').length,
          avgAge: calculateAverageAge(partyLeaders)
        }
      }).sort((a, b) => b.memberCount - a.memberCount) // Sort by member count

      setParties(enhancedParties)
    } catch (error) {
      console.error('Error loading parties:', error)
    } finally {
      setLoading(false)
    }
  }

  const calculateAverageAge = (leaders) => {
    const ages = leaders
      .map(l => parseInt(l.metadata?.age))
      .filter(age => !isNaN(age))
    
    if (ages.length === 0) return 'N/A'
    return Math.round(ages.reduce((sum, age) => sum + age, 0) / ages.length)
  }

  const getPartyColor = (partyName) => {
    const colors = {
      'Nepali Congress': 'from-green-500 to-green-600',
      'CPN (UML)': 'from-yellow-500 to-yellow-600',
      'CPN (Maoist Centre)': 'from-red-500 to-red-600',
      'Rastriya Swatantra Party': 'from-blue-500 to-blue-600',
      'Janata Samajbadi Party': 'from-orange-500 to-orange-600',
      'CPN (Unified Socialist)': 'from-purple-500 to-purple-600',
    }
    return colors[partyName] || 'from-gray-500 to-gray-600'
  }

  const getPartyTextColor = (partyName) => {
    const colors = {
      'Nepali Congress': 'text-green-700',
      'CPN (UML)': 'text-yellow-700',
      'CPN (Maoist Centre)': 'text-red-700',
      'Rastriya Swatantra Party': 'text-blue-700',
      'Janata Samajbadi Party': 'text-orange-700',
      'CPN (Unified Socialist)': 'text-purple-700',
    }
    return colors[partyName] || 'text-gray-700'
  }

  const handlePartyClick = (party) => {
    setSelectedParty(party)
    setPartyLeaders(party.leaders || [])
  }

  if (loading) {
    return <LoadingSpinner />
  }

  return (
    <>
      <Helmet>
        <title>Political Parties - Who's My Neta Nepal</title>
        <meta name="description" content="Explore Nepal's political parties, their members, and representation statistics." />
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
              Political Parties
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Explore Nepal's political landscape through party representation and statistics
            </p>
          </motion.div>

          {/* Parties Grid */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8"
          >
            {parties.map((party, index) => (
              <motion.div
                key={party.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                whileHover={{ y: -5, scale: 1.02 }}
                onClick={() => handlePartyClick(party)}
                className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden"
              >
                {/* Party Header */}
                <div className={`bg-gradient-to-r ${getPartyColor(party.name)} p-6 text-white`}>
                  <h3 className="text-xl font-bold mb-2">{party.name}</h3>
                  <div className="flex items-center justify-between">
                    <span className="text-sm opacity-90">
                      {party.memberCount} Members
                    </span>
                    <div className="text-2xl">🏛️</div>
                  </div>
                </div>

                {/* Party Stats */}
                <div className="p-6">
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900">
                        {party.memberCount}
                      </div>
                      <div className="text-sm text-gray-600">Total Members</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-pink-600">
                        {party.femaleCount}
                      </div>
                      <div className="text-sm text-gray-600">Female Members</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center">
                      <div className="text-lg font-semibold text-gray-900">
                        {party.avgAge}
                      </div>
                      <div className="text-sm text-gray-600">Avg Age</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-gray-900">
                        {party.femaleCount > 0 ? Math.round((party.femaleCount / party.memberCount) * 100) : 0}%
                      </div>
                      <div className="text-sm text-gray-600">Female %</div>
                    </div>
                  </div>

                  {/* Progress Bar for Female Representation */}
                  <div className="mt-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Female Representation</span>
                      <span>{party.femaleCount > 0 ? Math.round((party.femaleCount / party.memberCount) * 100) : 0}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-pink-500 h-2 rounded-full transition-all duration-500"
                        style={{ 
                          width: `${party.femaleCount > 0 ? (party.femaleCount / party.memberCount) * 100 : 0}%` 
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>

          {/* Party Details Modal/Section */}
          {selectedParty && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="bg-white rounded-xl shadow-xl p-8 mb-8"
            >
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className={`text-3xl font-bold ${getPartyTextColor(selectedParty.name)} mb-2`}>
                    {selectedParty.name}
                  </h2>
                  <p className="text-gray-600">
                    {selectedParty.description || `Political party with ${selectedParty.memberCount} elected representatives`}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedParty(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>

              {/* Detailed Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-3xl font-bold text-gray-900 mb-1">
                    {selectedParty.memberCount}
                  </div>
                  <div className="text-gray-600">Total Members</div>
                </div>
                <div className="text-center p-4 bg-pink-50 rounded-lg">
                  <div className="text-3xl font-bold text-pink-600 mb-1">
                    {selectedParty.femaleCount}
                  </div>
                  <div className="text-gray-600">Female Members</div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-3xl font-bold text-blue-600 mb-1">
                    {selectedParty.memberCount - selectedParty.femaleCount}
                  </div>
                  <div className="text-gray-600">Male Members</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-3xl font-bold text-green-600 mb-1">
                    {selectedParty.avgAge}
                  </div>
                  <div className="text-gray-600">Average Age</div>
                </div>
              </div>

              {/* Party Members Preview */}
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  Party Members ({partyLeaders.length})
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
                  {partyLeaders.slice(0, 12).map((leader) => (
                    <div
                      key={leader.id}
                      onClick={() => window.location.href = `/leader/${leader.id}`}
                      className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                    >
                      <img
                        src={leader.metadata?.image_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(leader.name.split(' ').map(n => n[0]).join(''))}&background=dc2626&color=fff&size=40`}
                        alt={leader.name}
                        className="w-10 h-10 rounded-full object-cover"
                        onError={(e) => {
                          e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(leader.name.split(' ').map(n => n[0]).join(''))}&background=dc2626&color=fff&size=40`
                        }}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900 truncate">
                          {leader.name}
                        </div>
                        <div className="text-sm text-gray-600 truncate">
                          {leader.metadata?.district}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                {partyLeaders.length > 12 && (
                  <div className="mt-4 text-center">
                    <button
                      onClick={() => window.location.href = `/leaders?party=${encodeURIComponent(selectedParty.name)}`}
                      className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors"
                    >
                      View All {partyLeaders.length} Members
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Summary Stats */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="bg-gradient-to-r from-primary-600 to-red-700 rounded-xl p-8 text-white text-center"
          >
            <h2 className="text-2xl font-bold mb-4">Political Representation Overview</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div>
                <div className="text-3xl font-bold mb-1">{parties.length}</div>
                <div className="text-red-100">Total Parties</div>
              </div>
              <div>
                <div className="text-3xl font-bold mb-1">
                  {parties.reduce((sum, party) => sum + party.memberCount, 0)}
                </div>
                <div className="text-red-100">Total Representatives</div>
              </div>
              <div>
                <div className="text-3xl font-bold mb-1">
                  {parties.reduce((sum, party) => sum + party.femaleCount, 0)}
                </div>
                <div className="text-red-100">Female Representatives</div>
              </div>
              <div>
                <div className="text-3xl font-bold mb-1">
                  {Math.round((parties.reduce((sum, party) => sum + party.femaleCount, 0) / parties.reduce((sum, party) => sum + party.memberCount, 0)) * 100) || 0}%
                </div>
                <div className="text-red-100">Female Representation</div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </>
  )
}

export default Parties