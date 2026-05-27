package com.aibid.common.feign.client;

import com.aibid.common.core.Result;
import com.aidbid.material.entity.BidMaterial;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 素材服务Feign客户端
 */
@FeignClient(name = "material-service", path = "/material")
public interface MaterialFeignClient {

    @GetMapping("/{id}")
    Result<BidMaterial> getById(@PathVariable("id") Long id);

    @GetMapping("/list")
    Result<List<BidMaterial>> list();

    @GetMapping("/list/project/{projectId}")
    Result<List<BidMaterial>> listByProjectId(@PathVariable("projectId") Long projectId);

    @PostMapping
    Result<Void> save(@RequestBody BidMaterial material);

    @PutMapping
    Result<Void> update(@RequestBody BidMaterial material);

    @DeleteMapping("/{id}")
    Result<Void> delete(@PathVariable("id") Long id);
}