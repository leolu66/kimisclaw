/**
 * 提交调查表云函数
 */
const cloud = require('wx-server-sdk')

cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
})

const db = cloud.database()

exports.main = async (event, context) => {
  const { 
    taskId, 
    userId, 
    templateId, 
    answers 
  } = event

  try {
    // 参数校验
    if (!taskId || !userId || !templateId || !answers || !Array.isArray(answers)) {
      return {
        code: -1,
        message: '缺少必要参数'
      }
    }

    // 检查是否已提交过
    const existing = await db.collection('survey_responses').where({
      taskId,
      userId
    }).get()

    if (existing.data.length > 0) {
      return {
        code: -1,
        message: '您已提交过调查表，不能重复提交'
      }
    }

    // 检查报名记录是否存在
    const regCheck = await db.collection('registrations').where({
      taskId,
      userId
    }).get()

    if (regCheck.data.length === 0) {
      return {
        code: -1,
        message: '您未报名该培训，无法提交调查表'
      }
    }

    // 保存调查结果
    const result = await db.collection('survey_responses').add({
      data: {
        taskId,
        userId,
        templateId,
        answers,
        submittedAt: db.serverDate()
      }
    })

    // 更新报名状态为已完成
    await db.collection('registrations').where({
      taskId,
      userId
    }).update({
      data: {
        status: 'completed',
        surveySubmittedAt: db.serverDate()
      }
    })

    return {
      code: 0,
      data: { responseId: result._id },
      message: '提交成功'
    }

  } catch (error) {
    console.error('提交调查表失败:', error)
    return {
      code: -1,
      message: '提交失败: ' + error.message
    }
  }
}