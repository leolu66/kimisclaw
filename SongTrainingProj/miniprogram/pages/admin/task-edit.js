// 任务编辑页
const { formatDate, showToast, showLoading, hideLoading } = require('../../utils/util')

Page({
  data: {
    taskId: '',
    isEdit: false,
    courses: [],
    teachers: [],
    units: [],
    surveys: [],
    statusOptions: [
      { label: '未开始', value: 'planned' },
      { label: '进行中', value: 'ongoing' },
      { label: '已完成', value: 'completed' },
      { label: '已取消', value: 'cancelled' }
    ],
    form: {
      title: '',
      courseId: '',
      courseName: '',
      teacherId: '',
      teacherName: '',
      unitId: '',
      unitName: '',
      date: '',
      location: '',
      capacity: 50,
      surveyTemplateId: '',
      surveyName: '',
      status: 'planned',
      statusText: '未开始'
    },
    dateRange: [],
    dateIndex: [0, 0, 0, 0, 0]
  },

  onLoad(options) {
    this.initDateRange()
    this.loadBaseData()
    
    if (options.id) {
      this.setData({ taskId: options.id, isEdit: true })
      this.loadTaskDetail(options.id)
    }
  },

  // 初始化日期范围
  initDateRange() {
    const years = []
    const months = []
    const days = []
    const hours = []
    const minutes = []

    const currentYear = new Date().getFullYear()
    for (let i = currentYear; i <= currentYear + 2; i++) {
      years.push(i + '年')
    }
    for (let i = 1; i <= 12; i++) {
      months.push(i + '月')
    }
    for (let i = 1; i <= 31; i++) {
      days.push(i + '日')
    }
    for (let i = 0; i < 24; i++) {
      hours.push(String(i).padStart(2, '0') + '时')
    }
    for (let i = 0; i < 60; i += 5) {
      minutes.push(String(i).padStart(2, '0') + '分')
    }

    this.setData({ dateRange: [years, months, days, hours, minutes] })
  },

  // 加载基础数据
  async loadBaseData() {
    try {
      const db = wx.cloud.database()
      const [courses, teachers, units, surveys] = await Promise.all([
        db.collection('courses').get(),
        db.collection('teachers').get(),
        db.collection('units').get(),
        db.collection('survey_templates').get()
      ])

      this.setData({
        courses: courses.data,
        teachers: teachers.data,
        units: units.data,
        surveys: [{ _id: '', name: '不关联调查表' }, ...surveys.data]
      })
    } catch (error) {
      console.error('加载基础数据失败:', error)
    }
  },

  // 加载任务详情
  async loadTaskDetail(id) {
    showLoading('加载中...')
    try {
      const db = wx.cloud.database()
      const res = await db.collection('tasks').doc(id).get()
      const task = res.data

      const course = this.data.courses.find(c => c._id === task.courseId)
      const teacher = this.data.teachers.find(t => t._id === task.teacherId)
      const unit = this.data.units.find(u => u._id === task.unitId)
      const survey = this.data.surveys.find(s => s._id === task.surveyTemplateId)

      const statusMap = { planned: '未开始', ongoing: '进行中', completed: '已完成', cancelled: '已取消' }

      this.setData({
        form: {
          title: task.title,
          courseId: task.courseId,
          courseName: course?.name || '',
          teacherId: task.teacherId,
          teacherName: teacher?.name || '',
          unitId: task.unitId,
          unitName: unit?.name || '',
          date: formatDate(task.date, 'YYYY-MM-DD HH:mm'),
          location: task.location,
          capacity: task.capacity || 50,
          surveyTemplateId: task.surveyTemplateId || '',
          surveyName: survey?.name || '',
          status: task.status,
          statusText: statusMap[task.status] || '未开始'
        }
      })
    } catch (error) {
      showToast('加载失败')
    } finally {
      hideLoading()
    }
  },

  // 输入处理
  onTitleInput(e) { this.setData({ 'form.title': e.detail.value }) },
  onLocationInput(e) { this.setData({ 'form.location': e.detail.value }) },
  onCapacityInput(e) { this.setData({ 'form.capacity': e.detail.value }) },

  // 选择器处理
  onCourseChange(e) {
    const index = e.detail.value
    const course = this.data.courses[index]
    this.setData({
      'form.courseId': course._id,
      'form.courseName': course.name
    })
  },

  onTeacherChange(e) {
    const index = e.detail.value
    const teacher = this.data.teachers[index]
    this.setData({
      'form.teacherId': teacher._id,
      'form.teacherName': teacher.name
    })
  },

  onUnitChange(e) {
    const index = e.detail.value
    const unit = this.data.units[index]
    this.setData({
      'form.unitId': unit._id,
      'form.unitName': unit.name
    })
  },

  onSurveyChange(e) {
    const index = e.detail.value
    const survey = this.data.surveys[index]
    this.setData({
      'form.surveyTemplateId': survey._id,
      'form.surveyName': survey.name
    })
  },

  onStatusChange(e) {
    const index = e.detail.value
    const option = this.data.statusOptions[index]
    this.setData({
      'form.status': option.value,
      'form.statusText': option.label
    })
  },

  onDateChange(e) {
    const val = e.detail.value
    const year = parseInt(this.data.dateRange[0][val[0]])
    const month = parseInt(this.data.dateRange[1][val[1]])
    const day = parseInt(this.data.dateRange[2][val[2]])
    const hour = parseInt(this.data.dateRange[3][val[3]])
    const minute = parseInt(this.data.dateRange[4][val[4]])

    const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')} ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
    this.setData({
      'form.date': dateStr,
      dateIndex: val
    })
  },

  // 保存任务
  async saveTask() {
    const { form, isEdit, taskId } = this.data

    if (!form.title.trim()) { showToast('请输入培训标题'); return }
    if (!form.courseId) { showToast('请选择课程'); return }
    if (!form.teacherId) { showToast('请选择老师'); return }
    if (!form.unitId) { showToast('请选择单位'); return }
    if (!form.date) { showToast('请选择培训日期'); return }
    if (!form.location.trim()) { showToast('请输入培训地点'); return }

    showLoading('保存中...')

    try {
      const db = wx.cloud.database()
      const data = {
        title: form.title.trim(),
        courseId: form.courseId,
        teacherId: form.teacherId,
        unitId: form.unitId,
        date: new Date(form.date),
        location: form.location.trim(),
        capacity: parseInt(form.capacity) || 50,
        surveyTemplateId: form.surveyTemplateId || '',
        status: form.status,
        updateAt: db.serverDate()
      }

      if (isEdit) {
        await db.collection('tasks').doc(taskId).update({ data })
        showToast('修改成功', 'success')
      } else {
        data.createdAt = db.serverDate()
        await db.collection('tasks').add({ data })
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