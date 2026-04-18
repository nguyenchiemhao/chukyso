<template>
  <header class="bg-slate-50/80 backdrop-blur-xl shadow-sm sticky top-0 z-50">
    <div class="flex justify-between items-center w-full px-8 py-4 max-w-480 mx-auto">
      <div class="flex flex-col">
        <span class="text-2xl font-black text-slate-900 italic tracking-tight">The Cryptographic Gallery</span>
        <p class="text-xs text-[#424754] font-medium uppercase tracking-widest mt-0.5">RSA Signature v2.4 Demo</p>
      </div>
      <nav class="hidden md:flex items-center space-x-8 font-semibold">
        <a class="text-blue-700 border-b-2 border-blue-600 pb-1" href="#">Gallery</a>
        <a class="text-slate-500 hover:text-slate-900 transition-colors" href="#">Principles</a>
        <a class="text-slate-500 hover:text-slate-900 transition-colors" href="#">RSA Math</a>
        <a class="text-slate-500 hover:text-slate-900 transition-colors" href="#">Verification</a>
      </nav>
      <div class="flex items-center gap-4">
        <button class="p-2 hover:bg-slate-100 rounded-lg transition-all">
          <span class="material-symbols-outlined text-slate-500">settings</span>
        </button>
        <button class="p-2 hover:bg-slate-100 rounded-lg transition-all">
          <span class="material-symbols-outlined text-slate-500">help_outline</span>
        </button>
      </div>
    </div>
    <div class="bg-linear-to-b from-slate-200/50 to-transparent h-px w-full"></div>
  </header>
</template>
