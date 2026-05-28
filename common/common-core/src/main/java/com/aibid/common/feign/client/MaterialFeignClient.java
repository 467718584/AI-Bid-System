package com.aibid.common.feign.client;

import com.aibid.common.core.Result;
import com.aibid.common.feign.dto.MaterialDTO;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 物料服务Feign客户端
 */
@FeignClient(name = "material-service", path = "/material")
public interface MaterialFeignClient {

    @GetMapping("/{id}")
    Result<MaterialDTO> getById(@PathVariable("id") Long id);

    @GetMapping("/list")
    Result<List<MaterialDTO>> list();

    @GetMapping("/list/project/{projectId}")
    Result<List<MaterialDTO>> listByProjectId(@PathVariable("projectId") Long projectId);

    @PostMapping
    Result<Void> save(@RequestBody MaterialDTO material);

    @PutMapping
    Result<Void> update(@RequestBody MaterialDTO material);

    @DeleteMapping("/{id}")
    Result<Void> delete(@PathVariable("id") Long id);
}