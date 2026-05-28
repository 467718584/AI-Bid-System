package com.aidbid.material.controller;

import com.aibid.common.core.Result;
import com.aidbid.material.entity.PrivateImageAlbum;
import com.aidbid.material.entity.PrivateImageLibrary;
import com.aidbid.material.service.PrivateImageService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/material/image")
@RequiredArgsConstructor
public class PrivateImageController {

    private final PrivateImageService privateImageService;

    private static final String UPLOAD_DIR = System.getenv("IMAGE_UPLOAD_DIR") != null
        ? System.getenv("IMAGE_UPLOAD_DIR") : "/data/images";

    // ==================== Image CRUD ====================

    @GetMapping("/{id}")
    public Result<PrivateImageLibrary> getById(@PathVariable Long id) {
        return Result.ok(privateImageService.getImageById(id));
    }

    @GetMapping("/list")
    public Result<List<PrivateImageLibrary>> list(@RequestParam Long userId) {
        return Result.ok(privateImageService.listImages(userId));
    }

    @GetMapping("/list/album/{albumId}")
    public Result<List<PrivateImageLibrary>> listByAlbum(@PathVariable Long albumId) {
        return Result.ok(privateImageService.listImagesByAlbum(albumId));
    }

    @GetMapping("/search")
    public Result<List<PrivateImageLibrary>> search(
            @RequestParam Long userId,
            @RequestParam String keyword) {
        return Result.ok(privateImageService.searchImages(userId, keyword));
    }

    @PostMapping
    public Result<Void> save(@RequestBody PrivateImageLibrary image) {
        privateImageService.saveImage(image);
        return Result.ok();
    }

    @PutMapping
    public Result<Void> update(@RequestBody PrivateImageLibrary image) {
        privateImageService.updateImage(image);
        return Result.ok();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        privateImageService.deleteImage(id);
        return Result.ok();
    }

    // ==================== Upload ====================

    @PostMapping("/upload")
    public Result<PrivateImageLibrary> upload(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "name", required = false) String name,
            @RequestParam(value = "description", required = false) String description,
            @RequestParam(value = "tags", required = false) String tags,
            @RequestParam(value = "userId", required = false) Long userId,
            @RequestParam(value = "albumId", required = false) Long albumId) {

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

            int[] dimensions = getImageDimensions(filePath.toString(), ext);

            PrivateImageLibrary image = new PrivateImageLibrary();
            image.setName(name != null ? name : originalFilename);
            image.setFilePath(filePath.toString());
            image.setFileUrl("/files/images/" + storedName);
            image.setFileSize(file.getSize());
            image.setWidth(dimensions[0]);
            image.setHeight(dimensions[1]);
            image.setTags(tags);
            image.setDescription(description);
            image.setUploadUserId(userId);
            image.setAlbumId(albumId);
            image.setCopyrightStatus("OWNED");
            image.setStatus("ACTIVE");

            privateImageService.saveImage(image);
            return Result.ok(image);

        } catch (IOException e) {
            return Result.fail(500, "图片上传失败: " + e.getMessage());
        }
    }

    // ==================== AI Generation ====================

    @PostMapping("/generate")
    public Result<PrivateImageLibrary> generate(
            @RequestBody java.util.Map<String, Object> request) {
        // Placeholder: AI image generation would be called here
        // For now, return a mock response indicating this is a placeholder
        String prompt = (String) request.get("prompt");
        String negativePrompt = (String) request.get("negativePrompt");
        String model = request.containsKey("model") ? (String) request.get("model") : "stable-diffusion";
        Long userId = request.containsKey("userId") ? ((Number) request.get("userId")).longValue() : null;

        PrivateImageLibrary image = new PrivateImageLibrary();
        image.setName("AI Generated Image");
        image.setAiGenerated(1);
        image.setAiModel(model);
        image.setAiPrompt(prompt);
        image.setAiNegativePrompt(negativePrompt);
        image.setCopyrightStatus("OWNED");
        image.setUploadUserId(userId);
        image.setStatus("ACTIVE");

        // Note: actual generation would integrate with Stable Diffusion / DALL-E / Midjourney API
        privateImageService.saveImage(image);
        return Result.ok(image);
    }

    // ==================== Copyright Detection ====================

    @PostMapping("/detect-copyright")
    public Result<PrivateImageLibrary> detectCopyright(
            @RequestBody java.util.Map<String, Object> request) {
        Long imageId = ((Number) request.get("imageId")).longValue();
        // Placeholder: actual detection would use reverse image search or AI model
        String detectedSources = "[]";
        Double score = 0.0;
        String result = "CLEAN";
        privateImageService.updateDetectionResult(imageId, result, detectedSources, score);
        return Result.ok(privateImageService.getImageById(imageId));
    }

    // ==================== Albums ====================

    @GetMapping("/album/{id}")
    public Result<PrivateImageAlbum> getAlbum(@PathVariable Long id) {
        return Result.ok(privateImageService.getAlbumById(id));
    }

    @GetMapping("/album/list")
    public Result<List<PrivateImageAlbum>> listAlbums(@RequestParam Long userId) {
        return Result.ok(privateImageService.listAlbums(userId));
    }

    @PostMapping("/album")
    public Result<Void> saveAlbum(@RequestBody PrivateImageAlbum album) {
        privateImageService.saveAlbum(album);
        return Result.ok();
    }

    @PutMapping("/album")
    public Result<Void> updateAlbum(@RequestBody PrivateImageAlbum album) {
        privateImageService.updateAlbum(album);
        return Result.ok();
    }

    @DeleteMapping("/album/{id}")
    public Result<Void> deleteAlbum(@PathVariable Long id) {
        privateImageService.deleteAlbum(id);
        return Result.ok();
    }

    // ==================== Helpers ====================

    private int[] getImageDimensions(String filePath, String ext) {
        // Placeholder - actual implementation would use ImageIO or similar
        return new int[]{0, 0};
    }
}