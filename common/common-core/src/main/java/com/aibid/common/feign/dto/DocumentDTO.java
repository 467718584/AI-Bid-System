package com.aibid.common.feign.dto;

import lombok.Data;
import java.io.Serializable;
import java.time.LocalDateTime;

@Data
public class DocumentDTO implements Serializable {
    private Long id;
    private String title;
    private String content;
    private String docType;
    private Long projectId;
    private Long enterpriseId;
    private String fileUrl;
    private String status;
    private Integer deleted;
    private Long createBy;
    private LocalDateTime createTime;
    private Long updateBy;
    private LocalDateTime updateTime;
}