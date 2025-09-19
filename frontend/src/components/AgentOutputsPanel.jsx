import React, { useState } from 'react'
import { Bot, Clock, CheckCircle, XCircle, ChevronDown, ChevronRight } from 'lucide-react'

function AgentOutputsPanel({ agentOutputs = [] }) {
  const [expandedOutputs, setExpandedOutputs] = useState(new Set())

  const toggleExpanded = (index) => {
    const newExpanded = new Set(expandedOutputs)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedOutputs(newExpanded)
  }

  const getAgentIcon = (agentType) => {
    switch (agentType) {
      case 'orchestrator':
        return '🎯'
      case 'summarizer':
        return '📊'
      case 'diagrammer':
        return '📈'
      default:
        return '🤖'
    }
  }

  const getAgentColor = (agentType) => {
    switch (agentType) {
      case 'orchestrator':
        return '#2196f3'
      case 'summarizer':
        return '#4caf50'
      case 'diagrammer':
        return '#ff9800'
      default:
        return '#9e9e9e'
    }
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  const truncateContent = (content, maxLength = 200) => {
    if (content.length <= maxLength) return content
    return content.substring(0, maxLength) + '...'
  }

  if (agentOutputs.length === 0) {
    return (
      <div className="agent-outputs-panel">
        <div className="panel-header">
          <Bot size={20} />
          <h3>Agent Outputs</h3>
        </div>
        <div className="no-outputs">
          <p>No agent outputs available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="agent-outputs-panel">
      <div className="panel-header">
        <Bot size={20} />
        <h3>Agent Outputs</h3>
        <span className="output-count">{agentOutputs.length}</span>
      </div>
      
      <div className="outputs-list">
        {agentOutputs.map((output, index) => {
          const isExpanded = expandedOutputs.has(index)
          const agentColor = getAgentColor(output.agent_type)
          const isSuccess = output.success !== false
          
          return (
            <div key={index} className="output-item">
              <div 
                className="output-header"
                onClick={() => toggleExpanded(index)}
                style={{ borderLeftColor: agentColor }}
              >
                <div className="output-info">
                  <span className="agent-icon">{getAgentIcon(output.agent_type)}</span>
                  <div className="output-details">
                    <div className="output-title">
                      <span className="agent-type">{output.agent_type}</span>
                      <span className="output-type">{output.output_type}</span>
                    </div>
                    <div className="output-meta">
                      <Clock size={12} />
                      <span>{formatTimestamp(output.timestamp)}</span>
                      {isSuccess ? (
                        <CheckCircle size={12} className="success-icon" />
                      ) : (
                        <XCircle size={12} className="error-icon" />
                      )}
                    </div>
                  </div>
                </div>
                <div className="output-actions">
                  {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                </div>
              </div>
              
              {isExpanded && (
                <div className="output-content">
                  <div className="content-section">
                    <h4>Output Content</h4>
                    <div className="content-text">
                      {output.output_content}
                    </div>
                  </div>
                  
                  {output.metadata && Object.keys(output.metadata).length > 0 && (
                    <div className="content-section">
                      <h4>Metadata</h4>
                      <div className="metadata-grid">
                        {Object.entries(output.metadata).map(([key, value]) => (
                          <div key={key} className="metadata-item">
                            <span className="metadata-key">{key}:</span>
                            <span className="metadata-value">
                              {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {output.error_message && (
                    <div className="content-section error-section">
                      <h4>Error Message</h4>
                      <div className="error-message">
                        {output.error_message}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default AgentOutputsPanel
