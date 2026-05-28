package com.aibid.common.feign.client;

import com.aibid.common.core.Result;
import com.aibid.common.feign.dto.ProjectDTO;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 项目服务Feign客户端
 */
@FeignClient(name = "project-service", path = "/project")
public interface ProjectFeignClient {

    @GetMapping("/{id}")
    Result<ProjectDTO> getById(@PathVariable("id") Long id);

    @GetMapping("/list")
    Result<List<ProjectDTO>> list();

    @PostMapping
    Result<Void> save(@RequestBody ProjectDTO project);

    @PutMapping
    Result<Void> update(@RequestBody ProjectDTO project);

    @DeleteMapping("/{id}")
    Result<Void> delete(@PathVariable("id") Long id);
}