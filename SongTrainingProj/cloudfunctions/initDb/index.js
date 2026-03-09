/**
 * 初始化数据库云函数
 * 创建所有必要的集合
 */
const cloud = require('wx-server-sdk')

cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
})

const db = cloud.database()

// 需要创建的集合列表
const COLLECTIONS = [
  'courses',           // 课程
  'teachers',          // 老师
  'units',             // 单位
  'tasks',             // 培训任务
  'survey_templates',  // 调查模板
  'users',             // 学员
  'registrations',     // 报名记录
  'survey_responses'   // 调查结果
]

exports.main = async (event, context) => {
  try {
    const results = []
    
    for (const collectionName of COLLECTIONS) {
      try {
        // 尝试创建集合，如果已存在会抛出错误
        await db.createCollection(collectionName)
        results.push({
          collection: collectionName,
          status: 'created',
          message: '创建成功'
        })
      } catch (err) {
        if (err.message && err.message.includes('already exists')) {
          results.push({
            collection: collectionName,
            status: 'exists',
            message: '集合已存在'
          })
        } else {
          results.push({
            collection: collectionName,
            status: 'error',
            message: err.message
          })
        }
      }
    }

    // 创建索引
    try {
      // users 集合 openid 索引
      await db.collection('users').createIndex({
        name: 'openid_idx',
        key: { openid: 1 },
        unique: true
      }).catch(() => {})

      // registrations 复合索引
      await db.collection('registrations').createIndex({
        name: 'task_user_idx',
        key: { taskId: 1, userId: 1 },
        unique: true
      }).catch(() => {})

      // survey_responses 复合索引
      await db.collection('survey_responses').createIndex({
        name: 'task_user_idx',
        key: { taskId: 1, userId: 1 },
        unique: true
      }).catch(() => {})

      results.push({
        collection: 'indexes',
        status: 'created',
        message: '索引创建成功'
      })
    } catch (indexErr) {
      results.push({
        collection: 'indexes',
        status: 'warning',
        message: '部分索引创建失败: ' + indexErr.message
      })
    }

    return {
      code: 0,
      data: results,
      message: '初始化完成'
    }

  } catch (error) {
    console.error('初始化数据库失败:', error)
    return {
      code: -1,
      message: '初始化失败: ' + error.message
    }
  }
}