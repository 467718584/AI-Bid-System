package com.aibid.material.entity;

import com.aibid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 团队成员
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("enterprise_team_member")
public class TeamMember extends BaseEntity {

    /** 企业ID */
    private Long enterpriseId;

    /** 成员姓名 */
    private String name;

    /** 职位/职称 */
    private String position;

    /** 部门 */
    private String department;

    /** 学历 */
    private String education;

    /** 从业年限 */
    private Integer experienceYears;

    /** 专业 */
    private String major;

    /** 证书编号 */
    private String certificateNo;

    /** 是否核心负责人: 0=否, 1=是 */
    private Integer isLeader;

    /** 头像路径 */
    private String avatarPath;

    /** 联系电话 */
    private String phone;

    /** 邮箱 */
    private String email;

    /** 个人简介 */
    private String bio;

    /** 主要业绩/成就 */
    private String achievements;

    /** 排序 */
    private Integer sort;

    /** 状态: 0=禁用, 1=启用 */
    private Integer status;
}