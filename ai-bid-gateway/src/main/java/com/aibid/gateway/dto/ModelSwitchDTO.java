package com.aibid.gateway.dto;

import lombok.Data;

import java.io.Serializable;

/**
 * 模型切换请求DTO
 */
@Data
public class ModelSwitchDTO implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 目标模型ID */
    private Long modelId;

    /** 切换原因 */
    private String reason;
}