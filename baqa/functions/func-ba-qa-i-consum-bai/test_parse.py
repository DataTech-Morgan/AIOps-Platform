from abc import ABC, abstractmethod
from typing import List
import ast
from typing import Any, List, Tuple

import contextlib
import mimetypes
from io import BufferedReader, BytesIO
from pathlib import PurePath
from typing import Any, Generator, List, Literal, Mapping, Optional, Union, cast
from typing import TYPE_CHECKING, AsyncIterator, Iterator, List, Optional
from pathlib import Path
from typing import Callable, Iterable, Iterator, Optional, Sequence, TypeVar, Union
from pydantic import Field, root_validator, BaseModel

from abc import ABC
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    TypedDict,
    Union,
    cast,
)

from typing_extensions import NotRequired
from abc import abstractmethod
from typing import TYPE_CHECKING, List

from tree_sitter import Language, Parser

class BaseSerialized(TypedDict):
    """Base class for serialized objects.

    Parameters:
        lc: The version of the serialization format.
        id: The unique identifier of the object.
        name: The name of the object. Optional.
        graph: The graph of the object. Optional.
    """

    lc: int
    id: List[str]
    name: NotRequired[str]
    graph: NotRequired[Dict[str, Any]]



class SerializedConstructor(BaseSerialized):
    """Serialized constructor.

    Parameters:
        type: The type of the object. Must be "constructor".
        kwargs: The constructor arguments.
    """

    type: Literal["constructor"]
    kwargs: Dict[str, Any]



class SerializedSecret(BaseSerialized):
    """Serialized secret.

    Parameters:
        type: The type of the object. Must be "secret".
    """

    type: Literal["secret"]



class SerializedNotImplemented(BaseSerialized):
    """Serialized not implemented.

    Parameters:
        type: The type of the object. Must be "not_implemented".
        repr: The representation of the object. Optional.
    """

    type: Literal["not_implemented"]
    repr: Optional[str]


def try_neq_default(value: Any, key: str, model: BaseModel) -> bool:
    """Try to determine if a value is different from the default.

    Args:
        value: The value.
        key: The key.
        model: The pydantic model.

    Returns:
        Whether the value is different from the default.

    Raises:
        Exception: If the key is not in the model.
    """
    try:
        return model.__fields__[key].get_default() != value
    except Exception:
        return True



class Serializable(BaseModel, ABC):
    """Serializable base class.

    This class is used to serialize objects to JSON.

    It relies on the following methods and properties:

    - `is_lc_serializable`: Is this class serializable?
        By design, even if a class inherits from Serializable, it is not serializable by
        default. This is to prevent accidental serialization of objects that should not
        be serialized.
    - `get_lc_namespace`: Get the namespace of the langchain object.
        During deserialization, this namespace is used to identify
        the correct class to instantiate.
        Please see the `Reviver` class in `langchain_core.load.load` for more details.
        During deserialization an additional mapping is handle
        classes that have moved or been renamed across package versions.
    - `lc_secrets`: A map of constructor argument names to secret ids.
    - `lc_attributes`: List of additional attribute names that should be included
        as part of the serialized representation.
    """

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Is this class serializable?

        By design, even if a class inherits from Serializable, it is not serializable by
        default. This is to prevent accidental serialization of objects that should not
        be serialized.

        Returns:
            Whether the class is serializable. Default is False.
        """
        return False

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object.

        For example, if the class is `langchain.llms.openai.OpenAI`, then the
        namespace is ["langchain", "llms", "openai"]
        """
        return cls.__module__.split(".")

    @property
    def lc_secrets(self) -> Dict[str, str]:
        """A map of constructor argument names to secret ids.

        For example,
            {"openai_api_key": "OPENAI_API_KEY"}
        """
        return dict()

    @property
    def lc_attributes(self) -> Dict:
        """List of attribute names that should be included in the serialized kwargs.

        These attributes must be accepted by the constructor.
        Default is an empty dictionary.
        """
        return {}

    @classmethod
    def lc_id(cls) -> List[str]:
        """A unique identifier for this class for serialization purposes.

        The unique identifier is a list of strings that describes the path
        to the object.
        For example, for the class `langchain.llms.openai.OpenAI`, the id is
        ["langchain", "llms", "openai", "OpenAI"].
        """
        return [*cls.get_lc_namespace(), cls.__name__]

    class Config:
        extra = "ignore"

    def __repr_args__(self) -> Any:
        return [
            (k, v)
            for k, v in super().__repr_args__()
            if (k not in self.__fields__ or try_neq_default(v, k, self))
        ]

    def to_json(self) -> Union[SerializedConstructor, SerializedNotImplemented]:
        """Serialize the object to JSON.

        Returns:
            A json serializable object or a SerializedNotImplemented object.
        """
        if not self.is_lc_serializable():
            return self.to_json_not_implemented()

        secrets = dict()
        # Get latest values for kwargs if there is an attribute with same name
        lc_kwargs = {
            k: getattr(self, k, v)
            for k, v in self
            if not (self.__exclude_fields__ or {}).get(k, False)  # type: ignore
            and _is_field_useful(self, k, v)
        }

        # Merge the lc_secrets and lc_attributes from every class in the MRO
        for cls in [None, *self.__class__.mro()]:
            # Once we get to Serializable, we're done
            if cls is Serializable:
                break

            if cls:
                deprecated_attributes = [
                    "lc_namespace",
                    "lc_serializable",
                ]

                for attr in deprecated_attributes:
                    if hasattr(cls, attr):
                        raise ValueError(
                            f"Class {self.__class__} has a deprecated "
                            f"attribute {attr}. Please use the corresponding "
                            f"classmethod instead."
                        )

            # Get a reference to self bound to each class in the MRO
            this = cast(Serializable, self if cls is None else super(cls, self))

            secrets.update(this.lc_secrets)
            # Now also add the aliases for the secrets
            # This ensures known secret aliases are hidden.
            # Note: this does NOT hide any other extra kwargs
            # that are not present in the fields.
            for key in list(secrets):
                value = secrets[key]
                if key in this.__fields__:
                    secrets[this.__fields__[key].alias] = value
            lc_kwargs.update(this.lc_attributes)

        # include all secrets, even if not specified in kwargs
        # as these secrets may be passed as an environment variable instead
        for key in secrets.keys():
            secret_value = getattr(self, key, None) or lc_kwargs.get(key)
            if secret_value is not None:
                lc_kwargs.update({key: secret_value})

        return {
            "lc": 1,
            "type": "constructor",
            "id": self.lc_id(),
            "kwargs": lc_kwargs
            if not secrets
            else _replace_secrets(lc_kwargs, secrets),
        }

    def to_json_not_implemented(self) -> SerializedNotImplemented:
        return to_json_not_implemented(self)



def _is_field_useful(inst: Serializable, key: str, value: Any) -> bool:
    """Check if a field is useful as a constructor argument.

    Args:
        inst: The instance.
        key: The key.
        value: The value.

    Returns:
        Whether the field is useful. If the field is required, it is useful.
        If the field is not required, it is useful if the value is not None.
        If the field is not required and the value is None, it is useful if the
        default value is different from the value.
    """
    field = inst.__fields__.get(key)
    if not field:
        return False
    return field.required is True or value or field.get_default() != value

PathLike = Union[str, PurePath]

class BaseMedia(Serializable):
    """Use to represent media content.

    Media objects can be used to represent raw data, such as text or binary data.

    LangChain Media objects allow associating metadata and an optional identifier
    with the content.

    The presence of an ID and metadata make it easier to store, index, and search
    over the content in a structured way.
    """

    # The ID field is optional at the moment.
    # It will likely become required in a future major release after
    # it has been adopted by enough vectorstore implementations.
    id: Optional[str] = None
    """An optional identifier for the document.

    Ideally this should be unique across the document collection and formatted 
    as a UUID, but this will not be enforced.
    
    .. versionadded:: 0.2.11
    """

    metadata: dict = Field(default_factory=dict)
    """Arbitrary metadata associated with the content."""



class Blob(BaseMedia):


    data: Union[bytes, str, None]
    """Raw data associated with the blob."""
    mimetype: Optional[str] = None
    """MimeType not to be confused with a file extension."""
    encoding: str = "utf-8"
    """Encoding to use if decoding the bytes into a string.

    Use utf-8 as default encoding, if decoding to string.
    """
    path: Optional[PathLike] = None
    """Location where the original content was found."""

    class Config:
        arbitrary_types_allowed = True
        frozen = True

    @property
    def source(self) -> Optional[str]:

        if self.metadata and "source" in self.metadata:
            return cast(Optional[str], self.metadata["source"])
        return str(self.path) if self.path else None

    @root_validator(pre=True)
    def check_blob_is_valid(cls, values: Mapping[str, Any]) -> Mapping[str, Any]:
        """Verify that either data or path is provided."""
        if "data" not in values and "path" not in values:
            raise ValueError("Either data or path must be provided")
        return values

    def as_string(self) -> str:
        """Read data as a string."""
        if self.data is None and self.path:
            with open(str(self.path), "r", encoding=self.encoding) as f:
                return f.read()
        elif isinstance(self.data, bytes):
            return self.data.decode(self.encoding)
        elif isinstance(self.data, str):
            return self.data
        else:
            raise ValueError(f"Unable to get string for blob {self}")


    def as_bytes(self) -> bytes:
        """Read data as bytes."""
        if isinstance(self.data, bytes):
            return self.data
        elif isinstance(self.data, str):
            return self.data.encode(self.encoding)
        elif self.data is None and self.path:
            with open(str(self.path), "rb") as f:
                return f.read()
        else:
            raise ValueError(f"Unable to get bytes for blob {self}")


    @contextlib.contextmanager
    def as_bytes_io(self) -> Generator[Union[BytesIO, BufferedReader], None, None]:
        """Read data as a byte stream."""
        if isinstance(self.data, bytes):
            yield BytesIO(self.data)
        elif self.data is None and self.path:
            with open(str(self.path), "rb") as f:
                yield f
        else:
            raise NotImplementedError(f"Unable to convert blob {self}")


    @classmethod
    def from_path(
        cls,
        path: PathLike,
        *,
        encoding: str = "utf-8",
        mime_type: Optional[str] = None,
        guess_type: bool = True,
        metadata: Optional[dict] = None,
    ):

        if mime_type is None and guess_type:
            _mimetype = mimetypes.guess_type(path)[0] if guess_type else None
        else:
            _mimetype = mime_type
        # We do not load the data immediately, instead we treat the blob as a
        # reference to the underlying data.
        return cls(
            data=None,
            mimetype=_mimetype,
            encoding=encoding,
            path=path,
            metadata=metadata if metadata is not None else {},
        )


    @classmethod
    def from_data(
        cls,
        data: Union[str, bytes],
        *,
        encoding: str = "utf-8",
        mime_type: Optional[str] = None,
        path: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):

        return cls(
            data=data,
            mimetype=mime_type,
            encoding=encoding,
            path=path,
            metadata=metadata if metadata is not None else {},
        )


    def __repr__(self) -> str:
        """Define the blob representation."""
        str_repr = f"Blob {id(self)}"
        if self.source:
            str_repr += f" {self.source}"
        return str_repr



class Document(BaseMedia):

    page_content: str
    """String text."""
    type: Literal["Document"] = "Document"

    def __init__(self, page_content: str, **kwargs: Any) -> None:
        """Pass page_content in as positional or named arg."""
        # my-py is complaining that page_content is not defined on the base class.
        # Here, we're relying on pydantic base class to handle the validation.
        super().__init__(page_content=page_content, **kwargs)  # type: ignore[call-arg]

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this class is serializable."""
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return ["langchain", "schema", "document"]

    def __str__(self) -> str:

        if self.metadata:
            return f"page_content='{self.page_content}' metadata={self.metadata}"
        else:
            return f"page_content='{self.page_content}'"



class BaseLoader(ABC):
    """Interface for Document Loader.

    Implementations should implement the lazy-loading method using generators
    to avoid loading all Documents into memory at once.

    `load` is provided just for user convenience and should not be overridden.
    """

    # Sub-classes should not implement this method directly. Instead, they
    # should implement the lazy load method.
    def load(self) -> List[Document]:
        """Load data into Document objects."""
        return list(self.lazy_load())


    async def aload(self) -> List[Document]:
        """Load data into Document objects."""
        return [document async for document in self.alazy_load()]


    def load_and_split(
        self, text_splitter = None
    ) -> List[Document]:
        """Load Documents and split into chunks. Chunks are returned as Documents.

        Do not override this method. It should be considered to be deprecated!

        Args:
            text_splitter: TextSplitter instance to use for splitting documents.
              Defaults to RecursiveCharacterTextSplitter.

        Returns:
            List of Documents.
        """

        if text_splitter is None:
            try:
                from langchain_text_splitters import RecursiveCharacterTextSplitter
            except ImportError as e:
                raise ImportError(
                    "Unable to import from langchain_text_splitters. Please specify "
                    "text_splitter or install langchain_text_splitters with "
                    "`pip install -U langchain-text-splitters`."
                ) from e

            _text_splitter: TextSplitter = RecursiveCharacterTextSplitter()
        else:
            _text_splitter = text_splitter
        docs = self.load()
        return _text_splitter.split_documents(docs)


    # Attention: This method will be upgraded into an abstractmethod once it's
    #            implemented in all the existing subclasses.
    def lazy_load(self) -> Iterator[Document]:
        """A lazy loader for Documents."""
        if type(self).load != BaseLoader.load:
            return iter(self.load())
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement lazy_load()"
        )


    async def alazy_load(self) -> AsyncIterator[Document]:
        """A lazy loader for Documents."""
        iterator = await run_in_executor(None, self.lazy_load)
        done = object()
        while True:
            doc = await run_in_executor(None, next, iterator, done)  # type: ignore[call-arg, arg-type]
            if doc is done:
                break
            yield doc  # type: ignore[misc]

class BaseBlobParser(ABC):

    def parse(self, blob: Blob) -> List[Document]:
        return list(self.lazy_parse(blob))


class BlobLoader(ABC):

    @abstractmethod
    def yield_blobs(
        self,
    ):
        return Iterable
        
T = TypeVar("T")

def _make_iterator(
    length_func: Callable[[], int], show_progress: bool = False
) -> Callable[[Iterable[T]], Iterator[T]]:
    """Create a function that optionally wraps an iterable in tqdm."""
    iterator: Callable[[Iterable[T]], Iterator[T]]
    if show_progress:
        try:
            from tqdm.auto import tqdm
        except ImportError:
            raise ImportError(
                "You must install tqdm to use show_progress=True."
                "You can install tqdm with `pip install tqdm`."
            )

        # Make sure to provide `total` here so that tqdm can show
        # a progress bar that takes into account the total number of files.
        def _with_tqdm(iterable: Iterable[T]) -> Iterator[T]:
            """Wrap an iterable in a tqdm progress bar."""
            return tqdm(iterable, total=length_func())

        iterator = _with_tqdm
    else:
        iterator = iter

    return iterator


class FileSystemBlobLoader(BlobLoader):


    def __init__(
        self,
        path: Union[str, Path],
        *,
        glob: str = "**/[!.]*",
        exclude: Sequence[str] = (),
        suffixes: Optional[Sequence[str]] = None,
        show_progress: bool = False,
    ) -> None:

        if isinstance(path, Path):
            _path = path
        elif isinstance(path, str):
            _path = Path(path)
        else:
            raise TypeError(f"Expected str or Path, got {type(path)}")

        self.path = _path.expanduser()  # Expand user to handle ~
        self.glob = glob
        self.suffixes = set(suffixes or [])
        self.show_progress = show_progress
        self.exclude = exclude


    def yield_blobs(
        self,
    ) -> Iterable[Blob]:
        """Yield blobs that match the requested pattern."""
        iterator = _make_iterator(
            length_func=self.count_matching_files, show_progress=self.show_progress
        )

        for path in iterator(self._yield_paths()):
            yield Blob.from_path(path)


    def _yield_paths(self) -> Iterable[Path]:
        """Yield paths that match the requested pattern."""
        if self.path.is_file():
            yield self.path
            return

        paths = self.path.glob(self.glob)
        for path in paths:
            if self.exclude:
                if any(path.match(glob) for glob in self.exclude):
                    continue
            if path.is_file():
                if self.suffixes and path.suffix not in self.suffixes:
                    continue
                yield path

    def count_matching_files(self) -> int:
        """Count files that match the pattern without loading them."""
        # Carry out a full iteration to count the files without
        # materializing anything expensive in memory.
        num = 0
        for _ in self._yield_paths():
            num += 1
        return num


class CodeSegmenter(ABC):
    
    def __init__(self, code: str):
        self.code = code
    def is_valid(self) -> bool:
        return True
    
    @abstractmethod
    def simplify_code(self) -> str:
        raise NotImplementedError()  # pragma: no cover
    
    @abstractmethod
    def extract_functions_classes(self) -> List[str]:
        raise NotImplementedError()  # pragma: no cover
    
class TreeSitterSegmenter(CodeSegmenter):
    """Abstract class for `CodeSegmenter`s that use the tree-sitter library."""

    def __init__(self, code: str):
        super().__init__(code)
        self.source_lines = self.code.splitlines()

        try:
            import tree_sitter  # noqa: F401
            import tree_sitter_languages  # noqa: F401
        except ImportError:
            raise ImportError(
                "Could not import tree_sitter/tree_sitter_languages Python packages. "
                "Please install them with "
                "`pip install tree-sitter tree-sitter-languages`."
            )


    def is_valid(self) -> bool:
        language = self.get_language()
        error_query = language.query("(ERROR) @error")

        parser = self.get_parser()
        tree = parser.parse(bytes(self.code, encoding="UTF-8"))

        return len(error_query.captures(tree.root_node)) == 0


    def extract_functions_classes(self) -> List[str]:
        language = self.get_language()
        query = language.query(self.get_chunk_query())

        parser = self.get_parser()
        tree = parser.parse(bytes(self.code, encoding="UTF-8"))
        captures = query.captures(tree.root_node)

        processed_lines = set()
        chunks = []

        for node, name in captures:
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            lines = list(range(start_line, end_line + 1))

            if any(line in processed_lines for line in lines):
                continue

            processed_lines.update(lines)
            chunk_text = node.text.decode("UTF-8")
            chunks.append(chunk_text)

        return chunks


    def simplify_code(self) -> str:
        language = self.get_language()
        query = language.query(self.get_chunk_query())

        parser = self.get_parser()
        tree = parser.parse(bytes(self.code, encoding="UTF-8"))
        processed_lines = set()

        simplified_lines = self.source_lines[:]
        for node, name in query.captures(tree.root_node):
            start_line = node.start_point[0]
            end_line = node.end_point[0]

            lines = list(range(start_line, end_line + 1))
            if any(line in processed_lines for line in lines):
                continue

            simplified_lines[start_line] = self.make_line_comment(
                f"Code for: {self.source_lines[start_line]}"
            )

            for line_num in range(start_line + 1, end_line + 1):
                simplified_lines[line_num] = None  # type: ignore

            processed_lines.update(lines)

        return "\n".join(line for line in simplified_lines if line is not None)


    def get_parser(self) -> "Parser":
        from tree_sitter import Parser
        parser = Parser(self.get_language())
        return parser


    @abstractmethod
    def get_language(self):
        raise NotImplementedError()  # pragma: no cover


    @abstractmethod
    def get_chunk_query(self) -> str:
        raise NotImplementedError()  # pragma: no cover


    @abstractmethod
    def make_line_comment(self, text: str) -> str:
        raise NotImplementedError()  # pragma: no cover


class CSegmenter(TreeSitterSegmenter):
    """Code segmenter for C."""

    def get_language(self) -> "Language":
        from tree_sitter_languages import get_language

        return get_language("c")


    def get_chunk_query(self) -> str:
        CHUNK_QUERY = """
    [
        (struct_specifier
            body: (field_declaration_list)) @struct
        (enum_specifier
            body: (enumerator_list)) @enum
        (union_specifier
            body: (field_declaration_list)) @union
        (function_definition) @function
    ]
""".strip()
        return CHUNK_QUERY


    def make_line_comment(self, text: str) -> str:
        return f"// {text}"


class PythonSegmenter(CodeSegmenter):
    """Code segmenter for `Python`."""

    def __init__(self, code: str):
        super().__init__(code)
        self.source_lines = self.code.splitlines()


    def is_valid(self) -> bool:
        try:
            ast.parse(self.code)
            return True
        except SyntaxError:
            return False


    def _extract_code(self, node: Any) -> str:
        start = node.lineno - 1
        end = node.end_lineno
        return "\n".join(self.source_lines[start:end])

    def extract_functions_classes(self) -> List[str]:
        tree = ast.parse(self.code)
        functions_classes = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                functions_classes.append(self._extract_code(node))

        return functions_classes


    def simplify_code(self) -> str:
        tree = ast.parse(self.code)
        simplified_lines = self.source_lines[:]

        indices_to_del: List[Tuple[int, int]] = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start, end = node.lineno - 1, node.end_lineno
                simplified_lines[start] = f"# Code for: {simplified_lines[start]}"
                assert isinstance(end, int)
                indices_to_del.append((start + 1, end))

        for start, end in reversed(indices_to_del):
            del simplified_lines[start + 0 : end]

        return "\n".join(simplified_lines)


LANGUAGE_EXTENSIONS: Dict[str, str] = {
    "py": "python",
    "js": "js",
    "cobol": "cobol",
    "c": "c",
    "cpp": "cpp",
    "cs": "csharp",
    "rb": "ruby",
    "scala": "scala",
    "rs": "rust",
    "go": "go",
    "kt": "kotlin",
    "lua": "lua",
    "pl": "perl",
    "ts": "ts",
    "java": "java",
    "php": "php",
    "ex": "elixir",
    "exs": "elixir",
}

LANGUAGE_SEGMENTERS: Dict[str, Any] = {
    "python": PythonSegmenter,
    # "js": JavaScriptSegmenter,
    # "cobol": CobolSegmenter,
    "c": CSegmenter,
    # "cpp": CPPSegmenter,
    # "csharp": CSharpSegmenter,
    # "ruby": RubySegmenter,
    # "rust": RustSegmenter,
    # "scala": ScalaSegmenter,
    # "go": GoSegmenter,
    # "kotlin": KotlinSegmenter,
    # "lua": LuaSegmenter,
    # "perl": PerlSegmenter,
    # "ts": TypeScriptSegmenter,
    # "java": JavaSegmenter,
    # "php": PHPSegmenter,
    # "elixir": ElixirSegmenter,
}

Language = Literal[
    "cpp",
    "go",
    "java",
    "kotlin",
    "js",
    "ts",
    "php",
    "proto",
    "python",
    "rst",
    "ruby",
    "rust",
    "scala",
    "swift",
    "markdown",
    "latex",
    "html",
    "sol",
    "csharp",
    "cobol",
    "c",
    "lua",
    "perl",
    "elixir",
]

class BaseBlobParser(ABC):

    def parse(self, blob):
        return list(self.lazy_parse(blob))

class LanguageParser(BaseBlobParser):
    """Parse using the respective programming language syntax.

    Each top-level function and class in the code is loaded into separate documents.
    Furthermore, an extra document is generated, containing the remaining top-level code
    that excludes the already segmented functions and classes.

    This approach can potentially improve the accuracy of QA models over source code.

    The supported languages for code parsing are:

    - C: "c" (*)
    - C++: "cpp" (*)
    - C#: "csharp" (*)
    - COBOL: "cobol"
    - Elixir: "elixir"
    - Go: "go" (*)
    - Java: "java" (*)
    - JavaScript: "js" (requires package `esprima`)
    - Kotlin: "kotlin" (*)
    - Lua: "lua" (*)
    - Perl: "perl" (*)
    - Python: "python"
    - Ruby: "ruby" (*)
    - Rust: "rust" (*)
    - Scala: "scala" (*)
    - TypeScript: "ts" (*)

    Items marked with (*) require the packages `tree_sitter` and
    `tree_sitter_languages`.

    The language used for parsing can be configured, along with the minimum number of
    lines required to activate the splitting based on syntax.

    If a language is not explicitly specified, `LanguageParser` will infer one from
    filename extensions, if present.

    Examples:

       .. code-block:: python

            loader = GenericLoader.from_filesystem(
                "./code",
                glob="**/*",
                suffixes=[".py", ".js"],
                parser=LanguageParser()
            )
            docs = loader.load()

        Example instantiations to manually select the language:

        .. code-block:: python


            loader = GenericLoader.from_filesystem(
                "./code",
                glob="**/*",
                suffixes=[".py"],
                parser=LanguageParser(language="python")
            )

        Example instantiations to set number of lines threshold:

        .. code-block:: python

            loader = GenericLoader.from_filesystem(
                "./code",
                glob="**/*",
                suffixes=[".py"],
                parser=LanguageParser(parser_threshold=200)
            )
    """

    def __init__(self, language = None, parser_threshold: int = 0):
        """
        Language parser that split code using the respective language syntax.

        Args:
            language: If None (default), it will try to infer language from source.
            parser_threshold: Minimum lines needed to activate parsing (0 by default).
        """
        if language and language not in LANGUAGE_SEGMENTERS:
            raise Exception(f"No parser available for {language}")
        self.language = language
        self.parser_threshold = parser_threshold


    def lazy_parse(self, blob):
        code = blob.as_string()

        language = self.language or (
            LANGUAGE_EXTENSIONS.get(blob.source.rsplit(".", 1)[-1])
            if isinstance(blob.source, str)
            else None
        )

        if language is None:
            yield Document(
                page_content=code,
                metadata={
                    "source": blob.source,
                },
            )
            return

        if self.parser_threshold >= len(code.splitlines()):
            yield Document(
                page_content=code,
                metadata={
                    "source": blob.source,
                    "language": language,
                },
            )
            return

        self.Segmenter = LANGUAGE_SEGMENTERS[language]
        segmenter = self.Segmenter(blob.as_string())
        if not segmenter.is_valid():
            yield Document(
                page_content=code,
                metadata={
                    "source": blob.source,
                },
            )
            return

        for functions_classes in segmenter.extract_functions_classes():
            yield Document(
                page_content=functions_classes,
                metadata={
                    "source": blob.source,
                    "content_type": "functions_classes",
                    "language": language,
                },
            )
        yield Document(
            page_content=segmenter.simplify_code(),
            metadata={
                "source": blob.source,
                "content_type": "simplified_code",
                "language": language,
            },
        )


class GenericLoader(BaseLoader):

    def __init__(
        self,
        blob_loader: BlobLoader,  # type: ignore[valid-type]
        blob_parser: BaseBlobParser,
    ) -> None:
        """A generic document loader.

        Args:
            blob_loader: A blob loader which knows how to yield blobs
            blob_parser: A blob parser which knows how to parse blobs into documents
        """
        self.blob_loader = blob_loader
        self.blob_parser = blob_parser


    def lazy_load(
        self,
    ) -> Iterator[Document]:
        """Load documents lazily. Use this when working at a large scale."""
        for blob in self.blob_loader.yield_blobs():  # type: ignore[attr-defined]
            yield from self.blob_parser.lazy_parse(blob)


    def load_and_split(
        self, text_splitter = None
    ) -> List[Document]:
        """Load all documents and split them into sentences."""
        raise NotImplementedError(
            "Loading and splitting is not yet implemented for generic loaders. "
            "When they will be implemented they will be added via the initializer. "
            "This method should not be used going forward."
        )


    @classmethod
    def from_filesystem(
        cls,
        path,
        *,
        glob: str = "**/[!.]*",
        exclude: Sequence[str] = (),
        suffixes: Optional[Sequence[str]] = None,
        show_progress: bool = False,
        parser = "default",
        parser_kwargs: Optional[dict] = None,
    ):
        blob_loader = FileSystemBlobLoader(  # type: ignore[attr-defined, misc]
            path,
            glob=glob,
            exclude=exclude,
            suffixes=suffixes,
            show_progress=show_progress,
        )

        blob_parser = parser
        return cls(blob_loader, blob_parser)


    @staticmethod
    def get_parser(**kwargs: Any) -> BaseBlobParser:
        """Override this method to associate a default parser with the class."""
        raise NotImplementedError()