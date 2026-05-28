package com.aidbid.common.core;

import lombok.Data;
import java.io.Serializable;

@Data
public class BaseEntity implements Serializable {
    private Long id;
    private Integer deleted;
    private Long createBy;
    private java.time.LocalDateTime createTime;
    private Long updateBy;
    private java.time.LocalDateTime updateTime;
}