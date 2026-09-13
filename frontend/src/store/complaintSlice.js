import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const emptyComplaint = {
  complaint_source: '', customer_name: '', product_name: '', product_strength: '',
  batch_number: '', affected_quantity: '', manufacturing_date: '', expiry_date: '',
  originating_site: '', impacted_material: '', complaint_category: '',
  complaint_description: '', severity: '', suggested_action: '', risk_assessment: '',
  status: 'Pending Triage'
}

export const sendMessage = createAsyncThunk('complaint/sendMessage', async (message, { getState, rejectWithValue }) => {
  try {
    const current_data = getState().complaint.form
    const { data } = await axios.post(`${API}/copilot/process`, { message, current_data })
    return { ...data, userMessage: message }
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Unable to contact the AI service.')
  }
})

export const uploadFile = createAsyncThunk('complaint/uploadFile', async (file, { rejectWithValue }) => {
  try {
    const body = new FormData()
    body.append('file', file)
    const { data } = await axios.post(`${API}/copilot/upload`, body)
    return { ...data, userMessage: `Uploaded ${file.name}` }
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Unable to process this file.')
  }
})

export const commitComplaint = createAsyncThunk('complaint/commit', async (_, { getState, rejectWithValue }) => {
  try {
    const { data } = await axios.post(`${API}/complaints`, getState().complaint.form)
    return data
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Unable to save the complaint.')
  }
})

const applyCopilot = (state, action) => {
  const incoming = action.payload.extracted_data
  Object.entries(incoming).forEach(([key, value]) => { if (value !== null && value !== '') state.form[key] = value })
  state.messages.push({ role: 'user', text: action.payload.userMessage })
  state.messages.push({ role: 'assistant', text: action.payload.assistant_message })
  if (action.payload.follow_up_question) state.messages.push({ role: 'assistant', text: action.payload.follow_up_question, followUp: true })
  state.missingFields = action.payload.missing_fields
  state.mode = action.payload.mode
}

const slice = createSlice({
  name: 'complaint',
  initialState: {
    form: emptyComplaint,
    messages: [{ role: 'assistant', text: 'Ready to process a new complaint. Paste text below or upload a complaint file.' }],
    missingFields: [], loading: false, error: null, savedId: null, mode: 'demo'
  },
  reducers: {
    updateField: (state, action) => { state.form[action.payload.name] = action.payload.value },
    resetComplaint: (state) => { state.form = { ...emptyComplaint }; state.missingFields = []; state.savedId = null }
  },
  extraReducers: builder => {
    builder
      .addCase(sendMessage.pending, state => { state.loading = true; state.error = null })
      .addCase(sendMessage.fulfilled, (state, action) => { state.loading = false; applyCopilot(state, action) })
      .addCase(sendMessage.rejected, (state, action) => { state.loading = false; state.error = action.payload })
      .addCase(uploadFile.pending, state => { state.loading = true; state.error = null })
      .addCase(uploadFile.fulfilled, (state, action) => { state.loading = false; applyCopilot(state, action) })
      .addCase(uploadFile.rejected, (state, action) => { state.loading = false; state.error = action.payload })
      .addCase(commitComplaint.pending, state => { state.loading = true; state.error = null })
      .addCase(commitComplaint.fulfilled, (state, action) => { state.loading = false; state.savedId = action.payload.id; state.form.status = 'Logged' })
      .addCase(commitComplaint.rejected, (state, action) => { state.loading = false; state.error = action.payload })
  }
})

export const { updateField, resetComplaint } = slice.actions
export default slice.reducer

