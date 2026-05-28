package com.aidbid.common.core;

import lombok.Data;
import java.io.Serializable;

@Data
public class BusinessException extends RuntimeException implements Serializable {
    private int code;
    private String message;

    public BusinessException(int code, String message) {
        super(message);
        this.code = code;
        this.message = message;
    }

    public BusinessException(ResultCode resultCode) {
        super(resultCode.getMessage());
        this.code = resultCode.getCode();
        this.message = resultCode.getMessage();
    }
}