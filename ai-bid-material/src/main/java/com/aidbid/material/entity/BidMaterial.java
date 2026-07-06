package com.aidbid.material.entity;

import com.aibid.common.core.BaseEntity;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("bid_material")
public class BidMaterial extends BaseEntity {

    /** 材料名称 */
    private String name;

    /** 材料类型 */
    private String materialType;

    /** 所属项目ID */
    private Long projectId;

    /** 文件路径 */
    private String filePath;

    /** 文件大小 */
    private Long fileSize;

    /** 文件类型 */
    private String fileType;

    /** 上传用户ID */
    private Long uploadUserId;

    /** 状态 */
    private String status;

    /** 备注 */
    private String remark;
}
