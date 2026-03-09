/**
 * 日期格式化工具函数
 * @param {Date|number|string} date - 日期对象或时间戳
 * @param {string} format - 格式化模板，默认 'YYYY-MM-DD HH:mm'
 * @returns {string} 格式化后的日期字符串
 */
function formatDate(date, format = 'YYYY-MM-DD HH:mm') {
  if (!date) return ''
  
  const d = date instanceof Date ? date : new Date(date)
  if (isNaN(d.getTime())) return ''

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化日期为友好显示
 * @param {Date|number|string} date 
 * @returns {string}
 */
function formatFriendlyDate(date) {
  if (!date) return ''
  
  const d = date instanceof Date ? date : new Date(date)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  
  if (diff < minute) {
    return '刚刚'
  } else if (diff < hour) {
    return Math.floor(diff / minute) + '分钟前'
  } else if (diff < day) {
    return Math.floor(diff / hour) + '小时前'
  } else if (diff < 7 * day) {
    return Math.floor(diff / day) + '天前'
  } else {
    return formatDate(date, 'YYYY-MM-DD')
  }
}

/**
 * 请求封装 - 调用云函数
 * @param {string} name - 云函数名称
 * @param {object} data - 请求参数
 * @returns {Promise}
 */
function callCloudFunction(name, data = {}) {
  return new Promise((resolve, reject) => {
    wx.cloud.callFunction({
      name,
      data,
      success: res => {
        if (res.result && res.result.code !== undefined && res.result.code !== 0) {
          reject(new Error(res.result.message || '请求失败'))
        } else {
          resolve(res.result)
        }
      },
      fail: err => {
        console.error(`云函数 ${name} 调用失败:`, err)
        reject(err)
      }
    })
  })
}

/**
 * 显示提示信息
 * @param {string} title - 提示内容
 * @param {string} icon - 图标类型：success, error, loading, none
 * @param {number} duration - 显示时长
 */
function showToast(title, icon = 'none', duration = 2000) {
  wx.showToast({
    title,
    icon,
    duration
  })
}

/**
 * 显示加载中
 * @param {string} title 
 */
function showLoading(title = '加载中...') {
  wx.showLoading({
    title,
    mask: true
  })
}

/**
 * 隐藏加载中
 */
function hideLoading() {
  wx.hideLoading()
}

/**
 * 显示确认对话框
 * @param {string} title 
 * @param {string} content 
 * @returns {Promise<boolean>}
 */
function showConfirm(title, content = '') {
  return new Promise((resolve) => {
    wx.showModal({
      title,
      content,
      success: (res) => {
        resolve(res.confirm)
      }
    })
  })
}

/**
 * 验证手机号格式
 * @param {string} phone 
 * @returns {boolean}
 */
function isValidPhone(phone) {
  return /^1[3-9]\d{9}$/.test(phone)
}

/**
 * 验证邮箱格式
 * @param {string} email 
 * @returns {boolean}
 */
function isValidEmail(email) {
  return /^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$/.test(email)
}

/**
 * 防抖函数
 * @param {Function} fn 
 * @param {number} delay 
 * @returns {Function}
 */
function debounce(fn, delay = 300) {
  let timer = null
  return function (...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 * @param {Function} fn 
 * @param {number} interval 
 * @returns {Function}
 */
function throttle(fn, interval = 300) {
  let lastTime = 0
  return function (...args) {
    const now = Date.now()
    if (now - lastTime >= interval) {
      lastTime = now
      fn.apply(this, args)
    }
  }
}

/**
 * 生成唯一ID
 * @returns {string}
 */
function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

/**
 * 深拷贝对象
 * @param {any} obj 
 * @returns {any}
 */
function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime())
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (obj instanceof Object) {
    const cloned = {}
    Object.keys(obj).forEach(key => {
      cloned[key] = deepClone(obj[key])
    })
    return cloned
  }
}

module.exports = {
  formatDate,
  formatFriendlyDate,
  callCloudFunction,
  showToast,
  showLoading,
  hideLoading,
  showConfirm,
  isValidPhone,
  isValidEmail,
  debounce,
  throttle,
  generateId,
  deepClone
}