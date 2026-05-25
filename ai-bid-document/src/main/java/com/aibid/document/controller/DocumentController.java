package com.aibid.document.controller;

import com.aibid.common.core.Result;
import com.aibid.document.entity.BidDocument;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/document")
@RequiredArgsConstructor
public class DocumentController {

    @GetMapping("/{id}")
    public Result<BidDocument> getById(@PathVariable Long id) {
        BidDocument doc = new BidDocument();
        doc.setId(id);
        doc.setName("测试文档");
        return Result.ok(doc);
    }

    @GetMapping("/list")
    public Result<?> list() {
        return Result.ok();
    }
}
