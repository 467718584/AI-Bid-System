package com.aidbid.material.controller;

import com.aibid.common.core.Result;
import com.aibid.material.entity.TeamMember;
import com.aibid.material.service.TeamMemberService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/enterprise/team-member")
@RequiredArgsConstructor
public class TeamMemberController {

    private final TeamMemberService teamMemberService;

    @GetMapping("/{id}")
    public Result<TeamMember> getById(@PathVariable Long id) {
        return Result.ok(teamMemberService.getById(id));
    }

    @GetMapping("/list/enterprise/{enterpriseId}")
    public Result<List<TeamMember>> listByEnterprise(@PathVariable Long enterpriseId) {
        return Result.ok(teamMemberService.listByEnterpriseId(enterpriseId));
    }

    @GetMapping("/list/leaders/{enterpriseId}")
    public Result<List<TeamMember>> listLeaders(@PathVariable Long enterpriseId) {
        return Result.ok(teamMemberService.listLeaders(enterpriseId));
    }

    @PostMapping
    public Result<Void> save(@RequestBody TeamMember member) {
        teamMemberService.save(member);
        return Result.ok();
    }

    @PutMapping
    public Result<Void> update(@RequestBody TeamMember member) {
        teamMemberService.update(member);
        return Result.ok();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        teamMemberService.delete(id);
        return Result.ok();
    }
}