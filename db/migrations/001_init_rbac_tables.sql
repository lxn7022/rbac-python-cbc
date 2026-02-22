-- ============================================================================
-- RBAC 系统数据库迁移
-- 版本: 001
-- 描述: 初始化 RBAC 系统表结构（用户、角色、权限及关联表）
-- ============================================================================

-- ============================================================================
-- 1. users 表（用户表）
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
-- 2. roles 表（角色表）
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
COMMENT ON TABLE public.roles IS '角色表，存储系统角色信息';
COMMENT ON COLUMN public.roles.id IS '角色唯一标识';
COMMENT ON COLUMN public.roles.name IS '角色显示名称';
COMMENT ON COLUMN public.roles.slug IS '角色标识符（用于代码引用）';
COMMENT ON COLUMN public.roles.description IS '角色描述';
COMMENT ON COLUMN public.roles.is_system IS '是否系统角色（系统角色不可删除）';
COMMENT ON COLUMN public.roles.priority IS '角色优先级（用于权限合并顺序）';
COMMENT ON COLUMN public.roles.parent_id IS '父角色ID（用于角色继承）';
COMMENT ON COLUMN public.roles.created_at IS '创建时间';
COMMENT ON COLUMN public.roles.updated_at IS '更新时间';

-- 创建更新时间戳触发器函数
CREATE OR REPLACE FUNCTION public.update_roles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
DROP TRIGGER IF EXISTS trigger_update_roles_updated_at ON public.roles;
CREATE TRIGGER trigger_update_roles_updated_at
    BEFORE UPDATE ON public.roles
    FOR EACH ROW
    EXECUTE FUNCTION public.update_roles_updated_at();

-- ============================================================================
-- 3. permissions 表（权限表）
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
CREATE INDEX IF NOT EXISTS idx_permissions_resource_action ON public.permissions(resource, action);
CREATE INDEX IF NOT EXISTS idx_permissions_is_system ON public.permissions(is_system);

-- 添加注释
COMMENT ON TABLE public.permissions IS '权限表，存储系统权限信息';
COMMENT ON COLUMN public.permissions.id IS '权限唯一标识';
COMMENT ON COLUMN public.permissions.resource IS '资源名称（如：user, article）';
COMMENT ON COLUMN public.permissions.action IS '操作类型（如：read, write, delete）';
COMMENT ON COLUMN public.permissions.description IS '权限描述';
COMMENT ON COLUMN public.permissions.is_system IS '是否系统权限（系统权限不可删除）';
COMMENT ON COLUMN public.permissions.module IS '所属模块（如：auth, rbac, content）';
COMMENT ON COLUMN public.permissions.created_at IS '创建时间';
COMMENT ON COLUMN public.permissions.updated_at IS '更新时间';

-- 创建更新时间戳触发器函数
CREATE OR REPLACE FUNCTION public.update_permissions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
DROP TRIGGER IF EXISTS trigger_update_permissions_updated_at ON public.permissions;
CREATE TRIGGER trigger_update_permissions_updated_at
    BEFORE UPDATE ON public.permissions
    FOR EACH ROW
    EXECUTE FUNCTION public.update_permissions_updated_at();

-- ============================================================================
-- 4. user_roles 表（用户角色关联表）
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
CREATE INDEX IF NOT EXISTS idx_user_roles_assigned_by ON public.user_roles(assigned_by);
CREATE INDEX IF NOT EXISTS idx_user_roles_is_active ON public.user_roles(is_active);
CREATE INDEX IF NOT EXISTS idx_user_roles_expires_at ON public.user_roles(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_roles_user_role ON public.user_roles(user_id, role_id);

-- 添加注释
COMMENT ON TABLE public.user_roles IS '用户角色关联表，实现用户与角色的多对多关系';
COMMENT ON COLUMN public.user_roles.id IS '关联记录唯一标识';
COMMENT ON COLUMN public.user_roles.user_id IS '用户ID';
COMMENT ON COLUMN public.user_roles.role_id IS '角色ID';
COMMENT ON COLUMN public.user_roles.assigned_by IS '分配人用户ID';
COMMENT ON COLUMN public.user_roles.assigned_at IS '分配时间';
COMMENT ON COLUMN public.user_roles.expires_at IS '过期时间（NULL 表示永不过期）';
COMMENT ON COLUMN public.user_roles.is_active IS '是否激活（可临时禁用角色）';

-- ============================================================================
-- 5. role_permissions 表（角色权限关联表）
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
CREATE INDEX IF NOT EXISTS idx_role_permissions_granted_by ON public.role_permissions(granted_by);
CREATE INDEX IF NOT EXISTS idx_role_permissions_is_active ON public.role_permissions(is_active);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role_permission ON public.role_permissions(role_id, permission_id);

-- 添加注释
COMMENT ON TABLE public.role_permissions IS '角色权限关联表，实现角色与权限的多对多关系';
COMMENT ON COLUMN public.role_permissions.id IS '关联记录唯一标识';
COMMENT ON COLUMN public.role_permissions.role_id IS '角色ID';
COMMENT ON COLUMN public.role_permissions.permission_id IS '权限ID';
COMMENT ON COLUMN public.role_permissions.granted_by IS '授权人用户ID';
COMMENT ON COLUMN public.role_permissions.granted_at IS '授权时间';
COMMENT ON COLUMN public.role_permissions.is_active IS '是否激活（可临时禁用权限）';

-- ============================================================================
-- 6. rbac_constraints 表（RBAC 约束规则表）
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
        'mutually_exclusive',  -- 互斥角色（SSD）
        'cardinality',         -- 基数约束
        'prerequisite'          -- 先决条件
    ))
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_rbac_constraints_type ON public.rbac_constraints(constraint_type);
CREATE INDEX IF NOT EXISTS idx_rbac_constraints_is_active ON public.rbac_constraints(is_active);

-- 添加注释
COMMENT ON TABLE public.rbac_constraints IS 'RBAC 约束规则表，存储权限约束配置';
COMMENT ON COLUMN public.rbac_constraints.id IS '约束规则唯一标识';
COMMENT ON COLUMN public.rbac_constraints.constraint_type IS '约束类型（互斥/基数/先决条件）';
COMMENT ON COLUMN public.rbac_constraints.name IS '约束规则名称';
COMMENT ON COLUMN public.rbac_constraints.description IS '约束规则描述';
COMMENT ON COLUMN public.rbac_constraints.config IS '约束配置（JSONB 格式）';
COMMENT ON COLUMN public.rbac_constraints.is_active IS '是否启用';
COMMENT ON COLUMN public.rbac_constraints.created_at IS '创建时间';
COMMENT ON COLUMN public.rbac_constraints.updated_at IS '更新时间';

-- ============================================================================
-- 7. 插入初始数据
-- ============================================================================

-- 插入系统默认角色
INSERT INTO public.roles (name, slug, description, is_system, priority) VALUES
    ('超级管理员', 'super-admin', '拥有系统所有权限', true, 100),
    ('管理员', 'admin', '系统管理员，拥有大部分权限', true, 80),
    ('编辑', 'editor', '内容编辑人员', true, 60),
    ('普通用户', 'user', '普通注册用户', true, 40),
    ('访客', 'guest', '未登录或临时访客', true, 20)
ON CONFLICT (slug) DO NOTHING;

-- 插入系统默认权限
INSERT INTO public.permissions (resource, action, description, is_system, module) VALUES
    -- 用户相关权限
    ('user', 'read', '读取用户信息', true, 'auth'),
    ('user', 'write', '编辑用户信息', true, 'auth'),
    ('user', 'delete', '删除用户', true, 'auth'),
    ('user', 'create', '创建用户', true, 'auth'),
    ('user', 'manage', '管理用户（包含所有操作）', true, 'auth'),
    
    -- 角色相关权限
    ('role', 'read', '读取角色信息', true, 'rbac'),
    ('role', 'write', '编辑角色信息', true, 'rbac'),
    ('role', 'delete', '删除角色', true, 'rbac'),
    ('role', 'create', '创建角色', true, 'rbac'),
    ('role', 'manage', '管理角色（包含所有操作）', true, 'rbac'),
    
    -- 权限相关权限
    ('permission', 'read', '读取权限信息', true, 'rbac'),
    ('permission', 'assign', '分配权限', true, 'rbac'),
    ('permission', 'revoke', '撤销权限', true, 'rbac'),
    
    -- 文章相关权限
    ('article', 'read', '读取文章', true, 'content'),
    ('article', 'write', '创建/编辑文章', true, 'content'),
    ('article', 'delete', '删除文章', true, 'content'),
    ('article', 'publish', '发布文章', true, 'content'),
    
    -- 订单相关权限
    ('order', 'read', '读取订单', true, 'order'),
    ('order', 'write', '创建/编辑订单', true, 'order'),
    ('order', 'delete', '删除订单', true, 'order'),
    ('order', 'manage', '管理订单', true, 'order')
ON CONFLICT (resource, action) DO NOTHING;

-- 为超级管理员角色分配所有权限
INSERT INTO public.role_permissions (role_id, permission_id, granted_by, granted_at, is_active)
SELECT 
    (SELECT id FROM public.roles WHERE slug = 'super-admin' LIMIT 1),
    id,
    NULL,
    CURRENT_TIMESTAMP,
    true
FROM public.permissions
WHERE is_system = true
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 为管理员角色分配部分权限（排除 user:delete, role:delete）
INSERT INTO public.role_permissions (role_id, permission_id, granted_by, granted_at, is_active)
SELECT 
    (SELECT id FROM public.roles WHERE slug = 'admin' LIMIT 1),
    id,
    NULL,
    CURRENT_TIMESTAMP,
    true
FROM public.permissions
WHERE is_system = true
  AND NOT (resource = 'user' AND action = 'delete')
  AND NOT (resource = 'role' AND action = 'delete')
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 为编辑角色分配内容相关权限
INSERT INTO public.role_permissions (role_id, permission_id, granted_by, granted_at, is_active)
SELECT 
    (SELECT id FROM public.roles WHERE slug = 'editor' LIMIT 1),
    id,
    NULL,
    CURRENT_TIMESTAMP,
    true
FROM public.permissions
WHERE module IN ('content')
  OR (resource = 'user' AND action = 'read')
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 为普通用户角色分配基础权限
INSERT INTO public.role_permissions (role_id, permission_id, granted_by, granted_at, is_active)
SELECT 
    (SELECT id FROM public.roles WHERE slug = 'user' LIMIT 1),
    id,
    NULL,
    CURRENT_TIMESTAMP,
    true
FROM public.permissions
WHERE (resource = 'article' AND action IN ('read'))
   OR (resource = 'order' AND action = 'read')
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 插入示例约束规则
INSERT INTO public.rbac_constraints (constraint_type, name, description, config) VALUES
    ('mutually_exclusive', '出纳员和会计互斥', '用户不能同时拥有出纳员和会计角色', 
     '{"roles": ["cashier", "accountant"], "check_type": "static"}'::jsonb),
    ('cardinality', '管理员角色限制', '管理员角色最多分配给 5 个用户', 
     '{"role": "admin", "max_users": 5}'::jsonb),
    ('prerequisite', '编辑角色先决条件', '用户必须拥有普通用户角色才能分配编辑角色', 
     '{"role": "editor", "required_roles": ["user"]}'::jsonb)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- 8. 创建有用的视图
-- ============================================================================

-- 视图：用户及其所有角色
CREATE OR REPLACE VIEW public.view_user_roles AS
SELECT 
    u.id AS user_id,
    u.username,
    u.email,
    u.full_name,
    u.is_active,
    json_agg(
        json_build_object(
            'id', r.id,
            'name', r.name,
            'slug', r.slug,
            'description', r.description,
            'priority', r.priority,
            'assigned_at', ur.assigned_at,
            'expires_at', ur.expires_at
        ) ORDER BY r.priority DESC
    ) AS roles
FROM public.users u
LEFT JOIN public.user_roles ur ON u.id = ur.user_id AND ur.is_active = true
    AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
LEFT JOIN public.roles r ON ur.role_id = r.id
GROUP BY u.id, u.username, u.email, u.full_name, u.is_active;

-- 视图：角色及其所有权限
CREATE OR REPLACE VIEW public.view_role_permissions AS
SELECT 
    r.id AS role_id,
    r.name,
    r.slug,
    r.description,
    r.is_system,
    r.priority,
    json_agg(
        json_build_object(
            'id', p.id,
            'resource', p.resource,
            'action', p.action,
            'description', p.description,
            'module', p.module
        )
    ) AS permissions
FROM public.roles r
LEFT JOIN public.role_permissions rp ON r.id = rp.role_id AND rp.is_active = true
LEFT JOIN public.permissions p ON rp.permission_id = p.id
GROUP BY r.id, r.name, r.slug, r.description, r.is_system, r.priority;

-- 视图：用户的所有权限（包括从角色继承的）
CREATE OR REPLACE VIEW public.view_user_permissions AS
SELECT DISTINCT
    u.id AS user_id,
    u.username,
    u.email,
    p.id AS permission_id,
    p.resource,
    p.action,
    p.description,
    p.module
FROM public.users u
INNER JOIN public.user_roles ur ON u.id = ur.user_id 
    AND ur.is_active = true 
    AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
INNER JOIN public.role_permissions rp ON ur.role_id = rp.role_id AND rp.is_active = true
INNER JOIN public.permissions p ON rp.permission_id = p.id
ORDER BY u.id, p.module, p.resource, p.action;

-- ============================================================================
-- 完成
-- ============================================================================
-- 迁移成功完成
-- 表结构：
--   - users (用户表)
--   - roles (角色表)
--   - permissions (权限表)
--   - user_roles (用户角色关联表)
--   - role_permissions (角色权限关联表)
--   - rbac_constraints (RBAC 约束规则表)
-- 视图：
--   - view_user_roles (用户及其角色)
--   - view_role_permissions (角色及其权限)
--   - view_user_permissions (用户的所有权限)
-- 初始数据：
--   - 5 个默认角色
--   - 19 个默认权限
--   - 角色权限分配
--   - 3 个示例约束规则
-- ============================================================================
