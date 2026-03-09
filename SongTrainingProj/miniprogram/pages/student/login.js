// 学员登录页
const { isValidPhone, showToast, showLoading, hideLoading } = require('../../utils/util')
const app = getApp()

Page({
  data: {
    form: {
      phone: '',
      password: ''
    }
  },

  onLoad() {
    // 检查是否已登录
    const openid = wx.getStorageSync('openid')
    if (openid) {
      wx.switchTab({ url: '/pages/student/my-tasks' })
    }
  },

  onPhoneInput(e) {
    this.setData({ 'form.phone': e.detail.value })
  },

  onPasswordInput(e) {
    this.setData({ 'form.password': e.detail.value })
  },

  // 微信一键登录
  async wxLogin() {
    showLoading('登录中...')
    
    try {
      const openid = await app.wxLogin()
      
      // 检查用户是否存在
      const db = wx.cloud.database()
      const userRes = await db.collection('users').where({ openid }).get()
      
      if (userRes.data.length === 0) {
        hideLoading()
        wx.showModal({
          title: '提示',
          content: '您还未注册，请先扫码报名培训',
          showCancel: false,
          success: () => {
            wx.redirectTo({ url: '/pages/student/scan' })
          }
        })
        return
      }

      // 保存用户信息
      const user = userRes.data[0]
      wx.setStorageSync('userInfo', {
        name: user.name,
        phone: user.phone
      })

      hideLoading()
      showToast('登录成功', 'success')
      
      setTimeout(() => {
        wx.switchTab({ url: '/pages/student/my-tasks' })
      }, 1000)
      
    } catch (error) {
      console.error('登录失败:', error)
      hideLoading()
      showToast('登录失败')
    }
  },

  // 手机号登录
  async login() {
    const { phone, password } = this.data.form

    if (!isValidPhone(phone)) {
      showToast('请输入正确的手机号')
      return
    }
    if (!password) {
      showToast('请输入密码')
      return
    }

    showLoading('登录中...')

    try {
      const db = wx.cloud.database()
      const userRes = await db.collection('users').where({ phone }).get()
      
      if (userRes.data.length === 0) {
        hideLoading()
        showToast('用户不存在')
        return
      }

      const user = userRes.data[0]
      
      // 简单密码验证（实际项目应使用加密）
      if (user.password !== password) {
        hideLoading()
        showToast('密码错误')
        return
      }

      // 保存登录态
      wx.setStorageSync('openid', user.openid)
      wx.setStorageSync('userInfo', {
        name: user.name,
        phone: user.phone
      })
      app.globalData.openid = user.openid

      hideLoading()
      showToast('登录成功', 'success')
      
      setTimeout(() => {
        wx.switchTab({ url: '/pages/student/my-tasks' })
      }, 1000)
      
    } catch (error) {
      console.error('登录失败:', error)
      hideLoading()
      showToast('登录失败')
    }
  },

  goToScan() {
    wx.redirectTo({ url: '/pages/student/scan' })
  },

  goToRegister() {
    wx.redirectTo({ url: '/pages/student/scan' })
  }
})