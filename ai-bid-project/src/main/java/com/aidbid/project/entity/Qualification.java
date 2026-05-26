package com.aidbid.project.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 资质证书实体
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("bid_qualification")
public class Qualification extends BaseEntity {

    /** 资质名称 */
    private String name;

    /** 资质类型: 施工/设计/监理/勘察等 */
    private String type;

    /** 资质等级: 特级/一级/二级/三级 */
    private String level;

    /** 资质编号 */
    private String certificateNo;

    /** 资质有效期起始 */
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDateTime validFrom;

    /** 资质有效期截止 */
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDateTime validUntil;

    /** 颁发机构 */
    private String issuingAuthority;

    /** 证书图片路径 */
    private String certificateImage;

    /** 关联项目ID */
    private Long projectId;

    /** 关联企业ID */
    private Long enterpriseId;

    /** 资质状态: ACTIVE/EXPIRED/REVOKED */
    private String status;

    /** 备注 */
    private String remark;
}