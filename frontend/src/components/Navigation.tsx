import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const Navigation: React.FC = () => {
  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="bg-gradient-to-r from-blue-600 to-blue-800 p-4 fixed w-full top-0 z-50"
    >
      <div className="container mx-auto flex justify-between items-center">
        <motion.div
          whileHover={{ scale: 1.1 }}
          className="text-white text-2xl font-bold"
        >
          VoterChain
        </motion.div>
        <div className="flex space-x-6">
          <NavLink to="/">Home</NavLink>
          <NavLink to="/verify">Verify</NavLink>
          <NavLink to="/dashboard">Dashboard</NavLink>
        </div>
      </div>
    </motion.nav>
  );
};

const NavLink: React.FC<{ to: string; children: React.ReactNode }> = ({ to, children }) => (
  <motion.div whileHover={{ scale: 1.1 }}>
    <Link
      to={to}
      className="text-white hover:text-blue-200 transition-colors duration-200"
    >
      {children}
    </Link>
  </motion.div>
);

export default Navigation; 