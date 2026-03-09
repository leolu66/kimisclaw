// 课程列表页
const { formatDate, showToast, showLoading, hideLoading, showConfirm } = require('../../utils/util')

Page({
  data: {
    courses: [],
    keyword: '',
    page: 1,
    pageSize: 20,
    hasMore: true,
    isRefreshing: false
  },

  onLoad() {
    this.loadCourses()
  },

  onShow() {
    this.loadCourses()
  },

  // 加载课程列表
  async loadCourses(reset = false) {
    if (reset) {
      this.setData({ page: 1, courses: [] })
    }

    const { page, pageSize, keyword } = this.data

    try {
      const db = wx.cloud.database()
      let query = db.collection('courses')

      if (keyword) {
        query = query.where({
          name: db.RegExp({
            regexp: keyword,
            options: 'i'
          })
        })
      }

      const countRes = await query.count()
      const total = countRes.total

      const res = await query
        .orderBy('createdAt', 'desc')
        .skip((page - 1) * pageSize)
        .limit(pageSize)
        .get()

      const courses = res.data.map(item => ({
        ...item,
        createdAt: formatDate(item.createdAt, 'YYYY-MM-DD')
      }))

      this.setData({
        courses: reset ? courses : [...this.data.courses, ...courses],
        hasMore: this.data.courses.length + courses.length < total,
        isRefreshing: false
      })

    } catch (error) {
      console.error('加载课程失败:', error)
      showToast('加载失败')
      this.setData({ isRefreshing: false })
    }
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  // 搜索
  onSearch() {
    this.loadCourses(true)
  },

  // 下拉刷新
  onRefresh() {
    this.setData({ isRefreshing: true })
    this.loadCourses(true)
  },

  // 加载更多
  loadMore() {
    if (!this.data.hasMore) return
    this.setData({ page: this.data.page + 1 })
    this.loadCourses()
  },

  // 添加课程
  addCourse() {
    wx.navigateTo({ url: '/pages/admin/course-edit' })
  },

  // 编辑课程
  editCourse(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/admin/course-edit?id=${id}` })
  },

  // 删除课程
  async deleteCourse(e) {
    const { id } = e.currentTarget.dataset
    
    const confirmed = await showConfirm('确认删除', '删除后无法恢复，是否继续？')
    if (!confirmed) return

    showLoading('删除中...')

    try {
      await wx.cloud.database().collection('courses').doc(id).remove()
      showToast('删除成功', 'success')
      this.loadCourses(true)
    } catch (error) {
      console.error('删除失败:', error)
      showToast('删除失败')
    } finally {
      hideLoading()
    }
  }
})