import React, { useState } from 'react'
import { Play, Zap } from 'lucide-react'

function QueryForm({ onSubmit, loading }) {
  const [query, setQuery] = useState('')
  const [simulate, setSimulate] = useState(false)
  const [systemPrompt, setSystemPrompt] = useState('')
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      onSubmit(query.trim(), simulate, systemPrompt.trim() || null)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="query-form">
      <div className="form-group">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query (e.g., 'How do I set up Intercom?')"
          className="query-input"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="submit-button"
        >
          {loading ? (
            <div className="loading-spinner"></div>
          ) : simulate ? (
            <Zap size={16} />
          ) : (
            <Play size={16} />
          )}
          {loading ? 'Processing...' : simulate ? 'Simulate' : 'Run Live'}
        </button>
      </div>
      
      <div className="form-options">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={simulate}
            onChange={(e) => setSimulate(e.target.checked)}
            disabled={loading}
          />
          <span>Use simulation mode</span>
        </label>
        
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="advanced-toggle"
          disabled={loading}
        >
          {showAdvanced ? 'Hide' : 'Show'} Advanced Options
        </button>
      </div>
      
      {showAdvanced && (
        <div className="advanced-options">
          <div className="form-group">
            <label htmlFor="system-prompt" className="field-label">
              Custom System Prompt (Optional)
            </label>
            <textarea
              id="system-prompt"
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder="Enter a custom system prompt to modify the orchestrator agent's behavior..."
              className="system-prompt-input"
              rows={4}
              disabled={loading}
            />
            <div className="field-help">
              This will override the default system prompt for the orchestrator agent. 
              Leave empty to use the default behavior.
            </div>
          </div>
        </div>
      )}
    </form>
  )
}

export default QueryForm
