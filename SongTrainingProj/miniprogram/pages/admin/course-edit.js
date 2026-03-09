// 课程编辑页
const { showToast, showLoading, hideLoading } = require('../../utils/util')

Page({
  data: {
    courseId: '',
    isEdit: false,
    form: {
      name: '',
      duration: '',
      description: ''
    }
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ 
        courseId: options.id,
        isEdit: true 
      })
      this.loadCourseDetail(options.id)
    }
  },

  // 加载课程详情
  async loadCourseDetail(id) {
    showLoading('加载中...')
    
    try {
      const res = await wx.cloud.database().collection('courses').doc(id).get()
      const course = res.data
      
      this.setData({
        form: {
          name: course.name,
          duration: String(course.duration),
          description: course.description || ''
        }
      })
    } catch (error) {
      console.error('加载失败:', error)
      showToast('加载失败')
    } finally {
      hideLoading()
    }
  },

  // 输入处理
  onNameInput(e) {
    this.setData({ 'form.name': e.detail.value })
  },

  onDurationInput(e) {
    this.setData({ 'form.duration': e.detail.value })
  },

  onDescInput(e) {
    this.setData({ 'form.description': e.detail.value })
  },

  // 保存课程
  async saveCourse() {
    const { form, isEdit, courseId } = this.data

    // 表单验证
    if (!form.name.trim()) {
      showToast('请输入课程名称')
      return
    }

    if (!form.duration || form.duration <= 0) {
      showToast('请输入有效的课程时长')
      return
    }

    showLoading('保存中...')

    try {
      const db = wx.cloud.database()
      const data = {
        name: form.name.trim(),
        duration: parseInt(form.duration),
        description: form.description.trim(),
        updateAt: db.serverDate()
      }

      if (isEdit) {
        await db.collection('courses').doc(courseId).update({ data })
        showToast('修改成功', 'success')
      } else {
        data.createdAt = db.serverDate()
        await db.collection('courses').add({ data })
        showToast('创建成功', 'success')
      }

      setTimeout(() => {
        wx.navigateBack()
      }, 1500)

    } catch (error) {
      console.error('保存失败:', error)
      showToast('保存失败')
    } finally {
      hideLoading()
    }
  },

  // 取消
  cancel() {
    wx.navigateBack()
  }
})