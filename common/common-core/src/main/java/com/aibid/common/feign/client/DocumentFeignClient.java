package com.aibid.common.feign.client;

import com.aibid.common.core.Result;
import com.aibid.common.feign.dto.DocumentDTO;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 文档服务Feign客户端
 */
@FeignClient(name = "document-service", path = "/document")
public interface DocumentFeignClient {

    @GetMapping("/{id}")
    Result<DocumentDTO> getById(@PathVariable("id") Long id);

    @GetMapping("/list")
    Result<List<DocumentDTO>> list();

    @GetMapping("/list/project/{projectId}")
    Result<List<DocumentDTO>> listByProjectId(@PathVariable("projectId") Long projectId);

    @PostMapping
    Result<Void> save(@RequestBody DocumentDTO document);

    @PutMapping
    Result<Void> update(@RequestBody DocumentDTO document);

    @DeleteMapping("/{id}")
    Result<Void> delete(@PathVariable("id") Long id);
}