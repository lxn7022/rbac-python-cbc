-- ============================================================================
-- RBAC 系统数据库初始化脚本 (Supabase PostgreSQL)
-- 版本: 001
-- 描述: 初始化 RBAC 系统表结构和初始数据
-- 
-- 使用方法:
-- 1. 访问 https://supabase.com/dashboard
-- 2. 选择你的项目
-- 3. 点击左侧菜单的 SQL Editor
-- 4. 点击 New query
-- 5. 粘贴此文件内容并点击 Run
-- ============================================================================

-- ============================================================================
-- 1. 删除已存在的表（慎用！）
-- ============================================================================

-- DROP TABLE IF EXISTS public.rbac_constraints CASCADE;
-- DROP TABLE IF EXISTS public.role_permissions CASCADE;
-- DROP TABLE IF EXISTS public.user_roles CASCADE;
-- DROP TABLE IF EXISTS public.permissions CASCADE;
-- DROP TABLE IF EXISTS public.roles CASCADE;
-- DROP TABLE IF EXISTS public.users CASCADE;

-- ============================================================================
-- 2. users 表（用户表）
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
    CONSTRAINT valid_username CHECK (char_length(username) >= 3)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON public.users(username);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON public.users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON public.users(created_at DESC);

-- 添加注释
COMMENT ON TABLE public.users IS '用户表，存储系统用户基本信息';
COMMENT ON COLUMN public.users.id IS '用户唯一标识';
COMMENT ON COLUMN public.users.username IS '用户名，唯一';
COMMENT ON COLUMN public.users.email IS '邮箱地址，唯一';
COMMENT ON COLUMN public.users.password_hash IS '密码哈希值（bcrypt加密）';
COMMENT ON COLUMN public.users.full_name IS '用户全名';
COMMENT ON COLUMN public.users.is_active IS '是否激活';
COMMENT ON COLUMN public.users.is_verified IS '邮箱是否验证';
COMMENT ON COLUMN public.users.last_login_at IS '最后登录时间';
COMMENT ON COLUMN public.users.created_at IS '创建时间';
COMMENT ON COLUMN public.users.updated_at IS '更新时间';

-- 创建更新时间戳触发器函数
CREATE OR REPLACE FUNCTION public.update_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
DROP TRIGGER IF EXISTS trigger_update_users_updated_at ON public.users;
CREATE TRIGGER trigger_update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION public.update_users_updated_at();

-- ============================================================================
-- 3. roles 表（角色表）
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT false,
    priority INTEGER DEFAULT 0,
    parent_id BIGINT REFERENCES public.roles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_name CHECK (char_length(name) >= 2),
    CONSTRAINT valid_slug CHECK (slug ~* '^[a-z0-9-]+$')
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_roles_slug ON public.roles(slug);
CREATE INDEX IF NOT EXISTS idx_roles_parent_id ON public.roles(parent_id);
CREATE INDEX IF NOT EXISTS idx_roles_is_system ON public.roles(is_system);
CREATE INDEX IF NOT EXISTS idx_roles_priority ON public.roles(priority);

-- 添加注释
COMMENT ON TABLE public.roles IS '角色表，支持 RBAC1 继承';
COMMENT ON COLUMN public.roles.parent_id IS '父角色ID（支持角色继承）';

-- 创建更新时间戳触发器
CREATE OR REPLACE FUNCTION public.update_roles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_roles_updated_at ON public.roles;
CREATE TRIGGER trigger_update_roles_updated_at
    BEFORE UPDATE ON public.roles
    FOR EACH ROW
    EXECUTE FUNCTION public.update_roles_updated_at();

-- ============================================================================
-- 4. permissions 表（权限表）
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.permissions (
    id BIGSERIAL PRIMARY KEY,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT false,
    module VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_resource CHECK (char_length(resource) >= 2),
    CONSTRAINT valid_action CHECK (char_length(action) >= 2),
    CONSTRAINT unique_resource_action UNIQUE (resource, action)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_permissions_resource ON public.permissions(resource);
CREATE INDEX IF NOT EXISTS idx_permissions_action ON public.permissions(action);
CREATE INDEX IF NOT EXISTS idx_permissions_module ON public.permissions(module);
CREATE INDEX IF NOT EXISTS idx_permissions_unique ON public.permissions(resource, action);

-- 添加注释
COMMENT ON TABLE public.permissions IS '权限表，存储系统所有权限';

-- 创建更新时间戳触发器
CREATE OR REPLACE FUNCTION public.update_permissions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_permissions_updated_at ON public.permissions;
CREATE TRIGGER trigger_update_permissions_updated_at
    BEFORE UPDATE ON public.permissions
    FOR EACH ROW
    EXECUTE FUNCTION public.update_permissions_updated_at();

-- ============================================================================
-- 5. user_roles 表（用户-角色关联表）
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.user_roles (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    assigned_by BIGINT REFERENCES public.users(id) ON DELETE SET NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    CONSTRAINT unique_user_role UNIQUE (user_id, role_id),
    CONSTRAINT valid_expires_at CHECK (expires_at IS NULL OR expires_at > assigned_at)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON public.user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON public.user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_is_active ON public.user_roles(is_active);

-- 添加注释
COMMENT ON TABLE public.user_roles IS '用户-角色关联表，支持多对多关系';

-- 创建更新时间戳触发器
CREATE OR REPLACE FUNCTION public.update_user_roles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- user_roles 没有 updated_at 字段，不需要触发器

-- ============================================================================
-- 6. role_permissions 表（角色-权限关联表）
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.role_permissions (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    permission_id BIGINT NOT NULL REFERENCES public.permissions(id) ON DELETE CASCADE,
    granted_by BIGINT REFERENCES public.users(id) ON DELETE SET NULL,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    CONSTRAINT unique_role_permission UNIQUE (role_id, permission_id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON public.role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission_id ON public.role_permissions(permission_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_is_active ON public.role_permissions(is_active);

-- 添加注释
COMMENT ON TABLE public.role_permissions IS '角色-权限关联表，支持多对多关系';

-- ============================================================================
-- 7. rbac_constraints 表（RBAC2 约束规则表）
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.rbac_constraints (
    id BIGSERIAL PRIMARY KEY,
    constraint_type VARCHAR(50) NOT NULL,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_constraint_type CHECK (constraint_type IN (
        'mutually_exclusive',
        'cardinality',
        'prerequisite'
    ))
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_rbac_constraints_type ON public.rbac_constraints(constraint_type);
CREATE INDEX IF NOT EXISTS idx_rbac_constraints_is_active ON public.rbac_constraints(is_active);

-- 添加注释
COMMENT ON TABLE public.rbac_constraints IS 'RBAC2 约束规则表';

-- 创建更新时间戳触发器
CREATE OR REPLACE FUNCTION public.update_rbac_constraints_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_rbac_constraints_updated_at ON public.rbac_constraints;
CREATE TRIGGER trigger_update_rbac_constraints_updated_at
    BEFORE UPDATE ON public.rbac_constraints
    FOR EACH ROW
    EXECUTE FUNCTION public.update_rbac_constraints_updated_at();

-- ============================================================================
-- 8. 创建默认角色
-- ============================================================================

INSERT INTO public.roles (name, slug, description, is_system, priority) VALUES
    ('超级管理员', 'super-admin', '拥有系统所有权限', true, 100),
    ('管理员', 'admin', '系统管理员，拥有大部分权限', false, 80),
    ('编辑', 'editor', '内容编辑人员', false, 60),
    ('普通用户', 'user', '普通注册用户', false, 40),
    ('访客', 'guest', '未登录或临时访客', true, 20)
ON CONFLICT (slug) DO NOTHING;

-- ============================================================================
-- 9. 创建默认权限
-- ============================================================================

INSERT INTO public.permissions (resource, action, description, module, is_system) VALUES
    -- 用户管理
    ('user', 'read', '读取用户信息', 'auth', true),
    ('user', 'write', '编辑用户信息', 'auth', true),
    ('user', 'create', '创建用户', 'auth', true),
    ('user', 'delete', '删除用户', 'auth', true),
    ('user', 'manage', '管理用户（包含所有操作）', 'auth', true),
    
    -- 角色管理
    ('role', 'read', '读取角色信息', 'rbac', true),
    ('role', 'write', '编辑角色信息', 'rbac', true),
    ('role', 'create', '创建角色', 'rbac', true),
    ('role', 'delete', '删除角色', 'rbac', true),
    ('role', 'manage', '管理角色（包含所有操作）', 'rbac', true),
    
    -- 权限管理
    ('permission', 'read', '读取权限信息', 'rbac', true),
    ('permission', 'assign', '分配权限', 'rbac', true),
    ('permission', 'revoke', '撤销权限', 'rbac', true),
    
    -- 内容管理
    ('article', 'read', '读取文章', 'content', true),
    ('article', 'write', '创建/编辑文章', 'content', true),
    ('article', 'delete', '删除文章', 'content', true),
    ('article', 'publish', '发布文章', 'content', true),
    
    -- 订单管理
    ('order', 'read', '读取订单', 'order', true),
    ('order', 'write', '创建/编辑订单', 'order', true),
    ('order', 'delete', '删除订单', 'order', true),
    ('order', 'manage', '管理订单（包含所有操作）', 'order', true)
ON CONFLICT (resource, action) DO NOTHING;

-- ============================================================================
-- 10. 为角色分配默认权限
-- ============================================================================

-- 超级管理员：所有权限
INSERT INTO public.role_permissions (role_id, permission_id)
SELECT 
    (SELECT id FROM public.roles WHERE slug = 'super-admin'),
    id
FROM public.permissions
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 管理员：除了删除用户和角色之外的所有权限
INSERT INTO public.role_permissions (role_id, permission_id)
SELECT 
    (SELECT id FROM public.roles WHERE slug = 'admin'),
    id
FROM public.permissions
WHERE (resource, action) NOT IN (
    ('user', 'delete'),
    ('role', 'delete')
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 编辑：内容管理权限
INSERT INTO public.role_permissions (role_id, permission_id)
SELECT 
    (SELECT id FROM public.roles WHERE slug = 'editor'),
    id
FROM public.permissions
WHERE module IN ('auth', 'content')
  AND (resource, action) IN (
    ('user', 'read'),
    ('article', 'read'),
    ('article', 'write'),
    ('article', 'delete'),
    ('article', 'publish')
  )
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 普通用户：基础读取权限
INSERT INTO public.role_permissions (role_id, permission_id)
SELECT 
    (SELECT id FROM public.roles WHERE slug = 'user'),
    id
FROM public.permissions
WHERE (resource, action) IN (
    ('article', 'read'),
    ('order', 'read')
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 访客：无权限
-- （不需要插入）

-- ============================================================================
-- 11. 创建默认约束规则
-- ============================================================================

INSERT INTO public.rbac_constraints (constraint_type, name, description, config, is_active) VALUES
    ('cardinality', '管理员数量限制', '管理员角色最多分配给 5 个用户', 
     '{"role": "admin", "max_users": 5}'::jsonb, true),
    ('prerequisite', '编辑角色先决条件', '用户必须拥有普通用户角色才能分配编辑角色',
     '{"role": "editor", "required_roles": ["user"]}'::jsonb, true)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- 12. 创建一个默认管理员用户（密码: admin123）
-- ============================================================================

INSERT INTO public.users (username, email, password_hash, full_name, is_active, is_verified)
VALUES (
    'admin', 
    'admin@example.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LHEuKz/bQn7Yb1zYQvZJjC9YqGy6wW5.', -- bcrypt hash of 'admin123'
    '系统管理员', 
    true, 
    true
) ON CONFLICT (username) DO NOTHING;

-- 为管理员分配超级管理员角色
INSERT INTO public.user_roles (user_id, role_id, is_active)
SELECT 
    (SELECT id FROM public.users WHERE username = 'admin'),
    (SELECT id FROM public.roles WHERE slug = 'super-admin'),
    true
ON CONFLICT (user_id, role_id) DO NOTHING;

-- ============================================================================
-- 完成
-- ============================================================================

-- 查看创建的数据
SELECT '数据库初始化完成！' AS status;

-- 显示角色数量
SELECT 
    '角色数量: ' || COUNT(*) AS info
FROM public.roles;

-- 显示权限数量
SELECT 
    '权限数量: ' || COUNT(*) AS info
FROM public.permissions;

-- 显示默认用户
SELECT 
    '默认用户: ' || username || ' (' || email || ')' AS info
FROM public.users
WHERE username = 'admin';
