package com.aibid.material.entity;

import com.aibid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 私人图库相册
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("private_image_album")
public class PrivateImageAlbum extends BaseEntity {

    /** 相册名称 */
    private String name;

    /** 相册描述 */
    private String description;

    /** 封面图片ID */
    private Long coverImageId;

    /** 图片数量 */
    private Integer imageCount;

    /** 用户ID */
    private Long uploadUserId;

    /** 排序 */
    private Integer sort;

    /** 状态 */
    private Integer status;
}