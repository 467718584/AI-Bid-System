package com.aibid.common.feign.client;

import com.aibid.common.core.Result;
import com.aidbid.project.entity.BidProject;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 项目服务Feign客户端
 */
@FeignClient(name = "project-service", path = "/project")
public interface ProjectFeignClient {

    @GetMapping("/{id}")
    Result<BidProject> getById(@PathVariable("id") Long id);

    @GetMapping("/list")
    Result<List<BidProject>> list();

    @GetMapping("/list/status/{status}")
    Result<List<BidProject>> listByStatus(@PathVariable("status") String status);

    @PostMapping
    Result<Void> save(@RequestBody BidProject project);

    @PutMapping
    Result<Void> update(@RequestBody BidProject project);

    @DeleteMapping("/{id}")
    Result<Void> delete(@PathVariable("id") Long id);

    @GetMapping("/count")
    Result<Long> count();
}