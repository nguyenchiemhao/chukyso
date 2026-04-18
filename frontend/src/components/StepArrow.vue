<template>
  <div class="hidden md:block flex-1 h-0.5 mx-4 relative transition-all duration-500"
       :class="active ? 'bg-[#2170e4]/40' : 'bg-[#c2c6d6]/30'">
    <div v-if="active" class="absolute inset-0 bg-linear-to-r from-[#2170e4]/60 to-[#2170e4]/20 rounded-full"></div>
    <div class="absolute right-0 -top-1.5">
      <span class="material-symbols-outlined text-sm transition-all duration-300"
            :class="active ? 'text-[#2170e4] animate-flow' : 'text-[#c2c6d6]'">
        chevron_right
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  active: { type: Boolean, default: false }
})
</script>
