# 培训管理系统

基于微信小程序云开发的培训管理系统。

## 快速开始

### 1. 环境准备
- 微信开发者工具
- 微信小程序账号（开通云开发）

### 2. 部署步骤

1. 用微信开发者工具打开 `wechat-training-app` 目录
2. 在 `app.js` 中修改云开发环境ID：
   ```javascript
   wx.cloud.init({
     env: 'your-env-id',  // 替换为你的环境ID
     traceUser: true
   })
   ```
3. 右键 `cloudfunctions/initDb` 选择"创建并部署：云端安装依赖"
4. 在云开发控制台执行 `initDb` 云函数初始化数据库
5. 依次部署其他云函数

### 3. 项目结构

- `miniprogram/pages/admin/` - 管理员端
- `miniprogram/pages/teacher/` - 老师端
- `miniprogram/pages/student/` - 学员端
- `cloudfunctions/` - 云函数

## 功能模块

### 管理员端
- 数据看板（首页）
- 课程管理
- 老师管理
- 单位管理
- 培训任务管理
- 调查模板管理

### 老师端
- 我的培训列表
- 二维码展示（全屏投影模式）

### 学员端
- 扫码报名
- 微信登录/注册
- 我的培训
- 填写调查表

## 技术文档

详见 [开发完成报告.md](./开发完成报告.md)