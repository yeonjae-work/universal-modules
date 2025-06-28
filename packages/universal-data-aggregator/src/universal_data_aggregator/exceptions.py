"""
DataAggregator 모듈의 예외 클래스

데이터 집계와 관련된 모든 예외를 정의합니다.
"""


class DataAggregatorException(Exception):
    """DataAggregator 기본 예외"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class InvalidInputDataException(DataAggregatorException):
    """잘못된 입력 데이터인 경우"""
    def __init__(self, field: str, reason: str):
        message = f"Invalid input data - {field}: {reason}"
        super().__init__(message, {
            "field": field,
            "reason": reason
        })


class AggregationFailedException(DataAggregatorException):
    """집계 처리 중 오류가 발생한 경우"""
    def __init__(self, operation: str, error: Exception):
        message = f"Aggregation failed during {operation}"
        super().__init__(message, {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error)
        })


class ComplexityCalculationException(DataAggregatorException):
    """복잡도 계산 중 오류가 발생한 경우"""
    def __init__(self, file_path: str, error: Exception):
        message = f"Complexity calculation failed for {file_path}"
        super().__init__(message, {
            "file_path": file_path,
            "error_type": type(error).__name__,
            "error_message": str(error)
        })


class CacheException(DataAggregatorException):
    """캐시 관련 오류"""
    def __init__(self, operation: str, error: Exception):
        message = f"Cache operation failed: {operation}"
        super().__init__(message, {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error)
        })


class DataValidationException(DataAggregatorException):
    """데이터 검증 오류"""
    def __init__(self, validation_rule: str, failed_data: str):
        message = f"Data validation failed: {validation_rule}"
        super().__init__(message, {
            "validation_rule": validation_rule,
            "failed_data": failed_data
        }) 