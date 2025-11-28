import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, Monitor, AlertTriangle, Brain, Settings, Shield } from 'lucide-react'

export default function Sidebar({ isOpen }) {
    const location = useLocation()

    const menuItems = [
        { path: '/', icon: Home, label: 'Dashboard' },
        { path: '/devices', icon: Monitor, label: 'Devices' },
        { path: '/threats', icon: AlertTriangle, label: 'Threats' },
        { path: '/ml', icon: Brain, label: 'ML Detection' },
        { path: '/policies', icon: Shield, label: 'Policies' },
        { path: '/trust', icon: Brain, label: 'Trust Dashboard' },
        { path: '/ids', icon: AlertTriangle, label: 'IDS / IPS' },
        { path: '/settings', icon: Settings, label: 'Settings' },
    ]

    if (!isOpen) return null

    return (
        <aside className="w-64 bg-white shadow-md">
            <nav className="mt-6">
                {menuItems.map((item) => {
                    const Icon = item.icon
                    const isActive = location.pathname === item.path

                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`flex items-center px-6 py-3 text-gray-700 hover:bg-gray-100 transition-colors ${isActive ? 'bg-primary-50 text-primary-700 border-r-4 border-primary-600' : ''
                                }`}
                        >
                            <Icon className="h-5 w-5 mr-3" />
                            <span className="font-medium">{item.label}</span>
                        </Link>
                    )
                })}
            </nav>
        </aside>
    )
}
