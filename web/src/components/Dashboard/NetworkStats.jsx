import React from 'react'
import { Monitor, Activity, ShieldAlert, ShieldCheck } from 'lucide-react'

export default function NetworkStats({ stats }) {
    if (!stats) return null

    const cards = [
        {
            title: 'Total Devices',
            value: stats.devices.total,
            icon: Monitor,
            color: 'bg-primary-500',
            change: stats.devices.new_today > 0 ? `+${stats.devices.new_today} today` : null
        },
        {
            title: 'Active Devices',
            value: stats.devices.active,
            icon: Activity,
            color: 'bg-success-500',
            change: null
        },
        {
            title: 'Blocked Devices',
            value: stats.devices.blocked,
            icon: ShieldAlert,
            color: 'bg-danger-500',
            change: null
        },
        {
            title: 'Threats Today',
            value: stats.security.threats_today,
            icon: ShieldCheck,
            color: 'bg-primary-500',
            change: stats.security.gsb_enabled ? 'GSB Active' : 'GSB Inactive'
        }
    ]

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {cards.map((card) => {
                const Icon = card.icon
                return (
                    <div key={card.title} className="bg-white rounded-lg shadow p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 mb-1">{card.title}</p>
                                <p className="text-3xl font-bold text-gray-800">{card.value}</p>
                                {card.change && (
                                    <p className="text-sm text-gray-500 mt-1">{card.change}</p>
                                )}
                            </div>
                            <div className={`${card.color} p-3 rounded-lg`}>
                                <Icon className="h-6 w-6 text-white" />
                            </div>
                        </div>
                    </div>
                )
            })}
        </div>
    )
}
