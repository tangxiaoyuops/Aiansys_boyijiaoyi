import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { commodityApi } from '@/api/commodity';
import type {
  AnalyzeRequest,
  StrategyRequest,
  BacktestRequest,
  AnalyzeResponse,
  StrategyResponse,
  BacktestResponse,
  StrategiesResponse,
  Strategy,
  BacktestResult
} from '@/api/commodity';

export const useCommodityStore = defineStore('commodity', () => {
  const form = ref({
    commodity: '',
    timeRange: { start: '', end: '' },
    strategyType: 'trend',
    userQuestion: '',
    enableBacktest: true,
    maxRounds: 2
  });

  const analysis = ref({
    loading: false,
    progress: 0,
    currentStep: '',
    elapsedTime: 0,
    estimatedTime: 0
  });

  const result = ref({
    marketOverview: null as any,
    fundamental: null as any,
    technical: null as any,
    strategies: [] as Strategy[],
    risk: null as any,
    backtest: null as any,
    report: ''
  });

  const strategies = ref([] as Strategy[]);
  const selectedStrategy = ref(null as Strategy | null);

  const ui = ref({
    activeTab: 'overview',
    showProgress: false,
    sidebarCollapsed: false
  });

  const commodityList = ref([
    '原油', '布伦特', 'WTI', '铜', '铝', '锌', '铅', '镍', '锡',
    '大豆', '豆粕', '豆油', '玉米', '小麦', '棉花', '白糖', '橡胶',
    '铁矿', '焦煤', '焦炭', '螺纹钢', '热卷',
    '甲醇', 'PTA', 'PP', 'PVC', '乙二醇', '尿素', '纯碱', '玻璃',
    '黄金', '白银',
    '原油产业链', '铜产业链', '大豆产业链', '钢铁产业链', '煤化工产业链'
  ]);

  const strategyTypes = ref([
    { value: 'trend', label: '趋势跟踪' },
    { value: 'arbitrage', label: '套利' },
    { value: 'hedge', label: '套期保值' },
    { value: 'event_driven', label: '事件驱动' }
  ]);

  const timeRangeOptions = ref([
    { value: 7, label: '最近7天' },
    { value: 30, label: '最近30天' },
    { value: 90, label: '最近90天' },
    { value: 'custom', label: '自定义' }
  ]);

  const isLoading = computed(() => analysis.value.loading);
  const hasResult = computed(() => {
    const hasReport = result.value.report && result.value.report.length > 0;
    console.log('[Store] hasResult计算:', hasReport, 'report长度:', result.value.report?.length);
    return hasReport;
  });
  const strategiesCount = computed(() => result.value.strategies.length);
  const backtestResultsCount = computed(() => result.value.backtest ? 1 : 0);

  const setForm = (newForm: Partial<typeof form.value>) => {
    Object.assign(form.value, newForm);
  };

  const resetForm = () => {
    form.value = {
      commodity: '',
      timeRange: { start: '', end: '' },
      strategyType: 'trend',
      userQuestion: '',
      enableBacktest: true,
      maxRounds: 2
    };
    result.value = {
      marketOverview: null,
      fundamental: null,
      technical: null,
      strategies: [],
      risk: null,
      backtest: null,
      report: ''
    };
    analysis.value = {
      loading: false,
      progress: 0,
      currentStep: '',
      elapsedTime: 0,
      estimatedTime: 0
    };
  };

  const saveForm = () => {
    localStorage.setItem('commodity_form', JSON.stringify(form.value));
  };

  const loadForm = () => {
    const saved = localStorage.getItem('commodity_form');
    if (saved) {
      form.value = JSON.parse(saved);
    }
  };

  const startAnalysis = async () => {
    try {
      console.log('[Store] 开始分析');
      console.log('[Store] 表单数据:', form.value);
      console.log('[Store] 选择的品种:', form.value.commodity);
      
      analysis.value.loading = true;
      analysis.value.progress = 0;
      analysis.value.currentStep = '正在初始化...';
      analysis.value.estimatedTime = form.value.maxRounds * 30;
      ui.value.showProgress = true;
      ui.value.activeTab = 'overview';

      const request: AnalyzeRequest = {
        commodity_or_chain: form.value.commodity,
        time_range: form.value.timeRange.start && form.value.timeRange.end 
          ? { start: form.value.timeRange.start, end: form.value.timeRange.end }
          : undefined,
        user_question: form.value.userQuestion || undefined,
        strategy_type: form.value.strategyType,
        enable_backtest: form.value.enableBacktest,
        max_rounds: form.value.maxRounds
      };

      const response = await commodityApi.analyze(request);

      console.log('[Store] API响应:', response);
      console.log('[Store] response.success:', response.success);
      console.log('[Store] response.data:', response.data);
      
      if (response.success && response.data) {
        const structured = response.data.structured || {};
        
        console.log('[Store] structured数据:', structured);
        console.log('[Store] 报告内容:', response.data.report);
        console.log('[Store] structured_output:', structured);
        console.log('[Store] strategy_signals:', structured.strategy_signals);
        console.log('[Store] technical_indicators:', structured.technical_indicators);
        
        result.value = {
          marketOverview: {
            commodity: structured.commodity_or_chain || '',
            timeRange: structured.time_range || undefined,
            marketState: structured.market_state || 'unknown',
            analysisTime: new Date().toLocaleString('zh-CN'),
            totalDuration: response.data.total_duration || 0,
            roundsUsed: response.data.rounds_used || 0,
            currentPrice: 0,
            priceChange: 0,
            volatility: 0,
            volume: 0
          },
          fundamental: structured.structured_analysis || null,
          technical: structured.technical_indicators || null,
          strategies: structured.strategy_signals || [],
          risk: structured.risk_metrics || null,
          backtest: structured.backtest_results?.[0] || null,
          report: response.data.report || ''
        };

        console.log('[Store] result.value设置后:', result.value);
        console.log('[Store] hasResult:', result.value.report !== '');
        console.log('[Store] strategies数量:', result.value.strategies.length);
        console.log('[Store] report长度:', result.value.report.length);

        analysis.value.progress = 100;
        analysis.value.currentStep = '分析完成';
      } else {
        console.error('[Store] API响应失败:', response);
        console.error('[Store] response.success:', response.success);
        console.error('[Store] response.data:', response.data);
      }
    } catch (error: any) {
      console.error('分析失败:', error);
      analysis.value.loading = false;
      throw error;
    } finally {
      analysis.value.loading = false;
    }
  };

  const cancelAnalysis = () => {
    analysis.value.loading = false;
    analysis.value.progress = 0;
    ui.value.showProgress = false;
  };

  const setResult = (newResult: any) => {
    result.value = newResult;
  };

  const clearResult = () => {
    result.value = {
      marketOverview: null,
      fundamental: null,
      technical: null,
      strategies: [],
      risk: null,
      backtest: null,
      report: ''
    };
  };

  const loadStrategies = async () => {
    try {
      const response = await commodityApi.listStrategies({
        commodity: form.value.commodity || undefined,
        strategy_type: form.value.strategyType || undefined,
        limit: 50
      });

      if (response.success && response.data) {
        strategies.value = response.data.strategies || [];
      }
    } catch (error: any) {
      console.error('加载策略失败:', error);
      throw error;
    }
  };

  const saveStrategy = async (strategy: Strategy) => {
    try {
      const response = await commodityApi.generateStrategy({
        commodity: strategy.commodity_id,
        strategy_type: strategy.strategy_type,
        parameters: strategy.indicators
      });

      if (response.success) {
        await loadStrategies();
      }
    } catch (error: any) {
      console.error('保存策略失败:', error);
      throw error;
    }
  };

  const deleteStrategy = async (id: string) => {
    try {
      strategies.value = strategies.value.filter(s => 
        `${s.commodity_id}_${s.direction}_${s.generated_at}` !== id
      );
    } catch (error: any) {
      console.error('删除策略失败:', error);
      throw error;
    }
  };

  const selectStrategy = (strategy: Strategy) => {
    selectedStrategy.value = strategy;
  };

  const setActiveTab = (tab: string) => {
    ui.value.activeTab = tab;
  };

  const toggleSidebar = () => {
    ui.value.sidebarCollapsed = !ui.value.sidebarCollapsed;
  };

  return {
    form,
    analysis,
    result,
    strategies,
    selectedStrategy,
    ui,
    commodityList,
    strategyTypes,
    timeRangeOptions,
    isLoading,
    hasResult,
    strategiesCount,
    backtestResultsCount,
    setForm,
    resetForm,
    saveForm,
    loadForm,
    startAnalysis,
    cancelAnalysis,
    setResult,
    clearResult,
    loadStrategies,
    saveStrategy,
    deleteStrategy,
    selectStrategy,
    setActiveTab,
    toggleSidebar
  };
});
