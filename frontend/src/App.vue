<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import StrategyForm from './components/StrategyForm.vue'
import SignalsPanel from './components/SignalsPanel.vue'
import StrategyStats from './components/StrategyStats.vue'
import StrategyChart from './components/StrategyChart.vue'

// Интерфейсы для данных из бэкенда
interface DailyStat {
  dt: string
  profit_on_date: number
  profit_to_date: number
  profitability_on_date: number
  profitability_to_date: number
  annual_252_profitability_to_date: number
  annual_365_profitability_to_date: number
  trades_on_date: number
  trades_to_date: number
  dynamic_win_rate: number
  avg_profitable_trade_on_date: number
  avg_profitable_trade_to_date: number
  avg_losing_trade_on_date: number
  avg_losing_trade_to_date: number
  max_drawdown_on_date: number
  max_drawdown_to_date: number
}

// Структура данных от бэкенда
interface StrategyData {
  hist: DailyStat[]
  last: DailyStat | null
  error?: string
  total_records?: number
}

interface StrategiesResponse {
  strategies: Record<string, StrategyData>
  last_update: string | null
  total_strategies: number
}

// Адаптированный интерфейс Strategy для компонентов
interface Strategy {
  id: string
  name: string
  description: string
  timeframe: 'h1' | 'h4' | 'd1'
  asset: string
  created: Date  // Изменено с createdAt на created
  monthlyProfitability: number[]
  dailyProfitability: number[]
  dailyWinRate: number[]
  dailyAvgProfit: number[]
  dailyAvgLoss: number[]
  profitToDate: number[]  // Добавлено поле
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

interface Signal {
  id?: number | string  // Добавляем id (опционально)
  strategyName: string
  type: 'buy' | 'sell'
  // timestamp: Date | string
  timestamp: Date
  asset: string
  openingPrice: number
  stopLoss: number
  takeProfit: number
  positionVolume: number
}

// Состояния
const strategiesData = ref<StrategiesResponse | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)
const selectedStrategyId = ref('')
const signals = ref<Signal[]>([])
const signalsLoading = ref(false)
const signalsError = ref<string | null>(null)

// Карта с информацией о стратегиях
const strategyInfoMap = ref<Record<string, { name: string; timeframe: string; asset: string; created: Date }>>({})

// Функция для загрузки информации о стратегиях
const fetchStrategiesInfo = async () => {
  try {
    const response = await fetch('http://localhost:8020/strategies/list')
    if (response.ok) {
      const data = await response.json()
      const infoMap: Record<string, { name: string; timeframe: string; asset: string; created: Date }> = {}
      data.forEach((s: any) => {
        infoMap[s.name] = {
          name: s.name,
          timeframe: s.timeframe || 'h1',
          asset: s.asset || 'BTCUSDT',
          created: s.createdat ? new Date(s.createdat) : new Date()
        }
      })
      strategyInfoMap.value = infoMap
    }
  } catch (err) {
    console.warn('Failed to fetch strategies info:', err)
  }
}

// Безопасное создание даты
const safeCreateDate = (dateValue: string | Date | null | undefined): Date => {
  if (!dateValue) return new Date()
  if (dateValue instanceof Date) {
    return isNaN(dateValue.getTime()) ? new Date() : dateValue
  }
  if (typeof dateValue === 'string') {
    try {
      const date = new Date(dateValue)
      if (!isNaN(date.getTime())) {
        return date
      }
    } catch (e) {
      // Игнорируем ошибку парсинга
    }
    return new Date()
  }
  return new Date()
}

// Вспомогательная функция для агрегации по месяцам
const aggregateByMonth = (hist: DailyStat[]): number[] => {
  if (!hist || hist.length === 0) return Array(12).fill(0)
  
  const monthlyMap = new Map<string, number>()
  
  hist.forEach(day => {
    if (!day || !day.dt) return
    const month = day.dt.slice(0, 7)
    const current = monthlyMap.get(month) || 0
    monthlyMap.set(month, current + (day.profitability_on_date || 0))
  })
  
  const last12Months = Array.from(monthlyMap.entries())
    .sort((a, b) => a[0].localeCompare(b[0]))
    .slice(-12)
    .map(([_, value]) => value)
  
  while (last12Months.length < 12) {
    last12Months.unshift(0)
  }
  
  return last12Months
}

// Вычисляемое свойство для адаптированных стратегий
const strategies = computed<Strategy[]>(() => {
  if (!strategiesData.value?.strategies) return []
  
  const result: Strategy[] = []
  
  for (const [strategyName, data] of Object.entries(strategiesData.value.strategies)) {
    if (!data || !data.hist) {
      console.warn(`Missing hist data for strategy: ${strategyName}`, data)
      continue
    }
    const info = strategyInfoMap.value[strategyName] || {
      
      name: strategyName,
      timeframe: 'h1',
      asset: 'BTCUSDT',
      created: new Date()
    }
    
    const last30Days = data.hist?.slice(-30) || []
    const monthlyData = aggregateByMonth(data.hist || [])
    
    // Безопасно создаем дату
    const createdDate = safeCreateDate(info.created)
    
    // Логируем для отладки
    console.log(`Creating strategy: ${strategyName}, date:`, createdDate)
    
    result.push({
      id: strategyName,
      name: info.name || strategyName,
      description: `${info.name} strategy`,
      timeframe: (info.timeframe as 'h1' | 'h4' | 'd1') || 'h1',
      asset: info.asset || 'BTCUSDT',
      created: createdDate,  // Изменено с createdAt на created
      monthlyProfitability: monthlyData,
      dailyProfitability: last30Days.map(d => d?.profitability_on_date || 0),
      dailyWinRate: last30Days.map(d => d?.dynamic_win_rate || 0),
      dailyAvgProfit: last30Days.map(d => d?.avg_profitable_trade_on_date || 0),
      dailyAvgLoss: last30Days.map(d => Math.abs(d?.avg_losing_trade_on_date || 0)),
      profitToDate: last30Days.map(d => d?.profit_to_date || 0),  // Добавлено поле
      totalProfitToday: data.last?.profit_to_date || 0,
      tradeCount: data.last?.trades_to_date || 0,
      winRate: data.last?.dynamic_win_rate || 0,
      sharpeRatio: 0,
      maxDrawdown: data.last?.max_drawdown_to_date || 0,
      avgProfitableTrade: data.last?.avg_profitable_trade_to_date || 0,
      avgLosingTrade: Math.abs(data.last?.avg_losing_trade_to_date || 0),
      profitabilityDynamic: data.last?.profitability_to_date || 0,
      annualProfitability: data.last?.annual_365_profitability_to_date || 0,
    })
  }
  
  return result
})

// Выбранная стратегия
const selectedStrategy = computed(() => {
  if (strategies.value.length === 0) return null
  if (selectedStrategyId.value) {
    return strategies.value.find(s => s.id === selectedStrategyId.value) || strategies.value[0]
  }
  return strategies.value[0]
})

// Форматирование даты для отображения
const formatLastUpdate = computed(() => {
  if (!strategiesData.value?.last_update) return null
  const date = new Date(strategiesData.value.last_update)
  if (isNaN(date.getTime())) return null
  return date.toLocaleString()
})

// Функция для получения статистики стратегий
const fetchStrategiesStats = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await fetch('http://localhost:8020/strategies/stats')
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    
    console.log('Response structure:', {
      hasStrategies: !!data.strategies,
      strategiesKeys: data.strategies ? Object.keys(data.strategies) : [],
      firstStrategy: data.strategies ? data.strategies[Object.keys(data.strategies)[0]] : null
    })
    
    strategiesData.value = data
    
    if (strategies.value.length > 0 && !selectedStrategyId.value) {
      selectedStrategyId.value = strategies.value[0].id
    }
    
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Ошибка загрузки данных стратегий'
    console.error('Ошибка при загрузке стратегий:', err)
  } finally {
    isLoading.value = false
  }
}

// Функция для получения сигналов
const fetchSignals = async () => {
  signalsLoading.value = true
  signalsError.value = null
  
  try {
    const response = await fetch('http://localhost:8020/signals')
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    
    signals.value = data.map((signal: any) => ({
      ...signal,
      // timestamp: new Date(signal.timestamp)
      timestamp: new Date(signal.timestamp)  // ✅ Гарантируем, что это Date
    }))
    
  } catch (err) {
    signalsError.value = err instanceof Error ? err.message : 'Ошибка загрузки сигналов'
    console.error('Ошибка при загрузке сигналов:', err)
  } finally {
    signalsLoading.value = false
  }
}

// Обработчик создания новой стратегии
const handleStrategyGenerated = (newStrategy: any) => {
  fetchStrategiesStats()
}

// Автообновление
let intervalId: ReturnType<typeof setInterval> | null = null

const startAutoUpdate = () => {
  intervalId = setInterval(() => {
    fetchSignals()
  }, 30000)
}

const stopAutoUpdate = () => {
  if (intervalId) {
    clearInterval(intervalId)
    intervalId = null
  }
}

onMounted(() => {
  fetchStrategiesInfo()
  fetchStrategiesStats()
  fetchSignals()
  startAutoUpdate()
})

onUnmounted(() => {
  stopAutoUpdate()
})
</script>

<template>
  <div class="min-h-screen bg-white font-apple">
    <header class="border-b border-gray-200 bg-white">
      <div class="mx-auto max-w-7xl px-6 py-6">
        <div class="flex items-center justify-between">
          <h1 class="text-3xl font-semibold text-black">IntelliTrade AI</h1>
          <div class="text-sm text-gray-500">
            <span v-if="formatLastUpdate" class="mr-3">
              Updated: {{ formatLastUpdate }}
            </span>
            <button 
              @click="fetchStrategiesStats" 
              :disabled="isLoading"
              class="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded disabled:opacity-50"
            >
              {{ isLoading ? '...' : '⟳' }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-7xl px-6 py-8">
      <div v-if="isLoading && !strategiesData" class="mb-8 text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <p class="mt-2 text-gray-500">Loading strategies...</p>
      </div>

      <div v-else-if="error" class="mb-8 text-center py-12 text-red-500">
        <p>Error: {{ error }}</p>
        <button 
          @click="fetchStrategiesStats" 
          class="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Try Again
        </button>
      </div>

      <template v-else>
        <div class="mb-8 grid grid-cols-2 gap-8">
          <StrategyForm @strategy-generated="handleStrategyGenerated" />
          <SignalsPanel 
            :signals="signals" 
            :loading="signalsLoading"
            :error="signalsError"
          />
        </div>

        <div class="mb-8">
          <StrategyStats 
            v-if="strategies.length > 0"
            :strategies="strategies"
          />
          <div v-else-if="!isLoading" class="text-center py-12 text-gray-500">
            <p>No active strategies found</p>
          </div>
        </div>

        <div v-if="selectedStrategy">
          <StrategyChart 
            :key="selectedStrategy.id"
            :strategy="selectedStrategy"
            :strategies="strategies"
            :stats-data="strategiesData"
            @strategy-selected="selectedStrategyId = $event"
          />
        </div>
      </template>
    </main>
  </div>
</template>