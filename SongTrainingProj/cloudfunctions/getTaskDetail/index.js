/**
 * 获取培训任务详情云函数
 */
const cloud = require('wx-server-sdk')

cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
})

const db = cloud.database()

exports.main = async (event, context) => {
  const { taskId, withRegistrations = false } = event

  try {
    if (!taskId) {
      return {
        code: -1,
        message: '任务ID不能为空'
      }
    }

    // 获取任务详情
    const taskResult = await db.collection('tasks').doc(taskId).get()
    
    if (!taskResult.data) {
      return {
        code: -1,
        message: '任务不存在'
      }
    }

    const task = taskResult.data

    // 获取关联信息
    const [course, teacher, unit, surveyTemplate] = await Promise.all([
      db.collection('courses').doc(task.courseId).get().catch(() => ({ data: null })),
      db.collection('teachers').doc(task.teacherId).get().catch(() => ({ data: null })),
      db.collection('units').doc(task.unitId).get().catch(() => ({ data: null })),
      task.surveyTemplateId 
        ? db.collection('survey_templates').doc(task.surveyTemplateId).get().catch(() => ({ data: null }))
        : Promise.resolve({ data: null })
    ])

    // 获取报名人数
    const regCount = await db.collection('registrations').where({
      taskId: taskId
    }).count()

    const result = {
      ...task,
      course: course.data,
      teacher: teacher.data,
      unit: unit.data,
      surveyTemplate: surveyTemplate.data,
      registeredCount: regCount.total
    }

    // 如果需要报名名单
    if (withRegistrations) {
      const registrations = await db.collection('registrations').where({
        taskId: taskId
      }).orderBy('registeredAt', 'desc').get()

      const userList = await Promise.all(
        registrations.data.map(async (reg) => {
          const user = await db.collection('users').doc(reg.userId).get().catch(() => ({ data: null }))
          return {
            ...reg,
            user: user.data
          }
        })
      )

      result.registrations = userList
    }

    return {
      code: 0,
      data: result,
      message: '获取成功'
    }

  } catch (error) {
    console.error('获取任务详情失败:', error)
    return {
      code: -1,
      message: '获取失败: ' + error.message
    }
  }
}