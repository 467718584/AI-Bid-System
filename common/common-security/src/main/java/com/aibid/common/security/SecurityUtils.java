package com.aibid.common.security;

import org.springframework.security.core.context.SecurityContextHolder;

/**
 * 安全工具类
 */
public class SecurityUtils {

    private static final ThreadLocal<LoginUser> USER_HOLDER = new ThreadLocal<>();

    /**
     * 设置当前登录用户
     */
    public void setLoginUser(LoginUser loginUser) {
        USER_HOLDER.set(loginUser);
    }

    /**
     * 获取当前登录用户
     */
    public LoginUser getLoginUser() {
        Object principal = SecurityContextHolder.getContext().getAuthentication().getPrincipal();
        if (principal instanceof LoginUser) {
            return (LoginUser) principal;
        }
        return USER_HOLDER.get();
    }

    /**
     * 获取当前登录用户ID
     */
    public Long getUserId() {
        LoginUser user = getLoginUser();
        return user != null ? user.getUserId() : null;
    }

    /**
     * 获取当前登录用户名
     */
    public String getUsername() {
        LoginUser user = getLoginUser();
        return user != null ? user.getUsername() : null;
    }

    /**
     * 清除当前登录用户
     */
    public void clear() {
        USER_HOLDER.remove();
    }

    /**
     * 判断当前用户是否已登录
     */
    public boolean isAuthenticated() {
        return getLoginUser() != null;
    }
}