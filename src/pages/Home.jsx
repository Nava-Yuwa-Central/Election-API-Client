import React from 'react'
import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import { Helmet } from 'react-helmet-async'
import Hero from '../components/Hero'
import Stats from '../components/Stats'
import FeaturedLeaders from '../components/FeaturedLeaders'
import SearchSection from '../components/SearchSection'

const Home = () => {
  const [statsRef, statsInView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  })

  const [leadersRef, leadersInView] = useInView({
    triggerOnce: true,
    threshold: 0.1,
  })

  return (
    <>
      <Helmet>
        <title>Who's My Neta Nepal - Know Your Political Representatives</title>
        <meta name="description" content="Discover and learn about Nepal's political leaders, their parties, constituencies, and performance. Transparent data for informed citizens." />
      </Helmet>

      <div className="min-h-screen">
        {/* Hero Section */}
        <Hero />

        {/* Search Section */}
        <SearchSection />

        {/* Stats Section */}
        <motion.section
          ref={statsRef}
          initial={{ opacity: 0, y: 50 }}
          animate={statsInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="py-16 bg-white"
        >
          <Stats />
        </motion.section>

        {/* Featured Leaders Section */}
        <motion.section
          ref={leadersRef}
          initial={{ opacity: 0, y: 50 }}
          animate={leadersInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="py-16 bg-gray-50"
        >
          <FeaturedLeaders />
        </motion.section>

        {/* Call to Action */}
        <section className="py-16 bg-gradient-to-r from-primary-600 to-red-700 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Stay Informed About Your Representatives
              </h2>
              <p className="text-xl mb-8 text-red-100">
                Transparency and accountability in Nepali politics
              </p>
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <button className="bg-white text-primary-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors shadow-lg">
                  Explore Leaders
                </button>
              </motion.div>
            </motion.div>
          </div>
        </section>
      </div>
    </>
  )
}

export default Home