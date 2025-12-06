"""Template management and discovery."""

from pathlib import Path
from typing import Dict

from .base import BaseTemplate, Jinja2Template
from ..exceptions import TemplateError


class TemplateManager:
    """Manages built-in and custom templates."""

    BUILTIN_TEMPLATES: Dict[str, str] = {
        "standard": "builtin/standard.ics",
        "sport": "builtin/sport.ics",
        "music": "builtin/music.ics",
        "recurring": "builtin/recurring.ics",
    }

    def __init__(self) -> None:
        self.template_dir = Path(__file__).parent
        self._cache: Dict[str, BaseTemplate] = {}

    def get_template(self, name: str) -> BaseTemplate:
        """
        Get template by name or path.

        Args:
            name: Built-in template name OR custom template path

        Returns:
            BaseTemplate instance

        Raises:
            TemplateError: Template not found or invalid
        """
        # Check cache first
        if name in self._cache:
            return self._cache[name]

        # Resolve template path
        if name in self.BUILTIN_TEMPLATES:
            template_path = self.template_dir / self.BUILTIN_TEMPLATES[name]
        else:
            # Treat as custom template path
            template_path = Path(name)
            if not template_path.exists():
                raise TemplateError(
                    f"Template not found: {name}. "
                    f"Available built-in templates: {list(self.BUILTIN_TEMPLATES.keys())}"
                )

        # Verify template exists
        if not template_path.exists():
            raise TemplateError(f"Template file not found: {template_path}")

        # Create and cache template
        try:
            template = Jinja2Template(template_path)
            self._cache[name] = template
            return template
        except Exception as e:
            raise TemplateError(f"Failed to load template {name}: {e}")

    def list_builtin_templates(self) -> list[str]:
        """Return list of available built-in templates."""
        return list(self.BUILTIN_TEMPLATES.keys())
