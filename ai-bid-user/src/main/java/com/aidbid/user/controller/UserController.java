package com.aidbid.user.controller;

import com.aidbid.common.core.PageRequest;
import com.aidbid.common.core.PageResponse;
import com.aidbid.common.core.Result;
import com.aidbid.user.entity.SysUser;
import com.aidbid.user.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/user")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    /**
     * 获取用户统计数据
     * GET /api/user/stats
     */
    @GetMapping("/stats")
    public Result<Map<String, Object>> getStats() {
        List<SysUser> users = userService.list();
        long totalUsers = users.size();
        long activeUsers = users.stream().filter(u -> "1".equals(u.getStatus())).count();

        Map<String, Object> stats = new HashMap<>();
        stats.put("totalUsers", totalUsers);
        stats.put("activeUsers", activeUsers);
        stats.put("inactiveUsers", totalUsers - activeUsers);

        return Result.ok(stats);
    }

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
