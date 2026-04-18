import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

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
