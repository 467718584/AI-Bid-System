package com.aidbid.material.entity;

import com.aibid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * 业绩案例
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("enterprise_project_case")
public class ProjectCase extends BaseEntity {

    /** 企业ID */
    private Long enterpriseId;

    /** 项目名称 */
    private String projectName;

    /** 项目类型 */
    private String projectType;

    /** 所属行业 */
    private String industry;

    /** 招标单位/甲方 */
    private String tenderer;

    /** 中标金额 */
    private BigDecimal tenderAmount;

    /** 投标金额 */
    private BigDecimal bidAmount;

    /** 中标日期 */
    private LocalDate winDate;

    /** 开始日期 */
    private LocalDate startDate;

    /** 结束日期 */
    private LocalDate endDate;

    /** 项目状态: IN_PROGRESS/COMPLETED/SUSPENDED */
    private String projectStatus;

    /** 项目描述 */
    private String description;

    /** 项目亮点 */
    private String keyHighlights;

    /** 业绩金额 */
    private BigDecimal performanceAmount;

    /** 业绩范围 */
    private String performanceScope;

    /** 合同编号 */
    private String contractNo;

    /** 甲方联系人 */
    private String contactPerson;

    /** 甲方联系电话 */
    private String contactPhone;

    /** 甲方评价等级 */
    private String evaluationRating;

    /** 甲方评价备注 */
    private String evaluationRemark;

    /** 是否首页展示: 0=否, 1=是 */
    private Integer showOnHomepage;

    /** 状态: 0=禁用, 1=启用 */
    private Integer status;
}