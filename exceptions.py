from fastapi import HTTPException

class CustomExceptionA(HTTPException):
    def __init__(self, detail: str = "Custom Exception A occurred"):
        super().__init__(status_code=400, detail=detail)
        self.error_code = "CUSTOM_A"

class CustomExceptionB(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)
        self.error_code = "CUSTOM_B"

class ProductNotFoundException(HTTPException):
    def __init__(self, product_id: int):
        super().__init__(status_code=404, detail=f"Product with id {product_id} not found")
        self.error_code = "PRODUCT_NOT_FOUND"