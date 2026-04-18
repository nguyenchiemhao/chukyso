<script setup>
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import StepProgress from './components/StepProgress.vue'
import ActionPanel from './components/ActionPanel.vue'
import VisualizationPanel from './components/VisualizationPanel.vue'
</script>

<template>
  <AppHeader />

  <main class="max-w-400 mx-auto p-8 lg:p-12">
    <!-- Hero -->
    <div class="mb-12">
      <h1 class="text-5xl font-black text-[#191b23] tracking-tighter mb-4">RSA Digital Signature Demo</h1>
      <p class="text-xl text-[#424754] font-light max-w-2xl">
        Sign and verify PDF files with visualized cryptography flow.
        Experience the intersection of mathematical certainty and digital trust.
      </p>
    </div>

    <!-- Step Progress Bar -->
    <StepProgress />

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-12">
      <ActionPanel />
      <VisualizationPanel />
    </div>
  </main>

  <AppFooter />
</template>
