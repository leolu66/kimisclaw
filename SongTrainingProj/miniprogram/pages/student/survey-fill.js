// 学员填写调查表
const { showToast, showLoading, hideLoading } = require('../../utils/util')

Page({
  data: {
    taskId: '',
    templateId: '',
    template: null,
    userId: '',
    answers: []
  },

  onLoad(options) {
    const { taskId, templateId } = options
    
    if (!taskId || !templateId) {
      wx.showModal({
        title: '提示',
        content: '参数错误',
        showCancel: false,
        success: () => wx.navigateBack()
      })
      return
    }

    this.setData({ taskId, templateId })
    this.getUserInfo()
    this.loadSurveyTemplate(templateId)
  },

  // 获取用户信息
  async getUserInfo() {
    const openid = wx.getStorageSync('openid')
    if (!openid) {
      wx.redirectTo({ url: '/pages/student/login' })
      return
    }

    try {
      const db = wx.cloud.database()
      const res = await db.collection('users').where({ openid }).get()
      if (res.data.length > 0) {
        this.setData({ userId: res.data[0]._id })
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  },

  // 加载调查模板
  async loadSurveyTemplate(templateId) {
    showLoading('加载中...')

    try {
      const db = wx.cloud.database()
      const res = await db.collection('survey_templates').doc(templateId).get()
      
      const template = res.data
      // 初始化答案数组
      const answers = template.questions.map(q => ({
        type: q.type,
        value: q.type === 'checkbox' ? [] : ''
      }))

      this.setData({
        template,
        answers
      })
    } catch (error) {
      console.error('加载失败:', error)
      showToast('加载失败')
    } finally {
      hideLoading()
    }
  },

  // 单选变化
  onRadioChange(e) {
    const index = e.currentTarget.dataset.index
    const value = e.detail.value
    const answers = this.data.answers
    answers[index].value = value
    this.setData({ answers })
  },

  // 多选变化
  onCheckboxChange(e) {
    const index = e.currentTarget.dataset.index
    const value = e.detail.value
    const answers = this.data.answers
    answers[index].value = value
    this.setData({ answers })
  },

  // 文本输入
  onTextInput(e) {
    const index = e.currentTarget.dataset.index
    const value = e.detail.value
    const answers = this.data.answers
    answers[index].value = value
    this.setData({ answers })
  },

  // 提交调查表
  async submitSurvey() {
    const { taskId, userId, templateId, answers, template } = this.data

    // 验证必填
    for (let i = 0; i < answers.length; i++) {
      const answer = answers[i]
      const question = template.questions[i]

      if (question.type === 'checkbox') {
        if (answer.value.length === 0) {
          showToast(`请回答第${i + 1}题`)
          return
        }
      } else {
        if (!answer.value) {
          showToast(`请回答第${i + 1}题`)
          return
        }
      }
    }

    showLoading('提交中...')

    try {
      const result = await wx.cloud.callFunction({
        name: 'submitSurvey',
        data: {
          taskId,
          userId,
          templateId,
          answers
        }
      })

      if (result.result.code === 0) {
        showToast('提交成功', 'success')
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      } else {
        showToast(result.result.message || '提交失败')
      }
    } catch (error) {
      console.error('提交失败:', error)
      showToast('提交失败，请重试')
    } finally {
      hideLoading()
    }
  }
})