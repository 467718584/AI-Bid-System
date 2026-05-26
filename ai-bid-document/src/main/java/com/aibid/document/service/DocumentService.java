package com.aibid.document.service;

import com.aibid.common.core.BusinessException;
import com.aibid.common.core.ResultCode;
import com.aibid.document.entity.BidDocument;
import com.aibid.document.mapper.DocumentMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class DocumentService {

    private final DocumentMapper documentMapper;

    public BidDocument getById(Long id) {
        BidDocument document = documentMapper.selectById(id);
        if (document == null) {
            throw new BusinessException(ResultCode.DOCUMENT_NOT_FOUND);
        }
        return document;
    }

    public List<BidDocument> list() {
        return documentMapper.selectList(new LambdaQueryWrapper<>());
    }

    public List<BidDocument> listByProjectId(Long projectId) {
        return documentMapper.selectList(new LambdaQueryWrapper<BidDocument>().eq(BidDocument::getProjectId, projectId));
    }

    public List<BidDocument> listByStatus(String status) {
        return documentMapper.selectList(new LambdaQueryWrapper<BidDocument>().eq(BidDocument::getStatus, status));
    }

    public List<BidDocument> listByParseStatus(String parseStatus) {
        return documentMapper.selectList(new LambdaQueryWrapper<BidDocument>().eq(BidDocument::getParseStatus, parseStatus));
    }

    public void save(BidDocument document) {
        documentMapper.insert(document);
    }

    public void update(BidDocument document) {
        if (document.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        documentMapper.updateById(document);
    }

    public void delete(Long id) {
        documentMapper.deleteById(id);
    }

    public long count() {
        return documentMapper.selectCount(null);
    }

    public long countByProjectId(Long projectId) {
        return documentMapper.selectCount(new LambdaQueryWrapper<BidDocument>().eq(BidDocument::getProjectId, projectId));
    }
}
