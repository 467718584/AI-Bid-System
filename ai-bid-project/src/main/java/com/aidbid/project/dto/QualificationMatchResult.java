package com.aidbid.project.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 资质匹配结果DTO
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class QualificationMatchResult {

    /** 匹配状态: FULL_MATCH/PARTIAL_MATCH/NO_MATCH */
    private String status;

    /** 匹配的资质列表 */
    private List<MatchedQualification> matched;

    /** 未匹配的资质要求列表 */
    private List<UnmatchedRequirement> unmatched;

    /** 资质有效期预警列表 */
    private List<ExpirationWarning> warnings;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class MatchedQualification {
        private Long qualificationId;
        private String name;
        private String type;
        private String level;
        private String certificateNo;
        private LocalDateTime validUntil;
        private String status;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class UnmatchedRequirement {
        private String type;
        private String level;
        private String reason;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ExpirationWarning {
        private Long qualificationId;
        private String name;
        private LocalDateTime validUntil;
        private Integer daysUntilExpiration;
        private String warningLevel;
    }
}