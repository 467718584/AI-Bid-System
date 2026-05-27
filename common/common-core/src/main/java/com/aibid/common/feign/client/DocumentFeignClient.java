package com.aibid.common.feign.client;

import com.aibid.common.core.Result;
import com.aidbid.document.entity.BidDocument;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 文档服务Feign客户端
 */
@FeignClient(name = "document-service", path = "/document")
public interface DocumentFeignClient {

    @GetMapping("/{id}")
    Result<BidDocument> getById(@PathVariable("id") Long id);

    @GetMapping("/list")
    Result<List<BidDocument>> list();

    @GetMapping("/list/project/{projectId}")
    Result<List<BidDocument>> listByProjectId(@PathVariable("projectId") Long projectId);

    @PostMapping
    Result<Void> save(@RequestBody BidDocument document);

    @PutMapping
    Result<Void> update(@RequestBody BidDocument document);

    @DeleteMapping("/{id}")
    Result<Void> delete(@PathVariable("id") Long id);
}