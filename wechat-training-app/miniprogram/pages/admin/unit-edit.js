// 单位编辑页
const { showToast, showLoading, hideLoading } = require('../../utils/util')

Page({
  data: {
    unitId: '',
    isEdit: false,
    form: { name: '' }
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ unitId: options.id, isEdit: true })
      this.loadUnitDetail(options.id)
    }
  },

  async loadUnitDetail(id) {
    showLoading('加载中...')
    try {
      const res = await wx.cloud.database().collection('units').doc(id).get()
      this.setData({ form: { name: res.data.name } })
    } catch (error) {
      showToast('加载失败')
    } finally {
      hideLoading()
    }
  },

  onNameInput(e) {
    this.setData({ 'form.name': e.detail.value })
  },

  async saveUnit() {
    const { form, isEdit, unitId } = this.data

    if (!form.name.trim()) {
      showToast('请输入单位名称')
      return
    }

    showLoading('保存中...')

    try {
      const db = wx.cloud.database()
      const data = {
        name: form.name.trim(),
        updateAt: db.serverDate()
      }

      if (isEdit) {
        await db.collection('units').doc(unitId).update({ data })
        showToast('修改成功', 'success')
      } else {
        data.createdAt = db.serverDate()
        await db.collection('units').add({ data })
        showToast('创建成功', 'success')
      }

      setTimeout(() => wx.navigateBack(), 1500)
    } catch (error) {
      showToast('保存失败')
    } finally {
      hideLoading()
    }
  },

  cancel() {
    wx.navigateBack()
  }
})