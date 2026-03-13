const fs = require('fs');
const path = require('path');
const dayjs = require('dayjs');

const dataPath = path.join(__dirname, '../data/tasks.json');
const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

// 1. 清理所有现有todoNumber和archivedTodoNumber
data.tasks.forEach(task => {
  delete task.todoNumber;
  delete task.archivedTodoNumber;
});

// 2. 获取所有待办任务，按创建时间排序
const pendingTasks = data.tasks
  .filter(t => t.status === 'pending')
  .sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));

// 3. 给待办任务分配1-99编号
let nextNumber = 1;
pendingTasks.forEach(task => {
  if (nextNumber <= 99) {
    task.todoNumber = nextNumber;
    nextNumber++;
  }
});

// 4. 给已完成/取消的任务生成归档编号
const finishedTasks = data.tasks.filter(t => t.status === 'completed' || t.status === 'cancelled');
finishedTasks.forEach(task => {
  // 使用完成时间或当前时间生成前缀
  const datePrefix = dayjs(task.completedAt || task.createdAt).format('YYMMDD');
  // 从uniqueId中提取序号
  const match = task.uniqueId.match(/-(\d+)$/);
  const seq = match ? match[1] : '000';
  task.archivedTodoNumber = datePrefix + '-' + parseInt(seq);
});

// 保存
fs.writeFileSync(dataPath, JSON.stringify(data, null, 2));

console.log('数据迁移完成');
console.log('待办任务数:', pendingTasks.length);
console.log('已完成/取消任务数:', finishedTasks.length);
console.log('\n待办任务编号分配:');
pendingTasks.forEach(t => console.log('  [' + t.todoNumber + '] ' + t.title));
