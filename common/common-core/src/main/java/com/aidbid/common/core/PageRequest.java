package com.aidbid.common.core;

import lombok.Data;
import java.io.Serializable;

@Data
public class PageRequest implements Serializable {
    private long pageNum = 1;
    private long pageSize = 10;
    private String orderBy;
    private boolean ascending = true;
}