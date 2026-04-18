import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '../api'

export const useSignatureStore = defineStore('signature', () => {
  // --- State ---
  const sessionId = ref(null)
  const publicKey = ref('')
  const privateKey = ref('')

  const uploadedFile = ref(null)   // { fileId, fileName, fileSize, hash }
  const signResult = ref(null)     // { signedFileId, originalHash, signedHash, signaturePreview, ... }
  const verifyResult = ref(null)   // { valid, message, hash, details }

  const loading = ref({
    keys: false,
    upload: false,
    sign: false,
    verify: false,
  })
  const error = ref(null)

  // Current active visualization step: 0=idle, 1=upload, 2=hash, 3=signing, 4=signature, 5=attached
  const currentStep = ref(0)

  // --- Computed ---
  const hasKeys = computed(() => !!sessionId.value)
  const hasFile = computed(() => !!uploadedFile.value)
  const hasSigned = computed(() => !!signResult.value)

  // --- Actions ---
  async function generateKeys() {
    loading.value.keys = true
    error.value = null
    try {
      const data = await api.generateKeys()
      sessionId.value = data.sessionId
      publicKey.value = data.publicKey
      privateKey.value = data.privateKey
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
    } finally {
      loading.value.keys = false
    }
  }

  async function uploadPdf(file) {
    loading.value.upload = true
    error.value = null
    signResult.value = null
    verifyResult.value = null
    currentStep.value = 1
    try {
      const data = await api.uploadPdf(file)
      uploadedFile.value = data
      // Move to hash step after short delay for animation
      setTimeout(() => { currentStep.value = 2 }, 600)
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      currentStep.value = 0
    } finally {
      loading.value.upload = false
    }
  }

  async function signPdf() {
    if (!uploadedFile.value || !sessionId.value) return
    loading.value.sign = true
    error.value = null
    currentStep.value = 3
    try {
      const data = await api.signPdf(uploadedFile.value.fileId, sessionId.value)
      signResult.value = data
      // Animate through steps
      setTimeout(() => { currentStep.value = 4 }, 800)
      setTimeout(() => { currentStep.value = 5 }, 1600)
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      currentStep.value = 2
    } finally {
      loading.value.sign = false
    }
  }

  async function verifySignature(file) {
    if (!sessionId.value) return
    loading.value.verify = true
    error.value = null
    verifyResult.value = null
    try {
      const data = await api.verifyPdf(file, sessionId.value)
      verifyResult.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
    } finally {
      loading.value.verify = false
    }
  }

  async function downloadSignedPdf() {
    if (!signResult.value) return
    const blob = await api.downloadSigned(signResult.value.signedFileId)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = signResult.value.fileName
    a.click()
    URL.revokeObjectURL(url)
  }

  function reset() {
    uploadedFile.value = null
    signResult.value = null
    verifyResult.value = null
    currentStep.value = 0
    error.value = null
  }

  return {
    sessionId, publicKey, privateKey,
    uploadedFile, signResult, verifyResult,
    loading, error, currentStep,
    hasKeys, hasFile, hasSigned,
    generateKeys, uploadPdf, signPdf,
    verifySignature, downloadSignedPdf, reset,
  }
})
