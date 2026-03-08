// 任务列表页
const { callCloudFunction, formatDate, showToast, showLoading, hideLoading } = require('../../utils/util')

Page({
  data: {
    tasks: [],
    keyword: '',
    status: '',
    page: 1,
    pageSize: 20,
    hasMore: true,
    isRefreshing: false,
    statusOptions: [
      { label: '全部状态', value: '' },
      { label: '未开始', value: 'planned' },
      { label: '进行中', value: 'ongoing' },
      { label: '已完成', value: 'completed' },
      { label: '已取消', value: 'cancelled' }
    ],
    currentStatusLabel: '全部状态'
  },

  onLoad() {
    this.loadTasks()
  },

  onShow() {
    this.loadTasks(true)
  },

  // 加载任务列表
  async loadTasks(reset = false) {
    if (reset) {
      this.setData({ page: 1, tasks: [] })
    }

    const { page, pageSize, keyword, status } = this.data

    showLoading('加载中...')

    try {
      const result = await callCloudFunction('getTasks', {
        page,
        pageSize,
        keyword,
        status
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
        statusText: statusMap[item.status] || '未知',
        statusClass: item.status
      }))

      this.setData({
        tasks: reset ? tasks : [...this.data.tasks, ...tasks],
        hasMore: result.data.hasMore,
        isRefreshing: false
      })
    } catch (error) {
      console.error('加载失败:', error)
      showToast('加载失败')
    } finally {
      hideLoading()
    }
  },

  // 状态筛选
  onStatusChange(e) {
    const index = e.detail.value
    const option = this.data.statusOptions[index]
    this.setData({
      status: option.value,
      currentStatusLabel: option.label
    })
    this.loadTasks(true)
  },

  // 搜索
  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
    // 防抖搜索
    clearTimeout(this.searchTimer)
    this.searchTimer = setTimeout(() => {
      this.loadTasks(true)
    }, 500)
  },

  // 下拉刷新
  onRefresh() {
    this.setData({ isRefreshing: true })
    this.loadTasks(true)
  },

  // 加载更多
  loadMore() {
    if (!this.data.hasMore) return
    this.setData({ page: this.data.page + 1 })
    this.loadTasks()
  },

  // 创建任务
  createTask() {
    wx.navigateTo({ url: '/pages/admin/task-edit' })
  },

  // 查看详情
  viewTaskDetail(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/admin/task-detail?id=${id}` })
  },

  // 编辑任务
  editTask(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/admin/task-edit?id=${id}` })
    e.stopPropagation()
  },

  // 显示二维码
  showQRCode(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/teacher/qr-display?taskId=${id}&from=admin` })
    e.stopPropagation()
  },

  stopPropagation(e) {
    e.stopPropagation()
  }
})