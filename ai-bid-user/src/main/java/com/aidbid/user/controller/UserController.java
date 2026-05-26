package com.aidbid.user.controller;

import com.aibid.common.core.PageRequest;
import com.aibid.common.core.PageResponse;
import com.aibid.common.core.Result;
import com.aibid.user.entity.SysUser;
import com.aibid.user.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/{id}")
    public Result<SysUser> getById(@PathVariable Long id) {
        return Result.ok(userService.getById(id));
    }

    @GetMapping("/list")
    public Result<List<SysUser>> list() {
        return Result.ok(userService.list());
    }

    @PostMapping
    public Result<Void> save(@RequestBody SysUser user) {
        userService.save(user);
        return Result.ok();
    }

    @PutMapping
    public Result<Void> update(@RequestBody SysUser user) {
        userService.update(user);
        return Result.ok();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        userService.delete(id);
        return Result.ok();
    }
}
