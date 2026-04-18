<template>
  <section class="mb-16">
    <div class="bg-[#ecedf7] rounded-xl p-8">
      <div class="flex flex-col md:flex-row items-center justify-between gap-4">
        <!-- Step 1: Upload -->
        <div class="flex flex-col items-center gap-3" :class="stepClass(1)">
          <div class="w-16 h-16 rounded-full flex items-center justify-center shadow-lg transition-all duration-500"
               :class="stepCircleClass(1)">
            <span class="material-symbols-outlined text-3xl filled">upload_file</span>
          </div>
          <span class="text-sm font-bold" :class="currentStep >= 1 ? 'text-[#0058be]' : 'text-slate-400'">Upload PDF</span>
        </div>

        <StepArrow :active="currentStep >= 2" />

        <!-- Step 2: Hash -->
        <div class="flex flex-col items-center gap-3" :class="stepClass(2)">
          <div class="w-14 h-14 rounded-full flex items-center justify-center transition-all duration-500"
               :class="stepCircleClass(2)">
            <span class="material-symbols-outlined text-2xl">fingerprint</span>
          </div>
          <span class="text-xs font-medium">Hash (SHA-256)</span>
        </div>

        <StepArrow :active="currentStep >= 3" />

        <!-- Step 3: RSA Signing -->
        <div class="flex flex-col items-center gap-3" :class="stepClass(3)">
          <div class="w-14 h-14 rounded-full flex items-center justify-center transition-all duration-500"
               :class="stepCircleClass(3)">
            <span class="material-symbols-outlined text-2xl">vpn_key</span>
          </div>
          <span class="text-xs font-medium">RSA Signing</span>
        </div>

        <StepArrow :active="currentStep >= 5" />

        <!-- Step 4: Attach Signature -->
        <div class="flex flex-col items-center gap-3" :class="stepClass(5)">
          <div class="w-14 h-14 rounded-full flex items-center justify-center transition-all duration-500"
               :class="stepCircleClass(5)">
            <span class="material-symbols-outlined text-2xl">verified</span>
          </div>
          <span class="text-xs font-medium">Attach Signature</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useSignatureStore } from '../stores/signature'
import StepArrow from './StepArrow.vue'

const store = useSignatureStore()
const currentStep = computed(() => store.currentStep)

function stepClass(step) {
  if (currentStep.value >= step) return 'opacity-100'
  return 'opacity-40'
}

function stepCircleClass(step) {
  if (currentStep.value === step) {
    return 'bg-[#2170e4] text-white ring-4 ring-blue-200 pulse-ring'
  }
  if (currentStep.value > step) {
    return 'bg-[#2170e4] text-white shadow-lg'
  }
  return 'bg-[#e6e7f2] text-[#424754]'
}
</script>
