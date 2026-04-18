<template>
  <section class="lg:col-span-8 space-y-10">
    <!-- Visual Cryptography Flow -->
    <div class="bg-[#ecedf7] rounded-xl overflow-hidden">
      <div class="p-8 border-b border-[#e6e7f2] flex justify-between items-center bg-[#f2f3fd]">
        <h3 class="text-lg font-bold">Visual Cryptography Flow</h3>
        <div class="flex gap-2">
          <span class="px-3 py-1 bg-[#ffdf9f] text-[#261a00] text-[10px] font-bold rounded-full uppercase tracking-tighter">RSA-2048</span>
          <span class="px-3 py-1 bg-[#d8e2ff] text-[#001a42] text-[10px] font-bold rounded-full uppercase tracking-tighter">SHA-256</span>
        </div>
      </div>

      <div class="p-12 flex flex-col items-center">
        <div class="w-full max-w-3xl flex flex-col md:flex-row items-center justify-between gap-12 relative">
          <!-- Original File -->
          <div class="relative group">
            <div class="bg-white p-6 rounded-xl shadow-md flex flex-col items-center gap-4 border transition-all duration-500"
                 :class="currentStep >= 1 ? 'border-[#2170e4] shadow-blue-100' : 'border-[#e6e7f2]'">
              <div class="w-16 h-20 bg-slate-50 border border-slate-200 rounded flex flex-col p-2 gap-1">
                <div class="h-1 w-full bg-slate-200 rounded"></div>
                <div class="h-1 w-3/4 bg-slate-200 rounded"></div>
                <div class="h-1 w-full bg-slate-200 rounded"></div>
                <div class="h-1 w-1/2 bg-slate-200 rounded"></div>
              </div>
              <span class="text-xs font-bold uppercase tracking-widest text-[#424754]">Original File</span>
              <p v-if="store.uploadedFile" class="text-[10px] text-[#727785] font-mono truncate max-w-30">
                {{ store.uploadedFile.fileName }}
              </p>
            </div>
            <div class="absolute -top-4 -right-4 bg-white p-2 rounded-full shadow-sm border border-[#e6e7f2] group-hover:scale-110 transition-transform cursor-help"
                 title="The original PDF document to be signed">
              <span class="material-symbols-outlined text-[#956e00] text-lg">info</span>
            </div>
          </div>

          <!-- Arrow: File → Hash -->
          <div class="flex flex-col items-center gap-4">
            <span class="material-symbols-outlined text-4xl transition-all duration-500"
                  :class="currentStep >= 2 ? 'text-[#0058be] animate-pulse' : 'text-[#c2c6d6]'">
              double_arrow
            </span>
            <div class="px-4 py-2 rounded-full transition-all duration-300"
                 :class="currentStep >= 2 ? 'bg-[#2170e4] text-white' : 'bg-[#e6e7f2] text-[#424754]'">
              <span class="text-[10px] font-black font-mono">
                {{ currentStep === 2 ? 'HASHING...' : currentStep > 2 ? 'HASHED ✓' : 'WAITING' }}
              </span>
            </div>
          </div>

          <!-- Digital Digest -->
          <div class="p-8 rounded-xl shadow-md flex flex-col items-center gap-4 transition-all duration-500"
               :class="currentStep >= 2
                 ? 'bg-white border-2 border-[#adc6ff]'
                 : 'bg-[#f2f3fd] border-2 border-[#e6e7f2]'">
            <div class="w-24 h-12 rounded-lg flex items-center justify-center font-mono text-[10px] overflow-hidden px-2 transition-all duration-500"
                 :class="currentStep >= 2 ? 'bg-blue-50 text-[#0058be] hash-glow' : 'bg-[#f2f3fd] text-[#c2c6d6]'">
              {{ hashDisplay }}
            </div>
            <span class="text-xs font-bold uppercase tracking-widest text-[#424754]">Digital Digest</span>

            <!-- Signature info (appears after signing) -->
            <div v-if="currentStep >= 4" class="w-full">
              <div class="bg-amber-50 border border-amber-200 rounded-lg p-2 text-[9px] font-mono text-amber-800 break-all mt-2">
                <span class="font-bold block mb-1 text-[10px]">🔐 Signed with Private Key (RSA)</span>
                {{ signatureDisplay }}
              </div>
            </div>

            <div class="flex gap-2 mt-2">
              <span class="material-symbols-outlined transition-all duration-300"
                    :class="currentStep >= 3 ? 'text-[#f9bd22] filled' : 'text-[#c2c6d6]'"
                    title="Private key used for signing">lock</span>
              <span class="material-symbols-outlined transition-all duration-300"
                    :class="currentStep >= 3 ? 'text-[#0058be]' : 'text-[#c2c6d6]'"
                    title="RSA encryption key">key</span>
            </div>
          </div>
        </div>

        <!-- Crypto Properties -->
        <div class="mt-16 w-full p-6 glass-panel rounded-2xl border border-white/40">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div class="flex items-start gap-4">
              <div class="p-3 bg-[#6cf8bb] rounded-xl">
                <span class="material-symbols-outlined text-[#00714d]">security</span>
              </div>
              <div>
                <p class="text-xs font-bold mb-1">Integrity</p>
                <p class="text-[11px] text-[#424754] leading-relaxed">Hash ensures data hasn't been altered.</p>
              </div>
            </div>
            <div class="flex items-start gap-4">
              <div class="p-3 bg-[#d8e2ff] rounded-xl">
                <span class="material-symbols-outlined text-[#001a42]">person_check</span>
              </div>
              <div>
                <p class="text-xs font-bold mb-1">Authenticity</p>
                <p class="text-[11px] text-[#424754] leading-relaxed">Private key proves document origin.</p>
              </div>
            </div>
            <div class="flex items-start gap-4">
              <div class="p-3 bg-[#ffdf9f] rounded-xl">
                <span class="material-symbols-outlined text-[#261a00]">history_edu</span>
              </div>
              <div>
                <p class="text-xs font-bold mb-1">Non-repudiation</p>
                <p class="text-[11px] text-[#424754] leading-relaxed">Signer cannot deny their signature.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom: Signed Output & Verification -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Signed Output -->
      <div class="bg-white rounded-xl p-8 shadow-sm transition-all duration-500"
           :class="store.hasSigned ? 'opacity-100' : 'opacity-50'">
        <div class="flex items-center justify-between mb-6">
          <h4 class="text-sm font-bold uppercase tracking-widest text-[#424754]">Signed Output</h4>
          <button v-if="store.hasSigned" @click="store.downloadSignedPdf()"
                  class="hover:text-[#0058be] transition-colors" title="Download signed PDF">
            <span class="material-symbols-outlined text-[#424754]">download</span>
          </button>
          <span v-else class="material-symbols-outlined text-[#c2c6d6]">download</span>
        </div>
        <div v-if="store.hasSigned" class="flex items-center gap-6 p-6 bg-[#f2f3fd] rounded-xl">
          <div class="w-12 h-16 bg-white border border-[#c2c6d6] rounded flex items-center justify-center relative">
            <span class="material-symbols-outlined text-[#0058be] text-2xl">description</span>
            <div class="absolute -bottom-2 -right-2 bg-[#6cf8bb] p-1 rounded-full border-2 border-white">
              <span class="material-symbols-outlined text-[10px] text-[#00714d] filled">verified</span>
            </div>
          </div>
          <div>
            <p class="text-sm font-bold">{{ store.signResult.fileName }}</p>
            <p class="text-[10px] text-[#727785]">{{ formatSize(store.signResult.fileSize) }} • RSA/SHA-256</p>
          </div>
        </div>
        <div v-else class="flex items-center justify-center p-10 text-[#c2c6d6]">
          <p class="text-sm">Sign a PDF to see output here</p>
        </div>
      </div>

      <!-- Verification Result -->
      <div class="bg-white rounded-xl p-8 shadow-sm transition-all duration-500"
           :class="verifyBorderClass">
        <div class="flex items-center justify-between mb-6">
          <h4 class="text-sm font-bold uppercase tracking-widest text-[#424754]">Verification Result</h4>
          <div v-if="store.verifyResult"
               class="w-3 h-3 rounded-full"
               :class="store.verifyResult.valid
                 ? 'bg-[#4edea3] shadow-[0_0_8px_rgba(78,222,163,0.8)]'
                 : 'bg-red-400 shadow-[0_0_8px_rgba(248,113,113,0.8)]'">
          </div>
        </div>

        <div v-if="store.loading.verify" class="flex flex-col items-center justify-center py-8">
          <span class="material-symbols-outlined text-5xl text-[#0058be] animate-spin">progress_activity</span>
          <p class="text-sm text-[#424754] mt-4">Verifying signature...</p>
        </div>
        <div v-else-if="store.verifyResult" class="flex flex-col items-center justify-center py-4">
          <span class="material-symbols-outlined text-6xl mb-2 filled check-pop"
                :class="store.verifyResult.valid ? 'text-[#006c49]' : 'text-[#ba1a1a]'">
            {{ store.verifyResult.valid ? 'verified' : 'gpp_bad' }}
          </span>
          <p class="text-2xl font-black tracking-tight"
             :class="store.verifyResult.valid ? 'text-[#006c49]' : 'text-[#ba1a1a]'">
            {{ store.verifyResult.valid ? 'VALID SIGNATURE' : 'INVALID SIGNATURE' }}
          </p>
          <p class="text-xs text-[#424754] mt-2 text-center">
            {{ store.verifyResult.valid
              ? '✓ Cryptographic identity matches the provided public key.'
              : store.verifyResult.message }}
          </p>

          <!-- Show which public key was used -->
          <div class="mt-3 w-full bg-blue-50 border border-blue-200 rounded-lg p-2">
            <p class="text-[9px] font-semibold text-blue-900 mb-1">🔑 Verified with Public Key:</p>
            <p class="text-[9px] font-mono text-blue-700 break-all">
              {{ store.verifyResult.usedPublicKey || store.publicKey.substring(0, 60) + '...' }}
            </p>
          </div>

          <!-- Detail info -->
          <div v-if="store.verifyResult.details?.length" class="mt-4 w-full text-left">
            <div v-for="d in store.verifyResult.details" :key="d.index"
                 class="bg-[#f2f3fd] rounded-lg p-3 text-[11px] space-y-1">
              <p><span class="font-bold">Signer:</span> {{ d.signer }}</p>
              <p><span class="font-bold">Hash:</span> {{ d.hashAlgorithm }}</p>
              <p><span class="font-bold">Mechanism:</span> {{ d.signatureMechanism }}</p>
              <p v-if="d.signedAt"><span class="font-bold">Signed at:</span> {{ d.signedAt }}</p>
            </div>
          </div>
        </div>
        <div v-else class="flex flex-col items-center justify-center py-8 text-[#c2c6d6]">
          <span class="material-symbols-outlined text-5xl">shield_question</span>
          <p class="text-sm mt-2">Upload a signed PDF to verify</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useSignatureStore } from '../stores/signature'

const store = useSignatureStore()
const currentStep = computed(() => store.currentStep)

const hashDisplay = computed(() => {
  if (store.uploadedFile?.hash) {
    return store.uploadedFile.hash.substring(0, 16) + '...'
  }
  return 'waiting...'
})

const signatureDisplay = computed(() => {
  if (store.signResult?.signaturePreview) {
    return store.signResult.signaturePreview
  }
  return ''
})

const verifyBorderClass = computed(() => {
  if (!store.verifyResult) return ''
  return store.verifyResult.valid
    ? 'border-2 border-[#6cf8bb]'
    : 'border-2 border-red-300'
})

function formatSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>
