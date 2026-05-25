package com.aibid.common.security;

import com.aibid.common.core.ResultCode;
import lombok.Data;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

/**
 * 登录用户信息
 */
@Data
public class LoginUser implements UserDetails {

    private static final long serialVersionUID = 1L;

    /** 用户ID */
    private Long userId;

    /** 用户名 */
    private String username;

    /** 密码 */
    private String password;

    /** 昵称 */
    private String nickname;

    /** 头像 */
    private String avatar;

    /** 部门ID */
    private Long deptId;

    /** 角色ID列表 */
    private Set<Long> roleIds = new HashSet<>();

    /** 权限标识列表 */
    private Set<String> permissions = new HashSet<>();

    /** 状态（0=正常, 1=禁用） */
    private Integer status;

    /** Token */
    private String token;

    /** 登录时间 */
    private Long loginTime;

    /** 过期时间 */
    private Long expireTime;

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return new HashSet<>();
    }

    @Override
    public String getPassword() {
        return this.password;
    }

    @Override
    public String getUsername() {
        return this.username;
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return this.status == null || this.status == 0;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        if (expireTime == null) {
            return true;
        }
        return System.currentTimeMillis() < expireTime;
    }

    @Override
    public boolean isEnabled() {
        return this.status == null || this.status == 0;
    }

    /**
     * 是否超管
     */
    public boolean isSuperAdmin() {
        return this.userId != null && this.userId == 1L;
    }

    /**
     * 是否有某个权限
     */
    public boolean hasPermission(String permission) {
        return isSuperAdmin() || this.permissions.contains(permission);
    }

    /**
     * 是否有某个角色
     */
    public boolean hasRole(Long roleId) {
        return isSuperAdmin() || this.roleIds.contains(roleId);
    }
}