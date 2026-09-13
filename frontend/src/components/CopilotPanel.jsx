import { useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Bot, FileUp, Send, Sparkles } from 'lucide-react'
import { sendMessage, uploadFile } from '../store/complaintSlice'

export default function CopilotPanel() {
  const dispatch = useDispatch()
  const { messages, loading, error, mode } = useSelector(state => state.complaint)
  const [text, setText] = useState('')
  const fileRef = useRef()
  const submit = event => {
    event.preventDefault()
    if (!text.trim() || loading) return
    dispatch(sendMessage(text.trim()))
    setText('')
  }
  return <aside className="copilot">
    <header className="copilot-head">
      <div className="bot-mark"><Bot size={20} /></div>
      <div><h2>AIVOA Copilot</h2><p>Complaint intake and risk triage</p></div>
      <span className="online"><i /> {mode === 'groq' ? 'Groq AI' : 'Demo AI'}</span>
    </header>
    <div className="messages">
      {messages.map((message, index) => <div key={index} className={`message ${message.role} ${message.followUp ? 'follow-up' : ''}`}>
        {message.role === 'assistant' && <Sparkles size={14} />}<span>{message.text}</span>
      </div>)}
      {loading && <div className="message assistant"><span className="typing">Analyzing complaint...</span></div>}
      {error && <div className="error">{error}</div>}
    </div>
    <form className="composer" onSubmit={submit}>
      <input ref={fileRef} type="file" accept=".pdf,.txt,.eml,.png,.jpg,.jpeg" hidden onChange={e => e.target.files[0] && dispatch(uploadFile(e.target.files[0]))} />
      <button type="button" className="icon-button" title="Upload complaint" onClick={() => fileRef.current.click()}><FileUp size={19} /></button>
      <textarea value={text} onChange={e => setText(e.target.value)} placeholder="Type or paste a complaint..." rows="2" onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) submit(e) }} />
      <button className="send" disabled={loading || !text.trim()}><Send size={18} /></button>
    </form>
    <p className="powered">Powered by LangGraph</p>
  </aside>
}

