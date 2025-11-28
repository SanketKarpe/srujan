import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

/**
 * PolicyTester Component
 * Allows users to test policies against hypothetical scenarios
 */
const PolicyTester = () => {
    const { id } = useParams();
    const [policy, setPolicy] = useState(null);
    const [loading, setLoading] = useState(true);
    const [testResults, setTestResults] = useState(null);

    // Test scenario state
    const [scenario, setScenario] = useState({
        source_mac: '',
        destination_ip: '8.8.8.8',
        trust_score: 50,
        time: '12:00',
        day_of_week: 'Monday',
        device_category: 'iot',
        ml_risk_level: 'low',
        network_zone: 'default'
    });

    useEffect(() => {
        if (id) {
            fetchPolicy();
        }
    }, [id]);

    const fetchPolicy = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/policies/${id}`);
            if (response.ok) {
                const data = await response.json();
                setPolicy(data);
            }
        } catch (error) {
            console.error('Error fetching policy:', error);
        } finally {
            setLoading(false);
        }
    };

    const runTest = async () => {
        try {
            // Format scenario for API
            const testCase = {
                ...scenario,
                trust_score: parseInt(scenario.trust_score)
            };

            const response = await fetch(`http://localhost:8000/api/v1/policies/${id}/test`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify([testCase])
            });

            const data = await response.json();
            setTestResults(data.test_results[0]);
        } catch (error) {
            console.error('Error running test:', error);
            alert('Failed to run test');
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (!policy) {
        return (
            <div className="p-6 text-center">
                <h2 className="text-xl font-bold text-gray-700">Policy not found</h2>
                <Link to="/policies" className="text-blue-600 hover:underline mt-2 inline-block">
                    Return to Policy List
                </Link>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-6 flex justify-between items-start">
                <div>
                    <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                        <Link to="/policies" className="hover:text-gray-900">Policies</Link>
                        <span>/</span>
                        <span>Test Policy</span>
                    </div>
                    <h1 className="text-3xl font-bold text-gray-900">Test Policy: {policy.name}</h1>
                    <p className="text-gray-600 mt-1">{policy.description}</p>
                </div>
                <div className="flex gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800`}>
                        Action: {policy.action.toUpperCase()}
                    </span>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Test Scenario Input */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Test Scenario</h2>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Source MAC</label>
                            <input
                                type="text"
                                value={scenario.source_mac}
                                onChange={(e) => setScenario({ ...scenario, source_mac: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                placeholder="aa:bb:cc:dd:ee:ff"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Destination IP</label>
                            <input
                                type="text"
                                value={scenario.destination_ip}
                                onChange={(e) => setScenario({ ...scenario, destination_ip: e.target.value })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                placeholder="8.8.8.8"
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Trust Score</label>
                                <input
                                    type="number"
                                    min="0"
                                    max="100"
                                    value={scenario.trust_score}
                                    onChange={(e) => setScenario({ ...scenario, trust_score: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Device Category</label>
                                <select
                                    value={scenario.device_category}
                                    onChange={(e) => setScenario({ ...scenario, device_category: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                >
                                    <option value="iot">IoT</option>
                                    <option value="mobile">Mobile</option>
                                    <option value="laptop">Laptop</option>
                                    <option value="unknown">Unknown</option>
                                </select>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Time</label>
                                <input
                                    type="time"
                                    value={scenario.time}
                                    onChange={(e) => setScenario({ ...scenario, time: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Day of Week</label>
                                <select
                                    value={scenario.day_of_week}
                                    onChange={(e) => setScenario({ ...scenario, day_of_week: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                >
                                    {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map(day => (
                                        <option key={day} value={day}>{day}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <button
                            onClick={runTest}
                            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition font-medium"
                        >
                            Run Test Simulation
                        </button>
                    </div>
                </div>

                {/* Results Panel */}
                <div className="space-y-6">
                    {/* Policy Conditions */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-3">Policy Conditions</h3>
                        <div className="space-y-2">
                            {policy.conditions.length === 0 ? (
                                <p className="text-gray-500 italic">No specific conditions (Always matches)</p>
                            ) : (
                                policy.conditions.map((cond, idx) => (
                                    <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded border border-gray-200">
                                        <span className="font-mono text-sm text-blue-800">{cond.type}</span>
                                        <div className="flex items-center gap-2">
                                            <span className="text-gray-500 font-mono text-xs">{cond.operator}</span>
                                            <span className="font-medium text-gray-900">
                                                {Array.isArray(cond.value) ? cond.value.join(', ') : cond.value}
                                            </span>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Test Result */}
                    {testResults && (
                        <div className={`rounded-lg shadow p-6 border-l-4 ${testResults.would_apply ? 'bg-green-50 border-green-500' : 'bg-gray-50 border-gray-400'
                            }`}>
                            <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                                Result:
                                <span className={testResults.would_apply ? 'text-green-700' : 'text-gray-600'}>
                                    {testResults.would_apply ? 'MATCHED' : 'DID NOT MATCH'}
                                </span>
                            </h3>

                            <p className="text-gray-700 mb-4">
                                {testResults.would_apply
                                    ? `Policy would trigger action: ${testResults.action.toUpperCase()}`
                                    : "Policy conditions were not met. Default action (ALLOW) would apply."}
                            </p>

                            {testResults.would_apply && (
                                <div className="text-sm text-green-800 bg-green-100 p-3 rounded">
                                    ✅ All conditions satisfied by the test scenario.
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default PolicyTester;
