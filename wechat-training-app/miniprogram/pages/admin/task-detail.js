// 任务详情页
const { callCloudFunction, formatDate, showToast, showLoading, hideLoading } = require('../../utils/util')

Page({
  data: {
    taskId: '',
    task: {}
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ taskId: options.id })
      this.loadTaskDetail()
    }
  },

  // 加载任务详情
  async loadTaskDetail() {
    showLoading('加载中...')
    
    try {
      const result = await callCloudFunction('getTaskDetail', {
        taskId: this.data.taskId,
        withRegistrations: true
      })

      const statusMap = {
        planned: '未开始',
        ongoing: '进行中',
        completed: '已完成',
        cancelled: '已取消'
      }

      const task = result.data
      task.statusText = statusMap[task.status] || '未知'
      task.date = formatDate(task.date, 'YYYY-MM-DD HH:mm')

      this.setData({ task })
    } catch (error) {
      console.error('加载失败:', error)
      showToast('加载失败')
    } finally {
      hideLoading()
    }
  },

  // 生成二维码
  async generateQRCode() {
    const { taskId, task } = this.data
    
    showLoading('生成中...')
    
    try {
      const result = await callCloudFunction('generateQRCode', {
        taskId,
        unitId: task.unitId
      })

      this.setData({
        'task.qrCodeUrl': result.data.qrCodeUrl
      })
      
      showToast('生成成功', 'success')
    } catch (error) {
      console.error('生成失败:', error)
      showToast('生成失败')
    } finally {
      hideLoading()
    }
  },

  // 编辑任务
  editTask() {
    wx.navigateTo({
      url: `/pages/admin/task-edit?id=${this.data.taskId}`
    })
  },

  // 显示二维码
  showQRCode() {
    wx.navigateTo({
      url: `/pages/teacher/qr-display?taskId=${this.data.taskId}&from=admin`
    })
  },

  // 查看调查统计
  viewSurveyStats() {
    const { taskId, task } = this.data
    if (!task.surveyTemplate) {
      showToast('未关联调查模板')
      return
    }
    
    wx.navigateTo({
      url: `/pages/admin/survey-stats?taskId=${taskId}&templateId=${task.surveyTemplate._id}`
    })
  }
})