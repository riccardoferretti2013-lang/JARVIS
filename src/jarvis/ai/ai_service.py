from collections.abc import Iterator

from ..memory import MemoryService
from ..projects import ProjectManager
from .ai_response import AIResponse
from .compression import (
    CompressionPolicy,
    CompressionResult,
    ContextCompressor,
)
from .context import (
    ContextProviderRegistry,
    ContextSystem,
)
from .context.providers import (
    MemoryContextProvider,
    ProjectContextProvider,
    SummaryContextProvider,
)
from .context.sources import (
    MemoryContextSource,
    ProjectContextSource,
    SummaryContextSource,
)
from .context_manager import ContextManager
from .conversation_manager import ConversationManager
from .prompt_manager import PromptManager
from .provider import Message, ToolDefinition
from .provider_manager import ProviderManager
from .summarization import (
    SummaryManager,
    SummaryPolicy,
    SummaryService,
)


class AIService:
    """
    Servizio principale dell'intelligenza artificiale.
    """

    def __init__(
        self,
        provider_manager: ProviderManager | None = None,
        conversation_manager: ConversationManager | None = None,
        context_manager: ContextManager | None = None,
        prompt_manager: PromptManager | None = None,
        memory_service: MemoryService | None = None,
        project_manager: ProjectManager | None = None,
        summary_service: SummaryService | None = None,
        summary_policy: SummaryPolicy | None = None,
        context_compressor: ContextCompressor | None = None,
    ) -> None:
        self._provider_manager = (
            provider_manager
            or ProviderManager()
        )

        self._conversation_manager = (
            conversation_manager
            or ConversationManager()
        )

        self._context_manager = (
            context_manager
            or ContextManager()
        )

        self._prompt_manager = (
            prompt_manager
            or PromptManager()
        )

        self._memory_service = (
            memory_service
            or MemoryService()
        )

        self._project_manager = (
            project_manager
            or ProjectManager()
        )

        self._summary_service = (
            summary_service
            or SummaryService(
                provider_manager=self._provider_manager
            )
        )

        self._summary_manager = SummaryManager(
            conversation_manager=(
                self._conversation_manager
            ),
            summary_service=(
                self._summary_service
            ),
            policy=(
                summary_policy
                or SummaryPolicy(
                    message_threshold=20,
                    messages_to_keep=8,
                )
            ),
        )

        self._context_compressor = (
            context_compressor
            or ContextCompressor(
                CompressionPolicy(
                    max_characters=12000,
                    minimum_recent_messages=6,
                )
            )
        )

        self._last_compression_result: (
            CompressionResult | None
        ) = None

        self._registry = (
            ContextProviderRegistry()
        )

        self._context_system = ContextSystem(
            self._registry
        )

        self._register_default_context()

    @property
    def provider_manager(
        self,
    ) -> ProviderManager:
        return self._provider_manager

    @property
    def conversation_manager(
        self,
    ) -> ConversationManager:
        return self._conversation_manager

    @property
    def context_manager(
        self,
    ) -> ContextManager:
        return self._context_manager

    @property
    def prompt_manager(
        self,
    ) -> PromptManager:
        return self._prompt_manager

    @property
    def memory_service(
        self,
    ) -> MemoryService:
        return self._memory_service

    @property
    def project_manager(
        self,
    ) -> ProjectManager:
        return self._project_manager

    @property
    def summary_manager(
        self,
    ) -> SummaryManager:
        return self._summary_manager

    @property
    def context_compressor(
        self,
    ) -> ContextCompressor:
        return self._context_compressor

    @property
    def last_compression_result(
        self,
    ) -> CompressionResult | None:
        return self._last_compression_result

    def is_available(self) -> bool:
        return (
            self._provider_manager
            .is_available()
        )

    def generate(
        self,
        message: str,
    ) -> str:
        clean_message = message.strip()

        if not clean_message:
            return (
                "Non hai inserito nessun messaggio."
            )

        self._prepare_user_message(
            clean_message
        )

        response = (
            self._provider_manager
            .provider
            .generate(
                self._build_messages()
            )
        )

        if response.strip():
            self._conversation_manager.add_assistant_message(
                response
            )

            self._update_summary()

        return response

    def generate_stream(
        self,
        message: str,
    ) -> Iterator[str]:
        clean_message = message.strip()

        if not clean_message:
            yield (
                "Non hai inserito nessun messaggio."
            )
            return

        self._prepare_user_message(
            clean_message
        )

        provider = (
            self._provider_manager.provider
        )

        complete_response = ""

        for chunk in provider.generate_stream(
            self._build_messages()
        ):
            complete_response += chunk
            yield chunk

        if complete_response.strip():
            self._conversation_manager.add_assistant_message(
                complete_response
            )

            self._update_summary()

    def generate_with_tools(
        self,
        message: str,
        tools: list[ToolDefinition],
    ) -> AIResponse:
        clean_message = message.strip()

        if not clean_message:
            return AIResponse(
                content=(
                    "Non hai inserito nessun messaggio."
                )
            )

        self._prepare_user_message(
            clean_message
        )

        return (
            self._provider_manager
            .provider
            .generate_with_tools(
                self._build_messages(),
                tools,
            )
        )

    def continue_with_tools(
        self,
        tools: list[ToolDefinition],
    ) -> AIResponse:
        return (
            self._provider_manager
            .provider
            .generate_with_tools(
                self._build_messages(),
                tools,
            )
        )

    def add_assistant_message(
        self,
        content: str,
    ) -> None:
        clean_content = content.strip()

        if not clean_content:
            return

        self._conversation_manager.add_assistant_message(
            clean_content
        )

        self._update_summary()

    def add_assistant_tool_calls(
        self,
        tool_calls: list[dict],
        content: str = "",
    ) -> None:
        self._conversation_manager.add_assistant_tool_calls(
            tool_calls=tool_calls,
            content=content,
        )

    def add_tool_result(
        self,
        tool_name: str,
        content: str,
    ) -> None:
        self._conversation_manager.add_tool_result(
            tool_name=tool_name,
            content=content,
        )

    def clear_conversation(
        self,
        clear_summary: bool = False,
    ) -> None:
        self._conversation_manager.clear()

        if clear_summary:
            self._summary_manager.clear()

    def get_summary(self) -> str:
        return (
            self._summary_manager
            .get_summary_content()
        )

    def rebuild_summary(self) -> str:
        messages = (
            self._conversation_manager
            .get_messages()
        )

        if not messages:
            return ""

        summary = (
            self._summary_service
            .summarize(messages)
        )

        if summary is None:
            return ""

        return summary.content

    def get_compression_info(self) -> str:
        result = self._last_compression_result

        if result is None:
            return (
                "La compressione non è ancora "
                "stata eseguita."
            )

        if not result.was_compressed:
            return (
                "Il contesto non ha richiesto compressione. "
                f"Caratteri: {result.final_characters}."
            )

        return (
            "Contesto compresso. "
            f"Messaggi rimossi: "
            f"{result.removed_messages}. "
            f"Caratteri risparmiati: "
            f"{result.saved_characters}. "
            f"Dimensione finale: "
            f"{result.final_characters} caratteri."
        )

    def get_provider_info(self) -> str:
        return (
            self._provider_manager
            .get_provider_info()
        )

    def _prepare_user_message(
        self,
        message: str,
    ) -> None:
        self._memory_service.process_user_message(
            message
        )

        self._conversation_manager.add_user_message(
            message
        )

    def _update_summary(self) -> None:
        try:
            self._summary_manager.update_if_needed()

        except Exception:
            return

    def _register_default_context(
        self,
    ) -> None:
        memory_source = MemoryContextSource(
            self._memory_service
        )

        project_source = ProjectContextSource(
            self._project_manager
        )

        summary_source = SummaryContextSource(
            self._summary_manager
        )

        self._registry.register(
            MemoryContextProvider(
                memory_source
            )
        )

        self._registry.register(
            ProjectContextProvider(
                project_source
            )
        )

        self._registry.register(
            SummaryContextProvider(
                summary_source
            )
        )

    def _build_messages(
        self,
    ) -> list[Message]:
        conversation_messages = (
            self._conversation_manager
            .get_messages()
        )

        selected_conversation = (
            self._context_manager
            .build_context(
                conversation_messages
            )
        )

        external_context = (
            self._context_system
            .build()
        )

        complete_context = [
            self._prompt_manager.get_system_message(),
            *external_context,
            *selected_conversation,
        ]

        compression_result = (
            self._context_compressor.compress(
                complete_context
            )
        )

        self._last_compression_result = (
            compression_result
        )

        return compression_result.messages