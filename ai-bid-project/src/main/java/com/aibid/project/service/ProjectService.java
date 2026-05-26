package com.aibid.project.service;

import com.aibid.common.core.BusinessException;
import com.aibid.common.core.ResultCode;
import com.aibid.project.entity.BidProject;
import com.aibid.project.mapper.ProjectMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ProjectService {

    private final ProjectMapper projectMapper;

    public BidProject getById(Long id) {
        BidProject project = projectMapper.selectById(id);
        if (project == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }
        return project;
    }

    public List<BidProject> list() {
        return projectMapper.selectList(new LambdaQueryWrapper<>());
    }

    public List<BidProject> listByStatus(String status) {
        return projectMapper.selectList(new LambdaQueryWrapper<BidProject>().eq(BidProject::getStatus, status));
    }

    public void save(BidProject project) {
        projectMapper.insert(project);
    }

    public void update(BidProject project) {
        if (project.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        projectMapper.updateById(project);
    }

    public void delete(Long id) {
        projectMapper.deleteById(id);
    }

    public long count() {
        return projectMapper.selectCount(null);
    }
}
