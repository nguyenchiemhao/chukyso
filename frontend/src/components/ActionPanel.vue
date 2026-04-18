<template>
  <aside class="lg:col-span-4 space-y-10">
    <!-- Source Material Card -->
    <div class="bg-white rounded-xl p-8 shadow-sm">
      <h3 class="text-lg font-bold mb-6 flex items-center gap-2">
        <span class="material-symbols-outlined text-[#0058be]">cloud_upload</span>
        Source Material
      </h3>

      <!-- Drop Zone -->
      <div
        class="border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center text-center group transition-colors cursor-pointer bg-[#f2f3fd]"
        :class="isDragging ? 'border-[#0058be] bg-blue-50' : 'border-[#c2c6d6] hover:border-[#0058be]'"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="handleDrop"
        @click="$refs.fileInput.click()"
      >
        <template v-if="!store.uploadedFile">
          <span class="material-symbols-outlined text-5xl mb-4 transition-colors"
                :class="isDragging ? 'text-[#0058be]' : 'text-[#c2c6d6] group-hover:text-[#0058be]'">
            description
          </span>
          <p class="text-sm font-semibold text-[#424754]">Drop PDF here</p>
          <p class="text-xs text-[#727785] mt-1">Maximum file size 10MB</p>
        </template>
        <template v-else>
          <span class="material-symbols-outlined text-5xl text-[#0058be] mb-4 filled">description</span>
          <p class="text-sm font-bold text-[#191b23]">{{ store.uploadedFile.fileName }}</p>
          <p class="text-xs text-[#727785] mt-1">{{ formatSize(store.uploadedFile.fileSize) }}</p>
          <button @click.stop="store.reset()" class="mt-3 text-xs text-red-500 hover:underline">Remove</button>
        </template>
        <input ref="fileInput" type="file" accept=".pdf" class="hidden" @change="handleFileSelect" />
      </div>

      <!-- Loading -->
      <div v-if="store.loading.upload" class="mt-4 flex items-center gap-2 text-sm text-[#0058be]">
        <span class="material-symbols-outlined animate-spin text-lg">progress_activity</span>
        Uploading & hashing...
      </div>

      <!-- Key Generation -->
      <div class="mt-8 pt-8 border-t border-[#ecedf7]">
        <button
          @click="store.generateKeys()"
          :disabled="store.loading.keys"
          class="w-full py-4 bg-[#e6e7f2] text-[#191b23] font-bold rounded-xl hover:bg-[#d8d9e3] transition-all flex items-center justify-center gap-2 mb-4 disabled:opacity-50"
        >
          <span v-if="store.loading.keys" class="material-symbols-outlined animate-spin text-lg">progress_activity</span>
          <span v-else class="material-symbols-outlined text-lg">autorenew</span>
          {{ store.hasKeys ? 'Regenerate RSA Key Pair' : 'Generate RSA Key Pair' }}
        </button>

        <div v-if="store.hasKeys" class="space-y-6">
          <!-- Public Key Help Text -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p class="text-[11px] text-[#0058be] font-semibold mb-1">🔐 How RSA Keys Work:</p>
            <p class="text-[10px] text-[#424754] leading-relaxed">
              <strong>Private Key:</strong> Locked secret used to <strong>SIGN</strong> documents (only you have this)<br>
              <strong>Public Key:</strong> Open key used to <strong>VERIFY</strong> signatures (you can share this)
            </p>
          </div>

          <div>
            <label class="text-[10px] uppercase tracking-widest font-bold text-[#424754] mb-2 flex items-center justify-between">
              <span class="flex items-center gap-1">
                Public Key
                <span class="material-symbols-outlined text-xs text-[#0058be] cursor-help" title="Share this with others so they can verify your signatures">help</span>
              </span>
              <button @click="copyToClipboard(store.publicKey, 'public')" class="flex items-center gap-1 text-[#727785] hover:text-[#0058be] transition-colors" title="Copy public key">
                <span class="material-symbols-outlined text-sm">{{ copiedField === 'public' ? 'check_circle' : 'content_copy' }}</span>
                <span class="text-[9px] font-medium">{{ copiedField === 'public' ? 'Copied!' : 'Copy' }}</span>
              </button>
            </label>
            <div class="bg-[#f2f3fd] p-4 rounded-lg text-[10px] font-mono text-[#727785] break-all max-h-20 overflow-y-auto border border-blue-100">
              {{ store.publicKey }}
            </div>
            <p class="text-[9px] text-[#727785] mt-2">✓ Safe to share - used to verify your signatures</p>
          </div>

          <div>
            <label class="text-[10px] uppercase tracking-widest font-bold text-[#424754] mb-2 flex items-center justify-between">
              <span class="flex items-center gap-1">
                Private Key
                <span class="material-symbols-outlined text-xs text-red-500 cursor-help" title="Keep this secret - never share!">help</span>
              </span>
              <button @click="copyToClipboard(store.privateKey, 'private')" class="flex items-center gap-1 text-[#727785] hover:text-[#0058be] transition-colors" title="Copy private key">
                <span class="material-symbols-outlined text-sm">{{ copiedField === 'private' ? 'check_circle' : 'content_copy' }}</span>
                <span class="text-[9px] font-medium">{{ copiedField === 'private' ? 'Copied!' : 'Copy' }}</span>
              </button>
            </label>
            <div class="bg-[#fff5f5] p-4 rounded-lg text-[10px] font-mono text-[#c92a2a] break-all flex justify-between items-start gap-2 border border-red-200">
              <span class="max-h-20 overflow-y-auto flex-1">
                {{ showPrivateKey ? store.privateKey : '••••••••••••••••••••••••••••••••••••••••••••' }}
              </span>
              <button @click="showPrivateKey = !showPrivateKey" class="shrink-0 mt-0.5">
                <span class="material-symbols-outlined text-sm hover:text-[#c92a2a] transition-colors">
                  {{ showPrivateKey ? 'visibility' : 'visibility_off' }}
                </span>
              </button>
            </div>
            <p class="text-[9px] text-red-600 mt-2">⚠ Keep secret - used to sign documents</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="grid grid-cols-1 gap-4">
      <button
        @click="store.signPdf()"
        :disabled="!store.hasFile || !store.hasKeys || store.loading.sign"
        class="w-full py-5 bg-linear-to-br from-[#0058be] to-[#2170e4] text-white font-bold rounded-xl shadow-lg shadow-blue-500/20 hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center gap-3 disabled:opacity-40 disabled:hover:scale-100 disabled:cursor-not-allowed"
        title="Sign the uploaded PDF with your PRIVATE KEY"
      >
        <span v-if="store.loading.sign" class="material-symbols-outlined animate-spin">progress_activity</span>
        <span v-else class="material-symbols-outlined">edit_document</span>
        Sign PDF (with Private Key)
      </button>
      <button
        @click="triggerVerify"
        :disabled="!store.hasKeys"
        class="w-full py-5 bg-[#6cf8bb] text-[#00714d] font-bold rounded-xl hover:bg-[#4edea3] transition-all flex items-center justify-center gap-3 disabled:opacity-40 disabled:cursor-not-allowed"
        title="Verify a signed PDF using your PUBLIC KEY"
      >
        <span v-if="store.loading.verify" class="material-symbols-outlined animate-spin">progress_activity</span>
        <span v-else class="material-symbols-outlined">verified_user</span>
        Verify Signature (with Public Key)
      </button>
      <input ref="verifyInput" type="file" accept=".pdf" class="hidden" @change="handleVerifyFile" />

      <!-- External Verification by Public Key -->
      <div class="pt-2 border-t border-[#ecedf7]">
        <p class="text-[11px] font-semibold text-[#424754] mb-2">Verify with External Public Key:</p>
        <p class="text-[10px] text-[#727785] mb-3">Dán PUBLIC KEY của người ký (BEGIN/END PUBLIC KEY), không dùng certificate.</p>
        <textarea
          v-model="externalPublicKey"
          placeholder="Paste signer PUBLIC KEY: -----BEGIN PUBLIC KEY----- ... -----END PUBLIC KEY-----"
          class="w-full p-3 border border-[#c2c6d6] rounded-lg text-[10px] font-mono resize-none h-20 focus:border-[#0058be] focus:ring-1 focus:ring-blue-300 transition-all"
        ></textarea>
        <button
          @click="useMyPublicKey()"
          :disabled="!store.publicKey"
          class="w-full mt-2 py-2 bg-[#f2f3fd] text-[#0058be] font-semibold rounded-lg hover:bg-[#e6e7f2] transition-all disabled:opacity-40"
        >
          Use My Current Public Key
        </button>
        <button
          @click="triggerExternalVerify"
          :disabled="!externalPublicKey || store.loading.verify"
          class="w-full mt-3 py-4 bg-[#e6e7f2] text-[#0058be] font-bold rounded-xl hover:bg-[#d8d9e3] transition-all flex items-center justify-center gap-2 disabled:opacity-40"
        >
          <span v-if="store.loading.verify" class="material-symbols-outlined animate-spin">progress_activity</span>
          <span v-else class="material-symbols-outlined">security</span>
          Verify with This Public Key
        </button>
        <input ref="externalVerifyInput" type="file" accept=".pdf" class="hidden" @change="handleExternalVerifyFile" />
      </div>
    </div>

    <!-- Error -->
    <div v-if="store.error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
      <span class="material-symbols-outlined text-base align-middle mr-1">error</span>
      {{ store.error }}
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { useSignatureStore } from '../stores/signature'
import { verifyExternalSignature } from '../api'

const store = useSignatureStore()
const isDragging = ref(false)
const showPrivateKey = ref(false)
const verifyInput = ref(null)
const externalVerifyInput = ref(null)
const copiedField = ref(null)
const externalPublicKey = ref('')

function copyToClipboard(text, field) {
  navigator.clipboard.writeText(text).then(() => {
    copiedField.value = field
    setTimeout(() => { copiedField.value = null }, 2000)
  })
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function handleDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.type === 'application/pdf') {
    store.uploadPdf(file)
  }
}

function handleFileSelect(e) {
  const file = e.target.files[0]
  if (file) store.uploadPdf(file)
  e.target.value = ''
}

function triggerVerify() {
  verifyInput.value.click()
}

function handleVerifyFile(e) {
  const file = e.target.files[0]
  if (file) store.verifySignature(file)
  e.target.value = ''
}

function triggerExternalVerify() {
  externalVerifyInput.value.click()
}

function useMyPublicKey() {
  if (store.publicKey) {
    externalPublicKey.value = store.publicKey
  }
}

async function handleExternalVerifyFile(e) {
  const file = e.target.files[0]
  if (file && externalPublicKey.value) {
    store.loading.verify = true
    try {
      const result = await verifyExternalSignature(file, externalPublicKey.value)
      store.verifyResult = result
      store.currentStep = 6
    } catch (err) {
      // Handle error response from backend
      if (err.response && err.response.data && err.response.data.detail) {
        store.error = `Verification failed: ${err.response.data.detail}`
      } else if (err.response && err.response.status === 400) {
        store.error = `Invalid request (400): Please ensure you pasted a valid PEM PUBLIC KEY starting with "-----BEGIN PUBLIC KEY-----"`
      } else {
        store.error = err.message || 'Verification failed'
      }
    } finally {
      store.loading.verify = false
    }
  }
  e.target.value = ''
}
</script>
