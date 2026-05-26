package com.aibid.gateway.dto;

import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 监控面板数据DTO
 */
@Data
public class MonitorDashboardDTO implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 总调用次数 */
    private Long totalCallCount;

    /** 今日调用次数 */
    private Long todayCallCount;

    /** 平均响应时间(ms) */
    private Long avgResponseTime;

    /** 今日总费用 */
    private BigDecimal todayTotalCost;

    /** 模型列表 */
    private List<ModelStatsDTO> modelStats;

    /** 每日调用量趋势 (最近7天) */
    private List<DailyCallTrend> dailyTrends;

    /** 模型切换记录 */
    private List<ModelSwitchRecord> switchRecords;

    /**
     * 每日调用趋势
     */
    @Data
    public static class DailyCallTrend implements Serializable {
        private LocalDateTime date;
        private Long callCount;
        private BigDecimal totalCost;
        private Long avgResponseTime;
    }

    /**
     * 模型切换记录
     */
    @Data
    public static class ModelSwitchRecord implements Serializable {
        private Long id;
        private String sourceModel;
        private String targetModel;
        private String reason;
        private LocalDateTime triggerTime;
    }
}