package com.aibid.common.core;

import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.util.List;

/**
 * 分页响应对象
 *
 * @param <T> 数据类型
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class PageResponse<T> extends BaseResponse implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 当前页码 */
    private long pageNum;

    /** 每页条数 */
    private long pageSize;

    /** 总记录数 */
    private long total;

    /** 总页数 */
    private long pages;

    /** 数据列表 */
    private List<T> list;

    /**
     * 构建分页响应
     */
    public static <T> PageResponse<T> of(long pageNum, long pageSize, long total, List<T> list) {
        PageResponse<T> response = new PageResponse<>();
        response.setPageNum(pageNum);
        response.setPageSize(pageSize);
        response.setTotal(total);
        response.setPages((total + pageSize - 1) / pageSize);
        response.setList(list);
        return response;
    }

    /**
     * 从MyBatis Plus IPage构建
     */
    public static <T> PageResponse<T> from(com.baomidou.mybatisplus.core.metadata.IPage<T> page) {
        return of(page.getCurrent(), page.getSize(), page.getTotal(), page.getRecords());
    }
}