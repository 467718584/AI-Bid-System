package com.aidbid.material.service;

import com.aibid.common.core.BusinessException;
import com.aibid.common.core.ResultCode;
import com.aidbid.material.entity.BidMaterial;
import com.aidbid.material.mapper.MaterialMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class MaterialService {

    private final MaterialMapper materialMapper;

    public BidMaterial getById(Long id) {
        BidMaterial material = materialMapper.selectById(id);
        if (material == null) {
            throw new BusinessException(ResultCode.NOT_FOUND);
        }
        return material;
    }

    public List<BidMaterial> list() {
        return materialMapper.selectList();
    }

    public List<BidMaterial> listByProjectId(Long projectId) {
        return materialMapper.selectByProjectId(projectId);
    }

    public List<BidMaterial> listByStatus(String status) {
        return materialMapper.selectByStatus(status);
    }

    public void save(BidMaterial material) {
        material.setCreateTime(LocalDateTime.now());
        materialMapper.insert(material);
    }

    public void update(BidMaterial material) {
        if (material.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        material.setUpdateTime(LocalDateTime.now());
        materialMapper.updateById(material);
    }

    public void delete(Long id) {
        materialMapper.deleteById(id);
    }

    public long count() {
        return materialMapper.selectCount();
    }

    public long countByProjectId(Long projectId) {
        return materialMapper.selectCountByProjectId(projectId);
    }
}
