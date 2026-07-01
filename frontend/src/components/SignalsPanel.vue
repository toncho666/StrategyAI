<script setup lang="ts">
import { ref, computed } from 'vue'

interface Signal {
  id?: number | string  // ✅ Добавляем опциональный id
  // strategyId: string
  strategyName: string
  type: 'buy' | 'sell'
  timestamp: Date
  asset: string
  openingPrice: number
  stopLoss: number
  takeProfit: number
  positionVolume: number
}

const props = defineProps<{
  signals: Signal[]
}>()

const filterAsset = ref('')
const filterType = ref<'' | 'buy' | 'sell'>('')
const filterDate = ref('')

const uniqueAssets = computed(() => {
  return [...new Set(props.signals.map(s => s.asset))].sort()
})

const filteredSignals = computed(() => {
  return props.signals.filter(signal => {
    const matchAsset = !filterAsset.value || signal.asset === filterAsset.value
    const matchType = !filterType.value || signal.type === filterType.value
    const matchDate = !filterDate.value || signal.timestamp.toDateString() === new Date(filterDate.value).toDateString()
    return matchAsset && matchType && matchDate
  })
})

const formatTime = (date: Date) => {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}d ago`
}

const formatDateTime = (date: Date) => {
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
}

const formatPrice = (price: number) => {
  if (price > 100) {
    return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  }
  return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 })
}
</script>

<template>
  <div class="flex flex-col rounded-lg border border-gray-200 bg-white p-8">
    <h2 class="mb-6 text-xl font-semibold text-black">Latest Trading Signals</h2>
    
    <!-- Filter Block -->
    <div class="mb-6 grid grid-cols-3 gap-4">
      <!-- Trading Instrument -->
      <div>
        <label class="mb-2 block text-xs font-medium text-gray-500">Trading Instrument</label>
        <select
          v-model="filterAsset"
          class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-black focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">All Assets</option>
          <option v-for="asset in uniqueAssets" :key="asset" :value="asset">
            {{ asset }}
          </option>
        </select>
      </div>

      <!-- Signal Direction -->
      <div>
        <label class="mb-2 block text-xs font-medium text-gray-500">Signal Direction</label>
        <select
          v-model="filterType"
          class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-black focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">All Signals</option>
          <option value="buy">Buy Signals</option>
          <option value="sell">Sell Signals</option>
        </select>
      </div>

      <!-- Date Filter -->
      <div>
        <label class="mb-2 block text-xs font-medium text-gray-500">Date</label>
        <input
          v-model="filterDate"
          type="date"
          class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-black focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>
    </div>

    <!-- Signals List -->
    <div class="flex flex-col gap-3 overflow-y-auto" style="max-height: 300px;">
      <div
        v-for="signal in filteredSignals"
        :key="signal.id"
        class="rounded-lg border border-gray-200 bg-gray-50 p-3 hover:bg-gray-100 transition-colors"
      >
        <!-- Header with strategy name and signal type -->
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <!-- Signal Type Badge -->
            <div
              :class="[
                'flex h-8 w-8 items-center justify-center rounded-full text-white font-semibold text-xs flex-shrink-0',
                signal.type === 'buy' ? 'bg-profit' : 'bg-loss'
              ]"
            >
              {{ signal.type === 'buy' ? '↑' : '↓' }}
            </div>

            <!-- Signal Details -->
            <div class="flex flex-col gap-0">
              <div class="text-xs font-semibold text-black">
                {{ signal.strategyName }}
              </div>
              <div class="text-xs text-gray-500">
                {{ signal.asset }}
              </div>
            </div>
          </div>

          <!-- Timestamp -->
          <div class="text-xs text-gray-500 whitespace-nowrap ml-2 flex-shrink-0">
            {{ formatTime(signal.timestamp) }}
          </div>
        </div>

        <!-- Signal Parameters Row -->
        <div class="grid grid-cols-5 gap-2 text-xs border-t border-gray-200 pt-2">
          <!-- Opening Price -->
          <div class="flex flex-col gap-0.5">
            <div class="text-gray-500 font-medium leading-tight">Entry</div>
            <div class="font-semibold text-black truncate text-xs">
              {{ formatPrice(signal.openingPrice) }}
            </div>
          </div>

          <!-- Stop Loss -->
          <div class="flex flex-col gap-0.5">
            <div class="text-gray-500 font-medium leading-tight">Stop</div>
            <div class="font-semibold text-loss truncate text-xs">
              {{ formatPrice(signal.stopLoss) }}
            </div>
          </div>

          <!-- Take Profit -->
          <div class="flex flex-col gap-0.5">
            <div class="text-gray-500 font-medium leading-tight">TP</div>
            <div class="font-semibold text-profit truncate text-xs">
              {{ formatPrice(signal.takeProfit) }}
            </div>
          </div>

          <!-- Position Volume -->
          <div class="flex flex-col gap-0.5">
            <div class="text-gray-500 font-medium leading-tight">Vol</div>
            <div class="font-semibold text-black truncate text-xs">
              {{ signal.positionVolume.toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) }}
            </div>
          </div>

          <!-- Signal Date and Time -->
          <div class="flex flex-col gap-0.5">
            <div class="text-gray-500 font-medium leading-tight">Time</div>
            <div class="font-semibold text-black truncate text-xs">
              {{ formatDateTime(signal.timestamp) }}
            </div>
          </div>
        </div>
      </div>

      <div v-if="filteredSignals.length === 0" class="flex items-center justify-center py-8 text-gray-400">
        <p class="text-sm">No signals match your filters</p>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
