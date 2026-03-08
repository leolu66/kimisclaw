// 单位列表页
const { showToast, showLoading, hideLoading, showConfirm } = require('../../utils/util')

Page({
  data: {
    units: [],
    keyword: ''
  },

  onLoad() { this.loadUnits() },
  onShow() { this.loadUnits() },

  async loadUnits() {
    try {
      const db = wx.cloud.database()
      let query = db.collection('units')
      if (this.data.keyword) {
        query = query.where({
          name: db.RegExp({ regexp: this.data.keyword, options: 'i' })
        })
      }
      const res = await query.orderBy('createdAt', 'desc').get()
      this.setData({ units: res.data })
    } catch (error) {
      showToast('加载失败')
    }
  },

  onSearchInput(e) { this.setData({ keyword: e.detail.value }) },
  onSearch() { this.loadUnits() },
  addUnit() { wx.navigateTo({ url: '/pages/admin/unit-edit' }) },
  editUnit(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/admin/unit-edit?id=${id}` })
  },

  async deleteUnit(e) {
    const { id } = e.currentTarget.dataset
    const confirmed = await showConfirm('确认删除', '删除后无法恢复')
    if (!confirmed) return

    showLoading('删除中...')
    try {
      await wx.cloud.database().collection('units').doc(id).remove()
      showToast('删除成功')
      this.loadUnits()
    } catch (error) {
      showToast('删除失败')
    } finally {
      hideLoading()
    }
  }
})