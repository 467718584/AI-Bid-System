package com.aidbid.material.entity;

import com.aibid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDate;

/**
 * 企业档案
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("enterprise_profile")
public class EnterpriseProfile extends BaseEntity {

    /** 企业名称 */
    private String name;

    /** 企业简称 */
    private String shortName;

    /** 企业Logo路径 */
    private String logo;

    /** 企业地址 */
    private String address;

    /** 法定代表人 */
    private String legalPerson;

    /** 联系人 */
    private String contactPerson;

    /** 联系电话 */
    private String contactPhone;

    /** 联系邮箱 */
    private String contactEmail;

    /** 官网地址 */
    private String website;

    /** 经营范围 */
    private String businessScope;

    /** 注册资本 */
    private String registeredCapital;

    /** 成立日期 */
    private LocalDate establishedDate;

    /** 企业简介 */
    private String description;

    /** 主要产品/服务 */
    private String mainProducts;

    /** 核心优势 */
    private String coreAdvantages;

    /** 年营业额 */
    private String annualRevenue;

    /** 员工规模 */
    private String employeeCount;

    /** 资质等级 */
    private String qualificationLevel;

    /** 状态: 0=禁用, 1=启用 */
    private Integer status;
}