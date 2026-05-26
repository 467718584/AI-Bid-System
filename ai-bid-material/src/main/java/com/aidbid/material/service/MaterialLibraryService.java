package com.aidbid.material.service;

import com.aibid.common.core.BusinessException;
import com.aibid.common.core.ResultCode;
import com.aibid.material.entity.MaterialLibrary;
import com.aibid.material.entity.MaterialUsageLog;
import com.aibid.material.mapper.MaterialLibraryMapper;
import com.aibid.material.mapper.MaterialUsageLogMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Arrays;
import java.util.List;

@Service
@RequiredArgsConstructor
public class MaterialLibraryService {

    private final MaterialLibraryMapper materialLibraryMapper;
    private final MaterialUsageLogMapper usageLogMapper;

    public MaterialLibrary getById(Long id) {
        MaterialLibrary material = materialLibraryMapper.selectById(id);
        if (material == null) {
            throw new BusinessException(ResultCode.NOT_FOUND, "素材不存在");
        }
        return material;
    }

    public List<MaterialLibrary> list() {
        return materialLibraryMapper.selectList(
            new LambdaQueryWrapper<MaterialLibrary>()
                .eq(MaterialLibrary::getStatus, "ACTIVE")
                .orderByDesc(MaterialLibrary::getCreateTime)
        );
    }

    public List<MaterialLibrary> listByType(String type) {
        return materialLibraryMapper.selectList(
            new LambdaQueryWrapper<MaterialLibrary>()
                .eq(MaterialLibrary::getType, type)
                .eq(MaterialLibrary::getStatus, "ACTIVE")
                .orderByDesc(MaterialLibrary::getCreateTime)
        );
    }

    public List<MaterialLibrary> listByCategory(String category) {
        return materialLibraryMapper.selectList(
            new LambdaQueryWrapper<MaterialLibrary>()
                .eq(MaterialLibrary::getCategory, category)
                .eq(MaterialLibrary::getStatus, "ACTIVE")
                .orderByDesc(MaterialLibrary::getCreateTime)
        );
    }

    public List<MaterialLibrary> listByTags(List<String> tags) {
        LambdaQueryWrapper<MaterialLibrary> wrapper = new LambdaQueryWrapper<MaterialLibrary>()
            .eq(MaterialLibrary::getStatus, "ACTIVE");
        for (String tag : tags) {
            wrapper.like(MaterialLibrary::getTags, tag);
        }
        return materialLibraryMapper.selectList(wrapper);
    }

    public List<MaterialLibrary> search(String keyword) {
        LambdaQueryWrapper<MaterialLibrary> wrapper = new LambdaQueryWrapper<MaterialLibrary>()
            .eq(MaterialLibrary::getStatus, "ACTIVE")
            .and(w -> w.like(MaterialLibrary::getName, keyword)
                .or()
                .like(MaterialLibrary::getDescription, keyword)
                .or()
                .like(MaterialLibrary::getTags, keyword)
            );
        return materialLibraryMapper.selectList(wrapper);
    }

    public void save(MaterialLibrary material) {
        materialLibraryMapper.insert(material);
    }

    public void update(MaterialLibrary material) {
        if (material.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        materialLibraryMapper.updateById(material);
    }

    public void delete(Long id) {
        materialLibraryMapper.deleteById(id);
    }

    @Transactional
    public void recordUsage(Long materialId, Long userId, String usageType, String usageContext) {
        MaterialUsageLog log = new MaterialUsageLog();
        log.setMaterialId(materialId);
        log.setUserId(userId);
        log.setUsageType(usageType);
        log.setUsageContext(usageContext);
        usageLogMapper.insert(log);

        materialLibraryMapper.update(null,
            new LambdaUpdateWrapper<MaterialLibrary>()
                .eq(MaterialLibrary::getId, materialId)
                .setSql("usage_count = usage_count + 1")
        );
    }

    public List<MaterialUsageLog> getUsageLogs(Long materialId) {
        return usageLogMapper.selectList(
            new LambdaQueryWrapper<MaterialUsageLog>()
                .eq(MaterialUsageLog::getMaterialId, materialId)
                .orderByDesc(MaterialUsageLog::getCreateTime)
        );
    }

    public List<MaterialUsageLog> getUsageLogsByProject(Long projectId) {
        return usageLogMapper.selectList(
            new LambdaQueryWrapper<MaterialUsageLog>()
                .eq(MaterialUsageLog::getUsageProjectId, projectId)
                .orderByDesc(MaterialUsageLog::getCreateTime)
        );
    }

    public List<String> listCategories() {
        List<MaterialLibrary> materials = materialLibraryMapper.selectList(
            new LambdaQueryWrapper<MaterialLibrary>()
                .select(MaterialLibrary::getCategory)
                .eq(MaterialLibrary::getStatus, "ACTIVE")
                .isNotNull(MaterialLibrary::getCategory)
                .groupBy(MaterialLibrary::getCategory)
        );
        return materials.stream().map(MaterialLibrary::getCategory).filter(c -> c != null).toList();
    }

    public List<MaterialLibrary> recommendByContext(String context, int limit) {
        LambdaQueryWrapper<MaterialLibrary> wrapper = new LambdaQueryWrapper<MaterialLibrary>()
            .eq(MaterialLibrary::getStatus, "ACTIVE")
            .and(w -> w.like(MaterialLibrary::getName, context)
                .or()
                .like(MaterialLibrary::getTags, context)
                .or()
                .like(MaterialLibrary::getDescription, context)
            )
            .orderByDesc(MaterialLibrary::getUsageCount)
            .last("LIMIT " + limit);
        return materialLibraryMapper.selectList(wrapper);
    }
}