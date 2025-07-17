<template>
  <div class="alert-info-page">
    <h1>告警中心</h1>

    <div class="alert-section control-section">
      <div class="filters">
        <label>
          状态过滤:
          <select v-model="filterStatus" @change="fetchAlerts(1)">
            <option value="">所有状态</option>
            <option value="unprocessed">未处理</option>
            <option value="viewed">已查看</option>
            <option value="resolved">已解决</option>
          </select>
        </label>
      </div>
      
      <div class="alerts-table-container">
        <table class="alerts-table">
          <thead>
            <tr>
              <th>快照/回放</th>
              <th>告警类型</th>
              <th>告警详情</th>
              <th>告警时间</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="alert in alerts" :key="alert.id" class="alert-row" :class="`status-${alert.status}`">
              <td class="alert-video">
                <img :src="getSnapshotUrl(alert.frame_snapshot_path)" 
                     alt="告警快照" 
                     class="alert-snapshot" 
                     @click="showSnapshotModal(getSnapshotUrl(alert.frame_snapshot_path))"
                     @error="onImageError"/>
                <button v-if="alert.video_path" @click="playVideo(alert.video_path)" class="play-button">
                  <i class="fa fa-play"></i> 回放
                </button>
              </td>
              <td>{{ alert.event_type }}</td>
              <td>{{ alert.details }}</td>
              <td>{{ new Date(alert.timestamp).toLocaleString() }}</td>
              <td>
                <span class="status-badge">{{ alert.status }}</span>
              </td>
              <td>
                <button @click="changeStatus(alert, 'viewed')" :disabled="alert.status === 'viewed' || alert.status === 'resolved'" class="handle-button">设为已读</button>
                <button @click="changeStatus(alert, 'resolved')" :disabled="alert.status === 'resolved'" class="handle-button">解决</button>
              </td>
            </tr>
            <tr v-if="!alerts.length" class="no-alert-row">
              <td colspan="6">
                <div class="video-placeholder">
                  <p>当前无告警信息</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="pagination-controls" v-if="totalPages > 1">
        <button @click="fetchAlerts(currentPage - 1)" :disabled="currentPage <= 1" class="page-button">
          上一页
        </button>
        <div class="page-numbers">
          <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
        </div>
        <button @click="fetchAlerts(currentPage + 1)" :disabled="currentPage >= totalPages" class="page-button">
          下一页
        </button>
      </div>
    </div>

    <!-- 快照放大模态框 -->
    <div v-if="snapshotModalVisible" class="snapshot-modal" @click="hideSnapshotModal">
      <div class="modal-content">
        <span class="close-button" @click="hideSnapshotModal">&times;</span>
        <img :src="modalSnapshotUrl" alt="告警快照放大" class="modal-image"/>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';
const SERVER_ROOT_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

const alerts = ref([]);
const currentPage = ref(1);
const totalPages = ref(1);
const filterStatus = ref('');
const snapshotModalVisible = ref(false);
const modalSnapshotUrl = ref('');

const fetchAlerts = async (page = 1) => {
  try {
    // 使用内存告警API
    const response = await fetch(`${API_BASE_URL}/alerts`);
    const data = await response.json();
    
    // 处理内存告警数据，现在应该是对象数组
    const memoryAlerts = (data.alerts || []).map((alert, index) => {
      // 如果是字符串，转换为对象格式
      if (typeof alert === 'string') {
        return {
          id: index + 1,
          event_type: "Memory Alert",
          details: alert,
          timestamp: new Date().toISOString(),
          status: "unprocessed",
          video_path: null,
          frame_snapshot_path: null
        };
      }
      // 如果已经是对象，直接使用
      return {
        id: alert.id || index + 1,
        event_type: alert.event_type || "Memory Alert",
        details: alert.details || alert.message || "未知告警",
        timestamp: alert.timestamp || new Date().toISOString(),
        status: alert.status || "unprocessed",
        video_path: alert.video_path || null,
        frame_snapshot_path: alert.snapshot_path || null
      };
    });
    
    alerts.value = memoryAlerts;
    currentPage.value = 1;
    totalPages.value = 1;
  } catch (error) {
    console.error('获取告警失败:', error);
    alerts.value = [];
  }
};

const changeStatus = async (alert, newStatus) => {
  // 内存告警系统不支持状态更新，只是在前端模拟
  const index = alerts.value.findIndex(a => a.id === alert.id);
  if (index !== -1) {
    alerts.value[index].status = newStatus;
  }
};

const getSnapshotUrl = (snapshotPath) => {
  if (!snapshotPath) {
    return 'https://via.placeholder.com/200x120?text=No+Snapshot';
  }
  return `${SERVER_ROOT_URL}${snapshotPath}`;
};

const onImageError = (event) => {
  event.target.src = 'https://via.placeholder.com/200x120?text=Error';
};

const playVideo = (videoPath) => {
  if (!videoPath) return;
  const videoUrl = `${SERVER_ROOT_URL}${videoPath}`;
  window.open(videoUrl, '_blank');
};

const showSnapshotModal = (url) => {
  modalSnapshotUrl.value = url;
  snapshotModalVisible.value = true;
};

const hideSnapshotModal = () => {
  snapshotModalVisible.value = false;
};

onMounted(() => {
  fetchAlerts(currentPage.value);
  // 每5秒刷新一次告警
  setInterval(() => {
    fetchAlerts(currentPage.value);
  }, 5000);
});
</script>

<style scoped>
/* 样式部分可以复用 AlertCenter.vue 的样式，或根据需要进行调整 */
.alert-info-page {
  padding: 2rem;
  font-family: sans-serif;
  max-width: 1400px;
  margin: 0 auto;
}
.filters {
  margin-bottom: 1rem;
}
.alerts-table {
  width: 100%;
  border-collapse: collapse;
}
.alerts-table th, .alerts-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}
.alerts-table th {
  background-color: #f2f2f2;
}
.alert-snapshot {
  width: 150px;
  height: auto;
  display: block;
  margin: 0 auto 5px;
  cursor: pointer; /* 添加指针手势，提示可以点击 */
}
.status-unprocessed {
  background-color: #fff3f3;
}
.status-viewed {
  background-color: #f3f9ff;
}
.status-resolved {
  background-color: #f3fff3;
}
.status-badge {
  padding: 0.2em 0.6em;
  border-radius: 0.8em;
  font-size: 0.8em;
  color: white;
  display: inline-block;
}
.status-unprocessed .status-badge { background-color: #f44336; }
.status-viewed .status-badge { background-color: #2196F3; }
.status-resolved .status-badge { background-color: #4CAF50; }

.handle-button {
  margin-right: 5px;
}
.pagination-controls {
  margin-top: 1rem;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

/* 快照模态框样式 */
.snapshot-modal {
  position: fixed;
  z-index: 1000;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0,0,0,0.8);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  position: relative;
  margin: auto;
  padding: 20px;
  background: #fff;
  border-radius: 5px;
  max-width: 90vw;
  max-height: 90vh;
}

.modal-image {
  max-width: 100%;
  max-height: calc(90vh - 60px); /* 留出一些空间给关闭按钮 */
  display: block;
}

.close-button {
  position: absolute;
  top: 10px;
  right: 25px;
  color: #f1f1f1;
  font-size: 40px;
  font-weight: bold;
  transition: 0.3s;
  cursor: pointer;
  }
  
.close-button:hover,
.close-button:focus {
  color: #bbb;
  text-decoration: none;
}
</style>