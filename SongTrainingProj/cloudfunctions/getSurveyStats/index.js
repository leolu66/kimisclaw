/**
 * 获取调查结果统计云函数
 */
const cloud = require('wx-server-sdk')

cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
})

const db = cloud.database()

exports.main = async (event, context) => {
  const { taskId, templateId } = event

  try {
    if (!taskId || !templateId) {
      return {
        code: -1,
        message: '缺少必要参数'
      }
    }

    // 获取调查模板
    const template = await db.collection('survey_templates').doc(templateId).get()
    
    if (!template.data) {
      return {
        code: -1,
        message: '调查模板不存在'
      }
    }

    const questions = template.data.questions || []

    // 获取所有回答
    const responses = await db.collection('survey_responses').where({
      taskId,
      templateId
    }).get()

    const totalCount = responses.data.length

    if (totalCount === 0) {
      return {
        code: 0,
        data: {
          totalCount: 0,
          questions: []
        },
        message: '暂无数据'
      }
    }

    // 统计每个问题的回答
    const questionStats = questions.map((question, index) => {
      const stats = {
        questionIndex: index,
        title: question.title,
        type: question.type,
        totalCount: totalCount
      }

      if (question.type === 'radio') {
        // 单选题统计
        const optionCounts = {}
        question.options.forEach(opt => {
          optionCounts[opt] = 0
        })

        responses.data.forEach(response => {
          const answer = response.answers[index]
          if (answer && answer.value) {
            optionCounts[answer.value] = (optionCounts[answer.value] || 0) + 1
          }
        })

        stats.options = question.options.map(opt => ({
          label: opt,
          count: optionCounts[opt] || 0,
          percentage: Math.round(((optionCounts[opt] || 0) / totalCount) * 100)
        }))

      } else if (question.type === 'checkbox') {
        // 多选题统计
        const optionCounts = {}
        question.options.forEach(opt => {
          optionCounts[opt] = 0
        })

        responses.data.forEach(response => {
          const answer = response.answers[index]
          if (answer && Array.isArray(answer.value)) {
            answer.value.forEach(val => {
              optionCounts[val] = (optionCounts[val] || 0) + 1
            })
          }
        })

        stats.options = question.options.map(opt => ({
          label: opt,
          count: optionCounts[opt] || 0,
          percentage: Math.round(((optionCounts[opt] || 0) / totalCount) * 100)
        }))

      } else if (question.type === 'text') {
        // 文本题收集所有回答
        stats.answers = responses.data
          .map(response => {
            const answer = response.answers[index]
            return answer && answer.value ? answer.value : ''
          })
          .filter(val => val)
      }

      return stats
    })

    return {
      code: 0,
      data: {
        totalCount,
        questions: questionStats
      },
      message: '获取成功'
    }

  } catch (error) {
    console.error('获取调查统计失败:', error)
    return {
      code: -1,
      message: '获取失败: ' + error.message
    }
  }
}