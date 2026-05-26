"""技能编排引擎核心模块"""
import logging
import uuid
import json
import asyncio
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SkillType(Enum):
    """技能类型枚举"""
    PARSER = "PARSER"
    GENERATOR = "GENERATOR"
    MATCHER = "MATCHER"
    EXPORT = "EXPORT"
    UTILITY = "UTILITY"


class ExecutionStatus(Enum):
    """执行状态枚举"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class SkillParameter:
    """技能参数定义"""
    name: str
    type: str  # string/integer/boolean/object/array
    required: bool = False
    default: Any = None
    description: str = ""


@dataclass
class SkillDefinition:
    """技能定义"""
    skill_id: str
    name: str
    description: str
    version: str = "1.0.0"
    skill_type: str = "UTILITY"
    input_params: List[SkillParameter] = field(default_factory=list)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    default_params: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    priority: int = 0
    handler: Optional[Callable] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "skill_type": self.skill_type,
            "input_params": [
                {
                    "name": p.name,
                    "type": p.type,
                    "required": p.required,
                    "default": p.default,
                    "description": p.description,
                }
                for p in self.input_params
            ],
            "output_schema": self.output_schema,
            "default_params": self.default_params,
            "dependencies": self.dependencies,
            "timeout": self.timeout,
            "enabled": self.enabled,
            "tags": self.tags,
            "priority": self.priority,
        }


@dataclass
class SkillCatalog:
    """技能分类目录"""
    catalog_id: str
    code: str
    name: str
    description: str = ""
    parent_id: Optional[str] = None
    sort_order: int = 0
    icon: str = ""
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "catalog_id": self.catalog_id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "parent_id": self.parent_id,
            "sort_order": self.sort_order,
            "icon": self.icon,
            "enabled": self.enabled,
        }


@dataclass
class SkillExecutionLog:
    """技能执行日志"""
    execution_id: str
    skill_id: str
    status: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    duration: int = 0
    start_time: str = ""
    end_time: str = ""
    project_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "skill_id": self.skill_id,
            "status": self.status,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "duration": self.duration,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "project_id": self.project_id,
            "pipeline_id": self.pipeline_id,
            "retry_count": self.retry_count,
        }


@dataclass
class PipelineStage:
    """流水线阶段定义"""
    skill_id: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None  # 条件表达式
    parallel: bool = False  # 是否并行执行


@dataclass
class PipelineDefinition:
    """流水线定义"""
    pipeline_id: str
    name: str
    description: str = ""
    stages: List[PipelineStage] = field(default_factory=list)
    timeout: int = 3600

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline_id": self.pipeline_id,
            "name": self.name,
            "description": self.description,
            "stages": [
                {
                    "skill_id": s.skill_id,
                    "inputs": s.inputs,
                    "condition": s.condition,
                    "parallel": s.parallel,
                }
                for s in self.stages
            ],
            "timeout": self.timeout,
        }


class SkillEngine:
    """
    技能编排引擎

    支持：
    - 单个技能执行
    - 多技能流水线编排
    - 条件分支
    - 并行执行
    - 执行日志记录
    """

    def __init__(self):
        self._registry: Dict[str, SkillDefinition] = {}
        self._catalogs: Dict[str, SkillCatalog] = {}
        self._execution_logs: Dict[str, SkillExecutionLog] = {}
        self._pipelines: Dict[str, PipelineDefinition] = {}

    def register_skill(self, skill_def: SkillDefinition) -> None:
        """注册技能"""
        if not self.validate_skill_definition(skill_def):
            raise ValueError(f"Invalid skill definition for {skill_def.skill_id}")
        self._registry[skill_def.skill_id] = skill_def
        logger.info(f"Registered skill: {skill_def.skill_id}")

    def register_catalog(self, catalog: SkillCatalog) -> None:
        """注册技能分类"""
        self._catalogs[catalog.catalog_id] = catalog
        logger.info(f"Registered catalog: {catalog.catalog_id}")

    def list_skills(self, catalog_id: Optional[str] = None,
                   skill_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出所有技能"""
        skills = []
        for skill_def in self._registry.values():
            if not skill_def.enabled:
                continue
            if catalog_id and skill_def.skill_type != catalog_id:
                continue
            if skill_type and skill_def.skill_type != skill_type:
                continue
            skills.append(skill_def.to_dict())
        return skills

    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """获取技能详情"""
        skill_def = self._registry.get(skill_id)
        return skill_def.to_dict() if skill_def else None

    def list_catalogs(self) -> List[Dict[str, Any]]:
        """列出所有技能分类"""
        return [cat.to_dict() for cat in self._catalogs.values() if cat.enabled]

    async def execute_skill(
        self,
        skill_id: str,
        inputs: Dict[str, Any],
        project_id: Optional[str] = None,
        pipeline_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        执行单个技能

        Args:
            skill_id: 技能ID
            inputs: 输入参数
            project_id: 项目ID(可选)
            pipeline_id: 流水线ID(可选)

        Returns:
            执行结果字典
        """
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        start_time = datetime.now()

        log = SkillExecutionLog(
            execution_id=execution_id,
            skill_id=skill_id,
            status=ExecutionStatus.PENDING.value,
            input_data=inputs,
            start_time=start_time.isoformat(),
            project_id=project_id,
            pipeline_id=pipeline_id,
        )

        skill_def = self._registry.get(skill_id)
        if not skill_def:
            log.status = ExecutionStatus.FAILED.value
            log.error_message = f"Skill not found: {skill_id}"
            log.end_time = datetime.now().isoformat()
            log.duration = int((datetime.now() - start_time).total_seconds() * 1000)
            self._execution_logs[execution_id] = log
            return log.to_dict()

        log.status = ExecutionStatus.RUNNING.value

        # 合并默认参数
        merged_inputs = {**skill_def.default_params, **inputs}

        # 验证必需参数
        for param in skill_def.input_params:
            if param.required and param.name not in merged_inputs:
                log.status = ExecutionStatus.FAILED.value
                log.error_message = f"Missing required parameter: {param.name}"
                log.end_time = datetime.now().isoformat()
                log.duration = int((datetime.now() - start_time).total_seconds() * 1000)
                self._execution_logs[execution_id] = log
                return log.to_dict()

        try:
            # 调用技能处理器
            if skill_def.handler:
                result = await self._call_handler(skill_def.handler, merged_inputs, skill_def.timeout)
                log.output_data = result
            else:
                log.output_data = {"message": f"Skill {skill_id} has no handler"}

            log.status = ExecutionStatus.COMPLETED.value

        except asyncio.TimeoutError:
            log.status = ExecutionStatus.FAILED.value
            log.error_message = f"Skill execution timeout after {skill_def.timeout}s"
        except Exception as e:
            log.status = ExecutionStatus.FAILED.value
            log.error_message = str(e)
            logger.exception(f"Skill execution failed: {skill_id}")

        log.end_time = datetime.now().isoformat()
        log.duration = int((datetime.now() - start_time).total_seconds() * 1000)
        self._execution_logs[execution_id] = log

        return log.to_dict()

    async def execute_pipeline(
        self,
        pipeline_def: PipelineDefinition,
        global_inputs: Dict[str, Any],
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        执行技能流水线

        Args:
            pipeline_def: 流水线定义
            global_inputs: 全局输入参数
            project_id: 项目ID(可选)

        Returns:
            流水线执行结果
        """
        pipeline_id = f"pipeline_{uuid.uuid4().hex[:12]}"
        pipeline_start = datetime.now()
        stage_results: Dict[str, Any] = {}
        context = {**global_inputs}

        try:
            # 分析流水线结构，识别并行阶段
            parallel_groups = self._group_parallel_stages(pipeline_def.stages)

            for group in parallel_groups:
                if len(group) == 1:
                    # 单个技能，顺序执行
                    stage = group[0]
                    result = await self._execute_stage(
                        stage, context, pipeline_id, project_id
                    )
                    if result["status"] == ExecutionStatus.FAILED.value:
                        return {
                            "pipeline_id": pipeline_id,
                            "status": ExecutionStatus.FAILED.value,
                            "stage_results": stage_results,
                            "error": result.get("error_message"),
                        }
                    stage_results[stage.skill_id] = result
                    # 将输出合并到上下文
                    context[stage.skill_id] = result.get("output_data", {})
                else:
                    # 并行执行
                    tasks = [
                        self._execute_stage(stage, context, pipeline_id, project_id)
                        for stage in group
                    ]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    for stage, result in zip(group, results):
                        if isinstance(result, Exception):
                            stage_results[stage.skill_id] = {
                                "status": ExecutionStatus.FAILED.value,
                                "error_message": str(result),
                            }
                        else:
                            stage_results[stage.skill_id] = result
                            context[stage.skill_id] = result.get("output_data", {})

            return {
                "pipeline_id": pipeline_id,
                "status": ExecutionStatus.COMPLETED.value,
                "stage_results": stage_results,
                "context": context,
                "duration": int((datetime.now() - pipeline_start).total_seconds() * 1000),
            }

        except Exception as e:
            logger.exception("Pipeline execution failed")
            return {
                "pipeline_id": pipeline_id,
                "status": ExecutionStatus.FAILED.value,
                "stage_results": stage_results,
                "error": str(e),
            }

    async def _execute_stage(
        self,
        stage: PipelineStage,
        context: Dict[str, Any],
        pipeline_id: str,
        project_id: Optional[str],
    ) -> Dict[str, Any]:
        """执行单个阶段"""
        # 解析输入：从上下文或直接值中获取
        inputs = self._resolve_inputs(stage.inputs, context)

        # 执行技能
        result = await self.execute_skill(
            skill_id=stage.skill_id,
            inputs=inputs,
            project_id=project_id,
            pipeline_id=pipeline_id,
        )

        return result

    def _group_parallel_stages(self, stages: List[PipelineStage]) -> List[List[PipelineStage]]:
        """将阶段分组以识别并行执行机会"""
        groups = []
        current_group: List[PipelineStage] = []

        for stage in stages:
            if stage.parallel and current_group:
                # 将当前技能加入并行组
                current_group.append(stage)
            else:
                # 完成当前组
                if current_group:
                    groups.append(current_group)
                current_group = [stage]

        if current_group:
            groups.append(current_group)

        return groups

    def _resolve_inputs(
        self, inputs: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """解析输入引用，从上下文或全局输入中获取值"""
        resolved = {}
        for key, value in inputs.items():
            if isinstance(value, str) and value.startswith("$"):
                # 引用上下文中的值
                ref = value[1:]
                resolved[key] = context.get(ref, {})
            else:
                resolved[key] = value
        return resolved

    async def _call_handler(
        self, handler: Callable, inputs: Dict[str, Any], timeout: int
    ) -> Any:
        """调用技能处理器，支持异步和同步函数"""
        if asyncio.iscoroutinefunction(handler):
            return await asyncio.wait_for(handler(inputs), timeout=timeout)
        else:
            loop = asyncio.get_event_loop()
            return await asyncio.wait_for(
                loop.run_in_executor(None, lambda: handler(inputs)),
                timeout=timeout,
            )

    def validate_skill_definition(self, skill_def: SkillDefinition) -> bool:
        """
        验证技能定义

        Returns:
            True如果有效，否则False
        """
        if not skill_def.skill_id:
            logger.error("Skill ID is required")
            return False
        if not skill_def.name:
            logger.error("Skill name is required")
            return False
        if not skill_def.description:
            logger.warning(f"Skill {skill_def.skill_id} has no description")

        # 验证输入参数
        param_names = set()
        for param in skill_def.input_params:
            if param.name in param_names:
                logger.error(f"Duplicate parameter name: {param.name}")
                return False
            param_names.add(param.name)

        # 验证依赖
        for dep in skill_def.dependencies:
            if dep not in self._registry:
                logger.warning(f"Dependency not registered: {dep}")

        return True

    def get_execution_log(
        self, execution_id: str
    ) -> Optional[SkillExecutionLog]:
        """获取执行日志"""
        return self._execution_logs.get(execution_id)

    def list_execution_logs(
        self, skill_id: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """列出执行日志"""
        logs = self._execution_logs.values()
        if skill_id:
            logs = [log for log in logs if log.skill_id == skill_id]
        return [log.to_dict() for log in list(logs)[-limit:]]

    def register_pipeline(self, pipeline_def: PipelineDefinition) -> None:
        """注册流水线"""
        self._pipelines[pipeline_def.pipeline_id] = pipeline_def
        logger.info(f"Registered pipeline: {pipeline_def.pipeline_id}")

    def get_pipeline(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """获取流水线定义"""
        pipeline = self._pipelines.get(pipeline_id)
        return pipeline.to_dict() if pipeline else None

    def list_pipelines(self) -> List[Dict[str, Any]]:
        """列出所有流水线"""
        return [p.to_dict() for p in self._pipelines.values()]