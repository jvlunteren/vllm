# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project

from typing import TYPE_CHECKING, Optional

import msgspec

from vllm.sampling_params import RequestOutputKind

if TYPE_CHECKING:
    from vllm.config import ModelConfig


class PoolingParams(
        msgspec.Struct,
        omit_defaults=True,  # type: ignore[call-arg]
        array_like=True):  # type: ignore[call-arg]
    """API parameters for pooling models. This 

    Attributes:
        dimensions: Reduce the dimensions of embeddings
                    if model support matryoshka representation.
    """

    dimensions: Optional[int] = None

    use_cross_encoder: bool = False
    """Internal use only."""

    logits_processing_needs_token_ids: bool = False
    """Internal use only."""

    output_kind: RequestOutputKind = RequestOutputKind.FINAL_ONLY

    def clone(self) -> "PoolingParams":
        """Returns a deep copy of the PoolingParams instance."""
        return PoolingParams(
            dimensions=self.dimensions,
            use_cross_encoder=self.use_cross_encoder,
            logits_processing_needs_token_ids=self.
            logits_processing_needs_token_ids,
        )

    def verify(self, model_config: "ModelConfig") -> None:
        if self.dimensions is not None:
            if not model_config.is_matryoshka:
                raise ValueError(
                    f'Model "{model_config.served_model_name}" does not '
                    f'support matryoshka representation, '
                    f'changing output dimensions will lead to poor results.')

            mds = model_config.matryoshka_dimensions
            if mds is not None:
                if self.dimensions not in mds:
                    raise ValueError(
                        f'Model "{model_config.served_model_name}" '
                        f'only supports {str(mds)} matryoshka dimensions, '
                        f'use other output dimensions will '
                        f'lead to poor results.')
            elif self.dimensions < 1:
                raise ValueError("Dimensions must be greater than 0")

    def __repr__(self) -> str:
        return (
            f"PoolingParams("
            f"dimensions={self.dimensions}, "
            f"use_cross_encoder={self.use_cross_encoder}, "
            f"logits_processing_needs_token_ids={self.logits_processing_needs_token_ids})"
        )

    def __post_init__(self) -> None:
        assert self.output_kind == RequestOutputKind.FINAL_ONLY,\
            "For pooling output_kind has to be FINAL_ONLY"
