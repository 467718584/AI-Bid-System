package com.aidbid.common.core;

import lombok.Data;
import java.io.Serializable;
import java.util.List;

@Data
public class PageResponse<T> implements Serializable {
    private long pageNum;
    private long pageSize;
    private long total;
    private long pages;
    private List<T> list;

    public static <T> PageResponse<T> of(long pageNum, long pageSize, long total, List<T> list) {
        PageResponse<T> response = new PageResponse<>();
        response.setPageNum(pageNum);
        response.setPageSize(pageSize);
        response.setTotal(total);
        response.setPages((total + pageSize - 1) / pageSize);
        response.setList(list);
        return response;
    }
}