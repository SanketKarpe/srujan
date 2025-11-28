import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

/**
 * TrustDashboard Component
 * Visualizes device trust scores and allows manual overrides
 */
const TrustDashboard = () => {
    const [trustScores, setTrustScores] = useState([]);
    const [statistics, setStatistics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        fetchTrustData();
    }, []);

    const fetchTrustData = async () => {
        setLoading(true);
        try {
            // Fetch all trust scores
            const scoresResponse = await fetch('http://localhost:8000/api/v1/trust');
            const scoresData = await scoresResponse.json();
            setTrustScores(scoresData.scores || []);

            // Fetch statistics
            const statsResponse = await fetch('http://localhost:8000/api/v1/trust/summary/statistics');
            const statsData = await statsResponse.json();
            setStatistics(statsData);
        } catch (error) {
            console.error('Error fetching trust data:', error);
        } finally {
            setLoading(false);
        }
    };

    const recalculateScores = async () => {
        try {
            await fetch('http://localhost:8000/api/v1/trust/recalculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(null)
            });
            fetchTrustData();
            alert('Trust scores recalculated successfully!');
        } catch (error) {
            console.error('Error recalculating scores:', error);
            alert('Failed to recalculate scores');
        }
    };

    const getTrustLevelColor = (level) => {
        const colors = {
            'highly_trusted': 'bg-green-100 text-green-800 border-green-300',
            'trusted': 'bg-blue-100 text-blue-800 border-blue-300',
            'neutral': 'bg-yellow-100 text-yellow-800 border-yellow-300',
            'low_trust': 'bg-orange-100 text-orange-800 border-orange-300',
            'untrusted': 'bg-red-100 text-red-800 border-red-300'
        };
        return colors[level] || colors.neutral;
    };

    const getTrustScoreBar = (score) => {
        let bgColor = 'bg-gray-400';
        if (score >= 90) bgColor = 'bg-green-500';
        else if (score >= 70) bgColor = 'bg-blue-500';
        else if (score >= 50) bgColor = 'bg-yellow-500';
        else if (score >= 30) bgColor = 'bg-orange-500';
        else bgColor = 'bg-red-500';

        return (
            <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                    className={`${bgColor} h-2.5 rounded-full transition-all duration-500`}
                    style={{ width: `${score}%` }}
                ></div>
            </div>
        );
    };

    const filteredScores = () => {
        if (filter === 'all') return trustScores;
        return trustScores.filter(s => s.level === filter);
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
                    <h1 className="text-3xl font-bold text-gray-900">Trust Dashboard</h1>
                    <p className="text-gray-600 mt-1">
                        Monitor device trust scores and security posture
                    </p>
                </div>
                <button
                    onClick={recalculateScores}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                    🔄 Recalculate All
                </button>
            </div>

            {/* Statistics Cards */}
            {statistics && (
                <div className="grid grid-cols-5 gap-4 mb-6">
                    <div className="bg-white p-4 rounded-lg shadow">
                        <div className="text-2xl font-bold text-gray-900">
                            {statistics.total_devices}
                        </div>
                        <div className="text-sm text-gray-600">Total Devices</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                        <div className="text-2xl font-bold text-blue-600">
                            {Math.round(statistics.average_score)}
                        </div>
                        <div className="text-sm text-gray-600">Avg Score</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                        <div className="text-2xl font-bold text-green-600">
                            {statistics.by_level?.highly_trusted || 0}
                        </div>
                        <div className="text-sm text-gray-600">High Trust</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                        <div className="text-2xl font-bold text-orange-600">
                            {statistics.by_level?.low_trust || 0}
                        </div>
                        <div className="text-sm text-gray-600">Low Trust</div>
                    </div>
                    <div className="bg-white p-4 rounded-lg shadow">
                        <div className="text-2xl font-bold text-red-600">
                            {statistics.by_level?.untrusted || 0}
                        </div>
                        <div className="text-sm text-gray-600">Untrusted</div>
                    </div>
                </div>
            )}

            {/* Trust Level Filter */}
            <div className="flex gap-2 mb-6 overflow-x-auto">
                {['all', 'highly_trusted', 'trusted', 'neutral', 'low_trust', 'untrusted'].map(level => (
                    <button
                        key={level}
                        onClick={() => setFilter(level)}
                        className={`px-4 py-2 rounded-lg whitespace-nowrap transition ${filter === level
                                ? 'bg-blue-600 text-white'
                                : 'bg-white text-gray-700 hover:bg-gray-100'
                            }`}
                    >
                        {level.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                    </button>
                ))}
            </div>

            {/* Trust Scores Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredScores().length === 0 ? (
                    <div className="col-span-full text-center py-12 text-gray-500">
                        <div className="text-4xl mb-2">🔒</div>
                        <div>No devices with this trust level</div>
                    </div>
                ) : (
                    filteredScores().map(scoreData => (
                        <div
                            key={scoreData.device_mac}
                            className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition"
                        >
                            {/* Device Header */}
                            <div className="flex justify-between items-start mb-3">
                                <div className="flex-1">
                                    <div className="font-mono text-sm text-gray-600">
                                        {scoreData.device_mac}
                                    </div>
                                    <span className={`inline-block mt-1 px-2 py-1 rounded-full text-xs font-medium border ${getTrustLevelColor(scoreData.level)}`}>
                                        {scoreData.level.split('_').join(' ').toUpperCase()}
                                    </span>
                                </div>
                                <div className="text-3xl font-bold text-gray-900">
                                    {scoreData.score}
                                </div>
                            </div>

                            {/* Trust Score Bar */}
                            <div className="mb-3">
                                {getTrustScoreBar(scoreData.score)}
                            </div>

                            {/* Factors Breakdown */}
                            <div className="space-y-1 text-xs">
                                <div className="font-semibold text-gray-700 mb-1">
                                    Trust Factors:
                                </div>
                                {Object.entries(scoreData.factors || {}).slice(0, 3).map(([key, value]) => (
                                    <div key={key} className="flex justify-between text-gray-600">
                                        <span className="truncate">{key.replace(/_/g, ' ')}</span>
                                        <span className={value.impact > 0 ? 'text-green-600' : 'text-red-600'}>
                                            {value.impact > 0 ? '+' : ''}{value.impact}
                                        </span>
                                    </div>
                                ))}
                                {Object.keys(scoreData.factors || {}).length > 3 && (
                                    <div className="text-gray-400 text-center pt-1">
                                        +{Object.keys(scoreData.factors).length - 3} more factors
                                    </div>
                                )}
                            </div>

                            {/* Actions */}
                            <div className="mt-4 flex gap-2">
                                <Link
                                    to={`/trust/${scoreData.device_mac}`}
                                    className="flex-1 text-center px-3 py-1.5 bg-blue-50 text-blue-600 rounded hover:bg-blue-100 transition text-sm"
                                >
                                    Details
                                </Link>
                                <Link
                                    to={`/policies/suggest/${scoreData.device_mac}`}
                                    className="flex-1 text-center px-3 py-1.5 bg-green-50 text-green-600 rounded hover:bg-green-100 transition text-sm"
                                >
                                    Suggest Policy
                                </Link>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Score Distribution Chart */}
            {statistics && statistics.score_distribution && (
                <div className="mt-8 bg-white rounded-lg shadow p-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">
                        Score Distribution
                    </h2>
                    <div className="space-y-3">
                        {Object.entries(statistics.score_distribution).map(([range, count]) => {
                            const total = statistics.total_devices;
                            const percentage = total > 0 ? (count / total) * 100 : 0;

                            return (
                                <div key={range}>
                                    <div className="flex justify-between mb-1">
                                        <span className="text-sm font-medium text-gray-700">{range}</span>
                                        <span className="text-sm text-gray-600">
                                            {count} devices ({percentage.toFixed(1)}%)
                                        </span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                        <div
                                            className="bg-blue-600 h-2 rounded-full transition-all"
                                            style={{ width: `${percentage}%` }}
                                        ></div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
};

export default TrustDashboard;
