// 老师端 - 我的培训列表
const { callCloudFunction, formatDate, showToast, showLoading, hideLoading } = require('../../utils/util')

Page({
  data: {
    isLoggedIn: false,
    teacherId: '',
    tasks: []
  },

  onLoad() {
    this.checkLogin()
  },

  onShow() {
    if (this.data.isLoggedIn) {
      this.loadTasks()
    }
  },

  // 检查登录状态
  checkLogin() {
    const openid = wx.getStorageSync('openid')
    const userInfo = wx.getStorageSync('userInfo')
    
    if (openid && userInfo) {
      this.setData({ isLoggedIn: true })
      this.getTeacherId(openid)
    } else {
      this.setData({ isLoggedIn: false })
    }
  },

  // 获取老师ID
  async getTeacherId(openid) {
    try {
      // 这里假设有一个绑定关系，简化处理
      // 实际项目中应该有老师身份验证机制
      const db = wx.cloud.database()
      const res = await db.collection('teachers').limit(1).get()
      if (res.data.length > 0) {
        this.setData({ teacherId: res.data[0]._id })
        this.loadTasks()
      }
    } catch (error) {
      console.error('获取老师信息失败:', error)
    }
  },

  // 加载培训任务
  async loadTasks() {
    if (!this.data.teacherId) return

    showLoading('加载中...')

    try {
      const result = await callCloudFunction('getTasks', {
        teacherId: this.data.teacherId,
        page: 1,
        pageSize: 50
      })

      const statusMap = {
        planned: '未开始',
        ongoing: '进行中',
        completed: '已完成',
        cancelled: '已取消'
      }

      const tasks = result.data.list.map(item => ({
        ...item,
        date: formatDate(item.date, 'YYYY-MM-DD HH:mm'),
        statusText: statusMap[item.status] || '未知'
      }))

      this.setData({ tasks })
    } catch (error) {
      console.error('加载失败:', error)
      showToast('加载失败')
    } finally {
      hideLoading()
    }
  },

  // 去登录
  goToLogin() {
    wx.navigateTo({ url: '/pages/student/login' })
  },

  // 查看任务详情
  viewTaskDetail(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/admin/task-detail?id=${id}` })
  },

  // 显示二维码（全屏）
  showQRCode(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ 
      url: `/pages/teacher/qr-display?taskId=${id}&from=teacher`
    })
    e.stopPropagation()
  }
})