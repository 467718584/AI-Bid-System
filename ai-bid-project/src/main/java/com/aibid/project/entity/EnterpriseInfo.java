package com.aibid.project.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 企业信息实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("bid_enterprise_info")
public class EnterpriseInfo extends BaseEntity {

    /** 企业名称 */
    private String name;

    /** 统一社会信用代码 */
    private String unifiedCreditCode;

    /** 企业类型: 国有/民营/外资等 */
    private String type;

    /** 所属行业 */
    private String industry;

    /** 注册资本(万元) */
    private BigDecimal registeredCapital;

    /** 实缴资本(万元) */
    private BigDecimal paidInCapital;

    /** 成立日期 */
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDateTime establishedDate;

    /** 营业期限起始 */
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDateTime businessFrom;

    /** 营业期限截止 */
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDateTime businessUntil;

    /** 法定代表人 */
    private String legalPerson;

    /** 联系电话 */
    private String contactPhone;

    /** 联系地址 */
    private String address;

    /** 营业执照图片路径 */
    private String businessLicenseImage;

    /** 企业简介 */
    private String description;

    /** 资质总数 */
    private Integer qualificationCount;

    /** 资质状态: ACTIVE/SUSPENDED/REVOKED */
    private String status;
}