/**
 * 微信登录云函数
 * 获取用户openid
 */
const cloud = require('wx-server-sdk')

// 初始化云开发环境
cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
})

// 云函数入口函数
exports.main = async (event, context) => {
  const { code } = event
  
  try {
    // 获取微信调用凭证
    const wxContext = cloud.getWXContext()
    
    // 返回用户openid
    return {
      code: 0,
      data: {
        openid: wxContext.OPENID,
        appid: wxContext.APPID,
        unionid: wxContext.UNIONID
      },
      message: '登录成功'
    }
  } catch (error) {
    console.error('登录失败:', error)
    return {
      code: -1,
      message: '登录失败: ' + error.message
    }
  }
}