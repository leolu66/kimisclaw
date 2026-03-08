// 培训管理系统 - 全局应用配置
App({
  globalData: {
    userInfo: null,
    openid: null,
    userRole: null, // admin, teacher, student
    currentUnit: null,
    currentTask: null
  },

  onLaunch: function () {
    // 初始化云开发环境
    if (!wx.cloud) {
      console.error('请使用 2.2.3 或以上的基础库以使用云能力')
    } else {
      wx.cloud.init({
        env: 'your-env-id', // 请替换为实际的云开发环境ID
        traceUser: true
      })
    }

    // 检查本地存储的登录状态
    this.checkLoginStatus()
  },

  // 检查登录状态
  checkLoginStatus: function () {
    const userInfo = wx.getStorageSync('userInfo')
    const openid = wx.getStorageSync('openid')
    if (userInfo && openid) {
      this.globalData.userInfo = userInfo
      this.globalData.openid = openid
    }
  },

  // 微信登录获取openid
  wxLogin: function () {
    return new Promise((resolve, reject) => {
      wx.login({
        success: (res) => {
          if (res.code) {
            // 调用云函数获取openid
            wx.cloud.callFunction({
              name: 'login',
              data: { code: res.code }
            }).then(result => {
              const { openid } = result.result
              this.globalData.openid = openid
              wx.setStorageSync('openid', openid)
              resolve(openid)
            }).catch(err => {
              console.error('登录失败:', err)
              reject(err)
            })
          } else {
            reject(new Error('登录失败: ' + res.errMsg))
          }
        },
        fail: reject
      })
    })
  },

  // 获取用户信息
  getUserProfile: function () {
    return new Promise((resolve, reject) => {
      wx.getUserProfile({
        desc: '用于完善用户资料',
        success: (res) => {
          this.globalData.userInfo = res.userInfo
          wx.setStorageSync('userInfo', res.userInfo)
          resolve(res.userInfo)
        },
        fail: reject
      })
    })
  },

  // 全局错误处理
  onError: function (msg) {
    console.error('全局错误:', msg)
  }
})