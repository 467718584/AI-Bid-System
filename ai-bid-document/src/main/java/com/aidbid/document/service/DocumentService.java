package com.aidbid.document.service;

import com.aidbid.common.core.BusinessException;
import com.aidbid.common.core.ResultCode;
import com.aidbid.document.entity.BidDocument;
import com.aidbid.document.mapper.DocumentMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
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
        return documentMapper.selectList();
    }

    public List<BidDocument> listByProjectId(Long projectId) {
        return documentMapper.selectByProjectId(projectId);
    }

    public List<BidDocument> listByStatus(String status) {
        return documentMapper.selectByStatus(status);
    }

    public List<BidDocument> listByParseStatus(String parseStatus) {
        return documentMapper.selectByParseStatus(parseStatus);
    }

    public void save(BidDocument document) {
        document.setCreateTime(LocalDateTime.now());
        documentMapper.insert(document);
    }

    public void update(BidDocument document) {
        if (document.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        document.setUpdateTime(LocalDateTime.now());
        documentMapper.updateById(document);
    }

    public void delete(Long id) {
        documentMapper.deleteById(id);
    }

    public long count() {
        return documentMapper.selectCount();
    }

    public long countByProjectId(Long projectId) {
        return documentMapper.selectCountByProjectId(projectId);
    }
}
