import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { deviceAPI } from '../../services/api'
import { Monitor, ArrowRight } from 'lucide-react'

export default function DeviceOverview() {
    const [devices, setDevices] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchDevices()
    }, [])

    const fetchDevices = async () => {
        try {
            const response = await deviceAPI.getAll()
            setDevices(response.data.devices.slice(0, 5)) // Show only top 5
            setLoading(false)
        } catch (error) {
            console.error('Error fetching devices:', error)
            setLoading(false)
        }
    }

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Recent Devices</h3>
                <Link
                    to="/devices"
                    className="text-primary-600 hover:text-primary-700 flex items-center text-sm"
                >
                    View all <ArrowRight className="h-4 w-4 ml-1" />
                </Link>
            </div>

            {loading ? (
                <div className="flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                </div>
            ) : devices.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No devices found</p>
            ) : (
                <div className="space-y-3">
                    {devices.map((device) => (
                        <div
                            key={device.mac}
                            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                            <div className="flex items-center space-x-3">
                                <Monitor className="h-5 w-5 text-gray-600" />
                                <div>
                                    <p className="font-medium text-gray-800">
                                        {device.hostname || device.mac}
                                    </p>
                                    <p className="text-sm text-gray-500">{device.ip}</p>
                                </div>
                            </div>
                            <span className={`px-2 py-1 rounded text-xs font-medium ${device.category === 'iot'
                                    ? 'bg-primary-100 text-primary-700'
                                    : 'bg-gray-200 text-gray-700'
                                }`}>
                                {device.category === 'iot' ? 'IoT' : 'Other'}
                            </span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
