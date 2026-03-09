// 二维码展示页 - 全屏适合投影
const { callCloudFunction, showToast, showLoading, hideLoading } = require('../../utils/util')

Page({
  data: {
    taskId: '',
    task: null,
    qrCodeUrl: '',
    showActions: true,
    isFullScreen: false
  },

  onLoad(options) {
    const { taskId, from } = options
    
    this.setData({ 
      taskId,
      showActions: from !== 'projection'
    })

    if (taskId) {
      this.loadTaskDetail(taskId)
    }
  },

  // 加载任务详情
  async loadTaskDetail(taskId) {
    showLoading('加载中...')

    try {
      const result = await callCloudFunction('getTaskDetail', { taskId })
      const task = result.data

      // 如果没有二维码，生成一个
      if (!task.qrCodeUrl) {
        await this.generateQRCode(taskId, task.unitId)
      } else {
        this.setData({
          task,
          qrCodeUrl: task.qrCodeUrl
        })
      }
    } catch (error) {
      console.error('加载失败:', error)
      showToast('加载失败')
    } finally {
      hideLoading()
    }
  },

  // 生成二维码
  async generateQRCode(taskId, unitId) {
    try {
      const result = await callCloudFunction('generateQRCode', {
        taskId,
        unitId
      })

      this.setData({
        'task.qrCodeUrl': result.data.qrCodeUrl,
        qrCodeUrl: result.data.qrCodeUrl
      })
    } catch (error) {
      console.error('生成二维码失败:', error)
      showToast('生成二维码失败')
    }
  },

  // 保存二维码到相册
  async saveQRCode() {
    if (!this.data.qrCodeUrl) {
      showToast('二维码尚未加载')
      return
    }

    try {
      // 先下载图片到本地
      const downloadRes = await wx.downloadFile({
        url: this.data.qrCodeUrl
      })

      // 保存到相册
      await wx.saveImageToPhotosAlbum({
        filePath: downloadRes.tempFilePath
      })

      showToast('保存成功', 'success')
    } catch (error) {
      console.error('保存失败:', error)
      if (error.errMsg?.includes('auth')) {
        wx.showModal({
          title: '需要授权',
          content: '请允许保存图片到相册',
          success: (res) => {
            if (res.confirm) {
              wx.openSetting()
            }
          }
        })
      } else {
        showToast('保存失败')
      }
    }
  },

  // 分享二维码
  shareQRCode() {
    wx.showShareMenu({
      withShareTicket: true
    })
  },

  // 切换全屏
  toggleFullScreen() {
    const isFullScreen = !this.data.isFullScreen
    this.setData({ isFullScreen, showActions: !isFullScreen })

    if (isFullScreen) {
      // 进入全屏模式
      wx.setNavigationBarColor({
        frontColor: '#ffffff',
        backgroundColor: '#000000'
      })
    } else {
      // 退出全屏模式
      wx.setNavigationBarColor({
        frontColor: '#000000',
        backgroundColor: '#ffffff'
      })
    }
  },

  onShareAppMessage() {
    return {
      title: `${this.data.task?.title || '培训报名'} - 扫码报名`,
      path: `/pages/student/register?taskId=${this.data.taskId}&unitId=${this.data.task?.unitId}`
    }
  }
})