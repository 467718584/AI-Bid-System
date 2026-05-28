package com.aidbid.material.service;

import com.aibid.common.core.BusinessException;
import com.aibid.common.core.ResultCode;
import com.aidbid.material.entity.Certificate;
import com.aidbid.material.mapper.CertificateMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CertificateService {

    private final CertificateMapper certificateMapper;

    public Certificate getById(Long id) {
        Certificate cert = certificateMapper.selectById(id);
        if (cert == null) {
            throw new BusinessException(ResultCode.NOT_FOUND, "证书不存在");
        }
        return cert;
    }

    public List<Certificate> listByEnterpriseId(Long enterpriseId) {
        return certificateMapper.selectList(
            new LambdaQueryWrapper<Certificate>()
                .eq(Certificate::getEnterpriseId, enterpriseId)
                .eq(Certificate::getStatus, 1)
                .orderByDesc(Certificate::getCreateTime)
        );
    }

    public List<Certificate> listByType(String certificateType) {
        return certificateMapper.selectList(
            new LambdaQueryWrapper<Certificate>()
                .eq(Certificate::getCertificateType, certificateType)
                .eq(Certificate::getStatus, 1)
                .orderByDesc(Certificate::getCreateTime)
        );
    }

    public List<Certificate> listExpiring(int days) {
        return certificateMapper.selectList(
            new LambdaQueryWrapper<Certificate>()
                .eq(Certificate::getStatus, 1)
                .le(Certificate::getExpiryDate, java.time.LocalDate.now().plusDays(days))
                .orderByAsc(Certificate::getExpiryDate)
        );
    }

    public void save(Certificate certificate) {
        certificateMapper.insert(certificate);
    }

    public void update(Certificate certificate) {
        if (certificate.getId() == null) {
            throw new BusinessException(ResultCode.PARAM_MISSING);
        }
        certificateMapper.updateById(certificate);
    }

    public void delete(Long id) {
        certificateMapper.deleteById(id);
    }
}