import { useDispatch, useSelector } from 'react-redux'
import { CheckCircle2, RotateCcw, ShieldAlert } from 'lucide-react'
import { commitComplaint, resetComplaint, updateField } from '../store/complaintSlice'

const groups = [
  { title: '1. Origin & Customer Details', fields: [['complaint_source', 'Complaint Source'], ['customer_name', 'Customer Name']] },
  { title: '2. Product & Batch Identification', fields: [['product_name', 'Product Name'], ['product_strength', 'Product Strength / Grade'], ['batch_number', 'Batch / Lot Number'], ['affected_quantity', 'Affected Quantity'], ['manufacturing_date', 'Manufacturing Date'], ['expiry_date', 'Expiry Date']] },
  { title: '3. Facility & Material Impact', fields: [['originating_site', 'Originating Site / Block'], ['impacted_material', 'Impacted Material']] },
]

export default function ComplaintForm() {
  const dispatch = useDispatch()
  const { form, missingFields, loading, savedId } = useSelector(state => state.complaint)
  const change = event => dispatch(updateField({ name: event.target.name, value: event.target.value }))
  return <main className="form-panel">
    <header className="page-head">
      <div><p className="eyebrow">API & FDF Quality Assurance Module</p><h1>Log Customer Complaint</h1></div>
      <span className={`status ${form.status === 'Logged' ? 'ready' : ''}`}>{form.status}</span>
    </header>

    {groups.map(group => <section className="form-section" key={group.title}>
      <h2>{group.title}</h2>
      <div className="field-grid">
        {group.fields.map(([name, label]) => <label key={name} className={missingFields.includes(name) ? 'missing' : ''}>
          <span>{label}</span><input name={name} value={form[name] || ''} onChange={change} placeholder="Awaiting AI extraction..." />
        </label>)}
      </div>
    </section>)}

    <section className="form-section">
      <h2>4. Defect Analysis</h2>
      <label><span>Complaint Category</span><input name="complaint_category" value={form.complaint_category || ''} onChange={change} /></label>
      <label><span>Complaint Description</span><textarea name="complaint_description" value={form.complaint_description || ''} onChange={change} rows="4" /></label>
    </section>

    <section className="risk-card">
      <div className="risk-title"><ShieldAlert size={17} /> AI Copilot Risk Assessment</div>
      <div className="field-grid">
        <label><span>Severity Suggested</span><input name="severity" value={form.severity || ''} onChange={change} /></label>
        <label><span>Suggested Next Action</span><input name="suggested_action" value={form.suggested_action || ''} onChange={change} /></label>
      </div>
      <label><span>Initial Risk Assessment</span><textarea name="risk_assessment" value={form.risk_assessment || ''} onChange={change} rows="3" /></label>
    </section>

    {savedId && <div className="success"><CheckCircle2 size={18} /> Complaint #{savedId} saved to the QMS ledger.</div>}
    <div className="actions">
      <button className="secondary" onClick={() => dispatch(resetComplaint())}><RotateCcw size={16} /> Reset</button>
      <button className="primary" disabled={loading} onClick={() => dispatch(commitComplaint())}>Commit to QMS Ledger</button>
    </div>
  </main>
}

