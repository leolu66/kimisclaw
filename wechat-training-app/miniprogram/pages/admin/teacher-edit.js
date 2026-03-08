// 老师编辑页
const { showToast, showLoading, hideLoading } = require('../../utils/util')

Page({
  data: {
    teacherId: '',
    isEdit: false,
    form: {
      name: '',
      title: '',
      bio: '',
      avatar: ''
    }
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ teacherId: options.id, isEdit: true })
      this.loadTeacherDetail(options.id)
    }
  },

  async loadTeacherDetail(id) {
    showLoading('加载中...')
    try {
      const res = await wx.cloud.database().collection('teachers').doc(id).get()
      const teacher = res.data
      this.setData({
        form: {
          name: teacher.name,
          title: teacher.title || '',
          bio: teacher.bio || '',
          avatar: teacher.avatar || ''
        }
      })
    } catch (error) {
      showToast('加载失败')
    } finally {
      hideLoading()
    }
  },

  onNameInput(e) { this.setData({ 'form.name': e.detail.value }) },
  onTitleInput(e) { this.setData({ 'form.title': e.detail.value }) },
  onBioInput(e) { this.setData({ 'form.bio': e.detail.value }) },

  // 选择头像
  async chooseAvatar() {
    try {
      const res = await wx.chooseMedia({
        count: 1,
        mediaType: ['image'],
        sourceType: ['album', 'camera']
      })

      showLoading('上传中...')
      const tempFilePath = res.tempFiles[0].tempFilePath

      // 上传到云存储
      const cloudPath = `avatars/teacher_${Date.now()}.jpg`
      const uploadRes = await wx.cloud.uploadFile({
        cloudPath,
        filePath: tempFilePath
      })

      // 获取临时链接
      const fileRes = await wx.cloud.getTempFileURL({
        fileList: [uploadRes.fileID]
      })

      this.setData({ 'form.avatar': fileRes.fileList[0].tempFileURL })
      hideLoading()
    } catch (error) {
      console.error('上传失败:', error)
      showToast('上传失败')
      hideLoading()
    }
  },

  // 保存
  async saveTeacher() {
    const { form, isEdit, teacherId } = this.data

    if (!form.name.trim()) {
      showToast('请输入老师姓名')
      return
    }

    showLoading('保存中...')

    try {
      const db = wx.cloud.database()
      const data = {
        name: form.name.trim(),
        title: form.title.trim(),
        bio: form.bio.trim(),
        avatar: form.avatar,
        updateAt: db.serverDate()
      }

      if (isEdit) {
        await db.collection('teachers').doc(teacherId).update({ data })
        showToast('修改成功', 'success')
      } else {
        data.createdAt = db.serverDate()
        await db.collection('teachers').add({ data })
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