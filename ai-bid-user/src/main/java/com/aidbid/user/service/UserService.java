package com.aidbid.user.service;

import com.aidbid.common.core.BusinessException;
import com.aidbid.common.core.ResultCode;
import com.aidbid.user.entity.SysUser;
import com.aidbid.user.mapper.UserMapper;
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
        return userMapper.selectAll();
    }

    public void save(SysUser user) {
        // 生成ID (如果未设置)
        if (user.getId() == null) {
            user.setId(System.currentTimeMillis());
        }
        userMapper.insert(user);
    }

    public void update(SysUser user) {
        if (user.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        userMapper.update(user);
    }

    public void delete(Long id) {
        userMapper.deleteById(id);
    }
}
