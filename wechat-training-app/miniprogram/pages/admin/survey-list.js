// 调查模板列表页
const { showToast, showLoading, hideLoading, showConfirm } = require('../../utils/util')

Page({
  data: {
    surveys: []
  },

  onLoad() { this.loadSurveys() },
  onShow() { this.loadSurveys() },

  async loadSurveys() {
    try {
      const db = wx.cloud.database()
      const res = await db.collection('survey_templates').orderBy('createdAt', 'desc').get()
      this.setData({ surveys: res.data })
    } catch (error) {
      showToast('加载失败')
    }
  },

  addSurvey() {
    wx.navigateTo({ url: '/pages/admin/survey-edit' })
  },

  editSurvey(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/admin/survey-edit?id=${id}` })
  },

  async deleteSurvey(e) {
    const { id } = e.currentTarget.dataset
    const confirmed = await showConfirm('确认删除', '删除后无法恢复')
    if (!confirmed) return

    showLoading('删除中...')
    try {
      await wx.cloud.database().collection('survey_templates').doc(id).remove()
      showToast('删除成功')
      this.loadSurveys()
    } catch (error) {
      showToast('删除失败')
    } finally {
      hideLoading()
    }
  }
})