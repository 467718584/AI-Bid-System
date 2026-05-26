package com.aibid.material.service;

import com.aibid.common.core.BusinessException;
import com.aibid.common.core.ResultCode;
import com.aibid.material.entity.EnterpriseProfile;
import com.aibid.material.mapper.EnterpriseProfileMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class EnterpriseProfileService {

    private final EnterpriseProfileMapper enterpriseProfileMapper;

    public EnterpriseProfile getById(Long id) {
        EnterpriseProfile profile = enterpriseProfileMapper.selectById(id);
        if (profile == null) {
            throw new BusinessException(ResultCode.NOT_FOUND, "企业档案不存在");
        }
        return profile;
    }

    public List<EnterpriseProfile> list() {
        return enterpriseProfileMapper.selectList(
            new LambdaQueryWrapper<EnterpriseProfile>()
                .eq(EnterpriseProfile::getStatus, 1)
                .orderByDesc(EnterpriseProfile::getCreateTime)
        );
    }

    public List<EnterpriseProfile> listActive() {
        return enterpriseProfileMapper.selectList(
            new LambdaQueryWrapper<EnterpriseProfile>()
                .eq(EnterpriseProfile::getStatus, 1)
                .orderByDesc(EnterpriseProfile::getCreateTime)
        );
    }

    public void save(EnterpriseProfile profile) {
        enterpriseProfileMapper.insert(profile);
    }

    public void update(EnterpriseProfile profile) {
        if (profile.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        enterpriseProfileMapper.updateById(profile);
    }

    public void delete(Long id) {
        enterpriseProfileMapper.deleteById(id);
    }

    public long count() {
        return enterpriseProfileMapper.selectCount(
            new LambdaQueryWrapper<EnterpriseProfile>().eq(EnterpriseProfile::getStatus, 1)
        );
    }
}