package com.aidbid.project.service;

import com.aidbid.common.core.BusinessException;
import com.aidbid.common.core.ResultCode;
import com.aidbid.project.entity.BidProject;
import com.aidbid.project.mapper.ProjectMapper;
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
        return projectMapper.selectList();
    }

    public List<BidProject> listByStatus(String status) {
        return projectMapper.selectList().stream()
            .filter(p -> status.equals(p.getStatus()))
            .toList();
    }

    public BidProject save(BidProject project) {
        if (project.getId() == null) {
            project.setId(System.currentTimeMillis());
        }
        projectMapper.insert(project);
        return project;
    }

    public void update(BidProject project) {
        if (project.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        projectMapper.update(project);
    }

    public void delete(Long id) {
        projectMapper.deleteById(id);
    }

    public long count() {
        return projectMapper.selectList().size();
    }
}
