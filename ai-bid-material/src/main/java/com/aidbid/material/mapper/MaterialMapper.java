package com.aidbid.material.mapper;

import com.aidbid.material.entity.BidMaterial;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface MaterialMapper {

    @Select("SELECT * FROM bid_material WHERE id = #{id}")
    BidMaterial selectById(@Param("id") Long id);

    @Select("SELECT * FROM bid_material")
    List<BidMaterial> selectList();

    @Select("SELECT * FROM bid_material WHERE project_id = #{projectId}")
    List<BidMaterial> selectByProjectId(@Param("projectId") Long projectId);

    @Select("SELECT * FROM bid_material WHERE status = #{status}")
    List<BidMaterial> selectByStatus(@Param("status") String status);

    @Insert("INSERT INTO bid_material (name, type, project_id, file_path, file_size, file_type, upload_user_id, status, remark, deleted, create_by, create_time) " +
            "VALUES (#{name}, #{type}, #{projectId}, #{filePath}, #{fileSize}, #{fileType}, #{uploadUserId}, #{status}, #{remark}, 0, #{createBy}, #{createTime})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(BidMaterial material);

    @Update("UPDATE bid_material SET name=#{name}, type=#{type}, project_id=#{projectId}, file_path=#{filePath}, " +
            "file_size=#{fileSize}, file_type=#{fileType}, upload_user_id=#{uploadUserId}, status=#{status}, remark=#{remark}, " +
            "update_by=#{updateBy}, update_time=#{updateTime} WHERE id=#{id}")
    int updateById(BidMaterial material);

    @Delete("DELETE FROM bid_material WHERE id = #{id}")
    int deleteById(@Param("id") Long id);

    @Select("SELECT COUNT(*) FROM bid_material")
    long selectCount();

    @Select("SELECT COUNT(*) FROM bid_material WHERE project_id = #{projectId}")
    long selectCountByProjectId(@Param("projectId") Long projectId);
}
