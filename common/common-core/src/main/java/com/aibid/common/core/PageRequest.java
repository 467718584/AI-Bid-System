package com.aibid.common.core;

import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;

/**
 * 分页请求对象
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class PageRequest<T> extends BaseRequest implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 当前页码，默认1 */
    private Integer pageNum = 1;

    /** 每页条数，默认20 */
    private Integer pageSize = 20;

    /** 排序字段 */
    private String orderBy;

    /** 排序方式：asc / desc */
    private String orderDirection = "desc";

    /** 搜索关键字 */
    private String keyword;

    /**
     * 获取偏移量
     */
    public long getOffset() {
        return (long) (pageNum - 1) * pageSize;
    }
}