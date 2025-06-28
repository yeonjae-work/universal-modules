"""
PromptBuilder 모듈의 예외 클래스

프롬프트 생성과 관련된 모든 예외를 정의합니다.
"""


class PromptBuilderException(Exception):
    """PromptBuilder 기본 예외"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class InvalidPromptTypeException(PromptBuilderException):
    """지원하지 않는 프롬프트 유형인 경우"""
    def __init__(self, prompt_type: str):
        message = f"Unsupported prompt type: {prompt_type}"
        super().__init__(message, {
            "prompt_type": prompt_type,
            "supported_types": ["daily_summary", "code_review", "work_pattern_analysis"]
        })


class TemplateNotFoundException(PromptBuilderException):
    """템플릿을 찾을 수 없는 경우"""
    def __init__(self, template_name: str):
        message = f"Template not found: {template_name}"
        super().__init__(message, {
            "template_name": template_name
        })


class TokenLimitExceededException(PromptBuilderException):
    """토큰 제한을 초과한 경우"""
    def __init__(self, current_tokens: int, limit: int):
        message = f"Token limit exceeded: {current_tokens} > {limit}"
        super().__init__(message, {
            "current_tokens": current_tokens,
            "limit": limit,
            "excess": current_tokens - limit
        })


class TemplateRenderException(PromptBuilderException):
    """템플릿 렌더링 중 오류가 발생한 경우"""
    def __init__(self, template_name: str, error: Exception):
        message = f"Template rendering failed for {template_name}"
        super().__init__(message, {
            "template_name": template_name,
            "error_type": type(error).__name__,
            "error_message": str(error)
        })


class MissingVariableException(PromptBuilderException):
    """필수 템플릿 변수가 누락된 경우"""
    def __init__(self, variable_name: str, template_name: str):
        message = f"Required variable '{variable_name}' missing for template '{template_name}'"
        super().__init__(message, {
            "variable_name": variable_name,
            "template_name": template_name
        })


class InvalidCustomizationException(PromptBuilderException):
    """잘못된 커스터마이징 옵션인 경우"""
    def __init__(self, option: str, value: str, valid_values: list):
        message = f"Invalid customization option '{option}': {value}"
        super().__init__(message, {
            "option": option,
            "value": value,
            "valid_values": valid_values
        }) 