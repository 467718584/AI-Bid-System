package com.aibid.document.mapper;

import com.aibid.document.entity.BidDocument;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface DocumentMapper extends BaseMapper<BidDocument> {
}
