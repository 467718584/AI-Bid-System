package com.aidbid.material.service;

import com.aibid.common.core.BusinessException;
import com.aibid.common.core.ResultCode;
import com.aibid.material.entity.BidMaterial;
import com.aibid.material.mapper.MaterialMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class MaterialService {

    private final MaterialMapper materialMapper;

    public BidMaterial getById(Long id) {
        BidMaterial material = materialMapper.selectById(id);
        if (material == null) {
            throw new BusinessException(ResultCode.MATERIAL_NOT_FOUND);
        }
        return material;
    }

    public List<BidMaterial> list() {
        return materialMapper.selectList(new LambdaQueryWrapper<>());
    }

    public List<BidMaterial> listByProjectId(Long projectId) {
        return materialMapper.selectList(new LambdaQueryWrapper<BidMaterial>().eq(BidMaterial::getProjectId, projectId));
    }

    public List<BidMaterial> listByStatus(String status) {
        return materialMapper.selectList(new LambdaQueryWrapper<BidMaterial>().eq(BidMaterial::getStatus, status));
    }

    public void save(BidMaterial material) {
        materialMapper.insert(material);
    }

    public void update(BidMaterial material) {
        if (material.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        materialMapper.updateById(material);
    }

    public void delete(Long id) {
        materialMapper.deleteById(id);
    }

    public long count() {
        return materialMapper.selectCount(null);
    }

    public long countByProjectId(Long projectId) {
        return materialMapper.selectCount(new LambdaQueryWrapper<BidMaterial>().eq(BidMaterial::getProjectId, projectId));
    }
}
