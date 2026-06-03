package com.aidbid.bid.service;

import com.aidbid.bid.entity.BidProject;
import com.aidbid.bid.mapper.BidProjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class BidProjectService {

    @Autowired
    private BidProjectMapper bidProjectMapper;

    public List<BidProject> list() {
        return bidProjectMapper.selectAll();
    }

    public BidProject getById(Long id) {
        return bidProjectMapper.selectById(id);
    }

    public BidProject create(BidProject project) {
        project.setStatus("DRAFT");
        project.setCreateTime(LocalDateTime.now());
        project.setUpdateTime(LocalDateTime.now());
        bidProjectMapper.insert(project);
        return project;
    }

    public BidProject update(Long id, BidProject project) {
        // 使用原生SQL更新，避免MyBatis-Plus乐观锁问题
        project.setId(id);
        project.setUpdateTime(LocalDateTime.now());
        bidProjectMapper.updateByIdManual(project);
        return getById(id);
    }

    public boolean delete(Long id) {
        // 逻辑删除 - 使用原生SQL
        bidProjectMapper.deleteByIdManual(id);
        return true;
    }
}
