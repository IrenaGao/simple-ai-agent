import React from 'react'
import { MessageSquare, Copy, Check } from 'lucide-react'
import { useState } from 'react'

function ResponseDisplay({ response, loading }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(response)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  if (loading) {
    return (
      <div className="response-display">
        <div className="response-header">
          <MessageSquare size={16} />
          <h3>Agent Response</h3>
        </div>
        <div className="response-content loading">
          <div className="loading-spinner"></div>
          <span>Processing your query...</span>
        </div>
      </div>
    )
  }

  if (!response) {
    return (
      <div className="response-display">
        <div className="response-header">
          <MessageSquare size={16} />
          <h3>Agent Response</h3>
        </div>
        <div className="response-content empty">
          <p>No response yet. Submit a query to see the agent's response here.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="response-display">
      <div className="response-header">
        <MessageSquare size={16} />
        <h3>Agent Response</h3>
        <button 
          onClick={handleCopy}
          className="copy-button"
          title="Copy response"
        >
          {copied ? <Check size={14} /> : <Copy size={14} />}
        </button>
      </div>
      <div className="response-content">
        <div className="response-text">
          {response.split('\n').map((line, index) => (
            <p key={index}>{line}</p>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ResponseDisplay
