from typing import *
from typing_extensions import Annotated
import os
import re
import yaml

import numpy as np

from pydantic import (
    Field,
    BaseModel,
    GetCoreSchemaHandler,
    # GetJsonSchemaHandler,
    # ValidationError,
)
from pydantic_core import (
    core_schema,
    PydanticCustomError,
    ValidationError,
    InitErrorDetails,
)
# from pydantic.json_schema import JsonSchemaValue


class ValidationSpec(BaseModel):
    function: AnyStr
    args: List[Any] = Field(default=[])
    kwargs: Dict[AnyStr, Any] = Field(default={})


class ValidationResult(BaseModel):
    is_valid: bool
    msg: str = Field(default="")


class PydanticBaseModel(BaseModel):
    """
    [EXAMPLE]
    class TestModel(PydanticBaseModel):
        __USER_DEFINED_VALIDATION__: List[ValidationSpec] = [
            ValidationSpec(function="validate_not_none", args=["a", "b"], kwargs={"min_count": 2}), # Validation Failed
            ValidationSpec(function="validate_not_none1", args=["b", "c"], kwargs={"min_count": 1}), # Spec Invalid
        ]
        a: int
        b: Optional[int]
        c: Optional[int]

    model = TestModel(a=1, b=None, c=None) // 2 validation error!
    """
    __USER_DEFINED_VALIDATION__: List[ValidationSpec] = []
    __USER_DEFINED_VALIDATION_SCOPE__: AnyStr = "User-Defined Validation"

    def model_post_init(self, context) -> None:
        data = self.dict()
        errors = []

        for spec in self.__USER_DEFINED_VALIDATION__:
            try:
                result = eval("self." + spec.function)(*spec.args, **spec.kwargs)
            except:
                error = InitErrorDetails(
                    type = PydanticCustomError(spec.__repr__(), "invalid spec defined"),
                    loc = [ self.__USER_DEFINED_VALIDATION_SCOPE__ ],
                    input = data,
                )
                errors.append(error)
                continue
                
            if not result.is_valid:
                error = InitErrorDetails(
                    type = PydanticCustomError(spec.__repr__(), result.msg),
                    loc = [ self.__USER_DEFINED_VALIDATION_SCOPE__ ],
                    input = data,
                )
                errors.append(error)
        
        if errors:
            raise ValidationError.from_exception_data(title=self.__USER_DEFINED_VALIDATION_SCOPE__ + " Failed", line_errors=errors)

    def validate_not_none(
        self,
        *field_names: str,
        **kwargs,
    ) -> ValidationResult:
        data = self.dict()
        is_not_none = map(lambda key: data[key] is not None, field_names)
        count_not_none = len(list(filter(None, is_not_none)))

        if kwargs.get("min_count", 0) <= count_not_none <= kwargs.get("max_count", len(field_names)):
            return ValidationResult(is_valid=True)
        else:
            return ValidationResult(is_valid=False, msg=f"{count_not_none} fields validated")


def NumpyArray(
    *,
    dtype: str,
    shape: Tuple[int] or List[int],
    is_strict: bool = False,
) -> Annotated:
    """
    [EXAMPLE]
    from pydantic import BaseModel

    class TestModel(BaseModel):
        value: NumpyArray(dtype=float, shape=[3, 3], is_strict=False)

    model = TestModel(value=list(range(9)))  # OK
    model = TestModel(value=list(range(3)))  # Error

    class TestModel(BaseModel):
        value: NumpyArray(dtype=float, shape=[3, 3], is_strict=False)

    model = TestModel(value=list(range(9)))  # Error
    """
    
    shape = tuple(shape)
    
    class PydanticAnnotation:
        @classmethod
        def numpy_validator(cls, value: Any):
            result = np.array(value, dtype=dtype)
            
            if is_strict:
                assert shape == result.shape, f"[type=shape, expected={shape}, actual={result.shape}]"
                # raise pydantic.PydanticUserError(code="custom", message=f"[type=shape, expected: {shape}, actual: {result.shape}]")
                # raise ValueError(f"[type=shape, expected: {shape}, actual: {result.shape}]")
            else:
                result = result.reshape(shape)
            
            return result
        
        @classmethod
        def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: GetCoreSchemaHandler,
        ) -> core_schema.CoreSchema:

            return core_schema.json_or_python_schema(
                json_schema=core_schema.chain_schema([
                    core_schema.no_info_plain_validator_function(cls.numpy_validator),
                ]),
                python_schema=core_schema.union_schema([
                    core_schema.no_info_plain_validator_function(cls.numpy_validator)
                ]),
                serialization=core_schema.plain_serializer_function_ser_schema(
                    np.ndarray.tolist
                ),
            )
    
        # @classmethod
        # def __get_pydantic_json_schema__(
        #     cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
        # ) -> JsonSchemaValue:
        #     pass

    return Annotated[
        np.ndarray,
        PydanticAnnotation
    ]


def parse_yaml(path: str) -> Dict[str, Any]:
    """
    To parse yaml file with environment variables

    [EXAMPLE]
    some_a:
      var1: ${ENVVAR} # $ENVVAR or <EMPTY_VALUE>
      var2: ${ENVVAR:DEFAULT_VALUE} # $ENVVAR or <DEFAULT_VALUE>
    """
    tag = None
    value_matcher = re.compile(r"\${([^}^{]+)}")
    field_matcher = re.compile(f"^{tag} ") if tag else re.compile(r"[^$]*\${([^}^{]+)}.*")

    # NOTE: make new loader class to add resolver and constructor
    class _Loader(yaml.SafeLoader):
        pass

    # NOTE: str.split(":")
    # to use like ${ENVVAR:DEFAULT_VALUE} pattern
    def _replace_func(match):
        envparts = f"{match.group(1)}:".split(":")
        output = os.getenv(envparts[0], envparts[1])
        if output.startswith("?"):
            raise Exception(output)
        return output

    def _constructor(loader, node):
        # print(node.tag, node.value)
        output = value_matcher.sub(_replace_func, node.value)
        return output or None

    # NOTE: tag is None
    # to parse all the ${ENVVAR}, or you can specify a tag to use like <TAG> ${ENVVAR} pattern.
    # example of <TAG> : !ENV, !envvar
    _Loader.add_implicit_resolver(tag, field_matcher, None)
    _Loader.add_constructor(tag, _constructor)

    # available exceptions: FileNotFoundError, PermissionError, ParserError
    # from yaml.parser import ParserError
    with open(path, "r") as f:
        return yaml.load(f, _Loader)
