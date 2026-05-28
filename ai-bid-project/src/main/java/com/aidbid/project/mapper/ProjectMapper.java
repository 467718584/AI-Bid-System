package com.aidbid.project.mapper;

import com.aidbid.project.entity.BidProject;
import org.apache.ibatis.annotations.*;
import java.util.List;

@Mapper
public interface ProjectMapper {
    
    @Select("SELECT * FROM bid_project WHERE id = #{id} AND deleted = 0")
    BidProject selectById(Long id);
    
    @Select("SELECT * FROM bid_project WHERE deleted = 0 LIMIT 100")
    List<BidProject> selectList();
    
    @Insert("INSERT INTO bid_project(name, project_no, owner_id, status, budget, deleted) " +
            "VALUES(#{name}, #{projectNo}, #{ownerId}, #{status}, #{budget}, 0)")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(BidProject project);
    
    @Update("UPDATE bid_project SET name=#{name}, project_no=#{projectNo}, " +
            "owner_id=#{ownerId}, status=#{status}, budget=#{budget} WHERE id=#{id}")
    int update(BidProject project);
    
    @Delete("UPDATE bid_project SET deleted=1 WHERE id=#{id}")
    int deleteById(Long id);
}
