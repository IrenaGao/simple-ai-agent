import React, { useState, useEffect } from 'react'
import { Clock, Activity, AlertCircle, CheckCircle, XCircle } from 'lucide-react'
import { apiService } from '../services/api'

function TelemetryPanel({ telemetry, onRunSelect, selectedRunId }) {
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadRuns()
  }, [])

  const loadRuns = async () => {
    setLoading(true)
    try {
      const response = await apiService.listRuns()
      setRuns(response.runs || [])
    } catch (error) {
      console.error('Error loading runs:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <Activity className="status-icon running" />
      case 'completed':
        return <CheckCircle className="status-icon completed" />
      case 'failed':
        return <XCircle className="status-icon failed" />
      default:
        return <Clock className="status-icon" />
    }
  }

  const formatDuration = (ms) => {
    if (!ms) return 'N/A'
    const seconds = Math.round(ms / 1000)
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
  }

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A'
    return new Date(timestamp).toLocaleTimeString()
  }

  return (
    <div className="telemetry-panel">
      <div className="panel-header">
        <h4>Recent Runs</h4>
        <button 
          onClick={loadRuns} 
          disabled={loading}
          className="refresh-button"
        >
          {loading ? '...' : '↻'}
        </button>
      </div>

      <div className="runs-list">
        {runs.map((run) => (
          <div
            key={run.run_id}
            className={`run-item ${selectedRunId === run.run_id ? 'selected' : ''}`}
            onClick={() => onRunSelect(run.run_id)}
          >
            <div className="run-header">
              <div className="run-id">{run.run_id.slice(0, 8)}...</div>
              <div className="run-status">
                {getStatusIcon(run.status)}
                <span className="status-text">{run.status}</span>
              </div>
            </div>
            <div className="run-details">
              <div className="run-time">
                <Clock size={12} />
                {formatTimestamp(run.start_time)} - {formatTimestamp(run.end_time)}
              </div>
              <div className="run-duration">
                Duration: {formatDuration(run.total_duration_ms)}
              </div>
              <div className="run-events">
                Events: {run.total_events}
              </div>
            </div>
          </div>
        ))}
      </div>

      {telemetry && (
        <div className="telemetry-details">
          <h4>Current Run Details</h4>
          <div className="telemetry-summary">
            <div className="summary-item">
              <strong>Run ID:</strong> {telemetry.run_id}
            </div>
            <div className="summary-item">
              <strong>Total Events:</strong> {telemetry.summary.total_events}
            </div>
            <div className="summary-item">
              <strong>Duration:</strong> {formatDuration(telemetry.summary.total_duration_ms)}
            </div>
            <div className="summary-item">
              <strong>Status:</strong> {telemetry.summary.status}
            </div>
            <div className="summary-item">
              <strong>LLM Calls:</strong> {telemetry.summary.total_llm_calls}
            </div>
            <div className="summary-item">
              <strong>Tool Calls:</strong> {telemetry.summary.total_tool_calls}
            </div>
            <div className="summary-item">
              <strong>Delegations:</strong> {telemetry.summary.total_delegations}
            </div>
            {telemetry.summary.error_count > 0 && (
              <div className="summary-item error">
                <AlertCircle size={14} />
                <strong>Errors:</strong> {telemetry.summary.error_count}
              </div>
            )}
          </div>

          <div className="events-list">
            <h5>Recent Events</h5>
            {telemetry.events.slice(-10).map((event, index) => (
              <div
                key={index}
                className={`telemetry-event ${event.success === false ? 'error' : 'success'}`}
              >
                <div className="event-header">
                  <span className="event-type">{event.event_type}</span>
                  <span className="event-time">
                    {formatTimestamp(event.timestamp)}
                  </span>
                </div>
                {event.agent_type && (
                  <div className="event-agent">
                    Agent: {event.agent_type}
                  </div>
                )}
                {event.step_name && (
                  <div className="event-step">
                    Step: {event.step_name}
                  </div>
                )}
                {event.duration_ms && (
                  <div className="event-duration">
                    Duration: {Math.round(event.duration_ms)}ms
                  </div>
                )}
                {event.error_message && (
                  <div className="event-error">
                    Error: {event.error_message}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default TelemetryPanel
