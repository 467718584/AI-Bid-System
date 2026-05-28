package com.aibid.common.feign.dto;

import lombok.Data;
import java.io.Serializable;
import java.time.LocalDateTime;

@Data
public class MaterialDTO implements Serializable {
    private Long id;
    private String name;
    private String spec;
    private String unit;
    private Double price;
    private String category;
    private Long enterpriseId;
    private Integer deleted;
    private Long createBy;
    private LocalDateTime createTime;
    private Long updateBy;
    private LocalDateTime updateTime;
}