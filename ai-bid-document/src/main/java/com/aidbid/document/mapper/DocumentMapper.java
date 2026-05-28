package com.aidbid.document.mapper;

import com.aidbid.document.entity.BidDocument;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface DocumentMapper {

    @Select("SELECT * FROM bid_document WHERE id = #{id}")
    BidDocument selectById(@Param("id") Long id);

    @Select("SELECT * FROM bid_document WHERE deleted = 0")
    List<BidDocument> selectList();

    @Select("SELECT * FROM bid_document WHERE project_id = #{projectId} AND deleted = 0")
    List<BidDocument> selectByProjectId(@Param("projectId") Long projectId);

    @Select("SELECT * FROM bid_document WHERE status = #{status} AND deleted = 0")
    List<BidDocument> selectByStatus(@Param("status") String status);

    @Select("SELECT * FROM bid_document WHERE parse_status = #{parseStatus} AND deleted = 0")
    List<BidDocument> selectByParseStatus(@Param("parseStatus") String parseStatus);

    @Insert("INSERT INTO bid_document (name, type, project_id, material_id, file_path, file_size, content, parse_status, analysis_result, status, deleted, create_time) " +
            "VALUES (#{name}, #{type}, #{projectId}, #{materialId}, #{filePath}, #{fileSize}, #{content}, #{parseStatus}, #{analysisResult}, #{status}, 0, #{createTime})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(BidDocument document);

    @Update("UPDATE bid_document SET name=#{name}, type=#{type}, project_id=#{projectId}, material_id=#{materialId}, " +
            "file_path=#{filePath}, file_size=#{fileSize}, content=#{content}, parse_status=#{parseStatus}, " +
            "analysis_result=#{analysisResult}, status=#{status}, update_time=#{updateTime} WHERE id=#{id}")
    int updateById(BidDocument document);

    @Delete("DELETE FROM bid_document WHERE id = #{id}")
    int deleteById(@Param("id") Long id);

    @Select("SELECT COUNT(*) FROM bid_document WHERE deleted = 0")
    long selectCount();

    @Select("SELECT COUNT(*) FROM bid_document WHERE project_id = #{projectId} AND deleted = 0")
    long selectCountByProjectId(@Param("projectId") Long projectId);
}
