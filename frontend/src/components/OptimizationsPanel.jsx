import React from 'react'
import { AlertTriangle, TrendingUp, Zap, Shield, Lightbulb } from 'lucide-react'

function OptimizationsPanel({ optimizations }) {
  const getSeverityIcon = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return <AlertTriangle className="severity-icon critical" />
      case 'high':
        return <AlertTriangle className="severity-icon high" />
      case 'medium':
        return <TrendingUp className="severity-icon medium" />
      case 'low':
        return <Lightbulb className="severity-icon low" />
      default:
        return <Lightbulb className="severity-icon" />
    }
  }

  const getCategoryIcon = (category) => {
    switch (category.toLowerCase()) {
      case 'performance':
        return <Zap className="category-icon" />
      case 'cost':
        return <TrendingUp className="category-icon" />
      case 'reliability':
        return <Shield className="category-icon" />
      case 'architecture':
        return <Lightbulb className="category-icon" />
      default:
        return <Lightbulb className="category-icon" />
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return '#9c27b0'
      case 'high':
        return '#f44336'
      case 'medium':
        return '#ff9800'
      case 'low':
        return '#4caf50'
      default:
        return '#2196f3'
    }
  }

  if (!optimizations || optimizations.length === 0) {
    return (
      <div className="optimizations-panel">
        <div className="no-optimizations">
          <Lightbulb size={24} />
          <p>No optimization suggestions available</p>
          <small>Run a simulation to see optimization recommendations</small>
        </div>
      </div>
    )
  }

  return (
    <div className="optimizations-panel">
      <div className="optimizations-header">
        <h4>Optimization Suggestions</h4>
        <span className="optimization-count">{optimizations.length} suggestions</span>
      </div>

      <div className="optimizations-list">
        {optimizations.map((optimization, index) => (
          <div
            key={optimization.id || index}
            className={`optimization-card ${optimization.severity?.toLowerCase() || 'low'}`}
          >
            <div className="optimization-header">
              <div className="optimization-title">
                {getSeverityIcon(optimization.severity)}
                <span>{optimization.title}</span>
              </div>
              <div className="optimization-category">
                {getCategoryIcon(optimization.category)}
                <span>{optimization.category}</span>
              </div>
            </div>

            <div className="optimization-content">
              <p className="optimization-description">
                {optimization.description}
              </p>

              <div className="optimization-suggestion">
                <strong>Suggestion:</strong> {optimization.suggestion}
              </div>

              {optimization.impact_estimate && (
                <div className="optimization-impact">
                  <strong>Expected Impact:</strong> {optimization.impact_estimate}
                </div>
              )}
            </div>

            <div className="optimization-footer">
              <div 
                className="severity-badge"
                style={{ backgroundColor: getSeverityColor(optimization.severity) }}
              >
                {optimization.severity?.toUpperCase() || 'LOW'}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="optimizations-summary">
        <h5>Summary</h5>
        <div className="summary-stats">
          {['critical', 'high', 'medium', 'low'].map(severity => {
            const count = optimizations.filter(opt => 
              opt.severity?.toLowerCase() === severity
            ).length
            if (count === 0) return null
            
            return (
              <div key={severity} className="summary-stat">
                <div 
                  className="stat-color"
                  style={{ backgroundColor: getSeverityColor(severity) }}
                ></div>
                <span className="stat-label">{severity}</span>
                <span className="stat-count">{count}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default OptimizationsPanel
