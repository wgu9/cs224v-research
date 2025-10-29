"""
Q1配置管理
统一管理守卫权重、阈值、feature flags等
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Q1Config:
    """Q1系统配置"""

    # ===== 守卫权重（来自proposal v2） =====
    weights: Dict[str, float] = field(default_factory=lambda: {
        'scope': 0.4,
        'plan': 0.3,
        'test': 0.2,
        'evidence': 0.1,
    })

    # ===== 决策阈值 =====
    thresholds: Dict[str, float] = field(default_factory=lambda: {
        'warn': 0.5,      # ≥0.5: 警告但允许
        'rollback': 0.8,  # ≥0.8: 建议回滚
    })

    # ===== Scope限制（基于difficulty） =====
    # 数据支持：85.8%的SWE-bench任务只修改1个文件
    scope_file_limits: Dict[str, int] = field(default_factory=lambda: {
        '< 15 min': 2,
        '<15 min': 2,
        '<15 min fix': 2,
        '15 min - 1 hour': 3,
        '1-4 hours': 5,
        '> 4 hours': 8,
    })

    # ===== 运行模式 =====
    mode: str = "shadow"  # shadow: 只监控不干预, advisory: 监控+建议

    # ===== Feature Flags =====
    # 注意：Q1核心功能不需要LLM！以下flags仅用于可选增强
    use_llm_evidence: bool = False  # Evidence Guard是否使用LLM（权重仅0.1）

    # ===== 可复现性 =====
    seed: int = 42
    p2p_sample_size: int = 100  # PASS_TO_PASS采样数量

    # ===== 调试 =====
    verbose: bool = True  # 是否打印详细日志

    def __post_init__(self):
        """验证配置合法性"""
        # 权重和必须为1.0（除非全为0表示关闭）
        total_weight = sum(self.weights.values())
        if total_weight > 0.01 and abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")

        # 阈值必须在[0,1]范围
        for name, value in self.thresholds.items():
            if not 0 <= value <= 1:
                raise ValueError(f"Threshold {name} must be in [0,1], got {value}")

        # warn阈值必须 < rollback阈值
        if self.thresholds['warn'] >= self.thresholds['rollback']:
            raise ValueError(
                f"warn threshold ({self.thresholds['warn']}) must be < "
                f"rollback threshold ({self.thresholds['rollback']})"
            )

        # mode必须是有效值
        if self.mode not in ['shadow', 'advisory']:
            raise ValueError(f"mode must be 'shadow' or 'advisory', got {self.mode}")


# ===== 预定义配置 =====

def get_baseline_config() -> Q1Config:
    """Baseline配置：Q1关闭，只记录drift"""
    return Q1Config(
        mode="shadow",
        weights={'scope': 0.0, 'plan': 0.0, 'test': 0.0, 'evidence': 0.0},  # 全部权重为0 = 关闭
    )


def get_default_config() -> Q1Config:
    """默认Q1配置（proposal v2）"""
    return Q1Config(
        mode="advisory",
        weights={'scope': 0.4, 'plan': 0.3, 'test': 0.2, 'evidence': 0.1},
        thresholds={'warn': 0.5, 'rollback': 0.8},
    )


def get_aggressive_config() -> Q1Config:
    """激进配置：更低的阈值，更早警告"""
    return Q1Config(
        mode="advisory",
        weights={'scope': 0.4, 'plan': 0.3, 'test': 0.2, 'evidence': 0.1},
        thresholds={'warn': 0.3, 'rollback': 0.6},  # 更低的阈值
    )


# ===== 使用示例 =====
if __name__ == "__main__":
    print("=" * 80)
    print("Q1 Configuration Examples")
    print("=" * 80)

    # 默认配置
    config = get_default_config()
    print("\n1. Default Config (Proposal v2):")
    print(f"   Mode: {config.mode}")
    print(f"   Weights: {config.weights}")
    print(f"   Thresholds: {config.thresholds}")

    # Baseline配置
    baseline = get_baseline_config()
    print("\n2. Baseline Config (Q1 Disabled):")
    print(f"   Weights: {baseline.weights}")
    print(f"   → All guards disabled for comparison")

    # 激进配置
    aggressive = get_aggressive_config()
    print("\n3. Aggressive Config:")
    print(f"   Thresholds: {aggressive.thresholds}")
    print(f"   → Warn earlier, rollback sooner")

    print("\n" + "=" * 80)
    print("✅ All configurations valid")
    print("=" * 80)
