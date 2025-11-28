import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, Activity, Lock } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const IDSDashboard = () => {
    const [stats, setStats] = useState(null);
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    const fetchData = async () => {
        try {
            const [statsRes, alertsRes] = await Promise.all([
                fetch('http://localhost:8000/api/v1/ids/stats'),
                fetch('http://localhost:8000/api/v1/ids/alerts?limit=10')
            ]);

            const statsData = await statsRes.json();
            const alertsData = await alertsRes.json();

            setStats(statsData);
            setAlerts(alertsData.alerts);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching IDS data:', error);
            setLoading(false);
        }
    };

    if (loading) return <div className="p-6">Loading IDS data...</div>;

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Intrusion Detection System</h1>
                    <p className="text-gray-600 mt-1">Real-time network threat monitoring (Suricata)</p>
                </div>
                <div className="flex gap-2">
                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium flex items-center">
                        <Activity className="w-4 h-4 mr-1" /> Engine Active
                    </span>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <StatCard
                    title="Total Alerts (24h)"
                    value={stats?.total_alerts_24h || 0}
                    icon={Shield}
                    color="blue"
                />
                <StatCard
                    title="High Severity"
                    value={stats?.high_severity || 0}
                    icon={AlertTriangle}
                    color="red"
                />
                <StatCard
                    title="Attacks Blocked"
                    value={stats?.blocked || 0}
                    icon={Lock}
                    color="green"
                />
                <StatCard
                    title="Active Rules"
                    value="2,450"
                    icon={Activity}
                    color="purple"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Recent Alerts */}
                <div className="bg-white rounded-xl shadow-sm p-6">
                    <h2 className="text-xl font-semibold mb-4">Recent Alerts</h2>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="border-b border-gray-200 text-gray-500 text-sm">
                                    <th className="pb-3">Time</th>
                                    <th className="pb-3">Severity</th>
                                    <th className="pb-3">Signature</th>
                                    <th className="pb-3">Source</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {alerts.map((alert) => (
                                    <tr key={alert.id} className="hover:bg-gray-50">
                                        <td className="py-3 text-sm text-gray-600">
                                            {new Date(alert.timestamp).toLocaleTimeString()}
                                        </td>
                                        <td className="py-3">
                                            <SeverityBadge level={alert.alert_severity} />
                                        </td>
                                        <td className="py-3 text-sm font-medium text-gray-900">
                                            {alert.alert_signature}
                                        </td>
                                        <td className="py-3 text-sm text-gray-600">
                                            {alert.src_ip}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Top Attackers */}
                <div className="bg-white rounded-xl shadow-sm p-6">
                    <h2 className="text-xl font-semibold mb-4">Top Attackers</h2>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={Object.entries(stats?.top_attackers || {}).map(([ip, count]) => ({ ip, count }))}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="ip" />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="count" fill="#EF4444" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

const StatCard = ({ title, value, icon: Icon, color }) => {
    const colors = {
        blue: 'bg-blue-100 text-blue-600',
        red: 'bg-red-100 text-red-600',
        green: 'bg-green-100 text-green-600',
        purple: 'bg-purple-100 text-purple-600',
    };

    return (
        <div className="bg-white rounded-xl shadow-sm p-6 flex items-center">
            <div className={`p-3 rounded-lg ${colors[color]} mr-4`}>
                <Icon className="w-6 h-6" />
            </div>
            <div>
                <p className="text-sm text-gray-500 font-medium">{title}</p>
                <p className="text-2xl font-bold text-gray-900">{value}</p>
            </div>
        </div>
    );
};

const SeverityBadge = ({ level }) => {
    if (level === 1) return <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">High</span>;
    if (level === 2) return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">Medium</span>;
    return <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">Low</span>;
};

export default IDSDashboard;
