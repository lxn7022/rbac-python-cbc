# 腾讯云开放 Supabase 端口配置指南

## 问题：防火墙阻挡 PostgreSQL 端口

错误信息：
```
connection to server at "db.orygzioqsfvuauzklogx.supabase.co", port 5432 failed: Connection timed out
```

## 解决方案：开放防火墙端口

### 方式 1：腾讯云控制台配置

1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 进入 **轻量应用服务器** → 选择服务器实例
3. 点击 **防火墙** 标签
4. 点击 **添加规则**

添加以下规则：

#### 规则 1：Supabase Pooler（推荐）

```
应用类型：自定义
协议：TCP
端口：6543
策略：允许
备注：Supabase 连接池端口
```

#### 规则 2：Supabase 直连（可选）

```
应用类型：自定义
协议：TCP
端口：5432
策略：允许
备注：Supabase PostgreSQL 直连端口
```

### 方式 2：使用腾讯云 CLI（命令行）

```bash
# 安装腾讯云 CLI
pip install tccli

# 配置密钥
tccli configure

# 添加防火墙规则（需要实例 ID）
tccli lighthouse CreateFirewallRules \
  --InstanceId lhins-xxxxxxxx \
  --FirewallRules '[
    {
      "Protocol": "TCP",
      "Port": "6543",
      "CidrBlock": "0.0.0.0/0",
      "Action": "ACCEPT",
      "FirewallRuleDescription": "Supabase Pooler"
    }
  ]'
```

### 方式 3：限制来源 IP（更安全）

```
应用类型：自定义
协议：TCP
端口：6543
来源：你的服务器公网IP/32
策略：允许
备注：仅允许本服务器访问 Supabase
```

---

## 验证端口是否开放

### Windows 测试

```powershell
# 测试端口 6543
Test-NetConnection -ComputerName aws-0-ap-southeast-1.pooler.supabase.com -Port 6543

# 测试端口 5432
Test-NetConnection -ComputerName db.orygzioqsfvuauzklogx.supabase.co -Port 5432
```

### Linux 测试

```bash
# 测试端口 6543
nc -zv aws-0-ap-southeast-1.pooler.supabase.com 6543

# 测试端口 5432
nc -zv db.orygzioqsfvuauzklogx.supabase.co 5432

# 或使用 telnet
telnet aws-0-ap-southeast-1.pooler.supabase.com 6543
```

### Python 测试

```python
import socket

host = "aws-0-ap-southeast-1.pooler.supabase.com"
port = 6543

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((host, port))
    
    if result == 0:
        print(f"✅ 端口 {port} 可访问")
    else:
        print(f"❌ 端口 {port} 不可访问")
    
    sock.close()
except Exception as e:
    print(f"❌ 连接失败: {e}")
```

---

## 修改 SQLAlchemy 连接配置

### 1. 获取 Supabase 连接信息

访问 Supabase 控制台：
- 项目设置 → Database → Connection string

**连接字符串格式**：
```
postgresql://postgres.[项目ID]:[密码]@aws-0-[区域].pooler.supabase.com:6543/postgres
```

**注意**：使用 **Pooler 端口 6543**，不是直连端口 5432

### 2. 配置环境变量

```bash
# .env
SUPABASE_DATABASE_URL=postgresql://postgres.orygzioqsfvuauzklogx:[密码]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

### 3. 修改数据库连接代码

```python
# src/db/base.py
from sqlalchemy import create_engine
from src.config.settings import get_settings
import os

settings = get_settings()

# 优先使用 Supabase 连接
database_url = os.getenv('SUPABASE_DATABASE_URL', settings.DATABASE_URL)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
    }
)
```

---

## 两种连接方式对比

### 直连（端口 5432）

```
数据库 URL：db.项目ID.supabase.co:5432
特点：
- 直连 PostgreSQL 实例
- 连接数有限（通常 20-100）
- 不推荐用于生产环境
```

### 连接池（端口 6543）

```
数据库 URL：aws-0-[区域].pooler.supabase.co:6543
特点：
- 通过 PgBouncer 连接池
- 支持大量并发连接
- 推荐用于生产环境
```

---

## 推荐方案

### 本地开发
```
使用本地 PostgreSQL（Docker）
DATABASE_URL=postgresql://postgres:password@localhost:5432/rbac_db
```

### 生产环境（需开放端口）
```
使用 Supabase Pooler
SUPABASE_DATABASE_URL=postgresql://...@pooler.supabase.com:6543/postgres
```

### 生产环境（端口受限）
```
使用 REST API（当前方案）
通过 HTTPS 443 端口，不受防火墙限制
```

---

## 常见问题

### Q: 开放端口后仍然连接超时？

检查：
1. Supabase 项目是否暂停
2. IP 白名单是否限制
3. 连接字符串是否正确
4. 密码是否包含特殊字符（需要 URL 编码）

### Q: 如何查看 Supabase 项目区域？

访问 Supabase 控制台 → 项目设置 → General → Region

### Q: 密码包含特殊字符怎么办？

使用 URL 编码：
```python
from urllib.parse import quote_plus

password = "p@ssw0rd#123"
encoded_password = quote_plus(password)
# 结果：p%40ssw0rd%23123
```

---

## 下一步

1. **开放防火墙端口**：在腾讯云控制台添加规则（端口 6543）
2. **验证端口**：运行测试命令确认端口可访问
3. **配置连接**：修改 `.env` 文件
4. **测试连接**：运行应用测试 SQLAlchemy 是否可用

如果无法开放端口，继续使用 REST API 方式（已实现且可用）。
