/**
 * Statistics Test Page
 * Demo page to test EntityStatistics and PhaseDistributionChart components
 */
import { useState } from 'react'
import EntityStatistics from '../components/hierarchy/EntityStatistics'
import PhaseDistributionChart from '../components/hierarchy/PhaseDistributionChart'

export default function StatisticsTestPage() {
  const [selectedPhase, setSelectedPhase] = useState<string | null>(null)

  // Sample phase distribution data
  const samplePhaseData = [
    { phase: 'Development', count: 8 },
    { phase: 'Testing', count: 6 },
    { phase: 'Design', count: 4 },
    { phase: 'Analysis', count: 2 }
  ]

  const handlePhaseClick = (phase: string) => {
    setSelectedPhase(phase)
    console.log('Phase clicked:', phase)
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Statistics Components Test</h1>
          <p className="text-gray-600 mt-2">
            Testing EntityStatistics and PhaseDistributionChart components
          </p>
        </div>

        {/* EntityStatistics Component */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Entity Statistics</h2>
          <EntityStatistics entityId="proj-1" entityType="project" />
        </div>

        {/* Standalone Phase Distribution Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Phase Distribution Chart (Standalone)
          </h2>
          {selectedPhase && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                Selected Phase: <span className="font-semibold">{selectedPhase}</span>
              </p>
            </div>
          )}
          <PhaseDistributionChart 
            data={samplePhaseData} 
            onPhaseClick={handlePhaseClick}
          />
        </div>

        {/* Component Features */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Features Implemented</h2>
          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-gray-900">EntityStatistics Component:</h3>
              <ul className="list-disc list-inside text-gray-600 mt-2 space-y-1">
                <li>Status distribution with color-coded badges</li>
                <li>Completion progress bar with percentage</li>
                <li>Phase distribution pie chart (for User Stories and above)</li>
                <li>Rollup counts table showing hierarchy summary</li>
                <li>Loading and error states</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">PhaseDistributionChart Component:</h3>
              <ul className="list-disc list-inside text-gray-600 mt-2 space-y-1">
                <li>Interactive pie chart using Recharts</li>
                <li>Color-coded by phase (Development, Analysis, Design, Testing)</li>
                <li>Click handler to filter by phase</li>
                <li>Custom tooltips with detailed information</li>
                <li>Summary cards showing count and percentage</li>
                <li>Active state highlighting on selection</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
