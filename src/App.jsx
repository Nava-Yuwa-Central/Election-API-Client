import React, { Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import Navbar from './components/Navbar'
import LoadingSpinner from './components/LoadingSpinner'
import ErrorBoundary from './components/ErrorBoundary'

// Lazy load pages for better performance
const Home = React.lazy(() => import('./pages/Home'))
const Leaders = React.lazy(() => import('./pages/Leaders'))
const Parties = React.lazy(() => import('./pages/Parties'))
const LeaderDetail = React.lazy(() => import('./pages/LeaderDetail'))

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />
      
      <ErrorBoundary>
        <motion.main 
          className="flex-1"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <Suspense fallback={<LoadingSpinner />}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/leaders" element={<Leaders />} />
              <Route path="/parties" element={<Parties />} />
              <Route path="/leader/:id" element={<LeaderDetail />} />
            </Routes>
          </Suspense>
        </motion.main>
      </ErrorBoundary>
      
      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            © 2025 Who's My Neta Nepal. Made with ❤️ for transparency in Nepali politics.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App