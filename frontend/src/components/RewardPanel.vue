<template>
  <div class="reward-panel">
    <div class="panel-section">
      <h3 class="section-title">
        <el-icon><Money /></el-icon>
        打赏支持
      </h3>
      <div class="description">
        <p>感谢您对本项目的支持！您的打赏将帮助我们持续改进和完善系统。</p>
      </div>

      <div v-if="!orderCreated && !paid" class="reward-form">
        <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
          <el-form-item label="打赏金额" prop="amount">
            <div class="amount-selector">
              <el-button
                v-for="amount in presetAmounts"
                :key="amount"
                :type="form.amount === amount ? 'primary' : 'default'"
                @click="form.amount = amount"
                class="amount-btn"
              >
                ¥{{ amount }}
              </el-button>
              <el-input-number
                v-model="customAmount"
                :min="1"
                :max="10000"
                :precision="2"
                placeholder="自定义"
                class="custom-amount-input"
                @change="handleCustomAmountChange"
              />
            </div>
          </el-form-item>
          <el-form-item label="留言" prop="message">
            <el-input
              v-model="form.message"
              type="textarea"
              :rows="4"
              placeholder="可选：留下您的鼓励和建议..."
              :maxlength="500"
              show-word-limit
            />
          </el-form-item>
          <el-form-item label="联系方式" prop="contact">
            <el-input
              v-model="form.contact"
              placeholder="可选：邮箱、微信、QQ等"
              :maxlength="100"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="creating"
              @click="handleCreateOrder"
              :disabled="!form.amount || form.amount <= 0"
            >
              <el-icon><Money /></el-icon>
              创建订单
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div v-if="orderCreated && !paid" class="payment-section">
        <el-card class="order-card">
          <template #header>
            <div class="card-header">
              <span>订单信息</span>
              <el-tag :type="orderInfo.payment_status === 'paid' ? 'success' : 'warning'">
                {{ orderInfo.payment_status === 'paid' ? '已支付' : '待支付' }}
              </el-tag>
            </div>
          </template>
          <div class="order-info">
            <div class="info-item">
              <span class="label">订单号：</span>
              <span class="value">{{ orderInfo.order_id }}</span>
            </div>
            <div class="info-item">
              <span class="label">金额：</span>
              <span class="value amount">¥{{ orderInfo.amount }}</span>
            </div>
            <div v-if="orderInfo.message" class="info-item">
              <span class="label">留言：</span>
              <span class="value">{{ orderInfo.message }}</span>
            </div>
            <div class="info-item">
              <span class="label">创建时间：</span>
              <span class="value">{{ formatTime(orderInfo.created_at) }}</span>
            </div>
          </div>
          <div class="payment-actions">
            <el-button
              type="primary"
              size="large"
              :loading="paying"
              @click="handlePay"
            >
              <el-icon><CreditCard /></el-icon>
              模拟支付
            </el-button>
            <el-button @click="handleReset">取消</el-button>
          </div>
        </el-card>
      </div>

      <div v-if="paid" class="success-section">
        <el-result
          icon="success"
          title="支付成功"
          sub-title="感谢您的支持！我们会继续努力改进系统"
        >
          <template #extra>
            <div class="success-info">
              <div class="info-item">
                <span class="label">订单号：</span>
                <span class="value">{{ orderInfo.order_id }}</span>
              </div>
              <div class="info-item">
                <span class="label">支付金额：</span>
                <span class="value amount">¥{{ orderInfo.amount }}</span>
              </div>
              <div class="info-item">
                <span class="label">支付时间：</span>
                <span class="value">{{ orderInfo.paid_at ? formatTime(orderInfo.paid_at) : '-' }}</span>
              </div>
            </div>
            <el-button type="primary" @click="handleReset">继续打赏</el-button>
          </template>
        </el-result>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { Money, CreditCard } from '@element-plus/icons-vue';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { createRewardOrder, payReward, type RewardRequest, type RewardResponse } from '../api/feedback';

const formRef = ref<FormInstance>();
const creating = ref(false);
const paying = ref(false);
const orderCreated = ref(false);
const paid = ref(false);
const orderInfo = ref<RewardResponse | null>(null);

const presetAmounts = [5, 10, 20, 50, 100, 200];
const customAmount = ref<number | null>(null);

const form = reactive<RewardRequest>({
  amount: 0,
  message: '',
  contact: ''
});

const rules: FormRules = {
  amount: [
    { required: true, message: '请选择或输入打赏金额', trigger: 'blur' },
    { type: 'number', min: 1, max: 10000, message: '金额应在1-10000元之间', trigger: 'blur' }
  ]
};

const handleCustomAmountChange = (value: number | null) => {
  if (value !== null && value > 0) {
    form.amount = value;
  }
};

const handleCreateOrder = async () => {
  if (!formRef.value) return;
  
  try {
    await formRef.value.validate();
    
    if (!form.amount || form.amount <= 0) {
      ElMessage.warning('请选择或输入打赏金额');
      return;
    }
    
    creating.value = true;
    const result = await createRewardOrder(form);
    
    orderInfo.value = result;
    orderCreated.value = true;
    ElMessage.success('订单创建成功！');
    
  } catch (error: any) {
    if (error?.fields) {
      // 表单验证失败
      return;
    }
    console.error('创建订单失败:', error);
    ElMessage.error(error?.response?.data?.detail || error?.message || '创建订单失败，请稍后重试');
  } finally {
    creating.value = false;
  }
};

const handlePay = async () => {
  if (!orderInfo.value) return;
  
  try {
    paying.value = true;
    const result = await payReward(orderInfo.value.order_id);
    
    if (result.success && result.status === 'paid') {
      paid.value = true;
      ElMessage.success('支付成功！');
      
      // 更新订单信息
      if (orderInfo.value) {
        orderInfo.value.payment_status = 'paid';
        orderInfo.value.payment_method = 'simulate';
        orderInfo.value.paid_at = new Date().toISOString();
      }
    } else {
      ElMessage.error('支付失败，请稍后重试');
    }
    
  } catch (error: any) {
    console.error('支付失败:', error);
    ElMessage.error(error?.response?.data?.detail || error?.message || '支付失败，请稍后重试');
  } finally {
    paying.value = false;
  }
};

const handleReset = () => {
  orderCreated.value = false;
  paid.value = false;
  orderInfo.value = null;
  formRef.value?.resetFields();
  form.amount = 0;
  form.message = '';
  form.contact = '';
  customAmount.value = null;
};

const formatTime = (timeStr: string) => {
  if (!timeStr) return '-';
  try {
    const date = new Date(timeStr);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  } catch {
    return timeStr;
  }
};
</script>

<style scoped>
.reward-panel {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.panel-section {
  background: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.description {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 6px;
  color: #64748b;
  line-height: 1.6;
}

.description p {
  margin: 0;
}

.amount-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.amount-btn {
  min-width: 80px;
}

.custom-amount-input {
  width: 150px;
}

.order-card {
  margin-top: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-info {
  margin-bottom: 24px;
}

.info-item {
  display: flex;
  margin-bottom: 12px;
  line-height: 1.8;
}

.info-item .label {
  color: #64748b;
  min-width: 100px;
}

.info-item .value {
  color: #1e293b;
  font-weight: 500;
}

.info-item .value.amount {
  color: #f59e0b;
  font-size: 18px;
  font-weight: 600;
}

.payment-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.success-section {
  margin-top: 24px;
}

.success-info {
  margin: 24px 0;
  padding: 20px;
  background: #f8fafc;
  border-radius: 6px;
}

.success-info .info-item {
  margin-bottom: 8px;
}
</style>

