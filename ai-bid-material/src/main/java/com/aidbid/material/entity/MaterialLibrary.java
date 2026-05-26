package com.aibid.material.entity;

import com.aibid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 素材库
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("material_library")
public class MaterialLibrary extends BaseEntity {

    /** 素材名称 */
    private String name;

    /** 素材类型: IMAGE/DOCUMENT/VIDEO/AUDIO/TEMPLATE */
    private String type;

    /** 素材分类 */
    private String category;

    /** 子分类 */
    private String subCategory;

    /** 标签(JSON数组) */
    private String tags;

    /** 素材描述 */
    private String description;

    /** 文件存储路径 */
    private String filePath;

    /** 文件访问URL */
    private String fileUrl;

    /** 文件大小(字节) */
    private Long fileSize;

    /** 文件MIME类型 */
    private String fileType;

    /** 文件哈希(SHA256) */
    private String fileHash;

    /** 图片/视频宽度 */
    private Integer width;

    /** 图片/视频高度 */
    private Integer height;

    /** 视频/音频时长(秒) */
    private Integer duration;

    /** 缩略图路径 */
    private String thumbnailPath;

    /** 是否AI生成: 0=否, 1=是 */
    private Integer aiGenerated;

    /** AI生成提示词 */
    private String aiPrompt;

    /** 版权状态: UNKNOWN/OWNED/LICENSED/THIRD_PARTY/COPYRIGHTED */
    private String copyrightStatus;

    /** 版权备注 */
    private String copyrightRemark;

    /** 素材来源 */
    private String source;

    /** 使用次数 */
    private Integer usageCount;

    /** 收藏次数 */
    private Integer favoriteCount;

    /** 关联项目ID */
    private Long projectId;

    /** 上传用户ID */
    private Long uploadUserId;

    /** 状态: ACTIVE/ARCHIVED/HIDDEN */
    private String status;
}