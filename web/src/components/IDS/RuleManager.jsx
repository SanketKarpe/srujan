import React, { useState, useEffect } from 'react';
import { Search, Filter, Shield, AlertTriangle } from 'lucide-react';

const RuleManager = () => {
    const [rules, setRules] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('all');

    useEffect(() => {
        fetchRules();
    }, []);

    const fetchRules = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/ids/rules');
            const data = await response.json();
            setRules(data.rules);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching rules:', error);
            setLoading(false);
        }
    };

    const toggleRule = async (sid, currentStatus) => {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/ids/rules/${sid}/toggle`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: !currentStatus })
            });

            if (response.ok) {
                setRules(rules.map(r =>
                    r.sid === sid ? { ...r, enabled: !currentStatus } : r
                ));
            }
        } catch (error) {
            console.error('Error toggling rule:', error);
        }
    };

    const filteredRules = rules.filter(rule => {
        const matchesSearch = rule.signature.toLowerCase().includes(filter.toLowerCase()) ||
            rule.sid.toString().includes(filter);
        const matchesCategory = categoryFilter === 'all' || rule.category === categoryFilter;
        return matchesSearch && matchesCategory;
    });

    const categories = ['all', ...new Set(rules.map(r => r.category))];

    if (loading) return <div className="p-6">Loading rules...</div>;

    return (
        <div className="p-6">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">IDS Rules Manager</h1>
                    <p className="text-gray-600 mt-1">Manage Suricata threat detection signatures</p>
                </div>
                <div className="text-sm text-gray-500">
                    {filteredRules.length} rules found
                </div>
            </div>

            {/* Filters */}
            <div className="bg-white p-4 rounded-xl shadow-sm mb-6 flex gap-4">
                <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="Search rules by name or SID..."
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                    />
                </div>
                <div className="w-64">
                    <select
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        value={categoryFilter}
                        onChange={(e) => setCategoryFilter(e.target.value)}
                    >
                        {categories.map(cat => (
                            <option key={cat} value={cat}>
                                {cat.charAt(0).toUpperCase() + cat.slice(1)}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Rules List */}
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">SID</th>
                            <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                            <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                            <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Signature</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {filteredRules.map((rule) => (
                            <tr key={rule.sid} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <button
                                        onClick={() => toggleRule(rule.sid, rule.enabled)}
                                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${rule.enabled ? 'bg-blue-600' : 'bg-gray-200'
                                            }`}
                                    >
                                        <span
                                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${rule.enabled ? 'translate-x-6' : 'translate-x-1'
                                                }`}
                                        />
                                    </button>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {rule.sid}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <SeverityBadge level={rule.severity} />
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {rule.category}
                                </td>
                                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                                    {rule.signature}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

const SeverityBadge = ({ level }) => {
    if (level === 1) return <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">High</span>;
    if (level === 2) return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">Medium</span>;
    return <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">Low</span>;
};

export default RuleManager;
