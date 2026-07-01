<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  'strategy-generated': [payload: { name: string; description: string; timeframe: 'h1' | 'h4' | 'd1'; asset: string }]
}>()

const description = ref('')
const timeframe = ref<string>('h4')
const asset = ref('')
const isGenerating = ref(false)

const assets = ['Bitcoin', 'Ethereum', 'Apple Stock', 'Tesla Stock', 'Microsoft Stock', 'Amazon Stock', 'Gold Futures', 'EUR/USD', 'GBP/USD', 'S&P 500 Index']

const handleGenerate = async () => {
  if (!description.value.trim() || !asset.value) {
    return
  }

  isGenerating.value = true

  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1200))

  const strategyName = `${description.value.split(' ').slice(0, 2).join(' ')} ${asset.value.split(' ')[0]}`

  emit('strategy-generated', {
    name: strategyName,
    description: description.value,
    timeframe: timeframe.value as 'h1' | 'h4' | 'd1',
    asset: asset.value,
  })

  description.value = ''
  timeframe.value = 'h4'
  asset.value = ''
  isGenerating.value = false
}
</script>

<template>
  <div class="rounded-lg border border-gray-200 bg-white p-8">
    <h2 class="mb-6 text-xl font-semibold text-black">Generate Strategy</h2>
    
    <form @submit.prevent="handleGenerate" class="space-y-5">
      <!-- Description -->
      <div>
        <label for="description" class="mb-2 block text-sm font-medium text-black">
          Strategy Description
        </label>
        <textarea
          id="description"
          v-model="description"
          placeholder="e.g., When the fast moving average crosses the slow moving average from the bottom up, we buy. When the opposite happens, we sell."
          class="h-24 w-full rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm text-black placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <!-- Timeframe -->
      <div>
        <label for="timeframe" class="mb-2 block text-sm font-medium text-black">
          Timeframe
        </label>
        <select
          id="timeframe"
          v-model="timeframe"
          class="w-full rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm text-black focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="h1">1 Hour</option>
          <option value="h4">4 Hours</option>
          <option value="d1">Daily</option>
        </select>
      </div>

      <!-- Asset -->
      <div>
        <label for="asset" class="mb-2 block text-sm font-medium text-black">
          Trading Instrument
        </label>
        <select
          id="asset"
          v-model="asset"
          class="w-full rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm text-black focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">Select an instrument...</option>
          <option v-for="a in assets" :key="a" :value="a">{{ a }}</option>
        </select>
      </div>

      <!-- Generate Button -->
      <button
        type="submit"
        :disabled="!description.trim() || !asset || isGenerating"
        class="mt-6 w-full rounded-lg bg-blue-500 px-6 py-3 font-semibold text-white transition-colors hover:bg-blue-600 disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed"
      >
        <span v-if="isGenerating" class="flex items-center justify-center gap-2">
          <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
          Generating...
        </span>
        <span v-else>Generate Strategy</span>
      </button>
    </form>
  </div>
</template>

<style scoped></style>
