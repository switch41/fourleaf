import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface VerificationLog {
  id: string;
  timestamp: string;
  status: 'success' | 'failure';
  voterID: string;
}

interface Statistics {
  totalVerifications: number;
  successfulVerifications: number;
  failedVerifications: number;
  averageResponseTime: number;
}

const Dashboard: React.FC = () => {
  const [logs, setLogs] = useState<VerificationLog[]>([]);
  const [stats, setStats] = useState<Statistics>({
    totalVerifications: 0,
    successfulVerifications: 0,
    failedVerifications: 0,
    averageResponseTime: 0,
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [logsResponse, statsResponse] = await Promise.all([
        fetch('http://localhost:5000/api/logs'),
        fetch('http://localhost:5000/api/statistics'),
      ]);

      if (logsResponse.ok && statsResponse.ok) {
        const logsData = await logsResponse.json();
        const statsData = await statsResponse.json();
        setLogs(logsData);
        setStats(statsData);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 pt-20">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-8"
        >
          <h2 className="text-3xl font-bold text-blue-800">
            Verification Dashboard
          </h2>

          <div className="grid md:grid-cols-4 gap-6">
            <StatCard
              title="Total Verifications"
              value={stats.totalVerifications}
              icon="📊"
            />
            <StatCard
              title="Successful"
              value={stats.successfulVerifications}
              icon="✅"
            />
            <StatCard
              title="Failed"
              value={stats.failedVerifications}
              icon="❌"
            />
            <StatCard
              title="Avg. Response Time"
              value={`${stats.averageResponseTime.toFixed(2)}ms`}
              icon="⚡"
            />
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold text-blue-800 mb-4">
              Recent Verification Logs
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b-2 border-gray-200">
                    <th className="text-left py-3 px-4">Timestamp</th>
                    <th className="text-left py-3 px-4">Voter ID</th>
                    <th className="text-left py-3 px-4">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <motion.tr
                      key={log.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="border-b border-gray-100 hover:bg-gray-50"
                    >
                      <td className="py-3 px-4">
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                      <td className="py-3 px-4">{log.voterID}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-1 rounded-full text-sm ${
                            log.status === 'success'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-red-100 text-red-700'
                          }`}
                        >
                          {log.status}
                        </span>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

const StatCard: React.FC<{
  title: string;
  value: number | string;
  icon: string;
}> = ({ title, value, icon }) => (
  <motion.div
    whileHover={{ y: -5 }}
    className="bg-white rounded-xl shadow-lg p-6"
  >
    <div className="text-3xl mb-2">{icon}</div>
    <div className="text-gray-600">{title}</div>
    <div className="text-2xl font-bold text-blue-800 mt-2">{value}</div>
  </motion.div>
);

export default Dashboard; 