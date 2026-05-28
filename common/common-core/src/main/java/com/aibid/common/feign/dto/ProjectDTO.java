package com.aibid.common.feign.dto;

import lombok.Data;
import java.io.Serializable;
import java.time.LocalDateTime;

@Data
public class ProjectDTO implements Serializable {
    private Long id;
    private String projectName;
    private String projectCode;
    private String bidNumber;
    private Long enterpriseId;
    private String status;
    private Integer deleted;
    private Long createBy;
    private LocalDateTime createTime;
    private Long updateBy;
    private LocalDateTime updateTime;
}