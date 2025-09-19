import React, { useState, useEffect } from 'react'
import { ReactFlow, Background, Controls, MiniMap } from 'reactflow'
import 'reactflow/dist/style.css'
import QueryForm from './components/QueryForm'
import TelemetryPanel from './components/TelemetryPanel'
import OptimizationsPanel from './components/OptimizationsPanel'
import ResponseDisplay from './components/ResponseDisplay'
import AgentOutputsPanel from './components/AgentOutputsPanel'
import { apiService } from './services/api'
import './App.css'

function App() {
  const [nodes, setNodes] = useState([])
  const [edges, setEdges] = useState([])
  const [optimizations, setOptimizations] = useState([])
  const [telemetry, setTelemetry] = useState(null)
  const [response, setResponse] = useState('')
  const [agentOutputs, setAgentOutputs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedRunId, setSelectedRunId] = useState(null)

  const handleQuerySubmit = async (query, simulate, systemPrompt) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await apiService.runSimulation(query, simulate, systemPrompt)
      
      // Update React Flow data
      setNodes(response.react_flow.nodes || [])
      setEdges(response.react_flow.edges || [])
      
      // Update other data
      setOptimizations(response.optimizations || [])
      setTelemetry(response.telemetry)
      setResponse(response.response || '')
      setAgentOutputs(response.agent_outputs || [])
      setSelectedRunId(response.run_id)
      
    } catch (err) {
      setError(err.message)
      console.error('Error running simulation:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleRunSelect = async (runId) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await apiService.getTelemetry(runId)
      setTelemetry(response)
      setSelectedRunId(runId)
      
      // Try to get diagram data if available
      try {
        const runResponse = await apiService.runSimulation("", true, null, runId)
        setNodes(runResponse.react_flow.nodes || [])
        setEdges(runResponse.react_flow.edges || [])
        setOptimizations(runResponse.optimizations || [])
      } catch (diagramErr) {
        console.warn('Could not load diagram data:', diagramErr)
      }
      
    } catch (err) {
      setError(err.message)
      console.error('Error loading run data:', err)
    } finally {
      setLoading(false)
    }
  }

  const nodeTypes = {
    agent: ({ data }) => (
      <div className="react-flow__node-agent">
        <div className="node-title">{data.label}</div>
        <div className="node-subtitle">{data.event_count} events</div>
        {data.events && data.events.length > 0 && (
          <div className="node-details">
            <div className="event-list">
              {data.events.slice(0, 3).map((event, idx) => (
                <div key={idx} className="event-item">
                  <span className="event-type">{event.type}</span>
                  <span className="event-step">{event.step}</span>
                  {event.duration_ms && (
                    <span className="event-duration">{Math.round(event.duration_ms)}ms</span>
                  )}
                </div>
              ))}
              {data.events.length > 3 && (
                <div className="event-more">+{data.events.length - 3} more</div>
              )}
            </div>
          </div>
        )}
      </div>
    ),
    tool: ({ data }) => (
      <div className="react-flow__node-tool">
        <div className="node-title">{data.label}</div>
        <div className="node-subtitle">{data.call_count} calls</div>
        {data.calls && data.calls.length > 0 && (
          <div className="node-details">
            <div className="call-list">
              {data.calls.slice(0, 3).map((call, idx) => (
                <div key={idx} className="call-item">
                  <span className="call-agent">{call.agent}</span>
                  <span className="call-duration">{Math.round(call.duration_ms)}ms</span>
                  <span className={`call-status ${call.success ? 'success' : 'error'}`}>
                    {call.success ? '✓' : '✗'}
                  </span>
                </div>
              ))}
              {data.calls.length > 3 && (
                <div className="call-more">+{data.calls.length - 3} more</div>
              )}
            </div>
          </div>
        )}
      </div>
    ),
    event: ({ data }) => (
      <div className="react-flow__node-event">
        <div className="node-title">{data.label}</div>
        <div className="node-subtitle">{data.step_name}</div>
        <div className="node-details">
          <div className="event-info">
            <div className="event-time">
              {new Date(data.timestamp).toLocaleTimeString()}
            </div>
            {data.duration_ms && (
              <div className="event-duration">
                {Math.round(data.duration_ms)}ms
              </div>
            )}
            {data.tool_name && (
              <div className="event-tool">Tool: {data.tool_name}</div>
            )}
            {data.model && (
              <div className="event-model">Model: {data.model}</div>
            )}
            {data.error_message && (
              <div className="event-error">Error: {data.error_message}</div>
            )}
            {data.from_agent && data.to_agent && (
              <div className="event-delegation">
                {data.from_agent} → {data.to_agent}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Multi-Agent Telemetry Visualizer</h1>
        <div className="header-controls">
          <QueryForm onSubmit={handleQuerySubmit} loading={loading} />
        </div>
      </header>

      <div className="app-content">
        <div className="main-panel">
          <div className="flow-container">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              nodeTypes={nodeTypes}
              fitView
              attributionPosition="bottom-left"
            >
              <Background />
              <Controls />
              <MiniMap />
            </ReactFlow>
          </div>
        </div>

        <div className="sidebar">
          <div className="sidebar-section">
            <ResponseDisplay response={response} loading={loading} />
          </div>

          <div className="sidebar-section">
            <h3>Telemetry Data</h3>
            <TelemetryPanel 
              telemetry={telemetry} 
              onRunSelect={handleRunSelect}
              selectedRunId={selectedRunId}
            />
          </div>

          <div className="sidebar-section">
            <h3>Optimizations</h3>
            <OptimizationsPanel optimizations={optimizations} />
          </div>

          <div className="sidebar-section">
            <AgentOutputsPanel agentOutputs={agentOutputs} />
          </div>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>Error: {error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <span>Processing...</span>
        </div>
      )}
    </div>
  )
}

export default App
