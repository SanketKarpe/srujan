import React, { useState, useEffect } from 'react'
import { threatsAPI } from '../../services/api'
import { AlertTriangle, Shield, Filter, Download } from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'

export default function ThreatsPage() {
    const [threats, setThreats] = useState([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('all') // all, high, medium, low

    useEffect(() => {
        fetchThreats()
    }, [])

    const fetchThreats = async () => {
        try {
            setLoading(true)
            const response = await threatsAPI.getRecent()
            setThreats(response.data.threats)
        } catch (error) {
            console.error('Error fetching threats:', error)
        } finally {
            setLoading(false)
        }
    }

    const filteredThreats = threats.filter(threat => {
        if (filter === 'all') return true
        return threat.severity === filter
    })

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'high':
                return 'bg-danger-100 text-danger-800 border-danger-200'
            case 'medium':
                return 'bg-yellow-100 text-yellow-800 border-yellow-200'
            case 'low':
                return 'bg-blue-100 text-blue-800 border-blue-200'
            default:
                return 'bg-gray-100 text-gray-800 border-gray-200'
        }
    }

    const exportThreats = () => {
        const csv = [
            ['Timestamp', 'Device IP', 'DNS Query', 'Tags', 'Severity'],
            ...filteredThreats.map(t => [
                t.timestamp,
                t.device_ip,
                t.dns_query,
                t.tags.join(';'),
                t.severity
            ])
        ].map(row => row.join(',')).join('\n')

        const blob = new Blob([csv], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `srujan-threats-${format(new Date(), 'yyyy-MM-dd')}.csv`
        a.click()
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold text-gray-800">Security Threats</h2>
                    <p className="text-gray-600 mt-1">Detected malicious activity and blocked threats</p>
                </div>
                <button
                    onClick={exportThreats}
                    className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                    <Download className="h-4 w-4" />
                    <span>Export CSV</span>
                </button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white rounded-lg shadow p-4">
                    <p className="text-sm text-gray-600">Total Threats</p>
                    <p className="text-2xl font-bold text-gray-800 mt-1">{threats.length}</p>
                </div>
                <div className="bg-danger-50 rounded-lg shadow p-4">
                    <p className="text-sm text-danger-600">High Severity</p>
                    <p className="text-2xl font-bold text-danger-800 mt-1">
                        {threats.filter(t => t.severity === 'high').length}
                    </p>
                </div>
                <div className="bg-yellow-50 rounded-lg shadow p-4">
                    <p className="text-sm text-yellow-600">Medium Severity</p>
                    <p className="text-2xl font-bold text-yellow-800 mt-1">
                        {threats.filter(t => t.severity === 'medium').length}
                    </p>
                </div>
                <div className="bg-success-50 rounded-lg shadow p-4">
                    <p className="text-sm text-success-600">All Blocked</p>
                    <p className="text-2xl font-bold text-success-800 mt-1">100%</p>
                </div>
            </div>

            {/* Filters */}
            <div className="bg-white rounded-lg shadow p-4">
                <div className="flex items-center space-x-4">
                    <Filter className="h-5 w-5 text-gray-600" />
                    <div className="flex space-x-2">
                        {['all', 'high', 'medium', 'low'].map(level => (
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

            {/* Threats List */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                {loading ? (
                    <div className="flex justify-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                    </div>
                ) : filteredThreats.length === 0 ? (
                    <div className="text-center py-12">
                        <Shield className="h-16 w-16 text-success-500 mx-auto mb-4" />
                        <p className="text-xl font-semibold text-gray-800">No Threats Detected</p>
                        <p className="text-gray-600 mt-2">Your network is secure</p>
                    </div>
                ) : (
                    <div className="divide-y divide-gray-200">
                        {filteredThreats.map((threat, index) => (
                            <div key={index} className="p-6 hover:bg-gray-50 transition-colors">
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-3 mb-2">
                                            <AlertTriangle className={`h-5 w-5 ${threat.severity === 'high' ? 'text-danger-600' : 'text-yellow-600'
                                                }`} />
                                            <h3 className="font-semibold text-gray-800 text-lg">
                                                {threat.dns_query}
                                            </h3>
                                            <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getSeverityColor(threat.severity)}`}>
                                                {threat.severity.toUpperCase()}
                                            </span>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                                            <div>
                                                <p className="text-sm text-gray-600">Device IP</p>
                                                <p className="font-medium text-gray-800">{threat.device_ip}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-600">Detection Source</p>
                                                <div className="flex flex-wrap gap-1 mt-1">
                                                    {threat.tags.map(tag => (
                                                        <span key={tag} className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded">
                                                            {tag}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                            <div>
                                                <p className="text-sm text-gray-600">Time</p>
                                                <p className="font-medium text-gray-800">
                                                    {threat.timestamp && formatDistanceToNow(new Date(threat.timestamp), { addSuffix: true })}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
