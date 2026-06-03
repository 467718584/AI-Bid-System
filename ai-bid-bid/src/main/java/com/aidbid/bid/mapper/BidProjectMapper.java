package com.aidbid.bid.mapper;

import com.aidbid.bid.entity.BidProject;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface BidProjectMapper {

    @Select("SELECT * FROM bid_project WHERE deleted = 0 ORDER BY create_time DESC")
    List<BidProject> selectAll();

    @Select("SELECT * FROM bid_project WHERE id = #{id} AND deleted = 0")
    BidProject selectById(@Param("id") Long id);

    @Insert("INSERT INTO bid_project(name, code, type, amount, tenderer, contact_person, contact_phone, deadline, status, description, content, outline, create_time, update_time, deleted, version) " +
            "VALUES(#{name}, #{code}, #{type}, #{amount}, #{tenderer}, #{contactPerson}, #{contactPhone}, #{deadline}, #{status}, #{description}, #{content}, #{outline}, #{createTime}, #{updateTime}, 0, 0)")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    void insert(BidProject project);

    @Update("UPDATE bid_project SET name=#{name}, type=#{type}, status=#{status}, description=#{description}, content=#{content}, outline=#{outline}, update_time=#{updateTime} WHERE id=#{id}")
    void updateByIdManual(BidProject project);

    @Update("UPDATE bid_project SET deleted=1, update_time=NOW() WHERE id=#{id}")
    void deleteByIdManual(@Param("id") Long id);
}
