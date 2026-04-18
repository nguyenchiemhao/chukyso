import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    if (status === 502) {
      // Vite proxy returns 502 when backend is unavailable.
      return Promise.reject(new Error('Backend is unreachable (502). Please start backend: python3 -m uvicorn backend.app:app --host 127.0.0.1 --port 8000'))
    }
    if (!error?.response) {
      return Promise.reject(new Error('Cannot connect to backend. Please check backend is running on 127.0.0.1:8000'))
    }
    return Promise.reject(error)
  }
)

export async function generateKeys() {
  const { data } = await api.post('/generate-keys')
  return data
}

export async function uploadPdf(file) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/upload', form)
  return data
}

export async function signPdf(fileId, sessionId) {
  const form = new FormData()
  form.append('fileId', fileId)
  form.append('sessionId', sessionId)
  const { data } = await api.post('/sign', form)
  return data
}

export async function verifyPdf(file, sessionId) {
  const form = new FormData()
  form.append('file', file)
  form.append('sessionId', sessionId)
  const { data } = await api.post('/verify', form)
  return data
}

export async function verifyExternalSignature(file, publicKey) {
  const form = new FormData()
  form.append('file', file)
  form.append('publicKey', publicKey)
  try {
    const { data } = await api.post('/verify-external', form)
    return data
  } catch (error) {
    // Re-throw with response data for better error handling
    if (error.response) {
      throw error
    }
    throw new Error(error.message || 'Verification failed')
  }
}

export async function downloadSigned(fileId) {
  const response = await api.get(`/download/${fileId}`, {
    responseType: 'blob',
  })
  return response.data
}

export async function tamperPdf(fileId) {
  const form = new FormData()
  form.append('fileId', fileId)
  const { data } = await api.post('/tamper', form)
  return data
}
