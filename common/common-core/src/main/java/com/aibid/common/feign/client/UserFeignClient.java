package com.aibid.common.feign.client;

import com.aibid.common.core.Result;
import com.aidbid.user.entity.SysUser;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 用户服务Feign客户端
 */
@FeignClient(name = "user-service", path = "/user")
public interface UserFeignClient {

    @GetMapping("/{id}")
    Result<SysUser> getById(@PathVariable("id") Long id);

    @GetMapping("/list")
    Result<List<SysUser>> list();

    @PostMapping
    Result<Void> save(@RequestBody SysUser user);

    @PutMapping
    Result<Void> update(@RequestBody SysUser user);

    @DeleteMapping("/{id}")
    Result<Void> delete(@PathVariable("id") Long id);
}