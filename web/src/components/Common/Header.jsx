import React from 'react'
import { Menu, Shield } from 'lucide-react'

export default function Header({ onMenuClick }) {
    return (
        <header className="bg-white shadow-sm z-10">
            <div className="flex items-center justify-between px-6 py-4">
                <div className="flex items-center space-x-4">
                    <button
                        onClick={onMenuClick}
                        className="text-gray-500 hover:text-gray-700 focus:outline-none"
                    >
                        <Menu className="h-6 w-6" />
                    </button>

                    <div className="flex items-center space-x-2">
                        <Shield className="h-8 w-8 text-primary-600" />
                        <h1 className="text-2xl font-bold text-gray-800">Srujan</h1>
                    </div>
                </div>

                <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                        <div className="h-2 w-2 bg-success-500 rounded-full animate-pulse"></div>
                        <span className="text-sm text-gray-600">Connected</span>
                    </div>
                </div>
            </div>
        </header>
    )
}
