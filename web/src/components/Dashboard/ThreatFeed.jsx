import React, { useState, useEffect } from 'react'
import { threatsAPI } from '../../services/api'
import { AlertTriangle, Shield } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function ThreatFeed() {
    const [threats, setThreats] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchThreats()
    }, [])

    const fetchThreats = async () => {
        try {
            const response = await threatsAPI.getRecent()
            setThreats(response.data.threats.slice(0, 5)) // Show only top 5
            setLoading(false)
        } catch (error) {
            console.error('Error fetching threats:', error)
            setLoading(false)
        }
    }

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Recent Threats</h3>
                <Shield className="h-5 w-5 text-primary-600" />
            </div>

            {loading ? (
                <div className="flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                </div>
            ) : threats.length === 0 ? (
                <div className="text-center py-8">
                    <ShieldCheck className="h-12 w-12 text-success-500 mx-auto mb-2" />
                    <p className="text-gray-500">No threats detected</p>
                </div>
            ) : (
                <div className="space-y-3">
                    {threats.map((threat, index) => (
                        <div
                            key={index}
                            className={`p-3 rounded-lg border ${threat.severity === 'high'
                                    ? 'bg-danger-50 border-danger-200'
                                    : 'bg-yellow-50 border-yellow-200'
                                }`}
                        >
                            <div className="flex items-start space-x-3">
                                <AlertTriangle className={`h-5 w-5 mt-0.5 ${threat.severity === 'high' ? 'text-danger-600' : 'text-yellow-600'
                                    }`} />
                                <div className="flex-1">
                                    <p className="font-medium text-gray-800 text-sm">
                                        {threat.dns_query}
                                    </p>
                                    <p className="text-xs text-gray-600 mt-1">
                                        {threat.device_ip} • {threat.tags.join(', ')}
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">
                                        {threat.timestamp && formatDistanceToNow(new Date(threat.timestamp), { addSuffix: true })}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

// Add ShieldCheck icon if not imported
const ShieldCheck = ({ className }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="width" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
)
