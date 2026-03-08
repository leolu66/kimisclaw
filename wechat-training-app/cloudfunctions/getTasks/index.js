/**
 * 获取培训任务列表云函数
 * 支持筛选和分页
 */
const cloud = require('wx-server-sdk')

cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
})

const db = cloud.database()
const _ = db.command

exports.main = async (event, context) => {
  const { 
    page = 1, 
    pageSize = 20, 
    keyword = '',
    status = '',
    teacherId = '',
    unitId = '',
    userId = ''
  } = event

  try {
    let where = {}
    
    // 关键词搜索
    if (keyword) {
      where.title = db.RegExp({
        regexp: keyword,
        options: 'i'
      })
    }
    
    // 状态筛选
    if (status) {
      where.status = status
    }
    
    // 老师筛选
    if (teacherId) {
      where.teacherId = teacherId
    }
    
    // 单位筛选
    if (unitId) {
      where.unitId = unitId
    }

    // 构建查询
    let query = db.collection('tasks').where(where)
    
    // 获取总数
    const countResult = await query.count()
    const total = countResult.total
    
    // 分页查询
    const tasks = await query
      .orderBy('date', 'desc')
      .skip((page - 1) * pageSize)
      .limit(pageSize)
      .get()

    // 获取关联数据
    const taskList = await Promise.all(tasks.data.map(async (task) => {
      // 获取课程信息
      const course = await db.collection('courses').doc(task.courseId).get().catch(() => ({ data: null }))
      
      // 获取老师信息
      const teacher = await db.collection('teachers').doc(task.teacherId).get().catch(() => ({ data: null }))
      
      // 获取单位信息
      const unit = await db.collection('units').doc(task.unitId).get().catch(() => ({ data: null }))
      
      // 获取报名人数
      const regCount = await db.collection('registrations').where({
        taskId: task._id
      }).count()

      return {
        ...task,
        courseName: course.data?.name || '未知课程',
        teacherName: teacher.data?.name || '未知老师',
        unitName: unit.data?.name || '未知单位',
        registeredCount: regCount.total
      }
    }))

    return {
      code: 0,
      data: {
        list: taskList,
        total,
        page,
        pageSize,
        hasMore: page * pageSize < total
      },
      message: '获取成功'
    }

  } catch (error) {
    console.error('获取任务列表失败:', error)
    return {
      code: -1,
      message: '获取失败: ' + error.message
    }
  }
}