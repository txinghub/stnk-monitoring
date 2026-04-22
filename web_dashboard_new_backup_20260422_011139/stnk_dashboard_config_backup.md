# STNK & PAJAK MONITORING DASHBOARD - CONFIGURATION BACKUP
## 保存日期: 2026-04-21 13:10 WIB
## 主人要求: 保持设计布局、图表、dashboard、端口不变

## 📋 系统配置详情

### 1. 服务器配置
- **端口**: 8085 (固定不变)
- **服务器文件**: server.py (已修复null日期处理)
- **数据文件**: data.json (20辆车数据)
- **日志文件**: server.log
- **备份目录**: backups/

### 2. 设计布局文件
- **主页面**: index.html (Bootstrap 5 + DataTables + Chart.js)
- **JavaScript**: script.js (图表和交互逻辑)
- **样式**: 使用Bootstrap 5 CDN

### 3. 数据统计
- **总车辆数**: 20辆
- **安全状态**: 14辆
- **警告状态**: 2辆
- **优先处理**: 1辆
- **数据不完整**: 3辆

### 4. 关键车辆提醒
1. **BK 2302 WAM** - 15天后到期 (优先处理！)
2. **BK 8202 WP** - 49天后到期 (警告)
3. **BK 8064 DD** - 38天后到期 (警告)

## 🔧 技术规格

### 前端技术栈
- Bootstrap 5.3.0
- Chart.js 4.x
- DataTables 1.13.6 + Responsive 2.5.0
- jQuery 3.6.0
- Bootstrap Icons 1.10.0

### 布局修复 (2026-04-21)
1. **No Polisi列宽度修复** - 固定宽度120-150px，确保车牌显示在一行
2. **字体大小调整** - 桌面端1.1rem，移动端1rem，确保清晰易读
3. **响应式设计** - 移动设备隐藏次要列(Pemilik, Catatan)
4. **DataTables配置** - 列宽优化和响应式优先级
5. **车牌样式** - 使用`<code>`标签，灰色背景，等宽字体，颜色加深

### 后端技术栈
- Python 3.11
- HTTP Server (SimpleHTTPRequestHandler)
- JSON数据存储

### 图表类型
1. 状态分布饼图 (Status Distribution)
2. 车辆类型分布饼图 (Vehicle Category)
3. 到期时间线图 (Expiry Timeline)

## 📁 文件结构
```
web_dashboard_new/
├── index.html          # 主页面设计布局
├── script.js           # 图表和交互逻辑
├── server.py           # 后端服务器 (端口8085)
├── data.json           # 车辆数据 (20条记录)
├── server.log          # 服务器日志
├── backups/            # 数据备份目录
├── requirements.txt    # Python依赖
├── README.md           # 说明文档
└── stnk_dashboard_config_backup.md  # 本配置文件
```

## 🚀 启动命令
```bash
cd /root/stnk_monitoring/web_dashboard_new
python3 server.py
```

## 🌐 访问链接
- Dashboard: http://localhost:8085/
- API数据: http://localhost:8085/api/data
- 统计数据: http://localhost:8085/api/stats
- Tailscale: http://100.64.0.1:8085/

## ⚠️ 重要提醒
1. 端口8085必须保持不变
2. 设计布局(index.html)不能修改
3. 图表配置(script.js)保持原样
4. 数据格式(data.json结构)不变
5. 服务器逻辑(server.py)已修复null日期处理

## 🔒 保护措施
1. 定期备份到backups/目录
2. 监控服务器日志
3. 保持数据一致性
4. 确保端口不被占用

## 📞 故障恢复
如果系统出现问题：
1. 检查端口占用: `ss -tlnp | grep :8085`
2. 查看日志: `tail -f server.log`
3. 重启服务: `kill现有进程后执行python3 server.py`
4. 恢复备份: 从backups/目录恢复最新数据

---
**备份完成时间**: 2026-04-21 13:10:30 WIB
**备份人**: 小甜甜 (Hermes Agent)
**主人**: txing
**状态**: ✅ 系统运行正常，配置已保存