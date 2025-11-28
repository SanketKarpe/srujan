import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { Brain, AlertTriangle, TrendingUp, Filter, RefreshCw } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function MLDashboard() {
    const [alerts, setAlerts] = useState([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('all') // all, critical, high, medium, low
    const [stats, setStats] = useState(null)

    useEffect(() => {
        fetchAlerts()
    }, [])

    const fetchAlerts = async () => {
        try {
            setLoading(true)
            const response = await axios.get('/api/v1/ml/alerts?hours=168&limit=100')
            setAlerts(response.data.alerts)
            setStats(response.data.by_risk_level)
        } catch (error) {
            console.error('Error fetching ML alerts:', error)
        } finally {
            setLoading(false)
        }
    }

    const filteredAlerts = alerts.filter(alert => {
        if (filter === 'all') return true
        return alert.risk_level === filter
    })

    const getRiskColor = (risk) => {
        switch (risk) {
            case 'critical': return 'bg-danger-100 text-danger-800 border-danger-200'
            case 'high': return 'bg-danger-50 text-danger-700 border-danger-100'
            case 'medium': return 'bg-yellow-50 text-yellow-700 border-yellow-100'
            case 'low': return 'bg-blue-50 text-blue-700 border-blue-100'
            default: return 'bg-gray-50 text-gray-700 border-gray-100'
        }
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold text-gray-800">ML Threat Detection</h2>
                    <p className="text-gray-600 mt-1">Behavioral analysis and anomaly detection</p>
                </div>
                <button
                    onClick={fetchAlerts}
                    disabled={loading}
                    className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                    <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                    <span>Refresh</span>
                </button>
            </div>

            {/* Stats Cards */}
            {stats && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <StatCard
                        label="Critical"
                        value={stats.critical}
                        color="danger"
                        icon={<AlertTriangle className="h-5 w-5" />}
                    />
                    <StatCard
                        label="High Risk"
                        value={stats.high}
                        color="warning"
                        icon={<TrendingUp className="h-5 w-5" />}
                    />
                    <StatCard
                        label="Medium Risk"
                        value={stats.medium}
                        color="yellow"
                        icon={<Brain className="h-5 w-5" />}
                    />
                    <StatCard
                        label="Low Risk"
                        value={stats.low}
                        color="blue"
                        icon={<Brain className="h-5 w-5" />}
                    />
                </div>
            )}

            {/* Filters */}
            <div className="bg-white rounded-lg shadow p-4">
                <div className="flex items-center space-x-4">
                    <Filter className="h-5 w-5 text-gray-600" />
                    <div className="flex space-x-2">
                        {['all', 'critical', 'high', 'medium', 'low'].map(level => (
                            <button
                                key={level}
                                onClick={() => setFilter(level)}
                                className={`px-4 py-2 rounded-lg transition-colors ${filter === level
                                        ? 'bg-primary-600 text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                {level.charAt(0).toUpperCase() + level.slice(1)}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Alert List */}
            <div className="bg-white rounded-lg shadow">
                {loading ? (
                    <div className="flex justify-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                    </div>
                ) : filteredAlerts.length === 0 ? (
                    <div className="text-center py-12">
                        <Brain className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-500">No anomalies detected</p>
                        <p className="text-sm text-gray-400 mt-2">All devices operating normally</p>
                    </div>
                ) : (
                    <div className="divide-y divide-gray-200">
                        {filteredAlerts.map((alert, index) => (
                            <AlertCard key={index} alert={alert} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}

function StatCard({ label, value, color, icon }) {
    const colorClasses = {
        danger: 'bg-danger-50 text-danger-700',
        warning: 'bg-danger-50 text-danger-600',
        yellow: 'bg-yellow-50 text-yellow-700',
        blue: 'bg-blue-50 text-blue-700'
    }

    return (
        <div className={`rounded-lg shadow p-4 ${colorClasses[color] || 'bg-gray-50'}`}>
            <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">{label}</span>
                {icon}
            </div>
            <p className="text-3xl font-bold">{value}</p>
        </div>
    )
}

function AlertCard({ alert }) {
    const getRiskColor = (risk) => {
        switch (risk) {
            case 'critical': return 'border-l-danger-600 bg-danger-50'
            case 'high': return 'border-l-danger-500 bg-danger-50'
            case 'medium': return 'border-l-yellow-500 bg-yellow-50'
            case 'low': return 'border-l-blue-500 bg-blue-50'
            default: return 'border-l-gray-500 bg-gray-50'
        }
    }

    return (
        <div className={`p-6 border-l-4 ${getRiskColor(alert.risk_level)} hover:bg-opacity-75 transition-colors`}>
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                        <AlertTriangle className={`h-5 w-5 ${alert.risk_level === 'critical' || alert.risk_level === 'high'
                                ? 'text-danger-600'
                                : alert.risk_level === 'medium'
                                    ? 'text-yellow-600'
                                    : 'text-blue-600'
                            }`} />
                        <h3 className="font-semibold text-gray-800">
                            Anomaly Detected - {alert.risk_level.toUpperCase()}
                        </h3>
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-white">
                            {alert.confidence}% confidence
                        </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                        <div>
                            <p className="text-sm text-gray-600">Device MAC</p>
                            <Link
                                to={`/ml/insights/${alert.mac}`}
                                className="font-medium text-primary-600 hover:text-primary-700"
                            >
                                {alert.mac}
                            </Link>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Anomaly Score</p>
                            <p className="font-medium text-gray-800">{alert.anomaly_score.toFixed(4)}</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Detected</p>
                            <p className="font-medium text-gray-800">
                                {formatDistanceToNow(new Date(alert.detected_at), { addSuffix: true })}
                            </p>
                        </div>
                    </div>

                    {alert.false_positive && (
                        <div className="mt-3 px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded inline-block">
                            Marked as False Positive
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
