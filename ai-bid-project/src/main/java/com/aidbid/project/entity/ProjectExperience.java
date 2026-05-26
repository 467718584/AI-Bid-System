package com.aidbid.project.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 业绩案例实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("bid_project_experience")
public class ProjectExperience extends BaseEntity {

    /** 项目名称 */
    private String projectName;

    /** 项目类型 */
    private String projectType;

    /** 项目规模分类: 大型/中型/小型 */
    private String scale;

    /** 中标金额(万元) */
    private BigDecimal bidAmount;

    /** 中标日期 */
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDateTime bidDate;

    /** 合同工期(天) */
    private Integer contractDuration;

    /** 实际完工日期 */
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDateTime actualCompletionDate;

    /** 甲方单位 */
    private String client;

    /** 甲方联系人 */
    private String clientContact;

    /** 甲方联系电话 */
    private String clientPhone;

    /** 项目地址 */
    private String location;

    /** 项目描述 */
    private String description;

    /** 合同文件路径 */
    private String contractFile;

    /** 验收文件路径 */
    private String acceptanceFile;

    /** 项目质量评级: 优良/合格 */
    private String qualityRating;

    /** 是否入库: 0=否, 1=是 */
    private Integer isArchived;

    /** 关联企业ID */
    private Long enterpriseId;

    /** 关联投标项目ID */
    private Long bidProjectId;
}