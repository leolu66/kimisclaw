/**
 * 生成小程序二维码云函数
 * 使用 wxacode.getUnlimited 接口
 */
const cloud = require('wx-server-sdk')

cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
})

exports.main = async (event, context) => {
  const { taskId, unitId, page = 'pages/student/register' } = event

  try {
    if (!taskId || !unitId) {
      return {
        code: -1,
        message: '缺少必要参数'
      }
    }

    // 构建 scene 参数
    const scene = `taskId=${taskId}&unitId=${unitId}`

    // 调用微信接口生成二维码
    const result = await cloud.openapi.wxacode.getUnlimited({
      scene: scene,
      page: page,
      width: 430,
      autoColor: false,
      lineColor: {
        r: 7,
        g: 193,
        b: 96
      },
      isHyaline: false
    })

    // 上传到云存储
    const fileName = `qrcodes/task_${taskId}_${Date.now()}.png`
    const uploadResult = await cloud.uploadFile({
      cloudPath: fileName,
      fileContent: result.buffer
    })

    // 获取临时链接
    const fileResult = await cloud.getTempFileURL({
      fileList: [uploadResult.fileID]
    })

    const qrCodeUrl = fileResult.fileList[0].tempFileURL

    // 更新任务记录中的二维码URL
    const db = cloud.database()
    await db.collection('tasks').doc(taskId).update({
      data: {
        qrCodeUrl: qrCodeUrl,
        qrCodeFileID: uploadResult.fileID,
        updateAt: db.serverDate()
      }
    })

    return {
      code: 0,
      data: {
        qrCodeUrl,
        fileID: uploadResult.fileID
      },
      message: '生成成功'
    }

  } catch (error) {
    console.error('生成二维码失败:', error)
    return {
      code: -1,
      message: '生成失败: ' + error.message
    }
  }
}