package com.aibid.material.entity;

import com.aibid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDate;

/**
 * 企业证书资质
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("enterprise_certificate")
public class Certificate extends BaseEntity {

    /** 企业ID */
    private Long enterpriseId;

    /** 证书名称 */
    private String name;

    /** 证书类型: QUALIFICATION/CREDIT/ISO/PATENT/AWARD */
    private String certificateType;

    /** 证书编号 */
    private String certificateNo;

    /** 发证机构 */
    private String issuingAuthority;

    /** 发证日期 */
    private LocalDate issueDate;

    /** 到期日期 */
    private LocalDate expiryDate;

    /** 证书等级 */
    private String certificateLevel;

    /** 证书文件路径 */
    private String filePath;

    /** 证书文件URL */
    private String fileUrl;

    /** 是否已认证: 0=未认证, 1=已认证 */
    private Integer isVerified;

    /** 状态: 0=禁用, 1=启用 */
    private Integer status;
}