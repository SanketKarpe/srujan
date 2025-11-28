import React, { useState, useEffect } from 'react'
import { networkAPI, createWebSocket } from '../../services/api'
import NetworkStats from './NetworkStats'
import DeviceOverview from './DeviceOverview'
import ThreatFeed from './ThreatFeed'

export default function Dashboard() {
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        // Fetch initial stats
        fetchStats()

        // Connect to WebSocket for real-time updates
        const ws = createWebSocket((message) => {
            if (message.type === 'stats_update') {
                setStats(message.data)
            }
        })

        return () => {
            ws.close()
        }
    }, [])

    const fetchStats = async () => {
        try {
            setLoading(true)
            const response = await networkAPI.getStats()
            setStats(response.data)
            setError(null)
        } catch (err) {
            setError('Failed to load network statistics')
            console.error('Error fetching stats:', err)
        } finally {
            setLoading(false)
        }
    }

    if (loading && !stats) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        )
    }

    if (error && !stats) {
        return (
            <div className="bg-danger-50 border border-danger-200 text-danger-700 px-4 py-3 rounded">
                {error}
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold text-gray-800">Dashboard</h2>
                <p className="text-gray-600 mt-1">Network overview and security status</p>
            </div>

            <NetworkStats stats={stats} />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <DeviceOverview />
                <ThreatFeed />
            </div>
        </div>
    )
}
