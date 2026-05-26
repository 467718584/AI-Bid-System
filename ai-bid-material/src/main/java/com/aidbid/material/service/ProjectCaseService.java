package com.aibid.material.service;

import com.aibid.common.core.BusinessException;
import com.aibid.common.core.ResultCode;
import com.aibid.material.entity.ProjectCase;
import com.aibid.material.mapper.ProjectCaseMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ProjectCaseService {

    private final ProjectCaseMapper projectCaseMapper;

    public ProjectCase getById(Long id) {
        ProjectCase projectCase = projectCaseMapper.selectById(id);
        if (projectCase == null) {
            throw new BusinessException(ResultCode.NOT_FOUND, "业绩案例不存在");
        }
        return projectCase;
    }

    public List<ProjectCase> listByEnterpriseId(Long enterpriseId) {
        return projectCaseMapper.selectList(
            new LambdaQueryWrapper<ProjectCase>()
                .eq(ProjectCase::getEnterpriseId, enterpriseId)
                .eq(ProjectCase::getStatus, 1)
                .orderByDesc(ProjectCase::getWinDate)
        );
    }

    public List<ProjectCase> listByIndustry(String industry) {
        return projectCaseMapper.selectList(
            new LambdaQueryWrapper<ProjectCase>()
                .eq(ProjectCase::getIndustry, industry)
                .eq(ProjectCase::getStatus, 1)
                .orderByDesc(ProjectCase::getWinDate)
        );
    }

    public List<ProjectCase> listFeatured() {
        return projectCaseMapper.selectList(
            new LambdaQueryWrapper<ProjectCase>()
                .eq(ProjectCase::getShowOnHomepage, 1)
                .eq(ProjectCase::getStatus, 1)
                .orderByDesc(ProjectCase::getWinDate)
        );
    }

    public void save(ProjectCase projectCase) {
        projectCaseMapper.insert(projectCase);
    }

    public void update(ProjectCase projectCase) {
        if (projectCase.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        projectCaseMapper.updateById(projectCase);
    }

    public void delete(Long id) {
        projectCaseMapper.deleteById(id);
    }
}