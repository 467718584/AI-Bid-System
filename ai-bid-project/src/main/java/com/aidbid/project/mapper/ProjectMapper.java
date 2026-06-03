package com.aidbid.project.mapper;

import com.aidbid.project.entity.BidProject;
import org.apache.ibatis.annotations.*;
import java.util.List;

@Mapper
public interface ProjectMapper {
    
    @Select("SELECT * FROM bid_project WHERE id = #{id} AND deleted = 0")
    BidProject selectById(Long id);
    
    @Select("SELECT * FROM bid_project WHERE deleted = 0 ORDER BY create_time DESC LIMIT 100")
    List<BidProject> selectList();
    
    @Insert("INSERT INTO bid_project(id, name, code, type, amount, tenderer, deadline, status, description, contact_person, contact_phone, deleted) " +
            "VALUES(#{id}, #{name}, #{code}, #{type}, #{amount}, #{tenderer}, #{deadline}, #{status}, #{description}, #{contactPerson}, #{contactPhone}, 0)")
    int insert(BidProject project);
    
    @Update("UPDATE bid_project SET name=#{name}, code=#{code}, type=#{type}, amount=#{amount}, " +
            "tenderer=#{tenderer}, deadline=#{deadline}, status=#{status}, description=#{description}, " +
            "contact_person=#{contactPerson}, contact_phone=#{contactPhone} WHERE id=#{id} AND deleted=0")
    int update(BidProject project);
    
    @Update("UPDATE bid_project SET deleted=1 WHERE id=#{id}")
    int deleteById(Long id);
}