// 管理员首页 - 数据看板
const { callCloudFunction, formatDate, showLoading, hideLoading } = require('../../utils/util')

Page({
  data: {
    pendingCount: 0,
    monthCount: 0,
    totalStudents: 0,
    totalCourses: 0,
    recentTasks: []
  },

  onLoad() {
    this.loadDashboardData()
  },

  onShow() {
    this.loadDashboardData()
  },

  onPullDownRefresh() {
    this.loadDashboardData().finally(() => {
      wx.stopPullDownRefresh()
    })
  },

  // 加载看板数据
  async loadDashboardData() {
    showLoading('加载中...')
    
    try {
      const db = wx.cloud.database()
      const _ = db.command
      
      // 获取当前时间
      const now = new Date()
      const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
      const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0)

      // 并行获取统计数据
      const [
        pendingRes,
        monthRes,
        studentsRes,
        coursesRes,
        recentRes
      ] = await Promise.all([
        // 待办任务数（状态为 planned）
        db.collection('tasks').where({
          status: 'planned',
          date: _.gte(now)
        }).count(),
        
        // 本月培训数
        db.collection('tasks').where({
          date: _.gte(startOfMonth).and(_.lte(endOfMonth))
        }).count(),
        
        // 累计学员数
        db.collection('users').count(),
        
        // 课程总数
        db.collection('courses').count(),
        
        // 近期培训（最近5条）
        db.collection('tasks')
          .orderBy('date', 'asc')
          .where({
            date: _.gte(now)
          })
          .limit(5)
          .get()
      ])

      // 处理近期培训数据
      const recentTasks = await Promise.all(
        recentRes.data.map(async (task) => {
          const [course, regCount] = await Promise.all([
            db.collection('courses').doc(task.courseId).get().catch(() => ({ data: { name: '未知' } })),
            db.collection('registrations').where({ taskId: task._id }).count()
          ])

          const date = new Date(task.date)
          const statusMap = {
            planned: { text: '未开始', class: 'planned' },
            ongoing: { text: '进行中', class: 'ongoing' },
            completed: { text: '已完成', class: 'completed' },
            cancelled: { text: '已取消', class: 'cancelled' }
          }

          return {
            ...task,
            day: date.getDate(),
            month: date.getMonth() + 1,
            courseName: course.data.name,
            registeredCount: regCount.total,
            statusText: statusMap[task.status]?.text || '未知',
            statusClass: statusMap[task.status]?.class || ''
          }
        })
      )

      this.setData({
        pendingCount: pendingRes.total,
        monthCount: monthRes.total,
        totalStudents: studentsRes.total,
        totalCourses: coursesRes.total,
        recentTasks
      })

    } catch (error) {
      console.error('加载数据失败:', error)
      wx.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      hideLoading()
    }
  },

  // 跳转到课程列表
  goToCourseList() {
    wx.navigateTo({ url: '/pages/admin/course-list' })
  },

  // 跳转到老师列表
  goToTeacherList() {
    wx.navigateTo({ url: '/pages/admin/teacher-list' })
  },

  // 跳转到单位列表
  goToUnitList() {
    wx.navigateTo({ url: '/pages/admin/unit-list' })
  },

  // 跳转到任务列表
  goToTaskList() {
    wx.navigateTo({ url: '/pages/admin/task-list' })
  },

  // 跳转到调查模板列表
  goToSurveyList() {
    wx.navigateTo({ url: '/pages/admin/survey-list' })
  },

  // 创建新任务
  createTask() {
    wx.navigateTo({ url: '/pages/admin/task-edit' })
  },

  // 查看任务详情
  viewTaskDetail(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/admin/task-detail?id=${id}` })
  }
})