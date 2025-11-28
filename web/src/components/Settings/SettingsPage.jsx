import React, { useState } from 'react'
import { Save, Shield, Wifi, Bell, Key } from 'lucide-react'

export default function SettingsPage() {
    const [settings, setSettings] = useState({
        // Network settings
        mainNetwork: '192.168.1.0/24',
        iotNetwork: '192.168.2.0/24',
        dnsServer1: '8.8.8.8',
        dnsServer2: '8.8.4.4',

        // Security settings
        gsbEnabled: true,
        autoBlockThreats: true,
        blockNewDevices: false,

        // Notification settings
        emailAlerts: false,
        alertEmail: '',
        threatNotifications: true,
        newDeviceNotifications: true,

        // Advanced
        logLevel: 'info',
        dataRetention: '30'
    })

    const [saved, setSaved] = useState(false)

    const handleChange = (key, value) => {
        setSettings({ ...settings, [key]: value })
        setSaved(false)
    }

    const handleSave = () => {
        // TODO: Call API to save settings
        console.log('Saving settings:', settings)
        setSaved(true)
        setTimeout(() => setSaved(false), 3000)
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold text-gray-800">Settings</h2>
                    <p className="text-gray-600 mt-1">Configure your Srujan security gateway</p>
                </div>
                <button
                    onClick={handleSave}
                    className="flex items-center space-x-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                    <Save className="h-4 w-4" />
                    <span>Save Changes</span>
                </button>
            </div>

            {saved && (
                <div className="bg-success-50 border border-success-200 text-success-800 px-4 py-3 rounded-lg">
                    Settings saved successfully!
                </div>
            )}

            {/* Network Settings */}
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center space-x-3 mb-6">
                    <Wifi className="h-6 w-6 text-primary-600" />
                    <h3 className="text-xl font-semibold text-gray-800">Network Configuration</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Main Network CIDR
                        </label>
                        <input
                            type="text"
                            value={settings.mainNetwork}
                            onChange={(e) => handleChange('mainNetwork', e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                        <p className="text-sm text-gray-500 mt-1">Network for trusted devices</p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            IoT Network CIDR
                        </label>
                        <input
                            type="text"
                            value={settings.iotNetwork}
                            onChange={(e) => handleChange('iotNetwork', e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                        <p className="text-sm text-gray-500 mt-1">Isolated network for IoT devices</p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Primary DNS Server
                        </label>
                        <input
                            type="text"
                            value={settings.dnsServer1}
                            onChange={(e) => handleChange('dnsServer1', e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Secondary DNS Server
                        </label>
                        <input
                            type="text"
                            value={settings.dnsServer2}
                            onChange={(e) => handleChange('dnsServer2', e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                    </div>
                </div>
            </div>

            {/* Security Settings */}
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center space-x-3 mb-6">
                    <Shield className="h-6 w-6 text-primary-600" />
                    <h3 className="text-xl font-semibold text-gray-800">Security Settings</h3>
                </div>

                <div className="space-y-4">
                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                        <div>
                            <p className="font-medium text-gray-800">Google Safe Browsing</p>
                            <p className="text-sm text-gray-600">Check URLs against Google's threat database</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.gsbEnabled}
                                onChange={(e) => handleChange('gsbEnabled', e.target.checked)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>

                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                        <div>
                            <p className="font-medium text-gray-800">Auto-block Threats</p>
                            <p className="text-sm text-gray-600">Automatically block detected malicious connections</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.autoBlockThreats}
                                onChange={(e) => handleChange('autoBlockThreats', e.target.checked)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>

                    <div className="flex items-center justify-between py-3">
                        <div>
                            <p className="font-medium text-gray-800">Block New Devices</p>
                            <p className="text-sm text-gray-600">Quarantine unknown devices until approved</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.blockNewDevices}
                                onChange={(e) => handleChange('blockNewDevices', e.target.checked)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>
                </div>
            </div>

            {/* Notification Settings */}
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center space-x-3 mb-6">
                    <Bell className="h-6 w-6 text-primary-600" />
                    <h3 className="text-xl font-semibold text-gray-800">Notifications</h3>
                </div>

                <div className="space-y-4">
                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                        <div>
                            <p className="font-medium text-gray-800">Email Alerts</p>
                            <p className="text-sm text-gray-600">Receive security alerts via email</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.emailAlerts}
                                onChange={(e) => handleChange('emailAlerts', e.target.checked)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>

                    {settings.emailAlerts && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Email Address
                            </label>
                            <input
                                type="email"
                                value={settings.alertEmail}
                                onChange={(e) => handleChange('alertEmail', e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                                placeholder="your@email.com"
                            />
                        </div>
                    )}

                    <div className="flex items-center justify-between py-3 border-b border-gray-200">
                        <div>
                            <p className="font-medium text-gray-800">Threat Notifications</p>
                            <p className="text-sm text-gray-600">Alert when threats are detected</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.threatNotifications}
                                onChange={(e) => handleChange('threatNotifications', e.target.checked)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>

                    <div className="flex items-center justify-between py-3">
                        <div>
                            <p className="font-medium text-gray-800">New Device Notifications</p>
                            <p className="text-sm text-gray-600">Alert when new devices connect</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={settings.newDeviceNotifications}
                                onChange={(e) => handleChange('newDeviceNotifications', e.target.checked)}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                        </label>
                    </div>
                </div>
            </div>

            {/* Advanced Settings */}
            <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center space-x-3 mb-6">
                    <Key className="h-6 w-6 text-primary-600" />
                    <h3 className="text-xl font-semibold text-gray-800">Advanced</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Log Level
                        </label>
                        <select
                            value={settings.logLevel}
                            onChange={(e) => handleChange('logLevel', e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        >
                            <option value="debug">Debug</option>
                            <option value="info">Info</option>
                            <option value="warning">Warning</option>
                            <option value="error">Error</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Data Retention (days)
                        </label>
                        <input
                            type="number"
                            value={settings.dataRetention}
                            onChange={(e) => handleChange('dataRetention', e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            min="7"
                            max="365"
                        />
                    </div>
                </div>
            </div>
        </div>
    )
}
