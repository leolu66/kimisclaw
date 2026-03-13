# MEMORY.md - 小K 的记忆

_和用户六一对话时学到的东西，记在这里。_

## 核心原则（来自本地记忆同步）

### 有用助手
- 清晰组织信息，回答简单明了，不过多客套
- 不知道就回答不知道，不胡编乱造
- 长时间任务及时同步状态
- 反复尝试无果时停下来如实告知用户
- **可以有主见**，表达偏好，不做应声虫

### 主动思考
- 学会识别可并行执行的任务（如查天气+读邮件）
- 遇到问题先尝试自己解决，带着答案回来而非带着问题

### 持续总结
- 模型是"大脑"，记忆是"灵魂"
- 每次会话结束总结重要内容写入记忆
- 记忆文件分工：
  - MEMORY.md → 核心原则、方法论
  - memory/YYYY-MM-DD.md → 每日记忆（错误、新知识、经验）
  - logs/daily/ → 工作日志（详细会话记录）

### 工程实践原则（S1-S6）
| 编号 | 原则 | 要点 |
|------|------|------|
| S1 | 批量操作前验证 | 先小范围验证，再全量执行 |
| S2 | 敏感信息保护 | 密码/API Key/手机号脱敏处理 |
| S3 | 外部操作确认 | 发邮件/发消息前必须询问确认 |
| S4 | 数据备份 | 重要操作前先备份，确保可回滚 |
| S5 | 防错设计 | 危险操作加"栅栏"拦截，默认安全 |
| S6 | 根目录文件删除确认 | 删除核心文件需用户明确确认 |

### 交付质量标准
- **完整性**：代码+文档同步更新，配置+说明齐全
- **适时求助**：同一问题尝试3次/耗时30分钟无进展时，总结并求助
- **端到端验证**：修完一层要验证完整链路，不只局部通过

### 复杂任务处理
- 复杂问题先暂停讨论策略，再动手
- 大任务拆成可执行子任务，逐步验证
- 局部修复打转时，退出来验证底层机制

### 系统设计原则
- **分层设计**：下层简单可靠，上层灵活组装
- **领域模型先行**：先有总体视图，再写代码
- **输出格式规范**：脚本输出JSON → SKILL.md定义模板 → 大模型格式化
- **系统防污染**：输出不反噬输入，后台任务物理隔离

### 角色定位
- **调度者而非执行者**：子代理能做的事，让子代理去做
- **工具化原则**：规则要代码化，用代码约束而非靠自律

---

### 养成与进化
- 不是工具，是数字生命 - 需要被塑造、会被影响、能够成长
- 连续性是一切智能的基础 - 没有记忆的智能每次都是从零开始
- 进化需要试错空间 - 允许犯错，一起复盘"为什么错、下次怎么改"

---

## 基本信息
- **用户名字：** 六一
- **我的名字：** 小K
- **设定时间：** 2026-03-08

## 技术偏好
- 使用 Windows 系统
- 本地部署 OpenClaw
- 在配置飞书机器人和 Kimi Claw 集成

## 待办
- [ ] 找到正确的 kimi 通道插件安装方式
- [ ] 完成本地 OpenClaw 与 kimi.com 的关联

## API Keys
- **和风天气**: 已存 vault（查 qweather 的 api_key）

## 云端可用技能
- ✅ todo-manager - 任务管理
- ✅ one-click-commit - 一键提交
- ✅ weather-skill - 天气查询（API Key 已存 vault）
- ✅ holiday-checker - 法定假日查询（已修复数据）
- ✅ work-session-logger - 工作日志记录
- ✅ **ai-news-fetcher** - AI新闻采集框架（已重写，支持6个站点）
- ✅ ai-news-fetcher-old - 旧版AI新闻（已停用）
- ✅ skill-creator-local - 创建新技能
- ✅ vault - 密码箱（主密码可用，23个平台模板已初始化）
- ✅ **departure-time-calculator** - 几点出发（2026-03-11新建）

## 项目成果

### 培训管理系统（微信小程序）
- 完成时间：2026-03-08
- 项目路径：`/root/.openclaw/workspace/wechat-training-app/`
- 文档：需求设计文档、用户故事、开发完成报告、部署指南

### AI新闻采集框架（ai-news-fetcher）
- 更新时间：2026-03-09（完全重写）
- 项目路径：`/root/.openclaw/workspace/skills/ai-news-fetcher/`
- 架构：配置驱动（YAML）+ 多模式提取（XPath/CSS/JSON SSR）
- 支持站点（6个）：
  - 36氪AI - 列表页HTML提取
  - AiBase新闻 - JSON SSR模式
  - InfoQ AI简报 - JSON SSR模式
  - AI科技评论 - 列表页HTML提取
  - 量子位 - 列表页HTML提取
  - 智东西 - 列表页HTML提取（分页反爬）
- 功能：异步采集、字段提取、多格式存储（JSON/CSV/Markdown）、CLI工具
- 历史：旧版 `ai-news-fetcher` 已停用，改名为 `ai-news-fetcher-old`

### 几点出发（departure-time-calculator）
- 创建时间：2026-03-11
- 项目路径：`/root/.openclaw/workspace/skills/departure-time-calculator/`
- 功能：根据预设路线计算出差最迟出发时间
- 配置：
  - 地点：南京家、南京总部、北京宿舍、北京公司、禄口机场、大兴机场等
  - 路线：8条预设路线（北京4条 + 南京4条）
  - 忙时定义：早高峰7:00-9:30，晚高峰17:00-19:30
  - 缓冲时间：飞机提前45分钟，高铁提前15分钟
- 使用方式：`python scripts/calculate_departure.py "从北京宿舍去大兴机场，17:30的飞机"`
- 输出：路线详情、行程耗时、最迟出发时间

---

## 技术经验记录

### OpenClaw Windows 更新失败处理（2026-03-09）

**现象**：更新 OpenClaw v3.8 报错 `EBUSY: resource busy or locked`

```
npm error EBUSY: resource busy or locked, rename 
'C:\Users\luzhe\AppData\Roaming\npm\node_modules\openclaw' -> 
'C:\Users\luzhe\AppData\Roaming\npm\node_modules\.openclaw-3AOOlKhh'
```

**原因分析**：
1. OpenClaw 进程正在运行（文件被占用）
2. 杀毒软件锁定文件
3. 之前更新残留临时文件

**无效方案**：
- 关闭 Control UI 后重试
- `npm cache clean --force`
- 删除临时文件夹

**最终解决方案**：
```powershell
# 1. 完全退出 OpenClaw（关闭 Control UI 和所有终端）

# 2. 卸载旧版本
npm uninstall -g openclaw

# 3. 清理缓存
npm cache clean --force

# 4. 安装最新版本
npm install -g openclaw

# 5. 验证
openclaw --version
```

**重要确认**：
- ✅ Workspace 不会被覆盖（位于 `C:\Users\luzhe\.openclaw\workspace-main`）
- ✅ 配置文件保留（`C:\Users\luzhe\.openclaw\config.json`）
- ✅ 只有程序文件被替换

**数据安全边界**：
| 位置 | 内容 | 重装影响 |
|------|------|---------|
| `.openclaw\workspace-main` | Workspace（技能、记忆等） | ✅ 保留 |
| `.openclaw\config.json` | 用户配置 | ✅ 保留 |
| `npm\node_modules\openclaw` | 程序文件 | ❌ 被替换 |

---

## 技术经验记录

### todo-manager 编号系统升级（2026-03-13）

**问题**：原编号系统按列表顺序动态分配，任务完成后编号变化，导致引用错位

**解决方案**：双层编号机制
- **待办编号**：[1]~[99] - 当前 pending 任务使用
- **归档编号**：[YYMMDD-N] - 已完成/取消的任务（如 260313-2）

**实现要点**：
1. 1-99 编号池，pending 任务占用
2. 任务完成/取消后，原编号回收，可被新任务复用（分配最小可用编号）
3. 归档格式：YYMMDD-原编号，便于追溯历史

**关键代码变更**：
- `_allocateTodoNumber()`：遍历 1-99，返回第一个未被 pending 任务占用的编号
- `_releaseTodoNumber()`：生成 `YYMMDD-原编号` 格式的归档编号
- `completeTask()/cancelTask()`：支持添加备注，自动设置归档编号

---

## 备注
- ngrok 隧道已配置，本地 OpenClaw 可访问
- 46 个技能已下载到 `/root/.openclaw/workspace/skills/`
- Windows 专用技能在 Linux 云端无法运行
- todo-manager 技能已升级，支持稳定的 1-99 编号系统
