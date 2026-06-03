package com.aidbid.user.mapper;

import com.aidbid.user.entity.SysUser;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface UserMapper {
    
    @Select("SELECT * FROM sys_user WHERE id = #{id} AND deleted = 0")
    SysUser selectById(Long id);
    
    @Select("SELECT * FROM sys_user WHERE username = #{username} AND deleted = 0")
    SysUser selectByUsername(String username);
    
    @Select("SELECT * FROM sys_user WHERE deleted = 0")
    List<SysUser> selectAll();
    
    @Insert("INSERT INTO sys_user(id, username, password, nickname, email, phone, avatar, gender, dept_id, status, remark, deleted) " +
            "VALUES(#{id}, #{username}, #{password}, #{nickname}, #{email}, #{phone}, #{avatar}, #{gender}, #{deptId}, #{status}, #{remark}, 0)")
    int insert(SysUser user);
    
    @Update("UPDATE sys_user SET username=#{username}, password=#{password}, nickname=#{nickname}, email=#{email}, " +
            "phone=#{phone}, avatar=#{avatar}, gender=#{gender}, dept_id=#{deptId}, status=#{status}, remark=#{remark} WHERE id=#{id} AND deleted=0")
    int update(SysUser user);
    
    @Update("UPDATE sys_user SET deleted=1 WHERE id=#{id}")
    int deleteById(Long id);
}