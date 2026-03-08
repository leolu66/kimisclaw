// 调查模板编辑页
const { showToast, showLoading, hideLoading } = require('../../utils/util')

Page({
  data: {
    surveyId: '',
    isEdit: false,
    form: {
      name: '',
      questions: []
    }
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ surveyId: options.id, isEdit: true })
      this.loadSurveyDetail(options.id)
    }
  },

  // 加载模板详情
  async loadSurveyDetail(id) {
    showLoading('加载中...')
    try {
      const res = await wx.cloud.database().collection('survey_templates').doc(id).get()
      this.setData({
        form: {
          name: res.data.name,
          questions: res.data.questions || []
        }
      })
    } catch (error) {
      showToast('加载失败')
    } finally {
      hideLoading()
    }
  },

  // 输入处理
  onNameInput(e) {
    this.setData({ 'form.name': e.detail.value })
  },

  onQuestionTitleInput(e) {
    const index = e.currentTarget.dataset.index
    const value = e.detail.value
    const questions = this.data.form.questions
    questions[index].title = value
    this.setData({ 'form.questions': questions })
  },

  onOptionInput(e) {
    const qIndex = e.currentTarget.dataset.qindex
    const oIndex = e.currentTarget.dataset.oindex
    const value = e.detail.value
    const questions = this.data.form.questions
    questions[qIndex].options[oIndex] = value
    this.setData({ 'form.questions': questions })
  },

  // 添加题目
  addRadioQuestion() {
    const questions = this.data.form.questions
    questions.push({
      type: 'radio',
      title: '',
      options: ['选项1', '选项2']
    })
    this.setData({ 'form.questions': questions })
  },

  addCheckboxQuestion() {
    const questions = this.data.form.questions
    questions.push({
      type: 'checkbox',
      title: '',
      options: ['选项1', '选项2', '选项3']
    })
    this.setData({ 'form.questions': questions })
  },

  addTextQuestion() {
    const questions = this.data.form.questions
    questions.push({
      type: 'text',
      title: ''
    })
    this.setData({ 'form.questions': questions })
  },

  // 添加选项
  addOption(e) {
    const index = e.currentTarget.dataset.index
    const questions = this.data.form.questions
    questions[index].options.push(`选项${questions[index].options.length + 1}`)
    this.setData({ 'form.questions': questions })
  },

  // 删除选项
  deleteOption(e) {
    const qIndex = e.currentTarget.dataset.qindex
    const oIndex = e.currentTarget.dataset.oindex
    const questions = this.data.form.questions
    
    if (questions[qIndex].options.length <= 2) {
      showToast('至少需要2个选项')
      return
    }
    
    questions[qIndex].options.splice(oIndex, 1)
    this.setData({ 'form.questions': questions })
  },

  // 删除题目
  deleteQuestion(e) {
    const index = e.currentTarget.dataset.index
    const questions = this.data.form.questions
    questions.splice(index, 1)
    this.setData({ 'form.questions': questions })
  },

  // 保存模板
  async saveSurvey() {
    const { form, isEdit, surveyId } = this.data

    if (!form.name.trim()) {
      showToast('请输入模板名称')
      return
    }

    if (form.questions.length === 0) {
      showToast('请至少添加一道题目')
      return
    }

    // 验证题目
    for (let i = 0; i < form.questions.length; i++) {
      const q = form.questions[i]
      if (!q.title.trim()) {
        showToast(`题目 ${i + 1} 标题不能为空`)
        return
      }
      if (q.type !== 'text') {
        const validOptions = q.options.filter(opt => opt.trim())
        if (validOptions.length < 2) {
          showToast(`题目 ${i + 1} 至少需要2个有效选项`)
          return
        }
      }
    }

    showLoading('保存中...')

    try {
      const db = wx.cloud.database()
      const data = {
        name: form.name.trim(),
        questions: form.questions.map(q => ({
          type: q.type,
          title: q.title.trim(),
          options: q.type === 'text' ? [] : q.options.filter(opt => opt.trim())
        })),
        updateAt: db.serverDate()
      }

      if (isEdit) {
        await db.collection('survey_templates').doc(surveyId).update({ data })
        showToast('修改成功', 'success')
      } else {
        data.createdAt = db.serverDate()
        await db.collection('survey_templates').add({ data })
        showToast('创建成功', 'success')
      }

      setTimeout(() => wx.navigateBack(), 1500)
    } catch (error) {
      console.error('保存失败:', error)
      showToast('保存失败')
    } finally {
      hideLoading()
    }
  },

  cancel() {
    wx.navigateBack()
  }
})