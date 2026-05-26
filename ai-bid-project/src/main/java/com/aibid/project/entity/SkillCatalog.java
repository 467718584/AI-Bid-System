package com.aibid.project.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 技能分类目录实体 - 对技能进行分组管理
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("bid_skill_catalog")
public class SkillCatalog extends BaseEntity {

    /** 分类编码 */
    private String code;

    /** 分类名称 */
    private String name;

    /** 分类描述 */
    private String description;

    /** 父分类ID */
    private Long parentId;

    /** 排序号 */
    private Integer sortOrder;

    /** 图标 */
    private String icon;

    /** 是否启用 */
    private Boolean enabled;
}