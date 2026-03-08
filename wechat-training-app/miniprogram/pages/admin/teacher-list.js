// 老师列表页
const { showToast, showLoading, hideLoading, showConfirm } = require('../../utils/util')

Page({
  data: {
    teachers: [],
    keyword: ''
  },

  onLoad() {
    this.loadTeachers()
  },

  onShow() {
    this.loadTeachers()
  },

  // 加载老师列表
  async loadTeachers() {
    try {
      const db = wx.cloud.database()
      let query = db.collection('teachers')

      if (this.data.keyword) {
        query = query.where({
          name: db.RegExp({
            regexp: this.data.keyword,
            options: 'i'
          })
        })
      }

      const res = await query.orderBy('createdAt', 'desc').get()
      this.setData({ teachers: res.data })
    } catch (error) {
      showToast('加载失败')
    }
  },

  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  onSearch() {
    this.loadTeachers()
  },

  addTeacher() {
    wx.navigateTo({ url: '/pages/admin/teacher-edit' })
  },

  editTeacher(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/admin/teacher-edit?id=${id}` })
  },

  async deleteTeacher(e) {
    const { id } = e.currentTarget.dataset
    const confirmed = await showConfirm('确认删除', '删除后无法恢复')
    if (!confirmed) return

    showLoading('删除中...')
    try {
      await wx.cloud.database().collection('teachers').doc(id).remove()
      showToast('删除成功')
      this.loadTeachers()
    } catch (error) {
      showToast('删除失败')
    } finally {
      hideLoading()
    }
  }
})