package com.aidbid.project.entity;

import com.aibid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

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

    /** 投标截止时间 */
    private java.time.LocalDateTime deadline;

    /** 项目状态 */
    private String status;

    /** 项目描述 */
    private String description;

    /** 甲方联系人 */
    private String contactPerson;

    /** 甲方联系电话 */
    private String contactPhone;
}
