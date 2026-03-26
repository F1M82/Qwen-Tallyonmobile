import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { connectorAPI } from '../lib/api'
import { Wifi, WifiOff, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ConnectorStatus() {
  const [companyId, setCompanyId] = useState<string | null>(null)

  const { data: status, isLoading, refetch } = useQuery({
    queryKey: ['connector-status', companyId],
    queryFn: () => companyId ? connectorAPI.status(companyId) : null,
    enabled: !!companyId,
    refetchInterval: 30000, // Check every 30 seconds
  })

  useEffect(() => {
    // Get current company from localStorage or context
    const storedCompany = localStorage.getItem('currentCompanyId')
    setCompanyId(storedCompany)
  }, [])

  const handleSync = async () => {
    if (!companyId) return
    
    try {
      await connectorAPI.sync(companyId)
      toast.success('Sync completed successfully')
      refetch()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Sync failed')
    }
  }

  if (!companyId || isLoading) {
    return (
      <div className="flex items-center space-x-2 text-sm text-gray-500">
        <RefreshCw className="h-4 w-4 animate-spin" />
        <span>Checking...</span>
      </div>
    )
  }

  const isConnected = status?.data?.connected

  return (
    <div className="mb-4 p-3 bg-gray-50 rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-gray-600">Tally Connection</span>
        {isConnected ? (
          <Wifi className="h-4 w-4 text-green-600" />
        ) : (
          <WifiOff className="h-4 w-4 text-red-600" />
        )}
      </div>
      
      <div className="flex items-center justify-between">
        <span className={`text-xs ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
        
        <button
          onClick={handleSync}
          disabled={!isConnected}
          className="text-xs text-blue-600 hover:text-blue-700 disabled:text-gray-400"
        >
          Sync Now
        </button>
      </div>
      
      {!isConnected && (
        <p className="mt-2 text-xs text-gray-500">
          Install TaxMind Connector on your PC to sync with Tally
        </p>
      )}
    </div>
  )
}
