package com.aidbid.material.entity;

import com.aibid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.math.BigDecimal;

/**
 * 私人图库
 */
@Data
@EqualsAndHashCode(callSuper = true)
@TableName("private_image_library")
public class PrivateImageLibrary extends BaseEntity {

    /** 图片名称 */
    private String name;

    /** 图片描述 */
    private String description;

    /** 标签(JSON数组) */
    private String tags;

    /** 文件存储路径 */
    private String filePath;

    /** 文件访问URL */
    private String fileUrl;

    /** 文件大小(字节) */
    private Long fileSize;

    /** 图片宽度 */
    private Integer width;

    /** 图片高度 */
    private Integer height;

    /** 缩略图路径 */
    private String thumbnailPath;

    /** 是否AI生成 */
    private Integer aiGenerated;

    /** AI模型名称 */
    private String aiModel;

    /** AI生成提示词 */
    private String aiPrompt;

    /** AI负面提示词 */
    private String aiNegativePrompt;

    /** 版权状态 */
    private String copyrightStatus;

    /** 版权备注 */
    private String copyrightRemark;

    /** 图片来源URL */
    private String sourceUrl;

    /** 检测到的相似图片来源(JSON) */
    private String detectedSources;

    /** 版权检测相似度分数 */
    private BigDecimal detectionScore;

    /** 检测结果: CLEAN/SUSPICIOUS/COPYRIGHTED */
    private String detectionResult;

    /** 使用次数 */
    private Integer usageCount;

    /** 上传用户ID */
    private Long uploadUserId;

    /** 所属相册ID */
    private Long albumId;

    /** 状态 */
    private String status;
}