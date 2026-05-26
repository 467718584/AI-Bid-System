package com.aidbid.material.entity;

import com.aibid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 素材使用记录
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("material_usage_log")
public class MaterialUsageLog extends BaseEntity {

    /** 素材ID */
    private Long materialId;

    /** 使用用户ID */
    private Long userId;

    /** 使用类型: DOWNLOAD/VIEW/EMBED/CITE */
    private String usageType;

    /** 使用场景/文档名 */
    private String usageContext;

    /** 使用项目ID */
    private Long usageProjectId;
}