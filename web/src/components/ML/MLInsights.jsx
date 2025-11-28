import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'
import { Brain, Activity, AlertTriangle, TrendingUp, Shield, CheckCircle } from 'lucide-react'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function MLInsights() {
    const { mac } = useParams()
    const [insights, setInsights] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (mac) {
            fetchInsights()
        }
    }, [mac])

    const fetchInsights = async () => {
        try {
            setLoading(true)
            const response = await axios.get(`/api/v1/ml/insights/${mac}`)
            setInsights(response.data)
        } catch (error) {
            console.error('Error fetching ML insights:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        )
    }

    if (!insights) {
        return (
            <div className="text-center py-12">
                <Brain className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No ML insights available</p>
            </div>
        )
    }

    const getRiskColor = (risk) => {
        switch (risk) {
            case 'critical': return 'text-danger-700 bg-danger-100'
            case 'high': return 'text-danger-600 bg-danger-50'
            case 'medium': return 'text-yellow-600 bg-yellow-50'
            case 'low': return 'text-success-600 bg-success-50'
            default: return 'text-gray-600 bg-gray-50'
        }
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">ML Insights</h2>
                    <p className="text-gray-600">{mac}</p>
                </div>
                <button
                    onClick={fetchInsights}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                    Refresh
                </button>
            </div>

            {/* Risk Score Card */}
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-sm text-gray-600 mb-1">Risk Score</p>
                        <p className="text-4xl font-bold text-gray-800">{insights.risk_score}/100</p>
                        <p className={`mt-2 px-3 py-1 rounded-full text-sm font-medium inline-block ${getRiskColor(insights.risk_level)}`}>
                            {insights.risk_level?.toUpperCase()}
                        </p>
                    </div>
                    <div className="text-right">
                        {insights.anomaly_detection?.is_anomaly ? (
                            <div className="text-danger-600">
                                <AlertTriangle className="h-16 w-16 mb-2" />
                                <p className="font-semibold">Anomaly Detected</p>
                            </div>
                        ) : (
                            <div className="text-success-600">
                                <CheckCircle className="h-16 w-16 mb-2" />
                                <p className="font-semibold">Normal Behavior</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Current Behavior */}
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                    <Activity className="h-5 w-5 mr-2" />
                    Current Behavior (Last Hour)
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <MetricCard
                        label="DNS Queries"
                        value={insights.current_behavior.dns_query_count}
                        icon={<TrendingUp className="h-4 w-4" />}
                    />
                    <MetricCard
                        label="Unique Domains"
                        value={insights.current_behavior.unique_domains}
                        icon={<Activity className="h-4 w-4" />}
                    />
                    <MetricCard
                        label="Connections"
                        value={insights.current_behavior.connection_count}
                        icon={<Shield className="h-4 w-4" />}
                    />
                    <MetricCard
                        label="Threat Count"
                        value={insights.current_behavior.threat_count}
                        alert={insights.current_behavior.threat_count > 0}
                    />
                </div>
            </div>

            {/* Recommendations */}
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Recommendations</h3>
                <div className="space-y-3">
                    {insights.recommendations?.map((rec, index) => (
                        <RecommendationCard key={index} recommendation={rec} />
                    ))}
                </div>
            </div>

            {/* Anomaly History */}
            {insights.recent_anomalies_count > 0 && (
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">Recent Anomalies</h3>
                    <p className="text-sm text-gray-600 mb-4">
                        {insights.recent_anomalies_count} anomalies detected in the past week
                    </p>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-danger-500"
                            style={{ width: `${Math.min((insights.recent_anomalies_count / 10) * 100, 100)}%` }}
                        />
                    </div>
                </div>
            )}
        </div>
    )
}

function MetricCard({ label, value, icon, alert }) {
    return (
        <div className={`p-4 rounded-lg ${alert ? 'bg-danger-50 border border-danger-200' : 'bg-gray-50'}`}>
            <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">{label}</span>
                {icon && <span className="text-gray-400">{icon}</span>}
            </div>
            <p className={`text-2xl font-bold ${alert ? 'text-danger-700' : 'text-gray-800'}`}>
                {value}
            </p>
        </div>
    )
}

function RecommendationCard({ recommendation }) {
    const getColor = (severity) => {
        switch (severity) {
            case 'critical': return 'border-danger-500 bg-danger-50'
            case 'high': return 'border-danger-400 bg-danger-50'
            case 'medium': return 'border-yellow-400 bg-yellow-50'
            case 'low': return 'border-blue-400 bg-blue-50'
            default: return 'border-gray-400 bg-gray-50'
        }
    }

    const getIcon = (severity) => {
        switch (severity) {
            case 'critical':
            case 'high':
                return <AlertTriangle className="h-5 w-5 text-danger-600" />
            case 'medium':
                return <AlertTriangle className="h-5 w-5 text-yellow-600" />
            default:
                return <Shield className="h-5 w-5 text-blue-600" />
        }
    }

    return (
        <div className={`border-l-4 p-4 rounded ${getColor(recommendation.severity)}`}>
            <div className="flex items-start">
                <div className="mr-3 mt-0.5">{getIcon(recommendation.severity)}</div>
                <div className="flex-1">
                    <h4 className="font-semibold text-gray-800 mb-1">{recommendation.title}</h4>
                    <p className="text-sm text-gray-700 mb-2">{recommendation.description}</p>
                    {recommendation.action && (
                        <p className="text-sm font-medium text-gray-900">
                            → {recommendation.action}
                        </p>
                    )}
                </div>
            </div>
        </div>
    )
}
