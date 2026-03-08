// 学员注册页
const { isValidPhone, isValidEmail, showToast, showLoading, hideLoading } = require('../../utils/util')
const app = getApp()

Page({
  data: {
    taskId: '',
    unitId: '',
    unitName: '',
    task: null,
    hasUserInfo: false,
    userInfo: null,
    openid: '',
    form: {
      name: '',
      phone: '',
      email: '',
      wechatId: '',
      password: ''
    }
  },

  onLoad(options) {
    const { taskId, unitId } = options
    
    if (!taskId || !unitId) {
      wx.showModal({
        title: '提示',
        content: '缺少必要参数',
        showCancel: false,
        success: () => wx.navigateBack()
      })
      return
    }

    this.setData({ taskId, unitId })
    this.loadUnitInfo(unitId)
    this.loadTaskInfo(taskId)
    this.wxLogin()
  },

  // 微信登录
  async wxLogin() {
    try {
      const openid = await app.wxLogin()
      this.setData({ openid })

      // 检查用户是否已存在
      const db = wx.cloud.database()
      const userRes = await db.collection('users').where({ openid }).get()
      
      if (userRes.data.length > 0) {
        // 用户已存在，自动填写信息
        const user = userRes.data[0]
        this.setData({
          'form.name': user.name,
          'form.phone': user.phone,
          'form.email': user.email || '',
          'form.wechatId': user.wechatId || ''
        })

        // 检查是否已报名
        const regRes = await db.collection('registrations').where({
          taskId: this.data.taskId,
          userId: user._id
        }).get()

        if (regRes.data.length > 0) {
          wx.showModal({
            title: '提示',
            content: '您已报名该培训，是否查看详情？',
            showCancel: true,
            success: (res) => {
              if (res.confirm) {
                wx.navigateTo({ url: `/pages/student/my-tasks` })
              }
            }
          })
        }
      }
    } catch (error) {
      console.error('登录失败:', error)
    }
  },

  // 加载单位信息
  async loadUnitInfo(unitId) {
    try {
      const db = wx.cloud.database()
      const res = await db.collection('units').doc(unitId).get()
      this.setData({ unitName: res.data.name })
    } catch (error) {
      console.error('加载单位信息失败:', error)
    }
  },

  // 加载任务信息
  async loadTaskInfo(taskId) {
    try {
      const db = wx.cloud.database()
      const res = await db.collection('tasks').doc(taskId).get()
      this.setData({ task: res.data })
    } catch (error) {
      console.error('加载任务信息失败:', error)
    }
  },

  // 获取用户信息
  async getUserProfile() {
    try {
      const userInfo = await app.getUserProfile()
      this.setData({
        hasUserInfo: true,
        userInfo
      })
    } catch (error) {
      showToast('授权失败')
    }
  },

  // 输入处理
  onNameInput(e) { this.setData({ 'form.name': e.detail.value }) },
  onPhoneInput(e) { this.setData({ 'form.phone': e.detail.value }) },
  onEmailInput(e) { this.setData({ 'form.email': e.detail.value }) },
  onWechatIdInput(e) { this.setData({ 'form.wechatId': e.detail.value }) },
  onPasswordInput(e) { this.setData({ 'form.password': e.detail.value }) },

  // 提交注册
  async submitRegister() {
    const { form, openid, taskId, unitId, userInfo } = this.data

    // 验证
    if (!form.name.trim()) {
      showToast('请输入姓名')
      return
    }
    if (!isValidPhone(form.phone)) {
      showToast('请输入正确的手机号')
      return
    }
    if (form.email && !isValidEmail(form.email)) {
      showToast('请输入正确的邮箱')
      return
    }

    showLoading('提交中...')

    try {
      const result = await wx.cloud.callFunction({
        name: 'registerUser',
        data: {
          openid,
          name: form.name.trim(),
          phone: form.phone.trim(),
          email: form.email.trim(),
          wechatId: form.wechatId.trim(),
          password: form.password,
          taskId,
          unitId,
          avatarUrl: userInfo?.avatarUrl || ''
        }
      })

      if (result.result.code === 0 || result.result.code === 1) {
        showToast('报名成功', 'success')
        
        // 保存用户信息到本地
        wx.setStorageSync('userInfo', {
          name: form.name.trim(),
          phone: form.phone.trim()
        })

        setTimeout(() => {
          wx.switchTab({ url: '/pages/student/my-tasks' })
        }, 1500)
      } else {
        showToast(result.result.message || '报名失败')
      }
    } catch (error) {
      console.error('报名失败:', error)
      showToast('报名失败，请重试')
    } finally {
      hideLoading()
    }
  },

  goToLogin() {
    wx.navigateTo({ url: '/pages/student/login' })
  }
})