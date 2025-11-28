import React, { useState, useEffect } from 'react'
import { deviceAPI, createWebSocket } from '../../services/api'
import { Monitor, ShieldOff, ShieldCheck, RefreshCw } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function DeviceList() {
    const [devices, setDevices] = useState([])
    const [loading, setLoading] = useState(true)
    const [actionLoading, setActionLoading] = useState(null)

    useEffect(() => {
        fetchDevices()

        // WebSocket for real-time updates
        const ws = createWebSocket((message) => {
            if (message.type === 'device_blocked' || message.type === 'device_allowed') {
                fetchDevices()
            }
        })

        return () => ws.close()
    }, [])

    const fetchDevices = async () => {
        try {
            setLoading(true)
            const response = await deviceAPI.getAll()
            setDevices(response.data.devices)
        } catch (error) {
            console.error('Error fetching devices:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleBlock = async (mac) => {
        try {
            setActionLoading(mac)
            await deviceAPI.block(mac)
            await fetchDevices()
        } catch (error) {
            console.error('Error blocking device:', error)
            alert('Failed to block device')
        } finally {
            setActionLoading(null)
        }
    }

    const handleAllow = async (mac) => {
        try {
            setActionLoading(mac)
            await deviceAPI.allow(mac)
            await fetchDevices()
        } catch (error) {
            console.error('Error allowing device:', error)
            alert('Failed to allow device')
        } finally {
            setActionLoading(null)
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold text-gray-800">Devices</h2>
                    <p className="text-gray-600 mt-1">Manage all connected devices</p>
                </div>
                <button
                    onClick={fetchDevices}
                    disabled={loading}
                    className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                    <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                    <span>Refresh</span>
                </button>
            </div>

            {loading && devices.length === 0 ? (
                <div className="flex justify-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                </div>
            ) : (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Device
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    IP Address
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Manufacturer
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Category
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Last Seen
                                </th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {devices.map((device) => (
                                <tr key={device.mac} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <Monitor className="h-5 w-5 text-gray-400 mr-3" />
                                            <div>
                                                <div className="text-sm font-medium text-gray-900">
                                                    {device.hostname || 'Unknown'}
                                                </div>
                                                <div className="text-sm text-gray-500">{device.mac}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        {device.ip || 'N/A'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {device.manufacturer || 'Unknown'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${device.category === 'iot'
                                                ? 'bg-primary-100 text-primary-800'
                                                : 'bg-gray-100 text-gray-800'
                                            }`}>
                                            {device.category === 'iot' ? 'IoT' : 'Non-IoT'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {device.last_seen
                                            ? formatDistanceToNow(new Date(device.last_seen), { addSuffix: true })
                                            : 'Never'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        {device.status === 'blocked' ? (
                                            <button
                                                onClick={() => handleAllow(device.mac)}
                                                disabled={actionLoading === device.mac}
                                                className="text-success-600 hover:text-success-900 disabled:opacity-50 inline-flex items-center"
                                            >
                                                <ShieldCheck className="h-4 w-4 mr-1" />
                                                Allow
                                            </button>
                                        ) : (
                                            <button
                                                onClick={() => handleBlock(device.mac)}
                                                disabled={actionLoading === device.mac}
                                                className="text-danger-600 hover:text-danger-900 disabled:opacity-50 inline-flex items-center"
                                            >
                                                <ShieldOff className="h-4 w-4 mr-1" />
                                                Block
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {devices.length === 0 && !loading && (
                        <div className="text-center py-12">
                            <Monitor className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-500">No devices found</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
