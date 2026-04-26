from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImproveRequest(_message.Message):
    __slots__ = ("prompt", "profile", "locale_hint", "sensitive", "attachments")
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    LOCALE_HINT_FIELD_NUMBER: _ClassVar[int]
    SENSITIVE_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENTS_FIELD_NUMBER: _ClassVar[int]
    prompt: str
    profile: str
    locale_hint: str
    sensitive: bool
    attachments: _containers.RepeatedCompositeFieldContainer[Attachment]
    def __init__(self, prompt: _Optional[str] = ..., profile: _Optional[str] = ..., locale_hint: _Optional[str] = ..., sensitive: bool = ..., attachments: _Optional[_Iterable[_Union[Attachment, _Mapping]]] = ...) -> None: ...

class Attachment(_message.Message):
    __slots__ = ("modality", "uri", "mime_type", "bytes_size")
    MODALITY_FIELD_NUMBER: _ClassVar[int]
    URI_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    BYTES_SIZE_FIELD_NUMBER: _ClassVar[int]
    modality: str
    uri: str
    mime_type: str
    bytes_size: int
    def __init__(self, modality: _Optional[str] = ..., uri: _Optional[str] = ..., mime_type: _Optional[str] = ..., bytes_size: _Optional[int] = ...) -> None: ...

class ImproveEvent(_message.Message):
    __slots__ = ("stage", "normalization", "strategy_selected", "candidate", "partial_eval", "final_decision")
    STAGE_FIELD_NUMBER: _ClassVar[int]
    NORMALIZATION_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_SELECTED_FIELD_NUMBER: _ClassVar[int]
    CANDIDATE_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_EVAL_FIELD_NUMBER: _ClassVar[int]
    FINAL_DECISION_FIELD_NUMBER: _ClassVar[int]
    stage: str
    normalization: Normalization
    strategy_selected: StrategySelected
    candidate: Candidate
    partial_eval: PartialEval
    final_decision: FinalDecision
    def __init__(self, stage: _Optional[str] = ..., normalization: _Optional[_Union[Normalization, _Mapping]] = ..., strategy_selected: _Optional[_Union[StrategySelected, _Mapping]] = ..., candidate: _Optional[_Union[Candidate, _Mapping]] = ..., partial_eval: _Optional[_Union[PartialEval, _Mapping]] = ..., final_decision: _Optional[_Union[FinalDecision, _Mapping]] = ...) -> None: ...

class Normalization(_message.Message):
    __slots__ = ("language", "task", "missing_parameters", "safety_flags")
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    MISSING_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    SAFETY_FLAGS_FIELD_NUMBER: _ClassVar[int]
    language: str
    task: str
    missing_parameters: _containers.RepeatedScalarFieldContainer[str]
    safety_flags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, language: _Optional[str] = ..., task: _Optional[str] = ..., missing_parameters: _Optional[_Iterable[str]] = ..., safety_flags: _Optional[_Iterable[str]] = ...) -> None: ...

class StrategySelected(_message.Message):
    __slots__ = ("strategy", "reason")
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    strategy: str
    reason: str
    def __init__(self, strategy: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class Candidate(_message.Message):
    __slots__ = ("text", "rationale", "estimated_tokens")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    RATIONALE_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_TOKENS_FIELD_NUMBER: _ClassVar[int]
    text: str
    rationale: str
    estimated_tokens: int
    def __init__(self, text: _Optional[str] = ..., rationale: _Optional[str] = ..., estimated_tokens: _Optional[int] = ...) -> None: ...

class PartialEval(_message.Message):
    __slots__ = ("metric", "value", "weight")
    METRIC_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    metric: str
    value: float
    weight: float
    def __init__(self, metric: _Optional[str] = ..., value: _Optional[float] = ..., weight: _Optional[float] = ...) -> None: ...

class FinalDecision(_message.Message):
    __slots__ = ("integrated_score", "explanation", "adapter", "profile")
    INTEGRATED_SCORE_FIELD_NUMBER: _ClassVar[int]
    EXPLANATION_FIELD_NUMBER: _ClassVar[int]
    ADAPTER_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    integrated_score: float
    explanation: str
    adapter: str
    profile: str
    def __init__(self, integrated_score: _Optional[float] = ..., explanation: _Optional[str] = ..., adapter: _Optional[str] = ..., profile: _Optional[str] = ...) -> None: ...
