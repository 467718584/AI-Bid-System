package com.aidbid.document.entity;

import com.aidbid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("bid_document")
public class BidDocument extends BaseEntity {

    /** 文档名称 */
    private String name;

    /** 文档类型 */
    private String type;

    /** 所属项目ID */
    private Long projectId;

    /** 文件路径 */
    private String filePath;

    /** 文件大小 */
    private Long fileSize;

    /** 文档内容（解析后的文本） */
    private String content;

    /** AI分析结果 */
    private String analysisResult;

    /** 状态 */
    private String status;

    /** 解析状态 */
    private String parseStatus;
}
