package com.aidbid.user.service;

import com.aibid.common.core.BusinessException;
import com.aibid.common.core.ResultCode;
import com.aibid.user.entity.SysUser;
import com.aibid.user.mapper.UserMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserMapper userMapper;

    public SysUser getById(Long id) {
        SysUser user = userMapper.selectById(id);
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }
        return user;
    }

    public List<SysUser> list() {
        return userMapper.selectList(new LambdaQueryWrapper<>());
    }

    public void save(SysUser user) {
        userMapper.insert(user);
    }

    public void update(SysUser user) {
        if (user.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        userMapper.updateById(user);
    }

    public void delete(Long id) {
        userMapper.deleteById(id);
    }
}
