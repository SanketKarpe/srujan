import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * PolicyBuilder Component
 * Visual interface for creating and editing network policies
 */
const PolicyBuilder = () => {
    const navigate = useNavigate();
    const [policy, setPolicy] = useState({
        name: '',
        description: '',
        source: 'any',
        destination: 'any',
        action: 'allow',
        priority: 50,
        enabled: true,
        conditions: []
    });

    const [newCondition, setNewCondition] = useState({
        type: 'trust_score',
        operator: '>=',
        value: ''
    });

    const [conflicts, setConflicts] = useState([]);

    const conditionTypes = [
        { value: 'trust_score', label: 'Trust Score', operators: ['>=', '<=', '=='] },
        { value: 'time_range', label: 'Time Range', operators: ['in'] },
        { value: 'day_of_week', label: 'Day of Week', operators: ['in'] },
        { value: 'ml_risk_level', label: 'ML Risk Level', operators: ['=='] },
        { value: 'device_category', label: 'Device Category', operators: ['=='] }
    ];

    const actions = [
        { value: 'allow', label: 'Allow', color: 'green' },
        { value: 'block', label: 'Block', color: 'red' },
        { value: 'quarantine', label: 'Quarantine', color: 'orange' },
        { value: 'rate_limit', label: 'Rate Limit', color: 'blue' },
        { value: 'log_only', label: 'Log Only', color: 'gray' }
    ];

    const addCondition = () => {
        if (!newCondition.value) {
            alert('Please enter a value for the condition');
            return;
        }

        const condition = { ...newCondition };

        // Parse value based on type
        if (newCondition.type === 'trust_score') {
            condition.value = parseInt(newCondition.value);
        } else if (newCondition.type === 'time_range' || newCondition.type === 'day_of_week') {
            condition.value = newCondition.value.split(',').map(v => v.trim());
        }

        setPolicy({
            ...policy,
            conditions: [...policy.conditions, condition]
        });

        setNewCondition({ type: 'trust_score', operator: '>=', value: '' });
    };

    const removeCondition = (index) => {
        setPolicy({
            ...policy,
            conditions: policy.conditions.filter((_, i) => i !== index)
        });
    };

    const savePolicy = async () => {
        if (!policy.name) {
            alert('Please enter a policy name');
            return;
        }

        try {
            const response = await fetch('http://localhost:8000/api/v1/policies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(policy)
            });

            const data = await response.json();

            if (data.conflicts && data.conflicts.length > 0) {
                setConflicts(data.conflicts);
                if (!confirm(`This policy has ${data.conflicts.length} conflicts. Create anyway?`)) {
                    return;
                }
            }

            alert('Policy created successfully!');
            navigate('/policies');
        } catch (error) {
            console.error('Error creating policy:', error);
            alert('Failed to create policy');
        }
    };

    return (
        <div className="p-6 max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-900">Create Network Policy</h1>
                <p className="text-gray-600 mt-1">Define context-aware access rules</p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
                {/* Basic Info */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Policy Name *
                    </label>
                    <input
                        type="text"
                        value={policy.name}
                        onChange={(e) => setPolicy({ ...policy, name: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="e.g., Block IoT at Night"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Description
                    </label>
                    <textarea
                        value={policy.description}
                        onChange={(e) => setPolicy({ ...policy, description: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        rows="3"
                        placeholder="What does this policy do?"
                    />
                </div>

                {/* Source & Destination */}
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Source
                        </label>
                        <input
                            type="text"
                            value={policy.source}
                            onChange={(e) => setPolicy({ ...policy, source: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                            placeholder="any, MAC, category:iot"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                            MAC address, category:iot, zone:guest, or "any"
                        </p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Destination
                        </label>
                        <input
                            type="text"
                            value={policy.destination}
                            onChange={(e) => setPolicy({ ...policy, destination: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                            placeholder="any, IP, CIDR"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                            IP address, CIDR (192.168.0.0/16), or "any"
                        </p>
                    </div>
                </div>

                {/* Action & Priority */}
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Action *
                        </label>
                        <select
                            value={policy.action}
                            onChange={(e) => setPolicy({ ...policy, action: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                            {actions.map(action => (
                                <option key={action.value} value={action.value}>
                                    {action.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Priority (0-100)
                        </label>
                        <input
                            type="number"
                            min="0"
                            max="100"
                            value={policy.priority}
                            onChange={(e) => setPolicy({ ...policy, priority: parseInt(e.target.value) })}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                            Higher = evaluated first (90+ recommended for security)
                        </p>
                    </div>
                </div>

                {/* Conditions */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                        Conditions
                    </label>

                    {/* Existing Conditions */}
                    <div className="space-y-2 mb-4">
                        {policy.conditions.map((cond, idx) => (
                            <div
                                key={idx}
                                className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200"
                            >
                                <div className="flex-1 font-mono text-sm">
                                    <span className="font-semibold text-blue-900">{cond.type}</span>
                                    <span className="text-blue-700 mx-2">{cond.operator}</span>
                                    <span className="text-blue-900">
                                        {Array.isArray(cond.value) ? cond.value.join(', ') : cond.value}
                                    </span>
                                </div>
                                <button
                                    onClick={() => removeCondition(idx)}
                                    className="text-red-600 hover:text-red-800"
                                >
                                    ✕
                                </button>
                            </div>
                        ))}

                        {policy.conditions.length === 0 && (
                            <div className="text-gray-400 text-sm text-center py-4 border-2 border-dashed border-gray-300 rounded-lg">
                                No conditions added. Policy will always apply.
                            </div>
                        )}
                    </div>

                    {/* Add New Condition */}
                    <div className="flex gap-2">
                        <select
                            value={newCondition.type}
                            onChange={(e) => setNewCondition({ ...newCondition, type: e.target.value })}
                            className="px-3 py-2 border border-gray-300 rounded-lg"
                        >
                            {conditionTypes.map(type => (
                                <option key={type.value} value={type.value}>
                                    {type.label}
                                </option>
                            ))}
                        </select>

                        <select
                            value={newCondition.operator}
                            onChange={(e) => setNewCondition({ ...newCondition, operator: e.target.value })}
                            className="px-3 py-2 border border-gray-300 rounded-lg"
                        >
                            {conditionTypes
                                .find(t => t.value === newCondition.type)
                                ?.operators.map(op => (
                                    <option key={op} value={op}>{op}</option>
                                ))}
                        </select>

                        <input
                            type="text"
                            value={newCondition.value}
                            onChange={(e) => setNewCondition({ ...newCondition, value: e.target.value })}
                            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                            placeholder={
                                newCondition.type === 'trust_score' ? '0-100' :
                                    newCondition.type === 'time_range' ? '22:00, 06:00' :
                                        newCondition.type === 'day_of_week' ? 'Monday, Tuesday' :
                                            'Enter value'
                            }
                        />

                        <button
                            onClick={addCondition}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                        >
                            + Add
                        </button>
                    </div>
                </div>

                {/* Conflicts Warning */}
                {conflicts.length > 0 && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <div className="font-semibold text-yellow-800 mb-2">
                            ⚠️ Policy Conflicts Detected
                        </div>
                        <div className="space-y-1">
                            {conflicts.map((conflict, idx) => (
                                <div key={idx} className="text-sm text-yellow-700">
                                    • Conflicts with "{conflict.policy_name}": {conflict.reason}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Actions */}
                <div className="flex justify-end gap-3 pt-4 border-t">
                    <button
                        onClick={() => navigate('/policies')}
                        className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={savePolicy}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                    >
                        Create Policy
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PolicyBuilder;
