package com.aibid.material.service;

import com.aibid.common.core.BusinessException;
import com.aibid.common.core.ResultCode;
import com.aibid.material.entity.PrivateImageAlbum;
import com.aibid.material.entity.PrivateImageLibrary;
import com.aibid.material.mapper.PrivateImageAlbumMapper;
import com.aibid.material.mapper.PrivateImageLibraryMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class PrivateImageService {

    private final PrivateImageLibraryMapper imageLibraryMapper;
    private final PrivateImageAlbumMapper albumMapper;

    // ==================== Image Library ====================

    public PrivateImageLibrary getImageById(Long id) {
        PrivateImageLibrary image = imageLibraryMapper.selectById(id);
        if (image == null) {
            throw new BusinessException(ResultCode.NOT_FOUND, "图片不存在");
        }
        return image;
    }

    public List<PrivateImageLibrary> listImages(Long userId) {
        return imageLibraryMapper.selectList(
            new LambdaQueryWrapper<PrivateImageLibrary>()
                .eq(PrivateImageLibrary::getUploadUserId, userId)
                .eq(PrivateImageLibrary::getStatus, "ACTIVE")
                .orderByDesc(PrivateImageLibrary::getCreateTime)
        );
    }

    public List<PrivateImageLibrary> listImagesByAlbum(Long albumId) {
        return imageLibraryMapper.selectList(
            new LambdaQueryWrapper<PrivateImageLibrary>()
                .eq(PrivateImageLibrary::getAlbumId, albumId)
                .eq(PrivateImageLibrary::getStatus, "ACTIVE")
                .orderByDesc(PrivateImageLibrary::getCreateTime)
        );
    }

    public List<PrivateImageLibrary> searchImages(Long userId, String keyword) {
        return imageLibraryMapper.selectList(
            new LambdaQueryWrapper<PrivateImageLibrary>()
                .eq(PrivateImageLibrary::getUploadUserId, userId)
                .eq(PrivateImageLibrary::getStatus, "ACTIVE")
                .and(w -> w.like(PrivateImageLibrary::getName, keyword)
                    .or()
                    .like(PrivateImageLibrary::getDescription, keyword)
                    .or()
                    .like(PrivateImageLibrary::getTags, keyword)
                )
                .orderByDesc(PrivateImageLibrary::getCreateTime)
        );
    }

    public void saveImage(PrivateImageLibrary image) {
        imageLibraryMapper.insert(image);
    }

    public void updateImage(PrivateImageLibrary image) {
        if (image.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        imageLibraryMapper.updateById(image);
    }

    public void deleteImage(Long id) {
        imageLibraryMapper.deleteById(id);
    }

    public void updateDetectionResult(Long imageId, String result, String sources, Double score) {
        PrivateImageLibrary image = new PrivateImageLibrary();
        image.setId(imageId);
        image.setDetectionResult(result);
        image.setDetectedSources(sources);
        image.setDetectionScore(score != null ? java.math.BigDecimal.valueOf(score) : null);
        imageLibraryMapper.updateById(image);
    }

    // ==================== Albums ====================

    public PrivateImageAlbum getAlbumById(Long id) {
        PrivateImageAlbum album = albumMapper.selectById(id);
        if (album == null) {
            throw new BusinessException(ResultCode.NOT_FOUND, "相册不存在");
        }
        return album;
    }

    public List<PrivateImageAlbum> listAlbums(Long userId) {
        return albumMapper.selectList(
            new LambdaQueryWrapper<PrivateImageAlbum>()
                .eq(PrivateImageAlbum::getUploadUserId, userId)
                .eq(PrivateImageAlbum::getStatus, 1)
                .orderByAsc(PrivateImageAlbum::getSort)
        );
    }

    public void saveAlbum(PrivateImageAlbum album) {
        albumMapper.insert(album);
    }

    public void updateAlbum(PrivateImageAlbum album) {
        if (album.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        albumMapper.updateById(album);
    }

    public void deleteAlbum(Long id) {
        albumMapper.deleteById(id);
    }
}