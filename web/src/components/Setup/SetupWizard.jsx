import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, Wifi, Lock, CheckCircle } from 'lucide-react'

export default function SetupWizard() {
    const [step, setStep] = useState(1)
    const [config, setConfig] = useState({
        networkName: '',
        adminPassword: '',
        gsbEnabled: true,
        iotNetwork: '192.168.2.0/24',
        mainNetwork: '192.168.1.0/24'
    })
    const navigate = useNavigate()

    const totalSteps = 4

    const nextStep = () => {
        if (step < totalSteps) {
            setStep(step + 1)
        } else {
            // Complete setup
            handleComplete()
        }
    }

    const prevStep = () => {
        if (step > 1) setStep(step - 1)
    }

    const handleComplete = () => {
        // TODO: Send configuration to API
        console.log('Setup complete:', config)
        localStorage.setItem('srujan_setup_complete', 'true')
        navigate('/')
    }

    const updateConfig = (key, value) => {
        setConfig({ ...config, [key]: value })
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
            <div className="max-w-2xl w-full bg-white rounded-2xl shadow-xl p-8">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="flex justify-center mb-4">
                        <Shield className="h-16 w-16 text-primary-600" />
                    </div>
                    <h1 className="text-3xl font-bold text-gray-800">Welcome to Srujan</h1>
                    <p className="text-gray-600 mt-2">Let's set up your smart home security gateway</p>
                </div>

                {/* Progress Bar */}
                <div className="mb-8">
                    <div className="flex justify-between mb-2">
                        <span className="text-sm text-gray600">Step {step} of {totalSteps}</span>
                        <span className="text-sm text-primary-600">{Math.round((step / totalSteps) * 100)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${(step / totalSteps) * 100}%` }}
                        />
                    </div>
                </div>

                {/* Step Content */}
                <div className="min-h-64">
                    {step === 1 && <WelcomeStep />}
                    {step === 2 && <NetworkStep config={config} updateConfig={updateConfig} />}
                    {step === 3 && <SecurityStep config={config} updateConfig={updateConfig} />}
                    {step === 4 && <ReviewStep config={config} />}
                </div>

                {/* Navigation */}
                <div className="flex justify-between mt-8 pt-6 border-t">
                    <button
                        onClick={prevStep}
                        disabled={step === 1}
                        className="px-6 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Back
                    </button>
                    <button
                        onClick={nextStep}
                        className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                    >
                        {step === totalSteps ? 'Complete Setup' : 'Continue'}
                    </button>
                </div>
            </div>
        </div>
    )
}

function WelcomeStep() {
    return (
        <div className="text-center py-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Smart Home Protection Made Easy</h2>
            <p className="text-gray-600 mb-6">
                Srujan automatically segregates your IoT devices from your personal devices,
                protecting your network from security threats.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                <div className="p-4">
                    <div className="bg-primary-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                        <Shield className="h-6 w-6 text-primary-600" />
                    </div>
                    <h3 className="font-semibold text-gray-800 mb-2">Auto Protection</h3>
                    <p className="text-sm text-gray-600">Devices are automatically categorized and isolated</p>
                </div>
                <div className="p-4">
                    <div className="bg-primary-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                        <Wifi className="h-6 w-6 text-primary-600" />
                    </div>
                    <h3 className="font-semibold text-gray-800 mb-2">Network Monitoring</h3>
                    <p className="text-sm text-gray-600">Real-time visibility into all network activity</p>
                </div>
                <div className="p-4">
                    <div className="bg-primary-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                        <Lock className="h-6 w-6 text-primary-600" />
                    </div>
                    <h3 className="font-semibold text-gray-800 mb-2">Threat Detection</h3>
                    <p className="text-sm text-gray-600">Google Safe Browsing integration blocks malicious sites</p>
                </div>
            </div>
        </div>
    )
}

function NetworkStep({ config, updateConfig }) {
    return (
        <div className="py-4">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Network Configuration</h2>
            <p className="text-gray-600 mb-6">Configure your network segmentation</p>

            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Main Network (Computers, Phones)
                    </label>
                    <input
                        type="text"
                        value={config.mainNetwork}
                        onChange={(e) => updateConfig('mainNetwork', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        placeholder="192.168.1.0/24"
                    />
                    <p className="text-sm text-gray-500 mt-1">Your trusted devices network</p>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        IoT Network (Smart Devices)
                    </label>
                    <input
                        type="text"
                        value={config.iotNetwork}
                        onChange={(e) => updateConfig('iotNetwork', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        placeholder="192.168.2.0/24"
                    />
                    <p className="text-sm text-gray-500 mt-1">Isolated network for IoT devices</p>
                </div>
            </div>
        </div>
    )
}

function SecurityStep({ config, updateConfig }) {
    return (
        <div className="py-4">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Security Settings</h2>
            <p className="text-gray-600 mb-6">Configure your security preferences</p>

            <div className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Admin Password
                    </label>
                    <input
                        type="password"
                        value={config.adminPassword}
                        onChange={(e) => updateConfig('adminPassword', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        placeholder="Enter a strong password"
                    />
                    <p className="text-sm text-gray-500 mt-1">Required for accessing the dashboard</p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-start">
                        <input
                            type="checkbox"
                            id="gsbEnabled"
                            checked={config.gsbEnabled}
                            onChange={(e) => updateConfig('gsbEnabled', e.target.checked)}
                            className="mt-1 h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                        />
                        <label htmlFor="gsbEnabled" className="ml-3">
                            <div className="font-medium text-gray-800">Enable Google Safe Browsing</div>
                            <p className="text-sm text-gray-600 mt-1">
                                Protect your network by checking URLs against Google's threat database.
                                Requires a (free) API key.
                            </p>
                        </label>
                    </div>
                </div>
            </div>
        </div>
    )
}

function ReviewStep({ config }) {
    return (
        <div className="py-4">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Review Configuration</h2>
            <p className="text-gray-600 mb-6">Please review your settings before completing setup</p>

            <div className="bg-gray-50 rounded-lg p-6 space-y-4">
                <div className="flex justify-between py-2 border-b border-gray-200">
                    <span className="text-gray-600">Main Network:</span>
                    <span className="font-medium text-gray-800">{config.mainNetwork}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-200">
                    <span className="text-gray-600">IoT Network:</span>
                    <span className="font-medium text-gray-800">{config.iotNetwork}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-200">
                    <span className="text-gray-600">Admin Password:</span>
                    <span className="font-medium text-gray-800">{'•'.repeat(config.adminPassword.length || 8)}</span>
                </div>
                <div className="flex justify-between py-2">
                    <span className="text-gray-600">Google Safe Browsing:</span>
                    <span className={`font-medium ${config.gsbEnabled ? 'text-success-600' : 'text-gray-400'}`}>
                        {config.gsbEnabled ? 'Enabled' : 'Disabled'}
                    </span>
                </div>
            </div>

            <div className="mt-6 bg-primary-50 border border-primary-200 rounded-lg p-4 flex items-start">
                <CheckCircle className="h-5 w-5 text-primary-600 mr-3 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-primary-800">
                    Once you complete setup, Srujan will start monitoring your network and protecting your devices automatically.
                </p>
            </div>
        </div>
    )
}
