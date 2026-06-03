package com.aidbid.bid.entity;

import com.aidbid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

/**
 * 投标项目实体类
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("bid_project")
public class BidProject extends BaseEntity {

    /** 项目名称 */
    private String name;

    /** 项目编号 */
    private String code;

    /** 项目类型 */
    private String type;

    /** 招标金额 */
    private java.math.BigDecimal amount;

    /** 招标单位 */
    private String tenderer;

    /** 甲方联系人 */
    private String contactPerson;

    /** 甲方联系电话 */
    private String contactPhone;

    /** 投标截止时间 */
    private LocalDateTime deadline;

    /** 项目状态 (DRAFT/IN_PROGRESS/SUBMITTED/COMPLETED/CANCELLED) */
    private String status;

    /** 项目描述 */
    private String description;

    /** 标书内容 (JSON格式) */
    private String content;

    /** 标书大纲 (JSON格式) */
    private String outline;
}
