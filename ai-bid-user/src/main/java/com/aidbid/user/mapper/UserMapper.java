package com.aidbid.user.mapper;

import com.aidbid.user.entity.SysUser;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface UserMapper {
    
    @Select("SELECT * FROM sys_user WHERE id = #{id}")
    SysUser selectById(Long id);
    
    @Select("SELECT * FROM sys_user WHERE username = #{username}")
    SysUser selectByUsername(String username);
    
    @Select("SELECT * FROM sys_user WHERE deleted = 0")
    List<SysUser> selectAll();
    
    @Insert("INSERT INTO sys_user(username, password, email, phone, department, position, enabled, deleted) " +
            "VALUES(#{username}, #{password}, #{email}, #{phone}, #{department}, #{position}, #{enabled}, 0)")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(SysUser user);
    
    @Update("UPDATE sys_user SET username=#{username}, password=#{password}, email=#{email}, " +
            "phone=#{phone}, department=#{department}, position=#{position}, enabled=#{enabled} WHERE id=#{id}")
    int update(SysUser user);
    
    @Delete("DELETE FROM sys_user WHERE id = #{id}")
    int deleteById(Long id);
}
