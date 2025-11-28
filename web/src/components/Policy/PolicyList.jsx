import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

/**
 * PolicyList Component
 * Displays and manages all network policies
 */
const PolicyList = () => {
    const [policies, setPolicies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, enabled, disabled

    useEffect(() => {
        fetchPolicies();
    }, [filter]);

    const fetchPolicies = async () => {
        setLoading(true);
        try {
            const enabledOnly = filter === 'enabled';
            const response = await fetch(
                `http://localhost:8000/api/v1/policies?enabled_only=${enabledOnly}`
            );
            const data = await response.json();

            let filteredPolicies = data.policies;
            if (filter === 'disabled') {
                filteredPolicies = data.policies.filter(p => !p.enabled);
            }

            setPolicies(filteredPolicies);
        } catch (error) {
            console.error('Error fetching policies:', error);
        } finally {
            setLoading(false);
        }
    };

    const togglePolicy = async (policyId, currentStatus) => {
        try {
            await fetch(`http://localhost:8000/api/v1/policies/${policyId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: !currentStatus })
            });
            fetchPolicies();
        } catch (error) {
            console.error('Error toggling policy:', error);
        }
    };

    const deletePolicy = async (policyId) => {
        if (!confirm('Are you sure you want to delete this policy?')) return;

        try {
            await fetch(`http://localhost:8000/api/v1/policies/${policyId}`, {
                method: 'DELETE'
            });
            fetchPolicies();
        } catch (error) {
            console.error('Error deleting policy:', error);
        }
    };

    const applyAllPolicies = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/policies/apply', {
                method: 'POST'
            });
            const data = await response.json();
            alert(`Applied ${data.results.applied} policies successfully!`);
        } catch (error) {
            console.error('Error applying policies:', error);
            alert('Failed to apply policies');
        }
    };

    const getPriorityBadge = (priority) => {
        if (priority >= 90) return 'bg-red-500';
        if (priority >= 70) return 'bg-orange-500';
        if (priority >= 50) return 'bg-yellow-500';
        return 'bg-gray-500';
    };

    const getActionBadge = (action) => {
        const badges = {
            'block': 'bg-red-600 text-white',
            'allow': 'bg-green-600 text-white',
            'quarantine': 'bg-orange-600 text-white',
            'rate_limit': 'bg-blue-600 text-white',
            'log_only': 'bg-gray-600 text-white'
        };
        return badges[action] || 'bg-gray-600 text-white';
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="p-6">
            {/* Header */}
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Network Policies</h1>
                    <p className="text-gray-600 mt-1">
                        Manage context-aware network access rules
                    </p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={applyAllPolicies}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                    >
                        Apply All Policies
                    </button>
                    <Link
                        to="/policies/new"
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                    >
                        + Create Policy
                    </Link>
                </div>
            </div>

            {/* Filter Tabs */}
            <div className="flex gap-2 mb-6 border-b">
                {['all', 'enabled', 'disabled'].map(tab => (
                    <button
                        key={tab}
                        onClick={() => setFilter(tab)}
                        className={`px-4 py-2 font-medium transition ${filter === tab
                                ? 'text-blue-600 border-b-2 border-blue-600'
                                : 'text-gray-600 hover:text-gray-900'
                            }`}
                    >
                        {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                ))}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4 mb-6">
                <div className="bg-white p-4 rounded-lg shadow">
                    <div className="text-2xl font-bold text-gray-900">{policies.length}</div>
                    <div className="text-sm text-gray-600">Total Policies</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                    <div className="text-2xl font-bold text-green-600">
                        {policies.filter(p => p.enabled).length}
                    </div>
                    <div className="text-sm text-gray-600">Enabled</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                    <div className="text-2xl font-bold text-red-600">
                        {policies.filter(p => p.action === 'block').length}
                    </div>
                    <div className="text-sm text-gray-600">Block Rules</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow">
                    <div className="text-2xl font-bold text-orange-600">
                        {policies.filter(p => p.priority >= 90).length}
                    </div>
                    <div className="text-sm text-gray-600">High Priority</div>
                </div>
            </div>

            {/* Policy Table */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Policy Name
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Source → Destination
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Conditions
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Action
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Priority
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                Status
                            </th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                Actions
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {policies.length === 0 ? (
                            <tr>
                                <td colSpan="7" className="px-6 py-12 text-center text-gray-500">
                                    <div className="text-4xl mb-2">📋</div>
                                    <div>No policies found. Create your first policy!</div>
                                </td>
                            </tr>
                        ) : (
                            policies.map(policy => (
                                <tr key={policy.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4">
                                        <div className="text-sm font-medium text-gray-900">
                                            {policy.name}
                                        </div>
                                        <div className="text-sm text-gray-500">
                                            {policy.description}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-900">
                                        <span className="font-mono">{policy.source}</span>
                                        <span className="mx-2">→</span>
                                        <span className="font-mono">{policy.destination}</span>
                                    </td>
                                    <td className="px-6 py-4 text-sm">
                                        <div className="flex flex-wrap gap-1">
                                            {policy.conditions.map((cond, idx) => (
                                                <span
                                                    key={idx}
                                                    className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs"
                                                >
                                                    {cond.type}
                                                </span>
                                            ))}
                                            {policy.conditions.length === 0 && (
                                                <span className="text-gray-400">No conditions</span>
                                            )}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getActionBadge(policy.action)}`}>
                                            {policy.action}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-1 rounded text-xs text-white font-medium ${getPriorityBadge(policy.priority)}`}>
                                            {policy.priority}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <button
                                            onClick={() => togglePolicy(policy.id, policy.enabled)}
                                            className={`relative inline-flex h-6 w-11 items-center rounded-full transition ${policy.enabled ? 'bg-green-600' : 'bg-gray-300'
                                                }`}
                                        >
                                            <span
                                                className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${policy.enabled ? 'translate-x-6' : 'translate-x-1'
                                                    }`}
                                            />
                                        </button>
                                    </td>
                                    <td className="px-6 py-4 text-right text-sm font-medium">
                                        <div className="flex justify-end gap-2">
                                            <Link
                                                to={`/policies/${policy.id}/test`}
                                                className="text-blue-600 hover:text-blue-900"
                                            >
                                                Test
                                            </Link>
                                            <Link
                                                to={`/policies/${policy.id}/edit`}
                                                className="text-indigo-600 hover:text-indigo-900"
                                            >
                                                Edit
                                            </Link>
                                            <button
                                                onClick={() => deletePolicy(policy.id)}
                                                className="text-red-600 hover:text-red-900"
                                            >
                                                Delete
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default PolicyList;
