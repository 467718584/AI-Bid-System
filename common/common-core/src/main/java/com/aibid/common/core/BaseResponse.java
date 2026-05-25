package com.aibid.common.core;

import lombok.Data;

import java.io.Serializable;

/**
 * 响应基类
 */
@Data
public abstract class BaseResponse implements Serializable {

    private static final long serialVersionUID = 1L;
}