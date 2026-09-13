@echo off
chcp 65001 >nul
echo ========================================
echo    UI布局优化 - 文件替换脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [步骤1] 备份原文件...
if exist "frontend\src\components\AgentMessage.vue" (
    copy "frontend\src\components\AgentMessage.vue" "frontend\src\components\AgentMessage_backup_%date:~0,10%.vue" >nul
    echo ✓ 已备份 AgentMessage.vue
) else (
    echo ! AgentMessage.vue 不存在,跳过备份
)

if exist "frontend\src\views\AgentFrameworkView.vue" (
    copy "frontend\src\views\AgentFrameworkView.vue" "frontend\src\views\AgentFrameworkView_backup_%date:~0,10%.vue" >nul
    echo ✓ 已备份 AgentFrameworkView.vue
) else (
    echo ! AgentFrameworkView.vue 不存在,跳过备份
)

echo.
echo [步骤2] 替换为新版本...
copy "frontend\src\components\AgentMessage_v2.vue" "frontend\src\components\AgentMessage.vue" >nul
echo ✓ 已替换 AgentMessage.vue

copy "frontend\src\views\AgentFrameworkView_RightPanel.vue" "frontend\src\views\AgentFrameworkView.vue" >nul
echo ✓ 已替换 AgentFrameworkView.vue

echo.
echo ========================================
echo    文件替换完成!
echo ========================================
echo.
echo 新增功能:
echo  1. 执行轨迹移到右侧面板显示
echo  2. 收集的数据移到右侧面板显示
echo  3. 聊天框更简洁清爽
echo.
echo 下一步操作:
echo  1. 重启前端服务: cd frontend ^&^& npm run dev
echo  2. 刷新浏览器查看效果
echo.
pause
