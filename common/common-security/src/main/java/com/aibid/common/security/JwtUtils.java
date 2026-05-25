package com.aibid.common.security;

import com.aibid.common.core.Constants;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.UnsupportedJwtException;
import io.jsonwebtoken.security.Keys;
import lombok.extern.slf4j.Slf4j;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

/**
 * JWT工具类
 */
@Slf4j
public class JwtUtils {

    private static final SecretKey KEY = Keys.hmacShaKeyFor(
            Constants.JWT_SECRET_KEY.getBytes(StandardCharsets.UTF_8));

    /**
     * 生成Token
     */
    public static String generateToken(LoginUser loginUser) {
        long now = System.currentTimeMillis();
        long expire = now + Constants.JWT_EXPIRE_TIME;

        return Jwts.builder()
                .subject(String.valueOf(loginUser.getUserId()))
                .claim("username", loginUser.getUsername())
                .claim("nickname", loginUser.getNickname())
                .claim("roleIds", loginUser.getRoleIds())
                .claim("permissions", loginUser.getPermissions())
                .issuedAt(new Date(now))
                .expiration(new Date(expire))
                .signWith(KEY)
                .compact();
    }

    /**
     * 解析Token
     */
    public static Claims parseToken(String token) {
        return Jwts.parser()
                .verifyWith(KEY)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    /**
     * 获取用户ID
     */
    public static Long getUserId(String token) {
        Claims claims = parseToken(token);
        return Long.valueOf(claims.getSubject());
    }

    /**
     * 获取用户名
     */
    public static String getUsername(String token) {
        Claims claims = parseToken(token);
        return claims.get("username", String.class);
    }

    /**
     * 验证Token是否有效
     */
    public static boolean validateToken(String token) {
        try {
            parseToken(token);
            return true;
        } catch (ExpiredJwtException e) {
            log.warn("JWT token expired: {}", e.getMessage());
        } catch (MalformedJwtException e) {
            log.warn("JWT token malformed: {}", e.getMessage());
        } catch (UnsupportedJwtException e) {
            log.warn("JWT token unsupported: {}", e.getMessage());
        } catch (IllegalArgumentException e) {
            log.warn("JWT token illegal argument: {}", e.getMessage());
        }
        return false;
    }

    /**
     * 判断Token是否过期
     */
    public static boolean isTokenExpired(String token) {
        try {
            Claims claims = parseToken(token);
            return claims.getExpiration().before(new Date());
        } catch (ExpiredJwtException e) {
            return true;
        }
    }

    /**
     * 刷新Token
     */
    public static String refreshToken(String token) {
        Claims claims = parseToken(token);
        long now = System.currentTimeMillis();
        long expire = now + Constants.JWT_EXPIRE_TIME;

        return Jwts.builder()
                .subject(claims.getSubject())
                .claim("username", claims.get("username"))
                .claim("nickname", claims.get("nickname"))
                .claim("roleIds", claims.get("roleIds"))
                .claim("permissions", claims.get("permissions"))
                .issuedAt(new Date(now))
                .expiration(new Date(expire))
                .signWith(KEY)
                .compact();
    }

    /**
     * 从Token中提取LoginUser
     */
    public static LoginUser getLoginUser(String token) {
        Claims claims = parseToken(token);
        LoginUser user = new LoginUser();
        user.setUserId(Long.valueOf(claims.getSubject()));
        user.setUsername(claims.get("username", String.class));
        user.setNickname(claims.get("nickname", String.class));
        user.setToken(token);
        user.setExpireTime(claims.getExpiration().getTime());
        return user;
    }
}