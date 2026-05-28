package com.aidbid.material.controller;

import com.aibid.common.core.Result;
import com.aidbid.material.entity.MaterialLibrary;
import com.aidbid.material.entity.MaterialUsageLog;
import com.aidbid.material.service.MaterialLibraryService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/material")
@RequiredArgsConstructor
public class MaterialLibraryController {

    private final MaterialLibraryService materialLibraryService;

    private static final String UPLOAD_DIR = System.getenv("MATERIAL_UPLOAD_DIR") != null
        ? System.getenv("MATERIAL_UPLOAD_DIR") : "/data/materials";

    // ==================== CRUD ====================

    @GetMapping("/{id}")
    public Result<MaterialLibrary> getById(@PathVariable Long id) {
        return Result.ok(materialLibraryService.getById(id));
    }

    @GetMapping("/list")
    public Result<List<MaterialLibrary>> list() {
        return Result.ok(materialLibraryService.list());
    }

    @GetMapping("/list/type/{type}")
    public Result<List<MaterialLibrary>> listByType(@PathVariable String type) {
        return Result.ok(materialLibraryService.listByType(type));
    }

    @GetMapping("/list/category/{category}")
    public Result<List<MaterialLibrary>> listByCategory(@PathVariable String category) {
        return Result.ok(materialLibraryService.listByCategory(category));
    }

    @GetMapping("/search")
    public Result<List<MaterialLibrary>> search(@RequestParam String keyword) {
        return Result.ok(materialLibraryService.search(keyword));
    }

    @PostMapping
    public Result<Void> save(@RequestBody MaterialLibrary material) {
        materialLibraryService.save(material);
        return Result.ok();
    }

    @PutMapping
    public Result<Void> update(@RequestBody MaterialLibrary material) {
        materialLibraryService.update(material);
        return Result.ok();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        materialLibraryService.delete(id);
        return Result.ok();
    }

    // ==================== Upload ====================

    @PostMapping("/upload")
    public Result<MaterialLibrary> upload(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "name", required = false) String name,
            @RequestParam(value = "tags", required = false) String tags,
            @RequestParam(value = "category", required = false) String category,
            @RequestParam(value = "description", required = false) String description,
            @RequestParam(value = "projectId", required = false) Long projectId,
            @RequestParam(value = "userId", required = false) Long userId) {

        try {
            String originalFilename = file.getOriginalFilename();
            String ext = originalFilename != null && originalFilename.contains(".")
                ? originalFilename.substring(originalFilename.lastIndexOf("."))
                : "";

            String storedName = UUID.randomUUID().toString() + ext;
            Path uploadPath = Paths.get(UPLOAD_DIR);
            Files.createDirectories(uploadPath);
            Path filePath = uploadPath.resolve(storedName);
            file.transferTo(filePath.toFile());

            String contentType = file.getContentType();
            long size = file.getSize();

            MaterialLibrary material = new MaterialLibrary();
            material.setName(name != null ? name : originalFilename);
            material.setFilePath(filePath.toString());
            material.setFileUrl("/files/materials/" + storedName);
            material.setFileSize(size);
            material.setFileType(contentType);
            material.setTags(tags);
            material.setCategory(category);
            material.setDescription(description);
            material.setProjectId(projectId);
            material.setUploadUserId(userId);
            material.setType(determineType(contentType, ext));
            material.setStatus("ACTIVE");

            materialLibraryService.save(material);
            return Result.ok(material);

        } catch (IOException e) {
            return Result.fail(500, "文件上传失败: " + e.getMessage());
        }
    }

    // ==================== Batch Upload ====================

    @PostMapping("/upload/batch")
    public Result<List<MaterialLibrary>> batchUpload(
            @RequestParam("files") MultipartFile[] files,
            @RequestParam(value = "tags", required = false) String tags,
            @RequestParam(value = "category", required = false) String category,
            @RequestParam(value = "userId", required = false) Long userId) {

        List<MaterialLibrary> results = new java.util.ArrayList<>();
        for (MultipartFile file : files) {
            try {
                String originalFilename = file.getOriginalFilename();
                String ext = originalFilename != null && originalFilename.contains(".")
                    ? originalFilename.substring(originalFilename.lastIndexOf("."))
                    : "";

                String storedName = UUID.randomUUID().toString() + ext;
                Path uploadPath = Paths.get(UPLOAD_DIR);
                Files.createDirectories(uploadPath);
                Path filePath = uploadPath.resolve(storedName);
                file.transferTo(filePath.toFile());

                MaterialLibrary material = new MaterialLibrary();
                material.setName(originalFilename);
                material.setFilePath(filePath.toString());
                material.setFileUrl("/files/materials/" + storedName);
                material.setFileSize(file.getSize());
                material.setFileType(file.getContentType());
                material.setTags(tags);
                material.setCategory(category);
                material.setUploadUserId(userId);
                material.setType(determineType(file.getContentType(), ext));
                material.setStatus("ACTIVE");

                materialLibraryService.save(material);
                results.add(material);
            } catch (IOException ignored) {}
        }
        return Result.ok(results);
    }

    // ==================== Categories ====================

    @GetMapping("/categories")
    public Result<List<String>> categories() {
        return Result.ok(materialLibraryService.listCategories());
    }

    // ==================== Recommend ====================

    @PostMapping("/recommend")
    public Result<List<MaterialLibrary>> recommend(
            @RequestBody java.util.Map<String, Object> request) {
        String context = (String) request.get("context");
        int limit = request.containsKey("limit")
            ? ((Number) request.get("limit")).intValue() : 10;
        return Result.ok(materialLibraryService.recommendByContext(context, limit));
    }

    // ==================== Usage Tracking ====================

    @PostMapping("/usage/record")
    public Result<Void> recordUsage(@RequestBody MaterialUsageLog log) {
        materialLibraryService.recordUsage(
            log.getMaterialId(),
            log.getUserId(),
            log.getUsageType(),
            log.getUsageContext()
        );
        return Result.ok();
    }

    @GetMapping("/usage/logs/{materialId}")
    public Result<List<MaterialUsageLog>> getUsageLogs(@PathVariable Long materialId) {
        return Result.ok(materialLibraryService.getUsageLogs(materialId));
    }

    @GetMapping("/usage/logs/project/{projectId}")
    public Result<List<MaterialUsageLog>> getUsageLogsByProject(@PathVariable Long projectId) {
        return Result.ok(materialLibraryService.getUsageLogsByProject(projectId));
    }

    // ==================== Helpers ====================

    private String determineType(String contentType, String ext) {
        if (contentType != null) {
            if (contentType.startsWith("image/")) return "IMAGE";
            if (contentType.startsWith("video/")) return "VIDEO";
            if (contentType.startsWith("audio/")) return "AUDIO";
            if (contentType.contains("pdf") || contentType.contains("document") || contentType.contains("word"))
                return "DOCUMENT";
        }
        if (ext != null) {
            String lower = ext.toLowerCase();
            if (Arrays.asList(".jpg",".jpeg",".png",".gif",".webp",".svg",".bmp").contains(lower)) return "IMAGE";
            if (Arrays.asList(".mp4",".avi",".mov",".mkv",".webm").contains(lower)) return "VIDEO";
            if (Arrays.asList(".mp3",".wav",".flac",".aac",".ogg").contains(lower)) return "AUDIO";
            if (Arrays.asList(".doc",".docx",".pdf",".txt",".rtf").contains(lower)) return "DOCUMENT";
            if (Arrays.asList(".docx",".dotx").contains(lower)) return "TEMPLATE";
        }
        return "DOCUMENT";
    }
}