package com.aibid.material.service;

import com.aibid.common.core.BusinessException;
import com.aibid.common.core.ResultCode;
import com.aibid.material.entity.TeamMember;
import com.aibid.material.mapper.TeamMemberMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class TeamMemberService {

    private final TeamMemberMapper teamMemberMapper;

    public TeamMember getById(Long id) {
        TeamMember member = teamMemberMapper.selectById(id);
        if (member == null) {
            throw new BusinessException(ResultCode.NOT_FOUND, "团队成员不存在");
        }
        return member;
    }

    public List<TeamMember> listByEnterpriseId(Long enterpriseId) {
        return teamMemberMapper.selectList(
            new LambdaQueryWrapper<TeamMember>()
                .eq(TeamMember::getEnterpriseId, enterpriseId)
                .eq(TeamMember::getStatus, 1)
                .orderByAsc(TeamMember::getSort)
        );
    }

    public List<TeamMember> listLeaders(Long enterpriseId) {
        return teamMemberMapper.selectList(
            new LambdaQueryWrapper<TeamMember>()
                .eq(TeamMember::getEnterpriseId, enterpriseId)
                .eq(TeamMember::getIsLeader, 1)
                .eq(TeamMember::getStatus, 1)
                .orderByAsc(TeamMember::getSort)
        );
    }

    public void save(TeamMember member) {
        teamMemberMapper.insert(member);
    }

    public void update(TeamMember member) {
        if (member.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        teamMemberMapper.updateById(member);
    }

    public void delete(Long id) {
        teamMemberMapper.deleteById(id);
    }
}