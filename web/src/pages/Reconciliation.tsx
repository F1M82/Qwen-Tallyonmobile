import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { reconciliationAPI, partyAPI } from '../lib/api'
import { Upload, Download, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Reconciliation() {
  const [selectedParty, setSelectedParty] = useState<string>('')
  const [reconResult, setReconResult] = useState<any>(null)

  const { data: parties } = useQuery({
    queryKey: ['parties'],
    queryFn: () => partyAPI.list(),
  })

  const uploadMutation = useMutation({
    mutationFn: ({ partyId, file }: { partyId: string; file: File }) =>
      reconciliationAPI.upload(partyId, file),
    onSuccess: (data) => {
      setReconResult(data.data)
      toast.success('Reconciliation completed')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Upload failed')
    },
  })

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !selectedParty) {
      toast.error('Please select a party and file')
      return
    }

    uploadMutation.mutate({ partyId: selectedParty, file })
  }

  const handleConfirmMatches = async () => {
    if (!reconResult) return

    const matchIds = reconResult.results
      .filter((r: any) => r.auto_postable || r.status === 'exact')
      .map((r: any) => r.id)

    try {
      await reconciliationAPI.confirm(reconResult.recon_id, matchIds)
      toast.success(`${matchIds.length} matches posted to Tally`)
      setReconResult(null)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to confirm')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reconciliation</h1>
        <p className="text-gray-500 mt-1">Match your books with party statements</p>
      </div>

      {/* Party Selection */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Party
        </label>
        <select
          value={selectedParty}
          onChange={(e) => setSelectedParty(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Choose a party...</option>
          {parties?.data?.map((party: any) => (
            <option key={party.id} value={party.id}>
              {party.name}
            </option>
          ))}
        </select>
      </div>

      {/* Upload */}
      {selectedParty && !reconResult && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload Party Statement
          </label>
          <div className="mt-2 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg">
            <div className="space-y-1 text-center">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div className="flex text-sm text-gray-600">
                <label className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500">
                  <span>Upload a file</span>
                  <input
                    type="file"
                    className="sr-only"
                    accept=".pdf,.xlsx,.xls,.csv"
                    onChange={handleFileUpload}
                  />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-gray-500">PDF, Excel, CSV up to 10MB</p>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {reconResult && (
        <>
          {/* Summary */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-4">
            <div className="bg-green-50 rounded-xl p-6 border border-green-200">
              <div className="flex items-center">
                <CheckCircle className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-green-800">Matched</p>
                  <p className="text-2xl font-bold text-green-900">
                    {reconResult.summary.matched_count}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-yellow-50 rounded-xl p-6 border border-yellow-200">
              <div className="flex items-center">
                <AlertCircle className="h-8 w-8 text-yellow-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-yellow-800">Fuzzy</p>
                  <p className="text-2xl font-bold text-yellow-900">
                    {reconResult.summary.fuzzy_count}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-red-50 rounded-xl p-6 border border-red-200">
              <div className="flex items-center">
                <XCircle className="h-8 w-8 text-red-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-red-800">Missing</p>
                  <p className="text-2xl font-bold text-red-900">
                    {reconResult.summary.missing_in_party_count}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-blue-50 rounded-xl p-6 border border-blue-200">
              <div className="flex items-center">
                <Download className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-blue-800">Difference</p>
                  <p className="text-2xl font-bold text-blue-900">
                    ₹{reconResult.summary.difference}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
            <div className="flex space-x-4">
              <button
                onClick={handleConfirmMatches}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Confirm Matches
              </button>
              <button
                onClick={() => setReconResult(null)}
                className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Start New
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
