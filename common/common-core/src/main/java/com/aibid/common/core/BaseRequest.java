package com.aibid.common.core;

import lombok.Data;

import java.io.Serializable;

/**
 * 请求基类
 */
@Data
public abstract class BaseRequest implements Serializable {

    private static final long serialVersionUID = 1L;
}