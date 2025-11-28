import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './components/Dashboard/Dashboard'
import DeviceList from './components/Devices/DeviceList'
import ThreatsPage from './components/Threats/ThreatsPage'
import SettingsPage from './components/Settings/SettingsPage'
import SetupWizard from './components/Setup/SetupWizard'
import MLDashboard from './components/ML/MLDashboard'
import MLInsights from './components/ML/MLInsights'
import PolicyList from './components/Policy/PolicyList'
import PolicyBuilder from './components/Policy/PolicyBuilder'
import TrustDashboard from './components/Policy/TrustDashboard'
import PolicyTester from './components/Policy/PolicyTester'
import IDSDashboard from './components/IDS/IDSDashboard'
import RuleManager from './components/IDS/RuleManager'
import Header from './components/Common/Header'
import Sidebar from './components/Common/Sidebar'

function App() {
    const [sidebarOpen, setSidebarOpen] = useState(true)
    const [setupComplete, setSetupComplete] = useState(false)

    useEffect(() => {
        // Check if setup is complete
        const isSetupComplete = localStorage.getItem('srujan_setup_complete')
        const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true'

        if (isDemoMode) {
            console.log('Demo Mode active: Bypassing setup wizard')
            setSetupComplete(true)
        } else {
            setSetupComplete(isSetupComplete === 'true')
        }

        // Register service worker for PWA
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/service-worker.js')
                    .then(registration => {
                        console.log('SW registered:', registration)
                    })
                    .catch(error => {
                        console.log('SW registration failed:', error)
                    })
            })
        }
    }, [])

    // Show setup wizard if not completed
    if (!setupComplete) {
        return (
            <Router>
                <Routes>
                    <Route path="/setup" element={<SetupWizard />} />
                    <Route path="*" element={<Navigate to="/setup" replace />} />
                </Routes>
            </Router>
        )
    }

    return (
        <Router>
            <div className="flex h-screen bg-gray-100">
                <Sidebar isOpen={sidebarOpen} />

                <div className="flex-1 flex flex-col overflow-hidden">
                    <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

                    <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/devices" element={<DeviceList />} />
                            <Route path="/threats" element={<ThreatsPage />} />
                            <Route path="/ml" element={<MLDashboard />} />
                            <Route path="/ml/insights/:mac" element={<MLInsights />} />
                            <Route path="/policies" element={<PolicyList />} />
                            <Route path="/policies/new" element={<PolicyBuilder />} />
                            <Route path="/policies/:id/test" element={<PolicyTester />} />
                            <Route path="/trust" element={<TrustDashboard />} />
                            <Route path="/ids" element={<IDSDashboard />} />
                            <Route path="/ids/rules" element={<RuleManager />} />
                            <Route path="/settings" element={<SettingsPage />} />
                            <Route path="*" element={<Navigate to="/" replace />} />
                        </Routes>
                    </main>
                </div>
            </div>
        </Router>
    )
}

export default App
