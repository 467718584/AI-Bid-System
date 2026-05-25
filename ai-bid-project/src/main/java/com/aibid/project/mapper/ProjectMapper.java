package com.aibid.project.mapper;

import com.aibid.project.entity.BidProject;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface ProjectMapper extends BaseMapper<BidProject> {
}
