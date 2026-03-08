// 学员扫码入口
Page({
  data: {},

  onLoad() {
    // 检查是否已有登录态
    const openid = wx.getStorageSync('openid')
    if (openid) {
      // 已登录，跳转到我的培训
      wx.switchTab({ url: '/pages/student/my-tasks' })
    }
  },

  // 扫码
  scanCode() {
    wx.scanCode({
      onlyFromCamera: true,
      scanType: ['qrCode'],
      success: (res) => {
        // 解析二维码内容
        const url = res.result
        
        // 如果是小程序码，解析 scene 参数
        if (url.includes('scene=')) {
          const scene = decodeURIComponent(url.split('scene=')[1])
          const params = this.parseScene(scene)
          this.navigateToRegister(params)
        } else if (url.includes('/pages/')) {
          // 直接是页面路径
          wx.navigateTo({ url: url.split('.com')[1] || url })
        } else {
          wx.showModal({
            title: '提示',
            content: '无法识别的二维码',
            showCancel: false
          })
        }
      },
      fail: (err) => {
        console.error('扫码失败:', err)
      }
    })
  },

  // 解析 scene 参数
  parseScene(scene) {
    const params = {}
    const pairs = scene.split('&')
    pairs.forEach(pair => {
      const [key, value] = pair.split('=')
      if (key && value) {
        params[key] = value
      }
    })
    return params
  },

  // 跳转到注册页
  navigateToRegister(params) {
    const { taskId, unitId } = params
    if (taskId && unitId) {
      wx.navigateTo({
        url: `/pages/student/register?taskId=${taskId}&unitId=${unitId}`
      })
    } else {
      wx.showModal({
        title: '提示',
        content: '二维码参数不完整',
        showCancel: false
      })
    }
  },

  // 去登录
  goToLogin() {
    wx.navigateTo({ url: '/pages/student/login' })
  }
})