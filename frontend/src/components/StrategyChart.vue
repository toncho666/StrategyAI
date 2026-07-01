<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Strategy {
  id: string
  name: string
  description: string
  timeframe: 'h1' | 'h4' | 'd1'
  asset: string
  created: Date
  monthlyProfitability: number[]
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

interface DailyMetric {
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

interface StrategiesStatsResponse {
  strategies: {
    [key: string]: {
      hist: DailyMetric[]
      last: DailyMetric | null
    }
  }
}

const props = defineProps<{
  strategy: Strategy
  strategies: Strategy[]
  statsData?: StrategiesStatsResponse | null
}>()

const emit = defineEmits<{
  'strategy-selected': [strategyId: string]
}>()

const selectedStrategyId = ref(props.strategy.id)
const selectedMetric = ref<'profit' | 'profitability' | 'annual252' | 'annual365' | 'trades' | 'winRate' | 'avgProfit' | 'avgLoss' | 'maxDrawdown'>('profitability')

const handleStrategyChange = (newId: string) => {
  selectedStrategyId.value = newId
  emit('strategy-selected', newId)
}

// Получаем данные для текущей стратегии из ответа эндпоинта
const currentStrategyData = computed(() => {
  if (!props.statsData?.strategies) {
    return null
  }
  
  const strategyName = props.strategy.name
  return props.statsData.strategies[strategyName] || null
})

// Получаем исторические данные для графика
const chartData = computed(() => {
  const data = currentStrategyData.value
  if (!data?.hist) {
    return []
  }
  
  const hist = data.hist
  if (!Array.isArray(hist) || hist.length === 0) {
    return []
  }
  
  const result = hist.map((metric) => {
    let value = 0
    switch (selectedMetric.value) {
      case 'profit':
        value = metric.profit_to_date || 0
        break
      case 'profitability':
        value = metric.profitability_to_date || 0
        break
      case 'annual252':
        value = metric.annual_252_profitability_to_date || 0
        break
      case 'annual365':
        value = metric.annual_365_profitability_to_date || 0
        break
      case 'trades':
        value = metric.trades_to_date || 0
        break
      case 'winRate':
        value = metric.dynamic_win_rate || 0
        break
      case 'avgProfit':
        value = metric.avg_profitable_trade_to_date || 0
        break
      case 'avgLoss':
        value = metric.avg_losing_trade_to_date || 0
        break
      case 'maxDrawdown':
        value = metric.max_drawdown_to_date || 0
        break
    }
    return {
      dt: metric.dt || '',
      value: value,
      raw: metric
    }
  })
  
  return result
})

// Последние данные
const lastData = computed(() => {
  return currentStrategyData.value?.last || null
})

// Вычисляем последнее значение для отображения в статистике
const lastValue = computed(() => {
  if (chartData.value.length === 0) return 0
  return chartData.value[chartData.value.length - 1].value
})

// Последнее значение "on date"
const lastOnDateValue = computed(() => {
  if (!lastData.value) return 0
  switch (selectedMetric.value) {
    case 'profit':
      return lastData.value.profit_on_date || 0
    case 'profitability':
      return lastData.value.profitability_on_date || 0
    case 'trades':
      return lastData.value.trades_on_date || 0
    case 'winRate':
      return lastData.value.dynamic_win_rate || 0
    case 'avgProfit':
      return lastData.value.avg_profitable_trade_on_date || 0
    case 'avgLoss':
      return lastData.value.avg_losing_trade_on_date || 0
    case 'maxDrawdown':
      return lastData.value.max_drawdown_on_date || 0
    default:
      return 0
  }
})

// Вычисляем максимальное и минимальное значение с отступами
const maxValue = computed(() => {
  if (chartData.value.length === 0) return 100
  
  const values = chartData.value.map(d => d.value)
  const max = Math.max(...values)
  const min = Math.min(...values)
  
  // Если все значения равны 0, возвращаем 100 для нормального отображения
  if (max === 0 && min === 0) return 100
  
  // Добавляем 20% отступа сверху для лучшей визуализации
  const padding = Math.abs(max) * 0.2
  return max + padding
})

const minValue = computed(() => {
  if (chartData.value.length === 0) return 0
  
  const values = chartData.value.map(d => d.value)
  const min = Math.min(...values)
  const max = Math.max(...values)
  
  // Если все значения равны 0, возвращаем 0
  if (min === 0 && max === 0) return 0
  
  // Добавляем 20% отступа снизу для отрицательных значений
  const padding = Math.abs(min) * 0.2
  return min - padding
})

const range = computed(() => {
  const r = maxValue.value - minValue.value
  return r === 0 ? 1 : r
})

// Функция для расчета высоты столбца
const getChartHeight = (value: number) => {
  if (chartData.value.length === 0) return 0
  
  // Если все значения равны 0, возвращаем минимальную высоту
  if (maxValue.value === 0 && minValue.value === 0) {
    return 1
  }
  
  const height = ((value - minValue.value) / range.value) * 100
  
  // Если значение очень маленькое, но не нулевое, показываем минимальную высоту
  if (value !== 0 && height < 1) {
    return 2
  }
  
  return Math.max(height, 0.5)
}

// Функция для получения меток оси Y (сверху вниз: от максимума к минимуму)
const getYAxisLabels = () => {
  if (chartData.value.length === 0) return []
  
  const labels = []
  const numLabels = 5
  
  for (let i = 0; i <= numLabels; i++) {
    const ratio = 1 - (i / numLabels)
    const value = minValue.value + (range.value * ratio)
    labels.push({
      value: value,
      label: value.toFixed(2)
    })
  }
  
  return labels
}

// Безопасное форматирование даты
const safeParseDate = (dateStr: string): Date | null => {
  if (!dateStr) return null
  try {
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) {
      return null
    }
    return date
  } catch (e) {
    return null
  }
}

const getDayLabel = (index: number) => {
  const data = chartData.value
  if (!data || data.length === 0 || index >= data.length) return ''
  
  const dt = data[index]?.dt
  if (!dt) return ''
  
  const date = safeParseDate(dt)
  if (!date) return ''
  
  const totalDays = data.length
  const interval = totalDays <= 30 ? 3 : totalDays <= 60 ? 6 : 10
  
  if (index % interval === 0) {
    const daysAgo = totalDays - index
    if (daysAgo <= 7) {
      const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
      return dayNames[date.getDay()]
    } else if (daysAgo <= 60) {
      return `${Math.floor(daysAgo / 7)}w`
    } else {
      return `${Math.floor(daysAgo / 30)}m`
    }
  }
  return ''
}

// Полная подпись для оси X
const getFullDayLabel = (index: number) => {
  const data = chartData.value
  if (!data || data.length === 0 || index >= data.length) return ''
  
  const dt = data[index]?.dt
  if (!dt) return ''
  
  const date = safeParseDate(dt)
  if (!date) return dt
  
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const chartLabel = computed(() => {
  switch (selectedMetric.value) {
    case 'profit':
      return 'Cumulative Profit'
    case 'profitability':
      return 'Cumulative Profitability'
    case 'annual252':
      return 'Annual Profitability (252 days)'
    case 'annual365':
      return 'Annual Profitability (365 days)'
    case 'trades':
      return 'Cumulative Trades'
    case 'winRate':
      return 'Win Rate Dynamics'
    case 'avgProfit':
      return 'Average Profitable Trade'
    case 'avgLoss':
      return 'Average Losing Trade'
    case 'maxDrawdown':
      return 'Maximum Drawdown'
    default:
      return 'Metric Dynamics'
  }
})

const getMetricUnit = () => {
  switch (selectedMetric.value) {
    case 'profit':
      return '$'
    case 'profitability':
      return '%'
    case 'annual252':
      return '%'
    case 'annual365':
      return '%'
    case 'trades':
      return ''
    case 'winRate':
      return '%'
    case 'avgProfit':
      return '$'
    case 'avgLoss':
      return '$'
    case 'maxDrawdown':
      return '%'
    default:
      return ''
  }
}

const getColor = (value: number) => {
  if (selectedMetric.value === 'trades') return '#007AFF'
  if (selectedMetric.value === 'winRate') return '#34C759'
  if (selectedMetric.value === 'maxDrawdown') return '#FF3B30'
  if (selectedMetric.value === 'avgProfit') return '#34C759'
  if (selectedMetric.value === 'avgLoss') return '#FF3B30'
  return value >= 0 ? '#34c759' : '#ff3b30'
}

// Показатели для статистики
const stats = computed(() => {
  if (chartData.value.length === 0) return null
  
  const values = chartData.value.map(d => d.value)
  const avg = values.reduce((a, b) => a + b, 0) / values.length
  
  return {
    current: lastValue.value,
    onDate: lastOnDateValue.value,
    max: Math.max(...values),
    min: Math.min(...values),
    avg: avg
  }
})

// Проверяем, загружены ли данные
const isLoading = computed(() => {
  if (!props.statsData) return true
  if (!props.statsData.strategies) return true
  if (!props.statsData.strategies[props.strategy.name]) return true
  return false
})

// Следим за изменением стратегии
watch(() => props.strategy.id, () => {
  selectedStrategyId.value = props.strategy.id
})
</script>

<template>
  <div class="rounded-lg border border-gray-200 bg-white p-8">
    <!-- Header with Strategy Selector and Metric Filter -->
    <div class="mb-8 flex items-center justify-between gap-6">
      <div>
        <h2 class="text-xl font-semibold text-black mb-1">Strategy Performance Chart</h2>
        <p class="text-sm text-gray-500">{{ chartLabel }}</p>
      </div>
      
      <div class="flex gap-4">
        <!-- Metric Selector -->
        <div>
          <label class="mb-2 block text-xs font-medium text-gray-500">Display Metric</label>
          <select
            v-model="selectedMetric"
            class="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm text-black focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="profit">Cumulative Profit</option>
            <option value="profitability">Cumulative Profitability</option>
            <option value="annual252">Annual Profitability (252)</option>
            <option value="annual365">Annual Profitability (365)</option>
            <option value="trades">Cumulative Trades</option>
            <option value="winRate">Win Rate Dynamics</option>
            <option value="avgProfit">Avg Profitable Trade</option>
            <option value="avgLoss">Avg Losing Trade</option>
            <option value="maxDrawdown">Max Drawdown</option>
          </select>
        </div>

        <!-- Strategy Selector -->
        <div>
          <label class="mb-2 block text-xs font-medium text-gray-500">Strategy</label>
          <select
            :value="selectedStrategyId"
            @change="handleStrategyChange(($event.target as HTMLSelectElement).value)"
            class="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm text-black focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option v-for="s in strategies" :key="s.id" :value="s.id">
              {{ s.name }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-500 border-r-transparent"></div>
        <p class="mt-4 text-sm text-gray-500">Loading strategy data...</p>
      </div>
    </div>

    <!-- Data Display -->
    <template v-else>
      <!-- Strategy Info Stats -->
      <div class="mb-8 grid grid-cols-6 gap-4">
        <div class="rounded-lg bg-gray-50 p-4">
          <div class="text-xs text-gray-500 mb-1">Current (To Date)</div>
          <div :class="['text-2xl font-semibold', selectedMetric === 'trades' || selectedMetric === 'winRate' ? 'text-black' : (lastValue >= 0 ? 'text-profit' : 'text-loss')]">
            {{ lastValue >= 0 && selectedMetric !== 'trades' ? '+' : '' }}{{ lastValue.toFixed(2) }}{{ getMetricUnit() }}
          </div>
        </div>

        <div class="rounded-lg bg-gray-50 p-4">
          <div class="text-xs text-gray-500 mb-1">On Date</div>
          <div :class="['text-2xl font-semibold', selectedMetric === 'trades' || selectedMetric === 'winRate' ? 'text-black' : (lastOnDateValue >= 0 ? 'text-profit' : 'text-loss')]">
            {{ lastOnDateValue >= 0 && selectedMetric !== 'trades' ? '+' : '' }}{{ lastOnDateValue.toFixed(2) }}{{ getMetricUnit() }}
          </div>
        </div>

        <div class="rounded-lg bg-gray-50 p-4">
          <div class="text-xs text-gray-500 mb-1">Chart Best</div>
          <div class="text-2xl font-semibold text-profit">
            {{ stats?.max.toFixed(2) || 0 }}{{ getMetricUnit() }}
          </div>
        </div>

        <div class="rounded-lg bg-gray-50 p-4">
          <div class="text-xs text-gray-500 mb-1">Chart Worst</div>
          <div class="text-2xl font-semibold text-loss">
            {{ stats?.min.toFixed(2) || 0 }}{{ getMetricUnit() }}
          </div>
        </div>

        <div class="rounded-lg bg-gray-50 p-4">
          <div class="text-xs text-gray-500 mb-1">Chart Average</div>
          <div class="text-2xl font-semibold text-black">
            {{ stats?.avg.toFixed(2) || 0 }}{{ getMetricUnit() }}
          </div>
        </div>

        <div class="rounded-lg bg-gray-50 p-4">
          <div class="text-xs text-gray-500 mb-1">Data Points</div>
          <div class="text-2xl font-semibold text-black">
            {{ chartData.length }}
          </div>
        </div>
      </div>

      <!-- Daily Chart -->
      <div class="rounded-lg bg-gray-50 p-8 mb-8">
        <div v-if="chartData.length === 0" class="flex items-center justify-center h-80">
          <p class="text-gray-500">No data available for this strategy</p>
        </div>
        <template v-else>
          <div class="flex">
            <!-- Y-axis Labels -->
            <div class="flex flex-col justify-between pr-4 py-2 h-80" style="min-width: 70px;">
              <div 
                v-for="label in getYAxisLabels()" 
                :key="label.value" 
                class="text-xs text-gray-500 text-right leading-none"
                style="height: 20%; display: flex; align-items: center; justify-content: flex-end;"
              >
                {{ label.label }}{{ getMetricUnit() }}
              </div>
            </div>
            
            <!-- Chart Area -->
            <div class="flex-1">
              <div class="flex items-end justify-between gap-0.5 h-80">
                <div
                  v-for="(item, index) in chartData"
                  :key="index"
                  class="flex flex-1 flex-col items-center gap-1 relative group"
                  :style="{
                    height: '100%',
                  }"
                >
                  <div class="flex items-end justify-center w-full h-full relative">
                    <div
                      class="w-full rounded-t transition-all duration-200 hover:opacity-80 cursor-pointer"
                      :style="{
                        height: `${getChartHeight(item.value)}%`,
                        backgroundColor: getColor(item.value),
                        minHeight: item.value !== 0 ? '3px' : '0px',
                      }"
                      :title="`${item.dt}: ${item.value.toFixed(4)}${getMetricUnit()}`"
                    />
                  </div>

                  <div v-if="getFullDayLabel(index)" class="invisible group-hover:visible absolute bottom-full mb-2 bg-black text-white text-xs rounded px-2 py-1 whitespace-nowrap z-10">
                    {{ getFullDayLabel(index) }}: {{ item.value.toFixed(4) }}{{ getMetricUnit() }}
                  </div>
                </div>
              </div>

              <!-- X-axis Labels -->
              <div class="flex items-start justify-between gap-0.5 mt-2 px-1 h-8">
                <div
                  v-for="(item, index) in chartData"
                  :key="`label-${index}`"
                  class="flex flex-1 justify-center text-xs text-gray-400 leading-none"
                >
                  {{ getDayLabel(index) }}
                </div>
              </div>
            </div>
          </div>

          <!-- Y-axis Labels Bottom -->
          <div class="mt-6 flex items-end justify-between" style="padding-left: 70px;">
            <div class="text-xs text-gray-500">
              Min: {{ minValue.toFixed(4) }}{{ getMetricUnit() }}
            </div>
            <div class="text-xs text-gray-500">
              Avg: {{ (chartData.reduce((a, b) => a + b.value, 0) / chartData.length).toFixed(4) }}{{ getMetricUnit() }}
            </div>
            <div class="text-xs text-gray-500">
              Max: {{ maxValue.toFixed(4) }}{{ getMetricUnit() }}
            </div>
          </div>
        </template>
      </div>

      <!-- Description -->
      <div class="rounded-lg border border-gray-200 bg-white p-4">
        <div class="text-xs text-gray-500 mb-2 font-medium">Strategy Description</div>
        <p class="text-sm text-gray-700">{{ strategy.description }}</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.text-profit {
  color: #34c759;
}
.text-loss {
  color: #ff3b30;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>