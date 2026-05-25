package com.aibid.material.controller;

import com.aibid.common.core.Result;
import com.aibid.material.entity.BidMaterial;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/material")
@RequiredArgsConstructor
public class MaterialController {

    @GetMapping("/{id}")
    public Result<BidMaterial> getById(@PathVariable Long id) {
        BidMaterial material = new BidMaterial();
        material.setId(id);
        material.setName("测试材料");
        return Result.ok(material);
    }

    @GetMapping("/list")
    public Result<?> list() {
        return Result.ok();
    }
}
