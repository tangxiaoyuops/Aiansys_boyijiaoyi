# HT Cursor Rules 插件使用指南

## 第一步：安装插件

1. 打开 Cursor 编辑器
2. 点击左侧边栏的扩展图标（或按 `Ctrl+Shift+X`）
3. 在搜索框中输入 "HT Cursor Rules"
4. 找到插件后点击 "Install" 安装

## 第二步：验证规则文件

规则文件已创建在项目根目录：`.cursorrules`

这个文件包含了针对本项目的开发规范：
- Python/FastAPI 后端规范
- Vue3 + TypeScript 前端规范
- 中文项目规范
- 项目架构约定

## 第三步：使用插件创建规则（可选）

如果你想使用插件创建更多规则文件：

1. 按 `Ctrl+Shift+P`（Windows/Linux）或 `Cmd+Shift+P`（Mac）打开命令面板
2. 输入 "HT Cursor Rules: Create Rule"
3. 选择适合的模板（如 React、Vue、Python、FastAPI 等）
4. 插件会在 `.cursor/rules/` 目录下创建规则文件

## 第四步：验证规则是否生效

### 方法一：测试 AI 代码生成

1. 在 Cursor 中打开任意代码文件
2. 使用 Cursor AI 功能（如 `Ctrl+K` 生成代码）
3. 观察生成的代码是否遵循 `.cursorrules` 中的规范：
   - 是否有类型提示
   - 是否有中文注释
   - 是否符合代码风格

### 方法二：检查 AI 建议

1. 编写一些不符合规范的代码
2. 观察 Cursor AI 是否会建议按照规范修改

## 规则文件说明

`.cursorrules` 文件包含以下主要规范：

### Python 后端规范
- 必须使用类型提示
- 遵循 PEP 8
- 所有函数必须有中文文档字符串
- API 使用 RESTful 风格

### Vue3 前端规范
- 使用 Composition API
- TypeScript 严格模式
- 组件命名使用 PascalCase
- Props 使用 interface 定义

### 中文项目规范
- 代码注释使用中文
- 变量名使用英文
- 用户界面文本使用中文

## 常见问题

### Q: 规则文件在哪里？
A: 项目根目录的 `.cursorrules` 文件

### Q: 如何修改规则？
A: 直接编辑 `.cursorrules` 文件，保存后 Cursor 会自动应用

### Q: 规则不生效怎么办？
A: 
1. 确认文件在项目根目录
2. 重启 Cursor 编辑器
3. 检查文件格式是否正确（YAML front matter + Markdown）

### Q: 可以创建多个规则文件吗？
A: 可以，但建议使用一个 `.cursorrules` 文件，通过 `globs` 字段指定适用范围

## 下一步

1. ✅ 规则文件已创建
2. ⏳ 安装 HT Cursor Rules 插件（需要手动操作）
3. ⏳ 测试规则是否生效

## 提示

- 规则文件使用 Markdown 格式，易于阅读和编辑
- 可以根据项目发展随时更新规则
- 建议团队成员都了解这些规范







