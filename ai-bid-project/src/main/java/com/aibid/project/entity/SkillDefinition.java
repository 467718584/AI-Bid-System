package com.aibid.project.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 技能定义实体 - 定义AI技能的结构、参数和输出
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("bid_skill_definition")
public class SkillDefinition extends BaseEntity {

    /** 技能唯一标识 */
    private String skillId;

    /** 技能名称 */
    private String name;

    /** 技能描述 */
    private String description;

    /** 技能版本 */
    private String version;

    /** 技能分类ID */
    private Long catalogId;

    /** 技能类型: PARSER/GENERATOR/MATCHER/EXPORT/UTILITY */
    private String type;

    /** 技能实现类名 */
    private String handlerClass;

    /** 输入参数JSON Schema */
    private String inputSchema;

    /** 输出参数JSON Schema */
    private String outputSchema;

    /** 默认参数 */
    private String defaultParams;

    /** 依赖技能列表(JSON数组) */
    private String dependencies;

    /** 执行超时时间(秒) */
    private Integer timeout;

    /** 是否启用 */
    private Boolean enabled;

    /** 技能标签(JSON数组) */
    private String tags;

    /** 优先级 */
    private Integer priority;
}