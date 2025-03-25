import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100 pt-20">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center py-12"
        >
          <h1 className="text-5xl font-bold text-blue-800 mb-6">
            AI & Blockchain Voter Verification
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Secure, transparent, and efficient voter verification powered by cutting-edge technology
          </p>
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="inline-block"
          >
            <Link
              to="/verify"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors duration-200"
            >
              Start Verification
            </Link>
          </motion.div>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 mt-12">
          <FeatureCard
            title="AI-Powered"
            description="Advanced fingerprint recognition using state-of-the-art AI models"
            icon="🤖"
          />
          <FeatureCard
            title="Blockchain Security"
            description="Immutable and transparent verification records on the blockchain"
            icon="🔒"
          />
          <FeatureCard
            title="Real-time Verification"
            description="Instant results with high accuracy and reliability"
            icon="⚡"
          />
        </div>
      </div>
    </div>
  );
};

const FeatureCard: React.FC<{
  title: string;
  description: string;
  icon: string;
}> = ({ title, description, icon }) => (
  <motion.div
    whileHover={{ y: -10 }}
    className="bg-white p-6 rounded-xl shadow-lg"
  >
    <div className="text-4xl mb-4">{icon}</div>
    <h3 className="text-xl font-semibold text-blue-800 mb-2">{title}</h3>
    <p className="text-gray-600">{description}</p>
  </motion.div>
);

export default Home; 