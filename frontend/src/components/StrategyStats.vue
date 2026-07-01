<script setup lang="ts">
import { ref } from 'vue'

interface Strategy {
  id: string
  name: string
  description: string
  timeframe: 'h1' | 'h4' | 'd1'
  asset: string
  created: Date
  dailyProfitability: number[]
  dailyWinRate: number[]
  dailyAvgProfit: number[]
  dailyAvgLoss: number[]
  profitToDate: number[]
  totalProfitToday: number
  tradeCount: number
  winRate: number
  sharpeRatio: number
  maxDrawdown: number
  avgProfitableTrade: number
  avgLosingTrade: number
  profitabilityDynamic: number
  annualProfitability: number
}

defineProps<{
  strategies: Strategy[]
}>()

const hoveredStrategyId = ref<string | null>(null)

// Используем dailyProfitability для графика (берем последние 12 значений)
const getLastDaysData = (dailyData: number[]) => {
  if (!dailyData || dailyData.length === 0) return []
  // Берем последние 12 дней или меньше, если данных меньше
  return dailyData.slice(-30)
}

const getBarColor = (value: number) => {
  if (value >= 0) return '#34c759'
  return '#ff3b30'
}

const getBarHeight = (value: number, allValues: number[]): number => {
  const max = Math.max(...allValues.map(Math.abs))
  if (max === 0) return 0
  // Возвращаем высоту в пикселях (максимальная высота 80px)
  return (Math.abs(value) / max) * 80
}

// безопасное форматирование даты
const formatCreationDate = (date: Date | string | null | undefined): string => {
  // Если дата не передана
  if (!date) return 'N/A'
  
  try {
    // Создаем объект Date
    const dateObj = new Date(date)
    
    // Проверяем, что дата валидна
    if (isNaN(dateObj.getTime())) {
      return 'Invalid date'
    }
    
    return dateObj.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    })
  } catch (error) {
    return 'Invalid date'
  }
}

// безопасное вычисление дней
const getDaysPassed = (date: Date | string | null | undefined): number => {
  if (!date) return 0
  
  try {
    const now = new Date()
    const created = new Date(date)
    
    // Проверяем валидность даты
    if (isNaN(created.getTime())) {
      return 0
    }
    
    // Обнуляем время для обоих дат
    created.setHours(0, 0, 0, 0)
    now.setHours(0, 0, 0, 0)
    
    const days = Math.floor((now.getTime() - created.getTime()) / (1000 * 60 * 60 * 24))
    return Math.max(0, days)
  } catch (error) {
    return 0
  }
}

</script>

<template>
  <div class="rounded-lg border border-gray-200 bg-white p-8">
    <h2 class="mb-8 text-xl font-semibold text-black">Strategy Performance Overview</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="strategy in strategies"
        :key="strategy.id"
        @mouseenter="hoveredStrategyId = strategy.id"
        @mouseleave="hoveredStrategyId = null"
        class="rounded-lg border border-gray-200 bg-white transition-all hover:shadow-md overflow-hidden flex flex-col"
        :class="hoveredStrategyId && hoveredStrategyId !== strategy.id ? 'opacity-50' : ''"
      >
        <!-- Header -->
        <div class="px-4 pt-4 pb-3 border-b border-gray-200 flex-shrink-0">
          <h3 class="text-sm font-semibold text-black truncate">
            {{ strategy.name }}
          </h3>
          <p class="text-xs text-gray-500 truncate">
            {{ strategy.asset }} • {{ strategy.timeframe }}
          </p>
        </div>

        <!-- Monthly Chart -->
        <div class="px-4 py-3 border-b border-gray-200 flex-shrink-0">
          <div class="flex items-center justify-between mb-1">
            <div class="text-xs text-gray-500 font-medium">Cumulative profit to date</div>
            <!-- <div class="text-[10px] text-gray-400">Last 12 days</div> -->
          </div>
          <div class="flex items-end justify-between gap-0.5 h-100">
            <div
              v-for="(value, index) in getLastDaysData(strategy.profitToDate)"
              :key="index"
              class="flex flex-1 flex-col items-center"
            >
              <div
                    class="w-full rounded-t transition-all duration-200 hover:opacity-80"
                    :style="{
                      height: `${getBarHeight(value, getLastDaysData(strategy.profitToDate))}px`,
                      backgroundColor: getBarColor(value),
                      minHeight: Math.abs(value) > 0 ? '1px' : '0',
                    }"/>
            </div>
          </div>
        </div>

        <!-- Profitability Dynamics & Creation Date -->
        <div class="px-4 py-3 border-b border-gray-200 flex-shrink-0">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-xs text-gray-500 font-medium">Profitability</div>
              <div :class="['text-lg font-semibold', strategy.profitabilityDynamic >= 0 ? 'text-profit' : 'text-loss']">
                {{ strategy.profitabilityDynamic.toFixed(1) }}% / {{ strategy.annualProfitability.toFixed(1) }}%
              </div>
              <div class="text-xs text-gray-400 mt-1">Current / Annual</div>
            </div>
            <div class="text-right">
              <div class="text-xs text-gray-500 font-medium">Created</div>
              <div class="text-sm font-semibold text-black">
                {{ formatCreationDate(strategy.created) }}
              </div>
              <div class="text-xs text-gray-400">
                {{ getDaysPassed(strategy.created) }}d ago
              </div>
            </div>
          </div>
        </div>

        <!-- Key Metrics Grid -->
        <div class="px-4 py-3 flex-1 overflow-hidden">
          <div class="grid grid-cols-3 gap-1.5 text-xs">
            <div class="rounded bg-gray-50 p-2">
              <div class="text-gray-500 mb-0.5 leading-tight">P&L</div>
              <div :class="['font-semibold text-xs leading-tight truncate', strategy.totalProfitToday >= 0 ? 'text-profit' : 'text-loss']">
                {{ strategy.totalProfitToday >= 0 ? '+' : '' }}${{ strategy.totalProfitToday }}
              </div>
            </div>

            <div class="rounded bg-gray-50 p-2">
              <div class="text-gray-500 mb-0.5 leading-tight">Trades</div>
              <div class="font-semibold text-black text-xs leading-tight">
                {{ strategy.tradeCount }}
              </div>
            </div>

            <div class="rounded bg-gray-50 p-2">
              <div class="text-gray-500 mb-0.5 leading-tight">Win %</div>
              <div class="font-semibold text-profit text-xs leading-tight">
                {{ strategy.winRate }}%
              </div>
            </div>

            <div class="rounded bg-gray-50 p-2">
              <div class="text-gray-500 mb-0.5 leading-tight">Sharpe</div>
              <div class="font-semibold text-black text-xs leading-tight">
                {{ strategy.sharpeRatio.toFixed(2) }}
              </div>
            </div>

            <div class="rounded bg-gray-50 p-2">
              <div class="text-gray-500 mb-0.5 leading-tight">Max DD</div>
              <div class="font-semibold text-loss text-xs leading-tight">
                {{ strategy.maxDrawdown.toFixed(1) }}%
              </div>
            </div>

            <div class="rounded bg-gray-50 p-2">
              <div class="text-gray-500 mb-0.5 leading-tight">W/L</div>
              <div class="flex items-center gap-0.5 text-xs font-semibold min-h-4">
                <span class="text-profit leading-tight">+{{ strategy.avgProfitableTrade.toFixed(2) }}</span>
                <span class="text-gray-400">/</span>
                <span class="text-loss leading-tight">{{ strategy.avgLosingTrade.toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.text-profit {
  color: #34c759;
}
.text-loss {
  color: #ff3b30;
}
</style>