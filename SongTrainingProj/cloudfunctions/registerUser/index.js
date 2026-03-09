/**
 * 用户注册云函数
 * 创建用户记录和报名记录
 */
const cloud = require('wx-server-sdk')

cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
})

const db = cloud.database()

exports.main = async (event, context) => {
  const { 
    openid,
    name, 
    phone, 
    email, 
    wechatId, 
    password,
    taskId, 
    unitId,
    avatarUrl = ''
  } = event

  try {
    // 参数校验
    if (!openid || !name || !phone || !taskId || !unitId) {
      return {
        code: -1,
        message: '缺少必要参数'
      }
    }

    // 验证手机号格式
    if (!/^1[3-9]\d{9}$/.test(phone)) {
      return {
        code: -1,
        message: '手机号格式不正确'
      }
    }

    // 检查用户是否已存在
    const userCheck = await db.collection('users').where({
      openid: openid
    }).get()

    let userId

    if (userCheck.data.length > 0) {
      // 用户已存在，更新信息
      userId = userCheck.data[0]._id
      await db.collection('users').doc(userId).update({
        data: {
          name,
          phone,
          email: email || '',
          wechatId: wechatId || '',
          password: password || '',
          unitId,
          updateAt: db.serverDate()
        }
      })
    } else {
      // 创建新用户
      const userResult = await db.collection('users').add({
        data: {
          openid,
          name,
          phone,
          email: email || '',
          wechatId: wechatId || '',
          password: password || '',
          avatarUrl,
          unitId,
          createdAt: db.serverDate(),
          updateAt: db.serverDate()
        }
      })
      userId = userResult._id
    }

    // 检查是否已报名该培训
    const regCheck = await db.collection('registrations').where({
      taskId,
      userId
    }).get()

    if (regCheck.data.length > 0) {
      return {
        code: 1,
        message: '您已经报名该培训',
        data: { userId }
      }
    }

    // 创建报名记录
    await db.collection('registrations').add({
      data: {
        taskId,
        userId,
        registeredAt: db.serverDate(),
        status: 'registered'
      }
    })

    return {
      code: 0,
      message: '注册成功',
      data: { userId }
    }

  } catch (error) {
    console.error('注册失败:', error)
    return {
      code: -1,
      message: '注册失败: ' + error.message
    }
  }
}