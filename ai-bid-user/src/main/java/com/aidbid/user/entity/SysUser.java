package com.aidbid.user.entity;

import com.aidbid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("sys_user")
public class SysUser extends BaseEntity {

    /** 用户名 */
    private String username;

    /** 密码 */
    private String password;

    /** 昵称 */
    private String nickname;

    /** 邮箱 */
    private String email;

    /** 手机号 */
    private String phone;

    /** 头像 */
    private String avatar;

    /** 性别 (0=未知, 1=男, 2=女) */
    private Integer gender;

    /** 部门ID */
    private Long deptId;

    /** 状态 (0=正常, 1=禁用) */
    private Integer status;

    /** 最后登录IP */
    private String lastLoginIp;

    /** 最后登录时间 */
    private java.time.LocalDateTime lastLoginTime;

    /** 备注 */
    private String remark;
}
