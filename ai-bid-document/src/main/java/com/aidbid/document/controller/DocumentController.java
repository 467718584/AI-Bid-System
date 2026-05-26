package com.aidbid.document.controller;

import com.aibid.common.core.Result;
import com.aibid.document.entity.BidDocument;
import com.aibid.document.service.DocumentService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/document")
@RequiredArgsConstructor
public class DocumentController {

    private final DocumentService documentService;

    @GetMapping("/{id}")
    public Result<BidDocument> getById(@PathVariable Long id) {
        return Result.ok(documentService.getById(id));
    }

    @GetMapping("/list")
    public Result<List<BidDocument>> list() {
        return Result.ok(documentService.list());
    }

    @GetMapping("/list/project/{projectId}")
    public Result<List<BidDocument>> listByProjectId(@PathVariable Long projectId) {
        return Result.ok(documentService.listByProjectId(projectId));
    }

    @PostMapping
    public Result<Void> save(@RequestBody BidDocument document) {
        documentService.save(document);
        return Result.ok();
    }

    @PutMapping
    public Result<Void> update(@RequestBody BidDocument document) {
        documentService.update(document);
        return Result.ok();
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        documentService.delete(id);
        return Result.ok();
    }
}
