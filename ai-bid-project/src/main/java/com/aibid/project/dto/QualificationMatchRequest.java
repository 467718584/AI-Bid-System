package com.aibid.project.dto;

import lombok.Data;

import java.util.List;

/**
 * 资质匹配请求DTO
 */
@Data
public class QualificationMatchRequest {

    /** 招标文件中的资质要求列表 */
    private List<QualificationRequirement> requirements;

    @Data
    public static class QualificationRequirement {
        /** 资质类型 */
        private String type;
        /** 资质等级要求 */
        private String level;
        /** 是否必须 */
        private Boolean required;
        /** 备注说明 */
        private String remark;
    }
}