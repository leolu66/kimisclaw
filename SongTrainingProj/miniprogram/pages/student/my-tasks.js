// 学员 - 我的培训列表
const { callCloudFunction, formatDate, showToast, showLoading, hideLoading } = require('../../utils/util')

Page({
  data: {
    isLoggedIn: false,
    userId: '',
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
    if (openid) {
      this.setData({ isLoggedIn: true })
      this.getUserInfo(openid)
    } else {
      this.setData({ isLoggedIn: false })
    }
  },

  // 获取用户信息
  async getUserInfo(openid) {
    try {
      const db = wx.cloud.database()
      const res = await db.collection('users').where({ openid }).get()
      if (res.data.length > 0) {
        this.setData({ userId: res.data[0]._id })
        this.loadTasks()
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  },

  // 加载培训列表
  async loadTasks() {
    const { userId } = this.data
    if (!userId) return

    showLoading('加载中...')

    try {
      const db = wx.cloud.database()
      const _ = db.command

      // 获取报名记录
      const regRes = await db.collection('registrations').where({
        userId
      }).orderBy('registeredAt', 'desc').get()

      if (regRes.data.length === 0) {
        this.setData({ tasks: [] })
        hideLoading()
        return
      }

      // 获取任务详情
      const tasks = await Promise.all(
        regRes.data.map(async (reg) => {
          const taskRes = await db.collection('tasks').doc(reg.taskId).get()
          const task = taskRes.data

          const [course, surveyRes] = await Promise.all([
            db.collection('courses').doc(task.courseId).get().catch(() => ({ data: { name: '未知' } })),
            db.collection('survey_responses').where({
              taskId: task._id,
              userId
            }).count()
          ])

          const statusMap = {
            planned: '未开始',
            ongoing: '进行中',
            completed: '已完成',
            cancelled: '已取消'
          }

          const regStatusMap = {
            registered: '已报名',
            cancelled: '已取消',
            completed: '已完成'
          }

          const canSurvey = task.status === 'completed' && reg.status === 'registered' && surveyRes.total === 0

          return {
            _id: task._id,
            title: task.title,
            date: formatDate(task.date, 'YYYY-MM-DD HH:mm'),
            location: task.location,
            courseName: course.data.name,
            status: task.status,
            statusText: statusMap[task.status] || '未知',
            regStatus: reg.status,
            regStatusText: regStatusMap[reg.status] || '未知',
            canSurvey,
            surveyTemplateId: task.surveyTemplateId
          }
        })
      )

      this.setData({ tasks })
    } catch (error) {
      console.error('加载失败:', error)
      showToast('加载失败')
    } finally {
      hideLoading()
    }
  },

  goToLogin() {
    wx.navigateTo({ url: '/pages/student/login' })
  },

  goToScan() {
    wx.navigateTo({ url: '/pages/student/scan' })
  },

  // 填写调查表
  goToSurvey(e) {
    const { id } = e.currentTarget.dataset
    const task = this.data.tasks.find(t => t._id === id)
    if (task && task.surveyTemplateId) {
      wx.navigateTo({
        url: `/pages/student/survey-fill?taskId=${id}&templateId=${task.surveyTemplateId}`
      })
    } else {
      showToast('暂无调查表')
    }
  }
})